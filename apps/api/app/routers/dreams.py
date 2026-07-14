import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.deps import current_user_id
from app.models.dream import Dream
from app.prompts import Lens
from app.ratelimit import limiter
from app.schemas.dream import (
    DreamCreateOut,
    InterpretationOut,
    TranscriptOut,
    TranscriptUpdate,
)
from app.services import emotions, pipeline, quota, stt
from app.services.users import ensure_user

router = APIRouter(prefix="/dreams", tags=["dreams"])

Language = Literal["ru", "kk"]

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[uuid.UUID, Depends(current_user_id)]


@router.post("", response_model=DreamCreateOut)
@limiter.limit(settings.rate_limit)
def create_dream(
    request: Request,
    session: SessionDep,
    user_id: UserDep,
    language: Annotated[Language, Form()],
    text: Annotated[str | None, Form()] = None,
    audio: Annotated[UploadFile | None, File()] = None,
    # The two chip rows shown right after recording. Comma-separated slugs —
    # multipart has no native list type.
    emotions_in_dream: Annotated[str | None, Form()] = None,
    emotions_on_waking: Annotated[str | None, Form()] = None,
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

    ensure_user(session, user_id, language)
    dream = Dream(user_id=user_id, transcript=transcript, language=language)
    session.add(dream)
    session.flush()

    emotions.attach(session, dream.id, emotions.parse_slugs(emotions_in_dream), "in_dream")
    emotions.attach(session, dream.id, emotions.parse_slugs(emotions_on_waking), "on_waking")

    session.commit()
    session.refresh(dream)
    return DreamCreateOut(dream_id=dream.id, transcript=dream.transcript, language=dream.language)


@router.patch("/{dream_id}/transcript", response_model=TranscriptOut)
@limiter.limit(settings.rate_limit)
def update_transcript(
    request: Request,
    session: SessionDep,
    user_id: UserDep,
    dream_id: uuid.UUID,
    payload: TranscriptUpdate,
) -> TranscriptOut:
    dream = _get_own_dream(session, dream_id, user_id)
    dream.transcript = payload.transcript
    session.commit()
    return TranscriptOut(dream_id=dream.id, transcript=payload.transcript)


@router.post("/{dream_id}/interpret", response_model=InterpretationOut)
@limiter.limit(settings.rate_limit)
def interpret(
    request: Request,
    session: SessionDep,
    user_id: UserDep,
    dream_id: uuid.UUID,
    lens: Annotated[Lens, Query()],
) -> InterpretationOut:
    dream = _get_own_dream(session, dream_id, user_id)
    if not dream.transcript:
        raise HTTPException(400, "dream has no transcript yet")

    try:
        quota.check_interpretation_quota(session, user_id)
    except quota.QuotaExceeded:
        raise HTTPException(402, detail={"reason": "quota", "paywall": True}) from None

    interpretation = pipeline.interpret_dream(session, dream, lens)
    quota.consume_interpretation(session, user_id)
    return InterpretationOut.model_validate(interpretation)


def _get_own_dream(session: Session, dream_id: uuid.UUID, user_id: uuid.UUID) -> Dream:
    """Fetch a dream owned by this user. Someone else's dream 404s — we do not
    leak its existence."""
    dream = session.scalar(
        select(Dream).where(
            Dream.id == dream_id,
            Dream.user_id == user_id,
            Dream.deleted_at.is_(None),
        )
    )
    if dream is None:
        raise HTTPException(404, "dream not found")
    return dream
