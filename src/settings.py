# pydantic-settings class

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Initial login URL (will redirect to dispatcher with a fresh login_challenge)
    MSE_INITIAL_LOGIN_URL: str = (
        "https://messervices.etudiant.gouv.fr/oauth2/login"
    )

    # Polling interval between checks (seconds)
    POLL_INTERVAL_SECONDS: int = Field(default=350)
    # Old URL
    # MSE_LOGIN_URL: str = "https://www.messervices.etudiant.gouv.fr/envole/oauth2/login"

    MSE_EMAIL: str = Field(default=...)
    MSE_PASSWORD: str = Field(default=...)

    TELEGRAM_BOT_TOKEN: str = Field(default=...)
    MY_TELEGRAM_ID: str = Field(default=...)
