"""D01-D26: strict source manifests, immutable history and exact-HEAD source proof."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/ci"))

import verify_w04_source_evolution as verifier  # noqa: E402

SOURCE_ROOT = "src/flowlens/investigation"
BASELINE_FILE = "src/flowlens/base.py"
BOOTSTRAP_FILE = f"{SOURCE_ROOT}/__init__.py"


def git(repo: Path, *args: str, input_text: str | None = None) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        input=input_text,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def commit(repo: Path, changes: dict[str, str | None], message: str = "fixture") -> str:
    for path, content in changes.items():
        target = repo / path
        if content is None:
            target.unlink()
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


@dataclass
class Repository:
    repo: Path
    baseline: str
    freeze: str
    document: dict[str, Any]

    @property
    def manifest_path(self) -> Path:
        return self.repo / verifier.MANIFEST_PATH

    @property
    def head(self) -> str:
        return git(self.repo, "rev-parse", "HEAD")

    def write_manifest(self) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            json.dumps(self.document, indent=2) + "\n", encoding="utf-8", newline="\n"
        )

    def publish_manifest(self) -> str:
        self.write_manifest()
        return commit(self.repo, {}, "manifest")

    def verify(self) -> dict[str, Any]:
        return verifier.verify_source_evolution(self.manifest_path, self.head, self.repo)

    def authorize(self, paths: list[str], checkpoint: str = "W04-C02") -> str:
        self.document["checkpoints"].append(
            {
                "checkpoint": checkpoint,
                "state": "AUTHORIZED",
                "source_freeze_sha": None,
                "files": [{"path": path, "blob_oid": None} for path in paths],
            }
        )
        return self.publish_manifest()

    def close(self, freeze: str) -> str:
        entry = self.document["checkpoints"][-1]
        entry["state"] = "CLOSED"
        entry["source_freeze_sha"] = freeze
        for source in entry["files"]:
            source["blob_oid"] = git(self.repo, "rev-parse", f"{freeze}:{source['path']}")
        return self.publish_manifest()


@pytest.fixture
def repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Repository:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "ci@example.test")
    git(tmp_path, "config", "user.name", "CI Test")
    git(tmp_path, "config", "core.autocrlf", "false")
    git(tmp_path, "config", "core.filemode", "false")
    baseline = commit(tmp_path, {BASELINE_FILE: "baseline = 1\n"}, "W03 baseline")
    freeze = commit(tmp_path, {BOOTSTRAP_FILE: "bootstrap = 1\n"}, "accepted bootstrap")
    oid = git(tmp_path, "rev-parse", f"{freeze}:{BOOTSTRAP_FILE}")
    monkeypatch.setattr(verifier, "W03_BASELINE_SHA", baseline)
    monkeypatch.setattr(verifier, "C01_SOURCE_FREEZE_SHA", freeze)
    monkeypatch.setattr(verifier, "C01_FILES", ((BOOTSTRAP_FILE, oid),))
    result = Repository(
        tmp_path,
        baseline,
        freeze,
        {
            "schema_version": verifier.SCHEMA_VERSION,
            "policy_id": verifier.POLICY_ID,
            "w03_baseline_sha": baseline,
            "w04_source_root": SOURCE_ROOT,
            "checkpoints": [
                {
                    "checkpoint": "W04-C01",
                    "state": "CLOSED",
                    "source_freeze_sha": freeze,
                    "files": [{"path": BOOTSTRAP_FILE, "blob_oid": oid}],
                }
            ],
        },
    )
    result.write_manifest()
    return result


def parse(document: dict[str, Any]) -> verifier.Manifest:
    return verifier.parse_manifest(json.dumps(document).encode("utf-8"))


def future_path(label: str = "fixture") -> str:
    """Synthetic future source; this does not describe or authorize real C02 work."""
    return f"{SOURCE_ROOT}/{label}_source.py"


def closed_future(repository: Repository) -> tuple[str, str]:
    repository.publish_manifest()
    path = future_path()
    repository.authorize([path])
    freeze = commit(repository.repo, {path: "fixture = 1\n"}, "authorized source")
    repository.close(freeze)
    return path, freeze


def test_d01_normative_manifest_has_exact_frozen_c01() -> None:
    path = Path(__file__).resolve().parents[1] / verifier.MANIFEST_PATH
    document = json.loads(path.read_text(encoding="utf-8"))
    assert verifier.W03_BASELINE_SHA == "af61bdfd5f7cf7961811c4c2dc8e554dd7eed509"
    assert verifier.C01_SOURCE_FREEZE_SHA == "084c2fea93d0e021994de015c986de9ff92bf9a3"
    assert verifier.C01_FILES == (
        (f"{SOURCE_ROOT}/__init__.py", "c23929f85dccd78bc72ef3b2b1415c6e8eaf0452"),
        (f"{SOURCE_ROOT}/contracts.py", "0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e"),
        (f"{SOURCE_ROOT}/enums.py", "9c818780423f32f144b18666784ebc9ea3abdccc"),
    )
    assert parse(document) == verifier._bootstrap()


@pytest.mark.parametrize("level", ["manifest", "checkpoint", "file"])
@pytest.mark.parametrize("defect", ["missing", "extra"])
def test_d01_strict_keys_at_every_level(repository: Repository, level: str, defect: str) -> None:
    document = copy.deepcopy(repository.document)
    target = document
    if level == "checkpoint":
        target = document["checkpoints"][0]
    elif level == "file":
        target = document["checkpoints"][0]["files"][0]
    if defect == "missing":
        target.pop(next(iter(target)))
    else:
        target["unexpected"] = True
    with pytest.raises(verifier.SourceEvolutionError, match="schema"):
        parse(document)


@pytest.mark.parametrize("field", ["schema_version", "policy_id", "checkpoints"])
def test_d01_invalid_top_level_values(repository: Repository, field: str) -> None:
    repository.document[field] = False
    with pytest.raises(verifier.SourceEvolutionError):
        parse(repository.document)


@pytest.mark.parametrize("location", ["manifest", "checkpoint", "file"])
def test_d02_duplicate_json_keys_rejected(repository: Repository, location: str) -> None:
    raw = json.dumps(repository.document)
    key = {"manifest": "policy_id", "checkpoint": "state", "file": "path"}[location]
    token = json.dumps(key) + ":"
    raw = raw.replace(token, token + " null, " + token, 1)
    with pytest.raises(verifier.SourceEvolutionError, match="duplicate JSON key"):
        verifier.parse_manifest(raw.encode())


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_d02_invalid_json_constants_rejected(repository: Repository, constant: str) -> None:
    raw = json.dumps(repository.document).replace('"W04-DEVCTRL-01"', constant)
    with pytest.raises(verifier.SourceEvolutionError, match="invalid JSON constant"):
        verifier.parse_manifest(raw.encode())


@pytest.mark.parametrize("raw", [b"{", b"[]", b"null", b"\xff", b"\xef\xbb\xbf{}"])
def test_d02_invalid_json_encoding_and_roots_rejected(raw: bytes) -> None:
    with pytest.raises(verifier.SourceEvolutionError):
        verifier.parse_manifest(raw)


def test_d03_w03_baseline_is_exact(repository: Repository) -> None:
    repository.document["w03_baseline_sha"] = "0" * 40
    with pytest.raises(verifier.SourceEvolutionError, match="W03 baseline SHA"):
        parse(repository.document)


@pytest.mark.parametrize("root", [SOURCE_ROOT + "/", "src/flowlens", "other", None])
def test_d04_w04_source_root_is_exact(repository: Repository, root: str | None) -> None:
    repository.document["w04_source_root"] = root
    with pytest.raises(verifier.SourceEvolutionError, match="W04 source root"):
        parse(repository.document)


@pytest.mark.parametrize("checkpoint", ["W04-C00", "W04-C11", "W04-C1", "W03-C01", 1])
def test_d05_checkpoint_id_closed_vocabulary(repository: Repository, checkpoint: str | int) -> None:
    repository.document["checkpoints"][0]["checkpoint"] = checkpoint
    with pytest.raises(verifier.SourceEvolutionError, match="checkpoint id"):
        parse(repository.document)


@pytest.mark.parametrize("state", ["OPEN", "AUTHORIZED ", "closed", None, {}])
def test_d05_checkpoint_state_closed_vocabulary(repository: Repository, state: Any) -> None:
    repository.document["checkpoints"][0]["state"] = state
    with pytest.raises(verifier.SourceEvolutionError, match="checkpoint state"):
        parse(repository.document)


@pytest.mark.parametrize("field", ["source_freeze_sha", "blob_oid"])
@pytest.mark.parametrize("value", [None, "f" * 39, "G" * 40, "F" * 40, 1])
def test_d05_closed_sha_and_blob_grammar(repository: Repository, field: str, value: Any) -> None:
    entry = repository.document["checkpoints"][0]
    target = entry if field == "source_freeze_sha" else entry["files"][0]
    target[field] = value
    with pytest.raises(verifier.SourceEvolutionError, match="invalid"):
        parse(repository.document)


@pytest.mark.parametrize("field", ["source_freeze_sha", "blob_oid"])
def test_d05_authorized_freeze_and_blobs_must_be_null(repository: Repository, field: str) -> None:
    repository.document["checkpoints"].append(
        {
            "checkpoint": "W04-C02",
            "state": "AUTHORIZED",
            "source_freeze_sha": None,
            "files": [{"path": future_path(), "blob_oid": None}],
        }
    )
    entry = repository.document["checkpoints"][-1]
    target = entry if field == "source_freeze_sha" else entry["files"][0]
    target[field] = "a" * 40
    with pytest.raises(verifier.SourceEvolutionError, match="must be null"):
        parse(repository.document)


@pytest.mark.parametrize("defect", ["duplicate", "unordered"])
def test_d06_checkpoint_ordering_and_uniqueness(repository: Repository, defect: str) -> None:
    repository.document["checkpoints"].append(copy.deepcopy(repository.document["checkpoints"][0]))
    if defect == "unordered":
        repository.document["checkpoints"][0]["checkpoint"] = "W04-C02"
    with pytest.raises(verifier.SourceEvolutionError, match="ordering or uniqueness"):
        parse(repository.document)


@pytest.mark.parametrize(
    "path",
    [
        "/src/flowlens/investigation/file.py",
        "C:/src/flowlens/investigation/file.py",
        "src\\flowlens\\investigation\\file.py",
        SOURCE_ROOT,
        SOURCE_ROOT + "/",
        SOURCE_ROOT + "//file.py",
        SOURCE_ROOT + "/./file.py",
        SOURCE_ROOT + "/../file.py",
        SOURCE_ROOT + "-other/file.py",
        "src/flowlens/elsewhere.py",
        SOURCE_ROOT + "/line\nbreak.py",
        SOURCE_ROOT + "/colon:name.py",
        None,
    ],
)
def test_d07_source_path_normalization_and_namespace(repository: Repository, path: Any) -> None:
    repository.document["checkpoints"][0]["files"][0]["path"] = path
    with pytest.raises(verifier.SourceEvolutionError, match="source path"):
        parse(repository.document)


@pytest.mark.parametrize("across_checkpoints", [False, True])
def test_d08_duplicate_source_path_rejected(
    repository: Repository, across_checkpoints: bool
) -> None:
    source = copy.deepcopy(repository.document["checkpoints"][0]["files"][0])
    if across_checkpoints:
        source["blob_oid"] = None
        repository.document["checkpoints"].append(
            {
                "checkpoint": "W04-C02",
                "state": "AUTHORIZED",
                "source_freeze_sha": None,
                "files": [source],
            }
        )
    else:
        repository.document["checkpoints"][0]["files"].append(source)
    with pytest.raises(verifier.SourceEvolutionError, match="duplicate source path"):
        parse(repository.document)


@pytest.mark.parametrize("committed", [False, True])
def test_d09_initial_manifest_cannot_bootstrap_future_authority(
    repository: Repository, committed: bool
) -> None:
    repository.document["checkpoints"].append(
        {
            "checkpoint": "W04-C02",
            "state": "AUTHORIZED",
            "source_freeze_sha": None,
            "files": [{"path": future_path(), "blob_oid": None}],
        }
    )
    repository.write_manifest()
    if committed:
        repository.publish_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="initial manifest"):
        repository.verify()


def test_d09_exact_c01_uncommitted_bootstrap_and_commit_pass(repository: Repository) -> None:
    assert repository.verify()["overall"] == "PASS"
    repository.publish_manifest()
    assert repository.verify()["overall"] == "PASS"


def test_d10_exact_c01_freeze_sha(repository: Repository) -> None:
    repository.document["checkpoints"][0]["source_freeze_sha"] = repository.baseline
    with pytest.raises(verifier.SourceEvolutionError, match="exact C01"):
        parse(repository.document)


def test_d11_exact_c01_blob_oid(repository: Repository) -> None:
    repository.document["checkpoints"][0]["files"][0]["blob_oid"] = "0" * 40
    with pytest.raises(verifier.SourceEvolutionError, match="exact C01"):
        parse(repository.document)


def test_d12_previous_closed_freeze_is_immutable(repository: Repository) -> None:
    closed_future(repository)
    previous_head = repository.head
    repository.document["checkpoints"][-1]["source_freeze_sha"] = previous_head
    repository.publish_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="CLOSED entry changed"):
        repository.verify()


@pytest.mark.parametrize("defect", ["replace", "append", "reorder", "reassign"])
def test_d13_authorized_paths_are_immutable(repository: Repository, defect: str) -> None:
    repository.publish_manifest()
    paths = [future_path("first"), future_path("second")]
    repository.authorize(paths)
    files = repository.document["checkpoints"][-1]["files"]
    if defect == "replace":
        files[0]["path"] = future_path("replacement")
    elif defect == "append":
        files.append({"path": future_path("extra"), "blob_oid": None})
    elif defect == "reorder":
        files.reverse()
    else:
        moved = files.pop()
        repository.document["checkpoints"].append(
            {
                "checkpoint": "W04-C03",
                "state": "AUTHORIZED",
                "source_freeze_sha": None,
                "files": [moved],
            }
        )
    repository.publish_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="AUTHORIZED path list changed"):
        repository.verify()


def test_d14_authorized_to_closed_transition_passes_once(repository: Repository) -> None:
    path, freeze = closed_future(repository)
    result = repository.verify()
    assert result["closed_checkpoints"] == ["W04-C01", "W04-C02"]
    assert result["authorized_checkpoints"] == []
    assert path in result["actual_added_source_paths"]
    assert repository.document["checkpoints"][-1]["source_freeze_sha"] == freeze
    commit(repository.repo, {"evidence.md": "unchanged closeout\n"})
    assert repository.verify()["overall"] == "PASS"


def test_d15_closed_to_authorized_is_rejected(repository: Repository) -> None:
    closed_future(repository)
    entry = repository.document["checkpoints"][-1]
    entry["state"] = "AUTHORIZED"
    entry["source_freeze_sha"] = None
    for source in entry["files"]:
        source["blob_oid"] = None
    repository.publish_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="CLOSED entry changed"):
        repository.verify()


def test_d16_checkpoint_entry_deletion_is_rejected(repository: Repository) -> None:
    repository.publish_manifest()
    repository.authorize([future_path()])
    repository.document["checkpoints"].pop()
    repository.publish_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="entry deletion"):
        repository.verify()


@pytest.mark.parametrize("recreate", [False, True])
def test_d16_manifest_deletion_and_recreation_do_not_reset_history(
    repository: Repository, recreate: bool
) -> None:
    repository.publish_manifest()
    commit(repository.repo, {verifier.MANIFEST_PATH: None}, "delete manifest")
    if recreate:
        repository.publish_manifest()
    else:
        repository.write_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="manifest deletion"):
        repository.verify()


def test_d12_full_dag_rejects_mutated_closed_side_branch_after_restoration(
    repository: Repository,
) -> None:
    closed_future(repository)
    fork = repository.head
    accepted = copy.deepcopy(repository.document)
    git(repository.repo, "checkout", "-q", "-b", "side")
    repository.document["checkpoints"][-1]["source_freeze_sha"] = fork
    repository.publish_manifest()
    repository.document = accepted
    repository.publish_manifest()
    git(repository.repo, "checkout", "-q", "main")
    commit(repository.repo, {"main-evidence.md": "main\n"})
    git(repository.repo, "merge", "--no-ff", "-q", "side", "-m", "merge restored side")
    with pytest.raises(verifier.SourceEvolutionError, match="CLOSED entry changed"):
        repository.verify()


def test_d13_merge_cannot_choose_one_of_conflicting_authorized_path_lists(
    repository: Repository,
) -> None:
    repository.publish_manifest()
    fork = repository.head
    initial = copy.deepcopy(repository.document)
    repository.authorize([future_path("main")])
    accepted_main = copy.deepcopy(repository.document)
    git(repository.repo, "checkout", "-q", "-b", "side", fork)
    repository.document = initial
    repository.authorize([future_path("side")])
    git(repository.repo, "checkout", "-q", "main")
    git(repository.repo, "merge", "-q", "--no-ff", "-s", "ours", "side", "-m", "select main")
    repository.document = accepted_main
    with pytest.raises(verifier.SourceEvolutionError, match="AUTHORIZED path list changed"):
        repository.verify()


def test_d17_new_checkpoint_must_begin_authorized(repository: Repository) -> None:
    repository.publish_manifest()
    path = future_path()
    freeze = commit(repository.repo, {path: "future = 1\n"})
    repository.document["checkpoints"].append(
        {
            "checkpoint": "W04-C02",
            "state": "CLOSED",
            "source_freeze_sha": freeze,
            "files": [
                {"path": path, "blob_oid": git(repository.repo, "rev-parse", f"{freeze}:{path}")}
            ],
        }
    )
    repository.publish_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="must begin AUTHORIZED"):
        repository.verify()


def test_d17_new_checkpoint_entries_must_be_appended(repository: Repository) -> None:
    repository.publish_manifest()
    repository.authorize([future_path("later")], "W04-C03")
    repository.document["checkpoints"].insert(
        1,
        {
            "checkpoint": "W04-C02",
            "state": "AUTHORIZED",
            "source_freeze_sha": None,
            "files": [{"path": future_path("inserted"), "blob_oid": None}],
        },
    )
    repository.publish_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="must be appended"):
        repository.verify()


@pytest.mark.parametrize("head", ["0" * 40, "HEAD", "f" * 39])
def test_d18_exact_expected_head_required(repository: Repository, head: str) -> None:
    with pytest.raises(verifier.SourceEvolutionError, match="HEAD"):
        verifier.verify_source_evolution(repository.manifest_path, head, repository.repo)


def test_d19_baseline_must_exist(repository: Repository, monkeypatch: pytest.MonkeyPatch) -> None:
    missing = "0" * 40
    monkeypatch.setattr(verifier, "W03_BASELINE_SHA", missing)
    repository.document["w03_baseline_sha"] = missing
    repository.write_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="Git proof failed"):
        repository.verify()


def test_d19_baseline_must_be_ancestor(
    repository: Repository, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(repository.repo, "checkout", "--orphan", "unrelated")
    git(repository.repo, "rm", "-q", "-r", "--cached", ".")
    unrelated = commit(repository.repo, {"unrelated.md": "unrelated\n"})
    git(repository.repo, "checkout", "-q", "main")
    monkeypatch.setattr(verifier, "W03_BASELINE_SHA", unrelated)
    repository.document["w03_baseline_sha"] = unrelated
    repository.write_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="Git proof failed"):
        repository.verify()


@pytest.mark.parametrize("defect", ["modify", "delete", "rename", "mode", "symlink"])
def test_d20_w03_baseline_source_freeze_includes_modes_and_types(
    repository: Repository, defect: str
) -> None:
    repository.publish_manifest()
    if defect == "modify":
        commit(repository.repo, {BASELINE_FILE: "baseline = 2\n"})
    elif defect == "delete":
        commit(repository.repo, {BASELINE_FILE: None})
    elif defect == "rename":
        git(repository.repo, "mv", BASELINE_FILE, "src/flowlens/renamed.py")
        commit(repository.repo, {})
    elif defect == "mode":
        git(repository.repo, "update-index", "--chmod=+x", BASELINE_FILE)
        git(repository.repo, "commit", "-q", "-m", "change baseline mode")
    else:
        oid = git(repository.repo, "hash-object", "-w", "--stdin", input_text="target.py\n")
        git(repository.repo, "update-index", "--cacheinfo", "120000", oid, BASELINE_FILE)
        git(repository.repo, "commit", "-q", "-m", "change baseline type")
    with pytest.raises(verifier.SourceEvolutionError, match="baseline source changed|non-regular"):
        repository.verify()


@pytest.mark.parametrize("path", [future_path("rogue"), "src/flowlens/rogue.py"])
def test_d21_unexpected_source_addition_rejected(repository: Repository, path: str) -> None:
    repository.publish_manifest()
    commit(repository.repo, {path: "rogue = 1\n"})
    with pytest.raises(verifier.SourceEvolutionError, match="unexpected source addition"):
        repository.verify()


@pytest.mark.parametrize("present", [False, True])
def test_d22_authorized_source_may_be_absent_or_present(
    repository: Repository, present: bool
) -> None:
    repository.publish_manifest()
    path = future_path()
    repository.authorize([path])
    if present:
        commit(repository.repo, {path: "authorized = 1\n"})
    result = repository.verify()
    assert result["overall"] == "PASS"
    assert result["authorized_checkpoints"] == ["W04-C02"]
    assert (path in result["actual_added_source_paths"]) is present


def test_d22_uncommitted_authorization_cannot_replace_head_policy(repository: Repository) -> None:
    repository.publish_manifest()
    repository.document["checkpoints"].append(
        {
            "checkpoint": "W04-C02",
            "state": "AUTHORIZED",
            "source_freeze_sha": None,
            "files": [{"path": future_path(), "blob_oid": None}],
        }
    )
    repository.write_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="does not match committed HEAD"):
        repository.verify()


def test_d22_alternate_manifest_path_cannot_evade_history(repository: Repository) -> None:
    repository.publish_manifest()
    alternate = repository.repo / "alternate.json"
    alternate.write_bytes(repository.manifest_path.read_bytes())
    with pytest.raises(verifier.SourceEvolutionError, match="canonical"):
        verifier.verify_source_evolution(alternate, repository.head, repository.repo)


@pytest.mark.parametrize("where", ["head", "freeze"])
def test_d23_closed_file_must_exist_at_head_and_freeze(repository: Repository, where: str) -> None:
    if where == "head":
        path, _ = closed_future(repository)
        commit(repository.repo, {path: None})
    else:
        repository.publish_manifest()
        path = future_path()
        freeze = repository.authorize([path])
        commit(repository.repo, {path: "new = 1\n"})
        repository.document["checkpoints"][-1]["state"] = "CLOSED"
        repository.document["checkpoints"][-1]["source_freeze_sha"] = freeze
        repository.document["checkpoints"][-1]["files"][0]["blob_oid"] = git(
            repository.repo, "rev-parse", f"HEAD:{path}"
        )
        repository.publish_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="CLOSED source missing"):
        repository.verify()


@pytest.mark.parametrize("defect", ["head_blob", "freeze_blob", "mode"])
def test_d24_closed_blob_and_mode_are_frozen(repository: Repository, defect: str) -> None:
    if defect == "freeze_blob":
        repository.publish_manifest()
        path = future_path()
        repository.authorize([path])
        freeze = commit(repository.repo, {path: "source = 1\n"})
        repository.document["checkpoints"][-1]["state"] = "CLOSED"
        repository.document["checkpoints"][-1]["source_freeze_sha"] = freeze
        repository.document["checkpoints"][-1]["files"][0]["blob_oid"] = "0" * 40
        repository.publish_manifest()
    else:
        path, _ = closed_future(repository)
        if defect == "head_blob":
            commit(repository.repo, {path: "source = 2\n"})
        else:
            git(repository.repo, "update-index", "--chmod=+x", path)
            git(repository.repo, "commit", "-q", "-m", "change closed mode")
    with pytest.raises(verifier.SourceEvolutionError, match="CLOSED source (blob|mode/type) drift"):
        repository.verify()


@pytest.mark.parametrize("kind", ["symlink", "submodule", "tree"])
def test_d24_nonregular_authorized_git_entries_are_rejected(
    repository: Repository, kind: str
) -> None:
    repository.publish_manifest()
    path = future_path("nonregular")
    repository.authorize([path])
    if kind == "symlink":
        oid = git(repository.repo, "hash-object", "-w", "--stdin", input_text="target.py\n")
        git(repository.repo, "update-index", "--add", "--cacheinfo", "120000", oid, path)
        git(repository.repo, "commit", "-q", "-m", "nonregular source")
    elif kind == "submodule":
        git(
            repository.repo, "update-index", "--add", "--cacheinfo", "160000", repository.head, path
        )
        git(repository.repo, "commit", "-q", "-m", "nonregular source")
    else:
        commit(repository.repo, {path + "/nested.py": "nested = 1\n"})
    with pytest.raises(
        verifier.SourceEvolutionError, match="non-regular|unexpected source addition"
    ):
        repository.verify()


@pytest.mark.parametrize("defect", ["staged", "unstaged", "untracked"])
def test_d25_source_worktree_drift_rejected(repository: Repository, defect: str) -> None:
    repository.publish_manifest()
    path = BASELINE_FILE if defect != "untracked" else future_path("untracked")
    (repository.repo / path).write_text("drift = 1\n", encoding="utf-8")
    if defect == "staged":
        git(repository.repo, "add", path)
    with pytest.raises(verifier.SourceEvolutionError, match="source worktree"):
        repository.verify()


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_d25_hidden_tracked_source_content_drift_rejected(
    repository: Repository, flag: str
) -> None:
    repository.publish_manifest()
    git(repository.repo, "update-index", flag, BASELINE_FILE)
    (repository.repo / BASELINE_FILE).write_text("hidden = 1\n", encoding="utf-8")
    assert git(repository.repo, "status", "--porcelain", "--", "src") == ""
    with pytest.raises(verifier.SourceEvolutionError, match="content drift"):
        repository.verify()


def test_d26_output_is_deterministic_and_sorted(repository: Repository) -> None:
    repository.publish_manifest()
    paths = [future_path("zeta"), future_path("alpha")]
    repository.authorize(paths)
    commit(repository.repo, {path: "value = 1\n" for path in paths})
    first = repository.verify()
    second = repository.verify()
    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["actual_added_source_paths"] == sorted([BOOTSTRAP_FILE, *paths])
    assert first["manifest_path"] == verifier.MANIFEST_PATH
    assert first["expected_head"] == repository.head
    assert first["w03_baseline_sha"] == repository.baseline
    assert set(first) == {
        "schema_version",
        "expected_head",
        "w03_baseline_sha",
        "manifest_path",
        "manifest_sha256",
        "closed_checkpoints",
        "authorized_checkpoints",
        "actual_added_source_paths",
        "overall",
    }


def test_d26_crlf_checkout_preserves_committed_digest_and_source_identity(
    repository: Repository,
) -> None:
    repository.publish_manifest()
    expected = repository.verify()
    cloned = repository.repo.parent / f"{repository.repo.name}-crlf-clone"
    git(
        repository.repo,
        "clone",
        "-q",
        "--config",
        "core.autocrlf=true",
        str(repository.repo),
        str(cloned),
    )
    repository.repo = cloned
    assert b"\r\n" in repository.manifest_path.read_bytes()
    for path in [BASELINE_FILE, BOOTSTRAP_FILE]:
        target = repository.repo / path
        assert b"\r\n" in target.read_bytes()
    assert repository.verify() == expected


def test_d26_cli_outputs_same_deterministic_json_and_fails_closed(repository: Repository) -> None:
    repository.publish_manifest()
    script = Path(verifier.__file__).resolve()
    # The child receives the same synthetic constants; the production CLI itself is unchanged.
    harness = (
        "import sys; from pathlib import Path; "
        f"sys.path.insert(0, {str(script.parent)!r}); "
        "import verify_w04_source_evolution as v; "
        f"v.W03_BASELINE_SHA={repository.baseline!r}; "
        f"v.C01_SOURCE_FREEZE_SHA={repository.freeze!r}; "
        f"v.C01_FILES={verifier.C01_FILES!r}; "
        "raise SystemExit(v.main())"
    )
    output = repository.repo.parent / f"{repository.repo.name}-proof.json"
    arguments = [
        sys.executable,
        "-c",
        harness,
        "--manifest",
        str(repository.manifest_path),
        "--expected-head",
        repository.head,
        "--repo",
        str(repository.repo),
        "--output-json",
        str(output),
    ]
    result = subprocess.run(arguments, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout) == repository.verify()
    assert json.loads(output.read_text(encoding="utf-8")) == repository.verify()
    arguments[arguments.index("--expected-head") + 1] = "0" * 40
    failure = subprocess.run(arguments, check=False, capture_output=True, text=True)
    assert failure.returncode == 1
    assert "exact HEAD mismatch" in failure.stdout
    failure_document = json.loads(output.read_text(encoding="utf-8"))
    assert failure_document["overall"] == "FAIL"
    assert failure_document["manifest_sha256"] is None
    assert failure_document["actual_added_source_paths"] == []


def test_d09_git_tree_at_manifest_path_cannot_masquerade_as_absent(repository: Repository) -> None:
    repository.manifest_path.unlink()
    nested = verifier.MANIFEST_PATH + "/nested.json"
    commit(repository.repo, {nested: "{}\n"})
    (repository.repo / nested).unlink()
    repository.manifest_path.rmdir()
    repository.write_manifest()
    with pytest.raises(verifier.SourceEvolutionError, match="non-regular Git entry"):
        repository.verify()


def test_d22_authorized_exact_path_cannot_be_a_tree_even_with_authorized_child(
    repository: Repository,
) -> None:
    repository.publish_manifest()
    parent = f"{SOURCE_ROOT}/fixture_directory"
    child = parent + "/fixture.py"
    repository.authorize([parent, child])
    commit(repository.repo, {child: "child = 1\n"})
    with pytest.raises(verifier.SourceEvolutionError, match="non-regular Git entry"):
        repository.verify()


def test_d14_freeze_identity_must_be_commit_not_annotated_tag(repository: Repository) -> None:
    repository.publish_manifest()
    path = future_path()
    repository.authorize([path])
    freeze = commit(repository.repo, {path: "future = 1\n"})
    git(repository.repo, "tag", "-a", "accepted", freeze, "-m", "tag is not commit")
    tag_oid = git(repository.repo, "rev-parse", "accepted")
    assert tag_oid != freeze
    repository.close(tag_oid)
    with pytest.raises(verifier.SourceEvolutionError, match="real commit object"):
        repository.verify()


@pytest.mark.parametrize("label", ["[literal]", "space name", "中文"])
def test_d07_authorized_paths_are_literal_git_and_hash_inputs(
    repository: Repository, label: str
) -> None:
    repository.publish_manifest()
    path = future_path(label)
    repository.authorize([path])
    freeze = commit(repository.repo, {path: "literal = 1\n"})
    repository.close(freeze)
    assert repository.verify()["overall"] == "PASS"


@pytest.mark.parametrize("mutation", ["head", "manifest", "initial_manifest"])
def test_d18_d26_concurrent_head_or_manifest_change_fails_closed(
    repository: Repository, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    if mutation != "initial_manifest":
        repository.publish_manifest()
    original = verifier._worktree

    def mutate(repo: Path, sources: dict[str, verifier.TreeEntry]) -> None:
        original(repo, sources)
        if mutation == "head":
            commit(repo, {"concurrent.md": "concurrent commit\n"})
        else:
            repository.manifest_path.write_bytes(repository.manifest_path.read_bytes() + b" ")

    monkeypatch.setattr(verifier, "_worktree", mutate)
    with pytest.raises(verifier.SourceEvolutionError, match="changed during source proof"):
        repository.verify()


def test_d26_cli_cannot_write_json_into_repository(
    repository: Repository, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    before = (repository.repo / BASELINE_FILE).read_bytes()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "verify_w04_source_evolution.py",
            "--manifest",
            str(repository.manifest_path),
            "--expected-head",
            repository.head,
            "--repo",
            str(repository.repo),
            "--output-json",
            str(repository.repo / BASELINE_FILE),
        ],
    )
    assert verifier.main() == 1
    assert "outside the repository" in capsys.readouterr().out
    assert (repository.repo / BASELINE_FILE).read_bytes() == before


def test_d26_cli_invalidates_old_pass_before_proof_starts(
    repository: Repository, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = repository.repo.parent / f"{repository.repo.name}-interrupted.json"
    output.write_text('{"overall": "PASS"}', encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "verify_w04_source_evolution.py",
            "--manifest",
            str(repository.manifest_path),
            "--expected-head",
            repository.head,
            "--repo",
            str(repository.repo),
            "--output-json",
            str(output),
        ],
    )

    def interrupt(manifest_path: Path, expected_head: str, repo: Path) -> dict[str, Any]:
        assert json.loads(output.read_text(encoding="utf-8"))["overall"] == "FAIL"
        raise KeyboardInterrupt

    monkeypatch.setattr(verifier, "verify_source_evolution", interrupt)
    with pytest.raises(KeyboardInterrupt):
        verifier.main()
    assert json.loads(output.read_text(encoding="utf-8"))["overall"] == "FAIL"
