"""SQLite configuration placeholder — no production DB wiring yet."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./tradepulse.db"
    app_name: str = "TradePulse API"
    app_version: str = "0.1.0-skeleton"


settings = Settings()


def get_sqlite_url() -> str:
    """Return the configured SQLite URL (placeholder for repositories)."""
    return settings.database_url
