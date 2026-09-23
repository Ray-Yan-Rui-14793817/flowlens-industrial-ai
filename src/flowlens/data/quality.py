"""Public, HGT-independent integrity checks over the frozen manufacturing rows."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import cast

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)

from flowlens.data import Base
from flowlens.data.generation import GeneratedDataset
from flowlens.data.generation.canonical import CANONICAL_TABLE_ORDER, canonical_content_hash
from flowlens.data.models import (
    Customer,
    Delivery,
    InventorySnapshot,
    Material,
    MaterialRequirement,
    Operation,
    Product,
    ProductMaterial,
    PurchaseOrder,
    QualityInspection,
    Rework,
    SalesOrder,
    Supplier,
    WorkCenter,
    WorkOrder,
)


@dataclass(frozen=True, slots=True)
class QualityCheck:
    category: str
    name: str
    violations: int

    @property
    def status(self) -> str:
        return "FAIL" if self.violations else "PASS"


@dataclass(frozen=True, slots=True)
class QualityResult:
    """Diagnostics contain counts and fixed check names, never row values/identities."""

    checks: tuple[QualityCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.violations == 0 for check in self.checks)

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"


def _valid_scalar(column: Column[object], value: object) -> bool:
    if value is None:
        return bool(column.nullable)
    kind = column.type
    if isinstance(kind, Boolean):
        return type(value) is bool
    if isinstance(kind, Integer):
        bits = 64 if isinstance(kind, BigInteger) else 32
        return type(value) is int and -(2 ** (bits - 1)) <= value < 2 ** (bits - 1)
    if isinstance(kind, DateTime):
        return isinstance(value, datetime) and value.utcoffset() is not None
    if isinstance(kind, Date):
        return type(value) is date
    if isinstance(kind, String):
        return isinstance(value, str) and (kind.length is None or len(value) <= kind.length)
    if isinstance(kind, Numeric):
        if not isinstance(value, Decimal) or not value.is_finite():
            return False
        assert kind.precision is not None and kind.scale is not None
        # Reject values PostgreSQL would round or overflow; never convert to float.
        return abs(value) < Decimal(10) ** (
            kind.precision - kind.scale
        ) and value == value.quantize(Decimal(1).scaleb(-kind.scale))
    return False


def validate_dataset(dataset: GeneratedDataset) -> QualityResult:
    """Check schema, all frozen FKs/keys, business rules, counts and C03 hash.

    Invalid structure/scalars stop dependent checks, not the FAIL result. This
    prevents comparisons/hashing of malformed values and avoids printing them.
    """
    if not isinstance(dataset, GeneratedDataset):
        raise TypeError("public validation requires GeneratedDataset")
    checks: list[QualityCheck] = []

    def record(category: str, name: str, violations: int) -> None:
        checks.append(QualityCheck(category, name, violations))

    record(
        "dataset",
        "business_table_set",
        int(set(dataset.rows_by_table) != set(CANONICAL_TABLE_ORDER)),
    )
    if checks[-1].violations:
        return QualityResult(tuple(checks))
    all_rows = {
        "dataset_version": (dataset.dataset_version,),
        **{name: dataset.rows_by_table[name] for name in CANONICAL_TABLE_ORDER},
    }
    model_types = {mapper.class_.__tablename__: mapper.class_ for mapper in Base.registry.mappers}
    for name, rows in all_rows.items():
        wrong_type = sum(type(row) is not model_types[name] for row in rows)
        record("schema", f"{name}.row_type", wrong_type)
        if wrong_type:
            continue
        table = Base.metadata.tables[name]
        record(
            "schema",
            f"{name}.scalar_types",
            sum(
                not _valid_scalar(column, getattr(row, column.name))
                for row in rows
                for column in table.columns
            ),
        )
    if any(check.violations for check in checks):
        return QualityResult(tuple(checks))

    # Key indexes are built once, making referential checks linear in row count.
    targets = {
        (name, column.name): {getattr(row, column.name) for row in rows}
        for name, rows in all_rows.items()
        for column in Base.metadata.tables[name].columns
        if column.primary_key
    }
    for name, rows in all_rows.items():
        table = Base.metadata.tables[name]
        keys = [tuple(getattr(row, c.name) for c in table.primary_key) for row in rows]
        record("referential", f"{name}.primary_key", len(keys) - len(set(keys)))
        for constraint in sorted(table.constraints, key=lambda item: str(item.name)):
            if isinstance(constraint, UniqueConstraint):
                keys = [tuple(getattr(row, c.name) for c in constraint.columns) for row in rows]
                record("referential", str(constraint.name), len(keys) - len(set(keys)))
        for fk in sorted(table.foreign_keys, key=lambda item: item.parent.name):
            allowed = targets[(fk.column.table.name, fk.column.name)]
            record(
                "referential",
                f"{name}.{fk.parent.name}",
                sum(
                    getattr(row, fk.parent.name) is not None
                    and getattr(row, fk.parent.name) not in allowed
                    for row in rows
                ),
            )

    def typed_rows[T: Base](model: type[T]) -> tuple[T, ...]:
        return cast(tuple[T, ...], dataset.rows_by_table[model.__tablename__])

    def rule[T: Base](
        category: str, name: str, values: Iterable[T], predicate: Callable[[T], bool]
    ) -> None:
        record(category, name, sum(not predicate(row) for row in values))

    metadata = dataset.dataset_version
    record(
        "dataset",
        "metadata",
        int(
            not (
                metadata.period_start < metadata.period_end
                and metadata.seed >= 0
                and metadata.profile in {"test", "ci", "demo"}
                and bool(metadata.generator_version.strip())
                and bool(metadata.dataset_version_id.strip())
            )
        ),
    )
    record(
        "dataset",
        "row_count_total",
        int(
            metadata.row_count_total
            != sum(len(values) for values in dataset.rows_by_table.values())
        ),
    )
    record(
        "dataset",
        "canonical_content_hash",
        int(canonical_content_hash(dataset.rows_by_table) != metadata.content_hash),
    )
    for name in CANONICAL_TABLE_ORDER:
        values = dataset.rows_by_table[name]
        record(
            "dataset",
            f"{name}.ownership",
            sum(
                getattr(row, "dataset_version_id", None) != metadata.dataset_version_id
                for row in values
            ),
        )

    rule(
        "quantity", "product.cycle_hours", typed_rows(Product), lambda r: r.standard_cycle_hours > 0
    )
    rule(
        "schema",
        "product.enums",
        typed_rows(Product),
        lambda r: (
            r.product_family in {"GROUNDING_SWITCH", "ISOLATION_SWITCH", "ELECTRIC_CHASSIS"}
            and r.complexity_class in {"LOW", "MEDIUM", "HIGH"}
        ),
    )
    rule(
        "quantity",
        "material.lead_time",
        typed_rows(Material),
        lambda r: r.standard_lead_time_days > 0,
    )
    rule(
        "schema",
        "material.criticality",
        typed_rows(Material),
        lambda r: r.criticality in {"LOW", "MEDIUM", "HIGH", "CRITICAL"},
    )
    rule(
        "quantity",
        "work_center.capacity",
        typed_rows(WorkCenter),
        lambda r: r.daily_capacity_hours > 0,
    )
    rule(
        "schema",
        "work_center.process",
        typed_rows(WorkCenter),
        lambda r: r.process_type in {"MACHINING", "WELDING", "ASSEMBLY", "INSPECTION", "PACKING"},
    )
    for model in (Product, Customer, Supplier, WorkCenter):
        rule(
            "temporal",
            f"{model.__tablename__}.active_window",
            cast(tuple[Product | Customer | Supplier | WorkCenter, ...], typed_rows(model)),
            lambda r: r.active_to is None or r.active_to >= r.active_from,
        )
    rule("quantity", "bom.quantity", typed_rows(ProductMaterial), lambda r: r.quantity_per_unit > 0)
    rule("quantity", "sales.quantity", typed_rows(SalesOrder), lambda r: r.order_quantity > 0)
    rule(
        "temporal",
        "sales.window",
        typed_rows(SalesOrder),
        lambda r: r.order_at < r.promised_delivery_at,
    )
    rule(
        "schema",
        "sales.enums",
        typed_rows(SalesOrder),
        lambda r: (
            r.priority in {"NORMAL", "HIGH", "EXPEDITE"}
            and r.status
            in {"OPEN", "IN_PRODUCTION", "PARTIALLY_DELIVERED", "DELIVERED", "CANCELLED"}
        ),
    )
    rule(
        "quantity",
        "purchase.quantity",
        typed_rows(PurchaseOrder),
        lambda r: r.ordered_quantity > 0 and 0 <= r.received_quantity <= r.ordered_quantity,
    )
    rule(
        "temporal",
        "purchase.promised",
        typed_rows(PurchaseOrder),
        lambda r: r.ordered_at < r.promised_receipt_at,
    )
    rule(
        "temporal",
        "purchase.actual",
        typed_rows(PurchaseOrder),
        lambda r: r.actual_receipt_at is None or r.actual_receipt_at >= r.ordered_at,
    )
    rule(
        "quantity",
        "work.quantity",
        typed_rows(WorkOrder),
        lambda r: r.planned_quantity > 0 and 0 <= r.completed_quantity <= r.planned_quantity,
    )
    rule(
        "schema",
        "work.status",
        typed_rows(WorkOrder),
        lambda r: r.status in {"PLANNED", "RELEASED", "IN_PROGRESS", "COMPLETED", "CANCELLED"},
    )
    rule(
        "temporal",
        "work.end_requires_start",
        typed_rows(WorkOrder),
        lambda r: r.actual_end_at is None or r.actual_start_at is not None,
    )
    for timed_model in (WorkOrder, Operation):
        rule(
            "temporal",
            f"{timed_model.__tablename__}.planned_window",
            cast(tuple[WorkOrder | Operation, ...], typed_rows(timed_model)),
            lambda r: r.planned_start_at < r.planned_end_at,
        )
        rule(
            "temporal",
            f"{timed_model.__tablename__}.actual_window",
            cast(tuple[WorkOrder | Operation, ...], typed_rows(timed_model)),
            lambda r: (
                r.actual_start_at is None
                or r.actual_end_at is None
                or r.actual_start_at <= r.actual_end_at
            ),
        )
    rule("quantity", "operation.sequence", typed_rows(Operation), lambda r: r.sequence_number > 0)
    rule(
        "quantity",
        "requirement.quantity",
        typed_rows(MaterialRequirement),
        lambda r: r.required_quantity > 0,
    )
    rule(
        "quantity",
        "inventory.quantity",
        typed_rows(InventorySnapshot),
        lambda r: r.on_hand_quantity >= 0 and 0 <= r.reserved_quantity <= r.on_hand_quantity,
    )
    rule(
        "quantity",
        "inspection.balance",
        typed_rows(QualityInspection),
        lambda r: (
            r.inspected_quantity > 0
            and r.passed_quantity >= 0
            and r.failed_quantity >= 0
            and r.passed_quantity + r.failed_quantity == r.inspected_quantity
        ),
    )
    rule(
        "quantity",
        "inspection.result",
        typed_rows(QualityInspection),
        lambda r: (
            (r.result == "PASS" and r.failed_quantity == 0)
            or (r.result == "FAIL" and r.failed_quantity > 0)
        ),
    )
    rule("quantity", "rework.quantity", typed_rows(Rework), lambda r: r.rework_quantity > 0)
    rule(
        "temporal",
        "rework.window",
        typed_rows(Rework),
        lambda r: r.rework_start_at <= r.rework_end_at,
    )
    rule("quantity", "delivery.quantity", typed_rows(Delivery), lambda r: r.delivered_quantity > 0)

    # Missing parents are already failures above; skip dependent comparisons only.
    sales = {r.sales_order_id: r for r in typed_rows(SalesOrder)}
    work = {r.work_order_id: r for r in typed_rows(WorkOrder)}
    operations = {r.operation_id: r for r in typed_rows(Operation)}
    inspections = {r.inspection_id: r for r in typed_rows(QualityInspection)}
    rule(
        "referential",
        "work.product_matches_sales",
        typed_rows(WorkOrder),
        lambda r: (
            r.sales_order_id not in sales or r.product_id == sales[r.sales_order_id].product_id
        ),
    )
    rule(
        "referential",
        "inspection.operation_ownership",
        typed_rows(QualityInspection),
        lambda r: (
            r.operation_id not in operations
            or operations[r.operation_id].work_order_id == r.work_order_id
        ),
    )
    rule(
        "referential",
        "rework.inspection_ownership",
        typed_rows(Rework),
        lambda r: (
            r.inspection_id not in inspections
            or inspections[r.inspection_id].work_order_id == r.work_order_id
        ),
    )

    def inspection_time(row: QualityInspection) -> bool:
        parent = work.get(row.work_order_id)
        return (
            parent is None
            or parent.actual_start_at is None
            or row.inspection_at >= parent.actual_start_at
        )

    rule("temporal", "inspection.after_work_start", typed_rows(QualityInspection), inspection_time)
    rule(
        "temporal",
        "rework.after_inspection",
        typed_rows(Rework),
        lambda r: (
            r.inspection_id not in inspections
            or r.rework_start_at >= inspections[r.inspection_id].inspection_at
        ),
    )
    rule(
        "quantity",
        "rework.within_failed",
        typed_rows(Rework),
        lambda r: (
            r.inspection_id not in inspections
            or r.rework_quantity <= inspections[r.inspection_id].failed_quantity
        ),
    )
    rule(
        "temporal",
        "delivery.after_order",
        typed_rows(Delivery),
        lambda r: (
            r.sales_order_id not in sales or r.delivery_at >= sales[r.sales_order_id].order_at
        ),
    )
    delivered: dict[str, int] = defaultdict(int)
    for delivery in typed_rows(Delivery):
        delivered[delivery.sales_order_id] += delivery.delivered_quantity
    rule(
        "quantity",
        "delivery.cumulative",
        typed_rows(SalesOrder),
        lambda r: delivered[r.sales_order_id] <= r.order_quantity,
    )
    return QualityResult(tuple(checks))
