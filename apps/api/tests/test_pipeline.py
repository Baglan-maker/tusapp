import pytest

from app.schemas.extraction import DreamExtraction, ExtractedSymbol
from app.services import llm
from app.services.llm import LLMError
from tests.conftest import FakeAnthropic


def test_extract_retries_on_unparseable_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    good = DreamExtraction(symbols=[ExtractedSymbol(slug="water", salience=0.8)])
    fake = FakeAnthropic([None, good])  # first response unparseable, second valid
    monkeypatch.setattr("app.services.llm._client", lambda: fake)

    result = llm.extract("сон про воду", "ru")

    assert result.symbols[0].slug == "water"
    assert fake.messages.parse_calls == 2  # it actually retried once


def test_extract_gives_up_after_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.llm._client", lambda: FakeAnthropic([None, None]))
    with pytest.raises(LLMError):
        llm.extract("непонятный сон", "ru")


def test_interpret_reports_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.llm._client",
        lambda: FakeAnthropic([DreamExtraction()], create_text="# Суть\nтёплый текст"),
    )
    from app.prompts import Lens

    result = llm.interpret(
        language="ru",
        lens=Lens.psych,
        symbols_line="water: 0.90",
        meanings_block="- water: эмоции",
        emotions_line="fear (in_dream)",
        recent_block="",
        patterns_block="",
        transcript="снилась вода",
    )
    assert result.content_md.startswith("# Суть")
    assert result.tokens_in == 100
    assert result.tokens_out == 50
