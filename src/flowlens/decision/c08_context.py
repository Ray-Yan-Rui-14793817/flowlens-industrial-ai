"""Pure DecisionPacket-only context projection for W03-C08."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from flowlens.decision.c08_policy import CONTEXT_SCHEMA_VERSION
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.enums import (
    ClaimType,
    FreshnessStatus,
    InterventionFamily,
    RecommendationDisposition,
    SignalState,
    SignalType,
    SimulationStatus,
    TrustLevel,
    UncertaintyStatus,
)
from flowlens.decision.primitives import ScalarValue, Validated
from flowlens.decision.serialization import canonical_json_text


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextRecommendation(Validated):
    disposition: RecommendationDisposition
    selected_candidate_id: str | None
    selected_candidate_family: InterventionFamily | None
    selected_candidate_registry_key: str | None
    candidate_order: tuple[str, ...]
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextClaim(Validated):
    claim_code: str
    claim_type: ClaimType
    statement: str
    evidence_ids: tuple[str, ...]
    limitation_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextDiagnosis(Validated):
    problem_code: str
    claims: tuple[ContextClaim, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextSignal(Validated):
    signal_type: SignalType
    state: SignalState
    evidence_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    limitation_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextMeasurement(Validated):
    name: str
    value: ScalarValue
    unit: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextSimulation(Validated):
    candidate_id: str
    family: InterventionFamily
    status: SimulationStatus
    measurements: tuple[ContextMeasurement, ...]
    limitation_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextEvidence(Validated):
    evidence_id: str
    source_entity: str
    source_record_id: str
    source_field: str
    value: ScalarValue
    observed_at: datetime | None
    available_at: datetime
    relationship_type: str
    trust_level: TrustLevel
    freshness_status: FreshnessStatus
    limitation_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextUncertainty(Validated):
    status: UncertaintyStatus
    code: str
    message: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ContextLimitation(Validated):
    code: str
    message: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ExplanationContextV1(Validated):
    schema_version: str
    run_id: str
    packet_id: str
    order_id: str
    as_of_time: datetime
    recommendation: ContextRecommendation
    diagnosis: ContextDiagnosis
    signals: tuple[ContextSignal, ...]
    simulations: tuple[ContextSimulation, ...]
    evidence: tuple[ContextEvidence, ...]
    uncertainties: tuple[ContextUncertainty, ...]
    limitations: tuple[ContextLimitation, ...]
    allowed_evidence_ids: tuple[str, ...]
    allowed_reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        Validated.__post_init__(self)
        if self.schema_version != CONTEXT_SCHEMA_VERSION:
            raise ValueError(f"schema_version must be {CONTEXT_SCHEMA_VERSION}")


def _relevant_candidate_ids(packet: DecisionPacket) -> set[str]:
    selected = packet.recommendation.selected_candidate_id
    return {
        candidate.candidate_id
        for candidate in packet.candidates.candidates
        if candidate.candidate_id == selected
        or "C04_RELEVANT_SIGNAL_ACTIVE" in candidate.reason_codes
    }


def build_explanation_context(packet: DecisionPacket) -> ExplanationContextV1:
    """Project an immutable packet into the exact deterministic C08 context."""

    relevant_candidate_ids = _relevant_candidate_ids(packet)
    selected = next(
        (
            candidate
            for candidate in packet.candidates.candidates
            if candidate.candidate_id == packet.recommendation.selected_candidate_id
        ),
        None,
    )

    evidence_ids = {
        *packet.recommendation.supporting_evidence_ids,
        *packet.diagnosis.supporting_evidence_ids,
        *(item for claim in packet.diagnosis.claims for item in claim.evidence_ids),
        *(
            item
            for signal in packet.signals.signals
            if signal.state is not SignalState.INACTIVE
            for item in signal.evidence_ids
        ),
        *(
            item
            for candidate in packet.candidates.candidates
            if candidate.candidate_id in relevant_candidate_ids
            for item in candidate.supporting_evidence_ids
        ),
        *(item for uncertainty in packet.uncertainties for item in uncertainty.evidence_ids),
    }
    allowed_evidence_ids = tuple(sorted(evidence_ids))

    reason_codes = {
        *packet.recommendation.reason_codes,
        *packet.diagnosis.reason_codes,
        *(
            item
            for signal in packet.signals.signals
            if signal.state is not SignalState.INACTIVE
            for item in signal.reason_codes
        ),
        *(
            item
            for candidate in packet.candidates.candidates
            if candidate.candidate_id in relevant_candidate_ids
            for item in candidate.reason_codes
        ),
    }
    candidate_by_id = {
        candidate.candidate_id: candidate for candidate in packet.candidates.candidates
    }
    evidence_by_id = {item.evidence_id: item for item in packet.evidence.evidence}

    context = ExplanationContextV1(
        schema_version=CONTEXT_SCHEMA_VERSION,
        run_id=packet.run.run_id,
        packet_id=packet.packet_id,
        order_id=packet.run.order_id,
        as_of_time=packet.run.as_of_time,
        recommendation=ContextRecommendation(
            disposition=packet.recommendation.disposition,
            selected_candidate_id=packet.recommendation.selected_candidate_id,
            selected_candidate_family=selected.family if selected else None,
            selected_candidate_registry_key=selected.registry_key if selected else None,
            candidate_order=packet.recommendation.candidate_order,
            reason_codes=packet.recommendation.reason_codes,
        ),
        diagnosis=ContextDiagnosis(
            problem_code=packet.diagnosis.problem_code,
            claims=tuple(
                ContextClaim(
                    claim_code=claim.claim_code,
                    claim_type=claim.claim_type,
                    statement=claim.statement,
                    evidence_ids=claim.evidence_ids,
                    limitation_codes=tuple(item.code for item in claim.limitations),
                )
                for claim in sorted(
                    packet.diagnosis.claims,
                    key=lambda item: (
                        item.claim_code,
                        item.claim_type.value,
                        item.statement,
                        item.evidence_ids,
                    ),
                )
            ),
        ),
        signals=tuple(
            ContextSignal(
                signal_type=signal.signal_type,
                state=signal.state,
                evidence_ids=signal.evidence_ids,
                reason_codes=signal.reason_codes,
                limitation_codes=tuple(item.code for item in signal.limitations),
            )
            for signal in sorted(packet.signals.signals, key=lambda item: item.signal_type.value)
        ),
        simulations=tuple(
            ContextSimulation(
                candidate_id=result.candidate_id,
                family=candidate_by_id[result.candidate_id].family,
                status=result.status,
                measurements=tuple(
                    ContextMeasurement(name=item.name, value=item.value, unit=item.unit)
                    for item in result.measurements
                ),
                limitation_codes=tuple(item.code for item in result.limitations),
            )
            for result in sorted(
                packet.simulations.results,
                key=lambda item: (item.candidate_id, item.simulation_id),
            )
        ),
        evidence=tuple(
            ContextEvidence(
                evidence_id=item.evidence_id,
                source_entity=item.source_entity,
                source_record_id=item.source_record_id,
                source_field=item.source_field,
                value=item.value,
                observed_at=item.observed_at,
                available_at=item.available_at,
                relationship_type=item.relationship_type,
                trust_level=item.trust_level,
                freshness_status=item.freshness_status,
                limitation_codes=tuple(limitation.code for limitation in item.limitations),
            )
            for item in (evidence_by_id[evidence_id] for evidence_id in allowed_evidence_ids)
        ),
        uncertainties=tuple(
            ContextUncertainty(
                status=item.status,
                code=item.code,
                message=item.message,
                evidence_ids=item.evidence_ids,
            )
            for item in sorted(
                packet.uncertainties,
                key=lambda item: (item.status.value, item.code, item.message, item.evidence_ids),
            )
        ),
        limitations=tuple(
            ContextLimitation(code=item.code, message=item.message)
            for item in sorted(packet.limitations, key=lambda item: (item.code, item.message))
        ),
        allowed_evidence_ids=allowed_evidence_ids,
        allowed_reason_codes=tuple(sorted(reason_codes)),
    )
    # Materialize canonical JSON here so unsupported context values fail before
    # any provider can observe them.
    canonical_json_text(context)
    return context
