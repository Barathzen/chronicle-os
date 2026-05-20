import pytest
from fastapi.testclient import TestClient

from app.main import app
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
    def __init__(self):
        self.docs = []
        self._next_id = 1

    async def execute(self, stmt):
        s = str(stmt)
        if "WHERE" in s and "id" in s:
            # extract id from stmt string rough heuristic
            # return first doc for unit tests
            return FakeResult([self.docs[0]]) if self.docs else FakeResult([])
        return FakeResult(self.docs)

    async def commit(self):
        return None

    async def refresh(self, obj):
        return None

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self._next_id
            self._next_id += 1
        # replace if exists
        for i, d in enumerate(self.docs):
            if d.id == obj.id:
                self.docs[i] = obj
                return
        self.docs.append(obj)


@pytest.fixture
def client():
    return TestClient(app)


def override_get_db_fake():
    session = FakeAsyncSession()

    async def _get_db():
        yield session

    return _get_db


def test_documents_crud_flow(client):
    app.dependency_overrides[get_db] = override_get_db_fake()

    # create
    r = client.post("/documents/", json={"title": "Doc1", "content": "abc", "metadata": {}})
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Doc1"
    doc_id = data["id"]

    # read
    r2 = client.get(f"/documents/{doc_id}")
    assert r2.status_code == 200

    # list
    r3 = client.get("/documents/")
    assert r3.status_code == 200
    assert isinstance(r3.json(), list)

    # update
    r4 = client.put(f"/documents/{doc_id}", json={"title": "Doc1 Updated"})
    assert r4.status_code == 200
    assert r4.json()["title"] == "Doc1 Updated"

    # delete
    r5 = client.delete(f"/documents/{doc_id}")
    assert r5.status_code == 204
