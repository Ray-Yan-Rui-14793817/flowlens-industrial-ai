"""Exact DecisionPacket assembly and replay tests for W03-C05."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from dataclasses import FrozenInstanceError, fields, replace
from typing import Any, cast

import pytest

from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.c05_policy import StressEffect
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.c05_validation import C05BuildError
from flowlens.decision.contracts import DecisionPacket, RecommendationRecord
from flowlens.decision.enums import (
    InterventionFamily,
    RecommendationDisposition,
    SimulationStatus,
)
from flowlens.decision.primitives import ArtifactProvenance, NamedValue
from flowlens.decision.serialization import canonical_json_bytes, canonical_json_text
from test_c05_policy import (
    C05Fixture,
    make_fixture,
    neutral_records,
    unsafe_replace,
    with_simulations,
)
from test_c05_recommendation import supplier_fixture


def test_packet_preserves_exact_nested_artifacts_and_unions_degradation() -> None:
    fixture = supplier_fixture()
    recommendation = build_recommendation(*fixture.args())
    first = build_decision_packet(*fixture.args(), recommendation=recommendation)
    second = build_decision_packet(*fixture.args(), recommendation=recommendation)

    assert first == second
    assert first.run is fixture.run
    assert first.snapshot is fixture.snapshot
    assert first.evidence is fixture.evidence
    assert first.signals is fixture.signals
    assert first.diagnosis is fixture.diagnosis
    assert first.candidates is fixture.candidates
    assert first.simulations is fixture.simulations
    assert first.recommendation is recommendation
    expected_uncertainties = {
        *fixture.evidence.uncertainties,
        *fixture.diagnosis.uncertainties,
        *recommendation.uncertainties,
    }
    assert set(first.uncertainties) == expected_uncertainties
    expected_limitations = {
        *(item for evidence in fixture.evidence.evidence for item in evidence.limitations),
        *(item for signal in fixture.signals.signals for item in signal.limitations),
        *(item for claim in fixture.diagnosis.claims for item in claim.limitations),
        *(item for candidate in fixture.candidates.candidates for item in candidate.limitations),
        *(item for result in fixture.simulations.results for item in result.limitations),
        *recommendation.limitations,
    }
    assert set(first.limitations) == expected_limitations
    assert first.provenance.producer == "flowlens.decision.c05_packet"
    assert first.provenance.producer_version == "w03-c05-packet-v1"


def test_packet_rejects_noncanonical_recommendation_instead_of_repairing_it() -> None:
    fixture = supplier_fixture()
    recommendation = build_recommendation(*fixture.args())
    tampered = replace(
        recommendation,
        provenance=ArtifactProvenance(
            producer="tampered",
            producer_version=recommendation.provenance.producer_version,
            input_artifact_ids=recommendation.provenance.input_artifact_ids,
            source_refs=recommendation.provenance.source_refs,
            contract_versions=recommendation.provenance.contract_versions,
            implementation_sha=None,
        ),
    )
    with pytest.raises(C05BuildError) as caught:
        build_decision_packet(*fixture.args(), recommendation=tampered)
    assert caught.value.code == "C05_NONCANONICAL_RECOMMENDATION"
    assert caught.value.state == "BLOCKED_CONTRACT"


def _assert_packet_rejects_recommendation(
    fixture: C05Fixture,
    recommendation: RecommendationRecord,
) -> None:
    with pytest.raises(C05BuildError) as caught:
        build_decision_packet(*fixture.args(), recommendation=recommendation)
    assert caught.value.code == "C05_NONCANONICAL_RECOMMENDATION"
    assert caught.value.state == "BLOCKED_CONTRACT"


@pytest.mark.parametrize(
    "attack",
    (
        "missing",
        "extra",
        "duplicate",
        "changed_categorical",
        "confidence",
        "probability",
        "utility",
        "benefit",
    ),
)
def test_packet_rejects_score_schema_and_categorical_attacks(attack: str) -> None:
    fixture = supplier_fixture()
    recommendation = build_recommendation(*fixture.args())
    assert len(recommendation.score_components) == 21
    components = list(recommendation.score_components)
    if attack == "missing":
        components.pop()
    elif attack == "extra":
        components.append(NamedValue(name="unexpected_component", value=1, unit=None))
    elif attack == "duplicate":
        components.append(components[0])
    elif attack == "changed_categorical":
        index = next(
            position
            for position, item in enumerate(components)
            if type(item.value) is str
        )
        item = components[index]
        components[index] = NamedValue(
            name=item.name,
            value="FORGED_CATEGORICAL_VALUE",
            unit=item.unit,
        )
    else:
        components.append(NamedValue(name=attack, value=1, unit=None))
    attacked = unsafe_replace(recommendation, score_components=tuple(components))
    _assert_packet_rejects_recommendation(fixture, attacked)


def test_float_score_component_is_rejected_at_contract_construction() -> None:
    with pytest.raises(TypeError, match="wrong type|forbidden"):
        NamedValue(name="confidence", value=cast(Any, 0.5), unit=None)


@pytest.mark.parametrize(
    "attack",
    ("external_evidence", "remove_uncertainty", "remove_limitation"),
)
def test_packet_rejects_grounding_or_degradation_removal(attack: str) -> None:
    if attack == "remove_uncertainty":
        fixture = make_fixture()
    else:
        fixture = supplier_fixture()
    recommendation = build_recommendation(*fixture.args())
    if attack == "external_evidence":
        attacked = unsafe_replace(
            recommendation,
            supporting_evidence_ids=tuple(
                sorted((*recommendation.supporting_evidence_ids, f"ev_{'f' * 64}"))
            ),
        )
    elif attack == "remove_uncertainty":
        assert recommendation.uncertainties
        attacked = unsafe_replace(
            recommendation,
            uncertainties=recommendation.uncertainties[1:],
        )
    elif attack == "remove_limitation":
        assert recommendation.limitations
        attacked = unsafe_replace(
            recommendation,
            limitations=recommendation.limitations[1:],
        )
    else:
        raise AssertionError(attack)
    _assert_packet_rejects_recommendation(fixture, attacked)


def test_packet_preserves_uncertainties_and_limitations_for_every_emitted_disposition() -> None:
    from test_c03_signals import CASES, _records_for_case

    multi_case = next(item for item in CASES if item["case_id"] == "C03-G27")
    multi = make_fixture(list(_records_for_case(multi_case)))
    deferred = with_simulations(
        multi,
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
    fixtures = (
        make_fixture(neutral_records()),
        make_fixture(),
        supplier_fixture(),
        deferred,
    )
    observed: set[RecommendationDisposition] = set()
    for fixture in fixtures:
        recommendation = build_recommendation(*fixture.args())
        packet = build_decision_packet(*fixture.args(), recommendation=recommendation)
        observed.add(recommendation.disposition)
        assert recommendation is packet.recommendation
        assert set(recommendation.uncertainties) <= set(packet.uncertainties)
        assert set(recommendation.limitations) <= set(packet.limitations)
    assert observed == {
        RecommendationDisposition.NO_ACTION,
        RecommendationDisposition.NO_RECOMMENDATION,
        RecommendationDisposition.INVESTIGATION_ONLY,
        RecommendationDisposition.DEFER_TO_HUMAN,
    }


def test_packet_surface_is_exact_immutable_and_contains_no_downstream_or_hgt_content() -> None:
    fixture = supplier_fixture()
    recommendation = build_recommendation(*fixture.args())
    packet = build_decision_packet(*fixture.args(), recommendation=recommendation)

    assert tuple(field.name for field in fields(DecisionPacket)) == (
        "packet_id",
        "schema_version",
        "run",
        "snapshot",
        "evidence",
        "signals",
        "diagnosis",
        "candidates",
        "simulations",
        "recommendation",
        "uncertainties",
        "limitations",
        "provenance",
    )
    with pytest.raises(FrozenInstanceError):
        packet.__setattr__("packet_id", "packet_tampered")
    rendered = canonical_json_text(packet).lower()
    for token in (
        "humandecisionevent",
        "human_decision_event",
        "explanationrecord",
        "explanation_record",
        "recommendationevaluation",
        "recommendation_evaluation",
        "outcomeevaluation",
        "outcome_evaluation",
        "hidden_ground_truth",
        "ground_truth",
        "hgt_",
        "operational_write",
        "schedule_production",
        "procure_automatically",
        "release_quality",
        "mutable_payload",
    ):
        assert token not in rendered


def test_packet_replays_in_same_and_fresh_process() -> None:
    fixture = supplier_fixture()
    recommendation = build_recommendation(*fixture.args())
    local = build_decision_packet(*fixture.args(), recommendation=recommendation)
    digest = hashlib.sha256(canonical_json_bytes(local)).hexdigest()
    code = """
import hashlib
import sys
sys.path.insert(0, 'tests')
from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.serialization import canonical_json_bytes
from test_c05_recommendation import supplier_fixture
fixture = supplier_fixture()
recommendation = build_recommendation(*fixture.args())
packet = build_decision_packet(*fixture.args(), recommendation=recommendation)
print(packet.packet_id)
print(hashlib.sha256(canonical_json_bytes(packet)).hexdigest())
"""
    for _ in range(2):
        completed = subprocess.run(
            [sys.executable, "-c", code],
            check=True,
            capture_output=True,
            text=True,
        )
        assert completed.stdout.splitlines() == [local.packet_id, digest]
