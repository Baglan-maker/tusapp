import uuid
from typing import Any

from sqlalchemy import String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Symbol(Base):
    __tablename__ = "symbols"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # Localized display names, e.g. {"ru": "вода", "kk": "су"}.
    names: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # Base meanings per lens, e.g. {"psych": "...", "classic": "...", ...}.
    lens_meanings: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
