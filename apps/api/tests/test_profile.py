"""Profile endpoints — what onboarding writes and what the routing gate reads."""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.dream_emotion import DreamEmotion
from tests.conftest import auth_headers


def test_fresh_user_gets_defaults_not_404(client: TestClient) -> None:
    """The gate must be able to ask 'did you onboard?' before any profile exists."""
    resp = client.get("/profile", headers=auth_headers(uuid.uuid4()))
    assert resp.status_code == 200
    body = resp.json()
    assert body["onboarding_completed"] is False
    assert body["default_lens"] == "psych"
    assert body["wake_time"] is None


def test_onboarding_saves_and_reads_back(client: TestClient) -> None:
    user_id = uuid.uuid4()
    headers = auth_headers(user_id)

    # step 1: language
    assert client.put("/profile", json={"locale": "kk"}, headers=headers).status_code == 200
    # step 2: wake time
    assert client.put("/profile", json={"wake_time": "06:30"}, headers=headers).status_code == 200
    # step 3: lens + done
    resp = client.put(
        "/profile",
        json={"default_lens": "ibn_sirin", "onboarding_completed": True},
        headers=headers,
    )
    assert resp.status_code == 200

    body = client.get("/profile", headers=headers).json()
    assert body["locale"] == "kk"
    assert body["wake_time"] == "06:30:00"
    assert body["default_lens"] == "ibn_sirin"
    assert body["onboarding_completed"] is True


def test_wake_time_can_be_cleared_to_varies(client: TestClient) -> None:
    """'По-разному' is an explicit null, not a missing field."""
    user_id = uuid.uuid4()
    headers = auth_headers(user_id)
    client.put("/profile", json={"wake_time": "07:00"}, headers=headers)

    resp = client.put("/profile", json={"wake_time": None}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["wake_time"] is None


def test_profile_requires_auth(client: TestClient) -> None:
    assert client.get("/profile").status_code == 401


def test_emotion_chips_are_saved_with_the_dream(client: TestClient, db_session: Session) -> None:
    user_id = uuid.uuid4()
    resp = client.post(
        "/dreams",
        data={
            "language": "ru",
            "text": "снилась вода",
            "emotions_in_dream": "fear,anxiety",
            "emotions_on_waking": "peace",
        },
        headers=auth_headers(user_id),
    )
    assert resp.status_code == 200
    dream_id = uuid.UUID(resp.json()["dream_id"])

    rows = db_session.execute(
        select(DreamEmotion.kind, func.count())
        .where(DreamEmotion.dream_id == dream_id)
        .group_by(DreamEmotion.kind)
    ).all()
    counts = dict(rows)
    assert counts["in_dream"] == 2
    assert counts["on_waking"] == 1
