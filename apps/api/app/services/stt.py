"""Speech-to-text with per-language routing.

ru -> Groq whisper-large-v3 (cheap, good). kk -> ElevenLabs Scribe (vanilla
Whisper is unusable on Kazakh). Audio is never persisted: callers transcribe,
keep the text, and drop the bytes.
"""

import httpx
from groq import Groq

from app.config import settings


class STTError(RuntimeError):
    pass


def transcribe(audio: bytes, filename: str, language: str) -> str:
    """Return a transcript for the audio in the given language ('ru' | 'kk')."""
    if language == "kk":
        return _elevenlabs_scribe(audio, filename)
    return _groq_whisper(audio, filename, language)


def _groq_whisper(audio: bytes, filename: str, language: str) -> str:
    client = Groq(api_key=settings.groq_api_key).with_options(
        timeout=settings.ai_timeout_seconds, max_retries=settings.ai_max_retries
    )
    result = client.audio.transcriptions.create(
        file=(filename, audio),
        model="whisper-large-v3",
        language=language,
    )
    return result.text.strip()


def _elevenlabs_scribe(audio: bytes, filename: str) -> str:
    resp = httpx.post(
        "https://api.elevenlabs.io/v1/speech-to-text",
        headers={"xi-api-key": settings.elevenlabs_api_key},
        data={"model_id": settings.elevenlabs_stt_model, "language_code": "kk"},
        files={"file": (filename, audio)},
        timeout=settings.ai_timeout_seconds,
    )
    if resp.status_code != 200:
        raise STTError(f"ElevenLabs Scribe failed: {resp.status_code} {resp.text}")
    text = resp.json().get("text")
    if not isinstance(text, str):
        raise STTError("ElevenLabs Scribe returned no text")
    return text.strip()
