"""C04 N01-N18/N52: closed query authority, identity, determinism and governance."""

from __future__ import annotations

import ast
import builtins
import inspect
import io
import json
import os
import socket
import subprocess
import sys
from collections.abc import Callable
from dataclasses import FrozenInstanceError, fields, replace
from datetime import timedelta
from functools import cache
from pathlib import Path
from types import MappingProxyType
from typing import Any, NoReturn, cast

import pytest

from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.enums import TrustLevel
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.decision.temporal import SOURCE_FIELDS
from flowlens.investigation import c04_queries as query_api
from flowlens.investigation import c04_registry as registry
from flowlens.investigation.c02_binding import build_investigation_case
from flowlens.investigation.c03_planning import (
    build_investigation_plan,
    build_investigation_questions,
)
from flowlens.investigation.contracts import (
    EntityKey,
    EvidenceQuerySpec,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
)
from test_c05_policy import make_fixture, neutral_records, unsafe_replace
from test_investigation_planning import _empty_packet, _packet

ROOT = Path(__file__).resolve().parents[1]
type Inputs = tuple[
    DecisionPacket, InvestigationCase, tuple[InvestigationQuestion, ...], InvestigationPlan,
]
type Profile = tuple[tuple[str, ...], str, TrustLevel]
DIRECT = TrustLevel.DIRECT_FACT
EXPECTED_PROFILES: dict[str, tuple[Profile, ...]] = {
    "dim_work_center": ((
        ("active_from", "daily_capacity_hours", "line_group", "process_type",
         "work_center_code", "work_center_id"), "MASTER_DATA_CONTEXT", DIRECT,
    ),),
    "fact_delivery": ((
        ("delivered_quantity", "delivery_at", "delivery_id", "sales_order_id"),
        "DIRECT_EVENT", DIRECT,
    ),),
    "fact_material_requirement": ((
        ("material_id", "material_requirement_id", "need_by_at", "required_quantity",
         "work_order_id"), "DIRECT_FK", DIRECT,
    ),),
    "fact_operation": (
        (("operation_id", "planned_end_at", "planned_start_at", "sequence_number",
          "work_center_id", "work_order_id"), "DIRECT_FK", DIRECT),
        (("actual_end_at", "actual_start_at"), "DIRECT_EVENT", DIRECT),
    ),
    "fact_purchase_order": ((
        ("actual_receipt_at", "material_id", "ordered_at", "ordered_quantity",
         "promised_receipt_at", "purchase_order_id", "received_quantity", "supplier_id"),
        "MATERIAL_TIME_ASSOCIATION", TrustLevel.ASSOCIATIVE_EVIDENCE,
    ),),
    "fact_quality_inspection": ((
        ("defect_category", "failed_quantity", "inspected_quantity", "inspection_at",
         "inspection_id", "inspection_type", "operation_id", "passed_quantity", "result",
         "severity", "work_order_id"), "DIRECT_EVENT", DIRECT,
    ),),
    "fact_rework": ((
        ("inspection_id", "rework_end_at", "rework_id", "rework_quantity", "rework_reason",
         "rework_start_at", "work_center_id", "work_order_id"), "DIRECT_EVENT", DIRECT,
    ),),
    "fact_sales_order": ((
        ("customer_id", "order_at", "order_quantity", "priority", "product_id",
         "promised_delivery_at", "sales_order_id"), "TARGET_RECORD", DIRECT,
    ),),
    "fact_work_order": (
        (("planned_end_at", "planned_quantity", "planned_start_at", "product_id",
          "sales_order_id", "work_order_id"), "DIRECT_FK", DIRECT),
        (("actual_end_at", "actual_start_at", "completed_quantity"), "DIRECT_EVENT", DIRECT),
    ),
}
EXPECTED_KEYS = {
    "dim_work_center": "work_center_id", "fact_delivery": "delivery_id",
    "fact_material_requirement": "material_requirement_id", "fact_operation": "operation_id",
    "fact_purchase_order": "purchase_order_id", "fact_quality_inspection": "inspection_id",
    "fact_rework": "rework_id", "fact_sales_order": "sales_order_id",
    "fact_work_order": "work_order_id",
}
C04_PATHS = [
    "src/flowlens/investigation/c04_navigation.py",
    "src/flowlens/investigation/c04_queries.py",
    "src/flowlens/investigation/c04_registry.py",
]


@cache
def _inputs(empty: bool = False) -> Inputs:
    packet = _empty_packet() if empty else build_decision_packet(*make_fixture([
        record for record in neutral_records() if record[0] == "fact_sales_order"
    ]).args())
    case = build_investigation_case(packet)
    questions = build_investigation_questions(packet, case)
    return packet, case, questions, build_investigation_plan(packet, case, questions)


@cache
def _queries(empty: bool = False) -> tuple[EvidenceQuerySpec, ...]:
    return query_api.build_evidence_query_specs(*_inputs(empty))


def _error(action: Callable[[], object], code: str) -> None:
    with pytest.raises(query_api.C04EvidenceError) as caught:
        action()
    assert caught.value.code == str(caught.value) == code
    assert caught.value.__suppress_context__ or caught.value.__context__ is None


def _query_attack(query: EvidenceQuerySpec) -> None:
    _error(
        lambda: query_api.validate_evidence_query_specs(*_inputs(), (query, *_queries()[1:])),
        "C04_QUERY_SET_MISMATCH",
    )


def _subclass[T](value: T) -> T:
    cls = type("HostileSubclass", (type(value),), {})
    instance: Any = object.__new__(cls)
    for field in fields(cast(Any, value)):
        object.__setattr__(instance, field.name, getattr(value, field.name))
    return cast(T, instance)


class _HostileTuple(tuple[object, ...]):
    def __iter__(self) -> NoReturn:
        raise AssertionError("a collection subclass must be rejected before traversal")


@pytest.mark.parametrize("attack", ["none", "subclass", "identity", "nested_identity"])
def test_n01_packet_exact_type_and_frozen_validation(attack: str) -> None:
    packet, case, questions, plan = _inputs()
    if attack == "none":
        packet = cast(DecisionPacket, None)
    elif attack == "subclass":
        packet = _subclass(packet)
    elif attack == "identity":
        packet = unsafe_replace(packet, packet_id="dpkt_" + "a" * 64)
    else:
        packet = unsafe_replace(packet, run=unsafe_replace(packet.run, run_id="run_" + "a" * 64))
    _error(lambda: query_api.build_evidence_query_specs(packet, case, questions, plan),
           "C04_INVALID_DECISION_PACKET")


@pytest.mark.parametrize("attack", ["none", "subclass", "identity", "root", "time"])
def test_n02_case_binding_is_exact(attack: str) -> None:
    packet, case, questions, plan = _inputs()
    if attack == "none":
        case = cast(InvestigationCase, None)
    elif attack == "subclass":
        case = _subclass(case)
    elif attack == "identity":
        case = unsafe_replace(case, artifact_id="icase_" + "a" * 64)
    elif attack == "root":
        case = replace(case, subject_id="SO-other")
    else:
        case = replace(case, as_of_time=case.as_of_time - timedelta(seconds=1))
    _error(lambda: query_api.build_evidence_query_specs(packet, case, questions, plan),
           "C04_CASE_BINDING_MISMATCH")


@pytest.mark.parametrize("attack", [
    "questions_list", "hostile_tuple", "question_subclass", "question_identity", "omit",
    "reorder", "family", "trust", "plan_subclass", "plan_identity", "step_identity", "steps_list",
])
def test_n03_exact_frozen_questions_and_plan(attack: str) -> None:
    packet, case, questions, plan = _inputs()
    if attack == "questions_list":
        questions = cast(tuple[InvestigationQuestion, ...], list(questions))
    elif attack == "hostile_tuple":
        questions = cast(tuple[InvestigationQuestion, ...], _HostileTuple(questions))
    elif attack == "question_subclass":
        questions = (_subclass(questions[0]), *questions[1:])
    elif attack == "question_identity":
        questions = (unsafe_replace(questions[0], content_hash="a" * 64), *questions[1:])
    elif attack == "omit":
        questions = questions[1:]
    elif attack == "reorder":
        questions = tuple(reversed(questions))
    elif attack == "family":
        questions = (replace(questions[0], required_evidence_families=("dim_supplier",)),
                     *questions[1:])
    elif attack == "trust":
        questions = (replace(questions[0], allowed_trust_classes=(TrustLevel.UNKNOWN,)),
                     *questions[1:])
    elif attack == "plan_subclass":
        plan = _subclass(plan)
    elif attack == "plan_identity":
        plan = unsafe_replace(plan, content_hash="a" * 64)
    elif attack == "step_identity":
        plan = unsafe_replace(plan, steps=(unsafe_replace(plan.steps[0], content_hash="a" * 64),
                                          *plan.steps[1:]))
    else:
        plan = unsafe_replace(plan, steps=list(plan.steps))
    _error(lambda: query_api.build_evidence_query_specs(packet, case, questions, plan),
           "C04_PLANNING_BINDING_MISMATCH")


def test_n01_n03_error_precedence() -> None:
    packet, case, questions, plan = _inputs()
    _error(lambda: query_api.validate_evidence_query_specs(
        cast(DecisionPacket, None), cast(InvestigationCase, None),
        cast(tuple[InvestigationQuestion, ...], None), cast(InvestigationPlan, None),
        cast(tuple[EvidenceQuerySpec, ...], None),
    ), "C04_INVALID_DECISION_PACKET")
    _error(lambda: query_api.validate_evidence_query_specs(
        packet, cast(InvestigationCase, None), (), plan, (),
    ), "C04_CASE_BINDING_MISMATCH")
    _error(lambda: query_api.validate_evidence_query_specs(packet, case, (), plan, ()),
           "C04_PLANNING_BINDING_MISMATCH")
    assert questions


def test_n04_n06_exact_immutable_registry_and_field_partition() -> None:
    assert tuple(registry.C04_SOURCE_REGISTRY) == tuple(EXPECTED_PROFILES)
    assert len(registry.C04_SOURCE_REGISTRY) == 9
    assert sum(len(item.profiles) for item in registry.C04_SOURCE_REGISTRY.values()) == 11
    assert isinstance(registry.C04_SOURCE_REGISTRY, MappingProxyType)
    for family, policy in registry.C04_SOURCE_REGISTRY.items():
        assert policy.primary_key == EXPECTED_KEYS[family]
        assert tuple((p.requested_fields, p.relationship_code, p.trust_class)
                     for p in policy.profiles) == EXPECTED_PROFILES[family]
        assert tuple(field for p in policy.profiles for field in p.requested_fields)
        assert set(field for p in policy.profiles for field in p.requested_fields) == set(
            SOURCE_FIELDS[family]
        )
        for profile in policy.profiles:
            assert profile.requested_fields == tuple(sorted(set(profile.requested_fields)))
            assert "status" not in profile.requested_fields
            with pytest.raises(FrozenInstanceError):
                cast(Any, profile).relationship_code = "FORGED"
        with pytest.raises(FrozenInstanceError):
            cast(Any, policy).primary_key = "forged"
    with pytest.raises(TypeError):
        cast(Any, registry.C04_SOURCE_REGISTRY)["arbitrary"] = object()
    assert registry.C04_SOURCE_REGISTRY_VERSION == "w04-c04-source-registry-v1"
    assert registry.C04_QUERY_CONTRACT_VERSION == "w04-c04-query-v1"
    assert registry.C04_NAVIGATION_CONTRACT_VERSION == "w04-c04-navigation-v1"
    assert registry.C04_ROOT_KEY_NAME == "sales_order_id"
    assert registry.C04_MAX_RECORDS_PER_QUERY == 4096
    assert registry.C04_MAX_OBSERVATIONS_PER_SLICE == 65536


def test_n07_n13_n14_exact_projection_count_and_order() -> None:
    _, case, questions, plan = _inputs()
    actual = _queries()
    by_id = {question.artifact_id: question for question in questions}
    expected: list[EvidenceQuerySpec] = []
    for step in plan.steps:
        question = by_id[step.question_id]
        for family in step.expected_evidence_families:
            assert family in question.required_evidence_families
            assert family in question.allowed_traversal_families
            for requested, relationship, trust in EXPECTED_PROFILES[family]:
                assert trust in question.allowed_trust_classes
                expected.append(EvidenceQuerySpec(
                    case_id=case.artifact_id, plan_id=plan.artifact_id,
                    step_id=step.artifact_id, question_id=question.artifact_id,
                    source_family_code=family,
                    entity_keys=(EntityKey(key_name="sales_order_id", key_value=case.subject_id),),
                    as_of_time=case.as_of_time, requested_fields=requested,
                    allowed_trust_classes=(trust,), expected_relationship_code=relationship,
                ))
    assert canonical_json_bytes(actual) == canonical_json_bytes(tuple(expected))
    assert len(actual) == 18
    assert {query.source_family_code for query in actual} == set(EXPECTED_PROFILES)
    query_api.validate_evidence_query_specs(*_inputs(), actual)


@pytest.mark.parametrize("name", ["C03-G01", "C03-G02", "C03-G16", "NEUTRAL"])
def test_n13_only_profiles_selected_by_real_frozen_signals(name: str) -> None:
    packet = _packet(name)
    case = build_investigation_case(packet)
    questions = build_investigation_questions(packet, case)
    plan = build_investigation_plan(packet, case, questions)
    queries = query_api.build_evidence_query_specs(packet, case, questions, plan)
    assert len(queries) == sum(len(EXPECTED_PROFILES[family]) for step in plan.steps
                               for family in step.expected_evidence_families)
    assert {query.source_family_code for query in queries} == {
        family for step in plan.steps for family in step.expected_evidence_families
    }


def test_n13_zero_step_plan_has_zero_queries() -> None:
    assert _inputs(True)[2] == () and _inputs(True)[3].steps == ()
    assert _queries(True) == ()
    query_api.validate_evidence_query_specs(*_inputs(True), ())
    _error(lambda: query_api.validate_evidence_query_specs(*_inputs(True), _queries()),
           "C04_QUERY_SET_MISMATCH")


@pytest.mark.parametrize("family", [
    "fact_inventory_snapshot", "dim_supplier", "dim_material", "bridge_product_material",
    "arbitrary_table", "https://example.invalid", "DROP_TABLE",
])
def test_n08_unregistered_and_nonplan_families_rejected(family: str) -> None:
    query = _queries()[0]
    _query_attack(unsafe_replace(query, source_family_code=family))
    _query_attack(replace(query, source_family_code="fact_sales_order"))


@pytest.mark.parametrize("attack", ["wrong_name", "wrong_root", "extra", "missing"])
def test_n09_exact_root_key_only(attack: str) -> None:
    query = _queries()[0]
    root = query.entity_keys[0]
    keys = {
        "wrong_name": (replace(root, key_name="work_order_id"),),
        "wrong_root": (replace(root, key_value="SO-other"),),
        "extra": (root, EntityKey(key_name="work_order_id", key_value="WO-1")),
        "missing": (),
    }[attack]
    _query_attack(unsafe_replace(query, entity_keys=keys))


@pytest.mark.parametrize("attack", ["widen", "subset", "reorder", "status", "raw_sql"])
def test_n10_exact_fields_cannot_be_changed(attack: str) -> None:
    query = _queries()[0]
    values = {
        "widen": tuple(sorted((*query.requested_fields, "dataset_version_id"))),
        "subset": query.requested_fields[1:],
        "reorder": tuple(reversed(query.requested_fields)),
        "status": ("status",),
        "raw_sql": ("SELECT * FROM fact_work_order",),
    }[attack]
    _query_attack(unsafe_replace(query, requested_fields=values))


@pytest.mark.parametrize("relationship", ["DIRECT_EVENT", "DIRECT_FK", "CAUSAL_PROOF"])
def test_n11_relationship_cannot_be_changed(relationship: str) -> None:
    _query_attack(replace(_queries()[0], expected_relationship_code=relationship))


@pytest.mark.parametrize("trust", [
    (TrustLevel.DERIVED_FACT,), (TrustLevel.UNKNOWN,), (TrustLevel.FORBIDDEN_INFERENCE,),
    (TrustLevel.DIRECT_FACT, TrustLevel.UNKNOWN), (), ("DIRECT_FACT",),
])
def test_n12_trust_cannot_be_widened_reclassified_or_forged(trust: tuple[object, ...]) -> None:
    _query_attack(unsafe_replace(_queries()[0], allowed_trust_classes=trust))


@pytest.mark.parametrize("attack", ["omit", "duplicate", "reorder", "list", "hostile_tuple"])
def test_n14_exact_query_tuple(attack: str) -> None:
    queries = _queries()
    supplied: object = {
        "omit": queries[1:], "duplicate": (*queries, queries[0]),
        "reorder": tuple(reversed(queries)), "list": list(queries),
        "hostile_tuple": _HostileTuple(queries),
    }[attack]
    _error(lambda: query_api.validate_evidence_query_specs(
        *_inputs(), cast(tuple[EvidenceQuerySpec, ...], supplied),
    ), "C04_QUERY_SET_MISMATCH")


def test_n15_repeated_queries_preserve_input_and_full_envelope() -> None:
    inputs = _inputs()
    before = canonical_json_bytes(inputs)
    first = query_api.build_evidence_query_specs(*inputs)
    second = query_api.build_evidence_query_specs(*inputs)
    assert first is not second and first == second
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert canonical_json_bytes(inputs) == before
    assert tuple(EvidenceQuerySpec.from_json(query.to_json()) for query in first) == first


def test_n16_fresh_process_and_hashseed_determinism() -> None:
    script = """
import sys
sys.path.insert(0, 'tests')
from test_investigation_evidence_queries import _inputs
from flowlens.investigation.c04_queries import build_evidence_query_specs
from flowlens.decision.serialization import canonical_json_bytes
sys.stdout.buffer.write(canonical_json_bytes(build_evidence_query_specs(*_inputs())))
"""
    expected = canonical_json_bytes(_queries())
    for seed in ("0", "1", "14793817"):
        result = subprocess.run([sys.executable, "-B", "-c", script], cwd=ROOT,
                                env=dict(os.environ, PYTHONHASHSEED=seed),
                                check=True, capture_output=True)
        assert result.stdout == expected


@pytest.mark.parametrize("attack", [
    "none", "subclass", "artifact_id", "content_hash", "nested_id", "nested_hash",
    "nested_subclass", "keys_list", "keys_hostile", "case", "plan", "step", "question", "as_of",
])
def test_n17_original_and_nested_identities_and_bindings(attack: str) -> None:
    query = _queries()[0]
    if attack == "none":
        query = cast(EvidenceQuerySpec, None)
    elif attack == "subclass":
        query = _subclass(query)
    elif attack in ("artifact_id", "content_hash"):
        query = unsafe_replace(query, **{attack: "a" * 64})
    elif attack in ("nested_id", "nested_hash"):
        key = unsafe_replace(query.entity_keys[0], **{
            "artifact_id" if attack == "nested_id" else "content_hash": "a" * 64,
        })
        query = unsafe_replace(query, entity_keys=(key,))
    elif attack == "nested_subclass":
        query = unsafe_replace(query, entity_keys=(_subclass(query.entity_keys[0]),))
    elif attack == "keys_list":
        query = unsafe_replace(query, entity_keys=list(query.entity_keys))
    elif attack == "keys_hostile":
        query = unsafe_replace(query, entity_keys=_HostileTuple(query.entity_keys))
    elif attack == "as_of":
        query = replace(query, as_of_time=query.as_of_time + timedelta(seconds=1))
    else:
        original = getattr(query, attack + "_id")
        prefix = original.split("_")[0]
        query = replace(query, **{attack + "_id": prefix + "_" + "a" * 64})
    _query_attack(query)


def test_n18_no_query_language_or_resource_arguments() -> None:
    assert tuple(inspect.signature(query_api.build_evidence_query_specs).parameters) == (
        "packet", "case", "questions", "plan",
    )
    assert tuple(inspect.signature(query_api.validate_evidence_query_specs).parameters) == (
        "packet", "case", "questions", "plan", "queries",
    )
    for field in ("sql", "url", "path", "table", "adapter", "fields", "traversal", "prompt"):
        with pytest.raises(TypeError):
            cast(Any, query_api.build_evidence_query_specs)(*_inputs(), **{field: "untrusted"})


def _capability_violations(source: str) -> tuple[str, ...]:
    forbidden_imports = (
        "sqlalchemy", "psycopg", "sqlite3", "flowlens.db", "flowlens.data", "pathlib",
        "os", "subprocess", "socket", "requests", "httpx", "openai", "anthropic", "mcp",
        "flowlens.decision.c06_store", "flowlens.decision.c07", "flowlens.decision.c08",
        "flowlens.decision.signals", "flowlens.decision.diagnosis", "flowlens.decision.c04",
        "flowlens.investigation.c05",
    )
    forbidden_calls = {"open", "eval", "exec", "compile", "now", "utcnow", "time", "uuid4"}
    violations: list[str] = []
    for node in ast.walk(ast.parse(source)):
        names = ([alias.name for alias in node.names] if isinstance(node, ast.Import) else
                 [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
        violations.extend(name for name in names if any(
            name == prefix or name.startswith(prefix + ".") or name.startswith(prefix + "_")
            for prefix in forbidden_imports
        ))
        if isinstance(node, ast.Call):
            name = (node.func.id if isinstance(node.func, ast.Name) else
                    node.func.attr if isinstance(node.func, ast.Attribute) else "")
            if name in forbidden_calls:
                violations.append(name)
    return tuple(violations)


@pytest.mark.parametrize("source", [
    "import sqlalchemy", "import flowlens.db", "import flowlens.data.scenarios",
    "from pathlib import Path", "import subprocess", "import openai", "import socket",
    "import flowlens.investigation.c05_findings", "open('x')", "eval('1')", "datetime.now()",
])
def test_n52_capability_audit_negative_controls(source: str) -> None:
    assert _capability_violations(source)


def test_n52_pure_runtime_ast_and_fresh_import() -> None:
    for path in C04_PATHS[1:]:
        assert not _capability_violations((ROOT / path).read_text(encoding="utf-8"))
    script = """
import json, sys
import flowlens.decision.temporal, flowlens.investigation.c03_planning
before = set(sys.modules)
import flowlens.investigation.c04_queries, flowlens.investigation.c04_registry
print(json.dumps(sorted(set(sys.modules) - before)))
"""
    result = subprocess.run([sys.executable, "-B", "-c", script], cwd=ROOT,
                            check=True, capture_output=True, text=True)
    assert not _capability_violations("\n".join("import " + name
                                               for name in json.loads(result.stdout)))


def test_n52_valid_projection_survives_blocked_external_capabilities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs = _inputs()
    expected = _queries()

    def forbidden(*args: object, **kwargs: object) -> NoReturn:
        raise AssertionError("C04 query projection attempted an external capability")

    for target, name in (
        (builtins, "open"), (io, "open"), (subprocess, "run"), (subprocess, "Popen"),
        (socket, "socket"), (socket, "create_connection"), (os, "system"),
        (Path, "read_text"), (Path, "read_bytes"), (Path, "write_text"), (Path, "write_bytes"),
    ):
        monkeypatch.setattr(target, name, forbidden)
    assert query_api.build_evidence_query_specs(*inputs) == expected
    query_api.validate_evidence_query_specs(*inputs, expected)


def _assert_lifecycle(entry: dict[str, Any], oid: Callable[[str], str]) -> None:
    assert [source["path"] for source in entry["files"]] == C04_PATHS
    if entry["state"] == "AUTHORIZED":
        assert entry["source_freeze_sha"] is None
        assert all(source["blob_oid"] is None for source in entry["files"])
    elif entry["state"] == "CLOSED":
        freeze = entry["source_freeze_sha"]
        assert isinstance(freeze, str) and len(freeze) == 40
        for source in entry["files"]:
            assert isinstance(source["blob_oid"], str) and len(source["blob_oid"]) == 40
            assert oid(f"{freeze}:{source['path']}") == source["blob_oid"]
            assert oid(f"HEAD:{source['path']}") == source["blob_oid"]
    else:
        raise AssertionError("unauthorized C04 lifecycle state")


@pytest.mark.parametrize("state", ["AUTHORIZED", "CLOSED"])
def test_n52_lifecycle_harness_accepts_authorized_and_future_closed(state: str) -> None:
    freeze = "a" * 40 if state == "CLOSED" else None
    oid = "b" * 40 if state == "CLOSED" else None
    entry = {"state": state, "source_freeze_sha": freeze,
             "files": [{"path": path, "blob_oid": oid} for path in C04_PATHS]}
    _assert_lifecycle(entry, lambda reference: "b" * 40)


def test_n52_committed_source_governance_and_frozen_blobs() -> None:
    def oid(reference: str) -> str:
        return subprocess.run(["git", "rev-parse", reference], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout.strip()

    expected = {
        "src/flowlens/investigation/__init__.py": "c23929f85dccd78bc72ef3b2b1415c6e8eaf0452",
        "src/flowlens/investigation/contracts.py": "0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e",
        "src/flowlens/investigation/enums.py": "9c818780423f32f144b18666784ebc9ea3abdccc",
        "src/flowlens/investigation/c02_binding.py": "5f0af237ed465fa83e5a3b84954512b1f3125551",
        "src/flowlens/investigation/c03_planning.py": "21d0055e12d86e6333a836d363d6e266cb0fcbd7",
        "src/flowlens/decision/temporal.py": "70ae018f4b50ac6ed45e894d6726e9ccee345c8a",
        "src/flowlens/decision/trust.py": "f216d22f1d6862e1eef886dfbe4c3af16f396ec1",
        "src/flowlens/db/decision_snapshot.py": "0323ad4ecf0c50abda42a8ab4714d59861ad98c3",
        "src/flowlens/data/models": "12a1ec70707ff4644b6d6bccb31eec59fb7230d3",
        "scripts/ci/verify_w04_source_evolution.py": "4efaefed505e24796a0c2fa545ce4b7eb252d70a",
        ".github/workflows/ci.yml": "14c826b122b7103953e8b4539981004241205ba4",
    }
    for path, expected_oid in expected.items():
        assert oid(f"HEAD:{path}") == expected_oid
    manifest = json.loads((ROOT / "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json").read_bytes())
    entries = {item["checkpoint"]: item for item in manifest["checkpoints"]}
    assert all(entries[name]["state"] == "CLOSED" for name in ("W04-C01", "W04-C02", "W04-C03"))
    _assert_lifecycle(entries["W04-C04"], oid)
    head = oid("HEAD")
    result = subprocess.run([
        sys.executable, "-B", "scripts/ci/verify_w04_source_evolution.py", "--manifest",
        "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json", "--expected-head", head, "--repo", str(ROOT),
    ], cwd=ROOT, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    proof = json.loads(result.stdout)
    assert proof["overall"] == "PASS" and proof["expected_head"] == head
