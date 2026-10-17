"""Pure deterministic W04-C06 Human review of exact frozen C05 artifacts."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import NoReturn

from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.primitives import (
    validate_aware_datetime,
    validate_sorted_unique,
    validate_structural_dataclass,
)
from flowlens.decision.serialization import canonical_json_bytes, sha256_hex
from flowlens.investigation.c05_findings import validate_findings_conflicts_uncertainty
from flowlens.investigation.c06_policy import (
    C06_CHAIN_CASE_MISMATCH,
    C06_CHAIN_TIME_REGRESSION,
    C06_EVENT_MISMATCH,
    C06_HUMAN_INPUT_INVALID,
    C06_INVALID_REVIEW_CONTEXT,
    C06_OUTCOME_CONTRACT_MISMATCH,
    C06_PREVIOUS_EVENT_MISMATCH,
    C06_REVIEW_REFERENCE_MISMATCH,
    C06HumanInvestigationError,
)
from flowlens.investigation.contracts import (
    ConflictRecord,
    EvidenceQuerySpec,
    EvidenceSlice,
    FindingRecord,
    HumanInvestigationEvent,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
    UncertaintyRegister,
)
from flowlens.investigation.enums import FindingStatus, HumanInvestigationOutcome


def _fail(code: str) -> NoReturn:
    raise C06HumanInvestigationError(code) from None


def _validate_review_context(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
    slices: tuple[EvidenceSlice, ...],
    findings: tuple[FindingRecord, ...],
    conflicts: tuple[ConflictRecord, ...],
    uncertainty_register: UncertaintyRegister,
) -> None:
    """Admit the complete exact C05 surface without duplicating C05 policy."""
    try:
        validate_findings_conflicts_uncertainty(
            packet,
            case,
            questions,
            plan,
            queries,
            slices,
            findings,
            conflicts,
            uncertainty_register,
        )
    except Exception:
        _fail(C06_INVALID_REVIEW_CONTEXT)


def _identity(event: HumanInvestigationEvent, code: str) -> None:
    """Verify original identity claims before detached construction can refresh them."""
    if type(event) is not HumanInvestigationEvent:
        _fail(code)
    try:
        validate_structural_dataclass(event)
        digest = sha256_hex(event.canonical_payload())
        if event.content_hash != digest or event.artifact_id != "hievt_" + digest:
            _fail(code)
        detached = replace(event)
        if canonical_json_bytes(event) != canonical_json_bytes(detached):
            _fail(code)
    except (AttributeError, TypeError, ValueError, OverflowError):
        _fail(code)


def _validate_human_inputs(
    case: InvestigationCase,
    findings: tuple[FindingRecord, ...],
    conflicts: tuple[ConflictRecord, ...],
    uncertainty_register: UncertaintyRegister,
    *,
    outcome: HumanInvestigationOutcome,
    actor_id: str,
    occurred_at: datetime,
    reviewed_finding_ids: tuple[str, ...] = (),
    reviewed_conflict_ids: tuple[str, ...] = (),
    acknowledged_uncertainty_item_ids: tuple[str, ...] = (),
    note_text: str | None = None,
) -> None:
    """Validate explicit Human fields only; notes never confer semantic authority."""
    try:
        if type(outcome) is not HumanInvestigationOutcome:
            _fail(C06_HUMAN_INPUT_INVALID)
        if type(actor_id) is not str or not actor_id or actor_id != actor_id.strip():
            _fail(C06_HUMAN_INPUT_INVALID)
        if type(occurred_at) is not datetime:
            _fail(C06_HUMAN_INPUT_INVALID)
        validate_aware_datetime(occurred_at, "occurred_at")
        if occurred_at < case.opened_at:
            _fail(C06_HUMAN_INPUT_INVALID)
        for refs in (
            reviewed_finding_ids,
            reviewed_conflict_ids,
            acknowledged_uncertainty_item_ids,
        ):
            if type(refs) is not tuple or any(type(ref) is not str for ref in refs):
                _fail(C06_HUMAN_INPUT_INVALID)
            if any(not ref or ref != ref.strip() for ref in refs):
                _fail(C06_HUMAN_INPUT_INVALID)
            validate_sorted_unique(refs, lambda ref: ref, "review references")
        if note_text is not None and (
            type(note_text) is not str or not note_text or note_text != note_text.strip()
        ):
            _fail(C06_HUMAN_INPUT_INVALID)
    except (AttributeError, TypeError, ValueError, OverflowError):
        _fail(C06_HUMAN_INPUT_INVALID)

    finding_ids = frozenset(finding.artifact_id for finding in findings)
    conflict_ids = frozenset(conflict.artifact_id for conflict in conflicts)
    uncertainty_ids = frozenset(item.artifact_id for item in uncertainty_register.items)
    reviewed = frozenset(reviewed_finding_ids)
    if (
        not reviewed <= finding_ids
        or not frozenset(reviewed_conflict_ids) <= conflict_ids
        or not frozenset(acknowledged_uncertainty_item_ids) <= uncertainty_ids
    ):
        _fail(C06_REVIEW_REFERENCE_MISMATCH)

    supported = frozenset(
        finding.artifact_id for finding in findings if finding.status is FindingStatus.SUPPORTED
    )
    unresolved = frozenset(
        finding.artifact_id
        for finding in findings
        if finding.status in (FindingStatus.UNRESOLVED, FindingStatus.UNKNOWN)
    )
    if outcome is HumanInvestigationOutcome.SUPPORTED_FINDING_RECORDED:
        valid = bool(reviewed & supported)
    elif outcome is HumanInvestigationOutcome.NO_SUPPORTED_FINDING:
        valid = reviewed == finding_ids and not supported
    elif outcome is HumanInvestigationOutcome.MORE_EVIDENCE_REQUIRED:
        valid = bool(
            reviewed & unresolved or reviewed_conflict_ids or acknowledged_uncertainty_item_ids
        )
    elif outcome is HumanInvestigationOutcome.INVESTIGATION_REVIEW_COMPLETE:
        valid = (
            reviewed == finding_ids
            and frozenset(reviewed_conflict_ids) == conflict_ids
            and frozenset(acknowledged_uncertainty_item_ids) == uncertainty_ids
        )
    else:
        valid = outcome is HumanInvestigationOutcome.DEFER
    if not valid:
        _fail(C06_OUTCOME_CONTRACT_MISMATCH)


def _validate_previous_event(
    case: InvestigationCase,
    findings: tuple[FindingRecord, ...],
    conflicts: tuple[ConflictRecord, ...],
    uncertainty_register: UncertaintyRegister,
    previous_event: HumanInvestigationEvent | None,
) -> None:
    if previous_event is None:
        return
    _identity(previous_event, C06_PREVIOUS_EVENT_MISMATCH)
    if previous_event.case_id != case.artifact_id:
        _fail(C06_CHAIN_CASE_MISMATCH)
    try:
        _validate_human_inputs(
            case,
            findings,
            conflicts,
            uncertainty_register,
            outcome=previous_event.outcome,
            actor_id=previous_event.actor_id,
            occurred_at=previous_event.occurred_at,
            reviewed_finding_ids=previous_event.reviewed_finding_ids,
            reviewed_conflict_ids=previous_event.reviewed_conflict_ids,
            acknowledged_uncertainty_item_ids=previous_event.acknowledged_uncertainty_item_ids,
            note_text=previous_event.note_text,
        )
    except C06HumanInvestigationError:
        _fail(C06_PREVIOUS_EVENT_MISMATCH)


def _build_admitted_event(
    case: InvestigationCase,
    findings: tuple[FindingRecord, ...],
    conflicts: tuple[ConflictRecord, ...],
    uncertainty_register: UncertaintyRegister,
    *,
    outcome: HumanInvestigationOutcome,
    actor_id: str,
    occurred_at: datetime,
    reviewed_finding_ids: tuple[str, ...] = (),
    reviewed_conflict_ids: tuple[str, ...] = (),
    acknowledged_uncertainty_item_ids: tuple[str, ...] = (),
    note_text: str | None = None,
    previous_event: HumanInvestigationEvent | None = None,
) -> HumanInvestigationEvent:
    """Construct only after the calling public operation admits the exact C05 context."""
    _validate_human_inputs(
        case,
        findings,
        conflicts,
        uncertainty_register,
        outcome=outcome,
        actor_id=actor_id,
        occurred_at=occurred_at,
        reviewed_finding_ids=reviewed_finding_ids,
        reviewed_conflict_ids=reviewed_conflict_ids,
        acknowledged_uncertainty_item_ids=acknowledged_uncertainty_item_ids,
        note_text=note_text,
    )
    _validate_previous_event(case, findings, conflicts, uncertainty_register, previous_event)
    if previous_event is not None and occurred_at < previous_event.occurred_at:
        _fail(C06_CHAIN_TIME_REGRESSION)
    try:
        return HumanInvestigationEvent(
            case_id=case.artifact_id,
            actor_id=actor_id,
            occurred_at=occurred_at,
            outcome=outcome,
            reviewed_finding_ids=reviewed_finding_ids,
            reviewed_conflict_ids=reviewed_conflict_ids,
            acknowledged_uncertainty_item_ids=acknowledged_uncertainty_item_ids,
            previous_event_id=None if previous_event is None else previous_event.artifact_id,
            note_text=note_text,
            note_class="HUMAN_NOTE_NON_EVIDENCE",
        )
    except (AttributeError, TypeError, ValueError, OverflowError):
        _fail(C06_HUMAN_INPUT_INVALID)


def build_human_investigation_event(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
    slices: tuple[EvidenceSlice, ...],
    findings: tuple[FindingRecord, ...],
    conflicts: tuple[ConflictRecord, ...],
    uncertainty_register: UncertaintyRegister,
    *,
    outcome: HumanInvestigationOutcome,
    actor_id: str,
    occurred_at: datetime,
    reviewed_finding_ids: tuple[str, ...] = (),
    reviewed_conflict_ids: tuple[str, ...] = (),
    acknowledged_uncertainty_item_ids: tuple[str, ...] = (),
    note_text: str | None = None,
    previous_event: HumanInvestigationEvent | None = None,
) -> HumanInvestigationEvent:
    """Record bounded review metadata; all Human values are explicit and deterministic."""
    _validate_review_context(
        packet,
        case,
        questions,
        plan,
        queries,
        slices,
        findings,
        conflicts,
        uncertainty_register,
    )
    return _build_admitted_event(
        case,
        findings,
        conflicts,
        uncertainty_register,
        outcome=outcome,
        actor_id=actor_id,
        occurred_at=occurred_at,
        reviewed_finding_ids=reviewed_finding_ids,
        reviewed_conflict_ids=reviewed_conflict_ids,
        acknowledged_uncertainty_item_ids=acknowledged_uncertainty_item_ids,
        note_text=note_text,
        previous_event=previous_event,
    )


def validate_human_investigation_event(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
    slices: tuple[EvidenceSlice, ...],
    findings: tuple[FindingRecord, ...],
    conflicts: tuple[ConflictRecord, ...],
    uncertainty_register: UncertaintyRegister,
    event: HumanInvestigationEvent,
    previous_event: HumanInvestigationEvent | None,
) -> None:
    """Check original identity before reconstructing the complete expected envelope."""
    _validate_review_context(
        packet,
        case,
        questions,
        plan,
        queries,
        slices,
        findings,
        conflicts,
        uncertainty_register,
    )
    _identity(event, C06_EVENT_MISMATCH)
    if event.case_id != case.artifact_id:
        _fail(C06_EVENT_MISMATCH)
    _validate_previous_event(case, findings, conflicts, uncertainty_register, previous_event)
    expected_parent = None if previous_event is None else previous_event.artifact_id
    if event.previous_event_id != expected_parent:
        _fail(C06_PREVIOUS_EVENT_MISMATCH)
    expected = _build_admitted_event(
        case,
        findings,
        conflicts,
        uncertainty_register,
        outcome=event.outcome,
        actor_id=event.actor_id,
        occurred_at=event.occurred_at,
        reviewed_finding_ids=event.reviewed_finding_ids,
        reviewed_conflict_ids=event.reviewed_conflict_ids,
        acknowledged_uncertainty_item_ids=event.acknowledged_uncertainty_item_ids,
        note_text=event.note_text,
        previous_event=previous_event,
    )
    if canonical_json_bytes(event) != canonical_json_bytes(expected):
        _fail(C06_EVENT_MISMATCH)
