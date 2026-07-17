import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, SmallInteger, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class UsageQuota(Base):
    """Per-day free-tier usage, counted on the backend. Composite PK (user_id, day)."""

    __tablename__ = "usage_quota"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    interpretations_used: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )
    transcriptions_used: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )
    chat_questions_used: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )
