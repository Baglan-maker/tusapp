from typing import Literal

from pydantic import BaseModel, Field


class ExtractedSymbol(BaseModel):
    slug: str
    salience: float = Field(ge=0.0, le=1.0)


class ExtractedEmotion(BaseModel):
    slug: str
    kind: Literal["in_dream", "on_waking"]


class DreamExtraction(BaseModel):
    """Structured output of LLM call #1. Validated by Pydantic."""

    symbols: list[ExtractedSymbol] = Field(default_factory=list)
    emotions: list[ExtractedEmotion] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    places: list[str] = Field(default_factory=list)
    is_lucid: bool = False
