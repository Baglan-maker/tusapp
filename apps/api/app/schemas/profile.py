from datetime import time
from typing import Literal

from pydantic import BaseModel

from app.prompts import Lens

Locale = Literal["ru", "kk"]


class ProfileOut(BaseModel):
    locale: str
    default_lens: Lens
    # None means "по-разному" — the user has no fixed wake time.
    wake_time: time | None
    timezone: str
    push_enabled: bool
    onboarding_completed: bool


class ProfileUpdate(BaseModel):
    """Partial update — onboarding writes these one step at a time."""

    locale: Locale | None = None
    default_lens: Lens | None = None
    wake_time: time | None = None
    timezone: str | None = None
    push_enabled: bool | None = None
    onboarding_completed: bool | None = None
