from pydantic import BaseModel
from typing import Optional, Dict, Any


class DocumentCreate(BaseModel):
    title: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    metadata: Optional[Dict[str, Any]]


class DocumentOut(BaseModel):
    id: int
    title: str
    content: Optional[str]
    owner_id: Optional[int]
    metadata: Optional[Dict[str, Any]]
    created_at: Optional[str]

    class Config:
        orm_mode = True
