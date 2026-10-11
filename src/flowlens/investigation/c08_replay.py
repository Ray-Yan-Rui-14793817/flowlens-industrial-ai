"""Pure re-admission of frozen C02-C07 artifacts, with no external capability."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import fields, is_dataclass
from types import UnionType
from typing import TypeAliasType, get_args, get_origin, get_type_hints

from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.primitives import validate_artifact_id, validate_sha256
from flowlens.decision.serialization import canonical_json_bytes, sha256_hex
from flowlens.investigation.c02_binding import (
    build_investigation_case,
    validate_investigation_case_binding,
)
from flowlens.investigation.c03_planning import validate_investigation_planning
from flowlens.investigation.c04_queries import validate_evidence_query_specs
from flowlens.investigation.c05_findings import (
    derive_findings_conflicts_uncertainty,
    validate_findings_conflicts_uncertainty,
)
from flowlens.investigation.c06_human import validate_human_investigation_event
from flowlens.investigation.c07_summary import (
    render_investigation_summary,
    validate_investigation_summary,
)
from flowlens.investigation.c08_policy import (
    C08_CASE_REPLAY_MISMATCH,
    C08_EVIDENCE_REPLAY_MISMATCH,
    C08_FINDINGS_REPLAY_MISMATCH,
    C08_HUMAN_CHAIN_REPLAY_MISMATCH,
    C08_INVALID_REPLAY_CONTEXT,
    C08_LIMITATION_CODES,
    C08_PLANNING_REPLAY_MISMATCH,
    C08_QUERY_REPLAY_MISMATCH,
    C08_REPLAY_CONTRACT_VERSION,
    C08_REPLAY_ID_PREFIX,
    C08_REPLAY_RECEIPT_MISMATCH,
    C08_REPLAY_RECEIPT_SCHEMA_VERSION,
    C08_SUMMARY_REPLAY_MISMATCH,
    InvestigationReplayReceipt,
    fail,
)
from flowlens.investigation.contracts import (
    _PREFIXES,
    ConflictRecord,
    EvidenceQuerySpec,
    EvidenceSlice,
    FindingRecord,
    HumanInvestigationEvent,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
    InvestigationSummaryRecord,
    UncertaintyRegister,
    _Artifact,
)
from flowlens.investigation.enums import SummaryRendererMode

type _Context = tuple[
    DecisionPacket,
    InvestigationCase,
    tuple[InvestigationQuestion, ...],
    InvestigationPlan,
    tuple[EvidenceQuerySpec, ...],
    tuple[EvidenceSlice, ...],
    tuple[FindingRecord, ...],
    tuple[ConflictRecord, ...],
    UncertaintyRegister,
]


@contextmanager
def _guard(code: str) -> Iterator[None]:
    try:
        yield
    except Exception:
        fail(code)


def _exact_structure(value: object, expected: object) -> bool:
    """Inspect declared frozen types before any canonicalization or reconstruction."""
    if isinstance(expected, TypeAliasType):
        return _exact_structure(value, expected.__value__)
    origin = get_origin(expected)
    if origin is UnionType:
        return any(_exact_structure(value, part) for part in get_args(expected))
    if origin is tuple:
        args = get_args(expected)
        if type(value) is not tuple:
            return False
        if len(args) == 2 and args[1] is Ellipsis:
            return all(_exact_structure(item, args[0]) for item in value)
        return len(value) == len(args) and all(
            _exact_structure(item, hint) for item, hint in zip(value, args, strict=True)
        )
    if not isinstance(expected, type) or type(value) is not expected:
        return False
    if is_dataclass(value):
        hints = get_type_hints(expected)
        return all(
            _exact_structure(getattr(value, item.name), hints[item.name]) for item in fields(value)
        )
    return True


def _original_identities(value: object) -> None:
    """Check every original C01 child; parent identities exclude child derived fields."""
    if type(value) is tuple:
        for member in value:
            _original_identities(member)
    elif is_dataclass(value):
        for item in fields(value):
            _original_identities(getattr(value, item.name))
        if isinstance(value, _Artifact):
            digest = sha256_hex(value.canonical_payload())
            if value.content_hash != digest or value.artifact_id != _PREFIXES[value._kind] + digest:
                raise ValueError


def _receipt(
    context: _Context,
    human_events: tuple[HumanInvestigationEvent, ...],
    authoritative: InvestigationSummaryRecord,
    presented: InvestigationSummaryRecord,
) -> InvestigationReplayReceipt:
    packet, case, questions, plan, queries, slices, findings, conflicts, register = context
    source_chain_sha256 = sha256_hex(
        {
            "packet": packet,
            "case": case,
            "questions": questions,
            "plan": plan,
            "queries": queries,
            "slices": slices,
            "findings": findings,
            "conflicts": conflicts,
            "uncertainty_register": register,
            "human_events": human_events,
        }
    )
    core: dict[str, object] = {
        "replay_contract_version": C08_REPLAY_CONTRACT_VERSION,
        "source_chain_sha256": source_chain_sha256,
        "authoritative_summary_id": authoritative.artifact_id,
        "authoritative_summary_content_hash": authoritative.content_hash,
        "limitation_codes": C08_LIMITATION_CODES,
    }
    core_sha256 = sha256_hex(core)
    payload: dict[str, object] = core | {
        "schema_version": C08_REPLAY_RECEIPT_SCHEMA_VERSION,
        "replay_core_sha256": core_sha256,
        "replay_id": C08_REPLAY_ID_PREFIX + core_sha256,
        "packet_id": packet.packet_id,
        "case_id": case.artifact_id,
        "question_ids": tuple(q.artifact_id for q in questions),
        "plan_id": plan.artifact_id,
        "query_ids": tuple(q.artifact_id for q in queries),
        "evidence_slice_ids": tuple(s.artifact_id for s in slices),
        "finding_ids": tuple(f.artifact_id for f in findings),
        "conflict_ids": tuple(c.artifact_id for c in conflicts),
        "uncertainty_register_id": register.artifact_id,
        "human_event_ids": tuple(e.artifact_id for e in human_events),
        "presented_summary_id": presented.artifact_id,
        "presented_summary_content_hash": presented.content_hash,
        "presented_renderer_mode": presented.sections[0].renderer_mode,
    }
    payload["receipt_sha256"] = sha256_hex(payload)
    receipt = object.__new__(InvestigationReplayReceipt)
    for name, value in payload.items():
        object.__setattr__(receipt, name, value)
    return receipt


def replay_investigation(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
    slices: tuple[EvidenceSlice, ...],
    findings: tuple[FindingRecord, ...],
    conflicts: tuple[ConflictRecord, ...],
    uncertainty_register: UncertaintyRegister,
    human_events: tuple[HumanInvestigationEvent, ...],
    summary: InvestigationSummaryRecord,
) -> InvestigationReplayReceipt:
    """Validate the captured chain in order and freeze deterministic replay authority."""
    context: _Context = (
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
    with _guard(C08_INVALID_REPLAY_CONTEXT):
        if not (
            _exact_structure(context, _Context)
            and _exact_structure(human_events, tuple[HumanInvestigationEvent, ...])
            and _exact_structure(summary, InvestigationSummaryRecord)
            and human_events
        ):
            raise ValueError
        # C02 checks the original W03 packet, including identity and decision-time availability.
        build_investigation_case(packet)

    with _guard(C08_CASE_REPLAY_MISMATCH):
        _original_identities(case)
        validate_investigation_case_binding(packet, case)
    with _guard(C08_PLANNING_REPLAY_MISMATCH):
        _original_identities((questions, plan))
        validate_investigation_planning(packet, case, questions, plan)
    with _guard(C08_QUERY_REPLAY_MISMATCH):
        _original_identities(queries)
        validate_evidence_query_specs(packet, case, questions, plan, queries)
    with _guard(C08_EVIDENCE_REPLAY_MISMATCH):
        _original_identities(slices)
        derive_findings_conflicts_uncertainty(packet, case, questions, plan, queries, slices)
    with _guard(C08_FINDINGS_REPLAY_MISMATCH):
        _original_identities((findings, conflicts, uncertainty_register))
        validate_findings_conflicts_uncertainty(*context)
    with _guard(C08_HUMAN_CHAIN_REPLAY_MISMATCH):
        _original_identities(human_events)
        previous: HumanInvestigationEvent | None = None
        for event in human_events:
            validate_human_investigation_event(*context, event, previous)
            previous = event
    with _guard(C08_SUMMARY_REPLAY_MISMATCH):
        _original_identities(summary)
        validate_investigation_summary(*context, human_events, summary)
        authoritative = render_investigation_summary(
            *context,
            human_events,
            renderer_mode=SummaryRendererMode.DETERMINISTIC,
            provider=None,
        )
    with _guard(C08_REPLAY_RECEIPT_MISMATCH):
        result = _receipt(context, human_events, authoritative, summary)
    return result


def _original_receipt(receipt: InvestigationReplayReceipt) -> bytes:
    if not _exact_structure(receipt, InvestigationReplayReceipt):
        raise ValueError
    if (
        receipt.schema_version != C08_REPLAY_RECEIPT_SCHEMA_VERSION
        or receipt.replay_contract_version != C08_REPLAY_CONTRACT_VERSION
        or receipt.limitation_codes != C08_LIMITATION_CODES
        or not receipt.human_event_ids
    ):
        raise ValueError
    for name in (
        "replay_core_sha256",
        "source_chain_sha256",
        "authoritative_summary_content_hash",
        "presented_summary_content_hash",
        "receipt_sha256",
    ):
        validate_sha256(getattr(receipt, name), name)
    for name, prefix in (
        ("packet_id", "pkt_"),
        ("case_id", "icase_"),
        ("plan_id", "iplan_"),
        ("uncertainty_register_id", "ureg_"),
        ("authoritative_summary_id", "isum_"),
        ("presented_summary_id", "isum_"),
    ):
        value = getattr(receipt, name)
        validate_artifact_id(value, prefix, value)
    for name, prefix in (
        ("question_ids", "iquest_"),
        ("query_ids", "eqry_"),
        ("evidence_slice_ids", "eslice_"),
        ("finding_ids", "ifind_"),
        ("conflict_ids", "iconf_"),
        ("human_event_ids", "hievt_"),
    ):
        values = getattr(receipt, name)
        if len(set(values)) != len(values):
            raise ValueError
        for value in values:
            validate_artifact_id(value, prefix, value)
    core = {
        name: getattr(receipt, name)
        for name in (
            "replay_contract_version",
            "source_chain_sha256",
            "authoritative_summary_id",
            "authoritative_summary_content_hash",
            "limitation_codes",
        )
    }
    if (
        receipt.replay_core_sha256 != sha256_hex(core)
        or receipt.replay_id != C08_REPLAY_ID_PREFIX + receipt.replay_core_sha256
    ):
        raise ValueError
    metadata = {
        item.name: getattr(receipt, item.name)
        for item in fields(receipt)
        if item.name != "receipt_sha256"
    }
    if receipt.receipt_sha256 != sha256_hex(metadata):
        raise ValueError
    return canonical_json_bytes(receipt)


def validate_investigation_replay(
    packet: DecisionPacket,
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
    plan: InvestigationPlan,
    queries: tuple[EvidenceQuerySpec, ...],
    slices: tuple[EvidenceSlice, ...],
    findings: tuple[FindingRecord, ...],
    conflicts: tuple[ConflictRecord, ...],
    uncertainty_register: UncertaintyRegister,
    human_events: tuple[HumanInvestigationEvent, ...],
    summary: InvestigationSummaryRecord,
    receipt: InvestigationReplayReceipt,
) -> None:
    """Check the original receipt, then re-admit the same chain and compare exact bytes."""
    with _guard(C08_REPLAY_RECEIPT_MISMATCH):
        original = _original_receipt(receipt)
    expected = replay_investigation(
        packet,
        case,
        questions,
        plan,
        queries,
        slices,
        findings,
        conflicts,
        uncertainty_register,
        human_events,
        summary,
    )
    with _guard(C08_REPLAY_RECEIPT_MISMATCH):
        if original != canonical_json_bytes(expected):
            raise ValueError
