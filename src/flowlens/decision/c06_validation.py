"""Pure frozen packet, Human input, and append-chain validation for W03-C06."""

from __future__ import annotations

from datetime import datetime
from typing import Final

from flowlens.decision.c06_policy import (
    C06_CHAIN_PACKET_MISMATCH,
    C06_CHAIN_RUN_MISMATCH,
    C06_CHAIN_TIME_REGRESSION,
    C06_DECISION_TIME_BEFORE_RUN,
    C06_EVENT_ID_COLLISION,
    C06_HUMAN_INPUT_INVALID,
    C06_NONCANONICAL_C05_PACKET,
    C06_PACKET_BINDING_MISMATCH,
    C06_PREVIOUS_EVENT_MISMATCH,
    C06_REASON_CODE_OVERLAP,
    C06_REASON_CODE_UNKNOWN,
    HUMAN_DECISION_POLICY_VERSION,
    HUMAN_DECISION_PRODUCER,
    C06Error,
)
from flowlens.decision.contracts import DecisionPacket, HumanDecisionEvent
from flowlens.decision.enums import HumanDecisionType, RecommendationDisposition
from flowlens.decision.primitives import (
    ArtifactProvenance,
    SourceRef,
    VersionRef,
    validate_aware_datetime,
    validate_sorted_unique,
)
from flowlens.decision.serialization import canonical_primitive

_C05_PACKET_PRODUCER: Final = "flowlens.decision.c05_packet"
_C05_PACKET_POLICY_VERSION: Final = "w03-c05-packet-v1"
_C05_RECOMMENDATION_PRODUCER: Final = "flowlens.decision.c05_recommendation"
_C05_RECOMMENDATION_POLICY_VERSION: Final = "w03-c05-decision-v1"

_ALLOWED_DISPOSITIONS: Final = (
    RecommendationDisposition.NO_ACTION,
    RecommendationDisposition.NO_RECOMMENDATION,
    RecommendationDisposition.INVESTIGATION_ONLY,
    RecommendationDisposition.DEFER_TO_HUMAN,
)

_C05_PACKET_CONTRACT_VERSIONS: Final = (
    VersionRef(name="w03-c01", version="v1"),
    VersionRef(name="w03-c02", version="v1"),
    VersionRef(name="w03-c03", version="v1"),
    VersionRef(name="w03-c04", version="v1"),
    VersionRef(name="w03-c05-decision", version="v1"),
    VersionRef(name="w03-c05-evaluation", version="v1"),
    VersionRef(name="w03-c05-packet", version="v1"),
)

_C06_CONTRACT_VERSIONS: Final = (
    VersionRef(name="w03-c01", version="v1"),
    VersionRef(name="w03-c05-packet", version="v1"),
    VersionRef(name="w03-c06-human", version="v1"),
    VersionRef(name="w03-c06-workflow", version="v1"),
)


def _source_ref_key(ref: SourceRef) -> tuple[str, str, str, str, str]:
    return (
        ref.source_entity,
        ref.source_record_id,
        ref.source_field,
        str(canonical_primitive(ref.observed_at)) if ref.observed_at else "",
        str(canonical_primitive(ref.available_at)),
    )


def _packet_source_refs(packet: DecisionPacket) -> tuple[SourceRef, ...]:
    return tuple(
        sorted(
            {
                ref
                for evidence in packet.evidence.evidence
                for ref in evidence.provenance.source_refs
            },
            key=_source_ref_key,
        )
    )


def _validate_c01_packet_structure(packet: DecisionPacket) -> None:
    try:
        packet.run.__post_init__()
        packet.snapshot.__post_init__()
        for evidence in packet.evidence.evidence:
            evidence.__post_init__()
        packet.evidence.__post_init__()
        for signal in packet.signals.signals:
            signal.__post_init__()
        packet.signals.__post_init__()
        packet.diagnosis.__post_init__()
        for candidate in packet.candidates.candidates:
            candidate.__post_init__()
        packet.candidates.__post_init__()
        for result in packet.simulations.results:
            result.__post_init__()
        packet.simulations.__post_init__()
        packet.recommendation.__post_init__()
        packet.__post_init__()
    except (AttributeError, TypeError, ValueError) as error:
        raise C06Error(C06_NONCANONICAL_C05_PACKET) from error


def validate_c05_packet(packet: DecisionPacket) -> None:
    """Require the exact canonical frozen C05 packet boundary without rebuilding policy."""

    if not isinstance(packet, DecisionPacket):
        raise C06Error(C06_NONCANONICAL_C05_PACKET)
    _validate_c01_packet_structure(packet)
    expected_input_ids = tuple(
        sorted(
            (
                packet.run.run_id,
                packet.snapshot.snapshot_id,
                packet.evidence.evidence_bundle_id,
                packet.signals.signal_bundle_id,
                packet.diagnosis.diagnosis_id,
                packet.candidates.candidate_set_id,
                packet.simulations.simulation_bundle_id,
                packet.recommendation.recommendation_id,
            )
        )
    )
    provenance = packet.provenance
    recommendation = packet.recommendation
    if (
        packet.schema_version != "decision-packet.v1"
        or provenance.producer != _C05_PACKET_PRODUCER
        or provenance.producer_version != _C05_PACKET_POLICY_VERSION
        or provenance.input_artifact_ids != expected_input_ids
        or provenance.source_refs != _packet_source_refs(packet)
        or provenance.contract_versions != _C05_PACKET_CONTRACT_VERSIONS
        or provenance.implementation_sha is not None
        or recommendation.schema_version != "recommendation-record.v1"
        or recommendation.policy_version != _C05_RECOMMENDATION_POLICY_VERSION
        or recommendation.provenance.producer != _C05_RECOMMENDATION_PRODUCER
        or recommendation.provenance.producer_version != _C05_RECOMMENDATION_POLICY_VERSION
        or recommendation.provenance.implementation_sha is not None
    ):
        raise C06Error(C06_PACKET_BINDING_MISMATCH)
    if recommendation.disposition not in _ALLOWED_DISPOSITIONS:
        raise C06Error(C06_NONCANONICAL_C05_PACKET)


def expected_event_provenance(
    packet: DecisionPacket,
    previous_event: HumanDecisionEvent | None,
) -> ArtifactProvenance:
    input_ids: tuple[str, ...] = (packet.packet_id,)
    if previous_event is not None:
        input_ids = tuple(sorted((packet.packet_id, previous_event.decision_event_id)))
    return ArtifactProvenance(
        producer=HUMAN_DECISION_PRODUCER,
        producer_version=HUMAN_DECISION_POLICY_VERSION,
        input_artifact_ids=input_ids,
        source_refs=(),
        contract_versions=_C06_CONTRACT_VERSIONS,
        implementation_sha=None,
    )


def validate_human_inputs(
    packet: DecisionPacket,
    *,
    decision: HumanDecisionType,
    actor_id: str,
    decided_at: datetime,
    accepted_reason_codes: tuple[str, ...],
    rejected_reason_codes: tuple[str, ...],
    comment: str | None,
    investigation_priority: str | None,
    previous_event: HumanDecisionEvent | None,
) -> None:
    """Validate explicit Human input and prior-chain binding without side effects."""

    validate_c05_packet(packet)
    try:
        if not isinstance(decision, HumanDecisionType):
            raise TypeError("decision must be HumanDecisionType")
        if type(actor_id) is not str or not actor_id or actor_id != actor_id.strip():
            raise ValueError("actor_id must be nonempty and stripped")
        if type(decided_at) is not datetime:
            raise TypeError("decided_at must be datetime")
        validate_aware_datetime(decided_at, "decided_at")
        if type(accepted_reason_codes) is not tuple or type(rejected_reason_codes) is not tuple:
            raise TypeError("reason-code values must be tuples")
        if any(type(item) is not str for item in (*accepted_reason_codes, *rejected_reason_codes)):
            raise TypeError("reason codes must be strings")
        validate_sorted_unique(accepted_reason_codes, lambda item: item, "accepted_reason_codes")
        validate_sorted_unique(rejected_reason_codes, lambda item: item, "rejected_reason_codes")
        text_values = (
            ("comment", comment),
            ("investigation_priority", investigation_priority),
        )
        for label, value in text_values:
            if value is not None and (
                type(value) is not str or not value or value != value.strip()
            ):
                raise ValueError(f"{label} must follow C01 string semantics")
    except (TypeError, ValueError) as error:
        raise C06Error(C06_HUMAN_INPUT_INVALID) from error

    if decided_at < packet.run.as_of_time:
        raise C06Error(C06_DECISION_TIME_BEFORE_RUN)
    available_codes = set(packet.recommendation.reason_codes)
    if not set(accepted_reason_codes).issubset(available_codes) or not set(
        rejected_reason_codes
    ).issubset(available_codes):
        raise C06Error(C06_REASON_CODE_UNKNOWN)
    if set(accepted_reason_codes).intersection(rejected_reason_codes):
        raise C06Error(C06_REASON_CODE_OVERLAP)

    if previous_event is None:
        return
    try:
        previous_event.__post_init__()
    except (AttributeError, TypeError, ValueError) as error:
        raise C06Error(C06_PREVIOUS_EVENT_MISMATCH) from error
    if previous_event.run_id != packet.run.run_id:
        raise C06Error(C06_CHAIN_RUN_MISMATCH)
    if previous_event.packet_id != packet.packet_id:
        raise C06Error(C06_CHAIN_PACKET_MISMATCH)
    previous_input_ids: tuple[str, ...] = (packet.packet_id,)
    if previous_event.previous_event_id is not None:
        previous_input_ids = tuple(
            sorted((packet.packet_id, previous_event.previous_event_id))
        )
    expected_previous_provenance = ArtifactProvenance(
        producer=HUMAN_DECISION_PRODUCER,
        producer_version=HUMAN_DECISION_POLICY_VERSION,
        input_artifact_ids=previous_input_ids,
        source_refs=(),
        contract_versions=_C06_CONTRACT_VERSIONS,
        implementation_sha=None,
    )
    if previous_event.provenance != expected_previous_provenance:
        raise C06Error(C06_EVENT_ID_COLLISION)
    if decided_at < previous_event.decided_at:
        raise C06Error(C06_CHAIN_TIME_REGRESSION)


def validate_human_decision_event(
    packet: DecisionPacket,
    event: HumanDecisionEvent,
    previous_event: HumanDecisionEvent | None,
) -> None:
    """Validate one reconstructed or newly built canonical event against its exact parent."""

    try:
        event.__post_init__()
    except (AttributeError, TypeError, ValueError) as error:
        raise C06Error(C06_HUMAN_INPUT_INVALID) from error
    if event.run_id != packet.run.run_id:
        raise C06Error(C06_CHAIN_RUN_MISMATCH)
    if event.packet_id != packet.packet_id:
        raise C06Error(C06_CHAIN_PACKET_MISMATCH)
    expected_previous_id = (
        None if previous_event is None else previous_event.decision_event_id
    )
    if event.previous_event_id != expected_previous_id:
        raise C06Error(C06_PREVIOUS_EVENT_MISMATCH)
    validate_human_inputs(
        packet,
        decision=event.decision,
        actor_id=event.actor_id,
        decided_at=event.decided_at,
        accepted_reason_codes=event.accepted_reason_codes,
        rejected_reason_codes=event.rejected_reason_codes,
        comment=event.comment,
        investigation_priority=event.investigation_priority,
        previous_event=previous_event,
    )
    if event.provenance != expected_event_provenance(packet, previous_event):
        raise C06Error(C06_EVENT_ID_COLLISION)
