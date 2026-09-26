"""Exact DecisionPacket assembly and replay tests for W03-C05."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from dataclasses import replace

import pytest

from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.c05_validation import C05BuildError
from flowlens.decision.primitives import ArtifactProvenance
from flowlens.decision.serialization import canonical_json_bytes
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
