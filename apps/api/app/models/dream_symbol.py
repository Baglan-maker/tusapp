import uuid

from sqlalchemy import Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DreamSymbol(Base):
    """Association between a dream and a symbol, with salience (0-1)."""

    __tablename__ = "dream_symbols"

    dream_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dreams.id", ondelete="CASCADE"), primary_key=True
    )
    symbol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("symbols.id", ondelete="CASCADE"), primary_key=True
    )
    salience: Mapped[float | None] = mapped_column(Float)
