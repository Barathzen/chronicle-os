from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import jwt

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Use a pure-Python compatible scheme by default to avoid C-extension
# dependency issues in test/dev environments. Production can switch to bcrypt.
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
	now = datetime.utcnow()
	if expires_delta:
		expire = now + expires_delta
	else:
		expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	to_encode = {"sub": subject, "exp": expire}
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt
