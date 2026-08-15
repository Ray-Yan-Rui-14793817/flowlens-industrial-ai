"""Tests for the Week 1 worker placeholder."""

import logging
from threading import Event

import pytest
from pydantic import SecretStr

import flowlens.worker.main as worker_main
from flowlens.config import Settings

DATABASE_URL = "postgresql+psycopg://flowlens:flowlens@localhost:5432/flowlens"


def _settings() -> Settings:
    return Settings(database_url=SecretStr(DATABASE_URL), _env_file=None)


def test_worker_starts_and_stops_without_business_jobs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    stop_event = Event()
    stop_event.set()

    with caplog.at_level(logging.INFO):
        worker_main.run_worker(_settings(), stop_event)

    assert "FlowLens worker started (environment=development)" in caplog.messages
    assert "FlowLens worker stopped" in caplog.messages


def test_worker_main_uses_canonical_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings()
    observed_settings: list[Settings] = []

    monkeypatch.setattr(worker_main, "get_settings", lambda: settings)
    monkeypatch.setattr("flowlens.worker.main.signal.signal", lambda *_args: None)

    def capture_run(received_settings: Settings, stop_event: Event) -> None:
        observed_settings.append(received_settings)
        assert isinstance(stop_event, Event)

    monkeypatch.setattr(worker_main, "run_worker", capture_run)

    worker_main.main()

    assert observed_settings == [settings]
