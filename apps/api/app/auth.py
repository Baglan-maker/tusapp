"""Auth helpers.

Full Supabase JWT verification arrives with the auth slice. For now this
module holds the one invariant we already agreed on: when we upsert a user
from JWT claims, a missing or empty ``sub`` must be rejected.
"""

from typing import Any


class InvalidTokenError(ValueError):
    """Raised when JWT claims are unusable (e.g. empty subject)."""


def require_sub(claims: dict[str, Any]) -> str:
    """Return the Supabase user id (``sub``) or raise if it is missing/empty.

    ``sub`` is the stable user identifier; an empty value must never be used
    to key a user row.
    """
    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub.strip():
        raise InvalidTokenError("JWT 'sub' claim is missing or empty")
    return sub
