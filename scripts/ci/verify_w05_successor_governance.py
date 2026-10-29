"""Bounded W05 governance: historical identity, current plan and protected surfaces."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

import plan_non_integration_shards as planner
import verify_w05_post_w04_source_compatibility as compatibility

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
        "tests/test_ci_change_classifier.py",
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


def git_tree_entry(repo: Path, revision: str, name: str) -> dict[str, str]:
    """Read one exact regular committed blob; filesystem execute bits are not authority."""
    rows = [row for row in git(repo, "ls-tree", "-z", revision, "--", name).split(b"\0") if row]
    require(len(rows) == 1, "missing/ambiguous committed entry: " + name)
    metadata, actual_name = rows[0].split(b"\t", 1)
    mode, kind, oid = metadata.decode().split()
    require(actual_name.decode() == name, "wrong committed entry: " + name)
    require(kind == "blob" and mode in {"100644", "100755"}, "nonregular committed entry: " + name)
    return {"git_blob_oid": oid, "mode": mode}


def blob_oid(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def verify_anchor(repo: Path = ROOT) -> None:
    """Validate historical identity/ancestry, including authorized main descendants.

    Exact G0 candidate topology is external G0_TASK_TOPOLOGY_PROOF evidence;
    this long-lived HISTORICAL_ANCESTRY_GUARD is not a bootstrap lifecycle guard.
    """
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
        not path.is_symlink()
        and not path.is_junction()
        and path.is_file()
        and path.resolve().is_relative_to(repo.resolve()),
        "missing/nonregular protected surface: " + name,
    )
    for parent in path.parents:
        if parent == repo:
            break
        require(not parent.is_symlink() and not parent.is_junction(), "indirect protected surface")
    return path.read_bytes()


def git_surface_entries(repo: Path, revision: str) -> dict[str, dict[str, str]]:
    """Inventory every committed frozen-surface leaf using Git object authority."""
    raw = git(repo, "ls-tree", "-rz", revision, "--", *SURFACES)
    require(not raw or raw.endswith(b"\0"), "malformed committed surface inventory")
    entries: dict[str, dict[str, str]] = {}
    for row in raw[:-1].split(b"\0") if raw else []:
        require(bool(row) and b"\t" in row, "malformed committed surface entry")
        metadata, raw_name = row.split(b"\t", 1)
        fields = metadata.split(b" ")
        require(len(fields) == 3 and all(fields), "malformed committed surface metadata")
        try:
            mode, kind, oid = (field.decode("ascii") for field in fields)
            name = raw_name.decode("utf-8")
        except UnicodeError as error:
            raise planner.ProofError("malformed committed surface encoding") from error
        require(
            kind == "blob" and mode in {"100644", "100755"}, "nonregular committed surface: " + name
        )
        require(
            re.fullmatch(r"[0-9a-f]{40}", oid) is not None,
            "malformed committed surface object: " + name,
        )
        require(
            bool(name)
            and not name.startswith("/")
            and "\\" not in name
            and all(part not in {"", ".", ".."} for part in name.split("/"))
            and (name in SURFACES or name.startswith(("migrations/", "apps/"))),
            "malformed/out-of-scope committed surface path",
        )
        require(name not in entries, "ambiguous committed surface path: " + name)
        entries[name] = {"git_blob_oid": oid, "mode": mode}
    return entries


def surface_names(repo: Path) -> set[str]:
    """Inspect working surfaces without following any link or nonregular entry."""
    names: set[str] = set()

    def entry_mode(path: Path) -> int:
        try:
            info = path.lstat()
        except OSError as error:
            raise planner.ProofError(
                "working surface inventory unreadable: " + str(path)
            ) from error
        attributes = getattr(info, "st_file_attributes", 0) or 0
        require(
            not stat.S_ISLNK(info.st_mode)
            and not path.is_junction()
            and not attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400),
            "nonregular working surface: " + str(path),
        )
        require(
            stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode),
            "nonregular working surface: " + str(path),
        )
        return info.st_mode

    def walk(directory: Path, cache: bool = False) -> None:
        try:
            children = list(directory.iterdir())
        except OSError as error:
            raise planner.ProofError(
                "working surface inventory unreadable: " + str(directory)
            ) from error
        for child in children:
            mode = entry_mode(child)
            if stat.S_ISDIR(mode):
                walk(child, cache or child.name == "__pycache__")
            elif not cache:
                names.add(child.relative_to(repo).as_posix())

    for name in SURFACES:
        path = repo / name
        mode = entry_mode(path)
        if name in SURFACES[:3]:
            require(stat.S_ISREG(mode), "nonregular working surface root: " + name)
            names.add(name)
        else:
            require(stat.S_ISDIR(mode), "nonregular working surface root: " + name)
            walk(path)
    return names


def verify_surfaces(repo: Path = ROOT, baseline: dict[str, Any] | None = None) -> None:
    value = planner.read_json(SURFACE_BASELINE) if baseline is None else baseline
    validate_surface_baseline(value)
    current_entries = git_surface_entries(repo, "HEAD")
    require(set(current_entries) == set(value["entries"]), "committed surface path set drift")
    for name, expected in value["entries"].items():
        current = current_entries[name]
        require(
            current["git_blob_oid"] == expected["git_blob_oid"],
            "surface committed content drift: " + name,
        )
        require(current["mode"] == expected["mode"], "surface mode drift: " + name)
    require(surface_names(repo) == set(value["entries"]), "working surface path set drift")
    for name, expected in value["entries"].items():
        require(
            blob_oid(regular_bytes(repo, name)) == expected["git_blob_oid"],
            "surface content drift: " + name,
        )


EVOLVED_TESTS = {
    "tests/test_investigation_case_binding.py": (
        "test_b36_c01_frozen_blobs_and_committed_source_governance_pass",
        "1de8de47568c7df789cde60d7ffa079721fe5147",
    ),
    "tests/test_investigation_replay.py": (
        "_check_native_metadata",
        "7c3e0bfdced89654f758c1920bd85cdf4a65117d",
    ),
}


def validate_test_source_unit(baseline: bytes, current: bytes, symbol: str) -> dict[str, str]:
    """The two reviewed lifecycle seams; no other source unit is mutable."""
    before_text, after_text = baseline.decode("utf-8"), current.decode("utf-8")
    before_tree, after_tree = ast.parse(before_text), ast.parse(after_text)
    before = [n for n in before_tree.body if isinstance(n, ast.FunctionDef) and n.name == symbol]
    after = [n for n in after_tree.body if isinstance(n, ast.FunctionDef) and n.name == symbol]
    require(len(before) == len(after) == 1, "missing/renamed/duplicate evolved test symbol")
    left, right = before[0], after[0]
    require(
        [ast.dump(n, include_attributes=False) for n in before_tree.body if n is not left]
        == [ast.dump(n, include_attributes=False) for n in after_tree.body if n is not right],
        "non-authorized top-level source unit changed",
    )
    require(before_tree.body.index(left) == after_tree.body.index(right), "source unit order drift")
    before_lines, after_lines = (
        before_text.splitlines(keepends=True),
        after_text.splitlines(keepends=True),
    )
    left_start = min([left.lineno, *(n.lineno for n in left.decorator_list)]) - 1
    right_start = min([right.lineno, *(n.lineno for n in right.decorator_list)]) - 1
    require(
        before_lines[:left_start] == after_lines[:right_start]
        and before_lines[left.end_lineno :] == after_lines[right.end_lineno :],
        "non-authorized source bytes changed",
    )
    require(
        before_lines[left_start : left.lineno] == after_lines[right_start : right.lineno],
        "evolved function header/decorators changed",
    )
    expected = copy.deepcopy(left)
    if symbol == "_check_native_metadata":
        sets = [
            n
            for n in ast.walk(expected)
            if isinstance(n, ast.Set)
            and all(isinstance(e, ast.Constant) for e in n.elts)
            and {ast.literal_eval(e) for e in n.elts} == {"I", "C"}
        ]
        require(len(sets) == 1, "wrong native metadata baseline")
        sets[0].elts.append(ast.Constant(value="UNKNOWN"))
    else:
        require(
            symbol == EVOLVED_TESTS["tests/test_investigation_case_binding.py"][0],
            "unauthorized second source unit",
        )
        replacements = 0
        for node in ast.walk(expected):
            if (
                isinstance(node, ast.Constant)
                and node.value == "scripts/ci/verify_w04_source_evolution.py"
            ):
                node.value = "scripts/ci/verify_w05_post_w04_source_compatibility.py"
                replacements += 1
            if isinstance(node, ast.List):
                positions = [
                    i
                    for i, e in enumerate(node.elts)
                    if isinstance(e, ast.Constant) and e.value == "--manifest"
                ]
                if positions:
                    require(len(positions) == 1, "ambiguous B36 baseline arguments")
                    index = positions[0]
                    require(
                        ast.literal_eval(node.elts[index + 1])
                        == "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json",
                        "wrong B36 baseline manifest",
                    )
                    del node.elts[index : index + 2]
        require(replacements == 1, "wrong B36 source-authority baseline")
        expected.body.append(
            ast.parse(
                'assert proof["SOURCE_ADMISSION_STATE"] in '
                '{"ADMISSION_STAGED", "BOOTSTRAP_MATERIALIZED"}'
            ).body[0]
        )
    require(
        ast.dump(right, include_attributes=False) == ast.dump(expected, include_attributes=False),
        "source unit exceeds exact reviewed lifecycle evolution",
    )
    return {
        "symbol": symbol,
        "evolution": "EXACT_ONE_SOURCE_UNIT",
        "baseline_sha256": hashlib.sha256(baseline).hexdigest(),
        "current_sha256": hashlib.sha256(current).hexdigest(),
    }


def verify_evolved_tests(repo: Path = ROOT) -> dict[str, Any]:
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    source = compatibility.verify_source_compatibility(repo, head)
    intro = str(source["policy_introduction_sha"])
    result: dict[str, Any] = {}
    for name, (symbol, baseline_oid) in EVOLVED_TESTS.items():
        require(
            git_tree_entry(repo, compatibility.ENTRY, name)
            == {"git_blob_oid": baseline_oid, "mode": "100644"},
            "wrong C2 test baseline",
        )
        introduced = git_tree_entry(repo, intro, name)
        require(introduced["mode"] == "100644", "evolved test mode drift")
        require(
            git_tree_entry(repo, "HEAD", name) == introduced,
            "evolved test changed after governance introduction",
        )
        raw = regular_bytes(repo, name)
        require(blob_oid(raw) == introduced["git_blob_oid"], "evolved test working bytes drift")
        unit = validate_test_source_unit(git(repo, "cat-file", "blob", baseline_oid), raw, symbol)
        result[name] = unit | {
            "baseline_git_blob_oid": baseline_oid,
            "frozen_git_blob_oid": introduced["git_blob_oid"],
            "mode": introduced["mode"],
            "frozen_at_commit": intro,
        }
    return result


def validate_historical_semantic_summary(path: Path) -> dict[str, Any]:
    value = planner.read_json(path)
    manifest_path = ROOT / "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json"
    raw = manifest_path.read_bytes()
    require(
        hashlib.sha256(raw).hexdigest()
        == "d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1",
        "historical semantic manifest identity drift",
    )
    manifest = planner.read_json(manifest_path)
    expected = planner.sealed(
        {
            "schema_version": "w04-c09-gate-summary-v1",
            "gate_version": "w04-c09-investigation-gate-v1",
            "implementation_sha": planner.HISTORICAL_ANCHOR,
            "manifest_sha256": hashlib.sha256(raw).hexdigest(),
            "manifest_content_sha256": planner.digest(manifest),
            "total_families": 9,
            "total_selectors": 67,
            "total_tests": 81,
            "families": [
                {
                    "id": row["id"],
                    "status": "PASS",
                    "selectors": len(row["targets"]),
                    "tests": row["expected_cases"],
                }
                for row in manifest["families"]
            ],
            "overall": "PASS",
        },
        "summary_sha256",
    )
    require(value == expected, "historical W04 semantic summary drift or incomplete evidence")
    return value


def verify_protected_material(repo: Path = ROOT) -> None:
    """Keep closed runtime, historical evidence and non-admitted controls intact."""
    original = tree_entries(repo, PROTECTED_ROOTS)
    evolved = verify_evolved_tests(repo) if set(original) & set(EVOLVED_TESTS) else {}
    for name, expected in original.items():
        if name in evolved:
            continue
        if name not in MUTABLE_CI:
            current = git_tree_entry(repo, "HEAD", name)
            require(
                current["git_blob_oid"] == expected["git_blob_oid"],
                "protected material committed content drift: " + name,
            )
            require(current["mode"] == expected["mode"], "protected material mode drift: " + name)
            require(
                blob_oid(regular_bytes(repo, name)) == expected["git_blob_oid"],
                "protected material drift: " + name,
            )
    # New tests and upstream packages need later checkpoint authority; additions inside
    # a closed runtime package or historical evidence plane are never admitted here.
    closed = sorted(
        {"/".join(name.split("/")[:3]) for name in original if name.startswith("src/flowlens/")}
    )
    tracked = {
        name.decode()
        for name in git(
            repo,
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            "src",
            "docs/w03",
            "docs/w04",
        ).split(b"\0")
        if name
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
    source = compatibility.verify_source_compatibility(repo, head)
    evolved = verify_evolved_tests(repo)
    verify_protected_material(repo)
    verify_docs(repo)
    planner.validate_plan(
        plan, planner.read_json(planner.WEIGHTS), planner.read_json(planner.BASELINE), head, repo
    )
    require(
        planner.collect_nodes(planner.MARKER, repo) == plan["current_nodeids"],
        "active plan is not exact current collection",
    )
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
            "POST_W04_SOURCE_COMPATIBILITY": "PASS",
            "SOURCE_ADMISSION_POLICY": "PASS",
            "SOURCE_ADMISSION_STATE": source["SOURCE_ADMISSION_STATE"],
            "PRODUCT_SOURCE_PRESENT": source["PRODUCT_SOURCE_PRESENT"],
            "B36_SUCCESSOR_EVOLUTION": "PASS",
            "R46_HELPER_SUCCESSOR_EVOLUTION": "PASS",
            "W04_VERIFIER_HISTORICAL_IDENTITY": "PASS",
            "PROTECTED_MATERIAL": "PASS",
            "PHASE_PROJECTION": "PASS",
            "source_compatibility": source,
            "evolved_test_files": evolved,
            "HISTORICAL_NO_LOSS": "PASS",
            "EXACT_CURRENT_UNION": "PASS",
            "EXACT_CURRENT_ONCE": "PASS",
            "surface_baseline": "PASS",
            "COMMITTED_GIT_SURFACE_INVENTORY": "PASS",
            "WORKING_TREE_SURFACE_INVENTORY": "PASS",
            "protected_material": "PASS",
            "phase_projection": "PASS",
            "overall": "PASS",
            "current_plan": planner.plan_summary(plan),
        },
        "proof_sha256",
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
        collection.get("nodes") == 2997
        and collection.get("files") == 63
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
    parser.add_argument("--historical-semantic-summary", type=Path, required=True)
    args = parser.parse_args()
    try:
        # No external-provider/database credentials are read or needed.
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        result = verify_current(planner.read_json(args.plan), args.expected_head)
        historical = validate_historical_log(args.historical_log)
        semantic = validate_historical_semantic_summary(args.historical_semantic_summary)
        result = planner.sealed(
            {key: value for key, value in result.items() if key != "proof_sha256"}
            | {
                "historical_w04_replay": historical,
                "historical_w04_semantic_replay": semantic,
                "HISTORICAL_W04_GOVERNANCE": "PASS",
                "HISTORICAL_W04_SEMANTIC_REPLAY": "PASS",
                "HISTORICAL_W04_FAMILIES": 9,
                "HISTORICAL_W04_SELECTORS": 67,
                "HISTORICAL_W04_CASES": 81,
            },
            "proof_sha256",
        )
        planner.write_json(planner.outside_repository(args.output_json), result)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"W05_SUCCESSOR_GOVERNANCE_FAIL_CLOSED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
