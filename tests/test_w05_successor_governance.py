"""W05-G0 additive admission and fail-closed successor controls (fixtures are not native proof)."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/ci"))

import plan_non_integration_shards as planner  # noqa: E402
import verify_w05_successor_governance as successor  # noqa: E402


@pytest.fixture
def historical() -> dict[str, Any]:
    return planner.read_json(planner.HISTORICAL_BASELINE)


@pytest.fixture
def model() -> dict[str, Any]:
    return planner.read_json(planner.WEIGHTS)


def build(selected: list[str], model: dict[str, Any], repo: Path = ROOT) -> dict[str, Any]:
    return planner.build_plan(
        sorted(selected),
        model,
        planner.read_json(planner.BASELINE),
        planner.HISTORICAL_ANCHOR,
        repo,
    )


def test_exact_historical_baseline_and_anchor(historical: dict[str, Any]) -> None:
    assert len(planner.validate_w04_baseline(historical)) == 2997
    assert historical["file_count"] == len(historical["files"]) == 63
    assert historical["shard_count"] == 7
    assert historical["governance_controls"] == [172, 223, 93, 95, 98]
    assert historical["w03"] == {"selectors": 38, "cases": 85}
    assert historical["w04"] == {"families": 9, "selectors": 67, "cases": 81}
    assert historical["integration_cases"] == 70
    successor.verify_anchor(ROOT)


def test_new_test_file_admitted_with_conservative_weight(
    historical: dict[str, Any], model: dict[str, Any], tmp_path: Path
) -> None:
    for file in historical["files"] + ["tests/test_w05_fixture.py"]:
        target = tmp_path / file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# collection-control fixture only\n")
    selected = historical["nodeids"] + ["tests/test_w05_fixture.py::test_added"]
    plan = build(selected, model, tmp_path)
    assert plan["addition_node_count"] == plan["addition_file_count"] == 1
    assert plan["current_node_count"] == 2998 and plan["current_file_count"] == 64
    row = next(item for item in plan["files"] if item["file"] == "tests/test_w05_fixture.py")
    assert row["weight_basis"] == "CONSERVATIVE_MAX_HISTORICAL_WEIGHT"
    assert row["weight_milliseconds"] == max(planner.validate_weights(model).values()) == 2040544
    assert row["collection_changed"] and not row["historical_file"]


def test_added_node_in_historical_file_admitted(
    historical: dict[str, Any], model: dict[str, Any]
) -> None:
    file = historical["files"][0]
    plan = build(historical["nodeids"] + [file + "::test_w05_addition_fixture"], model)
    row = next(item for item in plan["files"] if item["file"] == file)
    assert plan["addition_node_count"] == 1 and plan["addition_file_count"] == 0
    assert row["historical_file"] and row["collection_changed"]
    assert row["weight_basis"] == "CONSERVATIVE_MAX_HISTORICAL_WEIGHT"
    assert row["weight_milliseconds"] == max(planner.validate_weights(model).values())


def test_same_collection_same_plan_changed_collection_changes_identity(
    historical: dict[str, Any], model: dict[str, Any]
) -> None:
    first = build(historical["nodeids"], model)
    assert first == build(copy.deepcopy(historical["nodeids"]), copy.deepcopy(model))
    changed = build(
        historical["nodeids"] + [historical["files"][0] + "::test_added_fixture"], model
    )
    assert first["plan_sha256"] != changed["plan_sha256"]
    assert first["current_nodeids_sha256"] != changed["current_nodeids_sha256"]
    assert first["historical_nodeids_sha256"] == changed["historical_nodeids_sha256"]
    measured = planner.validate_weights(model)
    zeros = {"tests/test_c06_policy.py", "tests/test_c08_prompt.py"}
    assert {name for name, value in measured.items() if value == 0} == zeros
    for row in first["files"]:
        zero = row["file"] in zeros
        expected_basis = "CONSERVATIVE_MAX_HISTORICAL_WEIGHT" if zero else "HISTORICAL_MEASURED"
        assert row["weight_basis"] == expected_basis
        assert row["weight_milliseconds"] == (2040544 if zero else measured[row["file"]])
        assert row["weight_milliseconds"] > 0
        assert not row["collection_changed"]
    flattened = [n for shard in changed["shards"] for n in shard["nodeids"]]
    assert len(flattened) == len(set(flattened)) == changed["current_node_count"]
    assert sorted(flattened) == changed["current_nodeids"]


@pytest.mark.parametrize("damage", ["delete", "rename", "duplicate"])
def test_historical_loss_and_duplicate_rejected(
    historical: dict[str, Any], model: dict[str, Any], damage: str
) -> None:
    selected = list(historical["nodeids"])
    if damage == "delete":
        selected.pop()
    elif damage == "rename":
        selected[-1] += "_renamed"
    else:
        selected.append(selected[0])
    with pytest.raises(planner.ProofError):
        build(selected, model)


@pytest.mark.parametrize("damage", ["seal", "anchor", "digest", "node_count", "file", "extra"])
def test_historical_baseline_tampering_rejected(historical: dict[str, Any], damage: str) -> None:
    if damage == "seal":
        historical["baseline_sha256"] = "0" * 64
    elif damage == "anchor":
        historical["historical_anchor_sha"] = "0" * 40
    elif damage == "digest":
        historical["nodeids_sha256"] = "0" * 64
    elif damage == "node_count":
        historical["node_count"] = 1
    elif damage == "file":
        historical["files"][0] = "tests/substitution.py"
    else:
        historical["hidden_ground_truth"] = "admitted"
    if damage != "seal":
        historical = planner.sealed(
            {k: v for k, v in historical.items() if k != "baseline_sha256"}, "baseline_sha256"
        )
    with pytest.raises(planner.ProofError):
        planner.validate_w04_baseline(historical)


@pytest.mark.parametrize(
    "key,value",
    [
        ("shard_count", 8),
        ("runtime_hgt_access", "ALLOWED"),
        ("operational_mutation", "ALLOWED"),
        ("future_leakage", "ALLOWED"),
        ("changed_or_new_file_weight", "ZERO"),
        ("hidden_ground_truth", "ADMITTED"),
    ],
)
def test_wrong_policy_and_protected_admission_rejected(key: str, value: object) -> None:
    policy = planner.read_json(planner.ACTIVE_POLICY)
    policy[key] = value
    changed = planner.sealed(
        {k: v for k, v in policy.items() if k != "policy_sha256"}, "policy_sha256"
    )
    with pytest.raises(planner.ProofError):
        planner.validate_active_policy(changed)


@pytest.mark.parametrize("damage", ["unsealed", "shard_count", "missing_shard", "duplicate_node"])
def test_current_plan_tampering_rejected(
    historical: dict[str, Any], model: dict[str, Any], damage: str
) -> None:
    plan = build(historical["nodeids"], model)
    if damage == "unsealed":
        plan["plan_sha256"] = "0" * 64
    elif damage == "shard_count":
        plan["shard_count"] = 8
    elif damage == "missing_shard":
        plan["shards"].pop()
    else:
        plan["shards"][1]["nodeids"].append(plan["shards"][0]["nodeids"][0])
    if damage != "unsealed":
        plan = planner.sealed({k: v for k, v in plan.items() if k != "plan_sha256"}, "plan_sha256")
    with pytest.raises(planner.ProofError):
        planner.validate_plan(
            plan, model, planner.read_json(planner.BASELINE), planner.HISTORICAL_ANCHOR
        )


def test_zero_fallback_fails_closed(
    historical: dict[str, Any], model: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        planner, "validate_weights", lambda value: dict.fromkeys(historical["files"], 0)
    )
    with pytest.raises(planner.ProofError, match="fallback"):
        planner.active_file_weights(
            model, {"tests/new.py": ["tests/new.py::test_one"]}, historical["nodeids"]
        )


@pytest.mark.parametrize(
    "surface", ["pyproject.toml", "uv.lock", "docker-compose.yml", "migrations", "apps"]
)
def test_frozen_surface_drift_rejected(surface: str, tmp_path: Path) -> None:
    baseline = planner.read_json(successor.SURFACE_BASELINE)
    for name in baseline["entries"]:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(successor.git(ROOT, "show", planner.HISTORICAL_ANCHOR + ":" + name))
    successor.verify_surfaces(tmp_path, baseline)
    name = next(
        name for name in baseline["entries"] if name == surface or name.startswith(surface + "/")
    )
    (tmp_path / name).write_bytes(b"unauthorized surface drift\n")
    with pytest.raises(planner.ProofError, match="surface content drift"):
        successor.verify_surfaces(tmp_path, baseline)


def test_surface_addition_and_resealed_baseline_rejected(tmp_path: Path) -> None:
    baseline = planner.read_json(successor.SURFACE_BASELINE)
    altered = copy.deepcopy(baseline)
    altered["entries"]["apps/hgt.json"] = {"git_blob_oid": "0" * 40, "mode": "100644"}
    altered = planner.sealed(
        {k: v for k, v in altered.items() if k != "surface_sha256"}, "surface_sha256"
    )
    with pytest.raises(planner.ProofError):
        successor.validate_surface_baseline(altered)
    with pytest.raises(planner.ProofError, match="path set"):
        successor.verify_surfaces(tmp_path, baseline)


def test_closed_protected_source_mutation_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    name = "src/flowlens/investigation/protected_fixture.py"
    path = tmp_path / name
    path.parent.mkdir(parents=True)
    path.write_bytes(b"unauthorized mutation\n")
    monkeypatch.setattr(
        successor,
        "tree_entries",
        lambda repo, scopes: {
            name: {"git_blob_oid": successor.blob_oid(b"accepted fixture\n"), "mode": "100644"}
        },
    )
    with pytest.raises(planner.ProofError, match="protected material drift"):
        successor.verify_protected_material(tmp_path)


def test_actual_surface_and_protected_material_unchanged() -> None:
    assert "tests/test_ci_change_classifier.py" in successor.MUTABLE_CI
    assert "tests/test_ci_publication_gate.py" not in successor.MUTABLE_CI
    assert successor.MUTABLE_CI == {
        "scripts/ci/plan_non_integration_shards.py",
        "scripts/ci/pytest_outcome_receipt.py",
        "scripts/ci/run_non_integration_shard.py",
        "scripts/ci/verify_non_integration_shards.py",
        "tests/test_ci_change_classifier.py",
        "tests/test_ci_test_sharding.py",
        "tests/test_c09_ci_gate.py",
        "tests/test_investigation_replay.py",
    }
    successor.verify_surfaces(ROOT)
    successor.verify_protected_material(ROOT)
    successor.verify_docs(ROOT)


def test_workflow_separates_historical_replay_from_current_semantics() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    w04 = workflow.split("  w04-investigation-gate:\n", 1)[1].split("\n  compose-smoke:", 1)[0]
    assert "run_w04_investigation_gate.py" in w04
    assert "verify_w04_investigation_gate_contract.py" not in w04
    w05 = workflow.split("  w05-successor-governance:\n", 1)[1].split("\n  verification-gate:", 1)[
        0
    ]
    assert "git -c core.autocrlf=false worktree add --detach" in w05
    assert planner.HISTORICAL_ANCHOR in w05
    assert 'cd "$HISTORICAL"' in w05
    assert 'HISTORICAL_VENV="$RUNNER_TEMP/w05-historical-venv"' in w05
    sync = 'UV_PROJECT_ENVIRONMENT="$HISTORICAL_VENV" uv sync --frozen'
    interpreter = '"$HISTORICAL_VENV/bin/python" -B'
    assert w05.index('cd "$HISTORICAL"') < w05.index(sync) < w05.index(interpreter)
    assert "$GITHUB_WORKSPACE/.venv/bin/python" not in w05
    assert w05.count('test -z "$(git status --porcelain)"') == 2
    assert 'PYTHONPATH="$HISTORICAL/src"' in w05
    assert "set -euo pipefail" in w05
    assert "verify_w05_successor_governance.py" in w05
    assert "W05_RESULT" in workflow
    assert 'test "$W05_RESULT" = success' in workflow
    assert 'test "$W05_RESULT" = skipped' in workflow


def test_missing_historical_replay_never_becomes_success(tmp_path: Path) -> None:
    path = tmp_path / "incomplete.log"
    path.write_text(json.dumps({"gate_contract": "PASS"}) + "\n")
    with pytest.raises(planner.ProofError):
        successor.validate_historical_log(path)


def test_current_collection_contains_every_historical_node(historical: dict[str, Any]) -> None:
    selected = planner.collect_nodes(planner.MARKER)
    planner.enforce_historical(selected, historical)
    assert any(node.startswith("tests/test_w05_successor_governance.py::") for node in selected)
    assert len(selected) > 2997
    assert set(historical["nodeids"]) <= set(selected)
    # No historic test ID is removed or renamed by the four admitted meta-test edits.
    assert len(planner.collect_nodes("integration")) == 70


@pytest.mark.parametrize("failure", ["none", "sync", "verifier", "dirty"])
def test_historical_replay_shell_environment_and_failure_propagation(
    tmp_path: Path, failure: str
) -> None:
    """Execute the real workflow shell with bounded git/uv/interpreter fixtures."""
    import shutil
    import subprocess
    import textwrap

    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    step = workflow.split("      - name: Replay historical W04 governance at exact anchor\n", 1)[1]
    script = textwrap.dedent(step.split("        run: |\n", 1)[1].split("\n      - name:", 1)[0])
    bash = shutil.which("bash") if sys.platform != "win32" else "C:/Program Files/Git/bin/bash.exe"
    assert bash and Path(bash).is_file()
    fixture = r"""
set -euo pipefail
RUNNER_TEMP="$PWD/runner"
GITHUB_WORKSPACE="$PWD/current"
mkdir -p "$GITHUB_WORKSPACE"
printf current > "$GITHUB_WORKSPACE/uv.lock"
git() {
  case "$*" in
    "-c core.autocrlf=false worktree add --detach $RUNNER_TEMP/w05-historical ANCHOR")
      mkdir -p "$RUNNER_TEMP/w05-historical/src"
      printf historical > "$RUNNER_TEMP/w05-historical/uv.lock"
      printf historical > "$RUNNER_TEMP/w05-historical/pyproject.toml";;
    "rev-parse HEAD") printf ANCHOR;;
    "status --porcelain")
      if [[ "$FAILURE" == dirty && -f "$RUNNER_TEMP/verified" ]]; then printf dirty; fi;;
    *) return 91;;
  esac
}
uv() {
  test "$*" = "sync --frozen"
  test "$PWD" = "$RUNNER_TEMP/w05-historical"
  test "$(cat uv.lock)" = historical
  test "$(cat pyproject.toml)" = historical
  test "$UV_PROJECT_ENVIRONMENT" = "$RUNNER_TEMP/w05-historical-venv"
  if [[ "$FAILURE" == sync ]]; then return 92; fi
  mkdir -p "$UV_PROJECT_ENVIRONMENT/bin"
  cat > "$UV_PROJECT_ENVIRONMENT/bin/python" <<'PYTHON_FIXTURE'
#!/usr/bin/env bash
set -euo pipefail
test "$PWD" = "$RUNNER_TEMP/w05-historical"
test "$PYTHONPATH" = "$RUNNER_TEMP/w05-historical/src"
test "$*" = "-B scripts/ci/verify_w04_investigation_gate_contract.py"
if [[ "$FAILURE" == verifier ]]; then exit 93; fi
touch "$RUNNER_TEMP/verified"
printf 'fixture replay completed\n'
PYTHON_FIXTURE
  chmod +x "$UV_PROJECT_ENVIRONMENT/bin/python"
}
export RUNNER_TEMP GITHUB_WORKSPACE FAILURE
"""
    fixture = fixture.replace("ANCHOR", planner.HISTORICAL_ANCHOR)
    result = subprocess.run(
        [bash, "--noprofile", "--norc", "-c", "FAILURE=" + failure + "\n" + fixture + script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert (result.returncode == 0) == (failure == "none"), result.stdout + result.stderr
    assert (tmp_path / "runner/verified").exists() == (failure in {"none", "dirty"})
