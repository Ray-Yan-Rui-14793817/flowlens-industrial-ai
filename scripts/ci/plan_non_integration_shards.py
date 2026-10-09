"""Exact collection, entry no-loss enforcement and deterministic file-atomic LPT."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKER = "not integration"
SHARD_COUNT = 7
ENTRY_SHA = "f50d6c6f8eeacd9df3320dc4a8c6269aa6caa3a5"
ENTRY_DIGEST = "0089b5889f7de2dbe637ddef3774966ae07f6cf6d6518f2648f20e47ccbaa4a7"
ENTRY_FILES_DIGEST = "f252f29b1999267ef1d2f3117f45579c094da3b9001cf34c1e07b524a418480e"
BASELINE = ROOT / "docs/w04/devctrl-02/W04_DEVCTRL_02_ENTRY_TEST_BASELINE.json"
WEIGHTS = ROOT / "docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json"
PLAN_SCHEMA = "w04-devctrl02-non-integration-plan-v1"
SOURCE_NODES_DIGEST = "4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d"
SOURCE_ARTIFACTS_DIGEST = "c111d28caa2d4e319c01873f47cc6cc8bd9a80a9fd172ca2749b29bcc945b83a"
SOURCE_FILE_WEIGHTS_DIGEST = "43740d1f6b1eda83fb9410de761625504a8c96d90dd7c05cd1d69bf001ac0bdc"
WEIGHT_DERIVATION = (
    "Sum of JUnit testcase time attributes by file from the four complete #122 shard artifacts. "
    "Static scheduling evidence only."
)
AUTHORIZED_ADDITION_FILES = frozenset(
    {
        "tests/test_ci_test_sharding.py",
        "tests/test_c09_ci_gate.py",
        "tests/test_ci_change_classifier.py",
        "tests/test_ci_publication_gate.py",
    }
)


class ProofError(ValueError):
    """Evidence is missing, malformed or inconsistent; never infer success."""


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ProofError("noncanonical JSON evidence") from exc


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sealed(payload: dict[str, Any], key: str) -> dict[str, Any]:
    return payload | {key: digest(payload)}


def check_seal(payload: dict[str, Any], key: str) -> None:
    supplied = payload.get(key)
    if not isinstance(supplied, str) or supplied != digest(
        {name: value for name, value in payload.items() if name != key}
    ):
        raise ProofError(f"wrong {key}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProofError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ProofError(f"missing or nonregular evidence: {path}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=lambda token: (_ for _ in ()).throw(ProofError(f"nonfinite {token}")),
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProofError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ProofError("evidence must be an object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise ProofError(f"refuse stale evidence: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False).encode(
            "utf-8"
        )
        + b"\n"
    )


def exact_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    if set(value) != keys:
        raise ProofError(f"{label} schema keys differ")


def integer(value: Any, label: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ProofError(f"invalid {label}")
    return int(value)


def sha(value: Any, size: int = 64) -> str:
    if not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{size}}}", value):
        raise ProofError("invalid SHA")
    return value


def test_file(value: Any, repo: Path | None = None) -> str:
    if not isinstance(value, str):
        raise ProofError("invalid test file")
    path = PurePosixPath(value)
    if (
        not value.startswith("tests/")
        or not value.endswith(".py")
        or str(path) != value
        or any(part in {".", ".."} for part in path.parts)
        or "\\" in value
        or any(ord(char) < 32 for char in value)
    ):
        raise ProofError("invalid test file")
    if repo is not None:
        target = repo / value
        if (
            target.is_symlink()
            or not target.is_file()
            or not target.resolve().is_relative_to(repo.resolve())
        ):
            raise ProofError(f"missing or nonregular test file: {value}")
    return value


def nodes(value: Any, repo: Path | None = None, *, sorted_required: bool = True) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ProofError("empty or invalid node collection")
    for node in value:
        if (
            not isinstance(node, str)
            or "::" not in node
            or not node.split("::", 1)[1]
            or any(ord(char) < 32 for char in node)
        ):
            raise ProofError("invalid node ID")
        test_file(node.split("::", 1)[0], repo)
    if len(set(value)) != len(value):
        raise ProofError("duplicate node ID")
    ordered = sorted(value)
    if sorted_required and value != ordered:
        raise ProofError("unsorted node IDs")
    return ordered


def verify_head(expected: str, repo: Path = ROOT) -> None:
    sha(expected, 40)
    actual = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    if actual != expected:
        raise ProofError("wrong expected head SHA")


def validate_baseline(value: dict[str, Any]) -> list[str]:
    exact_keys(
        value,
        {
            "schema_version",
            "entry_sha",
            "pytest_version",
            "marker_expression",
            "selected_node_count",
            "sorted_nodeids",
            "nodeids_sha256",
            "selected_files",
            "selected_files_sha256",
            "baseline_run_number",
            "baseline_run_id",
        },
        "entry baseline",
    )
    selected = nodes(value["sorted_nodeids"])
    files = sorted({node.split("::", 1)[0] for node in selected})
    if (
        value["schema_version"] != "w04-devctrl02-entry-test-baseline-v1"
        or value["entry_sha"] != ENTRY_SHA
        or value["pytest_version"] != "9.1.1"
        or value["marker_expression"] != MARKER
        or integer(value["selected_node_count"], "baseline count", 1) != len(selected)
        or len(selected) != 2726
        or digest(selected) != ENTRY_DIGEST
        or value["nodeids_sha256"] != ENTRY_DIGEST
        or value["selected_files"] != files
        or digest(files) != ENTRY_FILES_DIGEST
        or value["selected_files_sha256"] != ENTRY_FILES_DIGEST
        or value["baseline_run_number"] != 118
        or value["baseline_run_id"] != 37773147744
    ):
        raise ProofError("wrong entry baseline digest or identity")
    return selected


def enforce_entry(selected: list[str], baseline: dict[str, Any]) -> None:
    entry = set(validate_baseline(baseline))
    current = set(nodes(selected))
    if not entry <= current:
        raise ProofError("entry no-loss guard: missing pre-entry node IDs")
    additions = current - entry
    if any(node.split("::", 1)[0] not in AUTHORIZED_ADDITION_FILES for node in additions):
        raise ProofError("unauthorized DEVCTRL test addition")


def validate_weights(
    value: dict[str, Any], selected_files: set[str] | None = None
) -> dict[str, int]:
    """Validate frozen JUnit evidence and return exact integer millisecond weights."""
    exact_keys(
        value,
        {
            "schema_version",
            "source_run_number",
            "source_run_id",
            "source_sha",
            "derivation_method",
            "source_artifacts",
            "source_collected_node_count",
            "source_collected_nodeids_sha256",
            "total_weight_seconds",
            "shard_count",
            "file_weights",
            "weights_sha256",
        },
        "weights",
    )
    check_seal(value, "weights_sha256")
    if (
        value["schema_version"] != "w04-devctrl02-test-weights-v2"
        or integer(value["source_run_number"], "source run", 1) != 122
        or integer(value["source_run_id"], "source run ID", 1) != 37889883403
        or value["source_sha"] != "9d5b6e3baea1a860446b70d9b254cc3dc41815a4"
        or integer(value["source_collected_node_count"], "source node count", 1) != 2807
        or value["source_collected_nodeids_sha256"] != SOURCE_NODES_DIGEST
        or digest(value["source_artifacts"]) != SOURCE_ARTIFACTS_DIGEST
        or value["derivation_method"] != WEIGHT_DERIVATION
        or integer(value["shard_count"], "shard count", 1) != SHARD_COUNT
    ):
        raise ProofError("wrong scheduling source or shard count")

    def weight(item: Any) -> int:
        if type(item) not in (int, float) or not math.isfinite(item) or item < 0:
            raise ProofError("malformed, negative or nonfinite weight")
        milliseconds = Decimal(str(item)) * 1000
        if milliseconds != milliseconds.to_integral_value():
            raise ProofError("weight must preserve exact JUnit millisecond precision")
        return int(milliseconds)

    entries = value["file_weights"]
    if not isinstance(entries, list) or len(entries) != 62:
        raise ProofError("missing or extra frozen JUnit file weights")
    result: dict[str, int] = {}
    for item in entries:
        if not isinstance(item, dict):
            raise ProofError("malformed weight entry")
        exact_keys(item, {"file", "weight_seconds"}, "weight")
        path = test_file(item["file"])
        if path in result:
            raise ProofError("duplicate file weight")
        result[path] = weight(item["weight_seconds"])
    if (
        list(result) != sorted(result)
        or digest(entries) != SOURCE_FILE_WEIGHTS_DIGEST
        or weight(value["total_weight_seconds"]) != 6671752
        or sum(result.values()) != 6671752
    ):
        raise ProofError("wrong frozen JUnit file weights or total")
    if selected_files is not None and selected_files != set(result):
        raise ProofError(
            "selected test files differ from frozen weight files: missing/extra/unmodeled"
        )
    return result


class CollectionRecorder:
    def __init__(self) -> None:
        self.nodeids: list[str] = []

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        self.nodeids = [item.nodeid for item in session.items]


def collect_nodes(marker: str, repo: Path = ROOT, files: list[str] | None = None) -> list[str]:
    if marker not in {MARKER, "integration"}:
        raise ProofError("invalid marker")
    with tempfile.TemporaryDirectory(prefix="flowlens-collect-") as temporary:
        output = Path(temporary) / "collection.json"
        arguments = [
            sys.executable,
            "-B",
            str(Path(__file__).resolve()),
            "collect",
            "--marker",
            marker,
            "--output",
            str(output),
        ]
        for file in files or []:
            arguments.extend(["--file", test_file(file, repo)])
        result = subprocess.run(arguments, cwd=repo, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise ProofError(
                f"collect-only failed ({result.returncode}): {result.stdout[-3000:]}"
                f"{result.stderr[-1500:]}"
            )
        return nodes(read_json(output)["nodeids"], repo, sorted_required=False)


def build_plan(
    selected: list[str],
    weights: dict[str, Any],
    baseline: dict[str, Any],
    head: str,
    repo: Path = ROOT,
) -> dict[str, Any]:
    sha(head, 40)
    selected = nodes(selected, repo)
    enforce_entry(selected, baseline)
    grouped: dict[str, list[str]] = {}
    for node in selected:
        grouped.setdefault(node.split("::", 1)[0], []).append(node)
    by_weight = validate_weights(weights, set(grouped))
    loads = [0] * SHARD_COUNT
    assignments: dict[str, int] = {}
    for file in sorted(grouped, key=lambda name: (-by_weight[name], name)):
        shard_id = min(range(SHARD_COUNT), key=lambda index: (loads[index], index))
        assignments[file] = shard_id
        loads[shard_id] += by_weight[file]
    files = [
        {
            "file": file,
            "weight_seconds": by_weight[file] / 1000,
            "node_count": len(grouped[file]),
            "nodeids": grouped[file],
            "nodeids_sha256": digest(grouped[file]),
            "shard_id": assignments[file],
        }
        for file in sorted(grouped)
    ]
    shards = []
    for index in range(SHARD_COUNT):
        owned_files = sorted(file for file in grouped if assignments[file] == index)
        owned_nodes = sorted(node for file in owned_files for node in grouped[file])
        if not owned_nodes:
            raise ProofError("empty shard")
        shards.append(
            {
                "shard_id": index,
                "estimated_weight_seconds": loads[index] / 1000,
                "file_count": len(owned_files),
                "node_count": len(owned_nodes),
                "files": owned_files,
                "nodeids": owned_nodes,
                "nodeids_sha256": digest(owned_nodes),
            }
        )
    return sealed(
        {
            "schema_version": PLAN_SCHEMA,
            "head_sha": head,
            "marker_expression": MARKER,
            "pytest_version": pytest.__version__,
            "shard_count": SHARD_COUNT,
            "weights_sha256": weights["weights_sha256"],
            "entry_baseline_nodeids_sha256": baseline["nodeids_sha256"],
            "collected_node_count": len(selected),
            "collected_nodeids": selected,
            "collected_nodeids_sha256": digest(selected),
            "files": files,
            "shards": shards,
        },
        "plan_sha256",
    )


def validate_plan(
    plan: dict[str, Any],
    weights: dict[str, Any],
    baseline: dict[str, Any],
    expected_head: str,
    repo: Path = ROOT,
) -> None:
    check_seal(plan, "plan_sha256")
    if plan.get("head_sha") != expected_head:
        raise ProofError("wrong plan head SHA")
    expected = build_plan(
        nodes(plan.get("collected_nodeids")), weights, baseline, expected_head, repo
    )
    if plan != expected:
        raise ProofError("plan schema, weights, baseline or exact assignment mismatch")


def outside_repository(path: Path, repo: Path = ROOT) -> Path:
    if path.is_symlink() or path.resolve().is_relative_to(repo.resolve()):
        raise ProofError("evidence output must be outside the source repository")
    return path.resolve()


def plan_summary(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        key: plan[key]
        for key in (
            "head_sha",
            "plan_sha256",
            "weights_sha256",
            "entry_baseline_nodeids_sha256",
            "collected_node_count",
            "collected_nodeids_sha256",
        )
    } | {
        "entry_no_loss": "PASS",
        "shards": [
            {
                key: item[key]
                for key in (
                    "shard_id",
                    "file_count",
                    "node_count",
                    "estimated_weight_seconds",
                    "nodeids_sha256",
                )
            }
            for item in plan["shards"]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    collector = sub.add_parser("collect")
    collector.add_argument("--marker", choices=[MARKER, "integration"], required=True)
    collector.add_argument("--output", type=Path, required=True)
    collector.add_argument("--file", action="append", default=[])
    planner = sub.add_parser("plan")
    planner.add_argument("--expected-head", required=True)
    planner.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "collect":
            recorder = CollectionRecorder()
            code = pytest.main(
                ["--collect-only", "-q", "-p", "no:cacheprovider", "-m", args.marker, *args.file],
                plugins=[recorder],
            )
            if code != 0:
                return int(code)
            write_json(args.output, {"nodeids": recorder.nodeids})
        else:
            verify_head(args.expected_head)
            plan = build_plan(
                collect_nodes(MARKER), read_json(WEIGHTS), read_json(BASELINE), args.expected_head
            )
            write_json(outside_repository(args.output), plan)
            print(json.dumps(plan_summary(plan), sort_keys=True))
        return 0
    except (ProofError, OSError, subprocess.CalledProcessError) as exc:
        print(f"PLAN_FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
