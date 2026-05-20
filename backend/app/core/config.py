import os
from dotenv import load_dotenv
from typing import Any

load_dotenv()

def get_env(name: str, default: Any = None) -> Any:
    return os.getenv(name, default)


SECRET_KEY: str = get_env("SECRET_KEY", "change-me-please")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ALGORITHM: str = get_env("ALGORITHM", "HS256")
DATABASE_URL: str = get_env("DATABASE_URL")
REDIS_URL: str = get_env("REDIS_URL", "redis://localhost:6379/0")
