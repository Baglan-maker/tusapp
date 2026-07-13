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

    # LLM
    anthropic_api_key: str = ""

    # Embeddings
    openai_api_key: str = ""


settings = Settings()
