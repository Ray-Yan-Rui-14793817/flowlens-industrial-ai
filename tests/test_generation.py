"""Unit tests for the deterministic Week 2 baseline generator."""

from __future__ import annotations

import os
import random
import subprocess
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Final, cast

import pytest
from sqlalchemy import DateTime, String

import flowlens.data.generation.generator as generation_module
from flowlens.data import Base
from flowlens.data.generation import (
    BUSINESS_TIMEZONE,
    DEFAULT_DEMO_SEED,
    PROFILE_DEFINITIONS,
    GeneratedDataset,
    GenerationConfig,
    GenerationProfile,
    generate_baseline,
)
from flowlens.data.generation.canonical import (
    CANONICAL_TABLE_ORDER,
    canonical_business_payload,
    canonical_content_hash,
    normalize_scalar,
)
from flowlens.data.generation.ids import DeterministicIdFactory
from flowlens.data.models import (
    Customer,
    Delivery,
    InventorySnapshot,
    MaterialRequirement,
    Operation,
    Product,
    ProductMaterial,
    PurchaseOrder,
    QualityInspection,
    Rework,
    SalesOrder,
    WorkCenter,
    WorkOrder,
)

PROJECT_ROOT: Final = Path(__file__).resolve().parents[1]
EXPECTED_PROFILE_COUNTS: Final = {
    GenerationProfile.TEST: (3, 150, 12, 25, 8, 15, 4),
    GenerationProfile.CI: (6, 800, 20, 50, 12, 30, 6),
    GenerationProfile.DEMO: (18, 12_000, 30, 80, 24, 60, 8),
}
FORBIDDEN_FIELDS: Final = {
    "is_delayed",
    "delay_days",
    "delivery_delay_rate",
    "supplier_risk_score",
    "supplier_on_time_rate",
    "material_availability_ratio",
    "first_pass_yield",
    "rework_rate",
    "delivery_risk_probability",
    "scenario_id",
    "scenario_name",
    "true_root_cause",
    "is_problem_order",
}


def _config(
    *,
    profile: GenerationProfile = GenerationProfile.TEST,
    seed: int = 20_260_824,
    generated_at: datetime = datetime(2026, 8, 24, 9, tzinfo=UTC),
) -> GenerationConfig:
    return GenerationConfig(
        profile=profile,
        seed=seed,
        period_start=date(2026, 1, 1),
        generator_version="0.1.0-c03",
        generated_at=generated_at,
    )


@pytest.fixture(scope="module")
def test_dataset() -> GeneratedDataset:
    return generate_baseline(_config())


@pytest.fixture(scope="module")
def ci_dataset() -> GeneratedDataset:
    return generate_baseline(_config(profile=GenerationProfile.CI))


def test_frozen_profile_definitions_and_periods() -> None:
    for profile, expected in EXPECTED_PROFILE_COUNTS.items():
        definition = PROFILE_DEFINITIONS[profile]
        assert (
            definition.months,
            definition.sales_orders,
            definition.products,
            definition.materials,
            definition.suppliers,
            definition.customers,
            definition.work_centers,
        ) == expected
        config = _config(profile=profile)
        expected_end = {
            GenerationProfile.TEST: date(2026, 3, 31),
            GenerationProfile.CI: date(2026, 6, 30),
            GenerationProfile.DEMO: date(2027, 6, 30),
        }[profile]
        assert config.period_end == expected_end
    assert DEFAULT_DEMO_SEED == 20_260_824


@pytest.mark.parametrize(
    ("dataset_fixture", "profile"),
    (("test_dataset", GenerationProfile.TEST), ("ci_dataset", GenerationProfile.CI)),
)
def test_generated_profiles_have_exact_frozen_counts(
    dataset_fixture: str,
    profile: GenerationProfile,
    request: pytest.FixtureRequest,
) -> None:
    dataset = request.getfixturevalue(dataset_fixture)
    assert isinstance(dataset, GeneratedDataset)
    definition = PROFILE_DEFINITIONS[profile]
    assert len(dataset.rows_for("dim_product")) == definition.products
    assert len(dataset.rows_for("dim_material")) == definition.materials
    assert len(dataset.rows_for("dim_supplier")) == definition.suppliers
    assert len(dataset.rows_for("dim_customer")) == definition.customers
    assert len(dataset.rows_for("dim_work_center")) == definition.work_centers
    assert len(dataset.rows_for("fact_sales_order")) == definition.sales_orders


def test_generation_is_deterministic_and_generated_at_is_isolated(
    test_dataset: GeneratedDataset,
) -> None:
    same = generate_baseline(_config())
    changed_provenance = generate_baseline(
        _config(generated_at=datetime(2030, 1, 1, 12, tzinfo=UTC))
    )

    expected_payload = canonical_business_payload(test_dataset.rows_by_table)
    assert canonical_business_payload(same.rows_by_table) == expected_payload
    assert canonical_business_payload(changed_provenance.rows_by_table) == expected_payload
    assert same.dataset_version.dataset_version_id == (
        test_dataset.dataset_version.dataset_version_id
    )
    assert changed_provenance.dataset_version.dataset_version_id == (
        test_dataset.dataset_version.dataset_version_id
    )
    assert same.row_count_total == changed_provenance.row_count_total
    assert same.content_hash == changed_provenance.content_hash == test_dataset.content_hash


def test_different_seed_changes_business_content_and_hash(
    test_dataset: GeneratedDataset,
) -> None:
    different = generate_baseline(_config(seed=20_260_825))
    assert canonical_business_payload(different.rows_by_table) != canonical_business_payload(
        test_dataset.rows_by_table
    )
    assert different.content_hash != test_dataset.content_hash


def test_all_business_timestamps_are_aware_and_use_shanghai(
    test_dataset: GeneratedDataset,
) -> None:
    for _, row in test_dataset.iter_business_rows():
        for column in row.__mapper__.columns:
            if not isinstance(column.type, DateTime):
                continue
            value = getattr(row, column.name)
            if value is not None:
                assert value.tzinfo is BUSINESS_TIMEZONE
                assert value.utcoffset() == timedelta(hours=8)


def test_generated_rows_map_exactly_to_frozen_orm_fields(
    test_dataset: GeneratedDataset,
) -> None:
    assert tuple(test_dataset.rows_by_table) == CANONICAL_TABLE_ORDER
    for table_name, row in test_dataset.iter_business_rows():
        assert row.__mapper__.local_table is Base.metadata.tables[table_name]
        mapped_fields = set(row.__mapper__.columns.keys())
        assert mapped_fields == set(Base.metadata.tables[table_name].columns.keys())
        assert set(row.__dict__) <= mapped_fields | {"_sa_instance_state"}
        assert mapped_fields.isdisjoint(FORBIDDEN_FIELDS)


def test_identifiers_are_unique_stable_and_within_frozen_lengths(
    test_dataset: GeneratedDataset,
) -> None:
    for table_name, rows in test_dataset.rows_by_table.items():
        primary_key_columns = tuple(Base.metadata.tables[table_name].primary_key.columns)
        keys = [tuple(getattr(row, column.name) for column in primary_key_columns) for row in rows]
        assert len(keys) == len(set(keys))
        for row in rows:
            for column in primary_key_columns:
                if isinstance(column.type, String):
                    assert column.type.length is not None
                    assert len(getattr(row, column.name)) <= column.type.length


def test_row_count_and_hash_metadata_are_exact(test_dataset: GeneratedDataset) -> None:
    independent_count = sum(len(rows) for rows in test_dataset.rows_by_table.values())
    assert test_dataset.row_count_total == independent_count
    assert test_dataset.dataset_version.row_count_total == independent_count
    assert test_dataset.content_hash == canonical_content_hash(test_dataset.rows_by_table)
    assert len(test_dataset.content_hash) == 64
    assert test_dataset.content_hash == test_dataset.content_hash.lower()
    assert all(character in "0123456789abcdef" for character in test_dataset.content_hash)


def test_material_requirements_are_derived_from_bom_and_work_quantity(
    test_dataset: GeneratedDataset,
) -> None:
    bom = {
        (row.product_id, row.material_id): row.quantity_per_unit
        for row in test_dataset.rows_for("bridge_product_material")
        if isinstance(row, ProductMaterial)
    }
    work_order_rows = cast(tuple[WorkOrder, ...], test_dataset.rows_for("fact_work_order"))
    requirement_rows = cast(
        tuple[MaterialRequirement, ...],
        test_dataset.rows_for("fact_material_requirement"),
    )
    work_orders = {row.work_order_id: row for row in work_order_rows}
    for row in requirement_rows:
        work_order = work_orders[row.work_order_id]
        assert row.required_quantity == (
            bom[(work_order.product_id, row.material_id)] * work_order.planned_quantity
        ).quantize(Decimal("0.0001"))


def test_initial_inventory_does_not_depend_on_future_sales_demand(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline = generate_baseline(_config())
    original = generation_module._generate_sales_orders

    def generate_changed_future(
        config: GenerationConfig,
        rng: random.Random,
        ids: DeterministicIdFactory,
        products: Sequence[Product],
        customers: Sequence[Customer],
    ) -> list[SalesOrder]:
        rows = original(config, rng, ids, products, customers)
        snapshot_cutoff = datetime.combine(
            config.period_start,
            datetime.min.time(),
            BUSINESS_TIMEZONE,
        ) + timedelta(hours=7)
        for row in rows:
            if row.order_at > snapshot_cutoff:
                row.order_quantity += 97
        return rows

    monkeypatch.setattr(generation_module, "_generate_sales_orders", generate_changed_future)
    changed_future = generate_baseline(_config())

    def inventory_state(dataset: GeneratedDataset) -> tuple[tuple[object, ...], ...]:
        rows = cast(
            tuple[InventorySnapshot, ...],
            dataset.rows_for("fact_inventory_snapshot"),
        )
        return tuple(
            (
                row.material_id,
                row.snapshot_at,
                row.on_hand_quantity,
                row.reserved_quantity,
            )
            for row in rows
        )

    assert inventory_state(changed_future) == inventory_state(baseline)


def test_purchase_orders_use_only_demand_known_by_their_order_time(
    test_dataset: GeneratedDataset,
) -> None:
    sales_orders = cast(
        tuple[SalesOrder, ...], test_dataset.rows_for("fact_sales_order")
    )
    purchase_orders = cast(
        tuple[PurchaseOrder, ...], test_dataset.rows_for("fact_purchase_order")
    )
    bom_by_product: dict[str, dict[str, Decimal]] = defaultdict(dict)
    for component in cast(
        tuple[ProductMaterial, ...],
        test_dataset.rows_for("bridge_product_material"),
    ):
        bom_by_product[component.product_id][component.material_id] = (
            component.quantity_per_unit
        )

    found_later_same_material_demand = False
    for purchase_order in purchase_orders:
        prior_decision = purchase_order.ordered_at - timedelta(days=7)
        contributing_orders = [
            order
            for order in sales_orders
            if prior_decision < order.order_at <= purchase_order.ordered_at
            and purchase_order.material_id in bom_by_product[order.product_id]
        ]
        assert contributing_orders
        expected_demand = sum(
            (
                bom_by_product[order.product_id][purchase_order.material_id]
                * order.order_quantity
                for order in contributing_orders
            ),
            start=Decimal("0"),
        )
        assert purchase_order.ordered_quantity == (
            expected_demand * Decimal("1.10")
        ).quantize(Decimal("0.0001"))
        assert max(order.order_at for order in contributing_orders) <= (
            purchase_order.ordered_at
        )
        found_later_same_material_demand |= any(
            order.order_at > purchase_order.ordered_at
            and purchase_order.material_id in bom_by_product[order.product_id]
            for order in sales_orders
        )

    assert found_later_same_material_demand


def test_early_procurement_is_invariant_to_later_sales_and_rng_consumption(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline = generate_baseline(_config())
    baseline_purchase_orders = cast(
        tuple[PurchaseOrder, ...], baseline.rows_for("fact_purchase_order")
    )
    cutoff = min(row.ordered_at for row in baseline_purchase_orders)
    original = generation_module._generate_sales_orders

    def generate_changed_future(
        config: GenerationConfig,
        rng: random.Random,
        ids: DeterministicIdFactory,
        products: Sequence[Product],
        customers: Sequence[Customer],
    ) -> list[SalesOrder]:
        rows = original(config, rng, ids, products, customers)
        for row in rows:
            if row.order_at > cutoff:
                row.order_quantity += 53
                rng.random()
        return rows

    monkeypatch.setattr(generation_module, "_generate_sales_orders", generate_changed_future)
    changed_future = generate_baseline(_config())

    def early_purchase_order_state(
        dataset: GeneratedDataset,
    ) -> tuple[tuple[object, ...], ...]:
        rows = cast(
            tuple[PurchaseOrder, ...], dataset.rows_for("fact_purchase_order")
        )
        return tuple(
            (
                row.purchase_order_id,
                row.supplier_id,
                row.material_id,
                row.ordered_at,
                row.promised_receipt_at,
                row.actual_receipt_at,
                row.ordered_quantity,
                row.received_quantity,
                row.status,
            )
            for row in rows
            if row.ordered_at <= cutoff
        )

    assert early_purchase_order_state(changed_future) == early_purchase_order_state(
        baseline
    )


def test_sales_orders_and_work_orders_have_direct_semantic_consistency(
    test_dataset: GeneratedDataset,
) -> None:
    sales_orders = {
        row.sales_order_id: row
        for row in cast(
            tuple[SalesOrder, ...], test_dataset.rows_for("fact_sales_order")
        )
    }
    work_orders = cast(
        tuple[WorkOrder, ...], test_dataset.rows_for("fact_work_order")
    )
    assert len(work_orders) == len(sales_orders)
    assert {row.sales_order_id for row in work_orders} == set(sales_orders)
    for work_order in work_orders:
        sales_order = sales_orders[work_order.sales_order_id]
        assert work_order.product_id == sales_order.product_id
        assert work_order.planned_quantity == sales_order.order_quantity


def test_work_order_operations_have_direct_semantic_consistency(
    test_dataset: GeneratedDataset,
) -> None:
    work_orders = cast(
        tuple[WorkOrder, ...], test_dataset.rows_for("fact_work_order")
    )
    operations = cast(
        tuple[Operation, ...], test_dataset.rows_for("fact_operation")
    )
    work_center_ids = {
        row.work_center_id
        for row in cast(
            tuple[WorkCenter, ...], test_dataset.rows_for("dim_work_center")
        )
    }
    operations_by_work_order: dict[str, list[Operation]] = defaultdict(list)
    for operation in operations:
        operations_by_work_order[operation.work_order_id].append(operation)
        assert operation.work_center_id in work_center_ids

    for work_order in work_orders:
        rows = sorted(
            operations_by_work_order[work_order.work_order_id],
            key=lambda row: row.sequence_number,
        )
        assert rows
        assert [row.sequence_number for row in rows] == list(range(1, len(rows) + 1))
        assert work_order.actual_start_at is not None
        assert work_order.actual_end_at is not None
        for operation in rows:
            assert work_order.planned_start_at <= operation.planned_start_at
            assert operation.planned_end_at <= work_order.planned_end_at
            assert operation.actual_start_at is not None
            assert operation.actual_end_at is not None
            assert work_order.actual_start_at <= operation.actual_start_at
            assert operation.actual_end_at <= work_order.actual_end_at
        for previous, current in zip(rows, rows[1:], strict=False):
            assert previous.planned_end_at <= current.planned_start_at
            assert previous.actual_end_at is not None
            assert current.actual_start_at is not None
            assert previous.actual_end_at <= current.actual_start_at


def test_quality_rework_inventory_and_delivery_are_coherent(
    test_dataset: GeneratedDataset,
) -> None:
    work_order_rows = cast(tuple[WorkOrder, ...], test_dataset.rows_for("fact_work_order"))
    inspection_rows = cast(
        tuple[QualityInspection, ...], test_dataset.rows_for("fact_quality_inspection")
    )
    sales_order_rows = cast(
        tuple[SalesOrder, ...], test_dataset.rows_for("fact_sales_order")
    )
    inventory_rows = cast(
        tuple[InventorySnapshot, ...], test_dataset.rows_for("fact_inventory_snapshot")
    )
    rework_rows = cast(tuple[Rework, ...], test_dataset.rows_for("fact_rework"))
    delivery_rows = cast(tuple[Delivery, ...], test_dataset.rows_for("fact_delivery"))
    work_orders = {row.work_order_id: row for row in work_order_rows}
    inspections = {row.inspection_id: row for row in inspection_rows}
    sales_orders = {row.sales_order_id: row for row in sales_order_rows}
    delivered_by_order: dict[str, int] = defaultdict(int)

    for row in inventory_rows:
        assert Decimal("0") <= row.reserved_quantity <= row.on_hand_quantity
    for inspection in inspections.values():
        work_order = work_orders[inspection.work_order_id]
        assert inspection.passed_quantity + inspection.failed_quantity == (
            inspection.inspected_quantity
        )
        assert (inspection.result == "PASS") is (inspection.failed_quantity == 0)
        assert work_order.actual_start_at is not None
        assert inspection.inspection_at >= work_order.actual_start_at
    for rework in rework_rows:
        inspection = inspections[rework.inspection_id]
        assert inspection.result == "FAIL"
        assert 0 < rework.rework_quantity <= inspection.failed_quantity
        assert rework.rework_start_at >= inspection.inspection_at
        assert rework.rework_end_at >= rework.rework_start_at
    for delivery in delivery_rows:
        order = sales_orders[delivery.sales_order_id]
        assert delivery.delivery_at >= order.order_at
        delivered_by_order[delivery.sales_order_id] += delivery.delivered_quantity
    for order_id, delivered in delivered_by_order.items():
        assert delivered <= sales_orders[order_id].order_quantity


def test_canonical_hash_convention_is_explicit_and_order_invariant(
    test_dataset: GeneratedDataset,
) -> None:
    assert normalize_scalar(Decimal("1.2300")) == "1.23"
    assert normalize_scalar(Decimal("-0")) == "0"
    assert normalize_scalar(Decimal("0E-10")) == "0"
    assert normalize_scalar(Decimal("0.0000")) == "0"
    assert normalize_scalar(Decimal("1E+20")) == "100000000000000000000"
    assert normalize_scalar(date(2026, 1, 2)) == "2026-01-02"
    shanghai_instant = datetime(2026, 1, 2, 8, tzinfo=BUSINESS_TIMEZONE)
    assert normalize_scalar(shanghai_instant) == normalize_scalar(
        datetime(2026, 1, 2, 0, tzinfo=UTC)
    )

    reversed_rows: Mapping[str, Sequence[Base]] = {
        table_name: tuple(reversed(rows))
        for table_name, rows in reversed(tuple(test_dataset.rows_by_table.items()))
    }
    assert canonical_content_hash(reversed_rows) == test_dataset.content_hash

    product = cast(tuple[Product, ...], test_dataset.rows_for("dim_product"))[0]
    original_name = product.model_name
    product.model_name = f"{original_name} changed"
    try:
        assert canonical_content_hash(test_dataset.rows_by_table) != test_dataset.content_hash
    finally:
        product.model_name = original_name


def test_generation_config_rejects_nondeterministic_or_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        _config(generated_at=datetime(2026, 1, 1))
    with pytest.raises(ValueError, match="nonnegative PostgreSQL BIGINT"):
        GenerationConfig(
            GenerationProfile.TEST,
            -1,
            date(2026, 1, 1),
            "0.1.0",
            datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_generation_import_is_side_effect_free() -> None:
    environment = os.environ.copy()
    environment.pop("FLOWLENS_DATABASE_URL", None)
    script = """
import alembic.command
import sqlalchemy
import sqlalchemy.orm

def unexpected_side_effect(*args, **kwargs):
    raise AssertionError("generation import triggered an external side effect")

alembic.command.upgrade = unexpected_side_effect
sqlalchemy.create_engine = unexpected_side_effect
sqlalchemy.MetaData.create_all = unexpected_side_effect
sqlalchemy.orm.sessionmaker = unexpected_side_effect

import flowlens.data.generation as generation

assert generation.GenerationProfile.TEST.value == "test"
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
