"""Published C03 policy, API and authorized-path conformance tests."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

from flowlens.decision.c03_policy import (
    C03_POLICY_REASON,
    C03_POLICY_VERSION,
    LIMITATION_MESSAGES,
    SIGNAL_POLICIES,
)
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import DiagnosisRecord, EvidenceBundle, SignalBundle
from flowlens.decision.diagnosis import build_diagnosis, evaluate_c03
from flowlens.decision.enums import SignalType
from flowlens.decision.signals import build_signal_bundle

ROOT = Path(__file__).parents[1]
SPEC_ROOT = ROOT / "docs" / "w03" / "checkpoints" / "c03" / "specs"


def test_compiled_policy_exactly_matches_published_json() -> None:
    policy = json.loads((SPEC_ROOT / "signal_policy.json").read_text(encoding="utf-8"))
    assert C03_POLICY_VERSION == policy["policy_version"] == "w03-c03-v1"
    assert C03_POLICY_REASON == policy["identity_reason_marker"] == "C03_POLICY_V1"
    assert dict(LIMITATION_MESSAGES) == policy["limitations"]
    assert set(SIGNAL_POLICIES) == set(SignalType)
    for signal_type, compiled in SIGNAL_POLICIES.items():
        published = policy["rules"][signal_type.value]
        assert sorted(compiled.entities) == sorted(published["entities"])
        assert sorted(compiled.domain_limitation_codes) == sorted(published["domain_limitations"])
        assert compiled.active_statement == published["active_statement"]
        assert compiled.unknown_statement == published["unknown_statement"]
        assert (
            compiled.active_claim_type.value if compiled.active_claim_type is not None else None
        ) == published["claim_type"]


def test_public_api_signatures_are_exact_and_narrow() -> None:
    signal_signature = inspect.signature(build_signal_bundle)
    diagnosis_signature = inspect.signature(build_diagnosis)
    evaluation_signature = inspect.signature(evaluate_c03)
    assert tuple(signal_signature.parameters) == ("bundle", "context")
    assert tuple(diagnosis_signature.parameters) == ("bundle", "context", "signals")
    assert tuple(evaluation_signature.parameters) == ("bundle", "context")
    assert inspect.get_annotations(build_signal_bundle, eval_str=True) == {
        "bundle": EvidenceBundle,
        "context": DecisionContext,
        "return": SignalBundle,
    }
    assert inspect.get_annotations(build_diagnosis, eval_str=True) == {
        "bundle": EvidenceBundle,
        "context": DecisionContext,
        "signals": SignalBundle,
        "return": DiagnosisRecord,
    }
    assert inspect.get_annotations(evaluate_c03, eval_str=True) == {
        "bundle": EvidenceBundle,
        "context": DecisionContext,
        "return": tuple[SignalBundle, DiagnosisRecord],
    }


def test_authorized_paths_and_frozen_files_are_explicit() -> None:
    scope = json.loads((SPEC_ROOT / "authorized_paths.json").read_text(encoding="utf-8"))
    assert scope["branch"] == "feat/w03-ai-decision-loop"
    assert scope["entry_sha"] == "2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978"
    assert scope["no_existing_test_edit"] is True
    assert scope["no_workflow_edit"] is True
    expected_runtime = {
        "src/flowlens/decision/c03_policy.py",
        "src/flowlens/decision/c03_validation.py",
        "src/flowlens/decision/signals.py",
        "src/flowlens/decision/diagnosis.py",
    }
    assert expected_runtime <= set(scope["implementation_stage"])
    assert not expected_runtime & set(scope["forbidden_even_when_convenient"])
