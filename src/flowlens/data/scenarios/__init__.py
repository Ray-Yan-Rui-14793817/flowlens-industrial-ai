"""Lazy public API for deterministic W2 scenario transformations."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flowlens.data.scenarios.application import apply_scenario
    from flowlens.data.scenarios.config import (
        CapacitySurgeConfig,
        QualityDeteriorationConfig,
        ScenarioConfig,
        ScenarioType,
        SupplierDegradationConfig,
    )
    from flowlens.data.scenarios.ground_truth import HiddenGroundTruth
    from flowlens.data.scenarios.transformer import ScenarioResult

__all__ = [
    "CapacitySurgeConfig",
    "HiddenGroundTruth",
    "QualityDeteriorationConfig",
    "ScenarioConfig",
    "ScenarioResult",
    "ScenarioType",
    "SupplierDegradationConfig",
    "apply_scenario",
]

_EXPORT_MODULES = {
    "CapacitySurgeConfig": "flowlens.data.scenarios.config",
    "HiddenGroundTruth": "flowlens.data.scenarios.ground_truth",
    "QualityDeteriorationConfig": "flowlens.data.scenarios.config",
    "ScenarioConfig": "flowlens.data.scenarios.config",
    "ScenarioResult": "flowlens.data.scenarios.transformer",
    "ScenarioType": "flowlens.data.scenarios.config",
    "SupplierDegradationConfig": "flowlens.data.scenarios.config",
    "apply_scenario": "flowlens.data.scenarios.application",
}


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(name)
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
