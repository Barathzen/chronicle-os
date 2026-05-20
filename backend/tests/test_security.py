from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import SECRET_KEY
from jose import jwt


def test_password_hash_and_verify():
    password = "s3cret"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_create_access_token_contains_sub():
    token = create_access_token(subject="123")
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert payload.get("sub") == "123"
