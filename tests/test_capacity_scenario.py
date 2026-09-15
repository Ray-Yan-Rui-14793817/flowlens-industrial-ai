"""Independent business, identity, and HGT checks for the frozen Capacity contract."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from types import MappingProxyType
from typing import cast

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import object_session

from flowlens.data import Base
from flowlens.data.generation import (
    BUSINESS_TIMEZONE,
    GeneratedDataset,
    GenerationConfig,
    GenerationProfile,
    generate_baseline,
)
from flowlens.data.generation.canonical import canonical_business_payload, canonical_content_hash
from flowlens.data.models import (
    Customer,
    DatasetVersion,
    Delivery,
    Material,
    MaterialRequirement,
    Operation,
    Product,
    PurchaseOrder,
    QualityInspection,
    Rework,
    SalesOrder,
    Supplier,
    WorkCenter,
    WorkOrder,
)
from flowlens.data.scenarios import CapacitySurgeConfig, ScenarioResult, apply_scenario
from flowlens.data.scenarios import capacity as implementation
from flowlens.data.scenarios.config import default_demo_window
from flowlens.data.scenarios.transformer import ScenarioIdentity, build_scenario_identity

NOW = datetime(2026, 9, 1, tzinfo=UTC)
START = datetime(2026, 1, 15, tzinfo=BUSINESS_TIMEZONE)
FACTS = {
    "fact_sales_order": ("sales_order_id", "so_", "capacity-sales-order"),
    "fact_work_order": ("work_order_id", "wo_", "capacity-work-order"),
    "fact_operation": ("operation_id", "op_", "capacity-operation"),
    "fact_material_requirement": (
        "material_requirement_id",
        "mr_",
        "capacity-material-requirement",
    ),
    "fact_purchase_order": ("purchase_order_id", "po_", "capacity-supplemental-purchase-order"),
    "fact_quality_inspection": ("inspection_id", "qi_", "capacity-quality-inspection"),
    "fact_rework": ("rework_id", "rw_", "capacity-rework"),
    "fact_delivery": ("delivery_id", "dl_", "capacity-delivery"),
}
type Edge = tuple[str, str, str, str, str]


def _rows[T: Base](dataset: GeneratedDataset, cls: type[T]) -> tuple[T, ...]:
    return cast(tuple[T, ...], dataset.rows_for(cls.__tablename__))


def _config(arrival: str = "1.5", queue: str = "1.7", count: int = 2) -> CapacitySurgeConfig:
    return CapacitySurgeConfig(
        scenario_version="1.0.0",
        scenario_seed=20260901,
        window_start=START,
        window_end=START + timedelta(days=15),
        arrival_volume_multiplier=Decimal(arrival),
        queue_time_multiplier=Decimal(queue),
        affected_work_center_count=count,
    )


def _rebuild(base: GeneratedDataset, rows: dict[str, list[Base]]) -> GeneratedDataset:
    old = base.dataset_version
    values = {col.name: getattr(old, col.name) for col in old.__mapper__.columns}
    values.update(
        content_hash=canonical_content_hash(rows),
        row_count_total=sum(len(items) for items in rows.values()),
    )
    return GeneratedDataset(
        DatasetVersion(**values),
        MappingProxyType({table: tuple(items) for table, items in rows.items()}),
    )


@pytest.fixture
def baseline() -> GeneratedDataset:
    """Two orders, four WOs, twelve ops, null/non-null QI parents and split deliveries."""
    base = generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.TEST,
            seed=20260824,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=NOW,
        )
    )
    rows = {table: list(items) for table, items in base.rows_by_table.items()}
    for table in FACTS:
        rows[table] = []
    dataset_id = base.dataset_version.dataset_version_id
    common = {"dataset_version_id": dataset_id}
    centers = _rows(base, WorkCenter)
    product_id = _rows(base, Product)[0].product_id
    customer_id = _rows(base, Customer)[0].customer_id
    material_id = _rows(base, Material)[0].material_id
    suppliers = [row.supplier_id for row in _rows(base, Supplier)]
    for n, supplier_id in enumerate(suppliers[:2]):
        rows["fact_purchase_order"].append(
            PurchaseOrder(
                **common,
                purchase_order_id=f"history-{n}",
                supplier_id=supplier_id,
                material_id=material_id,
                ordered_at=START - timedelta(days=2),
                promised_receipt_at=START,
                actual_receipt_at=START,
                ordered_quantity=Decimal("100"),
                received_quantity=Decimal("100"),
                status="RECEIVED",
            )
        )
    for order_n in range(2):
        order_id = f"order-{order_n}"
        order_at = START + timedelta(days=order_n * 2)
        rows["fact_sales_order"].append(
            SalesOrder(
                **common,
                sales_order_id=order_id,
                customer_id=customer_id,
                product_id=product_id,
                order_at=order_at,
                promised_delivery_at=order_at + timedelta(days=4),
                order_quantity=6,
                priority="HIGH" if order_n else "NORMAL",
                status="DELIVERED",
            )
        )
        for wo_n in range(2):
            wo_id = f"work-{order_n}-{wo_n}"
            start = order_at + timedelta(days=2, hours=wo_n * 2)
            end = start + timedelta(hours=3)
            rows["fact_work_order"].append(
                WorkOrder(
                    **common,
                    work_order_id=wo_id,
                    sales_order_id=order_id,
                    product_id=product_id,
                    planned_start_at=start - timedelta(days=1),
                    planned_end_at=end - timedelta(days=1),
                    actual_start_at=start,
                    actual_end_at=end,
                    planned_quantity=3,
                    completed_quantity=3,
                    status="COMPLETED",
                )
            )
            for op_n in range(3):
                op_start = start + timedelta(hours=op_n)
                rows["fact_operation"].append(
                    Operation(
                        **common,
                        operation_id=f"op-{order_n}-{wo_n}-{op_n}",
                        work_order_id=wo_id,
                        work_center_id=centers[op_n].work_center_id,
                        sequence_number=op_n + 1,
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
                    material_requirement_id=f"mr-{order_n}-{wo_n}",
                    work_order_id=wo_id,
                    material_id=material_id,
                    required_quantity=Decimal("3.1250"),
                    need_by_at=start - timedelta(days=1),
                )
            )
            for qi_n in range(2):
                rows["fact_quality_inspection"].append(
                    QualityInspection(
                        **common,
                        inspection_id=f"qi-{order_n}-{wo_n}-{qi_n}",
                        work_order_id=wo_id,
                        operation_id=f"op-{order_n}-{wo_n}-2" if qi_n == 0 else None,
                        inspection_at=end + timedelta(hours=1 + qi_n),
                        inspection_type="FINAL",
                        inspected_quantity=3,
                        passed_quantity=2,
                        failed_quantity=1,
                        defect_category="ASSEMBLY",
                        severity="LOW",
                        result="FAIL",
                    )
                )
            rows["fact_rework"].append(
                Rework(
                    **common,
                    rework_id=f"rw-{order_n}-{wo_n}",
                    inspection_id=f"qi-{order_n}-{wo_n}-0",
                    work_order_id=wo_id,
                    work_center_id=centers[1].work_center_id,
                    rework_start_at=end + timedelta(hours=3),
                    rework_end_at=end + timedelta(hours=4),
                    rework_quantity=1,
                    rework_reason="SYNTHETIC_ASSEMBLY_CORRECTION",
                )
            )
        for dl_n in range(2):
            rows["fact_delivery"].append(
                Delivery(
                    **common,
                    delivery_id=f"dl-{order_n}-{dl_n}",
                    sales_order_id=order_id,
                    delivery_at=order_at + timedelta(days=3, hours=dl_n),
                    delivered_quantity=3,
                )
            )
    return _rebuild(base, rows)


def _digest(payload: dict[str, str | int]) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _rank(ids: set[str], namespace: str, purpose: str) -> list[str]:
    return sorted(
        ids,
        key=lambda key: (
            _digest(
                {
                    "entity_identity": key,
                    "purpose": purpose,
                    "scenario_namespace": namespace,
                }
            ),
            key,
        ),
    )


def _targets(base: GeneratedDataset, config: CapacitySurgeConfig) -> tuple[str, ...]:
    orders = {
        so.sales_order_id
        for so in _rows(base, SalesOrder)
        if config.window_start <= so.order_at < config.window_end
    }
    work_orders = {wo.work_order_id for wo in _rows(base, WorkOrder) if wo.sales_order_id in orders}
    candidates = {
        op.work_center_id for op in _rows(base, Operation) if op.work_order_id in work_orders
    }
    namespace = build_scenario_identity(base, config).namespace
    return tuple(
        sorted(
            _rank(candidates, namespace, "capacity-work-center")[
                : config.affected_work_center_count
            ]
        )
    )


def _values(row: Base) -> dict[str, object]:
    return {
        col.name: getattr(row, col.name)
        for col in row.__mapper__.columns
        if col.name != "dataset_version_id"
    }


def _key(row: Base) -> tuple[str, str]:
    return row.__tablename__, str(getattr(row, row.__mapper__.primary_key[0].name))


def _edge(source: Base, target: Base, relationship: str) -> Edge:
    return (*_key(source), *_key(target), relationship)


def _edges(result: ScenarioResult) -> set[Edge]:
    return {
        (
            link.source_table,
            link.source_entity_id,
            link.target_table,
            link.target_entity_id,
            link.relationship,
        )
        for link in result.ground_truth.causal_chain
    }


def _assert_integrity(base: GeneratedDataset, result: ScenarioResult) -> None:
    actual = result.dataset
    before = {
        _key(row): row
        for _, row in base.iter_business_rows()
        if len(row.__mapper__.primary_key) == 1
    }
    after = {
        _key(row): row
        for _, row in actual.iter_business_rows()
        if len(row.__mapper__.primary_key) == 1
    }
    expected_affected: dict[str, set[str]] = defaultdict(set)
    for table, row in actual.iter_business_rows():
        if len(row.__mapper__.primary_key) == 1:
            key = _key(row)
            if key not in before or _values(row) != _values(before[key]):
                expected_affected[table].add(key[1])
            if key in before:
                assert row is not before[key]
                assert inspect(row) is not inspect(before[key])
        assert object_session(row) is None
        assert row.__dict__["dataset_version_id"] == actual.dataset_version.dataset_version_id
        for col in row.__mapper__.columns:
            value = getattr(row, col.name)
            length = getattr(col.type, "length", None)
            if length and value is not None:
                assert len(value) <= length
            for fk in col.foreign_keys:
                if value is not None and fk.column.table.name != "dataset_version":
                    assert (fk.column.table.name, value) in after
    assert dict(result.ground_truth.affected_entities_by_table) == {
        table: tuple(sorted(ids)) for table, ids in expected_affected.items()
    }
    assert set(expected_affected) <= FACTS.keys()
    allowed = {(table, key) for table, ids in expected_affected.items() for key in ids}
    allowed |= {("dim_work_center", key) for key in result.ground_truth.target_entity_ids}
    for st, si, tt, ti, _ in _edges(result):
        assert (st, si) in allowed & after.keys()
        assert (tt, ti) in allowed & after.keys()
    assert actual.content_hash == canonical_content_hash(actual.rows_by_table)
    assert actual.row_count_total == sum(map(len, actual.rows_by_table.values()))
    assert actual.dataset_version.dataset_version_id != base.dataset_version.dataset_version_id


@pytest.mark.parametrize("arrival,queue", [("1.5", "1.7"), ("1.5", "1"), ("1", "1.7"), ("1", "1")])
def test_four_modes_and_immutable_canonical_result(
    baseline: GeneratedDataset,
    arrival: str,
    queue: str,
) -> None:
    config = _config(arrival, queue)
    before = canonical_business_payload(baseline.rows_by_table)
    metadata = _values(baseline.dataset_version)
    result = apply_scenario(baseline, config, generated_at=NOW)
    assert result.ground_truth.target_entity_ids == _targets(baseline, config)
    assert len(_rows(result.dataset, SalesOrder)) == (3 if arrival != "1" else 2)
    direct = [
        link
        for link in result.ground_truth.causal_chain
        if link.relationship == "adds_operation_queue_delay"
    ]
    assert bool(direct) == (queue != "1")
    if queue == "1":
        for cls in (Operation, WorkOrder, QualityInspection, Rework, Delivery):
            old = {_key(row): _values(row) for row in _rows(baseline, cls)}
            for row in _rows(result.dataset, cls):
                if _key(row) in old:
                    assert _values(row) == old[_key(row)]
        if arrival == "1":
            assert not result.ground_truth.affected_entities_by_table
            assert not result.ground_truth.causal_chain
            assert result.dataset.content_hash != baseline.content_hash
        else:
            assert result.ground_truth.affected_entities_by_table["fact_operation"]
    _assert_integrity(baseline, result)
    repeated = apply_scenario(baseline, config, generated_at=NOW + timedelta(days=100))
    reversed_base = _rebuild(
        baseline,
        {
            name: list(reversed(rows))
            for name, rows in reversed(list(baseline.rows_by_table.items()))
        },
    )
    reordered = apply_scenario(reversed_base, config, generated_at=NOW)
    for other in (repeated, reordered):
        assert canonical_business_payload(other.dataset.rows_by_table) == (
            canonical_business_payload(result.dataset.rows_by_table)
        )
        assert other.dataset.content_hash == result.dataset.content_hash
        assert other.ground_truth == result.ground_truth
    assert canonical_business_payload(baseline.rows_by_table) == before
    assert _values(baseline.dataset_version) == metadata


@pytest.mark.parametrize("queue", ["1", "1.7"])
def test_exact_N_template_cycle_complete_threads_all_ids_and_procurement(
    baseline: GeneratedDataset,
    queue: str,
) -> None:
    config = _config("3.25", queue)
    result = apply_scenario(baseline, config, generated_at=NOW)
    identity = build_scenario_identity(baseline, config)
    orders = {so.sales_order_id: so for so in _rows(baseline, SalesOrder)}
    templates = _rank(set(orders), identity.namespace, "capacity-arrival-template")
    # N=2 despite four WOs, twelve operations, four deliveries, and order quantity six.
    added_count = 5
    actual = {
        _key(row): row
        for _, row in result.dataset.iter_business_rows()
        if len(row.__mapper__.primary_key) == 1
    }
    expected_creation: set[Edge] = set()
    created: set[tuple[str, str]] = set()

    def expect(source: Base, payload: dict[str, str | int], **rewrites: str | None) -> Base:
        table = source.__tablename__
        pk, prefix, purpose = FACTS[table]
        length = 37 if prefix in {"so_", "wo_", "po_"} else 45
        new_id = (
            prefix
            + _digest({"purpose": purpose, "scenario_namespace": identity.namespace, **payload})[
                :length
            ]
        )
        row = actual[table, new_id]
        # Timing of a copied thread matches its independently transformed source thread.
        expected = _values(actual[_key(source)])
        expected.update({pk: new_id, **rewrites})
        assert _values(row) == expected
        created.add((table, new_id))
        return row

    for i in range(added_count):
        source = orders[templates[i % 2]]
        order = cast(
            SalesOrder,
            expect(
                source,
                {
                    "source_sales_order_id": source.sales_order_id,
                    "arrival_ordinal": i,
                },
            ),
        )
        for center_id in result.ground_truth.target_entity_ids:
            expected_creation.add(
                (
                    "dim_work_center",
                    center_id,
                    "fact_sales_order",
                    order.sales_order_id,
                    "receives_added_sales_order_arrival",
                )
            )
        for wo in [
            w for w in _rows(baseline, WorkOrder) if w.sales_order_id == source.sales_order_id
        ]:
            new_wo = cast(
                WorkOrder,
                expect(
                    wo,
                    {
                        "scenario_sales_order_id": order.sales_order_id,
                        "source_work_order_id": wo.work_order_id,
                    },
                    sales_order_id=order.sales_order_id,
                ),
            )
            expected_creation.add(_edge(order, new_wo, "creates_work_order"))
            new_ops: dict[str, Operation] = {}
            for op in [
                o for o in _rows(baseline, Operation) if o.work_order_id == wo.work_order_id
            ]:
                new_op = cast(
                    Operation,
                    expect(
                        op,
                        {
                            "scenario_work_order_id": new_wo.work_order_id,
                            "source_operation_id": op.operation_id,
                        },
                        work_order_id=new_wo.work_order_id,
                    ),
                )
                new_ops[op.operation_id] = new_op
                expected_creation.add(_edge(new_wo, new_op, "creates_operation"))
            for mr in [
                m
                for m in _rows(baseline, MaterialRequirement)
                if m.work_order_id == wo.work_order_id
            ]:
                new_mr = cast(
                    MaterialRequirement,
                    expect(
                        mr,
                        {
                            "scenario_work_order_id": new_wo.work_order_id,
                            "source_material_requirement_id": mr.material_requirement_id,
                        },
                        work_order_id=new_wo.work_order_id,
                    ),
                )
                expected_creation.add(_edge(new_wo, new_mr, "creates_material_requirement"))
                suppliers = {
                    po.supplier_id
                    for po in _rows(baseline, PurchaseOrder)
                    if po.material_id == mr.material_id and po.ordered_at <= order.order_at
                }
                chosen = _rank(suppliers, identity.namespace, "capacity-supplemental-supplier")[0]
                po_id = (
                    "po_"
                    + _digest(
                        {
                            "purpose": "capacity-supplemental-purchase-order",
                            "scenario_namespace": identity.namespace,
                            "scenario_material_requirement_id": new_mr.material_requirement_id,
                            "supplier_id": chosen,
                        }
                    )[:37]
                )
                po = actual["fact_purchase_order", po_id]
                assert _values(po) == dict(
                    purchase_order_id=po_id,
                    supplier_id=chosen,
                    material_id=mr.material_id,
                    ordered_at=order.order_at,
                    promised_receipt_at=mr.need_by_at,
                    actual_receipt_at=mr.need_by_at,
                    ordered_quantity=mr.required_quantity,
                    received_quantity=mr.required_quantity,
                    status="RECEIVED",
                )
                created.add(("fact_purchase_order", po_id))
                expected_creation.add(_edge(new_mr, po, "creates_supplemental_procurement"))
            for qi in [
                q for q in _rows(baseline, QualityInspection) if q.work_order_id == wo.work_order_id
            ]:
                parent = new_ops[qi.operation_id] if qi.operation_id else new_wo
                new_qi = cast(
                    QualityInspection,
                    expect(
                        qi,
                        {
                            "scenario_work_order_id": new_wo.work_order_id,
                            "source_inspection_id": qi.inspection_id,
                        },
                        work_order_id=new_wo.work_order_id,
                        operation_id=new_ops[qi.operation_id].operation_id
                        if qi.operation_id
                        else None,
                    ),
                )
                expected_creation.add(_edge(parent, new_qi, "creates_quality_inspection"))
                for rw in [
                    r for r in _rows(baseline, Rework) if r.inspection_id == qi.inspection_id
                ]:
                    new_rw = expect(
                        rw,
                        {
                            "scenario_inspection_id": new_qi.inspection_id,
                            "source_rework_id": rw.rework_id,
                        },
                        inspection_id=new_qi.inspection_id,
                        work_order_id=new_wo.work_order_id,
                    )
                    expected_creation.add(_edge(new_qi, new_rw, "creates_rework"))
        for dl in [
            d for d in _rows(baseline, Delivery) if d.sales_order_id == source.sales_order_id
        ]:
            new_dl = expect(
                dl,
                {
                    "scenario_sales_order_id": order.sales_order_id,
                    "source_delivery_id": dl.delivery_id,
                },
                sales_order_id=order.sales_order_id,
            )
            expected_creation.add(_edge(order, new_dl, "creates_delivery"))
    assert {
        e for e in _edges(result) if e[4].startswith(("creates_", "receives_"))
    } == expected_creation
    before_keys = {
        _key(row)
        for _, row in baseline.iter_business_rows()
        if len(row.__mapper__.primary_key) == 1
    }
    assert actual.keys() - before_keys == created
    assert len(_rows(result.dataset, PurchaseOrder)) == 2 + added_count * 2
    _assert_integrity(baseline, result)


def test_queue_arithmetic_accumulation_and_exact_full_causal_graph(
    baseline: GeneratedDataset,
) -> None:
    config = _config("1", "1.7")
    result = apply_scenario(baseline, config, generated_at=NOW)
    selected = set(_targets(baseline, config))
    actual = {
        _key(row): row
        for _, row in result.dataset.iter_business_rows()
        if len(row.__mapper__.primary_key) == 1
    }
    expected_edges: set[Edge] = set()
    delta_by_wo: dict[str, timedelta] = {}
    for wo in _rows(baseline, WorkOrder):
        ops = sorted(
            [o for o in _rows(baseline, Operation) if o.work_order_id == wo.work_order_id],
            key=lambda o: (o.sequence_number, o.operation_id),
        )
        cumulative = timedelta(0)
        sources: list[Operation] = []
        for op in ops:
            direct = timedelta(0)
            if op.work_center_id in selected:
                duration = op.planned_end_at - op.planned_start_at
                microseconds = duration // timedelta(microseconds=1)
                direct = timedelta(
                    seconds=math.ceil(
                        Fraction(microseconds, 1_000_000)
                        * Fraction(config.queue_time_multiplier - 1)
                    )
                )
                assert direct == timedelta(seconds=2)  # ceil(1.5 * 0.7), not runtime-derived.
            cumulative += direct
            new = cast(Operation, actual[_key(op)])
            assert new.actual_start_at == cast(datetime, op.actual_start_at) + cumulative
            assert new.actual_end_at == cast(datetime, op.actual_end_at) + cumulative
            assert new.planned_start_at == op.planned_start_at
            assert new.planned_end_at == op.planned_end_at
            assert new.actual_end_at - new.actual_start_at == timedelta(hours=1)
            for upstream in sources:
                expected_edges.add(_edge(upstream, op, "shifts_downstream_operation"))
            if direct:
                expected_edges.add(
                    (
                        "dim_work_center",
                        op.work_center_id,
                        "fact_operation",
                        op.operation_id,
                        "adds_operation_queue_delay",
                    )
                )
                sources.append(op)
        new_wo = cast(WorkOrder, actual[_key(wo)])
        assert new_wo.actual_start_at == cast(Operation, actual[_key(ops[0])]).actual_start_at
        assert new_wo.actual_end_at == cast(datetime, wo.actual_end_at) + cumulative
        delta_by_wo[wo.work_order_id] = cumulative
        expected_edges.add(_edge(ops[-1], wo, "shifts_work_order_completion"))
        for qi in _rows(baseline, QualityInspection):
            if qi.work_order_id == wo.work_order_id:
                assert cast(QualityInspection, actual[_key(qi)]).inspection_at == (
                    qi.inspection_at + cumulative
                )
                expected_edges.add(_edge(wo, qi, "shifts_inspection_time"))
        for rw in _rows(baseline, Rework):
            if rw.work_order_id == wo.work_order_id:
                for column in ("rework_start_at", "rework_end_at"):
                    assert getattr(actual[_key(rw)], column) == getattr(rw, column) + cumulative
                expected_edges.add(_edge(wo, rw, "shifts_rework_window"))
    for dl in _rows(baseline, Delivery):
        owners = [wo for wo in _rows(baseline, WorkOrder) if wo.sales_order_id == dl.sales_order_id]
        pre = max(cast(datetime, wo.actual_end_at) for wo in owners)
        post = max(
            cast(datetime, wo.actual_end_at) + delta_by_wo[wo.work_order_id] for wo in owners
        )
        assert cast(Delivery, actual[_key(dl)]).delivery_at == dl.delivery_at + (post - pre)
        for wo in owners:
            expected_edges.add(_edge(wo, dl, "shifts_delivery_time"))
    assert _edges(result) == expected_edges
    _assert_integrity(baseline, result)


def _one_center(base: GeneratedDataset) -> str:
    center = _rows(base, WorkCenter)[0].work_center_id
    for op in _rows(base, Operation):
        op.work_center_id = center
    return center


def test_multiple_work_orders_use_one_order_anchor_delta(baseline: GeneratedDataset) -> None:
    _one_center(baseline)
    for op in _rows(baseline, Operation):
        seconds = 4000 if op.work_order_id == "work-0-0" else 1
        op.planned_end_at = op.planned_start_at + timedelta(seconds=seconds)
    result = apply_scenario(baseline, _config("1", "2", 1), generated_at=NOW)
    deliveries = {dl.delivery_id: dl for dl in _rows(result.dataset, Delivery)}
    # WO0 moves 12,000s, WO1 moves 3s; WO1 was 7,200s later before intervention.
    # Order delta = 4,800s, neither 12,000s nor 12,003s.
    for dl in _rows(baseline, Delivery):
        if dl.sales_order_id == "order-0":
            assert deliveries[dl.delivery_id].delivery_at == dl.delivery_at + timedelta(
                seconds=4800
            )
            links = [
                edge
                for edge in _edges(result)
                if edge[3] == dl.delivery_id and edge[4] == "shifts_delivery_time"
            ]
            assert {edge[1] for edge in links} == {"work-0-0", "work-0-1"}
    _assert_integrity(baseline, result)


def test_binding_operation_tie_uses_maximum_canonical_tuple(baseline: GeneratedDataset) -> None:
    _one_center(baseline)
    ops = [op for op in _rows(baseline, Operation) if op.work_order_id == "work-0-0"]
    finish = cast(datetime, ops[-1].actual_end_at)
    for n, op in enumerate(ops):
        op.planned_end_at = op.planned_start_at + timedelta(seconds=1)
        op.actual_end_at = finish - timedelta(seconds=n + 1)
    wo = _rows(baseline, WorkOrder)[0]
    wo.actual_end_at = finish - timedelta(seconds=1)
    result = apply_scenario(baseline, _config("1", "2", 1), generated_at=NOW)
    ties = [
        edge
        for edge in _edges(result)
        if edge[3] == wo.work_order_id and edge[4] == "shifts_work_order_completion"
    ]
    assert ties == [_edge(ops[-1], wo, "shifts_work_order_completion")]
    actual_ops = {op.operation_id: op for op in _rows(result.dataset, Operation)}
    assert {actual_ops[op.operation_id].actual_end_at for op in ops} == {finish}


def test_zero_completion_delta_has_no_downstream_completion_edges(
    baseline: GeneratedDataset,
) -> None:
    config = _config("1", "2", 1)
    center = _targets(baseline, config)[0]
    other = next(
        wc.work_center_id for wc in _rows(baseline, WorkCenter) if wc.work_center_id != center
    )
    ops = [op for op in _rows(baseline, Operation) if op.work_order_id == "work-0-0"]
    ops[0].work_center_id = other
    ops[0].actual_end_at = cast(datetime, ops[0].actual_start_at) + timedelta(hours=20)
    ops[1].work_center_id, ops[2].work_center_id = center, other
    wo = _rows(baseline, WorkOrder)[0]
    wo.actual_end_at = ops[0].actual_end_at
    result = apply_scenario(baseline, config, generated_at=NOW)
    new_wo = next(
        w for w in _rows(result.dataset, WorkOrder) if w.work_order_id == wo.work_order_id
    )
    assert _values(new_wo) == _values(wo)
    assert not any(
        edge[1] == wo.work_order_id
        or (edge[3] == wo.work_order_id and edge[4] == "shifts_work_order_completion")
        for edge in _edges(result)
    )
    assert not any(
        edge[4] == "shifts_delivery_time" and edge[3].startswith("dl-0-") for edge in _edges(result)
    )
    _assert_integrity(baseline, result)


def test_window_boundaries_real_graph_and_optional_reworks(baseline: GeneratedDataset) -> None:
    config = _config("2", "1.7", 3)
    _rows(baseline, SalesOrder)[1].order_at = config.window_end
    first = _rows(baseline, Operation)[0]
    first.actual_start_at = config.window_start - timedelta(hours=1)
    first.actual_end_at = config.window_start
    _rows(baseline, WorkOrder)[0].actual_start_at = first.actual_start_at
    rows = {name: list(items) for name, items in baseline.rows_by_table.items()}
    rows["fact_rework"] = []
    baseline = _rebuild(baseline, rows)
    result = apply_scenario(baseline, config, generated_at=NOW)
    assert len(_rows(result.dataset, SalesOrder)) == 3  # N=1, order_at == end excluded.
    actual = {
        _key(row): row
        for _, row in result.dataset.iter_business_rows()
        if len(row.__mapper__.primary_key) == 1
    }
    assert _values(actual[_key(first)]) == _values(first)
    assert not any(
        edge[3] == first.operation_id and edge[4] == "adds_operation_queue_delay"
        for edge in _edges(result)
    )
    for wo in _rows(baseline, WorkOrder):
        if wo.sales_order_id == "order-1":
            assert _values(actual[_key(wo)]) == _values(wo)
    assert len(result.ground_truth.target_entity_ids) == 3
    assert (
        _rows(baseline, WorkCenter)[3].work_center_id not in result.ground_truth.target_entity_ids
    )
    assert not _rows(result.dataset, Rework)
    _assert_integrity(baseline, result)


def test_queue_eligibility_uses_pre_intervention_not_shifted_start(
    baseline: GeneratedDataset,
) -> None:
    _one_center(baseline)
    config = _config("1", "2", 1)
    ops = [op for op in _rows(baseline, Operation) if op.work_order_id == "work-0-0"]
    for n, op in enumerate(ops):
        op.actual_start_at = config.window_end - timedelta(seconds=4 - n)
        op.actual_end_at = op.actual_start_at + timedelta(seconds=1)
        op.planned_end_at = op.planned_start_at + timedelta(seconds=10)
    wo = _rows(baseline, WorkOrder)[0]
    wo.actual_start_at, wo.actual_end_at = ops[0].actual_start_at, ops[-1].actual_end_at
    result = apply_scenario(baseline, config, generated_at=NOW)
    assert {edge[3] for edge in _edges(result) if edge[4] == "adds_operation_queue_delay"} >= {
        op.operation_id for op in ops
    }
    updated = {op.operation_id: op for op in _rows(result.dataset, Operation)}
    for n, op in enumerate(ops):
        assert updated[op.operation_id].actual_start_at == (
            cast(datetime, op.actual_start_at) + timedelta(seconds=10 * (n + 1))
        )


@pytest.mark.parametrize(
    "failure,match",
    [
        ("centers", "insufficient candidate"),
        ("zero-n", "N == 0"),
        ("empty-operations", "insufficient candidate"),
        ("anchor", "completion anchors"),
        ("op-start", "actual timing"),
        ("op-end", "actual timing"),
        ("duration", "duration must be positive"),
        ("supplier", "no eligible historical"),
        ("need-by", "later than decision time"),
        ("inspection", "inspection parent"),
        ("rework", "Rework inspection parent"),
        ("duplicate", "duplicate Capacity"),
    ],
)
def test_explicit_invalid_input_rejections(
    baseline: GeneratedDataset,
    failure: str,
    match: str,
) -> None:
    config = _config(count=3)
    rows = {name: list(items) for name, items in baseline.rows_by_table.items()}
    if failure == "centers":
        config = replace(config, affected_work_center_count=4)
    elif failure == "zero-n":
        rows["fact_quality_inspection"] = []
    elif failure == "empty-operations":
        rows["fact_operation"] = []
    elif failure == "anchor":
        _rows(baseline, WorkOrder)[0].actual_end_at = None
    elif failure == "op-start":
        _rows(baseline, Operation)[0].actual_start_at = None
    elif failure == "op-end":
        _rows(baseline, Operation)[0].actual_end_at = None
    elif failure == "duration":
        op = _rows(baseline, Operation)[0]
        op.planned_end_at = op.planned_start_at
    elif failure == "supplier":
        for po in _rows(baseline, PurchaseOrder):
            po.ordered_at = config.window_end  # All history is future-only.
    elif failure == "need-by":
        for mr in _rows(baseline, MaterialRequirement):
            mr.need_by_at = START
    elif failure == "inspection":
        _rows(baseline, QualityInspection)[0].operation_id = "op-1-0-0"
    elif failure == "rework":
        _rows(baseline, Rework)[0].inspection_id = "qi-1-0-0"
    elif failure == "duplicate":
        rows["fact_delivery"].append(_rows(baseline, Delivery)[0])
    baseline = _rebuild(baseline, rows)
    before = canonical_business_payload(baseline.rows_by_table)
    with pytest.raises(ValueError, match=match):
        apply_scenario(baseline, config, generated_at=NOW)
    assert canonical_business_payload(baseline.rows_by_table) == before


@pytest.mark.parametrize("table", list(FACTS))
def test_all_generated_identity_families_reject_collision(
    baseline: GeneratedDataset,
    table: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = implementation._created_id
    existing = _key(baseline.rows_for(table)[0])[1]

    def collide(
        identity: ScenarioIdentity,
        prefix: str,
        purpose: str,
        **fields: str | int,
    ) -> str:
        return (
            existing if prefix == FACTS[table][1] else original(identity, prefix, purpose, **fields)
        )

    monkeypatch.setattr(implementation, "_created_id", collide)
    before = canonical_business_payload(baseline.rows_by_table)
    with pytest.raises(ValueError, match="ID collision"):
        apply_scenario(baseline, _config("2"), generated_at=NOW)
    assert canonical_business_payload(baseline.rows_by_table) == before


def test_generated_to_generated_collision_rejects(
    baseline: GeneratedDataset,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = implementation._created_id

    def collide(
        identity: ScenarioIdentity,
        prefix: str,
        purpose: str,
        **fields: str | int,
    ) -> str:
        return (
            "so_" + "f" * 37 if prefix == "so_" else original(identity, prefix, purpose, **fields)
        )

    monkeypatch.setattr(implementation, "_created_id", collide)
    with pytest.raises(ValueError, match="ID collision"):
        apply_scenario(baseline, _config("2"), generated_at=NOW)


def test_negative_order_delta_rejects(baseline: GeneratedDataset) -> None:
    _one_center(baseline)
    for wo in _rows(baseline, WorkOrder):
        wo.actual_end_at = cast(datetime, wo.actual_end_at) + timedelta(days=10)
    with pytest.raises(ValueError, match="negative Capacity order completion delta"):
        apply_scenario(baseline, _config("1", "2", 1), generated_at=NOW)


def test_completion_without_binding_operation_rejects(baseline: GeneratedDataset) -> None:
    config = _config("1", "2", 1)
    selected = _targets(baseline, config)[0]
    other = next(
        wc.work_center_id for wc in _rows(baseline, WorkCenter) if wc.work_center_id != selected
    )
    ops = [op for op in _rows(baseline, Operation) if op.work_order_id == "work-0-0"]
    ops[0].work_center_id = other
    ops[0].actual_end_at = cast(datetime, ops[0].actual_end_at) + timedelta(days=10)
    ops[1].work_center_id, ops[2].work_center_id = selected, other
    with pytest.raises(ValueError, match="no binding Operation"):
        apply_scenario(baseline, config, generated_at=NOW)


def test_hgt_endpoint_guard_rejects_nonexistent_or_unaffected_entity(
    baseline: GeneratedDataset,
) -> None:
    config = _config()
    identity = build_scenario_identity(baseline, config)
    effects = implementation._Effects(
        {name: list(items) for name, items in baseline.rows_by_table.items()},
        identity,
        set(),
    )
    order, wo = _rows(baseline, SalesOrder)[0], _rows(baseline, WorkOrder)[0]
    effects.link(order, wo, "creates_work_order")
    with pytest.raises(ValueError, match="HGT endpoint"):
        implementation._validate_hgt(effects, {})
    effects.affected["fact_work_order"].add("missing")
    with pytest.raises(ValueError, match="affected map references a missing"):
        implementation._validate_hgt(effects, {})


def test_future_supplier_cannot_win_historical_ranking(baseline: GeneratedDataset) -> None:
    config = _config("2", "1")
    namespace = build_scenario_identity(baseline, config).namespace
    suppliers = {supplier.supplier_id for supplier in _rows(baseline, Supplier)}
    ranking = _rank(suppliers, namespace, "capacity-supplemental-supplier")
    early, future = _rows(baseline, PurchaseOrder)
    early.supplier_id, future.supplier_id = ranking[-1], ranking[0]
    future.ordered_at = config.window_end
    result = apply_scenario(baseline, config, generated_at=NOW)
    for po in _rows(result.dataset, PurchaseOrder):
        if po.purchase_order_id.startswith("po_"):
            assert po.supplier_id == early.supplier_id
    _assert_integrity(baseline, result)


@pytest.mark.parametrize("column", ["planned_start_at", "planned_end_at"])
def test_missing_planned_operation_timing_rejects(
    baseline: GeneratedDataset,
    column: str,
) -> None:
    setattr(_rows(baseline, Operation)[0], column, None)
    with pytest.raises(ValueError, match="timing/completion anchors"):
        apply_scenario(baseline, _config(count=3), generated_at=NOW)


def test_early_real_c03_arrivals_require_historical_procurement() -> None:
    base = generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.TEST,
            seed=20260824,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=NOW,
        )
    )
    config = replace(
        _config(),
        window_start=datetime(2026, 1, 1, tzinfo=BUSINESS_TIMEZONE),
        window_end=datetime(2026, 4, 1, tzinfo=BUSINESS_TIMEZONE),
    )
    before = canonical_business_payload(base.rows_by_table)
    with pytest.raises(ValueError, match="no eligible historical Capacity supplier"):
        apply_scenario(base, config, generated_at=NOW)
    assert canonical_business_payload(base.rows_by_table) == before


def test_default_capacity_on_full_real_demo_baseline() -> None:
    base = generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.DEMO,
            seed=20260824,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=NOW,
        )
    )
    config = _config()
    window_start, window_end = default_demo_window(
        config.scenario_type,
        date(2026, 1, 1),
        GenerationProfile.DEMO,
    )
    config = replace(config, window_start=window_start, window_end=window_end)
    before_hash = canonical_content_hash(base.rows_by_table)
    before_count = base.row_count_total
    result = apply_scenario(base, config, generated_at=NOW)
    assert result.ground_truth.target_entity_ids == _targets(base, config)
    selected = set(result.ground_truth.target_entity_ids)
    touched_wo = {
        op.work_order_id for op in _rows(base, Operation) if op.work_center_id in selected
    }
    touched_so = {
        wo.sales_order_id for wo in _rows(base, WorkOrder) if wo.work_order_id in touched_wo
    }
    n = sum(
        so.sales_order_id in touched_so and window_start <= so.order_at < window_end
        for so in _rows(base, SalesOrder)
    )
    assert n > 0
    assert len(_rows(result.dataset, SalesOrder)) == 12000 + math.ceil(Fraction(n, 2))
    assert any(
        link.relationship == "adds_operation_queue_delay"
        for link in result.ground_truth.causal_chain
    )
    assert canonical_content_hash(base.rows_by_table) == before_hash
    assert base.row_count_total == before_count
