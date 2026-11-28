from pathlib import Path

from pydantic import SecretStr
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
    # Signs access tokens (HS256); at least 32 characters. The app refuses to start without it.
    jwt_secret: SecretStr | None = None
    # Send the refresh cookie over HTTPS only. Set true wherever the site is served over HTTPS.
    cookie_secure: bool = False
    access_token_minutes: int = 15
    refresh_token_days: int = 30

    # Google sign-in is on only when all three are set (docs/google-oauth-setup.md).
    google_client_id: str | None = None
    google_client_secret: SecretStr | None = None
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    @property
    def google_enabled(self) -> bool:
        return bool(
            self.google_client_id
            and self.google_client_secret
            and self.google_client_secret.get_secret_value()
            and self.google_redirect_uri
        )
