"""C05 real PostgreSQL atomicity, duplicate, CLI and public artifact acceptance."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from threading import Barrier
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import event, func, inspect, select, text
from sqlalchemy.engine import Connection, Engine, ExecutionContext, make_url
from sqlalchemy.exc import IntegrityError

from flowlens.config import Settings
from flowlens.data import Base
from flowlens.data.generation import (
    BUSINESS_TIMEZONE,
    GeneratedDataset,
    GenerationConfig,
    GenerationProfile,
    generate_baseline,
)
from flowlens.data.generation.canonical import CANONICAL_TABLE_ORDER, canonical_business_payload
from flowlens.data.models import DatasetVersion
from flowlens.data.persistence import (
    DatasetLoadError,
    DuplicateDatasetError,
    persist_dataset,
    read_active_dataset,
    row_values,
)
from flowlens.data.quality import validate_dataset
from flowlens.data.scenarios import CapacitySurgeConfig, apply_scenario
from flowlens.db import create_database_engine

pytestmark = pytest.mark.integration
ROOT = Path(__file__).resolve().parents[2]


def _baseline(
    profile: GenerationProfile = GenerationProfile.TEST, seed: int = 20260824
) -> GeneratedDataset:
    return generate_baseline(
        GenerationConfig(
            profile=profile,
            seed=seed,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=datetime(2026, 8, 24, tzinfo=UTC),
        )
    )


def _counts(engine: Engine) -> dict[str, int]:
    with engine.connect() as connection:
        return {
            name: connection.execute(select(func.count()).select_from(table)).scalar_one()
            for name, table in Base.metadata.tables.items()
        }


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    try:
        settings = Settings()
    except ValidationError:
        if os.environ.get("FLOWLENS_DATABASE_URL"):
            raise
        pytest.skip("FLOWLENS_DATABASE_URL is required for C05 PostgreSQL acceptance")
    url = make_url(settings.database_url.get_secret_value())
    if (
        settings.app_environment != "test"
        or url.get_backend_name() != "postgresql"
        or not url.database
        or not url.database.endswith("_test")
    ):
        raise RuntimeError(
            "C05 integration requires PostgreSQL, test environment and '_test' database"
        )
    command.upgrade(Config(toml_file=str(ROOT / "pyproject.toml")), "head")
    target = create_database_engine(settings)
    try:
        assert set(inspect(target).get_table_names()) == set(Base.metadata.tables) | {
            "alembic_version"
        }
        assert all(count == 0 for count in _counts(target).values()), "Refuse nonempty test target"
        yield target
    finally:
        target.dispose()


@dataclass
class OwnedDatabase:
    engine: Engine
    dataset_ids: set[str] = field(default_factory=set)

    def own(self, dataset: GeneratedDataset) -> GeneratedDataset:
        self.dataset_ids.add(dataset.dataset_version.dataset_version_id)
        return dataset


@pytest.fixture
def database(engine: Engine) -> Iterator[OwnedDatabase]:
    assert all(count == 0 for count in _counts(engine).values()), "Refuse nonempty test target"
    owned = OwnedDatabase(engine)
    try:
        yield owned
    finally:
        # Test-only cleanup: guard all existing IDs, then remove ONLY registered test rows.
        with engine.begin() as connection:
            ids = set(connection.scalars(select(DatasetVersion.dataset_version_id)))
            assert ids <= owned.dataset_ids, "Unexpected dataset: do not delete it"
            for name in (*reversed(CANONICAL_TABLE_ORDER), "dataset_version"):
                table = Base.metadata.tables[name]
                connection.execute(
                    table.delete().where(table.c.dataset_version_id.in_(owned.dataset_ids))
                )
        assert all(count == 0 for count in _counts(engine).values())


def test_committed_round_trip_and_duplicate_zero_mutation(database: OwnedDatabase) -> None:
    source = database.own(_baseline())
    persisted = persist_dataset(database.engine, source)
    readback = read_active_dataset(database.engine)
    assert (
        canonical_business_payload(readback.rows_by_table)
        == canonical_business_payload(source.rows_by_table)
        == canonical_business_payload(persisted.rows_by_table)
    )
    assert row_values(readback.dataset_version) == row_values(source.dataset_version)
    assert validate_dataset(readback).passed
    counts = _counts(database.engine)
    assert counts == {
        "dataset_version": 1,
        **{name: len(rows) for name, rows in source.rows_by_table.items()},
    }
    # Python scalar equality independently protects Decimal/timestamp values and types.
    for name, rows in source.rows_by_table.items():
        for original, loaded in zip(rows, readback.rows_by_table[name], strict=True):
            assert row_values(original) == row_values(loaded)
            for column in original.__mapper__.columns:
                value = getattr(original, column.name)
                if value is not None:
                    assert isinstance(getattr(loaded, column.name), type(value))
    for duplicate in (source, database.own(_baseline(seed=20260825))):
        with pytest.raises(DuplicateDatasetError, match="already contains"):
            persist_dataset(database.engine, duplicate)
        assert _counts(database.engine) == counts
        assert canonical_business_payload(read_active_dataset(database.engine).rows_by_table) == (
            canonical_business_payload(source.rows_by_table)
        )


@pytest.mark.parametrize("failure", ["injected", "constraint", "postcheck"])
def test_mid_load_and_postcheck_roll_back_every_table(
    database: OwnedDatabase, failure: str
) -> None:
    source = database.own(_baseline())

    def fail(
        connection: Connection,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: ExecutionContext,
        executemany: bool,
    ) -> None:
        if not statement.startswith("INSERT INTO fact_inventory_snapshot"):
            return
        # Several complete tables have already been inserted in the active transaction.
        assert connection.scalar(
            select(func.count()).select_from(Base.metadata.tables["fact_work_order"])
        )
        if failure == "injected":
            raise RuntimeError("injected mid-load failure")
        if failure == "constraint":
            connection.execute(text("UPDATE fact_sales_order SET order_quantity = 0"))
        if failure == "postcheck":
            connection.execute(text("UPDATE dataset_version SET content_hash = 'invalid'"))

    event.listen(database.engine, "after_cursor_execute", fail)
    expected = {
        "injected": RuntimeError,
        "constraint": IntegrityError,
        "postcheck": DatasetLoadError,
    }
    try:
        with pytest.raises(expected[failure]):
            persist_dataset(database.engine, source)
    finally:
        event.remove(database.engine, "after_cursor_execute", fail)
    assert all(count == 0 for count in _counts(database.engine).values())
    # A failed transaction does not poison the next permitted load.
    assert persist_dataset(database.engine, source).content_hash == source.content_hash


def test_concurrent_different_dataset_loads_serialize(database: OwnedDatabase) -> None:
    sources = [database.own(_baseline(seed=seed)) for seed in (20260824, 20260825)]
    barrier = Barrier(2, timeout=20)

    def synchronize(
        connection: Connection,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: ExecutionContext,
        executemany: bool,
    ) -> None:
        if statement.startswith("LOCK TABLE"):
            barrier.wait()

    def load(dataset: GeneratedDataset) -> str:
        try:
            persist_dataset(database.engine, dataset)
            return "loaded"
        except DuplicateDatasetError:
            return "duplicate"

    event.listen(database.engine, "before_cursor_execute", synchronize)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            assert sorted(pool.map(load, sources)) == ["duplicate", "loaded"]
    finally:
        event.remove(database.engine, "before_cursor_execute", synchronize)
    readback = read_active_dataset(database.engine)
    assert readback.content_hash in {source.content_hash for source in sources}
    assert validate_dataset(readback).passed
    assert _counts(database.engine)["dataset_version"] == 1


def _cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "flowlens.data.cli", *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=240,
    )


@pytest.mark.parametrize("profile", list(GenerationProfile))
def test_actual_cli_generate_validate_and_duplicate(
    database: OwnedDatabase, tmp_path: Path, profile: GenerationProfile
) -> None:
    expected = database.own(_baseline(profile))
    arguments = (
        "generate",
        "--profile",
        profile.value,
        "--period-start",
        "2026-01-01",
        "--generator-version",
        "0.1.0-c03",
        "--output-dir",
        str(tmp_path),
    )
    generated = _cli(*arguments)
    assert generated.returncode == 0, generated.stderr
    assert "PASS" in generated.stdout
    manifest = json.loads((tmp_path / "dataset_manifest.json").read_bytes())
    assert manifest["content_hash"] == expected.content_hash
    assert manifest["row_count_total"] == expected.row_count_total
    assert manifest["seed"] == 20260824
    assert manifest["generated_at"] != "2026-08-24T00:00:00.000000Z"
    validated = _cli("validate", "--output-dir", str(tmp_path))
    assert validated.returncode == 0, validated.stderr
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    duplicate = _cli(*arguments)
    assert duplicate.returncode == 1 and "already contains" in duplicate.stderr
    assert before == {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    assert read_active_dataset(database.engine).content_hash == expected.content_hash


def test_empty_multiple_and_invalid_loaded_dataset(database: OwnedDatabase, tmp_path: Path) -> None:
    with pytest.raises(DatasetLoadError, match="No active"):
        read_active_dataset(database.engine)
    assert _cli("validate", "--output-dir", str(tmp_path)).returncode == 1
    assert list(tmp_path.iterdir()) == []
    source = database.own(_baseline())
    persist_dataset(database.engine, source)
    table = Base.metadata.tables["dataset_version"]
    with database.engine.begin() as connection:
        connection.execute(table.update().values(content_hash="0" * 64))
    invalid = _cli("validate", "--output-dir", str(tmp_path))
    assert invalid.returncode == 1 and "FAIL" in invalid.stdout
    assert json.loads((tmp_path / "data_quality_report.json").read_bytes())["status"] == "FAIL"
    assert "canonical_content_hash" in (tmp_path / "data_quality_report.md").read_text()
    assert read_active_dataset(database.engine).content_hash == "0" * 64  # no repair
    second = database.own(_baseline(seed=20260825))
    with database.engine.begin() as connection:
        connection.execute(table.insert(), row_values(second.dataset_version))
    with pytest.raises(DatasetLoadError, match="Multiple"):
        read_active_dataset(database.engine)
    multiple = _cli("validate", "--output-dir", str(tmp_path))
    assert multiple.returncode == 1 and "Multiple" in multiple.stderr


def test_invalid_preflight_never_writes(database: OwnedDatabase, tmp_path: Path) -> None:
    source = database.own(_baseline())
    source.dataset_version.row_count_total += 1
    with pytest.raises(DatasetLoadError, match="in-memory"):
        persist_dataset(database.engine, source)
    assert all(count == 0 for count in _counts(database.engine).values())
    invalid = _cli(
        "generate",
        "--profile",
        "test",
        "--period-start",
        "2026-01-01",
        "--generator-version",
        "",
        "--output-dir",
        str(tmp_path),
    )
    assert invalid.returncode == 1 and list(tmp_path.iterdir()) == []
    assert all(count == 0 for count in _counts(database.engine).values())


def test_artifact_failure_after_commit_recovers_via_validate(
    database: OwnedDatabase, tmp_path: Path
) -> None:
    database.own(_baseline())
    # A file cannot serve as an output directory. The committed data must survive.
    blocked = tmp_path / "not-a-directory"
    blocked.touch()
    result = _cli(
        "generate",
        "--profile",
        "test",
        "--period-start",
        "2026-01-01",
        "--generator-version",
        "0.1.0-c03",
        "--output-dir",
        str(blocked),
    )
    assert result.returncode == 1 and "rerun validate" in result.stderr
    assert validate_dataset(read_active_dataset(database.engine)).passed
    assert _cli("validate", "--output-dir", str(tmp_path / "reports")).returncode == 0
    assert (tmp_path / "reports" / "dataset_manifest.json").exists()


def test_finalized_scenario_business_dataset_uses_same_persistence(database: OwnedDatabase) -> None:
    result = apply_scenario(
        _baseline(),
        CapacitySurgeConfig(
            scenario_version="1.0.0",
            scenario_seed=20260901,
            window_start=datetime(2026, 1, 15, tzinfo=BUSINESS_TIMEZONE),
            window_end=datetime(2026, 2, 15, tzinfo=BUSINESS_TIMEZONE),
        ),
        generated_at=datetime(2026, 8, 24, tzinfo=UTC),
    )
    source = database.own(result.dataset)
    assert persist_dataset(database.engine, source).content_hash == source.content_hash
    assert canonical_business_payload(read_active_dataset(database.engine).rows_by_table) == (
        canonical_business_payload(source.rows_by_table)
    )
