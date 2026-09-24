"""Focused structural and safety gates for the W03-C01 immutable schemas."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from flowlens.decision import (
    ArtifactProvenance,
    CandidateSet,
    ClaimType,
    DecisionPacket,
    DecisionRun,
    DecisionRunState,
    DiagnosisClaim,
    DiagnosisRecord,
    EntityRef,
    EvaluationState,
    EvaluationStatus,
    Evidence,
    EvidenceBundle,
    ExplanationMode,
    ExplanationRecord,
    ExplanationSection,
    FreshnessStatus,
    HumanDecisionEvent,
    HumanDecisionType,
    InterventionCandidate,
    InterventionFamily,
    Limitation,
    NamedValue,
    OutcomeEvaluation,
    RecommendationDisposition,
    RecommendationEvaluation,
    RecommendationRecord,
    Signal,
    SignalBundle,
    SignalState,
    SignalType,
    SimulationBundle,
    SimulationResult,
    SimulationStatus,
    SnapshotEntry,
    SourceRef,
    StateSnapshot,
    TrustLevel,
    Uncertainty,
    UncertaintyStatus,
    VersionRef,
    compute_snapshot_hash,
    derive_artifact_id,
)

_TIME = datetime(2026, 9, 24, 8, tzinfo=UTC)
_HASH = "a" * 64


def _make[T](
    cls: type[T], kind: str, id_field: str, identity: dict[str, object], **values: Any
) -> T:
    return cls(  # type: ignore[call-arg]
        **{id_field: derive_artifact_id(kind, f"{kind}.v1", identity)},
        schema_version=f"{kind}.v1",
        **values,
    )


def sample_artifacts() -> tuple[
    DecisionPacket,
    ExplanationRecord,
    HumanDecisionEvent,
    RecommendationEvaluation,
    OutcomeEvaluation,
]:
    provenance = ArtifactProvenance(
        producer="test",
        producer_version="1",
        input_artifact_ids=(),
        source_refs=(),
        contract_versions=(VersionRef(name="w03-c01", version="v1"),),
        implementation_sha=None,
    )
    run_fields: dict[str, Any] = dict(
        order_id="SO-1",
        as_of_time=_TIME,
        dataset_version="dataset-1",
        dataset_hash=_HASH,
        contract_bundle_version="w03-c01-v1",
        tool_registry_version="g0-policy",
    )
    run = _make(
        DecisionRun,
        "decision-run",
        "run_id",
        run_fields,
        **run_fields,
        provenance=provenance,
    )
    source = SourceRef(
        source_entity="SalesOrder",
        source_record_id="SO-1",
        source_field="promised_at",
        observed_at=_TIME - timedelta(days=1),
        available_at=_TIME,
    )
    entry = SnapshotEntry(
        entry_key="SO-1:promised_at",
        entity=EntityRef(entity_type="SalesOrder", entity_id="SO-1"),
        field="promised_at",
        value=_TIME,
        observed_at=source.observed_at,
        available_at=source.available_at,
        source_ref=source,
    )
    unknown = Uncertainty(
        status=UncertaintyStatus.UNKNOWN,
        code="QUALITY_FINALITY",
        message="Formal release is unknown",
        evidence_ids=(),
    )
    snapshot_semantic = dict(
        order_id=run.order_id,
        as_of_time=run.as_of_time,
        dataset_version=run.dataset_version,
        dataset_hash=run.dataset_hash,
        entries=(entry,),
        unknowns=(unknown,),
    )
    snapshot_hash = compute_snapshot_hash(snapshot_semantic)
    snapshot = _make(
        StateSnapshot,
        "state-snapshot",
        "snapshot_id",
        dict(run_id=run.run_id, snapshot_hash=snapshot_hash),
        run_id=run.run_id,
        snapshot_hash=snapshot_hash,
        **snapshot_semantic,
        provenance=provenance,
    )
    evidence_fields: dict[str, Any] = dict(
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        source_entity=source.source_entity,
        source_record_id=source.source_record_id,
        source_field=source.source_field,
        value=_TIME,
        observed_at=source.observed_at,
        available_at=source.available_at,
        as_of_time=_TIME,
        relationship_type="DIRECT",
        trust_level=TrustLevel.DIRECT_FACT,
        freshness_status=FreshnessStatus.FRESH,
    )
    evidence = _make(
        Evidence,
        "evidence",
        "evidence_id",
        evidence_fields,
        **evidence_fields,
        limitations=(),
        provenance=provenance,
    )
    evidence_bundle = _make(
        EvidenceBundle,
        "evidence-bundle",
        "evidence_bundle_id",
        dict(
            run_id=run.run_id,
            snapshot_id=snapshot.snapshot_id,
            snapshot_hash=snapshot_hash,
            evidence_ids=(evidence.evidence_id,),
            uncertainties=(unknown,),
        ),
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        snapshot_hash=snapshot_hash,
        evidence=(evidence,),
        uncertainties=(unknown,),
        provenance=provenance,
    )
    signal_fields: dict[str, Any] = dict(
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        signal_type=SignalType.DELIVERY_RISK,
        state=SignalState.UNKNOWN,
        evidence_ids=(evidence.evidence_id,),
        reason_codes=("EVIDENCE_PRESENT",),
    )
    signal = _make(
        Signal,
        "signal",
        "signal_id",
        signal_fields,
        **signal_fields,
        limitations=(),
        provenance=provenance,
    )
    signals = _make(
        SignalBundle,
        "signal-bundle",
        "signal_bundle_id",
        dict(
            run_id=run.run_id,
            snapshot_id=snapshot.snapshot_id,
            signal_ids=(signal.signal_id,),
        ),
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        signals=(signal,),
        provenance=provenance,
    )
    claim = DiagnosisClaim(
        claim_code="PROMISE_OBSERVED",
        claim_type=ClaimType.FACT_CLAIM,
        statement="Promised time is recorded",
        evidence_ids=(evidence.evidence_id,),
        limitations=(),
    )
    diagnosis_fields: dict[str, Any] = dict(
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        problem_code="DELIVERY_REVIEW",
        claims=(claim,),
        supporting_signal_ids=(signal.signal_id,),
        supporting_evidence_ids=(evidence.evidence_id,),
        uncertainties=(unknown,),
        affected_path=(entry.entity,),
        reason_codes=("EVIDENCE_PRESENT",),
    )
    diagnosis = _make(
        DiagnosisRecord,
        "diagnosis-record",
        "diagnosis_id",
        diagnosis_fields,
        **diagnosis_fields,
        provenance=provenance,
    )
    candidate_fields: dict[str, Any] = dict(
        run_id=run.run_id,
        family=InterventionFamily.NO_ACTION,
        registry_key="no-action",
        parameters=(NamedValue(name="scope", value="current", unit=None),),
        supporting_evidence_ids=(evidence.evidence_id,),
        reason_codes=("EVIDENCE_PRESENT",),
    )
    candidate = _make(
        InterventionCandidate,
        "intervention-candidate",
        "candidate_id",
        candidate_fields,
        **candidate_fields,
        limitations=(),
        provenance=provenance,
    )
    candidates = _make(
        CandidateSet,
        "candidate-set",
        "candidate_set_id",
        dict(
            run_id=run.run_id,
            snapshot_id=snapshot.snapshot_id,
            diagnosis_id=diagnosis.diagnosis_id,
            candidate_ids=(candidate.candidate_id,),
        ),
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        diagnosis_id=diagnosis.diagnosis_id,
        candidates=(candidate,),
        provenance=provenance,
    )
    simulation_fields: dict[str, Any] = dict(
        run_id=run.run_id,
        candidate_id=candidate.candidate_id,
        status=SimulationStatus.UNAVAILABLE,
        baseline_snapshot_id=snapshot.snapshot_id,
        baseline_snapshot_hash=snapshot_hash,
        scenario_id=None,
        scenario_hash=None,
        affected_entities=(entry.entity,),
        measurements=(),
    )
    simulation = _make(
        SimulationResult,
        "simulation-result",
        "simulation_id",
        simulation_fields,
        **simulation_fields,
        limitations=(),
        provenance=provenance,
    )
    simulations = _make(
        SimulationBundle,
        "simulation-bundle",
        "simulation_bundle_id",
        dict(
            run_id=run.run_id,
            snapshot_id=snapshot.snapshot_id,
            candidate_simulation_ids=((candidate.candidate_id, simulation.simulation_id),),
        ),
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        results=(simulation,),
        provenance=provenance,
    )
    recommendation_fields: dict[str, Any] = dict(
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        diagnosis_id=diagnosis.diagnosis_id,
        candidate_set_id=candidates.candidate_set_id,
        simulation_bundle_id=simulations.simulation_bundle_id,
        policy_version="schema-only",
        disposition=RecommendationDisposition.NO_RECOMMENDATION,
        selected_candidate_id=None,
        candidate_order=(candidate.candidate_id,),
        score_components=(),
        reason_codes=("EVIDENCE_PRESENT",),
        supporting_evidence_ids=(evidence.evidence_id,),
        uncertainties=(unknown,),
    )
    recommendation = _make(
        RecommendationRecord,
        "recommendation-record",
        "recommendation_id",
        recommendation_fields,
        **recommendation_fields,
        limitations=(),
        provenance=provenance,
    )
    packet = _make(
        DecisionPacket,
        "decision-packet",
        "packet_id",
        dict(
            run_id=run.run_id,
            snapshot_id=snapshot.snapshot_id,
            evidence_bundle_id=evidence_bundle.evidence_bundle_id,
            signal_bundle_id=signals.signal_bundle_id,
            diagnosis_id=diagnosis.diagnosis_id,
            candidate_set_id=candidates.candidate_set_id,
            simulation_bundle_id=simulations.simulation_bundle_id,
            recommendation_id=recommendation.recommendation_id,
            uncertainties=(unknown,),
            limitations=(),
        ),
        run=run,
        snapshot=snapshot,
        evidence=evidence_bundle,
        signals=signals,
        diagnosis=diagnosis,
        candidates=candidates,
        simulations=simulations,
        recommendation=recommendation,
        uncertainties=(unknown,),
        limitations=(),
        provenance=provenance,
    )
    explanation_fields: dict[str, Any] = dict(
        run_id=run.run_id,
        packet_id=packet.packet_id,
        mode=ExplanationMode.DETERMINISTIC_TEMPLATE,
        explainer_version="schema-only",
        sections=(ExplanationSection(section_key="summary", text="Human review required"),),
        referenced_evidence_ids=(evidence.evidence_id,),
        reason_codes=("EVIDENCE_PRESENT",),
        limitations=(),
    )
    explanation = _make(
        ExplanationRecord,
        "explanation-record",
        "explanation_id",
        explanation_fields,
        **explanation_fields,
        provenance=provenance,
    )
    decision_fields: dict[str, Any] = dict(
        run_id=run.run_id,
        packet_id=packet.packet_id,
        decision=HumanDecisionType.DEFER,
        actor_id="human-1",
        decided_at=_TIME,
        accepted_reason_codes=(),
        rejected_reason_codes=(),
        comment=None,
        investigation_priority=None,
        previous_event_id=None,
    )
    human = _make(
        HumanDecisionEvent,
        "human-decision-event",
        "decision_event_id",
        decision_fields,
        **decision_fields,
        provenance=provenance,
    )
    rec_eval_fields: dict[str, Any] = dict(
        run_id=run.run_id,
        recommendation_id=recommendation.recommendation_id,
        status=EvaluationStatus.PENDING,
        evaluator_version="schema-only",
        metrics=(),
        reason_codes=(),
        limitations=(),
    )
    rec_eval = _make(
        RecommendationEvaluation,
        "recommendation-evaluation",
        "recommendation_evaluation_id",
        rec_eval_fields,
        **rec_eval_fields,
        provenance=provenance,
    )
    outcome_fields: dict[str, Any] = dict(
        run_id=run.run_id,
        packet_id=packet.packet_id,
        human_decision_event_id=human.decision_event_id,
        status=EvaluationStatus.PENDING,
        evaluator_version="schema-only",
        metrics=(),
        reason_codes=(),
        limitations=(),
    )
    outcome = _make(
        OutcomeEvaluation,
        "outcome-evaluation",
        "outcome_evaluation_id",
        outcome_fields,
        **outcome_fields,
        provenance=provenance,
    )
    return packet, explanation, human, rec_eval, outcome


def test_every_schema_constructs_and_is_deeply_immutable() -> None:
    packet, explanation, human, rec_eval, outcome = sample_artifacts()
    artifacts = (
        packet.run,
        packet.snapshot,
        packet.evidence.evidence[0],
        packet.evidence,
        packet.signals.signals[0],
        packet.signals,
        packet.diagnosis,
        packet.candidates.candidates[0],
        packet.candidates,
        packet.simulations.results[0],
        packet.simulations,
        packet.recommendation,
        packet,
        explanation,
        human,
        rec_eval,
        outcome,
    )
    assert len(artifacts) == 17
    for artifact in artifacts:
        assert is_dataclass(artifact)
        assert not hasattr(artifact, "__dict__")
        assert all(field.kw_only for field in fields(artifact))
        with pytest.raises(FrozenInstanceError):
            artifact.schema_version = "changed"  # type: ignore[misc]
        for field in fields(artifact):
            assert not isinstance(getattr(artifact, field.name), (list, dict, set))
    assert "human_decision" not in {field.name for field in fields(DecisionPacket)}
    assert not any("evaluation" in field.name for field in fields(DecisionPacket))
    assert human.packet_id == packet.packet_id
    limitation = Limitation(code="BOUNDARY", message="Review required")
    assert limitation.code == "BOUNDARY"
    with pytest.raises(FrozenInstanceError):
        limitation.code = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("enum", "members"),
    [
        (
            UncertaintyStatus,
            "UNKNOWN INSUFFICIENT_EVIDENCE ASSOCIATIVE_ONLY UNRESOLVED_DISPOSITION",
        ),
        (ClaimType, "FACT_CLAIM DERIVED_CLAIM ASSOCIATIVE_CLAIM UNCERTAINTY_STATEMENT"),
        (TrustLevel, "DIRECT_FACT DERIVED_FACT ASSOCIATIVE_EVIDENCE UNKNOWN FORBIDDEN_INFERENCE"),
        (FreshnessStatus, "FRESH STALE EXPIRED UNKNOWN NOT_APPLICABLE"),
        (
            SignalType,
            "SUPPLIER_LATE_RECEIPT MATERIAL_TIMING_RISK QUALITY_FAILURE REWORK_PRESENT "
            "QUALITY_DISPOSITION_UNKNOWN QUEUE_DELAY CAPACITY_PRESSURE DELIVERY_RISK",
        ),
        (SignalState, "ACTIVE INACTIVE UNKNOWN"),
        (
            InterventionFamily,
            "NO_ACTION SUPPLIER_INTERVENTION QUALITY_INTERVENTION CAPACITY_INTERVENTION",
        ),
        (SimulationStatus, "SUCCEEDED UNAVAILABLE FAILED"),
        (
            RecommendationDisposition,
            "CANDIDATE_RECOMMENDED NO_ACTION NO_RECOMMENDATION INVESTIGATION_ONLY DEFER_TO_HUMAN",
        ),
        (ExplanationMode, "DETERMINISTIC_TEMPLATE BOUNDED_LLM DEGRADED_TEMPLATE"),
        (HumanDecisionType, "ACCEPT REJECT DEFER"),
        (EvaluationStatus, "PENDING COMPLETED FAILED"),
        (
            DecisionRunState,
            "CREATED SNAPSHOT_BUILDING SNAPSHOT_READY TRUST_CHECKING TRUST_VERIFIED SIGNALS_READY "
            "DIAGNOSIS_READY CANDIDATES_READY SIMULATION_READY RECOMMENDATION_READY PACKET_READY "
            "EXPLANATION_READY HUMAN_PENDING HUMAN_DECIDED RUNTIME_COMPLETE BLOCKED_CONTEXT "
            "BLOCKED_TEMPORAL BLOCKED_HGT BLOCKED_TRUST BLOCKED_CONTRACT "
            "BLOCKED_INSUFFICIENT_EVIDENCE SIMULATION_PARTIAL SIMULATION_FAILED NO_RECOMMENDATION "
            "EXPLANATION_DEGRADED",
        ),
        (
            EvaluationState,
            "EVAL_NOT_STARTED RECOMMENDATION_EVAL_READY RECOMMENDATION_EVALUATED "
            "OUTCOME_PENDING OUTCOME_AVAILABLE OUTCOME_EVALUATED",
        ),
    ],
)
def test_frozen_enum_exactness(enum: Any, members: str) -> None:
    assert {member.value for member in enum} == set(members.split())


def test_naive_datetimes_and_floats_reject() -> None:
    packet, _, human, _, _ = sample_artifacts()
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(packet.run, as_of_time=_TIME.replace(tzinfo=None))
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(human, decided_at=_TIME.replace(tzinfo=None))
    with pytest.raises(TypeError):
        NamedValue(name="bad", value=1.25, unit=None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        replace(packet.evidence.evidence[0], value=1.25)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        replace(packet.snapshot.entries[0], value=[1])  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        replace(packet.signals.signals[0], state="ACTIVE")  # type: ignore[arg-type]


def test_evidence_future_data_rejects_and_boundary_accepts() -> None:
    packet, _, _, _, _ = sample_artifacts()
    evidence = packet.evidence.evidence[0]
    assert evidence.available_at == evidence.as_of_time
    earlier = evidence.available_at - timedelta(seconds=1)
    identity = dict(
        run_id=evidence.run_id,
        snapshot_id=evidence.snapshot_id,
        source_entity=evidence.source_entity,
        source_record_id=evidence.source_record_id,
        source_field=evidence.source_field,
        value=evidence.value,
        observed_at=evidence.observed_at,
        available_at=earlier,
        as_of_time=evidence.as_of_time,
        relationship_type=evidence.relationship_type,
        trust_level=evidence.trust_level,
        freshness_status=evidence.freshness_status,
    )
    assert (
        replace(
            evidence,
            available_at=earlier,
            evidence_id=derive_artifact_id("evidence", "evidence.v1", identity),
        ).available_at
        == earlier
    )
    later = evidence.as_of_time + timedelta(microseconds=1)
    with pytest.raises(ValueError, match="available_at"):
        replace(evidence, available_at=later)


def test_artifact_id_prefix_and_digest_are_checked() -> None:
    packet, _, _, _, _ = sample_artifacts()
    with pytest.raises(ValueError, match="artifact ID must be"):
        replace(packet.run, run_id="invalid")
    with pytest.raises(ValueError, match="canonical identity"):
        replace(packet.run, run_id="run_" + "b" * 64)


def test_bundle_and_packet_cross_references_reject_mismatch() -> None:
    packet, _, _, _, _ = sample_artifacts()
    original = packet.evidence.evidence[0]
    wrong_run_identity = dict(
        run_id="run_" + "b" * 64,
        snapshot_id=original.snapshot_id,
        source_entity=original.source_entity,
        source_record_id=original.source_record_id,
        source_field=original.source_field,
        value=original.value,
        observed_at=original.observed_at,
        available_at=original.available_at,
        as_of_time=original.as_of_time,
        relationship_type=original.relationship_type,
        trust_level=original.trust_level,
        freshness_status=original.freshness_status,
    )
    wrong_run_evidence = replace(
        original,
        run_id="run_" + "b" * 64,
        evidence_id=derive_artifact_id("evidence", "evidence.v1", wrong_run_identity),
    )
    with pytest.raises(ValueError, match="member run/snapshot"):
        replace(packet.evidence, evidence=(wrong_run_evidence,))
    with pytest.raises(ValueError, match="sorted and unique"):
        replace(packet.evidence, evidence=packet.evidence.evidence * 2)
    wrong_diag = "diag_" + "b" * 64
    candidate_identity = dict(
        run_id=packet.run.run_id,
        snapshot_id=packet.snapshot.snapshot_id,
        diagnosis_id=wrong_diag,
        candidate_ids=(packet.candidates.candidates[0].candidate_id,),
    )
    wrong_candidates = replace(
        packet.candidates,
        diagnosis_id=wrong_diag,
        candidate_set_id=derive_artifact_id(
            "candidate-set", "candidate-set.v1", candidate_identity
        ),
    )
    with pytest.raises(ValueError, match="nested artifact reference"):
        replace(packet, candidates=wrong_candidates)
    wrong_hash = "b" * 64
    bundle_identity = dict(
        run_id=packet.run.run_id,
        snapshot_id=packet.snapshot.snapshot_id,
        snapshot_hash=wrong_hash,
        evidence_ids=(original.evidence_id,),
        uncertainties=packet.evidence.uncertainties,
    )
    wrong_bundle = replace(
        packet.evidence,
        snapshot_hash=wrong_hash,
        evidence_bundle_id=derive_artifact_id(
            "evidence-bundle", "evidence-bundle.v1", bundle_identity
        ),
    )
    with pytest.raises(ValueError, match="snapshot binding"):
        replace(packet, evidence=wrong_bundle)
    later = packet.snapshot.as_of_time + timedelta(microseconds=1)
    later_identity = {**wrong_run_identity, "run_id": packet.run.run_id, "as_of_time": later}
    later_evidence = replace(
        original,
        as_of_time=later,
        evidence_id=derive_artifact_id("evidence", "evidence.v1", later_identity),
    )
    later_bundle_identity = {
        **bundle_identity,
        "snapshot_hash": packet.snapshot.snapshot_hash,
        "evidence_ids": (later_evidence.evidence_id,),
    }
    later_bundle = replace(
        packet.evidence,
        evidence=(later_evidence,),
        evidence_bundle_id=derive_artifact_id(
            "evidence-bundle", "evidence-bundle.v1", later_bundle_identity
        ),
    )
    with pytest.raises(ValueError, match="decision-time"):
        replace(packet, evidence=later_bundle)
    simulation = packet.simulations.results[0]
    with pytest.raises(ValueError, match="sorted and unique"):
        replace(simulation, affected_entities=simulation.affected_entities * 2)


def test_no_runtime_hgt_import_or_operational_side_effect() -> None:
    package = Path(__file__).resolve().parents[1] / "src" / "flowlens" / "decision"
    source = "\n".join(path.read_text(encoding="utf-8") for path in package.glob("*.py"))
    forbidden_imports = (
        "flowlens.db",
        "flowlens.data.scenarios.ground_truth",
        "flowlens.data.scenarios.serialization",
        "sqlalchemy",
        "openai",
    )
    assert not any(
        f"import {name}" in source or f"from {name}" in source for name in forbidden_imports
    )
    runtime = (DecisionRun, StateSnapshot, Evidence, Signal, DiagnosisRecord, DecisionPacket)
    forbidden_fields = ("hgt", "true_root_cause", "scenario_label", "human_decision")
    for cls in runtime:
        assert not any(
            term in field.name.lower() for field in fields(cls) for term in forbidden_fields
        )
    script = (
        "import sys; import flowlens.decision; "
        "assert not any(name.startswith(('flowlens.db', 'flowlens.data.scenarios', "
        "'sqlalchemy', 'openai')) for name in sys.modules)"
    )
    subprocess.run([sys.executable, "-c", script], check=True, capture_output=True)
