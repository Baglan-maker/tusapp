import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.models.dream import Dream
from app.models.user import User
from app.prompts import Lens
from app.schemas.dream import (
    DreamCreateOut,
    InterpretationOut,
    TranscriptOut,
    TranscriptUpdate,
)
from app.services import pipeline, stt

router = APIRouter(prefix="/dreams", tags=["dreams"])

Language = Literal["ru", "kk"]


@router.post("", response_model=DreamCreateOut)
def create_dream(
    session: Annotated[Session, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Form()],
    language: Annotated[Language, Form()],
    text: Annotated[str | None, Form()] = None,
    audio: Annotated[UploadFile | None, File()] = None,
) -> DreamCreateOut:
    """Create a dream from either a finished transcript or an audio recording.

    Audio is transcribed (ru->Groq, kk->ElevenLabs) and then discarded — we
    persist only the transcript. The client shows it for editing before interpret.
    """
    has_text = bool(text and text.strip())
    if has_text == (audio is not None):
        raise HTTPException(422, "provide exactly one of `text` or `audio`")

    if audio is not None:
        data = audio.file.read()
        if len(data) > settings.max_upload_bytes:
            raise HTTPException(413, "audio file too large")
        transcript = stt.transcribe(data, audio.filename or "audio.m4a", language)
    else:
        assert text is not None
        transcript = text.strip()

    _ensure_user(session, user_id, language)
    dream = Dream(user_id=user_id, transcript=transcript, language=language)
    session.add(dream)
    session.commit()
    session.refresh(dream)
    return DreamCreateOut(dream_id=dream.id, transcript=dream.transcript, language=dream.language)


@router.patch("/{dream_id}/transcript", response_model=TranscriptOut)
def update_transcript(
    session: Annotated[Session, Depends(get_session)],
    dream_id: uuid.UUID,
    payload: TranscriptUpdate,
) -> TranscriptOut:
    dream = _get_dream(session, dream_id)
    dream.transcript = payload.transcript
    session.commit()
    return TranscriptOut(dream_id=dream.id, transcript=payload.transcript)


@router.post("/{dream_id}/interpret", response_model=InterpretationOut)
def interpret(
    session: Annotated[Session, Depends(get_session)],
    dream_id: uuid.UUID,
    lens: Annotated[Lens, Query()],
) -> InterpretationOut:
    dream = _get_dream(session, dream_id)
    if not dream.transcript:
        raise HTTPException(400, "dream has no transcript yet")
    interpretation = pipeline.interpret_dream(session, dream, lens)
    return InterpretationOut.model_validate(interpretation)


def _get_dream(session: Session, dream_id: uuid.UUID) -> Dream:
    dream = session.scalar(select(Dream).where(Dream.id == dream_id, Dream.deleted_at.is_(None)))
    if dream is None:
        raise HTTPException(404, "dream not found")
    return dream


def _ensure_user(session: Session, user_id: uuid.UUID, language: str) -> None:
    """Upsert a bare user row so the dream FK holds (auth arrives next slice)."""
    session.execute(
        insert(User)
        .values(id=user_id, locale=language)
        .on_conflict_do_nothing(index_elements=[User.id])
    )
    session.flush()
