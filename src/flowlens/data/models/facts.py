"""Operational fact models for the canonical industrial data contract."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from flowlens.data import Base


class SalesOrder(Base):
    """One customer-by-product delivery commitment."""

    __tablename__ = "fact_sales_order"
    __table_args__ = (
        CheckConstraint("order_quantity > 0", name="order_quantity_positive"),
        CheckConstraint("order_at < promised_delivery_at", name="valid_order_window"),
        CheckConstraint(
            "priority IN ('NORMAL', 'HIGH', 'EXPEDITE')",
            name="priority_allowed",
        ),
        CheckConstraint(
            "status IN ('OPEN', 'IN_PRODUCTION', 'PARTIALLY_DELIVERED', "
            "'DELIVERED', 'CANCELLED')",
            name="status_allowed",
        ),
    )

    sales_order_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    customer_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_customer.customer_id")
    )
    product_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_product.product_id")
    )
    order_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    promised_delivery_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    order_quantity: Mapped[int] = mapped_column(Integer)
    priority: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(24))


class PurchaseOrder(Base):
    """One supplier-by-material purchase commitment."""

    __tablename__ = "fact_purchase_order"
    __table_args__ = (
        CheckConstraint("ordered_quantity > 0", name="ordered_quantity_positive"),
        CheckConstraint("received_quantity >= 0", name="received_quantity_nonnegative"),
        CheckConstraint(
            "received_quantity <= ordered_quantity",
            name="received_quantity_within_ordered",
        ),
        CheckConstraint(
            "ordered_at < promised_receipt_at",
            name="valid_promised_receipt",
        ),
        CheckConstraint(
            "actual_receipt_at IS NULL OR actual_receipt_at >= ordered_at",
            name="valid_actual_receipt",
        ),
    )

    purchase_order_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    supplier_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_supplier.supplier_id")
    )
    material_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_material.material_id")
    )
    ordered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    promised_receipt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual_receipt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ordered_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    received_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    status: Mapped[str] = mapped_column(String(20))


class WorkOrder(Base):
    """One production work order."""

    __tablename__ = "fact_work_order"
    __table_args__ = (
        CheckConstraint("planned_quantity > 0", name="planned_quantity_positive"),
        CheckConstraint("completed_quantity >= 0", name="completed_quantity_nonnegative"),
        CheckConstraint(
            "completed_quantity <= planned_quantity",
            name="completed_quantity_within_planned",
        ),
        CheckConstraint(
            "planned_start_at < planned_end_at",
            name="valid_planned_window",
        ),
        CheckConstraint(
            "actual_end_at IS NULL OR actual_start_at IS NOT NULL",
            name="actual_end_requires_start",
        ),
        CheckConstraint(
            "actual_start_at IS NULL OR actual_end_at IS NULL "
            "OR actual_start_at <= actual_end_at",
            name="valid_actual_window",
        ),
        CheckConstraint(
            "status IN ('PLANNED', 'RELEASED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')",
            name="status_allowed",
        ),
    )

    work_order_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    sales_order_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("fact_sales_order.sales_order_id")
    )
    product_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_product.product_id")
    )
    planned_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    planned_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual_start_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_quantity: Mapped[int] = mapped_column(Integer)
    completed_quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))


class Operation(Base):
    """One work-order process step."""

    __tablename__ = "fact_operation"
    __table_args__ = (
        CheckConstraint("sequence_number > 0", name="sequence_number_positive"),
        CheckConstraint(
            "planned_start_at < planned_end_at",
            name="valid_planned_window",
        ),
        CheckConstraint(
            "actual_start_at IS NULL OR actual_end_at IS NULL "
            "OR actual_start_at <= actual_end_at",
            name="valid_actual_window",
        ),
        UniqueConstraint("dataset_version_id", "work_order_id", "sequence_number"),
    )

    operation_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    work_order_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("fact_work_order.work_order_id")
    )
    work_center_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_work_center.work_center_id")
    )
    sequence_number: Mapped[int] = mapped_column(Integer)
    planned_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    planned_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual_start_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20))


class MaterialRequirement(Base):
    """One work-order-by-material requirement."""

    __tablename__ = "fact_material_requirement"
    __table_args__ = (
        CheckConstraint("required_quantity > 0", name="required_quantity_positive"),
    )

    material_requirement_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    work_order_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("fact_work_order.work_order_id")
    )
    material_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_material.material_id")
    )
    required_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    need_by_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InventorySnapshot(Base):
    """One material inventory snapshot event."""

    __tablename__ = "fact_inventory_snapshot"
    __table_args__ = (
        CheckConstraint("on_hand_quantity >= 0", name="on_hand_quantity_nonnegative"),
        CheckConstraint("reserved_quantity >= 0", name="reserved_quantity_nonnegative"),
        CheckConstraint(
            "reserved_quantity <= on_hand_quantity",
            name="reserved_quantity_within_on_hand",
        ),
    )

    inventory_snapshot_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    material_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_material.material_id")
    )
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    on_hand_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    reserved_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4))


class QualityInspection(Base):
    """One quality inspection event."""

    __tablename__ = "fact_quality_inspection"
    __table_args__ = (
        CheckConstraint("inspected_quantity > 0", name="inspected_quantity_positive"),
        CheckConstraint("passed_quantity >= 0", name="passed_quantity_nonnegative"),
        CheckConstraint("failed_quantity >= 0", name="failed_quantity_nonnegative"),
        CheckConstraint(
            "passed_quantity + failed_quantity = inspected_quantity",
            name="inspection_quantity_balanced",
        ),
        CheckConstraint("result IN ('PASS', 'FAIL')", name="result_allowed"),
        CheckConstraint(
            "result <> 'PASS' OR failed_quantity = 0",
            name="pass_has_no_failures",
        ),
        CheckConstraint(
            "result <> 'FAIL' OR failed_quantity > 0",
            name="fail_has_failures",
        ),
    )

    inspection_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    work_order_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("fact_work_order.work_order_id")
    )
    operation_id: Mapped[str | None] = mapped_column(
        String(48), ForeignKey("fact_operation.operation_id"), nullable=True
    )
    inspection_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    inspection_type: Mapped[str] = mapped_column(String(20))
    inspected_quantity: Mapped[int] = mapped_column(Integer)
    passed_quantity: Mapped[int] = mapped_column(Integer)
    failed_quantity: Mapped[int] = mapped_column(Integer)
    defect_category: Mapped[str | None] = mapped_column(String(40), nullable=True)
    severity: Mapped[str | None] = mapped_column(String(16), nullable=True)
    result: Mapped[str] = mapped_column(String(8))


class Rework(Base):
    """One rework event."""

    __tablename__ = "fact_rework"
    __table_args__ = (
        CheckConstraint("rework_quantity > 0", name="rework_quantity_positive"),
        CheckConstraint(
            "rework_start_at <= rework_end_at",
            name="valid_rework_window",
        ),
    )

    rework_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    inspection_id: Mapped[str] = mapped_column(
        String(48), ForeignKey("fact_quality_inspection.inspection_id")
    )
    work_order_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("fact_work_order.work_order_id")
    )
    work_center_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_work_center.work_center_id")
    )
    rework_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    rework_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    rework_quantity: Mapped[int] = mapped_column(Integer)
    rework_reason: Mapped[str] = mapped_column(String(80))


class Delivery(Base):
    """One actual delivery event."""

    __tablename__ = "fact_delivery"
    __table_args__ = (
        CheckConstraint("delivered_quantity > 0", name="delivered_quantity_positive"),
    )

    delivery_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    sales_order_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("fact_sales_order.sales_order_id")
    )
    delivery_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    delivered_quantity: Mapped[int] = mapped_column(Integer)
