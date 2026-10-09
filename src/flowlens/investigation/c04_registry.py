"""Closed, immutable W04-C04 source and query policy; no source access."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from flowlens.decision.enums import TrustLevel
from flowlens.decision.temporal import SOURCE_FIELDS

C04_SOURCE_REGISTRY_VERSION: Final = "w04-c04-source-registry-v1"
C04_QUERY_CONTRACT_VERSION: Final = "w04-c04-query-v1"
C04_NAVIGATION_CONTRACT_VERSION: Final = "w04-c04-navigation-v1"
C04_ROOT_KEY_NAME: Final = "sales_order_id"
C04_MAX_RECORDS_PER_QUERY: Final = 4096
C04_MAX_OBSERVATIONS_PER_SLICE: Final = 65536


@dataclass(frozen=True, slots=True)
class _QueryProfile:
    requested_fields: tuple[str, ...]
    relationship_code: str
    trust_class: TrustLevel = TrustLevel.DIRECT_FACT


@dataclass(frozen=True, slots=True)
class _SourcePolicy:
    primary_key: str
    traversal_code: str
    profiles: tuple[_QueryProfile, ...]


C04_SOURCE_REGISTRY: Final = MappingProxyType({
    "dim_work_center": _SourcePolicy(
        "work_center_id", "ORDER_WORK_ORDER_OPERATION_WORK_CENTER", (
            _QueryProfile((
                "active_from", "daily_capacity_hours", "line_group", "process_type",
                "work_center_code", "work_center_id",
            ), "MASTER_DATA_CONTEXT"),
        ),
    ),
    "fact_delivery": _SourcePolicy("delivery_id", "ORDER_DELIVERY", (
        _QueryProfile((
            "delivered_quantity", "delivery_at", "delivery_id", "sales_order_id",
        ), "DIRECT_EVENT"),
    )),
    "fact_material_requirement": _SourcePolicy(
        "material_requirement_id", "ORDER_WORK_ORDER_MATERIAL_REQUIREMENT", (
            _QueryProfile((
                "material_id", "material_requirement_id", "need_by_at",
                "required_quantity", "work_order_id",
            ), "DIRECT_FK"),
        ),
    ),
    "fact_operation": _SourcePolicy("operation_id", "ORDER_WORK_ORDER_OPERATION", (
        _QueryProfile((
            "operation_id", "planned_end_at", "planned_start_at", "sequence_number",
            "work_center_id", "work_order_id",
        ), "DIRECT_FK"),
        _QueryProfile(("actual_end_at", "actual_start_at"), "DIRECT_EVENT"),
    )),
    "fact_purchase_order": _SourcePolicy(
        "purchase_order_id", "ORDER_WORK_ORDER_MATERIAL_PURCHASE_ASSOCIATION", (
            _QueryProfile((
                "actual_receipt_at", "material_id", "ordered_at", "ordered_quantity",
                "promised_receipt_at", "purchase_order_id", "received_quantity", "supplier_id",
            ), "MATERIAL_TIME_ASSOCIATION", TrustLevel.ASSOCIATIVE_EVIDENCE),
        ),
    ),
    "fact_quality_inspection": _SourcePolicy(
        "inspection_id", "ORDER_WORK_ORDER_QUALITY_INSPECTION", (
            _QueryProfile((
                "defect_category", "failed_quantity", "inspected_quantity", "inspection_at",
                "inspection_id", "inspection_type", "operation_id", "passed_quantity",
                "result", "severity", "work_order_id",
            ), "DIRECT_EVENT"),
        ),
    ),
    "fact_rework": _SourcePolicy("rework_id", "ORDER_WORK_ORDER_REWORK", (
        _QueryProfile((
            "inspection_id", "rework_end_at", "rework_id", "rework_quantity", "rework_reason",
            "rework_start_at", "work_center_id", "work_order_id",
        ), "DIRECT_EVENT"),
    )),
    "fact_sales_order": _SourcePolicy("sales_order_id", "ORDER_TARGET", (
        _QueryProfile((
            "customer_id", "order_at", "order_quantity", "priority", "product_id",
            "promised_delivery_at", "sales_order_id",
        ), "TARGET_RECORD"),
    )),
    "fact_work_order": _SourcePolicy("work_order_id", "ORDER_WORK_ORDER", (
        _QueryProfile((
            "planned_end_at", "planned_quantity", "planned_start_at", "product_id",
            "sales_order_id", "work_order_id",
        ), "DIRECT_FK"),
        _QueryProfile((
            "actual_end_at", "actual_start_at", "completed_quantity",
        ), "DIRECT_EVENT"),
    )),
})


def _validate_registry() -> None:
    expected = (
        "dim_work_center", "fact_delivery", "fact_material_requirement", "fact_operation",
        "fact_purchase_order", "fact_quality_inspection", "fact_rework", "fact_sales_order",
        "fact_work_order",
    )
    if tuple(C04_SOURCE_REGISTRY) != expected or sum(
        len(policy.profiles) for policy in C04_SOURCE_REGISTRY.values()
    ) != 11:
        raise ValueError("invalid closed C04 source registry")
    for family, policy in C04_SOURCE_REGISTRY.items():
        fields: list[str] = []
        for profile in policy.profiles:
            if (
                not profile.requested_fields
                or profile.requested_fields != tuple(sorted(set(profile.requested_fields)))
                or not set(profile.requested_fields).issubset(SOURCE_FIELDS[family])
                or any("status" in field for field in profile.requested_fields)
                or profile.trust_class is not (
                    TrustLevel.ASSOCIATIVE_EVIDENCE if family == "fact_purchase_order"
                    else TrustLevel.DIRECT_FACT
                )
            ):
                raise ValueError("invalid closed C04 query profile")
            fields.extend(profile.requested_fields)
        if (
            len(fields) != len(set(fields))
            or set(fields) != set(SOURCE_FIELDS[family])
            or policy.primary_key not in fields
        ):
            raise ValueError("invalid C04 source field partition")


_validate_registry()
