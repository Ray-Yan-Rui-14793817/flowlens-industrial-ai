"""DEVCTRL-02 direct collection, scheduling, receipt and fail-closed transport proofs."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/ci"))

import plan_non_integration_shards as planner  # noqa: E402
import pytest_outcome_receipt as outcomes  # noqa: E402
import run_non_integration_shard as runner  # noqa: E402
import verify_non_integration_shards as verifier  # noqa: E402


@pytest.fixture
def baseline() -> dict[str, Any]:
    return planner.read_json(planner.BASELINE)


@pytest.fixture
def weights() -> dict[str, Any]:
    return planner.read_json(planner.WEIGHTS)


@pytest.fixture
def plan(baseline: dict[str, Any], weights: dict[str, Any]) -> dict[str, Any]:
    return planner.build_plan(
        sorted(
            baseline["sorted_nodeids"]
            + [
                "tests/test_ci_test_sharding.py::test_weight_source_and_correct_progress_attribution"
            ]
        ),
        weights,
        baseline,
        planner.ENTRY_SHA,
    )


def reseal(document: dict[str, Any], key: str) -> dict[str, Any]:
    return planner.sealed({name: value for name, value in document.items() if name != key}, key)


def write_junit(path: Path, selected: list[str], skipped: list[str] | None = None) -> None:
    skipped = skipped or []
    suite = ET.Element(
        "testsuite", tests=str(len(selected)), failures="0", errors="0", skipped=str(len(skipped))
    )
    for node in selected:
        case = ET.SubElement(suite, "testcase", classname="fixture", name=node)
        if node in skipped:
            ET.SubElement(case, "skipped", message="accepted")
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def receipt_fixture(
    directory: Path,
    plan: dict[str, Any],
    role: str,
    shard_id: int | None,
    selected: list[str],
    marker: str = planner.MARKER,
) -> dict[str, Any]:
    directory.mkdir(parents=True)
    skipped = sorted(set(outcomes.ACCEPTED_LINUX_SKIPS) & set(selected))
    junit = directory / "junit.xml"
    write_junit(junit, selected, skipped)
    terminal: dict[str, list[str]] = {key: [] for key in outcomes.OUTCOMES}
    terminal["passed"] = sorted(set(selected) - set(skipped))
    terminal["skipped"] = skipped
    value = outcomes.make_receipt(
        plan["head_sha"],
        role,
        marker,
        shard_id,
        plan,
        selected,
        selected,
        terminal,
        0,
        junit,
    )
    planner.write_json(directory / "receipt.json", value)
    return value


def four_receipts(directory: Path, plan: dict[str, Any]) -> None:
    for shard in plan["shards"]:
        receipt_fixture(
            directory / f"shard-{shard['shard_id']}",
            plan,
            "shadow-shard",
            shard["shard_id"],
            shard["nodeids"],
        )


def test_weight_source_and_correct_progress_attribution(weights: dict[str, Any]) -> None:
    # Preserve this historical node ID while replacing its obsolete timing-source assertion.
    by_file = planner.validate_weights(weights)
    assert weights["schema_version"] == "w04-devctrl02-test-weights-v2"
    assert weights["source_run_number"] == 122 and weights["source_run_id"] == 37889883403
    assert weights["source_sha"] == "9d5b6e3baea1a860446b70d9b254cc3dc41815a4"
    assert weights["total_weight_seconds"] == 6671.752
    assert len(by_file) == 62 and sum(by_file.values()) == 6671752
    assert by_file["tests/test_investigation_findings.py"] == 1061491
    assert by_file["tests/test_investigation_human.py"] == 1014403
    assert by_file["tests/test_investigation_human_store.py"] == 736120
    assert by_file["tests/test_ci_test_sharding.py"] == 30045
    assert by_file["tests/test_c06_policy.py"] == 0
    assert [item["artifact_id"] for item in weights["source_artifacts"]] == [
        11599246530,
        11598633083,
        11598796165,
        11598701090,
    ]
    assert sum(item["node_count"] for item in weights["source_artifacts"]) == 2807
    assert not {"step_start_timestamp", "default_unseen_file_weight_seconds"} & set(weights)
    assert all(set(item) == {"file", "weight_seconds"} for item in weights["file_weights"])
    for selected in (
        set(by_file) - {"tests/test_ci_test_sharding.py"},
        set(by_file) | {"tests/unmodeled.py"},
    ):
        with pytest.raises(planner.ProofError, match="missing/extra/unmodeled"):
            planner.validate_weights(weights, selected)
    for field, wrong in (
        ("artifact_id", 0),
        ("junit_sha256", "0" * 64),
        ("receipt_sha256", "0" * 64),
        ("node_count", 1047),
        ("shard_id", 1),
    ):
        damaged = copy.deepcopy(weights)
        damaged["source_artifacts"][0][field] = wrong
        with pytest.raises(planner.ProofError):
            planner.validate_weights(reseal(damaged, "weights_sha256"))


def test_baseline_identity_and_digest_are_deterministic(baseline: dict[str, Any]) -> None:
    selected = planner.validate_baseline(baseline)
    assert len(selected) == 2726
    assert planner.digest(selected) == planner.ENTRY_DIGEST
    assert planner.digest(selected) == hashlib.sha256(planner.canonical(selected)).hexdigest()
    assert planner.canonical(baseline) == planner.canonical(copy.deepcopy(baseline))


@pytest.mark.parametrize("damage", ["hash", "count", "duplicate", "sha", "marker", "extra"])
def test_malformed_baseline_rejected(baseline: dict[str, Any], damage: str) -> None:
    if damage == "hash":
        baseline["nodeids_sha256"] = "0" * 64
    elif damage == "count":
        baseline["selected_node_count"] -= 1
    elif damage == "duplicate":
        baseline["sorted_nodeids"].append(baseline["sorted_nodeids"][0])
    elif damage == "sha":
        baseline["entry_sha"] = "0" * 40
    elif damage == "marker":
        baseline["marker_expression"] = "integration"
    else:
        baseline["unrecognized"] = True
    with pytest.raises(planner.ProofError):
        planner.validate_baseline(baseline)


@pytest.mark.parametrize(
    "damage",
    [
        "negative",
        "nan",
        "infinity",
        "string",
        "bool",
        "duplicate",
        "missing",
        "five",
        "default",
        "shift",
        "hash",
    ],
)
def test_malformed_weight_or_shifted_duration_rejected(
    weights: dict[str, Any], damage: str
) -> None:
    changes: dict[str, Any] = {
        "negative": -1,
        "nan": float("nan"),
        "infinity": float("inf"),
        "string": "1",
        "bool": True,
    }
    if damage in changes:
        weights["file_weights"][0]["weight_seconds"] = changes[damage]
    elif damage == "duplicate":
        weights["file_weights"][1] = weights["file_weights"][0]
    elif damage == "missing":
        weights["file_weights"].pop()
    elif damage == "five":
        weights["shard_count"] = 5
    elif damage == "default":
        weights["default_unseen_file_weight_seconds"] = 1
    elif damage == "shift":
        weights["file_weights"][0]["weight_seconds"] += 1
    else:
        weights["weights_sha256"] = "0" * 64
    with pytest.raises(planner.ProofError):
        if damage != "hash":
            weights = reseal(weights, "weights_sha256")
        planner.validate_weights(weights)


def test_lpt_deterministic_four_shards_file_atomic_exact_union(
    plan: dict[str, Any], baseline: dict[str, Any], weights: dict[str, Any]
) -> None:
    again = planner.build_plan(plan["collected_nodeids"], weights, baseline, planner.ENTRY_SHA)
    assert plan == again
    assert planner.SHARD_COUNT == plan["shard_count"] == 7
    assert [s["shard_id"] for s in plan["shards"]] == list(range(7))
    assert [s["estimated_weight_seconds"] for s in plan["shards"]] == [
        1061.491,
        1014.403,
        919.267,
        919.131,
        919.138,
        919.131,
        919.191,
    ]
    assert [s["file_count"] for s in plan["shards"]] == [1, 1, 10, 15, 10, 14, 11]
    assert "tests/test_c06_policy.py" in plan["shards"][3]["files"]
    assert "tests/test_c06_policy.py" not in plan["shards"][5]["files"]
    assert plan["shards"][0]["files"] == ["tests/test_investigation_findings.py"]
    assert plan["shards"][1]["files"] == ["tests/test_investigation_human.py"]
    files = [file for shard in plan["shards"] for file in shard["files"]]
    nodeids = [node for shard in plan["shards"] for node in shard["nodeids"]]
    assert len(set(files)) == len(files) == len(plan["files"])
    assert len(set(nodeids)) == len(nodeids) == plan["collected_node_count"]
    assert sorted(nodeids) == plan["collected_nodeids"]
    for shard in plan["shards"]:
        assert {node.split("::", 1)[0] for node in shard["nodeids"]} == set(shard["files"])
        for other in plan["shards"]:
            if shard["shard_id"] != other["shard_id"]:
                assert not set(shard["nodeids"]) & set(other["nodeids"])
    heavy = sorted(plan["files"], key=lambda file: (-file["weight_seconds"], file["file"]))
    assert [file["shard_id"] for file in heavy[:7]] == list(range(7))
    unseen = next(
        file for file in plan["files"] if file["file"] == "tests/test_ci_test_sharding.py"
    )
    assert unseen["weight_seconds"] == 30.045
    assert unseen["node_count"] == 1
    planner.validate_plan(plan, weights, baseline, planner.ENTRY_SHA)


def test_lpt_path_then_lowest_shard_tie_break(
    monkeypatch: pytest.MonkeyPatch, baseline: dict[str, Any], weights: dict[str, Any]
) -> None:
    monkeypatch.setattr(
        planner,
        "validate_weights",
        lambda value, selected_files: {file: 1000 for file in selected_files},
    )
    result = planner.build_plan(baseline["sorted_nodeids"], weights, baseline, planner.ENTRY_SHA)
    assert [file["shard_id"] for file in result["files"]] == [
        index % planner.SHARD_COUNT for index in range(len(result["files"]))
    ]


def test_no_loss_and_only_authorized_additions(baseline: dict[str, Any]) -> None:
    entry = baseline["sorted_nodeids"]
    planner.enforce_entry(entry, baseline)
    with pytest.raises(planner.ProofError, match="no-loss"):
        planner.enforce_entry(entry[1:], baseline)
    for file in sorted(planner.AUTHORIZED_ADDITION_FILES):
        planner.enforce_entry(sorted(entry + [file + "::new_authorized_test"]), baseline)
    with pytest.raises(planner.ProofError, match="unauthorized"):
        planner.enforce_entry(
            sorted(entry + ["tests/test_models.py::new_unauthorized_test"]), baseline
        )


@pytest.mark.parametrize(
    "value",
    [
        [],
        ["bad"],
        ["/tests/test_models.py::test_x"],
        ["tests/../test_x.py::test_x"],
        ["tests/test_models.py::test_x\n"],
        ["tests/test_models.py::test_x"] * 2,
    ],
)
def test_invalid_or_duplicate_nodes_rejected(value: list[str]) -> None:
    with pytest.raises(planner.ProofError):
        planner.nodes(value)


def test_missing_test_file_and_wrong_head_fail_closed() -> None:
    with pytest.raises(planner.ProofError, match="missing"):
        planner.test_file("tests/nonexistent_devctrl02.py", ROOT)
    with pytest.raises(planner.ProofError, match="head SHA"):
        planner.verify_head("0" * 40)


@pytest.mark.parametrize(
    "damage",
    [
        "head",
        "plan",
        "weights",
        "baseline",
        "count",
        "duplicate_file",
        "split_file",
        "missing_node",
        "extra",
    ],
)
def test_wrong_plan_bindings_and_assignments_rejected(
    plan: dict[str, Any], baseline: dict[str, Any], weights: dict[str, Any], damage: str
) -> None:
    if damage == "head":
        plan["head_sha"] = "0" * 40
    elif damage == "plan":
        plan["plan_sha256"] = "0" * 64
    elif damage == "weights":
        plan["weights_sha256"] = "0" * 64
    elif damage == "baseline":
        plan["entry_baseline_nodeids_sha256"] = "0" * 64
    elif damage == "count":
        plan["collected_node_count"] -= 1
    elif damage == "duplicate_file":
        plan["files"].append(plan["files"][0])
    elif damage == "split_file":
        plan["shards"][1]["files"].append(plan["shards"][0]["files"][0])
    elif damage == "missing_node":
        plan["shards"][0]["nodeids"].pop()
    else:
        plan["unrecognized"] = True
    if damage != "plan":
        plan = reseal(plan, "plan_sha256")
    with pytest.raises(planner.ProofError):
        planner.validate_plan(plan, weights, baseline, planner.ENTRY_SHA)


def test_collection_deterministic_and_duplicate_json_rejected(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_fixture.py").write_text(
        "import pytest\n@pytest.mark.parametrize('x',[0,1])\ndef test_case(x): assert x >= 0\n",
        encoding="utf-8",
    )
    first = planner.collect_nodes(planner.MARKER, tmp_path)
    assert first == planner.collect_nodes(planner.MARKER, tmp_path)
    assert first == ["tests/test_fixture.py::test_case[0]", "tests/test_fixture.py::test_case[1]"]
    invalid = tmp_path / "bad.json"
    invalid.write_text('{"nodeids":[],"nodeids":["duplicate"]}', encoding="utf-8")
    with pytest.raises(planner.ProofError, match="duplicate JSON"):
        planner.read_json(invalid)


def test_shard_collect_only_mismatch_prevents_execution(
    plan: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(runner, "verify_head", lambda head: None)
    monkeypatch.setattr(runner, "read_json", lambda path: plan)
    monkeypatch.setattr(runner, "validate_plan", lambda *args: None)
    monkeypatch.setattr(runner, "collect_nodes", lambda *args, **kwargs: ["mismatch"])
    with pytest.raises(planner.ProofError, match="collect-only"):
        runner.run_shard(tmp_path / "plan.json", planner.ENTRY_SHA, 0, "shadow-shard", tmp_path)


def test_shard_process_uses_argument_list_without_shell(
    plan: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(runner, "verify_head", lambda head: None)
    monkeypatch.setattr(runner, "read_json", lambda path: plan)
    monkeypatch.setattr(runner, "validate_plan", lambda *args: None)
    monkeypatch.setattr(
        runner, "collect_nodes", lambda *args, **kwargs: plan["shards"][0]["nodeids"]
    )
    captured: list[str] = []

    def process(arguments: list[str], *, check: bool) -> subprocess.CompletedProcess[str]:
        assert check is False
        captured.extend(arguments)
        return subprocess.CompletedProcess(arguments, 0)

    monkeypatch.setattr(subprocess, "run", process)
    assert (
        runner.run_shard(
            tmp_path / "plan.json", planner.ENTRY_SHA, 0, "shadow-shard", tmp_path / "out"
        )
        == 0
    )
    assert captured[0] == sys.executable and "--shard-id" in captured
    assert "--marker" in captured and captured[captured.index("--marker") + 1] == planner.MARKER


def test_real_pytest_terminal_outcomes_include_empty_xfail_and_strict_xpass(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    source = textwrap.dedent("""
        import pytest
        def test_pass(): pass
        def test_skip(): pytest.skip("expected")
        @pytest.mark.xfail(reason="")
        def test_xfail(): assert False
        @pytest.mark.xfail(reason="", strict=False)
        def test_xpass(): pass
        @pytest.mark.xfail(reason="", strict=True)
        def test_strict_xpass(): pass
        def test_failed(): assert False
        @pytest.fixture
        def bad_setup(): raise ValueError("setup")
        def test_setup_error(bad_setup): pass
        @pytest.fixture
        def bad_teardown():
            yield
            raise ValueError("teardown")
        def test_teardown_error(bad_teardown): pass
    """)
    (tmp_path / "tests/test_fixture.py").write_text(source, encoding="utf-8")
    names = [
        "pass",
        "skip",
        "xfail",
        "xpass",
        "strict_xpass",
        "failed",
        "setup_error",
        "teardown_error",
    ]
    assigned = sorted(f"tests/test_fixture.py::test_{name}" for name in names)
    program = """
import sys, json
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import pytest
from pytest_outcome_receipt import OutcomeRecorder
recorder = OutcomeRecorder(json.loads(sys.argv[2]))
code = int(pytest.main(["-q", "--junitxml", "junit.xml"], plugins=[recorder]))
Path("result.json").write_text(json.dumps({"code":code, "collected":recorder.collected,
    "outcomes":recorder.terminal_outcomes()}), encoding="utf-8")
raise SystemExit(code)
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", program, str(ROOT / "scripts/ci"), json.dumps(assigned)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    evidence = planner.read_json(tmp_path / "result.json")
    assert evidence["collected"] == assigned
    for category, expected_names in {
        "passed": ["pass"],
        "skipped": ["skip"],
        "xfail": ["xfail"],
        "xpass": ["strict_xpass", "xpass"],
        "failed": ["failed"],
        "error": ["setup_error", "teardown_error"],
    }.items():
        assert evidence["outcomes"][category] == sorted(
            f"tests/test_fixture.py::test_{name}" for name in expected_names
        )


def test_canonical_receipt_exact_sets_and_digest(plan: dict[str, Any], tmp_path: Path) -> None:
    selected = plan["shards"][0]["nodeids"]
    receipt = receipt_fixture(tmp_path / "receipt", plan, "shadow-shard", 0, selected)
    junit = tmp_path / "receipt/junit.xml"
    outcomes.validate_receipt(receipt, plan, "shadow-shard", 0, selected, junit)
    outcomes.require_success(receipt, junit)
    assert receipt["assigned_nodeids"] == receipt["collected_nodeids"] == selected
    assert receipt == reseal(receipt, "receipt_sha256")
    assert sorted(receipt["passed_nodeids"] + receipt["skipped_nodeids"]) == selected
    # A zero pytest exit status cannot turn either xfail or xpass into accepted success.
    for category in ("xfail", "xpass"):
        invalid = copy.deepcopy(receipt)
        node = invalid["passed_nodeids"].pop()
        invalid["passed_count"] -= 1
        invalid[category + "_nodeids"] = [node]
        invalid[category + "_count"] = 1
        invalid = reseal(invalid, "receipt_sha256")
        outcomes.validate_receipt(invalid, plan, "shadow-shard", 0, selected, junit)
        with pytest.raises(planner.ProofError):
            outcomes.require_success(invalid, junit)


@pytest.mark.parametrize(
    "damage",
    [
        "schema",
        "hash",
        "count",
        "head",
        "shard",
        "role",
        "plan",
        "weights",
        "baseline",
        "missing_node",
        "duplicate",
        "unexpected",
        "outcome_count",
        "junit",
        "extra",
    ],
)
def test_malformed_or_inconsistent_receipt_rejected(
    plan: dict[str, Any], tmp_path: Path, damage: str
) -> None:
    selected = plan["shards"][0]["nodeids"]
    value = receipt_fixture(tmp_path / "receipt", plan, "shadow-shard", 0, selected)
    junit = tmp_path / "receipt/junit.xml"
    if damage == "schema":
        value["schema_version"] = "unknown"
    elif damage == "hash":
        value["receipt_sha256"] = "0" * 64
    elif damage == "count":
        value["collected_node_count"] -= 1
    elif damage == "head":
        value["head_sha"] = "0" * 40
    elif damage == "shard":
        value["shard_id"] = 1
    elif damage == "role":
        value["proof_role"] = "legacy-nonint"
    elif damage in {"plan", "weights"}:
        value[damage + "_sha256"] = "0" * 64
    elif damage == "baseline":
        value["entry_baseline_nodeids_sha256"] = "0" * 64
    elif damage == "missing_node":
        value["passed_nodeids"].pop()
        value["passed_count"] -= 1
    elif damage == "duplicate":
        value["passed_nodeids"].append(value["passed_nodeids"][0])
        value["passed_nodeids"].sort()
        value["passed_count"] += 1
    elif damage == "unexpected":
        value["passed_nodeids"][0] = "tests/test_ci_test_sharding.py::unexpected"
        value["passed_nodeids"].sort()
    elif damage == "outcome_count":
        value["passed_count"] -= 1
    elif damage == "junit":
        value["junit_sha256"] = "0" * 64
    else:
        value["unrecognized"] = True
    if damage != "hash":
        value = reseal(value, "receipt_sha256")
    with pytest.raises(planner.ProofError):
        outcomes.validate_receipt(value, plan, "shadow-shard", 0, selected, junit)


def test_successful_four_shard_aggregate_exact_once(plan: dict[str, Any], tmp_path: Path) -> None:
    four_receipts(tmp_path / "shards", plan)
    receipt = verifier.aggregate(plan, tmp_path / "shards", "shadow-shard", tmp_path / "aggregate")
    assert receipt["collected_nodeids"] == plan["collected_nodeids"]
    assert receipt["collected_node_count"] == plan["collected_node_count"]
    assert receipt["skipped_nodeids"] == outcomes.ACCEPTED_LINUX_SKIPS
    assert receipt["failed_count"] == receipt["error_count"] == 0


@pytest.mark.parametrize(
    "damage",
    [
        "missing",
        "unexpected",
        "duplicate",
        "missing_receipt",
        "extra_file",
        "wrong_head",
        "nonzero",
        "junit_failure",
        "junit_error",
        "new_skip",
        "lost_skip",
    ],
)
def test_aggregate_rejects_missing_duplicate_failed_and_skip_drift(
    plan: dict[str, Any], tmp_path: Path, damage: str
) -> None:
    shards = tmp_path / "shards"
    four_receipts(shards, plan)
    if damage == "missing":
        (shards / "shard-0").rename(shards / "removed")
    elif damage == "unexpected":
        (shards / f"shard-{planner.SHARD_COUNT}").mkdir()
    elif damage == "duplicate":
        target = planner.read_json(shards / "shard-1/receipt.json")
        target["shard_id"] = 0
        (shards / "shard-1/receipt.json").write_bytes(
            planner.canonical(reseal(target, "receipt_sha256"))
        )
    elif damage == "missing_receipt":
        (shards / "shard-0/receipt.json").unlink()
    elif damage == "extra_file":
        (shards / "shard-0/extra.json").write_text("{}", encoding="utf-8")
    else:
        # Find the shard containing accepted skips when testing disappeared skip evidence.
        index = next(
            s["shard_id"]
            for s in plan["shards"]
            if damage != "lost_skip" or set(s["nodeids"]) & set(outcomes.ACCEPTED_LINUX_SKIPS)
        )
        directory = shards / f"shard-{index}"
        target = planner.read_json(directory / "receipt.json")
        if damage == "wrong_head":
            target["head_sha"] = "0" * 40
        elif damage == "nonzero":
            target["pytest_exit_code"] = 1
        elif damage in {"junit_failure", "junit_error"}:
            tree = ET.parse(directory / "junit.xml")
            case = next(tree.getroot().iter("testcase"))
            ET.SubElement(case, "failure" if damage == "junit_failure" else "error")
            tree.getroot().set("failures" if damage == "junit_failure" else "errors", "1")
            tree.write(directory / "junit.xml", encoding="utf-8")
            target["junit_sha256"] = hashlib.sha256(
                (directory / "junit.xml").read_bytes()
            ).hexdigest()
        else:
            if damage == "new_skip":
                node = target["passed_nodeids"].pop()
                target["skipped_nodeids"].append(node)
            else:
                node = target["skipped_nodeids"].pop()
                target["passed_nodeids"].append(node)
            for category in ("passed", "skipped"):
                target[category + "_nodeids"].sort()
                target[category + "_count"] = len(target[category + "_nodeids"])
            write_junit(
                directory / "junit.xml", target["collected_nodeids"], target["skipped_nodeids"]
            )
            target["junit_sha256"] = hashlib.sha256(
                (directory / "junit.xml").read_bytes()
            ).hexdigest()
        (directory / "receipt.json").write_bytes(
            planner.canonical(reseal(target, "receipt_sha256"))
        )
    with pytest.raises(planner.ProofError):
        verifier.aggregate(plan, shards, "shadow-shard", tmp_path / "aggregate")


@pytest.mark.parametrize("category", outcomes.OUTCOMES)
def test_equivalence_compares_each_exact_terminal_set(
    category: str, plan: dict[str, Any], tmp_path: Path
) -> None:
    selected = plan["shards"][0]["nodeids"]
    left = receipt_fixture(tmp_path / "left", plan, "shadow-shard", 0, selected)
    right = copy.deepcopy(left)
    verifier.compare_outcomes(left, right)
    right[category + "_nodeids"] = right[category + "_nodeids"] + ["different exact node"]
    with pytest.raises(planner.ProofError, match="SHADOW_EQUIVALENCE_FAILED"):
        verifier.compare_outcomes(left, right)


def test_integration_and_nonintegration_equivalence_requires_same_exact_collections(
    plan: dict[str, Any], tmp_path: Path
) -> None:
    left = receipt_fixture(tmp_path / "left", plan, "shadow-shard", 0, plan["shards"][0]["nodeids"])
    for marker in ("integration", planner.MARKER):
        right = copy.deepcopy(left)
        left["marker_expression"] = right["marker_expression"] = marker
        verifier.compare_outcomes(left, right)
        right["collected_nodeids"] = right["collected_nodeids"][1:]
        with pytest.raises(planner.ProofError):
            verifier.compare_outcomes(left, right)


def test_complete_legacy_shadow_equivalence_uses_four_bound_receipts(
    plan: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    integration = ["tests/integration/test_database.py::test_fixture_integration"]
    monkeypatch.setattr(verifier, "collect_nodes", lambda marker: integration)
    nonint = plan["collected_nodeids"]
    receipt_fixture(tmp_path / "legacy-nonint", plan, "legacy-nonint", None, nonint)
    receipt_fixture(tmp_path / "shadow-nonint", plan, "shadow-nonint-aggregate", None, nonint)
    receipt_fixture(
        tmp_path / "legacy-integration",
        plan,
        "legacy-integration",
        None,
        integration,
        "integration",
    )
    receipt_fixture(
        tmp_path / "shadow-integration",
        plan,
        "shadow-integration",
        None,
        integration,
        "integration",
    )
    result = verifier.equivalence(
        plan,
        tmp_path / "legacy-nonint",
        tmp_path / "legacy-integration",
        tmp_path / "shadow-nonint",
        tmp_path / "shadow-integration",
    )
    assert result["overall"] == "PASS"
    assert result["coverage_equivalence"] == result["terminal_outcome_equivalence"] == "PASS"
    assert len(result["receipts"]) == 4
    invalid = planner.read_json(tmp_path / "shadow-integration/receipt.json")
    invalid["passed_nodeids"] = []
    invalid["passed_count"] = 0
    invalid["error_nodeids"] = integration
    invalid["error_count"] = 1
    (tmp_path / "shadow-integration/receipt.json").write_bytes(
        planner.canonical(reseal(invalid, "receipt_sha256"))
    )
    with pytest.raises(planner.ProofError):
        verifier.equivalence(
            plan,
            tmp_path / "legacy-nonint",
            tmp_path / "legacy-integration",
            tmp_path / "shadow-nonint",
            tmp_path / "shadow-integration",
        )


def test_stale_missing_or_repository_output_evidence_rejected(tmp_path: Path) -> None:
    with pytest.raises(planner.ProofError, match="outside"):
        planner.outside_repository(ROOT / "devctrl02-pass.json")
    path = tmp_path / "old.json"
    planner.write_json(path, {"result": "FAIL"})
    with pytest.raises(planner.ProofError, match="stale"):
        planner.write_json(path, {"result": "PASS"})
    with pytest.raises(planner.ProofError, match="missing"):
        verifier.read_evidence(tmp_path / "missing")


def test_workflow_exact_transport_timeout_and_no_runtime_dependency_mutation() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "cancel-in-progress" not in workflow and "continue-on-error" not in workflow
    assert "fail-fast: false" in workflow and "max-parallel: 7" in workflow
    assert "shard: [0, 1, 2, 3, 4, 5, 6]" in workflow
    assert not re.search(r"secrets\.|OPENAI_API_KEY|pytest-xdist", workflow)
    for action in re.findall(r"uses: ([^\s]+)", workflow):
        assert re.fullmatch(r"[a-zA-Z0-9-]+/[a-zA-Z0-9-]+@[0-9a-f]{40}", action)
    for block in workflow.split("      - name: Download ")[1:]:
        action = block.split("      - name:", 1)[0]
        assert "name: w04-devctrl02-" in action and "pattern:" not in action
        assert "github.event.pull_request.head.sha" in action
        assert "run-id:" not in action and "github-token:" not in action
    assert "if-no-files-found: error" in workflow
    job_content = workflow.split("jobs:\n", 1)[1]
    starts = list(re.finditer(r"^  ([a-z][a-z0-9-]+):\n", job_content, re.MULTILINE))
    jobs = {
        match[1]: job_content[
            match.start() : starts[index + 1].start()
            if index + 1 < len(starts)
            else len(job_content)
        ]
        for index, match in enumerate(starts)
    }
    assert "shadow-equivalence" not in jobs
    authoritative = {
        "static-and-plan": 15,
        "integration-and-data": 25,
        "non-integration": 55,
        "non-integration-aggregate": 10,
    }
    for name, timeout in authoritative.items():
        content = jobs[name]
        assert f"timeout-minutes: {timeout}" in content
        assert "ref: ${{ github.event_name == 'pull_request'" in content
        assert 'test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD"' in content
    for name, timeout in {
        "quality": 5,
        "w03-ai-loop-gate": 15,
        "verification-gate": 5,
        "compose-smoke": 15,
    }.items():
        assert f"timeout-minutes: {timeout}" in jobs[name]
    shard = jobs["non-integration"]
    assert "pgvector/pgvector:0.8.6-pg17-bookworm" in shard
    assert "check_database_connectivity" in shard and "uv run alembic upgrade head" in shard
    assert "    env:\n      EXPECTED_HEAD:" in shard
    assert "        env:\n          POSTGRES_DB:" in shard
    assert "        env:\n      EXPECTED_HEAD:" not in shard
    assert "--role nonint-shard" in shard
    assert '--role integration-data --marker "integration"' in jobs["integration-and-data"]
    aggregate_job = jobs["non-integration-aggregate"]
    assert 'test "$SHARDS_RESULT" = success' in aggregate_job
    assert 'test "$STATIC_RESULT" = success' in aggregate_job
    assert "--role nonint-shard" in aggregate_job
    assert re.findall(r"Download shard-(\d+) exact-SHA", aggregate_job) == [
        str(index) for index in range(planner.SHARD_COUNT)
    ]
    for path in (
        "pyproject.toml",
        "uv.lock",
        "docker-compose.yml",
        "scripts/ci/run_w03_ai_loop_gate.py",
        "docs/w03/checkpoints/c09/specs/c09_gate_manifest.json",
        "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json",
    ):
        changed = subprocess.run(
            ["git", "diff", planner.ENTRY_SHA, "--", path],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert not changed, path
