"""Bounded W05 governance: historical identity, current plan and protected surfaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import plan_non_integration_shards as planner

ROOT = Path(__file__).resolve().parents[2]
SURFACE_BASELINE = ROOT / "docs/w05/governance/W05_G0_SURFACE_BASELINE.json"
SURFACE_SEAL = "c0010e65beac4d47dec106d350353fc1508a1260b99d5607114fc083617cb189"
SURFACES = ("pyproject.toml", "uv.lock", "docker-compose.yml", "migrations", "apps")
MUTABLE_CI = frozenset(
    {
        "scripts/ci/plan_non_integration_shards.py",
        "scripts/ci/pytest_outcome_receipt.py",
        "scripts/ci/run_non_integration_shard.py",
        "scripts/ci/verify_non_integration_shards.py",
        "tests/test_ci_test_sharding.py",
        "tests/test_c09_ci_gate.py",
        "tests/test_investigation_replay.py",
    }
)
PROTECTED_ROOTS = ("src", "docs/w03", "docs/w04", "scripts/ci", "tests")


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.PIPE)


def require(value: bool, message: str) -> None:
    if not value:
        raise planner.ProofError(message)


def tree_entries(repo: Path, scopes: tuple[str, ...]) -> dict[str, dict[str, str]]:
    entries = {}
    for row in git(repo, "ls-tree", "-rz", planner.HISTORICAL_ANCHOR, "--", *scopes).split(b"\0"):
        if not row:
            continue
        metadata, name = row.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        require(kind == "blob" and mode in {"100644", "100755"}, "nonregular historical source")
        entries[name.decode()] = {"git_blob_oid": oid, "mode": mode}
    return entries


def blob_oid(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def verify_anchor(repo: Path = ROOT) -> None:
    anchor = planner.HISTORICAL_ANCHOR
    require(
        git(repo, "show", "-s", "--format=%P", anchor).decode().strip()
        == "b2b582541d38180c3bf8360699e6df271979829a bd29242f8e21ba31bc7782e0c98e1a8aed3641f8",
        "historical anchor parent mismatch",
    )
    require(
        git(repo, "rev-parse", anchor + "^{tree}").decode().strip()
        == "5b649a7010f1e7255b8d7256fce5b8bf53ffc453",
        "historical anchor tree mismatch",
    )
    git(repo, "merge-base", "--is-ancestor", anchor, "HEAD")


def validate_surface_baseline(value: dict[str, Any]) -> None:
    planner.check_seal(value, "surface_sha256")
    require(
        value.get("surface_sha256") == SURFACE_SEAL
        and value.get("schema_version") == "w05-g0-surface-baseline-v1"
        and value.get("historical_anchor_sha") == planner.HISTORICAL_ANCHOR
        and value.get("scopes") == list(SURFACES),
        "wrong surface baseline seal, anchor or scope",
    )


def regular_bytes(repo: Path, name: str) -> bytes:
    path = repo / name
    require(
        not path.is_symlink() and not path.is_junction()
        and path.is_file() and path.resolve().is_relative_to(repo.resolve()),
        "missing/nonregular protected surface: " + name,
    )
    for parent in path.parents:
        if parent == repo:
            break
        require(not parent.is_symlink() and not parent.is_junction(), "indirect protected surface")
    return path.read_bytes()


def surface_names(repo: Path) -> set[str]:
    names: set[str] = set()
    for name in SURFACES:
        path = repo / name
        require(not path.is_symlink() and not path.is_junction(), "indirect surface root")
        if name in SURFACES[:3]:
            names.add(name)
        elif path.is_dir():
            for item in path.rglob("*"):
                if "__pycache__" not in item.parts and item.is_file():
                    names.add(item.relative_to(repo).as_posix())
    return names


def verify_surfaces(repo: Path = ROOT, baseline: dict[str, Any] | None = None) -> None:
    value = planner.read_json(SURFACE_BASELINE) if baseline is None else baseline
    validate_surface_baseline(value)
    require(surface_names(repo) == set(value["entries"]), "surface path set drift")
    for name, expected in value["entries"].items():
        require(blob_oid(regular_bytes(repo, name)) == expected["git_blob_oid"],
                "surface content drift: " + name)


def verify_protected_material(repo: Path = ROOT) -> None:
    """Keep closed runtime, historical evidence and non-admitted controls intact."""
    original = tree_entries(repo, PROTECTED_ROOTS)
    for name, expected in original.items():
        if name not in MUTABLE_CI:
            require(blob_oid(regular_bytes(repo, name)) == expected["git_blob_oid"],
                    "protected material drift: " + name)
    # New tests and upstream packages need later checkpoint authority; additions inside
    # a closed runtime package or historical evidence plane are never admitted here.
    closed = sorted(
        {"/".join(name.split("/")[:3]) for name in original if name.startswith("src/flowlens/")}
    )
    tracked = {
        name.decode() for name in git(
            repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard",
            "--", "src", "docs/w03", "docs/w04",
        ).split(b"\0") if name
    }
    for name in tracked - set(original):
        require(
            not name.startswith(("docs/w03/", "docs/w04/"))
            and not any(name == root or name.startswith(root + "/") for root in closed),
            "new protected/HGT-plane material: " + name,
        )


def verify_docs(repo: Path = ROOT) -> None:
    required = (
        "CURRENT_PHASE = W05 / SUCCESSOR GOVERNANCE ACTIVE",
        "POST_W04_STABILIZATION = CLOSED",
        "POST_MERGE_DOC_SYNC = COMPLETE",
        "PR8 = MERGED / CLOSED / VERIFIED",
        "P2_03 = MERGED_NATIVE_PROVEN_CLOSED",
        "W04_HISTORICAL_GOVERNANCE_ANCHOR = " + planner.HISTORICAL_ANCHOR,
        "W05_ACTIVE_PLAN = " + planner.PLAN_SCHEMA,
        "W05_C01 = NOT AUTHORIZED BY THIS TASK",
        "W05_PRODUCT_API = NOT IMPLEMENTED",
        "W05_UI = NOT IMPLEMENTED",
        "W06 = NOT AUTHORIZED",
        "FLOWLENS_V1_0 = NOT RELEASED",
    )
    for name in ("AGENTS.md", "docs/CURRENT_STATE.md"):
        lines = (repo / name).read_text(encoding="utf-8").splitlines()
        for line in required:
            require(lines.count(line) == 1, "missing/ambiguous phase projection: " + line)


def verify_current(plan: dict[str, Any], head: str, repo: Path = ROOT) -> dict[str, Any]:
    planner.verify_head(head, repo)
    verify_anchor(repo)
    historical = planner.read_json(planner.HISTORICAL_BASELINE)
    planner.validate_w04_baseline(historical)
    planner.validate_active_policy(planner.read_json(planner.ACTIVE_POLICY))
    require(
        tree_entries(repo, SURFACES) == planner.read_json(SURFACE_BASELINE)["entries"],
        "surface baseline does not describe exact historical tree",
    )
    verify_surfaces(repo)
    verify_protected_material(repo)
    verify_docs(repo)
    planner.validate_plan(
        plan, planner.read_json(planner.WEIGHTS), planner.read_json(planner.BASELINE), head, repo
    )
    require(planner.collect_nodes(planner.MARKER, repo) == plan["current_nodeids"],
            "active plan is not exact current collection")
    flattened = [node for shard in plan["shards"] for node in shard["nodeids"]]
    require(sorted(flattened) == plan["current_nodeids"], "current union mismatch")
    require(len(flattened) == len(set(flattened)), "duplicate current node assignment")
    planner.verify_head(head, repo)
    return planner.sealed(
        {
            "schema_version": "w05-successor-governance-proof-v1",
            "head_sha": head,
            "historical_anchor_sha": planner.HISTORICAL_ANCHOR,
            "plan_sha256": plan["plan_sha256"],
            "historical_baseline_sha256": historical["baseline_sha256"],
            "surface_baseline_sha256": SURFACE_SEAL,
            "HISTORICAL_NO_LOSS": "PASS",
            "EXACT_CURRENT_UNION": "PASS",
            "EXACT_CURRENT_ONCE": "PASS",
            "surface_baseline": "PASS",
            "protected_material": "PASS",
            "phase_projection": "PASS",
            "overall": "PASS",
            "current_plan": planner.plan_summary(plan),
        }, "proof_sha256"
    )



def validate_historical_log(path: Path) -> dict[str, Any]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("{"):
            record = json.loads(line)
            require(isinstance(record, dict), "invalid historical replay record")
            records.append(record)

    def one(key: str) -> dict[str, Any]:
        matching = [item for item in records if key in item]
        require(len(matching) == 1, "missing/ambiguous historical replay record: " + key)
        return dict(matching[0])

    gate = one("gate_contract")
    require(
        gate["gate_contract"] == "PASS"
        and gate.get("closeout_lifecycle") == "W04_POST_MERGE_INTEGRATED"
        and gate.get("adversarial_controls") == 172
        and gate.get("actual_shell_truth_cases") == 223,
        "historical W04 governance result drift",
    )
    collection = gate["collection"]
    require(
        collection.get("nodes") == 2997 and collection.get("files") == 63
        and collection.get("shards") == 7
        and collection.get("node_digest") == planner.CURRENT_NODES_DIGEST
        and collection.get("weights_digest") == planner.MEASURED_WEIGHTS_DIGEST,
        "historical W04 collection identity drift",
    )
    for key, count in (
        ("w04_p2_03_controls", 93),
        ("w04_p2_03_r2_controls", 95),
        ("w04_p2_03_pr8_merge_controls", 98),
    ):
        require(one(key)[key] == count, "historical control count drift")
    merge = one("w04_p2_03_pr8_lifecycle")
    require(
        merge["w04_p2_03_pr8_lifecycle"] == "P2_03_PR8_MERGED_MAIN"
        and merge.get("w04_p2_03_pr8_integration_anchor") == planner.HISTORICAL_ANCHOR
        and merge.get("w04_p2_03_source_tip") == "bd29242f8e21ba31bc7782e0c98e1a8aed3641f8",
        "historical P2 merge lifecycle drift",
    )
    return {
        "historical_anchor_sha": planner.HISTORICAL_ANCHOR,
        "log_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "governance_controls": [172, 223, 93, 95, 98],
        "overall": "PASS",
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--historical-log", type=Path, required=True)
    args = parser.parse_args()
    try:
        # No external-provider/database credentials are read or needed.
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        result = verify_current(planner.read_json(args.plan), args.expected_head)
        historical = validate_historical_log(args.historical_log)
        result = planner.sealed(
            {key: value for key, value in result.items() if key != "proof_sha256"}
            | {"historical_w04_replay": historical}, "proof_sha256"
        )
        planner.write_json(planner.outside_repository(args.output_json), result)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"W05_SUCCESSOR_GOVERNANCE_FAIL_CLOSED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

