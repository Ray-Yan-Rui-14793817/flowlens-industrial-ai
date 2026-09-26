"""In-memory Capacity Surge under the frozen F8-R1, R2, and R3 contracts."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import ROUND_CEILING, Decimal
from typing import cast

from flowlens.data import Base
from flowlens.data.generation import GeneratedDataset
from flowlens.data.models import (
    Delivery,
    MaterialRequirement,
    Operation,
    PurchaseOrder,
    QualityInspection,
    Rework,
    SalesOrder,
    WorkCenter,
    WorkOrder,
)
from flowlens.data.scenarios._deterministic import ceil_duration, rank_candidates
from flowlens.data.scenarios.config import CapacitySurgeConfig
from flowlens.data.scenarios.transformer import (
    BusinessCausalLink,
    BusinessScenarioEffects,
    ScenarioIdentity,
    ScenarioPreconditionUnavailable,
    _clone_row,
)


def _group[T](rows: Iterable[T], key: Callable[[T], str]) -> dict[str, list[T]]:
    grouped: dict[str, list[T]] = defaultdict(list)
    for row in rows:
        grouped[key(row)].append(row)
    return grouped


def _entity(row: Base) -> tuple[str, str]:
    return row.__tablename__, str(getattr(row, row.__mapper__.primary_key[0].name))


def _timestamp(value: datetime | None) -> datetime:
    if value is None or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Capacity requires complete aware actual timing/completion anchors")
    return value


@dataclass(frozen=True)
class _Thread:
    order: SalesOrder
    work_orders: tuple[WorkOrder, ...]
    operations: tuple[Operation, ...]
    requirements: tuple[MaterialRequirement, ...]
    inspections: tuple[QualityInspection, ...]
    reworks: tuple[Rework, ...]
    deliveries: tuple[Delivery, ...]

    def complete(self) -> bool:
        return bool(
            self.work_orders
            and self.inspections
            and self.deliveries
            and {row.work_order_id for row in self.operations}
            == {row.work_order_id for row in self.work_orders}
        )

    def validate(self) -> None:
        if not self.complete():
            raise ValueError("incomplete reusable Capacity source topology")
        operations = {row.operation_id: row for row in self.operations}
        inspections = {row.inspection_id: row for row in self.inspections}
        for inspection in self.inspections:
            if inspection.operation_id is not None:
                parent = operations.get(inspection.operation_id)
                if parent is None or parent.work_order_id != inspection.work_order_id:
                    raise ValueError("inconsistent Capacity inspection parent")
        for rework in self.reworks:
            rework_inspection = inspections.get(rework.inspection_id)
            if rework_inspection is None or rework_inspection.work_order_id != rework.work_order_id:
                raise ValueError("inconsistent Capacity Rework inspection parent")
        for work_order in self.work_orders:
            _timestamp(work_order.actual_start_at)
            _timestamp(work_order.actual_end_at)
        for operation in self.operations:
            if _timestamp(operation.actual_end_at) < _timestamp(operation.actual_start_at):
                raise ValueError("invalid Capacity Operation actual timing")


def _threads(rows: dict[str, list[Base]]) -> list[_Thread]:
    work_orders = _group(
        cast(list[WorkOrder], rows["fact_work_order"]), lambda row: row.sales_order_id
    )
    operations = _group(
        cast(list[Operation], rows["fact_operation"]), lambda row: row.work_order_id
    )
    requirements = _group(
        cast(list[MaterialRequirement], rows["fact_material_requirement"]),
        lambda row: row.work_order_id,
    )
    inspections = _group(
        cast(list[QualityInspection], rows["fact_quality_inspection"]),
        lambda row: row.work_order_id,
    )
    reworks = _group(cast(list[Rework], rows["fact_rework"]), lambda row: row.work_order_id)
    deliveries = _group(cast(list[Delivery], rows["fact_delivery"]), lambda row: row.sales_order_id)
    return [
        _Thread(
            order,
            tuple(work_orders[order.sales_order_id]),
            tuple(
                op
                for wo in work_orders[order.sales_order_id]
                for op in operations[wo.work_order_id]
            ),
            tuple(
                mr
                for wo in work_orders[order.sales_order_id]
                for mr in requirements[wo.work_order_id]
            ),
            tuple(
                qi
                for wo in work_orders[order.sales_order_id]
                for qi in inspections[wo.work_order_id]
            ),
            tuple(
                rw for wo in work_orders[order.sales_order_id] for rw in reworks[wo.work_order_id]
            ),
            tuple(deliveries[order.sales_order_id]),
        )
        for order in cast(list[SalesOrder], rows["fact_sales_order"])
    ]


def _created_id(identity: ScenarioIdentity, prefix: str, purpose: str, **fields: str | int) -> str:
    payload = {"purpose": purpose, "scenario_namespace": identity.namespace, **fields}
    encoded = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return prefix + digest[: 37 if prefix in {"so_", "wo_", "po_"} else 45]


@dataclass
class _Effects:
    rows: dict[str, list[Base]]
    identity: ScenarioIdentity
    used_ids: set[str]
    affected: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    links: set[BusinessCausalLink] = field(default_factory=set)

    def affect(self, row: Base) -> None:
        table, entity_id = _entity(row)
        self.affected[table].add(entity_id)

    def link(self, source: Base, target: Base, relationship: str) -> None:
        source_table, source_id = _entity(source)
        target_table, target_id = _entity(target)
        self.links.add(
            BusinessCausalLink(source_table, source_id, target_table, target_id, relationship)
        )

    def add[T: Base](self, row: T) -> T:
        table, entity_id = _entity(row)
        if entity_id in self.used_ids:
            raise ValueError("scenario-created Capacity ID collision")
        self.used_ids.add(entity_id)
        self.rows[table].append(row)
        self.affect(row)
        return row

    def create[T: Base](self, source: T, entity_id: str, **rewrites: str | None) -> T:
        # Reuse the foundation's independent-row primitive for each new identity.
        row = cast(T, _clone_row(source, self.identity.scenario_dataset_version_id))
        setattr(row, row.__mapper__.primary_key[0].name, entity_id)
        for key, value in rewrites.items():
            setattr(row, key, value)
        return self.add(row)


def _create_thread(
    source: _Thread,
    ordinal: int,
    effects: _Effects,
    centers: dict[str, WorkCenter],
    historical_suppliers: dict[str, dict[str, datetime]],
) -> _Thread:
    identity = effects.identity
    order = effects.create(
        source.order,
        _created_id(
            identity,
            "so_",
            "capacity-sales-order",
            source_sales_order_id=source.order.sales_order_id,
            arrival_ordinal=ordinal,
        ),
    )
    for center_id in sorted({op.work_center_id for op in source.operations} & centers.keys()):
        effects.link(centers[center_id], order, "receives_added_sales_order_arrival")
    work_orders: dict[str, WorkOrder] = {}
    for old in source.work_orders:
        new = effects.create(
            old,
            _created_id(
                identity,
                "wo_",
                "capacity-work-order",
                scenario_sales_order_id=order.sales_order_id,
                source_work_order_id=old.work_order_id,
            ),
            sales_order_id=order.sales_order_id,
        )
        work_orders[old.work_order_id] = new
        effects.link(order, new, "creates_work_order")
    operations: dict[str, Operation] = {}
    for old_op in source.operations:
        parent = work_orders[old_op.work_order_id]
        op = effects.create(
            old_op,
            _created_id(
                identity,
                "op_",
                "capacity-operation",
                scenario_work_order_id=parent.work_order_id,
                source_operation_id=old_op.operation_id,
            ),
            work_order_id=parent.work_order_id,
        )
        operations[old_op.operation_id] = op
        effects.link(parent, op, "creates_operation")
    requirements: list[MaterialRequirement] = []
    for old_mr in source.requirements:
        parent = work_orders[old_mr.work_order_id]
        mr = effects.create(
            old_mr,
            _created_id(
                identity,
                "mr_",
                "capacity-material-requirement",
                scenario_work_order_id=parent.work_order_id,
                source_material_requirement_id=old_mr.material_requirement_id,
            ),
            work_order_id=parent.work_order_id,
        )
        requirements.append(mr)
        effects.link(parent, mr, "creates_material_requirement")
        if mr.need_by_at <= order.order_at:
            raise ValueError("Capacity need_by_at must be later than decision time")
        suppliers = rank_candidates(
            (
                supplier_id
                for supplier_id, first_ordered_at in historical_suppliers.get(
                    mr.material_id, {}
                ).items()
                if first_ordered_at <= order.order_at
            ),
            identity,
            "capacity-supplemental-supplier",
            lambda supplier_id: supplier_id,
        )
        if not suppliers:
            raise ScenarioPreconditionUnavailable("no eligible historical Capacity supplier")
        supplier_id = suppliers[0]
        po = effects.add(
            PurchaseOrder(
                purchase_order_id=_created_id(
                    identity,
                    "po_",
                    "capacity-supplemental-purchase-order",
                    scenario_material_requirement_id=mr.material_requirement_id,
                    supplier_id=supplier_id,
                ),
                dataset_version_id=identity.scenario_dataset_version_id,
                supplier_id=supplier_id,
                material_id=mr.material_id,
                ordered_at=order.order_at,
                promised_receipt_at=mr.need_by_at,
                actual_receipt_at=mr.need_by_at,
                ordered_quantity=mr.required_quantity,
                received_quantity=mr.required_quantity,
                status="RECEIVED",
            )
        )
        effects.link(mr, po, "creates_supplemental_procurement")
    inspections: dict[str, QualityInspection] = {}
    for old_qi in source.inspections:
        parent = work_orders[old_qi.work_order_id]
        inspection_op = operations[old_qi.operation_id] if old_qi.operation_id else None
        qi = effects.create(
            old_qi,
            _created_id(
                identity,
                "qi_",
                "capacity-quality-inspection",
                scenario_work_order_id=parent.work_order_id,
                source_inspection_id=old_qi.inspection_id,
            ),
            work_order_id=parent.work_order_id,
            operation_id=inspection_op.operation_id if inspection_op else None,
        )
        inspections[old_qi.inspection_id] = qi
        effects.link(
            inspection_op if inspection_op is not None else parent, qi, "creates_quality_inspection"
        )
    reworks: list[Rework] = []
    for old_rw in source.reworks:
        qi = inspections[old_rw.inspection_id]
        rw = effects.create(
            old_rw,
            _created_id(
                identity,
                "rw_",
                "capacity-rework",
                scenario_inspection_id=qi.inspection_id,
                source_rework_id=old_rw.rework_id,
            ),
            inspection_id=qi.inspection_id,
            work_order_id=work_orders[old_rw.work_order_id].work_order_id,
        )
        reworks.append(rw)
        effects.link(qi, rw, "creates_rework")
    deliveries: list[Delivery] = []
    for old_dl in source.deliveries:
        dl = effects.create(
            old_dl,
            _created_id(
                identity,
                "dl_",
                "capacity-delivery",
                scenario_sales_order_id=order.sales_order_id,
                source_delivery_id=old_dl.delivery_id,
            ),
            sales_order_id=order.sales_order_id,
        )
        deliveries.append(dl)
        effects.link(order, dl, "creates_delivery")
    return _Thread(
        order,
        tuple(work_orders.values()),
        tuple(operations.values()),
        tuple(requirements),
        tuple(inspections.values()),
        tuple(reworks),
        tuple(deliveries),
    )


def _shift_operations(
    operations: list[Operation],
    config: CapacitySurgeConfig,
    centers: dict[str, WorkCenter],
    effects: _Effects,
) -> set[str]:
    accumulated = timedelta(0)
    direct_sources: list[Operation] = []
    changed: set[str] = set()
    for op in sorted(operations, key=lambda row: (row.sequence_number, row.operation_id)):
        start, end = _timestamp(op.actual_start_at), _timestamp(op.actual_end_at)
        delay = timedelta(0)
        if op.work_center_id in centers and config.window_start <= start < config.window_end:
            duration = _timestamp(op.planned_end_at) - _timestamp(op.planned_start_at)
            if duration <= timedelta(0):
                raise ValueError("Capacity planned Operation duration must be positive")
            delay = ceil_duration(duration, config.queue_time_multiplier - 1)
            if delay < timedelta(0):
                raise ValueError("negative Capacity queue delay")
        accumulated += delay
        if accumulated:
            op.actual_start_at, op.actual_end_at = start + accumulated, end + accumulated
            changed.add(op.operation_id)
            effects.affect(op)
            for upstream in direct_sources:
                effects.link(upstream, op, "shifts_downstream_operation")
        if delay:
            effects.link(centers[op.work_center_id], op, "adds_operation_queue_delay")
            direct_sources.append(op)
    return changed


def _propagate(
    thread: _Thread,
    config: CapacitySurgeConfig,
    centers: dict[str, WorkCenter],
    effects: _Effects,
) -> None:
    operations = _group(thread.operations, lambda row: row.work_order_id)
    inspections = _group(thread.inspections, lambda row: row.work_order_id)
    reworks = _group(thread.reworks, lambda row: row.work_order_id)
    pre_completion = max(_timestamp(wo.actual_end_at) for wo in thread.work_orders)
    shifted_work_orders: list[WorkOrder] = []
    for wo in thread.work_orders:
        pre_start, pre_end = _timestamp(wo.actual_start_at), _timestamp(wo.actual_end_at)
        ops = operations[wo.work_order_id]
        changed = _shift_operations(ops, config, centers, effects)
        if not changed:
            # R3: no normalization-only mutation for neutral/zero-effect input.
            continue
        wo.actual_start_at = min(_timestamp(op.actual_start_at) for op in ops)
        wo.actual_end_at = max(_timestamp(op.actual_end_at) for op in ops)
        if (wo.actual_start_at, wo.actual_end_at) != (pre_start, pre_end):
            effects.affect(wo)
        delta = wo.actual_end_at - pre_end
        if not delta:
            continue
        candidates = [
            op for op in ops if op.operation_id in changed and op.actual_end_at == wo.actual_end_at
        ]
        if not candidates:
            raise ValueError("changed Capacity completion has no binding Operation")
        binding = max(candidates, key=lambda op: (op.sequence_number, op.operation_id))
        effects.link(binding, wo, "shifts_work_order_completion")
        shifted_work_orders.append(wo)
        for qi in inspections[wo.work_order_id]:
            qi.inspection_at += delta
            effects.affect(qi)
            effects.link(wo, qi, "shifts_inspection_time")
        for rw in reworks[wo.work_order_id]:
            rw.rework_start_at += delta
            rw.rework_end_at += delta
            effects.affect(rw)
            effects.link(wo, rw, "shifts_rework_window")
    order_delta = max(_timestamp(wo.actual_end_at) for wo in thread.work_orders) - pre_completion
    if order_delta < timedelta(0):
        raise ValueError("negative Capacity order completion delta")
    if order_delta:
        for delivery in thread.deliveries:
            delivery.delivery_at += order_delta
            effects.affect(delivery)
            for wo in shifted_work_orders:
                effects.link(wo, delivery, "shifts_delivery_time")


def _validate_hgt(effects: _Effects, centers: dict[str, WorkCenter]) -> None:
    existing = {
        _entity(row)
        for rows in effects.rows.values()
        for row in rows
        if len(row.__mapper__.primary_key) == 1
    }
    affected = {(table, entity_id) for table, ids in effects.affected.items() for entity_id in ids}
    allowed = affected | {("dim_work_center", center_id) for center_id in centers}
    if not affected <= existing:
        raise ValueError("Capacity affected map references a missing entity")
    for link in effects.links:
        endpoints = {
            (link.source_table, link.source_entity_id),
            (link.target_table, link.target_entity_id),
        }
        if not endpoints <= allowed or not endpoints <= existing:
            raise ValueError("Capacity HGT endpoint missing from business rows/affected graph")


def apply_capacity_surge(
    baseline: GeneratedDataset,
    identity: ScenarioIdentity,
    config: CapacitySurgeConfig,
    rows_by_table: dict[str, list[Base]],
) -> BusinessScenarioEffects:
    """Transform only detached scenario rows and return compatibility effects."""

    threads = [
        thread
        for thread in _threads(rows_by_table)
        if config.window_start <= thread.order.order_at < config.window_end
    ]
    center_rows = {
        row.work_center_id: row for row in cast(list[WorkCenter], rows_by_table["dim_work_center"])
    }
    candidate_ids = {op.work_center_id for thread in threads for op in thread.operations}
    if not candidate_ids <= center_rows.keys():
        raise ValueError("Capacity Operation references a missing WorkCenter")
    selected = rank_candidates(
        (center_rows[key] for key in candidate_ids),
        identity,
        "capacity-work-center",
        lambda row: row.work_center_id,
    )[: config.affected_work_center_count]
    if len(selected) != config.affected_work_center_count:
        raise ScenarioPreconditionUnavailable("insufficient candidate Capacity WorkCenters")
    centers = {row.work_center_id: row for row in selected}
    qualifying = [
        thread
        for thread in threads
        if thread.complete() and any(op.work_center_id in centers for op in thread.operations)
    ]
    if not qualifying:
        raise ScenarioPreconditionUnavailable(
            "Capacity N == 0: no complete reusable selected order threads"
        )
    for thread in qualifying:
        thread.validate()
    templates = rank_candidates(
        qualifying,
        identity,
        "capacity-arrival-template",
        lambda thread: thread.order.sales_order_id,
    )
    added_count = int(
        (Decimal(len(templates)) * (config.arrival_volume_multiplier - 1)).to_integral_value(
            rounding=ROUND_CEILING
        )
    )
    if added_count < 0:
        raise ValueError("negative Capacity added arrival count")
    used_ids: set[str] = set()
    for rows in rows_by_table.values():
        for row in rows:
            if len(row.__mapper__.primary_key) == 1:
                entity_id = _entity(row)[1]
                if entity_id in used_ids:
                    raise ValueError("duplicate Capacity input entity identity")
                used_ids.add(entity_id)
    effects = _Effects(rows_by_table, identity, used_ids)
    historical_suppliers: dict[str, dict[str, datetime]] = defaultdict(dict)
    for po in cast(tuple[PurchaseOrder, ...], baseline.rows_for("fact_purchase_order")):
        suppliers = historical_suppliers[po.material_id]
        suppliers[po.supplier_id] = min(suppliers.get(po.supplier_id, po.ordered_at), po.ordered_at)
    # Materialize every source copy before any baseline-derived thread is shifted.
    added = [
        _create_thread(templates[i % len(templates)], i, effects, centers, historical_suppliers)
        for i in range(added_count)
    ]
    for thread in [*templates, *added]:
        _propagate(thread, config, centers, effects)
    _validate_hgt(effects, centers)
    return BusinessScenarioEffects(
        target_entity_ids=tuple(centers),
        affected_entities_by_table={
            table: tuple(sorted(ids)) for table, ids in effects.affected.items() if ids
        },
        causal_chain=tuple(effects.links),
    )
