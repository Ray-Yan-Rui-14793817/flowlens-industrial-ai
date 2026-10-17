"""Pure W04-C02 binding of frozen C05 packets to immutable C01 cases."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256
from typing import Final

from flowlens.decision.c06_validation import validate_c05_packet
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.enums import SignalState
from flowlens.decision.primitives import validate_structural_dataclass
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.investigation.contracts import InvestigationCase

C02_BINDING_POLICY_VERSION: Final = "w04-c02-v1"
C02_SUBJECT_TYPE: Final = "ORDER"
C02_OPENED_BY: Final = "FLOWLENS_W04_C02_BINDER"

C02_INVALID_DECISION_PACKET: Final = "C02_INVALID_DECISION_PACKET"
C02_FUTURE_INFORMATION: Final = "C02_FUTURE_INFORMATION"
C02_CASE_BINDING_MISMATCH: Final = "C02_CASE_BINDING_MISMATCH"


class C02BindingError(ValueError):
    """A stable public binding failure without inherited W03 error text."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _check_time(value: datetime | None, boundary: datetime) -> None:
    if value is not None and value.astimezone(UTC) > boundary:
        raise C02BindingError(C02_FUTURE_INFORMATION)


def _validate_packet(packet: DecisionPacket) -> None:
    if type(packet) is not DecisionPacket:
        raise C02BindingError(C02_INVALID_DECISION_PACKET)
    try:
        validate_c05_packet(packet)
    except Exception:
        # Frozen W03 validation owns structural, identity and C05 policy errors.
        raise C02BindingError(C02_INVALID_DECISION_PACKET) from None

    boundary = packet.run.as_of_time.astimezone(UTC)
    for entry in packet.snapshot.entries:
        _check_time(entry.observed_at, boundary)
        _check_time(entry.available_at, boundary)
        _check_time(entry.source_ref.observed_at, boundary)
        _check_time(entry.source_ref.available_at, boundary)
    for evidence in packet.evidence.evidence:
        _check_time(evidence.observed_at, boundary)
        _check_time(evidence.available_at, boundary)
    for source in packet.provenance.source_refs:
        _check_time(source.observed_at, boundary)
        _check_time(source.available_at, boundary)


def _project(packet: DecisionPacket) -> InvestigationCase:
    digest = sha256(canonical_json_bytes(packet)).hexdigest()
    retained = tuple(
        signal for signal in packet.signals.signals if signal.state != SignalState.INACTIVE
    )
    return InvestigationCase(
        schema_version="investigation-case.v1",
        source_decision_packet_id=packet.packet_id,
        source_decision_packet_hash=digest,
        decision_run_id=packet.run.run_id,
        subject_type=C02_SUBJECT_TYPE,
        subject_id=packet.run.order_id,
        as_of_time=packet.run.as_of_time,
        opened_at=packet.run.as_of_time,
        opened_by=C02_OPENED_BY,
        risk_families=tuple(sorted({signal.signal_type.value for signal in retained})),
        source_signal_ids=tuple(sorted({signal.signal_id for signal in retained})),
        source_diagnosis_id=packet.diagnosis.diagnosis_id,
        source_recommendation_id=packet.recommendation.recommendation_id,
    )


def build_investigation_case(packet: DecisionPacket) -> InvestigationCase:
    """Validate the frozen packet and project a deterministic case without I/O."""
    _validate_packet(packet)
    return _project(packet)


def validate_investigation_case_binding(
    packet: DecisionPacket, case: InvestigationCase,
) -> None:
    """Require the complete original case envelope to match this exact packet."""
    _validate_packet(packet)
    if type(case) is not InvestigationCase:
        raise C02BindingError(C02_CASE_BINDING_MISMATCH)
    try:
        # C01 rejects malformed init fields before traversal/canonicalization.
        revalidated = replace(case)
        # Validate original derived claims, which only the detached copy resets.
        validate_structural_dataclass(case)
        original = canonical_json_bytes(case)
        if original != canonical_json_bytes(revalidated):
            raise C02BindingError(C02_CASE_BINDING_MISMATCH)
    except (AttributeError, TypeError, ValueError):
        raise C02BindingError(C02_CASE_BINDING_MISMATCH) from None
    if original != canonical_json_bytes(_project(packet)):
        raise C02BindingError(C02_CASE_BINDING_MISMATCH)
