"""Classify the exact source-head delta for the W03 development proof gate.

Only a verified pull_request/synchronize before/after boundary can use the
publication path. Every other event or ambiguous boundary selects full proof.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, TypeGuard

FULL = "FULL_EXACT_SHA"
PUBLICATION = "PUBLICATION_EXACT_SHA"
SHA = re.compile(r"[0-9a-fA-F]{40}\Z")
CONTROL_TESTS = {
    "tests/test_ci_change_classifier.py",
    "tests/test_ci_publication_gate.py",
    "tests/fixtures/w03_ci_history.json",
}
FOUNDATION_NAMES = {
    "alembic.ini",
    "pyproject.toml",
    "uv.lock",
    "docker-compose.yml",
    "compose.yml",
    "compose.yaml",
}
RANK = {"P": 0, "C": 1, "I": 2, "F": 3}


def valid_sha(value: object) -> TypeGuard[str]:
    return isinstance(value, str) and bool(SHA.fullmatch(value)) and value != "0" * 40


def is_publication_path(path: str) -> bool:
    return path == "docs/CURRENT_STATE.md" or (
        path.startswith("docs/w03/reports/") and len(path) > len("docs/w03/reports/")
    )


def classify_path(path: str) -> str:
    """Return a class for one untrusted Git path, preserving uncertainty."""
    if (
        not path
        or path.startswith("/")
        or "\\" in path
        or "\x00" in path
        or any(part in {"", ".", ".."} for part in path.split("/"))
    ):
        return "UNKNOWN"
    name = PurePosixPath(path).name
    if path.startswith("migrations/") or name in FOUNDATION_NAMES or name.startswith("Dockerfile"):
        return "F"
    if is_publication_path(path):
        return "P"
    if path in CONTROL_TESTS:
        return "C"
    if (
        path.startswith(".github/workflows/")
        or path.startswith("scripts/ci/")
        or path.startswith("skills/")
        or path.startswith("docs/w03/checkpoints/")
        or path.startswith("docs/sprints/")
        or path.startswith("docs/context/")
        or (path.startswith("docs/w03/") and path.count("/") == 2 and name.endswith(".md"))
        or name in {"AGENTS.md", "LOOP.md"}
    ):
        return "C"
    if path.startswith("src/") or path.startswith("tests/"):
        return "I"
    return "UNKNOWN"


def classify_paths(paths: list[str]) -> str:
    if not paths or len(paths) != len(set(paths)):
        return "UNKNOWN"
    classes = {classify_path(path) for path in paths}
    if "UNKNOWN" in classes:
        return "UNKNOWN"
    return max(classes, key=RANK.__getitem__)


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True
    ).stdout.strip()


def changed_paths(repo: Path, base: str, head: str) -> list[str]:
    raw = subprocess.run(
        ["git", "diff", "--name-only", "--no-renames", "-z", base, head, "--"],
        cwd=repo,
        check=True,
        capture_output=True,
    ).stdout
    if not raw or not raw.endswith(b"\x00"):
        return []
    return sorted(item.decode("utf-8", errors="strict") for item in raw[:-1].split(b"\x00"))


def result(
    change_class: str,
    base_sha: str | None,
    head_sha: str | None,
    paths: list[str],
    *reasons: str,
) -> dict[str, Any]:
    return {
        "class": change_class,
        "gate": PUBLICATION if change_class == "P" else FULL,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "changed_paths": sorted(paths),
        "reason_codes": list(reasons),
    }


def classify_event(
    event: dict[str, Any], event_name: str, expected_head: str, repo: Path
) -> dict[str, Any]:
    """Use only the verified PR source-head transition, else require full proof."""
    head = expected_head.lower() if valid_sha(expected_head) else None
    try:
        if head is None or git(repo, "rev-parse", "HEAD").decode("ascii").lower() != head:
            return result("UNKNOWN", None, head, [], "checkout_mismatch")
        if event_name == "push":
            return result("UNKNOWN", None, head, [], "push_full")
        if event_name != "pull_request" or event.get("action") != "synchronize":
            return result("UNKNOWN", None, head, [], "ambiguous_event")
        before = event.get("before")
        after = event.get("after")
        pr = event.get("pull_request")
        pr_head = pr.get("head") if isinstance(pr, dict) else None
        source_head = pr_head.get("sha") if isinstance(pr_head, dict) else None
        if (
            not valid_sha(before)
            or not valid_sha(after)
            or not valid_sha(source_head)
            or before.lower() == after.lower()
            or after.lower() != head
            or source_head.lower() != head
        ):
            return result("UNKNOWN", None, head, [], "invalid_boundary")
        base = before.lower()
        if git(repo, "cat-file", "-t", base) != b"commit":
            return result("UNKNOWN", base, head, [], "invalid_base_object")
        if git(repo, "cat-file", "-t", head) != b"commit":
            return result("UNKNOWN", base, head, [], "invalid_head_object")
        git(repo, "merge-base", "--is-ancestor", base, head)
        paths = changed_paths(repo, base, head)
        change_class = classify_paths(paths)
        reason = (
            "verified_source_head_delta" if change_class != "UNKNOWN" else "unknown_or_empty_delta"
        )
        return result(change_class, base, head, paths, reason)
    except (OSError, subprocess.CalledProcessError, UnicodeError, ValueError):
        return result("UNKNOWN", None, head, [], "classification_error")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-path", type=Path, required=True)
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        event = json.loads(args.event_path.read_text(encoding="utf-8"))
        if not isinstance(event, dict):
            raise ValueError("event is not an object")
        classified = classify_event(event, args.event_name, args.expected_head, args.repo)
    except (OSError, ValueError, UnicodeError):
        head = args.expected_head.lower() if valid_sha(args.expected_head) else None
        classified = result("UNKNOWN", None, head, [], "invalid_event_payload")
    output = json.dumps(classified, sort_keys=True, separators=(",", ":"))
    print(output)
    if args.output_json:
        args.output_json.write_text(output + "\n", encoding="utf-8")
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as stream:
            stream.write(f"class={classified['class']}\n")
            stream.write(f"gate={classified['gate']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
