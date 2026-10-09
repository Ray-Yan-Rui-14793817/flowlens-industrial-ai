"""W04-C02 B01-B36: frozen packet binding, temporal rejection and pure execution."""

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
from dataclasses import fields, replace
from datetime import UTC, datetime, timedelta, timezone
from enum import StrEnum
from functools import partial
from pathlib import Path
from typing import Any, NoReturn, cast
from zoneinfo import ZoneInfo

import pytest

from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.c05_policy import StressEffect
from flowlens.decision.c06_validation import validate_c05_packet
from flowlens.decision.contracts import (
    CandidateSet,
    DecisionPacket,
    DiagnosisRecord,
    Evidence,
    EvidenceBundle,
    RecommendationRecord,
    Signal,
    SignalBundle,
    SimulationBundle,
    StateSnapshot,
)
from flowlens.decision.enums import (
    FreshnessStatus,
    InterventionFamily,
    RecommendationDisposition,
    SignalState,
    SignalType,
    SimulationStatus,
    TrustLevel,
)
from flowlens.decision.primitives import (
    ArtifactProvenance,
    EntityRef,
    NamedValue,
    SnapshotEntry,
    SourceRef,
    VersionRef,
)
from flowlens.decision.serialization import (
    canonical_json_bytes,
    canonical_primitive,
    compute_snapshot_hash,
    derive_artifact_id,
)
from flowlens.investigation import c02_binding as binding
from flowlens.investigation.contracts import (
    EvidenceQuerySpec,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
    InvestigationStep,
)
from test_c03_signals import CASES, _records_for_case
from test_c05_policy import (
    C05Fixture,
    make_fixture,
    neutral_records,
    rebind_result,
    rebind_simulation_bundle,
    unsafe_replace,
    with_simulations,
)
from test_c05_recommendation import supplier_fixture
from test_decision_snapshot import AS_OF, make_run

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src/flowlens/investigation/c02_binding.py"
INVALID = "C02_INVALID_DECISION_PACKET"
FUTURE = "C02_FUTURE_INFORMATION"
MISMATCH = "C02_CASE_BINDING_MISMATCH"
CONTRACT_NAMES = (
    "w03-c01",
    "w03-c02",
    "w03-c03",
    "w03-c04",
    "w03-c05-decision",
    "w03-c05-evaluation",
    "w03-c05-packet",
)


def _artifact[T](
    cls: type[T],
    kind: str,
    id_field: str,
    identity: dict[str, Any],
    **extra: Any,
) -> T:
    constructor = cast(Callable[..., T], cls)
    return constructor(
        **{
            id_field: derive_artifact_id(kind, f"{kind}.v1", identity),
            "schema_version": f"{kind}.v1",
            **identity,
            **extra,
        }
    )


def _minimal_packet(
    *,
    as_of: datetime = AS_OF,
    snapshot_observed: datetime | None = AS_OF,
    snapshot_ref_observed: datetime | None = AS_OF,
    evidence_observed: datetime | None = AS_OF,
    source_observed: datetime | None = AS_OF,
    available: datetime = AS_OF,
    states: tuple[tuple[SignalType, SignalState], ...] = (
        (SignalType.DELIVERY_RISK, SignalState.INACTIVE),
    ),
    disposition: RecommendationDisposition = RecommendationDisposition.NO_ACTION,
) -> DecisionPacket:
    """Independent C01 envelope for edges impossible to emit through temporal builders.

    Each identity is constructed with frozen W03 functions. Successful future-
    observation tests independently require validate_c05_packet to accept it.
    Real C05 builder fixtures separately prove all emitted dispositions.
    """
    run = make_run(as_of)
    source = SourceRef(
        source_entity="fact_sales_order",
        source_record_id=run.order_id,
        source_field="status",
        observed_at=source_observed,
        available_at=available,
    )
    provenance = ArtifactProvenance(
        producer="fixture",
        producer_version="v1",
        input_artifact_ids=(),
        source_refs=(source,),
        contract_versions=(),
        implementation_sha=None,
    )
    entry = SnapshotEntry(
        entry_key="fact_sales_order.SO-1.status",
        entity=EntityRef(entity_type="fact_sales_order", entity_id=run.order_id),
        field="status",
        value="OPEN",
        observed_at=snapshot_observed,
        available_at=available,
        source_ref=replace(source, observed_at=snapshot_ref_observed),
    )
    semantic: dict[str, Any] = {
        "order_id": run.order_id,
        "as_of_time": as_of,
        "dataset_version": run.dataset_version,
        "dataset_hash": run.dataset_hash,
        "entries": (entry,),
        "unknowns": (),
    }
    snapshot = _artifact(
        StateSnapshot,
        "state-snapshot",
        "snapshot_id",
        {"run_id": run.run_id, "snapshot_hash": compute_snapshot_hash(semantic)},
        **semantic,
        provenance=provenance,
    )
    evidence = _artifact(
        Evidence,
        "evidence",
        "evidence_id",
        {
            "run_id": run.run_id,
            "snapshot_id": snapshot.snapshot_id,
            "source_entity": source.source_entity,
            "source_record_id": source.source_record_id,
            "source_field": source.source_field,
            "value": "OPEN",
            "observed_at": evidence_observed,
            "available_at": available,
            "as_of_time": as_of,
            "relationship_type": "ORDER_FIELD",
            "trust_level": TrustLevel.DIRECT_FACT,
            "freshness_status": FreshnessStatus.FRESH,
        },
        limitations=(),
        provenance=provenance,
    )
    bundle_identity = {
        "run_id": run.run_id,
        "snapshot_id": snapshot.snapshot_id,
        "snapshot_hash": snapshot.snapshot_hash,
        "evidence_ids": (evidence.evidence_id,),
        "uncertainties": (),
    }
    bundle = EvidenceBundle(
        evidence_bundle_id=derive_artifact_id(
            "evidence-bundle", "evidence-bundle.v1", bundle_identity
        ),
        schema_version="evidence-bundle.v1",
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        snapshot_hash=snapshot.snapshot_hash,
        evidence=(evidence,),
        uncertainties=(),
        provenance=provenance,
    )
    signal_items = tuple(
        _artifact(
            Signal,
            "signal",
            "signal_id",
            {
                "run_id": run.run_id,
                "snapshot_id": snapshot.snapshot_id,
                "signal_type": family,
                "state": state,
                "evidence_ids": (),
                "reason_codes": ("FIXTURE",),
            },
            limitations=(),
            provenance=provenance,
        )
        for family, state in sorted(states, key=lambda item: item[0].value)
    )
    signals = SignalBundle(
        signal_bundle_id=derive_artifact_id(
            "signal-bundle",
            "signal-bundle.v1",
            {
                "run_id": run.run_id,
                "snapshot_id": snapshot.snapshot_id,
                "signal_ids": tuple(signal.signal_id for signal in signal_items),
            },
        ),
        schema_version="signal-bundle.v1",
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        signals=signal_items,
        provenance=provenance,
    )
    diagnosis = _artifact(
        DiagnosisRecord,
        "diagnosis-record",
        "diagnosis_id",
        {
            "run_id": run.run_id,
            "snapshot_id": snapshot.snapshot_id,
            "problem_code": "ORDER_DELIVERY_RISK",
            "claims": (),
            "supporting_signal_ids": (),
            "supporting_evidence_ids": (),
            "uncertainties": (),
            "affected_path": (),
            "reason_codes": (),
        },
        provenance=provenance,
    )
    candidates = CandidateSet(
        candidate_set_id=derive_artifact_id(
            "candidate-set",
            "candidate-set.v1",
            {
                "run_id": run.run_id,
                "snapshot_id": snapshot.snapshot_id,
                "diagnosis_id": diagnosis.diagnosis_id,
                "candidate_ids": (),
            },
        ),
        schema_version="candidate-set.v1",
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        diagnosis_id=diagnosis.diagnosis_id,
        candidates=(),
        provenance=provenance,
    )
    simulations = SimulationBundle(
        simulation_bundle_id=derive_artifact_id(
            "simulation-bundle",
            "simulation-bundle.v1",
            {
                "run_id": run.run_id,
                "snapshot_id": snapshot.snapshot_id,
                "candidate_simulation_ids": (),
            },
        ),
        schema_version="simulation-bundle.v1",
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        results=(),
        provenance=provenance,
    )
    input_ids = (
        run.run_id,
        snapshot.snapshot_id,
        bundle.evidence_bundle_id,
        signals.signal_bundle_id,
        diagnosis.diagnosis_id,
        candidates.candidate_set_id,
        simulations.simulation_bundle_id,
    )
    recommendation = _artifact(
        RecommendationRecord,
        "recommendation-record",
        "recommendation_id",
        {
            "run_id": run.run_id,
            "snapshot_id": snapshot.snapshot_id,
            "diagnosis_id": diagnosis.diagnosis_id,
            "candidate_set_id": candidates.candidate_set_id,
            "simulation_bundle_id": simulations.simulation_bundle_id,
            "policy_version": "w03-c05-decision-v1",
            "disposition": disposition,
            "selected_candidate_id": None,
            "candidate_order": (),
            "score_components": (),
            "reason_codes": (),
            "supporting_evidence_ids": (),
            "uncertainties": (),
        },
        limitations=(),
        provenance=ArtifactProvenance(
            producer="flowlens.decision.c05_recommendation",
            producer_version="w03-c05-decision-v1",
            input_artifact_ids=tuple(sorted(input_ids)),
            source_refs=(),
            contract_versions=(),
            implementation_sha=None,
        ),
    )
    identity = {
        "run_id": run.run_id,
        "snapshot_id": snapshot.snapshot_id,
        "evidence_bundle_id": bundle.evidence_bundle_id,
        "signal_bundle_id": signals.signal_bundle_id,
        "diagnosis_id": diagnosis.diagnosis_id,
        "candidate_set_id": candidates.candidate_set_id,
        "simulation_bundle_id": simulations.simulation_bundle_id,
        "recommendation_id": recommendation.recommendation_id,
        "uncertainties": (),
        "limitations": (),
    }
    return DecisionPacket(
        packet_id=derive_artifact_id("decision-packet", "decision-packet.v1", identity),
        schema_version="decision-packet.v1",
        run=run,
        snapshot=snapshot,
        evidence=bundle,
        signals=signals,
        diagnosis=diagnosis,
        candidates=candidates,
        simulations=simulations,
        recommendation=recommendation,
        uncertainties=(),
        limitations=(),
        provenance=ArtifactProvenance(
            producer="flowlens.decision.c05_packet",
            producer_version="w03-c05-packet-v1",
            input_artifact_ids=tuple(sorted((*input_ids, recommendation.recommendation_id))),
            source_refs=(source,),
            contract_versions=tuple(VersionRef(name=name, version="v1") for name in CONTRACT_NAMES),
            implementation_sha=None,
        ),
    )


def _packet(fixture: C05Fixture | None = None) -> DecisionPacket:
    result = build_decision_packet(*(supplier_fixture() if fixture is None else fixture).args())
    validate_c05_packet(result)
    return result


def _real_fixture(disposition: RecommendationDisposition) -> C05Fixture:
    if disposition is RecommendationDisposition.NO_ACTION:
        return make_fixture(neutral_records())
    if disposition is RecommendationDisposition.NO_RECOMMENDATION:
        return make_fixture()
    if disposition is RecommendationDisposition.INVESTIGATION_ONLY:
        return supplier_fixture()
    multi = next(case for case in CASES if case["case_id"] == "C03-G27")
    return with_simulations(
        make_fixture(list(_records_for_case(multi))),
        {
            InterventionFamily.SUPPLIER_INTERVENTION: (
                SimulationStatus.SUCCEEDED,
                StressEffect.WORSENED,
            ),
            InterventionFamily.QUALITY_INTERVENTION: (
                SimulationStatus.SUCCEEDED,
                StressEffect.WORSENED,
            ),
        },
    )


def _ref_key(ref: SourceRef) -> tuple[str, str, str, str, str]:
    return (
        ref.source_entity,
        ref.source_record_id,
        ref.source_field,
        str(canonical_primitive(ref.observed_at)) if ref.observed_at else "",
        str(canonical_primitive(ref.available_at)),
    )


def _provenance_time(packet: DecisionPacket, field: str, value: datetime) -> DecisionPacket:
    evidence = next(item for item in packet.evidence.evidence if item.provenance.source_refs)
    original = evidence.provenance.source_refs[0]
    reference = (
        replace(original, observed_at=value)
        if field == "observed_at"
        else replace(original, available_at=value)
    )
    references = tuple(sorted((reference, *evidence.provenance.source_refs[1:]), key=_ref_key))
    changed = replace(evidence, provenance=replace(evidence.provenance, source_refs=references))
    items = tuple(changed if item is evidence else item for item in packet.evidence.evidence)
    packet_refs = tuple(
        sorted({ref for item in items for ref in item.provenance.source_refs}, key=_ref_key)
    )
    result = replace(
        packet,
        evidence=replace(packet.evidence, evidence=items),
        provenance=replace(packet.provenance, source_refs=packet_refs),
    )
    validate_c05_packet(result)
    return result


def _rebind_packet(packet: DecisionPacket, **changes: object) -> DecisionPacket:
    changed = unsafe_replace(packet, **changes)
    identity = {
        "run_id": changed.run.run_id,
        "snapshot_id": changed.snapshot.snapshot_id,
        "evidence_bundle_id": changed.evidence.evidence_bundle_id,
        "signal_bundle_id": changed.signals.signal_bundle_id,
        "diagnosis_id": changed.diagnosis.diagnosis_id,
        "candidate_set_id": changed.candidates.candidate_set_id,
        "simulation_bundle_id": changed.simulations.simulation_bundle_id,
        "recommendation_id": changed.recommendation.recommendation_id,
        "uncertainties": changed.uncertainties,
        "limitations": changed.limitations,
    }
    source_refs = tuple(
        sorted(
            {ref for item in changed.evidence.evidence for ref in item.provenance.source_refs},
            key=_ref_key,
        )
    )
    result = replace(
        changed,
        packet_id=derive_artifact_id("decision-packet", "decision-packet.v1", identity),
        provenance=replace(
            changed.provenance,
            input_artifact_ids=tuple(
                sorted(cast(str, value) for key, value in identity.items() if key.endswith("_id"))
            ),
            source_refs=source_refs,
        ),
    )
    validate_c05_packet(result)
    return result


def _error(action: Callable[[], object], code: str) -> binding.C02BindingError:
    with pytest.raises(binding.C02BindingError) as caught:
        action()
    assert caught.value.code == code and str(caught.value) == code
    assert caught.value.__cause__ is None
    return caught.value


def _validate_binding(packet: DecisionPacket, case: InvestigationCase) -> None:
    validator = cast(
        Callable[[DecisionPacket, InvestigationCase], object],
        binding.validate_investigation_case_binding,
    )
    assert validator(packet, case) is None


def test_b01_exact_packet_type_rejects_untrusted_values_and_subclasses() -> None:
    packet = _packet()
    subclass = type("PacketSubclass", (DecisionPacket,), {})
    copied: DecisionPacket = object.__new__(subclass)
    for item in fields(packet):
        object.__setattr__(copied, item.name, getattr(packet, item.name))
    for value in (None, {}, object(), copied):
        _error(
            partial(binding.build_investigation_case, cast(DecisionPacket, value)),
            INVALID,
        )


def test_b02_frozen_validator_is_reused_once_and_internal_failures_are_hidden(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet = _packet()
    calls: list[DecisionPacket] = []

    def observe(value: DecisionPacket) -> None:
        calls.append(value)
        validate_c05_packet(value)

    monkeypatch.setattr(binding, "validate_c05_packet", observe)
    case = binding.build_investigation_case(packet)
    assert calls == [packet]
    _validate_binding(packet, case)
    assert calls == [packet, packet]

    def fail(_value: DecisionPacket) -> NoReturn:
        raise ValueError("W03_INTERNAL_DETAILS_MUST_NOT_ESCAPE")

    monkeypatch.setattr(binding, "validate_c05_packet", fail)
    error = _error(lambda: binding.build_investigation_case(packet), INVALID)
    assert error.__suppress_context__


def test_b03_b10_b17_b18_exact_projection_and_public_constants() -> None:
    packet = _packet()
    before = canonical_json_bytes(packet)
    case = binding.build_investigation_case(packet)
    assert binding.C02_BINDING_POLICY_VERSION == "w04-c02-v1"
    assert binding.C02_SUBJECT_TYPE == "ORDER"
    assert binding.C02_OPENED_BY == "FLOWLENS_W04_C02_BINDER"
    assert binding.C02_INVALID_DECISION_PACKET == INVALID
    assert binding.C02_FUTURE_INFORMATION == FUTURE
    assert binding.C02_CASE_BINDING_MISMATCH == MISMATCH
    assert type(case) is InvestigationCase and case.schema_version == "investigation-case.v1"
    assert case.source_decision_packet_id == packet.packet_id
    assert case.decision_run_id == packet.run.run_id
    assert case.subject_type == "ORDER" and case.subject_id == packet.run.order_id
    assert case.as_of_time == case.opened_at == packet.run.as_of_time
    assert case.opened_by == "FLOWLENS_W04_C02_BINDER"
    assert case.source_diagnosis_id == packet.diagnosis.diagnosis_id
    assert case.source_recommendation_id == packet.recommendation.recommendation_id
    assert canonical_json_bytes(packet) == before


def test_b04_hashes_complete_packet_including_provenance_excluded_from_packet_id() -> None:
    packet = _packet()
    changed = _provenance_time(packet, "observed_at", packet.run.as_of_time - timedelta(seconds=1))
    assert packet.packet_id == changed.packet_id
    assert canonical_json_bytes(packet) != canonical_json_bytes(changed)
    case = binding.build_investigation_case(packet)
    changed_case = binding.build_investigation_case(changed)
    assert (
        case.source_decision_packet_hash == hashlib.sha256(canonical_json_bytes(packet)).hexdigest()
    )
    assert (
        changed_case.source_decision_packet_hash
        == hashlib.sha256(canonical_json_bytes(changed)).hexdigest()
    )
    assert case.source_decision_packet_hash != packet.packet_id.removeprefix("pkt_")
    assert case.source_decision_packet_hash != packet.snapshot.snapshot_hash
    assert case.source_decision_packet_hash != packet.run.dataset_hash
    assert changed_case.source_decision_packet_hash != case.source_decision_packet_hash
    _error(lambda: binding.validate_investigation_case_binding(changed, case), MISMATCH)


@pytest.mark.parametrize("state", tuple(SignalState))
def test_b11_b13_signal_state_projection_does_not_upgrade_unknown(state: SignalState) -> None:
    packet = _minimal_packet(states=((SignalType.DELIVERY_RISK, state),))
    validate_c05_packet(packet)
    case = binding.build_investigation_case(packet)
    expected_family = () if state is SignalState.INACTIVE else ("DELIVERY_RISK",)
    expected_refs = () if state is SignalState.INACTIVE else (packet.signals.signals[0].signal_id,)
    assert case.risk_families == expected_family and case.source_signal_ids == expected_refs
    assert packet.signals.signals[0].state is state


def test_b14_b15_signal_families_and_ids_are_sorted_unique_and_share_selection() -> None:
    packet = _minimal_packet(
        states=(
            (SignalType.QUALITY_FAILURE, SignalState.UNKNOWN),
            (SignalType.SUPPLIER_LATE_RECEIPT, SignalState.ACTIVE),
            (SignalType.DELIVERY_RISK, SignalState.INACTIVE),
            (SignalType.CAPACITY_PRESSURE, SignalState.ACTIVE),
        )
    )
    validate_c05_packet(packet)
    selected = tuple(
        item for item in packet.signals.signals if item.state is not SignalState.INACTIVE
    )
    case = binding.build_investigation_case(packet)
    assert case.risk_families == tuple(sorted({item.signal_type.value for item in selected}))
    assert case.source_signal_ids == tuple(sorted({item.signal_id for item in selected}))
    assert len(case.risk_families) == len(case.source_signal_ids) == 3
    excluded = next(item for item in packet.signals.signals if item.state is SignalState.INACTIVE)
    assert excluded.signal_id not in case.source_signal_ids


@pytest.mark.parametrize("empty_bundle", [False, True])
def test_b16_empty_retained_signals_are_valid(empty_bundle: bool) -> None:
    packet = _minimal_packet(
        states=()
        if empty_bundle
        else tuple((family, SignalState.INACTIVE) for family in SignalType)
    )
    validate_c05_packet(packet)
    assert all(signal.state is SignalState.INACTIVE for signal in packet.signals.signals)
    case = binding.build_investigation_case(packet)
    assert case.risk_families == case.source_signal_ids == ()
    _validate_binding(packet, case)


@pytest.mark.parametrize(
    "disposition",
    (
        RecommendationDisposition.NO_ACTION,
        RecommendationDisposition.NO_RECOMMENDATION,
        RecommendationDisposition.INVESTIGATION_ONLY,
        RecommendationDisposition.DEFER_TO_HUMAN,
    ),
)
def test_b19_all_four_real_c05_dispositions_remain_eligible(
    disposition: RecommendationDisposition,
) -> None:
    packet = _packet(_real_fixture(disposition))
    before = canonical_json_bytes(packet)
    assert packet.recommendation.disposition is disposition
    case = binding.build_investigation_case(packet)
    assert case.source_recommendation_id == packet.recommendation.recommendation_id
    _validate_binding(packet, case)
    assert canonical_json_bytes(packet) == before


def test_b19_reserved_disposition_is_structural_but_not_canonical_c05() -> None:
    packet = _minimal_packet(disposition=RecommendationDisposition.CANDIDATE_RECOMMENDED)
    packet.recommendation.__post_init__()
    packet.__post_init__()
    with pytest.raises(ValueError):
        validate_c05_packet(packet)
    _error(lambda: binding.build_investigation_case(packet), INVALID)


@pytest.mark.parametrize("field", ["snapshot_observed", "snapshot_ref_observed"])
def test_b20_future_snapshot_observations_survive_w03_and_fail_c02(field: str) -> None:
    future = AS_OF + timedelta(microseconds=1)
    packet = (
        _minimal_packet(snapshot_observed=future)
        if field == "snapshot_observed"
        else (_minimal_packet(snapshot_ref_observed=future))
    )
    validate_c05_packet(packet)
    _error(lambda: binding.build_investigation_case(packet), FUTURE)


@pytest.mark.parametrize("field", ["entry", "source_ref"])
def test_b21_future_snapshot_availability_is_owned_by_frozen_w03(field: str) -> None:
    packet = _minimal_packet()
    entry = packet.snapshot.entries[0]
    future = AS_OF + timedelta(microseconds=1)
    entry = (
        unsafe_replace(entry, available_at=future)
        if field == "entry"
        else unsafe_replace(entry, source_ref=replace(entry.source_ref, available_at=future))
    )
    snapshot = unsafe_replace(packet.snapshot, entries=(entry,))
    attacked = unsafe_replace(packet, snapshot=snapshot)
    with pytest.raises(ValueError, match="unavailable at as_of_time"):
        snapshot.__post_init__()
    _error(lambda: binding.build_investigation_case(attacked), INVALID)


def test_b22_future_evidence_observation_survives_w03_and_fails_c02() -> None:
    packet = _minimal_packet(evidence_observed=AS_OF + timedelta(microseconds=1))
    validate_c05_packet(packet)
    _error(lambda: binding.build_investigation_case(packet), FUTURE)


def test_b23_future_evidence_availability_is_owned_by_frozen_w03() -> None:
    packet = _minimal_packet()
    evidence = unsafe_replace(
        packet.evidence.evidence[0], available_at=AS_OF + timedelta(seconds=1)
    )
    attacked = unsafe_replace(
        packet, evidence=unsafe_replace(packet.evidence, evidence=(evidence,))
    )
    with pytest.raises(ValueError, match="available_at exceeds as_of_time"):
        evidence.__post_init__()
    _error(lambda: binding.build_investigation_case(attacked), INVALID)


@pytest.mark.parametrize("field", ["observed_at", "available_at"])
def test_b24_future_canonical_packet_source_refs_fail_c02(field: str) -> None:
    packet = _provenance_time(_packet(), field, AS_OF + timedelta(microseconds=1))
    validate_c05_packet(packet)
    assert any(
        isinstance(value := getattr(ref, field), datetime) and value > AS_OF
        for ref in packet.provenance.source_refs
    )
    _error(lambda: binding.build_investigation_case(packet), FUTURE)


def test_b20_b24_none_observations_and_exact_boundary_are_valid() -> None:
    for observed in (None, AS_OF):
        packet = _minimal_packet(
            snapshot_observed=observed,
            snapshot_ref_observed=observed,
            evidence_observed=observed,
            source_observed=observed,
        )
        validate_c05_packet(packet)
        case = binding.build_investigation_case(packet)
        _validate_binding(packet, case)


def test_b24_future_counterfactual_measurement_is_not_observational_source_truth() -> None:
    fixture = supplier_fixture()
    packet = _packet(fixture)
    result = fixture.simulations.results[0]
    measurements = tuple(
        sorted(
            (
                *result.measurements,
                NamedValue(name="future_model_at", value=AS_OF + timedelta(days=7), unit=None),
            ),
            key=lambda item: item.name,
        )
    )
    changed_result = rebind_result(result, measurements=measurements)
    changed_results = tuple(
        changed_result if item is result else item for item in fixture.simulations.results
    )
    simulations = rebind_simulation_bundle(fixture, changed_results)
    recommendation = unsafe_replace(
        packet.recommendation, simulation_bundle_id=simulations.simulation_bundle_id
    )
    identity = {
        item.name: getattr(recommendation, item.name)
        for item in fields(recommendation)
        if item.name not in {"recommendation_id", "schema_version", "provenance", "limitations"}
    }
    recommendation = replace(
        recommendation,
        recommendation_id=derive_artifact_id(
            "recommendation-record", "recommendation-record.v1", identity
        ),
    )
    changed = _rebind_packet(packet, simulations=simulations, recommendation=recommendation)
    case = binding.build_investigation_case(changed)
    _validate_binding(changed, case)


@pytest.mark.parametrize("offset_hours", [-7, 8])
def test_b25_timezone_equivalent_instants_have_identical_canonical_outputs(
    offset_hours: int,
) -> None:
    offset = AS_OF.astimezone(timezone(timedelta(hours=offset_hours)))
    first = _minimal_packet()
    second = _minimal_packet(
        as_of=offset,
        snapshot_observed=offset,
        snapshot_ref_observed=offset,
        evidence_observed=offset,
        source_observed=offset,
        available=offset,
    )
    validate_c05_packet(first)
    validate_c05_packet(second)
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert (
        binding.build_investigation_case(first).to_json()
        == binding.build_investigation_case(second).to_json()
    )


def test_b25_dst_fold_future_observation_compares_actual_utc_instants() -> None:
    zone = ZoneInfo("America/New_York")
    boundary = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=0)
    future = boundary.replace(fold=1)
    assert future == boundary  # Python local comparisons alone conceal this future instant.
    assert future.astimezone(UTC) > boundary.astimezone(UTC)
    packet = _minimal_packet(
        as_of=boundary,
        snapshot_observed=future,
        snapshot_ref_observed=boundary,
        evidence_observed=boundary,
        source_observed=boundary,
        available=boundary,
    )
    validate_c05_packet(packet)
    _error(lambda: binding.build_investigation_case(packet), FUTURE)


def test_b26_same_process_is_deterministic_and_validation_preserves_input() -> None:
    packet = _packet()
    before = canonical_json_bytes(packet)
    cases = tuple(binding.build_investigation_case(packet) for _ in range(3))
    assert (
        len(
            {
                (
                    case.to_json(),
                    case.content_hash,
                    case.artifact_id,
                    case.source_decision_packet_hash,
                )
                for case in cases
            }
        )
        == 1
    )
    case_before = canonical_json_bytes(cases[0])
    _validate_binding(packet, cases[0])
    assert canonical_json_bytes(cases[0]) == case_before
    assert canonical_json_bytes(packet) == before


@pytest.mark.parametrize("seed", ["0", "1", "73", "123456"])
def test_b27_b28_real_fresh_process_and_hash_seeds_are_identical(seed: str) -> None:
    case = binding.build_investigation_case(_packet())
    script = """
import json, sys
sys.path.insert(0, 'tests')
from test_c05_recommendation import supplier_fixture
from flowlens.decision.c05_packet import build_decision_packet
from flowlens.investigation.c02_binding import build_investigation_case
case = build_investigation_case(build_decision_packet(*supplier_fixture().args()))
print(json.dumps([case.to_json(), case.content_hash, case.artifact_id,
                  case.source_decision_packet_hash]))
"""
    completed = subprocess.run(
        [sys.executable, "-B", "-c", script],
        cwd=ROOT,
        env={**os.environ, "PYTHONHASHSEED": seed},
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(completed.stdout) == [
        case.to_json(),
        case.content_hash,
        case.artifact_id,
        case.source_decision_packet_hash,
    ]


@pytest.mark.parametrize("attack", ["id", "schema", "nested_id", "mutable", "naive", "float"])
def test_b29_packet_structural_tampering_is_rejected(attack: str) -> None:
    packet = _minimal_packet()
    if attack == "id":
        attacked = unsafe_replace(packet, packet_id="pkt_" + "f" * 64)
    elif attack == "schema":
        attacked = unsafe_replace(packet, schema_version="decision-packet.v2")
    elif attack == "nested_id":
        attacked = unsafe_replace(packet, run=unsafe_replace(packet.run, run_id="run_" + "f" * 64))
    elif attack == "mutable":
        attacked = unsafe_replace(packet, signals=unsafe_replace(packet.signals, signals=[]))
    elif attack == "naive":
        attacked = unsafe_replace(
            packet, run=unsafe_replace(packet.run, as_of_time=AS_OF.replace(tzinfo=None))
        )
    else:
        evidence = unsafe_replace(packet.evidence.evidence[0])
        object.__setattr__(evidence, "value", 1.5)
        attacked = unsafe_replace(
            packet, evidence=unsafe_replace(packet.evidence, evidence=(evidence,))
        )
    case = binding.build_investigation_case(packet)
    _error(lambda: binding.build_investigation_case(attacked), INVALID)
    _error(lambda: binding.validate_investigation_case_binding(attacked, case), INVALID)


@pytest.mark.parametrize(
    "attack",
    [
        "producer",
        "version",
        "inputs",
        "contracts",
        "implementation",
        "source_refs",
        "recommendation_producer",
        "recommendation_version",
        "recommendation_implementation",
    ],
)
def test_b30_packet_provenance_boundary_tampering_is_rejected(attack: str) -> None:
    packet = _minimal_packet()
    value: object
    if attack.startswith("recommendation_"):
        field = attack.removeprefix("recommendation_")
        key = {
            "producer": "producer",
            "version": "producer_version",
            "implementation": "implementation_sha",
        }[field]
        value = "a" * 40 if field == "implementation" else "forged"
        recommendation = replace(
            packet.recommendation,
            provenance=replace(
                packet.recommendation.provenance, **cast(dict[str, Any], {key: value})
            ),
        )
        attacked = replace(packet, recommendation=recommendation)
    else:
        key, value = {
            "producer": ("producer", "forged"),
            "version": ("producer_version", "forged"),
            "inputs": ("input_artifact_ids", ()),
            "contracts": ("contract_versions", ()),
            "implementation": ("implementation_sha", "a" * 40),
            "source_refs": ("source_refs", ()),
        }[attack]
        attacked = replace(
            packet, provenance=replace(packet.provenance, **cast(dict[str, Any], {key: value}))
        )
    _error(lambda: binding.build_investigation_case(attacked), INVALID)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_decision_packet_id", "pkt_" + "f" * 64),
        ("source_decision_packet_hash", "f" * 64),
        ("decision_run_id", "run_" + "f" * 64),
        ("subject_type", "OTHER"),
        ("subject_id", "SO-other"),
        ("as_of_time", AS_OF - timedelta(seconds=1)),
        ("opened_at", AS_OF + timedelta(seconds=1)),
        ("opened_by", "OTHER_ACTOR"),
        ("risk_families", ("OTHER_RISK",)),
        ("source_signal_ids", ("sig_" + "f" * 64,)),
        ("source_diagnosis_id", "diag_" + "f" * 64),
        ("source_recommendation_id", "rec_" + "f" * 64),
    ],
)
def test_b31_b32_complete_case_semantic_mismatches_rejected(field: str, value: object) -> None:
    packet = _minimal_packet()
    case = binding.build_investigation_case(packet)
    changed = replace(case, **cast(dict[str, Any], {field: value}))
    assert InvestigationCase.from_json(changed.to_json()).to_json() == changed.to_json()
    before = canonical_json_bytes(changed)
    _error(lambda: binding.validate_investigation_case_binding(packet, changed), MISMATCH)
    assert canonical_json_bytes(changed) == before


@pytest.mark.parametrize("field", ["artifact_id", "content_hash"])
@pytest.mark.parametrize("attack", ["stale", "enum_same_value"])
def test_b31_b33_original_derived_identity_claims_and_exact_types_revalidated(
    field: str,
    attack: str,
) -> None:
    packet = _minimal_packet()
    case = binding.build_investigation_case(packet)
    legitimate = getattr(case, field)
    value: object = ("icase_" if field == "artifact_id" else "") + "f" * 64
    if attack == "enum_same_value":

        class SpoofedIdentity(StrEnum):
            SPOOF = legitimate

        value = SpoofedIdentity.SPOOF
    attacked = unsafe_replace(case, **{field: value})
    before = canonical_json_bytes(attacked)
    if attack == "enum_same_value":
        assert before == canonical_json_bytes(case)
    _error(lambda: binding.validate_investigation_case_binding(packet, attacked), MISMATCH)
    assert getattr(attacked, field) is value and canonical_json_bytes(attacked) == before


@pytest.mark.parametrize(
    "attack", ["schema", "naive", "hash", "tuple_subclass", "subclass", "other"]
)
def test_b31_case_structure_and_exact_type_rejected_without_mutating_claims(attack: str) -> None:
    packet = _minimal_packet()
    case = binding.build_investigation_case(packet)
    if attack == "schema":
        attacked: Any = unsafe_replace(case, schema_version="investigation-case.v2")
    elif attack == "naive":
        attacked = unsafe_replace(case, opened_at=AS_OF.replace(tzinfo=None))
    elif attack == "hash":
        attacked = unsafe_replace(case, source_decision_packet_hash="invalid")
    elif attack == "tuple_subclass":
        subclass = type("TupleSubclass", (tuple,), {})
        attacked = unsafe_replace(case, risk_families=subclass(case.risk_families))
        assert canonical_json_bytes(attacked) == canonical_json_bytes(case)
    elif attack == "subclass":
        subclass = type("CaseSubclass", (InvestigationCase,), {})
        attacked = object.__new__(subclass)
        for item in fields(case):
            object.__setattr__(attacked, item.name, getattr(case, item.name))
    else:
        attacked = object()
    before = tuple(getattr(attacked, item.name, None) for item in fields(case))
    _error(lambda: binding.validate_investigation_case_binding(packet, attacked), MISMATCH)
    assert tuple(getattr(attacked, item.name, None) for item in fields(case)) == before


def test_b31_hostile_tuple_iterator_is_rejected_before_caller_hooks() -> None:
    packet = _minimal_packet()
    case = binding.build_investigation_case(packet)

    class HostileTuple(tuple[str, ...]):
        def __iter__(self) -> NoReturn:
            raise AssertionError("UNTRUSTED_ITERATOR_MUST_NOT_EXECUTE")

    hostile = HostileTuple(case.risk_families)
    with pytest.raises(AssertionError, match="UNTRUSTED_ITERATOR_MUST_NOT_EXECUTE"):
        tuple(hostile)
    attacked = unsafe_replace(case, risk_families=hostile)
    _error(lambda: binding.validate_investigation_case_binding(packet, attacked), MISMATCH)
    assert attacked.risk_families is hostile
    assert attacked.artifact_id == case.artifact_id and attacked.content_hash == case.content_hash


def test_b33_c01_case_wire_identity_and_immutability_remain_exact() -> None:
    packet = _minimal_packet()
    case = binding.build_investigation_case(packet)
    wire = case.to_json()
    restored = InvestigationCase.from_json(wire)
    assert restored.to_json() == wire
    assert (
        case.content_hash
        == hashlib.sha256(canonical_json_bytes(case.canonical_payload())).hexdigest()
    )
    assert case.artifact_id == "icase_" + case.content_hash
    assert set(json.loads(wire)) == {item.name for item in fields(InvestigationCase)}
    assert not hasattr(case, "__dict__")
    _validate_binding(packet, restored)
    assert restored.to_json() == wire


class CapabilityDenied(RuntimeError):
    """Harness sentinel proving that denied capabilities would fail if invoked."""


def _deny(*_args: object, **_kwargs: object) -> NoReturn:
    raise CapabilityDenied("C02_FORBIDDEN_CAPABILITY")


class NoClock(datetime):
    @classmethod
    def now(cls, tz: Any = None) -> NoReturn:
        _deny(tz)

    @classmethod
    def utcnow(cls) -> NoReturn:
        _deny()


def test_b34_live_capability_denials_and_negative_controls(monkeypatch: pytest.MonkeyPatch) -> None:
    packet = _packet()
    case = binding.build_investigation_case(packet)
    before = canonical_json_bytes(packet)
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
        (secrets, "token_bytes"),
        (secrets, "token_hex"),
        (time, "time"),
        (time, "monotonic"),
        (os, "system"),
        (os, "popen"),
    )
    with monkeypatch.context() as guard:
        for owner, name in denied:
            guard.setattr(owner, name, _deny)
            with pytest.raises(CapabilityDenied):
                getattr(owner, name)()
        guard.setattr(binding, "datetime", NoClock)
        with pytest.raises(CapabilityDenied):
            NoClock.now()
        with pytest.raises(CapabilityDenied):
            NoClock.utcnow()
        result = binding.build_investigation_case(packet)
        _validate_binding(packet, case)
        assert result.to_json() == case.to_json()
    assert canonical_json_bytes(packet) == before


def test_b34_runtime_imports_and_ast_have_no_external_or_execution_capabilities() -> None:
    tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0 and node.module is not None
            imports.add(node.module)
    assert imports <= {
        "__future__",
        "dataclasses",
        "datetime",
        "hashlib",
        "typing",
        "flowlens.decision.c06_validation",
        "flowlens.decision.contracts",
        "flowlens.decision.enums",
        "flowlens.decision.primitives",
        "flowlens.decision.serialization",
        "flowlens.investigation.contracts",
    }
    forbidden = {
        "open",
        "exec",
        "eval",
        "compile",
        "__import__",
        "now",
        "utcnow",
        "time",
        "random",
        "uuid4",
        "uuid1",
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
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            function = node.func
            name = (
                function.id
                if isinstance(function, ast.Name)
                else (function.attr if isinstance(function, ast.Attribute) else "")
            )
            assert name not in forbidden
    script = """
import json, sys
before = set(sys.modules)
import flowlens.investigation.c02_binding
print(json.dumps(sorted(set(sys.modules) - before)))
"""
    completed = subprocess.run(
        [sys.executable, "-B", "-c", script], cwd=ROOT, check=True, capture_output=True, text=True
    )
    added = json.loads(completed.stdout)
    forbidden_prefixes = (
        "sqlalchemy",
        "psycopg",
        "flowlens.db",
        "flowlens.data",
        "socket",
        "subprocess",
        "requests",
        "httpx",
        "openai",
        "anthropic",
        "flowlens.decision.c06_store",
        "flowlens.decision.c07",
        "flowlens.decision.c08",
    )
    assert not any(
        name == prefix or name.startswith(prefix + ".")
        for name in added
        for prefix in forbidden_prefixes
    )


def test_b35_planning_artifact_constructors_are_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    packet = _packet()
    classes = (InvestigationQuestion, InvestigationStep, InvestigationPlan, EvidenceQuerySpec)
    with monkeypatch.context() as guard:
        for cls in classes:
            guard.setattr(cls, "__init__", _deny)
            with pytest.raises(CapabilityDenied):
                cast(Callable[..., object], cls)()
        case = binding.build_investigation_case(packet)
        _validate_binding(packet, case)
    tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
    assert not any(
        isinstance(node, ast.Name) and node.id in {cls.__name__ for cls in classes}
        for node in ast.walk(tree)
    )


def test_b36_c01_frozen_blobs_and_committed_source_governance_pass() -> None:
    # This exact-HEAD proof intentionally fails while source is uncommitted.
    # Precommit implementation checks exclude only this selector; final committed
    # execution and native CI must execute it and require actual verifier PASS.
    expected = {
        "src/flowlens/investigation/__init__.py": "c23929f85dccd78bc72ef3b2b1415c6e8eaf0452",
        "src/flowlens/investigation/contracts.py": "0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e",
        "src/flowlens/investigation/enums.py": "9c818780423f32f144b18666784ebc9ea3abdccc",
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
    c02_entries = [entry for entry in manifest["checkpoints"] if entry["checkpoint"] == "W04-C02"]
    assert len(c02_entries) == 1
    assert [item["path"] for item in c02_entries[0]["files"]] == [
        "src/flowlens/investigation/c02_binding.py"
    ]
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
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
    assert set(expected) | {"src/flowlens/investigation/c02_binding.py"} <= set(
        proof["actual_added_source_paths"]
    )
