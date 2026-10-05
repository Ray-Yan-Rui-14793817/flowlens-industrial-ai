"""RecommendationEvaluation construction and protected output tests for C07."""

from __future__ import annotations

import pytest

from flowlens.decision.contracts import RecommendationEvaluation
from flowlens.decision.enums import EvaluationStatus, InterventionFamily
from flowlens.decision.primitives import Limitation, NamedValue
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.evaluation import C07EvaluationError, evaluate_recommendation
from flowlens.evaluation.c07_policy import (
    EVALUATOR_VERSION,
    LIMITATION_MESSAGES,
    METRIC_NAMES,
    METRIC_TYPES,
    PRODUCER,
    UNIVERSAL_LIMITATION_CODES,
)
from flowlens.evaluation.c07_recommendation import _validate_output_envelope
from flowlens.evaluation.c07_validation import validate_evaluation_inputs
from test_c07_replay import adversarial_packet_fixture, replay_case


def _evaluate(kind: str = "supplier") -> RecommendationEvaluation:
    case = replay_case(kind)
    return evaluate_recommendation(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )


def test_recommendation_evaluation_uses_unchanged_c01_schema_and_identity() -> None:
    case = replay_case("supplier")
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
    assert first.schema_version == "recommendation-evaluation.v1"
    assert first.status is EvaluationStatus.COMPLETED
    assert first.evaluator_version == EVALUATOR_VERSION
    assert first.run_id == case.scenario_packet.run.run_id
    assert first.recommendation_id == case.scenario_packet.recommendation.recommendation_id
    assert first.recommendation_evaluation_id.startswith("reval_")
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    first.__post_init__()


def test_metric_envelope_is_exact_sorted_typed_and_float_free() -> None:
    result = _evaluate()
    metrics = result.metrics
    assert tuple(item.name for item in metrics) == METRIC_NAMES
    assert len(metrics) == len({item.name for item in metrics}) == 17
    for item in metrics:
        assert item.unit is None
        assert type(item.value) in METRIC_TYPES[item.name]
        assert type(item.value) is not float


def test_provenance_contains_only_evaluated_c01_ids_and_frozen_contracts() -> None:
    case = replay_case("quality")
    result = evaluate_recommendation(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )
    assert case.baseline_packet is not None
    assert result.provenance.producer == PRODUCER
    assert result.provenance.producer_version == EVALUATOR_VERSION
    assert result.provenance.input_artifact_ids == tuple(
        sorted(
            (
                case.baseline_packet.packet_id,
                case.baseline_packet.recommendation.recommendation_id,
                case.scenario_packet.packet_id,
                case.scenario_packet.recommendation.recommendation_id,
            )
        )
    )
    assert result.provenance.source_refs == ()
    assert result.provenance.implementation_sha is None
    assert {(item.name, item.version) for item in result.provenance.contract_versions} == {
        ("w02-hgt", case.scenario.ground_truth.schema_version),
        ("w03-c01", "v1"),
        ("w03-c05-packet", "v1"),
        ("w03-c07-evaluation", "v1"),
        ("w03-c07-metrics", "v1"),
    }


def test_observable_metrics_are_descriptive_and_expected_family_bounded() -> None:
    result = _evaluate("supplier")
    metrics = {item.name: item.value for item in result.metrics}
    assert metrics["evaluation.candidate_relevance"] in (True, False, None)
    assert metrics["evaluation.recommendation_coverage"] in (True, False, None)
    assert metrics["evaluation.false_positive"] in (True, False, None)
    assert metrics["truth.expected_family"] == "SUPPLIER_INTERVENTION"
    assert metrics["truth.order_affected"] is True


def test_new_non_expected_active_family_is_a_false_positive() -> None:
    case = replay_case("supplier")
    attacked = adversarial_packet_fixture(
        case.scenario.dataset,
        case.scenario_packet.run.order_id,
        InterventionFamily.QUALITY_INTERVENTION,
        case.scenario_packet.run.as_of_time,
    )
    result = evaluate_recommendation(
        attacked,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=adversarial_packet_fixture(
            case.baseline,
            case.scenario_packet.run.order_id,
            None,
            case.scenario_packet.run.as_of_time,
        ),
    )
    metrics = {item.name: item.value for item in result.metrics}
    assert metrics["evaluation.candidate_relevance"] is False
    assert metrics["evaluation.false_positive"] is True
    assert "C07_FALSE_POSITIVE_PRESENT" in result.reason_codes


def test_neutral_new_family_causes_false_escalation_and_semantic_drift() -> None:
    case = replay_case("capacity_neutral")
    attacked = adversarial_packet_fixture(
        case.scenario.dataset,
        case.scenario_packet.run.order_id,
        InterventionFamily.SUPPLIER_INTERVENTION,
        case.scenario_packet.run.as_of_time,
    )
    result = evaluate_recommendation(
        attacked,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=adversarial_packet_fixture(
            case.baseline,
            case.scenario_packet.run.order_id,
            None,
            case.scenario_packet.run.as_of_time,
        ),
    )
    metrics = {item.name: item.value for item in result.metrics}
    assert metrics["evaluation.false_positive"] is True
    assert metrics["evaluation.neutral_stability"] is False
    assert "C07_NEUTRAL_UNSTABLE" in result.reason_codes


def test_universal_limitations_are_exact_and_protected_only() -> None:
    result = _evaluate("quality")
    assert tuple(item.code for item in result.limitations) == UNIVERSAL_LIMITATION_CODES
    assert all(
        item.message == LIMITATION_MESSAGES[item.code]
        for item in result.limitations
    )


def test_output_envelope_rejects_metric_reason_and_limitation_drift() -> None:
    case = replay_case("supplier")
    result = evaluate_recommendation(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )
    inputs = validate_evaluation_inputs(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )
    with pytest.raises(C07EvaluationError, match="C07_METRIC_ENVELOPE_MISMATCH"):
        _validate_output_envelope(
            result.metrics[:-1], result.reason_codes, result.limitations, inputs
        )
    wrong_type = tuple(
        NamedValue(name=item.name, value=1, unit=None)
        if item.name == "evaluation.applicable"
        else item
        for item in result.metrics
    )
    with pytest.raises(C07EvaluationError, match="C07_METRIC_TYPE_MISMATCH"):
        _validate_output_envelope(
            wrong_type, result.reason_codes, result.limitations, inputs
        )
    with pytest.raises(C07EvaluationError, match="C07_REASON_CODE_VOCABULARY_MISMATCH"):
        _validate_output_envelope(
            result.metrics,
            (*result.reason_codes[:-1], "C07_DRIFT"),
            result.limitations,
            inputs,
        )
    removed = result.limitations[1:]
    with pytest.raises(C07EvaluationError, match="C07_LIMITATION_VOCABULARY_MISMATCH"):
        _validate_output_envelope(result.metrics, result.reason_codes, removed, inputs)
    with pytest.raises(TypeError, match="wrong type"):
        NamedValue(name="evaluation.applicable", value=0.5, unit=None)  # type: ignore[arg-type]


def test_wrong_limitation_message_is_rejected_even_with_allowed_code() -> None:
    case = replay_case("quality")
    result = evaluate_recommendation(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )
    inputs = validate_evaluation_inputs(
        case.scenario_packet,
        case.scenario,
        baseline_dataset=case.baseline,
        baseline_packet=case.baseline_packet,
    )
    changed = (
        Limitation(code=result.limitations[0].code, message="drift"),
        *result.limitations[1:],
    )
    with pytest.raises(C07EvaluationError, match="C07_LIMITATION_VOCABULARY_MISMATCH"):
        _validate_output_envelope(result.metrics, result.reason_codes, changed, inputs)
