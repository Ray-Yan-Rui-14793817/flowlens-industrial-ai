"""Canonical environment-backed application settings."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ApplicationEnvironment = Literal["development", "test", "staging", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """FlowLens settings loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="FLOWLENS_",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    service_name: Annotated[str, Field(min_length=1)] = "flowlens-api"
    app_environment: ApplicationEnvironment = "development"
    log_level: LogLevel = "INFO"
    database_url: Annotated[SecretStr, Field(min_length=1)]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide canonical settings instance."""

    return Settings()
