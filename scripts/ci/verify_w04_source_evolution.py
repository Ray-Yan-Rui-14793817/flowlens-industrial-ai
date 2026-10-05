"""Fail-closed exact-HEAD proof of checkpoint-scoped W04 source evolution."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

SCHEMA_VERSION = "w04-source-evolution-manifest-v1"
POLICY_ID = "W04-DEVCTRL-01"
W03_BASELINE_SHA = "af61bdfd5f7cf7961811c4c2dc8e554dd7eed509"
W04_SOURCE_ROOT = "src/flowlens/investigation"
MANIFEST_PATH = "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json"
C01_SOURCE_FREEZE_SHA = "084c2fea93d0e021994de015c986de9ff92bf9a3"
C01_FILES = (
    (f"{W04_SOURCE_ROOT}/__init__.py", "c23929f85dccd78bc72ef3b2b1415c6e8eaf0452"),
    (f"{W04_SOURCE_ROOT}/contracts.py", "0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e"),
    (f"{W04_SOURCE_ROOT}/enums.py", "9c818780423f32f144b18666784ebc9ea3abdccc"),
)
OID = re.compile(r"[0-9a-f]{40}\Z")
CHECKPOINT_ID = re.compile(r"W04-C(?:0[1-9]|10)\Z")
REGULAR_MODES = {"100644", "100755"}


class SourceEvolutionError(ValueError):
    """The manifest, Git history or source tree violates the frozen policy."""


@dataclass(frozen=True)
class SourceFile:
    path: str
    blob_oid: str | None


@dataclass(frozen=True)
class Checkpoint:
    checkpoint: str
    state: str
    source_freeze_sha: str | None
    files: tuple[SourceFile, ...]


@dataclass(frozen=True)
class Manifest:
    checkpoints: tuple[Checkpoint, ...]


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    kind: str
    oid: str


def _fail(message: str) -> NoReturn:
    raise SourceEvolutionError(message)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> NoReturn:
    _fail(f"invalid JSON constant: {value}")


def _object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _fail(f"invalid {label} schema")
    return dict(value)


def _oid(value: Any, label: str) -> str:
    if not isinstance(value, str) or OID.fullmatch(value) is None:
        _fail(f"invalid {label}")
    return str(value)


def _source_path(value: Any) -> str:
    if not isinstance(value, str):
        _fail("invalid source path")
    path = str(value)
    if (
        not path.startswith(W04_SOURCE_ROOT + "/")
        or "\\" in path
        or ":" in path
        or any(ord(character) < 32 or ord(character) == 127 for character in path)
        or any(part in {"", ".", ".."} for part in path.split("/"))
    ):
        _fail(f"invalid source path: {path!r}")
    return path


def _bootstrap() -> Manifest:
    return Manifest(
        (
            Checkpoint(
                "W04-C01",
                "CLOSED",
                C01_SOURCE_FREEZE_SHA,
                tuple(SourceFile(path, oid) for path, oid in C01_FILES),
            ),
        )
    )


def parse_manifest(content: bytes) -> Manifest:
    """Read only the exact schema, rejecting duplicate keys and JSON extensions."""
    try:
        value = json.loads(
            content.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_invalid_constant,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise SourceEvolutionError("invalid manifest JSON") from error
    document = _object(
        value,
        {"schema_version", "policy_id", "w03_baseline_sha", "w04_source_root", "checkpoints"},
        "manifest",
    )
    if document["schema_version"] != SCHEMA_VERSION or document["policy_id"] != POLICY_ID:
        _fail("invalid manifest schema_version or policy_id")
    if document["w03_baseline_sha"] != W03_BASELINE_SHA:
        _fail("invalid W03 baseline SHA")
    if document["w04_source_root"] != W04_SOURCE_ROOT:
        _fail("invalid W04 source root")
    values = document["checkpoints"]
    if not isinstance(values, list) or not values:
        _fail("invalid checkpoints list")
    checkpoints: list[Checkpoint] = []
    seen_paths: set[str] = set()
    previous_id = ""
    for value in values:
        item = _object(value, {"checkpoint", "state", "source_freeze_sha", "files"}, "checkpoint")
        checkpoint_id = item["checkpoint"]
        if not isinstance(checkpoint_id, str) or CHECKPOINT_ID.fullmatch(checkpoint_id) is None:
            _fail("invalid checkpoint id")
        if checkpoint_id <= previous_id:
            _fail("checkpoint ordering or uniqueness violation")
        previous_id = checkpoint_id
        state = item["state"]
        if not isinstance(state, str) or state not in {"AUTHORIZED", "CLOSED"}:
            _fail("invalid checkpoint state")
        freeze = item["source_freeze_sha"]
        if state == "AUTHORIZED":
            if freeze is not None:
                _fail("AUTHORIZED source_freeze_sha must be null")
        else:
            freeze = _oid(freeze, "source_freeze_sha")
        file_values = item["files"]
        if not isinstance(file_values, list) or not file_values:
            _fail("invalid files list")
        files: list[SourceFile] = []
        for file_value in file_values:
            source = _object(file_value, {"path", "blob_oid"}, "file")
            path = _source_path(source["path"])
            if path in seen_paths:
                _fail(f"duplicate source path: {path}")
            seen_paths.add(path)
            blob = source["blob_oid"]
            if state == "AUTHORIZED":
                if blob is not None:
                    _fail("AUTHORIZED blob_oid must be null")
            else:
                blob = _oid(blob, "blob_oid")
            files.append(SourceFile(path, blob))
        checkpoints.append(Checkpoint(checkpoint_id, state, freeze, tuple(files)))
    result = Manifest(tuple(checkpoints))
    if result.checkpoints[0] != _bootstrap().checkpoints[0]:
        _fail("exact C01 bootstrap entry required")
    return result


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "--literal-pathspecs", *args],
        cwd=repo,
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        _fail(f"Git proof failed: {args[0]}")
    return result.stdout


def _ancestor(repo: Path, ancestor: str, head: str) -> None:
    if _git(repo, "cat-file", "-t", ancestor).strip() != b"commit":
        _fail("source freeze/baseline identity must be a real commit object")
    _git(repo, "merge-base", "--is-ancestor", ancestor, head)


def _tree(
    repo: Path, commit: str, *paths: str, include_trees: bool = False
) -> dict[str, TreeEntry]:
    result: dict[str, TreeEntry] = {}
    flags = ("-r", "-z", "-t") if include_trees else ("-r", "-z")
    for record in _git(repo, "ls-tree", *flags, commit, "--", *paths).split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, oid = metadata.decode("ascii").split(" ")
        result[raw_path.decode("utf-8", errors="strict")] = TreeEntry(mode, kind, oid)
    return result


def _regular(entry: TreeEntry, path: str) -> None:
    if entry.mode not in REGULAR_MODES or entry.kind != "blob":
        _fail(f"non-regular Git entry: {path}")


def _transition(previous: Manifest, current: Manifest) -> None:
    previous_entries = {entry.checkpoint: entry for entry in previous.checkpoints}
    current_entries = {entry.checkpoint: entry for entry in current.checkpoints}
    for checkpoint_id, before in previous_entries.items():
        after = current_entries.get(checkpoint_id)
        if after is None:
            _fail(f"checkpoint entry deletion: {checkpoint_id}")
        if before.state == "CLOSED" and before != after:
            _fail(f"CLOSED entry changed: {checkpoint_id}")
        if before.state == "AUTHORIZED":
            if tuple(file.path for file in before.files) != tuple(
                file.path for file in after.files
            ):
                _fail(f"AUTHORIZED path list changed: {checkpoint_id}")
    previous_ids = tuple(previous_entries)
    if tuple(current_entries)[: len(previous_ids)] != previous_ids:
        _fail("new checkpoint entries must be appended")
    for checkpoint_id, entry in current_entries.items():
        if checkpoint_id not in previous_entries and entry.state != "AUTHORIZED":
            _fail(f"new checkpoint must begin AUTHORIZED: {checkpoint_id}")


def _history(repo: Path, head: str, manifest_path: str) -> tuple[Manifest | None, str | None]:
    """Validate all parent edges, including deletion and non-first-parent histories."""
    graph = (
        _git(
            repo,
            "rev-list",
            "--parents",
            "--reverse",
            "--topo-order",
            head,
            "--not",
            W03_BASELINE_SHA,
        )
        .decode("ascii")
        .splitlines()
    )
    states: dict[str, tuple[Manifest | None, str | None]] = {}
    parsed: dict[str, Manifest] = {}
    for line in graph:
        commit, *parents = line.split()
        tree = _tree(repo, commit, manifest_path, include_trees=True)
        entry = tree.get(manifest_path)
        inherited = [
            states[parent][0]
            for parent in parents
            if parent in states and states[parent][0] is not None
        ]
        if entry is None:
            if inherited:
                _fail(f"manifest deletion at commit: {commit}")
            states[commit] = (None, None)
            continue
        _regular(entry, manifest_path)
        if entry.oid not in parsed:
            parsed[entry.oid] = parse_manifest(_git(repo, "cat-file", "blob", entry.oid))
        current = parsed[entry.oid]
        if not inherited and current != _bootstrap():
            _fail("initial manifest must contain exactly the C01 bootstrap")
        for previous in inherited:
            if previous is not None:
                _transition(previous, current)
        # An historical closeout must bind an ancestor of that actual version,
        # rather than a later commit that only becomes an ancestor of final HEAD.
        for checkpoint in current.checkpoints:
            if checkpoint.source_freeze_sha is not None:
                _ancestor(repo, checkpoint.source_freeze_sha, commit)
        states[commit] = (current, entry.oid)
    return states.get(head, (None, None))


def _source_tree(
    repo: Path, head: str, manifest: Manifest
) -> tuple[dict[str, TreeEntry], list[str]]:
    baseline = _tree(repo, W03_BASELINE_SHA, "src")
    current_with_trees = _tree(repo, head, "src", include_trees=True)
    current = {path: entry for path, entry in current_with_trees.items() if entry.kind != "tree"}
    for path, entry in current.items():
        _regular(entry, path)
    for path, entry in baseline.items():
        _regular(entry, path)
        if current.get(path) != entry:
            _fail(f"W03 baseline source changed: {path}")
    registered = {file.path for entry in manifest.checkpoints for file in entry.files}
    for path in sorted(registered):
        if path in current_with_trees:
            _regular(current_with_trees[path], path)
    if registered & baseline.keys():
        _fail("manifest reassigns W03 baseline source")
    added = sorted(current.keys() - baseline.keys())
    unexpected = set(added) - registered
    if unexpected:
        _fail(f"unexpected source addition: {sorted(unexpected)[0]}")
    frozen_trees: dict[str, dict[str, TreeEntry]] = {}
    for checkpoint in manifest.checkpoints:
        freeze = checkpoint.source_freeze_sha
        if checkpoint.state == "AUTHORIZED":
            continue
        if freeze is None:
            _fail("CLOSED source_freeze_sha missing")
        _ancestor(repo, freeze, head)
        if freeze not in frozen_trees:
            frozen_trees[freeze] = _tree(repo, freeze, W04_SOURCE_ROOT)
        frozen = frozen_trees[freeze]
        for source in checkpoint.files:
            at_freeze = frozen.get(source.path)
            at_head = current.get(source.path)
            if at_freeze is None or at_head is None:
                _fail(f"CLOSED source missing: {source.path}")
            _regular(at_freeze, source.path)
            if at_freeze.oid != source.blob_oid or at_head.oid != source.blob_oid:
                _fail(f"CLOSED source blob drift: {source.path}")
            if at_head != at_freeze:
                _fail(f"CLOSED source mode/type drift: {source.path}")
    return current, added


def _worktree(repo: Path, sources: dict[str, TreeEntry]) -> None:
    if _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", "src"):
        _fail("source worktree staged/unstaged/untracked drift")
    paths = sorted(sources)
    for path in paths:
        local = repo
        parts = path.split("/")
        for part in parts[:-1]:
            local /= part
            if not stat.S_ISDIR(local.lstat().st_mode):
                _fail(f"non-regular source worktree directory: {path}")
        if not stat.S_ISREG((local / parts[-1]).lstat().st_mode):
            _fail(f"non-regular source worktree file: {path}")
    # Hash through Git's filters so ordinary LF/CRLF checkouts remain valid.
    # This also detects content hidden by assume-unchanged/skip-worktree flags.
    inputs = "".join(json.dumps(path, ensure_ascii=False) + "\n" for path in paths).encode("utf-8")
    hashes = (
        _git(repo, "hash-object", "--stdin-paths", input_bytes=inputs).decode("ascii").splitlines()
    )
    if len(hashes) != len(paths) or any(
        oid != sources[path].oid for path, oid in zip(paths, hashes, strict=True)
    ):
        _fail("source worktree content drift")


def verify_source_evolution(manifest_path: Path, expected_head: str, repo: Path) -> dict[str, Any]:
    """Prove the exact HEAD against the manifest and its complete ancestor history."""
    try:
        return _verify_source_evolution(manifest_path, expected_head, repo)
    except (OSError, UnicodeError) as error:
        raise SourceEvolutionError("source proof filesystem or encoding failure") from error


def _verify_source_evolution(manifest_path: Path, expected_head: str, repo: Path) -> dict[str, Any]:
    _oid(expected_head, "expected HEAD")
    repo = repo.resolve()
    git_root = Path(_git(repo, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve()
    if git_root != repo:
        _fail("repo must be the Git worktree root")
    manifest_path = manifest_path if manifest_path.is_absolute() else repo / manifest_path
    if not manifest_path.resolve().is_relative_to(repo) or not stat.S_ISREG(
        manifest_path.lstat().st_mode
    ):
        _fail("manifest must be a regular file inside the repository")
    relative = manifest_path.relative_to(repo).as_posix()
    if relative != MANIFEST_PATH:
        _fail("manifest path must be the canonical W04 source-evolution manifest")
    local = repo
    for part in relative.split("/")[:-1]:
        local /= part
        if not stat.S_ISDIR(local.lstat().st_mode):
            _fail("manifest worktree directory must be regular")
    content = manifest_path.read_bytes()
    worktree_content = content
    manifest = parse_manifest(content)
    head = _git(repo, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()
    if head != expected_head:
        _fail("exact HEAD mismatch")
    _ancestor(repo, W03_BASELINE_SHA, head)
    historical, manifest_oid = _history(repo, head, relative)
    if historical is None:
        if manifest != _bootstrap():
            _fail("initial manifest must contain exactly the C01 bootstrap")
    else:
        actual_oid = (
            _git(repo, "hash-object", f"--path={relative}", relative).decode("ascii").strip()
        )
        if manifest_oid != actual_oid or manifest != historical:
            _fail("manifest worktree does not match committed HEAD")
        # The output digest is bound to Git's accepted bytes, independent of checkout EOLs.
        if manifest_oid is not None:
            content = _git(repo, "cat-file", "blob", manifest_oid)
    sources, added = _source_tree(repo, head, manifest)
    _worktree(repo, sources)
    if _git(repo, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip() != head:
        _fail("exact HEAD changed during source proof")
    if manifest_path.read_bytes() != worktree_content:
        _fail("manifest changed during source proof")
    return {
        "schema_version": SCHEMA_VERSION,
        "expected_head": expected_head,
        "w03_baseline_sha": W03_BASELINE_SHA,
        "manifest_path": relative,
        "manifest_sha256": hashlib.sha256(content).hexdigest(),
        "closed_checkpoints": [
            entry.checkpoint for entry in manifest.checkpoints if entry.state == "CLOSED"
        ],
        "authorized_checkpoints": [
            entry.checkpoint for entry in manifest.checkpoints if entry.state == "AUTHORIZED"
        ],
        "actual_added_source_paths": added,
        "overall": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    output_path: Path | None = None
    failure = {
        "schema_version": SCHEMA_VERSION,
        "expected_head": args.expected_head,
        "w03_baseline_sha": W03_BASELINE_SHA,
        "manifest_path": MANIFEST_PATH,
        "manifest_sha256": None,
        "closed_checkpoints": [],
        "authorized_checkpoints": [],
        "actual_added_source_paths": [],
        "overall": "FAIL",
        "error": "source proof has not completed",
    }
    try:
        if args.output_json is not None:
            git_root = Path(
                _git(args.repo.resolve(), "rev-parse", "--show-toplevel").decode("utf-8").strip()
            ).resolve()
            candidate = args.output_json.resolve()
            if candidate.is_relative_to(git_root):
                _fail("output JSON must be outside the repository")
            output_path = candidate
            # Invalidate stale PASS evidence before any proof work can be interrupted.
            output_path.write_text(
                json.dumps(failure, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        result = verify_source_evolution(args.manifest, args.expected_head, args.repo)
        output = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if output_path is not None:
            output_path.write_text(output, encoding="utf-8", newline="\n")
    except (SourceEvolutionError, OSError) as error:
        if output_path is not None:
            failure["error"] = str(error)
            try:
                output_path.write_text(
                    json.dumps(failure, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
            except OSError as output_error:
                print(f"Source evolution failure output could not be written: {output_error}")
        print(f"Source evolution proof failed: {error}")
        return 1
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
