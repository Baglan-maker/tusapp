import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

# OpenAI text-embedding-3-small dimensionality.
EMBEDDING_DIM = 1536


class DreamEmbedding(Base):
    __tablename__ = "dream_embeddings"

    dream_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dreams.id", ondelete="CASCADE"), primary_key=True
    )
    embedding: Mapped[Any] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
