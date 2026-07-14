"""Supabase JWT verification.

The mobile client authenticates with Supabase (Apple/Google/email) and calls
this API with the resulting JWT. We verify it against Supabase's JWKS endpoint
(asymmetric keys, cached) and take `sub` as the user id — that is also the PK
of our own `users` table.
"""

import uuid
from typing import Any

import jwt
from jwt import PyJWKClient

from app.config import settings

ALGORITHMS = ["ES256", "RS256"]


class InvalidTokenError(ValueError):
    """Raised when a JWT is missing, malformed, expired, or has no usable subject."""


_jwks_client: PyJWKClient | None = None


def _jwks() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(
            f"{settings.supabase_url}/auth/v1/.well-known/jwks.json", cache_keys=True
        )
    return _jwks_client


def require_sub(claims: dict[str, Any]) -> str:
    """Return the Supabase user id (``sub``) or raise if it is missing/empty.

    ``sub`` is the stable user identifier; an empty value must never be used
    to key a user row.
    """
    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub.strip():
        raise InvalidTokenError("JWT 'sub' claim is missing or empty")
    return sub


def verify_token(token: str) -> uuid.UUID:
    """Verify a Supabase JWT and return its subject as a UUID."""
    try:
        signing_key = _jwks().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=ALGORITHMS,
            audience=settings.supabase_jwt_audience,
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    sub = require_sub(claims)
    try:
        return uuid.UUID(sub)
    except ValueError as exc:
        raise InvalidTokenError("JWT 'sub' claim is not a UUID") from exc
