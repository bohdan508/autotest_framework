"""Central configuration, loaded from environment / .env.

Import the ready-to-use `settings` instance:

    from config.settings import settings
    settings.base_url
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env lives next to this file (config/.env). Resolve it absolutely so the
# config loads the same way no matter which directory pytest is run from.
ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",  # ignore unrelated env vars instead of erroring
    )

    # --- API ---
    base_url: str = "https://automationexercise.com"
    api_prefix: str = "/api"
    timeout: float = 30.0  # seconds, per request

    # --- Behaviour ---
    log_level: str = "INFO"

    @property
    def api_url(self) -> str:
        """Full API base, e.g. https://automationexercise.com/api"""
        return f"{self.base_url.rstrip('/')}{self.api_prefix}"


# Single shared instance imported across the framework.
settings = Settings()
