"""Master-data models for the canonical industrial data contract."""

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from flowlens.data import Base


class Product(Base):
    """One synthetic product model."""

    __tablename__ = "dim_product"
    __table_args__ = (
        CheckConstraint("standard_cycle_hours > 0", name="standard_cycle_hours_positive"),
        CheckConstraint(
            "active_to IS NULL OR active_to >= active_from",
            name="valid_active_window",
        ),
        CheckConstraint(
            "product_family IN ('GROUNDING_SWITCH', 'ISOLATION_SWITCH', "
            "'ELECTRIC_CHASSIS')",
            name="product_family_allowed",
        ),
        CheckConstraint(
            "complexity_class IN ('LOW', 'MEDIUM', 'HIGH')",
            name="complexity_class_allowed",
        ),
        UniqueConstraint("dataset_version_id", "product_code"),
    )

    product_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    product_code: Mapped[str] = mapped_column(String(32))
    product_family: Mapped[str] = mapped_column(String(32))
    model_name: Mapped[str] = mapped_column(String(80))
    complexity_class: Mapped[str] = mapped_column(String(16))
    standard_cycle_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    active_from: Mapped[date] = mapped_column(Date)
    active_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class Material(Base):
    """One synthetic material."""

    __tablename__ = "dim_material"
    __table_args__ = (
        CheckConstraint(
            "standard_lead_time_days > 0",
            name="standard_lead_time_days_positive",
        ),
        CheckConstraint(
            "criticality IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="criticality_allowed",
        ),
        UniqueConstraint("dataset_version_id", "material_code"),
    )

    material_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    material_code: Mapped[str] = mapped_column(String(32))
    material_group: Mapped[str] = mapped_column(String(40))
    criticality: Mapped[str] = mapped_column(String(16))
    standard_lead_time_days: Mapped[int] = mapped_column(Integer)
    unit_of_measure: Mapped[str] = mapped_column(String(16))


class Supplier(Base):
    """One synthetic supplier."""

    __tablename__ = "dim_supplier"

    supplier_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    supplier_code: Mapped[str] = mapped_column(String(32))
    supplier_tier: Mapped[str] = mapped_column(String(16))
    region: Mapped[str] = mapped_column(String(40))
    active_from: Mapped[date] = mapped_column(Date)
    active_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class Customer(Base):
    """One anonymized synthetic B2B customer."""

    __tablename__ = "dim_customer"

    customer_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    customer_code: Mapped[str] = mapped_column(String(32))
    customer_segment: Mapped[str] = mapped_column(String(24))
    region: Mapped[str] = mapped_column(String(40))
    active_from: Mapped[date] = mapped_column(Date)
    active_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class WorkCenter(Base):
    """One synthetic manufacturing work center."""

    __tablename__ = "dim_work_center"
    __table_args__ = (
        CheckConstraint(
            "daily_capacity_hours > 0",
            name="daily_capacity_hours_positive",
        ),
        CheckConstraint(
            "process_type IN ('MACHINING', 'WELDING', 'ASSEMBLY', "
            "'INSPECTION', 'PACKING')",
            name="process_type_allowed",
        ),
    )

    work_center_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dataset_version.dataset_version_id")
    )
    work_center_code: Mapped[str] = mapped_column(String(32))
    process_type: Mapped[str] = mapped_column(String(24))
    line_group: Mapped[str] = mapped_column(String(32))
    daily_capacity_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    active_from: Mapped[date] = mapped_column(Date)
    active_to: Mapped[date | None] = mapped_column(Date, nullable=True)
