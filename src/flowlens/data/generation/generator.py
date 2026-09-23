"""Deterministic, persistence-neutral Week 2 baseline dataset generator."""

from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from types import MappingProxyType
from typing import Final
from zoneinfo import ZoneInfo

from flowlens.data import Base
from flowlens.data.generation.canonical import (
    CANONICAL_TABLE_ORDER,
    canonical_content_hash,
    canonicalize_rows,
)
from flowlens.data.generation.config import GenerationConfig
from flowlens.data.generation.ids import DeterministicIdFactory
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

BUSINESS_TIMEZONE: Final = ZoneInfo("Asia/Shanghai")


@dataclass(frozen=True, slots=True)
class _BaselineTuning:
    """Synthetic technical parameters; these are not empirical enterprise rates."""

    bom_materials_min: int = 3
    bom_materials_max: int = 6
    operation_count_min: int = 3
    operation_count_max: int = 5
    inspection_failure_probability: float = 0.08
    rework_probability: float = 0.65
    partial_receipt_probability: float = 0.12
    late_receipt_probability: float = 0.10
    split_delivery_probability: float = 0.24
    partial_delivery_probability: float = 0.10


_TUNING: Final = _BaselineTuning()
_PRODUCT_FAMILIES: Final = (
    "GROUNDING_SWITCH",
    "ISOLATION_SWITCH",
    "ELECTRIC_CHASSIS",
)
_COMPLEXITIES: Final = ("LOW", "MEDIUM", "HIGH")
_MATERIAL_GROUPS: Final = ("METAL", "INSULATION", "ELECTRICAL", "FASTENER", "PACKAGING")
_CRITICALITIES: Final = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
_UNITS: Final = ("EA", "KG", "M", "SET")
_REGIONS: Final = ("EAST", "NORTH", "SOUTH", "CENTRAL", "WEST")
_SUPPLIER_TIERS: Final = ("TIER_1", "TIER_2", "TIER_3")
_CUSTOMER_SEGMENTS: Final = ("UTILITY", "INDUSTRIAL", "INFRASTRUCTURE")
_PROCESS_TYPES: Final = ("MACHINING", "WELDING", "ASSEMBLY", "INSPECTION", "PACKING")
_PRIORITIES: Final = ("NORMAL", "NORMAL", "NORMAL", "HIGH", "EXPEDITE")
_DEFECT_CATEGORIES: Final = ("DIMENSIONAL", "SURFACE", "ASSEMBLY", "ELECTRICAL")
_SEVERITIES: Final = ("LOW", "MEDIUM", "HIGH")
_REWORK_REASONS: Final = (
    "SYNTHETIC_DIMENSIONAL_ADJUSTMENT",
    "SYNTHETIC_ASSEMBLY_CORRECTION",
    "SYNTHETIC_SURFACE_REFINISH",
)
_FOUR_PLACES: Final = Decimal("0.0001")
_TWO_PLACES: Final = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class GeneratedDataset:
    """One detached, canonically ordered, in-memory manufacturing dataset."""

    dataset_version: DatasetVersion
    rows_by_table: Mapping[str, tuple[Base, ...]]

    @property
    def row_count_total(self) -> int:
        return self.dataset_version.row_count_total

    @property
    def content_hash(self) -> str:
        return self.dataset_version.content_hash

    def rows_for(self, table_name: str) -> tuple[Base, ...]:
        return self.rows_by_table[table_name]

    def iter_business_rows(self) -> Iterator[tuple[str, Base]]:
        for table_name in CANONICAL_TABLE_ORDER:
            for row in self.rows_by_table[table_name]:
                yield table_name, row


def _decimal(value: int, scale: Decimal = _FOUR_PLACES) -> Decimal:
    return Decimal(value).quantize(scale)


def _business_datetime(value: date, hour: int = 8, minute: int = 0) -> datetime:
    return datetime.combine(value, time(hour=hour, minute=minute), BUSINESS_TIMEZONE)


def _random_business_datetime(
    rng: random.Random,
    period_start: date,
    latest_date: date,
) -> datetime:
    day_offset = rng.randint(0, max(0, (latest_date - period_start).days))
    return _business_datetime(
        period_start + timedelta(days=day_offset),
        hour=rng.randint(8, 16),
        minute=rng.choice((0, 15, 30, 45)),
    )


def _generate_dimensions(
    config: GenerationConfig,
    rng: random.Random,
    ids: DeterministicIdFactory,
) -> tuple[list[Product], list[Material], list[Supplier], list[Customer], list[WorkCenter]]:
    definition = config.definition
    dataset_id = ids.dataset_version_id
    products = [
        Product(
            product_id=ids.make("prd", index, 32),
            dataset_version_id=dataset_id,
            product_code=f"SYN-PROD-{index:04d}",
            product_family=_PRODUCT_FAMILIES[(index - 1) % len(_PRODUCT_FAMILIES)],
            model_name=f"Synthetic Product Model {index:04d}",
            complexity_class=_COMPLEXITIES[(index - 1) % len(_COMPLEXITIES)],
            standard_cycle_hours=_decimal(rng.randrange(1600, 8001, 25), _TWO_PLACES) / 100,
            active_from=config.period_start,
            active_to=None,
        )
        for index in range(1, definition.products + 1)
    ]
    materials = [
        Material(
            material_id=ids.make("mat", index, 32),
            dataset_version_id=dataset_id,
            material_code=f"SYN-MAT-{index:04d}",
            material_group=_MATERIAL_GROUPS[(index - 1) % len(_MATERIAL_GROUPS)],
            criticality=_CRITICALITIES[(index - 1) % len(_CRITICALITIES)],
            standard_lead_time_days=rng.randint(3, 35),
            unit_of_measure=_UNITS[(index - 1) % len(_UNITS)],
        )
        for index in range(1, definition.materials + 1)
    ]
    suppliers = [
        Supplier(
            supplier_id=ids.make("sup", index, 32),
            dataset_version_id=dataset_id,
            supplier_code=f"SYN-SUP-{index:04d}",
            supplier_tier=_SUPPLIER_TIERS[(index - 1) % len(_SUPPLIER_TIERS)],
            region=_REGIONS[(index - 1) % len(_REGIONS)],
            active_from=config.period_start,
            active_to=None,
        )
        for index in range(1, definition.suppliers + 1)
    ]
    customers = [
        Customer(
            customer_id=ids.make("cus", index, 32),
            dataset_version_id=dataset_id,
            customer_code=f"SYN-CUS-{index:04d}",
            customer_segment=_CUSTOMER_SEGMENTS[(index - 1) % len(_CUSTOMER_SEGMENTS)],
            region=_REGIONS[(index + 1) % len(_REGIONS)],
            active_from=config.period_start,
            active_to=None,
        )
        for index in range(1, definition.customers + 1)
    ]
    work_centers = [
        WorkCenter(
            work_center_id=ids.make("wc", index, 32),
            dataset_version_id=dataset_id,
            work_center_code=f"SYN-WC-{index:03d}",
            process_type=_PROCESS_TYPES[(index - 1) % len(_PROCESS_TYPES)],
            line_group=f"SYN-LINE-{((index - 1) % 3) + 1:02d}",
            daily_capacity_hours=_decimal(rng.randrange(800, 2401, 25), _TWO_PLACES) / 100,
            active_from=config.period_start,
            active_to=None,
        )
        for index in range(1, definition.work_centers + 1)
    ]
    return products, materials, suppliers, customers, work_centers


def _generate_bom(
    rng: random.Random,
    ids: DeterministicIdFactory,
    products: Sequence[Product],
    materials: Sequence[Material],
) -> list[ProductMaterial]:
    rows: list[ProductMaterial] = []
    material_count = len(materials)
    for product_index, product in enumerate(products):
        count = min(
            material_count,
            rng.randint(_TUNING.bom_materials_min, _TUNING.bom_materials_max),
        )
        required_index = product_index % material_count
        selected = {required_index}
        while len(selected) < count:
            selected.add(rng.randrange(material_count))
        for material_index in sorted(selected):
            material = materials[material_index]
            rows.append(
                ProductMaterial(
                    dataset_version_id=ids.dataset_version_id,
                    product_id=product.product_id,
                    material_id=material.material_id,
                    quantity_per_unit=(Decimal(rng.randint(1, 200)) / Decimal(20)).quantize(
                        _FOUR_PLACES
                    ),
                    is_critical=material.criticality in {"HIGH", "CRITICAL"},
                )
            )
    return rows


def _generate_sales_orders(
    config: GenerationConfig,
    rng: random.Random,
    ids: DeterministicIdFactory,
    products: Sequence[Product],
    customers: Sequence[Customer],
) -> list[SalesOrder]:
    latest_order_date = config.period_end - timedelta(days=40)
    rows: list[SalesOrder] = []
    for index in range(1, config.definition.sales_orders + 1):
        ordered_at = _random_business_datetime(rng, config.period_start, latest_order_date)
        promised_at = ordered_at + timedelta(days=rng.randint(20, 34))
        rows.append(
            SalesOrder(
                sales_order_id=ids.make("so", index, 40),
                dataset_version_id=ids.dataset_version_id,
                customer_id=rng.choice(customers).customer_id,
                product_id=rng.choice(products).product_id,
                order_at=ordered_at,
                promised_delivery_at=promised_at,
                order_quantity=rng.randint(1, 20),
                priority=rng.choice(_PRIORITIES),
                status="IN_PRODUCTION",
            )
        )
    return rows


def _bom_by_product(
    bom: Sequence[ProductMaterial],
) -> dict[str, list[ProductMaterial]]:
    bom_by_product: dict[str, list[ProductMaterial]] = defaultdict(list)
    for row in bom:
        bom_by_product[row.product_id].append(row)
    return dict(bom_by_product)


def _procurement_decision_at(config: GenerationConfig, bucket_index: int) -> datetime:
    """Return the deterministic close time for one seven-day demand bucket."""

    decision_date = config.period_start + timedelta(days=(bucket_index * 7) + 6)
    return _business_datetime(decision_date, 18)


def _generate_purchase_orders(
    config: GenerationConfig,
    ids: DeterministicIdFactory,
    suppliers: Sequence[Supplier],
    materials: Sequence[Material],
    sales_orders: Sequence[SalesOrder],
    bom: Sequence[ProductMaterial],
) -> list[PurchaseOrder]:
    """Generate weekly POs using only demand known by each decision time."""

    bom_by_product = _bom_by_product(bom)
    demand_by_bucket: dict[tuple[int, str], Decimal] = defaultdict(Decimal)
    for order in sorted(sales_orders, key=lambda row: (row.order_at, row.sales_order_id)):
        bucket_index = (order.order_at.date() - config.period_start).days // 7
        for component in bom_by_product[order.product_id]:
            demand_by_bucket[(bucket_index, component.material_id)] += (
                component.quantity_per_unit * order.order_quantity
            )

    material_by_id = {row.material_id: row for row in materials}
    material_ordinal = {row.material_id: index for index, row in enumerate(materials, start=1)}
    candidates = sorted(
        (
            _procurement_decision_at(config, bucket_index),
            material_id,
            bucket_index,
            demand,
        )
        for (bucket_index, material_id), demand in demand_by_bucket.items()
    )
    rows: list[PurchaseOrder] = []
    for index, (ordered_at, material_id, bucket_index, demand) in enumerate(
        candidates, start=1
    ):
        material = material_by_id[material_id]
        stable_material_ordinal = material_ordinal[material_id]
        promised_at = ordered_at + timedelta(days=material.standard_lead_time_days)
        ordered_quantity = (demand * Decimal("1.10")).quantize(_FOUR_PLACES)

        # Procurement outcomes are local deterministic policies. They deliberately do
        # not consume the run RNG after future sales events have been generated.
        policy_value = (
            config.seed + (stable_material_ordinal * 37) + (bucket_index * 101)
        ) % 100
        timing_value = (
            (config.seed // 101) + (stable_material_ordinal * 17) + (bucket_index * 43)
        )
        if policy_value < int(_TUNING.partial_receipt_probability * 100):
            received_quantity = (ordered_quantity * Decimal("0.75")).quantize(_FOUR_PLACES)
            actual_receipt_at: datetime | None = promised_at + timedelta(
                days=timing_value % 4
            )
            status = "PARTIAL"
        elif policy_value < int(
            (_TUNING.partial_receipt_probability + _TUNING.late_receipt_probability) * 100
        ):
            received_quantity = ordered_quantity
            actual_receipt_at = promised_at + timedelta(days=(timing_value % 5) + 1)
            status = "RECEIVED"
        else:
            received_quantity = ordered_quantity
            actual_receipt_at = promised_at - timedelta(days=timing_value % 3)
            status = "RECEIVED"
        rows.append(
            PurchaseOrder(
                purchase_order_id=ids.make("po", index, 40),
                dataset_version_id=ids.dataset_version_id,
                supplier_id=suppliers[
                    (config.seed + stable_material_ordinal + bucket_index) % len(suppliers)
                ].supplier_id,
                material_id=material.material_id,
                ordered_at=ordered_at,
                promised_receipt_at=promised_at,
                actual_receipt_at=actual_receipt_at,
                ordered_quantity=ordered_quantity,
                received_quantity=received_quantity,
                status=status,
            )
        )
    return rows


def _generate_work_orders(
    rng: random.Random,
    ids: DeterministicIdFactory,
    sales_orders: Sequence[SalesOrder],
) -> list[WorkOrder]:
    rows: list[WorkOrder] = []
    for index, order in enumerate(sales_orders, start=1):
        planned_start = order.order_at + timedelta(days=rng.randint(1, 3))
        planned_end = planned_start + timedelta(days=rng.randint(3, 7))
        actual_start = planned_start + timedelta(hours=rng.randint(0, 12))
        actual_end = planned_end + timedelta(hours=rng.randint(-6, 18))
        if actual_end < actual_start:
            actual_end = actual_start + timedelta(hours=1)
        rows.append(
            WorkOrder(
                work_order_id=ids.make("wo", index, 40),
                dataset_version_id=ids.dataset_version_id,
                sales_order_id=order.sales_order_id,
                product_id=order.product_id,
                planned_start_at=planned_start,
                planned_end_at=planned_end,
                actual_start_at=actual_start,
                actual_end_at=actual_end,
                planned_quantity=order.order_quantity,
                completed_quantity=order.order_quantity,
                status="COMPLETED",
            )
        )
    return rows


def _generate_operations(
    rng: random.Random,
    ids: DeterministicIdFactory,
    work_orders: Sequence[WorkOrder],
    work_centers: Sequence[WorkCenter],
) -> tuple[list[Operation], dict[str, list[Operation]]]:
    rows: list[Operation] = []
    by_work_order: dict[str, list[Operation]] = defaultdict(list)
    ordinal = 1
    for work_index, work_order in enumerate(work_orders):
        if work_order.actual_start_at is None or work_order.actual_end_at is None:
            raise AssertionError("baseline work orders must have complete actual windows")
        count = min(
            len(work_centers),
            rng.randint(_TUNING.operation_count_min, _TUNING.operation_count_max),
        )
        planned_span = work_order.planned_end_at - work_order.planned_start_at
        actual_span = work_order.actual_end_at - work_order.actual_start_at
        for sequence in range(1, count + 1):
            planned_start = work_order.planned_start_at + planned_span * ((sequence - 1) / count)
            planned_end = work_order.planned_start_at + planned_span * (sequence / count)
            actual_start = work_order.actual_start_at + actual_span * ((sequence - 1) / count)
            actual_end = work_order.actual_start_at + actual_span * (sequence / count)
            operation = Operation(
                operation_id=ids.make("op", ordinal, 48),
                dataset_version_id=ids.dataset_version_id,
                work_order_id=work_order.work_order_id,
                work_center_id=work_centers[
                    (work_index + sequence - 1) % len(work_centers)
                ].work_center_id,
                sequence_number=sequence,
                planned_start_at=planned_start,
                planned_end_at=planned_end,
                actual_start_at=actual_start,
                actual_end_at=actual_end,
                status="COMPLETED",
            )
            rows.append(operation)
            by_work_order[work_order.work_order_id].append(operation)
            ordinal += 1
    return rows, dict(by_work_order)


def _generate_material_requirements(
    ids: DeterministicIdFactory,
    work_orders: Sequence[WorkOrder],
    bom: Sequence[ProductMaterial],
) -> list[MaterialRequirement]:
    bom_by_product: dict[str, list[ProductMaterial]] = defaultdict(list)
    for row in bom:
        bom_by_product[row.product_id].append(row)
    rows: list[MaterialRequirement] = []
    ordinal = 1
    for work_order in work_orders:
        for component in bom_by_product[work_order.product_id]:
            rows.append(
                MaterialRequirement(
                    material_requirement_id=ids.make("mr", ordinal, 48),
                    dataset_version_id=ids.dataset_version_id,
                    work_order_id=work_order.work_order_id,
                    material_id=component.material_id,
                    required_quantity=(
                        component.quantity_per_unit * work_order.planned_quantity
                    ).quantize(_FOUR_PLACES),
                    need_by_at=work_order.planned_start_at,
                )
            )
            ordinal += 1
    return rows


def _generate_inventory(
    config: GenerationConfig,
    ids: DeterministicIdFactory,
    materials: Sequence[Material],
) -> list[InventorySnapshot]:
    """Generate opening stock from master data, never from future realized demand."""

    snapshot_at = _business_datetime(config.period_start, 7)
    rows: list[InventorySnapshot] = []
    for index, material in enumerate(materials, start=1):
        criticality_units = {
            "LOW": 80,
            "MEDIUM": 120,
            "HIGH": 170,
            "CRITICAL": 230,
        }[material.criticality]
        stable_variation = (
            config.seed + (index * 29) + (material.standard_lead_time_days * 7)
        ) % 61
        on_hand = _decimal(criticality_units + stable_variation)
        reserved = (on_hand * Decimal("0.20")).quantize(_FOUR_PLACES)
        rows.append(
            InventorySnapshot(
                inventory_snapshot_id=ids.make("inv", index, 48),
                dataset_version_id=ids.dataset_version_id,
                material_id=material.material_id,
                snapshot_at=snapshot_at,
                on_hand_quantity=on_hand,
                reserved_quantity=reserved,
            )
        )
    return rows


def _generate_quality(
    rng: random.Random,
    ids: DeterministicIdFactory,
    work_orders: Sequence[WorkOrder],
    operations_by_work_order: Mapping[str, Sequence[Operation]],
) -> list[QualityInspection]:
    rows: list[QualityInspection] = []
    for index, work_order in enumerate(work_orders, start=1):
        if work_order.actual_end_at is None:
            raise AssertionError("baseline work orders must have an actual end before inspection")
        inspected = work_order.completed_quantity
        is_failure = rng.random() < _TUNING.inspection_failure_probability
        failed = rng.randint(1, min(3, inspected)) if is_failure else 0
        final_operation = operations_by_work_order[work_order.work_order_id][-1]
        rows.append(
            QualityInspection(
                inspection_id=ids.make("qi", index, 48),
                dataset_version_id=ids.dataset_version_id,
                work_order_id=work_order.work_order_id,
                operation_id=final_operation.operation_id,
                inspection_at=work_order.actual_end_at + timedelta(hours=2),
                inspection_type="FINAL",
                inspected_quantity=inspected,
                passed_quantity=inspected - failed,
                failed_quantity=failed,
                defect_category=rng.choice(_DEFECT_CATEGORIES) if is_failure else None,
                severity=rng.choice(_SEVERITIES) if is_failure else None,
                result="FAIL" if is_failure else "PASS",
            )
        )
    return rows


def _generate_rework(
    rng: random.Random,
    ids: DeterministicIdFactory,
    inspections: Sequence[QualityInspection],
    operations_by_work_order: Mapping[str, Sequence[Operation]],
) -> list[Rework]:
    rows: list[Rework] = []
    for inspection in inspections:
        if inspection.failed_quantity == 0 or rng.random() >= _TUNING.rework_probability:
            continue
        start = inspection.inspection_at + timedelta(hours=rng.randint(1, 6))
        rows.append(
            Rework(
                rework_id=ids.make("rw", len(rows) + 1, 48),
                dataset_version_id=ids.dataset_version_id,
                inspection_id=inspection.inspection_id,
                work_order_id=inspection.work_order_id,
                work_center_id=operations_by_work_order[inspection.work_order_id][-1].work_center_id,
                rework_start_at=start,
                rework_end_at=start + timedelta(hours=rng.randint(1, 12)),
                rework_quantity=rng.randint(1, inspection.failed_quantity),
                rework_reason=rng.choice(_REWORK_REASONS),
            )
        )
    return rows


def _generate_deliveries(
    rng: random.Random,
    ids: DeterministicIdFactory,
    sales_orders: Sequence[SalesOrder],
    work_orders: Sequence[WorkOrder],
) -> list[Delivery]:
    work_by_sales = {row.sales_order_id: row for row in work_orders}
    rows: list[Delivery] = []
    for order in sales_orders:
        work_order = work_by_sales[order.sales_order_id]
        if work_order.actual_end_at is None:
            raise AssertionError("baseline work orders must have an actual end before delivery")
        partial = order.order_quantity > 1 and rng.random() < _TUNING.partial_delivery_probability
        delivered_total = (
            max(1, (order.order_quantity * 3) // 4) if partial else order.order_quantity
        )
        split = delivered_total > 1 and rng.random() < _TUNING.split_delivery_probability
        quantities = (
            (delivered_total // 2, delivered_total - delivered_total // 2)
            if split
            else (delivered_total,)
        )
        first_delivery = max(
            work_order.actual_end_at + timedelta(days=1),
            order.promised_delivery_at + timedelta(days=rng.randint(-2, 4)),
        )
        for sequence, quantity in enumerate(quantities):
            rows.append(
                Delivery(
                    delivery_id=ids.make("del", len(rows) + 1, 48),
                    dataset_version_id=ids.dataset_version_id,
                    sales_order_id=order.sales_order_id,
                    delivery_at=first_delivery + timedelta(days=sequence),
                    delivered_quantity=quantity,
                )
            )
        order.status = "PARTIALLY_DELIVERED" if partial else "DELIVERED"
    return rows


def generate_baseline(config: GenerationConfig) -> GeneratedDataset:
    """Generate one canonical baseline dataset with no scenario intervention."""

    rng = random.Random(config.seed)
    ids = DeterministicIdFactory.from_config(config)
    products, materials, suppliers, customers, work_centers = _generate_dimensions(
        config, rng, ids
    )
    bom = _generate_bom(rng, ids, products, materials)
    sales_orders = _generate_sales_orders(config, rng, ids, products, customers)
    purchase_orders = _generate_purchase_orders(
        config, ids, suppliers, materials, sales_orders, bom
    )
    work_orders = _generate_work_orders(rng, ids, sales_orders)
    operations, operations_by_work_order = _generate_operations(
        rng, ids, work_orders, work_centers
    )
    material_requirements = _generate_material_requirements(ids, work_orders, bom)
    inventory = _generate_inventory(config, ids, materials)
    inspections = _generate_quality(rng, ids, work_orders, operations_by_work_order)
    rework = _generate_rework(rng, ids, inspections, operations_by_work_order)
    deliveries = _generate_deliveries(rng, ids, sales_orders, work_orders)

    unordered: dict[str, Sequence[Base]] = {
        "dim_product": products,
        "dim_material": materials,
        "dim_supplier": suppliers,
        "dim_customer": customers,
        "dim_work_center": work_centers,
        "bridge_product_material": bom,
        "fact_sales_order": sales_orders,
        "fact_purchase_order": purchase_orders,
        "fact_work_order": work_orders,
        "fact_operation": operations,
        "fact_material_requirement": material_requirements,
        "fact_inventory_snapshot": inventory,
        "fact_quality_inspection": inspections,
        "fact_rework": rework,
        "fact_delivery": deliveries,
    }
    ordered = canonicalize_rows(unordered)
    row_count_total = sum(len(rows) for rows in ordered.values())
    content_hash = canonical_content_hash(ordered)
    dataset_version = DatasetVersion(
        dataset_version_id=ids.dataset_version_id,
        seed=config.seed,
        generator_version=config.generator_version,
        profile=config.profile.value,
        period_start=config.period_start,
        period_end=config.period_end,
        generated_at=config.generated_at,
        content_hash=content_hash,
        row_count_total=row_count_total,
    )
    return GeneratedDataset(dataset_version, MappingProxyType(ordered))
