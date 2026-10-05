"""Pure canonical serialization and identity functions for W03-C01."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum

_PREFIXES = {
    "decision-run": "run_",
    "state-snapshot": "snap_",
    "evidence": "ev_",
    "evidence-bundle": "evb_",
    "signal": "sig_",
    "signal-bundle": "sigb_",
    "diagnosis-record": "diag_",
    "intervention-candidate": "cand_",
    "candidate-set": "cset_",
    "simulation-result": "sim_",
    "simulation-bundle": "simb_",
    "recommendation-record": "rec_",
    "decision-packet": "pkt_",
    "explanation-record": "exp_",
    "human-decision-event": "hdec_",
    "recommendation-evaluation": "reval_",
    "outcome-evaluation": "oeval_",
}


def canonical_primitive(value: object) -> object:
    """Convert a contract value to JSON primitives without lossy coercion."""
    if value is None or type(value) in (bool, int, str):
        return value
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("canonical Decimal must be finite")
        rendered = format(value, "f")
        if "." in rendered:
            rendered = rendered.rstrip("0").rstrip(".")
        return "0" if rendered in ("", "-0") else rendered
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("canonical datetime must be timezone-aware")
        return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, tuple):
        return [canonical_primitive(item) for item in value]
    if is_dataclass(value):
        return {
            field.name: canonical_primitive(getattr(value, field.name)) for field in fields(value)
        }
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise TypeError("canonical mapping keys must be strings")
        return {key: canonical_primitive(item) for key, item in value.items()}
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        canonical_primitive(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_json_text(value: object) -> str:
    return canonical_json_bytes(value).decode("utf-8")


def sha256_hex(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def derive_artifact_id(kind: str, schema_version: str, identity_payload: object) -> str:
    if kind not in _PREFIXES or schema_version != f"{kind}.v1":
        raise ValueError("unknown artifact kind or schema version")
    identity_object = {
        "artifact_kind": kind,
        "schema_version": schema_version,
        "identity": identity_payload,
    }
    return _PREFIXES[kind] + sha256_hex(identity_object)


def compute_snapshot_hash(snapshot_semantic_payload: Mapping[str, object]) -> str:
    required = {"order_id", "as_of_time", "dataset_version", "dataset_hash", "entries", "unknowns"}
    if set(snapshot_semantic_payload) != required:
        raise ValueError("snapshot semantic payload must have exactly the frozen fields")
    return sha256_hex(snapshot_semantic_payload)
