"""Create the canonical Week 2 industrial data schema.

Revision ID: 0002_industrial_data_foundation
Revises: 0001_enable_pgvector
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_industrial_data_foundation"
down_revision: str | None = "0001_enable_pgvector"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the 16 frozen Week 2 domain tables."""

    op.create_table(
        "dataset_version",
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("seed", sa.BigInteger(), nullable=False),
        sa.Column("generator_version", sa.String(length=32), nullable=False),
        sa.Column("profile", sa.String(length=16), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("row_count_total", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "period_start < period_end",
            name=op.f("ck_dataset_version_valid_period"),
        ),
        sa.CheckConstraint("seed >= 0", name=op.f("ck_dataset_version_seed_nonnegative")),
        sa.CheckConstraint(
            "profile IN ('test', 'ci', 'demo')",
            name=op.f("ck_dataset_version_profile_allowed"),
        ),
        sa.PrimaryKeyConstraint(
            "dataset_version_id",
            name=op.f("pk_dataset_version"),
        ),
    )
    op.create_table(
        "dim_product",
        sa.Column("product_id", sa.String(length=32), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("product_code", sa.String(length=32), nullable=False),
        sa.Column("product_family", sa.String(length=32), nullable=False),
        sa.Column("model_name", sa.String(length=80), nullable=False),
        sa.Column("complexity_class", sa.String(length=16), nullable=False),
        sa.Column("standard_cycle_hours", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("active_from", sa.Date(), nullable=False),
        sa.Column("active_to", sa.Date(), nullable=True),
        sa.CheckConstraint(
            "standard_cycle_hours > 0",
            name=op.f("ck_dim_product_standard_cycle_hours_positive"),
        ),
        sa.CheckConstraint(
            "active_to IS NULL OR active_to >= active_from",
            name=op.f("ck_dim_product_valid_active_window"),
        ),
        sa.CheckConstraint(
            "product_family IN ('GROUNDING_SWITCH', 'ISOLATION_SWITCH', "
            "'ELECTRIC_CHASSIS')",
            name=op.f("ck_dim_product_product_family_allowed"),
        ),
        sa.CheckConstraint(
            "complexity_class IN ('LOW', 'MEDIUM', 'HIGH')",
            name=op.f("ck_dim_product_complexity_class_allowed"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_dim_product_dataset_version_id_dataset_version"),
        ),
        sa.PrimaryKeyConstraint("product_id", name=op.f("pk_dim_product")),
        sa.UniqueConstraint(
            "dataset_version_id",
            "product_code",
            name=op.f("uq_dim_product_dataset_version_id"),
        ),
    )
    op.create_table(
        "dim_material",
        sa.Column("material_id", sa.String(length=32), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("material_code", sa.String(length=32), nullable=False),
        sa.Column("material_group", sa.String(length=40), nullable=False),
        sa.Column("criticality", sa.String(length=16), nullable=False),
        sa.Column("standard_lead_time_days", sa.Integer(), nullable=False),
        sa.Column("unit_of_measure", sa.String(length=16), nullable=False),
        sa.CheckConstraint(
            "standard_lead_time_days > 0",
            name=op.f("ck_dim_material_standard_lead_time_days_positive"),
        ),
        sa.CheckConstraint(
            "criticality IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name=op.f("ck_dim_material_criticality_allowed"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_dim_material_dataset_version_id_dataset_version"),
        ),
        sa.PrimaryKeyConstraint("material_id", name=op.f("pk_dim_material")),
        sa.UniqueConstraint(
            "dataset_version_id",
            "material_code",
            name=op.f("uq_dim_material_dataset_version_id"),
        ),
    )
    op.create_table(
        "dim_supplier",
        sa.Column("supplier_id", sa.String(length=32), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("supplier_code", sa.String(length=32), nullable=False),
        sa.Column("supplier_tier", sa.String(length=16), nullable=False),
        sa.Column("region", sa.String(length=40), nullable=False),
        sa.Column("active_from", sa.Date(), nullable=False),
        sa.Column("active_to", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_dim_supplier_dataset_version_id_dataset_version"),
        ),
        sa.PrimaryKeyConstraint("supplier_id", name=op.f("pk_dim_supplier")),
    )
    op.create_table(
        "dim_customer",
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("customer_code", sa.String(length=32), nullable=False),
        sa.Column("customer_segment", sa.String(length=24), nullable=False),
        sa.Column("region", sa.String(length=40), nullable=False),
        sa.Column("active_from", sa.Date(), nullable=False),
        sa.Column("active_to", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_dim_customer_dataset_version_id_dataset_version"),
        ),
        sa.PrimaryKeyConstraint("customer_id", name=op.f("pk_dim_customer")),
    )
    op.create_table(
        "dim_work_center",
        sa.Column("work_center_id", sa.String(length=32), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("work_center_code", sa.String(length=32), nullable=False),
        sa.Column("process_type", sa.String(length=24), nullable=False),
        sa.Column("line_group", sa.String(length=32), nullable=False),
        sa.Column("daily_capacity_hours", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("active_from", sa.Date(), nullable=False),
        sa.Column("active_to", sa.Date(), nullable=True),
        sa.CheckConstraint(
            "daily_capacity_hours > 0",
            name=op.f("ck_dim_work_center_daily_capacity_hours_positive"),
        ),
        sa.CheckConstraint(
            "process_type IN ('MACHINING', 'WELDING', 'ASSEMBLY', "
            "'INSPECTION', 'PACKING')",
            name=op.f("ck_dim_work_center_process_type_allowed"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_dim_work_center_dataset_version_id_dataset_version"),
        ),
        sa.PrimaryKeyConstraint("work_center_id", name=op.f("pk_dim_work_center")),
    )
    op.create_table(
        "bridge_product_material",
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("product_id", sa.String(length=32), nullable=False),
        sa.Column("material_id", sa.String(length=32), nullable=False),
        sa.Column("quantity_per_unit", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("is_critical", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "quantity_per_unit > 0",
            name=op.f("ck_bridge_product_material_quantity_per_unit_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_bridge_product_material_dataset_version_id_dataset_version"),
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["dim_material.material_id"],
            name=op.f("fk_bridge_product_material_material_id_dim_material"),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["dim_product.product_id"],
            name=op.f("fk_bridge_product_material_product_id_dim_product"),
        ),
        sa.PrimaryKeyConstraint(
            "dataset_version_id",
            "product_id",
            "material_id",
            name=op.f("pk_bridge_product_material"),
        ),
    )
    op.create_table(
        "fact_sales_order",
        sa.Column("sales_order_id", sa.String(length=40), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("customer_id", sa.String(length=32), nullable=False),
        sa.Column("product_id", sa.String(length=32), nullable=False),
        sa.Column("order_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("promised_delivery_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("order_quantity", sa.Integer(), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.CheckConstraint(
            "order_quantity > 0",
            name=op.f("ck_fact_sales_order_order_quantity_positive"),
        ),
        sa.CheckConstraint(
            "order_at < promised_delivery_at",
            name=op.f("ck_fact_sales_order_valid_order_window"),
        ),
        sa.CheckConstraint(
            "priority IN ('NORMAL', 'HIGH', 'EXPEDITE')",
            name=op.f("ck_fact_sales_order_priority_allowed"),
        ),
        sa.CheckConstraint(
            "status IN ('OPEN', 'IN_PRODUCTION', 'PARTIALLY_DELIVERED', "
            "'DELIVERED', 'CANCELLED')",
            name=op.f("ck_fact_sales_order_status_allowed"),
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["dim_customer.customer_id"],
            name=op.f("fk_fact_sales_order_customer_id_dim_customer"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_fact_sales_order_dataset_version_id_dataset_version"),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["dim_product.product_id"],
            name=op.f("fk_fact_sales_order_product_id_dim_product"),
        ),
        sa.PrimaryKeyConstraint("sales_order_id", name=op.f("pk_fact_sales_order")),
    )
    op.create_table(
        "fact_purchase_order",
        sa.Column("purchase_order_id", sa.String(length=40), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("supplier_id", sa.String(length=32), nullable=False),
        sa.Column("material_id", sa.String(length=32), nullable=False),
        sa.Column("ordered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("promised_receipt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_receipt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ordered_quantity", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("received_quantity", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.CheckConstraint(
            "ordered_quantity > 0",
            name=op.f("ck_fact_purchase_order_ordered_quantity_positive"),
        ),
        sa.CheckConstraint(
            "received_quantity >= 0",
            name=op.f("ck_fact_purchase_order_received_quantity_nonnegative"),
        ),
        sa.CheckConstraint(
            "received_quantity <= ordered_quantity",
            name=op.f("ck_fact_purchase_order_received_quantity_within_ordered"),
        ),
        sa.CheckConstraint(
            "ordered_at < promised_receipt_at",
            name=op.f("ck_fact_purchase_order_valid_promised_receipt"),
        ),
        sa.CheckConstraint(
            "actual_receipt_at IS NULL OR actual_receipt_at >= ordered_at",
            name=op.f("ck_fact_purchase_order_valid_actual_receipt"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_fact_purchase_order_dataset_version_id_dataset_version"),
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["dim_material.material_id"],
            name=op.f("fk_fact_purchase_order_material_id_dim_material"),
        ),
        sa.ForeignKeyConstraint(
            ["supplier_id"],
            ["dim_supplier.supplier_id"],
            name=op.f("fk_fact_purchase_order_supplier_id_dim_supplier"),
        ),
        sa.PrimaryKeyConstraint(
            "purchase_order_id",
            name=op.f("pk_fact_purchase_order"),
        ),
    )
    op.create_table(
        "fact_work_order",
        sa.Column("work_order_id", sa.String(length=40), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("sales_order_id", sa.String(length=40), nullable=False),
        sa.Column("product_id", sa.String(length=32), nullable=False),
        sa.Column("planned_start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("planned_end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_quantity", sa.Integer(), nullable=False),
        sa.Column("completed_quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.CheckConstraint(
            "planned_quantity > 0",
            name=op.f("ck_fact_work_order_planned_quantity_positive"),
        ),
        sa.CheckConstraint(
            "completed_quantity >= 0",
            name=op.f("ck_fact_work_order_completed_quantity_nonnegative"),
        ),
        sa.CheckConstraint(
            "completed_quantity <= planned_quantity",
            name=op.f("ck_fact_work_order_completed_quantity_within_planned"),
        ),
        sa.CheckConstraint(
            "planned_start_at < planned_end_at",
            name=op.f("ck_fact_work_order_valid_planned_window"),
        ),
        sa.CheckConstraint(
            "actual_end_at IS NULL OR actual_start_at IS NOT NULL",
            name=op.f("ck_fact_work_order_actual_end_requires_start"),
        ),
        sa.CheckConstraint(
            "actual_start_at IS NULL OR actual_end_at IS NULL "
            "OR actual_start_at <= actual_end_at",
            name=op.f("ck_fact_work_order_valid_actual_window"),
        ),
        sa.CheckConstraint(
            "status IN ('PLANNED', 'RELEASED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')",
            name=op.f("ck_fact_work_order_status_allowed"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_fact_work_order_dataset_version_id_dataset_version"),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["dim_product.product_id"],
            name=op.f("fk_fact_work_order_product_id_dim_product"),
        ),
        sa.ForeignKeyConstraint(
            ["sales_order_id"],
            ["fact_sales_order.sales_order_id"],
            name=op.f("fk_fact_work_order_sales_order_id_fact_sales_order"),
        ),
        sa.PrimaryKeyConstraint("work_order_id", name=op.f("pk_fact_work_order")),
    )
    op.create_table(
        "fact_operation",
        sa.Column("operation_id", sa.String(length=48), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("work_order_id", sa.String(length=40), nullable=False),
        sa.Column("work_center_id", sa.String(length=32), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("planned_start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("planned_end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.CheckConstraint(
            "sequence_number > 0",
            name=op.f("ck_fact_operation_sequence_number_positive"),
        ),
        sa.CheckConstraint(
            "planned_start_at < planned_end_at",
            name=op.f("ck_fact_operation_valid_planned_window"),
        ),
        sa.CheckConstraint(
            "actual_start_at IS NULL OR actual_end_at IS NULL "
            "OR actual_start_at <= actual_end_at",
            name=op.f("ck_fact_operation_valid_actual_window"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_fact_operation_dataset_version_id_dataset_version"),
        ),
        sa.ForeignKeyConstraint(
            ["work_center_id"],
            ["dim_work_center.work_center_id"],
            name=op.f("fk_fact_operation_work_center_id_dim_work_center"),
        ),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["fact_work_order.work_order_id"],
            name=op.f("fk_fact_operation_work_order_id_fact_work_order"),
        ),
        sa.PrimaryKeyConstraint("operation_id", name=op.f("pk_fact_operation")),
        sa.UniqueConstraint(
            "dataset_version_id",
            "work_order_id",
            "sequence_number",
            name=op.f("uq_fact_operation_dataset_version_id"),
        ),
    )
    op.create_table(
        "fact_material_requirement",
        sa.Column("material_requirement_id", sa.String(length=48), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("work_order_id", sa.String(length=40), nullable=False),
        sa.Column("material_id", sa.String(length=32), nullable=False),
        sa.Column("required_quantity", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("need_by_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "required_quantity > 0",
            name=op.f("ck_fact_material_requirement_required_quantity_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_fact_material_requirement_dataset_version_id_dataset_version"),
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["dim_material.material_id"],
            name=op.f("fk_fact_material_requirement_material_id_dim_material"),
        ),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["fact_work_order.work_order_id"],
            name=op.f("fk_fact_material_requirement_work_order_id_fact_work_order"),
        ),
        sa.PrimaryKeyConstraint(
            "material_requirement_id",
            name=op.f("pk_fact_material_requirement"),
        ),
    )
    op.create_table(
        "fact_inventory_snapshot",
        sa.Column("inventory_snapshot_id", sa.String(length=48), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("material_id", sa.String(length=32), nullable=False),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("on_hand_quantity", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column("reserved_quantity", sa.Numeric(precision=14, scale=4), nullable=False),
        sa.CheckConstraint(
            "on_hand_quantity >= 0",
            name=op.f("ck_fact_inventory_snapshot_on_hand_quantity_nonnegative"),
        ),
        sa.CheckConstraint(
            "reserved_quantity >= 0",
            name=op.f("ck_fact_inventory_snapshot_reserved_quantity_nonnegative"),
        ),
        sa.CheckConstraint(
            "reserved_quantity <= on_hand_quantity",
            name=op.f("ck_fact_inventory_snapshot_reserved_quantity_within_on_hand"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_fact_inventory_snapshot_dataset_version_id_dataset_version"),
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["dim_material.material_id"],
            name=op.f("fk_fact_inventory_snapshot_material_id_dim_material"),
        ),
        sa.PrimaryKeyConstraint(
            "inventory_snapshot_id",
            name=op.f("pk_fact_inventory_snapshot"),
        ),
    )
    op.create_table(
        "fact_quality_inspection",
        sa.Column("inspection_id", sa.String(length=48), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("work_order_id", sa.String(length=40), nullable=False),
        sa.Column("operation_id", sa.String(length=48), nullable=True),
        sa.Column("inspection_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inspection_type", sa.String(length=20), nullable=False),
        sa.Column("inspected_quantity", sa.Integer(), nullable=False),
        sa.Column("passed_quantity", sa.Integer(), nullable=False),
        sa.Column("failed_quantity", sa.Integer(), nullable=False),
        sa.Column("defect_category", sa.String(length=40), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=True),
        sa.Column("result", sa.String(length=8), nullable=False),
        sa.CheckConstraint(
            "inspected_quantity > 0",
            name=op.f("ck_fact_quality_inspection_inspected_quantity_positive"),
        ),
        sa.CheckConstraint(
            "passed_quantity >= 0",
            name=op.f("ck_fact_quality_inspection_passed_quantity_nonnegative"),
        ),
        sa.CheckConstraint(
            "failed_quantity >= 0",
            name=op.f("ck_fact_quality_inspection_failed_quantity_nonnegative"),
        ),
        sa.CheckConstraint(
            "passed_quantity + failed_quantity = inspected_quantity",
            name=op.f("ck_fact_quality_inspection_inspection_quantity_balanced"),
        ),
        sa.CheckConstraint(
            "result IN ('PASS', 'FAIL')",
            name=op.f("ck_fact_quality_inspection_result_allowed"),
        ),
        sa.CheckConstraint(
            "result <> 'PASS' OR failed_quantity = 0",
            name=op.f("ck_fact_quality_inspection_pass_has_no_failures"),
        ),
        sa.CheckConstraint(
            "result <> 'FAIL' OR failed_quantity > 0",
            name=op.f("ck_fact_quality_inspection_fail_has_failures"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_fact_quality_inspection_dataset_version_id_dataset_version"),
        ),
        sa.ForeignKeyConstraint(
            ["operation_id"],
            ["fact_operation.operation_id"],
            name=op.f("fk_fact_quality_inspection_operation_id_fact_operation"),
        ),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["fact_work_order.work_order_id"],
            name=op.f("fk_fact_quality_inspection_work_order_id_fact_work_order"),
        ),
        sa.PrimaryKeyConstraint(
            "inspection_id",
            name=op.f("pk_fact_quality_inspection"),
        ),
    )
    op.create_table(
        "fact_rework",
        sa.Column("rework_id", sa.String(length=48), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("inspection_id", sa.String(length=48), nullable=False),
        sa.Column("work_order_id", sa.String(length=40), nullable=False),
        sa.Column("work_center_id", sa.String(length=32), nullable=False),
        sa.Column("rework_start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rework_end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rework_quantity", sa.Integer(), nullable=False),
        sa.Column("rework_reason", sa.String(length=80), nullable=False),
        sa.CheckConstraint(
            "rework_quantity > 0",
            name=op.f("ck_fact_rework_rework_quantity_positive"),
        ),
        sa.CheckConstraint(
            "rework_start_at <= rework_end_at",
            name=op.f("ck_fact_rework_valid_rework_window"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_fact_rework_dataset_version_id_dataset_version"),
        ),
        sa.ForeignKeyConstraint(
            ["inspection_id"],
            ["fact_quality_inspection.inspection_id"],
            name=op.f("fk_fact_rework_inspection_id_fact_quality_inspection"),
        ),
        sa.ForeignKeyConstraint(
            ["work_center_id"],
            ["dim_work_center.work_center_id"],
            name=op.f("fk_fact_rework_work_center_id_dim_work_center"),
        ),
        sa.ForeignKeyConstraint(
            ["work_order_id"],
            ["fact_work_order.work_order_id"],
            name=op.f("fk_fact_rework_work_order_id_fact_work_order"),
        ),
        sa.PrimaryKeyConstraint("rework_id", name=op.f("pk_fact_rework")),
    )
    op.create_table(
        "fact_delivery",
        sa.Column("delivery_id", sa.String(length=48), nullable=False),
        sa.Column("dataset_version_id", sa.String(length=64), nullable=False),
        sa.Column("sales_order_id", sa.String(length=40), nullable=False),
        sa.Column("delivery_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered_quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "delivered_quantity > 0",
            name=op.f("ck_fact_delivery_delivered_quantity_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.dataset_version_id"],
            name=op.f("fk_fact_delivery_dataset_version_id_dataset_version"),
        ),
        sa.ForeignKeyConstraint(
            ["sales_order_id"],
            ["fact_sales_order.sales_order_id"],
            name=op.f("fk_fact_delivery_sales_order_id_fact_sales_order"),
        ),
        sa.PrimaryKeyConstraint("delivery_id", name=op.f("pk_fact_delivery")),
    )


def downgrade() -> None:
    """Remove the Week 2 domain tables while preserving the Week 1 foundation."""

    op.drop_table("fact_delivery")
    op.drop_table("fact_rework")
    op.drop_table("fact_quality_inspection")
    op.drop_table("fact_inventory_snapshot")
    op.drop_table("fact_material_requirement")
    op.drop_table("fact_operation")
    op.drop_table("fact_work_order")
    op.drop_table("fact_purchase_order")
    op.drop_table("fact_sales_order")
    op.drop_table("bridge_product_material")
    op.drop_table("dim_work_center")
    op.drop_table("dim_customer")
    op.drop_table("dim_supplier")
    op.drop_table("dim_material")
    op.drop_table("dim_product")
    op.drop_table("dataset_version")
