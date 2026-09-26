"""Contract, isolation, wording, and fail-closed harness for W03-C05."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from flowlens.decision.c05_policy import StressEffect
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.c05_validation import C05BuildError
from flowlens.decision.enums import InterventionFamily, SimulationStatus
from flowlens.decision.primitives import ArtifactProvenance
from test_c05_policy import make_fixture, with_simulations

ROOT = Path(__file__).parents[1]
C05_FILES = tuple(sorted((ROOT / "src/flowlens/decision").glob("c05_*.py")))


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def test_runtime_import_surface_has_no_forbidden_capabilities_or_scenario_engine() -> None:
    forbidden = {
        "flowlens.data.scenarios.application",
        "flowlens.data.scenarios.ground_truth",
        "flowlens.data.scenarios.runtime_adapter",
        "flowlens.decision.c04_simulation",
        "flowlens.db",
        "sqlalchemy",
        "requests",
        "httpx",
        "openai",
        "socket",
        "subprocess",
        "random",
        "pathlib",
    }
    assert len(C05_FILES) == 5
    for path in C05_FILES:
        imports = _imports(path)
        assert forbidden.isdisjoint(imports), (path, imports & forbidden)
        source = path.read_text(encoding="utf-8")
        for token in (
            "datetime.now",
            "datetime.utcnow",
            "time.time",
            "apply_scenario",
            "HumanDecisionEvent",
            "ExplanationRecord",
            "RecommendationEvaluation",
            "OutcomeEvaluation",
        ):
            assert token not in source, (path, token)


def test_pure_package_import_remains_free_of_scenario_hgt_and_c05_eager_imports() -> None:
    code = """
import sys
import flowlens.decision
for name in (
    'flowlens.data.scenarios.application',
    'flowlens.data.scenarios.runtime_adapter',
    'flowlens.data.scenarios.ground_truth',
    'flowlens.decision.c05_evaluation',
    'flowlens.decision.c05_recommendation',
    'flowlens.decision.c05_packet',
):
    assert name not in sys.modules, name
print('PURE')
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == "PURE"


def test_noncanonical_upstream_artifacts_fail_closed() -> None:
    fixture = make_fixture()
    bad_signals = replace(
        fixture.signals,
        provenance=ArtifactProvenance(
            producer="tampered",
            producer_version=fixture.signals.provenance.producer_version,
            input_artifact_ids=fixture.signals.provenance.input_artifact_ids,
            source_refs=fixture.signals.provenance.source_refs,
            contract_versions=fixture.signals.provenance.contract_versions,
            implementation_sha=None,
        ),
    )
    bad_fixture = replace(fixture, signals=bad_signals)
    with pytest.raises(C05BuildError) as caught:
        build_recommendation(*bad_fixture.args())
    assert caught.value.code == "C05_NONCANONICAL_C03_INPUT"

    bad_candidates = replace(
        fixture.candidates,
        provenance=ArtifactProvenance(
            producer="tampered",
            producer_version=fixture.candidates.provenance.producer_version,
            input_artifact_ids=fixture.candidates.provenance.input_artifact_ids,
            source_refs=fixture.candidates.provenance.source_refs,
            contract_versions=fixture.candidates.provenance.contract_versions,
            implementation_sha=None,
        ),
    )
    bad_fixture = replace(fixture, candidates=bad_candidates)
    with pytest.raises(C05BuildError) as caught:
        build_recommendation(*bad_fixture.args())
    assert caught.value.code == "C05_NONCANONICAL_C04_CANDIDATES"

    bad_simulations = replace(
        fixture.simulations,
        provenance=ArtifactProvenance(
            producer="tampered",
            producer_version=fixture.simulations.provenance.producer_version,
            input_artifact_ids=fixture.simulations.provenance.input_artifact_ids,
            source_refs=fixture.simulations.provenance.source_refs,
            contract_versions=fixture.simulations.provenance.contract_versions,
            implementation_sha=None,
        ),
    )
    bad_fixture = replace(fixture, simulations=bad_simulations)
    with pytest.raises(C05BuildError) as caught:
        build_recommendation(*bad_fixture.args())
    assert caught.value.code == "C05_NONCANONICAL_C04_SIMULATION"


def test_malformed_no_action_is_a_hard_contract_failure() -> None:
    fixture = make_fixture()
    malformed = with_simulations(
        fixture,
        {
            InterventionFamily.NO_ACTION: (
                SimulationStatus.FAILED,
                StressEffect.UNCHANGED,
            )
        },
    )
    with pytest.raises(C05BuildError) as caught:
        build_recommendation(*malformed.args())
    assert caught.value.code == "C05_NONCANONICAL_C04_SIMULATION"
    assert caught.value.state == "BLOCKED_CONTRACT"


def test_governance_specs_are_present_valid_and_match_frozen_versions() -> None:
    spec_dir = ROOT / "docs/w03/checkpoints/c05/specs"
    expected = {
        "authorized_paths.json",
        "evaluation_policy.json",
        "score_component_schema.json",
        "reason_codes.json",
        "limitation_codes.json",
    }
    assert {item.name for item in spec_dir.glob("*.json")} == expected
    values = {
        name: json.loads((spec_dir / name).read_text(encoding="utf-8"))
        for name in expected
    }
    assert values["evaluation_policy.json"]["decision_policy_version"] == (
        "w03-c05-decision-v1"
    )
    assert values["score_component_schema.json"]["schema_version"] == (
        "w03-c05-evaluation-v1"
    )
    context_lock = (ROOT / "docs/w03/checkpoints/c05/W03_C05_CONTEXT_LOCK.md").read_text(
        encoding="utf-8"
    )
    assert "context_lock_status = LOCKED" in context_lock
    assert "W03-C05 HUMAN AUTHORIZATION: APPROVED" in context_lock
