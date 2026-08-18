"""Deterministic identity, detached cloning, and scenario finalization primitives."""

from __future__ import annotations

import copy
import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType

from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.orm import object_session

from flowlens.data import Base
from flowlens.data.generation import GeneratedDataset
from flowlens.data.generation.canonical import (
    CANONICAL_TABLE_ORDER,
    canonical_content_hash,
    canonicalize_rows,
)
from flowlens.data.models import DatasetVersion
from flowlens.data.scenarios.config import (
    ScenarioConfig,
    scenario_namespace,
    validate_config_for_baseline_period,
)
from flowlens.data.scenarios.ground_truth import HiddenGroundTruth


@dataclass(frozen=True, slots=True)
class ScenarioIdentity:
    """The deterministic namespace and both frozen scenario identifiers."""

    baseline_dataset_version_id: str
    namespace: str
    scenario_id: str
    scenario_dataset_version_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.baseline_dataset_version_id, str):
            raise TypeError("baseline_dataset_version_id must be a string")
        if not self.baseline_dataset_version_id or self.baseline_dataset_version_id != (
            self.baseline_dataset_version_id.strip()
        ):
            raise ValueError(
                "baseline_dataset_version_id must be non-empty without surrounding whitespace"
            )
        if not isinstance(self.namespace, str):
            raise TypeError("namespace must be a string")
        if len(self.namespace) != 64:
            raise ValueError("namespace must contain exactly 64 hexadecimal characters")
        if self.namespace != self.namespace.lower():
            raise ValueError("namespace must be lowercase hexadecimal")
        if any(character not in "0123456789abcdef" for character in self.namespace):
            raise ValueError("namespace must be lowercase hexadecimal")
        expected_suffix = self.namespace[:32]
        if self.scenario_id != f"scn_{expected_suffix}":
            raise ValueError("scenario_id must match the scenario namespace")
        if self.scenario_dataset_version_id != f"dsv_{expected_suffix}":
            raise ValueError("scenario_dataset_version_id must match the scenario namespace")


def build_scenario_identity(
    baseline: GeneratedDataset,
    config: ScenarioConfig,
) -> ScenarioIdentity:
    """Validate the baseline window and derive the frozen SHA-256 namespace."""

    validate_config_for_baseline_period(
        config,
        baseline.dataset_version.period_start,
        baseline.dataset_version.period_end,
    )
    baseline_id = baseline.dataset_version.dataset_version_id
    namespace = scenario_namespace(baseline_id, config)
    return ScenarioIdentity(
        baseline_dataset_version_id=baseline_id,
        namespace=namespace,
        scenario_id=f"scn_{namespace[:32]}",
        scenario_dataset_version_id=f"dsv_{namespace[:32]}",
    )


def deterministic_rank(identity: ScenarioIdentity, entity_identity: str) -> str:
    """Return a stable future selection rank independent from C03 RNG state."""

    if not entity_identity or entity_identity != entity_identity.strip():
        raise ValueError("entity_identity must be non-empty")
    payload = f"{identity.namespace}:{entity_identity}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clone_row(row: Base, scenario_dataset_version_id: str) -> Base:
    values = {
        column.name: (
            scenario_dataset_version_id
            if column.name == "dataset_version_id"
            else copy.deepcopy(getattr(row, column.name))
        )
        for column in row.__mapper__.columns
    }
    clone = type(row)(**values)
    if clone is row or sqlalchemy_inspect(clone) is sqlalchemy_inspect(row):
        raise AssertionError("detached cloning must create independent ORM instrumentation")
    if object_session(clone) is not None:
        raise AssertionError("scenario clones must remain detached from database sessions")
    return clone


def clone_business_rows(
    baseline: GeneratedDataset,
    identity: ScenarioIdentity,
) -> dict[str, list[Base]]:
    """Clone every canonical business row into a mutable, fully detached graph."""

    if identity.baseline_dataset_version_id != baseline.dataset_version.dataset_version_id:
        raise ValueError("scenario identity does not belong to the supplied baseline")
    canonical_baseline = canonicalize_rows(baseline.rows_by_table)
    return {
        table_name: [
            _clone_row(row, identity.scenario_dataset_version_id)
            for row in canonical_baseline[table_name]
        ]
        for table_name in CANONICAL_TABLE_ORDER
    }


def finalize_scenario_dataset(
    baseline: GeneratedDataset,
    identity: ScenarioIdentity,
    rows_by_table: Mapping[str, Sequence[Base]],
    *,
    generated_at: datetime,
) -> GeneratedDataset:
    """Canonically finalize an already-cloned graph after a future intervention."""

    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must be timezone-aware")
    if identity.baseline_dataset_version_id != baseline.dataset_version.dataset_version_id:
        raise ValueError("scenario identity does not belong to the supplied baseline")

    ordered = canonicalize_rows(rows_by_table)
    baseline_object_ids = {
        id(row)
        for table_name in CANONICAL_TABLE_ORDER
        for row in baseline.rows_by_table[table_name]
    }
    scenario_object_ids = {
        id(row)
        for table_name in CANONICAL_TABLE_ORDER
        for row in ordered[table_name]
    }
    if baseline_object_ids & scenario_object_ids:
        raise ValueError("scenario graph must not share ORM rows with the baseline")
    for table_name in CANONICAL_TABLE_ORDER:
        for row in ordered[table_name]:
            if object_session(row) is not None:
                raise ValueError("scenario rows must remain detached from database sessions")
            if row.__dict__.get("dataset_version_id") != identity.scenario_dataset_version_id:
                raise ValueError("every scenario row must reference the scenario dataset ID")

    row_count_total = sum(len(rows) for rows in ordered.values())
    content_hash = canonical_content_hash(ordered)
    baseline_metadata = baseline.dataset_version
    dataset_version = DatasetVersion(
        dataset_version_id=identity.scenario_dataset_version_id,
        seed=baseline_metadata.seed,
        generator_version=baseline_metadata.generator_version,
        profile=baseline_metadata.profile,
        period_start=baseline_metadata.period_start,
        period_end=baseline_metadata.period_end,
        generated_at=generated_at,
        content_hash=content_hash,
        row_count_total=row_count_total,
    )
    return GeneratedDataset(dataset_version, MappingProxyType(ordered))


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    """Keep finalized operational scenario data separate from evaluation truth."""

    dataset: GeneratedDataset
    ground_truth: HiddenGroundTruth

    def __post_init__(self) -> None:
        if (
            self.dataset.dataset_version.dataset_version_id
            != self.ground_truth.scenario_dataset_version_id
        ):
            raise ValueError("scenario dataset and Hidden Ground Truth identities differ")
