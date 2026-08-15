"""Real PostgreSQL, pgvector, and Alembic integration verification."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.engine import Engine

from flowlens.config import Settings
from flowlens.db import (
    check_database_connectivity,
    create_database_engine,
    is_pgvector_available,
    is_pgvector_enabled,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def migrated_database_engine() -> Iterator[Engine]:
    try:
        settings = Settings()
    except ValidationError:
        pytest.skip("FLOWLENS_DATABASE_URL is required for database integration tests")

    config = Config(toml_file=str(PROJECT_ROOT / "pyproject.toml"))
    command.upgrade(config, "head")

    engine = create_database_engine(settings)
    try:
        yield engine
    finally:
        engine.dispose()


def test_real_database_connectivity(migrated_database_engine: Engine) -> None:
    assert check_database_connectivity(migrated_database_engine) is True


def test_pgvector_is_available_and_enabled(migrated_database_engine: Engine) -> None:
    assert is_pgvector_available(migrated_database_engine) is True
    assert is_pgvector_enabled(migrated_database_engine) is True


def test_alembic_baseline_is_applied(migrated_database_engine: Engine) -> None:
    with migrated_database_engine.connect() as connection:
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()

    assert revision == "0001_enable_pgvector"
