"""Behavior tests for W02-C04-D/E deterministic scenario interventions."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_CEILING, Decimal
from functools import cache
from types import MappingProxyType
from typing import cast

import pytest
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.orm import object_session

from flowlens.data import Base
from flowlens.data.generation import (
    BUSINESS_TIMEZONE,
    GeneratedDataset,
    GenerationConfig,
    GenerationProfile,
    generate_baseline,
)
from flowlens.data.generation.canonical import (
    CANONICAL_TABLE_ORDER,
    canonical_business_payload,
    canonical_content_hash,
    canonicalize_rows,
)
from flowlens.data.models import (
    DatasetVersion,
    Delivery,
    Material,
    MaterialRequirement,
    Operation,
    ProductMaterial,
    PurchaseOrder,
    QualityInspection,
    Rework,
    WorkCenter,
    WorkOrder,
)
from flowlens.data.scenarios import (
    CapacitySurgeConfig,
    QualityDeteriorationConfig,
    SupplierDegradationConfig,
    apply_scenario,
)
from flowlens.data.scenarios._deterministic import (
    add_business_days,
    ceil_duration,
    choose_hundredth_decimal,
    choose_inclusive_int,
    median_duration_microseconds,
    probability_target_count,
)
from flowlens.data.scenarios.config import ScenarioType, default_demo_window
from flowlens.data.scenarios.quality import _scenario_rework_id
from flowlens.data.scenarios.transformer import ScenarioResult, build_scenario_identity

SCENARIO_VERSION = "1.0.0"
SCENARIO_SEED = 20_260_901
GENERATED_AT = datetime(2026, 9, 1, tzinfo=UTC)

SUPPLIER_RELATIONSHIPS = {
    "degrades_purchase_order_receipt",
    "creates_material_shortage",
    "sets_work_order_material_delay",
    "shifts_operation_actual_window",
    "shifts_inspection_time",
    "shifts_existing_rework_window",
    "shifts_delivery_time",
}
QUALITY_RELATIONSHIPS = {
    "degrades_quality_inspection",
    "extends_existing_rework_duration",
    "creates_scenario_rework",
    "extends_work_order_completion",
    "shifts_delivery_time",
}


def _baseline() -> GeneratedDataset:
    return generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.TEST,
            seed=20_260_824,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=datetime(2026, 8, 24, 9, tzinfo=UTC),
        )
    )


@cache
def _demo_baseline() -> GeneratedDataset:
    return generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.DEMO,
            seed=20_260_824,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=datetime(2026, 8, 24, 9, tzinfo=UTC),
        )
    )


def _supplier_config(**overrides: object) -> SupplierDegradationConfig:
    values: dict[str, object] = {
        "scenario_version": SCENARIO_VERSION,
        "scenario_seed": SCENARIO_SEED,
        "window_start": datetime(2026, 1, 1, tzinfo=BUSINESS_TIMEZONE),
        "window_end": datetime(2026, 4, 1, tzinfo=BUSINESS_TIMEZONE),
    }
    values.update(overrides)
    return SupplierDegradationConfig(**values)  # type: ignore[arg-type]


def _quality_config(**overrides: object) -> QualityDeteriorationConfig:
    values: dict[str, object] = {
        "scenario_version": SCENARIO_VERSION,
        "scenario_seed": SCENARIO_SEED,
        "window_start": datetime(2026, 1, 1, tzinfo=BUSINESS_TIMEZONE),
        "window_end": datetime(2026, 4, 1, tzinfo=BUSINESS_TIMEZONE),
        "affected_work_center_count": 4,
        "affected_product_count": 12,
    }
    values.update(overrides)
    return QualityDeteriorationConfig(**values)  # type: ignore[arg-type]


def _rebuild(
    baseline: GeneratedDataset,
    overrides: Mapping[str, Sequence[Base]] | None = None,
) -> GeneratedDataset:
    rows: dict[str, Sequence[Base]] = {
        table_name: tuple(baseline.rows_for(table_name))
        for table_name in CANONICAL_TABLE_ORDER
    }
    if overrides:
        rows.update(overrides)
    ordered = canonicalize_rows(rows)
    metadata = baseline.dataset_version
    dataset_version = DatasetVersion(
        dataset_version_id=metadata.dataset_version_id,
        seed=metadata.seed,
        generator_version=metadata.generator_version,
        profile=metadata.profile,
        period_start=metadata.period_start,
        period_end=metadata.period_end,
        generated_at=metadata.generated_at,
        content_hash=canonical_content_hash(ordered),
        row_count_total=sum(len(table_rows) for table_rows in ordered.values()),
    )
    return GeneratedDataset(dataset_version, MappingProxyType(ordered))


def _row_map[T](
    dataset: GeneratedDataset,
    table_name: str,
    key: str,
    row_type: type[T],
) -> dict[str, T]:
    del row_type
    rows = cast(tuple[T, ...], dataset.rows_for(table_name))
    return {cast(str, getattr(row, key)): row for row in rows}


def _subtract_business_days(timestamp: datetime, days: int) -> datetime:
    result = timestamp
    remaining = days
    while remaining:
        result -= timedelta(days=1)
        if result.weekday() < 5:
            remaining -= 1
    return result


def _business_row_index(dataset: GeneratedDataset) -> set[tuple[str, str]]:
    """Index physical table names and their single primary business IDs."""

    indexed: set[tuple[str, str]] = set()
    for table_name, row in dataset.iter_business_rows():
        business_primary_keys = [
            column
            for column in row.__mapper__.primary_key
            if column.name != "dataset_version_id"
        ]
        if len(business_primary_keys) == 1:
            indexed.add(
                (
                    table_name,
                    str(getattr(row, business_primary_keys[0].name)),
                )
            )
    return indexed


def _assert_hgt_referential_integrity(
    result: ScenarioResult,
    *,
    quality: bool,
) -> None:
    row_index = _business_row_index(result.dataset)
    physical_tables = set(CANONICAL_TABLE_ORDER)
    affected = {
        (table_name, entity_id)
        for table_name, entity_ids in result.ground_truth.affected_entities_by_table.items()
        for entity_id in entity_ids
    }
    for link in result.ground_truth.causal_chain:
        assert link.source_table in physical_tables
        assert link.target_table in physical_tables
        assert (link.source_table, link.source_entity_id) in row_index
        assert (link.target_table, link.target_entity_id) in row_index
        if quality or link.relationship != "creates_material_shortage":
            assert (link.target_table, link.target_entity_id) in affected


def _dataset_version_without_generated_at(dataset: GeneratedDataset) -> tuple[object, ...]:
    version = dataset.dataset_version
    return (
        version.dataset_version_id,
        version.seed,
        version.generator_version,
        version.profile,
        version.period_start,
        version.period_end,
        version.content_hash,
        version.row_count_total,
    )


def _supplier_outcome(result: ScenarioResult) -> tuple[object, ...]:
    purchase_orders = _row_map(
        result.dataset,
        "fact_purchase_order",
        "purchase_order_id",
        PurchaseOrder,
    )
    changed_purchase_orders = result.ground_truth.affected_entities_by_table.get(
        "fact_purchase_order", ()
    )
    return (
        result.ground_truth.target_entity_ids,
        changed_purchase_orders,
        tuple(
            (purchase_order_id, purchase_orders[purchase_order_id].actual_receipt_at)
            for purchase_order_id in changed_purchase_orders
        ),
        tuple(
            (table_name, entity_ids)
            for table_name, entity_ids in result.ground_truth.affected_entities_by_table.items()
            if table_name != "fact_purchase_order"
        ),
        result.ground_truth.causal_chain,
    )


def test_public_dispatch_rejects_capacity_and_business_days_are_exact() -> None:
    friday = datetime(2026, 1, 2, 18, tzinfo=BUSINESS_TIMEZONE)
    saturday = datetime(2026, 1, 3, 18, tzinfo=BUSINESS_TIMEZONE)
    assert add_business_days(friday, 1) == datetime(
        2026, 1, 5, 18, tzinfo=BUSINESS_TIMEZONE
    )
    assert add_business_days(friday, 3) == datetime(
        2026, 1, 7, 18, tzinfo=BUSINESS_TIMEZONE
    )
    assert add_business_days(saturday, 1) == datetime(
        2026, 1, 5, 18, tzinfo=BUSINESS_TIMEZONE
    )
    with pytest.raises(ValueError, match="positive integer"):
        add_business_days(friday, 0)

    supplier = apply_scenario(_baseline(), _supplier_config(), generated_at=GENERATED_AT)
    assert supplier.ground_truth.scenario_type.value == "SCN_SUPPLIER_DEGRADATION"
    quality = apply_scenario(_baseline(), _quality_config(), generated_at=GENERATED_AT)
    assert quality.ground_truth.scenario_type.value == "SCN_QUALITY_DETERIORATION"
    with pytest.raises(NotImplementedError, match="W02-C04-F"):
        apply_scenario(
            _baseline(),
            CapacitySurgeConfig(
                scenario_version=SCENARIO_VERSION,
                scenario_seed=SCENARIO_SEED,
                window_start=datetime(2026, 1, 1, tzinfo=BUSINESS_TIMEZONE),
                window_end=datetime(2026, 4, 1, tzinfo=BUSINESS_TIMEZONE),
            ),
            generated_at=GENERATED_AT,
        )


def test_supplier_graph_counts_late_target_and_delay_are_exact() -> None:
    baseline = _baseline()
    config = _supplier_config()
    assert config.affected_supplier_count == 2
    assert config.affected_critical_material_count == 5
    assert config.late_probability_delta == Decimal("0.25")
    assert config.additional_delay_business_days_min == 3
    assert config.additional_delay_business_days_max == 8
    result = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    targets = set(result.ground_truth.target_entity_ids)
    suppliers = {target for target in targets if target.startswith("sup_")}
    materials = {target for target in targets if target.startswith("mat_")}
    assert len(suppliers) == 2
    assert len(materials) == 5
    material_by_id = _row_map(baseline, "dim_material", "material_id", Material)
    assert {material_by_id[value].criticality for value in materials} <= {
        "HIGH",
        "CRITICAL",
    }

    baseline_pos = _row_map(
        baseline, "fact_purchase_order", "purchase_order_id", PurchaseOrder
    )
    scenario_pos = _row_map(
        result.dataset, "fact_purchase_order", "purchase_order_id", PurchaseOrder
    )
    relevant = [
        row
        for row in baseline_pos.values()
        if config.window_start <= row.ordered_at < config.window_end
        and row.supplier_id in suppliers
        and row.material_id in materials
    ]
    work_orders = _row_map(baseline, "fact_work_order", "work_order_id", WorkOrder)
    bom_edges = {
        (row.product_id, row.material_id)
        for row in cast(
            tuple[ProductMaterial, ...],
            baseline.rows_for("bridge_product_material"),
        )
    }
    requirements = cast(
        tuple[MaterialRequirement, ...],
        baseline.rows_for("fact_material_requirement"),
    )
    chain_material_ids = {
        row.material_id
        for row in requirements
        if (work_orders[row.work_order_id].product_id, row.material_id) in bom_edges
    }
    assert len(relevant) == 10
    assert all(row.actual_receipt_at is not None for row in relevant)
    assert all(row.material_id in chain_material_ids for row in relevant)
    actual_edges = {(row.supplier_id, row.material_id) for row in relevant}
    assert {supplier_id for supplier_id, _ in actual_edges} == suppliers
    assert {material_id for _, material_id in actual_edges} == materials
    assert all(
        any(
            row.supplier_id == supplier_id and row.material_id == material_id
            for row in baseline_pos.values()
        )
        for supplier_id, material_id in actual_edges
    )
    baseline_late = sum(
        row.actual_receipt_at is not None
        and row.actual_receipt_at > row.promised_receipt_at
        for row in relevant
    )
    target_rate = min(
        Decimal("1"),
        (Decimal(baseline_late) / Decimal(len(relevant)))
        + config.late_probability_delta,
    )
    target_late = probability_target_count(len(relevant), target_rate)
    changed_ids = set(
        result.ground_truth.affected_entities_by_table["fact_purchase_order"]
    )
    assert len(changed_ids) == target_late - baseline_late == 3
    for purchase_order_id in changed_ids:
        before = baseline_pos[purchase_order_id]
        after = scenario_pos[purchase_order_id]
        assert before.actual_receipt_at is not None
        assert after.actual_receipt_at is not None
        assert after.actual_receipt_at > after.promised_receipt_at
        matching_delays = [
            days
            for days in range(
                config.additional_delay_business_days_min,
                config.additional_delay_business_days_max + 1,
            )
            if add_business_days(before.actual_receipt_at, days)
            == after.actual_receipt_at
        ]
        assert len(matching_delays) == 1
        assert before.status == after.status
        assert before.ordered_quantity == after.ordered_quantity
        assert before.received_quantity == after.received_quantity
    assert {link.relationship for link in result.ground_truth.causal_chain} == {
        "degrades_purchase_order_receipt"
    }
    assert len(result.dataset.rows_for("fact_rework")) == len(
        baseline.rows_for("fact_rework")
    )
    _assert_hgt_referential_integrity(result, quality=False)


def test_supplier_rejects_insufficient_graph_and_bom_contradiction() -> None:
    with pytest.raises(ValueError, match="insufficient eligible suppliers"):
        apply_scenario(
            _baseline(),
            _supplier_config(affected_supplier_count=99),
            generated_at=GENERATED_AT,
        )

    baseline = _baseline()
    config = _supplier_config()
    first = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    selected_material_id = next(
        value
        for value in first.ground_truth.target_entity_ids
        if value.startswith("mat_")
    )
    for component in cast(
        tuple[ProductMaterial, ...], baseline.rows_for("bridge_product_material")
    ):
        if component.material_id == selected_material_id:
            component.is_critical = False
    baseline = _rebuild(baseline)
    with pytest.raises(ValueError, match="BOM classification contradiction"):
        apply_scenario(baseline, config, generated_at=GENERATED_AT)

    insufficient_delay = _baseline()
    for purchase_order in cast(
        tuple[PurchaseOrder, ...],
        insufficient_delay.rows_for("fact_purchase_order"),
    ):
        purchase_order.actual_receipt_at = purchase_order.ordered_at + timedelta(hours=1)
    insufficient_delay = _rebuild(insufficient_delay)
    with pytest.raises(ValueError, match="insufficient materializable new-late"):
        apply_scenario(
            insufficient_delay,
            _supplier_config(
                additional_delay_business_days_min=1,
                additional_delay_business_days_max=1,
            ),
            generated_at=GENERATED_AT,
        )


def test_supplier_shortage_propagation_all_hgt_tokens_and_binding_ties() -> None:
    baseline = _baseline()
    config = _supplier_config()
    initial = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    baseline_pos = _row_map(
        baseline, "fact_purchase_order", "purchase_order_id", PurchaseOrder
    )
    changed_po_ids = list(
        initial.ground_truth.affected_entities_by_table["fact_purchase_order"]
    )
    changed_by_material: dict[str, PurchaseOrder] = {}
    for purchase_order_id in changed_po_ids:
        purchase_order = baseline_pos[purchase_order_id]
        changed_by_material.setdefault(purchase_order.material_id, purchase_order)
    assert len(changed_by_material) >= 2
    first_po, second_po = list(changed_by_material.values())[:2]

    requirements = cast(
        tuple[MaterialRequirement, ...], baseline.rows_for("fact_material_requirement")
    )
    rework_work_order_ids = {
        row.work_order_id
        for row in cast(tuple[Rework, ...], baseline.rows_for("fact_rework"))
    }
    first_requirement = next(
        row
        for row in requirements
        if row.material_id == first_po.material_id
        and row.work_order_id in rework_work_order_ids
    )
    work_order = _row_map(baseline, "fact_work_order", "work_order_id", WorkOrder)[
        first_requirement.work_order_id
    ]

    identity = build_scenario_identity(baseline, config)
    common_receipt = add_business_days(
        max(first_po.ordered_at, second_po.ordered_at), 20
    )
    for purchase_order in (first_po, second_po):
        delay = choose_inclusive_int(
            3,
            8,
            identity,
            "supplier-delay-days",
            purchase_order.purchase_order_id,
        )
        purchase_order.actual_receipt_at = _subtract_business_days(common_receipt, delay)
        purchase_order.promised_receipt_at = add_business_days(
            purchase_order.actual_receipt_at, 3
        ) - timedelta(hours=1)

    first_requirement.need_by_at = common_receipt - timedelta(hours=1)
    components = list(
        cast(tuple[ProductMaterial, ...], baseline.rows_for("bridge_product_material"))
    )
    assert not any(
        row.product_id == work_order.product_id
        and row.material_id == second_po.material_id
        for row in components
    )
    components.append(
        ProductMaterial(
            dataset_version_id=baseline.dataset_version.dataset_version_id,
            product_id=work_order.product_id,
            material_id=second_po.material_id,
            quantity_per_unit=Decimal("1.0000"),
            is_critical=True,
        )
    )
    requirements_with_tie = list(requirements)
    tied_requirement = MaterialRequirement(
        material_requirement_id="mr_contract_binding_tie",
        dataset_version_id=baseline.dataset_version.dataset_version_id,
        work_order_id=work_order.work_order_id,
        material_id=second_po.material_id,
        required_quantity=Decimal("1.0000"),
        need_by_at=common_receipt - timedelta(hours=1),
    )
    requirements_with_tie.append(tied_requirement)

    work_order.actual_start_at = common_receipt - timedelta(hours=2)
    work_order.actual_end_at = common_receipt + timedelta(hours=6)
    operations = cast(tuple[Operation, ...], baseline.rows_for("fact_operation"))
    work_operations = sorted(
        (row for row in operations if row.work_order_id == work_order.work_order_id),
        key=lambda row: row.sequence_number,
    )
    for index, operation in enumerate(work_operations):
        operation.actual_start_at = work_order.actual_start_at + timedelta(hours=index)
        operation.actual_end_at = operation.actual_start_at + timedelta(minutes=45)
    inspections = cast(
        tuple[QualityInspection, ...], baseline.rows_for("fact_quality_inspection")
    )
    inspection = next(row for row in inspections if row.work_order_id == work_order.work_order_id)
    inspection.inspection_at = work_order.actual_end_at + timedelta(hours=1)
    reworks = cast(tuple[Rework, ...], baseline.rows_for("fact_rework"))
    work_reworks = [row for row in reworks if row.work_order_id == work_order.work_order_id]
    for rework in work_reworks:
        rework.rework_start_at = inspection.inspection_at + timedelta(hours=1)
        rework.rework_end_at = rework.rework_start_at + timedelta(hours=2)
    deliveries = cast(tuple[Delivery, ...], baseline.rows_for("fact_delivery"))
    work_deliveries = [
        row for row in deliveries if row.sales_order_id == work_order.sales_order_id
    ]
    for index, delivery in enumerate(work_deliveries):
        delivery.delivery_at = inspection.inspection_at + timedelta(hours=4 + index)

    baseline = _rebuild(
        baseline,
        {
            "bridge_product_material": components,
            "fact_material_requirement": requirements_with_tie,
        },
    )
    result = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    relationships = {link.relationship for link in result.ground_truth.causal_chain}
    assert relationships == SUPPLIER_RELATIONSHIPS
    shortage_links = [
        link
        for link in result.ground_truth.causal_chain
        if link.relationship == "creates_material_shortage"
    ]
    assert len(shortage_links) == 11
    assert len(result.ground_truth.affected_entities_by_table["fact_work_order"]) == 10
    binding_links = [
        link
        for link in result.ground_truth.causal_chain
        if link.relationship == "sets_work_order_material_delay"
        and link.target_entity_id == work_order.work_order_id
    ]
    assert {link.source_entity_id for link in binding_links} == {
        first_requirement.material_requirement_id,
        tied_requirement.material_requirement_id,
    }
    scenario_work_order = _row_map(
        result.dataset, "fact_work_order", "work_order_id", WorkOrder
    )[work_order.work_order_id]
    shift = common_receipt - work_order.actual_start_at
    assert scenario_work_order.actual_start_at == work_order.actual_start_at + shift
    assert scenario_work_order.actual_end_at == work_order.actual_end_at + shift
    assert set(result.ground_truth.affected_entities_by_table) >= {
        "fact_purchase_order",
        "fact_work_order",
        "fact_operation",
        "fact_quality_inspection",
        "fact_rework",
        "fact_delivery",
    }
    assert len(result.dataset.rows_for("fact_rework")) == len(reworks)
    assert not {
        "dim_supplier",
        "dim_material",
    }.intersection(result.ground_truth.affected_entities_by_table)
    _assert_hgt_referential_integrity(result, quality=False)


def test_supplier_repeatability_generated_at_order_and_baseline_isolation() -> None:
    baseline = _baseline()
    config = _supplier_config()
    payload_before = canonical_business_payload(baseline.rows_by_table)
    hash_before = baseline.content_hash
    count_before = baseline.row_count_total
    dataset_id_before = baseline.dataset_version.dataset_version_id

    first = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    repeated = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    later = apply_scenario(
        baseline,
        config,
        generated_at=datetime(2035, 9, 1, tzinfo=UTC),
    )
    reversed_baseline = GeneratedDataset(
        baseline.dataset_version,
        MappingProxyType(
            {
                table_name: tuple(reversed(baseline.rows_for(table_name)))
                for table_name in reversed(CANONICAL_TABLE_ORDER)
            }
        ),
    )
    reordered = apply_scenario(reversed_baseline, config, generated_at=GENERATED_AT)

    identity = build_scenario_identity(baseline, config)
    assert identity.namespace == build_scenario_identity(reversed_baseline, config).namespace
    assert first.ground_truth.scenario_id == identity.scenario_id
    assert first.ground_truth.scenario_id == repeated.ground_truth.scenario_id
    assert first.ground_truth.scenario_id == later.ground_truth.scenario_id
    assert first.dataset.dataset_version.dataset_version_id == (
        repeated.dataset.dataset_version.dataset_version_id
    )
    assert first.dataset.dataset_version.dataset_version_id == (
        later.dataset.dataset_version.dataset_version_id
    )

    first_payload = canonical_business_payload(first.dataset.rows_by_table)
    assert first_payload == canonical_business_payload(repeated.dataset.rows_by_table)
    assert first_payload == canonical_business_payload(later.dataset.rows_by_table)
    assert first_payload == canonical_business_payload(reordered.dataset.rows_by_table)
    assert first.dataset.content_hash == repeated.dataset.content_hash
    assert first.dataset.content_hash == later.dataset.content_hash
    assert first.dataset.content_hash == reordered.dataset.content_hash
    assert _supplier_outcome(first) == _supplier_outcome(repeated)
    assert _supplier_outcome(first) == _supplier_outcome(later)
    assert _supplier_outcome(first) == _supplier_outcome(reordered)
    assert dict(first.ground_truth.affected_entities_by_table) == dict(
        later.ground_truth.affected_entities_by_table
    )
    assert dict(first.ground_truth.affected_entities_by_table) == dict(
        reordered.ground_truth.affected_entities_by_table
    )
    assert first.ground_truth.hgt_id == later.ground_truth.hgt_id
    assert first.ground_truth.hgt_hash == later.ground_truth.hgt_hash
    assert first.ground_truth.hgt_hash == reordered.ground_truth.hgt_hash
    assert _dataset_version_without_generated_at(first.dataset) == (
        _dataset_version_without_generated_at(later.dataset)
    )
    assert first.dataset.dataset_version.generated_at != (
        later.dataset.dataset_version.generated_at
    )

    assert canonical_business_payload(baseline.rows_by_table) == payload_before
    assert baseline.content_hash == hash_before
    assert baseline.row_count_total == count_before
    assert baseline.dataset_version.dataset_version_id == dataset_id_before
    for table_name in CANONICAL_TABLE_ORDER:
        baseline_rows = baseline.rows_for(table_name)
        scenario_rows = first.dataset.rows_for(table_name)
        assert {id(row) for row in baseline_rows}.isdisjoint(
            id(row) for row in scenario_rows
        )
        assert {id(sqlalchemy_inspect(row)) for row in baseline_rows}.isdisjoint(
            id(sqlalchemy_inspect(row)) for row in scenario_rows
        )
        assert all(object_session(row) is None for row in scenario_rows)
    _assert_hgt_referential_integrity(first, quality=False)


def test_quality_frozen_defaults_materialize_real_demo_graph() -> None:
    baseline = _demo_baseline()
    window_start, window_end = default_demo_window(
        ScenarioType.QUALITY_DETERIORATION,
        baseline.dataset_version.period_start,
        GenerationProfile.DEMO,
    )
    config = QualityDeteriorationConfig(
        scenario_version=SCENARIO_VERSION,
        scenario_seed=SCENARIO_SEED,
        window_start=window_start,
        window_end=window_end,
    )
    assert config.affected_product_count == 2
    assert config.affected_work_center_count == 1
    assert config.failure_probability_multiplier == Decimal("2.2")
    assert config.rework_probability_delta == Decimal("0.30")
    assert config.rework_duration_multiplier_min == Decimal("1.2")
    assert config.rework_duration_multiplier_max == Decimal("1.5")

    result = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    target_ids = set(result.ground_truth.target_entity_ids)
    selected_work_centers = {
        entity_id for entity_id in target_ids if entity_id.startswith("wc_")
    }
    selected_products = {
        entity_id for entity_id in target_ids if entity_id.startswith("prd_")
    }
    assert len(selected_work_centers) == 1
    assert len(selected_products) == 2
    assert result.ground_truth.target_entity_ids == tuple(
        sorted(selected_work_centers | selected_products)
    )

    work_orders = _row_map(baseline, "fact_work_order", "work_order_id", WorkOrder)
    operations = _row_map(baseline, "fact_operation", "operation_id", Operation)
    operations_by_work_order: dict[str, list[Operation]] = defaultdict(list)
    for operation in operations.values():
        operations_by_work_order[operation.work_order_id].append(operation)
    relevant: list[tuple[QualityInspection, str, str]] = []
    for inspection in cast(
        tuple[QualityInspection, ...], baseline.rows_for("fact_quality_inspection")
    ):
        if not config.window_start <= inspection.inspection_at < config.window_end:
            continue
        work_order = work_orders[inspection.work_order_id]
        resolved_operation: Operation | None = (
            operations.get(inspection.operation_id)
            if inspection.operation_id is not None
            else max(
                operations_by_work_order[inspection.work_order_id],
                key=lambda row: (row.sequence_number, row.operation_id),
            )
        )
        if (
            resolved_operation is None
            or resolved_operation.work_order_id != inspection.work_order_id
        ):
            continue
        if (
            work_order.product_id in selected_products
            and resolved_operation.work_center_id in selected_work_centers
        ):
            relevant.append(
                (
                    inspection,
                    work_order.product_id,
                    resolved_operation.work_center_id,
                )
            )

    relevant_ids = {inspection.inspection_id for inspection, _, _ in relevant}
    actual_edges = {
        (product_id, work_center_id)
        for _, product_id, work_center_id in relevant
    }
    assert {product_id for product_id, _ in actual_edges} == selected_products
    assert {work_center_id for _, work_center_id in actual_edges} == (
        selected_work_centers
    )
    assert all(
        product_id in selected_products and work_center_id in selected_work_centers
        for _, product_id, work_center_id in relevant
    )
    changed_inspection_ids = set(
        result.ground_truth.affected_entities_by_table["fact_quality_inspection"]
    )
    assert changed_inspection_ids <= relevant_ids

    baseline_failures = sum(inspection.result == "FAIL" for inspection, _, _ in relevant)
    target_failures = probability_target_count(
        len(relevant),
        min(
            Decimal("1"),
            (Decimal(baseline_failures) / Decimal(len(relevant)))
            * config.failure_probability_multiplier,
        ),
    )
    scenario_inspections = _row_map(
        result.dataset,
        "fact_quality_inspection",
        "inspection_id",
        QualityInspection,
    )
    assert sum(
        scenario_inspections[inspection_id].result == "FAIL"
        for inspection_id in relevant_ids
    ) == target_failures
    assert result.ground_truth.affected_entities_by_table.get("fact_rework")
    _assert_hgt_referential_integrity(result, quality=True)


def test_quality_graph_failure_rework_counts_and_new_identity_are_exact() -> None:
    baseline = _baseline()
    config = _quality_config()
    result = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    targets = set(result.ground_truth.target_entity_ids)
    assert len({value for value in targets if value.startswith("wc_")}) == 4
    assert len({value for value in targets if value.startswith("prd_")}) == 12

    baseline_inspections = cast(
        tuple[QualityInspection, ...], baseline.rows_for("fact_quality_inspection")
    )
    scenario_inspections = cast(
        tuple[QualityInspection, ...], result.dataset.rows_for("fact_quality_inspection")
    )
    baseline_fail = sum(row.result == "FAIL" for row in baseline_inspections)
    target_fail = probability_target_count(
        len(baseline_inspections),
        (Decimal(baseline_fail) / Decimal(len(baseline_inspections)))
        * config.failure_probability_multiplier,
    )
    assert (len(baseline_inspections), baseline_fail, target_fail) == (150, 11, 25)
    assert sum(row.result == "FAIL" for row in scenario_inspections) == target_fail
    assert len(
        result.ground_truth.affected_entities_by_table["fact_quality_inspection"]
    ) == 14
    for inspection in scenario_inspections:
        assert inspection.passed_quantity + inspection.failed_quantity == (
            inspection.inspected_quantity
        )
        if inspection.result == "PASS":
            assert inspection.failed_quantity == 0
        else:
            assert inspection.failed_quantity > 0

    baseline_reworks = cast(tuple[Rework, ...], baseline.rows_for("fact_rework"))
    scenario_reworks = cast(tuple[Rework, ...], result.dataset.rows_for("fact_rework"))
    assert len(baseline_reworks) == 5
    assert len(scenario_reworks) == 19
    new_reworks = [
        row
        for row in scenario_reworks
        if row.rework_id not in {baseline_row.rework_id for baseline_row in baseline_reworks}
    ]
    assert len(new_reworks) == 14
    identity = build_scenario_identity(baseline, config)
    scenario_inspection_by_id = {row.inspection_id: row for row in scenario_inspections}
    for rework in new_reworks:
        assert rework.rework_id == _scenario_rework_id(identity, rework.inspection_id)
        assert len(rework.rework_id) == 48
        assert rework.rework_id.startswith("rw_")
        inspection = scenario_inspection_by_id[rework.inspection_id]
        assert rework.rework_quantity == inspection.failed_quantity
        assert timedelta(hours=1) <= rework.rework_start_at - inspection.inspection_at <= (
            timedelta(hours=6)
        )
        assert rework.rework_reason in {
            "SYNTHETIC_DIMENSIONAL_ADJUSTMENT",
            "SYNTHETIC_ASSEMBLY_CORRECTION",
            "SYNTHETIC_SURFACE_REFINISH",
        }
    assert {link.relationship for link in result.ground_truth.causal_chain} == (
        QUALITY_RELATIONSHIPS - {"shifts_delivery_time"}
    )
    assert not {
        "dim_product",
        "dim_work_center",
    }.intersection(result.ground_truth.affected_entities_by_table)
    scenario_inspection_ids = {row.inspection_id for row in scenario_inspections}
    scenario_work_order_ids = {
        row.work_order_id
        for row in cast(tuple[WorkOrder, ...], result.dataset.rows_for("fact_work_order"))
    }
    scenario_work_center_ids = {
        row.work_center_id
        for row in cast(
            tuple[WorkCenter, ...], result.dataset.rows_for("dim_work_center")
        )
    }
    for rework in scenario_reworks:
        assert rework.inspection_id in scenario_inspection_ids
        assert rework.work_order_id in scenario_work_order_ids
        assert rework.work_center_id in scenario_work_center_ids
        inspection = scenario_inspection_by_id[rework.inspection_id]
        assert 0 < rework.rework_quantity <= inspection.failed_quantity
        assert rework.rework_start_at >= inspection.inspection_at
        assert rework.rework_start_at <= rework.rework_end_at
    changed_targets = {
        (table_name, entity_id)
        for table_name, entity_ids in result.ground_truth.affected_entities_by_table.items()
        for entity_id in entity_ids
    }
    for link in result.ground_truth.causal_chain:
        if link.target_table in result.ground_truth.affected_entities_by_table:
            assert (link.target_table, link.target_entity_id) in changed_targets
    _assert_hgt_referential_integrity(result, quality=True)


def test_quality_duration_median_rounding_and_completion_propagation() -> None:
    baseline = _baseline()
    config = _quality_config()
    result = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    baseline_reworks = _row_map(baseline, "fact_rework", "rework_id", Rework)
    scenario_reworks = _row_map(result.dataset, "fact_rework", "rework_id", Rework)
    reference = median_duration_microseconds(
        [row.rework_end_at - row.rework_start_at for row in baseline_reworks.values()]
    )
    identity = build_scenario_identity(baseline, config)
    for rework_id, baseline_rework in baseline_reworks.items():
        scenario_rework = scenario_reworks[rework_id]
        multiplier = choose_hundredth_decimal(
            config.rework_duration_multiplier_min,
            config.rework_duration_multiplier_max,
            identity,
            "quality-rework-duration",
            rework_id,
        )
        assert scenario_rework.rework_start_at == baseline_rework.rework_start_at
        assert scenario_rework.rework_end_at == baseline_rework.rework_start_at + (
            ceil_duration(
                baseline_rework.rework_end_at - baseline_rework.rework_start_at,
                multiplier,
            )
        )
        assert scenario_rework.rework_end_at.microsecond == 0

    new_reworks = [row for key, row in scenario_reworks.items() if key not in baseline_reworks]
    for rework in new_reworks:
        multiplier = choose_hundredth_decimal(
            config.rework_duration_multiplier_min,
            config.rework_duration_multiplier_max,
            identity,
            "quality-rework-duration",
            rework.rework_id,
        )
        expected_seconds = int(
            ((reference * multiplier) / Decimal(1_000_000)).to_integral_value(
                rounding=ROUND_CEILING
            )
        )
        assert rework.rework_end_at - rework.rework_start_at == timedelta(
            seconds=expected_seconds
        )

    baseline_work_orders = _row_map(
        baseline, "fact_work_order", "work_order_id", WorkOrder
    )
    scenario_work_orders = _row_map(
        result.dataset, "fact_work_order", "work_order_id", WorkOrder
    )
    affected_reworks_by_work: dict[str, list[Rework]] = defaultdict(list)
    for rework_id in result.ground_truth.affected_entities_by_table["fact_rework"]:
        affected_reworks_by_work[scenario_reworks[rework_id].work_order_id].append(
            scenario_reworks[rework_id]
        )
    for work_order_id, reworks in affected_reworks_by_work.items():
        required = max(row.rework_end_at for row in reworks)
        assert scenario_work_orders[work_order_id].actual_start_at == (
            baseline_work_orders[work_order_id].actual_start_at
        )
        assert scenario_work_orders[work_order_id].planned_start_at == (
            baseline_work_orders[work_order_id].planned_start_at
        )
        assert scenario_work_orders[work_order_id].planned_end_at == (
            baseline_work_orders[work_order_id].planned_end_at
        )
        assert scenario_work_orders[work_order_id].actual_end_at == required
    completion_links = [
        link
        for link in result.ground_truth.causal_chain
        if link.relationship == "extends_work_order_completion"
    ]
    for link in completion_links:
        source_rework = scenario_reworks[link.source_entity_id]
        work_reworks = affected_reworks_by_work[link.target_entity_id]
        assert source_rework.rework_end_at == max(
            row.rework_end_at for row in work_reworks
        )


def test_quality_delivery_shift_fallback_and_unresolved_exclusion() -> None:
    baseline = _baseline()
    inspections = cast(
        tuple[QualityInspection, ...], baseline.rows_for("fact_quality_inspection")
    )
    for inspection in inspections:
        inspection.operation_id = None
    deliveries = cast(tuple[Delivery, ...], baseline.rows_for("fact_delivery"))
    work_orders = _row_map(baseline, "fact_work_order", "work_order_id", WorkOrder)
    for delivery in deliveries:
        work_order = next(
            row
            for row in work_orders.values()
            if row.sales_order_id == delivery.sales_order_id
        )
        inspection = next(
            row
            for row in inspections
            if row.work_order_id == work_order.work_order_id
        )
        delivery.delivery_at = inspection.inspection_at + timedelta(minutes=30)
    baseline = _rebuild(baseline)
    result = apply_scenario(baseline, _quality_config(), generated_at=GENERATED_AT)
    assert "shifts_delivery_time" in {
        link.relationship for link in result.ground_truth.causal_chain
    }
    assert "fact_delivery" in result.ground_truth.affected_entities_by_table
    baseline_deliveries = _row_map(baseline, "fact_delivery", "delivery_id", Delivery)
    scenario_deliveries = _row_map(
        result.dataset, "fact_delivery", "delivery_id", Delivery
    )
    for delivery_id in result.ground_truth.affected_entities_by_table["fact_delivery"]:
        assert scenario_deliveries[delivery_id].delivery_at > (
            baseline_deliveries[delivery_id].delivery_at
        )
    _assert_hgt_referential_integrity(result, quality=True)

    unresolved = _baseline()
    unresolved_inspection = cast(
        QualityInspection, unresolved.rows_for("fact_quality_inspection")[0]
    )
    unresolved_inspection.operation_id = "op_missing"
    unresolved = _rebuild(unresolved)
    unresolved_result = apply_scenario(
        unresolved, _quality_config(), generated_at=GENERATED_AT
    )
    assert all(
        link.source_entity_id != unresolved_inspection.inspection_id
        and link.target_entity_id != unresolved_inspection.inspection_id
        for link in unresolved_result.ground_truth.causal_chain
    )


def test_quality_rejects_incoherent_zero_failure_missing_reference_and_collision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValueError, match="insufficient eligible products"):
        apply_scenario(
            _baseline(),
            _quality_config(affected_product_count=99),
            generated_at=GENERATED_AT,
        )

    incoherent = _baseline()
    inspection = cast(
        QualityInspection, incoherent.rows_for("fact_quality_inspection")[0]
    )
    inspection.passed_quantity += 1
    incoherent = _rebuild(incoherent)
    with pytest.raises(ValueError, match="incoherent baseline"):
        apply_scenario(incoherent, _quality_config(), generated_at=GENERATED_AT)

    zero_failure = _baseline()
    for row in cast(
        tuple[QualityInspection, ...], zero_failure.rows_for("fact_quality_inspection")
    ):
        row.result = "PASS"
        row.failed_quantity = 0
        row.passed_quantity = row.inspected_quantity
        row.defect_category = None
        row.severity = None
    zero_failure = _rebuild(zero_failure, {"fact_rework": ()})
    with pytest.raises(ValueError, match="nonzero baseline FAIL"):
        apply_scenario(zero_failure, _quality_config(), generated_at=GENERATED_AT)

    missing_reference = _rebuild(_baseline(), {"fact_rework": ()})
    with pytest.raises(ValueError, match="valid baseline duration reference"):
        apply_scenario(missing_reference, _quality_config(), generated_at=GENERATED_AT)

    collision = _baseline()
    existing_id = cast(Rework, collision.rows_for("fact_rework")[0]).rework_id
    monkeypatch.setattr(
        "flowlens.data.scenarios.quality._scenario_rework_id",
        lambda identity, inspection_id: existing_id,
    )
    with pytest.raises(ValueError, match="Rework ID collision"):
        apply_scenario(collision, _quality_config(), generated_at=GENERATED_AT)


def test_repeatability_generated_at_isolation_input_order_and_baseline_immutability() -> None:
    baseline = _baseline()
    config = _quality_config()
    payload_before = canonical_business_payload(baseline.rows_by_table)
    hash_before = baseline.content_hash
    count_before = baseline.row_count_total
    dataset_id_before = baseline.dataset_version.dataset_version_id
    first = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    second = apply_scenario(
        baseline,
        config,
        generated_at=datetime(2035, 9, 1, tzinfo=UTC),
    )
    reversed_baseline = GeneratedDataset(
        baseline.dataset_version,
        MappingProxyType(
            {
                table_name: tuple(reversed(baseline.rows_for(table_name)))
                for table_name in reversed(CANONICAL_TABLE_ORDER)
            }
        ),
    )
    reordered = apply_scenario(reversed_baseline, config, generated_at=GENERATED_AT)

    assert canonical_business_payload(baseline.rows_by_table) == payload_before
    assert baseline.content_hash == hash_before
    assert baseline.row_count_total == count_before
    assert baseline.dataset_version.dataset_version_id == dataset_id_before
    assert first.dataset.content_hash == second.dataset.content_hash
    assert first.dataset.content_hash == reordered.dataset.content_hash
    assert first.ground_truth.hgt_hash == second.ground_truth.hgt_hash
    assert first.ground_truth.hgt_hash == reordered.ground_truth.hgt_hash
    assert first.ground_truth.target_entity_ids == second.ground_truth.target_entity_ids
    assert first.dataset.row_count_total == baseline.row_count_total + 14
    assert second.dataset.dataset_version.generated_at != (
        first.dataset.dataset_version.generated_at
    )
    changed_semantics = apply_scenario(
        baseline,
        _quality_config(scenario_seed=SCENARIO_SEED + 1),
        generated_at=GENERATED_AT,
    )
    assert changed_semantics.ground_truth.scenario_id != first.ground_truth.scenario_id
    assert changed_semantics.ground_truth.hgt_hash != first.ground_truth.hgt_hash
    assert changed_semantics.dataset.content_hash != first.dataset.content_hash
    for table_name in CANONICAL_TABLE_ORDER:
        baseline_rows = {id(row) for row in baseline.rows_for(table_name)}
        scenario_rows = first.dataset.rows_for(table_name)
        assert not baseline_rows.intersection(id(row) for row in scenario_rows)
        assert all(object_session(row) is None for row in scenario_rows)
        assert all(
            sqlalchemy_inspect(row) is not sqlalchemy_inspect(baseline_row)
            for row in scenario_rows
            for baseline_row in baseline.rows_for(table_name)
            if getattr(row, "dataset_version_id", None)
            == first.dataset.dataset_version.dataset_version_id
        )
    forbidden = {
        "scenario_id",
        "scenario_name",
        "scenario_type",
        "root_cause",
        "true_root_cause",
        "is_affected",
        "is_anomaly",
        "expected_causal_chain",
    }
    assert all(
        forbidden.isdisjoint(row.__mapper__.columns.keys())
        for _, row in first.dataset.iter_business_rows()
    )
