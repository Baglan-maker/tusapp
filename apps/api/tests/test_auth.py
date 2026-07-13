import pytest

from app.auth import InvalidTokenError, require_sub


def test_require_sub_returns_subject() -> None:
    assert require_sub({"sub": "user-123"}) == "user-123"


@pytest.mark.parametrize("claims", [{}, {"sub": ""}, {"sub": "   "}, {"sub": None}])
def test_require_sub_rejects_empty(claims: dict) -> None:
    with pytest.raises(InvalidTokenError):
        require_sub(claims)
