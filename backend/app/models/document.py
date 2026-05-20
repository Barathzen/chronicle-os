from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # `metadata` is a reserved attribute name on Declarative base; store in DB column `metadata`
    metadata_ = Column('metadata', JSON, nullable=True)
    # embedding stored as JSON list by default; can be migrated to pgvector later
    embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="documents")

    # Note: do NOT define an attribute named `metadata` on the class level
    # because SQLAlchemy's declarative base expects `metadata` to be the
    # MetaData object. Use the `metadata_` attribute for storage and map
    # to `metadata` in serializers or response models.
