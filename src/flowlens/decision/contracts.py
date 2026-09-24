"""W03-C01 immutable artifact envelopes and structural invariants only."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from flowlens.decision.enums import (
    EvaluationStatus,
    ExplanationMode,
    FreshnessStatus,
    HumanDecisionType,
    InterventionFamily,
    RecommendationDisposition,
    SignalState,
    SignalType,
    SimulationStatus,
    TrustLevel,
)
from flowlens.decision.primitives import (
    ArtifactProvenance,
    DiagnosisClaim,
    EntityRef,
    ExplanationSection,
    Limitation,
    NamedValue,
    ScalarValue,
    SnapshotEntry,
    Uncertainty,
    Validated,
    validate_artifact_id,
    validate_sha256,
    validate_sorted_unique,
)
from flowlens.decision.serialization import compute_snapshot_hash, derive_artifact_id


def _finish(artifact: Validated, kind: str, identity: dict[str, object]) -> None:
    Validated.__post_init__(artifact)
    schema = getattr(artifact, "schema_version")  # noqa: B009
    if schema != f"{kind}.v1":
        raise ValueError(f"schema_version must be {kind}.v1")
    for name, reference_prefix in _REFERENCE_PREFIXES.items():
        if hasattr(artifact, name):
            reference = getattr(artifact, name)
            if reference is not None:
                validate_artifact_id(reference, reference_prefix, reference)
    for name, reference_prefix in _REFERENCE_TUPLES.items():
        if hasattr(artifact, name):
            for reference in getattr(artifact, name):
                validate_artifact_id(reference, reference_prefix, reference)
    prefix = derive_artifact_id(kind, schema, identity).split("_")[0] + "_"
    validate_artifact_id(
        getattr(artifact, _ID_FIELDS[kind]), prefix, derive_artifact_id(kind, schema, identity)
    )


_ID_FIELDS = {
    "decision-run": "run_id",
    "state-snapshot": "snapshot_id",
    "evidence": "evidence_id",
    "evidence-bundle": "evidence_bundle_id",
    "signal": "signal_id",
    "signal-bundle": "signal_bundle_id",
    "diagnosis-record": "diagnosis_id",
    "intervention-candidate": "candidate_id",
    "candidate-set": "candidate_set_id",
    "simulation-result": "simulation_id",
    "simulation-bundle": "simulation_bundle_id",
    "recommendation-record": "recommendation_id",
    "decision-packet": "packet_id",
    "explanation-record": "explanation_id",
    "human-decision-event": "decision_event_id",
    "recommendation-evaluation": "recommendation_evaluation_id",
    "outcome-evaluation": "outcome_evaluation_id",
}

_REFERENCE_PREFIXES = {
    "run_id": "run_",
    "snapshot_id": "snap_",
    "evidence_id": "ev_",
    "evidence_bundle_id": "evb_",
    "signal_id": "sig_",
    "signal_bundle_id": "sigb_",
    "diagnosis_id": "diag_",
    "candidate_id": "cand_",
    "candidate_set_id": "cset_",
    "simulation_id": "sim_",
    "simulation_bundle_id": "simb_",
    "recommendation_id": "rec_",
    "packet_id": "pkt_",
    "explanation_id": "exp_",
    "decision_event_id": "hdec_",
    "recommendation_evaluation_id": "reval_",
    "outcome_evaluation_id": "oeval_",
    "baseline_snapshot_id": "snap_",
    "selected_candidate_id": "cand_",
    "previous_event_id": "hdec_",
    "human_decision_event_id": "hdec_",
}

_REFERENCE_TUPLES = {
    "evidence_ids": "ev_",
    "supporting_evidence_ids": "ev_",
    "referenced_evidence_ids": "ev_",
    "supporting_signal_ids": "sig_",
    "candidate_order": "cand_",
}


def _fields(artifact: object, *names: str) -> dict[str, object]:
    return {name: getattr(artifact, name) for name in names}


def _sorted_codes(artifact: object, *names: str) -> None:
    for name in names:
        validate_sorted_unique(getattr(artifact, name), lambda item: item, name)


def _limitations(artifact: object) -> None:
    values: tuple[Limitation, ...] = getattr(artifact, "limitations")  # noqa: B009
    validate_sorted_unique(values, lambda item: (item.code, item.message), "limitations")


def _uncertainties(values: tuple[Uncertainty, ...], label: str) -> None:
    validate_sorted_unique(
        values,
        lambda item: (item.status.value, item.code, item.message, item.evidence_ids),
        label,
    )


def _named(values: tuple[NamedValue, ...], label: str) -> None:
    validate_sorted_unique(values, lambda item: item.name, label)


@dataclass(frozen=True, slots=True, kw_only=True)
class DecisionRun(Validated):
    run_id: str
    schema_version: str
    order_id: str
    as_of_time: datetime
    dataset_version: str
    dataset_hash: str
    contract_bundle_version: str
    tool_registry_version: str
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        if self.contract_bundle_version != "w03-c01-v1":
            raise ValueError("contract_bundle_version must be w03-c01-v1")
        validate_sha256(self.dataset_hash, "dataset_hash")
        _finish(
            self,
            "decision-run",
            _fields(
                self,
                "order_id",
                "as_of_time",
                "dataset_version",
                "dataset_hash",
                "contract_bundle_version",
                "tool_registry_version",
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class StateSnapshot(Validated):
    snapshot_id: str
    schema_version: str
    run_id: str
    order_id: str
    as_of_time: datetime
    dataset_version: str
    dataset_hash: str
    snapshot_hash: str
    entries: tuple[SnapshotEntry, ...]
    unknowns: tuple[Uncertainty, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        validate_sha256(self.dataset_hash, "dataset_hash")
        validate_sha256(self.snapshot_hash, "snapshot_hash")
        validate_sorted_unique(self.entries, lambda item: item.entry_key, "entries")
        _uncertainties(self.unknowns, "unknowns")
        for entry in self.entries:
            if (
                entry.available_at > self.as_of_time
                or entry.source_ref.available_at > self.as_of_time
            ):
                raise ValueError("snapshot entry is unavailable at as_of_time")
        semantic = _fields(
            self, "order_id", "as_of_time", "dataset_version", "dataset_hash", "entries", "unknowns"
        )
        if self.snapshot_hash != compute_snapshot_hash(semantic):
            raise ValueError("snapshot_hash does not match semantic observation")
        _finish(self, "state-snapshot", _fields(self, "run_id", "snapshot_hash"))


@dataclass(frozen=True, slots=True, kw_only=True)
class Evidence(Validated):
    evidence_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    source_entity: str
    source_record_id: str
    source_field: str
    value: ScalarValue
    observed_at: datetime | None
    available_at: datetime
    as_of_time: datetime
    relationship_type: str
    trust_level: TrustLevel
    freshness_status: FreshnessStatus
    limitations: tuple[Limitation, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        if self.available_at > self.as_of_time:
            raise ValueError("Evidence available_at exceeds as_of_time")
        _limitations(self)
        _finish(
            self,
            "evidence",
            _fields(
                self,
                "run_id",
                "snapshot_id",
                "source_entity",
                "source_record_id",
                "source_field",
                "value",
                "observed_at",
                "available_at",
                "as_of_time",
                "relationship_type",
                "trust_level",
                "freshness_status",
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceBundle(Validated):
    evidence_bundle_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    snapshot_hash: str
    evidence: tuple[Evidence, ...]
    uncertainties: tuple[Uncertainty, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        validate_sha256(self.snapshot_hash, "snapshot_hash")
        validate_sorted_unique(self.evidence, lambda item: item.evidence_id, "evidence")
        _uncertainties(self.uncertainties, "uncertainties")
        if any(
            item.run_id != self.run_id or item.snapshot_id != self.snapshot_id
            for item in self.evidence
        ):
            raise ValueError("EvidenceBundle member run/snapshot mismatch")
        _finish(
            self,
            "evidence-bundle",
            {
                **_fields(self, "run_id", "snapshot_id", "snapshot_hash"),
                "evidence_ids": tuple(item.evidence_id for item in self.evidence),
                "uncertainties": self.uncertainties,
            },
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class Signal(Validated):
    signal_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    signal_type: SignalType
    state: SignalState
    evidence_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    limitations: tuple[Limitation, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        _sorted_codes(self, "evidence_ids", "reason_codes")
        _limitations(self)
        _finish(
            self,
            "signal",
            _fields(
                self,
                "run_id",
                "snapshot_id",
                "signal_type",
                "state",
                "evidence_ids",
                "reason_codes",
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class SignalBundle(Validated):
    signal_bundle_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    signals: tuple[Signal, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        validate_sorted_unique(self.signals, lambda item: item.signal_type.value, "signals")
        if any(
            item.run_id != self.run_id or item.snapshot_id != self.snapshot_id
            for item in self.signals
        ):
            raise ValueError("SignalBundle member run/snapshot mismatch")
        _finish(
            self,
            "signal-bundle",
            {
                **_fields(self, "run_id", "snapshot_id"),
                "signal_ids": tuple(item.signal_id for item in self.signals),
            },
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class DiagnosisRecord(Validated):
    diagnosis_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    problem_code: str
    claims: tuple[DiagnosisClaim, ...]
    supporting_signal_ids: tuple[str, ...]
    supporting_evidence_ids: tuple[str, ...]
    uncertainties: tuple[Uncertainty, ...]
    affected_path: tuple[EntityRef, ...]
    reason_codes: tuple[str, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        _sorted_codes(self, "supporting_signal_ids", "supporting_evidence_ids", "reason_codes")
        _uncertainties(self.uncertainties, "uncertainties")
        _finish(
            self,
            "diagnosis-record",
            _fields(
                self,
                "run_id",
                "snapshot_id",
                "problem_code",
                "claims",
                "supporting_signal_ids",
                "supporting_evidence_ids",
                "uncertainties",
                "affected_path",
                "reason_codes",
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class InterventionCandidate(Validated):
    candidate_id: str
    schema_version: str
    run_id: str
    family: InterventionFamily
    registry_key: str
    parameters: tuple[NamedValue, ...]
    supporting_evidence_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    limitations: tuple[Limitation, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        _named(self.parameters, "parameters")
        _sorted_codes(self, "supporting_evidence_ids", "reason_codes")
        _limitations(self)
        _finish(
            self,
            "intervention-candidate",
            _fields(
                self,
                "run_id",
                "family",
                "registry_key",
                "parameters",
                "supporting_evidence_ids",
                "reason_codes",
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CandidateSet(Validated):
    candidate_set_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    diagnosis_id: str
    candidates: tuple[InterventionCandidate, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        validate_sorted_unique(self.candidates, lambda item: item.candidate_id, "candidates")
        if any(item.run_id != self.run_id for item in self.candidates):
            raise ValueError("CandidateSet member run mismatch")
        _finish(
            self,
            "candidate-set",
            {
                **_fields(self, "run_id", "snapshot_id", "diagnosis_id"),
                "candidate_ids": tuple(item.candidate_id for item in self.candidates),
            },
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class SimulationResult(Validated):
    simulation_id: str
    schema_version: str
    run_id: str
    candidate_id: str
    status: SimulationStatus
    baseline_snapshot_id: str
    baseline_snapshot_hash: str
    scenario_id: str | None
    scenario_hash: str | None
    affected_entities: tuple[EntityRef, ...]
    measurements: tuple[NamedValue, ...]
    limitations: tuple[Limitation, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        validate_sha256(self.baseline_snapshot_hash, "baseline_snapshot_hash")
        if self.scenario_hash is not None:
            validate_sha256(self.scenario_hash, "scenario_hash")
        validate_sorted_unique(
            self.affected_entities,
            lambda item: (item.entity_type, item.entity_id),
            "affected_entities",
        )
        _named(self.measurements, "measurements")
        _limitations(self)
        _finish(
            self,
            "simulation-result",
            _fields(
                self,
                "run_id",
                "candidate_id",
                "status",
                "baseline_snapshot_id",
                "baseline_snapshot_hash",
                "scenario_id",
                "scenario_hash",
                "affected_entities",
                "measurements",
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class SimulationBundle(Validated):
    simulation_bundle_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    results: tuple[SimulationResult, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        validate_sorted_unique(
            self.results, lambda item: (item.candidate_id, item.simulation_id), "results"
        )
        if any(
            item.run_id != self.run_id or item.baseline_snapshot_id != self.snapshot_id
            for item in self.results
        ):
            raise ValueError("SimulationBundle member run/snapshot mismatch")
        _finish(
            self,
            "simulation-bundle",
            {
                **_fields(self, "run_id", "snapshot_id"),
                "candidate_simulation_ids": tuple(
                    (item.candidate_id, item.simulation_id) for item in self.results
                ),
            },
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class RecommendationRecord(Validated):
    recommendation_id: str
    schema_version: str
    run_id: str
    snapshot_id: str
    diagnosis_id: str
    candidate_set_id: str
    simulation_bundle_id: str
    policy_version: str
    disposition: RecommendationDisposition
    selected_candidate_id: str | None
    candidate_order: tuple[str, ...]
    score_components: tuple[NamedValue, ...]
    reason_codes: tuple[str, ...]
    supporting_evidence_ids: tuple[str, ...]
    uncertainties: tuple[Uncertainty, ...]
    limitations: tuple[Limitation, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        if len(set(self.candidate_order)) != len(self.candidate_order):
            raise ValueError("candidate_order contains duplicates")
        _named(self.score_components, "score_components")
        _sorted_codes(self, "reason_codes", "supporting_evidence_ids")
        _uncertainties(self.uncertainties, "uncertainties")
        _limitations(self)
        _finish(
            self,
            "recommendation-record",
            _fields(
                self,
                "run_id",
                "snapshot_id",
                "diagnosis_id",
                "candidate_set_id",
                "simulation_bundle_id",
                "policy_version",
                "disposition",
                "selected_candidate_id",
                "candidate_order",
                "score_components",
                "reason_codes",
                "supporting_evidence_ids",
                "uncertainties",
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class DecisionPacket(Validated):
    packet_id: str
    schema_version: str
    run: DecisionRun
    snapshot: StateSnapshot
    evidence: EvidenceBundle
    signals: SignalBundle
    diagnosis: DiagnosisRecord
    candidates: CandidateSet
    simulations: SimulationBundle
    recommendation: RecommendationRecord
    uncertainties: tuple[Uncertainty, ...]
    limitations: tuple[Limitation, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        _uncertainties(self.uncertainties, "uncertainties")
        _limitations(self)
        run_id = self.run.run_id
        snapshot_id = self.snapshot.snapshot_id
        if any(
            item.run_id != run_id
            for item in (
                self.snapshot,
                self.evidence,
                self.signals,
                self.diagnosis,
                self.candidates,
                self.simulations,
                self.recommendation,
            )
        ):
            raise ValueError("DecisionPacket nested run mismatch")
        if any(
            item.snapshot_id != snapshot_id
            for item in (
                self.evidence,
                self.signals,
                self.diagnosis,
                self.candidates,
                self.simulations,
                self.recommendation,
            )
        ):
            raise ValueError("DecisionPacket nested snapshot mismatch")
        if (
            self.snapshot.order_id != self.run.order_id
            or self.snapshot.as_of_time != self.run.as_of_time
            or self.snapshot.dataset_version != self.run.dataset_version
            or self.snapshot.dataset_hash != self.run.dataset_hash
            or self.evidence.snapshot_hash != self.snapshot.snapshot_hash
        ):
            raise ValueError("DecisionPacket snapshot binding mismatch")
        if any(
            item.as_of_time != self.snapshot.as_of_time
            or item.available_at > self.snapshot.as_of_time
            for item in self.evidence.evidence
        ):
            raise ValueError("DecisionPacket evidence decision-time mismatch")
        if any(
            item.baseline_snapshot_hash != self.snapshot.snapshot_hash
            for item in self.simulations.results
        ):
            raise ValueError("DecisionPacket simulation snapshot hash mismatch")
        if (
            self.candidates.diagnosis_id != self.diagnosis.diagnosis_id
            or self.recommendation.diagnosis_id != self.diagnosis.diagnosis_id
            or self.recommendation.candidate_set_id != self.candidates.candidate_set_id
            or self.recommendation.simulation_bundle_id != self.simulations.simulation_bundle_id
        ):
            raise ValueError("DecisionPacket nested artifact reference mismatch")
        candidate_ids = {item.candidate_id for item in self.candidates.candidates}
        if (
            self.recommendation.selected_candidate_id is not None
            and self.recommendation.selected_candidate_id not in candidate_ids
        ) or not set(self.recommendation.candidate_order).issubset(candidate_ids):
            raise ValueError("DecisionPacket recommendation candidate reference mismatch")
        if any(item.candidate_id not in candidate_ids for item in self.simulations.results):
            raise ValueError("DecisionPacket simulation candidate reference mismatch")
        evidence_ids = {item.evidence_id for item in self.evidence.evidence}
        signal_ids = {item.signal_id for item in self.signals.signals}
        evidence_refs = (
            *self.diagnosis.supporting_evidence_ids,
            *self.recommendation.supporting_evidence_ids,
            *(ref for item in self.signals.signals for ref in item.evidence_ids),
            *(ref for item in self.candidates.candidates for ref in item.supporting_evidence_ids),
            *(ref for claim in self.diagnosis.claims for ref in claim.evidence_ids),
            *(ref for item in self.uncertainties for ref in item.evidence_ids),
            *(ref for item in self.evidence.uncertainties for ref in item.evidence_ids),
            *(ref for item in self.diagnosis.uncertainties for ref in item.evidence_ids),
            *(ref for item in self.recommendation.uncertainties for ref in item.evidence_ids),
        )
        if not set(evidence_refs).issubset(evidence_ids) or not set(
            self.diagnosis.supporting_signal_ids
        ).issubset(signal_ids):
            raise ValueError("DecisionPacket evidence/signal reference mismatch")
        _finish(
            self,
            "decision-packet",
            {
                "run_id": run_id,
                "snapshot_id": snapshot_id,
                "evidence_bundle_id": self.evidence.evidence_bundle_id,
                "signal_bundle_id": self.signals.signal_bundle_id,
                "diagnosis_id": self.diagnosis.diagnosis_id,
                "candidate_set_id": self.candidates.candidate_set_id,
                "simulation_bundle_id": self.simulations.simulation_bundle_id,
                "recommendation_id": self.recommendation.recommendation_id,
                "uncertainties": self.uncertainties,
                "limitations": self.limitations,
            },
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ExplanationRecord(Validated):
    explanation_id: str
    schema_version: str
    run_id: str
    packet_id: str
    mode: ExplanationMode
    explainer_version: str
    sections: tuple[ExplanationSection, ...]
    referenced_evidence_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    limitations: tuple[Limitation, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        _sorted_codes(self, "referenced_evidence_ids", "reason_codes")
        _limitations(self)
        _finish(
            self,
            "explanation-record",
            _fields(
                self,
                "run_id",
                "packet_id",
                "mode",
                "explainer_version",
                "sections",
                "referenced_evidence_ids",
                "reason_codes",
                "limitations",
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class HumanDecisionEvent(Validated):
    decision_event_id: str
    schema_version: str
    run_id: str
    packet_id: str
    decision: HumanDecisionType
    actor_id: str
    decided_at: datetime
    accepted_reason_codes: tuple[str, ...]
    rejected_reason_codes: tuple[str, ...]
    comment: str | None
    investigation_priority: str | None
    previous_event_id: str | None
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        _sorted_codes(self, "accepted_reason_codes", "rejected_reason_codes")
        if self.previous_event_id is not None:
            validate_artifact_id(self.previous_event_id, "hdec_", self.previous_event_id)
        _finish(
            self,
            "human-decision-event",
            _fields(
                self,
                "run_id",
                "packet_id",
                "decision",
                "actor_id",
                "decided_at",
                "accepted_reason_codes",
                "rejected_reason_codes",
                "comment",
                "investigation_priority",
                "previous_event_id",
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class RecommendationEvaluation(Validated):
    recommendation_evaluation_id: str
    schema_version: str
    run_id: str
    recommendation_id: str
    status: EvaluationStatus
    evaluator_version: str
    metrics: tuple[NamedValue, ...]
    reason_codes: tuple[str, ...]
    limitations: tuple[Limitation, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        _named(self.metrics, "metrics")
        _sorted_codes(self, "reason_codes")
        _limitations(self)
        _finish(
            self,
            "recommendation-evaluation",
            _fields(
                self,
                "run_id",
                "recommendation_id",
                "status",
                "evaluator_version",
                "metrics",
                "reason_codes",
                "limitations",
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class OutcomeEvaluation(Validated):
    outcome_evaluation_id: str
    schema_version: str
    run_id: str
    packet_id: str
    human_decision_event_id: str
    status: EvaluationStatus
    evaluator_version: str
    metrics: tuple[NamedValue, ...]
    reason_codes: tuple[str, ...]
    limitations: tuple[Limitation, ...]
    provenance: ArtifactProvenance

    def __post_init__(self) -> None:
        _named(self.metrics, "metrics")
        _sorted_codes(self, "reason_codes")
        _limitations(self)
        _finish(
            self,
            "outcome-evaluation",
            _fields(
                self,
                "run_id",
                "packet_id",
                "human_decision_event_id",
                "status",
                "evaluator_version",
                "metrics",
                "reason_codes",
                "limitations",
            ),
        )
