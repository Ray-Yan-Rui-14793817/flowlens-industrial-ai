# FlowLens Industrial AI — W03-C02 PostgreSQL Snapshot Isolation Contract

**Contract:** `w03-c02-postgres-snapshot.v1`

## 1. Purpose

The PostgreSQL Snapshot Reader at:

```text
src/flowlens/db/decision_snapshot.py
```

is the only C02 runtime capability permitted to access PostgreSQL.

It feeds the DB-free Snapshot Assembler in `flowlens.decision.snapshot`.

Together they produce one consistent decision-time observation world while preserving
the frozen C01 rule that importing `flowlens.decision` does not load SQLAlchemy/database
modules.

## 2. Transaction contract

Use the existing SQLAlchemy dependency.

Required form is semantically equivalent to:

```python
with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
    with connection.begin():
        connection.execute(text("SET TRANSACTION READ ONLY"))
        ...
```

The transaction must remain open for all database reads used to create the StateSnapshot.

No commit-side mutation is allowed.

## 3. Runtime read scope

The Snapshot Builder may read only:

```text
alembic_version
dataset_version

dim_product
dim_material
dim_supplier
dim_customer
dim_work_center

bridge_product_material

fact_sales_order
fact_work_order
fact_operation
fact_material_requirement
fact_purchase_order
fact_inventory_snapshot
fact_quality_inspection
fact_rework
fact_delivery
```

No scenario/HGT filesystem or protected material is an authorized runtime source.

## 4. Do not reuse global full-dataset runtime loading

C02 runtime Snapshot Builder MUST NOT call:

```text
flowlens.data.persistence.read_active_dataset
```

as its operational read path.

Reason:

```text
read_active_dataset materializes the complete active business dataset,
including unrelated orders and future fields.

C02 requires an order-centric, field-projected runtime boundary.
```

The existing function may be used in tests to verify database immutability before/after C02.

## 5. Explicit-column policy

Do not load whole ORM rows for the runtime snapshot.

Use SQLAlchemy Core/Table/explicit-column queries.

This is especially required for fields excluded by the temporal contract:

```text
SalesOrder.status
PurchaseOrder.status
WorkOrder.status
Operation.status
```

Those columns must not be selected by C02 runtime queries.

## 6. SQL-side future masking

For rows that must be read for plan/identity data but contain future actual fields,
future values should be masked at SQL projection time.

Equivalent semantics:

```text
CASE WHEN actual_start_at <= :as_of_time
     THEN actual_start_at
     ELSE NULL
END

CASE WHEN actual_end_at <= :as_of_time
     THEN actual_end_at
     ELSE NULL
END
```

Apply to:

```text
WorkOrder.actual_start_at
WorkOrder.actual_end_at
WorkOrder.completed_quantity (eligible only with actual_end_at)

Operation.actual_start_at
Operation.actual_end_at

PurchaseOrder.actual_receipt_at
PurchaseOrder.received_quantity (eligible only with actual_receipt_at)

Rework.rework_end_at
```

For event rows whose entire event is unavailable before event time, filter in SQL:

```text
QualityInspection.inspection_at <= as_of_time
Rework.rework_start_at <= as_of_time
Delivery.delivery_at <= as_of_time
InventorySnapshot.snapshot_at <= as_of_time
PurchaseOrder.ordered_at <= as_of_time
```

The Python layer must never receive excluded raw statuses from C02 runtime queries.

## 7. Dataset binding sequence

Inside the transaction:

```text
1. verify alembic_version == 0002_industrial_data_foundation
2. read DatasetVersion
3. require exactly one active dataset
4. validate run.dataset_version
5. validate run.dataset_hash == content_hash
6. validate as_of_time in dataset period
7. read target SalesOrder
8. require target order exists
9. require order_at <= as_of_time
10. collect bounded direct graph
11. collect associative graph through MaterialRequirement material IDs
12. validate dataset ownership
13. create sorted SnapshotEntry set
14. create StateSnapshot
15. leave transaction
```

No Evidence/Context building occurs while relying on new database reads.

## 8. Deterministic graph query

Recommended deterministic query order:

```text
SalesOrder
Customer
Product
ProductMaterial
WorkOrder
Operation
WorkCenter
MaterialRequirement
Material
QualityInspection
Rework
Delivery
PurchaseOrder
Supplier
InventorySnapshot
```

SQL row return order must not determine artifact identity.

Every multirow result must be explicitly sorted by a stable key before SnapshotEntry creation.

## 9. Required set semantics

### Target WorkOrders

```text
fact_work_order.sales_order_id == target order
```

No WorkOrder is a valid unknown state, not an immediate DB error.

### Operations / MR / Quality / Rework

Only rows on target WorkOrders.

### ProductMaterial

Only rows for target SalesOrder.product_id.

### PurchaseOrder / Inventory

Only for material IDs from target MaterialRequirement rows.

BOM membership alone does not authorize order-specific procurement association.

### Supplier

Only Suppliers referenced by admitted associated PurchaseOrders.

## 10. Master data policy

Read only referenced master IDs.

Do not scan and inject all customers/products/materials/suppliers/work centers.

Relevant Product/Customer/WorkCenter attributes require `active_from <= as_of_time`.

Supplier attributes are admitted only when its associated PO is admitted and
`active_from <= as_of_time`.

Material has the synthetic period-start availability rule.

## 11. Failure / no partial snapshot

Any exception before StateSnapshot construction:

```text
produces no StateSnapshot
produces no EvidenceBundle
produces no DecisionContext
```

No partial artifact may escape.

Required block mapping:

```text
NO_ACTIVE_DATASET
MULTIPLE_ACTIVE_DATASETS
DATASET_BINDING_MISMATCH
SCHEMA_REVISION_MISMATCH
→ BLOCKED_CONTEXT

AS_OF_OUTSIDE_DATASET_HORIZON
→ BLOCKED_CONTEXT

TARGET_ORDER_NOT_FOUND
→ BLOCKED_CONTEXT

TARGET_ORDER_NOT_AVAILABLE
TEMPORAL_ADMISSION_VIOLATION
→ BLOCKED_TEMPORAL

DATASET_OWNERSHIP_MISMATCH
DIRECT_REFERENCE_MISSING
DELIVERY_QUANTITY_CONTRACT_VIOLATION
→ BLOCKED_CONTRACT

HGT_BOUNDARY_VIOLATION
→ BLOCKED_HGT

READ_ONLY_VIOLATION
→ hard failure / no artifact
```

Exception-class structure is an engineering choice; the observable code/state mapping is not.

## 12. Operational mutation proof

C02 must prove:

```text
row counts unchanged
W2 canonical business payload unchanged
DatasetVersion unchanged
no INSERT/UPDATE/DELETE/TRUNCATE/DDL from Snapshot Builder
```

PostgreSQL READ ONLY is the primary runtime enforcement.

Tests may independently compare database content before/after.

## 13. Runtime SQL audit

Integration tests must capture executed statements for the Snapshot Builder and prove:

```text
no INSERT
no UPDATE
no DELETE
no TRUNCATE
no ALTER
no CREATE
no DROP

no SELECT from an HGT/protected table/path
no excluded status column in runtime SELECT projections
```

Infrastructure statements such as:

```text
SET TRANSACTION READ ONLY
SHOW / SELECT transaction settings
```

are permitted.

## 14. Repeatable-read proof

Integration harness must verify the builder operates under:

```text
transaction_isolation = repeatable read
transaction_read_only = on
```

No downgrade is permitted.

## 15. Connection / engine ownership

The Snapshot Builder accepts an existing SQLAlchemy `Engine`.

It does not:

```text
construct Settings
read .env directly
create a second database
persist connection credentials
log database URLs/secrets
```

## 16. No retry semantics inside artifact construction

A failed snapshot transaction may be retried by a future orchestrator only according to
the G0 failure policy.

C02 builder itself must not merge data from multiple attempts into one artifact.

Each attempt is all-or-nothing.
