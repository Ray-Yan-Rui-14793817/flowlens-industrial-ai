"""Isolation, determinism, capability, and semantic-diff harness for W03-C04."""

from __future__ import annotations

import ast
import hashlib
import subprocess
import sys
from pathlib import Path
from types import MappingProxyType
from typing import cast

from flowlens.data import Base
from flowlens.data.generation import GeneratedDataset
from flowlens.data.generation.canonical import (
    CANONICAL_TABLE_ORDER,
    canonical_content_hash,
    canonicalize_rows,
)
from flowlens.data.models import DatasetVersion, Supplier
from flowlens.data.scenarios.transformer import _clone_row
from flowlens.decision.c04_simulation import semantic_affected_entities
from flowlens.decision.serialization import canonical_json_bytes
from test_c04_registry import make_c04_fixture
from test_c04_simulation import closed_baseline

ROOT = Path(__file__).parents[1]
C04_RUNTIME_FILES = (
    ROOT / "src/flowlens/decision/c04_registry.py",
    ROOT / "src/flowlens/decision/c04_validation.py",
    ROOT / "src/flowlens/decision/c04_simulation.py",
    ROOT / "src/flowlens/data/scenarios/runtime_adapter.py",
)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def _ownership_clone(baseline: GeneratedDataset, *, mutate: bool) -> GeneratedDataset:
    new_id = "dsv_" + "1" * 32
    rows: dict[str, list[Base]] = {
        table: [_clone_row(row, new_id) for row in baseline.rows_for(table)]
        for table in CANONICAL_TABLE_ORDER
    }
    if mutate:
        supplier = cast(Supplier, rows["dim_supplier"][0])
        supplier.supplier_code = f"{supplier.supplier_code}-SEMANTIC-CHANGE"
    ordered = canonicalize_rows(rows)
    old = baseline.dataset_version
    metadata = DatasetVersion(
        dataset_version_id=new_id,
        seed=old.seed,
        generator_version=old.generator_version,
        profile=old.profile,
        period_start=old.period_start,
        period_end=old.period_end,
        generated_at=old.generated_at,
        content_hash=canonical_content_hash(ordered),
        row_count_total=sum(len(items) for items in ordered.values()),
    )
    return GeneratedDataset(metadata, MappingProxyType(ordered))


def test_runtime_import_surface_has_no_hgt_or_forbidden_capability_modules() -> None:
    forbidden_modules = {
        "flowlens.data.scenarios.ground_truth",
        "flowlens.db",
        "flowlens.persistence",
        "requests",
        "httpx",
        "openai",
        "socket",
        "subprocess",
        "random",
    }
    for path in C04_RUNTIME_FILES:
        imports = _imports(path)
        assert forbidden_modules.isdisjoint(imports), (path, imports & forbidden_modules)
        source = path.read_text(encoding="utf-8")
        assert "RecommendationRecord" not in source
        assert "DecisionPacket" not in source
        assert "apply_scenario(" not in source
        assert "datetime.now" not in source
        assert "datetime.utcnow" not in source
        assert "time.time" not in source
        assert "Path(" not in source
        assert "open(" not in source


def test_pure_decision_import_does_not_eagerly_load_scenario_or_hgt_modules() -> None:
    code = """
import sys
import flowlens.decision
for name in (
    'flowlens.data.scenarios.application',
    'flowlens.data.scenarios.runtime_adapter',
    'flowlens.data.scenarios.ground_truth',
):
    assert name not in sys.modules, name
print('PURE')
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == "PURE"


def test_hgt_free_runtime_adapter_import_and_execution_in_fresh_process() -> None:
    code = """
import sys
from datetime import UTC, date, datetime
from flowlens.data.generation import GenerationConfig, GenerationProfile, generate_baseline
from flowlens.data.scenarios.config import SupplierDegradationConfig
from flowlens.data.generation import BUSINESS_TIMEZONE
assert 'flowlens.data.scenarios.ground_truth' not in sys.modules
from flowlens.data.scenarios.runtime_adapter import apply_scenario_business_only
assert 'flowlens.data.scenarios.ground_truth' not in sys.modules
baseline = generate_baseline(GenerationConfig(
    profile=GenerationProfile.TEST,
    seed=20260824,
    period_start=date(2026, 1, 1),
    generator_version='0.1.0-c03',
    generated_at=datetime(2026, 8, 24, 9, tzinfo=UTC),
))
config = SupplierDegradationConfig(
    scenario_version='1.0.0',
    scenario_seed=20260901,
    window_start=datetime(2026, 1, 1, tzinfo=BUSINESS_TIMEZONE),
    window_end=datetime(2026, 4, 1, tzinfo=BUSINESS_TIMEZONE),
)
result = apply_scenario_business_only(
    baseline,
    config,
    generated_at=datetime(2026, 9, 1, tzinfo=UTC),
)
assert result.content_hash
assert 'flowlens.data.scenarios.ground_truth' not in sys.modules
print(result.content_hash)
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert len(completed.stdout.strip()) == 64


def test_registry_has_deterministic_replay_and_cross_process_replay() -> None:
    local = make_c04_fixture()[-1]
    local_hash = hashlib.sha256(canonical_json_bytes(local)).hexdigest()
    code = """
import hashlib
import sys
sys.path.insert(0, 'tests')
from flowlens.decision.serialization import canonical_json_bytes
from test_c04_registry import make_c04_fixture
print(hashlib.sha256(canonical_json_bytes(make_c04_fixture()[-1])).hexdigest())
"""
    results = []
    for _ in range(2):
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        results.append(completed.stdout.strip())
    assert results == [local_hash, local_hash]


def test_affected_entity_diff_ignores_dataset_ownership_and_detects_business_change() -> None:
    baseline = closed_baseline()
    ownership_only = _ownership_clone(baseline, mutate=False)
    assert semantic_affected_entities(baseline, ownership_only) == ()

    changed = _ownership_clone(baseline, mutate=True)
    affected = semantic_affected_entities(baseline, changed)
    supplier = cast(Supplier, baseline.rows_for("dim_supplier")[0])
    assert affected == (
        type(affected[0])(
            entity_type="dim_supplier",
            entity_id=supplier.supplier_id,
        ),
    )


def test_context_lock_frozen_sources_remain_byte_exact() -> None:
    expected = {
        ROOT / "src/flowlens/data/scenarios/config.py": (
            "03a789130096f10e8f6ed2e0a723d60fa0038f94572d48868e54ae3d857d874b",
            "2ec47cdcab56bc5d1439a37a5a29e2c0362bd98bfe2675234eeb726bef84a35c",
        ),
        ROOT / "src/flowlens/data/scenarios/ground_truth.py": (
            "3b75e9d301bd5980c2f10051d32a980c03e474758032bf35c0bf1063159c9cad",
            "6b6671d568b404506da094785e8bde461d54a3754b7884f9f9311f4ac4f0a01e",
        ),
    }
    for path, (repository_digest, locked_windows_digest) in expected.items():
        normalized = path.read_bytes().replace(b"\r\n", b"\n")
        locked_windows_bytes = normalized.replace(b"\n", b"\r\n")
        assert hashlib.sha256(normalized).hexdigest() == repository_digest
        assert hashlib.sha256(locked_windows_bytes).hexdigest() == locked_windows_digest
