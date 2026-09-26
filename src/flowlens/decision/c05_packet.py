"""Exact immutable DecisionPacket assembly for W03-C05."""

from __future__ import annotations

from flowlens.decision.c03_validation import source_refs_for
from flowlens.decision.c05_policy import PACKET_POLICY_VERSION
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.c05_validation import C05BuildError
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import (
    CandidateSet,
    DecisionPacket,
    DecisionRun,
    DiagnosisRecord,
    EvidenceBundle,
    RecommendationRecord,
    SignalBundle,
    SimulationBundle,
    StateSnapshot,
)
from flowlens.decision.primitives import ArtifactProvenance, Limitation, Uncertainty, VersionRef
from flowlens.decision.serialization import canonical_json_bytes, derive_artifact_id


def _uncertainty_key(item: Uncertainty) -> tuple[object, ...]:
    return (item.status.value, item.code, item.message, item.evidence_ids)


def _limitation_key(item: Limitation) -> tuple[str, str]:
    return (item.code, item.message)


def build_decision_packet(
    run: DecisionRun,
    snapshot: StateSnapshot,
    bundle: EvidenceBundle,
    context: DecisionContext,
    signals: SignalBundle,
    diagnosis: DiagnosisRecord,
    candidates: CandidateSet,
    simulations: SimulationBundle,
    recommendation: RecommendationRecord | None = None,
) -> DecisionPacket:
    """Assemble an exact C01 packet after independently rebuilding the canonical C05 result."""

    expected = build_recommendation(
        run, snapshot, bundle, context, signals, diagnosis, candidates, simulations
    )
    if recommendation is None:
        recommendation = expected
    elif (
        not isinstance(recommendation, RecommendationRecord)
        or canonical_json_bytes(recommendation) != canonical_json_bytes(expected)
    ):
        raise C05BuildError("C05_NONCANONICAL_RECOMMENDATION", "BLOCKED_CONTRACT")
    uncertainties = tuple(
        sorted(
            {*bundle.uncertainties, *diagnosis.uncertainties, *recommendation.uncertainties},
            key=_uncertainty_key,
        )
    )
    limitations = tuple(
        sorted(
            {
                *(item for evidence in bundle.evidence for item in evidence.limitations),
                *(item for signal in signals.signals for item in signal.limitations),
                *(item for claim in diagnosis.claims for item in claim.limitations),
                *(item for candidate in candidates.candidates for item in candidate.limitations),
                *(item for result in simulations.results for item in result.limitations),
                *recommendation.limitations,
            },
            key=_limitation_key,
        )
    )
    identity = {
        "run_id": run.run_id,
        "snapshot_id": snapshot.snapshot_id,
        "evidence_bundle_id": bundle.evidence_bundle_id,
        "signal_bundle_id": signals.signal_bundle_id,
        "diagnosis_id": diagnosis.diagnosis_id,
        "candidate_set_id": candidates.candidate_set_id,
        "simulation_bundle_id": simulations.simulation_bundle_id,
        "recommendation_id": recommendation.recommendation_id,
        "uncertainties": uncertainties,
        "limitations": limitations,
    }
    return DecisionPacket(
        packet_id=derive_artifact_id("decision-packet", "decision-packet.v1", identity),
        schema_version="decision-packet.v1",
        run=run,
        snapshot=snapshot,
        evidence=bundle,
        signals=signals,
        diagnosis=diagnosis,
        candidates=candidates,
        simulations=simulations,
        recommendation=recommendation,
        uncertainties=uncertainties,
        limitations=limitations,
        provenance=ArtifactProvenance(
            producer="flowlens.decision.c05_packet",
            producer_version=PACKET_POLICY_VERSION,
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
                        recommendation.recommendation_id,
                    )
                )
            ),
            source_refs=source_refs_for(bundle.evidence),
            contract_versions=(
                VersionRef(name="w03-c01", version="v1"),
                VersionRef(name="w03-c02", version="v1"),
                VersionRef(name="w03-c03", version="v1"),
                VersionRef(name="w03-c04", version="v1"),
                VersionRef(name="w03-c05-decision", version="v1"),
                VersionRef(name="w03-c05-evaluation", version="v1"),
                VersionRef(name="w03-c05-packet", version="v1"),
            ),
            implementation_sha=None,
        ),
    )
