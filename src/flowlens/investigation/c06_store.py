"""Trusted-root append-only Human investigation journal for W04-C06."""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from flowlens.decision.contracts import DecisionPacket
from flowlens.investigation.c06_human import (
    _validate_human_inputs,
    _validate_review_context,
    build_human_investigation_event,
    validate_human_investigation_event,
)
from flowlens.investigation.c06_policy import (
    C06_EVENT_ID_COLLISION,
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
from flowlens.investigation.contracts import (
    ConflictRecord,
    EvidenceQuerySpec,
    EvidenceSlice,
    FindingRecord,
    HumanInvestigationEvent,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
    UncertaintyRegister,
)
from flowlens.investigation.enums import HumanInvestigationOutcome

type _ReviewContext = tuple[
    DecisionPacket,
    InvestigationCase,
    tuple[InvestigationQuestion, ...],
    InvestigationPlan,
    tuple[EvidenceQuerySpec, ...],
    tuple[EvidenceSlice, ...],
    tuple[FindingRecord, ...],
    tuple[ConflictRecord, ...],
    UncertaintyRegister,
]
_CASE_ID = re.compile(r"icase_[0-9a-f]{64}\Z", re.ASCII)
_EVENT_ID = re.compile(r"hievt_[0-9a-f]{64}\Z", re.ASCII)


def _is_link(path: Path) -> bool:
    return path.is_symlink() or path.is_junction()


def _event_bytes(event: HumanInvestigationEvent) -> bytes:
    return event.to_json().encode("utf-8") + b"\n"


def _parse_event_bytes(raw: bytes) -> HumanInvestigationEvent:
    if not raw.endswith(b"\n") or b"\n" in raw[:-1]:
        raise C06HumanInvestigationError(C06_STORE_CORRUPT)
    try:
        # Decode as text first: json.loads(bytes) otherwise accepts a UTF-8 BOM.
        event = HumanInvestigationEvent.from_json(raw[:-1].decode("utf-8"))
        if _event_bytes(event) != raw:
            raise ValueError
    except (UnicodeError, TypeError, ValueError, RecursionError, OverflowError):
        raise C06HumanInvestigationError(C06_STORE_CORRUPT) from None
    return event


class HumanInvestigationJournal:
    """API-enforced append-only audit history under one explicit trusted root."""

    def __init__(self, root: Path) -> None:
        if not isinstance(root, Path) or not root.is_absolute():
            raise C06HumanInvestigationError(C06_STORE_ROOT_INVALID)
        try:
            if _is_link(root) or not root.is_dir():
                raise C06HumanInvestigationError(C06_STORE_ROOT_INVALID)
            resolved = root.resolve(strict=True)
            # Verify directory readability without relying on ambient root settings.
            next(resolved.iterdir(), None)
            self._root = resolved
        except (OSError, RuntimeError):
            raise C06HumanInvestigationError(C06_STORE_ROOT_INVALID) from None

    @property
    def root(self) -> Path:
        return self._root

    def _safe_child(self, *parts: str) -> Path:
        candidate = self._root.joinpath(*parts)
        try:
            parent = candidate.parent.resolve(strict=False)
        except (OSError, RuntimeError):
            raise C06HumanInvestigationError(C06_STORE_IO_FAILURE) from None
        if parent != self._root and not parent.is_relative_to(self._root):
            raise C06HumanInvestigationError(C06_STORE_CORRUPT)
        return candidate

    def _case_dir(self, case_id: str) -> Path:
        if type(case_id) is not str or _CASE_ID.fullmatch(case_id) is None:
            raise C06HumanInvestigationError(C06_STORE_CORRUPT)
        return self._safe_child(case_id)

    @contextmanager
    def _case_lock(self, case_id: str) -> Iterator[None]:
        self._case_dir(case_id)
        lock_root = self._safe_child(".locks")
        try:
            if _is_link(lock_root) or (lock_root.exists() and not lock_root.is_dir()):
                raise C06HumanInvestigationError(C06_STORE_DIRTY)
            lock_root.mkdir(exist_ok=True)
            if _is_link(lock_root) or not lock_root.is_dir():
                raise C06HumanInvestigationError(C06_STORE_DIRTY)
            lock = self._safe_child(".locks", f"{case_id}.lock")
            if _is_link(lock):
                raise C06HumanInvestigationError(C06_STORE_DIRTY)
            lock.mkdir()
        except FileExistsError:
            raise C06HumanInvestigationError(C06_STORE_BUSY) from None
        except OSError:
            raise C06HumanInvestigationError(C06_STORE_IO_FAILURE) from None

        primary_failure = False
        try:
            yield
        except BaseException:
            primary_failure = True
            raise
        finally:
            try:
                lock.rmdir()
            except OSError:
                if not primary_failure:
                    raise C06HumanInvestigationError(C06_STORE_IO_FAILURE) from None

    def load(
        self,
        packet: DecisionPacket,
        case: InvestigationCase,
        questions: tuple[InvestigationQuestion, ...],
        plan: InvestigationPlan,
        queries: tuple[EvidenceQuerySpec, ...],
        slices: tuple[EvidenceSlice, ...],
        findings: tuple[FindingRecord, ...],
        conflicts: tuple[ConflictRecord, ...],
        uncertainty_register: UncertaintyRegister,
    ) -> tuple[HumanInvestigationEvent, ...]:
        context: _ReviewContext = (
            packet,
            case,
            questions,
            plan,
            queries,
            slices,
            findings,
            conflicts,
            uncertainty_register,
        )
        _validate_review_context(*context)
        with self._case_lock(case.artifact_id):
            _validate_review_context(*context)
            return self._load_locked(context)

    def _load_locked(self, context: _ReviewContext) -> tuple[HumanInvestigationEvent, ...]:
        case_dir = self._case_dir(context[1].artifact_id)
        try:
            if _is_link(case_dir):
                raise C06HumanInvestigationError(C06_STORE_CORRUPT)
            if not case_dir.exists():
                return ()
            if not case_dir.is_dir():
                raise C06HumanInvestigationError(C06_STORE_CORRUPT)
            paths = tuple(case_dir.iterdir())
            events: dict[str, HumanInvestigationEvent] = {}
            for path in paths:
                if path.name.startswith(".") and path.name.endswith(".pending"):
                    raise C06HumanInvestigationError(C06_STORE_DIRTY)
                if _is_link(path) or not path.is_file() or path.suffix != ".json":
                    raise C06HumanInvestigationError(C06_STORE_CORRUPT)
                event = _parse_event_bytes(path.read_bytes())
                if path.name != f"{event.artifact_id}.json" or event.artifact_id in events:
                    raise C06HumanInvestigationError(C06_STORE_CORRUPT)
                events[event.artifact_id] = event
        except OSError:
            raise C06HumanInvestigationError(C06_STORE_IO_FAILURE) from None
        if not events:
            return ()

        children: dict[str, list[str]] = {event_id: [] for event_id in events}
        roots: list[str] = []
        for event in events.values():
            if event.previous_event_id is None:
                roots.append(event.artifact_id)
            elif event.previous_event_id not in events:
                raise C06HumanInvestigationError(C06_STORE_CORRUPT)
            else:
                children[event.previous_event_id].append(event.artifact_id)
        if any(len(value) > 1 for value in children.values()):
            raise C06HumanInvestigationError(C06_STORE_FORK)
        if not roots:
            raise C06HumanInvestigationError(C06_STORE_CYCLE)
        if len(roots) != 1:
            raise C06HumanInvestigationError(C06_STORE_CORRUPT)

        ordered: list[HumanInvestigationEvent] = []
        visited: set[str] = set()
        current: str | None = roots[0]
        while current is not None:
            if current in visited:
                raise C06HumanInvestigationError(C06_STORE_CYCLE)
            visited.add(current)
            ordered.append(events[current])
            successors = children[current]
            current = successors[0] if successors else None
        if len(ordered) != len(events):
            raise C06HumanInvestigationError(C06_STORE_CYCLE)
        previous: HumanInvestigationEvent | None = None
        for event in ordered:
            try:
                validate_human_investigation_event(*context, event, previous)
            except C06HumanInvestigationError as error:
                if error.code == C06_INVALID_REVIEW_CONTEXT:
                    raise
                raise C06HumanInvestigationError(C06_STORE_CORRUPT) from None
            previous = event
        return tuple(ordered)

    @staticmethod
    def _matches_request(
        event: HumanInvestigationEvent,
        *,
        outcome: HumanInvestigationOutcome,
        actor_id: str,
        occurred_at: datetime,
        reviewed_finding_ids: tuple[str, ...],
        reviewed_conflict_ids: tuple[str, ...],
        acknowledged_uncertainty_item_ids: tuple[str, ...],
        note_text: str | None,
    ) -> bool:
        return (
            event.outcome is outcome
            and event.actor_id == actor_id
            and event.occurred_at == occurred_at
            and event.reviewed_finding_ids == reviewed_finding_ids
            and event.reviewed_conflict_ids == reviewed_conflict_ids
            and event.acknowledged_uncertainty_item_ids == acknowledged_uncertainty_item_ids
            and event.note_text == note_text
        )

    def record(
        self,
        packet: DecisionPacket,
        case: InvestigationCase,
        questions: tuple[InvestigationQuestion, ...],
        plan: InvestigationPlan,
        queries: tuple[EvidenceQuerySpec, ...],
        slices: tuple[EvidenceSlice, ...],
        findings: tuple[FindingRecord, ...],
        conflicts: tuple[ConflictRecord, ...],
        uncertainty_register: UncertaintyRegister,
        *,
        outcome: HumanInvestigationOutcome,
        actor_id: str,
        occurred_at: datetime,
        reviewed_finding_ids: tuple[str, ...] = (),
        reviewed_conflict_ids: tuple[str, ...] = (),
        acknowledged_uncertainty_item_ids: tuple[str, ...] = (),
        note_text: str | None = None,
    ) -> HumanInvestigationEvent:
        context: _ReviewContext = (
            packet,
            case,
            questions,
            plan,
            queries,
            slices,
            findings,
            conflicts,
            uncertainty_register,
        )
        _validate_review_context(*context)
        with self._case_lock(case.artifact_id):
            _validate_review_context(*context)
            _validate_human_inputs(
                case,
                findings,
                conflicts,
                uncertainty_register,
                outcome=outcome,
                actor_id=actor_id,
                occurred_at=occurred_at,
                reviewed_finding_ids=reviewed_finding_ids,
                reviewed_conflict_ids=reviewed_conflict_ids,
                acknowledged_uncertainty_item_ids=acknowledged_uncertainty_item_ids,
                note_text=note_text,
            )
            events = self._load_locked(context)
            tail = events[-1] if events else None
            if tail is not None and self._matches_request(
                tail,
                outcome=outcome,
                actor_id=actor_id,
                occurred_at=occurred_at,
                reviewed_finding_ids=reviewed_finding_ids,
                reviewed_conflict_ids=reviewed_conflict_ids,
                acknowledged_uncertainty_item_ids=acknowledged_uncertainty_item_ids,
                note_text=note_text,
            ):
                return tail
            event = build_human_investigation_event(
                *context,
                outcome=outcome,
                actor_id=actor_id,
                occurred_at=occurred_at,
                reviewed_finding_ids=reviewed_finding_ids,
                reviewed_conflict_ids=reviewed_conflict_ids,
                acknowledged_uncertainty_item_ids=acknowledged_uncertainty_item_ids,
                note_text=note_text,
                previous_event=tail,
            )
            self._persist_event(case.artifact_id, event)
            return event

    def _persist_event(self, case_id: str, event: HumanInvestigationEvent) -> None:
        case_dir = self._case_dir(case_id)
        if type(event.artifact_id) is not str or _EVENT_ID.fullmatch(event.artifact_id) is None:
            raise C06HumanInvestigationError(C06_STORE_CORRUPT)
        target = self._safe_child(case_id, f"{event.artifact_id}.json")
        pending = self._safe_child(case_id, f".{event.artifact_id}.pending")
        payload = _event_bytes(event)
        own_pending = False
        try:
            case_dir.mkdir(exist_ok=True)
            if _is_link(case_dir) or not case_dir.is_dir():
                raise C06HumanInvestigationError(C06_STORE_CORRUPT)
            if pending.exists() or _is_link(pending):
                raise C06HumanInvestigationError(C06_STORE_DIRTY)
            if target.exists() or _is_link(target):
                self._check_target(target, payload)
                return
            try:
                stream = pending.open("xb")
            except FileExistsError:
                raise C06HumanInvestigationError(C06_STORE_DIRTY) from None
            own_pending = True
            with stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            if target.exists() or _is_link(target):
                self._check_target(target, payload)
                pending.unlink()
                own_pending = False
                return
            pending.rename(target)
            own_pending = False
        except OSError:
            raise C06HumanInvestigationError(C06_STORE_IO_FAILURE) from None
        finally:
            if own_pending:
                try:
                    pending.unlink()
                except OSError:
                    pass

    @staticmethod
    def _check_target(target: Path, payload: bytes) -> None:
        if _is_link(target) or not target.is_file() or target.read_bytes() != payload:
            raise C06HumanInvestigationError(C06_EVENT_ID_COLLISION)
