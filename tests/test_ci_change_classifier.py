"""DEVCTRL-01 classifier boundary, history replay, and routing proofs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/ci"))

from classify_change import (  # noqa: E402
    FULL,
    PUBLICATION,
    changed_paths,
    classify_event,
    classify_path,
    classify_paths,
    is_publication_path,
)

ROOT = Path(__file__).resolve().parents[1]


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def commit(repo: Path, path: str, content: str) -> str:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", "--", path)
    git(repo, "commit", "-q", "-m", "fixture")
    return git(repo, "rev-parse", "HEAD")


def repository(tmp_path: Path) -> tuple[Path, str]:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "ci@example.test")
    git(tmp_path, "config", "user.name", "CI Test")
    return tmp_path, commit(tmp_path, "README.md", "fixture\n")


def event(before: str, after: str, action: str = "synchronize") -> dict[str, Any]:
    return {
        "action": action,
        "before": before,
        "after": after,
        "pull_request": {"head": {"sha": after}},
    }


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("docs/w03/reports/evidence.md", "P"),
        ("docs/CURRENT_STATE.md", "P"),
        ("docs/w03/checkpoints/c02/contract.md", "C"),
        ("docs/w03/AI_LOOP_CONSTITUTION.md", "C"),
        ("docs/sprints/W03_ai_decision_loop.md", "C"),
        ("docs/context/MATERIAL_REGISTRY.md", "C"),
        (".github/workflows/ci.yml", "C"),
        ("scripts/ci/classify_change.py", "C"),
        ("tests/test_ci_change_classifier.py", "C"),
        ("tests/fixtures/w03_ci_history.json", "C"),
        ("tests/test_decision_context.py", "I"),
        ("src/flowlens/decision/signals.py", "I"),
        ("migrations/versions/new.py", "F"),
        ("apps/api/Dockerfile", "F"),
        ("docker-compose.yml", "F"),
        ("pyproject.toml", "F"),
        ("new/unknown.md", "UNKNOWN"),
        ("docs/w03/reports/../AI_LOOP_CONSTITUTION.md", "UNKNOWN"),
    ],
)
def test_path_classes(path: str, expected: str) -> None:
    assert classify_path(path) == expected


@pytest.mark.parametrize(
    ("paths", "expected"),
    [
        (["docs/w03/reports/a.md", "docs/CURRENT_STATE.md"], "P"),
        (["docs/w03/reports/a.md", ".github/workflows/ci.yml"], "C"),
        (["docs/CURRENT_STATE.md", "docs/sprints/W03_ai_decision_loop.md"], "C"),
        (["docs/w03/reports/a.md", "src/flowlens/decision/signals.py"], "I"),
        (["docs/w03/reports/a.md", "tests/test_x.py"], "I"),
        (["docs/w03/reports/a.md", "pyproject.toml"], "F"),
        (["src/x.py", "migrations/versions/x.py"], "F"),
        (["docs/CURRENT_STATE.md", "new/unknown.md"], "UNKNOWN"),
        (
            ["docs/w04/checkpoints/c02/W04_C02_FINAL_CLOSEOUT_REPORT.md", "docs/CURRENT_STATE.md"],
            "P",
        ),
        (
            [
                "docs/w04/checkpoints/c02/W04_C02_FINAL_CLOSEOUT_REPORT.md",
                "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json",
            ],
            "C",
        ),
        (
            [
                "docs/w04/checkpoints/c02/W04_C02_FINAL_CLOSEOUT_REPORT.md",
                "src/flowlens/investigation/contracts.py",
            ],
            "I",
        ),
        (["docs/w04/W04_FINAL_CLOSEOUT_REPORT.md", "uv.lock"], "F"),
        (["docs/w04/W04_FINAL_CLOSEOUT_REPORT.md", "new/unknown.md"], "UNKNOWN"),
        (["docs/w04/W04_FINAL_CLOSEOUT_REPORT.md"] * 2, "UNKNOWN"),
        ([], "UNKNOWN"),
    ],
)
def test_mixed_classes_fail_closed(paths: list[str], expected: str) -> None:
    assert classify_paths(paths) == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("docs/w04/checkpoints/c02/W04_C02_R_DEVELOPMENT_ROUND_REPORT.md", "P"),
        ("docs/w04/checkpoints/c02/W04_C02_GPT_INDEPENDENT_REVIEW_R1.md", "P"),
        ("docs/w04/checkpoints/c02/W04_C02_GPT_INDEPENDENT_DEEP_REVIEW_R12.md", "P"),
        ("docs/w04/checkpoints/c02/W04_C02_FINAL_CLOSEOUT_REPORT.md", "P"),
        ("docs/w04/devctrl/W04_DEVCTRL_01_R_DEVELOPMENT_ROUND_REPORT.md", "P"),
        ("docs/w04/W04_GPT_INDEPENDENT_REVIEW_R10.md", "P"),
        ("docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json", "C"),
        ("docs/w04/checkpoints/c02/W04_C02_HUMAN_AUTHORIZATION.md", "C"),
        ("docs/w04/checkpoints/c02/W04_C02_CONTEXT_LOCK.md", "C"),
        ("docs/w04/checkpoints/c02/W04_C02_CODEX_TASK.md", "C"),
        ("docs/w04/checkpoints/c02/W04_C02_GPT_DESIGN_REVIEW_R1.md", "C"),
        ("docs/w04/checkpoints/c02/report.md", "C"),
        ("docs/w04/W04_SOURCE_EVOLUTION_MANIFEST_FINAL_CLOSEOUT_REPORT.json", "C"),
        ("docs/w04/W04_FINAL_CLOSEOUT_REPORT.md.bak", "C"),
        ("docs/w04/W04_FINAL_CLOSEOUT_REPORT.MD", "C"),
        ("docs/w04/W04_GPT_INDEPENDENT_REVIEW_R.md", "C"),
        ("docs/w04/W04_GPT_INDEPENDENT_REVIEW_Rone.md", "C"),
        ("docs/w04/W04_GPT_INDEPENDENT_REVIEW_R١.md", "C"),
        ("docs/w04/W04_GPT_INDEPENDENT_REVIEW_R1_extra.md", "C"),
        ("docs/w04/W04_GPT_INDEPENDENT_DEEP_REVIEW_R1.txt", "C"),
        ("docs/w04/W04_r_DEVELOPMENT_ROUND_REPORT.md", "C"),
        ("docs/w04/nested/pyproject.toml", "C"),
        ("docs/w04/nested/uv.lock", "C"),
        ("docs/w04/nested/Dockerfile", "C"),
        ("docs/w04/nested/Dockerfile_FINAL_CLOSEOUT_REPORT.md", "P"),
        ("src/flowlens/investigation/contracts.py", "I"),
        ("src/flowlens/investigation/nested/module.py", "I"),
        ("src/flowlens/investigation/pyproject.toml", "I"),
        ("src/flowlens/investigation/Dockerfile", "I"),
        ("pyproject.toml", "F"),
        ("uv.lock", "F"),
        ("docker-compose.yml", "F"),
        ("migrations/versions/new.py", "F"),
        ("other/W04_FINAL_CLOSEOUT_REPORT.md", "UNKNOWN"),
        ("docs/w040/W04_FINAL_CLOSEOUT_REPORT.md", "UNKNOWN"),
    ],
)
def test_w04_path_grammar_and_control_boundary(path: str, expected: str) -> None:
    assert classify_path(path) == expected
    assert is_publication_path(path) is (expected == "P")


@pytest.mark.parametrize(
    "path",
    [
        "",
        "/docs/w04/W04_FINAL_CLOSEOUT_REPORT.md",
        "docs\\w04\\W04_FINAL_CLOSEOUT_REPORT.md",
        "docs/w04/../w04/W04_FINAL_CLOSEOUT_REPORT.md",
        "docs/w04/./W04_FINAL_CLOSEOUT_REPORT.md",
        "docs/w04//W04_FINAL_CLOSEOUT_REPORT.md",
        "docs/w04/W04_FINAL_CLOSEOUT_REPORT.md/",
        "docs/w04/\x00W04_FINAL_CLOSEOUT_REPORT.md",
    ],
)
def test_w04_malformed_paths_rejected_by_shared_helper(path: str) -> None:
    assert classify_path(path) == "UNKNOWN"
    assert not is_publication_path(path)


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("docs/w04/W04_R_DEVELOPMENT_ROUND_REPORT.md", "P"),
        ("docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json", "C"),
        ("src/flowlens/investigation/fixture.py", "I"),
        ("uv.lock", "F"),
        ("unknown/file.md", "UNKNOWN"),
    ],
)
def test_w04_current_git_delta_routes_each_class(tmp_path: Path, path: str, expected: str) -> None:
    repo, base = repository(tmp_path)
    head = commit(repo, path, "fixture\n")
    actual = classify_event(event(base, head), "pull_request", head, repo)
    assert actual["class"] == expected
    assert actual["gate"] == (PUBLICATION if expected == "P" else FULL)
    assert actual["base_sha"] == base and actual["head_sha"] == head
    assert actual["changed_paths"] == [path]


@pytest.mark.parametrize("boundary", ["push", "opened", "missing_before", "head_mismatch"])
def test_w04_publication_ambiguous_boundary_keeps_full(tmp_path: Path, boundary: str) -> None:
    repo, base = repository(tmp_path)
    head = commit(repo, "docs/w04/W04_FINAL_CLOSEOUT_REPORT.md", "# Closeout\n")
    payload = event(base, head)
    event_name = "pull_request"
    expected_head = head
    if boundary == "push":
        event_name = "push"
    elif boundary == "opened":
        payload["action"] = "opened"
    elif boundary == "missing_before":
        payload.pop("before")
    else:
        expected_head = base
    actual = classify_event(payload, event_name, expected_head, repo)
    assert actual["class"] == "UNKNOWN" and actual["gate"] == FULL


def test_verified_synchronize_uses_current_delta_and_deterministic_json(tmp_path: Path) -> None:
    repo, base = repository(tmp_path)
    head = commit(repo, "docs/w03/reports/round.md", "# Round\n")
    first = classify_event(event(base, head), "pull_request", head, repo)
    second = classify_event(event(base, head), "pull_request", head, repo)
    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first == {
        "class": "P",
        "gate": PUBLICATION,
        "base_sha": base,
        "head_sha": head,
        "changed_paths": ["docs/w03/reports/round.md"],
        "reason_codes": ["verified_source_head_delta"],
    }
    assert classify_event(event(base, head), "push", head, repo)["gate"] == FULL
    assert classify_event(event(base, head, "opened"), "pull_request", head, repo)["gate"] == FULL


def test_invalid_or_unproven_boundary_selects_full(tmp_path: Path) -> None:
    repo, base = repository(tmp_path)
    head = commit(repo, "docs/CURRENT_STATE.md", "# State\n")
    for invalid in (
        event("not-a-sha", head),
        event(head, head),
        event(base, base),
        {"action": "synchronize", "after": head, "pull_request": {"head": {"sha": head}}},
    ):
        assert classify_event(invalid, "pull_request", head, repo)["gate"] == FULL
    assert classify_event(event(base, head), "pull_request", base, repo)["gate"] == FULL


def test_non_ancestor_boundary_selects_full(tmp_path: Path) -> None:
    repo, base = repository(tmp_path)
    git(repo, "checkout", "-q", "-b", "other")
    unrelated = commit(repo, "docs/CURRENT_STATE.md", "other\n")
    git(repo, "checkout", "-q", "main")
    head = commit(repo, "docs/w03/reports/round.md", "head\n")
    assert base != unrelated
    assert classify_event(event(unrelated, head), "pull_request", head, repo)["gate"] == FULL


def test_accepted_w03_history_replays_from_actual_git_diffs() -> None:
    fixtures = json.loads((ROOT / "tests/fixtures/w03_ci_history.json").read_text())
    assert len(fixtures) >= 11
    for item in fixtures:
        sha = item["commit"]
        parent = git(ROOT, "rev-parse", f"{sha}^")
        paths = changed_paths(ROOT, parent, sha)
        actual = classify_paths(paths)
        assert actual == item["class"], (sha, paths)
        assert (PUBLICATION if actual == "P" else FULL) == (
            PUBLICATION if item["class"] == "P" else FULL
        )


def test_workflow_routes_all_classes_to_a_stable_fail_closed_gate() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for required in (
        "classify-change:",
        "name: Quality gate",
        "name: Docker Compose smoke",
        "name: Publication proof",
        "name: Verification gate",
        "needs: [classify-change, quality, compose-smoke, publication-proof, "
        "w03-ai-loop-gate, shadow-equivalence]",
        "if: always()",
        '--event-path "$GITHUB_EVENT_PATH"',
        'test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD"',
        "fetch-depth: 0",
        'test "$QUALITY_RESULT" = skipped',
        'test "$COMPOSE_RESULT" = skipped',
        'test "$PUBLICATION_RESULT" = success',
        'test "$PUBLICATION_RESULT" = skipped',
        'test "$QUALITY_RESULT" = success',
        'test "$COMPOSE_RESULT" = success',
    ):
        assert required in workflow
    assert 'uv run pytest -m "not integration"' in workflow
    assert "uv run pytest -m integration" in workflow


def test_shadow_workflow_requires_equivalence_and_preserves_classification() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "name: Shadow equivalence" in workflow
    assert "fail-fast: false" in workflow and "max-parallel: 7" in workflow
    assert "shard: [0, 1, 2, 3, 4, 5, 6]" in workflow
    w03 = workflow.split("  w03-ai-loop-gate:\n", 1)[1].split("  compose-smoke:\n", 1)[0]
    assert "    needs: classify-change\n" in w03
    assert 'test "$SHADOW_RESULT" = success' in workflow
    assert 'test "$SHADOW_RESULT" = skipped' in workflow
    assert (
        git(
            ROOT,
            "diff",
            "4a5ab37251c1fecff4291ae6198e03c847cf8735",
            "--",
            "scripts/ci/classify_change.py",
            "scripts/ci/verify_publication.py",
        )
        == ""
    )
