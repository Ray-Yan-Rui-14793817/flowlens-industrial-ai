"""Canonical ordering and SHA-256 hashing for generated business content."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Final

from flowlens.data import Base

CANONICAL_TABLE_ORDER: Final[tuple[str, ...]] = (
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
)

type CanonicalScalar = None | bool | int | str
type CanonicalRow = list[tuple[str, CanonicalScalar]]
type CanonicalPayload = list[tuple[str, list[CanonicalRow]]]


def normalize_scalar(value: object) -> CanonicalScalar:
    """Normalize one ORM scalar without locale or representation ambiguity."""

    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, Decimal):
        rendered = format(value, "f")
        if "." in rendered:
            rendered = rendered.rstrip("0").rstrip(".")
        return "0" if rendered in {"", "-0"} else rendered
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("canonical hashing requires timezone-aware datetimes")
        return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(f"unsupported canonical scalar type: {type(value).__name__}")


def _primary_key(row: Base) -> tuple[str, ...]:
    return tuple(str(getattr(row, column.name)) for column in row.__mapper__.primary_key)


def canonicalize_rows(
    rows_by_table: Mapping[str, Sequence[Base]],
) -> dict[str, tuple[Base, ...]]:
    """Return all business rows in fixed table and full-primary-key order."""

    actual_tables = set(rows_by_table)
    expected_tables = set(CANONICAL_TABLE_ORDER)
    if actual_tables != expected_tables:
        missing = sorted(expected_tables - actual_tables)
        extra = sorted(actual_tables - expected_tables)
        raise ValueError(f"business table set mismatch; missing={missing}, extra={extra}")
    return {
        table_name: tuple(sorted(rows_by_table[table_name], key=_primary_key))
        for table_name in CANONICAL_TABLE_ORDER
    }


def canonical_business_payload(rows_by_table: Mapping[str, Sequence[Base]]) -> CanonicalPayload:
    """Build the explicit column-ordered payload used for reproducibility."""

    ordered = canonicalize_rows(rows_by_table)
    payload: CanonicalPayload = []
    for table_name in CANONICAL_TABLE_ORDER:
        table_rows: list[CanonicalRow] = []
        for row in ordered[table_name]:
            table_rows.append(
                [
                    (column.name, normalize_scalar(getattr(row, column.name)))
                    for column in row.__mapper__.columns
                ]
            )
        payload.append((table_name, table_rows))
    return payload


def canonical_content_hash(rows_by_table: Mapping[str, Sequence[Base]]) -> str:
    """Hash all non-metadata business rows with the frozen C03 convention."""

    payload = canonical_business_payload(rows_by_table)
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
