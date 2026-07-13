import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Streak(Base):
    __tablename__ = "streaks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    current: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    longest: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    last_entry_date: Mapped[date | None] = mapped_column(Date)
