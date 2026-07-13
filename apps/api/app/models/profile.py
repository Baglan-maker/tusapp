import uuid
from datetime import time
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, Time, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        CheckConstraint(
            "default_lens in ('psych','classic','ibn_sirin','science')",
            name="ck_profiles_default_lens",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    default_lens: Mapped[str] = mapped_column(String, nullable=False, server_default="psych")
    onboarding: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    push_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    # Wake time drives the morning push; timezone anchors it.
    wake_time: Mapped[time | None] = mapped_column(Time)
    timezone: Mapped[str] = mapped_column(String, nullable=False, server_default="Asia/Almaty")
