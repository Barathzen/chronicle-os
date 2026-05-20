from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.document import DocumentCreate, DocumentOut, DocumentUpdate
from app.services.documents.service import (
    create_document,
    get_document,
    list_documents,
    update_document,
    delete_document,
)

router = APIRouter()


def _serialize_doc(doc) -> dict:
    return {
        "id": doc.id,
        "title": doc.title,
        "content": doc.content,
        "owner_id": doc.owner_id,
        "metadata": getattr(doc, "metadata_") if hasattr(doc, "metadata_") else None,
        "created_at": doc.created_at.isoformat() if getattr(doc, "created_at", None) is not None else None,
    }


@router.post("/", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def create(doc_in: DocumentCreate, db: AsyncSession = Depends(get_db)):
    doc = await create_document(db, doc_in.title, doc_in.content, None, doc_in.metadata)
    return _serialize_doc(doc)


@router.get("/", response_model=List[DocumentOut])
async def list_docs(owner_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    docs = await list_documents(db, owner_id)
    return [_serialize_doc(d) for d in docs]


@router.get("/{doc_id}", response_model=DocumentOut)
async def read_doc(doc_id: int, db: AsyncSession = Depends(get_db)):
    doc = await get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _serialize_doc(doc)


@router.put("/{doc_id}", response_model=DocumentOut)
async def update_doc(doc_id: int, doc_in: DocumentUpdate, db: AsyncSession = Depends(get_db)):
    data = {k: v for k, v in doc_in.model_dump().items() if v is not None}
    doc = await update_document(db, doc_id, data)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _serialize_doc(doc)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_doc(doc_id: int, db: AsyncSession = Depends(get_db)):
    await delete_document(db, doc_id)
    return None
