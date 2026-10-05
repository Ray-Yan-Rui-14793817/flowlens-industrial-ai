"""Compatibility proof for the HGT-free W2 business transformation boundary."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import Any, cast

import pytest

from flowlens.data.generation import GeneratedDataset
from flowlens.data.generation.canonical import canonical_business_payload
from flowlens.data.models import QualityInspection
from flowlens.data.scenarios import ScenarioConfig, apply_scenario
from flowlens.data.scenarios.ground_truth import canonical_hgt_payload
from flowlens.data.scenarios.runtime_adapter import apply_scenario_business_only
from flowlens.data.scenarios.transformer import ScenarioPreconditionUnavailable
from test_capacity_scenario import _config as _accepted_capacity_config
from test_capacity_scenario import baseline as _capacity_baseline_fixture
from test_scenario_interventions import (
    GENERATED_AT,
    _baseline,
    _quality_config,
    _supplier_config,
)


def _capacity_baseline() -> GeneratedDataset:
    fixture_factory = cast(
        Callable[[], GeneratedDataset],
        cast(Any, _capacity_baseline_fixture).__wrapped__,
    )
    return fixture_factory()


@pytest.mark.parametrize(
    ("baseline_factory", "config"),
    [
        (_baseline, _supplier_config()),
        (_baseline, _quality_config()),
        (_capacity_baseline, _accepted_capacity_config()),
    ],
    ids=("supplier", "quality", "capacity"),
)
def test_business_adapter_exactly_preserves_legacy_dataset_and_hgt_behavior(
    baseline_factory: Callable[[], GeneratedDataset], config: ScenarioConfig
) -> None:
    baseline = baseline_factory()
    before_payload = canonical_business_payload(baseline.rows_by_table)
    before_hash = baseline.content_hash
    before_count = baseline.row_count_total

    first = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    repeated = apply_scenario(
        baseline,
        config,
        generated_at=GENERATED_AT + timedelta(days=100),
    )
    business_only = apply_scenario_business_only(
        baseline,
        config,
        generated_at=GENERATED_AT,
    )

    assert isinstance(business_only, GeneratedDataset)
    assert business_only.dataset_version.dataset_version_id == (
        first.dataset.dataset_version.dataset_version_id
    )
    assert business_only.content_hash == first.dataset.content_hash
    assert business_only.row_count_total == first.dataset.row_count_total
    assert canonical_business_payload(business_only.rows_by_table) == (
        canonical_business_payload(first.dataset.rows_by_table)
    )
    assert first.ground_truth.scenario_id == repeated.ground_truth.scenario_id
    assert first.ground_truth.hgt_id == repeated.ground_truth.hgt_id
    assert first.ground_truth.hgt_hash == repeated.ground_truth.hgt_hash
    assert canonical_hgt_payload(first.ground_truth) == canonical_hgt_payload(repeated.ground_truth)
    assert first.dataset.content_hash == repeated.dataset.content_hash
    assert canonical_business_payload(baseline.rows_by_table) == before_payload
    assert baseline.content_hash == before_hash
    assert baseline.row_count_total == before_count


@pytest.mark.parametrize(
    ("arrival", "queue"),
    [
        ("1.5", "1.7"),
        ("1.5", "1"),
        ("1", "1.7"),
        ("1", "1"),
    ],
    ids=("combined", "arrival-only", "queue-only", "neutral"),
)
def test_capacity_all_accepted_modes_preserve_business_and_hgt_compatibility(
    arrival: str, queue: str
) -> None:
    baseline = _capacity_baseline()
    config = _accepted_capacity_config(arrival, queue)
    before_payload = canonical_business_payload(baseline.rows_by_table)
    before_hash = baseline.content_hash
    before_count = baseline.row_count_total

    legacy = apply_scenario(baseline, config, generated_at=GENERATED_AT)
    repeated = apply_scenario(
        baseline,
        config,
        generated_at=GENERATED_AT + timedelta(days=100),
    )
    business_only = apply_scenario_business_only(
        baseline,
        config,
        generated_at=GENERATED_AT,
    )

    assert business_only.dataset_version.dataset_version_id == (
        legacy.dataset.dataset_version.dataset_version_id
    )
    assert business_only.content_hash == legacy.dataset.content_hash
    assert business_only.row_count_total == legacy.dataset.row_count_total
    assert canonical_business_payload(business_only.rows_by_table) == (
        canonical_business_payload(legacy.dataset.rows_by_table)
    )
    assert legacy.dataset.dataset_version.dataset_version_id == (
        repeated.dataset.dataset_version.dataset_version_id
    )
    assert legacy.dataset.content_hash == repeated.dataset.content_hash
    assert legacy.dataset.row_count_total == repeated.dataset.row_count_total
    assert canonical_business_payload(legacy.dataset.rows_by_table) == (
        canonical_business_payload(repeated.dataset.rows_by_table)
    )
    assert legacy.ground_truth.scenario_id == repeated.ground_truth.scenario_id
    assert legacy.ground_truth.hgt_id == repeated.ground_truth.hgt_id
    assert legacy.ground_truth.hgt_hash == repeated.ground_truth.hgt_hash
    assert canonical_hgt_payload(legacy.ground_truth) == canonical_hgt_payload(
        repeated.ground_truth
    )
    assert canonical_business_payload(baseline.rows_by_table) == before_payload
    assert baseline.content_hash == before_hash
    assert baseline.row_count_total == before_count


def test_typed_expected_preconditions_preserve_value_error_api_compatibility() -> None:
    config = _supplier_config(affected_supplier_count=999)
    with pytest.raises(ScenarioPreconditionUnavailable) as caught:
        apply_scenario(_baseline(), config, generated_at=GENERATED_AT)
    assert isinstance(caught.value, ValueError)


def test_unexpected_w2_invariant_value_errors_are_not_typed_as_unavailable() -> None:
    baseline = _baseline()
    inspection = cast(QualityInspection, baseline.rows_for("fact_quality_inspection")[0])
    inspection.passed_quantity += 1
    with pytest.raises(ValueError) as caught:
        apply_scenario(baseline, _quality_config(), generated_at=GENERATED_AT)
    assert not isinstance(caught.value, ScenarioPreconditionUnavailable)
