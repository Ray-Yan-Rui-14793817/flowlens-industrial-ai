"""Append-only journal, narrow readback, corruption and locking tests for W03-C06."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

import pytest

import flowlens.decision.c06_store as c06_store
from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.c06_human import build_human_decision_event
from flowlens.decision.c06_policy import (
    C06_EVENT_ID_COLLISION,
    C06_STORE_BUSY,
    C06_STORE_CORRUPT,
    C06_STORE_CYCLE,
    C06_STORE_DIRTY,
    C06_STORE_FORK,
    C06_STORE_IO_FAILURE,
    C06_STORE_ROOT_INVALID,
    C06Error,
)
from flowlens.decision.c06_store import HumanDecisionJournal
from flowlens.decision.c06_validation import expected_event_provenance
from flowlens.decision.contracts import DecisionPacket, HumanDecisionEvent
from flowlens.decision.enums import HumanDecisionType
from flowlens.decision.serialization import canonical_json_bytes, derive_artifact_id
from test_c05_policy import make_fixture, neutral_records, unsafe_replace
from test_c05_recommendation import supplier_fixture


def _packet() -> DecisionPacket:
    fixture = supplier_fixture()
    recommendation = build_recommendation(*fixture.args())
    return build_decision_packet(*fixture.args(), recommendation=recommendation)


def _other_packet() -> DecisionPacket:
    fixture = make_fixture(neutral_records())
    return build_decision_packet(*fixture.args())


def _event_path(root: Path, event: HumanDecisionEvent) -> Path:
    return root / event.packet_id / f"{event.decision_event_id}.json"


def _write_event(root: Path, event: HumanDecisionEvent) -> Path:
    packet_dir = root / event.packet_id
    packet_dir.mkdir(exist_ok=True)
    path = _event_path(root, event)
    path.write_bytes(canonical_json_bytes(event) + b"\n")
    return path


@pytest.mark.parametrize("kind", ("relative", "missing", "file"))
def test_store_root_must_be_absolute_preexisting_directory(tmp_path: Path, kind: str) -> None:
    if kind == "relative":
        root = Path("relative-c06-root")
    elif kind == "missing":
        root = tmp_path / "missing"
    else:
        root = tmp_path / "root-file"
        root.write_text("not a directory", encoding="utf-8")
    with pytest.raises(C06Error) as caught:
        HumanDecisionJournal(root)
    assert caught.value.code == C06_STORE_ROOT_INVALID


def test_first_event_layout_and_canonical_bytes(tmp_path: Path) -> None:
    packet = _packet()
    journal = HumanDecisionJournal(tmp_path)
    event = journal.record(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="reviewer",
        decided_at=packet.run.as_of_time,
    )
    assert event.previous_event_id is None
    assert _event_path(tmp_path, event).read_bytes() == canonical_json_bytes(event) + b"\n"
    assert tuple(journal.load(packet)) == (event,)
    assert (tmp_path / ".locks").is_dir()
    assert not (tmp_path / ".locks" / f"{packet.packet_id}.lock").exists()


def test_three_event_chain_preserves_historical_bytes(tmp_path: Path) -> None:
    packet = _packet()
    journal = HumanDecisionJournal(tmp_path)
    first = journal.record(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="reviewer",
        decided_at=packet.run.as_of_time,
        comment="first",
    )
    first_bytes = _event_path(tmp_path, first).read_bytes()
    second = journal.record(
        packet,
        decision=HumanDecisionType.ACCEPT,
        actor_id="reviewer",
        decided_at=packet.run.as_of_time + timedelta(seconds=1),
    )
    second_bytes = _event_path(tmp_path, second).read_bytes()
    third = journal.record(
        packet,
        decision=HumanDecisionType.REJECT,
        actor_id="reviewer",
        decided_at=packet.run.as_of_time + timedelta(seconds=2),
    )
    assert tuple(item.decision for item in journal.load(packet)) == (
        HumanDecisionType.DEFER,
        HumanDecisionType.ACCEPT,
        HumanDecisionType.REJECT,
    )
    assert second.previous_event_id == first.decision_event_id
    assert third.previous_event_id == second.decision_event_id
    assert _event_path(tmp_path, first).read_bytes() == first_bytes
    assert _event_path(tmp_path, second).read_bytes() == second_bytes


def test_exact_retry_is_idempotent_and_does_not_rewrite(tmp_path: Path) -> None:
    packet = _packet()
    journal = HumanDecisionJournal(tmp_path)
    kwargs = {
        "decision": HumanDecisionType.ACCEPT,
        "actor_id": "reviewer",
        "decided_at": packet.run.as_of_time,
        "comment": "same explicit request",
    }
    first = journal.record(packet, **kwargs)
    path = _event_path(tmp_path, first)
    before = path.read_bytes()
    second = journal.record(packet, **kwargs)
    assert second == first
    assert path.read_bytes() == before
    assert len(tuple((tmp_path / packet.packet_id).glob("*.json"))) == 1


def test_same_id_different_canonical_bytes_is_hard_collision(tmp_path: Path) -> None:
    packet = _packet()
    journal = HumanDecisionJournal(tmp_path)
    event = journal.record(
        packet,
        decision=HumanDecisionType.ACCEPT,
        actor_id="reviewer",
        decided_at=packet.run.as_of_time,
    )
    attacked = unsafe_replace(
        event,
        provenance=unsafe_replace(event.provenance, producer="forged.c06"),
    )
    path = _event_path(tmp_path, event)
    attacked_bytes = canonical_json_bytes(attacked) + b"\n"
    path.write_bytes(attacked_bytes)
    with pytest.raises(C06Error) as caught:
        journal.record(
            packet,
            decision=HumanDecisionType.ACCEPT,
            actor_id="reviewer",
            decided_at=packet.run.as_of_time,
        )
    assert caught.value.code == C06_EVENT_ID_COLLISION
    assert path.read_bytes() == attacked_bytes


def test_same_and_fresh_process_readback_match_ids_order_and_bytes(tmp_path: Path) -> None:
    packet = _packet()
    journal = HumanDecisionJournal(tmp_path)
    first = journal.record(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="reviewer",
        decided_at=packet.run.as_of_time,
    )
    second = journal.record(
        packet,
        decision=HumanDecisionType.ACCEPT,
        actor_id="reviewer",
        decided_at=packet.run.as_of_time + timedelta(seconds=1),
    )
    local = journal.load(packet)
    digest = hashlib.sha256(b"".join(canonical_json_bytes(item) for item in local)).hexdigest()
    code = """
import hashlib
import sys
from pathlib import Path
sys.path.insert(0, 'tests')
from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.c05_recommendation import build_recommendation
from flowlens.decision.c06_store import HumanDecisionJournal
from flowlens.decision.serialization import canonical_json_bytes
from test_c05_recommendation import supplier_fixture
fixture = supplier_fixture()
recommendation = build_recommendation(*fixture.args())
packet = build_decision_packet(*fixture.args(), recommendation=recommendation)
events = HumanDecisionJournal(Path(sys.argv[1])).load(packet)
print(','.join(item.decision_event_id for item in events))
print(hashlib.sha256(b''.join(canonical_json_bytes(item) for item in events)).hexdigest())
"""
    completed = subprocess.run(
        [sys.executable, "-c", code, str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.splitlines() == [
        f"{first.decision_event_id},{second.decision_event_id}",
        digest,
    ]


def _extra_field(raw: bytes) -> bytes:
    item = json.loads(raw)
    item["unexpected"] = "value"
    return json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _missing_field(raw: bytes) -> bytes:
    item = json.loads(raw)
    del item["actor_id"]
    return json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _float_value(raw: bytes) -> bytes:
    item = json.loads(raw)
    item["comment"] = 1.5
    return json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _naive_datetime(raw: bytes) -> bytes:
    item = json.loads(raw)
    item["decided_at"] = "2026-01-01T00:00:00.000000"
    return json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _noncanonical_datetime(raw: bytes) -> bytes:
    item = json.loads(raw)
    item["decided_at"] = "2026-01-01T08:00:00.000000+08:00"
    return json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _invalid_enum(raw: bytes) -> bytes:
    item = json.loads(raw)
    item["decision"] = "EXECUTE"
    return json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _wrong_schema(raw: bytes) -> bytes:
    item = json.loads(raw)
    item["schema_version"] = "human-decision-event.v2"
    return json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _pretty(raw: bytes) -> bytes:
    return json.dumps(json.loads(raw), indent=2, sort_keys=True).encode() + b"\n"


@pytest.mark.parametrize(
    "transform",
    (
        _extra_field,
        _missing_field,
        _float_value,
        _naive_datetime,
        _noncanonical_datetime,
        _invalid_enum,
        _wrong_schema,
        _pretty,
        lambda raw: raw.rstrip(b"\n"),
        lambda raw: raw + b"\n",
        lambda raw: b"\xef\xbb\xbf" + raw,
        lambda raw: raw[:-1] + b" trailing\n",
        lambda raw: b"\xff\n",
    ),
)
def test_narrow_readback_rejects_malformed_or_noncanonical_bytes(
    tmp_path: Path,
    transform: Callable[[bytes], bytes],
) -> None:
    packet = _packet()
    journal = HumanDecisionJournal(tmp_path)
    event = journal.record(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="reviewer",
        decided_at=packet.run.as_of_time,
    )
    path = _event_path(tmp_path, event)
    attacked = transform(path.read_bytes())
    path.write_bytes(attacked)
    with pytest.raises(C06Error) as caught:
        journal.load(packet)
    assert caught.value.code == C06_STORE_CORRUPT
    assert path.read_bytes() == attacked


def test_wrong_filename_and_unexpected_file_fail_closed(tmp_path: Path) -> None:
    packet = _packet()
    journal = HumanDecisionJournal(tmp_path)
    event = journal.record(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="reviewer",
        decided_at=packet.run.as_of_time,
    )
    original = _event_path(tmp_path, event)
    wrong = original.with_name(f"hdec_{'f' * 64}.json")
    original.rename(wrong)
    with pytest.raises(C06Error) as filename_error:
        journal.load(packet)
    assert filename_error.value.code == C06_STORE_CORRUPT
    wrong.rename(original)
    extra = original.parent / "unexpected.txt"
    extra.write_text("unexpected", encoding="utf-8")
    with pytest.raises(C06Error) as extra_error:
        journal.load(packet)
    assert extra_error.value.code == C06_STORE_CORRUPT


def test_missing_parent_multiple_roots_and_fork_fail_closed(tmp_path: Path) -> None:
    packet = _packet()
    root = build_human_decision_event(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="root",
        decided_at=packet.run.as_of_time,
    )
    child_one = build_human_decision_event(
        packet,
        decision=HumanDecisionType.ACCEPT,
        actor_id="child-one",
        decided_at=packet.run.as_of_time + timedelta(seconds=1),
        previous_event=root,
    )
    child_two = build_human_decision_event(
        packet,
        decision=HumanDecisionType.REJECT,
        actor_id="child-two",
        decided_at=packet.run.as_of_time + timedelta(seconds=1),
        previous_event=root,
    )

    missing_root = tmp_path / "missing-parent"
    missing_root.mkdir()
    _write_event(missing_root, child_one)
    with pytest.raises(C06Error) as missing:
        HumanDecisionJournal(missing_root).load(packet)
    assert missing.value.code == C06_STORE_CORRUPT

    roots_root = tmp_path / "multiple-roots"
    roots_root.mkdir()
    _write_event(roots_root, root)
    second_root = build_human_decision_event(
        packet,
        decision=HumanDecisionType.ACCEPT,
        actor_id="other-root",
        decided_at=packet.run.as_of_time,
    )
    _write_event(roots_root, second_root)
    with pytest.raises(C06Error) as multiple:
        HumanDecisionJournal(roots_root).load(packet)
    assert multiple.value.code == C06_STORE_CORRUPT

    fork_root = tmp_path / "fork"
    fork_root.mkdir()
    for event in (root, child_one, child_two):
        _write_event(fork_root, event)
    before = {path.name: path.read_bytes() for path in (fork_root / packet.packet_id).iterdir()}
    with pytest.raises(C06Error) as fork:
        HumanDecisionJournal(fork_root).load(packet)
    assert fork.value.code == C06_STORE_FORK
    after = {path.name: path.read_bytes() for path in (fork_root / packet.packet_id).iterdir()}
    assert after == before


def test_cycle_detector_fails_closed_without_repair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet = _packet()
    first_id = f"hdec_{'a' * 64}"
    second_id = f"hdec_{'b' * 64}"
    template = build_human_decision_event(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="cycle",
        decided_at=packet.run.as_of_time,
    )
    first = unsafe_replace(template, decision_event_id=first_id, previous_event_id=second_id)
    second = unsafe_replace(template, decision_event_id=second_id, previous_event_id=first_id)
    packet_dir = tmp_path / packet.packet_id
    packet_dir.mkdir()
    (packet_dir / f"{first_id}.json").write_bytes(b"first\n")
    (packet_dir / f"{second_id}.json").write_bytes(b"second\n")

    def fake_parse(raw: bytes) -> HumanDecisionEvent:
        return first if raw == b"first\n" else second

    monkeypatch.setattr(c06_store, "_parse_event_bytes", fake_parse)
    with pytest.raises(C06Error) as caught:
        HumanDecisionJournal(tmp_path).load(packet)
    assert caught.value.code == C06_STORE_CYCLE
    assert (packet_dir / f"{first_id}.json").read_bytes() == b"first\n"
    assert (packet_dir / f"{second_id}.json").read_bytes() == b"second\n"


def test_cross_packet_cross_run_and_time_regression_stores_reject(tmp_path: Path) -> None:
    packet = _packet()
    other = _other_packet()
    event = build_human_decision_event(
        other,
        decision=HumanDecisionType.DEFER,
        actor_id="other",
        decided_at=other.run.as_of_time,
    )
    cross_root = tmp_path / "cross"
    cross_root.mkdir()
    packet_dir = cross_root / packet.packet_id
    packet_dir.mkdir()
    (packet_dir / f"{event.decision_event_id}.json").write_bytes(
        canonical_json_bytes(event) + b"\n"
    )
    with pytest.raises(C06Error) as cross:
        HumanDecisionJournal(cross_root).load(packet)
    assert cross.value.code == C06_STORE_CORRUPT

    time_root = tmp_path / "time"
    time_root.mkdir()
    first = build_human_decision_event(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="first",
        decided_at=packet.run.as_of_time + timedelta(seconds=2),
    )
    identity = {
        "run_id": packet.run.run_id,
        "packet_id": packet.packet_id,
        "decision": HumanDecisionType.ACCEPT,
        "actor_id": "second",
        "decided_at": packet.run.as_of_time + timedelta(seconds=1),
        "accepted_reason_codes": (),
        "rejected_reason_codes": (),
        "comment": None,
        "investigation_priority": None,
        "previous_event_id": first.decision_event_id,
    }
    second = HumanDecisionEvent(
        decision_event_id=derive_artifact_id(
            "human-decision-event", "human-decision-event.v1", identity
        ),
        schema_version="human-decision-event.v1",
        run_id=packet.run.run_id,
        packet_id=packet.packet_id,
        decision=HumanDecisionType.ACCEPT,
        actor_id="second",
        decided_at=packet.run.as_of_time + timedelta(seconds=1),
        accepted_reason_codes=(),
        rejected_reason_codes=(),
        comment=None,
        investigation_priority=None,
        previous_event_id=first.decision_event_id,
        provenance=expected_event_provenance(packet, first),
    )
    _write_event(time_root, first)
    _write_event(time_root, second)
    with pytest.raises(C06Error) as time_error:
        HumanDecisionJournal(time_root).load(packet)
    assert time_error.value.code == C06_STORE_CORRUPT


def test_stale_pending_file_fails_closed(tmp_path: Path) -> None:
    packet = _packet()
    packet_dir = tmp_path / packet.packet_id
    packet_dir.mkdir()
    pending = packet_dir / f".hdec_{'a' * 64}.pending"
    pending.write_bytes(b"stale")
    with pytest.raises(C06Error) as caught:
        HumanDecisionJournal(tmp_path).load(packet)
    assert caught.value.code == C06_STORE_DIRTY
    assert pending.read_bytes() == b"stale"


def test_packet_lock_contention_and_different_packet_independence(tmp_path: Path) -> None:
    packet = _packet()
    other = _other_packet()
    lock_root = tmp_path / ".locks"
    lock_root.mkdir()
    held = lock_root / f"{packet.packet_id}.lock"
    held.mkdir()
    journal = HumanDecisionJournal(tmp_path)
    with pytest.raises(C06Error) as caught:
        journal.record(
            packet,
            decision=HumanDecisionType.DEFER,
            actor_id="reviewer",
            decided_at=packet.run.as_of_time,
        )
    assert caught.value.code == C06_STORE_BUSY
    other_event = journal.record(
        other,
        decision=HumanDecisionType.DEFER,
        actor_id="reviewer",
        decided_at=other.run.as_of_time,
    )
    assert other_event.packet_id == other.packet_id
    assert held.is_dir()


def test_audit_text_cannot_choose_paths_or_escape_root(tmp_path: Path) -> None:
    packet = _packet()
    journal = HumanDecisionJournal(tmp_path)
    event = journal.record(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="../../actor/path",
        decided_at=packet.run.as_of_time,
        comment="../../comment/path",
        investigation_priority="../../priority/path",
    )
    assert _event_path(tmp_path, event).is_file()
    assert {path.name for path in tmp_path.iterdir()} == {".locks", packet.packet_id}
    assert tuple(journal.load(packet)) == (event,)


def test_write_failure_preserves_history_and_cleans_owned_pending(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet = _packet()
    journal = HumanDecisionJournal(tmp_path)
    first = journal.record(
        packet,
        decision=HumanDecisionType.DEFER,
        actor_id="reviewer",
        decided_at=packet.run.as_of_time,
    )
    first_path = _event_path(tmp_path, first)
    before = first_path.read_bytes()

    def denied_rename(self: Path, target: Path) -> Path:
        raise OSError("simulated rename failure")

    monkeypatch.setattr(Path, "rename", denied_rename)
    with pytest.raises(C06Error) as caught:
        journal.record(
            packet,
            decision=HumanDecisionType.ACCEPT,
            actor_id="reviewer",
            decided_at=packet.run.as_of_time + timedelta(seconds=1),
        )
    assert caught.value.code == C06_STORE_IO_FAILURE
    assert first_path.read_bytes() == before
    assert not tuple((tmp_path / packet.packet_id).glob("*.pending"))
