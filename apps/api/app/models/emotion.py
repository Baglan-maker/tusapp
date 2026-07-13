from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Emotion(Base):
    """Reference table of emotions (fear, joy, anxiety, ...)."""

    __tablename__ = "emotions"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True)
