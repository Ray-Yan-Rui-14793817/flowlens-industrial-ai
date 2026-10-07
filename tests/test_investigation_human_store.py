"""W04-C06 J25-J45/J48: journal confinement, bytes, graph and lifecycle proofs."""

from __future__ import annotations

import ast
import inspect
import json
import os
import random
import secrets
import socket
import sqlite3
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, NoReturn

import pytest

from flowlens.investigation import c06_store as store
from flowlens.investigation.c06_policy import (
    C06_EVENT_ID_COLLISION,
    C06_HUMAN_INPUT_INVALID,
    C06_INVALID_REVIEW_CONTEXT,
    C06_STORE_BUSY,
    C06_STORE_CORRUPT,
    C06_STORE_CYCLE,
    C06_STORE_DIRTY,
    C06_STORE_FORK,
    C06_STORE_IO_FAILURE,
    C06_STORE_ROOT_INVALID,
    C06HumanInvestigationError,
)
from flowlens.investigation.c06_store import HumanInvestigationJournal
from flowlens.investigation.contracts import HumanInvestigationEvent
from flowlens.investigation.enums import HumanInvestigationOutcome
from test_c05_policy import unsafe_replace
from test_investigation_human import ReviewContext, _context, _event, _request

ROOT = Path(__file__).resolve().parents[1]
SOURCES = tuple(
    "src/flowlens/investigation/" + name
    for name in ("c06_human.py", "c06_policy.py", "c06_store.py")
)


def _error(action: Callable[[], object], code: str) -> None:
    with pytest.raises(C06HumanInvestigationError) as caught:
        action()
    assert caught.value.code == code and str(caught.value) == code
    assert caught.value.__cause__ is None


def _bytes(event: HumanInvestigationEvent) -> bytes:
    return event.to_json().encode("utf-8") + b"\n"


def _path(root: Path, event: HumanInvestigationEvent) -> Path:
    return root / event.case_id / (event.artifact_id + ".json")


def _write(root: Path, event: HumanInvestigationEvent, case_id: str | None = None) -> Path:
    directory = root / (event.case_id if case_id is None else case_id)
    directory.mkdir(exist_ok=True)
    path = directory / (event.artifact_id + ".json")
    path.write_bytes(_bytes(event))
    return path


@pytest.mark.parametrize("kind", ["relative", "missing", "file", "string"])
def test_j25_root_requires_explicit_absolute_preexisting_directory(
    tmp_path: Path, kind: str
) -> None:
    root: Any = tmp_path
    if kind == "relative":
        root = Path("relative-journal")
    elif kind == "missing":
        root = tmp_path / "missing"
    elif kind == "file":
        root = tmp_path / "file"
        root.write_bytes(b"file")
    else:
        root = str(tmp_path)
    _error(lambda: HumanInvestigationJournal(root), C06_STORE_ROOT_INVALID)


@pytest.mark.parametrize("operation", ["resolve", "iterdir"])
def test_j25_unresolvable_or_unreadable_root_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    def denied(*args: Any, **kwargs: Any) -> NoReturn:
        raise PermissionError("private filesystem details")

    with monkeypatch.context() as traps:
        traps.setattr(Path, operation, denied)
        _error(lambda: HumanInvestigationJournal(tmp_path), C06_STORE_ROOT_INVALID)


def test_j26_root_stays_explicit_after_cwd_and_environment_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    context = _context()
    trusted = tmp_path / "trusted"
    trusted.mkdir()
    journal = HumanInvestigationJournal(trusted)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    def denied(*args: Any, **kwargs: Any) -> NoReturn:
        raise AssertionError("ambient root source used")

    with monkeypatch.context() as traps:
        traps.chdir(elsewhere)
        traps.setenv("FLOWLENS_JOURNAL_ROOT", str(elsewhere))
        traps.setattr(Path, "cwd", denied)
        traps.setattr(os, "getenv", denied)
        event = journal.record(*context, **_request(context))
        assert journal.load(*context) == (event,)
    assert journal.root == trusted.resolve()
    assert not tuple(elsewhere.iterdir())
    assert _path(trusted, event).is_file()


def test_j27_event_bytes_are_exact_canonical_utf8_with_one_lf(tmp_path: Path) -> None:
    context = _context()
    journal = HumanInvestigationJournal(tmp_path)
    assert journal.load(*context) == ()
    event = journal.record(*context, **_request(context, note_text="Human 审阅\nline"))
    raw = _path(tmp_path, event).read_bytes()
    assert raw == _bytes(event) and raw.endswith(b"\n") and b"\n" not in raw[:-1]
    assert HumanInvestigationEvent.from_json(raw[:-1].decode("utf-8")) == event
    assert journal.load(*context) == (event,)
    assert not tuple((tmp_path / ".locks").iterdir())


def test_j28_filename_must_match_exact_artifact_identity(tmp_path: Path) -> None:
    context = _context()
    event = _event(context)
    path = _write(tmp_path, event)
    wrong = path.with_name("hievt_" + "f" * 64 + ".json")
    path.rename(wrong)
    journal = HumanInvestigationJournal(tmp_path)
    _error(lambda: journal.load(*context), C06_STORE_CORRUPT)
    assert wrong.read_bytes() == _bytes(event)


def test_j29_three_event_chain_preserves_all_prior_bytes(tmp_path: Path) -> None:
    context = _context()
    journal = HumanInvestigationJournal(tmp_path)
    first = journal.record(*context, **_request(context, note_text="first"))
    before = _path(tmp_path, first).read_bytes()
    second = journal.record(*context, **_request(context, note_text="second"))
    second_before = _path(tmp_path, second).read_bytes()
    third = journal.record(*context, **_request(context, note_text="third"))
    assert journal.load(*context) == (first, second, third)
    assert first.previous_event_id is None and second.previous_event_id == first.artifact_id
    assert third.previous_event_id == second.artifact_id
    assert _path(tmp_path, first).read_bytes() == before
    assert _path(tmp_path, second).read_bytes() == second_before


def test_j30_exact_tail_retry_has_no_write_and_keeps_historical_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    context = _context()
    journal = HumanInvestigationJournal(tmp_path)
    first = journal.record(*context, **_request(context))
    tail = journal.record(*context, **_request(context, note_text="tail"))
    before = {path.name: path.read_bytes() for path in _path(tmp_path, tail).parent.iterdir()}

    def denied(*args: Any, **kwargs: Any) -> NoReturn:
        raise AssertionError("retry tried to append or rebuild")

    with monkeypatch.context() as traps:
        traps.setattr(journal, "_persist_event", denied)
        traps.setattr(store, "build_human_investigation_event", denied)
        assert journal.record(*context, **_request(context, note_text="tail")) == tail
    assert tail.previous_event_id == first.artifact_id
    assert {
        path.name: path.read_bytes() for path in _path(tmp_path, tail).parent.iterdir()
    } == before


def test_j30_retry_cannot_bypass_exact_input_types(tmp_path: Path) -> None:
    class Actor(str):
        pass

    context = _context()
    journal = HumanInvestigationJournal(tmp_path)
    event = journal.record(*context, **_request(context))
    _error(
        lambda: journal.record(*context, **_request(context, actor_id=Actor(event.actor_id))),
        C06_HUMAN_INPUT_INVALID,
    )
    assert journal.load(*context) == (event,)


@pytest.mark.parametrize(
    "field",
    [
        "actor_id",
        "occurred_at",
        "outcome",
        "reviewed_finding_ids",
        "reviewed_conflict_ids",
        "acknowledged_uncertainty_item_ids",
        "note_text",
    ],
)
def test_j31_changed_request_appends_exactly_one_event(tmp_path: Path, field: str) -> None:
    context = _context(conflict=True)
    journal = HumanInvestigationJournal(tmp_path)
    first = journal.record(*context, **_request(context))
    changes: dict[str, Any] = {
        "actor_id": "other-reviewer",
        "occurred_at": first.occurred_at + timedelta(seconds=1),
        "outcome": HumanInvestigationOutcome.MORE_EVIDENCE_REQUIRED,
        "reviewed_finding_ids": (context[6][0].artifact_id,),
        "reviewed_conflict_ids": (context[7][0].artifact_id,),
        "acknowledged_uncertainty_item_ids": (context[8].items[0].artifact_id,),
        "note_text": "changed audit note",
    }
    request = _request(context, **{field: changes[field]})
    if field == "outcome":
        request["reviewed_conflict_ids"] = (context[7][0].artifact_id,)
    second = journal.record(*context, **request)
    assert journal.load(*context) == (first, second)
    assert second.artifact_id != first.artifact_id and second.previous_event_id == first.artifact_id
    assert len(tuple(_path(tmp_path, second).parent.iterdir())) == 2


@pytest.mark.parametrize("same_bytes", [False, True])
def test_j32_existing_target_collision_or_identical_bytes_is_preserved(
    tmp_path: Path, same_bytes: bool
) -> None:
    context = _context()
    event = _event(context)
    path = _write(tmp_path, event)
    raw = _bytes(event) if same_bytes else b"hostile existing bytes\n"
    path.write_bytes(raw)
    journal = HumanInvestigationJournal(tmp_path)
    if same_bytes:
        journal._persist_event(event.case_id, event)
    else:
        _error(lambda: journal._persist_event(event.case_id, event), C06_EVENT_ID_COLLISION)
    assert path.read_bytes() == raw and len(tuple(path.parent.iterdir())) == 1


@pytest.mark.parametrize("same_bytes", [False, True])
def test_j32_target_recheck_before_rename_handles_collision_or_identical_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, same_bytes: bool
) -> None:
    context = _context()
    event = _event(context)
    target = _path(tmp_path, event)
    original_fsync = os.fsync
    collision = _bytes(event) if same_bytes else b"other-writer\n"

    def injected(fd: int) -> None:
        original_fsync(fd)
        target.write_bytes(collision)

    with monkeypatch.context() as traps:
        traps.setattr(os, "fsync", injected)
        journal = HumanInvestigationJournal(tmp_path)
        if same_bytes:
            assert journal.record(*context, **_request(context)) == event
        else:
            _error(lambda: journal.record(*context, **_request(context)), C06_EVENT_ID_COLLISION)
    assert target.read_bytes() == collision and len(tuple(target.parent.iterdir())) == 1


@pytest.mark.parametrize("shape", ["missing", "roots", "fork"])
def test_j33_j34_j35_missing_parent_multiple_roots_and_fork_fail_closed(
    tmp_path: Path, shape: str
) -> None:
    context = _context()
    first = _event(context)
    child = _event(context, previous_event=first, actor_id="child")
    sibling = _event(context, previous_event=first, actor_id="sibling")
    if shape == "missing":
        _write(tmp_path, child)
        code = C06_STORE_CORRUPT
    elif shape == "roots":
        _write(tmp_path, first)
        _write(tmp_path, _event(context, actor_id="another-root"))
        code = C06_STORE_CORRUPT
    else:
        for event in (first, child, sibling):
            _write(tmp_path, event)
        code = C06_STORE_FORK
    journal = HumanInvestigationJournal(tmp_path)
    _error(lambda: journal.load(*context), code)


def test_j36_cycle_like_tampered_history_fails_closed_without_repair(tmp_path: Path) -> None:
    context = _context()
    event = _event(context)
    path = _write(tmp_path, event)
    item = json.loads(path.read_bytes())
    item["previous_event_id"] = event.artifact_id
    raw = json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    path.write_bytes(raw)
    journal = HumanInvestigationJournal(tmp_path)
    with pytest.raises(C06HumanInvestigationError) as caught:
        journal.load(*context)
    assert caught.value.code in {C06_STORE_CORRUPT, C06_STORE_CYCLE}
    assert path.read_bytes() == raw


def _alter(raw: bytes, defect: str) -> bytes:
    if defect == "json":
        return b"{\n"
    if defect == "array":
        return b"[]\n"
    if defect == "null":
        return b"null\n"
    if defect == "escaped_string":
        return raw.replace(b'"actor_id":"human-reviewer"', b'"actor_id":"\\u0068uman-reviewer"', 1)
    if defect == "utf8":
        return b"\xff\n"
    if defect == "bom":
        return b"\xef\xbb\xbf" + raw
    if defect == "space":
        return b" " + raw
    if defect == "pretty":
        return json.dumps(json.loads(raw), indent=2).encode() + b"\n"
    if defect == "missing_lf":
        return raw[:-1]
    if defect == "double_lf":
        return raw + b"\n"
    if defect == "crlf":
        return raw[:-1] + b"\r\n"
    if defect == "duplicate":
        return raw.replace(b'"actor_id":', b'"actor_id":"duplicate","actor_id":', 1)
    item = json.loads(raw)
    if defect == "datetime_precision":
        item["occurred_at"] = item["occurred_at"].replace(".000000Z", "Z")
    elif defect == "offset_time":
        item["occurred_at"] = (
            datetime.fromisoformat(item["occurred_at"])
            .astimezone(timezone(timedelta(hours=8)))
            .isoformat()
        )
    elif defect == "extra":
        item["unauthorized_action"] = "execute"
    elif defect == "missing":
        del item["actor_id"]
    elif defect == "float":
        item["actor_id"] = 1.0
    elif defect == "nonfinite":
        item["actor_id"] = float("nan")
    else:
        field, value = {
            "enum": ("outcome", "EXECUTE_REMEDY"),
            "naive_time": ("occurred_at", "2026-01-01T00:00:00"),
            "bad_time": ("occurred_at", "tomorrow"),
            "upper_time_overflow": ("occurred_at", "9999-12-31T23:59:59.999999-01:00"),
            "lower_time_overflow": ("occurred_at", "0001-01-01T00:00:00.000000+01:00"),
            "offset_time": ("occurred_at", "2026-01-20T08:00:00.000000+08:00"),
            "hash": ("content_hash", "f" * 64),
            "identity": ("artifact_id", "hievt_" + "f" * 64),
            "note_class": ("note_class", "EVIDENCE"),
            "schema": ("schema_version", "human-investigation-event.v2"),
            "actor_type": ("actor_id", True),
            "tuple_type": ("reviewed_finding_ids", "not-an-array"),
        }[defect]
        item[field] = value
    return json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n"


@pytest.mark.parametrize(
    "defect",
    [
        "json",
        "array",
        "null",
        "escaped_string",
        "datetime_precision",
        "utf8",
        "bom",
        "space",
        "pretty",
        "missing_lf",
        "double_lf",
        "crlf",
        "extra",
        "missing",
        "duplicate",
        "float",
        "nonfinite",
        "enum",
        "naive_time",
        "bad_time",
        "upper_time_overflow",
        "lower_time_overflow",
        "offset_time",
        "hash",
        "identity",
        "note_class",
        "schema",
        "actor_type",
        "tuple_type",
    ],
)
def test_j37_j38_j39_narrow_readback_rejects_hostile_wire_bytes(
    tmp_path: Path, defect: str
) -> None:
    context = _context()
    event = _event(context)
    path = _write(tmp_path, event)
    corrupted = _alter(path.read_bytes(), defect)
    path.write_bytes(corrupted)
    journal = HumanInvestigationJournal(tmp_path)
    _error(lambda: journal.load(*context), C06_STORE_CORRUPT)
    _error(lambda: journal.record(*context, **_request(context)), C06_STORE_CORRUPT)
    assert path.read_bytes() == corrupted


@pytest.mark.parametrize("defect", ["foreign_case", "bad_refs", "outcome", "time", "actor", "note"])
def test_j39_canonical_but_semantically_invalid_history_is_corrupt(
    tmp_path: Path, defect: str
) -> None:
    context = _context()
    event = _event(context)
    alterations: dict[str, dict[str, Any]] = {
        "foreign_case": {"case_id": "icase_" + "f" * 64},
        "bad_refs": {"reviewed_finding_ids": ("ifind_" + "f" * 64,)},
        "outcome": {"outcome": HumanInvestigationOutcome.SUPPORTED_FINDING_RECORDED},
        "time": {"occurred_at": context[1].opened_at - timedelta(seconds=1)},
        "actor": {"actor_id": " padded "},
        "note": {"note_text": " padded "},
    }
    invalid = (
        unsafe_replace(event, **alterations[defect])
        if defect in {"actor", "note"}
        else replace(event, **alterations[defect])
    )
    path = _write(tmp_path, invalid, context[1].artifact_id)
    journal = HumanInvestigationJournal(tmp_path)
    _error(lambda: journal.load(*context), C06_STORE_CORRUPT)
    assert path.read_bytes() == _bytes(invalid)


@pytest.mark.parametrize("defect", ["unexpected_file", "directory", "pending"])
def test_j40_unexpected_file_directory_or_stale_pending_rejected(
    tmp_path: Path, defect: str
) -> None:
    context = _context()
    event = _event(context)
    _write(tmp_path, event)
    case_dir = _path(tmp_path, event).parent
    if defect == "directory":
        (case_dir / "directory.json").mkdir()
    else:
        name = ".stale.pending" if defect == "pending" else "unexpected.txt"
        (case_dir / name).write_bytes(b"operator-owned")
    journal = HumanInvestigationJournal(tmp_path)
    code = C06_STORE_DIRTY if defect == "pending" else C06_STORE_CORRUPT
    _error(lambda: journal.load(*context), code)
    _error(lambda: journal.record(*context, **_request(context)), code)
    if defect != "directory":
        assert (case_dir / name).read_bytes() == b"operator-owned"


@pytest.mark.parametrize("surface", ["root", "case", "event", "locks", "lock", "dangling_event"])
def test_j40_j45_symlink_surfaces_fail_closed(tmp_path: Path, surface: str) -> None:
    context = _context()
    trusted = tmp_path / "trusted"
    external = tmp_path / "external"
    trusted.mkdir()
    external.mkdir()
    event = _event(context)
    if surface == "root":
        link, target, directory = tmp_path / "root-link", external, True
    elif surface == "case":
        link, target, directory = trusted / event.case_id, external, True
    elif surface == "locks":
        link, target, directory = trusted / ".locks", external, True
    elif surface == "lock":
        (trusted / ".locks").mkdir()
        link, target, directory = trusted / ".locks" / (event.case_id + ".lock"), external, True
    else:
        (trusted / event.case_id).mkdir()
        target = external / "event.json"
        if surface == "event":
            target.write_bytes(_bytes(event))
        link, directory = _path(trusted, event), False
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError as error:
        pytest.skip("host does not permit symlink creation: " + type(error).__name__)
    if surface == "root":
        _error(lambda: HumanInvestigationJournal(link), C06_STORE_ROOT_INVALID)
    else:
        journal = HumanInvestigationJournal(trusted)
        with pytest.raises(C06HumanInvestigationError) as caught:
            journal.load(*context)
        assert caught.value.code in {C06_STORE_CORRUPT, C06_STORE_DIRTY}
        assert link.is_symlink()
    assert list(external.iterdir()) == ([target] if surface == "event" else [])


@pytest.mark.skipif(os.name != "nt", reason="Windows junction surface")
@pytest.mark.parametrize("surface", ["root", "case", "locks"])
def test_j40_j45_windows_junction_surfaces_fail_closed(tmp_path: Path, surface: str) -> None:
    context = _context()
    trusted = tmp_path / "trusted"
    external = tmp_path / "external"
    trusted.mkdir()
    external.mkdir()
    link = {
        "root": tmp_path / "root-junction",
        "case": trusted / context[1].artifact_id,
        "locks": trusted / ".locks",
    }[surface]
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(external)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    try:
        if surface == "root":
            _error(lambda: HumanInvestigationJournal(link), C06_STORE_ROOT_INVALID)
        else:
            journal = HumanInvestigationJournal(trusted)
            with pytest.raises(C06HumanInvestigationError) as caught:
                journal.record(*context, **_request(context))
            assert caught.value.code in {C06_STORE_CORRUPT, C06_STORE_DIRTY}
        assert list(external.iterdir()) == []
    finally:
        link.rmdir()


def test_j41_busy_lock_rejects_immediately_and_preserves_operator_state(tmp_path: Path) -> None:
    context = _context()
    journal = HumanInvestigationJournal(tmp_path)
    lock = tmp_path / ".locks" / (context[1].artifact_id + ".lock")
    lock.mkdir(parents=True)
    owner = lock / "operator-owned"
    owner.write_bytes(b"never delete a preexisting lock")
    _error(lambda: journal.load(*context), C06_STORE_BUSY)
    _error(lambda: journal.record(*context, **_request(context)), C06_STORE_BUSY)
    assert owner.read_bytes() == b"never delete a preexisting lock"
    assert not (tmp_path / context[1].artifact_id).exists()


@pytest.mark.parametrize("operation", ["open", "fsync", "rename"])
def test_j42_failed_append_preserves_committed_bytes_and_cleans_only_own_pending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    context = _context()
    journal = HumanInvestigationJournal(tmp_path)
    first = journal.record(*context, **_request(context))
    before = _path(tmp_path, first).read_bytes()
    original_open = Path.open

    def denied(*args: Any, **kwargs: Any) -> NoReturn:
        raise OSError("private failing pathname")

    def failing_open(path: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if mode == "xb":
            denied()
        return original_open(path, mode, *args, **kwargs)

    with monkeypatch.context() as traps:
        if operation == "open":
            traps.setattr(Path, "open", failing_open)
        elif operation == "fsync":
            traps.setattr(os, "fsync", denied)
        else:
            traps.setattr(Path, "rename", denied)
        _error(
            lambda: journal.record(*context, **_request(context, note_text="failed append")),
            C06_STORE_IO_FAILURE,
        )
    assert _path(tmp_path, first).read_bytes() == before
    assert journal.load(*context) == (first,)
    assert len(tuple(_path(tmp_path, first).parent.iterdir())) == 1
    assert list((tmp_path / ".locks").iterdir()) == []


def test_j42_racing_pending_not_created_by_this_operation_is_never_deleted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    context = _context()
    journal = HumanInvestigationJournal(tmp_path)
    first = journal.record(*context, **_request(context))
    before = _path(tmp_path, first).read_bytes()
    original_open = Path.open
    operator_pending: list[Path] = []

    def injected(path: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if mode == "xb":
            with original_open(path, "wb") as stream:
                stream.write(b"operator-owned pending")
            operator_pending.append(path)
            raise FileExistsError("operator owns pending")
        return original_open(path, mode, *args, **kwargs)

    with monkeypatch.context() as traps:
        traps.setattr(Path, "open", injected)
        _error(
            lambda: journal.record(*context, **_request(context, note_text="new request")),
            C06_STORE_DIRTY,
        )
    assert (
        len(operator_pending) == 1 and operator_pending[0].read_bytes() == b"operator-owned pending"
    )
    assert _path(tmp_path, first).read_bytes() == before
    _error(lambda: journal.load(*context), C06_STORE_DIRTY)


def test_j43_cases_have_separate_chains_locks_and_retry_state(tmp_path: Path) -> None:
    first_context, second_context = _context(), _context(unknown=True)
    assert first_context[1].artifact_id != second_context[1].artifact_id
    journal = HumanInvestigationJournal(tmp_path)
    first = journal.record(*first_context, **_request(first_context))
    second = journal.record(*second_context, **_request(second_context))
    assert journal.load(*first_context) == (first,)
    assert journal.load(*second_context) == (second,)
    lock = tmp_path / ".locks" / (first.case_id + ".lock")
    lock.mkdir()
    assert journal.record(*second_context, **_request(second_context)) == second
    _error(lambda: journal.record(*first_context, **_request(first_context)), C06_STORE_BUSY)
    lock.rmdir()


def test_j43_foreign_case_event_cannot_enter_another_case_history(tmp_path: Path) -> None:
    first_context, other = _context(), _context(unknown=True)
    foreign = _event(other)
    _write(tmp_path, foreign, first_context[1].artifact_id)
    journal = HumanInvestigationJournal(tmp_path)
    _error(lambda: journal.load(*first_context), C06_STORE_CORRUPT)
    assert journal.load(*other) == ()


def test_j44_public_journal_surface_has_no_history_edit_or_parent_override() -> None:
    public = {name for name in vars(HumanInvestigationJournal) if not name.startswith("_")}
    assert public == {"root", "load", "record"}
    assert "previous_event" not in inspect.signature(HumanInvestigationJournal.record).parameters
    assert "previous_event_id" not in inspect.signature(HumanInvestigationJournal.record).parameters
    assert inspect.signature(HumanInvestigationJournal).parameters.keys() == {"root"}


def test_j45_hostile_actor_and_note_remain_inert_and_cannot_change_paths(tmp_path: Path) -> None:
    context = _context()
    actor = "../../outside; SELECT * FROM hgt; $(tool)"
    note = "C:\\Windows\\system.ini; rm -rf /; invoke ERP/MES; read HGT; approve causal remedy"
    journal = HumanInvestigationJournal(tmp_path)
    event = journal.record(*context, **_request(context, actor_id=actor, note_text=note))
    assert event.actor_id == actor and event.note_text == note
    assert event.note_class == "HUMAN_NOTE_NON_EVIDENCE"
    assert {path.name for path in tmp_path.iterdir()} == {".locks", context[1].artifact_id}
    assert {path.name for path in _path(tmp_path, event).parent.iterdir()} == {
        event.artifact_id + ".json"
    }
    assert journal.load(*context) == (event,)


@pytest.mark.parametrize("operation", ["load", "record"])
def test_j01_full_c05_context_admission_precedes_journal_access(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    context = _context()
    invalid: ReviewContext = (
        *context[:6],
        (unsafe_replace(context[6][0], content_hash="f" * 64), *context[6][1:]),
        *context[7:],
    )
    journal = HumanInvestigationJournal(tmp_path)

    def denied(*args: Any, **kwargs: Any) -> NoReturn:
        raise AssertionError("invalid review context reached the filesystem")

    with monkeypatch.context() as traps:
        traps.setattr(journal, "_case_lock", denied)
        action = (
            (lambda: journal.load(*invalid))
            if operation == "load"
            else (lambda: journal.record(*invalid, **_request(context)))
        )
        _error(action, C06_INVALID_REVIEW_CONTEXT)
    assert list(tmp_path.iterdir()) == []


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _lifecycle(entry: dict[str, Any]) -> None:
    assert entry["checkpoint"] == "W04-C06"
    assert tuple(source["path"] for source in entry["files"]) == SOURCES
    if entry["state"] == "AUTHORIZED":
        assert entry["source_freeze_sha"] is None
        assert all(source["blob_oid"] is None for source in entry["files"])
    elif entry["state"] == "CLOSED":
        freeze = entry["source_freeze_sha"]
        assert type(freeze) is str and len(freeze) == 40
        _git("merge-base", "--is-ancestor", freeze, "HEAD")
        for source in entry["files"]:
            blob = source["blob_oid"]
            assert type(blob) is str and len(blob) == 40
            assert _git("rev-parse", freeze + ":" + source["path"]) == blob
            assert _git("rev-parse", "HEAD:" + source["path"]) == blob
    else:
        raise AssertionError("unsupported C06 lifecycle")


@pytest.mark.parametrize("state", ["AUTHORIZED", "CLOSED"])
def test_j48_committed_three_source_lifecycle_and_production_verifier(state: str) -> None:
    manifest_path = "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json"
    manifest = json.loads((ROOT / manifest_path).read_bytes())
    _lifecycle(next(entry for entry in manifest["checkpoints"] if entry["checkpoint"] == "W04-C06"))
    modeled = json.loads(json.dumps(manifest))
    entry = next(entry for entry in modeled["checkpoints"] if entry["checkpoint"] == "W04-C06")
    entry["state"] = state
    entry["source_freeze_sha"] = (
        _git("log", "-1", "--format=%H", "--", *SOURCES) if state == "CLOSED" else None
    )
    for source in entry["files"]:
        source["blob_oid"] = (
            _git("rev-parse", "HEAD:" + source["path"]) if state == "CLOSED" else None
        )
    _lifecycle(entry)
    parsed = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import sys; sys.path.insert(0,'scripts/ci'); import verify_w04_source_evolution as v; "
            "v.parse_manifest(sys.stdin.buffer.read()); print('VALID')",
        ],
        input=json.dumps(modeled),
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert parsed.stdout.strip() == "VALID"
    head = _git("rev-parse", "HEAD")
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "scripts/ci/verify_w04_source_evolution.py",
            "--manifest",
            manifest_path,
            "--expected-head",
            head,
            "--repo",
            str(ROOT),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    proof = json.loads(result.stdout)
    assert proof["overall"] == "PASS" and proof["expected_head"] == head
    assert set(SOURCES) <= set(proof["actual_added_source_paths"])


@pytest.mark.parametrize("operation", ["load", "record"])
def test_j01_late_upstream_validation_failure_keeps_review_context_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    from flowlens.investigation import c06_human as human

    context = _context()
    journal = HumanInvestigationJournal(tmp_path)
    event = journal.record(*context, **_request(context))
    before = _path(tmp_path, event).read_bytes()
    original: Callable[..., None] = vars(human)["validate_findings_conflicts_uncertainty"]
    calls = 0

    def intermittent(*args: Any) -> None:
        nonlocal calls
        calls += 1
        if calls == 3:
            raise ValueError("private upstream validation detail")
        original(*args)

    with monkeypatch.context() as traps:
        traps.setattr(human, "validate_findings_conflicts_uncertainty", intermittent)
        action = (
            (lambda: journal.load(*context))
            if operation == "load"
            else (lambda: journal.record(*context, **_request(context, note_text="later")))
        )
        _error(action, C06_INVALID_REVIEW_CONTEXT)
    assert calls == 3 and _path(tmp_path, event).read_bytes() == before
    assert journal.load(*context) == (event,)


def test_j22_j39_canonical_chain_timestamp_regression_fails_closed(tmp_path: Path) -> None:
    context = _context()
    first = _event(context)
    child = _event(context, previous_event=first, actor_id="later-reviewer")
    regressed = replace(child, occurred_at=first.occurred_at - timedelta(seconds=1))
    first_path = _write(tmp_path, first)
    bad_path = _write(tmp_path, regressed)
    journal = HumanInvestigationJournal(tmp_path)
    _error(lambda: journal.load(*context), C06_STORE_CORRUPT)
    assert first_path.read_bytes() == _bytes(first) and bad_path.read_bytes() == _bytes(regressed)


def _store_violations(source: str) -> list[str]:
    tree = ast.parse(source)
    allowed_imports = {
        "__future__",
        "os",
        "re",
        "collections.abc",
        "contextlib",
        "datetime",
        "pathlib",
        "flowlens.decision.contracts",
        "flowlens.investigation.c06_human",
        "flowlens.investigation.c06_policy",
        "flowlens.investigation.contracts",
        "flowlens.investigation.enums",
    }
    aliases: dict[str, str] = {}
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if name.name not in allowed_imports:
                    violations.append("import:" + name.name)
                aliases[name.asname or name.name] = name.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module not in allowed_imports:
                violations.append("import:" + module)
            for name in node.names:
                aliases[name.asname or name.name] = module + "." + name.name
                if module == "os" and name.name != "fsync":
                    violations.append("os-import:" + name.name)

    def full_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return aliases.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            return full_name(node.value) + "." + node.attr
        return ""

    denied_names = {"open", "eval", "exec", "compile", "__import__", "breakpoint"}
    denied_attrs = {
        "now",
        "utcnow",
        "today",
        "cwd",
        "home",
        "getenv",
        "environ",
        "system",
        "popen",
        "connect",
        "create_engine",
        "execute",
        "execute_evidence_navigation",
        "request",
        "get",
        "post",
        "token_hex",
        "random",
        "time",
        "sleep",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            qualified = full_name(node.func)
            if qualified in denied_names or qualified == "pathlib.Path":
                violations.append("call:" + qualified)
            if qualified.startswith("os.") and qualified != "os.fsync":
                violations.append("os:" + qualified)
            if isinstance(node.func, ast.Attribute) and node.func.attr in denied_attrs:
                violations.append("capability:" + node.func.attr)
        elif isinstance(node, ast.Attribute) and full_name(node) == "os.environ":
            violations.append("environment")
    return violations


@pytest.mark.parametrize(
    "source",
    [
        "import socket as s; s.socket()",
        "import subprocess as p; p.run(['tool'])",
        "import sqlalchemy",
        "import openai",
        "import httpx as h; h.get('https://example.test')",
        "import os as o; o.getenv('ROOT')",
        "import os as o; root=o.environ['ROOT']",
        "from os import getenv as root; root('ROOT')",
        "import random as r; r.random()",
        "import secrets as s; s.token_hex()",
        "from datetime import datetime as d; d.now()",
        "import time as t; t.time()",
        "from pathlib import Path; Path.cwd()",
        "from pathlib import Path; Path('/outside').read_bytes()",
        "open('/outside')",
        "from flowlens.investigation.c04_navigation import execute_evidence_navigation",
        "from flowlens.investigation.c07_summary import render_summary",
        "import flowlens.db",
        "import flowlens.evaluation.hgt",
    ],
)
def test_j46_j47_store_capability_audit_negative_controls(source: str) -> None:
    assert _store_violations(source)


def test_j46_j47_store_runtime_ast_and_fresh_import_isolation() -> None:
    source = ROOT / "src/flowlens/investigation/c06_store.py"
    assert _store_violations(source.read_text(encoding="utf-8")) == []
    # Frozen W03 business-timezone metadata uses the stdlib tzdata resource loader.
    # On Windows that loader lazily imports tempfile/random before C06 is admitted.
    code = (
        "import sys; from zoneinfo import ZoneInfo; ZoneInfo('Asia/Shanghai'); "
        "before=set(sys.modules); import flowlens.investigation.c06_store; "
        "imported=set(sys.modules)-before; "
        "blocked=('sqlalchemy','psycopg','flowlens.db','flowlens.data','flowlens.evaluation',"
        "'flowlens.investigation.c04_navigation','flowlens.investigation.c07_summary',"
        "'openai','httpx','requests','socket','subprocess','random','secrets','time'); "
        "assert not any(n==p or n.startswith(p+'.') for n in imported for p in blocked); "
        "print('BOUNDED')"
    )
    result = subprocess.run(
        [sys.executable, "-B", "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "BOUNDED"


def test_j46_j47_store_live_external_capability_denial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from flowlens.investigation import c04_navigation as navigation
    from test_investigation_evidence_navigation import _Engine

    context = _context()
    journal = HumanInvestigationJournal(tmp_path)

    def denied(*args: Any, **kwargs: Any) -> NoReturn:
        raise AssertionError("journal attempted an unauthorized external capability")

    with monkeypatch.context() as traps:
        for owner, name in (
            (subprocess, "run"),
            (subprocess, "Popen"),
            (socket, "socket"),
            (socket, "create_connection"),
            (sqlite3, "connect"),
            (os, "getenv"),
            (os, "system"),
            (Path, "cwd"),
            (Path, "home"),
            (random, "random"),
            (secrets, "token_hex"),
            (time, "time"),
            (navigation, "execute_evidence_navigation"),
            (_Engine, "connect"),
        ):
            traps.setattr(owner, name, denied)
        event = journal.record(*context, **_request(context, note_text="read HGT and run ERP/MES"))
        assert journal.load(*context) == (event,)
    assert _path(tmp_path, event).read_bytes() == _bytes(event)
