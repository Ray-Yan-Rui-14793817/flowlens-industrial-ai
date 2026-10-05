"""Pure categorical counterfactual evaluation for W03-C05."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import cast

from flowlens.decision.c05_policy import (
    DECISION_METRIC_DIRECTIONS,
    MATERIAL_NONCAPACITY_SIGNALS,
    SIMULATION_STATUS_ORDER,
    STRESS_EFFECT_ORDER,
    MetricEffect,
    RelevanceClass,
    StressEffect,
)
from flowlens.decision.c05_validation import validate_c05_inputs
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import (
    CandidateSet,
    DecisionRun,
    DiagnosisRecord,
    EvidenceBundle,
    SignalBundle,
    SimulationBundle,
    StateSnapshot,
)
from flowlens.decision.enums import (
    InterventionFamily,
    RecommendationDisposition,
    SignalState,
    SignalType,
    SimulationStatus,
)
from flowlens.decision.primitives import NamedValue


@dataclass(frozen=True, slots=True)
class CandidateEvaluation:
    candidate_id: str
    family: InterventionFamily
    relevance_class: RelevanceClass
    simulation_status: SimulationStatus
    stress_effect: StressEffect
    decision_eligible: bool
    metric_effects: tuple[tuple[str, MetricEffect], ...]


@dataclass(frozen=True, slots=True)
class C05Evaluation:
    candidates: tuple[CandidateEvaluation, ...]
    candidate_order: tuple[str, ...]
    disposition: RecommendationDisposition
    selected_candidate_id: str | None
    active_family_count: int
    active_succeeded_count: int
    partial_active_comparison: bool
    neutral_no_action_eligible: bool
    top_tie_count: int
    outcome_code: str


def compare_metric(
    name: str,
    baseline: int | Decimal | None,
    stressed: int | Decimal | None,
) -> MetricEffect:
    """Compare one frozen target-order dimension in its declared monotonic direction."""

    direction = DECISION_METRIC_DIRECTIONS.get(name)
    if direction is None:
        raise ValueError("metric is not a C05 decision dimension")
    for value in (baseline, stressed):
        if value is not None and type(value) not in (int, Decimal):
            raise TypeError("decision metric has a noncanonical value")
    if baseline is None and stressed is None:
        return MetricEffect.EQUAL
    if baseline is None or stressed is None:
        return MetricEffect.NOT_COMPARABLE
    if stressed == baseline:
        return MetricEffect.EQUAL
    worse = stressed < baseline if direction == "LOWER" else stressed > baseline
    return MetricEffect.WORSE if worse else MetricEffect.BETTER


def aggregate_stress_effect(effects: tuple[MetricEffect, ...]) -> StressEffect:
    if not effects:
        raise ValueError("at least one frozen decision metric is required")
    comparable = tuple(item for item in effects if item is not MetricEffect.NOT_COMPARABLE)
    if not comparable:
        return StressEffect.NOT_COMPARABLE
    has_worse = MetricEffect.WORSE in comparable
    has_better = MetricEffect.BETTER in comparable
    if has_worse and has_better:
        return StressEffect.MIXED
    if has_worse:
        return StressEffect.WORSENED
    if has_better:
        return StressEffect.IMPROVED
    return StressEffect.UNCHANGED


def _values(measurements: tuple[NamedValue, ...]) -> dict[str, object]:
    return {item.name: item.value for item in measurements}


def _material_uncertainty(signals: SignalBundle) -> bool:
    by_type = {item.signal_type: item for item in signals.signals}
    return any(
        by_type[item].state is SignalState.UNKNOWN
        for item in MATERIAL_NONCAPACITY_SIGNALS
    )


def _semantic_key(item: CandidateEvaluation) -> tuple[int, int, int, str]:
    relevance = {
        RelevanceClass.ACTIVE: 0,
        RelevanceClass.BASELINE: 1,
        RelevanceClass.NOT_ESTABLISHED: 2,
    }[item.relevance_class]
    return (
        relevance,
        SIMULATION_STATUS_ORDER[item.simulation_status],
        STRESS_EFFECT_ORDER[item.stress_effect],
        item.candidate_id,
    )


def evaluate_c05(
    run: DecisionRun,
    snapshot: StateSnapshot,
    bundle: EvidenceBundle,
    context: DecisionContext,
    signals: SignalBundle,
    diagnosis: DiagnosisRecord,
    candidates: CandidateSet,
    simulations: SimulationBundle,
) -> C05Evaluation:
    canonical = validate_c05_inputs(
        run, snapshot, bundle, context, signals, diagnosis, candidates, simulations
    )
    result_by_id = {item.candidate_id: item for item in canonical.simulations.results}
    no_action = next(
        item for item in canonical.candidates.candidates
        if item.family is InterventionFamily.NO_ACTION
    )
    baseline = _values(result_by_id[no_action.candidate_id].measurements)
    provisional: list[CandidateEvaluation] = []
    for candidate in canonical.candidates.candidates:
        result = result_by_id[candidate.candidate_id]
        relevance = (
            RelevanceClass.BASELINE
            if candidate.family is InterventionFamily.NO_ACTION
            else RelevanceClass.ACTIVE
            if "C04_RELEVANT_SIGNAL_ACTIVE" in candidate.reason_codes
            else RelevanceClass.NOT_ESTABLISHED
        )
        metric_effects: tuple[tuple[str, MetricEffect], ...] = ()
        if candidate.family is InterventionFamily.NO_ACTION:
            stress = StressEffect.BASELINE
        elif result.status is not SimulationStatus.SUCCEEDED:
            stress = StressEffect.NOT_COMPARABLE
        else:
            stressed = _values(result.measurements)
            metric_effects = tuple(
                (
                    name,
                    compare_metric(
                        name,
                        cast(int | Decimal | None, baseline[name]),
                        cast(int | Decimal | None, stressed[name]),
                    ),
                )
                for name in sorted(DECISION_METRIC_DIRECTIONS)
            )
            stress = aggregate_stress_effect(tuple(item[1] for item in metric_effects))
        provisional.append(
            CandidateEvaluation(
                candidate.candidate_id,
                candidate.family,
                relevance,
                result.status,
                stress,
                False,
                metric_effects,
            )
        )

    signal_by_type = {item.signal_type: item.state for item in canonical.signals.signals}
    active = tuple(
        item for item in provisional
        if item.relevance_class is RelevanceClass.ACTIVE
    )
    active_succeeded = tuple(
        item for item in active if item.simulation_status is SimulationStatus.SUCCEEDED
    )
    partial = bool(active_succeeded) and len(active_succeeded) != len(active)
    neutral = (
        not active
        and signal_by_type[SignalType.DELIVERY_RISK] is SignalState.INACTIVE
        and all(
            signal_by_type[item] is SignalState.INACTIVE
            for item in MATERIAL_NONCAPACITY_SIGNALS
        )
        and result_by_id[no_action.candidate_id].status is SimulationStatus.SUCCEEDED
        and not _material_uncertainty(canonical.signals)
    )
    evaluated = tuple(
        CandidateEvaluation(
            item.candidate_id,
            item.family,
            item.relevance_class,
            item.simulation_status,
            item.stress_effect,
            (
                neutral
                if item.family is InterventionFamily.NO_ACTION
                else item.relevance_class is RelevanceClass.ACTIVE
                and item.simulation_status is SimulationStatus.SUCCEEDED
                and item.stress_effect not in (StressEffect.MIXED, StressEffect.IMPROVED)
            ),
            item.metric_effects,
        )
        for item in provisional
    )

    selected: str | None = None
    if signal_by_type[SignalType.DELIVERY_RISK] is SignalState.UNKNOWN:
        disposition = RecommendationDisposition.NO_RECOMMENDATION
        outcome = "C05_MATERIAL_UNCERTAINTY_BLOCKS_NO_ACTION"
        tie_count = 0
    elif not active:
        if neutral:
            disposition = RecommendationDisposition.NO_ACTION
            selected = no_action.candidate_id
            outcome = "C05_NEUTRAL_NO_ACTION"
            tie_count = 1
        else:
            disposition = RecommendationDisposition.NO_RECOMMENDATION
            outcome = (
                "C05_DELIVERY_RISK_WITHOUT_ACTIVE_FAMILY"
                if signal_by_type[SignalType.DELIVERY_RISK] is SignalState.ACTIVE
                else "C05_MATERIAL_UNCERTAINTY_BLOCKS_NO_ACTION"
            )
            tie_count = 0
    elif not active_succeeded:
        disposition = RecommendationDisposition.NO_RECOMMENDATION
        outcome = "C05_ACTIVE_SIMULATION_EVIDENCE_UNAVAILABLE"
        tie_count = len(active)
    elif partial:
        disposition = RecommendationDisposition.DEFER_TO_HUMAN
        outcome = "C05_PARTIAL_ACTIVE_COMPARISON"
        tie_count = len(active)
    elif any(
        item.stress_effect in (StressEffect.MIXED, StressEffect.IMPROVED)
        for item in active_succeeded
    ):
        disposition = RecommendationDisposition.DEFER_TO_HUMAN
        outcome = "C05_NONMONOTONIC_STRESS_RESULT"
        tie_count = len(active)
    else:
        worsened = tuple(
            item for item in active_succeeded if item.stress_effect is StressEffect.WORSENED
        )
        if len(worsened) == 1:
            disposition = RecommendationDisposition.INVESTIGATION_ONLY
            selected = worsened[0].candidate_id
            outcome = "C05_UNIQUE_STRESS_SENSITIVE_INVESTIGATION"
            tie_count = 1
        elif len(worsened) > 1:
            disposition = RecommendationDisposition.DEFER_TO_HUMAN
            outcome = "C05_TOP_TIE_DEFERRED"
            tie_count = len(worsened)
        elif len(active) == 1:
            disposition = RecommendationDisposition.INVESTIGATION_ONLY
            selected = active[0].candidate_id
            outcome = "C05_SINGLE_ACTIVE_FAMILY_INVESTIGATION"
            tie_count = 1
        else:
            disposition = RecommendationDisposition.DEFER_TO_HUMAN
            outcome = "C05_TOP_TIE_DEFERRED"
            tie_count = len(active)
    ordered = tuple(sorted(evaluated, key=_semantic_key))
    return C05Evaluation(
        ordered,
        tuple(item.candidate_id for item in ordered),
        disposition,
        selected,
        len(active),
        len(active_succeeded),
        partial,
        neutral,
        tie_count,
        outcome,
    )
