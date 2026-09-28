"""Pure protected replay helpers for deterministic C07 order selection."""

from __future__ import annotations

from collections.abc import Mapping

from flowlens.data import Base
from flowlens.data.generation.generator import GeneratedDataset
from flowlens.data.scenarios.ground_truth import HiddenGroundTruth

_TABLE_ID_FIELDS = {
    "fact_sales_order": "sales_order_id",
    "fact_work_order": "work_order_id",
    "fact_operation": "operation_id",
    "fact_material_requirement": "material_requirement_id",
    "fact_quality_inspection": "inspection_id",
    "fact_rework": "rework_id",
    "fact_delivery": "delivery_id",
}

_QUEUE_RELATIONSHIPS = frozenset(
    {
        "adds_operation_queue_delay",
        "shifts_downstream_operation",
        "shifts_work_order_completion",
        "shifts_inspection_time",
        "shifts_rework_window",
        "shifts_delivery_time",
    }
)


def _string_attr(row: Base, name: str) -> str:
    value = getattr(row, name)
    if type(value) is not str:
        raise ValueError(f"{name} must be a string")
    return value


def _index(dataset: GeneratedDataset, table: str) -> dict[str, Base]:
    identifier = _TABLE_ID_FIELDS[table]
    dataset_id = dataset.dataset_version.dataset_version_id
    result: dict[str, Base] = {}
    for row in dataset.rows_for(table):
        if _string_attr(row, "dataset_version_id") != dataset_id:
            raise ValueError(f"{table} row crosses the scenario dataset boundary")
        key = _string_attr(row, identifier)
        if key in result:
            raise ValueError(f"duplicate {table} identity")
        result[key] = row
    return result


def dataset_order_ids(dataset: GeneratedDataset) -> tuple[str, ...]:
    """Return canonical Sales Order IDs without reading an operational store."""

    return tuple(sorted(_index(dataset, "fact_sales_order")))


def _entity_order_map(dataset: GeneratedDataset) -> dict[tuple[str, str], str]:
    indexes = {table: _index(dataset, table) for table in _TABLE_ID_FIELDS}
    work_orders = indexes["fact_work_order"]
    result: dict[tuple[str, str], str] = {}
    for sales_order_id in indexes["fact_sales_order"]:
        result[("fact_sales_order", sales_order_id)] = sales_order_id
    for work_order_id, row in work_orders.items():
        sales_order_id = _string_attr(row, "sales_order_id")
        if sales_order_id not in indexes["fact_sales_order"]:
            raise ValueError("WorkOrder references a missing SalesOrder")
        result[("fact_work_order", work_order_id)] = sales_order_id
    for table in (
        "fact_operation",
        "fact_material_requirement",
        "fact_quality_inspection",
        "fact_rework",
    ):
        for entity_id, row in indexes[table].items():
            work_order_id = _string_attr(row, "work_order_id")
            work_order = work_orders.get(work_order_id)
            if work_order is None:
                raise ValueError(f"{table} references a missing WorkOrder")
            result[(table, entity_id)] = _string_attr(work_order, "sales_order_id")
    for delivery_id, row in indexes["fact_delivery"].items():
        sales_order_id = _string_attr(row, "sales_order_id")
        if sales_order_id not in indexes["fact_sales_order"]:
            raise ValueError("Delivery references a missing SalesOrder")
        result[("fact_delivery", delivery_id)] = sales_order_id
    return result


def derive_affected_order_ids(
    dataset: GeneratedDataset,
    ground_truth: HiddenGroundTruth,
) -> tuple[str, ...]:
    """Resolve every mapped HGT entity and derive its protected Sales Order set."""

    entity_orders = _entity_order_map(dataset)
    affected: set[str] = set()
    for table, entity_ids in ground_truth.affected_entities_by_table.items():
        if table not in _TABLE_ID_FIELDS:
            continue
        for entity_id in entity_ids:
            order_id = entity_orders.get((table, entity_id))
            if order_id is None:
                raise ValueError(f"HGT affected ID is missing from {table}")
            affected.add(order_id)
    return tuple(sorted(affected))


def hgt_proves_capacity_arrival(
    ground_truth: HiddenGroundTruth,
    order_id: str,
) -> bool:
    return any(
        link.relationship == "receives_added_sales_order_arrival"
        and link.target_table == "fact_sales_order"
        and link.target_entity_id == order_id
        for link in ground_truth.causal_chain
    )


def hgt_proves_capacity_queue(
    dataset: GeneratedDataset,
    ground_truth: HiddenGroundTruth,
    order_id: str,
) -> bool:
    entity_orders = _entity_order_map(dataset)
    for link in ground_truth.causal_chain:
        if link.relationship not in _QUEUE_RELATIONSHIPS:
            continue
        endpoints = (
            (link.source_table, link.source_entity_id),
            (link.target_table, link.target_entity_id),
        )
        if any(entity_orders.get(endpoint) == order_id for endpoint in endpoints):
            return True
    return False


def select_existing_affected_order(
    baseline: GeneratedDataset,
    scenario: GeneratedDataset,
    ground_truth: HiddenGroundTruth,
) -> str | None:
    baseline_ids = set(dataset_order_ids(baseline))
    candidates = tuple(
        order_id
        for order_id in derive_affected_order_ids(scenario, ground_truth)
        if order_id in baseline_ids
    )
    return candidates[0] if candidates else None


def select_created_affected_order(
    baseline: GeneratedDataset,
    scenario: GeneratedDataset,
    ground_truth: HiddenGroundTruth,
) -> str | None:
    baseline_ids = set(dataset_order_ids(baseline))
    candidates = tuple(
        order_id
        for order_id in derive_affected_order_ids(scenario, ground_truth)
        if order_id not in baseline_ids
    )
    return candidates[0] if candidates else None


def select_neutral_order(
    baseline: GeneratedDataset,
    scenario: GeneratedDataset,
) -> str:
    common = tuple(sorted(set(dataset_order_ids(baseline)) & set(dataset_order_ids(scenario))))
    if not common:
        raise ValueError("neutral replay has no common Sales Order")
    return common[0]


def mapped_entity_order_view(dataset: GeneratedDataset) -> Mapping[tuple[str, str], str]:
    """Expose an immutable-by-convention deterministic view for harness assertions."""

    return _entity_order_map(dataset)
