from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/src/twin/settings.py -> the repository root, where .env lives.
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    """Environment variables with the TWIN_ prefix, read once at start-up."""

    model_config = SettingsConfigDict(
        env_prefix="TWIN_", env_file=_ENV_FILE, extra="ignore"
    )

    host: str = "127.0.0.1"
    port: int = 8000
    # postgresql+psycopg://user:password@host:port/database; the default matches .env.example.
    database_url: str = "postgresql+psycopg://twin:twin@127.0.0.1:5432/twin"
