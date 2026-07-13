import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ShareCard(Base):
    __tablename__ = "share_cards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    dream_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dreams.id", ondelete="CASCADE"), nullable=False
    )
    template: Mapped[str | None] = mapped_column(String)
    image_url: Mapped[str | None] = mapped_column(Text)
    # Null until actually shared — the K-factor / virality metric.
    shared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
