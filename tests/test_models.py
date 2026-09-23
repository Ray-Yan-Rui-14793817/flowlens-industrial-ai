"""Contract-fidelity tests for the canonical Week 2 ORM model graph."""

import subprocess
import sys
from pathlib import Path

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
)
from sqlalchemy.sql.sqltypes import TypeEngine

from flowlens.data import Base
from flowlens.data.models import register_models

PROJECT_ROOT = Path(__file__).resolve().parents[1]

register_models()

EXPECTED_COLUMNS: dict[str, dict[str, str]] = {
    "dataset_version": {
        "dataset_version_id": "varchar(64)",
        "seed": "bigint",
        "generator_version": "varchar(32)",
        "profile": "varchar(16)",
        "period_start": "date",
        "period_end": "date",
        "generated_at": "timestamptz",
        "content_hash": "varchar(128)",
        "row_count_total": "bigint",
    },
    "dim_product": {
        "product_id": "varchar(32)",
        "dataset_version_id": "varchar(64)",
        "product_code": "varchar(32)",
        "product_family": "varchar(32)",
        "model_name": "varchar(80)",
        "complexity_class": "varchar(16)",
        "standard_cycle_hours": "numeric(10,2)",
        "active_from": "date",
        "active_to": "date",
    },
    "dim_material": {
        "material_id": "varchar(32)",
        "dataset_version_id": "varchar(64)",
        "material_code": "varchar(32)",
        "material_group": "varchar(40)",
        "criticality": "varchar(16)",
        "standard_lead_time_days": "integer",
        "unit_of_measure": "varchar(16)",
    },
    "dim_supplier": {
        "supplier_id": "varchar(32)",
        "dataset_version_id": "varchar(64)",
        "supplier_code": "varchar(32)",
        "supplier_tier": "varchar(16)",
        "region": "varchar(40)",
        "active_from": "date",
        "active_to": "date",
    },
    "dim_customer": {
        "customer_id": "varchar(32)",
        "dataset_version_id": "varchar(64)",
        "customer_code": "varchar(32)",
        "customer_segment": "varchar(24)",
        "region": "varchar(40)",
        "active_from": "date",
        "active_to": "date",
    },
    "dim_work_center": {
        "work_center_id": "varchar(32)",
        "dataset_version_id": "varchar(64)",
        "work_center_code": "varchar(32)",
        "process_type": "varchar(24)",
        "line_group": "varchar(32)",
        "daily_capacity_hours": "numeric(10,2)",
        "active_from": "date",
        "active_to": "date",
    },
    "bridge_product_material": {
        "dataset_version_id": "varchar(64)",
        "product_id": "varchar(32)",
        "material_id": "varchar(32)",
        "quantity_per_unit": "numeric(12,4)",
        "is_critical": "boolean",
    },
    "fact_sales_order": {
        "sales_order_id": "varchar(40)",
        "dataset_version_id": "varchar(64)",
        "customer_id": "varchar(32)",
        "product_id": "varchar(32)",
        "order_at": "timestamptz",
        "promised_delivery_at": "timestamptz",
        "order_quantity": "integer",
        "priority": "varchar(16)",
        "status": "varchar(24)",
    },
    "fact_purchase_order": {
        "purchase_order_id": "varchar(40)",
        "dataset_version_id": "varchar(64)",
        "supplier_id": "varchar(32)",
        "material_id": "varchar(32)",
        "ordered_at": "timestamptz",
        "promised_receipt_at": "timestamptz",
        "actual_receipt_at": "timestamptz",
        "ordered_quantity": "numeric(14,4)",
        "received_quantity": "numeric(14,4)",
        "status": "varchar(20)",
    },
    "fact_work_order": {
        "work_order_id": "varchar(40)",
        "dataset_version_id": "varchar(64)",
        "sales_order_id": "varchar(40)",
        "product_id": "varchar(32)",
        "planned_start_at": "timestamptz",
        "planned_end_at": "timestamptz",
        "actual_start_at": "timestamptz",
        "actual_end_at": "timestamptz",
        "planned_quantity": "integer",
        "completed_quantity": "integer",
        "status": "varchar(20)",
    },
    "fact_operation": {
        "operation_id": "varchar(48)",
        "dataset_version_id": "varchar(64)",
        "work_order_id": "varchar(40)",
        "work_center_id": "varchar(32)",
        "sequence_number": "integer",
        "planned_start_at": "timestamptz",
        "planned_end_at": "timestamptz",
        "actual_start_at": "timestamptz",
        "actual_end_at": "timestamptz",
        "status": "varchar(20)",
    },
    "fact_material_requirement": {
        "material_requirement_id": "varchar(48)",
        "dataset_version_id": "varchar(64)",
        "work_order_id": "varchar(40)",
        "material_id": "varchar(32)",
        "required_quantity": "numeric(14,4)",
        "need_by_at": "timestamptz",
    },
    "fact_inventory_snapshot": {
        "inventory_snapshot_id": "varchar(48)",
        "dataset_version_id": "varchar(64)",
        "material_id": "varchar(32)",
        "snapshot_at": "timestamptz",
        "on_hand_quantity": "numeric(14,4)",
        "reserved_quantity": "numeric(14,4)",
    },
    "fact_quality_inspection": {
        "inspection_id": "varchar(48)",
        "dataset_version_id": "varchar(64)",
        "work_order_id": "varchar(40)",
        "operation_id": "varchar(48)",
        "inspection_at": "timestamptz",
        "inspection_type": "varchar(20)",
        "inspected_quantity": "integer",
        "passed_quantity": "integer",
        "failed_quantity": "integer",
        "defect_category": "varchar(40)",
        "severity": "varchar(16)",
        "result": "varchar(8)",
    },
    "fact_rework": {
        "rework_id": "varchar(48)",
        "dataset_version_id": "varchar(64)",
        "inspection_id": "varchar(48)",
        "work_order_id": "varchar(40)",
        "work_center_id": "varchar(32)",
        "rework_start_at": "timestamptz",
        "rework_end_at": "timestamptz",
        "rework_quantity": "integer",
        "rework_reason": "varchar(80)",
    },
    "fact_delivery": {
        "delivery_id": "varchar(48)",
        "dataset_version_id": "varchar(64)",
        "sales_order_id": "varchar(40)",
        "delivery_at": "timestamptz",
        "delivered_quantity": "integer",
    },
}

NULLABLE_COLUMNS = {
    ("dim_product", "active_to"),
    ("dim_supplier", "active_to"),
    ("dim_customer", "active_to"),
    ("dim_work_center", "active_to"),
    ("fact_purchase_order", "actual_receipt_at"),
    ("fact_work_order", "actual_start_at"),
    ("fact_work_order", "actual_end_at"),
    ("fact_operation", "actual_start_at"),
    ("fact_operation", "actual_end_at"),
    ("fact_quality_inspection", "operation_id"),
    ("fact_quality_inspection", "defect_category"),
    ("fact_quality_inspection", "severity"),
}

EXPECTED_PRIMARY_KEYS = {
    "dataset_version": ("dataset_version_id",),
    "dim_product": ("product_id",),
    "dim_material": ("material_id",),
    "dim_supplier": ("supplier_id",),
    "dim_customer": ("customer_id",),
    "dim_work_center": ("work_center_id",),
    "bridge_product_material": ("dataset_version_id", "product_id", "material_id"),
    "fact_sales_order": ("sales_order_id",),
    "fact_purchase_order": ("purchase_order_id",),
    "fact_work_order": ("work_order_id",),
    "fact_operation": ("operation_id",),
    "fact_material_requirement": ("material_requirement_id",),
    "fact_inventory_snapshot": ("inventory_snapshot_id",),
    "fact_quality_inspection": ("inspection_id",),
    "fact_rework": ("rework_id",),
    "fact_delivery": ("delivery_id",),
}

EXPECTED_FOREIGN_KEYS: dict[str, set[tuple[str, str]]] = {
    "dataset_version": set(),
    "dim_product": {("dataset_version_id", "dataset_version.dataset_version_id")},
    "dim_material": {("dataset_version_id", "dataset_version.dataset_version_id")},
    "dim_supplier": {("dataset_version_id", "dataset_version.dataset_version_id")},
    "dim_customer": {("dataset_version_id", "dataset_version.dataset_version_id")},
    "dim_work_center": {("dataset_version_id", "dataset_version.dataset_version_id")},
    "bridge_product_material": {
        ("dataset_version_id", "dataset_version.dataset_version_id"),
        ("product_id", "dim_product.product_id"),
        ("material_id", "dim_material.material_id"),
    },
    "fact_sales_order": {
        ("dataset_version_id", "dataset_version.dataset_version_id"),
        ("customer_id", "dim_customer.customer_id"),
        ("product_id", "dim_product.product_id"),
    },
    "fact_purchase_order": {
        ("dataset_version_id", "dataset_version.dataset_version_id"),
        ("supplier_id", "dim_supplier.supplier_id"),
        ("material_id", "dim_material.material_id"),
    },
    "fact_work_order": {
        ("dataset_version_id", "dataset_version.dataset_version_id"),
        ("sales_order_id", "fact_sales_order.sales_order_id"),
        ("product_id", "dim_product.product_id"),
    },
    "fact_operation": {
        ("dataset_version_id", "dataset_version.dataset_version_id"),
        ("work_order_id", "fact_work_order.work_order_id"),
        ("work_center_id", "dim_work_center.work_center_id"),
    },
    "fact_material_requirement": {
        ("dataset_version_id", "dataset_version.dataset_version_id"),
        ("work_order_id", "fact_work_order.work_order_id"),
        ("material_id", "dim_material.material_id"),
    },
    "fact_inventory_snapshot": {
        ("dataset_version_id", "dataset_version.dataset_version_id"),
        ("material_id", "dim_material.material_id"),
    },
    "fact_quality_inspection": {
        ("dataset_version_id", "dataset_version.dataset_version_id"),
        ("work_order_id", "fact_work_order.work_order_id"),
        ("operation_id", "fact_operation.operation_id"),
    },
    "fact_rework": {
        ("dataset_version_id", "dataset_version.dataset_version_id"),
        ("inspection_id", "fact_quality_inspection.inspection_id"),
        ("work_order_id", "fact_work_order.work_order_id"),
        ("work_center_id", "dim_work_center.work_center_id"),
    },
    "fact_delivery": {
        ("dataset_version_id", "dataset_version.dataset_version_id"),
        ("sales_order_id", "fact_sales_order.sales_order_id"),
    },
}

EXPECTED_UNIQUES: dict[str, set[tuple[str, ...]]] = {
    "dim_product": {("dataset_version_id", "product_code")},
    "dim_material": {("dataset_version_id", "material_code")},
    "fact_operation": {("dataset_version_id", "work_order_id", "sequence_number")},
}

EXPECTED_CHECK_SUFFIXES: dict[str, set[str]] = {
    "dataset_version": {"valid_period", "seed_nonnegative", "profile_allowed"},
    "dim_product": {
        "standard_cycle_hours_positive",
        "valid_active_window",
        "product_family_allowed",
        "complexity_class_allowed",
    },
    "dim_material": {"standard_lead_time_days_positive", "criticality_allowed"},
    "dim_supplier": set(),
    "dim_customer": set(),
    "dim_work_center": {"daily_capacity_hours_positive", "process_type_allowed"},
    "bridge_product_material": {"quantity_per_unit_positive"},
    "fact_sales_order": {
        "order_quantity_positive",
        "valid_order_window",
        "priority_allowed",
        "status_allowed",
    },
    "fact_purchase_order": {
        "ordered_quantity_positive",
        "received_quantity_nonnegative",
        "received_quantity_within_ordered",
        "valid_promised_receipt",
        "valid_actual_receipt",
    },
    "fact_work_order": {
        "planned_quantity_positive",
        "completed_quantity_nonnegative",
        "completed_quantity_within_planned",
        "valid_planned_window",
        "actual_end_requires_start",
        "valid_actual_window",
        "status_allowed",
    },
    "fact_operation": {
        "sequence_number_positive",
        "valid_planned_window",
        "valid_actual_window",
    },
    "fact_material_requirement": {"required_quantity_positive"},
    "fact_inventory_snapshot": {
        "on_hand_quantity_nonnegative",
        "reserved_quantity_nonnegative",
        "reserved_quantity_within_on_hand",
    },
    "fact_quality_inspection": {
        "inspected_quantity_positive",
        "passed_quantity_nonnegative",
        "failed_quantity_nonnegative",
        "inspection_quantity_balanced",
        "result_allowed",
        "pass_has_no_failures",
        "fail_has_failures",
    },
    "fact_rework": {"rework_quantity_positive", "valid_rework_window"},
    "fact_delivery": {"delivered_quantity_positive"},
}

FORBIDDEN_COLUMNS = {
    "is_delayed",
    "delay_days",
    "delivery_delay_rate",
    "supplier_risk_score",
    "supplier_on_time_rate",
    "material_availability_ratio",
    "first_pass_yield",
    "rework_rate",
    "delivery_risk_probability",
    "true_root_cause",
    "scenario_id",
    "scenario_name",
    "is_problem_order",
}


def _type_signature(column_type: TypeEngine[object]) -> str:
    if isinstance(column_type, BigInteger):
        return "bigint"
    if isinstance(column_type, Integer):
        return "integer"
    if isinstance(column_type, String):
        return f"varchar({column_type.length})"
    if isinstance(column_type, Numeric):
        return f"numeric({column_type.precision},{column_type.scale})"
    if isinstance(column_type, DateTime):
        return "timestamptz" if column_type.timezone else "timestamp"
    if isinstance(column_type, Date):
        return "date"
    if isinstance(column_type, Boolean):
        return "boolean"
    raise AssertionError(f"Unexpected SQL type: {column_type!r}")


def test_canonical_table_set_and_column_contract() -> None:
    assert set(Base.metadata.tables) == set(EXPECTED_COLUMNS)

    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        table = Base.metadata.tables[table_name]
        assert set(table.columns.keys()) == set(expected_columns)
        for column_name, expected_type in expected_columns.items():
            column = table.columns[column_name]
            assert _type_signature(column.type) == expected_type
            assert column.nullable is ((table_name, column_name) in NULLABLE_COLUMNS)


def test_primary_foreign_and_unique_key_contract() -> None:
    for table_name, expected_pk in EXPECTED_PRIMARY_KEYS.items():
        table = Base.metadata.tables[table_name]
        assert tuple(column.name for column in table.primary_key.columns) == expected_pk

        actual_foreign_keys = {
            (foreign_key.parent.name, foreign_key.target_fullname)
            for foreign_key in table.foreign_keys
        }
        assert actual_foreign_keys == EXPECTED_FOREIGN_KEYS[table_name]

        actual_uniques = {
            tuple(column.name for column in constraint.columns)
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        assert actual_uniques == EXPECTED_UNIQUES.get(table_name, set())


def test_all_frozen_checks_are_present_and_explicitly_named() -> None:
    for table_name, expected_suffixes in EXPECTED_CHECK_SUFFIXES.items():
        table = Base.metadata.tables[table_name]
        checks = {
            str(constraint.name): constraint
            for constraint in table.constraints
            if isinstance(constraint, CheckConstraint)
        }
        assert set(checks) == {
            f"ck_{table_name}_{semantic_name}" for semantic_name in expected_suffixes
        }
        assert all(constraint.name is not None for constraint in checks.values())


def test_schema_has_no_speculative_explicit_indexes() -> None:
    assert all(not table.indexes for table in Base.metadata.tables.values())


def test_operational_schema_contains_no_derived_or_scenario_columns() -> None:
    actual_columns = {
        column.name for table in Base.metadata.tables.values() for column in table.columns
    }
    assert actual_columns.isdisjoint(FORBIDDEN_COLUMNS)


def test_fresh_process_model_registration_is_complete_and_side_effect_free() -> None:
    script = """
import alembic.command
import psycopg
import sqlalchemy

def unexpected_side_effect(*args, **kwargs):
    raise AssertionError("model registration opened or migrated a database")

alembic.command.upgrade = unexpected_side_effect
psycopg.connect = unexpected_side_effect
sqlalchemy.create_engine = unexpected_side_effect
sqlalchemy.MetaData.create_all = unexpected_side_effect

from flowlens.data import Base
from flowlens.data import models as _models

assert len(Base.metadata.tables) == 16
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
