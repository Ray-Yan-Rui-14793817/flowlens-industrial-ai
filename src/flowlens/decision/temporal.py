"""Pure field-level decision-time projection for the frozen C02 source matrix."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Final
from zoneinfo import ZoneInfo

from flowlens.decision.primitives import ScalarValue, validate_aware_datetime

BUSINESS_TIMEZONE: Final = ZoneInfo("Asia/Shanghai")

SOURCE_FIELDS: Final[Mapping[str, tuple[str, ...]]] = {
    "dim_product": (
        "product_id",
        "product_code",
        "product_family",
        "complexity_class",
        "standard_cycle_hours",
        "active_from",
    ),
    "dim_customer": ("customer_id", "customer_code", "customer_segment", "region", "active_from"),
    "dim_work_center": (
        "work_center_id",
        "work_center_code",
        "process_type",
        "line_group",
        "daily_capacity_hours",
        "active_from",
    ),
    "dim_material": (
        "material_id",
        "material_code",
        "material_group",
        "criticality",
        "standard_lead_time_days",
        "unit_of_measure",
    ),
    "dim_supplier": ("supplier_id", "supplier_code", "supplier_tier", "region", "active_from"),
    "bridge_product_material": ("product_id", "material_id", "quantity_per_unit", "is_critical"),
    "fact_sales_order": (
        "sales_order_id",
        "customer_id",
        "product_id",
        "order_at",
        "promised_delivery_at",
        "order_quantity",
        "priority",
    ),
    "fact_work_order": (
        "work_order_id",
        "sales_order_id",
        "product_id",
        "planned_start_at",
        "planned_end_at",
        "planned_quantity",
        "actual_start_at",
        "actual_end_at",
        "completed_quantity",
    ),
    "fact_operation": (
        "operation_id",
        "work_order_id",
        "work_center_id",
        "sequence_number",
        "planned_start_at",
        "planned_end_at",
        "actual_start_at",
        "actual_end_at",
    ),
    "fact_material_requirement": (
        "material_requirement_id",
        "work_order_id",
        "material_id",
        "required_quantity",
        "need_by_at",
    ),
    "fact_purchase_order": (
        "purchase_order_id",
        "supplier_id",
        "material_id",
        "ordered_at",
        "promised_receipt_at",
        "ordered_quantity",
        "actual_receipt_at",
        "received_quantity",
    ),
    "fact_inventory_snapshot": (
        "inventory_snapshot_id",
        "material_id",
        "snapshot_at",
        "on_hand_quantity",
        "reserved_quantity",
    ),
    "fact_quality_inspection": (
        "inspection_id",
        "work_order_id",
        "operation_id",
        "inspection_at",
        "inspection_type",
        "inspected_quantity",
        "passed_quantity",
        "failed_quantity",
        "defect_category",
        "severity",
        "result",
    ),
    "fact_rework": (
        "rework_id",
        "inspection_id",
        "work_order_id",
        "work_center_id",
        "rework_start_at",
        "rework_end_at",
        "rework_quantity",
        "rework_reason",
    ),
    "fact_delivery": ("delivery_id", "sales_order_id", "delivery_at", "delivered_quantity"),
}

_MASTER_ACTIVE = frozenset({"dim_product", "dim_customer", "dim_work_center", "dim_supplier"})
_BASELINE = frozenset({"dim_material", "bridge_product_material"})
_PLAN = frozenset({"fact_work_order", "fact_operation", "fact_material_requirement"})
_EVENT_TIME: Final[Mapping[str, str]] = {
    "fact_inventory_snapshot": "snapshot_at",
    "fact_quality_inspection": "inspection_at",
    "fact_delivery": "delivery_at",
}


class C02BuildError(ValueError):
    """An observable fail-closed C02 code and loop state."""

    def __init__(self, code: str, state: str) -> None:
        self.code = code
        self.state = state
        super().__init__(f"{state}: {code}")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProjectedSourceField:
    source_entity: str
    source_record_id: str
    source_field: str
    value: ScalarValue
    observed_at: datetime | None
    available_at: datetime

    def __post_init__(self) -> None:
        if self.source_field not in SOURCE_FIELDS.get(self.source_entity, ()):
            raise C02BuildError("SOURCE_FIELD_NOT_AUTHORIZED", "BLOCKED_CONTRACT")
        validate_aware_datetime(self.available_at, "available_at")
        if self.observed_at is not None:
            validate_aware_datetime(self.observed_at, "observed_at")


def _business_start(day: date) -> datetime:
    return datetime.combine(day, time.min, BUSINESS_TIMEZONE)


def validate_as_of(as_of_time: datetime, period_start: date, period_end: date) -> None:
    validate_aware_datetime(as_of_time, "as_of_time")
    upper = datetime.combine(period_end, time.max, BUSINESS_TIMEZONE)
    if not _business_start(period_start) <= as_of_time <= upper:
        raise C02BuildError("AS_OF_OUTSIDE_DATASET_HORIZON", "BLOCKED_CONTEXT")


def _event_time(value: ScalarValue) -> datetime:
    if not isinstance(value, datetime):
        raise C02BuildError("TEMPORAL_ADMISSION_VIOLATION", "BLOCKED_TEMPORAL")
    validate_aware_datetime(value, "event time")
    return value


def project_record(
    source_entity: str,
    source_record_id: str,
    fields: Mapping[str, ScalarValue],
    *,
    as_of_time: datetime,
    period_start: date,
    target_order_at: datetime,
) -> tuple[ProjectedSourceField, ...]:
    """Admit only whitelisted fields whose business availability is no later than as-of.

    The DB adapter separately masks future actual values in SQL; this projector is
    the second temporal gate and is also usable with in-memory test records.
    """
    if source_entity not in SOURCE_FIELDS:
        raise C02BuildError("SOURCE_ENTITY_NOT_AUTHORIZED", "BLOCKED_CONTRACT")
    validate_aware_datetime(as_of_time, "as_of_time")
    validate_aware_datetime(target_order_at, "target_order_at")
    if source_entity in _MASTER_ACTIVE:
        active_from = fields.get("active_from")
        if not isinstance(active_from, date) or isinstance(active_from, datetime):
            raise C02BuildError("TEMPORAL_ADMISSION_VIOLATION", "BLOCKED_TEMPORAL")
        common_time = _business_start(active_from)
    elif source_entity in _BASELINE:
        common_time = _business_start(period_start)
    elif source_entity == "fact_sales_order":
        common_time = _event_time(fields.get("order_at"))
    elif source_entity in _PLAN:
        common_time = target_order_at
    elif source_entity == "fact_purchase_order":
        common_time = _event_time(fields.get("ordered_at"))
    elif source_entity == "fact_rework":
        common_time = _event_time(fields.get("rework_start_at"))
    else:
        common_time = _event_time(fields.get(_EVENT_TIME[source_entity]))
    if common_time > as_of_time:
        return ()

    result: list[ProjectedSourceField] = []
    for field in SOURCE_FIELDS[source_entity]:
        if field not in fields:
            raise C02BuildError("SOURCE_FIELD_MISSING", "BLOCKED_CONTRACT")
        value = fields[field]
        if source_entity in ("fact_work_order", "fact_operation") and field in (
            "actual_start_at",
            "actual_end_at",
            "completed_quantity",
        ):
            gate_field = "actual_end_at" if field == "completed_quantity" else field
            gate = fields[gate_field]
            if gate is None:
                continue
            available_at = _event_time(gate)
        elif source_entity == "fact_purchase_order" and field in (
            "actual_receipt_at",
            "received_quantity",
        ):
            gate = fields["actual_receipt_at"]
            if gate is None:
                continue
            available_at = _event_time(gate)
        elif source_entity == "fact_rework" and field == "rework_end_at":
            if value is None:
                continue
            available_at = _event_time(value)
        else:
            available_at = common_time
        if available_at > as_of_time:
            continue
        plan_field = source_entity in _PLAN and field not in (
            "actual_start_at",
            "actual_end_at",
            "completed_quantity",
        )
        observed_at = (
            None if source_entity in _MASTER_ACTIVE | _BASELINE or plan_field else available_at
        )
        result.append(
            ProjectedSourceField(
                source_entity=source_entity,
                source_record_id=source_record_id,
                source_field=field,
                value=value,
                observed_at=observed_at,
                available_at=available_at,
            )
        )
    return tuple(result)
