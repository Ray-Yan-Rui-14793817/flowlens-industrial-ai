"""Deterministic W02-C04-E Quality Deterioration intervention."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import timedelta
from decimal import Decimal
from typing import cast

from flowlens.data import Base
from flowlens.data.generation import GeneratedDataset
from flowlens.data.models import (
    Delivery,
    Operation,
    Product,
    QualityInspection,
    Rework,
    WorkCenter,
    WorkOrder,
)
from flowlens.data.scenarios._deterministic import (
    ceil_duration,
    ceil_microsecond_duration,
    choose_hundredth_decimal,
    choose_inclusive_int,
    choose_value,
    median_duration_microseconds,
    probability_target_count,
    rank_candidates,
)
from flowlens.data.scenarios.config import QualityDeteriorationConfig
from flowlens.data.scenarios.transformer import (
    BusinessCausalLink,
    BusinessScenarioEffects,
    ScenarioIdentity,
    ScenarioPreconditionUnavailable,
)

_DEFECT_CATEGORIES = ("DIMENSIONAL", "SURFACE", "ASSEMBLY", "ELECTRICAL")
_SEVERITIES = ("LOW", "MEDIUM", "HIGH")
_REWORK_REASONS = (
    "SYNTHETIC_DIMENSIONAL_ADJUSTMENT",
    "SYNTHETIC_ASSEMBLY_CORRECTION",
    "SYNTHETIC_SURFACE_REFINISH",
)


def _affected_mapping(
    affected: Mapping[str, set[str]],
) -> dict[str, tuple[str, ...]]:
    return {
        table_name: tuple(sorted(entity_ids))
        for table_name, entity_ids in affected.items()
        if entity_ids
    }


def _scenario_rework_id(identity: ScenarioIdentity, inspection_id: str) -> str:
    payload = {
        "inspection_id": inspection_id,
        "purpose": "scenario-rework-id",
        "scenario_namespace": identity.namespace,
    }
    serialized = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"rw_{digest[:45]}"


def _final_operation(
    operations: Sequence[Operation],
) -> Operation | None:
    if not operations:
        return None
    return max(operations, key=lambda row: (row.sequence_number, row.operation_id))


def apply_quality_deterioration(
    baseline: GeneratedDataset,
    identity: ScenarioIdentity,
    config: QualityDeteriorationConfig,
    rows_by_table: dict[str, list[Base]],
) -> BusinessScenarioEffects:
    """Mutate only the cloned graph and return compatibility effects."""

    products = cast(tuple[Product, ...], baseline.rows_for("dim_product"))
    work_centers = cast(tuple[WorkCenter, ...], baseline.rows_for("dim_work_center"))
    work_orders = cast(tuple[WorkOrder, ...], baseline.rows_for("fact_work_order"))
    operations = cast(tuple[Operation, ...], baseline.rows_for("fact_operation"))
    inspections = cast(
        tuple[QualityInspection, ...], baseline.rows_for("fact_quality_inspection")
    )
    baseline_reworks = cast(tuple[Rework, ...], baseline.rows_for("fact_rework"))
    deliveries = cast(tuple[Delivery, ...], baseline.rows_for("fact_delivery"))

    scenario_work_orders = {
        row.work_order_id: row
        for row in cast(list[WorkOrder], rows_by_table["fact_work_order"])
    }
    scenario_inspections = {
        row.inspection_id: row
        for row in cast(
            list[QualityInspection], rows_by_table["fact_quality_inspection"]
        )
    }
    scenario_rework_rows = cast(list[Rework], rows_by_table["fact_rework"])
    scenario_reworks = {row.rework_id: row for row in scenario_rework_rows}
    scenario_deliveries = {
        row.delivery_id: row
        for row in cast(list[Delivery], rows_by_table["fact_delivery"])
    }

    product_ids = {row.product_id for row in products}
    work_center_ids = {row.work_center_id for row in work_centers}
    work_order_by_id = {row.work_order_id: row for row in work_orders}
    operation_by_id = {row.operation_id: row for row in operations}
    operations_by_work_order: dict[str, list[Operation]] = defaultdict(list)
    for operation in operations:
        operations_by_work_order[operation.work_order_id].append(operation)

    resolved: dict[str, tuple[QualityInspection, str, str]] = {}
    for inspection in inspections:
        if not config.window_start <= inspection.inspection_at < config.window_end:
            continue
        work_order = work_order_by_id.get(inspection.work_order_id)
        if work_order is None or work_order.product_id not in product_ids:
            continue
        if inspection.operation_id is not None:
            resolved_operation = operation_by_id.get(inspection.operation_id)
            if (
                resolved_operation is None
                or resolved_operation.work_order_id != inspection.work_order_id
            ):
                continue
        else:
            resolved_operation = _final_operation(
                operations_by_work_order.get(inspection.work_order_id, ())
            )
            if resolved_operation is None:
                continue
        if resolved_operation.work_center_id not in work_center_ids:
            continue
        resolved[inspection.inspection_id] = (
            inspection,
            work_order.product_id,
            resolved_operation.work_center_id,
        )

    candidate_work_center_ids = {item[2] for item in resolved.values()}
    selected_work_centers = rank_candidates(
        (
            row
            for row in work_centers
            if row.work_center_id in candidate_work_center_ids
        ),
        identity,
        "quality-work-center-target",
        lambda row: row.work_center_id,
    )[: config.affected_work_center_count]
    if len(selected_work_centers) != config.affected_work_center_count:
        raise ScenarioPreconditionUnavailable(
            "insufficient eligible work centers for Quality Deterioration"
        )
    selected_work_center_ids = {row.work_center_id for row in selected_work_centers}

    candidate_product_ids = {
        product_id
        for _, product_id, work_center_id in resolved.values()
        if work_center_id in selected_work_center_ids
    }
    selected_products = rank_candidates(
        (row for row in products if row.product_id in candidate_product_ids),
        identity,
        "quality-product-target",
        lambda row: row.product_id,
    )[: config.affected_product_count]
    if len(selected_products) != config.affected_product_count:
        raise ScenarioPreconditionUnavailable(
            "insufficient eligible products for Quality Deterioration"
        )
    selected_product_ids = {row.product_id for row in selected_products}

    relevant = [
        item
        for item in resolved.values()
        if item[1] in selected_product_ids and item[2] in selected_work_center_ids
    ]
    if not relevant:
        raise ScenarioPreconditionUnavailable(
            "final Quality target graph has no eligible inspection edges"
        )
    if {item[2] for item in relevant} != selected_work_center_ids:
        raise ValueError("selected work center has no final Quality graph edge")
    if {item[1] for item in relevant} != selected_product_ids:
        raise ValueError("selected product has no final Quality graph edge")

    for inspection, _, _ in relevant:
        quantities_coherent = (
            inspection.inspected_quantity > 0
            and inspection.passed_quantity >= 0
            and inspection.failed_quantity >= 0
            and inspection.passed_quantity + inspection.failed_quantity
            == inspection.inspected_quantity
        )
        result_coherent = (
            inspection.result == "PASS" and inspection.failed_quantity == 0
        ) or (inspection.result == "FAIL" and inspection.failed_quantity > 0)
        if not quantities_coherent or not result_coherent:
            raise ValueError("incoherent baseline Quality inspection state")

    relevant_inspections = [item[0] for item in relevant]
    relevant_ids = {row.inspection_id for row in relevant_inspections}
    resulting_inspection_by_id = {
        row.inspection_id: row for row in relevant_inspections
    }
    resolved_work_center = {item[0].inspection_id: item[2] for item in relevant}
    population = len(relevant_inspections)
    baseline_failures = [row for row in relevant_inspections if row.result == "FAIL"]
    failure_count = len(baseline_failures)
    if failure_count == 0:
        raise ScenarioPreconditionUnavailable(
            "Quality deterioration requires a nonzero baseline FAIL count"
        )
    baseline_failure_rate = Decimal(failure_count) / Decimal(population)
    target_failure_rate = min(
        Decimal("1"), baseline_failure_rate * config.failure_probability_multiplier
    )
    target_failure_count = probability_target_count(population, target_failure_rate)
    additional_failures = max(0, target_failure_count - failure_count)
    selected_new_failures = rank_candidates(
        (row for row in relevant_inspections if row.result == "PASS"),
        identity,
        "quality-failure-event",
        lambda row: row.inspection_id,
    )[:additional_failures]
    if len(selected_new_failures) != additional_failures:
        raise ScenarioPreconditionUnavailable(
            "insufficient PASS inspections for Quality failure target"
        )

    affected: dict[str, set[str]] = defaultdict(set)
    links: set[BusinessCausalLink] = set()
    for inspection in selected_new_failures:
        scenario_inspection = scenario_inspections[inspection.inspection_id]
        scenario_inspection.failed_quantity = 1
        scenario_inspection.passed_quantity = inspection.inspected_quantity - 1
        scenario_inspection.result = "FAIL"
        scenario_inspection.defect_category = choose_value(
            _DEFECT_CATEGORIES,
            identity,
            "quality-defect-category",
            inspection.inspection_id,
        )
        scenario_inspection.severity = choose_value(
            _SEVERITIES,
            identity,
            "quality-severity",
            inspection.inspection_id,
        )
        affected["fact_quality_inspection"].add(inspection.inspection_id)
        links.add(
            BusinessCausalLink(
                source_table="dim_work_center",
                source_entity_id=resolved_work_center[inspection.inspection_id],
                target_table="fact_quality_inspection",
                target_entity_id=inspection.inspection_id,
                relationship="degrades_quality_inspection",
            )
        )

    baseline_reworks_by_inspection: dict[str, list[Rework]] = defaultdict(list)
    for rework in baseline_reworks:
        baseline_reworks_by_inspection[rework.inspection_id].append(rework)
    for inspection_id in relevant_ids:
        inspection = resulting_inspection_by_id[inspection_id]
        for rework in baseline_reworks_by_inspection[inspection_id]:
            if (
                rework.work_order_id != inspection.work_order_id
                or rework.work_center_id not in work_center_ids
                or rework.rework_quantity <= 0
                or rework.rework_quantity > inspection.failed_quantity
                or rework.rework_start_at < inspection.inspection_at
                or rework.rework_end_at < rework.rework_start_at
            ):
                raise ValueError("incoherent baseline Quality rework state")

    baseline_reworked_failure_ids = {
        inspection.inspection_id
        for inspection in baseline_failures
        if any(
            rework.work_order_id == inspection.work_order_id
            for rework in baseline_reworks_by_inspection[inspection.inspection_id]
        )
    }
    baseline_rework_rate = Decimal(len(baseline_reworked_failure_ids)) / Decimal(
        failure_count
    )
    target_rework_rate = min(
        Decimal("1"), baseline_rework_rate + config.rework_probability_delta
    )
    resulting_failure_ids = {
        row.inspection_id for row in baseline_failures
    } | {row.inspection_id for row in selected_new_failures}
    target_rework_count = probability_target_count(
        len(resulting_failure_ids), target_rework_rate
    )
    existing_reworked_resulting_ids = {
        inspection_id
        for inspection_id in resulting_failure_ids
        if baseline_reworks_by_inspection[inspection_id]
    }
    additional_reworks = max(
        0, target_rework_count - len(existing_reworked_resulting_ids)
    )
    selected_new_rework_inspections = rank_candidates(
        (
            resulting_inspection_by_id[inspection_id]
            for inspection_id in resulting_failure_ids
            if inspection_id not in existing_reworked_resulting_ids
        ),
        identity,
        "quality-rework-event",
        lambda row: row.inspection_id,
    )[:additional_reworks]
    if len(selected_new_rework_inspections) != additional_reworks:
        raise ScenarioPreconditionUnavailable(
            "insufficient failures without rework for Quality rework target"
        )

    affected_existing_reworks = [
        rework
        for rework in baseline_reworks
        if rework.inspection_id in relevant_ids
        and resulting_inspection_by_id[rework.inspection_id].result == "FAIL"
        and rework.work_order_id
        == resulting_inspection_by_id[rework.inspection_id].work_order_id
    ]
    valid_reference_durations = [
        rework.rework_end_at - rework.rework_start_at
        for rework in baseline_reworks
        if rework.inspection_id in relevant_ids
        and rework.work_order_id
        == resulting_inspection_by_id[rework.inspection_id].work_order_id
        and rework.rework_end_at >= rework.rework_start_at
    ]
    median_reference = (
        median_duration_microseconds(valid_reference_durations)
        if valid_reference_durations
        else None
    )
    if selected_new_rework_inspections and median_reference is None:
        raise ScenarioPreconditionUnavailable(
            "new Quality rework requires a valid baseline duration reference"
        )

    scenario_affected_reworks_by_work_order: dict[str, list[Rework]] = defaultdict(list)
    for baseline_rework in affected_existing_reworks:
        multiplier = choose_hundredth_decimal(
            config.rework_duration_multiplier_min,
            config.rework_duration_multiplier_max,
            identity,
            "quality-rework-duration",
            baseline_rework.rework_id,
        )
        new_duration = ceil_duration(
            baseline_rework.rework_end_at - baseline_rework.rework_start_at,
            multiplier,
        )
        scenario_rework = scenario_reworks[baseline_rework.rework_id]
        scenario_rework.rework_end_at = baseline_rework.rework_start_at + new_duration
        scenario_affected_reworks_by_work_order[baseline_rework.work_order_id].append(
            scenario_rework
        )
        if scenario_rework.rework_end_at != baseline_rework.rework_end_at:
            affected["fact_rework"].add(baseline_rework.rework_id)
            links.add(
                BusinessCausalLink(
                    source_table="fact_quality_inspection",
                    source_entity_id=baseline_rework.inspection_id,
                    target_table="fact_rework",
                    target_entity_id=baseline_rework.rework_id,
                    relationship="extends_existing_rework_duration",
                )
            )

    existing_rework_ids = set(scenario_reworks)
    for inspection in selected_new_rework_inspections:
        rework_id = _scenario_rework_id(identity, inspection.inspection_id)
        if rework_id in existing_rework_ids:
            raise ValueError("scenario-created Rework ID collision")
        existing_rework_ids.add(rework_id)
        if median_reference is None:
            raise AssertionError("new rework must have a baseline duration reference")
        start_offset = choose_inclusive_int(
            1,
            6,
            identity,
            "quality-rework-start",
            inspection.inspection_id,
        )
        start_at = inspection.inspection_at + timedelta(hours=start_offset)
        multiplier = choose_hundredth_decimal(
            config.rework_duration_multiplier_min,
            config.rework_duration_multiplier_max,
            identity,
            "quality-rework-duration",
            rework_id,
        )
        duration = ceil_microsecond_duration(median_reference, multiplier)
        scenario_inspection = scenario_inspections[inspection.inspection_id]
        new_rework = Rework(
            rework_id=rework_id,
            dataset_version_id=identity.scenario_dataset_version_id,
            inspection_id=inspection.inspection_id,
            work_order_id=inspection.work_order_id,
            work_center_id=resolved_work_center[inspection.inspection_id],
            rework_start_at=start_at,
            rework_end_at=start_at + duration,
            rework_quantity=scenario_inspection.failed_quantity,
            rework_reason=choose_value(
                _REWORK_REASONS,
                identity,
                "quality-rework-reason",
                inspection.inspection_id,
            ),
        )
        scenario_rework_rows.append(new_rework)
        scenario_reworks[rework_id] = new_rework
        scenario_affected_reworks_by_work_order[inspection.work_order_id].append(
            new_rework
        )
        affected["fact_rework"].add(rework_id)
        links.add(
            BusinessCausalLink(
                source_table="fact_quality_inspection",
                source_entity_id=inspection.inspection_id,
                target_table="fact_rework",
                target_entity_id=rework_id,
                relationship="creates_scenario_rework",
            )
        )

    deliveries_by_sales_order: dict[str, list[Delivery]] = defaultdict(list)
    for delivery in deliveries:
        deliveries_by_sales_order[delivery.sales_order_id].append(delivery)
    for work_order_id, affected_reworks in scenario_affected_reworks_by_work_order.items():
        baseline_work_order = work_order_by_id.get(work_order_id)
        if baseline_work_order is None or baseline_work_order.actual_end_at is None:
            raise ValueError("quality-affected work order requires baseline actual end")
        required_completion = max(row.rework_end_at for row in affected_reworks)
        if required_completion <= baseline_work_order.actual_end_at:
            continue
        scenario_work_orders[work_order_id].actual_end_at = required_completion
        affected["fact_work_order"].add(work_order_id)
        for rework in affected_reworks:
            if rework.rework_end_at == required_completion:
                links.add(
                    BusinessCausalLink(
                        source_table="fact_rework",
                        source_entity_id=rework.rework_id,
                        target_table="fact_work_order",
                        target_entity_id=work_order_id,
                        relationship="extends_work_order_completion",
                    )
                )

        sales_deliveries = sorted(
            deliveries_by_sales_order[baseline_work_order.sales_order_id],
            key=lambda row: (row.delivery_at, row.delivery_id),
        )
        if not sales_deliveries or sales_deliveries[0].delivery_at >= required_completion:
            continue
        delivery_shift = required_completion - sales_deliveries[0].delivery_at
        for delivery in sales_deliveries:
            scenario_deliveries[delivery.delivery_id].delivery_at = (
                delivery.delivery_at + delivery_shift
            )
            affected["fact_delivery"].add(delivery.delivery_id)
            links.add(
                BusinessCausalLink(
                    source_table="fact_work_order",
                    source_entity_id=work_order_id,
                    target_table="fact_delivery",
                    target_entity_id=delivery.delivery_id,
                    relationship="shifts_delivery_time",
                )
            )

    return BusinessScenarioEffects(
        target_entity_ids=tuple(selected_product_ids | selected_work_center_ids),
        affected_entities_by_table=_affected_mapping(affected),
        causal_chain=tuple(links),
    )
