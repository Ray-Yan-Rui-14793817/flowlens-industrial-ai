"""Immutable in-memory Hidden Ground Truth and deterministic identity."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType

from flowlens.data.generation.canonical import normalize_scalar
from flowlens.data.scenarios.config import (
    ScenarioType,
    scenario_config_from_parameters,
    scenario_namespace,
)

type GroundTruthParameter = None | bool | int | str | Decimal


def _require_nonempty(field_name: str, value: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{field_name} must be non-empty without surrounding whitespace")


def _validate_prefixed_digest(field_name: str, value: str, prefix: str) -> None:
    _require_nonempty(field_name, value)
    digest = value.removeprefix(prefix)
    if not value.startswith(prefix) or len(digest) != 32:
        raise ValueError(f"{field_name} must use the frozen {prefix}<32-hex> format")
    if digest != digest.lower() or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError(f"{field_name} must contain lowercase hexadecimal characters")


@dataclass(frozen=True, slots=True, order=True)
class CausalLink:
    """One deterministic evaluation-truth edge in an injected causal chain."""

    source_table: str
    source_entity_id: str
    target_table: str
    target_entity_id: str
    relationship: str

    def __post_init__(self) -> None:
        for field_name in (
            "source_table",
            "source_entity_id",
            "target_table",
            "target_entity_id",
            "relationship",
        ):
            _require_nonempty(field_name, getattr(self, field_name))


def _canonical_parameter(value: GroundTruthParameter) -> None | bool | int | str:
    if isinstance(value, Decimal):
        return normalize_scalar(value)
    if value is None or isinstance(value, (bool, int, str)):
        return value
    raise TypeError(f"unsupported HGT parameter type: {type(value).__name__}")


@dataclass(frozen=True, slots=True, kw_only=True)
class HiddenGroundTruth:
    """Protected evaluation truth, structurally separate from operational rows."""

    schema_version: str
    scenario_id: str
    scenario_type: ScenarioType
    scenario_version: str
    scenario_seed: int
    baseline_dataset_version_id: str
    scenario_dataset_version_id: str
    window_start: datetime
    window_end: datetime
    parameters: Mapping[str, GroundTruthParameter]
    target_entity_ids: tuple[str, ...]
    affected_entities_by_table: Mapping[str, tuple[str, ...]]
    causal_chain: tuple[CausalLink, ...]
    hgt_id: str = field(init=False)
    hgt_hash: str = field(init=False)

    def __post_init__(self) -> None:
        _require_nonempty("schema_version", self.schema_version)
        _validate_prefixed_digest("scenario_id", self.scenario_id, "scn_")
        _require_nonempty(
            "baseline_dataset_version_id",
            self.baseline_dataset_version_id,
        )
        _validate_prefixed_digest(
            "scenario_dataset_version_id",
            self.scenario_dataset_version_id,
            "dsv_",
        )

        canonical_parameters = {
            key: self.parameters[key]
            for key in sorted(self.parameters)
        }
        for key, parameter_value in canonical_parameters.items():
            _require_nonempty("parameter name", key)
            _canonical_parameter(parameter_value)
        validated_config = scenario_config_from_parameters(
            scenario_type=self.scenario_type,
            scenario_version=self.scenario_version,
            scenario_seed=self.scenario_seed,
            window_start=self.window_start,
            window_end=self.window_end,
            parameters=canonical_parameters,
        )
        expected_namespace = scenario_namespace(
            self.baseline_dataset_version_id,
            validated_config,
        )
        if self.scenario_id != f"scn_{expected_namespace[:32]}":
            raise ValueError("scenario_id does not match canonical HGT scenario semantics")
        if self.scenario_dataset_version_id != f"dsv_{expected_namespace[:32]}":
            raise ValueError(
                "scenario_dataset_version_id does not match canonical HGT scenario semantics"
            )
        targets = tuple(sorted(set(self.target_entity_ids)))
        for target in targets:
            _require_nonempty("target_entity_id", target)
        affected: dict[str, tuple[str, ...]] = {}
        for table_name in sorted(self.affected_entities_by_table):
            _require_nonempty("affected table name", table_name)
            entity_ids = tuple(sorted(set(self.affected_entities_by_table[table_name])))
            for entity_id in entity_ids:
                _require_nonempty("affected entity ID", entity_id)
            affected[table_name] = entity_ids
        causal_chain = tuple(sorted(set(self.causal_chain)))

        object.__setattr__(self, "parameters", MappingProxyType(canonical_parameters))
        object.__setattr__(self, "target_entity_ids", targets)
        object.__setattr__(
            self,
            "affected_entities_by_table",
            MappingProxyType(affected),
        )
        object.__setattr__(self, "causal_chain", causal_chain)

        payload = _canonical_hgt_base_payload(self)
        hgt_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        object.__setattr__(self, "hgt_hash", hgt_hash)
        object.__setattr__(self, "hgt_id", f"hgt_{hgt_hash[:32]}")


def _canonical_hgt_base_payload(ground_truth: HiddenGroundTruth) -> str:
    payload = {
        "affected_entities_by_table": {
            table_name: list(entity_ids)
            for table_name, entity_ids in ground_truth.affected_entities_by_table.items()
        },
        "baseline_dataset_version_id": ground_truth.baseline_dataset_version_id,
        "causal_chain": [
            {
                "relationship": link.relationship,
                "source_entity_id": link.source_entity_id,
                "source_table": link.source_table,
                "target_entity_id": link.target_entity_id,
                "target_table": link.target_table,
            }
            for link in ground_truth.causal_chain
        ],
        "parameters": {
            key: _canonical_parameter(value)
            for key, value in ground_truth.parameters.items()
        },
        "scenario_dataset_version_id": ground_truth.scenario_dataset_version_id,
        "scenario_id": ground_truth.scenario_id,
        "scenario_seed": ground_truth.scenario_seed,
        "scenario_type": ground_truth.scenario_type.value,
        "scenario_version": ground_truth.scenario_version,
        "schema_version": ground_truth.schema_version,
        "target_entity_ids": list(ground_truth.target_entity_ids),
        "window_end": normalize_scalar(ground_truth.window_end),
        "window_start": normalize_scalar(ground_truth.window_start),
    }
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def canonical_hgt_payload(ground_truth: HiddenGroundTruth) -> str:
    """Return the canonical semantic payload used by the frozen HGT hash."""

    return _canonical_hgt_base_payload(ground_truth)
