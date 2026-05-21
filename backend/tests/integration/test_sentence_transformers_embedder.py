import pytest

from app.db.database import AsyncSessionLocal
from app.models.document import Document
from app.services.embeddings.service import compute_and_store_embedding, semantic_search

try:
    from app.services.embeddings.adapters import SentenceTransformersEmbedder
except Exception:
    SentenceTransformersEmbedder = None


@pytest.mark.asyncio
async def test_sentence_transformers_embedder_integration():
    if SentenceTransformersEmbedder is None:
        pytest.skip("sentence-transformers not installed; skipping integration test")

    async with AsyncSessionLocal() as session:
        # create a document
        doc = Document(title="ST Integration Doc", content="Embeddings with sentence-transformers test.")
        session.add(doc)
        await session.commit()
        await session.refresh(doc)

        # instantiate local embedder (CPU)
        embedder = SentenceTransformersEmbedder(device="cpu")

        # compute and store embedding
        updated = await compute_and_store_embedding(session, doc.id, embedder)
        assert updated.embedding is not None
        assert isinstance(updated.embedding, list)
        assert len(updated.embedding) > 0

        # run semantic search using the stored vector
        results = await semantic_search(session, updated.embedding, top_k=3)
        assert isinstance(results, list)
        # should find at least one result (the doc itself)
        assert any(r[0].id == updated.id for r in results)
