"""Protected deterministic RecommendationEvaluation construction for W03-C07."""

from __future__ import annotations

from flowlens.data.generation.generator import GeneratedDataset
from flowlens.data.scenarios.config import ScenarioType
from flowlens.data.scenarios.transformer import ScenarioResult
from flowlens.decision.contracts import DecisionPacket, RecommendationEvaluation
from flowlens.decision.enums import (
    EvaluationStatus,
    InterventionFamily,
    RecommendationDisposition,
    SignalState,
    SignalType,
)
from flowlens.decision.primitives import ArtifactProvenance, Limitation, NamedValue, VersionRef
from flowlens.decision.serialization import derive_artifact_id
from flowlens.evaluation.c07_policy import (
    COMMON_REASON_CODES,
    EVALUATOR_VERSION,
    EXPECTED_SIGNALS,
    LIMITATION_MESSAGES,
    METRIC_NAMES,
    METRIC_TYPES,
    PRODUCER,
    RESULT_REASON_CODES,
    UNIVERSAL_LIMITATION_CODES,
    TruthEffectMode,
)
from flowlens.evaluation.c07_validation import (
    C07EvaluationError,
    ValidatedEvaluationInputs,
    validate_evaluation_inputs,
)


def _selected_family(packet: DecisionPacket) -> InterventionFamily | None:
    selected_id = packet.recommendation.selected_candidate_id
    if selected_id is None:
        return None
    return next(
        candidate.family
        for candidate in packet.candidates.candidates
        if candidate.candidate_id == selected_id
    )


def _score_values(packet: DecisionPacket) -> dict[str, object]:
    return {item.name: item.value for item in packet.recommendation.score_components}


def _active_families(packet: DecisionPacket) -> frozenset[InterventionFamily]:
    values = _score_values(packet)
    return frozenset(
        family
        for family in InterventionFamily
        if family is not InterventionFamily.NO_ACTION
        and values[f"evaluation.{family.value}.relevance_class"] == "ACTIVE"
    )


def _candidate_relevance(
    packet: DecisionPacket,
    expected: InterventionFamily,
) -> bool:
    candidate = next(
        (item for item in packet.candidates.candidates if item.family is expected),
        None,
    )
    if candidate is None:
        return False
    return (
        "C04_RELEVANT_SIGNAL_ACTIVE" in candidate.reason_codes
        and expected in _active_families(packet)
    )


def _review_set(packet: DecisionPacket) -> frozenset[InterventionFamily]:
    recommendation = packet.recommendation
    if recommendation.disposition is RecommendationDisposition.INVESTIGATION_ONLY:
        selected = _selected_family(packet)
        return frozenset() if selected is None else frozenset({selected})
    if recommendation.disposition is RecommendationDisposition.DEFER_TO_HUMAN:
        return _active_families(packet)
    if recommendation.disposition is RecommendationDisposition.NO_ACTION:
        return frozenset({InterventionFamily.NO_ACTION})
    return frozenset()


def _signal_states(packet: DecisionPacket) -> dict[SignalType, SignalState]:
    return {signal.signal_type: signal.state for signal in packet.signals.signals}


def _paired_direction(
    baseline: DecisionPacket | None,
    scenario: DecisionPacket,
    expected_signals: tuple[SignalType, ...],
) -> bool | None:
    if baseline is None:
        return None
    baseline_states = _signal_states(baseline)
    scenario_states = _signal_states(scenario)
    pairs = tuple((baseline_states[item], scenario_states[item]) for item in expected_signals)
    if any(
        before is SignalState.ACTIVE
        or before is SignalState.UNKNOWN
        or after is SignalState.UNKNOWN
        for before, after in pairs
    ):
        return None
    if any(
        before is SignalState.INACTIVE and after is SignalState.ACTIVE
        for before, after in pairs
    ):
        return True
    if all(after is SignalState.INACTIVE for _, after in pairs):
        return False
    return None


def _cause_direction(inputs: ValidatedEvaluationInputs) -> bool | None:
    if inputs.effect_mode is not TruthEffectMode.EFFECTFUL_OBSERVABLE:
        return None
    scenario_type = inputs.scenario.ground_truth.scenario_type
    return _paired_direction(
        inputs.baseline_packet,
        inputs.scenario_packet,
        EXPECTED_SIGNALS[scenario_type],
    )


def _semantic_projection(packet: DecisionPacket) -> tuple[object, ...]:
    family_by_id = {
        candidate.candidate_id: candidate.family.value
        for candidate in packet.candidates.candidates
    }
    recommendation = packet.recommendation
    selected = _selected_family(packet)
    return (
        recommendation.disposition.value,
        selected.value if selected is not None else None,
        tuple(family_by_id[item] for item in recommendation.candidate_order),
        tuple((item.name, item.value) for item in recommendation.score_components),
        recommendation.reason_codes,
        tuple(
            (item.status.value, item.code, item.message)
            for item in recommendation.uncertainties
        ),
        tuple((item.code, item.message) for item in recommendation.limitations),
        len(recommendation.supporting_evidence_ids),
    )


def _reason_code(prefix: str, value: bool | None, *, not_applicable: str) -> str:
    if value is None:
        return not_applicable
    return f"{prefix}_{'PRESENT' if value else 'MISSING'}"


def _reason_codes(
    mode: TruthEffectMode,
    cause_direction: bool | None,
    candidate_relevance: bool | None,
    recommendation_coverage: bool | None,
    false_positive: bool | None,
    neutral_stability: bool | None,
) -> tuple[str, ...]:
    values = set(COMMON_REASON_CODES)
    values.add(
        {
            TruthEffectMode.NEUTRAL_CONTROL: "C07_NEUTRAL_CONTROL",
            TruthEffectMode.EFFECTFUL_OBSERVABLE: "C07_EFFECTFUL_OBSERVABLE",
            TruthEffectMode.EFFECTFUL_NOT_OBSERVABLE: "C07_EFFECTFUL_NOT_OBSERVABLE",
        }[mode]
    )
    values.add(
        "C07_CAUSE_DIRECTION_NOT_APPLICABLE"
        if cause_direction is None
        else "C07_CAUSE_DIRECTION_CORRECT"
        if cause_direction
        else "C07_CAUSE_DIRECTION_MISMATCH"
    )
    values.add(
        _reason_code(
            "C07_CANDIDATE_RELEVANCE",
            candidate_relevance,
            not_applicable="C07_CANDIDATE_RELEVANCE_NOT_APPLICABLE",
        )
    )
    values.add(
        _reason_code(
            "C07_RECOMMENDATION_COVERAGE",
            recommendation_coverage,
            not_applicable="C07_RECOMMENDATION_COVERAGE_NOT_APPLICABLE",
        )
    )
    values.add(
        "C07_FALSE_POSITIVE_NOT_APPLICABLE"
        if false_positive is None
        else "C07_FALSE_POSITIVE_PRESENT"
        if false_positive
        else "C07_FALSE_POSITIVE_NONE"
    )
    values.add(
        "C07_NEUTRAL_STABILITY_NOT_APPLICABLE"
        if neutral_stability is None
        else "C07_NEUTRAL_STABLE"
        if neutral_stability
        else "C07_NEUTRAL_UNSTABLE"
    )
    return tuple(sorted(values))


def _limitations(inputs: ValidatedEvaluationInputs) -> tuple[Limitation, ...]:
    codes = set(UNIVERSAL_LIMITATION_CODES)
    if (
        inputs.effect_mode is TruthEffectMode.EFFECTFUL_NOT_OBSERVABLE
        and inputs.scenario.ground_truth.scenario_type is ScenarioType.CAPACITY_SURGE
    ):
        codes.add("C07_CAPACITY_ARRIVAL_ONLY_NOT_IDENTIFIABLE")
    return tuple(
        Limitation(code=code, message=LIMITATION_MESSAGES[code]) for code in sorted(codes)
    )


def _validate_output_envelope(
    metrics: tuple[NamedValue, ...],
    reasons: tuple[str, ...],
    limitations: tuple[Limitation, ...],
    inputs: ValidatedEvaluationInputs,
) -> None:
    if tuple(item.name for item in metrics) != METRIC_NAMES:
        raise C07EvaluationError("C07_METRIC_ENVELOPE_MISMATCH")
    for item in metrics:
        if item.unit is not None or type(item.value) not in METRIC_TYPES[item.name]:
            raise C07EvaluationError("C07_METRIC_TYPE_MISMATCH")
    if (
        len(reasons) != 8
        or not set(COMMON_REASON_CODES) <= set(reasons)
        or not set(reasons) - set(COMMON_REASON_CODES) <= RESULT_REASON_CODES
    ):
        raise C07EvaluationError("C07_REASON_CODE_VOCABULARY_MISMATCH")
    expected_codes = set(UNIVERSAL_LIMITATION_CODES)
    if (
        inputs.effect_mode is TruthEffectMode.EFFECTFUL_NOT_OBSERVABLE
        and inputs.scenario.ground_truth.scenario_type is ScenarioType.CAPACITY_SURGE
    ):
        expected_codes.add("C07_CAPACITY_ARRIVAL_ONLY_NOT_IDENTIFIABLE")
    if {item.code for item in limitations} != expected_codes or any(
        item.message != LIMITATION_MESSAGES.get(item.code) for item in limitations
    ):
        raise C07EvaluationError("C07_LIMITATION_VOCABULARY_MISMATCH")


def evaluate_recommendation(
    scenario_packet: DecisionPacket,
    scenario: ScenarioResult,
    *,
    baseline_dataset: GeneratedDataset,
    baseline_packet: DecisionPacket | None = None,
) -> RecommendationEvaluation:
    """Evaluate one frozen C05 recommendation against protected synthetic truth."""

    inputs = validate_evaluation_inputs(
        scenario_packet,
        scenario,
        baseline_dataset=baseline_dataset,
        baseline_packet=baseline_packet,
    )
    mode = inputs.effect_mode
    expected = inputs.expected_family
    cause_direction = _cause_direction(inputs)
    candidate_relevance = (
        _candidate_relevance(scenario_packet, expected)
        if mode is TruthEffectMode.EFFECTFUL_OBSERVABLE and expected is not None
        else None
    )
    recommendation_coverage = (
        expected in _review_set(scenario_packet)
        if mode is TruthEffectMode.EFFECTFUL_OBSERVABLE and expected is not None
        else None
    )
    baseline_active = (
        frozenset()
        if baseline_packet is None
        else _active_families(baseline_packet)
    )
    scenario_active = _active_families(scenario_packet)
    if mode is TruthEffectMode.EFFECTFUL_OBSERVABLE:
        assert expected is not None
        false_positive: bool | None = any(
            family is not expected for family in scenario_active - baseline_active
        )
    elif mode is TruthEffectMode.NEUTRAL_CONTROL:
        false_positive = bool(scenario_active - baseline_active)
    else:
        false_positive = None
    neutral_stability = (
        _semantic_projection(scenario_packet) == _semantic_projection(baseline_packet)
        if mode is TruthEffectMode.NEUTRAL_CONTROL and baseline_packet is not None
        else None
    )
    selected = _selected_family(scenario_packet)
    ground_truth = scenario.ground_truth
    metric_values: dict[str, bool | str | None] = {
        "evaluation.applicable": mode is not TruthEffectMode.EFFECTFUL_NOT_OBSERVABLE,
        "evaluation.candidate_relevance": candidate_relevance,
        "evaluation.cause_direction_correct": cause_direction,
        "evaluation.false_positive": false_positive,
        "evaluation.neutral_stability": neutral_stability,
        "evaluation.recommendation_coverage": recommendation_coverage,
        "recommendation.disposition": scenario_packet.recommendation.disposition.value,
        "recommendation.selected_family": selected.value if selected is not None else None,
        "truth.effect_mode": mode.value,
        "truth.expected_family": expected.value if expected is not None else None,
        "truth.hgt_hash": ground_truth.hgt_hash,
        "truth.hgt_id": ground_truth.hgt_id,
        "truth.observable_by_c03": inputs.observable_by_c03,
        "truth.order_affected": inputs.order_affected,
        "truth.scenario_dataset_version_id": ground_truth.scenario_dataset_version_id,
        "truth.scenario_id": ground_truth.scenario_id,
        "truth.scenario_type": ground_truth.scenario_type.value,
    }
    metrics = tuple(
        NamedValue(name=name, value=metric_values[name], unit=None) for name in METRIC_NAMES
    )
    reasons = _reason_codes(
        mode,
        cause_direction,
        candidate_relevance,
        recommendation_coverage,
        false_positive,
        neutral_stability,
    )
    limitations = _limitations(inputs)
    _validate_output_envelope(metrics, reasons, limitations, inputs)
    identity = {
        "run_id": scenario_packet.run.run_id,
        "recommendation_id": scenario_packet.recommendation.recommendation_id,
        "status": EvaluationStatus.COMPLETED,
        "evaluator_version": EVALUATOR_VERSION,
        "metrics": metrics,
        "reason_codes": reasons,
        "limitations": limitations,
    }
    input_ids = {
        scenario_packet.packet_id,
        scenario_packet.recommendation.recommendation_id,
    }
    if baseline_packet is not None:
        input_ids.update(
            (
                baseline_packet.packet_id,
                baseline_packet.recommendation.recommendation_id,
            )
        )
    contracts = tuple(
        sorted(
            (
                VersionRef(name="w02-hgt", version=ground_truth.schema_version),
                VersionRef(name="w03-c01", version="v1"),
                VersionRef(name="w03-c05-packet", version="v1"),
                VersionRef(name="w03-c07-evaluation", version="v1"),
                VersionRef(name="w03-c07-metrics", version="v1"),
            ),
            key=lambda item: (item.name, item.version),
        )
    )
    return RecommendationEvaluation(
        recommendation_evaluation_id=derive_artifact_id(
            "recommendation-evaluation", "recommendation-evaluation.v1", identity
        ),
        schema_version="recommendation-evaluation.v1",
        run_id=scenario_packet.run.run_id,
        recommendation_id=scenario_packet.recommendation.recommendation_id,
        status=EvaluationStatus.COMPLETED,
        evaluator_version=EVALUATOR_VERSION,
        metrics=metrics,
        reason_codes=reasons,
        limitations=limitations,
        provenance=ArtifactProvenance(
            producer=PRODUCER,
            producer_version=EVALUATOR_VERSION,
            input_artifact_ids=tuple(sorted(input_ids)),
            source_refs=(),
            contract_versions=contracts,
            implementation_sha=None,
        ),
    )
