"""W04-C03 P01-P40: bounded projection, semantic enforcement and pure planning."""

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
import uuid
from collections.abc import Callable
from dataclasses import FrozenInstanceError, fields, replace
from datetime import timedelta
from enum import StrEnum
from functools import cache, lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any, NoReturn, cast

import pytest

from flowlens.decision import diagnosis as w03_diagnosis
from flowlens.decision import signals as w03_signals
from flowlens.decision.c03_policy import COMMON_LIMITATION_CODES, SIGNAL_POLICIES
from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.c06_validation import validate_c05_packet
from flowlens.decision.contracts import DecisionPacket, Signal, SignalBundle
from flowlens.decision.enums import (
    ClaimType,
    SignalState,
    SignalType,
    TrustLevel,
    UncertaintyStatus,
)
from flowlens.decision.primitives import DiagnosisClaim, EntityRef, Limitation, Uncertainty
from flowlens.decision.serialization import canonical_json_bytes, derive_artifact_id
from flowlens.investigation import c02_binding as binding
from flowlens.investigation import c03_planning as planning
from flowlens.investigation.contracts import (
    EvidenceQuerySpec,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
    InvestigationStep,
)
from test_c03_signals import CASES, _records_for_case
from test_c05_policy import make_fixture, neutral_records, unsafe_replace
from test_investigation_case_binding import _minimal_packet, _rebind_packet

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src/flowlens/investigation/c03_planning.py"
INVALID = "C03_INVALID_DECISION_PACKET"
BINDING = "C03_CASE_BINDING_MISMATCH"
SEMANTIC = "C03_W03_SEMANTIC_MISMATCH"
QUESTIONS = "C03_QUESTION_SET_MISMATCH"
PLAN = "C03_PLAN_BINDING_MISMATCH"
VERSION = "w04-c03-v1"
FAMILIES = {
    SignalType.CAPACITY_PRESSURE: ("dim_work_center", "fact_operation"),
    SignalType.DELIVERY_RISK: ("fact_delivery", "fact_sales_order", "fact_work_order"),
    SignalType.MATERIAL_TIMING_RISK: ("fact_material_requirement", "fact_purchase_order"),
    SignalType.QUALITY_DISPOSITION_UNKNOWN: ("fact_quality_inspection", "fact_rework"),
    SignalType.QUALITY_FAILURE: ("fact_quality_inspection",),
    SignalType.QUEUE_DELAY: ("fact_operation",),
    SignalType.REWORK_PRESENT: ("fact_quality_inspection", "fact_rework"),
    SignalType.SUPPLIER_LATE_RECEIPT: ("fact_material_requirement", "fact_purchase_order"),
}
ASSOCIATIVE_TRUST = (
    TrustLevel.ASSOCIATIVE_EVIDENCE,
    TrustLevel.DIRECT_FACT,
    TrustLevel.UNKNOWN,
)
FACT_TRUST = (TrustLevel.DIRECT_FACT, TrustLevel.UNKNOWN)
DERIVED_TRUST = (TrustLevel.DERIVED_FACT, TrustLevel.DIRECT_FACT, TrustLevel.UNKNOWN)
TRUST = {
    SignalType.CAPACITY_PRESSURE: FACT_TRUST,
    SignalType.DELIVERY_RISK: DERIVED_TRUST,
    SignalType.MATERIAL_TIMING_RISK: ASSOCIATIVE_TRUST,
    SignalType.QUALITY_DISPOSITION_UNKNOWN: DERIVED_TRUST,
    SignalType.QUALITY_FAILURE: FACT_TRUST,
    SignalType.QUEUE_DELAY: DERIVED_TRUST,
    SignalType.REWORK_PRESENT: FACT_TRUST,
    SignalType.SUPPLIER_LATE_RECEIPT: ASSOCIATIVE_TRUST,
}
DIAGNOSIS_FIELDS = (
    "run_id",
    "snapshot_id",
    "problem_code",
    "claims",
    "supporting_signal_ids",
    "supporting_evidence_ids",
    "uncertainties",
    "affected_path",
    "reason_codes",
)
RECOMMENDATION_FIELDS = (
    "run_id",
    "snapshot_id",
    "diagnosis_id",
    "candidate_set_id",
    "simulation_bundle_id",
    "policy_version",
    "disposition",
    "selected_candidate_id",
    "candidate_order",
    "score_components",
    "reason_codes",
    "supporting_evidence_ids",
    "uncertainties",
)


@cache
def _packet(name: str = "C03-G01") -> DecisionPacket:
    if name == "NEUTRAL":
        records = neutral_records()
    else:
        vector = next(item for item in CASES if item["case_id"] == name)
        records = list(_records_for_case(vector))
    if name == "PARTIAL":  # handled below before vector selection
        raise AssertionError("partial fixture must use _partial_packet")
    packet = build_decision_packet(*make_fixture(records).args())
    validate_c05_packet(packet)
    binding.validate_investigation_case_binding(packet, binding.build_investigation_case(packet))
    return packet


@lru_cache(maxsize=1)
def _partial_packet() -> DecisionPacket:
    vector = next(item for item in CASES if item["case_id"] == "C03-G01")
    records = list(_records_for_case(vector))
    original = next(values for entity, _, values in records if entity == "fact_purchase_order")
    records.append(
        (
            "fact_purchase_order",
            "PO-2",
            dict(
                original,
                purchase_order_id="PO-2",
                promised_receipt_at=None,
            ),
        )
    )
    packet = build_decision_packet(*make_fixture(records).args())
    validate_c05_packet(packet)
    binding.validate_investigation_case_binding(packet, binding.build_investigation_case(packet))
    return packet


def _error(action: Callable[[], object], code: str) -> planning.C03PlanningError:
    with pytest.raises(planning.C03PlanningError) as caught:
        action()
    assert caught.value.code == code and str(caught.value) == code
    assert caught.value.__cause__ is None
    return caught.value


def _identified[T](
    value: T,
    kind: str,
    id_field: str,
    identity: dict[str, object],
    **changes: object,
) -> T:
    return cast(
        T,
        replace(
            cast(Any, value),
            **changes,
            **{id_field: derive_artifact_id(kind, f"{kind}.v1", identity)},
        ),
    )


def _semantic_packet(
    packet: DecisionPacket,
    *,
    signals: SignalBundle | None = None,
    **changes: object,
) -> DecisionPacket:
    """Rebind structural identities/references without approving upstream policy.

    Every caller proves acceptance by both frozen inherited validators. These
    packets deliberately exercise the extra packet-contained C03 semantic gate.
    """
    signals = packet.signals if signals is None else signals
    identity = {
        name: changes.get(name, getattr(packet.diagnosis, name)) for name in DIAGNOSIS_FIELDS
    }
    diagnosis = _identified(
        packet.diagnosis,
        "diagnosis-record",
        "diagnosis_id",
        identity,
        **identity,
    )
    candidate_identity: dict[str, object] = {
        "run_id": packet.run.run_id,
        "snapshot_id": packet.snapshot.snapshot_id,
        "diagnosis_id": diagnosis.diagnosis_id,
        "candidate_ids": tuple(item.candidate_id for item in packet.candidates.candidates),
    }
    candidates = _identified(
        packet.candidates,
        "candidate-set",
        "candidate_set_id",
        candidate_identity,
        diagnosis_id=diagnosis.diagnosis_id,
    )
    recommendation_identity = {
        name: getattr(packet.recommendation, name) for name in RECOMMENDATION_FIELDS
    }
    recommendation_identity.update(
        diagnosis_id=diagnosis.diagnosis_id,
        candidate_set_id=candidates.candidate_set_id,
    )
    recommendation = _identified(
        packet.recommendation,
        "recommendation-record",
        "recommendation_id",
        recommendation_identity,
        **recommendation_identity,
    )
    result = _rebind_packet(
        packet,
        signals=signals,
        diagnosis=diagnosis,
        candidates=candidates,
        recommendation=recommendation,
    )
    validate_c05_packet(result)
    case = binding.build_investigation_case(result)
    binding.validate_investigation_case_binding(result, case)
    return result


def _signals(packet: DecisionPacket, items: tuple[Signal, ...]) -> SignalBundle:
    identity: dict[str, object] = {
        "run_id": packet.run.run_id,
        "snapshot_id": packet.snapshot.snapshot_id,
        "signal_ids": tuple(item.signal_id for item in items),
    }
    return _identified(
        packet.signals,
        "signal-bundle",
        "signal_bundle_id",
        identity,
        signals=items,
    )


def _uncertainty_key(item: Uncertainty) -> tuple[str, str, str, tuple[str, ...]]:
    return item.status.value, item.code, item.message, item.evidence_ids


@lru_cache(maxsize=1)
def _empty_packet() -> DecisionPacket:
    packet = _minimal_packet(states=tuple((kind, SignalState.INACTIVE) for kind in SignalType))
    return _semantic_packet(
        packet,
        problem_code="INSUFFICIENT_EVIDENCE_FOR_RISK_ASSESSMENT",
        claims=(),
        supporting_signal_ids=tuple(sorted(item.signal_id for item in packet.signals.signals)),
        affected_path=(EntityRef(entity_type="fact_sales_order", entity_id=packet.run.order_id),),
        reason_codes=tuple(
            sorted(
                {
                    "C03_STRUCTURED_NOT_CAUSAL",
                    *(reason for item in packet.signals.signals for reason in item.reason_codes),
                }
            )
        ),
    )


def _expected_questions(
    packet: DecisionPacket,
    case: InvestigationCase,
) -> tuple[InvestigationQuestion, ...]:
    result = []
    for signal in sorted(packet.signals.signals, key=lambda item: item.signal_type.value):
        if signal.state is SignalState.INACTIVE:
            continue
        kind = signal.signal_type
        refs = {
            packet.diagnosis.diagnosis_id,
            signal.signal_id,
            f"C03_{kind.value}_{signal.state.value}_V1",
        }
        if signal.state is SignalState.UNKNOWN:
            refs.add(f"C03_UNKNOWN_{kind.value}")
        if signal.state is SignalState.ACTIVE and "C03_INPUT_INCOMPLETE" in signal.reason_codes:
            refs.add(f"C03_PARTIAL_{kind.value}")
        result.append(
            InvestigationQuestion(
                case_id=case.artifact_id,
                question_code=f"W04_C03_{kind.value}_{signal.state.value}",
                trigger_refs=tuple(sorted(refs)),
                required_evidence_families=FAMILIES[kind],
                allowed_traversal_families=FAMILIES[kind],
                allowed_trust_classes=TRUST[kind],
                as_of_time=case.as_of_time,
                forbidden_inference_codes=tuple(
                    sorted(
                        {
                            *COMMON_LIMITATION_CODES,
                            *SIGNAL_POLICIES[kind].domain_limitation_codes,
                        }
                    )
                ),
            )
        )
    return tuple(result)


def _expected_plan(
    case: InvestigationCase,
    questions: tuple[InvestigationQuestion, ...],
) -> InvestigationPlan:
    return InvestigationPlan(
        case_id=case.artifact_id,
        as_of_time=case.as_of_time,
        planner_contract_version=VERSION,
        steps=tuple(
            InvestigationStep(
                case_id=case.artifact_id,
                question_id=question.artifact_id,
                ordinal=ordinal,
                depends_on_step_ids=(),
                expected_evidence_families=question.required_evidence_families,
            )
            for ordinal, question in enumerate(questions, start=1)
        ),
    )


def _planning(
    packet: DecisionPacket | None = None,
) -> tuple[DecisionPacket, InvestigationCase, tuple[InvestigationQuestion, ...], InvestigationPlan]:
    packet = _packet() if packet is None else packet
    case = binding.build_investigation_case(packet)
    questions = planning.build_investigation_questions(packet, case)
    plan = planning.build_investigation_plan(packet, case, questions)
    assert (
        cast(Callable[..., object], planning.validate_investigation_planning)(
            packet,
            case,
            questions,
            plan,
        )
        is None
    )
    return packet, case, questions, plan


def _reject_semantics(packet: DecisionPacket) -> None:
    validate_c05_packet(packet)
    case = binding.build_investigation_case(packet)
    binding.validate_investigation_case_binding(packet, case)
    before = canonical_json_bytes(packet)
    _error(lambda: planning.build_investigation_questions(packet, case), SEMANTIC)
    _error(lambda: planning.build_investigation_plan(packet, case, ()), SEMANTIC)
    empty = _expected_plan(case, ())
    _error(lambda: planning.validate_investigation_planning(packet, case, (), empty), SEMANTIC)
    assert canonical_json_bytes(packet) == before


def test_p01_exact_packet_type_is_required_before_caller_hooks() -> None:
    packet, case, questions, plan = _planning()
    subclass = type("PacketSubclass", (DecisionPacket,), {})
    extended: Any = object.__new__(subclass)
    for item in fields(packet):
        object.__setattr__(extended, item.name, getattr(packet, item.name))

    def reject(invalid: object) -> None:
        _error(
            lambda: planning.build_investigation_questions(
                cast(Any, invalid),
                case,
            ),
            INVALID,
        )
        _error(
            lambda: planning.build_investigation_plan(
                cast(Any, invalid),
                case,
                questions,
            ),
            INVALID,
        )
        _error(
            lambda: planning.validate_investigation_planning(
                cast(Any, invalid),
                case,
                questions,
                plan,
            ),
            INVALID,
        )

    for invalid in (None, object(), {}, extended):
        reject(invalid)


def test_p02_frozen_validator_reuse_order_and_stable_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet, case, _, _ = _planning()
    called: list[str] = []

    def validate(value: DecisionPacket) -> None:
        called.append("packet")
        validate_c05_packet(value)

    def bind(value: DecisionPacket, bound: InvestigationCase) -> None:
        called.append("binding")
        binding.validate_investigation_case_binding(value, bound)

    monkeypatch.setattr(planning, "validate_c05_packet", validate)
    monkeypatch.setattr(planning, "validate_investigation_case_binding", bind)
    planning.build_investigation_questions(packet, case)
    assert called[0] == "packet" and "binding" in called[1:]

    def invalid(_value: DecisionPacket) -> NoReturn:
        raise RuntimeError("INHERITED_PRIVATE_VALIDATOR_DETAIL")

    monkeypatch.setattr(planning, "validate_c05_packet", invalid)
    _error(lambda: planning.build_investigation_questions(packet, case), INVALID)


@pytest.mark.parametrize("attack", ["foreign", "subclass", "stale_hash", "future_packet"])
def test_p03_exact_c02_binding_and_temporal_boundary(attack: str) -> None:
    packet, case, questions, plan = _planning()
    if attack == "foreign":
        case = replace(case, opened_by="OTHER_BINDER")
    elif attack == "subclass":
        subclass = type("CaseSubclass", (InvestigationCase,), {})
        value: Any = object.__new__(subclass)
        for item in fields(case):
            object.__setattr__(value, item.name, getattr(case, item.name))
        case = value
    elif attack == "stale_hash":
        case = unsafe_replace(case, content_hash="f" * 64)
    else:
        packet = _minimal_packet(snapshot_observed=case.as_of_time + timedelta(seconds=1))
        validate_c05_packet(packet)
    code = INVALID if attack == "future_packet" else BINDING
    _error(lambda: planning.build_investigation_questions(packet, case), code)
    _error(lambda: planning.build_investigation_plan(packet, case, questions), code)
    _error(lambda: planning.validate_investigation_planning(packet, case, questions, plan), code)


@pytest.mark.parametrize(
    "inherited_code",
    [
        binding.C02_FUTURE_INFORMATION,
        binding.C02_INVALID_DECISION_PACKET,
        binding.C02_CASE_BINDING_MISMATCH,
    ],
)
def test_p03_c02_errors_have_closed_c03_mapping(
    inherited_code: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet, case, _, _ = _planning()

    def fail(_packet: DecisionPacket, _case: InvestigationCase) -> NoReturn:
        raise binding.C02BindingError(inherited_code)

    monkeypatch.setattr(planning, "validate_investigation_case_binding", fail)
    expected = BINDING if inherited_code == binding.C02_CASE_BINDING_MISMATCH else INVALID
    _error(lambda: planning.build_investigation_questions(packet, case), expected)


def test_p04_missing_family_passes_inherited_boundary_but_fails_semantics() -> None:
    packet = _packet()
    items = packet.signals.signals[1:]
    attacked = _semantic_packet(
        packet,
        signals=_signals(packet, items),
        supporting_signal_ids=tuple(sorted(item.signal_id for item in items)),
    )
    _reject_semantics(attacked)


@pytest.mark.parametrize("attack", ["duplicate", "reorder", "stale_signal", "mutable_signals"])
def test_p04_noncanonical_signal_envelopes_fail_inherited_validation(attack: str) -> None:
    packet, case, _, _ = _planning()
    items: Any = packet.signals.signals
    if attack == "duplicate":
        items = (*items, items[0])
    elif attack == "reorder":
        items = tuple(reversed(items))
    elif attack == "stale_signal":
        items = (unsafe_replace(items[0], signal_id="sig_" + "f" * 64), *items[1:])
    else:
        items = list(items)
    attacked = unsafe_replace(packet, signals=unsafe_replace(packet.signals, signals=items))
    _error(lambda: planning.build_investigation_questions(attacked, case), INVALID)


@pytest.mark.parametrize(
    "name, problem",
    [
        ("C03-G01", "OBSERVED_DELIVERY_RISK_INDICATORS"),
        ("C03-G27", "DELIVERY_COMMITMENT_WARNING"),
        ("NEUTRAL", "INSUFFICIENT_EVIDENCE_FOR_RISK_ASSESSMENT"),
    ],
)
def test_p05_problem_precedence_real_fixtures_and_rehashed_tamper(name: str, problem: str) -> None:
    packet = _packet(name)
    assert packet.diagnosis.problem_code == problem
    _planning(packet)
    _reject_semantics(_semantic_packet(packet, problem_code="OTHER_PROBLEM"))


def test_p06_inactive_claim_injection_is_rejected() -> None:
    packet = _packet("NEUTRAL")
    signal = next(item for item in packet.signals.signals if item.state is SignalState.INACTIVE)
    claim = DiagnosisClaim(
        claim_code=f"C03_{signal.signal_type.value}_INACTIVE_V1",
        claim_type=ClaimType.FACT_CLAIM,
        statement="Caller invented an inactive claim.",
        evidence_ids=signal.evidence_ids,
        limitations=signal.limitations,
    )
    _reject_semantics(_semantic_packet(packet, claims=(*packet.diagnosis.claims, claim)))


@pytest.mark.parametrize("attack", ["missing", "duplicate", "wrong_code"])
def test_p07_each_selected_signal_requires_one_canonical_claim(attack: str) -> None:
    packet = _packet()
    claims = packet.diagnosis.claims
    if attack == "missing":
        claims = claims[1:]
    elif attack == "duplicate":
        claims = (*claims, claims[0])
    else:
        claims = (replace(claims[0], claim_code="CALLER_CLAIM"), *claims[1:])
    _reject_semantics(_semantic_packet(packet, claims=claims))


@pytest.mark.parametrize(
    "kind", [kind for kind in SignalType if kind is not SignalType.CAPACITY_PRESSURE]
)
def test_p08_active_claim_type_matches_frozen_policy(kind: SignalType) -> None:
    packet = _packet(
        "C03-G27"
        if kind is SignalType.DELIVERY_RISK
        else "C03-G20"
        if kind is SignalType.QUEUE_DELAY
        else "C03-G01"
    )
    code = f"C03_{kind.value}_ACTIVE_V1"
    claim = next(item for item in packet.diagnosis.claims if item.claim_code == code)
    assert claim.claim_type is SIGNAL_POLICIES[kind].active_claim_type
    claims = tuple(
        replace(item, claim_type=ClaimType.UNCERTAINTY_STATEMENT) if item is claim else item
        for item in packet.diagnosis.claims
    )
    _reject_semantics(_semantic_packet(packet, claims=claims))


def test_p08_capacity_active_is_rejected_without_rebuilding_evidence() -> None:
    packet = _packet()
    original = packet.signals.signals[0]
    assert original.signal_type is SignalType.CAPACITY_PRESSURE
    identity = {
        name: getattr(original, name)
        for name in (
            "run_id",
            "snapshot_id",
            "signal_type",
            "state",
            "evidence_ids",
            "reason_codes",
        )
    }
    identity["state"] = SignalState.ACTIVE
    signal = _identified(original, "signal", "signal_id", identity, state=SignalState.ACTIVE)
    items = (signal, *packet.signals.signals[1:])
    _reject_semantics(
        _semantic_packet(
            packet,
            signals=_signals(packet, items),
            supporting_signal_ids=tuple(sorted(item.signal_id for item in items)),
        )
    )


@pytest.mark.parametrize(
    "kind, name",
    [
        (SignalType.CAPACITY_PRESSURE, "C03-G01"),
        (SignalType.DELIVERY_RISK, "C03-G01"),
        (SignalType.MATERIAL_TIMING_RISK, "C03-G02"),
        (SignalType.QUALITY_DISPOSITION_UNKNOWN, "C03-G16"),
        (SignalType.QUALITY_FAILURE, "C03-G16"),
        (SignalType.QUEUE_DELAY, "C03-G01"),
        (SignalType.REWORK_PRESENT, "C03-G16"),
        (SignalType.SUPPLIER_LATE_RECEIPT, "C03-G02"),
    ],
)
def test_p09_unknown_claim_type_remains_uncertainty(kind: SignalType, name: str) -> None:
    packet = _packet(name)
    code = f"C03_{kind.value}_UNKNOWN_V1"
    claim = next(item for item in packet.diagnosis.claims if item.claim_code == code)
    assert claim.claim_type is ClaimType.UNCERTAINTY_STATEMENT
    claims = tuple(
        replace(item, claim_type=ClaimType.FACT_CLAIM) if item is claim else item
        for item in packet.diagnosis.claims
    )
    _reject_semantics(_semantic_packet(packet, claims=claims))


@pytest.mark.parametrize("field", ["statement", "evidence_ids", "limitations"])
@pytest.mark.parametrize("state", [SignalState.ACTIVE, SignalState.UNKNOWN])
def test_p10_complete_claim_policy_semantics_are_exact(field: str, state: SignalState) -> None:
    packet = _packet()
    signal = next(item for item in packet.signals.signals if item.state is state)
    code = f"C03_{signal.signal_type.value}_{state.value}_V1"
    claim = next(item for item in packet.diagnosis.claims if item.claim_code == code)
    policy = SIGNAL_POLICIES[signal.signal_type]
    assert claim.statement == (
        policy.active_statement if state is SignalState.ACTIVE else policy.unknown_statement
    )
    assert claim.evidence_ids == signal.evidence_ids and claim.limitations == signal.limitations
    value: object = "Changed frozen statement."
    if field == "evidence_ids":
        existing = next(
            item.evidence_id
            for item in packet.evidence.evidence
            if item.evidence_id not in claim.evidence_ids
        )
        value = (existing,)
    elif field == "limitations":
        value = (Limitation(code="OTHER_LIMITATION", message="Changed frozen limitation."),)
    changed = replace(claim, **cast(dict[str, Any], {field: value}))
    claims = tuple(changed if item is claim else item for item in packet.diagnosis.claims)
    _reject_semantics(_semantic_packet(packet, claims=claims))


def test_p11_supporting_signals_are_all_eight_not_only_active() -> None:
    packet = _packet("NEUTRAL")
    assert packet.diagnosis.supporting_signal_ids == tuple(
        sorted(item.signal_id for item in packet.signals.signals)
    )
    _reject_semantics(
        _semantic_packet(
            packet,
            supporting_signal_ids=packet.diagnosis.supporting_signal_ids[1:],
        )
    )


@pytest.mark.parametrize("attack", ["order", "entity", "missing", "extra"])
def test_p12_affected_path_is_exact_order_binding(attack: str) -> None:
    packet = _packet()
    path = (EntityRef(entity_type="fact_sales_order", entity_id=packet.run.order_id),)
    assert packet.diagnosis.affected_path == path
    altered: tuple[EntityRef, ...] = (
        EntityRef(entity_type="fact_sales_order", entity_id="OTHER_ORDER"),
    )
    if attack == "entity":
        altered = (EntityRef(entity_type="fact_work_order", entity_id=packet.run.order_id),)
    elif attack == "missing":
        altered = ()
    elif attack == "extra":
        altered = (*path, *altered)
    _reject_semantics(_semantic_packet(packet, affected_path=altered))


@pytest.mark.parametrize("attack", ["remove", "add"])
def test_p13_reason_codes_are_exact_signal_union(attack: str) -> None:
    packet = _packet()
    expected = tuple(
        sorted(
            {
                "C03_STRUCTURED_NOT_CAUSAL",
                *(code for item in packet.signals.signals for code in item.reason_codes),
            }
        )
    )
    assert packet.diagnosis.reason_codes == expected
    changed = expected[1:] if attack == "remove" else tuple(sorted((*expected, "OTHER_REASON")))
    _reject_semantics(_semantic_packet(packet, reason_codes=changed))


@pytest.mark.parametrize("partial", [False, True])
@pytest.mark.parametrize("attack", ["missing", "status", "message", "evidence", "duplicate_code"])
def test_p14_p15_required_uncertainty_complete_record_is_exact(partial: bool, attack: str) -> None:
    packet = _partial_packet() if partial else _packet()
    prefix = "C03_PARTIAL_" if partial else "C03_UNKNOWN_"
    original = next(item for item in packet.diagnosis.uncertainties if item.code.startswith(prefix))
    assert original.status is UncertaintyStatus.INSUFFICIENT_EVIDENCE
    if partial:
        assert original.message == (
            "A positive witness exists, but some rule-relevant evidence is incomplete."
        )
    else:
        kind = SignalType(original.code.removeprefix(prefix))
        assert original.message == SIGNAL_POLICIES[kind].unknown_statement
    signal = next(
        item for item in packet.signals.signals if original.code == prefix + item.signal_type.value
    )
    assert original.evidence_ids == signal.evidence_ids
    items = tuple(item for item in packet.diagnosis.uncertainties if item is not original)
    if attack != "missing":
        changes: dict[str, Any] = {"message": "Different inherited uncertainty statement."}
        if attack == "status":
            changes = {"status": UncertaintyStatus.UNKNOWN}
        elif attack == "evidence":
            changes = {
                "evidence_ids": (
                    next(
                        item.evidence_id
                        for item in packet.evidence.evidence
                        if item.evidence_id not in original.evidence_ids
                    ),
                )
            }
        changed = replace(original, **changes)
        items = (*items, changed)
        if attack == "duplicate_code":
            items = (*items, original)
    _reject_semantics(
        _semantic_packet(packet, uncertainties=tuple(sorted(items, key=_uncertainty_key)))
    )


def test_p14_p15_unrelated_inherited_uncertainties_are_preserved() -> None:
    packet = _packet("NEUTRAL")
    inherited = (
        Uncertainty(
            status=UncertaintyStatus.UNKNOWN,
            code="INHERITED_OTHER_SCOPE",
            message="Unrelated inherited scope is unknown.",
            evidence_ids=(),
        ),
        Uncertainty(
            status=UncertaintyStatus.INSUFFICIENT_EVIDENCE,
            code="C03_UNKNOWN_LEGACY_CONTEXT",
            message="Legacy context remains unknown.",
            evidence_ids=(),
        ),
        Uncertainty(
            status=UncertaintyStatus.INSUFFICIENT_EVIDENCE,
            code="C03_PARTIAL_QUALITY_FAILURE",
            message="An untriggered inherited item.",
            evidence_ids=(),
        ),
    )
    changed = _semantic_packet(
        packet,
        uncertainties=tuple(
            sorted(
                (*packet.diagnosis.uncertainties, *inherited),
                key=_uncertainty_key,
            )
        ),
    )
    before = canonical_json_bytes(changed)
    _planning(changed)
    assert set(inherited) <= set(changed.diagnosis.uncertainties)
    assert canonical_json_bytes(changed) == before


def test_p16_registry_is_exact_mapping_proxy_with_frozen_policies() -> None:
    registry = planning._QUESTION_REGISTRY
    assert type(registry) is MappingProxyType
    assert set(registry) == set(SignalType) == set(FAMILIES) == set(TRUST)
    with pytest.raises(TypeError):
        cast(Any, registry)[SignalType.CAPACITY_PRESSURE] = object()
    policy = registry[SignalType.CAPACITY_PRESSURE]
    with pytest.raises(FrozenInstanceError):
        cast(Any, policy).required_evidence_families = ()
    for policy in registry.values():
        for name in (
            "required_evidence_families",
            "allowed_traversal_families",
            "allowed_trust_classes",
            "forbidden_inference_codes",
        ):
            value = getattr(policy, name)
            assert type(value) is tuple and value == tuple(sorted(set(value)))


@pytest.mark.parametrize("kind", list(SignalType))
def test_p17_p18_exact_evidence_and_traversal_families(kind: SignalType) -> None:
    policy = planning._QUESTION_REGISTRY[kind]
    assert policy.required_evidence_families == SIGNAL_POLICIES[kind].entities == FAMILIES[kind]
    assert policy.allowed_traversal_families == policy.required_evidence_families


@pytest.mark.parametrize("kind", list(SignalType))
def test_p19_p20_p21_p22_p23_exact_trust_registry(kind: SignalType) -> None:
    policy = planning._QUESTION_REGISTRY[kind]
    assert policy.allowed_trust_classes == TRUST[kind]
    assert TrustLevel.FORBIDDEN_INFERENCE not in policy.allowed_trust_classes


@pytest.mark.parametrize("kind", list(SignalType))
def test_p24_forbidden_inference_codes_exact_frozen_union(kind: SignalType) -> None:
    assert planning._QUESTION_REGISTRY[kind].forbidden_inference_codes == tuple(
        sorted(
            {
                *COMMON_LIMITATION_CODES,
                *SIGNAL_POLICIES[kind].domain_limitation_codes,
            }
        )
    )


@pytest.mark.parametrize(
    "name",
    [
        "C03-G01",
        "C03-G02",
        "C03-G15",
        "C03-G16",
        "C03-G20",
        "C03-G27",
        "NEUTRAL",
    ],
)
def test_p25_p26_p27_p28_p29_real_projection_complete_canonical_envelopes(name: str) -> None:
    packet, case, questions, plan = _planning(_packet(name))
    expected = _expected_questions(packet, case)
    assert canonical_json_bytes(questions) == canonical_json_bytes(expected)
    assert canonical_json_bytes(plan) == canonical_json_bytes(_expected_plan(case, expected))
    selected = tuple(
        item for item in packet.signals.signals if item.state is not SignalState.INACTIVE
    )
    assert len(questions) == len(selected)
    assert [item.question_code for item in questions] == [
        f"W04_C03_{item.signal_type.value}_{item.state.value}" for item in selected
    ]
    for signal, question in zip(selected, questions, strict=True):
        if signal.state is SignalState.UNKNOWN:
            assert f"C03_UNKNOWN_{signal.signal_type.value}" in question.trigger_refs


def test_p15_p28_partial_active_projection_contains_exact_partial_triggers() -> None:
    packet, case, questions, _ = _planning(_partial_packet())
    assert canonical_json_bytes(questions) == canonical_json_bytes(
        _expected_questions(packet, case)
    )
    partial = [
        item for item in packet.signals.signals if "C03_INPUT_INCOMPLETE" in item.reason_codes
    ]
    assert {item.signal_type for item in partial} == {
        SignalType.MATERIAL_TIMING_RISK,
        SignalType.SUPPLIER_LATE_RECEIPT,
    }
    for signal in partial:
        question = next(
            item for item in questions if signal.signal_type.value in item.question_code
        )
        assert f"C03_PARTIAL_{signal.signal_type.value}" in question.trigger_refs


def test_p25_p32_p35_all_eight_inactive_support_empty_questions_and_plan() -> None:
    packet, case, questions, plan = _planning(_empty_packet())
    assert len(packet.signals.signals) == 8
    assert all(item.state is SignalState.INACTIVE for item in packet.signals.signals)
    assert case.risk_families == () and case.source_signal_ids == ()
    assert questions == () and plan.steps == ()
    assert plan.to_json() == _expected_plan(case, ()).to_json()
    restored = InvestigationPlan.from_json(plan.to_json())
    assert (
        cast(Callable[..., object], planning.validate_investigation_planning)(
            packet,
            case,
            (),
            restored,
        )
        is None
    )


@pytest.mark.parametrize("attack", ["omit", "duplicate", "reorder", "injection"])
def test_p30_p31_question_tuple_must_equal_full_deterministic_projection(attack: str) -> None:
    packet, case, questions, plan = _planning()
    changed = questions[1:]
    if attack == "duplicate":
        changed = (*questions, questions[0])
    elif attack == "reorder":
        changed = tuple(reversed(questions))
    elif attack == "injection":
        changed = (*questions, replace(questions[0], question_code="CALLER_FREE_FORM_QUESTION"))
    _error(lambda: planning.build_investigation_plan(packet, case, changed), QUESTIONS)
    _error(lambda: planning.validate_investigation_planning(packet, case, changed, plan), QUESTIONS)


def test_p32_p33_p34_p35_exact_dependency_free_plan_projection() -> None:
    packet, case, questions, plan = _planning(_packet("C03-G27"))
    assert planning.C03_PLANNER_CONTRACT_VERSION == VERSION
    assert plan.to_json() == _expected_plan(case, questions).to_json()
    assert plan.case_id == case.artifact_id and plan.as_of_time == case.as_of_time
    assert plan.planner_contract_version == VERSION
    assert tuple(item.ordinal for item in plan.steps) == tuple(range(1, len(questions) + 1))
    for question, step in zip(questions, plan.steps, strict=True):
        assert step.case_id == case.artifact_id and step.question_id == question.artifact_id
        assert step.expected_evidence_families == question.required_evidence_families
        assert step.depends_on_step_ids == ()
    assert (
        cast(Callable[..., object], planning.validate_investigation_planning)(
            packet,
            case,
            questions,
            plan,
        )
        is None
    )


def test_p36_same_process_determinism_roundtrip_and_input_preservation() -> None:
    packet = _partial_packet()
    before = canonical_json_bytes(packet)
    first = _planning(packet)
    second = _planning(packet)
    assert canonical_json_bytes(first[1:]) == canonical_json_bytes(second[1:])
    _, case, questions, plan = first
    restored_questions = tuple(
        InvestigationQuestion.from_json(item.to_json()) for item in questions
    )
    restored_plan = InvestigationPlan.from_json(plan.to_json())
    assert (
        cast(Callable[..., object], planning.validate_investigation_planning)(
            packet,
            case,
            restored_questions,
            restored_plan,
        )
        is None
    )
    assert canonical_json_bytes(packet) == before
    for question in questions:
        assert question.artifact_id == "iquest_" + question.content_hash
        assert (
            question.content_hash
            == hashlib.sha256(
                canonical_json_bytes(
                    question.canonical_payload(),
                )
            ).hexdigest()
        )
    assert plan.artifact_id == "iplan_" + plan.content_hash


@pytest.mark.parametrize("seed", ["1", "31337", "random"])
def test_p37_p38_fresh_process_and_hash_seed_complete_identity(seed: str) -> None:
    _, case, questions, plan = _planning(_packet("C03-G27"))
    expected = canonical_json_bytes((case, questions, plan)).hex()
    script = """
import sys
sys.path.insert(0, 'tests')
from test_investigation_planning import _packet, _planning
from flowlens.decision.serialization import canonical_json_bytes
_, case, questions, plan = _planning(_packet('C03-G27'))
print(canonical_json_bytes((case, questions, plan)).hex())
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONHASHSEED": seed},
    )
    assert result.stdout.strip() == expected


@pytest.mark.parametrize(
    "attack",
    [
        "case",
        "state_code",
        "trigger",
        "required_family",
        "traversal_family",
        "trust_widen",
        "forbidden_remove",
        "time",
    ],
)
def test_p39_rehashed_question_semantic_forgeries_are_rejected(attack: str) -> None:
    packet, case, questions, plan = _planning()
    original = questions[0]
    changes: dict[str, Any] = {"case_id": "icase_" + "f" * 64}
    if attack == "state_code":
        changes = {"question_code": original.question_code.replace("UNKNOWN", "ACTIVE")}
    elif attack == "trigger":
        changes = {"trigger_refs": tuple(sorted((*original.trigger_refs, "CALLER_TRIGGER")))}
    elif attack == "required_family":
        changes = {"required_evidence_families": ("fact_inventory_snapshot",)}
    elif attack == "traversal_family":
        changes = {
            "allowed_traversal_families": tuple(
                sorted(
                    (*original.allowed_traversal_families, "fact_inventory_snapshot"),
                )
            )
        }
    elif attack == "trust_widen":
        changes = {
            "allowed_trust_classes": tuple(
                sorted(
                    (*original.allowed_trust_classes, TrustLevel.ASSOCIATIVE_EVIDENCE),
                )
            )
        }
    elif attack == "forbidden_remove":
        changes = {"forbidden_inference_codes": original.forbidden_inference_codes[1:]}
    elif attack == "time":
        changes = {"as_of_time": original.as_of_time + timedelta(seconds=1)}
    forged = replace(original, **changes)
    assert InvestigationQuestion.from_json(forged.to_json()).to_json() == forged.to_json()
    altered = (forged, *questions[1:])
    _error(lambda: planning.build_investigation_plan(packet, case, altered), QUESTIONS)
    _error(lambda: planning.validate_investigation_planning(packet, case, altered, plan), QUESTIONS)


@pytest.mark.parametrize(
    "attack",
    [
        "missing_step",
        "extra_step",
        "question_id",
        "families",
        "dependency",
        "case",
        "time",
        "version",
    ],
)
def test_p39_rehashed_structural_plan_forgeries_are_rejected(attack: str) -> None:
    packet, case, questions, plan = _planning()
    steps = plan.steps
    changes: dict[str, Any] = {}
    if attack == "missing_step":
        changes = {"steps": steps[:-1]}
    elif attack == "extra_step":
        changes = {"steps": (*steps, replace(steps[-1], ordinal=len(steps) + 1))}
    elif attack == "question_id":
        changes = {"steps": (replace(steps[0], question_id="iquest_" + "f" * 64), *steps[1:])}
    elif attack == "families":
        changes = {
            "steps": (
                replace(steps[0], expected_evidence_families=("fact_inventory_snapshot",)),
                *steps[1:],
            )
        }
    elif attack == "dependency":
        changes = {
            "steps": (
                steps[0],
                replace(steps[1], depends_on_step_ids=(steps[0].artifact_id,)),
                *steps[2:],
            )
        }
    elif attack == "case":
        foreign = "icase_" + "f" * 64
        changes = {
            "case_id": foreign,
            "steps": tuple(replace(item, case_id=foreign) for item in steps),
        }
    elif attack == "time":
        changes = {"as_of_time": plan.as_of_time + timedelta(seconds=1)}
    else:
        changes = {"planner_contract_version": "w04-c03-other"}
    forged = replace(plan, **changes)
    assert InvestigationPlan.from_json(forged.to_json()).to_json() == forged.to_json()
    _error(lambda: planning.validate_investigation_planning(packet, case, questions, forged), PLAN)


@pytest.mark.parametrize("artifact", ["question", "step", "plan"])
@pytest.mark.parametrize("field", ["artifact_id", "content_hash"])
@pytest.mark.parametrize("attack", ["stale", "enum_same_value"])
def test_p39_original_and_nested_derived_identity_claims_are_revalidated(
    artifact: str,
    field: str,
    attack: str,
) -> None:
    packet, case, questions, plan = _planning()
    original = (
        questions[0] if artifact == "question" else plan.steps[0] if artifact == "step" else plan
    )
    legitimate = getattr(original, field)
    prefix = {"question": "iquest_", "step": "istep_", "plan": "iplan_"}[artifact]
    value: object = (prefix if field == "artifact_id" else "") + "f" * 64
    if attack == "enum_same_value":
        value = cast(Any, StrEnum("SpoofedIdentity", {"SPOOF": legitimate}))["SPOOF"]
    changed = unsafe_replace(original, **{field: value})
    if attack == "enum_same_value":
        assert canonical_json_bytes(changed) == canonical_json_bytes(original)
    if artifact == "question":
        altered = (cast(InvestigationQuestion, changed), *questions[1:])
        _error(lambda: planning.build_investigation_plan(packet, case, altered), QUESTIONS)
        _error(
            lambda: planning.validate_investigation_planning(packet, case, altered, plan), QUESTIONS
        )
    else:
        forged = (
            cast(InvestigationPlan, changed)
            if artifact == "plan"
            else unsafe_replace(
                plan,
                steps=(cast(InvestigationStep, changed), *plan.steps[1:]),
            )
        )
        _error(
            lambda: planning.validate_investigation_planning(packet, case, questions, forged), PLAN
        )
    assert getattr(changed, field) is value


@pytest.mark.parametrize(
    "attack",
    [
        "questions_list",
        "question_subclass",
        "question_schema",
        "plan_subclass",
        "plan_list",
        "step_subclass",
        "step_schema",
        "step_mutable_refs",
    ],
)
def test_p39_exact_question_plan_and_step_types_are_required(attack: str) -> None:
    packet, case, questions, plan = _planning()
    altered: Any = questions
    forged: Any = plan
    expected = PLAN
    if attack == "questions_list":
        altered = list(questions)
        expected = QUESTIONS
    elif attack in ("question_subclass", "plan_subclass", "step_subclass"):
        original = (
            questions[0]
            if attack == "question_subclass"
            else (plan if attack == "plan_subclass" else plan.steps[0])
        )
        cls = type("ArtifactSubclass", (type(original),), {})
        value: Any = object.__new__(cls)
        for item in fields(original):
            object.__setattr__(value, item.name, getattr(original, item.name))
        if attack == "question_subclass":
            altered = (value, *questions[1:])
            expected = QUESTIONS
        elif attack == "plan_subclass":
            forged = value
        else:
            forged = unsafe_replace(plan, steps=(value, *plan.steps[1:]))
    elif attack == "question_schema":
        altered = (
            unsafe_replace(questions[0], schema_version="investigation-question.v2"),
            *questions[1:],
        )
        expected = QUESTIONS
    elif attack == "plan_list":
        forged = unsafe_replace(plan, steps=list(plan.steps))
    else:
        changes: dict[str, Any] = (
            {"schema_version": "investigation-step.v2"}
            if attack == "step_schema"
            else {
                "depends_on_step_ids": [],
            }
        )
        forged = unsafe_replace(
            plan, steps=(unsafe_replace(plan.steps[0], **changes), *plan.steps[1:])
        )
    if expected == QUESTIONS:
        _error(lambda: planning.build_investigation_plan(packet, case, altered), QUESTIONS)
    _error(
        lambda: planning.validate_investigation_planning(packet, case, altered, forged), expected
    )


@pytest.mark.parametrize(
    "artifact, field",
    [
        (name, item.name)
        for name, cls in (
            ("question", InvestigationQuestion),
            ("step", InvestigationStep),
            ("plan", InvestigationPlan),
        )
        for item in fields(cls)
    ],
)
def test_p39_missing_original_slots_are_rejected_without_repair(
    artifact: str,
    field: str,
) -> None:
    packet, case, questions, plan = _planning()
    original = (
        questions[0] if artifact == "question" else (plan.steps[0] if artifact == "step" else plan)
    )
    changed: Any = unsafe_replace(original)
    object.__delattr__(changed, field)
    altered = (changed, *questions[1:]) if artifact == "question" else questions
    forged = (
        changed
        if artifact == "plan"
        else (
            unsafe_replace(plan, steps=(changed, *plan.steps[1:])) if artifact == "step" else plan
        )
    )
    expected = QUESTIONS if artifact == "question" else PLAN
    if artifact == "question":
        _error(lambda: planning.build_investigation_plan(packet, case, altered), expected)
    _error(
        lambda: planning.validate_investigation_planning(packet, case, altered, forged), expected
    )
    with pytest.raises(AttributeError):
        getattr(changed, field)


@pytest.mark.parametrize("artifact", ["question", "step", "plan"])
def test_p39_uninitialized_exact_artifacts_have_stable_errors(artifact: str) -> None:
    packet, case, questions, plan = _planning()
    cls = {"question": InvestigationQuestion, "step": InvestigationStep, "plan": InvestigationPlan}[
        artifact
    ]
    changed: Any = object.__new__(cls)
    altered = (changed, *questions[1:]) if artifact == "question" else questions
    forged = (
        changed
        if artifact == "plan"
        else (
            unsafe_replace(plan, steps=(changed, *plan.steps[1:])) if artifact == "step" else plan
        )
    )
    expected = QUESTIONS if artifact == "question" else PLAN
    if artifact == "question":
        _error(lambda: planning.build_investigation_plan(packet, case, altered), expected)
    _error(
        lambda: planning.validate_investigation_planning(packet, case, altered, forged), expected
    )
    assert all(not hasattr(changed, item.name) for item in fields(cls))


def test_p23_p39_forbidden_inference_question_cannot_be_constructed_or_submitted() -> None:
    packet, case, questions, plan = _planning()
    widened = tuple(sorted((*questions[0].allowed_trust_classes, TrustLevel.FORBIDDEN_INFERENCE)))
    with pytest.raises(ValueError):
        replace(questions[0], allowed_trust_classes=widened)
    forged = unsafe_replace(questions[0], allowed_trust_classes=widened)
    altered = (forged, *questions[1:])
    _error(lambda: planning.build_investigation_plan(packet, case, altered), QUESTIONS)
    _error(lambda: planning.validate_investigation_planning(packet, case, altered, plan), QUESTIONS)


@pytest.mark.parametrize("target", ["questions", "question_refs", "plan_steps", "step_refs"])
def test_p39_hostile_tuple_iterators_are_rejected_before_caller_hooks(target: str) -> None:
    packet, case, questions, plan = _planning()
    invoked: list[str] = []

    class HostileTuple(tuple[Any, ...]):
        def __iter__(self) -> NoReturn:
            invoked.append("iterated")
            raise AssertionError("UNTRUSTED_ITERATOR_MUST_NOT_EXECUTE")

    original: tuple[Any, ...] = questions
    if target == "question_refs":
        original = questions[0].trigger_refs
    elif target == "plan_steps":
        original = plan.steps
    elif target == "step_refs":
        original = plan.steps[0].depends_on_step_ids
    hostile = HostileTuple(original)
    with pytest.raises(AssertionError, match="UNTRUSTED_ITERATOR_MUST_NOT_EXECUTE"):
        tuple(hostile)
    assert invoked == ["iterated"]
    invoked.clear()
    altered: Any = questions
    forged = plan
    if target == "questions":
        altered = hostile
    elif target == "question_refs":
        altered = (unsafe_replace(questions[0], trigger_refs=hostile), *questions[1:])
    elif target == "plan_steps":
        forged = unsafe_replace(plan, steps=hostile)
    else:
        forged = unsafe_replace(
            plan,
            steps=(
                unsafe_replace(plan.steps[0], depends_on_step_ids=hostile),
                *plan.steps[1:],
            ),
        )
    expected = QUESTIONS if target in ("questions", "question_refs") else PLAN
    if expected == QUESTIONS:
        _error(lambda: planning.build_investigation_plan(packet, case, altered), expected)
    _error(
        lambda: planning.validate_investigation_planning(packet, case, altered, forged), expected
    )
    assert invoked == []


class CapabilityDenied(RuntimeError):
    """A live negative-control sentinel for forbidden planner capabilities."""


def _deny(*_args: object, **_kwargs: object) -> NoReturn:
    raise CapabilityDenied("C03_FORBIDDEN_CAPABILITY")


def test_p40_live_capability_denials_and_direct_negative_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet, case, questions, plan = _planning(_partial_packet())
    before = canonical_json_bytes((packet, case, questions, plan))
    denied = (
        (builtins, "open"),
        (io, "open"),
        (Path, "open"),
        (Path, "read_text"),
        (Path, "read_bytes"),
        (Path, "write_text"),
        (Path, "write_bytes"),
        (socket, "socket"),
        (socket, "create_connection"),
        (subprocess, "run"),
        (subprocess, "Popen"),
        (sqlite3, "connect"),
        (random, "random"),
        (random, "randint"),
        (uuid, "uuid1"),
        (uuid, "uuid4"),
        (secrets, "token_hex"),
        (secrets, "token_bytes"),
        (time, "time"),
        (time, "monotonic"),
        (os, "system"),
        (os, "popen"),
        (w03_signals, "build_signal_bundle"),
        (w03_diagnosis, "build_diagnosis"),
        (w03_diagnosis, "evaluate_c03"),
    )
    with monkeypatch.context() as guard:
        for owner, name in denied:
            guard.setattr(owner, name, _deny)
            with pytest.raises(CapabilityDenied):
                getattr(owner, name)()
        guard.setattr(EvidenceQuerySpec, "__init__", _deny)
        with pytest.raises(CapabilityDenied):
            cast(Callable[..., object], EvidenceQuerySpec)()
        assert planning.build_investigation_questions(packet, case) == questions
        assert planning.build_investigation_plan(packet, case, questions) == plan
        assert (
            cast(Callable[..., object], planning.validate_investigation_planning)(
                packet,
                case,
                questions,
                plan,
            )
            is None
        )
    assert canonical_json_bytes((packet, case, questions, plan)) == before


def _runtime_violations(source: str) -> tuple[str, ...]:
    allowed = {
        "__future__",
        "collections.abc",
        "dataclasses",
        "datetime",
        "types",
        "typing",
        "flowlens.decision.c03_policy",
        "flowlens.decision.c06_validation",
        "flowlens.decision.contracts",
        "flowlens.decision.enums",
        "flowlens.decision.primitives",
        "flowlens.decision.serialization",
        "flowlens.investigation.c02_binding",
        "flowlens.investigation.contracts",
    }
    forbidden_calls = {
        "open",
        "eval",
        "exec",
        "compile",
        "__import__",
        "now",
        "utcnow",
        "time",
        "monotonic",
        "random",
        "randint",
        "uuid1",
        "uuid4",
        "token_hex",
        "token_bytes",
        "run",
        "Popen",
        "read_text",
        "read_bytes",
        "write_text",
        "write_bytes",
        "connect",
        "create_engine",
        "build_signal_bundle",
        "build_diagnosis",
        "evaluate_c03",
        "build_evidence_bundle",
        "build_state_snapshot",
        "build_decision_context",
        "build_candidate_set",
        "build_simulation_bundle",
        "EvidenceQuerySpec",
    }
    violations: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            violations.extend(alias.name for alias in node.names if alias.name not in allowed)
        elif isinstance(node, ast.ImportFrom):
            if node.level or node.module not in allowed:
                violations.append(str(node.module))
            if any(alias.name == "EvidenceQuerySpec" for alias in node.names):
                violations.append("EvidenceQuerySpec")
        elif isinstance(node, ast.Call):
            name = (
                node.func.id
                if isinstance(node.func, ast.Name)
                else (node.func.attr if isinstance(node.func, ast.Attribute) else "")
            )
            if name in forbidden_calls:
                violations.append(name)
    return tuple(violations)


@pytest.mark.parametrize(
    "source",
    [
        "import sqlite3\nsqlite3.connect('db')",
        "import socket\nsocket.socket()",
        "from pathlib import Path\nPath('x').read_text()",
        "import subprocess\nsubprocess.run([])",
        "from datetime import datetime\ndatetime.now()",
        "from flowlens.decision.signals import build_signal_bundle\n"
        "build_signal_bundle(None, None)",
        "from flowlens.investigation.contracts import EvidenceQuerySpec\nEvidenceQuerySpec()",
        "import flowlens.data.scenarios",
        "import openai",
        "eval('1')",
    ],
)
def test_p40_runtime_audit_rejects_forbidden_capability_negative_controls(source: str) -> None:
    assert _runtime_violations(source)


def test_p40_runtime_ast_and_fresh_import_have_no_execution_capabilities() -> None:
    assert not _runtime_violations("from dataclasses import dataclass\nvalue = tuple()")
    assert not _runtime_violations(RUNTIME.read_text(encoding="utf-8"))
    script = """
import json, sys
before = set(sys.modules)
import flowlens.investigation.c03_planning
print(json.dumps(sorted(set(sys.modules) - before)))
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    imported = json.loads(result.stdout)
    forbidden = (
        "sqlalchemy",
        "psycopg",
        "sqlite3",
        "flowlens.db",
        "flowlens.data",
        "socket",
        "subprocess",
        "requests",
        "httpx",
        "openai",
        "anthropic",
        "mcp",
        "flowlens.decision.c06_store",
        "flowlens.decision.c07",
        "flowlens.decision.c08",
        "flowlens.decision.signals",
        "flowlens.decision.diagnosis",
        "flowlens.decision.c04",
    )
    assert not any(
        name == prefix or name.startswith(prefix + ".") for name in imported for prefix in forbidden
    )


def test_p40_committed_source_governance_and_frozen_blobs() -> None:
    # Exclude this assertion only during precommit source construction. The full
    # committed harness and exact-SHA CI must require real verifier PASS.
    expected = {
        "src/flowlens/investigation/__init__.py": "c23929f85dccd78bc72ef3b2b1415c6e8eaf0452",
        "src/flowlens/investigation/contracts.py": "0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e",
        "src/flowlens/investigation/enums.py": "9c818780423f32f144b18666784ebc9ea3abdccc",
        "src/flowlens/investigation/c02_binding.py": "5f0af237ed465fa83e5a3b84954512b1f3125551",
    }
    for path, oid in expected.items():
        result = subprocess.run(
            ["git", "rev-parse", f"HEAD:{path}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == oid
    manifest = json.loads((ROOT / "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json").read_bytes())
    assert manifest["checkpoints"][0]["state"] == "CLOSED"
    c02 = next(item for item in manifest["checkpoints"] if item["checkpoint"] == "W04-C02")
    assert c02["state"] == "CLOSED"
    assert c02["source_freeze_sha"] == "18648915414a26dddbdc904965663730ea631cf2"
    c03 = [item for item in manifest["checkpoints"] if item["checkpoint"] == "W04-C03"]
    assert len(c03) == 1
    assert [item["path"] for item in c03[0]["files"]] == [
        "src/flowlens/investigation/c03_planning.py",
    ]
    c03_entry = c03[0]
    if c03_entry["state"] == "AUTHORIZED":
        assert c03_entry["source_freeze_sha"] is None
        assert c03_entry["files"][0]["blob_oid"] is None
    elif c03_entry["state"] == "CLOSED":
        assert c03_entry["source_freeze_sha"] == (
            "42047bcfe6591f7c9ed9b0034bd94467401ba72f"
        )
        assert c03_entry["files"][0]["blob_oid"] == (
            "21d0055e12d86e6333a836d363d6e266cb0fcbd7"
        )
    else:
        pytest.fail(f"unexpected W04-C03 state: {c03_entry['state']!r}")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "scripts/ci/verify_w04_source_evolution.py"),
            "--manifest",
            "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json",
            "--expected-head",
            head,
            "--repo",
            str(ROOT),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    proof = json.loads(result.stdout)
    assert proof["overall"] == "PASS" and proof["expected_head"] == head
    assert proof["actual_added_source_paths"] == sorted(
        [
            *expected,
            "src/flowlens/investigation/c03_planning.py",
        ]
    )
