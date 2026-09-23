"""Public foundation API for deterministic C04 scenario transformations."""

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
