"""Transcript embeddings via OpenAI text-embedding-3-small (1536 dims)."""

from openai import OpenAI

from app.config import settings


def embed(text: str) -> list[float]:
    client = OpenAI(api_key=settings.openai_api_key).with_options(
        timeout=settings.ai_timeout_seconds, max_retries=settings.ai_max_retries
    )
    response = client.embeddings.create(model=settings.embedding_model, input=text)
    return response.data[0].embedding
