"""Auth isolation and free-tier quota — the two things that must not regress."""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from tests.conftest import auth_headers


def _create_dream(client: TestClient, user_id: uuid.UUID) -> uuid.UUID:
    resp = client.post(
        "/dreams",
        data={"language": "ru", "text": "мне снилась вода"},
        headers=auth_headers(user_id),
    )
    assert resp.status_code == 200, resp.text
    return uuid.UUID(resp.json()["dream_id"])


def _interpret(client: TestClient, dream_id: uuid.UUID, user_id: uuid.UUID):  # type: ignore[no-untyped-def]
    return client.post(
        f"/dreams/{dream_id}/interpret",
        params={"lens": "psych"},
        headers=auth_headers(user_id),
    )


# --- auth ------------------------------------------------------------------


def test_no_token_is_401(client: TestClient) -> None:
    resp = client.post("/dreams", data={"language": "ru", "text": "сон"})
    assert resp.status_code == 401


def test_garbage_token_is_401(client: TestClient) -> None:
    resp = client.post(
        "/dreams",
        data={"language": "ru", "text": "сон"},
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert resp.status_code == 401


def test_health_stays_public(client: TestClient) -> None:
    assert client.get("/health").status_code == 200


# --- user isolation --------------------------------------------------------


def test_user_b_cannot_read_or_interpret_user_a_dream(client: TestClient) -> None:
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    dream_id = _create_dream(client, user_a)

    # B tries to edit A's transcript
    resp = client.patch(
        f"/dreams/{dream_id}/transcript",
        json={"transcript": "взлом"},
        headers=auth_headers(user_b),
    )
    assert resp.status_code == 404  # not 403 — we don't leak that it exists

    # B tries to interpret A's dream
    assert _interpret(client, dream_id, user_b).status_code == 404

    # A still can
    assert _interpret(client, dream_id, user_a).status_code == 200


# --- quota -----------------------------------------------------------------


def test_fresh_user_without_subscription_row_gets_one_free_interpretation(
    client: TestClient, db_session: Session
) -> None:
    """No subscriptions row must mean FREE (1/day), not blocked (0/day)."""
    user_id = uuid.uuid4()
    dream_id = _create_dream(client, user_id)

    # Precondition: this user genuinely has no subscription row.
    assert (
        db_session.scalar(
            select(func.count()).select_from(Subscription).where(Subscription.user_id == user_id)
        )
        == 0
    )

    resp = _interpret(client, dream_id, user_id)
    assert resp.status_code == 200, resp.text


def test_second_interpretation_same_day_is_402_with_paywall(client: TestClient) -> None:
    user_id = uuid.uuid4()
    first = _create_dream(client, user_id)
    second = _create_dream(client, user_id)

    assert _interpret(client, first, user_id).status_code == 200

    resp = _interpret(client, second, user_id)
    assert resp.status_code == 402
    assert resp.json()["detail"] == {"reason": "quota", "paywall": True}


def test_quota_is_per_user_not_global(client: TestClient) -> None:
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    dream_a = _create_dream(client, user_a)
    dream_b = _create_dream(client, user_b)

    assert _interpret(client, dream_a, user_a).status_code == 200
    # B's free interpretation must not be eaten by A's.
    assert _interpret(client, dream_b, user_b).status_code == 200
