from typing import List, Protocol, runtime_checkable, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import numpy as np

from app.models.document import Document


@runtime_checkable
class Embedder(Protocol):
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Return a list-of-list float embeddings for the input texts."""


class DummyEmbedder:
    """Simple embedder for tests/dev: returns zero vectors of length 1536."""

    def __init__(self, dim: int = 1536):
        self.dim = dim

    async def embed(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * self.dim for _ in texts]


async def compute_and_store_embedding(db: AsyncSession, document_id: int, embedder: Embedder) -> Document:
    """Compute embedding for a document and persist it on the `embedding` column."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalars().first()
    if doc is None:
        raise ValueError(f"document {document_id} not found")

    vectors = await embedder.embed([doc.content or ""])
    if not vectors or not isinstance(vectors[0], list):
        raise ValueError("embedder returned invalid vectors")

    doc.embedding = vectors[0]
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def semantic_search(db: AsyncSession, query_vector: List[float], top_k: int = 5) -> List[Tuple[Document, float]]:
    """Perform a simple in-memory similarity search over `documents.embedding`.

    This works with `embedding` stored as JSONB (list of floats) or as a pgvector column.
    When pgvector is available you should replace this with a DB-side nearest-neighbor query.
    Returns list of (Document, score) ordered by descending similarity (cosine).
    """

    result = await db.execute(select(Document).where(Document.embedding != None))
    docs = result.scalars().all()
    if not docs:
        return []

    q = np.array(query_vector, dtype=float)
    q_norm = np.linalg.norm(q)
    scores = []
    for d in docs:
        emb = d.embedding
        if emb is None:
            continue
        try:
            v = np.array(emb, dtype=float)
        except Exception:
            continue
        denom = (np.linalg.norm(v) * q_norm)
        score = float(np.dot(q, v) / denom) if denom > 0 else 0.0
        scores.append((d, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]

