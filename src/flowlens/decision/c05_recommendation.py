"""Canonical deterministic RecommendationRecord construction for W03-C05."""

from __future__ import annotations

from flowlens.decision.c03_validation import source_refs_for
from flowlens.decision.c05_evaluation import C05Evaluation, evaluate_c05
from flowlens.decision.c05_policy import (
    COMMON_LIMITATION_CODES,
    COMMON_REASON_CODES,
    DECISION_POLICY_VERSION,
    LIMITATION_MESSAGES,
    RelevanceClass,
)
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import (
    CandidateSet,
    DecisionRun,
    DiagnosisRecord,
    EvidenceBundle,
    RecommendationRecord,
    SignalBundle,
    SimulationBundle,
    StateSnapshot,
)
from flowlens.decision.enums import RecommendationDisposition, UncertaintyStatus
from flowlens.decision.primitives import (
    ArtifactProvenance,
    Limitation,
    NamedValue,
    Uncertainty,
    VersionRef,
)
from flowlens.decision.serialization import derive_artifact_id


def _uncertainty_key(item: Uncertainty) -> tuple[object, ...]:
    return (item.status.value, item.code, item.message, item.evidence_ids)


def _limitation_key(item: Limitation) -> tuple[str, str]:
    return (item.code, item.message)


def _c05_uncertainty(code: str, evidence_ids: tuple[str, ...]) -> Uncertainty:
    from flowlens.decision.c05_policy import UNCERTAINTY_MESSAGES

    status = (
        UncertaintyStatus.INSUFFICIENT_EVIDENCE
        if code == "C05_INSUFFICIENT_RECOMMENDATION_BASIS"
        else UncertaintyStatus.UNRESOLVED_DISPOSITION
    )
    return Uncertainty(
        status=status,
        code=code,
        message=UNCERTAINTY_MESSAGES[code],
        evidence_ids=evidence_ids,
    )


def _score_components(evaluation: C05Evaluation) -> tuple[NamedValue, ...]:
    values: list[NamedValue] = []
    for item in evaluation.candidates:
        prefix = f"evaluation.{item.family.value}"
        values.extend(
            (
                NamedValue(
                    name=f"{prefix}.relevance_class",
                    value=item.relevance_class.value,
                    unit=None,
                ),
                NamedValue(
                    name=f"{prefix}.simulation_status",
                    value=item.simulation_status.value,
                    unit=None,
                ),
                NamedValue(
                    name=f"{prefix}.stress_effect",
                    value=item.stress_effect.value,
                    unit=None,
                ),
                NamedValue(
                    name=f"{prefix}.decision_eligible",
                    value=item.decision_eligible,
                    unit=None,
                ),
            )
        )
    values.extend(
        (
            NamedValue(
                name="policy.active_family_count",
                value=evaluation.active_family_count,
                unit=None,
            ),
            NamedValue(
                name="policy.active_succeeded_count",
                value=evaluation.active_succeeded_count,
                unit=None,
            ),
            NamedValue(
                name="policy.partial_active_comparison",
                value=evaluation.partial_active_comparison,
                unit=None,
            ),
            NamedValue(
                name="policy.neutral_no_action_eligible",
                value=evaluation.neutral_no_action_eligible,
                unit=None,
            ),
            NamedValue(
                name="policy.top_tie_count",
                value=evaluation.top_tie_count,
                unit=None,
            ),
        )
    )
    return tuple(sorted(values, key=lambda item: item.name))


def _supporting_evidence(
    evaluation: C05Evaluation,
    diagnosis: DiagnosisRecord,
    candidates: CandidateSet,
) -> tuple[str, ...]:
    by_id = {item.candidate_id: item for item in candidates.candidates}
    selected: set[str] = set(diagnosis.supporting_evidence_ids)
    if evaluation.disposition is RecommendationDisposition.INVESTIGATION_ONLY:
        assert evaluation.selected_candidate_id is not None
        selected.update(by_id[evaluation.selected_candidate_id].supporting_evidence_ids)
    elif evaluation.disposition in (
        RecommendationDisposition.DEFER_TO_HUMAN,
        RecommendationDisposition.NO_RECOMMENDATION,
    ):
        active_ids = {
            item.candidate_id
            for item in evaluation.candidates
            if item.relevance_class is RelevanceClass.ACTIVE
        }
        for candidate_id in active_ids:
            selected.update(by_id[candidate_id].supporting_evidence_ids)
    return tuple(sorted(selected))


def _reason_codes(evaluation: C05Evaluation) -> tuple[str, ...]:
    reasons = set(COMMON_REASON_CODES)
    outcome = evaluation.outcome_code
    if evaluation.disposition is RecommendationDisposition.INVESTIGATION_ONLY:
        reasons.update(("C05_SELECTED_FROM_ACTIVE_RELEVANCE", outcome))
        if outcome == "C05_SINGLE_ACTIVE_FAMILY_INVESTIGATION":
            reasons.add("C05_SIMULATION_NOT_DECISION_DISCRIMINATING")
    elif evaluation.disposition is RecommendationDisposition.NO_ACTION:
        reasons.update(("C05_NEUTRAL_NO_ACTION", "C05_NO_ACTIVE_INTERVENTION_RELEVANCE"))
    elif evaluation.disposition is RecommendationDisposition.DEFER_TO_HUMAN:
        reasons.add(outcome)
        if outcome == "C05_TOP_TIE_DEFERRED" and not any(
            item.stress_effect.value == "WORSENED" for item in evaluation.candidates
        ):
            reasons.add("C05_SIMULATION_NOT_DECISION_DISCRIMINATING")
    else:
        reasons.update(("C05_INSUFFICIENT_RECOMMENDATION_BASIS", outcome))
    return tuple(sorted(reasons))


def _uncertainties(
    evaluation: C05Evaluation,
    bundle: EvidenceBundle,
    diagnosis: DiagnosisRecord,
    supporting: tuple[str, ...],
) -> tuple[Uncertainty, ...]:
    result = {*bundle.uncertainties, *diagnosis.uncertainties}
    if evaluation.disposition is RecommendationDisposition.NO_RECOMMENDATION:
        result.add(_c05_uncertainty("C05_INSUFFICIENT_RECOMMENDATION_BASIS", supporting))
    if evaluation.outcome_code == "C05_TOP_TIE_DEFERRED":
        result.add(_c05_uncertainty("C05_TOP_TIE", supporting))
    if evaluation.outcome_code == "C05_PARTIAL_ACTIVE_COMPARISON":
        result.add(_c05_uncertainty("C05_PARTIAL_ACTIVE_COMPARISON", supporting))
    return tuple(sorted(result, key=_uncertainty_key))


def _limitations(
    evaluation: C05Evaluation,
    signals: SignalBundle,
    diagnosis: DiagnosisRecord,
    candidates: CandidateSet,
    simulations: SimulationBundle,
) -> tuple[Limitation, ...]:
    by_candidate = {item.candidate_id: item for item in candidates.candidates}
    by_result = {item.candidate_id: item for item in simulations.results}
    relevant_ids: set[str] = set()
    if evaluation.selected_candidate_id is not None:
        relevant_ids.add(evaluation.selected_candidate_id)
    if evaluation.disposition in (
        RecommendationDisposition.DEFER_TO_HUMAN,
        RecommendationDisposition.NO_RECOMMENDATION,
    ):
        relevant_ids.update(
            item.candidate_id
            for item in evaluation.candidates
            if item.relevance_class is RelevanceClass.ACTIVE
        )
    result = {
        *(
            Limitation(code=code, message=LIMITATION_MESSAGES[code])
            for code in COMMON_LIMITATION_CODES
        ),
        *(limitation for signal in signals.signals for limitation in signal.limitations),
        *(limitation for claim in diagnosis.claims for limitation in claim.limitations),
        *(
            limitation
            for candidate_id in relevant_ids
            for limitation in by_candidate[candidate_id].limitations
        ),
        *(
            limitation
            for candidate_id in relevant_ids
            for limitation in by_result[candidate_id].limitations
        ),
    }
    if relevant_ids:
        for code in (
            "C05_SCENARIO_SCOPE_NOT_ORDER_TARGETED",
            "C05_STRESS_PROBE_NOT_INTERVENTION_EFFICACY",
        ):
            result.add(Limitation(code=code, message=LIMITATION_MESSAGES[code]))
    conditional: tuple[str, ...] = ()
    if evaluation.disposition is RecommendationDisposition.INVESTIGATION_ONLY:
        conditional += ("C05_INVESTIGATION_NOT_EXECUTION",)
    if evaluation.disposition is RecommendationDisposition.NO_ACTION:
        conditional += ("C05_NO_ACTION_NOT_OPERATIONAL_EXECUTION",)
    if evaluation.outcome_code == "C05_TOP_TIE_DEFERRED":
        conditional += ("C05_TIE_NOT_AUTO_RESOLVED",)
    if evaluation.outcome_code == "C05_PARTIAL_ACTIVE_COMPARISON":
        conditional += ("C05_PARTIAL_COMPARISON",)
    if evaluation.outcome_code == "C05_NONMONOTONIC_STRESS_RESULT":
        conditional += ("C05_NONMONOTONIC_STRESS_RESULT",)
    if "C05_SIMULATION_NOT_DECISION_DISCRIMINATING" in _reason_codes(evaluation):
        conditional += ("C05_SIMULATION_NOT_DECISION_DISCRIMINATING",)
    result.update(Limitation(code=code, message=LIMITATION_MESSAGES[code]) for code in conditional)
    return tuple(sorted(result, key=_limitation_key))


def build_recommendation(
    run: DecisionRun,
    snapshot: StateSnapshot,
    bundle: EvidenceBundle,
    context: DecisionContext,
    signals: SignalBundle,
    diagnosis: DiagnosisRecord,
    candidates: CandidateSet,
    simulations: SimulationBundle,
) -> RecommendationRecord:
    """Build the only canonical C05 recommendation for the supplied frozen artifacts."""

    evaluation = evaluate_c05(
        run, snapshot, bundle, context, signals, diagnosis, candidates, simulations
    )
    supporting = _supporting_evidence(evaluation, diagnosis, candidates)
    uncertainties = _uncertainties(evaluation, bundle, diagnosis, supporting)
    score_components = _score_components(evaluation)
    reasons = _reason_codes(evaluation)
    identity = {
        "run_id": run.run_id,
        "snapshot_id": snapshot.snapshot_id,
        "diagnosis_id": diagnosis.diagnosis_id,
        "candidate_set_id": candidates.candidate_set_id,
        "simulation_bundle_id": simulations.simulation_bundle_id,
        "policy_version": DECISION_POLICY_VERSION,
        "disposition": evaluation.disposition,
        "selected_candidate_id": evaluation.selected_candidate_id,
        "candidate_order": evaluation.candidate_order,
        "score_components": score_components,
        "reason_codes": reasons,
        "supporting_evidence_ids": supporting,
        "uncertainties": uncertainties,
    }
    evidence_by_id = {item.evidence_id: item for item in bundle.evidence}
    return RecommendationRecord(
        recommendation_id=derive_artifact_id(
            "recommendation-record", "recommendation-record.v1", identity
        ),
        schema_version="recommendation-record.v1",
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        diagnosis_id=diagnosis.diagnosis_id,
        candidate_set_id=candidates.candidate_set_id,
        simulation_bundle_id=simulations.simulation_bundle_id,
        policy_version=DECISION_POLICY_VERSION,
        disposition=evaluation.disposition,
        selected_candidate_id=evaluation.selected_candidate_id,
        candidate_order=evaluation.candidate_order,
        score_components=score_components,
        reason_codes=reasons,
        supporting_evidence_ids=supporting,
        uncertainties=uncertainties,
        limitations=_limitations(evaluation, signals, diagnosis, candidates, simulations),
        provenance=ArtifactProvenance(
            producer="flowlens.decision.c05_recommendation",
            producer_version=DECISION_POLICY_VERSION,
            input_artifact_ids=tuple(
                sorted(
                    (
                        run.run_id,
                        snapshot.snapshot_id,
                        bundle.evidence_bundle_id,
                        signals.signal_bundle_id,
                        diagnosis.diagnosis_id,
                        candidates.candidate_set_id,
                        simulations.simulation_bundle_id,
                    )
                )
            ),
            source_refs=source_refs_for(tuple(evidence_by_id[item] for item in supporting)),
            contract_versions=(
                VersionRef(name="w03-c01", version="v1"),
                VersionRef(name="w03-c02", version="v1"),
                VersionRef(name="w03-c03", version="v1"),
                VersionRef(name="w03-c04", version="v1"),
                VersionRef(name="w03-c05-decision", version="v1"),
                VersionRef(name="w03-c05-evaluation", version="v1"),
            ),
            implementation_sha=None,
        ),
    )
