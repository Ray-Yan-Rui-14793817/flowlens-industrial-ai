"""Frozen W03-C07 policy vocabulary and directional semantics."""

from __future__ import annotations

import pytest

from flowlens.data.scenarios.config import ScenarioType
from flowlens.decision.enums import InterventionFamily
from flowlens.evaluation import TruthEffectMode, evaluate_recommendation
from flowlens.evaluation.c07_policy import (
    COMMON_REASON_CODES,
    EVALUATOR_VERSION,
    EXPECTED_SIGNALS,
    LIMITATION_MESSAGES,
    METRIC_NAMES,
    METRIC_POLICY_VERSION,
    PRODUCER,
    REPLAY_POLICY_VERSION,
    RESULT_REASON_CODES,
    SCENARIO_FAMILY,
    UNIVERSAL_LIMITATION_CODES,
)
from test_c07_replay import _packet, metric_map, replay_case


def test_versions_modes_and_scenario_family_mapping_are_frozen() -> None:
    assert EVALUATOR_VERSION == "w03-c07-evaluator-v1"
    assert METRIC_POLICY_VERSION == "w03-c07-metrics-v1"
    assert REPLAY_POLICY_VERSION == "w03-c07-replay-v1"
    assert PRODUCER == "flowlens.evaluation.c07_recommendation"
    assert tuple(TruthEffectMode) == (
        TruthEffectMode.NEUTRAL_CONTROL,
        TruthEffectMode.EFFECTFUL_OBSERVABLE,
        TruthEffectMode.EFFECTFUL_NOT_OBSERVABLE,
    )
    assert SCENARIO_FAMILY == {
        ScenarioType.SUPPLIER_DEGRADATION: InterventionFamily.SUPPLIER_INTERVENTION,
        ScenarioType.QUALITY_DETERIORATION: InterventionFamily.QUALITY_INTERVENTION,
        ScenarioType.CAPACITY_SURGE: InterventionFamily.CAPACITY_INTERVENTION,
    }


def test_expected_signals_preserve_c03_observability_boundary() -> None:
    assert tuple(item.value for item in EXPECTED_SIGNALS[ScenarioType.SUPPLIER_DEGRADATION]) == (
        "SUPPLIER_LATE_RECEIPT",
        "MATERIAL_TIMING_RISK",
    )
    assert tuple(item.value for item in EXPECTED_SIGNALS[ScenarioType.QUALITY_DETERIORATION]) == (
        "QUALITY_FAILURE",
        "REWORK_PRESENT",
    )
    assert tuple(item.value for item in EXPECTED_SIGNALS[ScenarioType.CAPACITY_SURGE]) == (
        "QUEUE_DELAY",
    )


def test_metric_reason_and_limitation_vocabularies_are_exact() -> None:
    assert METRIC_NAMES == tuple(sorted(METRIC_NAMES))
    assert len(METRIC_NAMES) == len(set(METRIC_NAMES)) == 17
    assert COMMON_REASON_CODES == (
        "C07_POLICY_V1",
        "C07_PROTECTED_EVALUATION_ONLY",
    )
    assert len(RESULT_REASON_CODES) == 18
    assert UNIVERSAL_LIMITATION_CODES == tuple(sorted(UNIVERSAL_LIMITATION_CODES))
    assert set(LIMITATION_MESSAGES) == {
        *UNIVERSAL_LIMITATION_CODES,
        "C07_CAPACITY_ARRIVAL_ONLY_NOT_IDENTIFIABLE",
    }


@pytest.mark.parametrize("kind", ("supplier", "quality", "capacity_queue"))
def test_observable_replay_has_correct_direction(kind: str) -> None:
    assert metric_map(replay_case(kind))["evaluation.cause_direction_correct"] is True


@pytest.mark.parametrize(
    ("kind", "family"),
    (
        ("supplier", InterventionFamily.SUPPLIER_INTERVENTION),
        ("quality", InterventionFamily.QUALITY_INTERVENTION),
        ("capacity_queue", InterventionFamily.CAPACITY_INTERVENTION),
    ),
)
def test_missing_expected_signal_direction_is_descriptively_false(
    kind: str,
    family: InterventionFamily,
) -> None:
    case = replay_case(kind)
    scenario_packet = _packet(
        case.scenario.dataset,
        case.scenario_packet.run.order_id,
        None,
        case.scenario_packet.run.as_of_time,
    )
    result = evaluate_recommendation(
        scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )
    metrics = {item.name: item.value for item in result.metrics}
    assert metrics["evaluation.cause_direction_correct"] is False
    assert metrics["evaluation.candidate_relevance"] is False
    assert metrics["truth.expected_family"] == family.value


def test_saturated_baseline_direction_is_not_applicable() -> None:
    case = replay_case("supplier")
    active_baseline = _packet(
        case.baseline,
        case.scenario_packet.run.order_id,
        InterventionFamily.SUPPLIER_INTERVENTION,
        case.scenario_packet.run.as_of_time,
    )
    result = evaluate_recommendation(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=active_baseline,
    )
    assert {item.name: item.value for item in result.metrics}[
        "evaluation.cause_direction_correct"
    ] is None
    assert "C07_CAUSE_DIRECTION_NOT_APPLICABLE" in result.reason_codes


def test_capacity_arrival_only_is_not_retroactively_observable() -> None:
    case = replay_case("capacity_arrival")
    result = evaluate_recommendation(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
    )
    metrics = {item.name: item.value for item in result.metrics}
    assert metrics["truth.effect_mode"] == "EFFECTFUL_NOT_OBSERVABLE"
    assert metrics["truth.observable_by_c03"] is False
    assert metrics["evaluation.cause_direction_correct"] is None
    assert metrics["evaluation.candidate_relevance"] is None
    assert metrics["evaluation.recommendation_coverage"] is None
    assert metrics["evaluation.false_positive"] is None
    assert {item.code for item in result.limitations} == {
        *UNIVERSAL_LIMITATION_CODES,
        "C07_CAPACITY_ARRIVAL_ONLY_NOT_IDENTIFIABLE",
    }


def test_completed_results_select_exactly_one_code_per_policy_dimension() -> None:
    for kind in (
        "supplier",
        "quality",
        "capacity_combined",
        "capacity_arrival",
        "capacity_queue",
        "capacity_neutral",
    ):
        case = replay_case(kind)
        result = evaluate_recommendation(
            case.scenario_packet,
            case.scenario,
            baseline_dataset=case.baseline,
            baseline_packet=case.baseline_packet,
        )
        assert len(result.reason_codes) == 8
        assert set(COMMON_REASON_CODES) <= set(result.reason_codes)
        assert set(result.reason_codes) - set(COMMON_REASON_CODES) <= RESULT_REASON_CODES
