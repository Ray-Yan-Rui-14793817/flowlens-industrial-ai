"""Focused tests for the W02-C04-B/C deterministic scenario foundation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Final, cast

import pytest
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.orm import object_session

import flowlens.data.scenarios as scenario_package
from flowlens.data import Base
from flowlens.data.generation import (
    BUSINESS_TIMEZONE,
    GeneratedDataset,
    GenerationConfig,
    GenerationProfile,
    generate_baseline,
)
from flowlens.data.generation.canonical import (
    CANONICAL_TABLE_ORDER,
    canonical_business_payload,
    canonical_content_hash,
)
from flowlens.data.models import Product
from flowlens.data.scenarios import (
    CapacitySurgeConfig,
    HiddenGroundTruth,
    QualityDeteriorationConfig,
    ScenarioResult,
    ScenarioType,
    SupplierDegradationConfig,
)
from flowlens.data.scenarios.config import (
    canonical_scenario_identity_payload,
    default_demo_window,
    scenario_parameters,
    validate_config_for_baseline_period,
)
from flowlens.data.scenarios.ground_truth import (
    CausalLink,
    GroundTruthParameter,
    canonical_hgt_payload,
)
from flowlens.data.scenarios.transformer import (
    ScenarioIdentity,
    build_scenario_identity,
    clone_business_rows,
    deterministic_rank,
    finalize_scenario_dataset,
)

SCENARIO_VERSION: Final = "1.0.0"
SCENARIO_SEED: Final = 20_260_901
FORBIDDEN_HGT_FIELDS: Final = {
    "affected_entities_by_table",
    "expected_causal_chain",
    "hgt_hash",
    "hgt_id",
    "injected_failure",
    "is_affected",
    "is_anomaly",
    "root_cause",
    "scenario_id",
    "scenario_name",
    "scenario_type",
    "target_label",
    "true_root_cause",
}


def _baseline_config(
    generated_at: datetime = datetime(2026, 8, 24, 9, tzinfo=UTC),
) -> GenerationConfig:
    return GenerationConfig(
        profile=GenerationProfile.TEST,
        seed=20_260_824,
        period_start=date(2026, 1, 1),
        generator_version="0.1.0-c03",
        generated_at=generated_at,
    )


@pytest.fixture(scope="module")
def baseline() -> GeneratedDataset:
    return generate_baseline(_baseline_config())


def _window(day_offset: int = 0) -> tuple[datetime, datetime]:
    start = datetime(2026, 1, 15, tzinfo=BUSINESS_TIMEZONE) + timedelta(days=day_offset)
    return start, start + timedelta(days=28)


def _supplier_config(
    *,
    scenario_seed: int = SCENARIO_SEED,
    scenario_version: str = SCENARIO_VERSION,
    day_offset: int = 0,
    affected_supplier_count: int = 2,
) -> SupplierDegradationConfig:
    window_start, window_end = _window(day_offset)
    return SupplierDegradationConfig(
        scenario_version=scenario_version,
        scenario_seed=scenario_seed,
        window_start=window_start,
        window_end=window_end,
        affected_supplier_count=affected_supplier_count,
    )


def _quality_config() -> QualityDeteriorationConfig:
    window_start, window_end = _window()
    return QualityDeteriorationConfig(
        scenario_version=SCENARIO_VERSION,
        scenario_seed=SCENARIO_SEED,
        window_start=window_start,
        window_end=window_end,
    )


def _capacity_config() -> CapacitySurgeConfig:
    window_start, window_end = _window()
    return CapacitySurgeConfig(
        scenario_version=SCENARIO_VERSION,
        scenario_seed=SCENARIO_SEED,
        window_start=window_start,
        window_end=window_end,
    )


def _ground_truth(
    identity: ScenarioIdentity,
    config: SupplierDegradationConfig,
    *,
    targets: tuple[str, ...] = ("sup-2", "sup-1"),
    affected: dict[str, tuple[str, ...]] | None = None,
    relationship: str = "delayed_receipt_crosses_need_time",
    scenario_type: ScenarioType | None = None,
    scenario_version: str | None = None,
    scenario_seed: int | None = None,
    window_start: datetime | None = None,
    window_end: datetime | None = None,
    parameters: Mapping[str, GroundTruthParameter] | None = None,
) -> HiddenGroundTruth:
    affected_rows = affected or {
        "fact_work_order": ("wo-2", "wo-1"),
        "fact_purchase_order": ("po-2", "po-1"),
    }
    return HiddenGroundTruth(
        schema_version="1.0",
        scenario_id=identity.scenario_id,
        scenario_type=config.scenario_type if scenario_type is None else scenario_type,
        scenario_version=(
            config.scenario_version if scenario_version is None else scenario_version
        ),
        scenario_seed=config.scenario_seed if scenario_seed is None else scenario_seed,
        baseline_dataset_version_id=identity.baseline_dataset_version_id,
        scenario_dataset_version_id=identity.scenario_dataset_version_id,
        window_start=config.window_start if window_start is None else window_start,
        window_end=config.window_end if window_end is None else window_end,
        parameters=scenario_parameters(config) if parameters is None else parameters,
        target_entity_ids=targets,
        affected_entities_by_table=affected_rows,
        causal_chain=(
            CausalLink(
                source_table="fact_purchase_order",
                source_entity_id="po-1",
                target_table="fact_work_order",
                target_entity_id="wo-1",
                relationship=relationship,
            ),
        ),
    )


def _row_values_without_dataset_id(row: Base) -> tuple[tuple[str, object], ...]:
    return tuple(
        (column.name, getattr(row, column.name))
        for column in row.__mapper__.columns
        if column.name != "dataset_version_id"
    )


def _assign_attribute(target: object, field_name: str, value: object) -> None:
    setattr(target, field_name, value)


def test_package_public_api_is_limited_to_stable_domain_types() -> None:
    expected = {
        "ScenarioType",
        "SupplierDegradationConfig",
        "QualityDeteriorationConfig",
        "CapacitySurgeConfig",
        "ScenarioConfig",
        "HiddenGroundTruth",
        "ScenarioResult",
    }
    internal = {
        "ScenarioIdentity",
        "build_scenario_identity",
        "canonical_hgt_payload",
        "canonical_scenario_configuration",
        "canonical_scenario_identity_payload",
        "clone_business_rows",
        "deterministic_rank",
        "finalize_scenario_dataset",
        "scenario_parameters",
        "validate_config_for_baseline_period",
    }
    assert set(scenario_package.__all__) == expected
    assert internal.isdisjoint(scenario_package.__all__)
    assert all(not hasattr(scenario_package, name) for name in internal)


def test_scenario_identity_rejects_every_internally_contradictory_state() -> None:
    namespace = "a" * 64
    valid = ScenarioIdentity(
        baseline_dataset_version_id="dsv_baseline",
        namespace=namespace,
        scenario_id=f"scn_{namespace[:32]}",
        scenario_dataset_version_id=f"dsv_{namespace[:32]}",
    )
    assert valid.namespace == namespace

    with pytest.raises(ValueError, match="baseline_dataset_version_id"):
        ScenarioIdentity("", namespace, f"scn_{namespace[:32]}", f"dsv_{namespace[:32]}")
    with pytest.raises(ValueError, match="baseline_dataset_version_id"):
        ScenarioIdentity(" baseline ", namespace, f"scn_{namespace[:32]}", f"dsv_{namespace[:32]}")
    with pytest.raises(ValueError, match="exactly 64"):
        ScenarioIdentity("baseline", "a" * 63, "scn_short", "dsv_short")
    with pytest.raises(ValueError, match="lowercase hexadecimal"):
        ScenarioIdentity("baseline", "A" * 64, f"scn_{'A' * 32}", f"dsv_{'A' * 32}")
    with pytest.raises(ValueError, match="lowercase hexadecimal"):
        ScenarioIdentity("baseline", "g" * 64, f"scn_{'g' * 32}", f"dsv_{'g' * 32}")
    with pytest.raises(ValueError, match="scenario_id"):
        ScenarioIdentity(
            "baseline",
            namespace,
            f"scn_{'b' * 32}",
            f"dsv_{namespace[:32]}",
        )
    with pytest.raises(ValueError, match="scenario_dataset_version_id"):
        ScenarioIdentity(
            "baseline",
            namespace,
            f"scn_{namespace[:32]}",
            f"dsv_{'b' * 32}",
        )


def test_scenario_inventory_and_frozen_defaults_are_exact() -> None:
    assert {member.value for member in ScenarioType} == {
        "SCN_SUPPLIER_DEGRADATION",
        "SCN_QUALITY_DETERIORATION",
        "SCN_CAPACITY_SURGE",
    }
    supplier = _supplier_config()
    assert (
        supplier.affected_supplier_count,
        supplier.affected_critical_material_count,
        supplier.late_probability_delta,
        supplier.additional_delay_business_days_min,
        supplier.additional_delay_business_days_max,
    ) == (2, 5, Decimal("0.25"), 3, 8)
    quality = _quality_config()
    assert (
        quality.affected_product_count,
        quality.affected_work_center_count,
        quality.failure_probability_multiplier,
        quality.rework_probability_delta,
        quality.rework_duration_multiplier_min,
        quality.rework_duration_multiplier_max,
    ) == (2, 1, Decimal("2.2"), Decimal("0.30"), Decimal("1.2"), Decimal("1.5"))
    capacity = _capacity_config()
    assert (
        capacity.affected_work_center_count,
        capacity.arrival_volume_multiplier,
        capacity.queue_time_multiplier,
    ) == (2, Decimal("1.5"), Decimal("1.7"))


def test_configurations_are_immutable() -> None:
    config = _supplier_config()
    with pytest.raises(FrozenInstanceError):
        _assign_attribute(config, "scenario_seed", 1)


def test_configuration_rejects_invalid_common_values() -> None:
    start, end = _window()
    with pytest.raises(ValueError, match="nonnegative PostgreSQL BIGINT"):
        SupplierDegradationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=-1,
            window_start=start,
            window_end=end,
        )
    with pytest.raises(ValueError, match="scenario_version must be non-empty"):
        SupplierDegradationConfig(
            scenario_version="",
            scenario_seed=1,
            window_start=start,
            window_end=end,
        )
    with pytest.raises(ValueError, match="timezone-aware"):
        SupplierDegradationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=1,
            window_start=datetime(2026, 1, 1),
            window_end=end,
        )
    with pytest.raises(ValueError, match="Asia/Shanghai"):
        SupplierDegradationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=1,
            window_start=datetime(2026, 1, 1, tzinfo=UTC),
            window_end=datetime(2026, 2, 1, tzinfo=UTC),
        )
    with pytest.raises(ValueError, match="window_start < window_end"):
        SupplierDegradationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=1,
            window_start=start,
            window_end=start,
        )


def test_configuration_rejects_invalid_scenario_parameters() -> None:
    start, end = _window()
    with pytest.raises(ValueError, match="affected_supplier_count must be positive"):
        SupplierDegradationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=1,
            window_start=start,
            window_end=end,
            affected_supplier_count=0,
        )
    with pytest.raises(ValueError, match="between 0 and 1"):
        SupplierDegradationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=1,
            window_start=start,
            window_end=end,
            late_probability_delta=Decimal("1.01"),
        )
    with pytest.raises(ValueError, match="minimum must not exceed maximum"):
        SupplierDegradationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=1,
            window_start=start,
            window_end=end,
            additional_delay_business_days_min=9,
            additional_delay_business_days_max=8,
        )
    with pytest.raises(ValueError, match="at least 1"):
        QualityDeteriorationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=1,
            window_start=start,
            window_end=end,
            failure_probability_multiplier=Decimal("0.9"),
        )
    with pytest.raises(ValueError, match="minimum must not exceed maximum"):
        QualityDeteriorationConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=1,
            window_start=start,
            window_end=end,
            rework_duration_multiplier_min=Decimal("1.6"),
            rework_duration_multiplier_max=Decimal("1.5"),
        )
    with pytest.raises(ValueError, match="at least 1"):
        CapacitySurgeConfig(
            scenario_version=SCENARIO_VERSION,
            scenario_seed=1,
            window_start=start,
            window_end=end,
            arrival_volume_multiplier=Decimal("0.9"),
        )


def test_demo_windows_are_exact_and_short_profiles_require_explicit_windows() -> None:
    period_start = date(2026, 1, 1)
    assert default_demo_window(
        ScenarioType.SUPPLIER_DEGRADATION,
        period_start,
        GenerationProfile.DEMO,
    ) == (
        datetime(2026, 5, 1, tzinfo=BUSINESS_TIMEZONE),
        datetime(2026, 9, 1, tzinfo=BUSINESS_TIMEZONE),
    )
    assert default_demo_window(
        ScenarioType.QUALITY_DETERIORATION,
        period_start,
        GenerationProfile.DEMO,
    ) == (
        datetime(2026, 9, 1, tzinfo=BUSINESS_TIMEZONE),
        datetime(2026, 12, 1, tzinfo=BUSINESS_TIMEZONE),
    )
    assert default_demo_window(
        ScenarioType.CAPACITY_SURGE,
        period_start,
        GenerationProfile.DEMO,
    ) == (
        datetime(2027, 1, 1, tzinfo=BUSINESS_TIMEZONE),
        datetime(2027, 4, 1, tzinfo=BUSINESS_TIMEZONE),
    )
    with pytest.raises(ValueError, match="only for the DEMO profile"):
        default_demo_window(
            ScenarioType.SUPPLIER_DEGRADATION,
            period_start,
            GenerationProfile.TEST,
        )


def test_baseline_period_containment_rejects_outside_windows() -> None:
    validate_config_for_baseline_period(_supplier_config(), date(2026, 1, 1), date(2026, 3, 31))
    start = datetime(2025, 12, 31, tzinfo=BUSINESS_TIMEZONE)
    outside = SupplierDegradationConfig(
        scenario_version=SCENARIO_VERSION,
        scenario_seed=SCENARIO_SEED,
        window_start=start,
        window_end=start + timedelta(days=10),
    )
    with pytest.raises(ValueError, match="inside the baseline business period"):
        validate_config_for_baseline_period(outside, date(2026, 1, 1), date(2026, 3, 31))


def test_scenario_identity_is_deterministic_and_sensitive_to_every_identity_input(
    baseline: GeneratedDataset,
) -> None:
    config = _supplier_config()
    identity = build_scenario_identity(baseline, config)
    assert build_scenario_identity(baseline, config) == identity
    assert identity.scenario_id == f"scn_{identity.namespace[:32]}"
    assert identity.scenario_dataset_version_id == f"dsv_{identity.namespace[:32]}"
    assert len(identity.namespace) == 64
    assert build_scenario_identity(baseline, _supplier_config(scenario_seed=2)) != identity
    assert build_scenario_identity(
        baseline,
        _supplier_config(scenario_version="1.0.1"),
    ) != identity
    assert build_scenario_identity(baseline, _supplier_config(day_offset=1)) != identity
    assert build_scenario_identity(
        baseline,
        _supplier_config(affected_supplier_count=3),
    ) != identity
    assert build_scenario_identity(baseline, _quality_config()) != identity
    assert deterministic_rank(identity, "entity-1") == deterministic_rank(identity, "entity-1")
    assert deterministic_rank(identity, "entity-1") != deterministic_rank(identity, "entity-2")


def test_scenario_identity_payload_is_canonical_and_generated_at_independent(
    baseline: GeneratedDataset,
) -> None:
    config = _supplier_config()
    same_business_baseline = generate_baseline(
        _baseline_config(datetime(2035, 1, 1, tzinfo=UTC))
    )
    assert baseline.dataset_version.generated_at != (
        same_business_baseline.dataset_version.generated_at
    )
    assert build_scenario_identity(baseline, config) == build_scenario_identity(
        same_business_baseline,
        config,
    )
    payload = canonical_scenario_identity_payload(
        baseline.dataset_version.dataset_version_id,
        config,
    )
    assert payload == canonical_scenario_identity_payload(
        baseline.dataset_version.dataset_version_id,
        config,
    )
    assert "generated_at" not in payload
    assert "0.25" in payload


def test_hidden_ground_truth_is_order_invariant_sensitive_and_immutable(
    baseline: GeneratedDataset,
) -> None:
    config = _supplier_config()
    identity = build_scenario_identity(baseline, config)
    first = _ground_truth(identity, config)
    reordered = _ground_truth(
        identity,
        config,
        targets=("sup-1", "sup-2", "sup-1"),
        affected={
            "fact_purchase_order": ("po-1", "po-2", "po-1"),
            "fact_work_order": ("wo-1", "wo-2"),
        },
    )
    assert canonical_hgt_payload(first) == canonical_hgt_payload(reordered)
    assert first.hgt_hash == reordered.hgt_hash
    assert first.hgt_id == reordered.hgt_id == f"hgt_{first.hgt_hash[:32]}"
    assert len(first.hgt_hash) == 64
    changed = _ground_truth(identity, config, relationship="different_semantic_link")
    assert changed.hgt_hash != first.hgt_hash
    assert first.target_entity_ids == ("sup-1", "sup-2")
    with pytest.raises(TypeError):
        cast(dict[str, object], first.parameters)["new"] = "forbidden"
    with pytest.raises(TypeError):
        cast(dict[str, object], first.affected_entities_by_table)["new"] = ()
    with pytest.raises(FrozenInstanceError):
        _assign_attribute(first, "scenario_seed", 7)
    assert "generated_at" not in canonical_hgt_payload(first)


def test_hgt_semantics_are_cryptographically_bound_to_scenario_identity(
    baseline: GeneratedDataset,
) -> None:
    config = _supplier_config()
    identity = build_scenario_identity(baseline, config)
    assert _ground_truth(identity, config).scenario_id == identity.scenario_id

    quality_parameters = scenario_parameters(_quality_config())
    with pytest.raises(ValueError, match="canonical HGT scenario semantics"):
        _ground_truth(
            identity,
            config,
            scenario_type=ScenarioType.QUALITY_DETERIORATION,
            parameters=quality_parameters,
        )
    with pytest.raises(ValueError, match="canonical HGT scenario semantics"):
        _ground_truth(identity, config, scenario_version="1.0.1")
    with pytest.raises(ValueError, match="canonical HGT scenario semantics"):
        _ground_truth(identity, config, scenario_seed=config.scenario_seed + 1)
    with pytest.raises(ValueError, match="canonical HGT scenario semantics"):
        _ground_truth(
            identity,
            config,
            window_start=config.window_start + timedelta(days=1),
        )
    with pytest.raises(ValueError, match="canonical HGT scenario semantics"):
        _ground_truth(
            identity,
            config,
            window_end=config.window_end + timedelta(days=1),
        )

    changed_parameters = dict(scenario_parameters(config))
    changed_parameters["affected_supplier_count"] = 3
    with pytest.raises(ValueError, match="canonical HGT scenario semantics"):
        _ground_truth(identity, config, parameters=changed_parameters)
    with pytest.raises(ValueError, match="parameter set mismatch"):
        _ground_truth(identity, config, parameters=quality_parameters)

    invalid_parameters = dict(scenario_parameters(config))
    invalid_parameters["affected_supplier_count"] = 0
    with pytest.raises(ValueError, match="affected_supplier_count must be positive"):
        _ground_truth(identity, config, parameters=invalid_parameters)

    missing_parameter = dict(scenario_parameters(config))
    del missing_parameter["late_probability_delta"]
    with pytest.raises(ValueError, match="parameter set mismatch"):
        _ground_truth(identity, config, parameters=missing_parameter)
    extra_parameter = dict(scenario_parameters(config))
    extra_parameter["unexpected"] = 1
    with pytest.raises(ValueError, match="parameter set mismatch"):
        _ground_truth(identity, config, parameters=extra_parameter)


def test_hgt_is_separate_from_business_rows_and_scenario_result_enforces_identity(
    baseline: GeneratedDataset,
) -> None:
    config = _supplier_config()
    identity = build_scenario_identity(baseline, config)
    cloned = clone_business_rows(baseline, identity)
    scenario = finalize_scenario_dataset(
        baseline,
        identity,
        cloned,
        generated_at=datetime(2026, 9, 1, tzinfo=UTC),
    )
    ground_truth = _ground_truth(identity, config)
    result = ScenarioResult(dataset=scenario, ground_truth=ground_truth)
    assert result.dataset is scenario
    assert result.ground_truth is ground_truth
    assert all(
        FORBIDDEN_HGT_FIELDS.isdisjoint(row.__mapper__.columns.keys())
        for _, row in scenario.iter_business_rows()
    )
    assert set(scenario.rows_by_table) == set(CANONICAL_TABLE_ORDER)

    with pytest.raises(ValueError, match="canonical HGT scenario semantics"):
        HiddenGroundTruth(
            schema_version="1.0",
            scenario_id="scn_00000000000000000000000000000000",
            scenario_type=config.scenario_type,
            scenario_version=config.scenario_version,
            scenario_seed=config.scenario_seed,
            baseline_dataset_version_id=identity.baseline_dataset_version_id,
            scenario_dataset_version_id=identity.scenario_dataset_version_id,
            window_start=config.window_start,
            window_end=config.window_end,
            parameters=scenario_parameters(config),
            target_entity_ids=(),
            affected_entities_by_table={},
            causal_chain=(),
        )


def test_cloning_is_complete_detached_and_preserves_baseline_entity_values(
    baseline: GeneratedDataset,
) -> None:
    identity = build_scenario_identity(baseline, _supplier_config())
    cloned = clone_business_rows(baseline, identity)
    assert tuple(cloned) == CANONICAL_TABLE_ORDER
    assert sum(map(len, cloned.values())) == baseline.row_count_total

    for table_name in CANONICAL_TABLE_ORDER:
        baseline_rows = baseline.rows_by_table[table_name]
        cloned_rows = cloned[table_name]
        assert len(cloned_rows) == len(baseline_rows)
        for baseline_row, cloned_row in zip(baseline_rows, cloned_rows, strict=True):
            assert cloned_row is not baseline_row
            assert sqlalchemy_inspect(cloned_row) is not sqlalchemy_inspect(baseline_row)
            assert object_session(cloned_row) is None
            assert object_session(baseline_row) is None
            assert _row_values_without_dataset_id(cloned_row) == (
                _row_values_without_dataset_id(baseline_row)
            )
            assert cloned_row.__dict__["dataset_version_id"] == (
                identity.scenario_dataset_version_id
            )
            assert baseline_row.__dict__["dataset_version_id"] == (
                baseline.dataset_version.dataset_version_id
            )

    baseline_product = cast(Product, baseline.rows_by_table["dim_product"][0])
    cloned_product = cast(Product, cloned["dim_product"][0])
    baseline_name = baseline_product.model_name
    cloned_product.model_name = "mutated clone only"
    assert baseline_product.model_name == baseline_name
    assert cloned_product.model_name != baseline_product.model_name


def test_full_baseline_payload_and_metadata_remain_unchanged_after_finalization(
    baseline: GeneratedDataset,
) -> None:
    payload_before = canonical_business_payload(baseline.rows_by_table)
    hash_before = baseline.content_hash
    count_before = baseline.row_count_total
    dataset_id_before = baseline.dataset_version.dataset_version_id
    identity = build_scenario_identity(baseline, _supplier_config())
    cloned = clone_business_rows(baseline, identity)
    scenario = finalize_scenario_dataset(
        baseline,
        identity,
        cloned,
        generated_at=datetime(2026, 9, 1, tzinfo=UTC),
    )

    assert canonical_business_payload(baseline.rows_by_table) == payload_before
    assert baseline.content_hash == hash_before
    assert baseline.row_count_total == count_before
    assert baseline.dataset_version.dataset_version_id == dataset_id_before
    assert scenario.dataset_version is not baseline.dataset_version


def test_finalization_recomputes_canonical_metadata_without_intervention(
    baseline: GeneratedDataset,
) -> None:
    identity = build_scenario_identity(baseline, _supplier_config())
    cloned = clone_business_rows(baseline, identity)
    reversed_clone = {
        table_name: list(reversed(rows))
        for table_name, rows in reversed(tuple(cloned.items()))
    }
    scenario = finalize_scenario_dataset(
        baseline,
        identity,
        reversed_clone,
        generated_at=datetime(2026, 9, 1, tzinfo=UTC),
    )
    assert scenario.dataset_version.dataset_version_id == identity.scenario_dataset_version_id
    assert scenario.dataset_version.dataset_version_id != (
        baseline.dataset_version.dataset_version_id
    )
    assert scenario.row_count_total == sum(len(rows) for rows in scenario.rows_by_table.values())
    assert scenario.row_count_total == baseline.row_count_total
    assert scenario.content_hash == canonical_content_hash(scenario.rows_by_table)
    assert scenario.content_hash != baseline.content_hash
    assert tuple(scenario.rows_by_table) == CANONICAL_TABLE_ORDER
    assert scenario.dataset_version.seed == baseline.dataset_version.seed
    assert scenario.dataset_version.generator_version == baseline.dataset_version.generator_version
    assert scenario.dataset_version.profile == baseline.dataset_version.profile
    assert scenario.dataset_version.period_start == baseline.dataset_version.period_start
    assert scenario.dataset_version.period_end == baseline.dataset_version.period_end

    for table_name in CANONICAL_TABLE_ORDER:
        for baseline_row, scenario_row in zip(
            baseline.rows_by_table[table_name],
            scenario.rows_by_table[table_name],
            strict=True,
        ):
            assert _row_values_without_dataset_id(scenario_row) == (
                _row_values_without_dataset_id(baseline_row)
            )


def test_generated_at_does_not_change_identity_rows_hash_count_or_hgt(
    baseline: GeneratedDataset,
) -> None:
    config = _supplier_config()
    identity = build_scenario_identity(baseline, config)
    first = finalize_scenario_dataset(
        baseline,
        identity,
        clone_business_rows(baseline, identity),
        generated_at=datetime(2026, 9, 1, tzinfo=UTC),
    )
    second = finalize_scenario_dataset(
        baseline,
        identity,
        clone_business_rows(baseline, identity),
        generated_at=datetime(2035, 9, 1, tzinfo=UTC),
    )
    first_hgt = _ground_truth(identity, config)
    second_hgt = _ground_truth(identity, config)
    assert first.dataset_version.generated_at != second.dataset_version.generated_at
    assert canonical_business_payload(first.rows_by_table) == canonical_business_payload(
        second.rows_by_table
    )
    assert first.row_count_total == second.row_count_total
    assert first.content_hash == second.content_hash
    assert first_hgt.hgt_id == second_hgt.hgt_id
    assert first_hgt.hgt_hash == second_hgt.hgt_hash
    assert identity.scenario_id == first_hgt.scenario_id


def test_finalize_rejects_shared_rows_and_naive_generated_at(
    baseline: GeneratedDataset,
) -> None:
    identity = build_scenario_identity(baseline, _supplier_config())
    with pytest.raises(ValueError, match="must not share ORM rows"):
        finalize_scenario_dataset(
            baseline,
            identity,
            baseline.rows_by_table,
            generated_at=datetime(2026, 9, 1, tzinfo=UTC),
        )
    with pytest.raises(ValueError, match="timezone-aware"):
        finalize_scenario_dataset(
            baseline,
            identity,
            clone_business_rows(baseline, identity),
            generated_at=datetime(2026, 9, 1),
        )
