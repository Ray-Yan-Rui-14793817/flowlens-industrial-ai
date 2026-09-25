"""Fail-closed exact-SHA proof for a verified publication-only PR delta."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from classify_change import classify_event, is_publication_path

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
CONFLICT = re.compile(r"^(?:<{7}(?:\s|$)|={7}$|>{7}(?:\s|$))", re.MULTILINE)


def balanced_fences(content: str) -> bool:
    opened: tuple[str, int] | None = None
    for line in content.splitlines():
        match = FENCE.match(line)
        if match is None:
            continue
        marker, trailing = match.groups()
        if opened is None:
            opened = (marker[0], len(marker))
        elif marker[0] == opened[0] and len(marker) >= opened[1] and not trailing.strip():
            opened = None
    return opened is None


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True).stdout


def verify_publication(
    event: dict[str, object], event_name: str, expected_head: str, repo: Path
) -> dict[str, object]:
    classified = classify_event(event, event_name, expected_head, repo)
    if classified["class"] != "P":
        raise ValueError("verified event delta is not publication-only")
    base = classified["base_sha"]
    head = classified["head_sha"]
    paths = classified["changed_paths"]
    if not isinstance(base, str) or not isinstance(head, str) or not isinstance(paths, list):
        raise ValueError("missing verified source-head boundary")
    if not paths or not all(isinstance(path, str) and is_publication_path(path) for path in paths):
        raise ValueError("changed path is outside the publication allowlist")
    git(repo, "diff", "--check", base, head, "--")
    for path in paths:
        tree_entry = git(repo, "ls-tree", "-z", head, "--", path)
        if not tree_entry:
            continue  # A deleted publication document has no head content to scan.
        entries = tree_entry.rstrip(b"\x00").split(b"\x00")
        if len(entries) != 1 or not entries[0].endswith(b"\t" + path.encode("utf-8")):
            raise ValueError(f"ambiguous tree entry: {path}")
        mode = entries[0].split(b" ", 1)[0]
        if mode not in {b"100644", b"100755"}:
            raise ValueError(f"non-regular publication file: {path}")
        content = git(repo, "show", f"{head}:{path}").decode("utf-8", errors="strict")
        if CONFLICT.search(content):
            raise ValueError(f"merge-conflict marker: {path}")
        if path.endswith(".md") and not balanced_fences(content):
            raise ValueError(f"unbalanced Markdown fence: {path}")
    return classified


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-path", type=Path, required=True)
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        event = json.loads(args.event_path.read_text(encoding="utf-8"))
        if not isinstance(event, dict):
            raise ValueError("event is not an object")
        classified = verify_publication(event, args.event_name, args.expected_head, args.repo)
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Publication proof failed: {error}")
        return 1
    print(f"Publication proof passed: {classified['head_sha']} from {classified['base_sha']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
