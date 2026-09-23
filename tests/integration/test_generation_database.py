"""PostgreSQL compatibility proof for generated C03 baseline rows."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from typing import Final

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.engine import Connection, make_url

from flowlens.config import Settings
from flowlens.data import Base
from flowlens.data.generation import GenerationConfig, GenerationProfile, generate_baseline
from flowlens.db import create_database_engine

pytestmark = pytest.mark.integration

PROJECT_ROOT: Final = Path(__file__).resolve().parents[2]


def _settings_or_skip() -> Settings:
    try:
        settings = Settings()
    except ValidationError:
        pytest.skip("FLOWLENS_DATABASE_URL is required for database integration tests")
    database_name = make_url(settings.database_url.get_secret_value()).database
    if settings.app_environment != "test" or not database_name or not database_name.endswith(
        "_test"
    ):
        raise RuntimeError(
            "C03 integration requires FLOWLENS_APP_ENVIRONMENT=test and "
            "a database name ending in '_test'"
        )
    return settings


def _alembic_config() -> Config:
    return Config(toml_file=str(PROJECT_ROOT / "pyproject.toml"))


def _row_values(row: Base) -> dict[str, object]:
    return {column.name: getattr(row, column.name) for column in row.__mapper__.columns}


def _insert_generated_dataset(connection: Connection) -> int:
    dataset = generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.TEST,
            seed=20_260_824,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=datetime(2026, 8, 24, 9, tzinfo=UTC),
        )
    )
    connection.execute(
        Base.metadata.tables["dataset_version"].insert(),
        _row_values(dataset.dataset_version),
    )
    for table_name, rows in dataset.rows_by_table.items():
        if rows:
            connection.execute(
                Base.metadata.tables[table_name].insert(),
                [_row_values(row) for row in rows],
            )
    return dataset.row_count_total


def test_generated_test_profile_fits_frozen_postgresql_schema() -> None:
    settings = _settings_or_skip()
    command.upgrade(_alembic_config(), "head")
    engine = create_database_engine(settings)
    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                inserted_count = _insert_generated_dataset(connection)
                actual_count = sum(
                    connection.execute(
                        select(func.count()).select_from(Base.metadata.tables[table_name])
                    ).scalar_one()
                    for table_name in Base.metadata.tables
                    if table_name != "dataset_version"
                )
                assert actual_count == inserted_count
            finally:
                transaction.rollback()
    finally:
        engine.dispose()
