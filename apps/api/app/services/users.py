"""User row bootstrap.

`users.id` is the Supabase JWT `sub`. The row is created lazily on the user's
first authenticated write so the FKs hold.
"""

import uuid

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.user import User


def ensure_user(session: Session, user_id: uuid.UUID, locale: str = "ru") -> None:
    session.execute(
        insert(User)
        .values(id=user_id, locale=locale)
        .on_conflict_do_nothing(index_elements=[User.id])
    )
    session.flush()
