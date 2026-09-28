"""Protected replay fixtures and the frozen W03-C07 replay matrix."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal
from functools import cache

import pytest

from flowlens.data.generation import BUSINESS_TIMEZONE, GeneratedDataset
from flowlens.data.generation.canonical import canonical_business_payload
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
from flowlens.decision.enums import InterventionFamily
from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.primitives import ScalarValue
from flowlens.decision.serialization import canonical_json_bytes, derive_artifact_id
from flowlens.decision.snapshot import build_state_snapshot, source_unknowns
from flowlens.decision.temporal import ProjectedSourceField, project_record
from flowlens.evaluation import TruthEffectMode, evaluate_recommendation
from flowlens.evaluation.c07_replay import (
    derive_affected_order_ids,
    select_created_affected_order,
    select_existing_affected_order,
    select_neutral_order,
)
from test_c03_signals import Record
from test_c04_simulation import successful_baseline
from test_c05_policy import neutral_records, records_for_active
from test_decision_snapshot import ORDER_AT, make_run
from test_scenario_interventions import _baseline as intervention_baseline

SCENARIO_VERSION = "1.0.0"
SCENARIO_SEED = 20_260_901


@dataclass(frozen=True, slots=True)
class ReplayCase:
    baseline: GeneratedDataset
    scenario: ScenarioResult
    scenario_packet: DecisionPacket
    baseline_packet: DecisionPacket | None


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


def _records_for_order(
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


def _packet(
    dataset: GeneratedDataset,
    order_id: str,
    family: InterventionFamily | None,
    as_of: datetime,
) -> DecisionPacket:
    template = make_run(
        as_of,
        dataset_version=dataset.dataset_version.dataset_version_id,
        dataset_hash=dataset.dataset_version.content_hash,
    )
    identity = {
        "order_id": order_id,
        "as_of_time": as_of,
        "dataset_version": dataset.dataset_version.dataset_version_id,
        "dataset_hash": dataset.dataset_version.content_hash,
        "contract_bundle_version": template.contract_bundle_version,
        "tool_registry_version": template.tool_registry_version,
    }
    run = DecisionRun(
        run_id=derive_artifact_id("decision-run", "decision-run.v1", identity),
        schema_version="decision-run.v1",
        order_id=order_id,
        as_of_time=as_of,
        dataset_version=dataset.dataset_version.dataset_version_id,
        dataset_hash=dataset.dataset_version.content_hash,
        contract_bundle_version=template.contract_bundle_version,
        tool_registry_version=template.tool_registry_version,
        provenance=template.provenance,
    )
    projected: list[ProjectedSourceField] = []
    records = _records_for_order(order_id, family)
    for entity, record_id, values in records:
        projected.extend(
            project_record(
                entity,
                record_id,
                values,
                as_of_time=as_of,
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
    unknowns = source_unknowns(
        sum(entity == "fact_work_order" for entity, _ in observed),
        sum(entity == "fact_material_requirement" for entity, _ in observed),
        required_materials,
        inventory_materials,
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
    if kind == "capacity_neutral":
        order_id = select_neutral_order(baseline, scenario.dataset)
        family = None
    elif kind == "capacity_arrival":
        selected = select_created_affected_order(
            baseline, scenario.dataset, scenario.ground_truth
        )
        assert selected is not None
        order_id = selected
        family = None
    else:
        selected = select_existing_affected_order(
            baseline, scenario.dataset, scenario.ground_truth
        )
        assert selected is not None
        order_id = selected
        family = {
            "supplier": InterventionFamily.SUPPLIER_INTERVENTION,
            "quality": InterventionFamily.QUALITY_INTERVENTION,
            "capacity_combined": InterventionFamily.CAPACITY_INTERVENTION,
            "capacity_queue": InterventionFamily.CAPACITY_INTERVENTION,
        }[kind]
    as_of = datetime.combine(baseline.dataset_version.period_end, time.max, BUSINESS_TIMEZONE)
    scenario_packet = _packet(scenario.dataset, order_id, family, as_of)
    baseline_packet = (
        None if kind == "capacity_arrival" else _packet(baseline, order_id, None, as_of)
    )
    return ReplayCase(baseline, scenario, scenario_packet, baseline_packet)


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
        assert metrics["evaluation.cause_direction_correct"] is True
        assert metrics["evaluation.candidate_relevance"] is True
        assert metrics["evaluation.false_positive"] is False
    elif mode is TruthEffectMode.EFFECTFUL_NOT_OBSERVABLE:
        assert metrics["evaluation.applicable"] is False
        assert metrics["evaluation.cause_direction_correct"] is None
    else:
        assert metrics["evaluation.neutral_stability"] is True
        assert metrics["evaluation.false_positive"] is False


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
