"""Frozen W04-C01 H01-H40 structural, determinism, and isolation proofs."""

from __future__ import annotations

import ast
import builtins
import io
import json
import os
import random
import socket
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Callable, Iterator, Mapping
from dataclasses import MISSING, FrozenInstanceError, fields, is_dataclass, replace
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from typing import cast

import pytest

import flowlens.investigation as investigation
from flowlens.decision.enums import TrustLevel as W03TrustLevel
from flowlens.decision.primitives import Validated
from flowlens.decision.serialization import (
    canonical_json_bytes as w03_canonical_json_bytes,
)
from flowlens.decision.serialization import (
    canonical_json_text as w03_canonical_json_text,
)
from flowlens.decision.serialization import (
    canonical_primitive as w03_canonical_primitive,
)
from flowlens.decision.serialization import (
    sha256_hex as w03_sha256_hex,
)
from flowlens.investigation import (
    ConflictRecord,
    ConflictType,
    EntityKey,
    EvidenceObservation,
    EvidenceQuerySpec,
    EvidenceSlice,
    FindingRecord,
    FindingStatus,
    HumanInvestigationEvent,
    HumanInvestigationOutcome,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
    InvestigationStep,
    InvestigationSummaryRecord,
    SummaryRendererMode,
    SummarySectionRecord,
    TrustLevel,
    UncertaintyItem,
    UncertaintyRegister,
    UncertaintyType,
)

type Artifact = (
    InvestigationCase
    | InvestigationQuestion
    | InvestigationStep
    | InvestigationPlan
    | EntityKey
    | EvidenceQuerySpec
    | EvidenceObservation
    | EvidenceSlice
    | FindingRecord
    | ConflictRecord
    | UncertaintyItem
    | UncertaintyRegister
    | SummarySectionRecord
    | InvestigationSummaryRecord
    | HumanInvestigationEvent
)

_TIME = datetime(2026, 10, 5, 8, tzinfo=UTC)
_ROOT = Path(__file__).resolve().parents[1]
_KINDS = {
    "case": "investigation-case",
    "question": "investigation-question",
    "step": "investigation-step",
    "plan": "investigation-plan",
    "key": "entity-key",
    "query": "evidence-query-spec",
    "observation": "evidence-observation",
    "slice": "evidence-slice",
    "finding": "finding-record",
    "conflict": "conflict-record",
    "uncertainty": "uncertainty-item",
    "register": "uncertainty-register",
    "section": "summary-section-record",
    "summary": "investigation-summary-record",
    "human": "human-investigation-event",
}
_NAMES = tuple(_KINDS)
_SEMANTIC_FIELDS = {
    "case": "source_decision_packet_id source_decision_packet_hash decision_run_id "
    "subject_type subject_id as_of_time opened_at opened_by risk_families source_signal_ids "
    "source_diagnosis_id source_recommendation_id",
    "question": "case_id question_code trigger_refs required_evidence_families "
    "allowed_traversal_families allowed_trust_classes as_of_time forbidden_inference_codes",
    "step": "case_id question_id ordinal depends_on_step_ids expected_evidence_families",
    "plan": "case_id as_of_time planner_contract_version steps",
    "key": "key_name key_value",
    "query": "case_id plan_id step_id question_id source_family_code entity_keys as_of_time "
    "requested_fields allowed_trust_classes expected_relationship_code",
    "observation": "source_family_code source_record_id source_field source_value available_at "
    "event_time freshness_code provenance_ref trust_class relationship_code",
    "slice": "case_id plan_id step_id question_id query_id as_of_time observations",
    "finding": "case_id question_id finding_code status supporting_evidence_ids "
    "contradicting_evidence_ids related_conflict_ids uncertainty_item_ids",
    "conflict": "case_id question_id conflict_code conflict_type evidence_ids",
    "uncertainty": "case_id question_id uncertainty_code uncertainty_type related_refs",
    "register": "case_id items",
    "section": "section_code renderer_mode text grounding_refs",
    "summary": "case_id plan_id finding_ids conflict_ids uncertainty_register_id human_event_ids "
    "summary_contract_version sections",
    "human": "case_id actor_id occurred_at outcome reviewed_finding_ids reviewed_conflict_ids "
    "acknowledged_uncertainty_item_ids previous_event_id note_text note_class",
}
_SET_FIELDS = (
    ("case", "risk_families"),
    ("case", "source_signal_ids"),
    ("question", "trigger_refs"),
    ("question", "required_evidence_families"),
    ("question", "allowed_traversal_families"),
    ("question", "allowed_trust_classes"),
    ("question", "forbidden_inference_codes"),
    ("step", "depends_on_step_ids"),
    ("step", "expected_evidence_families"),
    ("query", "entity_keys"),
    ("query", "requested_fields"),
    ("query", "allowed_trust_classes"),
    ("slice", "observations"),
    ("finding", "supporting_evidence_ids"),
    ("finding", "contradicting_evidence_ids"),
    ("finding", "related_conflict_ids"),
    ("finding", "uncertainty_item_ids"),
    ("conflict", "evidence_ids"),
    ("uncertainty", "related_refs"),
    ("register", "items"),
    ("section", "grounding_refs"),
    ("summary", "finding_ids"),
    ("summary", "conflict_ids"),
    ("summary", "human_event_ids"),
    ("human", "reviewed_finding_ids"),
    ("human", "reviewed_conflict_ids"),
    ("human", "acknowledged_uncertainty_item_ids"),
)
_EXECUTABLE_FIELDS = (
    "sql",
    "query_text",
    "raw_query",
    "url",
    "endpoint",
    "tool_name",
    "tool_args",
    "shell_command",
    "python_code",
    "filesystem_path",
    "graph_query",
    "vector_query",
)
_OPERATIONAL_FIELDS = (
    "operational_action",
    "target_system",
    "write_back_command",
    "procurement_action",
    "schedule_action",
    "quality_release",
    "supplier_replacement",
)
_CODE_FIELDS = (
    ("case", "subject_type"),
    ("question", "question_code"),
    ("key", "key_name"),
    ("query", "source_family_code"),
    ("query", "expected_relationship_code"),
    ("observation", "source_family_code"),
    ("observation", "source_field"),
    ("observation", "freshness_code"),
    ("observation", "relationship_code"),
    ("finding", "finding_code"),
    ("conflict", "conflict_code"),
    ("uncertainty", "uncertainty_code"),
    ("section", "section_code"),
    ("step", "case_id"),
    ("step", "question_id"),
    ("plan", "planner_contract_version"),
    ("summary", "summary_contract_version"),
    ("case", "risk_families"),
    ("question", "required_evidence_families"),
    ("question", "allowed_traversal_families"),
    ("question", "forbidden_inference_codes"),
    ("step", "expected_evidence_families"),
    ("query", "requested_fields"),
)


class _MutableTuple(tuple[object, ...]):
    mutable_state: list[str]


class _ForbiddenMapping(Mapping[str, object]):
    def __getitem__(self, key: str) -> object:
        raise AssertionError("invalid source payload was inspected")

    def __iter__(self) -> Iterator[str]:
        raise AssertionError("invalid source payload was iterated")

    def __len__(self) -> int:
        raise AssertionError("invalid source payload length was read")


def sample_artifacts() -> dict[str, Artifact]:
    """Create linked examples using only structural C01 constructors."""
    case = InvestigationCase(
        source_decision_packet_id="pkt_" + "a" * 64,
        source_decision_packet_hash="a" * 64,
        decision_run_id="run_" + "b" * 64,
        subject_type="SalesOrder",
        subject_id="SO-1",
        as_of_time=_TIME,
        opened_at=_TIME,
        opened_by="human-1",
        risk_families=("CAPACITY", "SUPPLIER"),
        source_signal_ids=("sig_a", "sig_b"),
        source_diagnosis_id="diag_" + "c" * 64,
        source_recommendation_id="rec_" + "d" * 64,
    )
    question = InvestigationQuestion(
        case_id=case.artifact_id,
        question_code="SUPPLY_TIMING",
        trigger_refs=("sig_a", "sig_b"),
        required_evidence_families=("MATERIAL", "RECEIPT"),
        allowed_traversal_families=("DIRECT", "SUPPLY"),
        allowed_trust_classes=(TrustLevel.DERIVED_FACT, TrustLevel.DIRECT_FACT),
        as_of_time=_TIME,
        forbidden_inference_codes=("CAUSAL_UPGRADE", "ROOT_CAUSE"),
    )
    first = InvestigationStep(
        case_id=case.artifact_id,
        question_id=question.artifact_id,
        ordinal=1,
        depends_on_step_ids=(),
        expected_evidence_families=("MATERIAL", "RECEIPT"),
    )
    second = replace(first, ordinal=2, depends_on_step_ids=(first.artifact_id,))
    plan = InvestigationPlan(
        case_id=case.artifact_id,
        as_of_time=_TIME,
        planner_contract_version="w04-c01-v1",
        steps=(first, second),
    )
    key = EntityKey(key_name="order_id", key_value="SO-1")
    query = EvidenceQuerySpec(
        case_id=case.artifact_id,
        plan_id=plan.artifact_id,
        step_id=first.artifact_id,
        question_id=question.artifact_id,
        source_family_code="RECEIPT",
        entity_keys=(key, EntityKey(key_name="supplier_id", key_value="S-1")),
        as_of_time=_TIME,
        requested_fields=("available_at", "receipt_state"),
        allowed_trust_classes=(TrustLevel.DERIVED_FACT, TrustLevel.DIRECT_FACT),
        expected_relationship_code="DIRECT",
    )
    observation = EvidenceObservation(
        source_family_code="RECEIPT",
        source_record_id="REC-1",
        source_field="receipt_state",
        source_value="PENDING",
        available_at=_TIME,
        event_time=_TIME - timedelta(hours=1),
        freshness_code="FRESH",
        provenance_ref="source-row-1",
        trust_class=TrustLevel.DIRECT_FACT,
        relationship_code="DIRECT",
    )
    other_observation = replace(observation, source_record_id="REC-2", source_value="RECEIVED")
    observations = tuple(
        sorted((observation, other_observation), key=lambda item: item.artifact_id)
    )
    evidence_slice = EvidenceSlice(
        case_id=case.artifact_id,
        plan_id=plan.artifact_id,
        step_id=first.artifact_id,
        question_id=question.artifact_id,
        query_id=query.artifact_id,
        as_of_time=_TIME,
        observations=observations,
    )
    uncertainty = UncertaintyItem(
        case_id=case.artifact_id,
        question_id=question.artifact_id,
        uncertainty_code="DISPOSITION_UNKNOWN",
        uncertainty_type=UncertaintyType.UNKNOWN_EVIDENCE,
        related_refs=("REC-1", "REC-2"),
    )
    other_uncertainty = replace(uncertainty, uncertainty_code="FORMALITY_UNKNOWN")
    register = UncertaintyRegister(
        case_id=case.artifact_id,
        items=tuple(sorted((uncertainty, other_uncertainty), key=lambda item: item.artifact_id)),
    )
    conflict = ConflictRecord(
        case_id=case.artifact_id,
        question_id=question.artifact_id,
        conflict_code="RECEIPT_DISAGREEMENT",
        conflict_type=ConflictType.VALUE_CONFLICT,
        evidence_ids=tuple(sorted(item.artifact_id for item in observations)),
    )
    finding = FindingRecord(
        case_id=case.artifact_id,
        question_id=question.artifact_id,
        finding_code="RECEIPT_REVIEW",
        status=FindingStatus.UNRESOLVED,
        supporting_evidence_ids=(observation.artifact_id,),
        contradicting_evidence_ids=(other_observation.artifact_id,),
        related_conflict_ids=(conflict.artifact_id,),
        uncertainty_item_ids=(uncertainty.artifact_id,),
    )
    human = HumanInvestigationEvent(
        case_id=case.artifact_id,
        actor_id="human-1",
        occurred_at=_TIME,
        outcome=HumanInvestigationOutcome.MORE_EVIDENCE_REQUIRED,
        reviewed_finding_ids=(finding.artifact_id,),
        reviewed_conflict_ids=(conflict.artifact_id,),
        acknowledged_uncertainty_item_ids=(uncertainty.artifact_id,),
        previous_event_id=None,
        note_text="Formal receipt evidence remains incomplete.",
        note_class="HUMAN_NOTE_NON_EVIDENCE",
    )
    section = SummarySectionRecord(
        section_code="EVIDENCE_REVIEW",
        renderer_mode=SummaryRendererMode.DETERMINISTIC,
        text="Human review remains pending.",
        grounding_refs=tuple(sorted((finding.artifact_id, uncertainty.artifact_id))),
    )
    summary = InvestigationSummaryRecord(
        case_id=case.artifact_id,
        plan_id=plan.artifact_id,
        finding_ids=(finding.artifact_id,),
        conflict_ids=(conflict.artifact_id,),
        uncertainty_register_id=register.artifact_id,
        human_event_ids=(human.artifact_id,),
        summary_contract_version="w04-c01-v1",
        sections=(section, replace(section, section_code="UNCERTAINTY")),
    )
    return {
        "case": case,
        "question": question,
        "step": second,
        "plan": plan,
        "key": key,
        "query": query,
        "observation": observation,
        "slice": evidence_slice,
        "finding": finding,
        "conflict": conflict,
        "uncertainty": uncertainty,
        "register": register,
        "section": section,
        "summary": summary,
        "human": human,
    }


def _get[T](name: str, cls: type[T]) -> T:
    value = sample_artifacts()[name]
    assert isinstance(value, cls)
    return value


def _construct(artifact: Artifact, **overrides: object) -> Artifact:
    values = {
        field.name: getattr(artifact, field.name) for field in fields(artifact) if field.init
    }
    values.update(overrides)
    # Negative tests deliberately supply invalid/extra constructor keywords dynamically.
    constructor = cast(Callable[..., Artifact], type(artifact))
    return constructor(**values)


def _mutable_subclass(artifact: Artifact) -> Artifact:
    subclass = type(f"Mutable{type(artifact).__name__}", (type(artifact),), {})
    constructor = cast(Callable[..., Artifact], subclass)
    clone = constructor(
        **{field.name: getattr(artifact, field.name) for field in fields(artifact) if field.init}
    )
    object.__setattr__(clone, "mutable_state", [])
    assert hasattr(clone, "__dict__")
    return clone


def _wire(artifact: Artifact) -> dict[str, object]:
    value: object = json.loads(artifact.to_json())
    assert isinstance(value, dict)
    return cast(dict[str, object], value)


def _public_values(value: object) -> Iterator[object]:
    yield value
    if isinstance(value, tuple):
        for item in value:
            yield from _public_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _public_values(item)
    elif is_dataclass(value) and not isinstance(value, type):
        for field in fields(value):
            yield from _public_values(getattr(value, field.name))


@pytest.mark.parametrize("name", _NAMES)
def test_h01_top_level_assignment_rejected(name: str) -> None:
    artifact = sample_artifacts()[name]
    assert is_dataclass(artifact)
    assert isinstance(artifact, Validated)
    assert not hasattr(artifact, "__dict__")
    assert all(field.kw_only for field in fields(artifact))
    for field in fields(artifact):
        with pytest.raises((FrozenInstanceError, AttributeError)):
            setattr(artifact, field.name, getattr(artifact, field.name))


@pytest.mark.parametrize("name", _NAMES)
def test_h02_nested_public_collections_immutable(name: str) -> None:
    artifact = sample_artifacts()[name]
    for value in _public_values(artifact):
        assert not isinstance(value, (list, dict, set, bytearray))
        if isinstance(value, tuple):
            assert not hasattr(value, "append")
            assert not hasattr(value, "__setitem__")
        elif is_dataclass(value) and not isinstance(value, type):
            with pytest.raises((FrozenInstanceError, AttributeError)):
                setattr(value, fields(value)[0].name, "changed")
    for field in fields(artifact):
        current = getattr(artifact, field.name)
        if isinstance(current, tuple):
            with pytest.raises(TypeError):
                _construct(artifact, **{field.name: list(current)})
            subclass = _MutableTuple(current)
            subclass.mutable_state = []
            with pytest.raises(TypeError):
                _construct(artifact, **{field.name: subclass})
            if current and is_dataclass(current[0]):
                member = cast(Artifact, current[0])
                with pytest.raises(TypeError):
                    _construct(artifact, **{field.name: (_mutable_subclass(member),)})


@pytest.mark.parametrize("name", _NAMES)
def test_h03_extra_missing_and_duplicate_wire_fields_rejected(name: str) -> None:
    artifact = sample_artifacts()[name]
    with pytest.raises(TypeError):
        _construct(artifact, unauthorized_field="FORBIDDEN")
    wire = _wire(artifact)
    with pytest.raises((TypeError, ValueError)):
        type(artifact).from_json(json.dumps({**wire, "unauthorized_field": "FORBIDDEN"}))
    for field in fields(artifact):
        if not field.init:
            continue
        missing = {key: value for key, value in wire.items() if key != field.name}
        with pytest.raises((TypeError, ValueError)):
            type(artifact).from_json(json.dumps(missing))
        if field.default is MISSING and field.default_factory is MISSING:
            required_missing = {
                item.name: getattr(artifact, item.name)
                for item in fields(artifact)
                if item.init and item.name != field.name
            }
            constructor = cast(Callable[..., Artifact], type(artifact))
            with pytest.raises(TypeError):
                constructor(**required_missing)
    duplicate = artifact.to_json()[:-1] + ',"schema_version":"ignored.v9"}'
    with pytest.raises((TypeError, ValueError)):
        type(artifact).from_json(duplicate)


@pytest.mark.parametrize("name", _NAMES)
def test_h04_schema_version_stable_and_closed(name: str) -> None:
    artifact = sample_artifacts()[name]
    assert {field.name for field in fields(artifact)} == set(_SEMANTIC_FIELDS[name].split()) | {
        "schema_version", "content_hash", "artifact_id"
    }
    assert artifact.schema_version == f"{_KINDS[name]}.v1"
    for wrong in ("", "v1", f"{_KINDS[name]}.v2", "other-kind.v1"):
        with pytest.raises(ValueError):
            _construct(artifact, schema_version=wrong)
    assert artifact.canonical_payload()["schema_version"] == artifact.schema_version


@pytest.mark.parametrize("name", _NAMES)
def test_h05_same_process_canonical_determinism(name: str) -> None:
    first = sample_artifacts()[name]
    for _ in range(3):
        second = sample_artifacts()[name]
        assert second.to_json() == first.to_json()
        assert second.canonical_payload() == first.canonical_payload()
        assert second.content_hash == first.content_hash
        assert second.artifact_id == first.artifact_id
    assert first.content_hash == w03_sha256_hex(first.canonical_payload())
    assert first.artifact_id.endswith(first.content_hash)
    assert len(first.content_hash) == 64
    payload = first.canonical_payload()
    assert set(payload) == {"artifact_kind", "schema_version", "identity"}
    for value in _public_values(payload["identity"]):
        if isinstance(value, dict):
            assert "content_hash" not in value and "artifact_id" not in value


@pytest.mark.parametrize("seed", ["0", "1", "34567"])
def test_h06_fresh_process_determinism(seed: str) -> None:
    expected = {
        name: [artifact.to_json(), artifact.content_hash, artifact.artifact_id]
        for name, artifact in sample_artifacts().items()
    }
    script = (
        "import json, runpy; "
        "samples=runpy.run_path('tests/test_investigation_contracts.py')['sample_artifacts'](); "
        "print(json.dumps({n:[a.to_json(),a.content_hash,a.artifact_id] "
        "for n,a in samples.items()},sort_keys=True))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=_ROOT,
        env={**os.environ, "PYTHONHASHSEED": seed},
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(completed.stdout) == expected


@pytest.mark.parametrize("name", _NAMES)
def test_h07_serialize_parse_serialize_identity(name: str) -> None:
    artifact = sample_artifacts()[name]
    for raw in (artifact.to_json(), artifact.to_json().encode("utf-8")):
        restored = type(artifact).from_json(raw)
        assert restored.to_json() == artifact.to_json()
        assert restored.artifact_id == artifact.artifact_id
        assert restored.content_hash == artifact.content_hash
        assert restored == artifact


@pytest.mark.parametrize("name", _NAMES)
@pytest.mark.parametrize("identity_field", ["artifact_id", "content_hash"])
def test_h08_supplied_mismatching_identity_rejected(name: str, identity_field: str) -> None:
    artifact = sample_artifacts()[name]
    assert not next(field for field in fields(artifact) if field.name == identity_field).init
    for supplied in (getattr(artifact, identity_field), "f" * 64):
        with pytest.raises(TypeError):
            _construct(artifact, **{identity_field: supplied})
    wire = _wire(artifact)
    wire[identity_field] = "invalid_identity"
    with pytest.raises((TypeError, ValueError)):
        type(artifact).from_json(json.dumps(wire))


@pytest.mark.parametrize("name", _NAMES)
def test_h09_semantic_mutation_changes_identity(name: str) -> None:
    artifact = sample_artifacts()[name]
    # Each representative has a semantic string that can be changed without another invariant.
    field_names = {
        "case": "subject_id",
        "question": "question_code",
        "step": "question_id",
        "plan": "planner_contract_version",
        "key": "key_value",
        "query": "source_family_code",
        "observation": "source_record_id",
        "slice": "query_id",
        "finding": "finding_code",
        "conflict": "conflict_code",
        "uncertainty": "uncertainty_code",
        "register": "case_id",
        "section": "text",
        "summary": "summary_contract_version",
        "human": "actor_id",
    }
    field_name = field_names[name]
    changed: Artifact
    if name == "register":
        register = _get("register", UncertaintyRegister)
        changed = replace(
            register,
            case_id="case_changed",
            items=tuple(
                sorted(
                    (replace(item, case_id="case_changed") for item in register.items),
                    key=lambda item: item.artifact_id,
                )
            ),
        )
    else:
        changed = _construct(artifact, **{field_name: f"{getattr(artifact, field_name)}_changed"})
    assert changed.content_hash != artifact.content_hash
    assert changed.artifact_id != artifact.artifact_id
    wire = _wire(artifact)
    wire[field_name] = getattr(changed, field_name)
    if name != "register":
        with pytest.raises((TypeError, ValueError)):
            type(artifact).from_json(json.dumps(wire))


def test_h10_identity_has_no_random_clock_process_or_hash_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = {name: artifact.artifact_id for name, artifact in sample_artifacts().items()}

    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("nondeterministic identity input accessed")

    with monkeypatch.context() as context:
        for owner, attribute in (
            (time, "time"),
            (random, "random"),
            (random, "randint"),
            (uuid, "uuid4"),
            (os, "getpid"),
            (threading, "get_ident"),
            (builtins, "hash"),
        ):
            context.setattr(owner, attribute, forbidden)
        actual = {name: artifact.artifact_id for name, artifact in sample_artifacts().items()}
    assert actual == expected
    for path in (_ROOT / "src/flowlens/investigation").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"now", "utcnow", "uuid4", "getpid", "get_ident"}


@pytest.mark.parametrize(
    ("name", "field_name"),
    [
        ("case", "as_of_time"),
        ("case", "opened_at"),
        ("question", "as_of_time"),
        ("plan", "as_of_time"),
        ("query", "as_of_time"),
        ("observation", "available_at"),
        ("observation", "event_time"),
        ("slice", "as_of_time"),
        ("human", "occurred_at"),
    ],
)
def test_h11_naive_business_timestamps_rejected(name: str, field_name: str) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        _construct(sample_artifacts()[name], **{field_name: _TIME.replace(tzinfo=None)})


@pytest.mark.parametrize("name", _NAMES)
def test_h12_equivalent_timezones_reuse_w03_convention(name: str) -> None:
    artifact = sample_artifacts()[name]
    changes = {
        field.name: value.astimezone(timezone(timedelta(hours=8)))
        for field in fields(artifact)
        if isinstance(value := getattr(artifact, field.name), datetime)
    }
    equivalent = _construct(artifact, **changes)
    assert equivalent.content_hash == artifact.content_hash
    assert equivalent.artifact_id == artifact.artifact_id
    assert equivalent.to_json() == artifact.to_json()
    assert w03_canonical_primitive(_TIME) == "2026-10-05T08:00:00.000000Z"


@pytest.mark.parametrize(("name", "field_name"), _CODE_FIELDS)
@pytest.mark.parametrize("invalid", ["", " ", "bad code", "bad/code", "https://host", "x" * 129])
def test_h13_blank_or_executable_code_values_rejected(
    name: str, field_name: str, invalid: str
) -> None:
    artifact = sample_artifacts()[name]
    is_tuple = isinstance(getattr(artifact, field_name), tuple)
    with pytest.raises(ValueError):
        _construct(artifact, **{field_name: (invalid,) if is_tuple else invalid})
    boundary = "x" * 128
    assert _construct(artifact, **{field_name: (boundary,) if is_tuple else boundary})


@pytest.mark.parametrize(("name", "field_name"), _SET_FIELDS)
def test_h14_duplicate_set_like_references_rejected(name: str, field_name: str) -> None:
    artifact = sample_artifacts()[name]
    value = getattr(artifact, field_name)
    assert isinstance(value, tuple) and value
    with pytest.raises(ValueError):
        _construct(artifact, **{field_name: (value[0], value[0])})


def test_h15_case_cannot_open_before_decision_time() -> None:
    case = _get("case", InvestigationCase)
    assert case.opened_at == case.as_of_time
    assert replace(case, opened_at=_TIME + timedelta(microseconds=1))
    with pytest.raises(ValueError):
        replace(case, opened_at=_TIME - timedelta(microseconds=1))
    for digest in ("a" * 40, "A" * 64, "g" * 64, "a" * 63, ""):
        with pytest.raises(ValueError):
            replace(case, source_decision_packet_hash=digest)


@pytest.mark.parametrize("ordinals", [(2,), (1, 3), (2, 1), (1, 1)])
def test_h16_plan_ordinals_contiguous(ordinals: tuple[int, ...]) -> None:
    plan = _get("plan", InvestigationPlan)
    assert replace(plan, steps=()).steps == ()
    steps = tuple(
        replace(plan.steps[0], ordinal=ordinal, depends_on_step_ids=()) for ordinal in ordinals
    )
    with pytest.raises(ValueError):
        replace(plan, steps=steps)
    with pytest.raises(ValueError):
        replace(plan.steps[0], ordinal=0)
    with pytest.raises(TypeError):
        _construct(plan.steps[0], ordinal=True)
    with pytest.raises(ValueError):
        replace(plan, steps=(replace(plan.steps[0], case_id="other_case"),))


@pytest.mark.parametrize("dependency", ["same", "future", "unknown"])
def test_h17_plan_dependencies_only_reference_earlier_steps(dependency: str) -> None:
    plan = _get("plan", InvestigationPlan)
    target = {
        "same": plan.steps[0].artifact_id,
        "future": plan.steps[1].artifact_id,
        "unknown": "unknown_step",
    }[dependency]
    changed = replace(plan.steps[0], depends_on_step_ids=(target,))
    with pytest.raises(ValueError):
        replace(plan, steps=(changed, replace(plan.steps[1], depends_on_step_ids=())))
    assert plan.steps[1].depends_on_step_ids == (plan.steps[0].artifact_id,)


def test_h18_plan_cycles_and_executable_dependencies_rejected() -> None:
    plan = _get("plan", InvestigationPlan)
    first = replace(plan.steps[0], depends_on_step_ids=(plan.steps[1].artifact_id,))
    second = replace(plan.steps[1], depends_on_step_ids=(first.artifact_id,))
    with pytest.raises(ValueError):
        replace(plan, steps=(first, second))
    for executable in ("SELECT * FROM orders", "https://example.org", "C:\\evidence", "../data"):
        with pytest.raises(ValueError):
            replace(plan.steps[0], depends_on_step_ids=(executable,))


@pytest.mark.parametrize("field_name", _EXECUTABLE_FIELDS)
def test_h19_query_has_no_executable_escape_fields(field_name: str) -> None:
    query = _get("query", EvidenceQuerySpec)
    assert field_name not in {field.name for field in fields(query)}
    with pytest.raises(TypeError):
        _construct(query, **{field_name: "EXECUTE"})
    with pytest.raises((TypeError, ValueError)):
        EvidenceQuerySpec.from_json(json.dumps({**_wire(query), field_name: "EXECUTE"}))
    # Entity values are data; code-like key names do not turn values into execution authority.
    data = EntityKey(key_name="order_id", key_value="SELECT * FROM orders; https://example.org")
    assert replace(query, entity_keys=(data,)).entity_keys == (data,)


@pytest.mark.parametrize("field_name", ["entity_keys", "requested_fields", "allowed_trust_classes"])
def test_h20_query_required_nonempty_collections(field_name: str) -> None:
    query = _get("query", EvidenceQuerySpec)
    with pytest.raises(ValueError):
        _construct(query, **{field_name: ()})
    with pytest.raises(ValueError):
        replace(
            query,
            entity_keys=(query.entity_keys[0], replace(query.entity_keys[0], key_value="2")),
        )


@pytest.mark.parametrize("name", ["query", "question"])
def test_h21_forbidden_trust_not_allowed(name: str) -> None:
    artifact = sample_artifacts()[name]
    with pytest.raises(ValueError):
        _construct(artifact, allowed_trust_classes=(TrustLevel.FORBIDDEN_INFERENCE,))
    with pytest.raises(TypeError):
        _construct(artifact, allowed_trust_classes=("DIRECT_FACT",))
    allowed = tuple(sorted((TrustLevel.UNKNOWN, TrustLevel.ASSOCIATIVE_EVIDENCE), key=str))
    assert _construct(artifact, allowed_trust_classes=allowed)


def test_h22_empty_evidence_result_remains_explicit() -> None:
    evidence_slice = _get("slice", EvidenceSlice)
    empty = replace(evidence_slice, observations=())
    assert empty.observations == ()
    assert EvidenceSlice.from_json(empty.to_json()).observations == ()
    assert empty.artifact_id != evidence_slice.artifact_id


def test_h23_evidence_availability_is_bounded_by_as_of() -> None:
    evidence_slice = _get("slice", EvidenceSlice)
    observation = evidence_slice.observations[0]
    assert replace(evidence_slice, observations=(observation,))
    assert replace(
        evidence_slice,
        observations=(replace(observation, available_at=_TIME - timedelta(microseconds=1)),),
    )
    with pytest.raises(ValueError):
        replace(
            evidence_slice,
            observations=(replace(observation, available_at=_TIME + timedelta(microseconds=1)),),
        )


def test_h24_duplicate_observations_rejected() -> None:
    evidence_slice = _get("slice", EvidenceSlice)
    observation = evidence_slice.observations[0]
    with pytest.raises(ValueError):
        replace(evidence_slice, observations=(observation, observation))


@pytest.mark.parametrize("trust", tuple(TrustLevel))
def test_h25_forbidden_observation_cannot_enter_usable_slice(trust: TrustLevel) -> None:
    evidence_slice = _get("slice", EvidenceSlice)
    observation = replace(evidence_slice.observations[0], trust_class=trust)
    if trust is TrustLevel.FORBIDDEN_INFERENCE:
        with pytest.raises(ValueError):
            replace(evidence_slice, observations=(observation,))
    else:
        usable = replace(evidence_slice, observations=(observation,))
        assert usable.observations[0].trust_class is trust


def test_h26_finding_support_and_contradiction_disjoint() -> None:
    finding = _get("finding", FindingRecord)
    with pytest.raises(ValueError):
        replace(finding, contradicting_evidence_ids=finding.supporting_evidence_ids)
    assert set(finding.supporting_evidence_ids).isdisjoint(finding.contradicting_evidence_ids)
    for forbidden in (
        "root_cause_probability",
        "causal_score",
        "confidence_probability",
        "remedy_efficacy",
        "recommended_action",
    ):
        with pytest.raises(TypeError):
            _construct(finding, **{forbidden: "UNAUTHORIZED"})


def test_h27_supported_finding_requires_support() -> None:
    finding = _get("finding", FindingRecord)
    assert replace(finding, status=FindingStatus.SUPPORTED)
    with pytest.raises(ValueError):
        replace(finding, status=FindingStatus.SUPPORTED, supporting_evidence_ids=())


def test_h28_contradicted_finding_requires_contradiction() -> None:
    finding = _get("finding", FindingRecord)
    assert replace(finding, status=FindingStatus.CONTRADICTED)
    with pytest.raises(ValueError):
        replace(finding, status=FindingStatus.CONTRADICTED, contradicting_evidence_ids=())


def test_h29_unknown_requires_uncertainty_and_unresolved_requires_basis() -> None:
    finding = _get("finding", FindingRecord)
    assert replace(finding, status=FindingStatus.UNKNOWN)
    with pytest.raises(ValueError):
        replace(finding, status=FindingStatus.UNKNOWN, uncertainty_item_ids=())
    empty = {
        "supporting_evidence_ids": (),
        "contradicting_evidence_ids": (),
        "related_conflict_ids": (),
        "uncertainty_item_ids": (),
    }
    with pytest.raises(ValueError):
        _construct(finding, status=FindingStatus.UNRESOLVED, **empty)
    for basis in empty:
        assert _construct(
            finding, status=FindingStatus.UNRESOLVED, **{**empty, basis: ("explicit_basis",)}
        )


@pytest.mark.parametrize("refs", [(), ("ev_a",), ("ev_a", "ev_a")])
def test_h30_conflict_requires_two_unique_evidence_refs(refs: tuple[str, ...]) -> None:
    conflict = _get("conflict", ConflictRecord)
    with pytest.raises(ValueError):
        replace(conflict, evidence_ids=refs)
    assert replace(conflict, evidence_ids=("ev_a", "ev_b"))
    for forbidden in ("winner", "resolution", "causal_truth"):
        with pytest.raises(TypeError):
            _construct(conflict, **{forbidden: "ev_a"})


def test_h31_uncertainty_register_preserves_items_and_empty_is_legal() -> None:
    register = _get("register", UncertaintyRegister)
    restored = UncertaintyRegister.from_json(register.to_json())
    assert restored.items == register.items
    assert replace(register, items=()).items == ()
    with pytest.raises(ValueError):
        replace(register, items=(replace(register.items[0], case_id="other_case"),))
    with pytest.raises(ValueError):
        replace(register, items=(register.items[0], register.items[0]))
    for uncertainty_type in UncertaintyType:
        assert replace(register.items[0], uncertainty_type=uncertainty_type)


@pytest.mark.parametrize(
    ("enum", "expected"),
    [
        (FindingStatus, "SUPPORTED CONTRADICTED UNRESOLVED UNKNOWN"),
        (
            ConflictType,
            "DIRECT_VS_DIRECT DIRECT_VS_DERIVED TIMESTAMP_CONFLICT "
            "IDENTITY_CONFLICT VALUE_CONFLICT",
        ),
        (
            UncertaintyType,
            "UNKNOWN_EVIDENCE MISSING_EVIDENCE STALE_EVIDENCE CONFLICTING_EVIDENCE "
            "ASSOCIATIVE_ONLY FORBIDDEN_INFERENCE UNRESOLVED_QUESTION",
        ),
        (SummaryRendererMode, "DETERMINISTIC BOUNDED_LLM DEGRADED_FALLBACK"),
        (
            HumanInvestigationOutcome,
            "SUPPORTED_FINDING_RECORDED NO_SUPPORTED_FINDING MORE_EVIDENCE_REQUIRED "
            "DEFER INVESTIGATION_REVIEW_COMPLETE",
        ),
    ],
)
def test_h32_closed_outcomes_and_all_structural_enums(enum: type[StrEnum], expected: str) -> None:
    assert {member.value for member in enum} == set(expected.split())
    assert len(enum.__members__) == len(expected.split())
    for invalid in ("OTHER", "EXECUTE", "", "SUPPORTED "):
        with pytest.raises(ValueError):
            enum(invalid)
    human = _get("human", HumanInvestigationEvent)
    with pytest.raises(TypeError):
        _construct(human, outcome="DEFER")


@pytest.mark.parametrize("invalid", ["EVIDENCE", "FINDING", "", " HUMAN_NOTE_NON_EVIDENCE"])
def test_h33_human_note_fixed_non_evidence_class(invalid: str) -> None:
    human = _get("human", HumanInvestigationEvent)
    assert human.note_class == "HUMAN_NOTE_NON_EVIDENCE"
    assert replace(human, note_text=None).note_text is None
    with pytest.raises(ValueError):
        replace(human, note_class=invalid)
    for blank in ("", " ", "\t\n"):
        with pytest.raises(ValueError):
            replace(human, note_text=blank)
    assert not any("evidence_id" in field.name for field in fields(human))


@pytest.mark.parametrize("field_name", _OPERATIONAL_FIELDS)
def test_h34_human_events_have_no_operational_action_fields(field_name: str) -> None:
    human = _get("human", HumanInvestigationEvent)
    assert field_name not in {field.name for field in fields(human)}
    with pytest.raises(TypeError):
        _construct(human, **{field_name: "UNAUTHORIZED"})
    with pytest.raises((TypeError, ValueError)):
        HumanInvestigationEvent.from_json(json.dumps({**_wire(human), field_name: "UNAUTHORIZED"}))


@pytest.mark.parametrize("renderer_mode", tuple(SummaryRendererMode))
def test_h35_summary_text_retains_grounding_without_truth_authority(
    renderer_mode: SummaryRendererMode,
) -> None:
    examples = sample_artifacts()
    before = {name: value.artifact_id for name, value in examples.items()}
    section = _get("section", SummarySectionRecord)
    summary = _get("summary", InvestigationSummaryRecord)
    changed = replace(section, text="Presentation text changed.", renderer_mode=renderer_mode)
    assert changed.grounding_refs == section.grounding_refs
    assert changed.artifact_id != section.artifact_id
    assert replace(section, grounding_refs=()).grounding_refs == ()
    assert {name: value.artifact_id for name, value in examples.items()} == before
    restored = SummarySectionRecord.from_json(changed.to_json())
    assert restored.grounding_refs == section.grounding_refs
    assert replace(summary, sections=(changed,)).sections == (changed,)
    assert replace(summary, sections=()).sections == ()
    for artifact in (section, summary):
        for forbidden in ("evidence_ids", "finding_code", "recommended_action", "execution"):
            with pytest.raises(TypeError):
                _construct(artifact, **{forbidden: "UNAUTHORIZED"})


def _local_dependency_sources() -> dict[str, str]:
    """Follow actual local import edges, including package initializers, transitively."""
    pending = ["flowlens.investigation"]
    sources: dict[str, str] = {}
    while pending:
        module = pending.pop()
        if module in sources:
            continue
        location = _ROOT / "src" / Path(*module.split("."))
        file = location / "__init__.py" if location.is_dir() else location.with_suffix(".py")
        assert file.is_file(), module
        source = file.read_text(encoding="utf-8")
        sources[module] = source
        tree = ast.parse(source)
        package = module if file.name == "__init__.py" else module.rpartition(".")[0]
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    parent_parts = package.split(".")[: len(package.split(".")) - node.level + 1]
                    base = ".".join(parent_parts + ([node.module] if node.module else []))
                else:
                    base = node.module or ""
                imported = [base]
                for alias in node.names:
                    target = f"{base}.{alias.name}"
                    target_path = _ROOT / "src" / Path(*target.split("."))
                    if target_path.is_dir() or target_path.with_suffix(".py").is_file():
                        imported.append(target)
            else:
                continue
            for imported_module in imported:
                if imported_module == "flowlens" or imported_module.startswith("flowlens."):
                    # Python executes each package initializer before its dotted submodule.
                    parts = imported_module.split(".")
                    pending.extend(".".join(parts[:count]) for count in range(1, len(parts) + 1))
    return sources


def test_h36_no_transitive_db_network_model_tool_or_hgt_capability_imports() -> None:
    sources = _local_dependency_sources()
    assert {"flowlens", "flowlens.decision", "flowlens.investigation"} <= sources.keys()
    allowed_local = {
        "flowlens",
        "flowlens.decision",
        "flowlens.decision.contracts",
        "flowlens.decision.enums",
        "flowlens.decision.primitives",
        "flowlens.decision.serialization",
    }
    forbidden = {
        "subprocess",
        "socket",
        "urllib",
        "http",
        "httpx",
        "requests",
        "openai",
        "sqlalchemy",
        "psycopg",
        "sqlite3",
        "boto3",
        "langchain",
        "langgraph",
        "pydantic_ai",
        "mcp",
        "pathlib",
        "os",
    }
    for module, source in sources.items():
        assert module.startswith("flowlens.investigation") or module in allowed_local, module
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
                assert not roots & forbidden, (module, roots & forbidden)
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden, (module, node.module)
        assert "flowlens.data.scenarios" not in source
        assert "flowlens.db" not in source
    script = (
        "import sys, flowlens.investigation; "
        "blocked=('flowlens.db','flowlens.data.scenarios','openai','sqlalchemy',"
        "'psycopg','httpx','requests','subprocess','socket'); "
        "assert not any(name.startswith(blocked) for name in sys.modules)"
    )
    subprocess.run([sys.executable, "-c", script], cwd=_ROOT, check=True, capture_output=True)


def test_h37_exact_w03_trust_and_serialization_framework_reused() -> None:
    assert TrustLevel is W03TrustLevel
    assert investigation.canonical_json_bytes is w03_canonical_json_bytes
    assert investigation.canonical_json_text is w03_canonical_json_text
    assert investigation.canonical_primitive is w03_canonical_primitive
    assert investigation.sha256_hex is w03_sha256_hex
    assert {member.value for member in TrustLevel} == {
        "DIRECT_FACT",
        "DERIVED_FACT",
        "ASSOCIATIVE_EVIDENCE",
        "UNKNOWN",
        "FORBIDDEN_INFERENCE",
    }
    assert all(isinstance(artifact, Validated) for artifact in sample_artifacts().values())


@pytest.mark.parametrize(
    "scalar", [None, True, 7, "source value", Decimal("1.2500"), date(2026, 10, 5), _TIME]
)
def test_h38_all_public_artifacts_canonical_roundtrip_with_w03_scalars(scalar: object) -> None:
    observation = _get("observation", EvidenceObservation)
    changed = _construct(observation, source_value=scalar)
    restored = EvidenceObservation.from_json(changed.to_json())
    assert restored.to_json() == changed.to_json()
    assert restored.content_hash == changed.content_hash
    assert restored.artifact_id == changed.artifact_id
    examples = sample_artifacts()
    assert len(examples) == 15
    for artifact in examples.values():
        assert type(artifact).from_json(artifact.to_json()).to_json() == artifact.to_json()
    invalid_scalars: tuple[object, ...] = (
        1.25, [], {}, {1}, b"bytes", Decimal("NaN"), Decimal("Infinity")
    )
    for invalid in invalid_scalars:
        with pytest.raises((TypeError, ValueError)):
            _construct(observation, source_value=invalid)
    for token in ("1.25", "NaN", "Infinity", "-Infinity"):
        encoded = observation.to_json().replace(
            '"source_value":"PENDING"', f'"source_value":{token}'
        )
        assert encoded != observation.to_json()
        with pytest.raises((TypeError, ValueError)):
            EvidenceObservation.from_json(encoded)


def _ordering_pair(name: str, field_name: str) -> tuple[object, object]:
    artifact = sample_artifacts()[name]
    values = getattr(artifact, field_name)
    assert isinstance(values, tuple) and values
    first = values[0]
    if len(values) > 1:
        return first, values[1]
    if isinstance(first, str):
        return "ref_a", "ref_b"
    if isinstance(first, UncertaintyItem):
        second = replace(first, uncertainty_code="SECOND_UNCERTAINTY")
        ordered = sorted((first, second), key=lambda item: item.artifact_id)
        return ordered[0], ordered[1]
    raise AssertionError((name, field_name, type(first)))


@pytest.mark.parametrize(("name", "field_name"), _SET_FIELDS)
def test_h39_set_like_order_is_deterministic_and_ordered_sequences_preserved(
    name: str, field_name: str
) -> None:
    artifact = sample_artifacts()[name]
    first, second = _ordering_pair(name, field_name)
    with pytest.raises(ValueError):
        _construct(artifact, **{field_name: (second, first)})
    plan = _get("plan", InvestigationPlan)
    assert tuple(step.ordinal for step in plan.steps) == (1, 2)
    summary = _get("summary", InvestigationSummaryRecord)
    reversed_summary = replace(summary, sections=tuple(reversed(summary.sections)))
    assert reversed_summary.sections == tuple(reversed(summary.sections))
    assert reversed_summary.artifact_id != summary.artifact_id
    assert InvestigationSummaryRecord.from_json(reversed_summary.to_json()).sections == (
        tuple(reversed(summary.sections))
    )


def test_h40_contract_construction_and_parse_perform_no_external_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    examples = sample_artifacts()
    wires = {name: artifact.to_json() for name, artifact in examples.items()}

    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("external I/O attempted by contract construction")

    with monkeypatch.context() as context:
        for owner, attribute in (
            (builtins, "open"),
            (io, "open"),
            (os, "open"),
            (os, "listdir"),
            (os, "scandir"),
            (os, "system"),
            (socket, "socket"),
            (socket, "create_connection"),
            (subprocess, "Popen"),
            (subprocess, "run"),
            (Path, "open"),
            (Path, "read_text"),
            (Path, "read_bytes"),
            (Path, "write_text"),
            (Path, "write_bytes"),
        ):
            context.setattr(owner, attribute, forbidden)
        constructed = sample_artifacts()
        for name, artifact in constructed.items():
            assert artifact.artifact_id == examples[name].artifact_id
            assert type(artifact).from_json(wires[name]).to_json() == wires[name]
        with pytest.raises(TypeError):
            _construct(examples["observation"], source_value=_ForbiddenMapping())
