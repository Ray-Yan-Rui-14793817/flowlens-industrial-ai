"""The sole C02 PostgreSQL reader: bounded, repeatable-read, and read-only."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, cast

from sqlalchemy import case, select, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.selectable import FromClause

from flowlens.data.models import (
    Customer,
    DatasetVersion,
    Delivery,
    InventorySnapshot,
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
from flowlens.decision.contracts import DecisionRun, StateSnapshot
from flowlens.decision.primitives import ScalarValue
from flowlens.decision.snapshot import build_state_snapshot, source_unknowns
from flowlens.decision.temporal import (
    SOURCE_FIELDS,
    C02BuildError,
    ProjectedSourceField,
    project_record,
    validate_as_of,
)

_TABLES: dict[str, FromClause] = {
    "dim_product": Product.__table__,
    "dim_customer": Customer.__table__,
    "dim_work_center": WorkCenter.__table__,
    "dim_material": Material.__table__,
    "dim_supplier": Supplier.__table__,
    "bridge_product_material": ProductMaterial.__table__,
    "fact_sales_order": SalesOrder.__table__,
    "fact_work_order": WorkOrder.__table__,
    "fact_operation": Operation.__table__,
    "fact_material_requirement": MaterialRequirement.__table__,
    "fact_purchase_order": PurchaseOrder.__table__,
    "fact_inventory_snapshot": InventorySnapshot.__table__,
    "fact_quality_inspection": QualityInspection.__table__,
    "fact_rework": Rework.__table__,
    "fact_delivery": Delivery.__table__,
}

_PRIMARY_KEY: dict[str, str] = {
    "dim_product": "product_id",
    "dim_customer": "customer_id",
    "dim_work_center": "work_center_id",
    "dim_material": "material_id",
    "dim_supplier": "supplier_id",
    "fact_sales_order": "sales_order_id",
    "fact_work_order": "work_order_id",
    "fact_operation": "operation_id",
    "fact_material_requirement": "material_requirement_id",
    "fact_purchase_order": "purchase_order_id",
    "fact_inventory_snapshot": "inventory_snapshot_id",
    "fact_quality_inspection": "inspection_id",
    "fact_rework": "rework_id",
    "fact_delivery": "delivery_id",
}


def _masked_column(
    entity: str, table: FromClause, field: str, as_of_time: datetime
) -> ColumnElement[Any]:
    gate: str | None = None
    if entity in ("fact_work_order", "fact_operation"):
        if field in ("actual_start_at", "actual_end_at"):
            gate = field
        elif entity == "fact_work_order" and field == "completed_quantity":
            gate = "actual_end_at"
    elif entity == "fact_purchase_order" and field in (
        "actual_receipt_at",
        "received_quantity",
    ):
        gate = "actual_receipt_at"
    elif entity == "fact_rework" and field == "rework_end_at":
        gate = "rework_end_at"
    if gate is not None:
        return case((table.c[gate] <= as_of_time, table.c[field]), else_=None).label(field)
    return table.c[field]


def _fetch(
    connection: Connection,
    entity: str,
    run: DecisionRun,
    *conditions: ColumnElement[bool],
) -> list[dict[str, ScalarValue]]:
    """Select the exact runtime field whitelist plus ownership metadata."""
    table = _TABLES[entity]
    columns: list[ColumnElement[Any]] = [table.c.dataset_version_id]
    columns.extend(
        _masked_column(entity, table, field, run.as_of_time) for field in SOURCE_FIELDS[entity]
    )
    statement = select(*columns).where(*conditions)
    result: list[dict[str, ScalarValue]] = []
    for row in connection.execute(statement).mappings():
        if row["dataset_version_id"] != run.dataset_version:
            raise C02BuildError("DATASET_OWNERSHIP_MISMATCH", "BLOCKED_CONTRACT")
        result.append({field: cast(ScalarValue, row[field]) for field in SOURCE_FIELDS[entity]})
    key = _PRIMARY_KEY.get(entity)
    if key is None:
        result.sort(key=lambda item: (str(item["product_id"]), str(item["material_id"])))
    else:
        result.sort(key=lambda item: str(item[key]))
    return result


def _ids(rows: list[dict[str, ScalarValue]], field: str) -> tuple[str, ...]:
    return tuple(sorted({value for row in rows if isinstance((value := row[field]), str)}))


def _required_master(
    connection: Connection,
    entity: str,
    ids: tuple[str, ...],
    run: DecisionRun,
) -> list[dict[str, ScalarValue]]:
    if not ids:
        return []
    key = _PRIMARY_KEY[entity]
    rows = _fetch(connection, entity, run, _TABLES[entity].c[key].in_(ids))
    if set(_ids(rows, key)) != set(ids):
        raise C02BuildError("DIRECT_REFERENCE_MISSING", "BLOCKED_CONTRACT")
    return rows


def _record_id(entity: str, row: dict[str, ScalarValue], dataset_version: str) -> str:
    if entity == "bridge_product_material":
        return f"{dataset_version}|{row['product_id']}|{row['material_id']}"
    value = row[_PRIMARY_KEY[entity]]
    if not isinstance(value, str):
        raise C02BuildError("DIRECT_REFERENCE_MISSING", "BLOCKED_CONTRACT")
    return value


def build_decision_snapshot(engine: Engine, run: DecisionRun) -> StateSnapshot:
    """Read one target order's authorized decision-time world in one transaction."""
    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            isolation = connection.execute(text("SHOW transaction_isolation")).scalar_one()
            read_only = connection.execute(text("SHOW transaction_read_only")).scalar_one()
            if isolation != "repeatable read" or read_only != "on":
                raise C02BuildError("READ_ONLY_VIOLATION", "BLOCKED_CONTRACT")
            revisions = (
                connection.execute(text("SELECT version_num FROM alembic_version")).scalars().all()
            )
            if revisions != ["0002_industrial_data_foundation"]:
                raise C02BuildError("SCHEMA_REVISION_MISMATCH", "BLOCKED_CONTEXT")
            dataset = DatasetVersion.__table__
            versions = (
                connection.execute(
                    select(
                        dataset.c.dataset_version_id,
                        dataset.c.content_hash,
                        dataset.c.period_start,
                        dataset.c.period_end,
                    )
                )
                .mappings()
                .all()
            )
            if not versions:
                raise C02BuildError("NO_ACTIVE_DATASET", "BLOCKED_CONTEXT")
            if len(versions) != 1:
                raise C02BuildError("MULTIPLE_ACTIVE_DATASETS", "BLOCKED_CONTEXT")
            version = versions[0]
            if (
                run.dataset_version != version["dataset_version_id"]
                or run.dataset_hash != version["content_hash"]
            ):
                raise C02BuildError("DATASET_BINDING_MISMATCH", "BLOCKED_CONTEXT")
            period_start = cast(date, version["period_start"])
            period_end = cast(date, version["period_end"])
            validate_as_of(run.as_of_time, period_start, period_end)

            order_rows = _fetch(
                connection,
                "fact_sales_order",
                run,
                _TABLES["fact_sales_order"].c.sales_order_id == run.order_id,
            )
            if not order_rows:
                raise C02BuildError("TARGET_ORDER_NOT_FOUND", "BLOCKED_CONTEXT")
            order = order_rows[0]
            order_at = order["order_at"]
            if not isinstance(order_at, datetime):
                raise C02BuildError("TEMPORAL_ADMISSION_VIOLATION", "BLOCKED_TEMPORAL")
            if order_at > run.as_of_time:
                raise C02BuildError("TARGET_ORDER_NOT_AVAILABLE", "BLOCKED_TEMPORAL")
            customer_ids = _ids(order_rows, "customer_id")
            product_ids = _ids(order_rows, "product_id")
            work_orders = _fetch(
                connection,
                "fact_work_order",
                run,
                _TABLES["fact_work_order"].c.sales_order_id == run.order_id,
            )
            work_ids = _ids(work_orders, "work_order_id")
            operations = (
                _fetch(
                    connection,
                    "fact_operation",
                    run,
                    _TABLES["fact_operation"].c.work_order_id.in_(work_ids),
                )
                if work_ids
                else []
            )
            requirements = (
                _fetch(
                    connection,
                    "fact_material_requirement",
                    run,
                    _TABLES["fact_material_requirement"].c.work_order_id.in_(work_ids),
                )
                if work_ids
                else []
            )
            inspections = (
                _fetch(
                    connection,
                    "fact_quality_inspection",
                    run,
                    _TABLES["fact_quality_inspection"].c.work_order_id.in_(work_ids),
                    _TABLES["fact_quality_inspection"].c.inspection_at <= run.as_of_time,
                )
                if work_ids
                else []
            )
            reworks = (
                _fetch(
                    connection,
                    "fact_rework",
                    run,
                    _TABLES["fact_rework"].c.work_order_id.in_(work_ids),
                    _TABLES["fact_rework"].c.rework_start_at <= run.as_of_time,
                )
                if work_ids
                else []
            )
            deliveries = _fetch(
                connection,
                "fact_delivery",
                run,
                _TABLES["fact_delivery"].c.sales_order_id == run.order_id,
                _TABLES["fact_delivery"].c.delivery_at <= run.as_of_time,
            )
            bom = _fetch(
                connection,
                "bridge_product_material",
                run,
                _TABLES["bridge_product_material"].c.product_id.in_(product_ids),
            )
            required_material_ids = _ids(requirements, "material_id")
            material_ids = tuple(sorted(set(required_material_ids) | set(_ids(bom, "material_id"))))
            purchase_orders = (
                _fetch(
                    connection,
                    "fact_purchase_order",
                    run,
                    _TABLES["fact_purchase_order"].c.material_id.in_(required_material_ids),
                    _TABLES["fact_purchase_order"].c.ordered_at <= run.as_of_time,
                )
                if required_material_ids
                else []
            )
            inventory = (
                _fetch(
                    connection,
                    "fact_inventory_snapshot",
                    run,
                    _TABLES["fact_inventory_snapshot"].c.material_id.in_(required_material_ids),
                    _TABLES["fact_inventory_snapshot"].c.snapshot_at <= run.as_of_time,
                )
                if required_material_ids
                else []
            )
            rows: dict[str, list[dict[str, ScalarValue]]] = {
                "fact_sales_order": order_rows,
                "dim_customer": _required_master(connection, "dim_customer", customer_ids, run),
                "dim_product": _required_master(connection, "dim_product", product_ids, run),
                "bridge_product_material": bom,
                "fact_work_order": work_orders,
                "fact_operation": operations,
                "dim_work_center": _required_master(
                    connection, "dim_work_center", _ids(operations, "work_center_id"), run
                ),
                "fact_material_requirement": requirements,
                "dim_material": _required_master(connection, "dim_material", material_ids, run),
                "fact_quality_inspection": inspections,
                "fact_rework": reworks,
                "fact_delivery": deliveries,
                "fact_purchase_order": purchase_orders,
                "dim_supplier": _required_master(
                    connection, "dim_supplier", _ids(purchase_orders, "supplier_id"), run
                ),
                "fact_inventory_snapshot": inventory,
            }
            projected: list[ProjectedSourceField] = []
            for entity in SOURCE_FIELDS:
                for row in rows[entity]:
                    projected.extend(
                        project_record(
                            entity,
                            _record_id(entity, row, run.dataset_version),
                            row,
                            as_of_time=run.as_of_time,
                            period_start=period_start,
                            target_order_at=order_at,
                        )
                    )
            unknowns = source_unknowns(
                len(work_orders),
                len(requirements),
                required_material_ids,
                _ids(inventory, "material_id"),
            )
            return build_state_snapshot(run, projected, unknowns)
