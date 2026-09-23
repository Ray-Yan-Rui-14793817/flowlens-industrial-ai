"""Explicit evaluation-only publication of finalized HGT in a source checkout.

This module is deliberately not a scenario-package export or runtime dependency.
The trusted checkout must not be concurrently modified by an untrusted filesystem
actor. Writers in this process are serialized; cross-process coordination belongs
to the evaluation caller, not to scenario execution.
"""

from __future__ import annotations

import json
import os
import stat
import tempfile
from dataclasses import fields
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from threading import Lock

from flowlens.data.generation import BUSINESS_TIMEZONE
from flowlens.data.scenarios.config import ScenarioType
from flowlens.data.scenarios.ground_truth import (
    CausalLink,
    GroundTruthParameter,
    HiddenGroundTruth,
    canonical_hgt_payload,
)

_REPOSITORY_ROOT = Path(__file__).absolute().parents[4]
_RECORD_FIELDS = frozenset(field.name for field in fields(HiddenGroundTruth))
_LINK_FIELDS = frozenset(field.name for field in fields(CausalLink))
_DECIMAL_PARAMETERS = frozenset(
    {
        "late_probability_delta",
        "failure_probability_multiplier",
        "rework_probability_delta",
        "rework_duration_multiplier_min",
        "rework_duration_multiplier_max",
        "arrival_volume_multiplier",
        "queue_time_multiplier",
    }
)
_WRITE_LOCK = Lock()


class ManifestValidationError(ValueError):
    """An existing manifest or incoming HGT violates the frozen contract."""


def _object(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise ManifestValidationError("expected a JSON object with string keys")
    return {key: item for key, item in value.items()}


def _array(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ManifestValidationError("expected a JSON array")
    return list(value)


def _string(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ManifestValidationError("expected a nonempty string without surrounding whitespace")
    return value


def _integer(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ManifestValidationError("expected an integer, not a boolean or float")
    return value


def _datetime(value: object) -> datetime:
    parsed = datetime.fromisoformat(_string(value))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ManifestValidationError("HGT datetime must have a timezone")
    return parsed.astimezone(BUSINESS_TIMEZONE)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ManifestValidationError("duplicate JSON object key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> object:
    raise ManifestValidationError(f"non-JSON numeric constant: {value}")


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _complete_record(ground_truth: HiddenGroundTruth) -> dict[str, object]:
    record = _object(json.loads(canonical_hgt_payload(ground_truth)))
    record.update(hgt_id=ground_truth.hgt_id, hgt_hash=ground_truth.hgt_hash)
    return record


def _validate_record(value: object) -> dict[str, object]:
    """Decode transport types, then delegate semantics/identity to existing HGT.

    The reconstructed object is only a validation witness. Exact round-trip
    comparison rejects coercions, normalization and identity repair; publication
    always retains the supplied complete record, never the witness's replacement.
    """
    record = _object(value)
    if record.keys() != _RECORD_FIELDS:
        raise ManifestValidationError("HGT record must contain exactly the 15 frozen fields")
    if record["schema_version"] != "1.0":
        raise ManifestValidationError("unsupported HGT schema_version")
    try:
        parameters: dict[str, GroundTruthParameter] = {}
        for key, item in _object(record["parameters"]).items():
            if key in _DECIMAL_PARAMETERS:
                decimal = Decimal(_string(item))
                if not decimal.is_finite():
                    raise ManifestValidationError("HGT Decimal must be finite")
                parameters[key] = decimal
            else:
                parameters[key] = _integer(item)
        links: list[CausalLink] = []
        for item in _array(record["causal_chain"]):
            link = _object(item)
            if link.keys() != _LINK_FIELDS:
                raise ManifestValidationError("causal link must contain exactly five frozen fields")
            links.append(CausalLink(**{key: _string(value) for key, value in link.items()}))
        witness = HiddenGroundTruth(
            schema_version=_string(record["schema_version"]),
            scenario_id=_string(record["scenario_id"]),
            scenario_type=ScenarioType(_string(record["scenario_type"])),
            scenario_version=_string(record["scenario_version"]),
            scenario_seed=_integer(record["scenario_seed"]),
            baseline_dataset_version_id=_string(record["baseline_dataset_version_id"]),
            scenario_dataset_version_id=_string(record["scenario_dataset_version_id"]),
            window_start=_datetime(record["window_start"]),
            window_end=_datetime(record["window_end"]),
            parameters=parameters,
            target_entity_ids=tuple(_string(item) for item in _array(record["target_entity_ids"])),
            affected_entities_by_table={
                _string(table): tuple(_string(item) for item in _array(items))
                for table, items in _object(record["affected_entities_by_table"]).items()
            },
            causal_chain=tuple(links),
        )
        if _json_bytes(_complete_record(witness)) != _json_bytes(record):
            raise ManifestValidationError("HGT semantics or stored identity/hash are inconsistent")
    except (ValueError, TypeError, ArithmeticError) as error:
        raise ManifestValidationError(f"invalid HGT record: {error}") from error
    return record


def _existing_records(original: bytes | None) -> dict[str, dict[str, object]]:
    if original is None:
        return {}
    try:
        envelope = _object(
            json.loads(
                original.decode("utf-8"),
                object_pairs_hook=_unique_object,
                parse_constant=_invalid_constant,
            )
        )
    except (ValueError, UnicodeError) as error:
        raise ManifestValidationError("existing manifest is not valid UTF-8 JSON") from error
    if envelope.keys() != {"records"}:
        raise ManifestValidationError("manifest envelope must contain only records")
    records: dict[str, dict[str, object]] = {}
    for item in _array(envelope["records"]):
        record = _validate_record(item)
        identity = _string(record["hgt_id"])
        if identity in records:
            raise ManifestValidationError("existing manifest contains duplicate hgt_id")
        records[identity] = record
    return records


def _safe_stat(path: Path) -> os.stat_result | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(info.st_mode) or (
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    ):
        raise ValueError("protected path must not contain symlink/reparse-point indirection")
    return info


def _destination(*, create: bool = False) -> Path:
    if Path(__file__).parts[-5:] != (
        "src",
        "flowlens",
        "data",
        "scenarios",
        "serialization.py",
    ):
        raise ValueError("protected writer requires the trusted source-checkout layout")
    root = _REPOSITORY_ROOT
    if not root.is_absolute() or ".." in root.parts:
        raise ValueError("protected repository root must be an absolute, non-traversing path")
    destination = root / "data" / "hidden_ground_truth" / "scenario_manifest.yaml"
    for directory in reversed(destination.parents):
        info = _safe_stat(directory)
        if info is None and create and directory in (root / "data", destination.parent):
            directory.mkdir(exist_ok=True)
            info = _safe_stat(directory)
        if info is not None and not stat.S_ISDIR(info.st_mode):
            raise ValueError("protected path parent must be a directory")
        if info is None and directory == root:
            raise ValueError("trusted repository root does not exist")
    info = _safe_stat(destination)
    if info is not None and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
        raise ValueError("protected manifest must be a regular, non-hardlinked file")
    return destination


def _read_existing(destination: Path) -> bytes | None:
    _destination()
    try:
        descriptor = os.open(
            destination,
            os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
    except FileNotFoundError:
        return None
    with os.fdopen(descriptor, "rb") as source:
        opened = os.fstat(source.fileno())
        current = _safe_stat(destination)
        if (
            current is None
            or not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino)
        ):
            raise ValueError("protected manifest changed during read")
        return source.read()


def _publish(destination: Path, original: bytes | None, payload: bytes) -> None:
    _destination(create=True)
    parent = destination.parent.stat()
    descriptor, name = tempfile.mkstemp(prefix=".hgt-", suffix=".tmp", dir=destination.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as target:
            target.write(payload)
            target.flush()
            os.fsync(target.fileno())
        _destination()
        current_parent = destination.parent.stat()
        if (parent.st_dev, parent.st_ino) != (current_parent.st_dev, current_parent.st_ino):
            raise ValueError("protected parent changed before publication")
        if _read_existing(destination) != original:
            raise ValueError("protected manifest changed before publication")
        os.replace(temporary, destination)
    finally:
        # Never follow a swapped directory to remove an unrelated file during cleanup.
        try:
            _destination()
            current_parent = destination.parent.stat()
            if (parent.st_dev, parent.st_ino) == (current_parent.st_dev, current_parent.st_ino):
                temporary.unlink(missing_ok=True)
        except (OSError, ValueError):
            pass


def write_protected_hgt(ground_truth: HiddenGroundTruth) -> Path:
    """Integrate ONE finalized HGT explicitly at the checkout's fixed protected path.

    Reject malformed existing collections before inspecting incoming HGT. No
    business data, scenario execution, caller-selected path, or runtime integration
    participates. A stable terminal LF is part of the manifest byte convention.
    """
    with _WRITE_LOCK:
        destination = _destination()
        original = _read_existing(destination)
        records = _existing_records(original)
        if not isinstance(ground_truth, HiddenGroundTruth):
            raise TypeError("writer requires one finalized HiddenGroundTruth")
        incoming = _validate_record(_complete_record(ground_truth))
        identity = ground_truth.hgt_id
        if identity in records and records[identity] != incoming:
            raise ManifestValidationError(
                "incoming hgt_id conflicts with existing semantic content"
            )
        records[identity] = incoming
        ordered = sorted(
            records.values(),
            key=lambda item: (
                _string(item["scenario_id"]),
                _string(item["hgt_id"]),
            ),
        )
        payload = _json_bytes({"records": ordered}) + b"\n"
        if payload != original:
            _publish(destination, original, payload)
        return destination
