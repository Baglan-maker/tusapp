import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.deps import current_user_id
from app.models.profile import Profile
from app.models.user import User
from app.prompts import Lens
from app.ratelimit import limiter
from app.schemas.profile import ProfileOut, ProfileUpdate
from app.services.users import ensure_user

router = APIRouter(prefix="/profile", tags=["profile"])

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[uuid.UUID, Depends(current_user_id)]

DEFAULT_LENS = Lens.psych
DEFAULT_TIMEZONE = "Asia/Almaty"


@router.get("", response_model=ProfileOut)
@limiter.limit(settings.rate_limit)
def get_profile(request: Request, session: SessionDep, user_id: UserDep) -> ProfileOut:
    """The onboarding gate reads this. A user with no profile row yet gets
    defaults with onboarding_completed=false — never a 404."""
    ensure_user(session, user_id)
    session.commit()
    return _read(session, user_id)


@router.put("", response_model=ProfileOut)
@limiter.limit(settings.rate_limit)
def update_profile(
    request: Request,
    session: SessionDep,
    user_id: UserDep,
    payload: ProfileUpdate,
) -> ProfileOut:
    ensure_user(session, user_id)

    if payload.locale is not None:
        session.execute(update(User).where(User.id == user_id).values(locale=payload.locale))

    profile = session.get(Profile, user_id)
    if profile is None:
        profile = Profile(user_id=user_id)
        session.add(profile)
        session.flush()

    if payload.default_lens is not None:
        profile.default_lens = payload.default_lens.value
    if payload.timezone is not None:
        profile.timezone = payload.timezone
    if payload.push_enabled is not None:
        profile.push_enabled = payload.push_enabled
    # wake_time is nullable on purpose: null == "по-разному".
    if "wake_time" in payload.model_fields_set:
        profile.wake_time = payload.wake_time
    if payload.onboarding_completed is not None:
        profile.onboarding = {
            **(profile.onboarding or {}),
            "completed": payload.onboarding_completed,
        }

    session.commit()
    return _read(session, user_id)


def _read(session: Session, user_id: uuid.UUID) -> ProfileOut:
    locale = session.scalar(select(User.locale).where(User.id == user_id)) or "ru"
    profile = session.get(Profile, user_id)
    if profile is None:
        return ProfileOut(
            locale=locale,
            default_lens=DEFAULT_LENS,
            wake_time=None,
            timezone=DEFAULT_TIMEZONE,
            push_enabled=True,
            onboarding_completed=False,
        )
    return ProfileOut(
        locale=locale,
        default_lens=Lens(profile.default_lens),
        wake_time=profile.wake_time,
        timezone=profile.timezone,
        push_enabled=profile.push_enabled,
        onboarding_completed=bool((profile.onboarding or {}).get("completed", False)),
    )
