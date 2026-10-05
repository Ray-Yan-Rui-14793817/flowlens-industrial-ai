"""Contract, isolation, wording, and fail-closed harness for W03-C05."""

from __future__ import annotations

import ast
import builtins
import json
import random
import socket
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.c05_policy import StressEffect
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.c05_validation import C05BuildError
from flowlens.decision.contracts import InterventionCandidate, SimulationResult
from flowlens.decision.enums import (
    InterventionFamily,
    SignalState,
    SimulationStatus,
)
from flowlens.decision.primitives import (
    ArtifactProvenance,
    EntityRef,
    Limitation,
    NamedValue,
)
from flowlens.decision.serialization import canonical_json_bytes
from test_c05_policy import (
    C05Fixture,
    make_fixture,
    rebind_result,
    rebind_simulation_bundle,
    records_for_active,
    replace_simulation_result,
    unsafe_replace,
    with_simulations,
)

ROOT = Path(__file__).parents[1]
C05_FILES = tuple(sorted((ROOT / "src/flowlens/decision").glob("c05_*.py")))


def _expect_recommendation_rejection(
    fixture: C05Fixture,
    code: str,
) -> None:
    with pytest.raises(C05BuildError) as caught:
        build_recommendation(*fixture.args())
    assert caught.value.code == code
    assert caught.value.state == "BLOCKED_CONTRACT"


def _candidate_for_family(
    fixture: C05Fixture,
    family: InterventionFamily,
) -> InterventionCandidate:
    return next(item for item in fixture.candidates.candidates if item.family is family)


def _result_for_family(
    fixture: C05Fixture,
    family: InterventionFamily,
) -> SimulationResult:
    candidate = _candidate_for_family(fixture, family)
    return next(
        item
        for item in fixture.simulations.results
        if item.candidate_id == candidate.candidate_id
    )


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


@pytest.mark.parametrize("artifact", ("signal", "diagnosis"))
def test_c03_outputs_are_independently_recomputed_and_reject_payload_tampering(
    artifact: str,
) -> None:
    fixture = make_fixture()
    if artifact == "signal":
        original = fixture.signals.signals[0]
        changed_state = (
            SignalState.ACTIVE
            if original.state is not SignalState.ACTIVE
            else SignalState.INACTIVE
        )
        attacked_signal = unsafe_replace(original, state=changed_state)
        attacked_signals = unsafe_replace(
            fixture.signals,
            signals=(attacked_signal, *fixture.signals.signals[1:]),
        )
        attacked = unsafe_replace(fixture, signals=attacked_signals)
    else:
        attacked_diagnosis = unsafe_replace(
            fixture.diagnosis,
            problem_code=f"{fixture.diagnosis.problem_code}_TAMPERED",
        )
        attacked = unsafe_replace(fixture, diagnosis=attacked_diagnosis)
    _expect_recommendation_rejection(attacked, "C05_NONCANONICAL_C03_INPUT")


@pytest.mark.parametrize(
    "attack",
    (
        "missing",
        "extra",
        "duplicate",
        "identifier",
        "payload",
        "family",
        "evidence_reference",
    ),
)
def test_candidate_set_attacks_fail_closed(attack: str) -> None:
    fixture = make_fixture()
    candidates = list(fixture.candidates.candidates)
    first = candidates[0]
    if attack == "missing":
        candidates = candidates[1:]
    elif attack == "extra":
        suffix = "0" if first.candidate_id[-1] != "0" else "1"
        candidates.append(
            unsafe_replace(first, candidate_id=f"{first.candidate_id[:-1]}{suffix}")
        )
        candidates.sort(key=lambda item: item.candidate_id)
    elif attack == "duplicate":
        candidates.append(first)
        candidates.sort(key=lambda item: item.candidate_id)
    elif attack == "identifier":
        suffix = "0" if first.candidate_id[-1] != "0" else "1"
        candidates[0] = unsafe_replace(
            first, candidate_id=f"{first.candidate_id[:-1]}{suffix}"
        )
    elif attack == "payload":
        candidates[0] = unsafe_replace(first, registry_key="C04_TAMPERED")
    elif attack == "family":
        candidates[0] = unsafe_replace(
            first,
            family=(
                InterventionFamily.SUPPLIER_INTERVENTION
                if first.family is not InterventionFamily.SUPPLIER_INTERVENTION
                else InterventionFamily.QUALITY_INTERVENTION
            ),
        )
    elif attack == "evidence_reference":
        candidates[0] = unsafe_replace(
            first,
            supporting_evidence_ids=(f"ev_{'f' * 64}",),
        )
    else:
        raise AssertionError(attack)
    attacked_set = unsafe_replace(fixture.candidates, candidates=tuple(candidates))
    attacked = unsafe_replace(fixture, candidates=attacked_set)
    _expect_recommendation_rejection(attacked, "C05_NONCANONICAL_C04_CANDIDATES")


@pytest.mark.parametrize(
    "attack",
    (
        "result_run",
        "result_snapshot",
        "result_hash",
        "result_candidate",
        "bundle_run",
        "bundle_snapshot",
        "missing_result",
        "extra_result",
        "duplicate_result",
        "result_order",
    ),
)
def test_simulation_bundle_binding_and_cardinality_attacks_fail_closed(
    attack: str,
) -> None:
    fixture = make_fixture()
    results = list(fixture.simulations.results)
    target = results[0]
    if attack == "result_run":
        results[0] = rebind_result(target, run_id="run_tampered")
        bundle = rebind_simulation_bundle(fixture, tuple(results))
    elif attack == "result_snapshot":
        results[0] = rebind_result(target, baseline_snapshot_id="snap_tampered")
        bundle = rebind_simulation_bundle(fixture, tuple(results))
    elif attack == "result_hash":
        results[0] = rebind_result(target, baseline_snapshot_hash="0" * 64)
        bundle = rebind_simulation_bundle(fixture, tuple(results))
    elif attack == "result_candidate":
        other = results[1].candidate_id
        results[0] = rebind_result(target, candidate_id=other)
        bundle = rebind_simulation_bundle(fixture, tuple(results))
    elif attack == "bundle_run":
        bundle = rebind_simulation_bundle(
            fixture, tuple(results), run_id="run_tampered"
        )
    elif attack == "bundle_snapshot":
        bundle = rebind_simulation_bundle(
            fixture, tuple(results), snapshot_id="snap_tampered"
        )
    elif attack == "missing_result":
        bundle = rebind_simulation_bundle(fixture, tuple(results[1:]))
    elif attack == "extra_result":
        suffix = "0" if target.simulation_id[-1] != "0" else "1"
        extra = unsafe_replace(
            target,
            simulation_id=f"{target.simulation_id[:-1]}{suffix}",
        )
        bundle = rebind_simulation_bundle(fixture, tuple((*results, extra)))
    elif attack == "duplicate_result":
        bundle = rebind_simulation_bundle(fixture, tuple((*results, target)))
    elif attack == "result_order":
        bundle = rebind_simulation_bundle(fixture, tuple(reversed(results)))
    else:
        raise AssertionError(attack)
    attacked = unsafe_replace(fixture, simulations=bundle)
    _expect_recommendation_rejection(attacked, "C05_NONCANONICAL_C04_SIMULATION")


@pytest.mark.parametrize("attack", ("status", "scenario", "affected", "measurement"))
def test_no_action_result_attacks_fail_closed(attack: str) -> None:
    fixture = make_fixture()
    target = _result_for_family(fixture, InterventionFamily.NO_ACTION)
    if attack == "status":
        changed = rebind_result(target, status=SimulationStatus.FAILED)
    elif attack == "scenario":
        changed = rebind_result(
            target,
            scenario_id="scenario-forbidden",
            scenario_hash="b" * 64,
        )
    elif attack == "affected":
        changed = rebind_result(
            target,
            affected_entities=(
                EntityRef(entity_type="sales_order", entity_id="SO-TAMPERED"),
            ),
        )
    elif attack == "measurement":
        first = target.measurements[0]
        measurements = (
            NamedValue(name=first.name, value="wrong-type", unit=first.unit),
            *target.measurements[1:],
        )
        changed = rebind_result(target, measurements=measurements)
    else:
        raise AssertionError(attack)
    attacked = replace_simulation_result(fixture, target, changed)
    _expect_recommendation_rejection(attacked, "C05_NONCANONICAL_C04_SIMULATION")


@pytest.mark.parametrize(
    "attack",
    (
        "missing_scenario_id",
        "missing_scenario_hash",
        "measurement_missing",
        "measurement_extra",
        "measurement_name",
        "measurement_unit",
        "measurement_type",
    ),
)
def test_successful_active_result_schema_attacks_fail_closed(attack: str) -> None:
    family = InterventionFamily.SUPPLIER_INTERVENTION
    fixture = with_simulations(
        make_fixture(records_for_active(family)),
        {family: (SimulationStatus.SUCCEEDED, StressEffect.WORSENED)},
    )
    target = _result_for_family(fixture, family)
    measurements = list(target.measurements)
    if attack == "missing_scenario_id":
        changed = rebind_result(target, scenario_id=None)
    elif attack == "missing_scenario_hash":
        changed = rebind_result(target, scenario_hash=None)
    elif attack == "measurement_missing":
        changed = rebind_result(target, measurements=tuple(measurements[1:]))
    elif attack == "measurement_extra":
        measurements.append(NamedValue(name="zz_extra", value=0, unit=None))
        changed = rebind_result(
            target,
            measurements=tuple(sorted(measurements, key=lambda item: item.name)),
        )
    elif attack == "measurement_name":
        measurements[0] = NamedValue(
            name="aa_wrong_name",
            value=measurements[0].value,
            unit=measurements[0].unit,
        )
        changed = rebind_result(
            target,
            measurements=tuple(sorted(measurements, key=lambda item: item.name)),
        )
    elif attack == "measurement_unit":
        measurements[0] = NamedValue(
            name=measurements[0].name,
            value=measurements[0].value,
            unit="WRONG",
        )
        changed = rebind_result(target, measurements=tuple(measurements))
    elif attack == "measurement_type":
        integer_index = next(
            index
            for index, item in enumerate(measurements)
            if item.name == "target_delivered_quantity"
        )
        item = measurements[integer_index]
        measurements[integer_index] = NamedValue(
            name=item.name,
            value="wrong-type",
            unit=item.unit,
        )
        changed = rebind_result(target, measurements=tuple(measurements))
    else:
        raise AssertionError(attack)
    attacked = replace_simulation_result(fixture, target, changed)
    _expect_recommendation_rejection(attacked, "C05_NONCANONICAL_C04_SIMULATION")


@pytest.mark.parametrize("status", (SimulationStatus.FAILED, SimulationStatus.UNAVAILABLE))
@pytest.mark.parametrize(
    "attack",
    ("scenario", "affected", "measurements", "limitation_code", "limitation_message"),
)
def test_failed_and_unavailable_result_payload_attacks_fail_closed(
    status: SimulationStatus,
    attack: str,
) -> None:
    family = InterventionFamily.SUPPLIER_INTERVENTION
    fixture = with_simulations(
        make_fixture(records_for_active(family)),
        {family: (status, StressEffect.UNCHANGED)},
    )
    target = _result_for_family(fixture, family)
    candidate = _candidate_for_family(fixture, family)
    extras = tuple(item for item in target.limitations if item not in candidate.limitations)
    assert len(extras) == 1
    extra = extras[0]
    if attack == "scenario":
        changed = rebind_result(
            target,
            scenario_id="scenario-forbidden",
            scenario_hash="b" * 64,
        )
    elif attack == "affected":
        changed = rebind_result(
            target,
            affected_entities=(
                EntityRef(entity_type="sales_order", entity_id="SO-TAMPERED"),
            ),
        )
    elif attack == "measurements":
        baseline = _result_for_family(fixture, InterventionFamily.NO_ACTION)
        changed = rebind_result(target, measurements=baseline.measurements)
    elif attack == "limitation_code":
        wrong = Limitation(code="C04_WRONG_FAILURE_CODE", message=extra.message)
        limitations = tuple(
            sorted((*candidate.limitations, wrong), key=lambda item: (item.code, item.message))
        )
        changed = rebind_result(target, limitations=limitations)
    elif attack == "limitation_message":
        wrong = Limitation(code=extra.code, message="Wrong frozen message.")
        limitations = tuple(
            sorted((*candidate.limitations, wrong), key=lambda item: (item.code, item.message))
        )
        changed = rebind_result(target, limitations=limitations)
    else:
        raise AssertionError(attack)
    attacked = replace_simulation_result(fixture, target, changed)
    _expect_recommendation_rejection(attacked, "C05_NONCANONICAL_C04_SIMULATION")


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


def test_runtime_capability_traps_and_input_immutability(monkeypatch: pytest.MonkeyPatch) -> None:
    """Execute C05 with forbidden capabilities trapped, not merely source-scanned."""

    family = InterventionFamily.SUPPLIER_INTERVENTION
    fixture = with_simulations(
        make_fixture(records_for_active(family)),
        {family: (SimulationStatus.SUCCEEDED, StressEffect.WORSENED)},
    )
    before = canonical_json_bytes(fixture.args())

    def denied(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("forbidden runtime capability used")

    import flowlens.decision.c04_simulation as c04_simulation

    monkeypatch.setattr(c04_simulation, "build_simulation_bundle", denied)
    monkeypatch.setattr(builtins, "open", denied)
    for name in ("open", "read_text", "read_bytes", "write_text", "write_bytes"):
        monkeypatch.setattr(Path, name, denied)
    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(subprocess, "run", denied)
    monkeypatch.setattr(subprocess, "Popen", denied)
    monkeypatch.setattr(random, "random", denied)
    monkeypatch.setattr(random, "randint", denied)
    monkeypatch.setattr(time, "time", denied)
    monkeypatch.setattr(time, "monotonic", denied)

    original_import = builtins.__import__
    forbidden_import_tokens = (
        "ground_truth",
        "flowlens.db",
        "sqlalchemy",
        "openai",
        "langchain",
        "requests",
        "httpx",
    )

    def guarded_import(
        name: str,
        globals: Any = None,
        locals: Any = None,
        fromlist: Any = (),
        level: int = 0,
    ) -> Any:
        assert not any(token in name for token in forbidden_import_tokens), name
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    recommendation = build_recommendation(*fixture.args())
    packet = build_decision_packet(*fixture.args(), recommendation=recommendation)

    assert packet.recommendation is recommendation
    assert canonical_json_bytes(fixture.args()) == before


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
