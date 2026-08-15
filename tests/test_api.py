"""Unit tests for the FastAPI application and health contract."""

from typing import Never

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from flowlens.api.app import create_app
from flowlens.config import Settings
from flowlens.db import DatabaseUnavailableError

DATABASE_URL = "postgresql+psycopg://flowlens:flowlens@localhost:5432/flowlens"
HEALTHY_RESPONSE = {
    "status": "ok",
    "service": "flowlens-api",
    "database": "ok",
}
DEGRADED_RESPONSE = {
    "status": "degraded",
    "service": "flowlens-api",
    "database": "unavailable",
}


def _settings() -> Settings:
    return Settings(database_url=SecretStr(DATABASE_URL), _env_file=None)


def test_application_creation_and_startup_do_not_connect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected_connect(*args: object, **kwargs: object) -> Never:
        raise AssertionError("Application startup attempted a database connection")

    monkeypatch.setattr("psycopg.connect", unexpected_connect)

    application = create_app(_settings())

    assert isinstance(application, FastAPI)
    with TestClient(application):
        assert application.state.settings.service_name == "flowlens-api"
        assert isinstance(application.state.database_engine, Engine)


def test_health_returns_exact_healthy_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def connectivity_succeeds(engine: Engine) -> bool:
        assert isinstance(engine, Engine)
        return True

    monkeypatch.setattr(
        "flowlens.api.health.check_database_connectivity",
        connectivity_succeeds,
    )

    with TestClient(create_app(_settings())) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == HEALTHY_RESPONSE


def test_health_returns_safe_degraded_response(monkeypatch: pytest.MonkeyPatch) -> None:
    sensitive_url = "postgresql+psycopg://secret-user:secret-password@db.internal/flowlens"

    def connectivity_fails(engine: Engine) -> Never:
        assert isinstance(engine, Engine)
        raw_error = OperationalError(
            "SELECT 1",
            None,
            OSError(f"could not connect to {sensitive_url}"),
        )
        raise DatabaseUnavailableError("Database connectivity check failed") from raw_error

    monkeypatch.setattr(
        "flowlens.api.health.check_database_connectivity",
        connectivity_fails,
    )

    with TestClient(create_app(_settings())) as client:
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == DEGRADED_RESPONSE
    response_body = response.text.lower()
    for unsafe_value in (
        "secret-user",
        "secret-password",
        "db.internal",
        "sqlalchemy",
        "psycopg",
        "operationalerror",
        "traceback",
    ):
        assert unsafe_value not in response_body
