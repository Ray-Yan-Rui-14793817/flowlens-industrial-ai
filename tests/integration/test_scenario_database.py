"""C04-H acceptance against real PostgreSQL; no production loading workflow.

Each snapshot is read inside its own rollback-only transaction. Shared global
business PKs never require baseline/scenario coexistence or replacement policy.
Run only against an externally verified disposable PostgreSQL test database.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from collections.abc import Iterator, Mapping
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_CEILING, Decimal
from pathlib import Path
from statistics import median
from types import MappingProxyType
from typing import NoReturn, cast

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import DateTime, Numeric, func, inspect, select, text
from sqlalchemy.engine import Connection, Engine, make_url
from sqlalchemy.exc import IntegrityError

from flowlens.config import Settings
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
    canonicalize_rows,
)
from flowlens.data.models import (
    Customer,
    DatasetVersion,
    Delivery,
    Material,
    MaterialRequirement,
    Operation,
    Product,
    ProductMaterial,
    PurchaseOrder,
    QualityInspection,
    Rework,
    SalesOrder,
    Supplier,
    WorkCenter,
    WorkOrder,
)
from flowlens.data.scenarios import (
    CapacitySurgeConfig,
    QualityDeteriorationConfig,
    ScenarioResult,
    SupplierDegradationConfig,
    apply_scenario,
    serialization,
)
from flowlens.db import create_database_engine

pytestmark = pytest.mark.integration
ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 9, 1, 9, 0, 0, 123456, tzinfo=UTC)
START = datetime(2026, 1, 1, tzinfo=BUSINESS_TIMEZONE)
END = datetime(2026, 4, 1, tzinfo=BUSINESS_TIMEZONE)
MODELS = {
    str(mapper.class_.__tablename__): cast(type[Base], mapper.class_)
    for mapper in Base.registry.mappers
}


def _values(row: Base, *, semantic: bool = False) -> dict[str, object]:
    return {
        c.name: getattr(row, c.name)
        for c in row.__mapper__.columns
        if not semantic or c.name != "dataset_version_id"
    }


def _key(row: Base) -> tuple[object, ...]:
    # Ownership is deliberately omitted ONLY for baseline/scenario comparisons.
    return tuple(
        getattr(row, c.name) for c in row.__mapper__.primary_key if c.name != "dataset_version_id"
    )


def _rows[T: Base](dataset: GeneratedDataset, model: type[T]) -> tuple[T, ...]:
    return cast(tuple[T, ...], dataset.rows_for(model.__tablename__))


def _map[T: Base](dataset: GeneratedDataset, model: type[T]) -> dict[str, T]:
    return {str(_key(row)[0]): row for row in _rows(dataset, model)}


def _time(value: datetime | None) -> datetime:
    assert value is not None and value.utcoffset() is not None
    return value


@pytest.fixture(autouse=True)
def protected_artifact_guard(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    path = ROOT / "data/hidden_ground_truth/scenario_manifest.yaml"
    before = path.read_bytes() if path.exists() else None

    def forbidden(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("PostgreSQL acceptance must not publish protected HGT")

    monkeypatch.setattr(serialization, "write_protected_hgt", forbidden)
    try:
        yield
    finally:
        assert (path.read_bytes() if path.exists() else None) == before


@pytest.fixture(scope="module")
def database_engine() -> Iterator[Engine]:
    try:
        settings = Settings()
    except ValidationError:
        if os.environ.get("FLOWLENS_DATABASE_URL"):
            raise  # A configured but invalid acceptance environment must fail.
        pytest.skip("FLOWLENS_DATABASE_URL is required for PostgreSQL acceptance")
    url = make_url(settings.database_url.get_secret_value())
    if (
        settings.app_environment != "test"
        or not url.database
        or not url.database.endswith("_test")
        or url.get_backend_name() != "postgresql"
    ):
        raise RuntimeError("C04-H requires PostgreSQL, test environment and a '_test' database")
    command.upgrade(Config(toml_file=str(ROOT / "pyproject.toml")), "head")
    engine = create_database_engine(settings)
    try:
        inspector = inspect(engine)
        assert set(inspector.get_table_names()) == set(Base.metadata.tables) | {"alembic_version"}
        forbidden = {"scenario_id", "scenario_name", "true_root_cause", "hgt_id", "hgt_hash"}
        counts = [0, 0, 0, 0]
        for name, table in Base.metadata.tables.items():
            columns = {c["name"] for c in inspector.get_columns(name)}
            assert columns == set(table.columns.keys())
            assert not columns & forbidden
            counts[0] += bool(inspector.get_pk_constraint(name)["constrained_columns"])
            counts[1] += len(inspector.get_foreign_keys(name))
            counts[2] += len(inspector.get_unique_constraints(name))
            checks = inspector.get_check_constraints(name)
            assert all(check["name"] for check in checks)
            counts[3] += len(checks)
        assert counts == [16, 34, 3, 45]
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT version_num FROM alembic_version")) == (
                "0002_industrial_data_foundation"
            )
            _assert_empty(connection)
        yield engine
    finally:
        engine.dispose()


def _assert_empty(connection: Connection) -> None:
    # Never clean an unexpected database: refuse it without deleting anything.
    for table in Base.metadata.tables.values():
        assert connection.scalar(select(func.count()).select_from(table)) == 0, table.name


def _insert_dataset(connection: Connection, dataset: GeneratedDataset) -> None:
    """Private Core insertion only; accepts no ScenarioResult/HGT or policy flags."""
    if not isinstance(dataset, GeneratedDataset):
        raise TypeError("test insertion accepts only GeneratedDataset")
    connection.execute(
        Base.metadata.tables["dataset_version"].insert(), _values(dataset.dataset_version)
    )
    for name in CANONICAL_TABLE_ORDER:
        rows = dataset.rows_for(name)
        if rows:
            connection.execute(Base.metadata.tables[name].insert(), [_values(row) for row in rows])


def _read_dataset(connection: Connection) -> GeneratedDataset:
    metadata = DatasetVersion(
        **dict(connection.execute(select(DatasetVersion.__table__)).mappings().one())
    )
    rows: dict[str, tuple[Base, ...]] = {}
    for name in reversed(CANONICAL_TABLE_ORDER):
        table = Base.metadata.tables[name]
        # Deliberately noncanonical SQL return ordering; C03 owns normalization.
        query = select(table).order_by(*(c.desc() for c in table.primary_key.columns))
        rows[name] = tuple(
            MODELS[name](**dict(row)) for row in connection.execute(query).mappings()
        )
    return GeneratedDataset(metadata, MappingProxyType(rows))


def _round_trip(engine: Engine, dataset: GeneratedDataset) -> GeneratedDataset:
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            _assert_empty(connection)
            _insert_dataset(connection, dataset)
            snapshot = _read_dataset(connection)
            assert _values(snapshot.dataset_version) == _values(dataset.dataset_version)
            assert snapshot.row_count_total == sum(map(len, snapshot.rows_by_table.values()))
            assert canonical_content_hash(snapshot.rows_by_table) == dataset.content_hash
            assert canonical_business_payload(snapshot.rows_by_table) == (
                canonical_business_payload(dataset.rows_by_table)
            )
            for name in CANONICAL_TABLE_ORDER:
                expected = {_key(row): row for row in dataset.rows_for(name)}
                for row in snapshot.rows_for(name):
                    original = expected[_key(row)]
                    for col in row.__mapper__.columns:
                        value, source = getattr(row, col.name), getattr(original, col.name)
                        assert value == source, (name, col.name)
                        if value is not None and isinstance(col.type, DateTime):
                            assert value.utcoffset() is not None
                            assert value.microsecond == source.microsecond
                        if value is not None and isinstance(col.type, Numeric):
                            assert isinstance(value, Decimal) and value == source
            _assert_parent_semantics(snapshot)
        finally:
            transaction.rollback()
    with engine.connect() as connection:
        _assert_empty(connection)
    return snapshot


def _assert_parent_semantics(dataset: GeneratedDataset) -> None:
    """Cross-row business assertions, separate from actual SQL constraint checks."""
    tables = {"dataset_version": (dataset.dataset_version,), **dataset.rows_by_table}
    indexes = {
        (name, col.name): {getattr(row, col.name): row for row in rows}
        for name, rows in tables.items()
        for col in Base.metadata.tables[name].columns
    }
    owner = dataset.dataset_version.dataset_version_id
    for name, rows in tables.items():
        for row in rows:
            assert _values(row)["dataset_version_id"] == owner
            for col in Base.metadata.tables[name].columns:
                value = getattr(row, col.name)
                for fk in col.foreign_keys:
                    if value is not None:
                        parent = indexes[(fk.column.table.name, fk.column.name)][value]
                        assert _values(parent)["dataset_version_id"] == owner
    work = _map(dataset, WorkOrder)
    operations = _map(dataset, Operation)
    inspections = _map(dataset, QualityInspection)
    orders = _map(dataset, SalesOrder)
    bom = {(r.product_id, r.material_id): r for r in _rows(dataset, ProductMaterial)}
    for wo in work.values():
        assert wo.product_id == orders[wo.sales_order_id].product_id
    for qi in inspections.values():
        if qi.operation_id is not None:
            assert operations[qi.operation_id].work_order_id == qi.work_order_id
        assert qi.inspected_quantity == qi.passed_quantity + qi.failed_quantity
        assert (qi.result == "PASS") == (qi.failed_quantity == 0)
    for rw in _rows(dataset, Rework):
        qi = inspections[rw.inspection_id]
        assert rw.work_order_id == qi.work_order_id
        assert 0 < rw.rework_quantity <= qi.failed_quantity
        assert qi.inspection_at <= rw.rework_start_at <= rw.rework_end_at
    for mr in _rows(dataset, MaterialRequirement):
        wo = work[mr.work_order_id]
        assert mr.required_quantity == bom[wo.product_id, mr.material_id].quantity_per_unit * (
            wo.planned_quantity
        )
    delivered: dict[str, int] = defaultdict(int)
    for dl in _rows(dataset, Delivery):
        delivered[dl.sales_order_id] += dl.delivered_quantity
        assert dl.delivery_at >= max(
            _time(w.actual_end_at) for w in work.values() if w.sales_order_id == dl.sales_order_id
        )
    assert all(quantity <= orders[key].order_quantity for key, quantity in delivered.items())


@pytest.fixture(scope="module")
def baseline() -> GeneratedDataset:
    return generate_baseline(
        GenerationConfig(
            GenerationProfile.TEST,
            20260824,
            date(2026, 1, 1),
            "0.1.0-c03",
            NOW,
        )
    )


@pytest.fixture(scope="module")
def targeted(baseline: GeneratedDataset) -> GeneratedDataset:
    """Three coherent threads: two in-window, one outside; fractional timing.

    A single historical critical-material PO crosses only the first need-by.
    FAIL/PASS inspections exercise new and existing Rework. Arrival multiplier
    two copies both eligible templates, guaranteeing a new Capacity Rework.
    This test fixture does not modify C03 generation or its returned objects.
    """
    rows = {
        name: [type(row)(**_values(row)) for row in items]
        for name, items in baseline.rows_by_table.items()
    }
    for name in rows:
        if name.startswith("fact_") or name == "bridge_product_material":
            rows[name] = []
    owner = baseline.dataset_version.dataset_version_id
    common = {"dataset_version_id": owner}
    product = _rows(baseline, Product)[0]
    material = next(r for r in _rows(baseline, Material) if r.criticality in {"HIGH", "CRITICAL"})
    supplier = _rows(baseline, Supplier)[0]
    customer = _rows(baseline, Customer)[0]
    centers = _rows(baseline, WorkCenter)
    rows["bridge_product_material"] = [
        ProductMaterial(
            **common,
            product_id=product.product_id,
            material_id=material.material_id,
            quantity_per_unit=Decimal("1.1250"),
            is_critical=True,
        )
    ]
    rows["fact_purchase_order"] = [
        PurchaseOrder(
            **common,
            purchase_order_id="po_fixture",
            supplier_id=supplier.supplier_id,
            material_id=material.material_id,
            ordered_at=START + timedelta(days=13),
            promised_receipt_at=START + timedelta(days=15),
            actual_receipt_at=START + timedelta(days=15),
            ordered_quantity=Decimal("100.1250"),
            received_quantity=Decimal("100.1250"),
            status="RECEIVED",
        )
    ]
    for n, day in enumerate((14, 23, 63)):
        order_at = START + timedelta(days=day, microseconds=123456)
        start = order_at + timedelta(days=2)
        end = start + timedelta(hours=3)
        qi_at = end + timedelta(hours=1)
        rows["fact_sales_order"].append(
            SalesOrder(
                **common,
                sales_order_id=f"so_fixture_{n}",
                customer_id=customer.customer_id,
                product_id=product.product_id,
                order_at=order_at,
                promised_delivery_at=order_at + timedelta(days=4),
                order_quantity=3,
                priority="NORMAL",
                status="DELIVERED",
            )
        )
        rows["fact_work_order"].append(
            WorkOrder(
                **common,
                work_order_id=f"wo_fixture_{n}",
                sales_order_id=f"so_fixture_{n}",
                product_id=product.product_id,
                planned_start_at=start - timedelta(days=1),
                planned_end_at=end - timedelta(days=1),
                actual_start_at=start,
                actual_end_at=end,
                planned_quantity=3,
                completed_quantity=3,
                status="COMPLETED",
            )
        )
        for seq in range(2):
            op_start = start + timedelta(hours=seq * 2)
            rows["fact_operation"].append(
                Operation(
                    **common,
                    operation_id=f"op_fixture_{n}_{seq}",
                    work_order_id=f"wo_fixture_{n}",
                    work_center_id=centers[seq].work_center_id,
                    sequence_number=seq + 1,
                    planned_start_at=op_start - timedelta(days=1),
                    planned_end_at=op_start - timedelta(days=1) + timedelta(seconds=1.5),
                    actual_start_at=op_start,
                    actual_end_at=op_start + timedelta(hours=1),
                    status="COMPLETED",
                )
            )
        rows["fact_material_requirement"].append(
            MaterialRequirement(
                **common,
                material_requirement_id=f"mr_fixture_{n}",
                work_order_id=f"wo_fixture_{n}",
                material_id=material.material_id,
                required_quantity=Decimal("3.3750"),
                need_by_at=start - timedelta(hours=2),
            )
        )
        rows["fact_quality_inspection"].append(
            QualityInspection(
                **common,
                inspection_id=f"qi_fixture_{n}",
                work_order_id=f"wo_fixture_{n}",
                operation_id=f"op_fixture_{n}_1" if n != 1 else None,
                inspection_at=qi_at,
                inspection_type="FINAL",
                inspected_quantity=3,
                passed_quantity=2 if n == 0 else 3,
                failed_quantity=1 if n == 0 else 0,
                defect_category="ASSEMBLY" if n == 0 else None,
                severity="LOW" if n == 0 else None,
                result="FAIL" if n == 0 else "PASS",
            )
        )
        if n == 0:
            rows["fact_rework"].append(
                Rework(
                    **common,
                    rework_id="rw_fixture_0",
                    inspection_id="qi_fixture_0",
                    work_order_id="wo_fixture_0",
                    work_center_id=centers[1].work_center_id,
                    rework_start_at=qi_at + timedelta(hours=1),
                    rework_end_at=qi_at + timedelta(hours=1, seconds=1.5),
                    rework_quantity=1,
                    rework_reason="SYNTHETIC_ASSEMBLY_CORRECTION",
                )
            )
        for split, quantity in enumerate((1, 2)):
            rows["fact_delivery"].append(
                Delivery(
                    **common,
                    delivery_id=f"dl_fixture_{n}_{split}",
                    sales_order_id=f"so_fixture_{n}",
                    delivery_at=qi_at + timedelta(hours=1 + split, seconds=1.75),
                    delivered_quantity=quantity,
                )
            )
    ordered = canonicalize_rows(rows)
    metadata = _values(baseline.dataset_version)
    metadata.update(
        content_hash=canonical_content_hash(ordered),
        row_count_total=sum(map(len, ordered.values())),
    )
    return GeneratedDataset(DatasetVersion(**metadata), MappingProxyType(ordered))


def _assert_effect_map(
    before: GeneratedDataset, after: GeneratedDataset, result: ScenarioResult
) -> None:
    changed: dict[str, tuple[str, ...]] = {}
    controls = 0
    for name in CANONICAL_TABLE_ORDER:
        old = {_key(row): row for row in before.rows_for(name)}
        affected = []
        for row in after.rows_for(name):
            key = _key(row)
            if key not in old or _values(row, semantic=True) != _values(old[key], semantic=True):
                assert len(key) == 1  # No scenario changes the BOM/master-data identity.
                affected.append(str(key[0]))
            else:
                controls += 1
        if affected:
            changed[name] = tuple(sorted(affected))
    # Controls are derived from actual DB differences, not merely direct targets.
    assert controls > 0
    assert changed == dict(result.ground_truth.affected_entities_by_table)


def _pair(
    engine: Engine, baseline: GeneratedDataset, result: ScenarioResult
) -> tuple[GeneratedDataset, GeneratedDataset]:
    before = _round_trip(engine, baseline)
    after = _round_trip(engine, result.dataset)
    _assert_effect_map(before, after, result)
    assert canonical_content_hash(baseline.rows_by_table) == baseline.content_hash
    return before, after


def _business_days(start: datetime, days: int) -> datetime:
    result = start.astimezone(BUSINESS_TIMEZONE)
    while days:
        result += timedelta(days=1)
        days -= result.weekday() < 5
    return result


def _ceil(value: Decimal) -> int:
    return int(value.to_integral_value(rounding=ROUND_CEILING))


def test_baseline_round_trip(database_engine: Engine, baseline: GeneratedDataset) -> None:
    _round_trip(database_engine, baseline)


@pytest.mark.parametrize("targeted_case", [False, True], ids=["ordinary", "propagation"])
def test_supplier_postgresql(
    database_engine: Engine,
    baseline: GeneratedDataset,
    targeted: GeneratedDataset,
    targeted_case: bool,
) -> None:
    base = targeted if targeted_case else baseline
    config = SupplierDegradationConfig(
        scenario_version="1.0.0",
        scenario_seed=20260901,
        window_start=START,
        window_end=END,
        affected_supplier_count=1 if targeted_case else 2,
        affected_critical_material_count=1 if targeted_case else 5,
        late_probability_delta=Decimal("1") if targeted_case else Decimal("0.25"),
        additional_delay_business_days_min=3,
        additional_delay_business_days_max=3 if targeted_case else 8,
    )
    result = apply_scenario(base, config, generated_at=NOW)
    before, after = _pair(database_engine, base, result)
    old, new = _map(before, PurchaseOrder), _map(after, PurchaseOrder)
    targets = set(result.ground_truth.target_entity_ids)
    relevant = [
        r
        for r in old.values()
        if r.supplier_id in targets
        and r.material_id in targets
        and START <= r.ordered_at < END
        and r.actual_receipt_at is not None
    ]
    assert relevant
    n = len(relevant)
    late = sum(_time(r.actual_receipt_at) > r.promised_receipt_at for r in relevant)
    target = min(
        n, _ceil(Decimal(n) * min(Decimal(1), Decimal(late) / n + config.late_probability_delta))
    )
    assert (
        sum(
            _time(new[r.purchase_order_id].actual_receipt_at) > r.promised_receipt_at
            for r in relevant
        )
        == target
    )
    changed = [r for key, r in old.items() if r.actual_receipt_at != new[key].actual_receipt_at]
    assert len(changed) == target - late > 0
    for row in changed:
        actual = new[row.purchase_order_id]
        assert actual.actual_receipt_at in {
            _business_days(_time(row.actual_receipt_at), days)
            for days in range(
                config.additional_delay_business_days_min,
                config.additional_delay_business_days_max + 1,
            )
        }
    for key, row in old.items():
        assert (row.ordered_quantity, row.received_quantity, row.status) == (
            new[key].ordered_quantity,
            new[key].received_quantity,
            new[key].status,
        )
    shifts: dict[str, timedelta] = {}
    for wo in _rows(before, WorkOrder):
        receipts = [
            _time(new[po.purchase_order_id].actual_receipt_at)
            for mr in _rows(before, MaterialRequirement)
            if mr.work_order_id == wo.work_order_id
            for po in changed
            if po.material_id == mr.material_id
            and _time(po.actual_receipt_at)
            <= mr.need_by_at
            < _time(new[po.purchase_order_id].actual_receipt_at)
        ]
        shifts[wo.work_order_id] = (
            max(timedelta(0), max(receipts) - _time(wo.actual_start_at))
            if receipts
            else timedelta(0)
        )
    for model, fields in (
        (WorkOrder, ("actual_start_at", "actual_end_at")),
        (Operation, ("actual_start_at", "actual_end_at")),
        (QualityInspection, ("inspection_at",)),
        (Rework, ("rework_start_at", "rework_end_at")),
    ):
        actual_rows = _map(after, model)
        for semantic_row in _rows(before, model):
            for field in fields:
                assert getattr(actual_rows[str(_key(semantic_row)[0])], field) == (
                    getattr(semantic_row, field)
                    + shifts[str(_values(semantic_row)["work_order_id"])]
                )
    work = _rows(before, WorkOrder)
    actual_deliveries = _map(after, Delivery)
    for dl in _rows(before, Delivery):
        shift = next(shifts[w.work_order_id] for w in work if w.sales_order_id == dl.sales_order_id)
        assert actual_deliveries[dl.delivery_id].delivery_at == dl.delivery_at + shift
    if targeted_case:
        assert shifts["wo_fixture_0"] > timedelta(0)
        assert shifts["wo_fixture_1"] == shifts["wo_fixture_2"] == timedelta(0)
        assert set(result.ground_truth.affected_entities_by_table) >= {
            "fact_operation",
            "fact_quality_inspection",
            "fact_rework",
            "fact_delivery",
        }


@pytest.mark.parametrize("targeted_case", [False, True], ids=["ordinary", "delivery"])
def test_quality_postgresql(
    database_engine: Engine,
    baseline: GeneratedDataset,
    targeted: GeneratedDataset,
    targeted_case: bool,
) -> None:
    base = targeted if targeted_case else baseline
    config = QualityDeteriorationConfig(
        scenario_version="1.0.0",
        scenario_seed=20260901,
        window_start=START,
        window_end=datetime(2026, 2, 1, tzinfo=BUSINESS_TIMEZONE) if targeted_case else END,
        affected_product_count=1 if targeted_case else 12,
        affected_work_center_count=1 if targeted_case else 4,
        rework_duration_multiplier_min=Decimal("1.5"),
        rework_duration_multiplier_max=Decimal("1.5"),
    )
    result = apply_scenario(base, config, generated_at=NOW)
    before, after = _pair(database_engine, base, result)
    old_qi, new_qi = _map(before, QualityInspection), _map(after, QualityInspection)
    # These fixtures explicitly select every in-window product/resolved work center.
    relevant = [
        q for q in old_qi.values() if config.window_start <= q.inspection_at < config.window_end
    ]
    targets = set(result.ground_truth.target_entity_ids)
    work, ops = _map(before, WorkOrder), _rows(before, Operation)
    for qi in relevant:
        operation = next((op for op in ops if op.operation_id == qi.operation_id), None)
        if operation is None:
            operation = max(
                (op for op in ops if op.work_order_id == qi.work_order_id),
                key=lambda op: (op.sequence_number, op.operation_id),
            )
        assert work[qi.work_order_id].product_id in targets and operation.work_center_id in targets
    failed = sum(q.result == "FAIL" for q in relevant)
    expected_fail = min(
        len(relevant),
        _ceil(
            Decimal(len(relevant))
            * min(
                Decimal(1),
                Decimal(failed) / len(relevant) * config.failure_probability_multiplier,
            )
        ),
    )
    assert sum(new_qi[q.inspection_id].result == "FAIL" for q in relevant) == expected_fail > failed
    for q in relevant:
        actual = new_qi[q.inspection_id]
        if q.result == "PASS" and actual.result == "FAIL":
            assert (actual.failed_quantity, actual.passed_quantity) == (1, q.inspected_quantity - 1)
    old_rw, new_rw = _map(before, Rework), _map(after, Rework)
    ids = {q.inspection_id for q in relevant}
    reference = [r for r in old_rw.values() if r.inspection_id in ids]
    reworked = len({r.inspection_id for r in reference})
    expected_reworked = min(
        expected_fail,
        _ceil(
            Decimal(expected_fail)
            * min(
                Decimal(1),
                Decimal(reworked) / failed + config.rework_probability_delta,
            )
        ),
    )
    assert (
        len({r.inspection_id for r in new_rw.values() if r.inspection_id in ids})
        == expected_reworked
    )
    reference_us = median(
        [
            Decimal((r.rework_end_at - r.rework_start_at) // timedelta(microseconds=1))
            for r in reference
        ]
    )
    affected_by_work: dict[str, list[Rework]] = defaultdict(list)
    for key, rw in new_rw.items():
        if rw.inspection_id not in ids:
            assert _values(rw, semantic=True) == _values(old_rw[key], semantic=True)
            continue
        duration = (
            Decimal(
                (old_rw[key].rework_end_at - old_rw[key].rework_start_at)
                // timedelta(microseconds=1)
            )
            if key in old_rw
            else reference_us
        )
        assert rw.rework_end_at - rw.rework_start_at == timedelta(
            seconds=_ceil(duration * Decimal("1.5") / 1_000_000),
        )
        if key in old_rw:
            assert rw.rework_start_at == old_rw[key].rework_start_at
        else:
            qi = new_qi[rw.inspection_id]
            assert len(key) == 48 and rw.rework_quantity == qi.failed_quantity
            assert timedelta(hours=1) <= rw.rework_start_at - qi.inspection_at <= timedelta(hours=6)
            resolved = max(
                (op for op in ops if op.work_order_id == qi.work_order_id),
                key=lambda op: (op.sequence_number, op.operation_id),
            )
            assert rw.work_center_id == resolved.work_center_id
        affected_by_work[rw.work_order_id].append(rw)
    actual_work = _map(after, WorkOrder)
    actual_deliveries = _map(after, Delivery)
    for key, wo in work.items():
        completion = max(
            [_time(wo.actual_end_at)] + [r.rework_end_at for r in affected_by_work[key]]
        )
        assert actual_work[key].actual_end_at == completion
        assert actual_work[key].actual_start_at == wo.actual_start_at
        deliveries = [d for d in _rows(before, Delivery) if d.sales_order_id == wo.sales_order_id]
        shift = max(timedelta(0), completion - min(d.delivery_at for d in deliveries))
        for dl in deliveries:
            assert actual_deliveries[dl.delivery_id].delivery_at == dl.delivery_at + shift
    for op in ops:
        assert _values(_map(after, Operation)[op.operation_id], semantic=True) == (
            _values(op, semantic=True)
        )
    if targeted_case:
        assert actual_deliveries["dl_fixture_0_0"].delivery_at > (
            _map(before, Delivery)["dl_fixture_0_0"].delivery_at
        )
        assert new_qi["qi_fixture_2"].result == "PASS"  # Out-of-window control.


@pytest.mark.parametrize(
    "arrival,queue",
    [("1.5", "1.7"), ("1.5", "1"), ("1", "1.7"), ("1", "1")],
    ids=["combined", "arrival-only", "queue-only", "neutral"],
)
@pytest.mark.parametrize("targeted_case", [False, True], ids=["ordinary", "complete-thread"])
def test_capacity_postgresql(
    database_engine: Engine,
    baseline: GeneratedDataset,
    targeted: GeneratedDataset,
    targeted_case: bool,
    arrival: str,
    queue: str,
) -> None:
    base = targeted if targeted_case else baseline
    config = CapacitySurgeConfig(
        scenario_version="1.0.0",
        scenario_seed=20260901,
        window_start=datetime(2026, 1, 15, tzinfo=BUSINESS_TIMEZONE),
        window_end=datetime(2026, 2, 1, tzinfo=BUSINESS_TIMEZONE),
        affected_work_center_count=2,
        arrival_volume_multiplier=Decimal("2" if targeted_case and arrival != "1" else arrival),
        queue_time_multiplier=Decimal(queue),
    )
    result = apply_scenario(base, config, generated_at=NOW)
    before, after = _pair(database_engine, base, result)
    orders, actual_orders = _map(before, SalesOrder), _map(after, SalesOrder)
    work, actual_work = _map(before, WorkOrder), _map(after, WorkOrder)
    ops, actual_ops = _map(before, Operation), _map(after, Operation)
    centers = set(result.ground_truth.target_entity_ids)
    qualifying = {
        so.sales_order_id
        for so in orders.values()
        if config.window_start <= so.order_at < config.window_end
        and any(
            op.work_center_id in centers
            and work[op.work_order_id].sales_order_id == so.sales_order_id
            for op in ops.values()
        )
    }
    added = set(actual_orders) - set(orders)
    assert len(added) == _ceil(Decimal(len(qualifying)) * (config.arrival_volume_multiplier - 1))
    id_lengths = {
        SalesOrder: 40,
        WorkOrder: 40,
        PurchaseOrder: 40,
        Operation: 48,
        MaterialRequirement: 48,
        QualityInspection: 48,
        Rework: 48,
        Delivery: 48,
    }
    for model, length in id_lengths.items():
        original = _map(before, model)
        new = _map(after, model)
        assert set(original) <= set(new)
        for key in set(new) - set(original):
            assert len(key) == length
        if not added:
            assert set(new) == set(original)
    # Existing-row queue arithmetic is calculated from DB-read baseline timings.
    direct = 0
    for key, wo in work.items():
        ordered = sorted(
            (op for op in ops.values() if op.work_order_id == key),
            key=lambda op: (op.sequence_number, op.operation_id),
        )
        cumulative = timedelta(0)
        for op in ordered:
            if (
                wo.sales_order_id in qualifying
                and op.work_center_id in centers
                and config.window_start <= _time(op.actual_start_at) < config.window_end
            ):
                seconds = (
                    Decimal((op.planned_end_at - op.planned_start_at) // timedelta(microseconds=1))
                    / 1_000_000
                )
                delay = _ceil(seconds * (config.queue_time_multiplier - 1))
                cumulative += timedelta(seconds=delay)
                direct += delay > 0
            actual = actual_ops[op.operation_id]
            assert actual.actual_start_at == _time(op.actual_start_at) + cumulative
            assert actual.actual_end_at == _time(op.actual_end_at) + cumulative
            assert (actual.planned_start_at, actual.planned_end_at) == (
                op.planned_start_at,
                op.planned_end_at,
            )
        delta = _time(actual_work[key].actual_end_at) - _time(wo.actual_end_at)
        assert delta == cumulative
        for model, fields in (
            (QualityInspection, ("inspection_at",)),
            (Rework, ("rework_start_at", "rework_end_at")),
        ):
            actual_rows = _map(after, model)
            for row in _rows(before, model):
                if _values(row)["work_order_id"] == key:
                    for field in fields:
                        assert (
                            getattr(actual_rows[str(_key(row)[0])], field)
                            == getattr(row, field) + delta
                        )
    for dl in _rows(before, Delivery):
        old_completion = max(
            _time(w.actual_end_at) for w in work.values() if w.sales_order_id == dl.sales_order_id
        )
        completion = max(
            _time(w.actual_end_at)
            for w in actual_work.values()
            if w.sales_order_id == dl.sales_order_id
        )
        assert _map(after, Delivery)[dl.delivery_id].delivery_at == (
            dl.delivery_at + (completion - old_completion)
        )
    # Creation topology is checked from PostgreSQL, not inferred from HGT labels.
    new_requirements = [
        r
        for r in _rows(after, MaterialRequirement)
        if actual_work[r.work_order_id].sales_order_id in added
    ]
    new_pos = [
        r for key, r in _map(after, PurchaseOrder).items() if key not in _map(before, PurchaseOrder)
    ]
    assert len(new_pos) == len(new_requirements)
    for order_id in added:
        owned_work = [w for w in actual_work.values() if w.sales_order_id == order_id]
        assert owned_work and any(d.sales_order_id == order_id for d in _rows(after, Delivery))
        for wo in owned_work:
            assert any(o.work_order_id == wo.work_order_id for o in actual_ops.values())
            assert any(q.work_order_id == wo.work_order_id for q in _rows(after, QualityInspection))
    for mr in new_requirements:
        order = actual_orders[actual_work[mr.work_order_id].sales_order_id]
        matches = [
            po
            for po in new_pos
            if po.material_id == mr.material_id
            and po.ordered_at == order.order_at
            and po.actual_receipt_at == mr.need_by_at
            and po.ordered_quantity == mr.required_quantity
        ]
        assert matches
        for po in matches:
            assert (
                po.received_quantity == po.ordered_quantity
                and po.promised_receipt_at == mr.need_by_at
            )
            assert po.status == "RECEIVED" and po.ordered_at < mr.need_by_at
            assert any(
                old.supplier_id == po.supplier_id
                and old.material_id == po.material_id
                and old.ordered_at <= order.order_at
                for old in _rows(before, PurchaseOrder)
            )
    queue_edges = [
        link
        for link in result.ground_truth.causal_chain
        if link.relationship == "adds_operation_queue_delay"
    ]
    if queue == "1":
        assert not queue_edges and direct == 0
    else:
        assert queue_edges and direct > 0
    if arrival == queue == "1":
        assert not result.ground_truth.affected_entities_by_table
        assert not result.ground_truth.causal_chain
        assert after.dataset_version.dataset_version_id != before.dataset_version.dataset_version_id
        for name in CANONICAL_TABLE_ORDER:
            assert {_key(r): _values(r, semantic=True) for r in after.rows_for(name)} == {
                _key(r): _values(r, semantic=True) for r in before.rows_for(name)
            }
    if targeted_case and added:
        assert len(set(_map(after, Rework)) - set(_map(before, Rework))) == 1
    _assert_created_threads(before, after, added, centers, config)


def _assert_clone(actual: Base, source: Base, rewrites: Mapping[str, object]) -> None:
    expected = _values(source, semantic=True)
    expected.update(rewrites)
    values = _values(actual, semantic=True)
    for column in source.__mapper__.primary_key:
        expected.pop(column.name, None)
        values.pop(column.name, None)
    assert values == expected


def _assert_created_threads(
    before: GeneratedDataset,
    after: GeneratedDataset,
    added: set[str],
    centers: set[str],
    config: CapacitySurgeConfig,
) -> None:
    """Independent clone/timing oracle using the persisted source template.

    The acceptance fixtures have one WO and inspection per source order; their
    unchanged SalesOrder fields identify the template without using HGT edges or
    copying the implementation's hashing/ranking algorithm.
    """
    orders = _map(before, SalesOrder)
    actual_orders = _map(after, SalesOrder)
    for order_id in added:
        order = actual_orders[order_id]
        candidates = [
            old
            for old in orders.values()
            if {k: v for k, v in _values(old, semantic=True).items() if k != "sales_order_id"}
            == {k: v for k, v in _values(order, semantic=True).items() if k != "sales_order_id"}
        ]
        assert len(candidates) == 1
        source_order = candidates[0]
        source_work = [
            w for w in _rows(before, WorkOrder) if w.sales_order_id == source_order.sales_order_id
        ]
        created_work = [w for w in _rows(after, WorkOrder) if w.sales_order_id == order_id]
        assert len(source_work) == len(created_work) == 1
        source, actual = source_work[0], created_work[0]
        source_ops = sorted(
            (o for o in _rows(before, Operation) if o.work_order_id == source.work_order_id),
            key=lambda o: o.sequence_number,
        )
        created_ops = sorted(
            (o for o in _rows(after, Operation) if o.work_order_id == actual.work_order_id),
            key=lambda o: o.sequence_number,
        )
        assert len(created_ops) == len(source_ops)
        operation_ids: dict[str, str] = {}
        cumulative = timedelta(0)
        for old_op, new_op in zip(source_ops, created_ops, strict=True):
            if (
                old_op.work_center_id in centers
                and config.window_start <= _time(old_op.actual_start_at) < config.window_end
            ):
                microseconds = (old_op.planned_end_at - old_op.planned_start_at) // timedelta(
                    microseconds=1
                )
                cumulative += timedelta(
                    seconds=_ceil(
                        Decimal(microseconds) * (config.queue_time_multiplier - 1) / 1_000_000,
                    )
                )
            _assert_clone(
                new_op,
                old_op,
                {
                    "work_order_id": actual.work_order_id,
                    "actual_start_at": _time(old_op.actual_start_at) + cumulative,
                    "actual_end_at": _time(old_op.actual_end_at) + cumulative,
                },
            )
            operation_ids[old_op.operation_id] = new_op.operation_id
        start = (
            min(_time(o.actual_start_at) for o in created_ops)
            if cumulative
            else source.actual_start_at
        )
        end = (
            max(_time(o.actual_end_at) for o in created_ops) if cumulative else source.actual_end_at
        )
        _assert_clone(
            actual,
            source,
            {"sales_order_id": order_id, "actual_start_at": start, "actual_end_at": end},
        )
        delta = _time(end) - _time(source.actual_end_at)
        source_qi = [
            q for q in _rows(before, QualityInspection) if q.work_order_id == source.work_order_id
        ]
        created_qi = [
            q for q in _rows(after, QualityInspection) if q.work_order_id == actual.work_order_id
        ]
        assert len(source_qi) == len(created_qi) == 1
        old_qi, new_qi = source_qi[0], created_qi[0]
        _assert_clone(
            new_qi,
            old_qi,
            {
                "work_order_id": actual.work_order_id,
                "operation_id": operation_ids[old_qi.operation_id] if old_qi.operation_id else None,
                "inspection_at": old_qi.inspection_at + delta,
            },
        )
        source_rw = [r for r in _rows(before, Rework) if r.inspection_id == old_qi.inspection_id]
        created_rw = [r for r in _rows(after, Rework) if r.inspection_id == new_qi.inspection_id]
        assert len(source_rw) == len(created_rw)
        for old_rw, new_rw in zip(source_rw, created_rw, strict=True):
            _assert_clone(
                new_rw,
                old_rw,
                {
                    "inspection_id": new_qi.inspection_id,
                    "work_order_id": actual.work_order_id,
                    "rework_start_at": old_rw.rework_start_at + delta,
                    "rework_end_at": old_rw.rework_end_at + delta,
                },
            )
        source_mr = sorted(
            (
                r
                for r in _rows(before, MaterialRequirement)
                if r.work_order_id == source.work_order_id
            ),
            key=lambda r: r.material_id,
        )
        created_mr = sorted(
            (
                r
                for r in _rows(after, MaterialRequirement)
                if r.work_order_id == actual.work_order_id
            ),
            key=lambda r: r.material_id,
        )
        assert len(source_mr) == len(created_mr)
        for old_mr, new_mr in zip(source_mr, created_mr, strict=True):
            _assert_clone(new_mr, old_mr, {"work_order_id": actual.work_order_id})
        source_dl = sorted(
            (d for d in _rows(before, Delivery) if d.sales_order_id == source_order.sales_order_id),
            key=lambda d: d.delivery_at,
        )
        created_dl = sorted(
            (d for d in _rows(after, Delivery) if d.sales_order_id == order_id),
            key=lambda d: d.delivery_at,
        )
        assert len(source_dl) == len(created_dl)
        for old_dl, new_dl in zip(source_dl, created_dl, strict=True):
            _assert_clone(
                new_dl,
                old_dl,
                {"sales_order_id": order_id, "delivery_at": old_dl.delivery_at + delta},
            )


def test_repeat_and_failure_rollback(
    database_engine: Engine, targeted: GeneratedDataset, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = _round_trip(database_engine, targeted)
    reordered = GeneratedDataset(
        targeted.dataset_version,
        MappingProxyType(
            {
                name: tuple(reversed(rows))
                for name, rows in reversed(list(targeted.rows_by_table.items()))
            }
        ),
    )
    repeated = _round_trip(database_engine, reordered)
    assert canonical_business_payload(first.rows_by_table) == canonical_business_payload(
        repeated.rows_by_table,
    )
    original = _insert_dataset

    def fail_after_insert(connection: Connection, dataset: GeneratedDataset) -> None:
        original(connection, dataset)
        # Actual PostgreSQL PK rejection leaves a failed transaction to roll back.
        connection.execute(
            Base.metadata.tables["dataset_version"].insert(), _values(dataset.dataset_version)
        )

    with monkeypatch.context() as patch:
        patch.setattr(sys.modules[__name__], "_insert_dataset", fail_after_insert)
        with pytest.raises(IntegrityError):
            _round_trip(database_engine, targeted)
    _round_trip(database_engine, targeted)  # Also proves no residue after failed SQL.

    def fail_read(connection: Connection) -> GeneratedDataset:
        raise AssertionError("injected acceptance failure")

    with monkeypatch.context() as patch:
        patch.setattr(sys.modules[__name__], "_read_dataset", fail_read)
        with pytest.raises(AssertionError, match="injected acceptance failure"):
            _round_trip(database_engine, targeted)
    _round_trip(database_engine, targeted)
