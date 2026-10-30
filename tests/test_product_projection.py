"""C01 explicit-source admission, preservation, hostile bindings and capability controls."""

from __future__ import annotations

import ast
import builtins
import copy
import io
import json
import os
import random
import secrets
import socket
import time
from dataclasses import fields, replace
from datetime import timedelta
from functools import cache
from pathlib import Path
from typing import Any, NoReturn, cast

import pytest

from flowlens.decision.c06_human import build_human_decision_event
from flowlens.decision.c08_explanation import explain_decision_packet
from flowlens.decision.contracts import HumanDecisionEvent
from flowlens.decision.enums import HumanDecisionType, SignalState
from flowlens.decision.serialization import canonical_json_bytes, sha256_hex
from flowlens.investigation.c06_human import build_human_investigation_event
from flowlens.investigation.c07_summary import render_investigation_summary
from flowlens.investigation.contracts import HumanInvestigationEvent
from flowlens.investigation.enums import (
    FindingStatus,
    HumanInvestigationOutcome,
    SummaryRendererMode,
)
from flowlens.product import contracts as pc
from flowlens.product.projection import ProductSourceBundle, project_product_case
from test_c05_policy import unsafe_replace
from test_investigation_human import _context, _event

ROOT = Path(__file__).resolve().parents[1]


def _replace[T](value: T, **changes: Any) -> T:
    """Typed hostile fixture replacement; deliberately allows invalid source field types."""
    return cast(T, replace(cast(Any, value), **changes))


@cache
def _source(shape: str = "baseline") -> ProductSourceBundle:
    context = _context(unknown=shape == "unknown", conflict=shape == "conflict")
    packet = context[0]
    events: tuple[HumanInvestigationEvent, ...] = (
        _event(context, note_text="C01_OPAQUE_REVIEW_NOTE"),
    )
    if shape == "investigation-review":
        events += (
            build_human_investigation_event(
                *context,
                outcome=HumanInvestigationOutcome.DEFER,
                actor_id="operations-manager",
                occurred_at=events[0].occurred_at + timedelta(hours=1),
                previous_event=events[0],
                note_text="C01_OPAQUE_FOLLOWUP_NOTE",
            ),
        )
    mode = (
        SummaryRendererMode.DEGRADED_FALLBACK
        if shape == "degraded-summary"
        else SummaryRendererMode.DETERMINISTIC
    )
    summary = render_investigation_summary(*context, events, renderer_mode=mode)
    decisions: tuple[HumanDecisionEvent, ...] = ()
    if shape == "decision-review":
        first = build_human_decision_event(
            packet,
            decision=HumanDecisionType.DEFER,
            actor_id="operations-manager",
            decided_at=packet.run.as_of_time + timedelta(hours=1),
            comment="C01_DECISION_NOTE",
        )
        decisions = (
            first,
            build_human_decision_event(
                packet,
                decision=HumanDecisionType.REJECT,
                actor_id="operations-manager",
                decided_at=first.decided_at + timedelta(hours=1),
                previous_event=first,
                comment="C01_DECISION_FOLLOWUP",
            ),
        )
    return ProductSourceBundle(
        packet=packet,
        explanation=None,
        decision_events=decisions,
        case=context[1],
        questions=context[2],
        plan=context[3],
        queries=context[4],
        slices=context[5],
        findings=context[6],
        conflicts=context[7],
        uncertainty_register=context[8],
        investigation_events=events,
        summary=summary,
    )


@cache
def _view(shape: str = "baseline") -> pc.ProductCaseView:
    return project_product_case(_source(shape))


def _reject(source: ProductSourceBundle, code: pc.ProductErrorCode | None = None) -> None:
    with pytest.raises(pc.ProductError) as caught:
        project_product_case(source)
    assert caught.value.code in pc.ProductErrorCode
    assert str(caught.value) == caught.value.code.value
    assert caught.value.__suppress_context__ and caught.value.__cause__ is None
    if code is not None:
        assert caught.value.code is code


@pytest.mark.parametrize(
    "shape",
    [
        "baseline",
        "unknown",
        "conflict",
        "degraded-summary",
        "decision-review",
        "investigation-review",
    ],
)
def test_exact_source_projection_is_repeated_and_detached(shape: str) -> None:
    source = _source(shape)
    before = canonical_json_bytes(source)
    view = _view(shape)
    assert view.to_json() == project_product_case(source).to_json()
    assert canonical_json_bytes(source) == before
    assert canonical_json_bytes(pc.source_value(view.decision)) == canonical_json_bytes(
        source.packet
    )
    assert view.investigation.case == source.case and view.investigation.case is not source.case
    assert view.identity.packet_hash == sha256_hex(source.packet)
    assert view.identity.packet_id == source.packet.packet_id
    assert view.identity.case_id == source.case.artifact_id
    assert view.identity.plan_id == source.plan.artifact_id
    assert view.identity.summary_id == source.summary.artifact_id


@pytest.mark.parametrize("name", [f.name for f in fields(ProductSourceBundle)])
def test_every_bundle_argument_rejects_wrong_exact_type(name: str) -> None:
    _reject(
        _replace(_source(), **{name: cast(Any, [])}), pc.ProductErrorCode.INVALID_PRODUCT_SOURCE
    )


@pytest.mark.parametrize("change", ["packet", "run", "subject", "as_of", "packet_hash"])
def test_case_identity_mismatch_is_rejected(change: str) -> None:
    source = _source()
    changes: dict[str, Any] = {
        "packet": {"source_decision_packet_id": "pkt_" + "0" * 64},
        "run": {"decision_run_id": "run_" + "0" * 64},
        "subject": {"subject_id": "DIFFERENT_ORDER"},
        "as_of": {"as_of_time": source.case.as_of_time - timedelta(seconds=1)},
        "packet_hash": {"source_decision_packet_hash": "0" * 64},
    }
    _reject(
        _replace(source, case=_replace(source.case, **changes[change])),
        pc.ProductErrorCode.SOURCE_IDENTITY_MISMATCH,
    )


@pytest.mark.parametrize("name", ["questions", "queries", "slices", "findings", "conflicts"])
def test_cross_case_members_are_rejected(name: str) -> None:
    source = _source("conflict")
    values = cast(tuple[Any, ...], getattr(source, name))
    assert values
    changed = _replace(values[0], case_id="icase_" + "0" * 64)
    _reject(
        _replace(source, **{name: (changed, *values[1:])}),
        pc.ProductErrorCode.SOURCE_SCOPE_MISMATCH,
    )


def test_plan_case_and_uncertainty_case_mismatches_are_rejected() -> None:
    source = _source("unknown")
    _reject(_replace(source, plan=_replace(source.plan, case_id="icase_" + "0" * 64, steps=())))
    item = _replace(source.uncertainty_register.items[0], case_id="icase_" + "0" * 64)
    register = _replace(source.uncertainty_register, case_id=item.case_id, items=(item,))
    _reject(_replace(source, uncertainty_register=register))


@pytest.mark.parametrize("name", ["finding_ids", "conflict_ids", "human_event_ids"])
def test_summary_reference_sets_must_match_exact_context(name: str) -> None:
    source = _source("conflict")
    _reject(
        _replace(source, summary=_replace(source.summary, **{name: ()})),
        pc.ProductErrorCode.SOURCE_SCOPE_MISMATCH,
    )


def test_summary_plan_and_uncertainty_reference_mismatches() -> None:
    source = _source()
    for name, wrong in (
        ("plan_id", "iplan_" + "0" * 64),
        ("uncertainty_register_id", "ureg_" + "0" * 64),
    ):
        _reject(_replace(source, summary=_replace(source.summary, **{name: wrong})))


@pytest.mark.parametrize("name", ["packet_id", "run_id"])
def test_explanation_must_bind_exact_packet_and_run(name: str) -> None:
    source = _source()
    explanation = explain_decision_packet(source.packet)
    prefix = "pkt_" if name == "packet_id" else "run_"
    # Bypass construction to prove ORIGINAL envelope admission, not just source ctor validation.
    damaged = unsafe_replace(explanation, **{name: prefix + "0" * 64})
    _reject(_replace(source, explanation=damaged))


def test_valid_explanation_preserves_mode_sections_and_refs() -> None:
    source = _source()
    explanation = explain_decision_packet(source.packet)
    view = project_product_case(_replace(source, explanation=explanation))
    assert view.decision.explanation is not None
    assert view.decision.explanation.mode is explanation.mode
    assert view.decision.explanation.sections == explanation.sections
    assert view.decision.explanation.referenced_evidence_ids == explanation.referenced_evidence_ids
    assert canonical_json_bytes(pc.source_value(view.decision.explanation)) == canonical_json_bytes(
        explanation
    )


@pytest.mark.parametrize("plane", ["decision", "investigation"])
@pytest.mark.parametrize("attack", ["reverse", "duplicate", "missing_parent", "wrong_scope"])
def test_both_human_chains_require_exact_scope_and_predecessors(plane: str, attack: str) -> None:
    source = _source("decision-review" if plane == "decision" else "investigation-review")
    name = "decision_events" if plane == "decision" else "investigation_events"
    events = cast(tuple[Any, ...], getattr(source, name))
    if attack == "reverse":
        changed = tuple(reversed(events))
    elif attack == "duplicate":
        changed = (events[0], events[0])
    elif attack == "missing_parent":
        changed = events[1:]
    else:
        changed = (
            unsafe_replace(
                events[0], **{"packet_id" if plane == "decision" else "case_id": "OTHER_SOURCE"}
            ),
        )
    _reject(_replace(source, **{name: changed}))


@pytest.mark.parametrize(
    "target",
    [
        "packet",
        "case",
        "question",
        "step",
        "query",
        "observation",
        "finding",
        "conflict",
        "uncertainty",
        "summary",
        "section",
    ],
)
def test_original_nested_identity_claims_cannot_be_repaired_by_projection(target: str) -> None:
    source = _source("conflict")
    objects: dict[str, Any] = {
        "packet": source.packet,
        "case": source.case,
        "question": source.questions[0],
        "step": source.plan.steps[0],
        "query": source.queries[0],
        "observation": next(o for s in source.slices for o in s.observations),
        "finding": source.findings[0],
        "conflict": source.conflicts[0],
        "uncertainty": source.uncertainty_register.items[0],
        "summary": source.summary,
        "section": source.summary.sections[0],
    }
    damaged = copy.deepcopy(source)
    # Locate by original object identity-independent canonical bytes.
    needle = canonical_json_bytes(objects[target])

    def damage(value: Any) -> bool:
        if hasattr(value, "__dataclass_fields__"):
            if canonical_json_bytes(value) == needle:
                key = "packet_id" if target == "packet" else "artifact_id"
                object.__setattr__(value, key, "FORGED_ORIGINAL_ID")
                return True
            return any(damage(getattr(value, f.name)) for f in fields(value))
        return type(value) is tuple and any(damage(v) for v in value)

    assert damage(damaged)
    _reject(damaged, pc.ProductErrorCode.INVALID_PRODUCT_SOURCE)


def test_unknown_conflict_candidate_order_and_limitations_are_not_simplified() -> None:
    unknown, conflict = _view("unknown"), _view("conflict")
    assert any(s.state is SignalState.UNKNOWN for s in unknown.decision.signals.signals)
    assert any(f.status is FindingStatus.UNKNOWN for f in unknown.investigation.findings)
    assert conflict.investigation.conflicts
    for shape in ("baseline", "unknown", "conflict"):
        source, view = _source(shape), _view(shape)
        assert view.decision.recommendation.candidate_order == (
            source.packet.recommendation.candidate_order
        )
        assert view.decision.recommendation.disposition is source.packet.recommendation.disposition
        assert (
            view.decision.recommendation.reason_codes == source.packet.recommendation.reason_codes
        )
        assert view.decision.limitations == source.packet.limitations
        assert view.decision.uncertainties == source.packet.uncertainties
        assert view.investigation.uncertainty_register.items
        for finding, original in zip(view.investigation.findings, source.findings, strict=True):
            assert finding.status is original.status
        for record, original_conflict in zip(
            view.investigation.conflicts, source.conflicts, strict=True
        ):
            assert record.conflict_type is original_conflict.conflict_type


def test_two_human_planes_and_notes_never_become_evidence() -> None:
    source = _source("decision-review")
    view = _view("decision-review")
    assert type(view.decision.human_reviews[0].decision) is HumanDecisionType
    assert type(view.investigation.human_reviews[0].outcome) is HumanInvestigationOutcome
    assert view.decision.human_reviews[0].note_class == "HUMAN_NOTE_NON_EVIDENCE"
    assert view.investigation.human_reviews[0].note_class == "HUMAN_NOTE_NON_EVIDENCE"
    assert view.decision.human_reviews[0].comment == source.decision_events[0].comment
    assert len(view.decision.evidence.evidence) == len(source.packet.evidence.evidence)
    assert len(view.investigation.findings) == len(source.findings)
    assert all("C01_OPAQUE" not in section.text for section in view.investigation.summary.sections)


def test_direct_product_model_construction_rejects_cross_world_identity() -> None:
    view = _view()
    identity = _replace(view.identity, order_id="OTHER_ORDER")
    with pytest.raises(pc.ProductError) as caught:
        _replace(view, identity=identity)
    assert caught.value.code is pc.ProductErrorCode.SOURCE_IDENTITY_MISMATCH


def test_product_package_has_only_pure_allowlisted_imports_and_calls() -> None:
    allowed = {
        "__future__",
        "json",
        "dataclasses",
        "datetime",
        "decimal",
        "enum",
        "types",
        "typing",
        "flowlens.decision.contracts",
        "flowlens.decision.enums",
        "flowlens.decision.primitives",
        "flowlens.decision.serialization",
        "flowlens.decision.c06_validation",
        "flowlens.investigation.contracts",
        "flowlens.investigation.enums",
        "flowlens.investigation.c02_binding",
        "flowlens.investigation.c03_planning",
        "flowlens.investigation.c05_findings",
        "flowlens.investigation.c07_summary",
        "flowlens.product.contracts",
        "flowlens.product.projection",
    }
    for path in sorted((ROOT / "src/flowlens/product").glob("*.py")):
        module = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(module):
            if isinstance(node, ast.Import):
                assert all(n.name in allowed for n in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module in (
                    "flowlens.decision",
                    "flowlens.investigation",
                    "flowlens.product",
                ):
                    assert all(node.module + "." + n.name in allowed for n in node.names)
                else:
                    assert node.module in allowed
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    assert node.func.id not in {
                        "open",
                        "eval",
                        "exec",
                        "compile",
                        "__import__",
                        "input",
                    }
                elif isinstance(node.func, ast.Attribute):
                    assert node.func.attr not in {
                        "now",
                        "today",
                        "utcnow",
                        "read_text",
                        "read_bytes",
                        "write_text",
                        "write_bytes",
                        "getenv",
                        "connect",
                        "execute",
                        "generate",
                        "system",
                    }


def test_projection_executes_with_runtime_capabilities_denied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _source()
    expected = _view().to_json()

    def deny(*args: Any, **kwargs: Any) -> NoReturn:
        raise AssertionError("FORBIDDEN_PRODUCT_CAPABILITY")

    class DeniedEnvironment(dict[str, str]):
        __getitem__ = deny
        get = deny

    with monkeypatch.context() as patch:
        for obj, names in (
            (builtins, ("open", "input")),
            (io, ("open",)),
            (Path, ("open", "read_text", "read_bytes", "write_text", "write_bytes")),
            (socket, ("socket", "create_connection")),
            (os, ("getenv", "system", "urandom")),
            (random, ("random", "randint", "choice")),
            (secrets, ("token_hex", "token_bytes")),
            (time, ("time", "monotonic")),
        ):
            for name in names:
                patch.setattr(obj, name, deny)
        patch.setattr(os, "environ", DeniedEnvironment())
        actual = project_product_case(source).to_json()
    assert actual == expected


def test_schema_has_no_invented_probability_causality_action_or_hgt_fields() -> None:
    schema = pc.product_schema()
    definitions = cast(dict[str, Any], schema["$defs"])
    forbidden = {
        "delay_probability",
        "risk_score",
        "root_cause",
        "hgt",
        "hidden_ground_truth",
        "execute",
        "apply",
        "schedule",
        "purchase",
        "quality_release",
        "resolved",
    }
    assert not any(forbidden & set(v["properties"]) for v in definitions.values())
    view = _view()
    assert json.loads(view.to_json())["capability_boundary"] == {
        "mode": "OFFLINE_SHADOW",
        "human_authority_required": True,
        "operational_write": "FORBIDDEN",
        "runtime_hgt": "FORBIDDEN",
        "llm_decision_authority": "NONE",
        "llm_tool_authority": "NONE",
        "recommendation_execution": "FORBIDDEN",
    }
