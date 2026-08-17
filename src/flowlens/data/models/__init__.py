"""Deterministic registration boundary for all canonical data models."""

from flowlens.data.models.bridge import ProductMaterial
from flowlens.data.models.dataset import DatasetVersion
from flowlens.data.models.dimensions import Customer, Material, Product, Supplier, WorkCenter
from flowlens.data.models.facts import (
    Delivery,
    InventorySnapshot,
    MaterialRequirement,
    Operation,
    PurchaseOrder,
    QualityInspection,
    Rework,
    SalesOrder,
    WorkOrder,
)


def register_models() -> None:
    """Provide an explicit import boundary for canonical metadata registration."""


__all__ = [
    "Customer",
    "DatasetVersion",
    "Delivery",
    "InventorySnapshot",
    "Material",
    "MaterialRequirement",
    "Operation",
    "Product",
    "ProductMaterial",
    "PurchaseOrder",
    "QualityInspection",
    "Rework",
    "SalesOrder",
    "Supplier",
    "WorkCenter",
    "WorkOrder",
    "register_models",
]
