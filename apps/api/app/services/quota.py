"""Free-tier quota accounting.

Two separate meters, because they cost differently and abuse differently:
- interpretations (LLM $) — the product limit, 1/day free.
- transcriptions (STT $) — an anti-abuse cap, 5/day free.

Tier rule: a user is premium only if they have a subscription row in an active
state. **No subscription row at all means FREE, not blocked** — a brand-new user
gets today's free allowance immediately.
"""

import uuid
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import settings
from app.models.subscription import Subscription
from app.models.usage_quota import UsageQuota

PREMIUM_STATUSES = ("trial", "active", "grace")


class QuotaExceeded(Exception):
    """A free user has used up today's allowance for `reason`."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


def _today() -> date:
    # UTC day for now; switch to the user's profile timezone when we surface
    # streaks (profiles.timezone already exists).
    return datetime.now(UTC).date()


def is_premium(session: Session, user_id: uuid.UUID) -> bool:
    subscription = session.scalar(
        select(Subscription.id).where(
            Subscription.user_id == user_id,
            Subscription.status.in_(PREMIUM_STATUSES),
        )
    )
    return subscription is not None


def _used_today(session: Session, user_id: uuid.UUID, column: Any) -> int:
    used = session.scalar(
        select(column).where(UsageQuota.user_id == user_id, UsageQuota.day == _today())
    )
    return used or 0


def _consume(session: Session, user_id: uuid.UUID, field: str) -> None:
    counter = getattr(UsageQuota, field)
    session.execute(
        insert(UsageQuota)
        .values(user_id=user_id, day=_today(), **{field: 1})
        .on_conflict_do_update(
            index_elements=[UsageQuota.user_id, UsageQuota.day],
            set_={field: counter + 1},
        )
    )


# --- interpretations (LLM) -------------------------------------------------


def check_interpretation_quota(session: Session, user_id: uuid.UUID) -> None:
    if is_premium(session, user_id):
        return
    if _used_today(session, user_id, UsageQuota.interpretations_used) >= (
        settings.free_daily_interpretations
    ):
        raise QuotaExceeded("quota")


def consume_interpretation(session: Session, user_id: uuid.UUID) -> None:
    """Count one interpretation, after it succeeded (check-then-consume).

    Two concurrent requests could both pass the check, costing at most one extra.
    If analytics show abuse, swap for an atomic reserve (INSERT ... ON CONFLICT
    ... RETURNING, reject when over) + refund on failure — the router does not change.
    """
    _consume(session, user_id, "interpretations_used")
    session.commit()


# --- transcriptions (STT) --------------------------------------------------


def check_transcription_quota(session: Session, user_id: uuid.UUID) -> None:
    if is_premium(session, user_id):
        return
    if _used_today(session, user_id, UsageQuota.transcriptions_used) >= (
        settings.free_daily_transcriptions
    ):
        raise QuotaExceeded("transcription")


def consume_transcription(session: Session, user_id: uuid.UUID) -> None:
    """Count one transcription. Flush only — the caller commits it together with
    the dream it belongs to."""
    _consume(session, user_id, "transcriptions_used")
    session.flush()
