"""Pure admission and deterministic projection of explicit frozen W03/W04 artifacts."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace
from typing import Any, cast

from flowlens.decision import contracts as dc
from flowlens.decision.c06_validation import validate_c05_packet, validate_human_decision_event
from flowlens.decision.serialization import canonical_json_bytes, sha256_hex
from flowlens.investigation import contracts as ic
from flowlens.investigation.c02_binding import validate_investigation_case_binding
from flowlens.investigation.c03_planning import validate_investigation_planning
from flowlens.investigation.c05_findings import validate_findings_conflicts_uncertainty
from flowlens.investigation.c07_summary import validate_investigation_summary
from flowlens.product import contracts as pc


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductSourceBundle:
    packet: dc.DecisionPacket
    explanation: dc.ExplanationRecord | None
    decision_events: tuple[dc.HumanDecisionEvent, ...]
    case: ic.InvestigationCase
    questions: tuple[ic.InvestigationQuestion, ...]
    plan: ic.InvestigationPlan
    queries: tuple[ic.EvidenceQuerySpec, ...]
    slices: tuple[ic.EvidenceSlice, ...]
    findings: tuple[ic.FindingRecord, ...]
    conflicts: tuple[ic.ConflictRecord, ...]
    uncertainty_register: ic.UncertaintyRegister
    investigation_events: tuple[ic.HumanInvestigationEvent, ...]
    summary: ic.InvestigationSummaryRecord


def _fail(code: pc.ProductErrorCode) -> None:
    raise pc.ProductError(code) from None


def validate_product_source(source: ProductSourceBundle) -> None:
    """Reject original identity/scope errors before any presentation projection."""
    try:
        pc.require_exact(source, ProductSourceBundle)
        pc.source_value(source)
    except Exception:
        _fail(pc.ProductErrorCode.INVALID_PRODUCT_SOURCE)
    packet, case = source.packet, source.case
    try:
        validate_c05_packet(packet)
        validate_investigation_case_binding(packet, case)
    except Exception:
        _fail(pc.ProductErrorCode.SOURCE_IDENTITY_MISMATCH)
    context = (
        packet,
        case,
        source.questions,
        source.plan,
        source.queries,
        source.slices,
        source.findings,
        source.conflicts,
        source.uncertainty_register,
    )
    try:
        validate_investigation_planning(packet, case, source.questions, source.plan)
        validate_findings_conflicts_uncertainty(*context)
    except Exception:
        _fail(pc.ProductErrorCode.SOURCE_SCOPE_MISMATCH)
    try:
        previous: dc.HumanDecisionEvent | None = None
        seen: set[str] = set()
        for event in source.decision_events:
            if event.decision_event_id in seen:
                _fail(pc.ProductErrorCode.SOURCE_IDENTITY_MISMATCH)
            validate_human_decision_event(packet, event, previous)
            seen.add(event.decision_event_id)
            previous = event
        explanation = source.explanation
        if explanation is not None:
            if (
                explanation.packet_id != packet.packet_id
                or explanation.run_id != packet.run.run_id
                or not set(explanation.referenced_evidence_ids)
                <= {e.evidence_id for e in packet.evidence.evidence}
                or explanation.provenance.input_artifact_ids != (packet.packet_id,)
                or any(
                    r.available_at > packet.run.as_of_time
                    or (r.observed_at is not None and r.observed_at > packet.run.as_of_time)
                    for r in explanation.provenance.source_refs
                )
            ):
                _fail(pc.ProductErrorCode.SOURCE_IDENTITY_MISMATCH)
    except Exception:
        _fail(pc.ProductErrorCode.SOURCE_IDENTITY_MISMATCH)
    try:
        if len({e.artifact_id for e in source.investigation_events}) != len(
            source.investigation_events
        ):
            _fail(pc.ProductErrorCode.SOURCE_SCOPE_MISMATCH)
        # The unchanged summary validator also revalidates every investigation
        # Human event against its actual predecessor and all C02-C05 bindings.
        validate_investigation_summary(*context, source.investigation_events, source.summary)
    except Exception:
        _fail(pc.ProductErrorCode.SOURCE_SCOPE_MISMATCH)


# Source to product classes only. No artifact dispatch from external names.
_MIRRORS = {
    cast(Any, cls)._source_type: cls
    for cls in (
        pc.ProductEvidenceView,
        pc.ProductEvidenceBundleView,
        pc.ProductSignalView,
        pc.ProductSignalBundleView,
        pc.ProductDiagnosisClaimView,
        pc.ProductDiagnosisView,
        pc.ProductCandidateView,
        pc.ProductCandidateSetView,
        pc.ProductSimulationView,
        pc.ProductSimulationBundleView,
        pc.ProductRecommendationView,
        pc.ProductExplanationView,
        pc.DecisionHumanReviewView,
        pc.ProductFindingView,
        pc.ProductConflictView,
        pc.ProductUncertaintyView,
        pc.ProductUncertaintyRegisterView,
        pc.ProductSummarySectionView,
        pc.InvestigationHumanReviewView,
        pc.ProductInvestigationSummaryView,
        pc.ProductDecisionView,
    )
}


def _mirror(value: object) -> Any:
    if type(value) is tuple:
        return tuple(_mirror(item) for item in value)
    cls = _MIRRORS.get(type(value))
    if cls is not None and is_dataclass(value) and not isinstance(value, type):
        return cast(Any, cls)(**{f.name: _mirror(getattr(value, f.name)) for f in fields(value)})
    return value


def _identity(source: ProductSourceBundle) -> pc.ProductCaseIdentity:
    packet = source.packet
    return pc.ProductCaseIdentity(
        order_id=packet.run.order_id,
        as_of_time=packet.run.as_of_time,
        dataset_version=packet.run.dataset_version,
        dataset_hash=packet.run.dataset_hash,
        run_id=packet.run.run_id,
        snapshot_id=packet.snapshot.snapshot_id,
        snapshot_hash=packet.snapshot.snapshot_hash,
        packet_id=packet.packet_id,
        packet_hash=sha256_hex(packet),
        case_id=source.case.artifact_id,
        plan_id=source.plan.artifact_id,
        summary_id=source.summary.artifact_id,
    )


def validate_product_view_sources(view: pc.ProductCaseView) -> None:
    """Also enforce admission on direct public model construction."""
    try:
        investigation = view.investigation
        source = ProductSourceBundle(
            packet=pc.source_value(view.decision),
            explanation=pc.source_value(view.decision.explanation),
            decision_events=pc.source_value(view.decision.human_reviews),
            case=investigation.case,
            questions=investigation.questions,
            plan=investigation.plan,
            queries=investigation.queries,
            slices=investigation.slices,
            findings=pc.source_value(investigation.findings),
            conflicts=pc.source_value(investigation.conflicts),
            uncertainty_register=pc.source_value(investigation.uncertainty_register),
            investigation_events=pc.source_value(investigation.human_reviews),
            summary=pc.source_value(investigation.summary),
        )
        validate_product_source(source)
        if canonical_json_bytes(view.identity) != canonical_json_bytes(_identity(source)):
            _fail(pc.ProductErrorCode.SOURCE_IDENTITY_MISMATCH)
    except pc.ProductError:
        raise
    except Exception:
        _fail(pc.ProductErrorCode.INVALID_PRODUCT_SOURCE)


def project_product_case(source: ProductSourceBundle) -> pc.ProductCaseView:
    """Same admitted source world yields byte-identical detached product JSON."""
    try:
        validate_product_source(source)
        # Copy original immutable artifacts; no outside reference can later
        # mutate this product through a deliberately bypassed frozen setter.
        detached = cast(ProductSourceBundle, pc.source_value(source))
        decision = replace(
            cast(pc.ProductDecisionView, _mirror(detached.packet)),
            explanation=_mirror(detached.explanation),
            human_reviews=_mirror(detached.decision_events),
        )
        investigation = pc.ProductInvestigationView(
            case=detached.case,
            questions=detached.questions,
            plan=detached.plan,
            queries=detached.queries,
            slices=detached.slices,
            findings=_mirror(detached.findings),
            conflicts=_mirror(detached.conflicts),
            uncertainty_register=_mirror(detached.uncertainty_register),
            human_reviews=_mirror(detached.investigation_events),
            summary=_mirror(detached.summary),
        )
        return pc.ProductCaseView(
            identity=_identity(detached),
            decision=decision,
            investigation=investigation,
            capability_boundary=pc.ProductCapabilityBoundary(),
        )
    except pc.ProductError:
        raise
    except Exception:
        _fail(pc.ProductErrorCode.INTERNAL_ERROR)
    raise AssertionError("unreachable")
