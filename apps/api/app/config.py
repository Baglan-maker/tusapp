from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment / .env.

    Secrets must never be hard-coded; keep .env.example in sync.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Postgres (local docker by default; Supabase connection string in prod)
    database_url: str = "postgresql+psycopg://tus:tus@localhost:5432/tus"

    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""

    # Speech-to-text
    groq_api_key: str = ""
    elevenlabs_api_key: str = ""

    # LLM (Anthropic). Extraction stays on Haiku; interpretation model is
    # swappable so we can eval Haiku vs Sonnet on the golden set.
    anthropic_api_key: str = ""
    extract_model: str = "claude-haiku-4-5"
    interpret_model: str = "claude-haiku-4-5"

    # Embeddings
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"

    # ElevenLabs Scribe STT model id (Kazakh path)
    elevenlabs_stt_model: str = "scribe_v2"

    # Reject request bodies larger than this (audio upload guard), in bytes.
    max_upload_bytes: int = 10 * 1024 * 1024

    # AI call hardening
    ai_timeout_seconds: float = 30.0
    ai_max_retries: int = 2


settings = Settings()
