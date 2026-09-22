"""Atomic, single-active-dataset PostgreSQL persistence. No replacement policy."""

from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.engine import Connection, Engine

from flowlens.data import Base
from flowlens.data.generation import GeneratedDataset
from flowlens.data.generation.canonical import CANONICAL_TABLE_ORDER, canonicalize_rows
from flowlens.data.models import DatasetVersion
from flowlens.data.quality import validate_dataset

_TABLES = ("dataset_version", *CANONICAL_TABLE_ORDER)
_BATCH_SIZE = 1000


class DatasetLoadError(ValueError):
    """A fixed-message workflow failure, never containing database parameters."""


class DuplicateDatasetError(DatasetLoadError):
    """The single-active-dataset policy rejected a load before mutation."""


def row_values(row: Base) -> dict[str, object]:
    """Copy canonical columns, preserving native scalar values."""
    return {column.name: getattr(row, column.name) for column in row.__mapper__.columns}


def _require_postgresql(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":
        raise DatasetLoadError("The data workflow requires PostgreSQL.")


def _require_schema(connection: Connection) -> None:
    revisions = connection.execute(text("SELECT version_num FROM alembic_version")).scalars().all()
    if revisions != ["0002_industrial_data_foundation"]:
        raise DatasetLoadError("Apply the approved Alembic head before using the data workflow.")


def _read(connection: Connection) -> GeneratedDataset:
    versions = connection.execute(select(DatasetVersion.__table__)).mappings().all()
    if not versions:
        raise DatasetLoadError("No active synthetic dataset exists in the database.")
    if len(versions) != 1:
        raise DatasetLoadError("Multiple synthetic datasets exist; exactly one is required.")
    models = {mapper.class_.__tablename__: mapper.class_ for mapper in Base.registry.mappers}
    # Read all rows: filtering by active ID would hide stray ownership/orphan rows.
    rows = {
        name: tuple(
            models[name](**dict(values))
            for values in connection.execute(select(Base.metadata.tables[name])).mappings()
        )
        for name in CANONICAL_TABLE_ORDER
    }
    return GeneratedDataset(DatasetVersion(**dict(versions[0])), canonicalize_rows(rows))


def read_active_dataset(engine: Engine) -> GeneratedDataset:
    """Read one consistent, detached snapshot without mutation or repair."""
    _require_postgresql(engine)
    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            _require_schema(connection)
            return _read(connection)


def persist_dataset(engine: Engine, dataset: GeneratedDataset) -> GeneratedDataset:
    """Preflight, batch-load and verify; any transaction failure rolls everything back.

    SHARE ROW EXCLUSIVE locks serialize loaders, including different dataset IDs,
    and exclude business writes during verification. READ COMMITTED lets a waiting
    loader see the preceding commit before checking for duplicates. No filesystem
    work occurs while holding locks. Database constraints remain the final boundary.
    """
    _require_postgresql(engine)
    if not isinstance(dataset, GeneratedDataset):
        raise TypeError("persistence requires GeneratedDataset")
    if not validate_dataset(dataset).passed:
        raise DatasetLoadError("Public in-memory data quality failed; no rows were loaded.")
    copied = GeneratedDataset(
        DatasetVersion(**row_values(dataset.dataset_version)),
        canonicalize_rows(
            {
                name: tuple(type(row)(**row_values(row)) for row in rows)
                for name, rows in dataset.rows_by_table.items()
            }
        ),
    )
    if not validate_dataset(copied).passed:
        raise DatasetLoadError("Input changed during preflight; no rows were loaded.")
    available: set[str] = set()
    for name in _TABLES:
        dependencies = {fk.column.table.name for fk in Base.metadata.tables[name].foreign_keys}
        if not dependencies <= available:
            raise DatasetLoadError("Canonical table order is not dependency-safe.")
        available.add(name)
    with engine.connect().execution_options(isolation_level="READ COMMITTED") as connection:
        with connection.begin():
            _require_schema(connection)
            connection.execute(text("SET LOCAL lock_timeout = '30s'"))
            # Identifiers come exclusively from the fixed canonical table names.
            connection.execute(
                text("LOCK TABLE " + ", ".join(_TABLES) + " IN SHARE ROW EXCLUSIVE MODE")
            )
            if connection.execute(select(DatasetVersion.dataset_version_id).limit(1)).first():
                raise DuplicateDatasetError(
                    "The database already contains a synthetic dataset; "
                    "replacement is not supported."
                )
            connection.execute(
                Base.metadata.tables["dataset_version"].insert(), row_values(copied.dataset_version)
            )
            for name in CANONICAL_TABLE_ORDER:
                rows = copied.rows_by_table[name]
                for start in range(0, len(rows), _BATCH_SIZE):
                    connection.execute(
                        Base.metadata.tables[name].insert(),
                        [row_values(row) for row in rows[start : start + _BATCH_SIZE]],
                    )
            persisted = _read(connection)
            if row_values(persisted.dataset_version) != row_values(copied.dataset_version):
                raise DatasetLoadError("Persisted dataset metadata does not match the input.")
            if not validate_dataset(persisted).passed:
                raise DatasetLoadError(
                    "Post-load public data quality failed; the load was rolled back."
                )
    return persisted
