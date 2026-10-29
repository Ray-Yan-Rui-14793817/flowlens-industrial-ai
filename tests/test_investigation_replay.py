"""W04-C08 R01-R46: frozen replay, presentation separation and protected proof."""

from __future__ import annotations

import ast
import builtins
import copy
import hashlib
import inspect
import io
import json
import os
import random
import secrets
import socket
import sqlite3
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import FrozenInstanceError, fields, replace
from datetime import timedelta
from enum import StrEnum
from functools import cache
from pathlib import Path
from typing import Any, NoReturn, cast

import pytest
from sqlalchemy.engine import Connection, Engine

from flowlens.decision.enums import TrustLevel
from flowlens.decision.serialization import canonical_json_bytes, sha256_hex
from flowlens.investigation import c04_navigation as navigation
from flowlens.investigation import c06_store as journal
from flowlens.investigation import c08_policy as policy
from flowlens.investigation import c08_replay as replay
from flowlens.investigation.c07_summary import render_investigation_summary
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
from flowlens.investigation.enums import (
    ConflictType,
    FindingStatus,
    SummaryRendererMode,
    UncertaintyType,
)
from test_c05_policy import unsafe_replace
from test_investigation_evidence_navigation import _Engine
from test_investigation_findings import _git, _observation, _parse_like, _process, _violations
from test_investigation_human import ReviewContext, _review_wire
from test_investigation_summary import (
    FROZEN_BLOBS,
    FakeProvider,
    _changed_section,
    _fixture,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/ci"))

import plan_non_integration_shards as planner  # noqa: E402
import pytest_outcome_receipt as outcomes  # noqa: E402
import verify_non_integration_shards as verifier  # noqa: E402

C08_SOURCES = (
    "src/flowlens/investigation/c08_policy.py",
    "src/flowlens/investigation/c08_replay.py",
)
C08_SOURCE_FREEZE_SHA = "1fa7b505980c1efc1b3725cd57a9732e254bccdf"
C08_SOURCE_BLOBS = {
    "src/flowlens/investigation/c08_policy.py": "273d288cf4b0e55b646cd2e6751f0259e463a5ff",
    "src/flowlens/investigation/c08_replay.py": "4fa391cf751377305315b7de8303ce94e6eb6c6e",
}
ENTRY_SHA = "9afc4bd047bd4e52dfc4956f16e6420b3762301f"
DEVCTRL_03_ENTRY_SHA = "a18e7f0733079ecc9aebdd94458625011e2f93f9"
C09_ENTRY_SHA = "1fa841f2ee0d6612774c9f0ced204289df86e7a1"
W04_C09_MANIFEST_CONTENT_SHA256 = "937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad"
LIMITATIONS = (
    "C08_FROZEN_ARTIFACT_REPLAY_ONLY",
    "C08_HUMAN_NOTE_NON_EVIDENCE",
    "C08_NO_EVIDENCE_REFRESH",
    "C08_NO_HGT_OR_CAUSAL_EVALUATION",
    "C08_NO_OPERATIONAL_AUTHORITY",
    "C08_PRESENTATION_NOT_AUTHORITY",
)


def _error(action: Callable[[], object], code: str) -> None:
    with pytest.raises(policy.C08ProtectedReplayError) as caught:
        action()
    assert caught.value.code == str(caught.value) == code
    assert caught.value.args == (code,)
    assert caught.value.__cause__ is None and caught.value.__suppress_context__


def _rehashed[T: _Artifact](value: T, **changes: Any) -> T:
    """Hostile but coherently hashed originals; never rely on a stale parent to reject them."""
    altered = unsafe_replace(value, **changes)
    digest = sha256_hex(altered.canonical_payload())
    return unsafe_replace(
        altered, content_hash=digest, artifact_id=_PREFIXES[altered._kind] + digest
    )


def _context_change(context: ReviewContext, index: int, value: Any) -> ReviewContext:
    changed: list[Any] = list(context)
    changed[index] = value
    return cast(ReviewContext, tuple(changed))


@cache
def _presentations(
    shape: str = "normal",
) -> tuple[InvestigationSummaryRecord, ...]:
    context, events, deterministic = _fixture(shape)
    return (
        deterministic,
        render_investigation_summary(
            *context, events, renderer_mode=SummaryRendererMode.DEGRADED_FALLBACK
        ),
        render_investigation_summary(
            *context,
            events,
            renderer_mode=SummaryRendererMode.BOUNDED_LLM,
            provider=FakeProvider(echo=True),
        ),
        render_investigation_summary(
            *context,
            events,
            renderer_mode=SummaryRendererMode.BOUNDED_LLM,
            provider=FakeProvider(echo=True, alternate=True),
        ),
    )


@cache
def _receipt(shape: str = "normal", presentation: int = 0) -> policy.InvestigationReplayReceipt:
    context, events, deterministic = _fixture(shape)
    summary = deterministic if presentation == 0 else _presentations(shape)[presentation]
    return replay.replay_investigation(*context, events, summary)


def test_r01_r10_original_chain_uses_frozen_validators_in_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, events, presented = _fixture("conflict")
    visited: list[str] = []

    def tracked(name: str, label: str) -> Callable[..., Any]:
        original = getattr(replay, name)

        def check(*args: Any, **kwargs: Any) -> Any:
            visited.append(label)
            if label == "render":
                assert kwargs == {
                    "renderer_mode": SummaryRendererMode.DETERMINISTIC,
                    "provider": None,
                }
            if label == "human":
                position = visited.count("human") - 1
                assert args[:9] == context
                assert args[-2:] == (events[position], events[position - 1] if position else None)
            return original(*args, **kwargs)

        return check

    for name, label in (
        ("build_investigation_case", "packet"),
        ("validate_investigation_case_binding", "case"),
        ("validate_investigation_planning", "planning"),
        ("validate_evidence_query_specs", "queries"),
        ("derive_findings_conflicts_uncertainty", "evidence"),
        ("validate_findings_conflicts_uncertainty", "findings"),
        ("validate_human_investigation_event", "human"),
        ("validate_investigation_summary", "summary"),
        ("render_investigation_summary", "render"),
    ):
        monkeypatch.setattr(replay, name, tracked(name, label))
    receipt = replay.replay_investigation(*context, events, presented)
    assert visited == [
        "packet",
        "case",
        "planning",
        "queries",
        "evidence",
        "findings",
        "human",
        "human",
        "summary",
        "render",
    ]
    assert receipt.authoritative_summary_id == presented.artifact_id
    assert all(o.available_at <= context[1].as_of_time for s in context[5] for o in s.observations)
    assert all(o.provenance_ref.startswith("c04prov_") for s in context[5] for o in s.observations)


def test_r11_r16_receipt_versions_source_core_id_and_full_hash() -> None:
    context, events, deterministic = _fixture()
    receipt = _receipt()
    source = dict(
        zip(
            (
                "packet",
                "case",
                "questions",
                "plan",
                "queries",
                "slices",
                "findings",
                "conflicts",
                "uncertainty_register",
            ),
            context,
            strict=True,
        )
    ) | {"human_events": events}
    assert receipt.schema_version == "w04-c08-replay-receipt-v1"
    assert receipt.replay_contract_version == "w04-c08-protected-replay-v1"
    assert receipt.limitation_codes == policy.C08_LIMITATION_CODES == LIMITATIONS
    assert receipt.source_chain_sha256 == sha256_hex(source)
    core = {
        "replay_contract_version": receipt.replay_contract_version,
        "source_chain_sha256": receipt.source_chain_sha256,
        "authoritative_summary_id": deterministic.artifact_id,
        "authoritative_summary_content_hash": deterministic.content_hash,
        "limitation_codes": LIMITATIONS,
    }
    assert receipt.replay_core_sha256 == sha256_hex(core)
    assert receipt.replay_id == "ireplay_" + sha256_hex(core)
    metadata = {
        f.name: getattr(receipt, f.name) for f in fields(receipt) if f.name != "receipt_sha256"
    }
    assert receipt.receipt_sha256 == sha256_hex(metadata)
    assert receipt.presented_summary_id == deterministic.artifact_id
    assert receipt.presented_summary_content_hash == deterministic.content_hash


def test_r17_r19_metadata_only_immutable_receipt_preserves_exact_orders() -> None:
    context, events, _ = _fixture("conflict")
    receipt = _receipt("conflict")
    assert receipt.packet_id == context[0].packet_id and receipt.case_id == context[1].artifact_id
    assert receipt.plan_id == context[3].artifact_id
    for name, values in (
        ("question_ids", context[2]),
        ("query_ids", context[4]),
        ("evidence_slice_ids", context[5]),
        ("finding_ids", context[6]),
        ("conflict_ids", context[7]),
        ("human_event_ids", events),
    ):
        assert getattr(receipt, name) == tuple(item.artifact_id for item in values)
    assert receipt.uncertainty_register_id == context[8].artifact_id
    expected = {
        "schema_version",
        "replay_contract_version",
        "replay_id",
        "replay_core_sha256",
        "source_chain_sha256",
        "packet_id",
        "case_id",
        "question_ids",
        "plan_id",
        "query_ids",
        "evidence_slice_ids",
        "finding_ids",
        "conflict_ids",
        "uncertainty_register_id",
        "human_event_ids",
        "authoritative_summary_id",
        "authoritative_summary_content_hash",
        "presented_summary_id",
        "presented_summary_content_hash",
        "presented_renderer_mode",
        "limitation_codes",
        "receipt_sha256",
    }
    assert {f.name for f in fields(receipt)} == expected
    assert all(not f.init for f in fields(receipt))
    assert not hasattr(receipt, "__dict__")
    for event in events:
        assert event.note_text and event.note_text not in receipt.to_json()
    with pytest.raises(FrozenInstanceError):
        cast(Any, receipt).source_chain_sha256 = "tampered"
    with pytest.raises(TypeError):
        cast(Any, policy.InvestigationReplayReceipt)(replay_id=receipt.replay_id)
    _error(policy.InvestigationReplayReceipt, policy.C08_REPLAY_RECEIPT_MISMATCH)


@pytest.mark.parametrize("field", [f.name for f in fields(policy.InvestigationReplayReceipt)])
def test_r20_receipt_original_claims_must_recompute_exactly(field: str) -> None:
    context, events, presented = _fixture("conflict")
    receipt = _receipt("conflict")
    value = getattr(receipt, field)
    replacement: Any = (
        tuple(reversed(value)) + ("tampered",)
        if type(value) is tuple
        else SummaryRendererMode.DEGRADED_FALLBACK
        if field == "presented_renderer_mode"
        else "tampered"
    )
    bad = unsafe_replace(receipt, **{field: replacement})
    # A caller recomputing the outer receipt hash cannot legitimize changed replay claims.
    if field != "receipt_sha256":
        bad = unsafe_replace(
            bad,
            receipt_sha256=sha256_hex(
                {f.name: getattr(bad, f.name) for f in fields(bad) if f.name != "receipt_sha256"}
            ),
        )
    _error(
        lambda: replay.validate_investigation_replay(*context, events, presented, bad),
        policy.C08_REPLAY_RECEIPT_MISMATCH,
    )


def test_r20_coherent_presentation_claim_still_recomputes_supplied_chain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, events, deterministic = _fixture()
    other = _receipt("normal", 3)
    original = replay.replay_investigation
    calls: list[tuple[Any, ...]] = []

    def tracked(*args: Any) -> policy.InvestigationReplayReceipt:
        calls.append(args)
        return original(*args)

    monkeypatch.setattr(replay, "replay_investigation", tracked)
    _error(
        lambda: replay.validate_investigation_replay(*context, events, deterministic, other),
        policy.C08_REPLAY_RECEIPT_MISMATCH,
    )
    assert calls == [(*context, events, deterministic)]


@pytest.mark.parametrize("shape", ["normal", "unknown", "conflict", "empty"])
def test_r21_r25_valid_modes_and_wording_share_deterministic_authority_without_provider(
    shape: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, events, deterministic = _fixture(shape)
    presentations = _presentations(shape)

    def denied(*args: Any, **kwargs: Any) -> NoReturn:
        raise AssertionError("C08 called a provider")

    with monkeypatch.context() as trap:
        trap.setattr(FakeProvider, "generate", denied)
        receipts = [replay.replay_investigation(*context, events, value) for value in presentations]
        for value, receipt in zip(presentations, receipts, strict=True):
            replay.validate_investigation_replay(*context, events, value, receipt)
    assert [r.presented_renderer_mode for r in receipts] == [
        SummaryRendererMode.DETERMINISTIC,
        SummaryRendererMode.DEGRADED_FALLBACK,
        SummaryRendererMode.BOUNDED_LLM,
        SummaryRendererMode.BOUNDED_LLM,
    ]
    assert (
        len({r.replay_id for r in receipts}) == len({r.replay_core_sha256 for r in receipts}) == 1
    )
    assert len({r.source_chain_sha256 for r in receipts}) == 1
    assert len({r.receipt_sha256 for r in receipts}) == 4
    assert all(r.authoritative_summary_id == deterministic.artifact_id for r in receipts)
    assert all(r.authoritative_summary_content_hash == deterministic.content_hash for r in receipts)
    assert presentations[2].sections[0].text != presentations[3].sections[0].text
    assert all(p.sections[5] == deterministic.sections[5] for p in presentations)


@pytest.mark.parametrize("shape", ["unknown", "conflict"])
def test_r26_presentation_never_upgrades_findings_or_uncertainty(shape: str) -> None:
    context, events, baseline = _fixture(shape)
    before = canonical_json_bytes((context, events))
    for presented in _presentations(shape):
        receipt = _receipt(shape, _presentations(shape).index(presented))
        assert receipt.authoritative_summary_id == baseline.artifact_id
        assert (
            presented.finding_ids,
            presented.conflict_ids,
            presented.uncertainty_register_id,
            presented.human_event_ids,
        ) == (
            baseline.finding_ids,
            baseline.conflict_ids,
            baseline.uncertainty_register_id,
            baseline.human_event_ids,
        )
    assert canonical_json_bytes((context, events)) == before
    assert any(f.status in {FindingStatus.UNKNOWN, FindingStatus.UNRESOLVED} for f in context[6])
    assert any(i.uncertainty_type is UncertaintyType.FORBIDDEN_INFERENCE for i in context[8].items)


@pytest.mark.parametrize("damage", ["identity", "nested", "provenance", "future"])
def test_r27_invalid_original_packet_is_rejected(damage: str) -> None:
    context, events, summary = _fixture()
    packet = context[0]
    if damage == "identity":
        packet = unsafe_replace(packet, packet_id="pkt_" + "f" * 64)
    elif damage == "nested":
        packet = unsafe_replace(packet, run=unsafe_replace(packet.run, run_id="run_" + "f" * 64))
    elif damage == "provenance":
        packet = unsafe_replace(
            packet, provenance=replace(packet.provenance, producer="UNAUTHORIZED_PRODUCER")
        )
    else:
        entry = packet.snapshot.entries[0]
        entry = unsafe_replace(entry, available_at=packet.run.as_of_time + timedelta(days=1))
        packet = unsafe_replace(
            packet,
            snapshot=unsafe_replace(packet.snapshot, entries=(entry, *packet.snapshot.entries[1:])),
        )
    _error(
        lambda: replay.replay_investigation(packet, *context[1:], events, summary),
        policy.C08_INVALID_REPLAY_CONTEXT,
    )


@pytest.mark.parametrize("damage", ["identity", "subject", "opened_at", "packet_hash"])
def test_r28_original_case_identity_and_exact_projection(damage: str) -> None:
    context, events, summary = _fixture()
    case = context[1]
    if damage == "identity":
        case = unsafe_replace(case, content_hash="f" * 64)
    else:
        variants: dict[str, dict[str, Any]] = {
            "subject": {"subject_id": "different-order"},
            "opened_at": {"opened_at": case.opened_at + timedelta(hours=1)},
            "packet_hash": {"source_decision_packet_hash": "f" * 64},
        }
        case = replace(case, **variants[damage])
    _error(
        lambda: replay.replay_investigation(*_context_change(context, 1, case), events, summary),
        policy.C08_CASE_REPLAY_MISMATCH,
    )


@pytest.mark.parametrize(
    "damage",
    [
        "question_identity",
        "question_order",
        "question_scope",
        "plan_identity",
        "step_identity",
        "step_order",
        "dependency",
        "version",
    ],
)
def test_r29_questions_plan_and_nested_original_dependencies(damage: str) -> None:
    context, events, summary = _fixture()
    questions, plan = context[2], context[3]
    if damage == "question_identity":
        questions = (unsafe_replace(questions[0], artifact_id="tampered"), *questions[1:])
    elif damage == "question_order":
        questions = tuple(reversed(questions))
    elif damage == "question_scope":
        questions = (
            replace(questions[0], allowed_traversal_families=("OTHER_FAMILY",)),
            *questions[1:],
        )
    elif damage == "plan_identity":
        plan = unsafe_replace(plan, artifact_id="tampered")
    elif damage == "step_identity":
        plan = unsafe_replace(
            plan, steps=(unsafe_replace(plan.steps[0], content_hash="f" * 64), *plan.steps[1:])
        )
    elif damage == "step_order":
        plan = _rehashed(plan, steps=tuple(reversed(plan.steps)))
    elif damage == "dependency":
        step = replace(plan.steps[1], depends_on_step_ids=(plan.steps[0].artifact_id,))
        plan = replace(plan, steps=(plan.steps[0], step, *plan.steps[2:]))
    else:
        plan = replace(plan, planner_contract_version="unauthorized-version")
    changed: ReviewContext = (*context[:2], questions, plan, *context[4:])
    _error(
        lambda: replay.replay_investigation(*changed, events, summary),
        policy.C08_PLANNING_REPLAY_MISMATCH,
    )


@pytest.mark.parametrize(
    "damage", ["identity", "order", "entity_identity", "entity_value", "fields", "relationship"]
)
def test_r30_exact_query_order_keys_and_registry_projection(damage: str) -> None:
    context, events, summary = _fixture()
    queries, query = context[4], context[4][0]
    if damage == "identity":
        query = unsafe_replace(query, artifact_id="tampered")
    elif damage == "order":
        queries = tuple(reversed(queries))
    elif damage == "entity_identity":
        query = unsafe_replace(
            query,
            entity_keys=(
                unsafe_replace(query.entity_keys[0], content_hash="f" * 64),
                *query.entity_keys[1:],
            ),
        )
    elif damage == "entity_value":
        query = replace(
            query,
            entity_keys=(
                replace(query.entity_keys[0], key_value="different-key"),
                *query.entity_keys[1:],
            ),
        )
    elif damage == "fields":
        query = replace(query, requested_fields=tuple(sorted((*query.requested_fields, "other"))))
    else:
        query = replace(query, expected_relationship_code="OTHER_RELATIONSHIP")
    if damage != "order":
        queries = (query, *queries[1:])
    _error(
        lambda: replay.replay_investigation(*_context_change(context, 4, queries), events, summary),
        policy.C08_QUERY_REPLAY_MISMATCH,
    )


@pytest.mark.parametrize(
    "damage",
    [
        "slice_identity",
        "query_binding",
        "order",
        "observation_identity",
        "provenance",
        "future_available",
        "future_event",
        "forbidden_trust",
        "family",
        "requested_field",
    ],
)
def test_r31_captured_evidence_binding_provenance_trust_and_future_time(damage: str) -> None:
    context, events, summary = _fixture()
    slices = context[5]
    slice_index = next(i for i, s in enumerate(slices) if s.observations)
    original = slices[slice_index]
    observation = original.observations[0]
    if damage == "slice_identity":
        altered = unsafe_replace(original, artifact_id="tampered")
    elif damage == "query_binding":
        altered = replace(original, query_id="eqry_" + "f" * 64)
    elif damage == "order":
        slices = tuple(reversed(slices))
        altered = original
    else:
        if damage == "observation_identity":
            observation = unsafe_replace(observation, content_hash="f" * 64)
        elif damage == "provenance":
            observation = replace(observation, provenance_ref="c04prov_" + "f" * 64)
        elif damage in {"future_available", "future_event"}:
            query = context[4][slice_index]
            future = context[1].as_of_time + timedelta(days=1)
            observation = _observation(
                context[0],
                query,
                observation.source_record_id,
                observation.source_field,
                observation.source_value,
                observation.freshness_code,
                available=future if damage == "future_available" else observation.available_at,
                event=future if damage == "future_event" else observation.event_time,
            )
        elif damage == "forbidden_trust":
            observation = replace(observation, trust_class=TrustLevel.FORBIDDEN_INFERENCE)
        elif damage == "family":
            observation = replace(observation, source_family_code="OTHER_FAMILY")
        else:
            observation = replace(observation, source_field="unauthorized_field")
        observations = tuple(
            sorted((observation, *original.observations[1:]), key=lambda o: o.artifact_id)
        )
        altered = _rehashed(original, observations=observations)
    if damage != "order":
        slices = (*slices[:slice_index], altered, *slices[slice_index + 1 :])
    _error(
        lambda: replay.replay_investigation(*_context_change(context, 5, slices), events, summary),
        policy.C08_EVIDENCE_REPLAY_MISMATCH,
    )


@pytest.mark.parametrize(
    "damage",
    [
        "finding_identity",
        "finding_order",
        "status_upgrade",
        "finding_ref",
        "conflict_identity",
        "conflict_type",
        "register_identity",
        "item_identity",
        "uncertainty_type",
        "uncertainty_ref",
    ],
)
def test_r32_findings_conflicts_and_nested_uncertainty_are_rederived(damage: str) -> None:
    context, events, summary = _fixture("conflict")
    findings, conflicts, register = context[6:]
    if damage == "finding_identity":
        findings = (unsafe_replace(findings[0], artifact_id="tampered"), *findings[1:])
    elif damage == "finding_order":
        findings = tuple(reversed(findings))
    elif damage == "status_upgrade":
        index = next(i for i, f in enumerate(findings) if f.status is FindingStatus.UNKNOWN)
        altered = _rehashed(
            findings[index],
            status=FindingStatus.SUPPORTED,
            supporting_evidence_ids=(
                next(o for s in context[5] for o in s.observations).artifact_id,
            ),
        )
        findings = (*findings[:index], altered, *findings[index + 1 :])
    elif damage == "finding_ref":
        findings = (
            _rehashed(findings[0], supporting_evidence_ids=("eobs_" + "f" * 64,)),
            *findings[1:],
        )
    elif damage == "conflict_identity":
        conflicts = (unsafe_replace(conflicts[0], content_hash="f" * 64), *conflicts[1:])
    elif damage == "conflict_type":
        conflicts = (
            _rehashed(conflicts[0], conflict_type=ConflictType.TIMESTAMP_CONFLICT),
            *conflicts[1:],
        )
    elif damage == "register_identity":
        register = unsafe_replace(register, artifact_id="tampered")
    elif damage == "item_identity":
        register = unsafe_replace(
            register,
            items=(unsafe_replace(register.items[0], artifact_id="tampered"), *register.items[1:]),
        )
    else:
        item = (
            _rehashed(
                register.items[0],
                uncertainty_type=next(
                    kind
                    for kind in UncertaintyType
                    if kind is not register.items[0].uncertainty_type
                ),
            )
            if damage == "uncertainty_type"
            else replace(register.items[0], related_refs=("unscoped_reference",))
        )
        register = replace(
            register, items=tuple(sorted((item, *register.items[1:]), key=lambda i: i.artifact_id))
        )
    altered_context: ReviewContext = (*context[:6], findings, conflicts, register)
    _error(
        lambda: replay.replay_investigation(*altered_context, events, summary),
        policy.C08_FINDINGS_REPLAY_MISMATCH,
    )


@pytest.mark.parametrize(
    "damage",
    [
        "empty",
        "identity",
        "reverse",
        "duplicate",
        "missing_parent",
        "parent",
        "time",
        "references",
        "complete_coverage",
        "note_authority",
    ],
)
def test_r09_r33_nonempty_exact_order_human_chain_and_opaque_note_authority(damage: str) -> None:
    context, events, summary = _fixture("conflict")
    if damage == "empty":
        events = ()
    elif damage == "identity":
        events = (unsafe_replace(events[0], artifact_id="tampered"), events[1])
    elif damage == "reverse":
        events = tuple(reversed(events))
    elif damage == "duplicate":
        events = (*events, events[-1])
    elif damage == "missing_parent":
        events = (events[1],)
    else:
        tail = events[-1]
        variants: dict[str, dict[str, Any]] = {
            "parent": {"previous_event_id": "hievt_" + "f" * 64},
            "time": {"occurred_at": events[0].occurred_at - timedelta(hours=1)},
            "references": {"reviewed_finding_ids": ("ifind_" + "f" * 64,)},
            "complete_coverage": {"reviewed_finding_ids": ()},
            "note_authority": {"note_class": "EVIDENCE"},
        }
        events = (events[0], _rehashed(tail, **variants[damage]))
    _error(
        lambda: replay.replay_investigation(*context, events, summary),
        policy.C08_INVALID_REPLAY_CONTEXT
        if damage == "empty"
        else policy.C08_HUMAN_CHAIN_REPLAY_MISMATCH,
    )


@pytest.mark.parametrize(
    "damage",
    [
        "identity",
        "section_identity",
        "references",
        "grounding",
        "order",
        "missing",
        "mode",
        "text",
        "authority",
        "version",
    ],
)
def test_r10_r34_original_summary_and_coherently_rehashed_presentation_tamper(damage: str) -> None:
    context, events, summary = _fixture("conflict")
    if damage == "identity":
        summary = unsafe_replace(summary, artifact_id="tampered")
    elif damage == "section_identity":
        summary = unsafe_replace(
            summary,
            sections=(
                unsafe_replace(summary.sections[0], content_hash="f" * 64),
                *summary.sections[1:],
            ),
        )
    elif damage == "references":
        summary = replace(summary, finding_ids=("ifind_" + "f" * 64,))
    elif damage == "grounding":
        summary = _changed_section(summary, 0, grounding_refs=("ifind_" + "f" * 64,))
    elif damage == "order":
        summary = replace(summary, sections=tuple(reversed(summary.sections)))
    elif damage == "missing":
        summary = replace(summary, sections=summary.sections[:-1])
    elif damage == "mode":
        summary = _changed_section(summary, 0, renderer_mode=SummaryRendererMode.BOUNDED_LLM)
    elif damage in {"text", "authority"}:
        summary = _changed_section(
            summary, 5 if damage == "authority" else 1, text="SECRET HGT invents causal authority"
        )
    else:
        summary = replace(summary, summary_contract_version="unauthorized-summary-version")
    _error(
        lambda: replay.replay_investigation(*context, events, summary),
        policy.C08_SUMMARY_REPLAY_MISMATCH,
    )


def _extended(value: Any) -> Any:
    extended: Any = object.__new__(type("ExtendedValue", (type(value),), {}))
    for field in fields(value):
        object.__setattr__(extended, field.name, getattr(value, field.name))
    return extended


@pytest.mark.parametrize(
    "damage",
    [
        "packet_subclass",
        "case_subclass",
        "question_tuple",
        "question_list",
        "step_subclass",
        "query_key_subclass",
        "observations_list",
        "observation_subclass",
        "human_tuple",
        "human_foreign_enum",
        "summary_subclass",
        "section_subclass",
        "renderer_string",
        "receipt_subclass",
        "receipt_list",
        "receipt_foreign_enum",
    ],
)
def test_r35_exact_envelope_rejects_subclasses_mutable_collections_and_foreign_enums(
    damage: str,
) -> None:
    context, events, summary = _fixture("conflict")
    invalid: list[Any] = list(context)
    receipt: Any = _receipt("conflict")
    code = policy.C08_INVALID_REPLAY_CONTEXT

    class ForeignOutcome(StrEnum):
        DEFER = "DEFER"

    class ForeignRenderer(StrEnum):
        DETERMINISTIC = "DETERMINISTIC"

    if damage == "packet_subclass":
        invalid[0] = _extended(context[0])
    elif damage == "case_subclass":
        invalid[1] = _extended(context[1])
    elif damage in {"question_tuple", "question_list"}:
        invalid[2] = (
            type("ExtendedTuple", (tuple,), {})(context[2])
            if damage == "question_tuple"
            else list(context[2])
        )
    elif damage == "step_subclass":
        invalid[3] = unsafe_replace(
            context[3], steps=(_extended(context[3].steps[0]), *context[3].steps[1:])
        )
    elif damage == "query_key_subclass":
        query = context[4][0]
        invalid[4] = (
            unsafe_replace(query, entity_keys=(_extended(query.entity_keys[0]),)),
            *context[4][1:],
        )
    elif damage in {"observations_list", "observation_subclass"}:
        index = next(i for i, s in enumerate(context[5]) if s.observations)
        original = context[5][index]
        values = (
            list(original.observations)
            if damage == "observations_list"
            else (_extended(original.observations[0]), *original.observations[1:])
        )
        invalid[5] = (
            *context[5][:index],
            unsafe_replace(original, observations=values),
            *context[5][index + 1 :],
        )
    elif damage == "human_tuple":
        events = cast(Any, type("ExtendedTuple", (tuple,), {})(events))
    elif damage == "human_foreign_enum":
        events = (unsafe_replace(events[0], outcome=ForeignOutcome.DEFER), events[1])
    elif damage == "summary_subclass":
        summary = _extended(summary)
    elif damage == "section_subclass":
        summary = unsafe_replace(
            summary, sections=(_extended(summary.sections[0]), *summary.sections[1:])
        )
    elif damage == "renderer_string":
        summary = unsafe_replace(
            summary,
            sections=(
                unsafe_replace(summary.sections[0], renderer_mode="DETERMINISTIC"),
                *summary.sections[1:],
            ),
        )
    elif damage == "receipt_subclass":
        receipt = _extended(receipt)
    elif damage == "receipt_list":
        receipt = unsafe_replace(receipt, human_event_ids=list(receipt.human_event_ids))
    else:
        receipt = unsafe_replace(receipt, presented_renderer_mode=ForeignRenderer.DETERMINISTIC)
    if damage.startswith("receipt_"):
        code = policy.C08_REPLAY_RECEIPT_MISMATCH
        _error(
            lambda: replay.validate_investigation_replay(*context, events, summary, receipt), code
        )
    else:
        changed = cast(ReviewContext, tuple(invalid))
        _error(lambda: replay.replay_investigation(*changed, events, summary), code)


@pytest.mark.parametrize(
    "target,code",
    [
        ("build_investigation_case", policy.C08_INVALID_REPLAY_CONTEXT),
        ("validate_investigation_case_binding", policy.C08_CASE_REPLAY_MISMATCH),
        ("validate_investigation_planning", policy.C08_PLANNING_REPLAY_MISMATCH),
        ("validate_evidence_query_specs", policy.C08_QUERY_REPLAY_MISMATCH),
        ("derive_findings_conflicts_uncertainty", policy.C08_EVIDENCE_REPLAY_MISMATCH),
        ("validate_findings_conflicts_uncertainty", policy.C08_FINDINGS_REPLAY_MISMATCH),
        ("validate_human_investigation_event", policy.C08_HUMAN_CHAIN_REPLAY_MISMATCH),
        ("validate_investigation_summary", policy.C08_SUMMARY_REPLAY_MISMATCH),
        ("render_investigation_summary", policy.C08_SUMMARY_REPLAY_MISMATCH),
        ("_receipt", policy.C08_REPLAY_RECEIPT_MISMATCH),
    ],
)
def test_r36_every_public_stage_failure_suppresses_protected_upstream_text(
    target: str,
    code: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, events, summary = _fixture()

    def failed(*args: Any, **kwargs: Any) -> NoReturn:
        raise RuntimeError("SECRET sql=SELECT * Human note provider output environment value")

    monkeypatch.setattr(replay, target, failed)
    _error(lambda: replay.replay_investigation(*context, events, summary), code)
    with pytest.raises(ValueError, match="unknown C08 error code"):
        policy.C08ProtectedReplayError("SECRET invented error")
    assert policy.C08_ERROR_CODES == frozenset(
        {
            "C08_INVALID_REPLAY_CONTEXT",
            "C08_CASE_REPLAY_MISMATCH",
            "C08_PLANNING_REPLAY_MISMATCH",
            "C08_QUERY_REPLAY_MISMATCH",
            "C08_EVIDENCE_REPLAY_MISMATCH",
            "C08_FINDINGS_REPLAY_MISMATCH",
            "C08_HUMAN_CHAIN_REPLAY_MISMATCH",
            "C08_SUMMARY_REPLAY_MISMATCH",
            "C08_REPLAY_RECEIPT_MISMATCH",
        }
    )


@pytest.mark.parametrize("damage", ["case", "step", "entity", "summary"])
def test_r02_r05_r10_nested_original_identity_precedes_frozen_reconstruction(
    damage: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, events, summary = _fixture()
    calls: list[str] = []

    def should_not_reconstruct(*args: Any, **kwargs: Any) -> NoReturn:
        calls.append("reconstructed")
        raise AssertionError("original identity was not checked first")

    if damage == "case":
        context = _context_change(context, 1, unsafe_replace(context[1], artifact_id="tampered"))
        target, code = "validate_investigation_case_binding", policy.C08_CASE_REPLAY_MISMATCH
    elif damage == "step":
        context = _context_change(
            context,
            3,
            unsafe_replace(
                context[3],
                steps=(
                    unsafe_replace(context[3].steps[0], artifact_id="tampered"),
                    *context[3].steps[1:],
                ),
            ),
        )
        target, code = "validate_investigation_planning", policy.C08_PLANNING_REPLAY_MISMATCH
    elif damage == "entity":
        query = context[4][0]
        context = _context_change(
            context,
            4,
            (
                unsafe_replace(
                    query,
                    entity_keys=(unsafe_replace(query.entity_keys[0], artifact_id="tampered"),),
                ),
                *context[4][1:],
            ),
        )
        target, code = "validate_evidence_query_specs", policy.C08_QUERY_REPLAY_MISMATCH
    else:
        summary = unsafe_replace(
            summary,
            sections=(
                unsafe_replace(summary.sections[0], artifact_id="tampered"),
                *summary.sections[1:],
            ),
        )
        target, code = "validate_investigation_summary", policy.C08_SUMMARY_REPLAY_MISMATCH
    monkeypatch.setattr(replay, target, should_not_reconstruct)
    _error(lambda: replay.replay_investigation(*context, events, summary), code)
    assert not calls


def test_r37_r39_same_process_bytes_and_all_inputs_unchanged() -> None:
    context, events, summary = _fixture("conflict")
    before = canonical_json_bytes((context, events, summary))
    first = replay.replay_investigation(*context, events, summary)
    second = replay.replay_investigation(*context, events, summary)
    assert first.to_json().encode("utf-8") == canonical_json_bytes(second)
    replay.validate_investigation_replay(*context, events, summary, first)
    assert canonical_json_bytes((context, events, summary)) == before


def _fresh_replay() -> None:
    """Reparse actual input wire bytes in a fresh interpreter, rather than rebuild the chain."""
    payload = json.loads(sys.stdin.read())
    packet = _parse_like(json.loads(payload["packet"]), _fixture()[0][0])
    context: ReviewContext = (
        packet,
        InvestigationCase.from_json(payload["case"]),
        tuple(InvestigationQuestion.from_json(q) for q in payload["questions"]),
        InvestigationPlan.from_json(payload["plan"]),
        tuple(EvidenceQuerySpec.from_json(q) for q in payload["queries"]),
        tuple(EvidenceSlice.from_json(s) for s in payload["slices"]),
        tuple(FindingRecord.from_json(f) for f in payload["findings"]),
        tuple(ConflictRecord.from_json(c) for c in payload["conflicts"]),
        UncertaintyRegister.from_json(payload["uncertainty_register"]),
    )
    events = tuple(HumanInvestigationEvent.from_json(e) for e in payload["human_events"])
    summary = InvestigationSummaryRecord.from_json(payload["summary"])
    assert canonical_json_bytes((context, events, summary)).hex() == payload["source_bytes_hex"]
    receipt = replay.replay_investigation(*context, events, summary)
    replay.validate_investigation_replay(*context, events, summary, receipt)
    print(canonical_json_bytes(receipt).hex())


@pytest.mark.parametrize("seed", ["0", "17", "917"])
def test_r38_actual_frozen_wire_replay_is_identical_across_fresh_hash_seeds(seed: str) -> None:
    context, events, summary = _fixture()
    payload = json.loads(_review_wire(context))
    payload.update(
        human_events=[e.to_json() for e in events],
        summary=summary.to_json(),
        source_bytes_hex=canonical_json_bytes((context, events, summary)).hex(),
    )
    actual = _process(
        "from test_investigation_replay import _fresh_replay; _fresh_replay()",
        seed=seed,
        stdin=json.dumps(payload),
    )
    assert actual == canonical_json_bytes(_receipt()).hex()


def _pure_violations(source: str) -> tuple[str, ...]:
    result = list(_violations(source))
    prohibited = (
        "flowlens.investigation.c06_store",
        "flowlens.investigation.c07_provider",
        "flowlens.evaluation",
        "flowlens.api",
        "flowlens.worker",
    )
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = (
                [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
            result.extend(
                name
                for name in names
                if any(name == p or name.startswith(p + ".") for p in prohibited)
            )
        if isinstance(node, ast.Attribute) and node.attr == "note_text":
            result.append("Human note interpretation")
    return tuple(result)


@pytest.mark.parametrize(
    "source",
    [
        "import sqlalchemy.orm",
        "from flowlens.db import models",
        "from flowlens.investigation.c04_navigation import execute_evidence_navigation",
        "import flowlens.data.scenarios.ground_truth",
        "import flowlens.evaluation",
        "import flowlens.api",
        "import flowlens.worker",
        "import flowlens.investigation.c06_store",
        "import flowlens.investigation.c07_provider",
        "from openai import OpenAI",
        "import httpx",
        "import requests",
        "import socket",
        "import subprocess",
        "import os; os.getenv('SECRET')",
        "import pathlib",
        "open('journal')",
        "import random",
        "import secrets",
        "from time import time",
        "from datetime import datetime; datetime.now()",
        "eval('x')",
        "exec('x')",
        "event.note_text",
    ],
)
def test_r40_r41_capability_audit_rejects_negative_controls(source: str) -> None:
    assert _pure_violations(source)


def test_r40_r41_runtime_ast_public_signature_and_fresh_import_are_protected() -> None:
    for source in C08_SOURCES:
        assert not _pure_violations((ROOT / source).read_text(encoding="utf-8"))
    arguments = (
        "packet",
        "case",
        "questions",
        "plan",
        "queries",
        "slices",
        "findings",
        "conflicts",
        "uncertainty_register",
        "human_events",
        "summary",
    )
    assert tuple(inspect.signature(replay.replay_investigation).parameters) == arguments
    assert tuple(inspect.signature(replay.validate_investigation_replay).parameters) == (
        *arguments,
        "receipt",
    )
    assert (
        _process(
            # Frozen ZoneInfo's Windows tzdata loader imports stdlib random, without replay use.
            "import sys; import flowlens.investigation.c07_summary; baseline=set(sys.modules); "
            "import flowlens.investigation.c08_replay; "
            "blocked=('sqlalchemy','psycopg','flowlens.db','flowlens.data','flowlens.evaluation',"
            "'flowlens.api','flowlens.worker','flowlens.investigation.c04_navigation',"
            "'flowlens.investigation.c06_store','flowlens.investigation.c07_provider',"
            "'openai','httpx','requests','socket','subprocess','random','secrets'); "
            "assert not any(n==p or n.startswith(p+'.') "
            "for n in set(sys.modules)-baseline for p in blocked); "
            "assert not any(n==p or n.startswith(p+'.') "
            "for n in sys.modules for p in blocked if p != 'random'); "
            "print('PURE')"
        )
        == "PURE"
    )


def test_r39_r40_r42_live_external_traps_no_refresh_or_operational_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, events, _ = _fixture("conflict")
    supplied = _presentations("conflict")[3]
    before = canonical_json_bytes((context, events, supplied))
    expected = _receipt("conflict", 3)
    touched: list[str] = []
    current_database = {"current_version": "changed-after-capture"}

    def denied(*args: Any, **kwargs: Any) -> NoReturn:
        touched.append("unauthorized")
        raise AssertionError("C08 tried external capability or operational write")

    with monkeypatch.context() as traps:
        for owner, name in (
            (builtins, "open"),
            (io, "open"),
            (Path, "read_text"),
            (Path, "read_bytes"),
            (Path, "write_text"),
            (Path, "write_bytes"),
            (Path, "open"),
            (subprocess, "run"),
            (subprocess, "Popen"),
            (socket, "socket"),
            (socket, "create_connection"),
            (sqlite3, "connect"),
            (os, "getenv"),
            (os, "system"),
            (type(os.environ), "get"),
            (random, "random"),
            (random, "getrandbits"),
            (secrets, "token_hex"),
            (time, "time"),
            (navigation, "execute_evidence_navigation"),
            (_Engine, "connect"),
            (Engine, "connect"),
            (Connection, "execute"),
            (Connection, "commit"),
            (journal.HumanInvestigationJournal, "load"),
            (journal.HumanInvestigationJournal, "record"),
            (FakeProvider, "generate"),
        ):
            traps.setattr(owner, name, denied)
        first = replay.replay_investigation(*context, events, supplied)
        current_database["current_version"] = "changed-again-after-capture"
        second = replay.replay_investigation(*context, events, supplied)
        replay.validate_investigation_replay(*context, events, supplied, first)
        assert (
            canonical_json_bytes(first)
            == canonical_json_bytes(second)
            == canonical_json_bytes(expected)
        )
        assert canonical_json_bytes((context, events, supplied)) == before
    assert not touched and current_database["current_version"] == "changed-again-after-capture"


def _devctrl03_workflow_delta_guard() -> None:
    """Historical bytes remain anchored; current workflow has successor obligations."""
    from verify_w05_successor_governance import (
        verify_anchor,
        verify_docs,
        verify_protected_material,
        verify_surfaces,
    )

    verify_anchor(ROOT)
    verify_docs(ROOT)
    verify_surfaces(ROOT)
    verify_protected_material(ROOT)
    historical = _git("show", planner.HISTORICAL_ANCHOR + ":.github/workflows/ci.yml")
    assert "verify_w04_investigation_gate_contract.py" in historical
    current = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "W05 successor governance" in current
    assert "W05_RESULT" in current
    assert "Replay historical W04 governance at exact anchor" in current

def test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged() -> None:
    manifest = json.loads((ROOT / "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json").read_bytes())
    entry = json.loads(_git("show", ENTRY_SHA + ":docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json"))
    assert manifest["checkpoints"][:7] == entry["checkpoints"]
    assert [c["checkpoint"] for c in manifest["checkpoints"]] == [
        *(f"W04-C{i:02}" for i in range(1, 8)),
        "W04-C08",
    ]
    assert all(c["state"] == "CLOSED" for c in manifest["checkpoints"][:7])
    authorized = {
        "checkpoint": "W04-C08",
        "state": "AUTHORIZED",
        "source_freeze_sha": None,
        "files": [{"path": path, "blob_oid": None} for path in C08_SOURCES],
    }
    closed = {
        "checkpoint": "W04-C08",
        "state": "CLOSED",
        "source_freeze_sha": C08_SOURCE_FREEZE_SHA,
        "files": [{"path": path, "blob_oid": C08_SOURCE_BLOBS[path]} for path in C08_SOURCES],
    }
    c08 = manifest["checkpoints"][-1]
    assert c08 in (authorized, closed)
    for path, blob in C08_SOURCE_BLOBS.items():
        assert _git("rev-parse", "HEAD:" + path) == blob
        assert not _git("diff", "HEAD", "--", path)
        if c08["state"] == "CLOSED":
            assert _git("rev-parse", C08_SOURCE_FREEZE_SHA + ":" + path) == blob
    for checkpoint in manifest["checkpoints"][:7]:
        for file in checkpoint["files"]:
            assert _git("rev-parse", "HEAD:" + file["path"]) == file["blob_oid"]
            assert not _git("diff", "HEAD", "--", file["path"])
    for path, blob in FROZEN_BLOBS.items():
        assert _git("rev-parse", "HEAD:" + path) == blob
    for path in (
        "src/flowlens/decision",
        "src/flowlens/evaluation",
        "src/flowlens/data",
        "src/flowlens/db",
        "src/flowlens/api",
        "src/flowlens/worker",
        "migrations",
        "apps",
        "docs/w03",
        "pyproject.toml",
        "uv.lock",
        "docker-compose.yml",
        "scripts/ci/verify_w04_source_evolution.py",
        "tests/test_investigation_summary.py",
        "tests/test_investigation_summary_provider.py",
    ):
        assert _git("rev-parse", "HEAD:" + path) == _git("rev-parse", ENTRY_SHA + ":" + path)
        assert not _git("diff", "HEAD", "--", path)
    assert all(c["state"] == "CLOSED" for c in manifest["checkpoints"])
    assert hashlib.sha256(
        (ROOT / "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json").read_bytes()
    ).hexdigest() == ("d22a12306f8fe98952b9e35a5f166f29fee968c9aedcff27511da59889c20c2d")
    _devctrl03_workflow_delta_guard()


FULL_JOBS = frozenset(
    {
        "Classify change",
        "Static and plan",
        "Integration and data",
        *(f"Non-integration / shard {i}" for i in range(7)),
        "Non-integration aggregate",
        "Quality gate",
        "Docker Compose smoke",
        "W03 AI loop gate",
        "W04 investigation gate",
        "W05 successor governance",
        "Verification gate",
    }
)


def _validate_w04_c09_gate_summary(
    value: dict[str, Any], head: str, raw: bytes | None = None
) -> None:
    """Independently require the exact semantic payload, canonical seal and native bytes."""
    manifest_raw = (ROOT / "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json").read_bytes()
    assert hashlib.sha256(manifest_raw).hexdigest() == (
        "d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1"
    )
    manifest = json.loads(manifest_raw)
    assert (
        hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        ).hexdigest()
        == W04_C09_MANIFEST_CONTENT_SHA256
    )
    payload = {
        "schema_version": "w04-c09-gate-summary-v1",
        "gate_version": "w04-c09-investigation-gate-v1",
        "implementation_sha": head,
        "manifest_sha256": "d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1",
        "manifest_content_sha256": W04_C09_MANIFEST_CONTENT_SHA256,
        "total_families": 9,
        "total_selectors": 67,
        "total_tests": 81,
        "families": [
            {
                "id": f["id"],
                "status": "PASS",
                "selectors": len(f["targets"]),
                "tests": f["expected_cases"],
            }
            for f in manifest["families"]
        ],
        "overall": "PASS",
    }
    expected = payload | {
        "summary_sha256": hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        ).hexdigest()
    }
    assert value == expected
    assert json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) == json.dumps(
        expected, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    if raw is not None:
        assert (
            raw
            == json.dumps(expected, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
            + b"\n"
        )


def _check_native_metadata(value: dict[str, Any], head: str) -> None:
    assert value["schema_version"] == "w04-c08-native-proof-v1"
    assert value["head_sha"] == value["run"]["head_sha"] == head
    assert value["run"]["status"] == "completed" and value["run"]["conclusion"] == "success"
    assert type(value["run"]["id"]) is int and value["run"]["id"] > 0
    names = [job["name"] for job in value["jobs"]]
    assert len(names) == len(set(names))
    assert set(names) == FULL_JOBS | {"Publication proof"}
    for job in value["jobs"]:
        assert job["head_sha"] == head and job["status"] == "completed"
        assert job["conclusion"] == ("skipped" if job["name"] == "Publication proof" else "success")
    assert value["classifier"]["head_sha"] == head
    assert value["classifier"]["gate"] == "FULL_EXACT_SHA"
    assert value["classifier"]["class"] in {"I", "C", "UNKNOWN"}
    assert value["w03"]["implementation_sha"] == head and value["w03"]["overall"] == "PASS"
    assert sum(family["selectors"] for family in value["w03"]["families"]) == 38
    assert sum(family["tests"] for family in value["w03"]["families"]) == 85

    _validate_w04_c09_gate_summary(value["w04"], head)

def _native_metadata_fixture(head: str) -> dict[str, Any]:
    """Explicit gate controls, never evidence that the current asynchronous run completed."""
    proof: dict[str, Any] = {
        "schema_version": "w04-c08-native-proof-v1",
        "head_sha": head,
        "evidence_kind": "FIXTURE",
        "run": {"head_sha": head, "id": 1, "status": "completed", "conclusion": "success"},
        "jobs": [
            {
                "name": name,
                "head_sha": head,
                "status": "completed",
                "conclusion": "skipped" if name == "Publication proof" else "success",
            }
            for name in sorted(FULL_JOBS | {"Publication proof"})
        ],
        "classifier": {"head_sha": head, "class": "C", "gate": "FULL_EXACT_SHA"},
        "w03": {
            "implementation_sha": head,
            "overall": "PASS",
            "families": [{"selectors": 38, "tests": 85}],
        },
    }

    manifest = json.loads(
        (ROOT / "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json").read_bytes()
    )
    payload = {
        "schema_version": "w04-c09-gate-summary-v1",
        "gate_version": "w04-c09-investigation-gate-v1",
        "implementation_sha": head,
        "manifest_sha256": "d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1",
        "manifest_content_sha256": W04_C09_MANIFEST_CONTENT_SHA256,
        "total_families": 9,
        "total_selectors": 67,
        "total_tests": 81,
        "families": [
            {
                "id": f["id"],
                "status": "PASS",
                "selectors": len(f["targets"]),
                "tests": f["expected_cases"],
            }
            for f in manifest["families"]
        ],
        "overall": "PASS",
    }
    proof["w04"] = payload | {
        "summary_sha256": hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        ).hexdigest()
    }
    return proof

@pytest.mark.parametrize(
    "damage",
    [
        "run_head",
        "run_failure",
        "pending",
        "missing_job",
        "duplicate_job",
        "job_head",
        "job_failure",
        "publication",
        "classifier",
        "w03_head",
        "w03_count",
    ],
)
def test_r46_native_full_proof_gate_rejects_incomplete_or_wrong_sha_controls(damage: str) -> None:
    head = "a" * 40
    proof = _native_metadata_fixture(head)
    if damage == "run_head":
        proof["run"]["head_sha"] = "b" * 40
    elif damage == "run_failure":
        proof["run"]["conclusion"] = "failure"
    elif damage == "pending":
        proof["run"]["status"] = "in_progress"
    elif damage == "missing_job":
        proof["jobs"].pop()
    elif damage == "duplicate_job":
        proof["jobs"].append(copy.deepcopy(proof["jobs"][0]))
    elif damage == "job_head":
        proof["jobs"][0]["head_sha"] = "b" * 40
    elif damage == "job_failure":
        proof["jobs"][0]["conclusion"] = "failure"
    elif damage == "publication":
        next(j for j in proof["jobs"] if j["name"] == "Publication proof")["conclusion"] = "success"
    elif damage == "classifier":
        proof["classifier"]["gate"] = "PUBLICATION_EXACT_SHA"
    elif damage == "w03_head":
        proof["w03"]["implementation_sha"] = "b" * 40
    else:
        proof["w03"]["families"][0]["tests"] = 84
    with pytest.raises(AssertionError):
        _check_native_metadata(proof, head)


def test_r46_stage_b_exact_sha_full_native_ci(tmp_path: Path) -> None:
    """Rerun after terminal CI with measured metadata and all original GitHub artifacts."""
    head = _git("rev-parse", "HEAD")
    evidence = os.environ.get("FLOWLENS_C08_NATIVE_PROOF")
    if evidence is None:
        controls = _native_metadata_fixture(head)
        assert controls["evidence_kind"] == "FIXTURE"
        _check_native_metadata(controls, head)
        return
    proof = planner.read_json(Path(evidence))
    assert proof["evidence_kind"] == "GITHUB_NATIVE"
    _check_native_metadata(proof, head)
    directory = Path(proof["directory"])
    expected_artifact_names = {
        f"w04-devctrl02-{name}-{head}"
        for name in (
            "plan",
            "integration-data",
            "nonint-aggregate",
            *(f"shard-{i}" for i in range(7)),
        )
    }
    expected_artifact_names.add(f"w04-c09-gate-{head}")
    expected_artifact_names.add(f"w05-successor-governance-{head}")
    assert {a["name"] for a in proof["artifacts"]} == expected_artifact_names
    assert len(proof["artifacts"]) == 12
    for artifact in proof["artifacts"]:
        assert artifact["head_sha"] == head and artifact["run_id"] == proof["run"]["id"]
        assert (
            artifact["digest"]
            == "sha256:" + hashlib.sha256(Path(artifact["zip_path"]).read_bytes()).hexdigest()
        )
    import zipfile

    w04_artifact = next(a for a in proof["artifacts"] if a["name"] == f"w04-c09-gate-{head}")
    with zipfile.ZipFile(w04_artifact["zip_path"]) as archive:
        assert archive.namelist() == ["w04-c09-gate-summary.json"]
        raw = archive.read("w04-c09-gate-summary.json")
    summary = json.loads(raw)
    _validate_w04_c09_gate_summary(summary, head, raw)
    assert summary == proof["w04"]
    assert hashlib.sha256(raw).hexdigest() == proof["w04_summary_raw_sha256"]
    _devctrl03_workflow_delta_guard()
    plan = planner.read_json(directory / "plan/plan.json")
    weights = planner.read_json(planner.WEIGHTS)
    baseline = planner.read_json(planner.BASELINE)
    planner.validate_plan(plan, weights, baseline, head)
    current = planner.collect_nodes(planner.MARKER)
    assert current == plan["collected_nodeids"]
    historical = planner.read_json(planner.HISTORICAL_BASELINE)
    planner.enforce_historical(current, historical)
    assert len(current) == plan["current_node_count"]
    assert len(plan["files"]) == plan["current_file_count"]
    assert plan["schema_version"] == "w05-active-non-integration-plan-v1"
    assert plan["historical_nodeids_sha256"] == planner.CURRENT_NODES_DIGEST
    assert weights["weights_sha256"] == planner.MEASURED_WEIGHTS_DIGEST == plan["weights_sha256"]
    assert plan["current_nodeids_sha256"] == planner.digest(current)
    assert set(baseline["sorted_nodeids"]) <= set(historical["nodeids"]) <= set(current)
    rebuilt = verifier.aggregate(
        plan, directory / "shards", "nonint-shard", tmp_path / "reaggregated"
    )
    native, junit = verifier.read_evidence(directory / "nonint-aggregate")
    outcomes.validate_receipt(
        native, plan, "nonint-aggregate", None, plan["collected_nodeids"], junit
    )
    outcomes.require_success(native, junit)
    verifier.compare_outcomes(native, rebuilt)
    assert native["skipped_nodeids"] == outcomes.ACCEPTED_LINUX_SKIPS
    assert native["passed_count"] == len(current) - 3
    for category in ("failed", "error", "xfail", "xpass"):
        assert native[category + "_count"] == 0
    integration, junit = verifier.read_evidence(directory / "integration-data")
    selected = planner.collect_nodes("integration")
    outcomes.validate_receipt(integration, plan, "integration-data", None, selected, junit)
    outcomes.require_success(integration, junit)
    assert integration["collected_node_count"] == integration["passed_count"] == len(selected) == 70
    assert not integration["skipped_nodeids"]
