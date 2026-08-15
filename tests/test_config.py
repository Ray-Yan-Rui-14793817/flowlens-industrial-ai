"""Tests for the canonical FlowLens settings."""

import pytest
from pydantic import SecretStr, ValidationError

from flowlens.config import Settings


def test_settings_can_be_constructed() -> None:
    settings = Settings(
        database_url=SecretStr(
            "postgresql+psycopg://flowlens:flowlens@localhost:5432/flowlens"
        ),
        _env_file=None,
    )

    assert settings.service_name == "flowlens-api"
    assert settings.app_environment == "development"
    assert settings.log_level == "INFO"
    assert settings.database_url.get_secret_value().startswith("postgresql+psycopg://")


def test_environment_variables_override_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLOWLENS_SERVICE_NAME", "flowlens-worker")
    monkeypatch.setenv("FLOWLENS_APP_ENVIRONMENT", "test")
    monkeypatch.setenv("FLOWLENS_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv(
        "FLOWLENS_DATABASE_URL",
        "postgresql+psycopg://test:test@localhost:5432/flowlens_test",
    )

    settings = Settings(_env_file=None)

    assert settings.service_name == "flowlens-worker"
    assert settings.app_environment == "test"
    assert settings.log_level == "DEBUG"
    assert settings.database_url.get_secret_value().endswith("/flowlens_test")


def test_database_url_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FLOWLENS_DATABASE_URL", raising=False)

    with pytest.raises(ValidationError, match="database_url"):
        Settings(_env_file=None)
