import pytest

from app.db.database import AsyncSessionLocal
from app.models.document import Document
from app.services.embeddings.service import compute_and_store_embedding, DummyEmbedder, semantic_search


@pytest.mark.asyncio
async def test_integration_compute_and_search():
    async with AsyncSessionLocal() as session:
        # create a document
        doc = Document(title="Integration Doc", content="The quick brown fox jumps over the lazy dog")
        session.add(doc)
        await session.commit()
        await session.refresh(doc)

        # compute embedding with dummy embedder
        dummy = DummyEmbedder(dim=16)
        updated = await compute_and_store_embedding(session, doc.id, dummy)
        assert updated.embedding is not None
        assert len(updated.embedding) == 16

        # semantic search should return the doc when searching with same vector
        results = await semantic_search(session, updated.embedding, top_k=3)
        assert len(results) >= 1
        top_doc, score = results[0]
        # instance identity may differ across sessions; assert same title
        assert top_doc.title == updated.title
