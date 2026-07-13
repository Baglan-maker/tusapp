import uuid

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DreamEmotion(Base):
    """Emotion tagged on a dream, either felt in the dream or on waking."""

    __tablename__ = "dream_emotions"
    __table_args__ = (
        CheckConstraint("kind in ('in_dream','on_waking')", name="ck_dream_emotions_kind"),
    )

    dream_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dreams.id", ondelete="CASCADE"), primary_key=True
    )
    emotion_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("emotions.id", ondelete="CASCADE"), primary_key=True
    )
    kind: Mapped[str] = mapped_column(primary_key=True)
