"""Request-scoped dependencies."""

import uuid

from fastapi import HTTPException, Request


def current_user_id(request: Request) -> uuid.UUID:
    """The authenticated user, put on request.state by the auth middleware.

    Endpoints must take the user id from here — never from a request parameter.
    """
    user_id = getattr(request.state, "user_id", None)
    if not isinstance(user_id, uuid.UUID):
        raise HTTPException(401, "not authenticated")
    return user_id
