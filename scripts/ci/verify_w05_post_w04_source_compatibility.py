"""Exact W05 initial-materialization epoch; historical W04 authority stays frozen."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

import plan_non_integration_shards as planner

ROOT = Path(__file__).resolve().parents[2]
ENTRY = "2af8fcd9c3f2fce5121b1b7a3ecead6067eb8aec"
POLICY = "docs/w05/governance/W05_POST_W04_SOURCE_ADMISSION_POLICY.json"
POLICY_SEAL = "2911ec2274c7f6710fb2d3425831a26549c9e93c9abfa280031d6393461e3568"
ADMITTED = (
    "src/flowlens/product/__init__.py",
    "src/flowlens/product/contracts.py",
    "src/flowlens/product/projection.py",
)
FROZEN_W04 = {
    "scripts/ci/verify_w04_source_evolution.py": "4efaefed505e24796a0c2fa545ce4b7eb252d70a",
    "scripts/ci/run_w04_investigation_gate.py": "4319c2cb62e27f1460e91eccfa2367f61d07ce29",
    "scripts/ci/verify_w04_investigation_gate_contract.py": (
        "d432791ded6dac89dd744c1773b233af725d891d"
    ),
    "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json": "8a4555dba4bfbe6556f19413d323f8b1761ebd54",
    "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json": (
        "7a81e38202ac1ce0ed1a3b4a494f85c41b52c52c"
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise planner.ProofError(message)


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.PIPE)


def blob_oid(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def policy_payload() -> dict[str, Any]:
    return {
        "schema_version": "w05-post-w04-source-admission-v2",
        "authority_entry_sha": ENTRY,
        "owner_checkpoint": "W05-C01",
        "admission_epoch": "C01_PRODUCT_ROOT_BOOTSTRAP",
        "admission_kind": "INITIAL_MATERIALIZATION_ONLY",
        "admitted_root": "src/flowlens/product",
        "implementation_may_mutate_policy": False,
        "content_authority": "SEPARATE_C01_CONTRACT",
        "admitted_paths": [{"path": name, "mode": "100644"} for name in ADMITTED],
    }


def validate_policy(value: dict[str, Any]) -> None:
    planner.check_seal(value, "policy_sha256")
    require(value == policy_payload() | {"policy_sha256": POLICY_SEAL}, "source policy drift")


def entries(repo: Path, revision: str, *scopes: str) -> dict[str, dict[str, str]]:
    result = {}
    for row in git(repo, "ls-tree", "-rz", revision, "--", *scopes).split(b"\0"):
        if row:
            metadata, raw_name = row.split(b"\t", 1)
            mode, kind, oid = metadata.decode("ascii").split()
            result[raw_name.decode("utf-8")] = {"mode": mode, "kind": kind, "oid": oid}
    return result


def regular(entry: dict[str, str], name: str, mode: str | None = None) -> None:
    require(
        entry["kind"] == "blob"
        and entry["mode"] in {"100644", "100755"}
        and (mode is None or entry["mode"] == mode),
        "nonregular or wrong-mode Git entry: " + name,
    )


def working_bytes(repo: Path, name: str) -> bytes:
    path = repo / name
    for part in (path, *path.parents):
        if part == repo:
            break
        require(not part.is_symlink() and not part.is_junction(), "indirect working entry")
    require(path.is_file() and stat.S_ISREG(path.lstat().st_mode), "nonregular working entry")
    return path.read_bytes()


def source_entries(repo: Path, revision: str) -> dict[str, dict[str, str]]:
    value = entries(repo, revision, "src")
    for name, row in value.items():
        regular(row, name)
    return value


def working_source(repo: Path) -> set[str]:
    result: set[str] = set()

    def walk(directory: Path) -> None:
        require(not directory.is_symlink() and not directory.is_junction(), "indirect source")
        require(stat.S_ISDIR(directory.lstat().st_mode), "nonregular source directory")
        for path in directory.iterdir():
            require(not path.is_symlink() and not path.is_junction(), "nonregular working source")
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode):
                walk(path)
            else:
                require(stat.S_ISREG(mode), "nonregular working source")
                name = path.relative_to(repo).as_posix()
                if "__pycache__" not in path.parts or path.suffix != ".pyc":
                    result.add(name)

    walk(repo / "src")
    return result


def introduction(repo: Path, head: str) -> str:
    """Find the sole policy introduction in actual reachable successor history."""
    git(repo, "merge-base", "--is-ancestor", ENTRY, head)
    revisions = git(repo, "rev-list", "--reverse", "--topo-order", ENTRY + ".." + head)
    candidates = []
    for revision in revisions.decode().splitlines():
        value = entries(repo, revision, POLICY)
        if POLICY not in value:
            continue
        parents = git(repo, "show", "-s", "--format=%P", revision).decode().split()
        if all(POLICY not in entries(repo, parent, POLICY) for parent in parents):
            candidates.append((revision, parents))
    require(len(candidates) == 1, "missing or ambiguous policy introduction")
    revision, parents = candidates[0]
    require(parents == [ENTRY], "policy introduction parent must be exact C2")
    return str(revision)


def verify_source_compatibility(
    repo: Path = ROOT, expected_head: str | None = None
) -> dict[str, Any]:
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    require(expected_head is None or expected_head == head, "wrong expected source head")
    policy = planner.read_json(repo / POLICY)
    validate_policy(policy)
    intro = introduction(repo, head)
    policy_entry = entries(repo, intro, POLICY)[POLICY]
    regular(policy_entry, POLICY, "100644")
    baseline = source_entries(repo, ENTRY)
    require(
        not any(
            n == "src/flowlens/product" or n.startswith("src/flowlens/product/") for n in baseline
        ),
        "source already present in policy parent",
    )
    require(source_entries(repo, intro) == baseline, "policy and source cannot self-authorize")
    frozen = {n: {"mode": "100644", "kind": "blob", "oid": o} for n, o in FROZEN_W04.items()}
    history = [
        intro,
        *git(repo, "rev-list", "--reverse", "--topo-order", "--ancestry-path", intro + ".." + head)
        .decode()
        .splitlines(),
    ]
    materialized: str | None = None
    product: dict[str, dict[str, str]] = {}
    for revision in history:
        require(
            entries(repo, revision, POLICY).get(POLICY) == policy_entry,
            "policy changed after introduction",
        )
        current_frozen = entries(repo, revision, *FROZEN_W04)
        require(current_frozen == frozen, "frozen W04 object drift")
        current = source_entries(repo, revision)
        require(
            all(current.get(n) == row for n, row in baseline.items()),
            "closed historical source drift",
        )
        extra = {n: row for n, row in current.items() if n not in baseline}
        require(not extra or set(extra) == set(ADMITTED), "partial or extra source materialization")
        for name, row in extra.items():
            regular(row, name, "100644")
        if extra and materialized is None:
            parents = git(repo, "show", "-s", "--format=%P", revision).decode().split()
            require(bool(parents), "materialization parent missing")
            for parent in parents:
                require(
                    entries(repo, parent, POLICY).get(POLICY) == policy_entry,
                    "materialization requires prior exact policy",
                )
                require(
                    source_entries(repo, parent) == baseline,
                    "materialization parent already contains source",
                )
                delta = (
                    git(repo, "diff", "--name-only", parent, revision, "--", "src")
                    .decode()
                    .splitlines()
                )
                require(
                    sorted(delta) == list(ADMITTED),
                    "materialization src delta must be exact three paths",
                )
            materialized, product = revision, extra
        elif materialized is not None:
            require(extra == product, "admitted source changed after first materialization")
            parents = git(repo, "show", "-s", "--format=%P", revision).decode().split()
            require(
                not all(source_entries(repo, parent) == baseline for parent in parents),
                "multiple first materialization commits",
            )
    require(materialized is not None or head == intro, "staged admission must be introduction HEAD")
    current = source_entries(repo, head)
    require(working_source(repo) == set(current), "working source path inventory drift")
    require(
        not git(repo, "status", "--porcelain", "--untracked-files=all", "--", "src"),
        "uncommitted source drift",
    )
    for name, row in (current | frozen | {POLICY: policy_entry}).items():
        require(blob_oid(working_bytes(repo, name)) == row["oid"], "working bytes drift: " + name)
    # The compatibility authority introduced by this epoch cannot evolve inside C01.
    helper = "scripts/ci/verify_w05_post_w04_source_compatibility.py"
    introduced_helper = entries(repo, intro, helper).get(helper)
    require(introduced_helper is not None, "missing committed compatibility authority")
    assert introduced_helper is not None
    regular(introduced_helper, helper, "100644")
    require(
        entries(repo, head, helper).get(helper) == introduced_helper,
        "compatibility authority drift",
    )
    require(
        blob_oid(working_bytes(repo, helper)) == introduced_helper["oid"],
        "working compatibility authority drift",
    )
    w03 = source_entries(repo, "af61bdfd5f7cf7961811c4c2dc8e554dd7eed509")
    return planner.sealed(
        {
            "schema_version": "w05-post-w04-source-compatibility-proof-v1",
            "overall": "PASS",
            "expected_head": head,
            "authority_entry_sha": ENTRY,
            "policy_introduction_sha": intro,
            "policy_sha256": POLICY_SEAL,
            "policy_git_blob": policy_entry,
            "compatibility_verifier_git_blob": introduced_helper,
            "SOURCE_ADMISSION_POLICY": "PASS",
            "SOURCE_ADMISSION_STATE": "ADMISSION_STAGED"
            if materialized is None
            else "BOOTSTRAP_MATERIALIZED",
            "materialization_sha": materialized,
            "admitted_source_entries": product,
            "PRODUCT_SOURCE_PRESENT": "NO" if materialized is None else "YES",
            "W04_VERIFIER_HISTORICAL_IDENTITY": "PASS",
            "COMMITTED_SOURCE_INVENTORY": "PASS",
            "WORKING_SOURCE_INVENTORY": "PASS",
            "actual_added_source_paths": sorted(set(current) - set(w03)),
        },
        "proof_sha256",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    try:
        proof = verify_source_compatibility(args.repo, args.expected_head)
        if args.output_json is not None:
            planner.write_json(planner.outside_repository(args.output_json), proof)
        print(json.dumps(proof, sort_keys=True))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print("POST_W04_SOURCE_COMPATIBILITY_FAIL_CLOSED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
