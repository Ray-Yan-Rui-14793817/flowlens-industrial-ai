"""Unit tests for lazy SQLAlchemy database infrastructure."""

from typing import Never
from unittest.mock import Mock

import pytest
from pydantic import SecretStr
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from flowlens.config import Settings
from flowlens.db import (
    DatabaseUnavailableError,
    check_database_connectivity,
    create_database_engine,
    create_session_factory,
    session_scope,
)

DATABASE_URL = "postgresql+psycopg://flowlens:flowlens@localhost:5432/flowlens"


def _settings() -> Settings:
    return Settings(database_url=SecretStr(DATABASE_URL), _env_file=None)


def test_engine_construction_is_lazy(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_connect(*args: object, **kwargs: object) -> Never:
        raise AssertionError("Engine construction attempted a database connection")

    monkeypatch.setattr("psycopg.connect", unexpected_connect)

    engine = create_database_engine(_settings())

    assert engine.url.drivername == "postgresql+psycopg"
    assert engine.url.database == "flowlens"
    engine.dispose()


def test_session_factory_can_be_constructed() -> None:
    engine = create_database_engine(_settings())

    session_factory = create_session_factory(engine)

    assert session_factory.kw["bind"] is engine
    assert session_factory.kw["autoflush"] is False
    assert session_factory.kw["expire_on_commit"] is False
    engine.dispose()


def test_session_scope_closes_without_rollback_on_success() -> None:
    session = Mock(spec=Session)
    session_factory = Mock(return_value=session)

    with session_scope(session_factory) as yielded_session:
        assert yielded_session is session

    session_factory.assert_called_once_with()
    session.rollback.assert_not_called()
    session.close.assert_called_once_with()


def test_session_scope_rolls_back_closes_and_propagates_exception() -> None:
    session = Mock(spec=Session)
    session_factory = Mock(return_value=session)
    error = RuntimeError("scope failed")

    with pytest.raises(RuntimeError) as raised:
        with session_scope(session_factory) as yielded_session:
            assert yielded_session is session
            raise error

    assert raised.value is error
    session_factory.assert_called_once_with()
    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()


def test_connectivity_failure_is_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_database_engine(_settings())

    def unavailable_connect() -> Never:
        raise OperationalError("SELECT 1", None, OSError("database unavailable"))

    monkeypatch.setattr(engine, "connect", unavailable_connect)

    with pytest.raises(DatabaseUnavailableError, match="connectivity check failed"):
        check_database_connectivity(engine)

    engine.dispose()
