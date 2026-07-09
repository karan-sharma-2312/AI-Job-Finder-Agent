from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Centralized environment settings for local, Docker, and Apify runs."""

    apify_token: str | None = None
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    database_url: str = "sqlite:///./data/jobs.db"
    log_level: str = "INFO"
    enable_ai_scoring: bool = True
    enable_proxy: bool = False
    proxy_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def get_settings() -> AppSettings:
    """Factory wrapper that can be swapped for cached settings later."""

    return AppSettings()
