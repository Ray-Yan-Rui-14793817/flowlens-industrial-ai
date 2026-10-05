"""Deterministic HumanDecisionEvent construction for W03-C06."""

from __future__ import annotations

from datetime import datetime

from flowlens.decision.c06_validation import expected_event_provenance, validate_human_inputs
from flowlens.decision.contracts import DecisionPacket, HumanDecisionEvent
from flowlens.decision.enums import HumanDecisionType
from flowlens.decision.serialization import derive_artifact_id


def build_human_decision_event(
    packet: DecisionPacket,
    *,
    decision: HumanDecisionType,
    actor_id: str,
    decided_at: datetime,
    accepted_reason_codes: tuple[str, ...] = (),
    rejected_reason_codes: tuple[str, ...] = (),
    comment: str | None = None,
    investigation_priority: str | None = None,
    previous_event: HumanDecisionEvent | None = None,
) -> HumanDecisionEvent:
    """Build one immutable event; no time, randomness, I/O, or action is inferred."""

    validate_human_inputs(
        packet,
        decision=decision,
        actor_id=actor_id,
        decided_at=decided_at,
        accepted_reason_codes=accepted_reason_codes,
        rejected_reason_codes=rejected_reason_codes,
        comment=comment,
        investigation_priority=investigation_priority,
        previous_event=previous_event,
    )
    previous_event_id = (
        None if previous_event is None else previous_event.decision_event_id
    )
    identity = {
        "run_id": packet.run.run_id,
        "packet_id": packet.packet_id,
        "decision": decision,
        "actor_id": actor_id,
        "decided_at": decided_at,
        "accepted_reason_codes": accepted_reason_codes,
        "rejected_reason_codes": rejected_reason_codes,
        "comment": comment,
        "investigation_priority": investigation_priority,
        "previous_event_id": previous_event_id,
    }
    return HumanDecisionEvent(
        decision_event_id=derive_artifact_id(
            "human-decision-event", "human-decision-event.v1", identity
        ),
        schema_version="human-decision-event.v1",
        run_id=packet.run.run_id,
        packet_id=packet.packet_id,
        decision=decision,
        actor_id=actor_id,
        decided_at=decided_at,
        accepted_reason_codes=accepted_reason_codes,
        rejected_reason_codes=rejected_reason_codes,
        comment=comment,
        investigation_priority=investigation_priority,
        previous_event_id=previous_event_id,
        provenance=expected_event_provenance(packet, previous_event),
    )
