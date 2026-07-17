"""Regressions from the audit: idempotent interpret, transcription quota + length."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usage_quota import UsageQuota
from tests.conftest import auth_headers


def _text_dream(client: TestClient, user_id: uuid.UUID) -> uuid.UUID:
    resp = client.post(
        "/dreams",
        data={"language": "ru", "text": "мне снилась вода"},
        headers=auth_headers(user_id),
    )
    assert resp.status_code == 200, resp.text
    return uuid.UUID(resp.json()["dream_id"])


def _audio_dream(client: TestClient, user_id: uuid.UUID):  # type: ignore[no-untyped-def]
    return client.post(
        "/dreams",
        data={"language": "kk"},
        files={"audio": ("dream.m4a", b"\x00\x01\x02", "audio/m4a")},
        headers=auth_headers(user_id),
    )


def _interpret(client: TestClient, dream_id: uuid.UUID, user_id: uuid.UUID):  # type: ignore[no-untyped-def]
    return client.post(
        f"/dreams/{dream_id}/interpret",
        params={"lens": "psych"},
        headers=auth_headers(user_id),
    )


# --- idempotent interpret (the retention-critical one) ---------------------


def test_reopening_own_interpretation_is_free_and_stable(
    client: TestClient, db_session: Session
) -> None:
    user_id = uuid.uuid4()
    dream_id = _text_dream(client, user_id)

    first = _interpret(client, dream_id, user_id)
    assert first.status_code == 200
    second = _interpret(client, dream_id, user_id)  # remount / refetch / retry
    assert second.status_code == 200

    # Same row, not a fresh generation.
    assert first.json()["id"] == second.json()["id"]

    # And the quota was charged exactly once — the free user is never paywalled
    # out of a result they already have.
    used = db_session.scalar(
        select(UsageQuota.interpretations_used).where(UsageQuota.user_id == user_id)
    )
    assert used == 1


def test_idempotent_interpret_does_not_call_llm_twice(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = {"n": 0}
    import app.services.pipeline as pipeline_mod

    real = pipeline_mod.interpret_dream

    def counting(session, dream, lens):  # type: ignore[no-untyped-def]
        calls["n"] += 1
        return real(session, dream, lens)

    monkeypatch.setattr(pipeline_mod, "interpret_dream", counting)

    user_id = uuid.uuid4()
    dream_id = _text_dream(client, user_id)
    _interpret(client, dream_id, user_id)
    _interpret(client, dream_id, user_id)

    assert calls["n"] == 1  # second call short-circuited to the cached row


def test_embedding_failure_does_not_lose_the_interpretation(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def boom(text: str):  # type: ignore[no-untyped-def]
        raise RuntimeError("OpenAI down")

    monkeypatch.setattr("app.services.embeddings.embed", boom)

    user_id = uuid.uuid4()
    dream_id = _text_dream(client, user_id)
    resp = _interpret(client, dream_id, user_id)
    assert resp.status_code == 200
    assert resp.json()["content_md"]


# --- transcription quota + length -----------------------------------------


def test_free_transcription_allowance_then_402(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "free_daily_transcriptions", 3)

    user_id = uuid.uuid4()
    for _ in range(3):
        assert _audio_dream(client, user_id).status_code == 200

    blocked = _audio_dream(client, user_id)
    assert blocked.status_code == 402
    assert blocked.json()["detail"] == {"reason": "transcription", "paywall": True}


def test_transcription_quota_is_per_user(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "free_daily_transcriptions", 1)
    a, b = uuid.uuid4(), uuid.uuid4()
    assert _audio_dream(client, a).status_code == 200
    assert _audio_dream(client, b).status_code == 200  # b's allowance is its own


def test_audio_over_length_limit_is_rejected(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.services.audio.duration_seconds", lambda data: 999.0)
    resp = _audio_dream(client, uuid.uuid4())
    assert resp.status_code == 413


def test_text_dream_needs_no_transcription_quota(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "free_daily_transcriptions", 0)  # audio blocked outright
    # Text path must be unaffected by the STT meter.
    assert _text_dream(client, uuid.uuid4()) is not None
