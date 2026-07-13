from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import engine, get_session
from app.main import app
from app.schemas.extraction import DreamExtraction, ExtractedEmotion, ExtractedSymbol

# --- Fake Anthropic client -------------------------------------------------
# Tests never hit a real provider. STT and embeddings are stubbed directly;
# the LLM is stubbed at the client boundary so llm.extract/interpret run their
# real logic (schema validation, retry, token accounting) over canned output.


class _FakeParseResp:
    def __init__(self, parsed: DreamExtraction | None) -> None:
        self.parsed_output = parsed


class _FakeUsage:
    input_tokens = 100
    output_tokens = 50


class _FakeTextBlock:
    type = "text"

    def __init__(self, text: str) -> None:
        self.text = text


class _FakeCreateResp:
    def __init__(self, text: str) -> None:
        self.content = [_FakeTextBlock(text)]
        self.usage = _FakeUsage()


class _FakeMessages:
    def __init__(self, parse_outputs: list[DreamExtraction | None], create_text: str) -> None:
        self._parse_outputs = parse_outputs
        self._create_text = create_text
        self.parse_calls = 0

    def parse(self, **_: Any) -> _FakeParseResp:
        idx = min(self.parse_calls, len(self._parse_outputs) - 1)
        self.parse_calls += 1
        return _FakeParseResp(self._parse_outputs[idx])

    def create(self, **_: Any) -> _FakeCreateResp:
        return _FakeCreateResp(self._create_text)


class FakeAnthropic:
    def __init__(
        self,
        parse_outputs: list[DreamExtraction | None],
        create_text: str = "# Толкование\nтест",
    ) -> None:
        self.messages = _FakeMessages(parse_outputs, create_text)

    def with_options(self, **_: Any) -> "FakeAnthropic":
        return self


def default_extraction() -> DreamExtraction:
    return DreamExtraction(
        symbols=[ExtractedSymbol(slug="water", salience=0.9)],
        emotions=[ExtractedEmotion(slug="fear", kind="in_dream")],
    )


@pytest.fixture(autouse=True)
def mock_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.llm._client", lambda: FakeAnthropic([default_extraction()]))
    monkeypatch.setattr(
        "app.services.stt.transcribe",
        lambda audio, filename, language: "мокнутый транскрипт сна",
    )
    monkeypatch.setattr("app.services.embeddings.embed", lambda text: [0.0] * 1536)


# --- DB session (rolled back per test) -------------------------------------


@pytest.fixture
def db_session() -> Iterator[Session]:
    connection = engine.connect()
    trans = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    def override() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_session] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
