"""Bounded append-only HumanDecisionEvent journal for W03-C06."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

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
from flowlens.decision.c06_validation import (
    validate_c05_packet,
    validate_human_decision_event,
)
from flowlens.decision.contracts import DecisionPacket, HumanDecisionEvent
from flowlens.decision.enums import HumanDecisionType
from flowlens.decision.primitives import ArtifactProvenance, SourceRef, VersionRef
from flowlens.decision.serialization import canonical_json_bytes, canonical_primitive

_EVENT_FIELDS = {
    "accepted_reason_codes",
    "actor_id",
    "comment",
    "decided_at",
    "decision",
    "decision_event_id",
    "investigation_priority",
    "packet_id",
    "previous_event_id",
    "provenance",
    "rejected_reason_codes",
    "run_id",
    "schema_version",
}
_PROVENANCE_FIELDS = {
    "contract_versions",
    "implementation_sha",
    "input_artifact_ids",
    "producer",
    "producer_version",
    "source_refs",
}
_SOURCE_REF_FIELDS = {
    "available_at",
    "observed_at",
    "source_entity",
    "source_field",
    "source_record_id",
}
_VERSION_FIELDS = {"name", "version"}
_CANONICAL_DATETIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z\Z")


def _reject_float(_: str) -> object:
    raise ValueError("float is not canonical C01 data")


def _reject_constant(_: str) -> object:
    raise ValueError("non-finite number is not canonical C01 data")


def _expect_dict(value: object, fields: set[str], label: str) -> dict[str, object]:
    if type(value) is not dict:
        raise ValueError(f"{label} must be an object")
    result = cast(dict[object, object], value)
    if any(type(key) is not str for key in result):
        raise ValueError(f"{label} keys must be strings")
    typed = cast(dict[str, object], result)
    if set(typed) != fields:
        raise ValueError(f"{label} fields do not match the frozen schema")
    return typed


def _expect_str(value: object, label: str) -> str:
    if type(value) is not str:
        raise ValueError(f"{label} must be a string")
    return value


def _expect_optional_str(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _expect_str(value, label)


def _expect_str_tuple(value: object, label: str) -> tuple[str, ...]:
    if type(value) is not list:
        raise ValueError(f"{label} must be an array")
    items = cast(list[object], value)
    if any(type(item) is not str for item in items):
        raise ValueError(f"{label} must contain only strings")
    return tuple(cast(str, item) for item in items)


def _parse_datetime(value: object, label: str) -> datetime:
    rendered = _expect_str(value, label)
    if _CANONICAL_DATETIME.fullmatch(rendered) is None:
        raise ValueError(f"{label} is not a canonical datetime")
    parsed = datetime.strptime(rendered, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
    if canonical_primitive(parsed) != rendered:
        raise ValueError(f"{label} is not a canonical datetime")
    return parsed


def _parse_source_ref(value: object) -> SourceRef:
    item = _expect_dict(value, _SOURCE_REF_FIELDS, "source_ref")
    observed = item["observed_at"]
    return SourceRef(
        source_entity=_expect_str(item["source_entity"], "source_entity"),
        source_record_id=_expect_str(item["source_record_id"], "source_record_id"),
        source_field=_expect_str(item["source_field"], "source_field"),
        observed_at=None if observed is None else _parse_datetime(observed, "observed_at"),
        available_at=_parse_datetime(item["available_at"], "available_at"),
    )


def _parse_version(value: object) -> VersionRef:
    item = _expect_dict(value, _VERSION_FIELDS, "contract_version")
    return VersionRef(
        name=_expect_str(item["name"], "contract name"),
        version=_expect_str(item["version"], "contract version"),
    )


def _parse_provenance(value: object) -> ArtifactProvenance:
    item = _expect_dict(value, _PROVENANCE_FIELDS, "provenance")
    source_refs = item["source_refs"]
    contract_versions = item["contract_versions"]
    if type(source_refs) is not list or type(contract_versions) is not list:
        raise ValueError("provenance collections must be arrays")
    return ArtifactProvenance(
        producer=_expect_str(item["producer"], "producer"),
        producer_version=_expect_str(item["producer_version"], "producer_version"),
        input_artifact_ids=_expect_str_tuple(
            item["input_artifact_ids"], "input_artifact_ids"
        ),
        source_refs=tuple(_parse_source_ref(ref) for ref in cast(list[object], source_refs)),
        contract_versions=tuple(
            _parse_version(ref) for ref in cast(list[object], contract_versions)
        ),
        implementation_sha=_expect_optional_str(
            item["implementation_sha"], "implementation_sha"
        ),
    )


def _parse_event_bytes(raw: bytes) -> HumanDecisionEvent:
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n") or b"\n" in raw[:-1]:
        raise C06Error(C06_STORE_CORRUPT)
    body = raw[:-1]
    try:
        text = body.decode("utf-8")
        parsed: object = json.loads(
            text,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
        item = _expect_dict(parsed, _EVENT_FIELDS, "HumanDecisionEvent")
        decision_text = _expect_str(item["decision"], "decision")
        event = HumanDecisionEvent(
            decision_event_id=_expect_str(item["decision_event_id"], "decision_event_id"),
            schema_version=_expect_str(item["schema_version"], "schema_version"),
            run_id=_expect_str(item["run_id"], "run_id"),
            packet_id=_expect_str(item["packet_id"], "packet_id"),
            decision=HumanDecisionType(decision_text),
            actor_id=_expect_str(item["actor_id"], "actor_id"),
            decided_at=_parse_datetime(item["decided_at"], "decided_at"),
            accepted_reason_codes=_expect_str_tuple(
                item["accepted_reason_codes"], "accepted_reason_codes"
            ),
            rejected_reason_codes=_expect_str_tuple(
                item["rejected_reason_codes"], "rejected_reason_codes"
            ),
            comment=_expect_optional_str(item["comment"], "comment"),
            investigation_priority=_expect_optional_str(
                item["investigation_priority"], "investigation_priority"
            ),
            previous_event_id=_expect_optional_str(
                item["previous_event_id"], "previous_event_id"
            ),
            provenance=_parse_provenance(item["provenance"]),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        if isinstance(error, C06Error):
            raise
        raise C06Error(C06_STORE_CORRUPT) from error
    if canonical_json_bytes(event) + b"\n" != raw:
        raise C06Error(C06_STORE_CORRUPT)
    return event


class HumanDecisionJournal:
    """One trusted-root, API-append-only Human decision audit journal."""

    def __init__(self, root: Path) -> None:
        if not isinstance(root, Path) or not root.is_absolute():
            raise C06Error(C06_STORE_ROOT_INVALID, "BLOCKED_CONTEXT")
        try:
            if not root.exists() or not root.is_dir():
                raise C06Error(C06_STORE_ROOT_INVALID, "BLOCKED_CONTEXT")
            self._root = root.resolve(strict=True)
        except OSError as error:
            raise C06Error(C06_STORE_ROOT_INVALID, "BLOCKED_CONTEXT") from error

    @property
    def root(self) -> Path:
        return self._root

    def _safe_child(self, *parts: str) -> Path:
        candidate = self._root.joinpath(*parts)
        try:
            resolved_parent = candidate.parent.resolve(strict=False)
        except OSError as error:
            raise C06Error(C06_STORE_IO_FAILURE, "BLOCKED_CONTEXT") from error
        if resolved_parent != self._root and not resolved_parent.is_relative_to(self._root):
            raise C06Error(C06_STORE_CORRUPT, "BLOCKED_CONTEXT")
        return candidate

    def _packet_dir(self, packet: DecisionPacket) -> Path:
        return self._safe_child(packet.packet_id)

    def _lock_path(self, packet: DecisionPacket) -> Path:
        return self._safe_child(".locks", f"{packet.packet_id}.lock")

    def _check_lock_state(self, packet: DecisionPacket) -> None:
        lock_root = self._safe_child(".locks")
        try:
            if lock_root.exists() and (not lock_root.is_dir() or lock_root.is_symlink()):
                raise C06Error(C06_STORE_DIRTY, "BLOCKED_CONTEXT")
            lock = self._lock_path(packet)
            if lock.exists():
                if not lock.is_dir() or lock.is_symlink():
                    raise C06Error(C06_STORE_DIRTY, "BLOCKED_CONTEXT")
                raise C06Error(C06_STORE_BUSY, "BLOCKED_CONTEXT")
        except OSError as error:
            raise C06Error(C06_STORE_IO_FAILURE, "BLOCKED_CONTEXT") from error

    @contextmanager
    def _packet_lock(self, packet: DecisionPacket) -> Iterator[None]:
        lock_root = self._safe_child(".locks")
        lock = self._lock_path(packet)
        try:
            if lock_root.exists() and (not lock_root.is_dir() or lock_root.is_symlink()):
                raise C06Error(C06_STORE_DIRTY, "BLOCKED_CONTEXT")
            lock_root.mkdir(exist_ok=True)
            lock.mkdir()
        except FileExistsError as error:
            raise C06Error(C06_STORE_BUSY, "BLOCKED_CONTEXT") from error
        except C06Error:
            raise
        except OSError as error:
            raise C06Error(C06_STORE_IO_FAILURE, "BLOCKED_CONTEXT") from error

        primary_failure = False
        try:
            yield
        except BaseException:
            primary_failure = True
            raise
        finally:
            try:
                lock.rmdir()
            except OSError as error:
                if not primary_failure:
                    raise C06Error(C06_STORE_IO_FAILURE, "BLOCKED_CONTEXT") from error

    def load(self, packet: DecisionPacket) -> tuple[HumanDecisionEvent, ...]:
        validate_c05_packet(packet)
        self._check_lock_state(packet)
        return self._load_locked(packet)

    def _load_locked(self, packet: DecisionPacket) -> tuple[HumanDecisionEvent, ...]:
        packet_dir = self._packet_dir(packet)
        try:
            if not packet_dir.exists():
                return ()
            if not packet_dir.is_dir() or packet_dir.is_symlink():
                raise C06Error(C06_STORE_CORRUPT)
            entries = tuple(packet_dir.iterdir())
        except C06Error:
            raise
        except OSError as error:
            raise C06Error(C06_STORE_IO_FAILURE, "BLOCKED_CONTEXT") from error

        events_by_id: dict[str, HumanDecisionEvent] = {}
        for path in entries:
            if path.name.startswith(".") and path.name.endswith(".pending"):
                raise C06Error(C06_STORE_DIRTY, "BLOCKED_CONTEXT")
            if not path.is_file() or path.is_symlink() or path.suffix != ".json":
                raise C06Error(C06_STORE_CORRUPT)
            try:
                raw = path.read_bytes()
            except OSError as error:
                raise C06Error(C06_STORE_IO_FAILURE, "BLOCKED_CONTEXT") from error
            event = _parse_event_bytes(raw)
            if path.name != f"{event.decision_event_id}.json":
                raise C06Error(C06_STORE_CORRUPT)
            if event.decision_event_id in events_by_id:
                raise C06Error(C06_STORE_CORRUPT)
            events_by_id[event.decision_event_id] = event

        if not events_by_id:
            return ()

        children: dict[str, list[str]] = {event_id: [] for event_id in events_by_id}
        roots: list[str] = []
        for event in events_by_id.values():
            if event.previous_event_id is None:
                roots.append(event.decision_event_id)
            elif event.previous_event_id not in events_by_id:
                raise C06Error(C06_STORE_CORRUPT)
            else:
                children[event.previous_event_id].append(event.decision_event_id)
        if any(len(value) > 1 for value in children.values()):
            raise C06Error(C06_STORE_FORK)

        visited: set[str] = set()
        active: set[str] = set()

        def visit(event_id: str) -> None:
            if event_id in active:
                raise C06Error(C06_STORE_CYCLE)
            if event_id in visited:
                return
            active.add(event_id)
            parent = events_by_id[event_id].previous_event_id
            if parent is not None:
                visit(parent)
            active.remove(event_id)
            visited.add(event_id)

        for event_id in events_by_id:
            visit(event_id)
        if len(roots) != 1:
            raise C06Error(C06_STORE_CORRUPT)

        ordered: list[HumanDecisionEvent] = []
        current_id: str | None = roots[0]
        while current_id is not None:
            ordered.append(events_by_id[current_id])
            successors = children[current_id]
            current_id = successors[0] if successors else None
        if len(ordered) != len(events_by_id):
            raise C06Error(C06_STORE_CYCLE)

        previous: HumanDecisionEvent | None = None
        for event in ordered:
            try:
                validate_human_decision_event(packet, event, previous)
            except C06Error as error:
                if error.code == C06_EVENT_ID_COLLISION:
                    raise
                raise C06Error(C06_STORE_CORRUPT) from error
            previous = event
        return tuple(ordered)

    @staticmethod
    def _matches_request(
        event: HumanDecisionEvent,
        *,
        decision: HumanDecisionType,
        actor_id: str,
        decided_at: datetime,
        accepted_reason_codes: tuple[str, ...],
        rejected_reason_codes: tuple[str, ...],
        comment: str | None,
        investigation_priority: str | None,
    ) -> bool:
        return (
            event.decision is decision
            and event.actor_id == actor_id
            and event.decided_at == decided_at
            and event.accepted_reason_codes == accepted_reason_codes
            and event.rejected_reason_codes == rejected_reason_codes
            and event.comment == comment
            and event.investigation_priority == investigation_priority
        )

    def record(
        self,
        packet: DecisionPacket,
        *,
        decision: HumanDecisionType,
        actor_id: str,
        decided_at: datetime,
        accepted_reason_codes: tuple[str, ...] = (),
        rejected_reason_codes: tuple[str, ...] = (),
        comment: str | None = None,
        investigation_priority: str | None = None,
    ) -> HumanDecisionEvent:
        validate_c05_packet(packet)
        with self._packet_lock(packet):
            events = self._load_locked(packet)
            tail = events[-1] if events else None
            if tail is not None and self._matches_request(
                tail,
                decision=decision,
                actor_id=actor_id,
                decided_at=decided_at,
                accepted_reason_codes=accepted_reason_codes,
                rejected_reason_codes=rejected_reason_codes,
                comment=comment,
                investigation_priority=investigation_priority,
            ):
                return tail
            event = build_human_decision_event(
                packet,
                decision=decision,
                actor_id=actor_id,
                decided_at=decided_at,
                accepted_reason_codes=accepted_reason_codes,
                rejected_reason_codes=rejected_reason_codes,
                comment=comment,
                investigation_priority=investigation_priority,
                previous_event=tail,
            )
            self._persist_event(packet, event)
            return event

    def _persist_event(self, packet: DecisionPacket, event: HumanDecisionEvent) -> None:
        packet_dir = self._packet_dir(packet)
        target = packet_dir / f"{event.decision_event_id}.json"
        pending = packet_dir / f".{event.decision_event_id}.pending"
        payload = canonical_json_bytes(event) + b"\n"
        try:
            packet_dir.mkdir(exist_ok=True)
            if not packet_dir.is_dir() or packet_dir.is_symlink():
                raise C06Error(C06_STORE_CORRUPT)
            if pending.exists():
                raise C06Error(C06_STORE_DIRTY, "BLOCKED_CONTEXT")
            if target.exists():
                if not target.is_file() or target.is_symlink():
                    raise C06Error(C06_EVENT_ID_COLLISION)
                if target.read_bytes() == payload:
                    return
                raise C06Error(C06_EVENT_ID_COLLISION)
            with pending.open("xb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            if target.exists():
                raise C06Error(C06_EVENT_ID_COLLISION)
            pending.rename(target)
        except C06Error:
            if pending.exists():
                try:
                    pending.unlink()
                except OSError:
                    pass
            raise
        except OSError as error:
            if pending.exists():
                try:
                    pending.unlink()
                except OSError:
                    pass
            raise C06Error(C06_STORE_IO_FAILURE, "BLOCKED_CONTEXT") from error
