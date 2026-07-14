"""Emotion tagging.

Two writers land in `dream_emotions`: the user's own chips picked right after
recording, and the LLM's extraction. Both upsert, so they coexist.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.dream_emotion import DreamEmotion
from app.models.emotion import Emotion

KINDS = ("in_dream", "on_waking")


def get_or_create_emotion(session: Session, slug: str) -> int:
    existing = session.scalar(select(Emotion.id).where(Emotion.slug == slug))
    if existing is not None:
        return existing
    session.execute(
        insert(Emotion).values(slug=slug).on_conflict_do_nothing(index_elements=[Emotion.slug])
    )
    session.flush()
    emotion_id = session.scalar(select(Emotion.id).where(Emotion.slug == slug))
    assert emotion_id is not None
    return emotion_id


def attach(session: Session, dream_id: uuid.UUID, slugs: list[str], kind: str) -> None:
    """Tag a dream with emotions of one kind ('in_dream' or 'on_waking')."""
    assert kind in KINDS
    for slug in slugs:
        emotion_id = get_or_create_emotion(session, slug)
        session.execute(
            insert(DreamEmotion)
            .values(dream_id=dream_id, emotion_id=emotion_id, kind=kind)
            .on_conflict_do_nothing(
                index_elements=[
                    DreamEmotion.dream_id,
                    DreamEmotion.emotion_id,
                    DreamEmotion.kind,
                ]
            )
        )
    session.flush()


def parse_slugs(raw: str | None) -> list[str]:
    """Form fields arrive as 'fear,anxiety' (multipart has no native lists)."""
    if not raw:
        return []
    return [slug.strip() for slug in raw.split(",") if slug.strip()]
