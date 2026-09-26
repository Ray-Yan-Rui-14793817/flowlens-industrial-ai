"""Frozen-registry and canonical-input tests for W03-C04."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime

import pytest

from flowlens.decision.c04_registry import build_candidate_set
from flowlens.decision.c04_validation import C04BuildError
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import (
    CandidateSet,
    DiagnosisRecord,
    EvidenceBundle,
    SignalBundle,
    StateSnapshot,
)
from flowlens.decision.diagnosis import evaluate_c03
from flowlens.decision.enums import InterventionFamily
from flowlens.decision.primitives import ArtifactProvenance
from test_c03_signals import build_c03_fixture


def make_c04_fixture(
    *,
    as_of: datetime | None = None,
    dataset_version: str = "dsv-1",
    dataset_hash: str = "a" * 64,
) -> tuple[
    StateSnapshot,
    EvidenceBundle,
    DecisionContext,
    SignalBundle,
    DiagnosisRecord,
    CandidateSet,
]:
    if as_of is None:
        snapshot, evidence, context = build_c03_fixture(
            dataset_version=dataset_version,
            dataset_hash=dataset_hash,
        )
    else:
        snapshot, evidence, context = build_c03_fixture(
            as_of=as_of,
            dataset_version=dataset_version,
            dataset_hash=dataset_hash,
        )
    signals, diagnosis = evaluate_c03(evidence, context)
    candidates = build_candidate_set(evidence, context, signals, diagnosis)
    return snapshot, evidence, context, signals, diagnosis, candidates


def test_exact_four_family_registry_is_complete_deterministic_and_conservative() -> None:
    first = make_c04_fixture()
    second = make_c04_fixture()
    candidates = first[-1]

    assert candidates == second[-1]
    assert len(candidates.candidates) == 4
    by_family = {item.family: item for item in candidates.candidates}
    assert set(by_family) == set(InterventionFamily)
    assert {item.registry_key for item in candidates.candidates} == {
        "c04.no-action.v1",
        "c04.supplier-stress-probe.v1",
        "c04.quality-stress-probe.v1",
        "c04.capacity-stress-probe.v1",
    }
    assert tuple(item.candidate_id for item in candidates.candidates) == tuple(
        sorted(item.candidate_id for item in candidates.candidates)
    )
    for family, candidate in by_family.items():
        assert tuple(item.name for item in candidate.parameters) == tuple(
            sorted(item.name for item in candidate.parameters)
        )
        if family is InterventionFamily.NO_ACTION:
            assert {item.name: item.value for item in candidate.parameters} == {
                "mode": "BASELINE_IDENTITY"
            }
            continue
        codes = {item.code for item in candidate.limitations}
        assert "C04_SCENARIO_SCOPE_NOT_ORDER_TARGETED" in codes
        assert "C04_STRESS_PROBE_NOT_INTERVENTION_EFFICACY" in codes
        assert "C04_STRESS_PROBE_NOT_ACTION_EFFECT" in candidate.reason_codes
        rendered = " ".join(
            (
                *candidate.reason_codes,
                *(item.message for item in candidate.limitations),
            )
        ).lower()
        for forbidden in ("probability of improvement", "confidence"):
            assert forbidden not in rendered
        if "root cause" in rendered:
            assert "does not prove capacity pressure or root cause" in rendered


def test_relevance_is_not_causality_and_all_families_remain_present() -> None:
    *_, candidates = make_c04_fixture()
    for candidate in candidates.candidates:
        if candidate.family is InterventionFamily.NO_ACTION:
            continue
        assert (
            "C04_RELEVANT_SIGNAL_ACTIVE" in candidate.reason_codes
            or "C04_RELEVANCE_NOT_ESTABLISHED" in candidate.reason_codes
        )
        assert all("causal" not in code.lower() for code in candidate.reason_codes)
        assert all("causal" not in item.message.lower() for item in candidate.limitations)


def test_noncanonical_c03_input_is_rebuilt_and_rejected() -> None:
    _, evidence, context, signals, diagnosis, _ = make_c04_fixture()
    tampered = replace(
        signals,
        provenance=ArtifactProvenance(
            producer="tampered",
            producer_version=signals.provenance.producer_version,
            input_artifact_ids=signals.provenance.input_artifact_ids,
            source_refs=signals.provenance.source_refs,
            contract_versions=signals.provenance.contract_versions,
            implementation_sha=None,
        ),
    )
    with pytest.raises(C04BuildError) as caught:
        build_candidate_set(evidence, context, tampered, diagnosis)
    assert caught.value.code == "C04_NONCANONICAL_C03_INPUT"
    assert caught.value.state == "BLOCKED_CONTRACT"
