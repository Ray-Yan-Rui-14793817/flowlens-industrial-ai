"""Independent collection, filesystem, identity and isolation acceptance for C04-G."""

from __future__ import annotations

import copy
import hashlib
import inspect
import json
import os
import stat
import subprocess
import sys
import tempfile
from dataclasses import asdict, replace
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest

from flowlens.data.generation import (
    BUSINESS_TIMEZONE,
    GeneratedDataset,
    GenerationConfig,
    GenerationProfile,
    generate_baseline,
)
from flowlens.data.generation.canonical import canonical_business_payload
from flowlens.data.scenarios import (
    CapacitySurgeConfig,
    HiddenGroundTruth,
    QualityDeteriorationConfig,
    ScenarioConfig,
    ScenarioResult,
    SupplierDegradationConfig,
    apply_scenario,
)
from flowlens.data.scenarios import serialization as writer

ROOT = Path(__file__).absolute().parents[1]
RELATIVE = Path("data/hidden_ground_truth/scenario_manifest.yaml")
NOW = datetime(2026, 9, 1, tzinfo=UTC)
FIELDS = {
    "schema_version",
    "scenario_id",
    "scenario_type",
    "scenario_version",
    "scenario_seed",
    "baseline_dataset_version_id",
    "scenario_dataset_version_id",
    "window_start",
    "window_end",
    "parameters",
    "target_entity_ids",
    "affected_entities_by_table",
    "causal_chain",
    "hgt_id",
    "hgt_hash",
}


def _record(hgt: HiddenGroundTruth) -> dict[str, object]:
    """Independent expected transport representation, not the writer's helpers."""

    def decimal_text(value: Decimal) -> str:
        text = format(value, "f")
        return text.rstrip("0").rstrip(".") if "." in text else text

    return {
        "schema_version": hgt.schema_version,
        "scenario_id": hgt.scenario_id,
        "scenario_type": hgt.scenario_type.value,
        "scenario_version": hgt.scenario_version,
        "scenario_seed": hgt.scenario_seed,
        "baseline_dataset_version_id": hgt.baseline_dataset_version_id,
        "scenario_dataset_version_id": hgt.scenario_dataset_version_id,
        "window_start": hgt.window_start.astimezone(UTC)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z"),
        "window_end": hgt.window_end.astimezone(UTC)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z"),
        "parameters": {
            key: decimal_text(value) if isinstance(value, Decimal) else value
            for key, value in hgt.parameters.items()
        },
        "target_entity_ids": list(hgt.target_entity_ids),
        "affected_entities_by_table": {
            table: list(ids) for table, ids in hgt.affected_entities_by_table.items()
        },
        "causal_chain": [asdict(link) for link in hgt.causal_chain],
        "hgt_id": hgt.hgt_id,
        "hgt_hash": hgt.hgt_hash,
    }


def _bytes(records: list[dict[str, object]]) -> bytes:
    ordered = sorted(records, key=lambda item: (str(item["scenario_id"]), str(item["hgt_id"])))
    return (
        json.dumps(
            {"records": ordered},
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


@pytest.fixture(scope="module")
def baseline() -> GeneratedDataset:
    return generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.TEST,
            seed=20260824,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=NOW,
        )
    )


def _configs() -> tuple[ScenarioConfig, ...]:
    start = datetime(2026, 1, 1, tzinfo=BUSINESS_TIMEZONE)
    end = datetime(2026, 4, 1, tzinfo=BUSINESS_TIMEZONE)
    return (
        SupplierDegradationConfig(
            scenario_version="1.0.0",
            scenario_seed=20260901,
            window_start=start,
            window_end=end,
        ),
        QualityDeteriorationConfig(
            scenario_version="1.0.0",
            scenario_seed=20260901,
            window_start=start,
            window_end=end,
            affected_work_center_count=4,
            affected_product_count=12,
        ),
        *(
            CapacitySurgeConfig(
                scenario_version="1.0.0",
                scenario_seed=20260901,
                window_start=datetime(2026, 1, 15, tzinfo=BUSINESS_TIMEZONE),
                window_end=datetime(2026, 2, 1, tzinfo=BUSINESS_TIMEZONE),
                arrival_volume_multiplier=Decimal(arrival),
                queue_time_multiplier=Decimal(queue),
            )
            for arrival, queue in (("1.5", "1.7"), ("1.5", "1"), ("1", "1.7"), ("1", "1"))
        ),
    )


@pytest.fixture(scope="module")
def results(baseline: GeneratedDataset) -> tuple[ScenarioResult, ...]:
    return tuple(apply_scenario(baseline, config, generated_at=NOW) for config in _configs())


@pytest.fixture
def destination(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(writer, "_REPOSITORY_ROOT", tmp_path)
    return tmp_path / RELATIVE


def _existing(destination: Path, payload: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)


@pytest.mark.parametrize(
    "index",
    range(6),
    ids=[
        "supplier",
        "quality",
        "capacity-combined",
        "arrival-only",
        "queue-only",
        "neutral",
    ],
)
def test_real_finalized_scenarios_and_independent_bytes(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    index: int,
) -> None:
    hgt = results[index].ground_truth
    assert writer.write_protected_hgt(hgt) == destination
    payload = destination.read_bytes()
    expected = _record(hgt)
    assert payload == _bytes([expected])
    assert set(expected) == FIELDS
    assert payload.endswith(b"\n") and not payload.endswith(b"\n\n") and b"\r" not in payload
    assert payload.decode("utf-8").encode("utf-8") == payload
    assert b"generated_at" not in payload
    semantic = {key: value for key, value in expected.items() if key not in {"hgt_id", "hgt_hash"}}
    digest = hashlib.sha256(
        json.dumps(
            semantic,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    assert hgt.hgt_hash == digest and hgt.hgt_id == f"hgt_{digest[:32]}"
    assert hashlib.sha256(payload).hexdigest() != hgt.hgt_hash
    if index == 5:
        assert expected["affected_entities_by_table"] == {}
        assert expected["causal_chain"] == []


def test_empty_collection_insert(destination: Path, results: tuple[ScenarioResult, ...]) -> None:
    _existing(destination, b'{"records": []}')
    writer.write_protected_hgt(results[0].ground_truth)
    assert destination.read_bytes() == _bytes([_record(results[0].ground_truth)])


def test_preserve_sort_reverse_invocations_existing_order_and_dict_order(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for result in results:
        writer.write_protected_hgt(result.ground_truth)
    expected = _bytes([_record(result.ground_truth) for result in results])
    assert destination.read_bytes() == expected
    reverse_root = destination.parents[2] / "reverse"
    reverse_root.mkdir()
    monkeypatch.setattr(writer, "_REPOSITORY_ROOT", reverse_root)
    for result in reversed(results):
        writer.write_protected_hgt(result.ground_truth)
    assert (reverse_root / RELATIVE).read_bytes() == expected
    unordered = [dict(reversed(list(_record(result.ground_truth).items()))) for result in results]
    _existing(reverse_root / RELATIVE, json.dumps({"records": unordered[::-1]}).encode())
    writer.write_protected_hgt(results[0].ground_truth)
    assert (reverse_root / RELATIVE).read_bytes() == expected


def test_identical_repeat_does_not_replace(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    writer.write_protected_hgt(results[0].ground_truth)
    original = destination.read_bytes()
    monkeypatch.setattr(os, "replace", _fail)
    writer.write_protected_hgt(results[0].ground_truth)
    assert destination.read_bytes() == original


def _fail(*args: object, **kwargs: object) -> None:
    raise OSError("injected failure")


@pytest.mark.parametrize("conflicting", [False, True])
def test_existing_duplicates_rejected_before_incoming(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    conflicting: bool,
) -> None:
    record = _record(results[0].ground_truth)
    duplicate = dict(record)
    if conflicting:
        duplicate["target_entity_ids"] = ["different"]
    original = _bytes([record, duplicate])
    _existing(destination, original)
    # An invalid incoming value proves existing validation takes precedence.
    with pytest.raises(writer.ManifestValidationError):
        writer.write_protected_hgt(cast(HiddenGroundTruth, None))
    assert destination.read_bytes() == original


@pytest.mark.parametrize(
    "case",
    [
        "json",
        "utf8",
        "array",
        "null",
        "missing-records",
        "extra-envelope",
        "wrong-records",
        "non-object",
        "missing-field",
        "extra-field",
        "schema",
        "id",
        "hash",
        "scenario-id",
        "seed-bool",
        "seed-float",
        "parameter-number",
        "parameter-nan",
        "parameter-extra",
        "targets-string",
        "targets-duplicate",
        "targets-unsorted",
        "affected-array",
        "affected-string",
        "chain-object",
        "chain-non-object",
        "chain-extra",
        "chain-duplicate",
        "chain-unsorted",
        "datetime-naive",
        "datetime-noncanonical",
        "duplicate-key",
        "nonjson-number",
        "bom",
    ],
)
def test_malformed_existing_preserved(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    case: str,
) -> None:
    record = copy.deepcopy(_record(results[0].ground_truth))
    envelope: object = {"records": [record]}
    raw: bytes | None = None
    match case:
        case "json":
            raw = b'{"records":'
        case "utf8":
            raw = b"\xff"
        case "array":
            envelope = []
        case "null":
            envelope = None
        case "missing-records":
            envelope = {}
        case "extra-envelope":
            envelope = {"records": [record], "generated_at": "not allowed"}
        case "wrong-records":
            envelope = {"records": {}}
        case "non-object":
            envelope = {"records": [1]}
        case "missing-field":
            record.pop("parameters")
        case "extra-field":
            record["generated_at"] = "not allowed"
        case "schema":
            record["schema_version"] = "2.0"
        case "id":
            record["hgt_id"] = "hgt_" + "0" * 32
        case "hash":
            record["hgt_hash"] = "0" * 64
        case "scenario-id":
            record["scenario_id"] = "scn_" + "0" * 32
        case "seed-bool":
            record["scenario_seed"] = True
        case "seed-float":
            record["scenario_seed"] = float(results[0].ground_truth.scenario_seed)
        case "parameter-number":
            cast(dict[str, object], record["parameters"])["late_probability_delta"] = 0.3
        case "parameter-nan":
            cast(dict[str, object], record["parameters"])["late_probability_delta"] = "NaN"
        case "parameter-extra":
            cast(dict[str, object], record["parameters"])["extra"] = 1
        case "targets-string":
            record["target_entity_ids"] = "entity"
        case "targets-duplicate":
            record["target_entity_ids"] = ["entity", "entity"]
        case "targets-unsorted":
            record["target_entity_ids"] = ["z", "a"]
        case "affected-array":
            record["affected_entities_by_table"] = []
        case "affected-string":
            record["affected_entities_by_table"] = {"fact_purchase_order": "id"}
        case "chain-object":
            record["causal_chain"] = {}
        case "chain-non-object":
            record["causal_chain"] = ["link"]
        case "chain-extra":
            cast(list[dict[str, object]], record["causal_chain"])[0]["extra"] = "extra"
        case "chain-duplicate":
            chain = cast(list[object], record["causal_chain"])
            chain.append(chain[0])
        case "chain-unsorted":
            cast(list[object], record["causal_chain"]).reverse()
        case "datetime-naive":
            record["window_start"] = "2026-01-01T00:00:00"
        case "datetime-noncanonical":
            record["window_start"] = "2026-01-01T00:00:00+08:00"
        case "duplicate-key":
            raw = b'{"records":[],"records":[]}'
        case "nonjson-number":
            raw = b'{"records":[NaN]}'
        case "bom":
            raw = b'\xef\xbb\xbf{"records":[]}'
    original = raw if raw is not None else json.dumps(envelope).encode("utf-8")
    _existing(destination, original)
    with pytest.raises(writer.ManifestValidationError):
        writer.write_protected_hgt(results[0].ground_truth)
    assert destination.read_bytes() == original
    assert list(destination.parent.iterdir()) == [destination]


@pytest.mark.parametrize(
    "field,value",
    [
        ("hgt_hash", "0" * 64),
        ("hgt_id", "hgt_" + "0" * 32),
        ("target_entity_ids", ("changed-semantic-content",)),
    ],
)
def test_tampered_incoming_identity_or_semantics_rejected_without_repair(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    field: str,
    value: object,
) -> None:
    original_hgt = results[0].ground_truth
    writer.write_protected_hgt(original_hgt)
    original = destination.read_bytes()
    incoming = replace(original_hgt)
    object.__setattr__(incoming, field, value)
    with pytest.raises(writer.ManifestValidationError):
        writer.write_protected_hgt(incoming)
    assert destination.read_bytes() == original
    assert getattr(incoming, field) == value


def test_full_existing_collection_validated_even_after_matching_record(
    destination: Path,
    results: tuple[ScenarioResult, ...],
) -> None:
    original = json.dumps({"records": [_record(results[0].ground_truth), {}]}).encode()
    _existing(destination, original)
    with pytest.raises(writer.ManifestValidationError):
        writer.write_protected_hgt(results[0].ground_truth)
    assert destination.read_bytes() == original


def _snapshot(dataset: GeneratedDataset) -> tuple[object, tuple[object, ...]]:
    metadata = dataset.dataset_version
    return (
        canonical_business_payload(dataset.rows_by_table),
        tuple(getattr(metadata, column.name) for column in metadata.__table__.columns),
    )


def test_no_mutation_no_implicit_write_and_generated_at_isolation(
    destination: Path,
    baseline: GeneratedDataset,
    results: tuple[ScenarioResult, ...],
) -> None:
    before = [_snapshot(baseline), *(_snapshot(result.dataset) for result in results)]
    truths = [_record(result.ground_truth) for result in results]
    for config, result in zip(_configs(), results, strict=True):
        alternate = apply_scenario(baseline, config, generated_at=datetime(2030, 1, 1, tzinfo=UTC))
        assert _record(alternate.ground_truth) == _record(result.ground_truth)
    assert not destination.parent.exists()
    for result in results:
        writer.write_protected_hgt(result.ground_truth)
    assert before == [_snapshot(baseline), *(_snapshot(result.dataset) for result in results)]
    assert truths == [_record(result.ground_truth) for result in results]


def test_fixed_path_ignores_cwd_and_has_no_output_argument(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    source = elsewhere / "source.py"
    source.write_bytes(b"source sentinel")
    business = elsewhere / "business.json"
    business.write_bytes(b"business sentinel")
    monkeypatch.chdir(elsewhere)
    assert tuple(inspect.signature(writer.write_protected_hgt).parameters) == ("ground_truth",)
    assert writer.write_protected_hgt(results[0].ground_truth) == destination
    assert not (elsewhere / RELATIVE).exists()
    assert source.read_bytes() == b"source sentinel"
    assert business.read_bytes() == b"business sentinel"


@pytest.mark.parametrize("part", ["root", "data", "directory", "file"])
@pytest.mark.parametrize("indirection", ["symlink", "reparse"])
def test_indirection_rejected_portably_without_privileges(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    monkeypatch: pytest.MonkeyPatch,
    part: str,
    indirection: str,
) -> None:
    original = _bytes([_record(results[0].ground_truth)])
    _existing(destination, original)
    suspect = {
        "root": destination.parents[2],
        "data": destination.parents[1],
        "directory": destination.parent,
        "file": destination,
    }[part]
    real_lstat = Path.lstat

    def indirect(path: Path, *, follow_symlinks: bool = False) -> os.stat_result:
        del follow_symlinks
        if path == suspect:
            return cast(
                os.stat_result,
                SimpleNamespace(
                    st_mode=stat.S_IFLNK if indirection == "symlink" else stat.S_IFDIR,
                    st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT
                    if indirection == "reparse"
                    else 0,
                ),
            )
        return real_lstat(path)

    monkeypatch.setattr(Path, "lstat", indirect)
    with pytest.raises(ValueError, match="indirection"):
        writer.write_protected_hgt(results[1].ground_truth)
    assert destination.read_bytes() == original


def test_hardlink_cannot_overwrite_source(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.py"
    source.write_bytes(b"source sentinel")
    destination.parent.mkdir(parents=True)
    os.link(source, destination)
    with pytest.raises(ValueError, match="non-hardlinked"):
        writer.write_protected_hgt(results[0].ground_truth)
    assert source.read_bytes() == destination.read_bytes() == b"source sentinel"


@pytest.mark.parametrize("invalid", [Path("relative"), Path("C:/trusted/../escape")])
def test_invalid_trusted_root_rejected(
    results: tuple[ScenarioResult, ...],
    monkeypatch: pytest.MonkeyPatch,
    invalid: Path,
) -> None:
    monkeypatch.setattr(writer, "_REPOSITORY_ROOT", invalid)
    with pytest.raises(ValueError, match="absolute, non-traversing"):
        writer.write_protected_hgt(results[0].ground_truth)


@pytest.mark.parametrize("stage", ["read", "serialize", "temporary", "fsync", "replace"])
@pytest.mark.parametrize("exists", [False, True])
def test_failures_preserve_final_and_clean_temporary(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    monkeypatch: pytest.MonkeyPatch,
    stage: str,
    exists: bool,
) -> None:
    original = _bytes([_record(results[0].ground_truth)])
    if exists:
        _existing(destination, original)
    targets = {
        "read": (writer, "_read_existing"),
        "serialize": (writer, "_json_bytes"),
        "temporary": (tempfile, "mkstemp"),
        "fsync": (os, "fsync"),
        "replace": (os, "replace"),
    }
    owner, attribute = targets[stage]
    monkeypatch.setattr(owner, attribute, _fail)
    with pytest.raises(OSError, match="injected failure"):
        writer.write_protected_hgt(results[1].ground_truth)
    assert destination.read_bytes() == original if exists else not destination.exists()
    if destination.parent.exists():
        assert list(destination.parent.iterdir()) == ([destination] if exists else [])


def test_concurrent_change_detected_before_publication(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    writer.write_protected_hgt(results[0].ground_truth)
    other = _bytes([_record(results[2].ground_truth)])
    real_fsync = os.fsync

    def concurrent_write(descriptor: int) -> None:
        real_fsync(descriptor)
        destination.write_bytes(other)

    monkeypatch.setattr(os, "fsync", concurrent_write)
    with pytest.raises(ValueError, match="changed before publication"):
        writer.write_protected_hgt(results[1].ground_truth)
    assert destination.read_bytes() == other
    assert list(destination.parent.iterdir()) == [destination]


def test_atomic_replace_receives_complete_collection_only(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    writer.write_protected_hgt(results[0].ground_truth)
    original = destination.read_bytes()
    expected = _bytes([_record(result.ground_truth) for result in results[:2]])
    real_replace = os.replace
    published: list[Path] = []

    def observe(source: Path, target: Path) -> None:
        assert source.parent == destination.parent
        assert source != destination and source.suffix == ".tmp"
        assert target == destination
        assert source.read_bytes() == expected
        assert destination.read_bytes() == original
        real_replace(source, target)
        published.append(target)

    monkeypatch.setattr(os, "replace", observe)
    writer.write_protected_hgt(results[1].ground_truth)
    assert published == [destination]
    assert destination.read_bytes() == expected
    assert list(destination.parent.iterdir()) == [destination]


def test_semantic_collision_branch_preserves_existing(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Model a validated SHA-256-prefix collision at the validation boundary.
    # Forged-ID rejection against the real validator is tested separately above.
    writer.write_protected_hgt(results[0].ground_truth)
    original = destination.read_bytes()
    incoming = replace(results[1].ground_truth)
    object.__setattr__(incoming, "hgt_id", results[0].ground_truth.hgt_id)
    actual_validate = writer._validate_record

    def collision_witness(value: object) -> dict[str, object]:
        if value == _record(incoming):
            return _record(incoming)
        return actual_validate(value)

    monkeypatch.setattr(writer, "_validate_record", collision_witness)
    with pytest.raises(writer.ManifestValidationError, match="conflicts"):
        writer.write_protected_hgt(incoming)
    assert destination.read_bytes() == original


def test_labels_cannot_select_paths(
    destination: Path,
    results: tuple[ScenarioResult, ...],
) -> None:
    hgt = replace(results[5].ground_truth, target_entity_ids=("../../src/source.py", "C:/outside"))
    assert writer.write_protected_hgt(hgt) == destination
    assert destination.read_bytes() == _bytes([_record(hgt)])
    assert list(destination.parents[2].rglob("*")) == [
        destination.parents[1],
        destination.parent,
        destination,
    ]


@pytest.mark.parametrize("obstacle", ["parent-file", "destination-directory", "wheel-layout"])
def test_unexpected_filesystem_layout_rejected(
    destination: Path,
    results: tuple[ScenarioResult, ...],
    monkeypatch: pytest.MonkeyPatch,
    obstacle: str,
) -> None:
    if obstacle == "parent-file":
        destination.parents[1].write_bytes(b"unrelated file")
    elif obstacle == "destination-directory":
        destination.mkdir(parents=True)
    else:
        monkeypatch.setattr(
            writer, "__file__", "C:/site-packages/flowlens/data/scenarios/writer.py"
        )
    with pytest.raises(ValueError):
        writer.write_protected_hgt(results[0].ground_truth)
    if obstacle == "parent-file":
        assert destination.parents[1].read_bytes() == b"unrelated file"
    elif obstacle == "destination-directory":
        assert destination.is_dir() and list(destination.iterdir()) == []
    else:
        assert not destination.parent.exists()


def test_invalid_incoming_creates_no_directories(destination: Path) -> None:
    with pytest.raises(TypeError, match="finalized HiddenGroundTruth"):
        writer.write_protected_hgt(cast(HiddenGroundTruth, None))
    assert not destination.parents[1].exists()


def _subprocess(script: str, cwd: Path, seed: str = "1") -> str:
    environment = dict(os.environ, PYTHONHASHSEED=seed, PYTHONPATH=str(ROOT / "src"))
    result = subprocess.run(
        [sys.executable, "-B", "-c", script],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_imports_have_no_writes_and_runtime_has_no_hgt_dependency(tmp_path: Path) -> None:
    script = """
import sys, os
def guard(event, args):
    if event == "open":
        path, mode, flags = args
        if path == os.devnull:
            return  # Windows platform detection opens NUL, not an artifact.
        assert not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
        assert "hidden_ground_truth" not in str(path)
sys.addaudithook(guard)
import flowlens.api.app
import flowlens.worker.main
assert not any(name.startswith("flowlens.data.scenarios") for name in sys.modules)
import flowlens.data.scenarios
import flowlens.data.scenarios.application
import flowlens.data.scenarios.ground_truth
import flowlens.data.scenarios.supplier
import flowlens.data.scenarios.quality
import flowlens.data.scenarios.capacity
import flowlens.data.scenarios.serialization
assert "write_protected_hgt" not in flowlens.data.scenarios.__dict__
"""
    _subprocess(script, tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_hash_seed_cwd_and_mapping_insertion_determinism(tmp_path: Path) -> None:
    script = """
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from flowlens.data.generation import BUSINESS_TIMEZONE
from flowlens.data.scenarios import CapacitySurgeConfig, HiddenGroundTruth
from flowlens.data.scenarios.config import scenario_namespace, scenario_parameters
from flowlens.data.scenarios import serialization
config = CapacitySurgeConfig(scenario_version="1.0.0", scenario_seed=42,
    window_start=datetime(2026,1,1,tzinfo=BUSINESS_TIMEZONE),
    window_end=datetime(2026,2,1,tzinfo=BUSINESS_TIMEZONE),
    arrival_volume_multiplier=Decimal("1"),queue_time_multiplier=Decimal("1"))
namespace = scenario_namespace("baseline", config)
parameters = scenario_parameters(config)
hgt = HiddenGroundTruth(schema_version="1.0", scenario_id="scn_"+namespace[:32],
    scenario_dataset_version_id="dsv_"+namespace[:32],baseline_dataset_version_id="baseline",
    scenario_type=config.scenario_type,scenario_version=config.scenario_version,
    scenario_seed=config.scenario_seed,window_start=config.window_start,window_end=config.window_end,
    parameters={key:parameters[key] for key in set(parameters)},target_entity_ids=("工业",),
    affected_entities_by_table={},causal_chain=())
serialization._REPOSITORY_ROOT=Path.cwd()
print(serialization.write_protected_hgt(hgt).read_bytes().hex())
"""
    payloads = []
    for seed in ("1", "47", "2030"):
        folder = tmp_path / seed
        folder.mkdir()
        payloads.append(_subprocess(script, folder, seed))
    assert len(set(payloads)) == 1
    assert bytes.fromhex(payloads[0]).endswith(b"\n")


@pytest.mark.parametrize("service", ["api", "worker"])
def test_docker_and_compose_exclude_protected_artifacts(service: str) -> None:
    dockerfile = (ROOT / "apps" / service / "Dockerfile").read_text(encoding="utf-8")
    copies = [line.strip() for line in dockerfile.splitlines() if line.strip().startswith("COPY ")]
    assert copies == [
        "COPY --from=uv /uv /uvx /bin/",
        "COPY pyproject.toml uv.lock README.md ./",
        "COPY src ./src",
    ]
    assert not any(line.strip().startswith("ADD ") for line in dockerfile.splitlines())
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    section = compose.split(f"  {service}:\n", 1)[1]
    section = section.split("\n  worker:", 1)[0].split("\nvolumes:", 1)[0]
    assert "volumes:" not in section and "hidden_ground_truth" not in compose
