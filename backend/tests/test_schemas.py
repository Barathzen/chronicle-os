from app.schemas.auth import UserCreate
from app.schemas.document import DocumentCreate


def test_usercreate_validation():
    u = UserCreate(email="test@example.com", password="pass")
    assert u.email == "test@example.com"


def test_documentcreate_optional_fields():
    d = DocumentCreate(title="t")
    assert d.title == "t"
    assert d.content is None
