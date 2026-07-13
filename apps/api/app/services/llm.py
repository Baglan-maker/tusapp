"""Anthropic calls: structured extraction (Haiku) and interpretation (swappable).

All calls carry a 30s timeout and 2 exponential-backoff retries (SDK-level).
Extraction validates the JSON against a Pydantic schema and re-requests once,
with the error surfaced in the prompt, before giving up.
"""

from dataclasses import dataclass

from anthropic import Anthropic
from anthropic.types import MessageParam, ThinkingConfigDisabledParam

from app import prompts
from app.config import settings
from app.prompts import Lens
from app.schemas.extraction import DreamExtraction


class LLMError(RuntimeError):
    pass


def _client() -> Anthropic:
    return Anthropic(api_key=settings.anthropic_api_key).with_options(
        timeout=settings.ai_timeout_seconds, max_retries=settings.ai_max_retries
    )


def extract(transcript: str, language: str) -> DreamExtraction:
    """LLM call #1 — structured symbol/emotion extraction.

    On an unparseable response, retry once with the error noted in the prompt.
    """
    client = _client()
    messages: list[MessageParam] = [
        {"role": "user", "content": prompts.extract_user(transcript, language)}
    ]
    for attempt in range(2):
        response = client.messages.parse(
            model=settings.extract_model,
            max_tokens=1024,
            system=prompts.EXTRACT_SYSTEM,
            messages=messages,
            output_format=DreamExtraction,
        )
        parsed = response.parsed_output
        if parsed is not None:
            return parsed
        if attempt == 0:
            messages = [
                *messages,
                {"role": "user", "content": prompts.EXTRACT_RETRY_NOTE},
            ]
    raise LLMError("extraction produced no valid structured output after retry")


@dataclass
class InterpretResult:
    content_md: str
    model: str
    tokens_in: int
    tokens_out: int


def interpret(
    *,
    language: str,
    lens: Lens,
    symbols_line: str,
    meanings_block: str,
    emotions_line: str,
    recent_block: str,
    patterns_block: str,
    transcript: str,
) -> InterpretResult:
    """LLM call #2 — the user-facing interpretation (Markdown)."""
    client = _client()
    model = settings.interpret_model
    # A 150-250 word note needs no thinking. Disable it explicitly so models
    # where adaptive thinking is the default (Sonnet/Opus) stay cheap and the
    # Haiku-vs-Sonnet comparison is apples-to-apples.
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        thinking=ThinkingConfigDisabledParam(type="disabled"),
        system=prompts.interpret_system(language, lens),
        messages=[
            {
                "role": "user",
                "content": prompts.interpret_user(
                    transcript=transcript,
                    lens=lens,
                    symbols_line=symbols_line,
                    meanings_block=meanings_block,
                    emotions_line=emotions_line,
                    recent_block=recent_block,
                    patterns_block=patterns_block,
                ),
            }
        ],
    )
    content_md = "".join(block.text for block in response.content if block.type == "text").strip()
    if not content_md:
        raise LLMError("interpretation returned no text")
    return InterpretResult(
        content_md=content_md,
        model=model,
        tokens_in=response.usage.input_tokens,
        tokens_out=response.usage.output_tokens,
    )
