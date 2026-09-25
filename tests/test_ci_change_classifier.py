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
        ([], "UNKNOWN"),
    ],
)
def test_mixed_classes_fail_closed(paths: list[str], expected: str) -> None:
    assert classify_paths(paths) == expected


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
        "needs: [classify-change, quality, compose-smoke, publication-proof]",
        "if: always()",
        "--event-path \"$GITHUB_EVENT_PATH\"",
        "test \"$(git rev-parse HEAD)\" = \"$EXPECTED_HEAD\"",
        "fetch-depth: 0",
        "test \"$QUALITY_RESULT\" = skipped",
        "test \"$COMPOSE_RESULT\" = skipped",
        "test \"$PUBLICATION_RESULT\" = success",
        "test \"$PUBLICATION_RESULT\" = skipped",
        "test \"$QUALITY_RESULT\" = success",
        "test \"$COMPOSE_RESULT\" = success",
    ):
        assert required in workflow
    assert 'uv run pytest -m "not integration"' in workflow
    assert "uv run pytest -m integration" in workflow
