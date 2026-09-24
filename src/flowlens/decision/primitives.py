"""Immutable support values and structural validators for C01 contracts."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from types import UnionType
from typing import Any, TypeAliasType, get_args, get_origin, get_type_hints

from flowlens.decision.enums import ClaimType, UncertaintyStatus
from flowlens.decision.serialization import canonical_primitive

type ScalarValue = None | bool | int | str | Decimal | date | datetime

_HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
_GIT_OID_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


def validate_aware_datetime(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")


def validate_sha256(value: str, label: str) -> None:
    if _HASH_RE.fullmatch(value) is None:
        raise ValueError(f"{label} must be a lowercase SHA-256 hex digest")


def validate_git_oid(value: str, label: str) -> None:
    if _GIT_OID_RE.fullmatch(value) is None:
        raise ValueError(f"{label} must be a 40- or 64-character lowercase Git object ID")


def validate_artifact_id(value: str, prefix: str, expected: str) -> None:
    if not value.startswith(prefix) or _HASH_RE.fullmatch(value[len(prefix) :]) is None:
        raise ValueError(f"artifact ID must be {prefix} plus a lowercase SHA-256 digest")
    if value != expected:
        raise ValueError("artifact ID does not match canonical identity")


def validate_sorted_unique[T](values: tuple[T, ...], key: Callable[[T], Any], label: str) -> None:
    keys = tuple(key(item) for item in values)
    if keys != tuple(sorted(set(keys))):
        raise ValueError(f"{label} must be sorted and unique")


def _matches(value: object, expected: object) -> bool:
    if isinstance(expected, TypeAliasType):
        return _matches(value, expected.__value__)
    origin = get_origin(expected)
    if origin is UnionType:
        return any(_matches(value, part) for part in get_args(expected))
    if origin is tuple:
        if not isinstance(value, tuple):
            return False
        args = get_args(expected)
        return (
            len(args) == 2
            and args[1] is Ellipsis
            and all(_matches(item, args[0]) for item in value)
        )
    if expected is type(None):
        return value is None
    if isinstance(expected, type):
        if expected in (bool, int, str, Decimal, date, datetime):
            return type(value) is expected
        return isinstance(value, expected)
    return False


def validate_structural_dataclass(instance: object) -> None:
    """Reject coercions, mutable payloads, floats and naive times at construction."""
    if not is_dataclass(instance):
        raise TypeError("expected a dataclass")
    hints = get_type_hints(type(instance))
    for field in fields(instance):
        value = getattr(instance, field.name)
        if not _matches(value, hints[field.name]):
            raise TypeError(f"{field.name} has the wrong type")
        _validate_deep(value, field.name)


def _validate_deep(value: object, label: str) -> None:
    if isinstance(value, (list, dict, set, bytes, bytearray, float)):
        raise TypeError(f"{label} contains a forbidden mutable or noncanonical value")
    if isinstance(value, tuple):
        for item in value:
            _validate_deep(item, label)
    elif isinstance(value, datetime):
        validate_aware_datetime(value, label)
    elif isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError(f"{label} must be finite")
    elif isinstance(value, str) and not isinstance(value, StrEnum):
        if label != "value" and (not value or value != value.strip()):
            raise ValueError(f"{label} must be nonempty and stripped")
    elif is_dataclass(value):
        validate_structural_dataclass(value)


class Validated:
    __slots__ = ()

    def __post_init__(self) -> None:
        validate_structural_dataclass(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class VersionRef(Validated):
    name: str
    version: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EntityRef(Validated):
    entity_type: str
    entity_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceRef(Validated):
    source_entity: str
    source_record_id: str
    source_field: str
    observed_at: datetime | None
    available_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class ArtifactProvenance(Validated):
    producer: str
    producer_version: str
    input_artifact_ids: tuple[str, ...]
    source_refs: tuple[SourceRef, ...]
    contract_versions: tuple[VersionRef, ...]
    implementation_sha: str | None

    def __post_init__(self) -> None:
        Validated.__post_init__(self)
        validate_sorted_unique(self.input_artifact_ids, lambda item: item, "input_artifact_ids")
        validate_sorted_unique(
            self.source_refs,
            lambda item: (
                item.source_entity,
                item.source_record_id,
                item.source_field,
                str(canonical_primitive(item.observed_at)) if item.observed_at else "",
                str(canonical_primitive(item.available_at)),
            ),
            "source_refs",
        )
        validate_sorted_unique(
            self.contract_versions, lambda item: (item.name, item.version), "contract_versions"
        )
        if self.implementation_sha is not None:
            validate_git_oid(self.implementation_sha, "implementation_sha")


@dataclass(frozen=True, slots=True, kw_only=True)
class Limitation(Validated):
    code: str
    message: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Uncertainty(Validated):
    status: UncertaintyStatus
    code: str
    message: str
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        Validated.__post_init__(self)
        validate_sorted_unique(self.evidence_ids, lambda item: item, "evidence_ids")
        for evidence_id in self.evidence_ids:
            validate_artifact_id(evidence_id, "ev_", evidence_id)


@dataclass(frozen=True, slots=True, kw_only=True)
class NamedValue(Validated):
    name: str
    value: ScalarValue
    unit: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class SnapshotEntry(Validated):
    entry_key: str
    entity: EntityRef
    field: str
    value: ScalarValue
    observed_at: datetime | None
    available_at: datetime
    source_ref: SourceRef


@dataclass(frozen=True, slots=True, kw_only=True)
class DiagnosisClaim(Validated):
    claim_code: str
    claim_type: ClaimType
    statement: str
    evidence_ids: tuple[str, ...]
    limitations: tuple[Limitation, ...]

    def __post_init__(self) -> None:
        Validated.__post_init__(self)
        validate_sorted_unique(self.evidence_ids, lambda item: item, "evidence_ids")
        for evidence_id in self.evidence_ids:
            validate_artifact_id(evidence_id, "ev_", evidence_id)
        validate_sorted_unique(
            self.limitations, lambda item: (item.code, item.message), "limitations"
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ExplanationSection(Validated):
    section_key: str
    text: str
