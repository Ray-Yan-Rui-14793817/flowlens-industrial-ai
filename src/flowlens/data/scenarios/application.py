"""Public application boundary for implemented deterministic C04 scenarios."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flowlens.data.generation import GeneratedDataset
from flowlens.data.scenarios.capacity import apply_capacity_surge
from flowlens.data.scenarios.config import (
    CapacitySurgeConfig,
    QualityDeteriorationConfig,
    ScenarioConfig,
    SupplierDegradationConfig,
    scenario_parameters,
)
from flowlens.data.scenarios.quality import apply_quality_deterioration
from flowlens.data.scenarios.supplier import apply_supplier_degradation
from flowlens.data.scenarios.transformer import (
    BusinessScenarioEffects,
    ScenarioIdentity,
    ScenarioResult,
    build_scenario_identity,
    clone_business_rows,
    finalize_scenario_dataset,
)


def _legacy_ground_truth(
    identity: ScenarioIdentity,
    config: ScenarioConfig,
    effects: BusinessScenarioEffects,
) -> Any:
    """Construct protected truth only at the legacy public boundary."""

    from flowlens.data.scenarios.ground_truth import CausalLink, HiddenGroundTruth

    return HiddenGroundTruth(
        schema_version="1.0",
        scenario_id=identity.scenario_id,
        scenario_type=config.scenario_type,
        scenario_version=config.scenario_version,
        scenario_seed=config.scenario_seed,
        baseline_dataset_version_id=identity.baseline_dataset_version_id,
        scenario_dataset_version_id=identity.scenario_dataset_version_id,
        window_start=config.window_start,
        window_end=config.window_end,
        parameters=scenario_parameters(config),
        target_entity_ids=effects.target_entity_ids,
        affected_entities_by_table=effects.affected_entities_by_table,
        causal_chain=tuple(
            CausalLink(
                source_table=item.source_table,
                source_entity_id=item.source_entity_id,
                target_table=item.target_table,
                target_entity_id=item.target_entity_id,
                relationship=item.relationship,
            )
            for item in effects.causal_chain
        ),
    )


def apply_scenario(
    baseline: GeneratedDataset,
    config: ScenarioConfig,
    *,
    generated_at: datetime,
) -> ScenarioResult:
    """Apply one implemented scenario to a detached clone of the C03 baseline."""

    identity = build_scenario_identity(baseline, config)
    rows_by_table = clone_business_rows(baseline, identity)
    if isinstance(config, SupplierDegradationConfig):
        effects = apply_supplier_degradation(
            baseline,
            identity,
            config,
            rows_by_table,
        )
    elif isinstance(config, QualityDeteriorationConfig):
        effects = apply_quality_deterioration(
            baseline,
            identity,
            config,
            rows_by_table,
        )
    elif isinstance(config, CapacitySurgeConfig):
        effects = apply_capacity_surge(
            baseline,
            identity,
            config,
            rows_by_table,
        )
    else:
        raise TypeError("config must be one of the three frozen scenario config types")
    ground_truth = _legacy_ground_truth(identity, config, effects)
    dataset = finalize_scenario_dataset(
        baseline,
        identity,
        rows_by_table,
        generated_at=generated_at,
    )
    return ScenarioResult(dataset=dataset, ground_truth=ground_truth)
