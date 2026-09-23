"""Product-material bridge model for the canonical industrial data contract."""

from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from flowlens.data import Base


class ProductMaterial(Base):
    """One product-by-material BOM requirement."""

    __tablename__ = "bridge_product_material"
    __table_args__ = (
        CheckConstraint("quantity_per_unit > 0", name="quantity_per_unit_positive"),
    )

    dataset_version_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("dataset_version.dataset_version_id"),
        primary_key=True,
    )
    product_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_product.product_id"), primary_key=True
    )
    material_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("dim_material.material_id"), primary_key=True
    )
    quantity_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    is_critical: Mapped[bool] = mapped_column(Boolean)
