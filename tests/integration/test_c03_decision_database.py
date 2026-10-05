"""C03 PostgreSQL handoff, zero-mutation and scenario direction smoke tests."""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from decimal import Decimal
from typing import cast
from zoneinfo import ZoneInfo

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import event, select
from sqlalchemy.engine import Engine, make_url
from test_decision_snapshot_database import (
    _counts,
    _run,
    _source,
)

from flowlens.config import Settings
from flowlens.data import Base
from flowlens.data.generation import GeneratedDataset
from flowlens.data.generation.canonical import CANONICAL_TABLE_ORDER, canonical_business_payload
from flowlens.data.models import (
    DatasetVersion,
    MaterialRequirement,
    Operation,
    PurchaseOrder,
    QualityInspection,
    Rework,
    SalesOrder,
    WorkOrder,
)
from flowlens.data.persistence import persist_dataset, read_active_dataset
from flowlens.data.scenarios import (
    CapacitySurgeConfig,
    QualityDeteriorationConfig,
    ScenarioResult,
    SupplierDegradationConfig,
    apply_scenario,
)
from flowlens.data.scenarios.config import ScenarioConfig
from flowlens.db import create_database_engine
from flowlens.db.decision_snapshot import build_decision_snapshot
from flowlens.decision.context import build_decision_context
from flowlens.decision.diagnosis import evaluate_c03
from flowlens.decision.enums import SignalState, SignalType
from flowlens.decision.evidence import build_evidence_bundle

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    try:
        settings = Settings()
    except ValidationError:
        if os.environ.get("FLOWLENS_DATABASE_URL"):
            raise
        pytest.skip("FLOWLENS_DATABASE_URL required for PostgreSQL C03 integration")
    url = make_url(settings.database_url.get_secret_value())
    if (
        settings.app_environment != "test"
        or url.get_backend_name() != "postgresql"
        or not url.database
        or not url.database.endswith("_test")
    ):
        raise RuntimeError(
            "C03 integration requires PostgreSQL test environment and '_test' database"
        )
    command.upgrade(Config(toml_file="pyproject.toml"), "head")
    target = create_database_engine(settings)
    try:
        assert all(count == 0 for count in _counts(target).values()), "Refuse nonempty test target"
        yield target
    finally:
        target.dispose()


@pytest.fixture
def source(engine: Engine) -> Iterator[GeneratedDataset]:
    assert all(count == 0 for count in _counts(engine).values()), "Refuse nonempty test target"
    generated = _source()
    persist_dataset(engine, generated)
    try:
        yield generated
    finally:
        with engine.begin() as connection:
            ids = set(connection.scalars(select(DatasetVersion.dataset_version_id)))
            assert ids <= {generated.dataset_version.dataset_version_id}
            for name in (*reversed(CANONICAL_TABLE_ORDER), "dataset_version"):
                table = Base.metadata.tables[name]
                connection.execute(
                    table.delete().where(
                        table.c.dataset_version_id == generated.dataset_version.dataset_version_id
                    )
                )
        assert all(count == 0 for count in _counts(engine).values())


def test_c03_database_handoff_is_pure_replayed_and_zero_mutation(
    engine: Engine,
    source: GeneratedDataset,
) -> None:
    before_counts = _counts(engine)
    before_business = canonical_business_payload(read_active_dataset(engine).rows_by_table)
    run = _run(source)
    snapshot = build_decision_snapshot(engine, run)
    bundle = build_evidence_bundle(snapshot)
    context = build_decision_context(snapshot, bundle)
    statements: list[str] = []

    def collect(
        _connection: object,
        _cursor: object,
        statement: str,
        _parameters: object,
        _context: object,
        _executemany: bool,
    ) -> None:
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", collect)
    try:
        first = evaluate_c03(bundle, context)
        second = evaluate_c03(bundle, context)
    finally:
        event.remove(engine, "before_cursor_execute", collect)
    assert first == second
    assert len(first[0].signals) == len(SignalType) == 8
    assert statements == []
    assert _counts(engine) == before_counts
    assert canonical_business_payload(read_active_dataset(engine).rows_by_table) == before_business


def _scenario_config(scenario: str) -> ScenarioConfig:
    zone = ZoneInfo("Asia/Shanghai")
    seed = 2 if scenario == "quality" else 20260901
    start = datetime(2026, 1, 1 if scenario == "quality" else 15, tzinfo=zone)
    end = (
        datetime(2026, 3, 31, 23, 59, 59, tzinfo=zone)
        if scenario == "quality"
        else datetime(2026, 2, 12, tzinfo=zone)
    )
    if scenario == "supplier":
        return SupplierDegradationConfig(
            scenario_version="1.0.0",
            scenario_seed=seed,
            window_start=start,
            window_end=end,
        )
    if scenario == "quality":
        return QualityDeteriorationConfig(
            scenario_version="1.0.0",
            scenario_seed=seed,
            window_start=start,
            window_end=end,
        )
    return CapacitySurgeConfig(
        scenario_version="1.0.0",
        scenario_seed=seed,
        window_start=start,
        window_end=end,
        arrival_volume_multiplier=Decimal("1.0" if scenario == "neutral" else "1.5"),
        queue_time_multiplier=Decimal("1.0" if scenario == "neutral" else "1.7"),
    )


def _scenario_candidate_orders(
    result: ScenarioResult, scenario: str, as_of: datetime
) -> tuple[str, ...]:
    """Use protected truth only to select test cases; runtime still receives business artifacts."""
    business = result.dataset
    affected = result.ground_truth.affected_entities_by_table
    work_orders: dict[str, WorkOrder] = {}
    for row in business.rows_for("fact_work_order"):
        work_order = cast(WorkOrder, row)
        work_orders[work_order.work_order_id] = work_order
    order_ids: set[str] = set()
    if scenario == "supplier":
        affected_pos = set(affected.get("fact_purchase_order", ()))
        materials: set[str] = set()
        for row in business.rows_for("fact_purchase_order"):
            purchase_order = cast(PurchaseOrder, row)
            if purchase_order.purchase_order_id in affected_pos:
                materials.add(purchase_order.material_id)
        work_ids: set[str] = set()
        for row in business.rows_for("fact_material_requirement"):
            requirement = cast(MaterialRequirement, row)
            if requirement.material_id in materials:
                work_ids.add(requirement.work_order_id)
        order_ids.update(
            work_orders[item].sales_order_id for item in work_ids if item in work_orders
        )
    elif scenario == "quality":
        work_ids = set(affected.get("fact_work_order", ()))
        affected_inspections = set(affected.get("fact_quality_inspection", ()))
        affected_reworks = set(affected.get("fact_rework", ()))
        for row in business.rows_for("fact_quality_inspection"):
            inspection = cast(QualityInspection, row)
            if inspection.inspection_id in affected_inspections:
                work_ids.add(inspection.work_order_id)
        for row in business.rows_for("fact_rework"):
            rework = cast(Rework, row)
            if rework.rework_id in affected_reworks:
                work_ids.add(rework.work_order_id)
        order_ids.update(
            work_orders[item].sales_order_id for item in work_ids if item in work_orders
        )
    elif scenario == "capacity":
        affected_operations = set(affected.get("fact_operation", ()))
        work_ids = set()
        for row in business.rows_for("fact_operation"):
            operation = cast(Operation, row)
            if operation.operation_id in affected_operations and (
                (
                    operation.actual_start_at is not None
                    and operation.actual_start_at <= as_of
                    and operation.actual_start_at > operation.planned_start_at
                )
                or (
                    (operation.actual_start_at is None or operation.actual_start_at > as_of)
                    and as_of > operation.planned_start_at
                )
            ):
                work_ids.add(operation.work_order_id)
        order_ids.update(
            work_orders[item].sales_order_id for item in work_ids if item in work_orders
        )
    else:
        order_ids.add(
            min(
                (
                    cast(SalesOrder, item)
                    for item in business.rows_for("fact_sales_order")
                    if cast(SalesOrder, item).order_at <= as_of
                ),
                key=lambda item: item.sales_order_id,
            ).sales_order_id
        )
    return tuple(sorted(order_ids))


@pytest.mark.parametrize(
    ("scenario", "expected_hash"),
    (
        ("supplier", "682dc4238ad146724068116b0e2ca93b291029670b537ecf9b7693e09a6ff3cb"),
        ("quality", "ef52d548ec704e21c5a4e0a034ac79d1167277fcd2e148253d08c5d069089093"),
        ("capacity", "f4b9848fb98ac834056e560e1dde690a0b3982a1ed5f8469b9a8157775106cee"),
        ("neutral", "d6c31ab8d68d9c4b1a735cfb4adea71931766907cc78db55763514d6cdb562e6"),
    ),
)
def test_scenario_business_facts_direction_smoke(
    engine: Engine,
    scenario: str,
    expected_hash: str,
) -> None:
    assert all(count == 0 for count in _counts(engine).values())
    result = apply_scenario(
        _source(),
        _scenario_config(scenario),
        generated_at=datetime(2026, 8, 24, tzinfo=UTC),
    )
    business = result.dataset
    assert business.content_hash == expected_hash
    persist_dataset(engine, business)
    try:
        as_of = datetime(2026, 2, 20, tzinfo=ZoneInfo("Asia/Shanghai"))
        active_types: set[SignalType] = set()
        checked = 0
        candidates = set(_scenario_candidate_orders(result, scenario, as_of))
        assert candidates
        orders = sorted(
            (
                cast(SalesOrder, item)
                for item in business.rows_for("fact_sales_order")
                if cast(SalesOrder, item).sales_order_id in candidates
            ),
            key=lambda item: item.sales_order_id,
        )
        for order in orders:
            if order.order_at > as_of:
                continue
            snapshot = build_decision_snapshot(
                engine, _run(business, as_of=as_of, order_id=order.sales_order_id)
            )
            bundle = build_evidence_bundle(snapshot)
            context = build_decision_context(snapshot, bundle)
            signals, _ = evaluate_c03(bundle, context)
            checked += 1
            capacity = next(
                item for item in signals.signals if item.signal_type is SignalType.CAPACITY_PRESSURE
            )
            assert capacity.state is SignalState.UNKNOWN
            assert "C03_CAPACITY_SCOPE_INSUFFICIENT" in capacity.reason_codes
            active_types.update(
                item.signal_type for item in signals.signals if item.state is SignalState.ACTIVE
            )
            if (
                (
                    scenario == "supplier"
                    and active_types
                    & {SignalType.SUPPLIER_LATE_RECEIPT, SignalType.MATERIAL_TIMING_RISK}
                )
                or (
                    scenario == "quality"
                    and active_types
                    & {
                        SignalType.QUALITY_FAILURE,
                        SignalType.REWORK_PRESENT,
                        SignalType.QUALITY_DISPOSITION_UNKNOWN,
                    }
                )
                or (scenario == "capacity" and SignalType.QUEUE_DELAY in active_types)
            ):
                break
        assert checked > 0
        if scenario == "supplier":
            assert active_types & {
                SignalType.SUPPLIER_LATE_RECEIPT,
                SignalType.MATERIAL_TIMING_RISK,
            }
        elif scenario == "quality":
            assert active_types & {
                SignalType.QUALITY_FAILURE,
                SignalType.REWORK_PRESENT,
                SignalType.QUALITY_DISPOSITION_UNKNOWN,
            }
        elif scenario == "capacity":
            assert SignalType.QUEUE_DELAY in active_types
        else:
            # No scenario metadata is available to the runtime; only admitted facts can activate.
            assert SignalType.CAPACITY_PRESSURE not in active_types
    finally:
        with engine.begin() as connection:
            ids = set(connection.scalars(select(DatasetVersion.dataset_version_id)))
            assert ids <= {business.dataset_version.dataset_version_id}
            for name in (*reversed(CANONICAL_TABLE_ORDER), "dataset_version"):
                table = Base.metadata.tables[name]
                connection.execute(
                    table.delete().where(
                        table.c.dataset_version_id == business.dataset_version.dataset_version_id
                    )
                )
        assert all(count == 0 for count in _counts(engine).values())
