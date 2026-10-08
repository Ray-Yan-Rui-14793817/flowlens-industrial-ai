"""Pure grounded presentation of exact frozen C05 artifacts and the full C06 chain."""

from __future__ import annotations

from dataclasses import replace
from typing import Protocol

from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.primitives import validate_structural_dataclass
from flowlens.decision.serialization import (
    canonical_json_bytes,
    canonical_json_text,
    canonical_primitive,
    sha256_hex,
)
from flowlens.investigation.c05_findings import validate_findings_conflicts_uncertainty
from flowlens.investigation.c06_human import validate_human_investigation_event
from flowlens.investigation.c07_policy import (
    AUTHORITY_BOUNDARY_TEXT,
    C07_HUMAN_CHAIN_INVALID,
    C07_HUMAN_CHAIN_REQUIRED,
    C07_INVALID_SUMMARY_CONTEXT,
    C07_RENDERER_MODE_INVALID,
    C07_SUMMARY_RECORD_MISMATCH,
    C07_SUMMARY_REFERENCE_MISMATCH,
    C07_SUMMARY_SECTION_MISMATCH,
    HUMAN_NOTE_BOUNDARY,
    SECTION_CODES,
    SUMMARY_CONTRACT_VERSION,
    fail,
    validate_provider_output,
    validate_provider_runtime,
    validate_provider_texts,
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
    InvestigationSummaryRecord,
    SummarySectionRecord,
    UncertaintyRegister,
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


class SummaryProvider(Protocol):
    def generate(self, runtime_data: str) -> str | bytes: ...


def _admit(context: _Context, human_events: tuple[HumanInvestigationEvent, ...]) -> None:
    try:
        validate_findings_conflicts_uncertainty(*context)
    except Exception:
        fail(C07_INVALID_SUMMARY_CONTEXT)
    if type(human_events) is not tuple:
        fail(C07_HUMAN_CHAIN_INVALID)
    if not human_events:
        fail(C07_HUMAN_CHAIN_REQUIRED)
    if any(type(event) is not HumanInvestigationEvent for event in human_events):
        fail(C07_HUMAN_CHAIN_INVALID)
    previous: HumanInvestigationEvent | None = None
    for event in human_events:
        try:
            validate_human_investigation_event(*context, event, previous)
        except Exception:
            fail(C07_HUMAN_CHAIN_INVALID)
        previous = event


def _rows(heading: str, rows: tuple[tuple[str, str], ...]) -> str:
    if not rows:
        return heading + ": none."
    return heading + ":\n" + "\n".join(code + ": " + value + "." for code, value in rows)


def _baseline(
    context: _Context,
    human_events: tuple[HumanInvestigationEvent, ...],
) -> InvestigationSummaryRecord:
    _, case, _, plan, _, _, findings, conflicts, register = context
    finding_ids = tuple(sorted({item.artifact_id for item in findings}))
    conflict_ids = tuple(sorted({item.artifact_id for item in conflicts}))
    human_ids = tuple(sorted({event.artifact_id for event in human_events}))
    latest = human_events[-1]
    texts = (
        f"Subject type: {case.subject_type}.\nSubject ID: {canonical_json_text(case.subject_id)}.\n"
        f"As-of time: {canonical_primitive(case.as_of_time)}.\nPlan steps: {len(plan.steps)}.",
        _rows(
            "Findings",
            tuple(
                (item.finding_code, item.status.value)
                for item in sorted(findings, key=lambda item: (item.finding_code, item.artifact_id))
            ),
        ),
        _rows(
            "Conflicts",
            tuple(
                (item.conflict_code, item.conflict_type.value)
                for item in sorted(
                    conflicts, key=lambda item: (item.conflict_code, item.artifact_id)
                )
            ),
        ),
        _rows(
            "Uncertainty",
            tuple(
                (item.uncertainty_code, item.uncertainty_type.value)
                for item in sorted(
                    register.items,
                    key=lambda item: (item.uncertainty_code, item.artifact_id),
                )
            ),
        ),
        f"Human event count: {len(human_events)}.\nLatest outcome: {latest.outcome.value}.\n"
        f"Latest occurred_at: {canonical_primitive(latest.occurred_at)}.\n" + HUMAN_NOTE_BOUNDARY,
        AUTHORITY_BOUNDARY_TEXT,
    )
    refs = (
        tuple(sorted((case.artifact_id, plan.artifact_id))),
        finding_ids,
        conflict_ids,
        tuple(sorted({register.artifact_id, *(item.artifact_id for item in register.items)})),
        human_ids,
        (),
    )
    return InvestigationSummaryRecord(
        case_id=case.artifact_id,
        plan_id=plan.artifact_id,
        finding_ids=finding_ids,
        conflict_ids=conflict_ids,
        uncertainty_register_id=register.artifact_id,
        human_event_ids=human_ids,
        summary_contract_version=SUMMARY_CONTRACT_VERSION,
        sections=tuple(
            SummarySectionRecord(
                section_code=code,
                renderer_mode=SummaryRendererMode.DETERMINISTIC,
                text=text,
                grounding_refs=grounding,
            )
            for code, text, grounding in zip(SECTION_CODES, texts, refs, strict=True)
        ),
    )


def _runtime_data(baseline: InvestigationSummaryRecord) -> str:
    value = canonical_json_text(
        tuple(
            {
                "section_code": section.section_code,
                "deterministic_text": section.text,
                "grounding_refs": section.grounding_refs,
            }
            for section in baseline.sections[:5]
        )
    )
    validate_provider_runtime(value)
    return value


def _with_mode(
    baseline: InvestigationSummaryRecord,
    mode: SummaryRendererMode,
    texts: tuple[str, ...] | None = None,
) -> InvestigationSummaryRecord:
    selected = tuple(section.text for section in baseline.sections[:5]) if texts is None else texts
    return replace(
        baseline,
        sections=(
            *(
                replace(section, renderer_mode=mode, text=text)
                for section, text in zip(baseline.sections[:5], selected, strict=True)
            ),
            baseline.sections[5],
        ),
    )


def render_investigation_summary(
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
    *,
    renderer_mode: SummaryRendererMode = SummaryRendererMode.DETERMINISTIC,
    provider: SummaryProvider | None = None,
) -> InvestigationSummaryRecord:
    """No note access, navigation, journal read or authority; model failure degrades as a whole."""
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
    _admit(context, human_events)
    if type(renderer_mode) is not SummaryRendererMode:
        fail(C07_RENDERER_MODE_INVALID)
    baseline = _baseline(context, human_events)
    if renderer_mode is SummaryRendererMode.DETERMINISTIC:
        return baseline
    fallback = _with_mode(baseline, SummaryRendererMode.DEGRADED_FALLBACK)
    if renderer_mode is SummaryRendererMode.DEGRADED_FALLBACK or provider is None:
        return fallback
    try:
        raw = provider.generate(_runtime_data(baseline))
        texts = validate_provider_output(raw, tuple(s.text for s in baseline.sections[:5]))
        return _with_mode(baseline, SummaryRendererMode.BOUNDED_LLM, texts)
    except Exception:
        return fallback


def _original_identity(summary: InvestigationSummaryRecord) -> None:
    if type(summary) is not InvestigationSummaryRecord:
        fail(C07_SUMMARY_RECORD_MISMATCH)
    if type(summary.sections) is not tuple or any(
        type(section) is not SummarySectionRecord for section in summary.sections
    ):
        fail(C07_SUMMARY_RECORD_MISMATCH)
    try:
        validate_structural_dataclass(summary)
        # Top identity deliberately excludes nested derived claims in C01.
        # Check EVERY original child as well, before ANY detached reconstruction.
        for item in (summary, *summary.sections):
            digest = sha256_hex(item.canonical_payload())
            prefix = "isum_" if type(item) is InvestigationSummaryRecord else "isect_"
            if item.content_hash != digest or item.artifact_id != prefix + digest:
                fail(C07_SUMMARY_RECORD_MISMATCH)
        detached = replace(summary, sections=tuple(replace(s) for s in summary.sections))
        if canonical_json_bytes(summary) != canonical_json_bytes(detached):
            fail(C07_SUMMARY_RECORD_MISMATCH)
    except Exception:
        fail(C07_SUMMARY_RECORD_MISMATCH)


def validate_investigation_summary(
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
) -> None:
    """Re-admit context, prove original identities, then enforce exact source/mode bindings."""
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
    _admit(context, human_events)
    _original_identity(summary)
    baseline = _baseline(context, human_events)
    if summary.summary_contract_version != SUMMARY_CONTRACT_VERSION:
        fail(C07_SUMMARY_RECORD_MISMATCH)
    if any(
        getattr(summary, name) != getattr(baseline, name)
        for name in (
            "case_id",
            "plan_id",
            "finding_ids",
            "conflict_ids",
            "uncertainty_register_id",
            "human_event_ids",
        )
    ):
        fail(C07_SUMMARY_REFERENCE_MISMATCH)
    if tuple(section.section_code for section in summary.sections) != SECTION_CODES:
        fail(C07_SUMMARY_SECTION_MISMATCH)
    if any(
        s.grounding_refs != b.grounding_refs
        for s, b in zip(summary.sections, baseline.sections, strict=True)
    ):
        fail(C07_SUMMARY_REFERENCE_MISMATCH)
    mode = summary.sections[0].renderer_mode
    if summary.sections[5].renderer_mode is not SummaryRendererMode.DETERMINISTIC or any(
        section.renderer_mode is not mode for section in summary.sections[:5]
    ):
        fail(C07_RENDERER_MODE_INVALID)
    if canonical_json_bytes(summary.sections[5]) != canonical_json_bytes(baseline.sections[5]):
        fail(C07_SUMMARY_SECTION_MISMATCH)
    if mode is SummaryRendererMode.DETERMINISTIC:
        expected = baseline
    elif mode is SummaryRendererMode.DEGRADED_FALLBACK:
        expected = _with_mode(baseline, mode)
    elif mode is SummaryRendererMode.BOUNDED_LLM:
        _runtime_data(baseline)
        texts = tuple(section.text for section in summary.sections[:5])
        validate_provider_texts(texts, tuple(section.text for section in baseline.sections[:5]))
        expected = _with_mode(baseline, mode, texts)
    else:
        fail(C07_RENDERER_MODE_INVALID)
    if canonical_json_bytes(summary) != canonical_json_bytes(expected):
        fail(C07_SUMMARY_RECORD_MISMATCH)
