"""W03-C03 diagnosis templates, provenance, replay and fail-closed checks."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime

import pytest

from flowlens.decision.c03_policy import SIGNAL_POLICIES
from flowlens.decision.c03_validation import C03BuildError
from flowlens.decision.diagnosis import build_diagnosis, evaluate_c03
from flowlens.decision.enums import ClaimType, SignalState, SignalType
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.decision.signals import build_signal_bundle
from test_c03_signals import build_c03_fixture


def test_diagnosis_is_fixed_template_structured_and_noncausal() -> None:
    _, bundle, context = build_c03_fixture()
    signals, diagnosis = evaluate_c03(bundle, context)
    by_type = {item.signal_type: item for item in signals.signals}
    claims = {item.claim_code: item for item in diagnosis.claims}
    assert diagnosis.problem_code == "OBSERVED_DELIVERY_RISK_INDICATORS"
    assert diagnosis.affected_path[0].entity_type == "fact_sales_order"
    assert diagnosis.affected_path[0].entity_id == "SO-1"
    assert "C03_STRUCTURED_NOT_CAUSAL" in diagnosis.reason_codes
    assert diagnosis.supporting_signal_ids == tuple(
        sorted(item.signal_id for item in signals.signals)
    )
    for signal_type, signal in by_type.items():
        code = f"C03_{signal_type.value}_{signal.state.value}_V1"
        if signal.state is SignalState.INACTIVE:
            assert code not in claims
            continue
        claim = claims[code]
        policy = SIGNAL_POLICIES[signal_type]
        assert claim.statement == (
            policy.active_statement
            if signal.state is SignalState.ACTIVE
            else policy.unknown_statement
        )
        assert claim.claim_type is (
            policy.active_claim_type
            if signal.state is SignalState.ACTIVE
            else ClaimType.UNCERTAINTY_STATEMENT
        )
        assert claim.evidence_ids == signal.evidence_ids
        assert claim.limitations == signal.limitations
    assert any(item.code == "QUALITY_FINALITY_UNKNOWN" for item in diagnosis.uncertainties)
    assert all("root cause" not in item.statement.lower() for item in diagnosis.claims)


def test_diagnosis_provenance_and_identity_replay_are_exact() -> None:
    _, bundle, context = build_c03_fixture()
    first_signals, first = evaluate_c03(bundle, context)
    second_signals, second = evaluate_c03(bundle, context)
    assert canonical_json_bytes(first_signals) == canonical_json_bytes(second_signals)
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert first.diagnosis_id == second.diagnosis_id
    assert first.provenance.producer == "flowlens.decision.diagnosis"
    assert first.provenance.producer_version == "w03-c03-v1"
    assert first.provenance.implementation_sha is None
    assert first.provenance.input_artifact_ids == tuple(
        sorted((bundle.evidence_bundle_id, context.context_id, first_signals.signal_bundle_id))
    )
    assert tuple((item.name, item.version) for item in first.provenance.contract_versions) == (
        ("w03-c01", "v1"),
        ("w03-c02", "v1"),
        ("w03-c02-context", "v1"),
        ("w03-c03", "v1"),
        ("w03-c03-diagnosis", "v1"),
        ("w03-c03-signals", "v1"),
    )


def test_noncanonical_supplied_signal_bundle_is_rejected() -> None:
    _, bundle, context = build_c03_fixture()
    signals = build_signal_bundle(bundle, context)
    tampered = signals.signals[0]
    original = tampered.state
    object.__setattr__(tampered, "state", SignalState.ACTIVE)
    with pytest.raises(C03BuildError) as caught:
        build_diagnosis(bundle, context, signals)
    assert (caught.value.code, caught.value.state) == (
        "C03_SIGNAL_POLICY_MISMATCH",
        "BLOCKED_CONTRACT",
    )
    object.__setattr__(tampered, "state", original)


def test_delivery_problem_precedence_and_fulfillment_override() -> None:
    from test_c03_harness import _patched_records

    overdue = _patched_records(
        "fact_sales_order",
        "SO-1",
        promised_delivery_at=datetime(2026, 1, 19, tzinfo=UTC),
    )
    _, overdue_bundle, overdue_context = build_c03_fixture(overdue)
    overdue_signals, overdue_diagnosis = evaluate_c03(overdue_bundle, overdue_context)
    assert (
        next(
            item.state
            for item in overdue_signals.signals
            if item.signal_type is SignalType.DELIVERY_RISK
        )
        is SignalState.ACTIVE
    )
    assert overdue_diagnosis.problem_code == "DELIVERY_COMMITMENT_WARNING"

    fulfilled = _patched_records("fact_delivery", "D-1", delivered_quantity=10)
    _, fulfilled_bundle, fulfilled_context = build_c03_fixture(fulfilled)
    fulfilled_signals, fulfilled_diagnosis = evaluate_c03(fulfilled_bundle, fulfilled_context)
    assert (
        next(
            item.state
            for item in fulfilled_signals.signals
            if item.signal_type is SignalType.DELIVERY_RISK
        )
        is SignalState.INACTIVE
    )
    assert fulfilled_diagnosis.problem_code == "OBSERVED_DELIVERY_RISK_INDICATORS"
    assert not any("all-clear" in item.statement.lower() for item in fulfilled_diagnosis.claims)


def test_cross_process_replay_produces_identical_artifact_ids() -> None:
    script = """
import json, sys
sys.path.insert(0, 'tests')
from test_c03_signals import build_c03_fixture
from flowlens.decision.diagnosis import evaluate_c03
_, bundle, context = build_c03_fixture()
signals, diagnosis = evaluate_c03(bundle, context)
print(json.dumps({
    'signals': signals.signal_bundle_id,
    'diagnosis': diagnosis.diagnosis_id,
}, sort_keys=True))
"""
    first = subprocess.check_output([sys.executable, "-c", script], text=True).strip()
    second = subprocess.check_output([sys.executable, "-c", script], text=True).strip()
    assert json.loads(first) == json.loads(second)
