"""PostgreSQL verification for the canonical Week 2 manufacturing schema."""

from collections.abc import Iterator
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    inspect,
    text,
)
from sqlalchemy.engine import Connection, Engine, make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.sqltypes import TypeEngine

from flowlens.config import Settings
from flowlens.data import Base
from flowlens.data.models import register_models
from flowlens.db import create_database_engine, is_pgvector_enabled

pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[2]
C02_REVISION = "0002_industrial_data_foundation"
register_models()
C02_TABLES = set(Base.metadata.tables)


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
            "C02 integration migrations require FLOWLENS_APP_ENVIRONMENT=test and "
            "a database name ending in '_test'"
        )
    return settings


def _alembic_config() -> Config:
    return Config(toml_file=str(PROJECT_ROOT / "pyproject.toml"))


def _type_signature(column_type: TypeEngine[object]) -> tuple[object, ...]:
    if isinstance(column_type, BigInteger):
        return ("bigint",)
    if isinstance(column_type, Integer):
        return ("integer",)
    if isinstance(column_type, String):
        return ("varchar", column_type.length)
    if isinstance(column_type, Numeric):
        return ("numeric", column_type.precision, column_type.scale)
    if isinstance(column_type, DateTime):
        return ("timestamp", column_type.timezone)
    if isinstance(column_type, Date):
        return ("date",)
    if isinstance(column_type, Boolean):
        return ("boolean",)
    raise AssertionError(f"Unexpected SQL type: {column_type!r}")


def _seed_digital_thread(connection: Connection) -> None:
    utc = UTC
    rows: dict[str, dict[str, Any]] = {
        "dataset_version": {
            "dataset_version_id": "c02-test",
            "seed": 20260824,
            "generator_version": "0.1.0",
            "profile": "test",
            "period_start": date(2026, 1, 1),
            "period_end": date(2026, 4, 1),
            "generated_at": datetime(2026, 1, 1, tzinfo=utc),
            "content_hash": "a" * 64,
            "row_count_total": 15,
        },
        "dim_product": {
            "product_id": "prod-1",
            "dataset_version_id": "c02-test",
            "product_code": "PROD-001",
            "product_family": "GROUNDING_SWITCH",
            "model_name": "Synthetic Product 1",
            "complexity_class": "MEDIUM",
            "standard_cycle_hours": Decimal("8.00"),
            "active_from": date(2026, 1, 1),
            "active_to": None,
        },
        "dim_material": {
            "material_id": "mat-1",
            "dataset_version_id": "c02-test",
            "material_code": "MAT-001",
            "material_group": "Synthetic Metal",
            "criticality": "HIGH",
            "standard_lead_time_days": 10,
            "unit_of_measure": "EA",
        },
        "dim_supplier": {
            "supplier_id": "sup-1",
            "dataset_version_id": "c02-test",
            "supplier_code": "SUP-001",
            "supplier_tier": "TIER_1",
            "region": "Synthetic East",
            "active_from": date(2026, 1, 1),
            "active_to": None,
        },
        "dim_customer": {
            "customer_id": "cus-1",
            "dataset_version_id": "c02-test",
            "customer_code": "CUS-001",
            "customer_segment": "B2B",
            "region": "Synthetic North",
            "active_from": date(2026, 1, 1),
            "active_to": None,
        },
        "dim_work_center": {
            "work_center_id": "wc-1",
            "dataset_version_id": "c02-test",
            "work_center_code": "WC-001",
            "process_type": "ASSEMBLY",
            "line_group": "LINE-A",
            "daily_capacity_hours": Decimal("16.00"),
            "active_from": date(2026, 1, 1),
            "active_to": None,
        },
        "bridge_product_material": {
            "dataset_version_id": "c02-test",
            "product_id": "prod-1",
            "material_id": "mat-1",
            "quantity_per_unit": Decimal("2.0000"),
            "is_critical": True,
        },
        "fact_sales_order": {
            "sales_order_id": "so-1",
            "dataset_version_id": "c02-test",
            "customer_id": "cus-1",
            "product_id": "prod-1",
            "order_at": datetime(2026, 1, 2, tzinfo=utc),
            "promised_delivery_at": datetime(2026, 2, 1, tzinfo=utc),
            "order_quantity": 10,
            "priority": "NORMAL",
            "status": "IN_PRODUCTION",
        },
        "fact_purchase_order": {
            "purchase_order_id": "po-1",
            "dataset_version_id": "c02-test",
            "supplier_id": "sup-1",
            "material_id": "mat-1",
            "ordered_at": datetime(2026, 1, 2, tzinfo=utc),
            "promised_receipt_at": datetime(2026, 1, 12, tzinfo=utc),
            "actual_receipt_at": datetime(2026, 1, 10, tzinfo=utc),
            "ordered_quantity": Decimal("20.0000"),
            "received_quantity": Decimal("20.0000"),
            "status": "RECEIVED",
        },
        "fact_work_order": {
            "work_order_id": "wo-1",
            "dataset_version_id": "c02-test",
            "sales_order_id": "so-1",
            "product_id": "prod-1",
            "planned_start_at": datetime(2026, 1, 15, tzinfo=utc),
            "planned_end_at": datetime(2026, 1, 20, tzinfo=utc),
            "actual_start_at": datetime(2026, 1, 15, tzinfo=utc),
            "actual_end_at": datetime(2026, 1, 19, tzinfo=utc),
            "planned_quantity": 10,
            "completed_quantity": 10,
            "status": "COMPLETED",
        },
        "fact_operation": {
            "operation_id": "op-1",
            "dataset_version_id": "c02-test",
            "work_order_id": "wo-1",
            "work_center_id": "wc-1",
            "sequence_number": 1,
            "planned_start_at": datetime(2026, 1, 15, tzinfo=utc),
            "planned_end_at": datetime(2026, 1, 16, tzinfo=utc),
            "actual_start_at": datetime(2026, 1, 15, tzinfo=utc),
            "actual_end_at": datetime(2026, 1, 16, tzinfo=utc),
            "status": "COMPLETED",
        },
        "fact_material_requirement": {
            "material_requirement_id": "mr-1",
            "dataset_version_id": "c02-test",
            "work_order_id": "wo-1",
            "material_id": "mat-1",
            "required_quantity": Decimal("20.0000"),
            "need_by_at": datetime(2026, 1, 14, tzinfo=utc),
        },
        "fact_inventory_snapshot": {
            "inventory_snapshot_id": "inv-1",
            "dataset_version_id": "c02-test",
            "material_id": "mat-1",
            "snapshot_at": datetime(2026, 1, 14, tzinfo=utc),
            "on_hand_quantity": Decimal("30.0000"),
            "reserved_quantity": Decimal("20.0000"),
        },
        "fact_quality_inspection": {
            "inspection_id": "qi-1",
            "dataset_version_id": "c02-test",
            "work_order_id": "wo-1",
            "operation_id": "op-1",
            "inspection_at": datetime(2026, 1, 17, tzinfo=utc),
            "inspection_type": "FINAL",
            "inspected_quantity": 10,
            "passed_quantity": 9,
            "failed_quantity": 1,
            "defect_category": "Synthetic Defect",
            "severity": "LOW",
            "result": "FAIL",
        },
        "fact_rework": {
            "rework_id": "rw-1",
            "dataset_version_id": "c02-test",
            "inspection_id": "qi-1",
            "work_order_id": "wo-1",
            "work_center_id": "wc-1",
            "rework_start_at": datetime(2026, 1, 17, tzinfo=utc),
            "rework_end_at": datetime(2026, 1, 18, tzinfo=utc),
            "rework_quantity": 1,
            "rework_reason": "Synthetic correction",
        },
        "fact_delivery": {
            "delivery_id": "del-1",
            "dataset_version_id": "c02-test",
            "sales_order_id": "so-1",
            "delivery_at": datetime(2026, 1, 25, tzinfo=utc),
            "delivered_quantity": 10,
        },
    }

    for table_name in (
        "dataset_version",
        "dim_product",
        "dim_material",
        "dim_supplier",
        "dim_customer",
        "dim_work_center",
        "bridge_product_material",
        "fact_sales_order",
        "fact_purchase_order",
        "fact_work_order",
        "fact_operation",
        "fact_material_requirement",
        "fact_inventory_snapshot",
        "fact_quality_inspection",
        "fact_rework",
        "fact_delivery",
    ):
        connection.execute(Base.metadata.tables[table_name].insert(), rows[table_name])


@pytest.fixture
def schema_engine() -> Iterator[Engine]:
    settings = _settings_or_skip()
    command.upgrade(_alembic_config(), "head")
    engine = create_database_engine(settings)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def digital_thread_connection(schema_engine: Engine) -> Iterator[Connection]:
    with schema_engine.connect() as connection:
        transaction = connection.begin()
        _seed_digital_thread(connection)
        try:
            yield connection
        finally:
            transaction.rollback()


def test_postgresql_schema_matches_canonical_metadata(schema_engine: Engine) -> None:
    inspector = inspect(schema_engine)
    domain_tables = {
        table_name
        for table_name in inspector.get_table_names()
        if table_name == "dataset_version"
        or table_name.startswith(("dim_", "bridge_", "fact_"))
    }
    assert domain_tables == C02_TABLES

    for table_name, model_table in Base.metadata.tables.items():
        database_columns = {column["name"]: column for column in inspector.get_columns(table_name)}
        assert set(database_columns) == set(model_table.columns.keys())
        for model_column in model_table.columns:
            database_column = database_columns[model_column.name]
            assert database_column["nullable"] is model_column.nullable
            assert _type_signature(database_column["type"]) == _type_signature(model_column.type)
            if isinstance(model_column.type, DateTime):
                assert isinstance(database_column["type"], DateTime)
                assert database_column["type"].timezone is True

        primary_key = inspector.get_pk_constraint(table_name)
        assert primary_key["name"] == str(model_table.primary_key.name)
        assert tuple(primary_key["constrained_columns"]) == tuple(
            column.name for column in model_table.primary_key.columns
        )

        actual_foreign_keys = {
            (
                foreign_key["name"],
                tuple(foreign_key["constrained_columns"]),
                foreign_key["referred_table"],
                tuple(foreign_key["referred_columns"]),
            )
            for foreign_key in inspector.get_foreign_keys(table_name)
        }
        expected_foreign_keys = {
            (
                str(constraint.name),
                tuple(column.name for column in constraint.columns),
                next(iter(constraint.elements)).column.table.name,
                tuple(element.column.name for element in constraint.elements),
            )
            for constraint in model_table.foreign_key_constraints
        }
        assert actual_foreign_keys == expected_foreign_keys

        actual_uniques = {
            (unique["name"], tuple(unique["column_names"]))
            for unique in inspector.get_unique_constraints(table_name)
        }
        expected_uniques = {
            (str(constraint.name), tuple(column.name for column in constraint.columns))
            for constraint in model_table.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        assert actual_uniques == expected_uniques

        actual_checks = {check["name"] for check in inspector.get_check_constraints(table_name)}
        expected_checks = {
            str(constraint.name)
            for constraint in model_table.constraints
            if isinstance(constraint, CheckConstraint)
        }
        assert actual_checks == expected_checks

        unexpected_indexes = [
            index
            for index in inspector.get_indexes(table_name)
            if not index.get("duplicates_constraint")
        ]
        assert unexpected_indexes == []


def test_migration_round_trip_preserves_week_1_pgvector() -> None:
    settings = _settings_or_skip()
    config = _alembic_config()
    engine = create_database_engine(settings)
    try:
        command.upgrade(config, "head")
        assert C02_TABLES <= set(inspect(engine).get_table_names())

        command.downgrade(config, "0001_enable_pgvector")
        assert C02_TABLES.isdisjoint(inspect(engine).get_table_names())
        with engine.connect() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
        assert revision == "0001_enable_pgvector"
        assert is_pgvector_enabled(engine) is True

        command.upgrade(config, "head")
        assert C02_TABLES <= set(inspect(engine).get_table_names())
        with engine.connect() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
        assert revision == C02_REVISION
    finally:
        engine.dispose()


def test_minimal_rows_form_both_required_digital_thread_paths(
    digital_thread_connection: Connection,
) -> None:
    for table_name in C02_TABLES:
        count = digital_thread_connection.execute(
            text(f"SELECT count(*) FROM {table_name}")
        ).scalar_one()
        assert count == 1


def _assert_rejected(
    connection: Connection,
    table_name: str,
    values: dict[str, Any],
) -> None:
    savepoint = connection.begin_nested()
    try:
        with pytest.raises(IntegrityError):
            connection.execute(Base.metadata.tables[table_name].insert(), values)
    finally:
        savepoint.rollback()


def test_postgresql_rejects_representative_invalid_rows(
    digital_thread_connection: Connection,
) -> None:
    utc = UTC
    dataset_base = {
        "seed": 1,
        "generator_version": "0.1.0",
        "profile": "test",
        "period_start": date(2026, 1, 1),
        "period_end": date(2026, 2, 1),
        "generated_at": datetime(2026, 1, 1, tzinfo=utc),
        "content_hash": "b" * 64,
        "row_count_total": 0,
    }
    dataset_invalid_rows: tuple[tuple[str, dict[str, Any]], ...] = (
        ("bad-profile", {"profile": "invalid"}),
        ("bad-seed", {"seed": -1}),
        ("bad-period", {"period_end": date(2025, 12, 31)}),
    )
    for dataset_id, overrides in dataset_invalid_rows:
        _assert_rejected(
            digital_thread_connection,
            "dataset_version",
            {"dataset_version_id": dataset_id, **dataset_base, **overrides},
        )

    product_base = {
        "dataset_version_id": "c02-test",
        "product_family": "GROUNDING_SWITCH",
        "model_name": "Invalid Test Product",
        "complexity_class": "LOW",
        "standard_cycle_hours": Decimal("1.00"),
        "active_from": date(2026, 1, 1),
        "active_to": None,
    }
    _assert_rejected(
        digital_thread_connection,
        "dim_product",
        {
            "product_id": "prod-zero-cycle",
            "product_code": "PROD-ZERO",
            **product_base,
            "standard_cycle_hours": Decimal("0"),
        },
    )
    _assert_rejected(
        digital_thread_connection,
        "dim_product",
        {"product_id": "prod-duplicate", "product_code": "PROD-001", **product_base},
    )
    _assert_rejected(
        digital_thread_connection,
        "bridge_product_material",
        {
            "dataset_version_id": "c02-test",
            "product_id": "prod-1",
            "material_id": "mat-1",
            "quantity_per_unit": Decimal("0"),
            "is_critical": True,
        },
    )

    sales_base = {
        "dataset_version_id": "c02-test",
        "customer_id": "cus-1",
        "product_id": "prod-1",
        "order_at": datetime(2026, 1, 2, tzinfo=utc),
        "promised_delivery_at": datetime(2026, 2, 1, tzinfo=utc),
        "order_quantity": 1,
        "priority": "NORMAL",
        "status": "OPEN",
    }
    sales_order_invalid_rows: tuple[tuple[str, dict[str, Any]], ...] = (
        ("so-zero", {"order_quantity": 0}),
        ("so-window", {"promised_delivery_at": datetime(2026, 1, 1, tzinfo=utc)}),
        ("so-priority", {"priority": "URGENT"}),
        ("so-status", {"status": "UNKNOWN"}),
    )
    for order_id, overrides in sales_order_invalid_rows:
        _assert_rejected(
            digital_thread_connection,
            "fact_sales_order",
            {"sales_order_id": order_id, **sales_base, **overrides},
        )

    _assert_rejected(
        digital_thread_connection,
        "fact_purchase_order",
        {
            "purchase_order_id": "po-over-received",
            "dataset_version_id": "c02-test",
            "supplier_id": "sup-1",
            "material_id": "mat-1",
            "ordered_at": datetime(2026, 1, 2, tzinfo=utc),
            "promised_receipt_at": datetime(2026, 1, 12, tzinfo=utc),
            "actual_receipt_at": None,
            "ordered_quantity": Decimal("1"),
            "received_quantity": Decimal("2"),
            "status": "OPEN",
        },
    )
    _assert_rejected(
        digital_thread_connection,
        "fact_work_order",
        {
            "work_order_id": "wo-over-completed",
            "dataset_version_id": "c02-test",
            "sales_order_id": "so-1",
            "product_id": "prod-1",
            "planned_start_at": datetime(2026, 1, 15, tzinfo=utc),
            "planned_end_at": datetime(2026, 1, 20, tzinfo=utc),
            "actual_start_at": None,
            "actual_end_at": None,
            "planned_quantity": 1,
            "completed_quantity": 2,
            "status": "PLANNED",
        },
    )
    _assert_rejected(
        digital_thread_connection,
        "fact_operation",
        {
            "operation_id": "op-duplicate-sequence",
            "dataset_version_id": "c02-test",
            "work_order_id": "wo-1",
            "work_center_id": "wc-1",
            "sequence_number": 1,
            "planned_start_at": datetime(2026, 1, 15, tzinfo=utc),
            "planned_end_at": datetime(2026, 1, 16, tzinfo=utc),
            "actual_start_at": None,
            "actual_end_at": None,
            "status": "PLANNED",
        },
    )
    _assert_rejected(
        digital_thread_connection,
        "fact_inventory_snapshot",
        {
            "inventory_snapshot_id": "inv-over-reserved",
            "dataset_version_id": "c02-test",
            "material_id": "mat-1",
            "snapshot_at": datetime(2026, 1, 14, tzinfo=utc),
            "on_hand_quantity": Decimal("1"),
            "reserved_quantity": Decimal("2"),
        },
    )

    inspection_base = {
        "dataset_version_id": "c02-test",
        "work_order_id": "wo-1",
        "operation_id": "op-1",
        "inspection_at": datetime(2026, 1, 17, tzinfo=utc),
        "inspection_type": "FINAL",
        "inspected_quantity": 10,
        "passed_quantity": 10,
        "failed_quantity": 0,
        "defect_category": None,
        "severity": None,
        "result": "PASS",
    }
    inspection_invalid_rows: tuple[tuple[str, dict[str, Any]], ...] = (
        ("qi-unbalanced", {"passed_quantity": 8}),
        ("qi-pass-failures", {"passed_quantity": 9, "failed_quantity": 1}),
        ("qi-fail-zero", {"result": "FAIL"}),
    )
    for inspection_id, overrides in inspection_invalid_rows:
        _assert_rejected(
            digital_thread_connection,
            "fact_quality_inspection",
            {"inspection_id": inspection_id, **inspection_base, **overrides},
        )

    rework_base = {
        "dataset_version_id": "c02-test",
        "inspection_id": "qi-1",
        "work_order_id": "wo-1",
        "work_center_id": "wc-1",
        "rework_start_at": datetime(2026, 1, 17, tzinfo=utc),
        "rework_end_at": datetime(2026, 1, 18, tzinfo=utc),
        "rework_quantity": 1,
        "rework_reason": "Synthetic correction",
    }
    _assert_rejected(
        digital_thread_connection,
        "fact_rework",
        {"rework_id": "rw-zero", **rework_base, "rework_quantity": 0},
    )
    _assert_rejected(
        digital_thread_connection,
        "fact_rework",
        {
            "rework_id": "rw-window",
            **rework_base,
            "rework_end_at": datetime(2026, 1, 16, tzinfo=utc),
        },
    )
    _assert_rejected(
        digital_thread_connection,
        "fact_delivery",
        {
            "delivery_id": "del-zero",
            "dataset_version_id": "c02-test",
            "sales_order_id": "so-1",
            "delivery_at": datetime(2026, 1, 25, tzinfo=utc),
            "delivered_quantity": 0,
        },
    )
