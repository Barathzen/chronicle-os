import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.embeddings.service import DummyEmbedder
from app.db.database import get_db
from app.models.document import Document


class FakeResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def first(self):
        return self._items[0] if self._items else None

    def all(self):
        return self._items


class FakeAsyncSession:
    def __init__(self, docs):
        self.docs = docs

    async def execute(self, stmt):
        # simple behavior: if stmt contains "WHERE", return first doc, else return all with embeddings
        if "WHERE" in str(stmt):
            return FakeResult([self.docs[0]])
        return FakeResult(self.docs)

    async def commit(self):
        return None

    async def refresh(self, obj):
        return None

    def add(self, obj):
        # mutate back into docs if matching id
        for i, d in enumerate(self.docs):
            if d.id == obj.id:
                self.docs[i] = obj
                return


@pytest.fixture
def client():
    return TestClient(app)


def override_get_db_with_doc(doc):
    async def _get_db():
        yield FakeAsyncSession([doc])

    return _get_db


def override_get_embedder_dummy():
    async def _get():
        return DummyEmbedder(dim=4)

    return _get


def test_dummy_embedder():
    d = DummyEmbedder(dim=8)
    import asyncio
    res = asyncio.run(d.embed(["a", "b"]))
    assert len(res) == 2
    assert len(res[0]) == 8


def test_embed_and_search_endpoints(client):
    # prepare a fake document
    doc = Document(id=1, title="T1", content="hello world")

    app.dependency_overrides[get_db] = override_get_db_with_doc(doc)
    from app.api.routes.embeddings import get_embedder

    app.dependency_overrides[get_embedder] = override_get_embedder_dummy()

    r = client.post("/documents/1/embed")
    assert r.status_code == 200
    assert r.json()["id"] == 1

    # test search
    r2 = client.post("/search", json={"query": "hello", "top_k": 1})
    assert r2.status_code == 200
    assert isinstance(r2.json(), list)
