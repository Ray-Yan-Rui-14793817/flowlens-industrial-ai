"""Protected replay fixtures and the frozen W03-C07 replay matrix."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal
from functools import cache
from typing import cast

import pytest

from flowlens.data import Base
from flowlens.data.generation import BUSINESS_TIMEZONE, GeneratedDataset
from flowlens.data.generation.canonical import CanonicalPayload, canonical_business_payload
from flowlens.data.models import SalesOrder
from flowlens.data.scenarios import (
    CapacitySurgeConfig,
    QualityDeteriorationConfig,
    ScenarioConfig,
    ScenarioResult,
    SupplierDegradationConfig,
    apply_scenario,
)
from flowlens.decision.c04_registry import build_candidate_set
from flowlens.decision.c04_simulation import build_simulation_bundle
from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.context import build_decision_context
from flowlens.decision.contracts import DecisionPacket, DecisionRun
from flowlens.decision.diagnosis import evaluate_c03
from flowlens.decision.enums import InterventionFamily, SignalState, SignalType
from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.primitives import ScalarValue, Uncertainty
from flowlens.decision.serialization import canonical_json_bytes, derive_artifact_id
from flowlens.decision.snapshot import build_state_snapshot, source_unknowns
from flowlens.decision.temporal import (
    SOURCE_FIELDS,
    ProjectedSourceField,
    project_record,
    validate_as_of,
)
from flowlens.evaluation import TruthEffectMode, evaluate_recommendation
from flowlens.evaluation.c07_replay import (
    derive_affected_order_ids,
    select_created_affected_order,
    select_existing_affected_order,
    select_neutral_order,
)
from test_c04_simulation import successful_baseline
from test_c05_policy import neutral_records, records_for_active
from test_decision_snapshot import ORDER_AT, make_run
from test_scenario_interventions import _baseline as intervention_baseline

SCENARIO_VERSION = "1.0.0"
SCENARIO_SEED = 20_260_901

type Record = tuple[str, str, dict[str, ScalarValue]]

_SOURCE_ID_FIELDS = {
    "fact_sales_order": "sales_order_id",
    "fact_work_order": "work_order_id",
    "fact_operation": "operation_id",
    "fact_material_requirement": "material_requirement_id",
    "fact_purchase_order": "purchase_order_id",
    "fact_inventory_snapshot": "inventory_snapshot_id",
    "fact_quality_inspection": "inspection_id",
    "fact_rework": "rework_id",
    "fact_delivery": "delivery_id",
}
_SOURCE_TABLES = tuple(_SOURCE_ID_FIELDS)


@dataclass(frozen=True, slots=True)
class _OrderClosure:
    records: tuple[Record, ...]
    target_order_at: datetime
    work_order_count: int
    requirement_count: int
    required_material_ids: tuple[str, ...]
    inventory_material_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReplayCase:
    baseline: GeneratedDataset
    scenario: ScenarioResult
    scenario_packet: DecisionPacket
    baseline_packet: DecisionPacket | None
    baseline_payload_before: CanonicalPayload
    scenario_payload_before: CanonicalPayload


def _config(kind: str) -> ScenarioConfig:
    window_start = datetime(2026, 1, 1, tzinfo=BUSINESS_TIMEZONE)
    window_end = datetime(2026, 4, 1, tzinfo=BUSINESS_TIMEZONE)
    if kind == "supplier":
        return SupplierDegradationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=SCENARIO_SEED,
            window_start=window_start,
            window_end=window_end,
            late_probability_delta=Decimal("1"),
            additional_delay_business_days_min=20,
            additional_delay_business_days_max=20,
        )
    if kind == "quality":
        return QualityDeteriorationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=SCENARIO_SEED,
            window_start=window_start,
            window_end=window_end,
            affected_product_count=12,
            affected_work_center_count=4,
        )
    modes = {
        "capacity_combined": (Decimal("1.5"), Decimal("1.7")),
        "capacity_arrival": (Decimal("1.5"), Decimal("1")),
        "capacity_queue": (Decimal("1"), Decimal("1.7")),
        "capacity_neutral": (Decimal("1"), Decimal("1")),
    }
    arrival, queue = modes[kind]
    return CapacitySurgeConfig(
        scenario_version=SCENARIO_VERSION,
        scenario_seed=SCENARIO_SEED,
        window_start=window_start,
        window_end=window_end,
        arrival_volume_multiplier=arrival,
        queue_time_multiplier=queue,
    )


def _string_attr(row: Base, field: str) -> str:
    value = getattr(row, field)
    if not isinstance(value, str):
        raise AssertionError(f"{field} must be a string")
    return value


def _record_id(entity: str, row: Base) -> str:
    return _string_attr(row, _SOURCE_ID_FIELDS[entity])


def _record(entity: str, row: Base) -> Record:
    return (
        entity,
        _record_id(entity, row),
        {field: cast(ScalarValue, getattr(row, field)) for field in SOURCE_FIELDS[entity]},
    )


def _order_closure(dataset: GeneratedDataset, order_id: str) -> _OrderClosure:
    sales_orders = tuple(
        row
        for row in dataset.rows_for("fact_sales_order")
        if _string_attr(row, "sales_order_id") == order_id
    )
    if len(sales_orders) != 1:
        raise AssertionError("target Sales Order must exist exactly once")
    target_order_at = cast(SalesOrder, sales_orders[0]).order_at
    if not isinstance(target_order_at, datetime):
        raise AssertionError("target Sales Order order_at must be a datetime")

    work_orders = tuple(
        row
        for row in dataset.rows_for("fact_work_order")
        if _string_attr(row, "sales_order_id") == order_id
    )
    work_order_ids = {_string_attr(row, "work_order_id") for row in work_orders}
    operations = tuple(
        row
        for row in dataset.rows_for("fact_operation")
        if _string_attr(row, "work_order_id") in work_order_ids
    )
    requirements = tuple(
        row
        for row in dataset.rows_for("fact_material_requirement")
        if _string_attr(row, "work_order_id") in work_order_ids
    )
    inspections = tuple(
        row
        for row in dataset.rows_for("fact_quality_inspection")
        if _string_attr(row, "work_order_id") in work_order_ids
    )
    reworks = tuple(
        row
        for row in dataset.rows_for("fact_rework")
        if _string_attr(row, "work_order_id") in work_order_ids
    )
    deliveries = tuple(
        row
        for row in dataset.rows_for("fact_delivery")
        if _string_attr(row, "sales_order_id") == order_id
    )
    required_material_ids = tuple(
        sorted({_string_attr(row, "material_id") for row in requirements})
    )
    purchase_orders = tuple(
        row
        for row in dataset.rows_for("fact_purchase_order")
        if _string_attr(row, "material_id") in required_material_ids
    )
    inventory = tuple(
        row
        for row in dataset.rows_for("fact_inventory_snapshot")
        if _string_attr(row, "material_id") in required_material_ids
    )
    selected = {
        "fact_sales_order": sales_orders,
        "fact_work_order": work_orders,
        "fact_operation": operations,
        "fact_material_requirement": requirements,
        "fact_purchase_order": purchase_orders,
        "fact_inventory_snapshot": inventory,
        "fact_quality_inspection": inspections,
        "fact_rework": reworks,
        "fact_delivery": deliveries,
    }
    records = tuple(
        _record(entity, row)
        for entity in _SOURCE_TABLES
        for row in sorted(selected[entity], key=lambda item: _record_id(entity, item))
    )
    return _OrderClosure(
        records=records,
        target_order_at=target_order_at,
        work_order_count=len(work_orders),
        requirement_count=len(requirements),
        required_material_ids=required_material_ids,
        inventory_material_ids=tuple(
            sorted({_string_attr(row, "material_id") for row in inventory})
        ),
    )


def _adversarial_records_for_order(
    order_id: str,
    family: InterventionFamily | None,
) -> list[Record]:
    source = neutral_records() if family is None else records_for_active(family)
    result: list[Record] = []
    for entity, record_id, supplied in source:
        values: dict[str, ScalarValue] = dict(supplied)
        selected_id = record_id
        if entity == "fact_sales_order":
            selected_id = order_id
            values["sales_order_id"] = order_id
        elif entity in ("fact_work_order", "fact_delivery"):
            values["sales_order_id"] = order_id
        result.append((entity, selected_id, values))
    return result


def _packet_from_records(
    dataset: GeneratedDataset,
    order_id: str,
    as_of_time: datetime,
    records: tuple[Record, ...] | list[Record],
    *,
    target_order_at: datetime,
    unknowns: tuple[Uncertainty, ...] = (),
) -> DecisionPacket:
    validate_as_of(
        as_of_time,
        dataset.dataset_version.period_start,
        dataset.dataset_version.period_end,
    )
    template = make_run(
        as_of_time,
        dataset_version=dataset.dataset_version.dataset_version_id,
        dataset_hash=dataset.dataset_version.content_hash,
    )
    identity = {
        "order_id": order_id,
        "as_of_time": as_of_time,
        "dataset_version": dataset.dataset_version.dataset_version_id,
        "dataset_hash": dataset.dataset_version.content_hash,
        "contract_bundle_version": template.contract_bundle_version,
        "tool_registry_version": template.tool_registry_version,
    }
    run = DecisionRun(
        run_id=derive_artifact_id("decision-run", "decision-run.v1", identity),
        schema_version="decision-run.v1",
        order_id=order_id,
        as_of_time=as_of_time,
        dataset_version=dataset.dataset_version.dataset_version_id,
        dataset_hash=dataset.dataset_version.content_hash,
        contract_bundle_version=template.contract_bundle_version,
        tool_registry_version=template.tool_registry_version,
        provenance=template.provenance,
    )
    projected: list[ProjectedSourceField] = []
    for entity, record_id, values in records:
        projected.extend(
            project_record(
                entity,
                record_id,
                values,
                as_of_time=as_of_time,
                period_start=dataset.dataset_version.period_start,
                target_order_at=target_order_at,
            )
        )
    snapshot = build_state_snapshot(run, projected, unknowns)
    evidence = build_evidence_bundle(snapshot)
    context = build_decision_context(snapshot, evidence)
    signals, diagnosis = evaluate_c03(evidence, context)
    candidates = build_candidate_set(evidence, context, signals, diagnosis)
    simulations = build_simulation_bundle(
        run,
        snapshot,
        evidence,
        context,
        signals,
        diagnosis,
        candidates,
        baseline=dataset,
    )
    return build_decision_packet(
        run,
        snapshot,
        evidence,
        context,
        signals,
        diagnosis,
        candidates,
        simulations,
    )


def packet_from_dataset(
    dataset: GeneratedDataset,
    order_id: str,
    as_of_time: datetime,
) -> DecisionPacket:
    """Build one family-blind runtime packet from the supplied business rows."""

    closure = _order_closure(dataset, order_id)
    if closure.target_order_at > as_of_time:
        raise AssertionError("decision time precedes target Sales Order")
    unknowns = source_unknowns(
        closure.work_order_count,
        closure.requirement_count,
        closure.required_material_ids,
        closure.inventory_material_ids,
    )
    return _packet_from_records(
        dataset,
        order_id,
        as_of_time,
        closure.records,
        target_order_at=closure.target_order_at,
        unknowns=unknowns,
    )


def adversarial_packet_fixture(
    dataset: GeneratedDataset,
    order_id: str,
    family: InterventionFamily | None,
    as_of_time: datetime,
) -> DecisionPacket:
    """Build a clearly synthetic packet used only by adversarial metric tests."""

    records = _adversarial_records_for_order(order_id, family)
    projected = tuple(
        item
        for entity, record_id, values in records
        for item in project_record(
            entity,
            record_id,
            values,
            as_of_time=as_of_time,
            period_start=dataset.dataset_version.period_start,
            target_order_at=ORDER_AT,
        )
    )
    observed = {(item.source_entity, item.source_record_id) for item in projected}
    required_materials = tuple(
        str(item.value)
        for item in projected
        if item.source_entity == "fact_material_requirement"
        and item.source_field == "material_id"
    )
    inventory_materials = tuple(
        str(item.value)
        for item in projected
        if item.source_entity == "fact_inventory_snapshot"
        and item.source_field == "material_id"
    )
    return _packet_from_records(
        dataset,
        order_id,
        as_of_time,
        records,
        target_order_at=ORDER_AT,
        unknowns=source_unknowns(
            sum(entity == "fact_work_order" for entity, _ in observed),
            sum(entity == "fact_material_requirement" for entity, _ in observed),
            required_materials,
            inventory_materials,
        ),
    )


@cache
def replay_case(kind: str) -> ReplayCase:
    baseline = (
        successful_baseline()
        if kind.startswith("capacity_")
        else intervention_baseline()
    )
    scenario = apply_scenario(
        baseline,
        _config(kind),
        generated_at=datetime(2026, 9, 1, 9, tzinfo=BUSINESS_TIMEZONE),
    )
    baseline_payload_before = canonical_business_payload(baseline.rows_by_table)
    scenario_payload_before = canonical_business_payload(scenario.dataset.rows_by_table)
    if kind == "capacity_neutral":
        order_id = select_neutral_order(baseline, scenario.dataset)
    elif kind == "capacity_arrival":
        selected = select_created_affected_order(
            baseline, scenario.dataset, scenario.ground_truth
        )
        assert selected is not None
        order_id = selected
    else:
        selected = select_existing_affected_order(
            baseline, scenario.dataset, scenario.ground_truth
        )
        assert selected is not None
        order_id = selected
    common_period_end = min(
        baseline.dataset_version.period_end,
        scenario.dataset.dataset_version.period_end,
    )
    as_of = datetime.combine(common_period_end, time.max, BUSINESS_TIMEZONE)
    scenario_packet = packet_from_dataset(scenario.dataset, order_id, as_of)
    baseline_packet = (
        None if kind == "capacity_arrival" else packet_from_dataset(baseline, order_id, as_of)
    )
    return ReplayCase(
        baseline,
        scenario,
        scenario_packet,
        baseline_packet,
        baseline_payload_before,
        scenario_payload_before,
    )


def metric_map(case: ReplayCase) -> dict[str, object]:
    result = evaluate_recommendation(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )
    return {item.name: item.value for item in result.metrics}


@pytest.mark.parametrize(
    ("kind", "mode", "expected_family"),
    (
        ("supplier", TruthEffectMode.EFFECTFUL_OBSERVABLE, "SUPPLIER_INTERVENTION"),
        ("quality", TruthEffectMode.EFFECTFUL_OBSERVABLE, "QUALITY_INTERVENTION"),
        ("capacity_combined", TruthEffectMode.EFFECTFUL_OBSERVABLE, "CAPACITY_INTERVENTION"),
        (
            "capacity_arrival",
            TruthEffectMode.EFFECTFUL_NOT_OBSERVABLE,
            "CAPACITY_INTERVENTION",
        ),
        ("capacity_queue", TruthEffectMode.EFFECTFUL_OBSERVABLE, "CAPACITY_INTERVENTION"),
        ("capacity_neutral", TruthEffectMode.NEUTRAL_CONTROL, None),
    ),
)
def test_required_replay_matrix(
    kind: str,
    mode: TruthEffectMode,
    expected_family: str | None,
) -> None:
    case = replay_case(kind)
    metrics = metric_map(case)
    assert metrics["truth.effect_mode"] == mode.value
    assert metrics["truth.expected_family"] == expected_family
    if mode is TruthEffectMode.EFFECTFUL_OBSERVABLE:
        for name in (
            "evaluation.cause_direction_correct",
            "evaluation.candidate_relevance",
            "evaluation.recommendation_coverage",
            "evaluation.false_positive",
        ):
            assert metrics[name] in (True, False, None)
    elif mode is TruthEffectMode.EFFECTFUL_NOT_OBSERVABLE:
        assert metrics["evaluation.applicable"] is False
        assert metrics["evaluation.cause_direction_correct"] is None
    else:
        assert metrics["evaluation.neutral_stability"] is True
        assert metrics["evaluation.false_positive"] is False

    capacity = next(
        item
        for item in case.scenario_packet.signals.signals
        if item.signal_type is SignalType.CAPACITY_PRESSURE
    )
    assert capacity.state is SignalState.UNKNOWN


_REPLAY_KINDS = (
    "supplier",
    "quality",
    "capacity_combined",
    "capacity_arrival",
    "capacity_queue",
    "capacity_neutral",
)


def _bound_packets(
    case: ReplayCase,
) -> tuple[tuple[DecisionPacket, GeneratedDataset], ...]:
    result = [(case.scenario_packet, case.scenario.dataset)]
    if case.baseline_packet is not None:
        result.append((case.baseline_packet, case.baseline))
    return tuple(result)


def _source_row_index(dataset: GeneratedDataset) -> dict[tuple[str, str], Base]:
    return {
        (entity, _record_id(entity, row)): row
        for entity in _SOURCE_TABLES
        for row in dataset.rows_for(entity)
    }


@pytest.mark.parametrize("kind", _REPLAY_KINDS)
def test_r1_g1_g2_and_g6_packets_bind_to_actual_dataset_rows(kind: str) -> None:
    case = replay_case(kind)
    for packet, dataset in _bound_packets(case):
        index = _source_row_index(dataset)
        assert packet.run.dataset_version == dataset.dataset_version.dataset_version_id
        assert packet.run.dataset_hash == dataset.dataset_version.content_hash
        for entry in packet.snapshot.entries:
            key = (entry.source_ref.source_entity, entry.source_ref.source_record_id)
            assert key in index
            assert entry.value == getattr(index[key], entry.field)


@pytest.mark.parametrize("kind", _REPLAY_KINDS)
def test_r1_g3_actual_sales_order_time_drives_temporal_projection(kind: str) -> None:
    case = replay_case(kind)
    for packet, dataset in _bound_packets(case):
        closure = _order_closure(dataset, packet.run.order_id)
        planned = tuple(
            entry
            for entry in packet.snapshot.entries
            if entry.source_ref.source_entity
            in {"fact_work_order", "fact_operation", "fact_material_requirement"}
            and entry.field
            not in {"actual_start_at", "actual_end_at", "completed_quantity"}
        )
        assert planned
        assert all(entry.available_at == closure.target_order_at for entry in planned)


def test_r1_g4_g5_and_g7_real_builder_is_family_and_hgt_blind() -> None:
    assert tuple(inspect.signature(packet_from_dataset).parameters) == (
        "dataset",
        "order_id",
        "as_of_time",
    )
    real_source = inspect.getsource(packet_from_dataset) + inspect.getsource(_order_closure)
    for token in (
        "InterventionFamily",
        "ScenarioType",
        "HiddenGroundTruth",
        "expected_family",
        "expected_signal",
        "truth_mode",
        "neutral_records",
        "records_for_active",
    ):
        assert token not in real_source
    replay_source = inspect.getsource(replay_case)
    assert "adversarial_packet_fixture" not in replay_source
    assert "neutral_records" not in replay_source
    assert "records_for_active" not in replay_source


@pytest.mark.parametrize("kind", _REPLAY_KINDS)
def test_r1_g8_packet_build_and_evaluation_do_not_mutate_datasets(kind: str) -> None:
    case = replay_case(kind)
    metric_map(case)
    assert canonical_business_payload(case.baseline.rows_by_table) == (
        case.baseline_payload_before
    )
    assert canonical_business_payload(case.scenario.dataset.rows_by_table) == (
        case.scenario_payload_before
    )


def test_affected_order_selection_is_sorted_and_bound() -> None:
    case = replay_case("capacity_combined")
    affected = derive_affected_order_ids(case.scenario.dataset, case.scenario.ground_truth)
    assert affected == tuple(sorted(set(affected)))
    assert case.scenario_packet.run.order_id in affected


def test_same_process_replay_is_byte_identical_and_non_mutating() -> None:
    case = replay_case("supplier")
    before_rows = canonical_business_payload(case.scenario.dataset.rows_by_table)
    before_packet = canonical_json_bytes(case.scenario_packet)
    first = evaluate_recommendation(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )
    second = evaluate_recommendation(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert first.recommendation_evaluation_id == second.recommendation_evaluation_id
    assert canonical_business_payload(case.scenario.dataset.rows_by_table) == before_rows
    assert canonical_json_bytes(case.scenario_packet) == before_packet
