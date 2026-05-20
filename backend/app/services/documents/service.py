from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document


async def create_document(db: AsyncSession, title: str, content: str | None, owner_id: int | None, metadata: dict | None) -> Document:
    doc = Document(title=title, content=content, owner_id=owner_id, metadata_=metadata)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def get_document(db: AsyncSession, doc_id: int) -> Optional[Document]:
    q = await db.execute(select(Document).where(Document.id == doc_id))
    return q.scalars().first()


async def list_documents(db: AsyncSession, owner_id: Optional[int] = None) -> List[Document]:
    q = select(Document)
    if owner_id is not None:
        q = q.where(Document.owner_id == owner_id)
    res = await db.execute(q)
    return res.scalars().all()


async def update_document(db: AsyncSession, doc_id: int, data: dict) -> Optional[Document]:
    # Fetch, update attributes and commit to ensure compatibility with async sessions and tests
    doc = await get_document(db, doc_id)
    if doc is None:
        return None
    for k, v in data.items():
        # map metadata key to metadata_ column
        if k == "metadata":
            setattr(doc, "metadata_", v)
        else:
            setattr(doc, k, v)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def delete_document(db: AsyncSession, doc_id: int) -> None:
    await db.execute(delete(Document).where(Document.id == doc_id))
    await db.commit()
