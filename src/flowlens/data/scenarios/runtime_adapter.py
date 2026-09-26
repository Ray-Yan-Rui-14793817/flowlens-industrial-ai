"""HGT-free in-memory business transformation boundary for W03-C04."""

from __future__ import annotations

from datetime import datetime

from flowlens.data.generation import GeneratedDataset
from flowlens.data.scenarios.capacity import apply_capacity_surge
from flowlens.data.scenarios.config import (
    CapacitySurgeConfig,
    QualityDeteriorationConfig,
    ScenarioConfig,
    SupplierDegradationConfig,
)
from flowlens.data.scenarios.quality import apply_quality_deterioration
from flowlens.data.scenarios.supplier import apply_supplier_degradation
from flowlens.data.scenarios.transformer import (
    build_scenario_identity,
    clone_business_rows,
    finalize_scenario_dataset,
)


def apply_scenario_business_only(
    baseline: GeneratedDataset,
    config: ScenarioConfig,
    *,
    generated_at: datetime,
) -> GeneratedDataset:
    """Apply frozen W2 business semantics without constructing protected truth."""

    identity = build_scenario_identity(baseline, config)
    rows_by_table = clone_business_rows(baseline, identity)
    if isinstance(config, SupplierDegradationConfig):
        apply_supplier_degradation(baseline, identity, config, rows_by_table)
    elif isinstance(config, QualityDeteriorationConfig):
        apply_quality_deterioration(baseline, identity, config, rows_by_table)
    elif isinstance(config, CapacitySurgeConfig):
        apply_capacity_surge(baseline, identity, config, rows_by_table)
    else:
        raise TypeError("config must be one of the three frozen scenario config types")
    return finalize_scenario_dataset(
        baseline,
        identity,
        rows_by_table,
        generated_at=generated_at,
    )
