from typing import Any
from fastapi import APIRouter, Depends, HTTPException
import os

from app.services.embeddings.service import Embedder
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.embeddings.adapters import OpenAIEmbedder, OllamaEmbedder, SentenceTransformersEmbedder, GroqEmbedder
from app.services.embeddings.service import DummyEmbedder
from app.services.embeddings.service import compute_and_store_embedding, semantic_search


async def get_embedder() -> Embedder:
    try:
        provider = os.getenv("EMBEDDER_PROVIDER", "dummy").lower()
        if provider == "openai":
            return OpenAIEmbedder()
        if provider == "ollama":
            return OllamaEmbedder()
        if provider == "groq":
            return GroqEmbedder()
        if provider == "sentence_transformers" or provider == "sentence-transformers":
            model = os.getenv("SENTENCE_MODEL_NAME", "all-mpnet-base-v2")
            device = os.getenv("TORCH_DEVICE", "cpu")
            return SentenceTransformersEmbedder(model_name=model, device=device)
        # explicit dummy provider support for tests and CI
        if provider == "dummy":
            return DummyEmbedder()

        # default to Ollama if available, else dummy fallback
        try:
            return OllamaEmbedder()
        except Exception:
            return DummyEmbedder()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


router = APIRouter()


class EmbedResponse(BaseModel):
    id: int
    message: str


@router.post("/documents/{doc_id}/embed", response_model=EmbedResponse)
async def embed_document(doc_id: int, db: AsyncSession = Depends(get_db), embedder: Embedder = Depends(get_embedder)) -> Any:
    """Compute embedding for a document using configured provider.

    The endpoint will read `OPENAI_API_KEY` or `OLLAMA_URL` from env to choose provider.
    """
    try:
        doc = await compute_and_store_embedding(db, doc_id, embedder)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"id": doc.id, "message": "embedding stored"}


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchHit(BaseModel):
    id: int
    title: str | None = None
    score: float


@router.post("/search", response_model=list[SearchHit])
async def search(req: SearchRequest, db: AsyncSession = Depends(get_db), embedder: Embedder = Depends(get_embedder)) -> Any:
    q_vecs = await embedder.embed([req.query])
    if not q_vecs:
        raise HTTPException(status_code=500, detail="failed to compute query embedding")

    results = await semantic_search(db, q_vecs[0], top_k=req.top_k)
    return [{"id": d.id, "title": d.title, "score": s} for d, s in results]
