"""W04-C05 K01-K48: direct semantic, hostile-envelope and capability proofs."""

from __future__ import annotations

import ast
import builtins
import hashlib
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
from dataclasses import fields, is_dataclass, replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from functools import cache
from pathlib import Path
from typing import Any, NoReturn, cast

import pytest

from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.enums import SignalState, SignalType, TrustLevel
from flowlens.decision.serialization import canonical_json_bytes, canonical_json_text
from flowlens.investigation import c04_navigation as navigation
from flowlens.investigation import c05_findings as c05
from flowlens.investigation.c04_queries import build_evidence_query_specs
from flowlens.investigation.contracts import (
    ConflictRecord,
    EvidenceObservation,
    EvidenceQuerySpec,
    EvidenceSlice,
    FindingRecord,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
    UncertaintyItem,
    UncertaintyRegister,
)
from flowlens.investigation.enums import ConflictType, FindingStatus, UncertaintyType
from test_c05_policy import make_fixture, neutral_records, unsafe_replace
from test_decision_snapshot import AS_OF, sample_records
from test_investigation_evidence_navigation import _Engine, _rows
from test_investigation_planning import _empty_packet, _planning

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src/flowlens/investigation/c05_findings.py"
SOURCE = "src/flowlens/investigation/c05_findings.py"
type Inputs = tuple[
    DecisionPacket,
    InvestigationCase,
    tuple[InvestigationQuestion, ...],
    InvestigationPlan,
    tuple[EvidenceQuerySpec, ...],
    tuple[EvidenceSlice, ...],
]
type Outputs = tuple[tuple[FindingRecord, ...], tuple[ConflictRecord, ...], UncertaintyRegister]

EXPECTED_CODES = {
    SignalType.SUPPLIER_LATE_RECEIPT: "W04_C05_ASSOCIATED_RECEIPT_LATENESS",
    SignalType.MATERIAL_TIMING_RISK: "W04_C05_ASSOCIATED_MATERIAL_TIMING_WARNING",
    SignalType.QUALITY_FAILURE: "W04_C05_RECORDED_QUALITY_FAILURE",
    SignalType.REWORK_PRESENT: "W04_C05_RECORDED_REWORK",
    SignalType.QUALITY_DISPOSITION_UNKNOWN: "W04_C05_QUALITY_DISPOSITION_UNRESOLVED",
    SignalType.QUEUE_DELAY: "W04_C05_START_SLIPPAGE_PROXY",
    SignalType.CAPACITY_PRESSURE: "W04_C05_CAPACITY_PRESSURE_UNRESOLVED",
    SignalType.DELIVERY_RISK: "W04_C05_DELIVERY_COMMITMENT_WARNING",
}


def _dt(day: int) -> datetime:
    return datetime(2026, 1, day, tzinfo=UTC)


@cache
def _upstream(
    unknown: bool = False, empty: bool = False
) -> tuple[
    DecisionPacket,
    InvestigationCase,
    tuple[InvestigationQuestion, ...],
    InvestigationPlan,
    tuple[EvidenceQuerySpec, ...],
]:
    if empty:
        packet = _empty_packet()
    else:
        records = neutral_records()
        if unknown:
            records = [row for row in records if row[0] == "fact_sales_order"]
        else:
            patches: dict[str, dict[str, Any]] = {
                "fact_sales_order": {"promised_delivery_at": _dt(18)},
                "fact_delivery": {"delivered_quantity": 4},
                "fact_purchase_order": {
                    "promised_receipt_at": _dt(12),
                    "actual_receipt_at": _dt(16),
                },
                "fact_quality_inspection": {
                    "failed_quantity": 3,
                    "passed_quantity": 7,
                    "result": "FAIL",
                },
                "fact_operation": {"planned_start_at": _dt(12), "actual_start_at": _dt(14)},
            }
            records = [
                (family, record, dict(values, **patches.get(family, {})))
                for family, record, values in records
            ]
            records.append(next(row for row in sample_records() if row[0] == "fact_rework"))
        packet = build_decision_packet(*make_fixture(records).args())
    packet, case, questions, plan = _planning(packet)
    return packet, case, questions, plan, build_evidence_query_specs(packet, case, questions, plan)


def _records() -> dict[str, list[dict[str, Any]]]:
    rows = _rows()
    patches: dict[str, dict[str, Any]] = {
        "fact_sales_order": {"promised_delivery_at": _dt(18)},
        "fact_delivery": {"delivered_quantity": 4, "delivery_at": _dt(19)},
        "fact_work_order": {
            "actual_start_at": _dt(12),
            "actual_end_at": None,
            "planned_end_at": _dt(19),
            "completed_quantity": 4,
        },
        "fact_operation": {
            "planned_start_at": _dt(12),
            "actual_start_at": _dt(14),
            "actual_end_at": _dt(19),
        },
        "fact_purchase_order": {"promised_receipt_at": _dt(12), "actual_receipt_at": _dt(16)},
        "fact_material_requirement": {"need_by_at": _dt(15)},
        "fact_quality_inspection": {"failed_quantity": 3, "passed_quantity": 7, "result": "FAIL"},
    }
    for family, values in patches.items():
        rows[family][0].update(values)
    return rows


def _observation(
    packet: DecisionPacket,
    query: EvidenceQuerySpec,
    record: str,
    field: str,
    value: Any,
    freshness: str = "FRESH",
    *,
    available: datetime = AS_OF,
    event: datetime | None = None,
) -> EvidenceObservation:
    payload = {
        "navigation_contract_version": "w04-c04-navigation-v1",
        "dataset_version": packet.run.dataset_version,
        "dataset_hash": packet.run.dataset_hash,
        "source_family_code": query.source_family_code,
        "source_record_id": record,
        "source_field": field,
        "source_value": value,
        "event_time": event,
        "available_at": available,
        "freshness_code": freshness,
        "trust_class": query.allowed_trust_classes[0],
        "relationship_code": query.expected_relationship_code,
    }
    return EvidenceObservation(
        source_family_code=query.source_family_code,
        source_record_id=record,
        source_field=field,
        source_value=value,
        available_at=available,
        event_time=event,
        freshness_code=freshness,
        trust_class=query.allowed_trust_classes[0],
        relationship_code=query.expected_relationship_code,
        provenance_ref="c04prov_" + hashlib.sha256(canonical_json_bytes(payload)).hexdigest(),
    )


def _sliced(
    rows: dict[str, list[dict[str, Any]]] | None = None,
    *,
    unknown: bool = False,
    freshness: str = "FRESH",
    empty: bool = False,
) -> Inputs:
    packet, case, questions, plan, queries = _upstream(unknown, empty)
    rows = _records() if rows is None else rows
    slices: list[EvidenceSlice] = []
    for query in queries:
        observations = tuple(
            _observation(
                packet, query, f"{query.source_family_code}:{index}", field, row[field], freshness
            )
            for index, row in enumerate(rows.get(query.source_family_code, []))
            for field in query.requested_fields
            if field in row
        )
        slices.append(
            EvidenceSlice(
                case_id=case.artifact_id,
                plan_id=plan.artifact_id,
                step_id=query.step_id,
                question_id=query.question_id,
                query_id=query.artifact_id,
                as_of_time=query.as_of_time,
                observations=tuple(sorted(observations, key=lambda obs: obs.artifact_id)),
            )
        )
    return packet, case, questions, plan, queries, tuple(slices)


@cache
def _inputs(unknown: bool = False) -> Inputs:
    return _sliced(unknown=unknown)


@cache
def _outputs(unknown: bool = False) -> Outputs:
    return c05.derive_findings_conflicts_uncertainty(*_inputs(unknown))


def _finding(outputs: Outputs, signal: SignalType) -> FindingRecord:
    return next(f for f in outputs[0] if f.finding_code == EXPECTED_CODES[signal])


def _uncertainties(outputs: Outputs, finding: FindingRecord) -> tuple[UncertaintyItem, ...]:
    return tuple(i for i in outputs[2].items if i.question_id == finding.question_id)


def _assert_status(
    rows: dict[str, list[dict[str, Any]]],
    signal: SignalType,
    status: FindingStatus,
    uncertainty: UncertaintyType | None = None,
) -> Outputs:
    inputs = _sliced(rows)
    outputs = c05.derive_findings_conflicts_uncertainty(*inputs)
    finding = _finding(outputs, signal)
    assert finding.status is status
    if uncertainty:
        assert uncertainty in {i.uncertainty_type for i in _uncertainties(outputs, finding)}
    c05.validate_findings_conflicts_uncertainty(*inputs, *outputs)
    return outputs


def _error(action: Callable[[], object], code: str) -> None:
    with pytest.raises(c05.C05FindingError) as caught:
        action()
    assert caught.value.code == code and str(caught.value) == code
    assert caught.value.__cause__ is None and caught.value.__suppress_context__


def _reject_outputs(inputs: Inputs, outputs: Outputs, code: str) -> None:
    _error(lambda: c05.validate_findings_conflicts_uncertainty(*inputs, *outputs), code)


def _one(
    inputs: Inputs,
    change: Callable[[EvidenceObservation], EvidenceObservation],
    *,
    family: str | None = None,
    field: str | None = None,
) -> Inputs:
    slices = list(inputs[5])
    for index, item in enumerate(slices):
        for obs in item.observations:
            if (family is None or obs.source_family_code == family) and (
                field is None or obs.source_field == field
            ):
                altered = tuple(change(o) if o is obs else o for o in item.observations)
                # Hostile originals cannot be legitimized by the enclosing constructor.
                slices[index] = unsafe_replace(item, observations=altered)
                return *inputs[:5], tuple(slices)
    raise AssertionError("fixture field absent")


def _reslice(
    inputs: Inputs,
    change: Callable[[EvidenceObservation], EvidenceObservation],
    family: str,
    field: str,
) -> Inputs:
    slices = tuple(
        replace(
            item,
            observations=tuple(
                sorted(
                    (
                        change(obs)
                        if obs.source_family_code == family and obs.source_field == field
                        else obs
                        for obs in item.observations
                    ),
                    key=lambda obs: obs.artifact_id,
                )
            ),
        )
        for item in inputs[5]
    )
    return *inputs[:5], slices


def _duplicate(
    family: str, field: str, value: Any, *, copies: int = 1, inputs: Inputs | None = None
) -> Inputs:
    inputs = _inputs() if inputs is None else inputs
    slices: list[EvidenceSlice] = []
    for query, item in zip(inputs[4], inputs[5], strict=True):
        obs = next(
            (
                o
                for o in item.observations
                if o.source_family_code == family and o.source_field == field
            ),
            None,
        )
        extra = (
            ()
            if obs is None
            else tuple(
                _observation(
                    inputs[0],
                    query,
                    obs.source_record_id,
                    field,
                    value,
                    available=AS_OF - timedelta(seconds=i + 1),
                )
                for i in range(copies)
            )
        )
        slices.append(
            replace(
                item,
                observations=tuple(
                    sorted((*item.observations, *extra), key=lambda o: o.artifact_id)
                ),
            )
        )
    return *inputs[:5], tuple(slices)


def _parse_like(wire: Any, exemplar: Any) -> Any:
    """Test-only W03 marshalling using declared exemplar types, never textual inference."""
    if is_dataclass(exemplar):
        constructor = cast(Any, type(exemplar))
        return constructor(
            **{
                f.name: _parse_like(wire[f.name], getattr(exemplar, f.name))
                for f in fields(exemplar)
                if f.init
            }
        )
    if type(exemplar) is tuple:
        assert len(wire) == len(exemplar)
        return tuple(
            _parse_like(value, original) for value, original in zip(wire, exemplar, strict=True)
        )
    if isinstance(exemplar, Enum):
        return type(exemplar)(wire)
    if type(exemplar) is datetime:
        return datetime.fromisoformat(wire)
    if type(exemplar) is date:
        return date.fromisoformat(wire)
    if type(exemplar) is Decimal:
        return Decimal(wire)
    return wire


def _wire(inputs: Inputs) -> str:
    return json.dumps(
        {
            "packet": canonical_json_text(inputs[0]),
            "case": inputs[1].to_json(),
            "questions": [q.to_json() for q in inputs[2]],
            "plan": inputs[3].to_json(),
            "queries": [q.to_json() for q in inputs[4]],
            "slices": [s.to_json() for s in inputs[5]],
        }
    )


def _fresh() -> None:
    payload = json.loads(sys.stdin.read())
    packet = _parse_like(json.loads(payload["packet"]), _upstream()[0])
    assert canonical_json_text(packet) == payload["packet"]
    inputs: Inputs = (
        packet,
        InvestigationCase.from_json(payload["case"]),
        tuple(InvestigationQuestion.from_json(q) for q in payload["questions"]),
        InvestigationPlan.from_json(payload["plan"]),
        tuple(EvidenceQuerySpec.from_json(q) for q in payload["queries"]),
        tuple(EvidenceSlice.from_json(s) for s in payload["slices"]),
    )
    assert any(
        type(o.source_value) is str and o.source_field == "ordered_quantity"
        for s in inputs[5]
        for o in s.observations
    )
    outputs = c05.derive_findings_conflicts_uncertainty(*inputs)
    c05.validate_findings_conflicts_uncertainty(*inputs, *outputs)
    print(canonical_json_bytes(outputs).hex())


def _process(source: str, *, seed: str = "0", stdin: str | None = None) -> str:
    env = dict(
        os.environ,
        PYTHONHASHSEED=seed,
        PYTHONPATH=os.pathsep.join((str(ROOT / "src"), str(ROOT / "tests"))),
    )
    result = subprocess.run(
        [sys.executable, "-B", "-c", source],
        cwd=ROOT,
        env=env,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


@pytest.mark.parametrize("defect", ["type", "identity", "nested"])
def test_k01_exact_w03_packet(defect: str) -> None:
    inputs = _inputs()
    bad: Any = (
        object()
        if defect == "type"
        else unsafe_replace(
            inputs[0], **({"packet_id": "bad"} if defect == "identity" else {"signals": ()})
        )
    )
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(bad, *inputs[1:]),
        c05.C05_INVALID_DECISION_PACKET,
    )


@pytest.mark.parametrize("defect", ["type", "identity", "binding"])
def test_k02_exact_case(defect: str) -> None:
    inputs = _inputs()
    bad: Any = (
        object()
        if defect == "type"
        else unsafe_replace(
            inputs[1],
            **(
                {"artifact_id": "bad"}
                if defect == "identity"
                else {"source_decision_packet_id": "bad"}
            ),
        )
    )
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(inputs[0], bad, *inputs[2:]),
        c05.C05_CASE_BINDING_MISMATCH,
    )


@pytest.mark.parametrize("defect", ["list", "omit", "reverse", "identity", "plan"])
def test_k03_exact_planning(defect: str) -> None:
    packet, case, questions, plan, queries, slices = _inputs()
    bad: Any = {
        "list": list(questions),
        "omit": questions[:-1],
        "reverse": tuple(reversed(questions)),
        "identity": (unsafe_replace(questions[0], content_hash="0" * 64), *questions[1:]),
        "plan": questions,
    }[defect]
    if defect == "plan":
        plan = unsafe_replace(plan, content_hash="0" * 64)
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(packet, case, bad, plan, queries, slices),
        c05.C05_PLANNING_BINDING_MISMATCH,
    )


@pytest.mark.parametrize("defect", ["list", "omit", "reverse", "identity", "fields"])
def test_k04_exact_queries(defect: str) -> None:
    inputs = _inputs()
    queries = inputs[4]
    bad: Any = {
        "list": list(queries),
        "omit": queries[:-1],
        "reverse": tuple(reversed(queries)),
        "identity": (unsafe_replace(queries[0], artifact_id="bad"), *queries[1:]),
        "fields": (replace(queries[0], requested_fields=("invented_field",)), *queries[1:]),
    }[defect]
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*inputs[:4], bad, inputs[5]),
        c05.C05_QUERY_SET_MISMATCH,
    )


@pytest.mark.parametrize("defect", ["list", "omit", "reverse", "case", "plan", "query", "time"])
def test_k05_exact_slices(defect: str) -> None:
    inputs = _inputs()
    slices = inputs[5]
    changes: dict[str, Any] = cast(
        dict[str, Any],
        (
            {"case_id": "bad"}
            if defect == "case"
            else {
                "plan": {"plan_id": "bad"},
                "query": {"query_id": "bad"},
                "time": {"as_of_time": AS_OF + timedelta(days=1)},
            }.get(defect, {})
        ),
    )
    bad: Any = (replace(slices[0], **changes), *slices[1:])
    if defect == "list":
        bad = list(slices)
    elif defect == "omit":
        bad = slices[:-1]
    elif defect == "reverse":
        bad = tuple(reversed(slices))
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*inputs[:5], bad),
        c05.C05_EVIDENCE_SET_MISMATCH,
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("artifact_id", "bad"),
        ("content_hash", "0" * 64),
        ("schema_version", "bad"),
        ("available_at", "2026-01-20"),
    ],
)
def test_k06_original_nested_identity(field: str, value: Any) -> None:
    inputs = _one(_inputs(), lambda o: unsafe_replace(o, **{field: value}))
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*inputs), c05.C05_EVIDENCE_SET_MISMATCH
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_family_code", "fact_rework"),
        ("source_field", "invented_field"),
        ("trust_class", TrustLevel.UNKNOWN),
        ("relationship_code", "INVENTED"),
        ("event_time", AS_OF + timedelta(seconds=1)),
        ("freshness_code", "INVENTED"),
    ],
)
def test_k07_exact_observation_binding(field: str, value: Any) -> None:
    inputs = _reslice(
        _inputs(), lambda o: replace(o, **{field: value}), "fact_sales_order", "order_quantity"
    )
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*inputs), c05.C05_EVIDENCE_SET_MISMATCH
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("provenance_ref", "c04prov_" + "0" * 64),
        ("source_value", 11),
        ("source_record_id", "other_record"),
        ("available_at", AS_OF - timedelta(seconds=1)),
    ],
)
def test_k08_provenance_recomputation(field: str, value: Any) -> None:
    inputs = _reslice(
        _inputs(), lambda o: replace(o, **{field: value}), "fact_sales_order", "order_quantity"
    )
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*inputs),
        c05.C05_EVIDENCE_PROVENANCE_MISMATCH,
    )


def test_k09_signal_binding_without_question_code() -> None:
    source = RUNTIME.read_text(encoding="utf-8")
    assert "question_code" not in source
    inputs, outputs = _inputs(), _outputs()
    for question, finding in zip(inputs[2], outputs[0], strict=True):
        signals = [s for s in inputs[0].signals.signals if s.signal_id in question.trigger_refs]
        assert len(signals) == 1 and signals[0].state is not SignalState.INACTIVE
        assert finding.finding_code == EXPECTED_CODES[signals[0].signal_type]


def test_k10_exact_eight_codes() -> None:
    assert {f.finding_code for f in _outputs()[0]} == set(EXPECTED_CODES.values())


@pytest.mark.parametrize("empty", [False, True])
def test_k11_one_per_question(empty: bool) -> None:
    inputs = _sliced(empty=empty)
    outputs = c05.derive_findings_conflicts_uncertainty(*inputs)
    assert tuple(f.question_id for f in outputs[0]) == tuple(q.artifact_id for q in inputs[2])
    c05.validate_findings_conflicts_uncertainty(*inputs, *outputs)


def test_k12_same_process_determinism_and_immutability() -> None:
    inputs = _inputs()
    before = canonical_json_bytes(inputs)
    assert canonical_json_bytes(c05.derive_findings_conflicts_uncertainty(*inputs)) == (
        canonical_json_bytes(c05.derive_findings_conflicts_uncertainty(*inputs))
    )
    assert canonical_json_bytes(inputs) == before


def test_k13_fresh_process_actual_wire_reparse() -> None:
    result = _process(
        "from test_investigation_findings import _fresh; _fresh()", stdin=_wire(_inputs())
    )
    assert result == canonical_json_bytes(_outputs()).hex()


@pytest.mark.parametrize("seed", ["1", "17", "123"])
def test_k14_multiple_hash_seeds(seed: str) -> None:
    result = _process(
        "from test_investigation_findings import _fresh; _fresh()",
        seed=seed,
        stdin=_wire(_inputs()),
    )
    assert result == canonical_json_bytes(_outputs()).hex()


def test_k15_actual_c04_typed_and_wire_parity() -> None:
    packet, case, questions, plan, queries = _upstream()
    engine = _Engine((packet, case, questions, plan))
    engine.connection.rows = _records()
    for rows in engine.connection.rows.values():
        for row in rows:
            row["dataset_version_id"] = packet.run.dataset_version
    slices = navigation.execute_evidence_navigation(engine, packet, case, questions, plan, queries)
    inputs: Inputs = packet, case, questions, plan, queries, slices
    reparsed = tuple(EvidenceSlice.from_json(s.to_json()) for s in slices)
    assert any(type(o.source_value) is Decimal for s in slices for o in s.observations)
    assert any(type(o.source_value) is datetime for s in slices for o in s.observations)
    assert canonical_json_bytes(c05.derive_findings_conflicts_uncertainty(*inputs)) == (
        canonical_json_bytes(c05.derive_findings_conflicts_uncertainty(*inputs[:5], reparsed))
    )
    assert _process(
        "from test_investigation_findings import _fresh; _fresh()", stdin=_wire(inputs)
    ) == (canonical_json_bytes(c05.derive_findings_conflicts_uncertainty(*inputs)).hex())


@pytest.mark.parametrize("defect", ["support", "contradiction"])
def test_k16_unknown_hard_gate_rejects_upgrade(defect: str) -> None:
    inputs, outputs = _inputs(True), _outputs(True)
    assert all(
        f.status is FindingStatus.UNKNOWN
        and not f.supporting_evidence_ids
        and not f.contradicting_evidence_ids
        for f in outputs[0]
    )
    first = outputs[0][0]
    evidence = next(
        o.artifact_id
        for s in inputs[5]
        if s.question_id == first.question_id
        for o in s.observations
    )
    changed = replace(
        first,
        status=(FindingStatus.SUPPORTED if defect == "support" else FindingStatus.CONTRADICTED),
        supporting_evidence_ids=(evidence,) if defect == "support" else (),
        contradicting_evidence_ids=(evidence,) if defect == "contradiction" else (),
    )
    _error(
        lambda: c05.validate_findings_conflicts_uncertainty(
            *inputs, (changed, *outputs[0][1:]), *outputs[1:]
        ),
        c05.C05_FINDING_SET_MISMATCH,
    )


def test_k17_empty_evidence_never_negative_proof() -> None:
    inputs = _sliced({})
    outputs = c05.derive_findings_conflicts_uncertainty(*inputs)
    assert all(
        f.status in (FindingStatus.UNKNOWN, FindingStatus.UNRESOLVED)
        and not f.supporting_evidence_ids
        and not f.contradicting_evidence_ids
        for f in outputs[0]
    )
    assert all(
        UncertaintyType.MISSING_EVIDENCE in {i.uncertainty_type for i in _uncertainties(outputs, f)}
        for f in outputs[0]
    )


def test_k18_forbidden_trust_rejected() -> None:
    inputs = _one(
        _inputs(), lambda o: unsafe_replace(o, trust_class=TrustLevel.FORBIDDEN_INFERENCE)
    )
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*inputs), c05.C05_EVIDENCE_SET_MISMATCH
    )


@pytest.mark.parametrize("freshness", ["STALE", "EXPIRED", "UNKNOWN", "NOT_APPLICABLE"])
def test_k19_freshness_eligibility(freshness: str) -> None:
    outputs = c05.derive_findings_conflicts_uncertainty(*_sliced(freshness=freshness))
    if freshness == "NOT_APPLICABLE":
        assert _finding(outputs, SignalType.QUALITY_FAILURE).status is FindingStatus.SUPPORTED
    else:
        assert all(
            not f.supporting_evidence_ids and not f.contradicting_evidence_ids for f in outputs[0]
        )
        kind = (
            UncertaintyType.UNKNOWN_EVIDENCE
            if freshness == "UNKNOWN"
            else UncertaintyType.STALE_EVIDENCE
        )
        assert kind in {i.uncertainty_type for i in outputs[2].items}


def test_k20_association_never_causal() -> None:
    outputs = _outputs()
    for signal in (SignalType.SUPPLIER_LATE_RECEIPT, SignalType.MATERIAL_TIMING_RISK):
        finding = _finding(outputs, signal)
        assert finding.status is FindingStatus.SUPPORTED and "ASSOCIATED" in finding.finding_code
        assert UncertaintyType.ASSOCIATIVE_ONLY in {
            i.uncertainty_type for i in _uncertainties(outputs, finding)
        }
        changed = replace(finding, finding_code="W04_C05_ROOT_CAUSE")
        altered = tuple(changed if f is finding else f for f in outputs[0])
        _reject_outputs(_inputs(), (altered, *outputs[1:]), c05.C05_FINDING_SET_MISMATCH)


@pytest.mark.parametrize("mode", ["actual_late", "outstanding"])
def test_k21_supplier_support(mode: str) -> None:
    rows = _records()
    if mode == "outstanding":
        rows["fact_purchase_order"][0].update(
            actual_receipt_at=None, received_quantity=Decimal("0")
        )
    _assert_status(
        rows,
        SignalType.SUPPLIER_LATE_RECEIPT,
        FindingStatus.SUPPORTED,
        UncertaintyType.ASSOCIATIVE_ONLY,
    )


def test_k22_supplier_complete_contradiction() -> None:
    rows = _records()
    rows["fact_purchase_order"][0]["promised_receipt_at"] = _dt(18)
    _assert_status(rows, SignalType.SUPPLIER_LATE_RECEIPT, FindingStatus.CONTRADICTED)


@pytest.mark.parametrize(
    "mode", ["no_po", "no_material", "missing_actual", "missing_received", "null_received"]
)
def test_k23_supplier_incomplete(mode: str) -> None:
    rows = _records()
    rows["fact_purchase_order"][0]["promised_receipt_at"] = _dt(18)
    if mode == "no_po":
        rows["fact_purchase_order"] = []
    elif mode == "no_material":
        rows["fact_purchase_order"][0]["material_id"] = "unrelated"
    elif mode == "null_received":
        rows["fact_purchase_order"][0]["received_quantity"] = None
    else:
        del rows["fact_purchase_order"][0][
            "actual_receipt_at" if mode == "missing_actual" else "received_quantity"
        ]
    _assert_status(
        rows,
        SignalType.SUPPLIER_LATE_RECEIPT,
        FindingStatus.UNRESOLVED,
        UncertaintyType.UNKNOWN_EVIDENCE
        if mode == "null_received"
        else UncertaintyType.MISSING_EVIDENCE,
    )


@pytest.mark.parametrize("mode", ["actual", "promise", "asof", "positive_with_gap"])
def test_k24_material_three_predicates(mode: str) -> None:
    rows = _records()
    po = rows["fact_purchase_order"][0]
    if mode in ("promise", "asof"):
        po.update(actual_receipt_at=None, received_quantity=Decimal("0"))
        po["promised_receipt_at"] = _dt(18) if mode == "promise" else _dt(14)
        rows["fact_material_requirement"][0]["need_by_at"] = (
            _dt(25) if mode == "promise" else _dt(15)
        )
        if mode == "promise":
            po["promised_receipt_at"] = _dt(28)
    elif mode == "positive_with_gap":
        del po["received_quantity"]
    _assert_status(
        rows,
        SignalType.MATERIAL_TIMING_RISK,
        FindingStatus.SUPPORTED,
        UncertaintyType.ASSOCIATIVE_ONLY,
    )


def test_k25_material_complete_contradiction() -> None:
    rows = _records()
    rows["fact_material_requirement"][0]["need_by_at"] = _dt(18)
    _assert_status(rows, SignalType.MATERIAL_TIMING_RISK, FindingStatus.CONTRADICTED)


@pytest.mark.parametrize("mode", ["unmatched", "extra_requirement", "missing_need", "null_need"])
def test_k26_material_association_gaps(mode: str) -> None:
    rows = _records()
    rows["fact_material_requirement"][0]["need_by_at"] = _dt(18)
    if mode == "unmatched":
        rows["fact_purchase_order"][0]["material_id"] = "other"
    elif mode == "extra_requirement":
        rows["fact_material_requirement"].append(
            dict(rows["fact_material_requirement"][0], material_id="other")
        )
    elif mode == "missing_need":
        del rows["fact_material_requirement"][0]["need_by_at"]
    else:
        rows["fact_material_requirement"][0]["need_by_at"] = None
    _assert_status(rows, SignalType.MATERIAL_TIMING_RISK, FindingStatus.UNRESOLVED)


@pytest.mark.parametrize(
    "mode,status",
    [
        ("positive", FindingStatus.SUPPORTED),
        ("zero", FindingStatus.CONTRADICTED),
        ("missing", FindingStatus.UNRESOLVED),
        ("null", FindingStatus.UNRESOLVED),
        ("mixed_valid_rows", FindingStatus.SUPPORTED),
    ],
)
def test_k27_quality_quantity(mode: str, status: FindingStatus) -> None:
    rows = _records()
    if mode == "zero":
        rows["fact_quality_inspection"][0].update(
            failed_quantity=0, passed_quantity=10, result="PASS"
        )
    elif mode == "missing":
        rows["fact_quality_inspection"] = []
    elif mode == "null":
        rows["fact_quality_inspection"][0]["failed_quantity"] = None
    elif mode == "mixed_valid_rows":
        rows["fact_quality_inspection"].append(
            dict(
                rows["fact_quality_inspection"][0],
                failed_quantity=0,
                passed_quantity=10,
                result="PASS",
            )
        )
    outputs = _assert_status(rows, SignalType.QUALITY_FAILURE, status)
    if mode == "mixed_valid_rows":
        assert not outputs[1]


@pytest.mark.parametrize(
    "mode,status",
    [
        ("positive", FindingStatus.SUPPORTED),
        ("zero", FindingStatus.CONTRADICTED),
        ("no_rows", FindingStatus.UNRESOLVED),
        ("null", FindingStatus.UNRESOLVED),
    ],
)
def test_k28_rework_explicit_rows(mode: str, status: FindingStatus) -> None:
    rows = _records()
    if mode == "no_rows":
        rows["fact_rework"] = []
    elif mode in ("zero", "null"):
        rows["fact_rework"][0]["rework_quantity"] = 0 if mode == "zero" else None
    _assert_status(
        rows,
        SignalType.REWORK_PRESENT,
        status,
        UncertaintyType.MISSING_EVIDENCE if mode == "no_rows" else None,
    )


def test_k29_disposition_always_unknown() -> None:
    rows = _records()
    rows["fact_quality_inspection"][0].update(failed_quantity=0, passed_quantity=10, result="PASS")
    outputs = _assert_status(rows, SignalType.QUALITY_DISPOSITION_UNKNOWN, FindingStatus.UNKNOWN)
    assert not _finding(outputs, SignalType.QUALITY_DISPOSITION_UNKNOWN).contradicting_evidence_ids


@pytest.mark.parametrize("mode", ["started_late", "explicit_not_started"])
def test_k30_queue_proxy_support(mode: str) -> None:
    rows = _records()
    if mode == "explicit_not_started":
        rows["fact_operation"][0]["actual_start_at"] = None
    outputs = _assert_status(rows, SignalType.QUEUE_DELAY, FindingStatus.SUPPORTED)
    assert _finding(outputs, SignalType.QUEUE_DELAY).finding_code == "W04_C05_START_SLIPPAGE_PROXY"


@pytest.mark.parametrize(
    "mode,status",
    [
        ("on_time", FindingStatus.CONTRADICTED),
        ("not_yet_due", FindingStatus.CONTRADICTED),
        ("missing_field", FindingStatus.UNRESOLVED),
        ("no_rows", FindingStatus.UNRESOLVED),
    ],
)
def test_k31_queue_proxy_complete_scope(mode: str, status: FindingStatus) -> None:
    rows = _records()
    if mode == "on_time":
        rows["fact_operation"][0]["actual_start_at"] = _dt(12)
    elif mode == "not_yet_due":
        rows["fact_operation"][0].update(planned_start_at=_dt(25), actual_start_at=None)
    elif mode == "missing_field":
        del rows["fact_operation"][0]["actual_start_at"]
    else:
        rows["fact_operation"] = []
    _assert_status(rows, SignalType.QUEUE_DELAY, status)


def test_k32_capacity_always_unknown() -> None:
    rows = _records()
    rows["dim_work_center"][0]["daily_capacity_hours"] = Decimal("0")
    outputs = _assert_status(rows, SignalType.CAPACITY_PRESSURE, FindingStatus.UNKNOWN)
    assert not _finding(outputs, SignalType.CAPACITY_PRESSURE).supporting_evidence_ids


@pytest.mark.parametrize("mode", ["overdue", "plan_with_remaining"])
def test_k33_delivery_warning_support(mode: str) -> None:
    rows = _records()
    if mode == "plan_with_remaining":
        rows["fact_sales_order"][0]["promised_delivery_at"] = _dt(25)
        rows["fact_work_order"][0]["planned_end_at"] = _dt(28)
    _assert_status(rows, SignalType.DELIVERY_RISK, FindingStatus.SUPPORTED)


@pytest.mark.parametrize("mode", ["fulfilled", "no_work_order", "missing_promise"])
def test_k34_delivery_fulfilled_contradiction(mode: str) -> None:
    rows = _records()
    rows["fact_delivery"][0]["delivered_quantity"] = 10
    if mode == "no_work_order":
        rows["fact_work_order"] = []
    elif mode == "missing_promise":
        del rows["fact_sales_order"][0]["promised_delivery_at"]
    _assert_status(rows, SignalType.DELIVERY_RISK, FindingStatus.CONTRADICTED)


@pytest.mark.parametrize(
    "mode",
    [
        "no_rows",
        "missing_quantity",
        "null_quantity",
        "before_deadline_no_warning",
        "missing_actual",
    ],
)
def test_k35_delivery_never_default_zero(mode: str) -> None:
    rows = _records()
    if mode == "no_rows":
        rows["fact_delivery"] = []
    elif mode == "missing_quantity":
        del rows["fact_delivery"][0]["delivered_quantity"]
    elif mode == "null_quantity":
        rows["fact_delivery"][0]["delivered_quantity"] = None
    else:
        rows["fact_sales_order"][0]["promised_delivery_at"] = _dt(25)
        if mode == "missing_actual":
            rows["fact_work_order"][0]["planned_end_at"] = _dt(28)
            del rows["fact_work_order"][0]["actual_end_at"]
    _assert_status(rows, SignalType.DELIVERY_RISK, FindingStatus.UNRESOLVED)


@pytest.mark.parametrize(
    "family,start,end,code,signal",
    [
        (
            "fact_work_order",
            "actual_start_at",
            "actual_end_at",
            "WORK_ORDER_ACTUAL_WINDOW",
            SignalType.DELIVERY_RISK,
        ),
        (
            "fact_operation",
            "actual_start_at",
            "actual_end_at",
            "OPERATION_ACTUAL_WINDOW",
            SignalType.QUEUE_DELAY,
        ),
        (
            "fact_rework",
            "rework_start_at",
            "rework_end_at",
            "REWORK_WINDOW",
            SignalType.REWORK_PRESENT,
        ),
        (
            "fact_purchase_order",
            "ordered_at",
            "actual_receipt_at",
            "PO_RECEIPT_BEFORE_ORDER",
            SignalType.SUPPLIER_LATE_RECEIPT,
        ),
        (
            "fact_delivery",
            "order_at",
            "delivery_at",
            "DELIVERY_BEFORE_ORDER",
            SignalType.DELIVERY_RISK,
        ),
    ],
)
def test_k36_closed_timestamp_conflicts(
    family: str, start: str, end: str, code: str, signal: SignalType
) -> None:
    rows = _records()
    rows["fact_sales_order" if family == "fact_delivery" else family][0][start] = _dt(18)
    rows[family][0][end] = _dt(17)
    outputs = _assert_status(
        rows, signal, FindingStatus.UNRESOLVED, UncertaintyType.CONFLICTING_EVIDENCE
    )
    assert any(
        c.conflict_code == "C05_CONFLICT_" + code
        and c.conflict_type is ConflictType.TIMESTAMP_CONFLICT
        for c in outputs[1]
    )


@pytest.mark.parametrize(
    "family,field,value,code,signal",
    [
        (
            "fact_quality_inspection",
            "passed_quantity",
            6,
            "QUALITY_RESULT_QUANTITY",
            SignalType.QUALITY_FAILURE,
        ),
        (
            "fact_quality_inspection",
            "result",
            "PASS",
            "QUALITY_RESULT_QUANTITY",
            SignalType.QUALITY_FAILURE,
        ),
        (
            "fact_purchase_order",
            "received_quantity",
            Decimal("21"),
            "PO_QUANTITY_EXCEEDS_ORDERED",
            SignalType.SUPPLIER_LATE_RECEIPT,
        ),
        (
            "fact_work_order",
            "completed_quantity",
            11,
            "WO_COMPLETION_EXCEEDS_PLANNED",
            SignalType.DELIVERY_RISK,
        ),
        (
            "fact_delivery",
            "delivered_quantity",
            11,
            "DELIVERY_EXCEEDS_ORDER",
            SignalType.DELIVERY_RISK,
        ),
    ],
)
def test_k37_closed_value_conflicts(
    family: str, field: str, value: Any, code: str, signal: SignalType
) -> None:
    rows = _records()
    rows[family][0][field] = value
    outputs = _assert_status(rows, signal, FindingStatus.UNRESOLVED)
    assert any(
        c.conflict_code == "C05_CONFLICT_" + code and c.conflict_type is ConflictType.VALUE_CONFLICT
        for c in outputs[1]
    )


def test_k38_support_contradiction_conflict() -> None:
    inputs = _duplicate("fact_quality_inspection", "failed_quantity", 0)
    outputs = c05.derive_findings_conflicts_uncertainty(*inputs)
    finding = _finding(outputs, SignalType.QUALITY_FAILURE)
    assert finding.status is FindingStatus.UNRESOLVED
    assert finding.supporting_evidence_ids and finding.contradicting_evidence_ids
    assert not set(finding.supporting_evidence_ids) & set(finding.contradicting_evidence_ids)
    assert {c.conflict_code for c in outputs[1]} == {
        "C05_CONFLICT_DUPLICATE_FIELD_VALUE",
        "C05_CONFLICT_SUPPORT_VS_CONTRADICTION",
    }
    assert any(c.conflict_type is ConflictType.DIRECT_VS_DIRECT for c in outputs[1])
    c05.validate_findings_conflicts_uncertainty(*inputs, *outputs)


@pytest.mark.parametrize("unknown,copies", [(False, 1), (False, 5), (True, 5)])
def test_k39_no_majority_vote_or_unknown_resolution(unknown: bool, copies: int) -> None:
    inputs = _duplicate(
        "fact_quality_inspection", "failed_quantity", 0, copies=copies, inputs=_inputs(unknown)
    )
    outputs = c05.derive_findings_conflicts_uncertainty(*inputs)
    finding = _finding(outputs, SignalType.QUALITY_FAILURE)
    assert finding.status is (FindingStatus.UNKNOWN if unknown else FindingStatus.UNRESOLVED)
    assert finding.related_conflict_ids
    if unknown:
        assert not finding.supporting_evidence_ids and not finding.contradicting_evidence_ids


def test_k40_bounded_uncertainty_projection() -> None:
    rows = _records()
    rows["fact_rework"] = []
    rows["fact_operation"][0]["actual_start_at"] = None
    inputs = _duplicate("fact_quality_inspection", "failed_quantity", 0, inputs=_sliced(rows))
    outputs = c05.derive_findings_conflicts_uncertainty(*inputs)
    stale = c05.derive_findings_conflicts_uncertainty(*_sliced(freshness="STALE"))
    assert {i.uncertainty_type for i in (*outputs[2].items, *stale[2].items)} == set(
        UncertaintyType
    )
    assert all(
        i.uncertainty_code == "C05_UNCERTAINTY_" + i.uncertainty_type.value
        for i in outputs[2].items
    )


def test_k41_forbidden_codes_preserved_exactly() -> None:
    inputs, outputs = _inputs(), _outputs()
    for question in inputs[2]:
        items = [
            i
            for i in outputs[2].items
            if i.question_id == question.artifact_id
            and i.uncertainty_type is UncertaintyType.FORBIDDEN_INFERENCE
        ]
        assert len(items) == 1
        assert items[0].related_refs == tuple(
            sorted((question.artifact_id, *question.forbidden_inference_codes))
        )


def test_k42_conflicting_uncertainty_exact_refs() -> None:
    outputs = c05.derive_findings_conflicts_uncertainty(
        *_duplicate("fact_quality_inspection", "failed_quantity", 0)
    )
    for item in outputs[2].items:
        if item.uncertainty_type is UncertaintyType.CONFLICTING_EVIDENCE:
            conflicts = [c for c in outputs[1] if c.question_id == item.question_id]
            assert set(item.related_refs) == {
                item.question_id,
                *(ref for c in conflicts for ref in (c.artifact_id, *c.evidence_ids)),
            }


def test_k43_register_sorted_case_question_integrity() -> None:
    inputs, outputs = _inputs(), _outputs()
    register = outputs[2]
    assert register.case_id == inputs[1].artifact_id
    ids = tuple(i.artifact_id for i in register.items)
    assert ids == tuple(sorted(set(ids)))
    assert all(
        i.case_id == register.case_id and i.question_id in {q.artifact_id for q in inputs[2]}
        for i in register.items
    )
    assert canonical_json_bytes(UncertaintyRegister.from_json(register.to_json())) == (
        canonical_json_bytes(register)
    )


@pytest.mark.parametrize(
    "kind",
    [
        "injected",
        "cross_question",
        "conflict",
        "uncertainty",
        "uncertainty_business_ref",
        "conflict_evidence",
    ],
)
def test_k44_references_are_question_scoped(kind: str) -> None:
    inputs = _duplicate("fact_quality_inspection", "failed_quantity", 0)
    outputs = c05.derive_findings_conflicts_uncertainty(*inputs)
    findings, conflicts, register = outputs
    target = _finding(outputs, SignalType.QUALITY_FAILURE)
    if kind in ("injected", "cross_question"):
        ref = (
            "injected"
            if kind == "injected"
            else next(
                o.artifact_id
                for s in inputs[5]
                if s.question_id != target.question_id
                for o in s.observations
            )
        )
        changed = replace(target, supporting_evidence_ids=(ref,), contradicting_evidence_ids=())
        findings = tuple(changed if f is target else f for f in findings)
    elif kind in ("conflict", "uncertainty"):
        changed = (
            replace(target, related_conflict_ids=("injected",))
            if kind == "conflict"
            else replace(target, uncertainty_item_ids=("injected",))
        )
        findings = tuple(changed if f is target else f for f in findings)
    elif kind == "conflict_evidence":
        conflicts = (
            replace(conflicts[0], evidence_ids=("injected_a", "injected_b")),
            *conflicts[1:],
        )
    else:
        changed_item = replace(register.items[0], related_refs=("SO-1",))
        register = replace(
            register,
            items=tuple(sorted((changed_item, *register.items[1:]), key=lambda i: i.artifact_id)),
        )
    _error(
        lambda: c05.validate_findings_conflicts_uncertainty(*inputs, findings, conflicts, register),
        c05.C05_OUTPUT_REFERENCE_MISMATCH,
    )


@pytest.mark.parametrize(
    "kind",
    [
        "finding_identity",
        "finding_hash",
        "finding_status",
        "finding_code",
        "finding_order",
        "finding_omit",
        "conflict_identity",
        "conflict_code",
        "conflict_omit",
        "register_identity",
        "register_hash",
        "item_identity",
        "item_code",
        "item_omit",
        "item_inject",
        "register_order",
    ],
)
def test_k45_output_tamper_rejected(kind: str) -> None:
    inputs = _duplicate("fact_quality_inspection", "failed_quantity", 0)
    findings, conflicts, register = c05.derive_findings_conflicts_uncertainty(*inputs)
    code = c05.C05_FINDING_SET_MISMATCH
    if kind == "finding_order":
        findings = tuple(reversed(findings))
    elif kind == "finding_omit":
        findings = findings[:-1]
    elif kind.startswith("finding"):
        changes: dict[str, Any] = cast(
            dict[str, Any],
            {
                "finding_identity": {"artifact_id": "bad"},
                "finding_hash": {"content_hash": "0" * 64},
                "finding_status": {"status": FindingStatus.UNRESOLVED},
                "finding_code": {"finding_code": "W04_C05_INVENTED"},
            }[kind],
        )
        first = findings[0]
        changed = (
            unsafe_replace(first, **changes)
            if kind in ("finding_identity", "finding_hash")
            else replace(first, **changes)
        )
        findings = changed, *findings[1:]
    elif kind.startswith("conflict"):
        code = c05.C05_CONFLICT_SET_MISMATCH
        if kind == "conflict_omit":
            conflicts = conflicts[:-1]
        else:
            changed_conflict = (
                unsafe_replace(conflicts[0], artifact_id="bad")
                if kind == "conflict_identity"
                else replace(conflicts[0], conflict_code="C05_CONFLICT_INVENTED")
            )
            conflicts = changed_conflict, *conflicts[1:]
    else:
        code = c05.C05_UNCERTAINTY_REGISTER_MISMATCH
        if kind in ("register_identity", "register_hash"):
            register = unsafe_replace(
                register,
                **(
                    {"artifact_id": "bad"}
                    if kind == "register_identity"
                    else {"content_hash": "0" * 64}
                ),
            )
        elif kind in ("item_identity", "item_code"):
            changed_item = (
                unsafe_replace(register.items[0], artifact_id="bad")
                if kind == "item_identity"
                else replace(register.items[0], uncertainty_code="C05_UNCERTAINTY_INVENTED")
            )
            register = unsafe_replace(register, items=(changed_item, *register.items[1:]))
        elif kind == "item_omit":
            register = replace(register, items=register.items[:-1])
        elif kind == "item_inject":
            extra = replace(register.items[0], uncertainty_code="C05_UNCERTAINTY_INVENTED")
            register = replace(
                register, items=tuple(sorted((*register.items, extra), key=lambda i: i.artifact_id))
            )
        else:
            register = unsafe_replace(register, items=tuple(reversed(register.items)))
    _error(
        lambda: c05.validate_findings_conflicts_uncertainty(*inputs, findings, conflicts, register),
        code,
    )


@pytest.mark.parametrize(
    "code",
    ["CAUSE", "ROOT_CAUSE", "PROBABILITY", "LIKELIHOOD", "EFFICACY", "REMEDY", "OPTIMAL_ACTION"],
)
def test_k46_no_semantic_authority_expansion(code: str) -> None:
    outputs = _outputs()
    changed = replace(outputs[0][0], finding_code="W04_C05_" + code)
    _error(
        lambda: c05.validate_findings_conflicts_uncertainty(
            *_inputs(), (changed, *outputs[0][1:]), *outputs[1:]
        ),
        c05.C05_FINDING_SET_MISMATCH,
    )
    parameters = {
        arg.arg
        for node in ast.walk(ast.parse(RUNTIME.read_text(encoding="utf-8")))
        if isinstance(node, ast.FunctionDef)
        and node.name
        in ("derive_findings_conflicts_uncertainty", "validate_findings_conflicts_uncertainty")
        for arg in node.args.args
    }
    assert not parameters & {"engine", "connection", "session", "model", "tool", "action"}


_FORBIDDEN_IMPORTS = (
    "sqlalchemy",
    "psycopg",
    "flowlens.db",
    "flowlens.data",
    "flowlens.evaluation",
    "flowlens.investigation.c04_navigation",
    "pathlib",
    "os",
    "subprocess",
    "socket",
    "sqlite3",
    "requests",
    "httpx",
    "openai",
    "urllib",
    "importlib",
    "random",
    "secrets",
    "time",
)
_FORBIDDEN_CALLS = frozenset(
    {
        "open",
        "eval",
        "exec",
        "__import__",
        "now",
        "utcnow",
        "today",
        "read_text",
        "read_bytes",
        "write_text",
        "write_bytes",
        "connect",
        "execute",
        "getenv",
        "system",
        "Popen",
        "run",
    }
)


def _violations(source: str) -> tuple[str, ...]:
    violations: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = (
                [a.name for a in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
            violations.extend(
                name
                for name in names
                if any(name == bad or name.startswith(bad + ".") for bad in _FORBIDDEN_IMPORTS)
            )
            if isinstance(node, ast.ImportFrom):
                violations.extend(a.name for a in node.names if a.name in _FORBIDDEN_CALLS)
        if isinstance(node, ast.Call):
            name = (
                node.func.id
                if isinstance(node.func, ast.Name)
                else node.func.attr
                if isinstance(node.func, ast.Attribute)
                else ""
            )
            if name in _FORBIDDEN_CALLS:
                violations.append(name)
    return tuple(violations)


@pytest.mark.parametrize(
    "source",
    [
        "import sqlalchemy.orm",
        "from flowlens.db import models",
        "from flowlens.investigation.c04_navigation import execute_evidence_navigation",
        "import flowlens.data.scenarios.ground_truth as hgt",
        "from openai import OpenAI as model",
        "import pathlib as p; p.Path('x').read_text()",
        "import os as o; o.getenv('x')",
        "import socket as s; s.socket()",
        "import subprocess as s; s.run([])",
        "from builtins import eval as e; e('1')",
        "exec('x')",
        "__import__('random')",
        "from datetime import datetime as d; d.now()",
        "open('x')",
        "import secrets as s",
        "from time import time as clock",
        "import requests as r",
        "import httpx as h",
    ],
)
def test_k47_capability_audit_negative_controls(source: str) -> None:
    assert _violations(source)


def test_k47_runtime_ast_and_fresh_import() -> None:
    assert not _violations(RUNTIME.read_text(encoding="utf-8"))
    result = _process(
        "import sys; import flowlens.investigation.c05_findings; "
        "blocked=('sqlalchemy','psycopg','flowlens.db','flowlens.data','flowlens.evaluation',"
        "'flowlens.investigation.c04_navigation','openai','httpx','requests'); "
        "assert not any(n==p or n.startswith(p+'.') for n in sys.modules for p in blocked); "
        "print('PURE')"
    )
    assert result == "PURE"


def test_k47_live_external_capability_denial(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs, expected = _inputs(), _outputs()
    before = canonical_json_bytes(inputs)

    def denied(*args: Any, **kwargs: Any) -> NoReturn:
        raise AssertionError("C05 attempted an external capability")

    with monkeypatch.context() as traps:
        for owner, name in (
            (builtins, "open"),
            (io, "open"),
            (Path, "read_text"),
            (Path, "read_bytes"),
            (Path, "write_text"),
            (Path, "write_bytes"),
            (subprocess, "run"),
            (subprocess, "Popen"),
            (socket, "socket"),
            (socket, "create_connection"),
            (sqlite3, "connect"),
            (os, "getenv"),
            (os, "system"),
            (random, "random"),
            (secrets, "token_hex"),
            (time, "time"),
            (navigation, "execute_evidence_navigation"),
            (_Engine, "connect"),
        ):
            traps.setattr(owner, name, denied)
        actual = c05.derive_findings_conflicts_uncertainty(*inputs)
        c05.validate_findings_conflicts_uncertainty(*inputs, *actual)
        assert canonical_json_bytes(actual) == canonical_json_bytes(expected)
        assert canonical_json_bytes(inputs) == before


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _lifecycle(entry: dict[str, Any]) -> None:
    assert entry["checkpoint"] == "W04-C05" and len(entry["files"]) == 1
    assert entry["files"][0]["path"] == SOURCE
    if entry["state"] == "AUTHORIZED":
        assert entry["source_freeze_sha"] is None and entry["files"][0]["blob_oid"] is None
    elif entry["state"] == "CLOSED":
        freeze, blob = entry["source_freeze_sha"], entry["files"][0]["blob_oid"]
        assert type(freeze) is str and len(freeze) == 40 and type(blob) is str and len(blob) == 40
        _git("merge-base", "--is-ancestor", freeze, "HEAD")
        assert _git("rev-parse", freeze + ":" + SOURCE) == blob
        assert _git("rev-parse", "HEAD:" + SOURCE) == blob
    else:
        raise AssertionError("unsupported C05 lifecycle")


@pytest.mark.parametrize("state", ["AUTHORIZED", "CLOSED"])
def test_k48_committed_source_lifecycle_and_verifier(state: str) -> None:
    manifest = json.loads((ROOT / "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json").read_bytes())
    entry = next(e for e in manifest["checkpoints"] if e["checkpoint"] == "W04-C05")
    _lifecycle(entry)
    # A read-only future-shape proof uses real committed source identities, without closing C05.
    modeled = json.loads(json.dumps(manifest))
    c05_entry = next(e for e in modeled["checkpoints"] if e["checkpoint"] == "W04-C05")
    c05_entry["state"] = state
    c05_entry["source_freeze_sha"] = (
        _git("log", "-1", "--format=%H", "--", SOURCE) if (state == "CLOSED") else None
    )
    c05_entry["files"][0]["blob_oid"] = (
        _git("rev-parse", "HEAD:" + SOURCE) if (state == "CLOSED") else None
    )
    _lifecycle(c05_entry)
    assert (
        _process(
            "import sys; sys.path.insert(0,'scripts/ci'); "
            "import verify_w04_source_evolution as v; "
            "v.parse_manifest(sys.stdin.buffer.read()); print('VALID')",
            stdin=json.dumps(modeled),
        )
        == "VALID"
    )
    head = _git("rev-parse", "HEAD")
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "scripts/ci/verify_w04_source_evolution.py",
            "--manifest",
            "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json",
            "--expected-head",
            head,
            "--repo",
            str(ROOT),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    proof = json.loads(result.stdout)
    assert proof["overall"] == "PASS" and proof["expected_head"] == head
    assert SOURCE in proof["actual_added_source_paths"]


@pytest.mark.parametrize(
    "family,field,value",
    [
        ("fact_purchase_order", "ordered_quantity", "NaN"),
        ("fact_purchase_order", "ordered_quantity", "Infinity"),
        ("fact_purchase_order", "received_quantity", Decimal("-1")),
        ("fact_purchase_order", "ordered_quantity", "2e1"),
        ("fact_purchase_order", "ordered_quantity", 20),
        ("fact_purchase_order", "ordered_quantity", 20.0),
        ("fact_sales_order", "order_quantity", "10"),
        ("fact_sales_order", "order_quantity", True),
        ("fact_sales_order", "order_quantity", -1),
        ("fact_operation", "actual_start_at", "2026-01-14T00:00:00"),
        ("fact_operation", "actual_start_at", "nonsense"),
        ("fact_operation", "actual_start_at", datetime(2026, 1, 14)),
        ("fact_material_requirement", "material_id", 1),
        ("fact_quality_inspection", "result", "RELEASED"),
    ],
)
def test_k15_closed_scalar_decoder_rejects_malformed(family: str, field: str, value: Any) -> None:
    if type(value) is float or (type(value) is datetime and value.tzinfo is None):
        inputs = _one(
            _inputs(), lambda o: unsafe_replace(o, source_value=value), family=family, field=field
        )
    else:
        rows = _records()
        rows[family][0][field] = value
        inputs = _sliced(rows)
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*inputs), c05.C05_EVIDENCE_VALUE_INVALID
    )


def test_k07_future_actual_cannot_hide_in_source_value() -> None:
    rows = _records()
    rows["fact_operation"][0]["actual_start_at"] = AS_OF + timedelta(seconds=1)
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*_sliced(rows)),
        c05.C05_EVIDENCE_SET_MISMATCH,
    )


def test_k06_nested_collection_and_identity_type_checked_before_refresh() -> None:
    inputs = _one(_inputs(), lambda o: unsafe_replace(o, content_hash=True))
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*inputs), c05.C05_EVIDENCE_SET_MISMATCH
    )
    items = _inputs()[5]
    bad = unsafe_replace(items[0], observations=list(items[0].observations))
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*_inputs()[:5], (bad, *items[1:])),
        c05.C05_EVIDENCE_SET_MISMATCH,
    )


def test_k06_missing_original_slots_rejected() -> None:
    def stripped(obs: EvidenceObservation) -> EvidenceObservation:
        clone = unsafe_replace(obs)
        object.__delattr__(clone, "source_value")
        return clone

    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*_one(_inputs(), stripped)),
        c05.C05_EVIDENCE_SET_MISMATCH,
    )
    item = unsafe_replace(_inputs()[5][0])
    object.__delattr__(item, "observations")
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(
            *_inputs()[:5], (item, *_inputs()[5][1:])
        ),
        c05.C05_EVIDENCE_SET_MISMATCH,
    )


def test_k20_associative_trust_cannot_be_promoted_to_direct() -> None:
    inputs = _reslice(
        _inputs(),
        lambda o: replace(o, trust_class=TrustLevel.DIRECT_FACT),
        "fact_purchase_order",
        "actual_receipt_at",
    )
    _error(
        lambda: c05.derive_findings_conflicts_uncertainty(*inputs), c05.C05_EVIDENCE_SET_MISMATCH
    )


def test_k45_missing_register_slots_rejected() -> None:
    register = unsafe_replace(_outputs()[2])
    object.__delattr__(register, "items")
    _reject_outputs(_inputs(), (*_outputs()[:2], register), c05.C05_UNCERTAINTY_REGISTER_MISMATCH)
