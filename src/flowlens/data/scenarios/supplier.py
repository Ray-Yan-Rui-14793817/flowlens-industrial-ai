"""Deterministic W02-C04-D Supplier Degradation intervention."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from datetime import datetime, timedelta
from decimal import Decimal
from typing import cast

from flowlens.data import Base
from flowlens.data.generation import GeneratedDataset
from flowlens.data.models import (
    Delivery,
    Material,
    MaterialRequirement,
    Operation,
    ProductMaterial,
    PurchaseOrder,
    QualityInspection,
    Rework,
    Supplier,
    WorkOrder,
)
from flowlens.data.scenarios._deterministic import (
    add_business_days,
    choose_inclusive_int,
    probability_target_count,
    rank_candidates,
)
from flowlens.data.scenarios.config import SupplierDegradationConfig
from flowlens.data.scenarios.transformer import (
    BusinessCausalLink,
    BusinessScenarioEffects,
    ScenarioIdentity,
    ScenarioPreconditionUnavailable,
)


def _affected_mapping(
    affected: Mapping[str, set[str]],
) -> dict[str, tuple[str, ...]]:
    return {
        table_name: tuple(sorted(entity_ids))
        for table_name, entity_ids in affected.items()
        if entity_ids
    }


def apply_supplier_degradation(
    baseline: GeneratedDataset,
    identity: ScenarioIdentity,
    config: SupplierDegradationConfig,
    rows_by_table: dict[str, list[Base]],
) -> BusinessScenarioEffects:
    """Mutate only the cloned graph and return compatibility effects."""

    suppliers = cast(tuple[Supplier, ...], baseline.rows_for("dim_supplier"))
    materials = cast(tuple[Material, ...], baseline.rows_for("dim_material"))
    bom = cast(tuple[ProductMaterial, ...], baseline.rows_for("bridge_product_material"))
    purchase_orders = cast(
        tuple[PurchaseOrder, ...], baseline.rows_for("fact_purchase_order")
    )
    work_orders = cast(tuple[WorkOrder, ...], baseline.rows_for("fact_work_order"))
    requirements = cast(
        tuple[MaterialRequirement, ...],
        baseline.rows_for("fact_material_requirement"),
    )
    operations = cast(tuple[Operation, ...], baseline.rows_for("fact_operation"))
    inspections = cast(
        tuple[QualityInspection, ...], baseline.rows_for("fact_quality_inspection")
    )
    reworks = cast(tuple[Rework, ...], baseline.rows_for("fact_rework"))
    deliveries = cast(tuple[Delivery, ...], baseline.rows_for("fact_delivery"))

    scenario_purchase_orders = {
        row.purchase_order_id: row
        for row in cast(list[PurchaseOrder], rows_by_table["fact_purchase_order"])
    }
    scenario_work_orders = {
        row.work_order_id: row
        for row in cast(list[WorkOrder], rows_by_table["fact_work_order"])
    }
    scenario_operations = {
        row.operation_id: row
        for row in cast(list[Operation], rows_by_table["fact_operation"])
    }
    scenario_inspections = {
        row.inspection_id: row
        for row in cast(
            list[QualityInspection], rows_by_table["fact_quality_inspection"]
        )
    }
    scenario_reworks = {
        row.rework_id: row for row in cast(list[Rework], rows_by_table["fact_rework"])
    }
    scenario_deliveries = {
        row.delivery_id: row
        for row in cast(list[Delivery], rows_by_table["fact_delivery"])
    }

    supplier_by_id = {row.supplier_id: row for row in suppliers}
    material_by_id = {row.material_id: row for row in materials}
    work_order_by_id = {row.work_order_id: row for row in work_orders}
    requirements_by_material: dict[str, list[MaterialRequirement]] = defaultdict(list)
    for requirement in requirements:
        requirements_by_material[requirement.material_id].append(requirement)
    bom_by_key = {(row.product_id, row.material_id): row for row in bom}

    chain_keys_by_material: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for requirement in requirements:
        work_order = work_order_by_id.get(requirement.work_order_id)
        if work_order is None:
            continue
        key = (work_order.product_id, requirement.material_id)
        if key in bom_by_key:
            chain_keys_by_material[requirement.material_id].add(key)

    eligible_purchase_orders: list[PurchaseOrder] = []
    for purchase_order in purchase_orders:
        material = material_by_id.get(purchase_order.material_id)
        if (
            not config.window_start <= purchase_order.ordered_at < config.window_end
            or purchase_order.supplier_id not in supplier_by_id
            or material is None
            or material.criticality not in {"HIGH", "CRITICAL"}
            or purchase_order.actual_receipt_at is None
            or not chain_keys_by_material[purchase_order.material_id]
        ):
            continue
        eligible_purchase_orders.append(purchase_order)

    candidate_supplier_ids = {row.supplier_id for row in eligible_purchase_orders}
    selected_suppliers = rank_candidates(
        (supplier_by_id[supplier_id] for supplier_id in candidate_supplier_ids),
        identity,
        "supplier-target",
        lambda row: row.supplier_id,
    )[: config.affected_supplier_count]
    if len(selected_suppliers) != config.affected_supplier_count:
        raise ScenarioPreconditionUnavailable(
            "insufficient eligible suppliers for Supplier Degradation"
        )
    selected_supplier_ids = {row.supplier_id for row in selected_suppliers}

    candidate_material_ids = {
        row.material_id
        for row in eligible_purchase_orders
        if row.supplier_id in selected_supplier_ids
    }
    selected_materials = rank_candidates(
        (material_by_id[material_id] for material_id in candidate_material_ids),
        identity,
        "supplier-material-target",
        lambda row: row.material_id,
    )[: config.affected_critical_material_count]
    if len(selected_materials) != config.affected_critical_material_count:
        raise ScenarioPreconditionUnavailable(
            "insufficient eligible critical materials for Supplier Degradation"
        )
    selected_material_ids = {row.material_id for row in selected_materials}

    for material_id in selected_material_ids:
        material = material_by_id[material_id]
        authoritative = material.criticality in {"HIGH", "CRITICAL"}
        if any(
            bom_by_key[key].is_critical is not authoritative
            for key in chain_keys_by_material[material_id]
        ):
            raise ValueError("critical-material BOM classification contradiction")

    final_purchase_orders = [
        row
        for row in eligible_purchase_orders
        if row.supplier_id in selected_supplier_ids
        and row.material_id in selected_material_ids
    ]
    if not final_purchase_orders:
        raise ScenarioPreconditionUnavailable(
            "final Supplier target graph has no eligible PO edges"
        )
    if {row.supplier_id for row in final_purchase_orders} != selected_supplier_ids:
        raise ValueError("selected supplier has no final Supplier graph edge")
    if {row.material_id for row in final_purchase_orders} != selected_material_ids:
        raise ValueError("selected material has no final Supplier graph edge")

    population = len(final_purchase_orders)
    baseline_late = sum(
        row.actual_receipt_at is not None
        and row.actual_receipt_at > row.promised_receipt_at
        for row in final_purchase_orders
    )
    baseline_rate = Decimal(baseline_late) / Decimal(population)
    target_rate = min(Decimal("1"), baseline_rate + config.late_probability_delta)
    target_late = probability_target_count(population, target_rate)
    additional_late = max(0, target_late - baseline_late)

    materializable: list[PurchaseOrder] = []
    minimum_delays: dict[str, int] = {}
    for purchase_order in final_purchase_orders:
        receipt = purchase_order.actual_receipt_at
        if receipt is None or receipt > purchase_order.promised_receipt_at:
            continue
        for delay in range(
            config.additional_delay_business_days_min,
            config.additional_delay_business_days_max + 1,
        ):
            if add_business_days(receipt, delay) > purchase_order.promised_receipt_at:
                minimum_delays[purchase_order.purchase_order_id] = delay
                materializable.append(purchase_order)
                break

    selected_new_late = rank_candidates(
        materializable,
        identity,
        "supplier-late-event",
        lambda row: row.purchase_order_id,
    )[:additional_late]
    if len(selected_new_late) != additional_late:
        raise ScenarioPreconditionUnavailable(
            "insufficient materializable new-late purchase orders"
        )

    affected: dict[str, set[str]] = defaultdict(set)
    links: set[BusinessCausalLink] = set()
    delayed_receipts: dict[str, tuple[PurchaseOrder, datetime]] = {}
    for purchase_order in selected_new_late:
        baseline_receipt = purchase_order.actual_receipt_at
        if baseline_receipt is None:
            raise AssertionError("materializable purchase order must have a receipt")
        delay = choose_inclusive_int(
            minimum_delays[purchase_order.purchase_order_id],
            config.additional_delay_business_days_max,
            identity,
            "supplier-delay-days",
            purchase_order.purchase_order_id,
        )
        scenario_receipt = add_business_days(baseline_receipt, delay)
        scenario_purchase_orders[purchase_order.purchase_order_id].actual_receipt_at = (
            scenario_receipt
        )
        delayed_receipts[purchase_order.purchase_order_id] = (
            purchase_order,
            scenario_receipt,
        )
        affected["fact_purchase_order"].add(purchase_order.purchase_order_id)
        links.add(
            BusinessCausalLink(
                source_table="dim_supplier",
                source_entity_id=purchase_order.supplier_id,
                target_table="fact_purchase_order",
                target_entity_id=purchase_order.purchase_order_id,
                relationship="degrades_purchase_order_receipt",
            )
        )

    shortage_links_by_work_order: dict[
        str, list[tuple[PurchaseOrder, MaterialRequirement, datetime]]
    ] = defaultdict(list)
    for purchase_order, scenario_receipt in delayed_receipts.values():
        for requirement in requirements_by_material[purchase_order.material_id]:
            baseline_receipt = purchase_order.actual_receipt_at
            if baseline_receipt is None:
                continue
            if baseline_receipt <= requirement.need_by_at < scenario_receipt:
                shortage_links_by_work_order[requirement.work_order_id].append(
                    (purchase_order, requirement, scenario_receipt)
                )
                links.add(
                    BusinessCausalLink(
                        source_table="fact_purchase_order",
                        source_entity_id=purchase_order.purchase_order_id,
                        target_table="fact_material_requirement",
                        target_entity_id=requirement.material_requirement_id,
                        relationship="creates_material_shortage",
                    )
                )

    operations_by_work_order: dict[str, list[Operation]] = defaultdict(list)
    inspections_by_work_order: dict[str, list[QualityInspection]] = defaultdict(list)
    reworks_by_work_order: dict[str, list[Rework]] = defaultdict(list)
    deliveries_by_sales_order: dict[str, list[Delivery]] = defaultdict(list)
    for operation in operations:
        operations_by_work_order[operation.work_order_id].append(operation)
    for inspection in inspections:
        inspections_by_work_order[inspection.work_order_id].append(inspection)
    for rework in reworks:
        reworks_by_work_order[rework.work_order_id].append(rework)
    for delivery in deliveries:
        deliveries_by_sales_order[delivery.sales_order_id].append(delivery)

    for work_order_id, shortage_links in shortage_links_by_work_order.items():
        baseline_work_order = work_order_by_id.get(work_order_id)
        if baseline_work_order is None:
            raise ValueError("shortage references a nonexistent work order")
        if (
            baseline_work_order.actual_start_at is None
            or baseline_work_order.actual_end_at is None
        ):
            raise ValueError("supplier-affected work order requires complete actual timing")
        required_available_at = max(
            item[2] for item in shortage_links
        )
        causal_shift = max(
            timedelta(0), required_available_at - baseline_work_order.actual_start_at
        )
        if causal_shift == timedelta(0):
            continue

        scenario_work_order = scenario_work_orders[work_order_id]
        scenario_work_order.actual_start_at = baseline_work_order.actual_start_at + causal_shift
        scenario_work_order.actual_end_at = baseline_work_order.actual_end_at + causal_shift
        affected["fact_work_order"].add(work_order_id)
        for _, requirement, scenario_receipt_value in shortage_links:
            if scenario_receipt_value == required_available_at:
                links.add(
                    BusinessCausalLink(
                        source_table="fact_material_requirement",
                        source_entity_id=requirement.material_requirement_id,
                        target_table="fact_work_order",
                        target_entity_id=work_order_id,
                        relationship="sets_work_order_material_delay",
                    )
                )

        for operation in operations_by_work_order[work_order_id]:
            scenario_operation = scenario_operations[operation.operation_id]
            changed = False
            if operation.actual_start_at is not None:
                scenario_operation.actual_start_at = operation.actual_start_at + causal_shift
                changed = True
            if operation.actual_end_at is not None:
                scenario_operation.actual_end_at = operation.actual_end_at + causal_shift
                changed = True
            if changed:
                affected["fact_operation"].add(operation.operation_id)
                links.add(
                    BusinessCausalLink(
                        source_table="fact_work_order",
                        source_entity_id=work_order_id,
                        target_table="fact_operation",
                        target_entity_id=operation.operation_id,
                        relationship="shifts_operation_actual_window",
                    )
                )

        for inspection in inspections_by_work_order[work_order_id]:
            scenario_inspections[inspection.inspection_id].inspection_at = (
                inspection.inspection_at + causal_shift
            )
            affected["fact_quality_inspection"].add(inspection.inspection_id)
            links.add(
                BusinessCausalLink(
                    source_table="fact_work_order",
                    source_entity_id=work_order_id,
                    target_table="fact_quality_inspection",
                    target_entity_id=inspection.inspection_id,
                    relationship="shifts_inspection_time",
                )
            )

        inspection_ids = {
            row.inspection_id for row in inspections_by_work_order[work_order_id]
        }
        for rework in reworks_by_work_order[work_order_id]:
            if rework.inspection_id not in inspection_ids:
                continue
            scenario_rework = scenario_reworks[rework.rework_id]
            scenario_rework.rework_start_at = rework.rework_start_at + causal_shift
            scenario_rework.rework_end_at = rework.rework_end_at + causal_shift
            affected["fact_rework"].add(rework.rework_id)
            links.add(
                BusinessCausalLink(
                    source_table="fact_work_order",
                    source_entity_id=work_order_id,
                    target_table="fact_rework",
                    target_entity_id=rework.rework_id,
                    relationship="shifts_existing_rework_window",
                )
            )

        for delivery in deliveries_by_sales_order[baseline_work_order.sales_order_id]:
            scenario_deliveries[delivery.delivery_id].delivery_at = (
                delivery.delivery_at + causal_shift
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
        target_entity_ids=tuple(selected_supplier_ids | selected_material_ids),
        affected_entities_by_table=_affected_mapping(affected),
        causal_chain=tuple(links),
    )
