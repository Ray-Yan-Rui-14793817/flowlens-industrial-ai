"""R3-A1 exact epoch, source-unit and truthful native-classification controls."""

from __future__ import annotations

import ast
import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/ci"))
import plan_non_integration_shards as planner  # noqa: E402
import verify_w05_post_w04_source_compatibility as source  # noqa: E402
import verify_w05_successor_governance as successor  # noqa: E402

import test_investigation_replay as replay  # noqa: E402

COPIED = (
    source.POLICY,
    "scripts/ci/verify_w05_post_w04_source_compatibility.py",
    "scripts/ci/verify_w05_successor_governance.py",
    *successor.EVOLVED_TESTS,
)


def git(repo: Path, *args: str, raw: bytes | None = None) -> bytes:
    environment = os.environ.copy()
    for key in (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
    ):
        environment.pop(key, None)
    return subprocess.run(
        [
            "git",
            "-c",
            "core.autocrlf=false",
            "-c",
            "core.filemode=false",
            "-c",
            "user.name=FlowLens inert R3 fixture",
            "-c",
            "user.email=fixture@flowlens.invalid",
            *args,
        ],
        cwd=repo,
        env=environment,
        input=raw,
        capture_output=True,
        check=True,
    ).stdout


def commit(repo: Path, name: str, raw: bytes = b"# inert source ownership fixture\n") -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    git(repo, "add", "--", name)
    git(repo, "commit", "-qm", "test: inert source epoch control")


def copied(repo: Path) -> None:
    for name in COPIED:
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / name).read_bytes())
    git(repo, "add", "--", *COPIED)


def product(
    repo: Path,
    names: tuple[str, ...] = source.ADMITTED,
    subject: str = "test: inert first materialization",
) -> None:
    for name in names:
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"# inert materialization fixture, no product behavior\n")
        git(repo, "add", "--", name)
    git(repo, "commit", "-qm", subject)


def proof(repo: Path) -> dict[str, Any]:
    return source.verify_source_compatibility(repo, git(repo, "rev-parse", "HEAD").decode().strip())


@pytest.fixture(scope="module")
def admission_base(tmp_path_factory: pytest.TempPathFactory) -> Path:
    directory = tmp_path_factory.mktemp("r3-source-epoch-foundation")
    repo = directory / "repo"
    git(directory, "clone", "--shared", "--no-checkout", str(ROOT), str(repo))
    git(repo, "checkout", "--detach", source.ENTRY)
    copied(repo)
    git(repo, "commit", "-qm", "test: inert prior policy epoch")
    return repo


@pytest.fixture
def repo(tmp_path: Path, admission_base: Path) -> Path:
    result = tmp_path / "repo"
    git(tmp_path, "clone", "--shared", "--no-checkout", str(admission_base), str(result))
    git(result, "checkout", "--detach", git(admission_base, "rev-parse", "HEAD").decode().strip())
    return result


def test_exact_staged_policy_and_two_bounded_source_units(repo: Path) -> None:
    value = proof(repo)
    assert value["overall"] == "PASS" and value["SOURCE_ADMISSION_STATE"] == "ADMISSION_STAGED"
    assert value["PRODUCT_SOURCE_PRESENT"] == "NO" and not (repo / "src/flowlens/product").exists()
    evolved = successor.verify_evolved_tests(repo)
    assert set(evolved) == set(successor.EVOLVED_TESTS)
    assert all(
        row["mode"] == "100644" and row["evolution"] == "EXACT_ONE_SOURCE_UNIT"
        for row in evolved.values()
    )


def test_one_materialization_then_docs_descendant_freezes_exact_blobs(repo: Path) -> None:
    intro = git(repo, "rev-parse", "HEAD").decode().strip()
    product(repo)
    value = proof(repo)
    assert value["SOURCE_ADMISSION_STATE"] == "BOOTSTRAP_MATERIALIZED"
    assert value["policy_introduction_sha"] == intro
    frozen = value["admitted_source_entries"]
    commit(repo, "docs/inert-closeout.txt", b"inert later documentation\n")
    assert proof(repo)["admitted_source_entries"] == frozen
    assert proof(repo)["materialization_sha"] == value["materialization_sha"]


@pytest.mark.parametrize("damage", ["policy_and_source", "source_in_parent", "wrong_ancestry"])
def test_policy_introduction_cannot_self_authorize_or_change_ancestry(
    repo: Path, damage: str
) -> None:
    git(
        repo,
        "checkout",
        "--detach",
        planner.HISTORICAL_ANCHOR if damage == "wrong_ancestry" else source.ENTRY,
    )
    if damage == "source_in_parent":
        product(repo)
    copied(repo)
    if damage == "policy_and_source":
        product(repo)
    else:
        git(repo, "commit", "-qm", "test: invalid authority epoch")
    with pytest.raises((planner.ProofError, subprocess.CalledProcessError)):
        proof(repo)


@pytest.mark.parametrize("count", [1, 2])
def test_partial_materialization_is_rejected(repo: Path, count: int) -> None:
    product(repo, source.ADMITTED[:count])
    with pytest.raises(planner.ProofError):
        proof(repo)


@pytest.mark.parametrize(
    "name",
    [
        "src/flowlens/product/fourth.py",
        "src/flowlens/investigation/extra.py",
        "src/flowlens/decision/extra.py",
        "src/flowlens/api/extra.py",
        "src/flowlens/unauthorized/extra.py",
        "src/flowlens/productivity/extra.py",
    ],
)
def test_fourth_closed_or_unadmitted_source_is_rejected(repo: Path, name: str) -> None:
    product(repo)
    commit(repo, name)
    with pytest.raises(planner.ProofError):
        proof(repo)


@pytest.mark.parametrize("damage", ["whitespace", "broadened", "working"])
def test_policy_cannot_mutate_during_or_after_materialization(repo: Path, damage: str) -> None:
    path = repo / source.POLICY
    value = json.loads(path.read_bytes())
    if damage == "broadened":
        value["admitted_paths"].append({"path": "src/flowlens/product/fourth.py", "mode": "100644"})
        value = planner.sealed(
            {k: v for k, v in value.items() if k != "policy_sha256"}, "policy_sha256"
        )
        path.write_bytes((json.dumps(value) + "\n").encode())
    else:
        path.write_bytes(path.read_bytes() + b" ")
    if damage != "working":
        git(repo, "add", "--", source.POLICY)
        product(repo)
    with pytest.raises(planner.ProofError):
        proof(repo)


@pytest.mark.parametrize(
    "mode,kind", [("100755", "blob"), ("120000", "blob"), ("160000", "commit")]
)
def test_committed_wrong_mode_symlink_and_gitlink_are_rejected(
    repo: Path, mode: str, kind: str
) -> None:
    for name in source.ADMITTED:
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"# inert regular fixture\n")
        git(repo, "add", "--", name)
    target = source.ADMITTED[1]
    oid = (
        git(repo, "rev-parse", "HEAD").decode().strip()
        if kind == "commit"
        else git(repo, "hash-object", "-w", "--stdin", raw=b"nonexistent-inert-target")
        .decode()
        .strip()
    )
    git(repo, "update-index", "--add", "--cacheinfo", mode, oid, target)
    git(repo, "commit", "-qm", "test: nonregular or wrong mode source entry")
    assert git(repo, "ls-tree", "-z", "HEAD", "--", target).split(b"\t")[0].decode().split() == [
        mode,
        kind,
        oid,
    ]
    with pytest.raises(planner.ProofError):
        proof(repo)


def test_directory_at_required_regular_source_path_is_rejected(repo: Path) -> None:
    product(repo, (source.ADMITTED[0], source.ADMITTED[2], source.ADMITTED[1] + "/leaf.py"))
    assert git(repo, "ls-tree", "-z", "HEAD", "--", source.ADMITTED[1]).startswith(b"040000 tree ")
    with pytest.raises(planner.ProofError):
        proof(repo)


@pytest.mark.parametrize("stage", ["staged", "materialized"])
def test_uncommitted_source_is_rejected(repo: Path, stage: str) -> None:
    if stage == "materialized":
        product(repo)
    path = repo / source.ADMITTED[1]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"# forbidden uncommitted source drift\n")
    with pytest.raises(planner.ProofError):
        proof(repo)


@pytest.mark.parametrize(
    "name",
    [
        "src/flowlens/decision/contracts.py",
        "src/flowlens/investigation/contracts.py",
        *source.FROZEN_W04,
    ],
)
def test_closed_source_and_frozen_w04_objects_never_evolve(repo: Path, name: str) -> None:
    path = repo / name
    commit(repo, name, path.read_bytes() + b"\n# forbidden drift\n")
    with pytest.raises(planner.ProofError):
        proof(repo)


def test_materialized_source_cannot_mutate_even_if_later_reverted(repo: Path) -> None:
    product(repo)
    path = repo / source.ADMITTED[1]
    raw = path.read_bytes()
    commit(repo, source.ADMITTED[1], raw + b"# invalid intermediate mutation\n")
    commit(repo, source.ADMITTED[1], raw)
    with pytest.raises(planner.ProofError):
        proof(repo)


def test_two_independent_first_materializations_are_not_unique(repo: Path) -> None:
    intro = git(repo, "rev-parse", "HEAD").decode().strip()
    git(repo, "checkout", "-b", "fixture-left")
    product(repo)
    git(repo, "checkout", "-b", "fixture-right", intro)
    product(repo, subject="test: independent competing materialization")
    git(repo, "merge", "--no-ff", "-m", "test: competing materializations", "fixture-left")
    with pytest.raises(planner.ProofError):
        proof(repo)


def test_staged_epoch_is_the_policy_introduction_head(repo: Path) -> None:
    commit(repo, "docs/inert-before-materialization.txt")
    with pytest.raises(planner.ProofError):
        proof(repo)


@pytest.mark.parametrize("name", list(successor.EVOLVED_TESTS))
@pytest.mark.parametrize(
    "damage", ["unrelated_bytes", "extra_unit", "rename", "signature", "decorator", "extra_body"]
)
def test_only_the_exact_two_reviewed_source_units_may_evolve(name: str, damage: str) -> None:
    symbol, oid = successor.EVOLVED_TESTS[name]
    baseline = git(ROOT, "cat-file", "blob", oid)
    current = (ROOT / name).read_text(encoding="utf-8")
    fn = next(
        n for n in ast.parse(current).body if isinstance(n, ast.FunctionDef) and n.name == symbol
    )
    lines = current.splitlines(keepends=True)
    if damage == "unrelated_bytes":
        current = "# unauthorized outside-unit bytes\n" + current
    elif damage == "extra_unit":
        current += "\nUNAUTHORIZED_SECOND_UNIT = True\n"
    elif damage == "rename":
        current = current.replace("def " + symbol + "(", "def renamed_" + symbol + "(")
    elif damage == "signature":
        lines[fn.lineno - 1] = lines[fn.lineno - 1].replace("(", "(unexpected: int, ", 1)
        current = "".join(lines)
    elif damage == "decorator":
        lines.insert(fn.lineno - 1, "@staticmethod\n")
        current = "".join(lines)
    else:
        lines.insert(fn.end_lineno or 0, "    assert True\n")
        current = "".join(lines)
    with pytest.raises(planner.ProofError):
        successor.validate_test_source_unit(baseline, current.encode(), symbol)


@pytest.mark.parametrize("name", list(successor.EVOLVED_TESTS))
def test_complete_evolved_file_refreezes_at_policy_commit(repo: Path, name: str) -> None:
    commit(repo, name, (repo / name).read_bytes() + b"\n# unauthorized later file drift\n")
    with pytest.raises(planner.ProofError):
        successor.verify_evolved_tests(repo)


@pytest.mark.parametrize("classification", ["I", "C", "UNKNOWN"])
def test_a1_accepts_only_reviewed_full_route_classes(classification: str) -> None:
    value = replay._native_metadata_fixture("a" * 40)
    assert value["evidence_kind"] == "FIXTURE"
    value["classifier"]["class"] = classification
    replay._check_native_metadata(value, "a" * 40)


@pytest.mark.parametrize(
    "damage",
    [
        "P",
        "F",
        "arbitrary",
        "missing_class",
        "gate",
        "classifier_head",
        "failed_run",
        "missing_job",
        "failed_job",
        "publication",
        "w03",
        "w04",
    ],
)
def test_a1_unknown_does_not_weaken_any_other_native_check(damage: str) -> None:
    value = replay._native_metadata_fixture("a" * 40)
    value["classifier"]["class"] = "UNKNOWN"
    if damage in {"P", "F", "arbitrary"}:
        value["classifier"]["class"] = damage
    elif damage == "missing_class":
        del value["classifier"]["class"]
    elif damage == "gate":
        value["classifier"]["gate"] = "PUBLICATION_EXACT_SHA"
    elif damage == "classifier_head":
        value["classifier"]["head_sha"] = "b" * 40
    elif damage == "failed_run":
        value["run"]["conclusion"] = "failure"
    elif damage == "missing_job":
        value["jobs"].pop()
    elif damage == "failed_job":
        value["jobs"][0]["conclusion"] = "failure"
    elif damage == "publication":
        next(row for row in value["jobs"] if row["name"] == "Publication proof")["conclusion"] = (
            "success"
        )
    elif damage == "w03":
        value["w03"]["families"][0]["tests"] = 84
    else:
        value["w04"]["total_tests"] = 80
    with pytest.raises((AssertionError, KeyError)):
        replay._check_native_metadata(value, "a" * 40)


@pytest.mark.parametrize(
    "damage", ["none", "head", "counts", "family", "manifest", "extra", "seal"]
)
def test_historical_semantic_summary_is_exact_and_sealed(tmp_path: Path, damage: str) -> None:
    value = copy.deepcopy(replay._native_metadata_fixture(planner.HISTORICAL_ANCHOR)["w04"])
    if damage == "head":
        value["implementation_sha"] = "b" * 40
    elif damage == "counts":
        value["total_tests"] = 80
    elif damage == "family":
        value["families"][0]["status"] = "FAIL"
    elif damage == "manifest":
        value["manifest_sha256"] = "0" * 64
    elif damage == "extra":
        value["unreviewed"] = True
    if damage != "seal":
        value = planner.sealed(
            {k: v for k, v in value.items() if k != "summary_sha256"}, "summary_sha256"
        )
    else:
        value["summary_sha256"] = "0" * 64
    path = tmp_path / "historical-semantic-summary.json"
    path.write_bytes((json.dumps(value) + "\n").encode())
    if damage == "none":
        assert successor.validate_historical_semantic_summary(path) == value
    else:
        with pytest.raises(planner.ProofError):
            successor.validate_historical_semantic_summary(path)


def test_workflow_only_strengthens_existing_w05_historical_job() -> None:
    before = git(ROOT, "show", source.ENTRY + ":.github/workflows/ci.yml").decode()
    after = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    marker, ending = "  w05-successor-governance:\n", "  verification-gate:\n"
    left_before, rest_before = before.split(marker, 1)
    left_after, rest_after = after.split(marker, 1)
    body_before, right_before = rest_before.split(ending, 1)
    body_after, right_after = rest_after.split(ending, 1)
    assert left_before == left_after and right_before == right_after and body_before != body_after
    assert "flowlens_w05_historical_w04_test" in body_after
    assert "services:" in body_after and "pgvector/pgvector:0.8.6-pg17-bookworm" in body_after
    assert "Replay historical W04 governance at exact anchor" in body_after
    assert planner.HISTORICAL_ANCHOR in body_after
    assert "-B -m alembic upgrade head" in body_after
    assert "verify_w04_investigation_gate_contract.py" in body_after
    assert "run_w04_investigation_gate.py" in body_after
    assert (
        '--historical-semantic-summary '
        '"$RUNNER_TEMP/w05-governance/historical-w04-semantic-summary.json"'
        in body_after
    )
    assert "name: w05-successor-governance-${{" in body_after
