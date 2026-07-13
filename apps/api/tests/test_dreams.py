import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.dream_embedding import DreamEmbedding
from app.models.dream_emotion import DreamEmotion
from app.models.dream_symbol import DreamSymbol
from app.models.interpretation import Interpretation


def _create_text_dream(client: TestClient, user_id: uuid.UUID) -> uuid.UUID:
    resp = client.post(
        "/dreams",
        data={"user_id": str(user_id), "language": "ru", "text": "мне снилась вода"},
    )
    assert resp.status_code == 200, resp.text
    return uuid.UUID(resp.json()["dream_id"])


def test_create_dream_text(client: TestClient) -> None:
    resp = client.post(
        "/dreams",
        data={"user_id": str(uuid.uuid4()), "language": "ru", "text": "снилась вода"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["transcript"] == "снилась вода"
    assert body["language"] == "ru"


def test_create_dream_audio_transcribes(client: TestClient) -> None:
    resp = client.post(
        "/dreams",
        data={"user_id": str(uuid.uuid4()), "language": "kk"},
        files={"audio": ("dream.m4a", b"\x00\x01\x02", "audio/m4a")},
    )
    assert resp.status_code == 200
    assert resp.json()["transcript"] == "мокнутый транскрипт сна"


def test_create_dream_requires_exactly_one_input(client: TestClient) -> None:
    resp = client.post("/dreams", data={"user_id": str(uuid.uuid4()), "language": "ru"})
    assert resp.status_code == 422


def test_update_transcript(client: TestClient) -> None:
    user_id = uuid.uuid4()
    dream_id = _create_text_dream(client, user_id)
    resp = client.patch(f"/dreams/{dream_id}/transcript", json={"transcript": "исправленный текст"})
    assert resp.status_code == 200
    assert resp.json()["transcript"] == "исправленный текст"


def test_interpret_persists_pipeline_rows(client: TestClient, db_session: Session) -> None:
    user_id = uuid.uuid4()
    dream_id = _create_text_dream(client, user_id)

    resp = client.post(f"/dreams/{dream_id}/interpret", params={"lens": "psych"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["lens"] == "psych"
    assert body["content_md"].startswith("#")
    assert body["tokens_in"] == 100
    assert body["tokens_out"] == 50

    assert (
        db_session.scalar(
            select(func.count()).select_from(DreamSymbol).where(DreamSymbol.dream_id == dream_id)
        )
        == 1
    )
    assert (
        db_session.scalar(
            select(func.count()).select_from(DreamEmotion).where(DreamEmotion.dream_id == dream_id)
        )
        == 1
    )
    assert (
        db_session.scalar(
            select(DreamEmbedding.dream_id).where(DreamEmbedding.dream_id == dream_id)
        )
        == dream_id
    )
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(Interpretation)
            .where(Interpretation.dream_id == dream_id)
        )
        == 1
    )


def test_interpret_rejects_unknown_lens(client: TestClient) -> None:
    dream_id = _create_text_dream(client, uuid.uuid4())
    resp = client.post(f"/dreams/{dream_id}/interpret", params={"lens": "astrology"})
    assert resp.status_code == 422


def test_interpret_missing_dream_404(client: TestClient) -> None:
    resp = client.post(f"/dreams/{uuid.uuid4()}/interpret", params={"lens": "psych"})
    assert resp.status_code == 404


def test_body_size_limit(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "max_upload_bytes", 5)
    resp = client.post(
        "/dreams",
        data={"user_id": str(uuid.uuid4()), "language": "ru", "text": "длинный текст"},
    )
    assert resp.status_code == 413
