# FlowLens Industrial AI — W03-C02 Source Field → StateSnapshot Matrix

**Contract:** `w03-c02-source-matrix.v1`  
**Purpose:** exact whitelist and decision-time availability semantics.

## 1. Entry conventions

Every admitted source field becomes exactly one `SnapshotEntry`.

Source entry key:

```text
entry_key = source_entity + "|" + source_record_id + "|" + source_field
```

For ordinary tables:

```text
source_record_id = table primary-key value
```

For `bridge_product_material`:

```text
source_record_id =
dataset_version_id + "|" + product_id + "|" + material_id
```

Entry:

```text
entity.entity_type = source_entity
entity.entity_id = source_record_id
field = source_field
source_ref.source_entity = source_entity
source_ref.source_record_id = source_record_id
source_ref.source_field = source_field
entry.available_at = source_ref.available_at
```

`observed_at=None` means the field is plan/master context rather than an observed event.

Fields not listed as INCLUDE below MUST NOT enter StateSnapshot.

## 2. DatasetVersion

DatasetVersion is control/binding metadata, not ordinary operational Evidence.

| Field | C02 action | Use |
|---|---|---|
| dataset_version_id | HEADER/BINDING ONLY | DecisionRun/StateSnapshot dataset binding |
| content_hash | HEADER/BINDING ONLY | `dataset_hash` |
| period_start | CONTROL ONLY | lower decision horizon / baseline availability |
| period_end | CONTROL ONLY | upper decision horizon |
| seed | EXCLUDE | development/generation metadata |
| generator_version | EXCLUDE | generation metadata |
| profile | EXCLUDE | generation metadata |
| generated_at | EXCLUDE | provenance only; never business availability |
| row_count_total | EXCLUDE | data-quality metadata |

## 3. dim_product

Eligibility:

```text
active_from 00:00 Asia/Shanghai <= as_of_time
```

Common `available_at`:

```text
active_from 00:00 Asia/Shanghai
```

`observed_at=None`.

| Field | Action |
|---|---|
| product_id | INCLUDE |
| product_code | INCLUDE |
| product_family | INCLUDE |
| complexity_class | INCLUDE |
| standard_cycle_hours | INCLUDE |
| active_from | INCLUDE |
| model_name | EXCLUDE — descriptive text not required for C02/C03 |
| active_to | EXCLUDE — no knowledge-time semantics in W2 |
| dataset_version_id | BINDING CHECK ONLY |

## 4. dim_customer

Eligibility/availability: `active_from 00:00 Asia/Shanghai`; `observed_at=None`.

| Field | Action |
|---|---|
| customer_id | INCLUDE |
| customer_code | INCLUDE |
| customer_segment | INCLUDE |
| region | INCLUDE |
| active_from | INCLUDE |
| active_to | EXCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

## 5. dim_work_center

Eligibility/availability: `active_from 00:00 Asia/Shanghai`; `observed_at=None`.

| Field | Action |
|---|---|
| work_center_id | INCLUDE |
| work_center_code | INCLUDE |
| process_type | INCLUDE |
| line_group | INCLUDE |
| daily_capacity_hours | INCLUDE |
| active_from | INCLUDE |
| active_to | EXCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

## 6. dim_material

W2 Material has no effective-time field.

Availability:

```text
DatasetVersion.period_start 00:00 Asia/Shanghai
```

`observed_at=None`.

Every included field carries source policy code:

```text
SYNTHETIC_MASTER_BASELINE_AVAILABILITY
```

| Field | Action |
|---|---|
| material_id | INCLUDE |
| material_code | INCLUDE |
| material_group | INCLUDE |
| criticality | INCLUDE |
| standard_lead_time_days | INCLUDE |
| unit_of_measure | INCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

## 7. dim_supplier

Supplier rows are collected only for POs associated through a required Material.

Eligibility/availability: `active_from 00:00 Asia/Shanghai`; `observed_at=None`.

| Field | Action |
|---|---|
| supplier_id | INCLUDE |
| supplier_code | INCLUDE |
| supplier_tier | INCLUDE |
| region | INCLUDE |
| active_from | INCLUDE |
| active_to | EXCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

Although the Supplier attributes are direct facts about that Supplier, their relevance
to the target SalesOrder is associative because the connecting PO is associative.

## 8. bridge_product_material

Rows:

```text
product_id == target SalesOrder.product_id
```

Availability:

```text
DatasetVersion.period_start 00:00 Asia/Shanghai
```

`observed_at=None`.

Every included field carries:

```text
SYNTHETIC_BOM_BASELINE_AVAILABILITY
```

| Field | Action |
|---|---|
| product_id | INCLUDE |
| material_id | INCLUDE |
| quantity_per_unit | INCLUDE |
| is_critical | INCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

ProductMaterial is direct product/BOM context. It does not establish specific PO
allocation or actual consumption.

## 9. fact_sales_order

Target row only.

All included fields:

```text
available_at = order_at
observed_at = order_at
```

| Field | Action |
|---|---|
| sales_order_id | INCLUDE |
| customer_id | INCLUDE |
| product_id | INCLUDE |
| order_at | INCLUDE |
| promised_delivery_at | INCLUDE — commitment known at order time |
| order_quantity | INCLUDE |
| priority | INCLUDE |
| status | EXCLUDE — non-bitemporal final/current state |
| dataset_version_id | BINDING CHECK ONLY |

## 10. fact_work_order

Rows:

```text
sales_order_id == target SalesOrder.sales_order_id
```

Plan/identity fields:

```text
available_at = target SalesOrder.order_at
observed_at = None
limitation = SYNTHETIC_ORDER_PLAN_AVAILABILITY_PROXY
```

| Field | Action / availability |
|---|---|
| work_order_id | INCLUDE / order_at proxy |
| sales_order_id | INCLUDE / order_at proxy |
| product_id | INCLUDE / order_at proxy |
| planned_start_at | INCLUDE / order_at proxy |
| planned_end_at | INCLUDE / order_at proxy |
| planned_quantity | INCLUDE / order_at proxy |
| actual_start_at | INCLUDE only if `actual_start_at <= as_of_time`; observed/available at actual_start_at |
| actual_end_at | INCLUDE only if `actual_end_at <= as_of_time`; observed/available at actual_end_at |
| completed_quantity | INCLUDE only when eligible `actual_end_at <= as_of_time`; observed/available at actual_end_at |
| status | EXCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

No WorkOrder rows is not a contract failure; it creates snapshot unknown:

```text
WORK_ORDER_EVIDENCE_MISSING
```

## 11. fact_operation

Rows belong to collected target WorkOrders.

Plan/identity fields:

```text
available_at = target SalesOrder.order_at
observed_at = None
limitation = SYNTHETIC_ORDER_PLAN_AVAILABILITY_PROXY
```

| Field | Action / availability |
|---|---|
| operation_id | INCLUDE / order_at proxy |
| work_order_id | INCLUDE / order_at proxy |
| work_center_id | INCLUDE / order_at proxy |
| sequence_number | INCLUDE / order_at proxy |
| planned_start_at | INCLUDE / order_at proxy |
| planned_end_at | INCLUDE / order_at proxy |
| actual_start_at | INCLUDE only if <= as_of; observed/available at actual_start_at |
| actual_end_at | INCLUDE only if <= as_of; observed/available at actual_end_at |
| status | EXCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

## 12. fact_material_requirement

Rows belong to target WorkOrders.

All fields below:

```text
available_at = target SalesOrder.order_at
observed_at = None
limitation = SYNTHETIC_ORDER_PLAN_AVAILABILITY_PROXY
```

| Field | Action |
|---|---|
| material_requirement_id | INCLUDE |
| work_order_id | INCLUDE |
| material_id | INCLUDE |
| required_quantity | INCLUDE |
| need_by_at | INCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

If WorkOrders exist but there are no MaterialRequirement rows:

```text
MATERIAL_REQUIREMENT_EVIDENCE_MISSING
```

Only MaterialRequirement material IDs authorize C02 procurement/inventory association.

## 13. fact_purchase_order

Rows:

```text
material_id is in target MaterialRequirement material IDs
and
ordered_at <= as_of_time
```

Order-side fields:

```text
available_at = ordered_at
observed_at = ordered_at
```

Receipt-side fields are admitted only if:

```text
actual_receipt_at is not None
and actual_receipt_at <= as_of_time
```

| Field | Action / availability |
|---|---|
| purchase_order_id | INCLUDE / ordered_at |
| supplier_id | INCLUDE / ordered_at |
| material_id | INCLUDE / ordered_at |
| ordered_at | INCLUDE / ordered_at |
| promised_receipt_at | INCLUDE / ordered_at |
| ordered_quantity | INCLUDE / ordered_at |
| actual_receipt_at | CONDITIONAL / actual_receipt_at |
| received_quantity | CONDITIONAL / actual_receipt_at |
| status | EXCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

Every PO entry is target-order associative context:

```text
MATERIAL_TIME_ASSOCIATION
ASSOCIATIVE_EVIDENCE
DOES_NOT_ESTABLISH_ORDER_SPECIFIC_ALLOCATION
```

The builder must not choose one PO as "the" supplier/allocation for the WorkOrder.

## 14. fact_inventory_snapshot

Rows:

```text
material_id is in target MaterialRequirement material IDs
and
snapshot_at <= as_of_time
```

All included fields:

```text
available_at = snapshot_at
observed_at = snapshot_at
```

| Field | Action |
|---|---|
| inventory_snapshot_id | INCLUDE |
| material_id | INCLUDE |
| snapshot_at | INCLUDE |
| on_hand_quantity | INCLUDE |
| reserved_quantity | INCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

All are:

```text
MATERIAL_TIME_ASSOCIATION
ASSOCIATIVE_EVIDENCE
```

with limitation:

```text
DOES_NOT_ESTABLISH_AVAILABILITY_AT_WORK_ORDER_EXECUTION
```

All eligible snapshots are retained. C02 does not silently discard older snapshots.

If no eligible snapshot exists for a required Material:

```text
INVENTORY_EVIDENCE_MISSING
```

## 15. fact_quality_inspection

Rows:

```text
work_order_id in target WorkOrders
and inspection_at <= as_of_time
```

All included fields are observed/available at `inspection_at`.

| Field | Action |
|---|---|
| inspection_id | INCLUDE |
| work_order_id | INCLUDE |
| operation_id | INCLUDE, including explicit null |
| inspection_at | INCLUDE |
| inspection_type | INCLUDE |
| inspected_quantity | INCLUDE |
| passed_quantity | INCLUDE |
| failed_quantity | INCLUDE |
| defect_category | INCLUDE |
| severity | INCLUDE |
| result | INCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

Inspection is a direct event.

It never proves formal release.

## 16. fact_rework

Rows:

```text
work_order_id in target WorkOrders
and rework_start_at <= as_of_time
```

Start-side fields are observed/available at `rework_start_at`:

| Field | Action / availability |
|---|---|
| rework_id | INCLUDE / rework_start_at |
| inspection_id | INCLUDE / rework_start_at |
| work_order_id | INCLUDE / rework_start_at |
| work_center_id | INCLUDE / rework_start_at |
| rework_start_at | INCLUDE / rework_start_at |
| rework_quantity | INCLUDE / rework_start_at |
| rework_reason | INCLUDE / rework_start_at + `UNTRUSTED_OPERATIONAL_TEXT` |
| rework_end_at | INCLUDE only if `rework_end_at <= as_of_time`; observed/available at rework_end_at |
| dataset_version_id | BINDING CHECK ONLY |

Rework is a direct event.

It never proves formal quality release.

## 17. fact_delivery

Rows:

```text
sales_order_id == target SalesOrder
and delivery_at <= as_of_time
```

All included fields are observed/available at `delivery_at`.

| Field | Action |
|---|---|
| delivery_id | INCLUDE |
| sales_order_id | INCLUDE |
| delivery_at | INCLUDE |
| delivered_quantity | INCLUDE |
| dataset_version_id | BINDING CHECK ONLY |

Future deliveries have zero visible semantic effect on an earlier snapshot.

## 18. Master references

After collecting source rows, referenced master records may be added only from:

```text
target SalesOrder customer/product
target ProductMaterial / MaterialRequirement materials
target Operations work centers
associated PurchaseOrders suppliers
```

No global master-data dump is authorized.

## 19. Sorting / determinism

Snapshot entries MUST be sorted and unique by:

```text
entry_key
```

Source refs in provenance MUST satisfy existing C01 sorted/unique rules.

The same dataset/run/contract must produce identical StateSnapshot bytes and identity.

## 20. Protected / forbidden material

Never query or project:

```text
scenario_id
scenario_type
scenario label
HGT
true root cause
affected entity list
causal chain
expected evaluation answer
developer review content
Codex prompt
```

No hidden-ground-truth path is an authorized source.
