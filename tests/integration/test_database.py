"""Real PostgreSQL, pgvector, and Alembic integration verification."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from pydantic import SecretStr, ValidationError
from sqlalchemy import text
from sqlalchemy.engine import Engine, make_url

from flowlens.config import ApplicationEnvironment, Settings
from flowlens.db import (
    check_database_connectivity,
    create_database_engine,
    is_pgvector_available,
    is_pgvector_enabled,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _require_explicit_test_database(settings: Settings) -> None:
    """Refuse integration-test migrations unless the target is explicitly test-only."""

    database_name = make_url(settings.database_url.get_secret_value()).database
    if settings.app_environment != "test" or not database_name or not database_name.endswith(
        "_test"
    ):
        raise RuntimeError(
            "Integration migrations require FLOWLENS_APP_ENVIRONMENT=test and "
            "a database name ending in '_test'"
        )


def _apply_test_migrations(settings: Settings) -> None:
    """Apply Alembic only after enforcing the explicit test-database boundary."""

    _require_explicit_test_database(settings)
    config = Config(toml_file=str(PROJECT_ROOT / "pyproject.toml"))
    command.upgrade(config, "head")


@pytest.fixture(scope="module")
def migrated_database_engine() -> Iterator[Engine]:
    try:
        settings = Settings()
    except ValidationError:
        pytest.skip("FLOWLENS_DATABASE_URL is required for database integration tests")

    _apply_test_migrations(settings)

    engine = create_database_engine(settings)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.mark.integration
def test_real_database_connectivity(migrated_database_engine: Engine) -> None:
    assert check_database_connectivity(migrated_database_engine) is True


@pytest.mark.integration
def test_pgvector_is_available_and_enabled(migrated_database_engine: Engine) -> None:
    assert is_pgvector_available(migrated_database_engine) is True
    assert is_pgvector_enabled(migrated_database_engine) is True


@pytest.mark.integration
def test_alembic_baseline_is_applied(migrated_database_engine: Engine) -> None:
    with migrated_database_engine.connect() as connection:
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()

    assert revision == "0001_enable_pgvector"


@pytest.mark.parametrize(
    ("environment", "database_name"),
    [
        ("development", "flowlens_test"),
        ("test", "flowlens"),
    ],
)
def test_migration_safety_rejects_unsafe_target_before_alembic(
    monkeypatch: pytest.MonkeyPatch,
    environment: ApplicationEnvironment,
    database_name: str,
) -> None:
    alembic_called = False

    def unexpected_upgrade(config: Config, revision: str) -> None:
        del config, revision
        nonlocal alembic_called
        alembic_called = True

    monkeypatch.setattr(command, "upgrade", unexpected_upgrade)
    settings = Settings(
        app_environment=environment,
        database_url=SecretStr(
            f"postgresql+psycopg://test:test@localhost:5432/{database_name}"
        ),
        _env_file=None,
    )

    with pytest.raises(RuntimeError, match="explicit test database|database name ending"):
        _apply_test_migrations(settings)

    assert alembic_called is False


def test_migration_safety_allows_explicit_test_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    applied_revisions: list[str] = []

    def record_upgrade(config: Config, revision: str) -> None:
        assert isinstance(config, Config)
        applied_revisions.append(revision)

    monkeypatch.setattr(command, "upgrade", record_upgrade)
    settings = Settings(
        app_environment="test",
        database_url=SecretStr(
            "postgresql+psycopg://test:test@localhost:5432/flowlens_test"
        ),
        _env_file=None,
    )

    _apply_test_migrations(settings)

    assert applied_revisions == ["head"]
