"""Free-tier quota accounting for interpretations.

Tier rule: a user is premium only if they have a subscription row in an active
state. **No subscription row at all means FREE, not blocked** — a brand-new user
gets today's free allowance immediately.
"""

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import settings
from app.models.subscription import Subscription
from app.models.usage_quota import UsageQuota

PREMIUM_STATUSES = ("trial", "active", "grace")


class QuotaExceeded(Exception):
    """The free user has used up today's interpretations."""


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


def interpretations_used_today(session: Session, user_id: uuid.UUID) -> int:
    used = session.scalar(
        select(UsageQuota.interpretations_used).where(
            UsageQuota.user_id == user_id, UsageQuota.day == _today()
        )
    )
    return used or 0


def check_interpretation_quota(session: Session, user_id: uuid.UUID) -> None:
    """Raise QuotaExceeded if a free user already spent today's allowance.

    Premium users are unlimited. A user with no subscription row is free.
    """
    if is_premium(session, user_id):
        return
    if interpretations_used_today(session, user_id) >= settings.free_daily_interpretations:
        raise QuotaExceeded()


def consume_interpretation(session: Session, user_id: uuid.UUID) -> None:
    """Count one interpretation against today's quota, after it succeeded.

    Deliberately check-then-consume: two concurrent requests could both pass the
    check, costing at most one extra interpretation. If post-launch analytics
    show abuse, swap this for an atomic reserve (INSERT ... ON CONFLICT DO
    UPDATE ... RETURNING, reject when over limit) plus a refund on failure —
    the call sites in the router do not change.
    """
    session.execute(
        insert(UsageQuota)
        .values(user_id=user_id, day=_today(), interpretations_used=1)
        .on_conflict_do_update(
            index_elements=[UsageQuota.user_id, UsageQuota.day],
            set_={"interpretations_used": UsageQuota.interpretations_used + 1},
        )
    )
    session.commit()
