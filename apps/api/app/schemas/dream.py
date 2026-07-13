import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DreamCreateOut(BaseModel):
    """Returned by POST /dreams — client shows transcript for editing."""

    dream_id: uuid.UUID
    transcript: str | None
    language: str | None


class TranscriptUpdate(BaseModel):
    transcript: str


class TranscriptOut(BaseModel):
    dream_id: uuid.UUID
    transcript: str


class InterpretationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dream_id: uuid.UUID
    lens: str
    model: str
    content_md: str
    tokens_in: int | None
    tokens_out: int | None
    created_at: datetime
