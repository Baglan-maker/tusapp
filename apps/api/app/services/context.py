"""Builds the user-history context injected into the interpretation prompt.

This is the anti-"same interpretation every time" lever: the interpreter sees
the user's last few dreams and active patterns and is told to reference them.
"""

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dream import Dream
from app.models.pattern import Pattern

RECENT_LIMIT = 5
SUMMARY_CHARS = 200


@dataclass
class DreamContext:
    recent_block: str
    patterns_block: str


def build_context(
    session: Session, user_id: uuid.UUID, *, exclude_dream_id: uuid.UUID
) -> DreamContext:
    recent = session.scalars(
        select(Dream)
        .where(
            Dream.user_id == user_id,
            Dream.deleted_at.is_(None),
            Dream.id != exclude_dream_id,
            Dream.transcript.is_not(None),
        )
        .order_by(Dream.recorded_at.desc())
        .limit(RECENT_LIMIT)
    ).all()
    recent_lines = [f"- {_summarize(d.transcript)}" for d in recent if d.transcript]

    patterns = session.scalars(
        select(Pattern)
        .where(Pattern.user_id == user_id)
        .order_by(Pattern.occurrences.desc())
        .limit(RECENT_LIMIT)
    ).all()
    pattern_lines = [f"- {p.description} (×{p.occurrences})" for p in patterns if p.description]

    return DreamContext(
        recent_block="\n".join(recent_lines),
        patterns_block="\n".join(pattern_lines),
    )


def _summarize(transcript: str) -> str:
    text = " ".join(transcript.split())
    if len(text) <= SUMMARY_CHARS:
        return text
    return text[:SUMMARY_CHARS].rstrip() + "…"
