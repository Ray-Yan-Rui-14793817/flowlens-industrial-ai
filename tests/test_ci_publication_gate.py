"""Publication proof rejects content or boundary defects before light CI passes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/ci"))

from verify_publication import balanced_fences, verify_publication  # noqa: E402


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def repository(tmp_path: Path) -> tuple[Path, str]:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "ci@example.test")
    git(tmp_path, "config", "user.name", "CI Test")
    (tmp_path / "README.md").write_text("fixture\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-q", "-m", "baseline")
    return tmp_path, git(tmp_path, "rev-parse", "HEAD")


def commit(repo: Path, changes: dict[str, str]) -> str:
    for path, content in changes.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "publication fixture")
    return git(repo, "rev-parse", "HEAD")


def event(base: str, head: str) -> dict[str, Any]:
    return {
        "action": "synchronize",
        "before": base,
        "after": head,
        "pull_request": {"head": {"sha": head}},
    }


def test_report_and_state_pass_exact_publication_proof(tmp_path: Path) -> None:
    repo, base = repository(tmp_path)
    head = commit(
        repo,
        {
            "docs/w03/reports/report.md": "# Round\n\n```text\nPASS\n```\n",
            "docs/CURRENT_STATE.md": "# Current\n",
        },
    )
    result = verify_publication(event(base, head), "pull_request", head, repo)
    assert result["class"] == "P"
    assert result["head_sha"] == head


@pytest.mark.parametrize(
    "extra_path",
    [
        "src/flowlens/decision/signals.py",
        "tests/test_x.py",
        ".github/workflows/ci.yml",
        "docs/sprints/W03_ai_decision_loop.md",
        "pyproject.toml",
        "unknown/file.md",
    ],
)
def test_mixed_delta_rejects_publication(tmp_path: Path, extra_path: str) -> None:
    repo, base = repository(tmp_path)
    head = commit(
        repo,
        {"docs/w03/reports/report.md": "# Report\n", extra_path: "changed\n"},
    )
    with pytest.raises(ValueError, match="not publication-only"):
        verify_publication(event(base, head), "pull_request", head, repo)


def test_diff_whitespace_error_rejects_publication(tmp_path: Path) -> None:
    repo, base = repository(tmp_path)
    head = commit(repo, {"docs/w03/reports/report.md": "# Report   \n"})
    with pytest.raises(subprocess.CalledProcessError):
        verify_publication(event(base, head), "pull_request", head, repo)


def test_unbalanced_markdown_fence_rejects_publication(tmp_path: Path) -> None:
    repo, base = repository(tmp_path)
    head = commit(repo, {"docs/w03/reports/report.md": "# Report\n\n```text\nopen\n"})
    with pytest.raises(ValueError, match="unbalanced Markdown fence"):
        verify_publication(event(base, head), "pull_request", head, repo)


@pytest.mark.parametrize("marker", ["<<<<<<< HEAD", "=======", ">>>>>>> branch"])
def test_merge_conflict_marker_rejects_publication(tmp_path: Path, marker: str) -> None:
    repo, base = repository(tmp_path)
    head = commit(repo, {"docs/w03/reports/report.md": f"# Report\n{marker}\n"})
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        verify_publication(event(base, head), "pull_request", head, repo)


def test_invalid_boundary_rejects_publication(tmp_path: Path) -> None:
    repo, base = repository(tmp_path)
    head = commit(repo, {"docs/w03/reports/report.md": "# Report\n"})
    with pytest.raises(ValueError, match="not publication-only"):
        verify_publication(event("0" * 40, head), "pull_request", head, repo)
    with pytest.raises(ValueError, match="not publication-only"):
        verify_publication(event(base, head), "push", head, repo)


def test_fence_parser_requires_matching_marker_and_length() -> None:
    assert balanced_fences("~~~~md\n``` literal\n~~~~\n")
    assert balanced_fences("````text\n``` literal\n````\n")
    assert not balanced_fences("````text\n```\n")
    assert not balanced_fences("~~~text\n```\n")
