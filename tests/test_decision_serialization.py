"""Canonical byte, replay, identity and snapshot-hash evidence for C01."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from flowlens.data.generation.canonical import normalize_scalar as w2_normalize_scalar
from flowlens.decision import (
    ArtifactProvenance,
    NamedValue,
    canonical_json_bytes,
    canonical_json_text,
    canonical_primitive,
    compute_snapshot_hash,
    derive_artifact_id,
)
from test_decision_contracts import sample_artifacts


@pytest.mark.parametrize(
    "value",
    [
        None,
        False,
        0,
        12,
        "text",
        Decimal("0.000"),
        Decimal("-0.000"),
        Decimal("1.2300E+2"),
        date(2026, 9, 24),
        datetime(2026, 9, 24, 8, 2, 3, 4, tzinfo=UTC),
        datetime(2026, 9, 24, 16, 2, 3, 4, tzinfo=timezone(timedelta(hours=8))),
    ],
)
def test_scalar_normalization_matches_frozen_w2(value: object) -> None:
    assert canonical_primitive(value) == w2_normalize_scalar(value)


def test_canonical_json_bytes_are_stable_and_sorted() -> None:
    value = {"z": Decimal("-0.00"), "a": (True, datetime(2026, 9, 24, tzinfo=UTC))}
    expected = b'{"a":[true,"2026-09-24T00:00:00.000000Z"],"z":"0"}'
    assert canonical_json_bytes(value) == expected
    assert canonical_json_text(value) == expected.decode("utf-8")
    assert canonical_json_bytes({"a": value["a"], "z": value["z"]}) == expected
    assert canonical_primitive(NamedValue(name="x", value=Decimal("1.20"), unit=None)) == {
        "name": "x",
        "value": "1.2",
        "unit": None,
    }


def test_canonical_rejects_float_naive_time_and_mutable_payload() -> None:
    for value in (1.2, [1], {"bad": {1}}, b"raw"):
        with pytest.raises(TypeError):
            canonical_json_bytes(value)
    with pytest.raises(ValueError, match="timezone-aware"):
        canonical_json_bytes(datetime(2026, 9, 24))
    with pytest.raises(ValueError, match="finite"):
        canonical_json_bytes(Decimal("NaN"))


def test_artifact_id_matches_independent_sha256_algorithm() -> None:
    identity = {"order_id": "SO-1", "as_of_time": datetime(2026, 9, 24, tzinfo=UTC)}
    payload = {
        "artifact_kind": "decision-run",
        "schema_version": "decision-run.v1",
        "identity": identity,
    }
    expected = (
        "run_"
        + hashlib.sha256(
            json.dumps(
                canonical_primitive(payload),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
    )
    assert derive_artifact_id("decision-run", "decision-run.v1", identity) == expected
    assert derive_artifact_id("decision-run", "decision-run.v1", identity) == expected
    changed = {**identity, "order_id": "SO-2"}
    assert derive_artifact_id("decision-run", "decision-run.v1", changed) != expected
    with pytest.raises(ValueError, match="unknown artifact"):
        derive_artifact_id("decision-run", "decision-run.v2", identity)


def test_snapshot_hash_tracks_only_semantic_observation() -> None:
    packet, _, _, _, _ = sample_artifacts()
    snapshot = packet.snapshot
    semantic = dict(
        order_id=snapshot.order_id,
        as_of_time=snapshot.as_of_time,
        dataset_version=snapshot.dataset_version,
        dataset_hash=snapshot.dataset_hash,
        entries=snapshot.entries,
        unknowns=snapshot.unknowns,
    )
    assert compute_snapshot_hash(semantic) == snapshot.snapshot_hash
    new_provenance = replace(snapshot.provenance, producer_version="2", implementation_sha="b" * 64)
    assert isinstance(new_provenance, ArtifactProvenance)
    assert replace(snapshot, provenance=new_provenance).snapshot_hash == snapshot.snapshot_hash
    changed_entry = replace(snapshot.entries[0], value=Decimal("2.0"))
    changed_semantic = {**semantic, "entries": (changed_entry,)}
    assert compute_snapshot_hash(changed_semantic) != snapshot.snapshot_hash
    with pytest.raises(ValueError, match="snapshot_hash"):
        replace(snapshot, entries=(changed_entry,))


def test_full_packet_replay_has_identical_ids_and_bytes() -> None:
    first = sample_artifacts()
    second = sample_artifacts()
    assert first == second
    for left, right in zip(first, second, strict=True):
        assert canonical_json_bytes(left) == canonical_json_bytes(right)
