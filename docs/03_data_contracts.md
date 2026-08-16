# FlowLens Industrial AI — Industrial Data Contracts / 工业数据契约

**Document:** `docs/03_data_contracts.md`
**Version / 版本:** `v0.1`
**Sprint / Sprint:** `Week 2 — Industrial Data Foundation`
**Stage / 阶段:** `DESCRIBE`
**Status / 状态:** `FROZEN FOR W02 CODEX IMPLEMENTATION`
**Contract Owner / 契约控制端:** `ChatGPT`
**Implementation Owner / 工程实现端:** `Codex`
**Domain / 领域:** `High-voltage Electrical Equipment Manufacturing — synthetic / anonymized / industry-inspired`

---

## 1. Purpose / 文档目的

### 中文

本文件冻结 FlowLens Industrial AI Week 2 的 canonical industrial data contract。

Week 2 的目标不是构建 Analytics、ML、RAG 或 LLM 功能，而是建立一套可复现、可测试、可追踪的 Synthetic Industrial Dataset，为后续以下能力提供稳定的数据语义基础：

- Week 3 Manufacturing Analytics；
- Week 4 Operations Dashboard；
- Week 5–8 Delivery Risk Prediction；
- Week 11–12 Evidence-Grounded Investigation。

所有 Week 2 工程实现必须遵守本文件。Codex 不得为了实现方便静默修改字段语义、粒度、主外键、时间语义、Ground Truth 隔离规则或数据质量规则。如发现不可实现、矛盾或遗漏，必须报告 contract conflict。

### English

This document freezes the canonical Week 2 industrial data contract for FlowLens Industrial AI.

Week 2 does not implement analytics, ML, RAG, or LLM capabilities. It establishes a reproducible, testable, traceable synthetic industrial dataset that becomes the stable semantic foundation for later analytics, delivery-risk prediction, and evidence-grounded investigation.

Implementation must conform to this document. Contract conflicts must be reported rather than silently resolved.

---

## 2. Week 2 Data Design Principles / 数据设计原则

1. **Contract first / 契约优先**
   Schema and business meaning are defined before implementation.

2. **Raw facts before derived metrics / 原始事实优先于派生指标**
   Week 2 stores business facts. Week 3 calculates metrics.

3. **Deterministic generation / 可复现生成**
   Same generator version + profile + seed + scenario configuration must produce the same canonical dataset content hash.

4. **No future leakage / 防止未来信息泄漏**
   Every field must have a data-availability classification for future ML use.

5. **Hidden Ground Truth isolation / 隐藏真相隔离**
   Scenario labels and true root causes must never appear in runtime operational tables or production application code paths.

6. **Industry-inspired, not company-internal / 行业参考而非真实企业内部数据**
   Synthetic parameters are modeling assumptions and must not be represented as the actual production parameters of Zhejiang Hengbo Electrical Manufacturing Co., Ltd. or any other real enterprise.

7. **One primary relational model / 单一主关系模型**
   PostgreSQL remains the primary database. Week 2 does not introduce a second operational database, warehouse, message broker, or event platform.

---

## 3. Canonical Order-to-Delivery Digital Thread / 订单到交付数字线程

```text
Customer
   ↓
Sales Order
   ↓
Product
   ↓
Product-Material BOM
   ↓
Material Requirement
   ↓
Supplier / Purchase Order
   ↓
Inventory Availability
   ↓
Work Order
   ↓
Operation / Work Center
   ↓
Quality Inspection
   ↓
Rework (when required)
   ↓
Delivery
```

This digital thread is the minimum data backbone for the first FlowLens vertical: **Production Delivery Intelligence**.

---

## 4. Naming Decision / 命名决策

Week 2 follows the approved four-month plan terminology:

- dimensions use `dim_*`;
- transaction / operational fact tables use `fact_*`;
- dataset metadata uses `dataset_version`;
- product-material BOM uses `bridge_product_material`.

This naming is intentionally retained for Week 2 consistency. A future migration to different domain naming requires an explicit ADR and must not be performed silently by Codex.

---

# 5. Dataset Metadata Contract / 数据集元数据契约

## 5.1 `dataset_version`

**Grain / 粒度:** one complete synthetic dataset generation run per row.

| Field | Type | Required | Meaning / 业务含义 |
|---|---|---:|---|
| `dataset_version_id` | varchar(64) PK | Yes | Stable dataset version identifier |
| `seed` | bigint | Yes | Deterministic random seed |
| `generator_version` | varchar(32) | Yes | Synthetic generator semantic version |
| `profile` | varchar(16) | Yes | `test`, `ci`, or `demo` |
| `period_start` | date | Yes | Beginning of business-time coverage |
| `period_end` | date | Yes | End of business-time coverage |
| `generated_at` | timestamptz | Yes | Technical generation timestamp |
| `content_hash` | varchar(128) | Yes | Hash of canonical sorted business content |
| `row_count_total` | bigint | Yes | Total generated business rows |

### Constraints

- `period_start < period_end`
- `seed >= 0`
- `profile IN ('test', 'ci', 'demo')`
- `content_hash` must not include `generated_at`
- runtime manifest must not contain scenario labels, affected entities, or true root causes

### Week 2 v1 database policy

Only one active synthetic dataset is required per development database. Re-loading the same `dataset_version_id` must not silently duplicate records.

Default behavior:

- existing dataset version → fail clearly;
- explicit development/test replacement may be supported through a documented `--replace` option;
- production-like runtime must not silently replace data.

---

# 6. Master Data Contracts / 主数据契约

All generated master-data rows belong to the active `dataset_version_id`.

## 6.1 `dim_product`

**Grain:** one synthetic product model per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `product_id` | varchar(32) PK | Yes | Stable synthetic product ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `product_code` | varchar(32) | Yes | Human-readable stable code |
| `product_family` | varchar(32) | Yes | Product family |
| `model_name` | varchar(80) | Yes | Synthetic model display name |
| `complexity_class` | varchar(16) | Yes | `LOW`, `MEDIUM`, `HIGH` |
| `standard_cycle_hours` | numeric(10,2) | Yes | Synthetic standard production cycle |
| `active_from` | date | Yes | Active start date |
| `active_to` | date nullable | No | Optional inactive date |

**Approved synthetic product families:**

- `GROUNDING_SWITCH`
- `ISOLATION_SWITCH`
- `ELECTRIC_CHASSIS`

**Constraints:**

- `standard_cycle_hours > 0`
- `active_to IS NULL OR active_to >= active_from`
- unique: `(dataset_version_id, product_code)`

---

## 6.2 `dim_material`

**Grain:** one synthetic material per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `material_id` | varchar(32) PK | Yes | Stable material ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `material_code` | varchar(32) | Yes | Stable material code |
| `material_group` | varchar(40) | Yes | Material classification |
| `criticality` | varchar(16) | Yes | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `standard_lead_time_days` | integer | Yes | Baseline synthetic sourcing lead time |
| `unit_of_measure` | varchar(16) | Yes | Unit of measure |

**Constraints:**

- `standard_lead_time_days > 0`
- unique: `(dataset_version_id, material_code)`

---

## 6.3 `dim_supplier`

**Grain:** one synthetic supplier per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `supplier_id` | varchar(32) PK | Yes | Stable synthetic supplier ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `supplier_code` | varchar(32) | Yes | Stable supplier code |
| `supplier_tier` | varchar(16) | Yes | Synthetic supplier tier |
| `region` | varchar(40) | Yes | Synthetic region |
| `active_from` | date | Yes | Active start date |
| `active_to` | date nullable | No | Optional inactive date |

**Do not store derived supplier metrics in this table**, including:

- supplier risk score;
- supplier delay rate;
- supplier on-time rate.

These are Week 3 derived analytics.

---

## 6.4 `dim_customer`

**Grain:** one anonymized synthetic B2B customer per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `customer_id` | varchar(32) PK | Yes | Stable synthetic customer ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `customer_code` | varchar(32) | Yes | Anonymized code such as `CUS-001` |
| `customer_segment` | varchar(24) | Yes | Synthetic B2B segment |
| `region` | varchar(40) | Yes | Synthetic region |
| `active_from` | date | Yes | Active start date |
| `active_to` | date nullable | No | Optional inactive date |

Real customer names must not be used.

---

## 6.5 `dim_work_center`

**Grain:** one manufacturing work center per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `work_center_id` | varchar(32) PK | Yes | Stable work-center ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `work_center_code` | varchar(32) | Yes | Work-center code |
| `process_type` | varchar(24) | Yes | Manufacturing process class |
| `line_group` | varchar(32) | Yes | Synthetic production line grouping |
| `daily_capacity_hours` | numeric(10,2) | Yes | Baseline daily available hours |
| `active_from` | date | Yes | Active start date |
| `active_to` | date nullable | No | Optional inactive date |

**Approved process types:**

- `MACHINING`
- `WELDING`
- `ASSEMBLY`
- `INSPECTION`
- `PACKING`

**Constraints:**

- `daily_capacity_hours > 0`

---

# 7. Product-Material Bridge / 产品物料桥接表

## 7.1 `bridge_product_material`

**Grain:** one product × material BOM requirement per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `product_id` | varchar(32) FK | Yes | Product |
| `material_id` | varchar(32) FK | Yes | Required material |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `quantity_per_unit` | numeric(12,4) | Yes | Material quantity required per product unit |
| `is_critical` | boolean | Yes | Whether material is critical to production |

**Primary / unique key:** `(dataset_version_id, product_id, material_id)`

**Constraints:**

- `quantity_per_unit > 0`

---

# 8. Transactional Fact Contracts / 交易事实契约

## 8.1 `fact_sales_order`

**Grain:** one customer × product delivery commitment per row.

For FlowLens v1, a row intentionally represents a single product commitment rather than implementing a full ERP order-header/order-line model.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `sales_order_id` | varchar(40) PK | Yes | Stable order ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `customer_id` | varchar(32) FK | Yes | Customer |
| `product_id` | varchar(32) FK | Yes | Product |
| `order_at` | timestamptz | Yes | Order creation business time |
| `promised_delivery_at` | timestamptz | Yes | Customer delivery commitment |
| `order_quantity` | integer | Yes | Ordered product quantity |
| `priority` | varchar(16) | Yes | `NORMAL`, `HIGH`, `EXPEDITE` |
| `status` | varchar(24) | Yes | Operational order status |

**Approved status values:**

- `OPEN`
- `IN_PRODUCTION`
- `PARTIALLY_DELIVERED`
- `DELIVERED`
- `CANCELLED`

**Constraints:**

- `order_quantity > 0`
- `order_at < promised_delivery_at`

**Do not store:**

- `is_delayed`
- `delay_days`
- `delivery_delay_rate`
- `delay_probability`

---

## 8.2 `fact_purchase_order`

**Grain:** one supplier × material purchase commitment per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `purchase_order_id` | varchar(40) PK | Yes | Stable PO ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `supplier_id` | varchar(32) FK | Yes | Supplier |
| `material_id` | varchar(32) FK | Yes | Material |
| `ordered_at` | timestamptz | Yes | PO creation time |
| `promised_receipt_at` | timestamptz | Yes | Supplier committed receipt time |
| `actual_receipt_at` | timestamptz nullable | No | Actual receipt time when received |
| `ordered_quantity` | numeric(14,4) | Yes | Ordered quantity |
| `received_quantity` | numeric(14,4) | Yes | Received quantity to date/final |
| `status` | varchar(20) | Yes | Purchase-order status |

**Constraints:**

- `ordered_quantity > 0`
- `received_quantity >= 0`
- `received_quantity <= ordered_quantity`
- `ordered_at < promised_receipt_at`
- `actual_receipt_at IS NULL OR actual_receipt_at >= ordered_at`

**Do not store:**

- `supplier_delay_days`
- `supplier_on_time_rate`
- `supplier_risk_score`

---

## 8.3 `fact_work_order`

**Grain:** one production work order per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `work_order_id` | varchar(40) PK | Yes | Stable work-order ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `sales_order_id` | varchar(40) FK | Yes | Source sales order |
| `product_id` | varchar(32) FK | Yes | Product |
| `planned_start_at` | timestamptz | Yes | Planned production start |
| `planned_end_at` | timestamptz | Yes | Planned production end |
| `actual_start_at` | timestamptz nullable | No | Actual start when started |
| `actual_end_at` | timestamptz nullable | No | Actual completion time when completed |
| `planned_quantity` | integer | Yes | Planned production quantity |
| `completed_quantity` | integer | Yes | Completed quantity |
| `status` | varchar(20) | Yes | Work-order status |

**Approved status values:**

- `PLANNED`
- `RELEASED`
- `IN_PROGRESS`
- `COMPLETED`
- `CANCELLED`

**Constraints:**

- `planned_quantity > 0`
- `0 <= completed_quantity <= planned_quantity`
- `planned_start_at < planned_end_at`
- `actual_end_at IS NULL OR actual_start_at IS NOT NULL`
- `actual_start_at IS NULL OR actual_end_at IS NULL OR actual_start_at <= actual_end_at`

---

## 8.4 `fact_operation`

**Grain:** one work-order process step per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `operation_id` | varchar(48) PK | Yes | Stable operation ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `work_order_id` | varchar(40) FK | Yes | Work order |
| `work_center_id` | varchar(32) FK | Yes | Work center |
| `sequence_number` | integer | Yes | Ordered process sequence |
| `planned_start_at` | timestamptz | Yes | Planned start |
| `planned_end_at` | timestamptz | Yes | Planned end |
| `actual_start_at` | timestamptz nullable | No | Actual start |
| `actual_end_at` | timestamptz nullable | No | Actual end |
| `status` | varchar(20) | Yes | Operation status |

**Unique:** `(dataset_version_id, work_order_id, sequence_number)`

**Constraints:**

- `sequence_number > 0`
- `planned_start_at < planned_end_at`
- `actual_start_at IS NULL OR actual_end_at IS NULL OR actual_start_at <= actual_end_at`

Queue time, WIP, utilization, and cycle-time metrics are derived later and are not stored as Week 2 facts.

---

## 8.5 `fact_material_requirement`

**Grain:** one work-order × material requirement per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `material_requirement_id` | varchar(48) PK | Yes | Stable requirement ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `work_order_id` | varchar(40) FK | Yes | Work order |
| `material_id` | varchar(32) FK | Yes | Material |
| `required_quantity` | numeric(14,4) | Yes | Required quantity |
| `need_by_at` | timestamptz | Yes | Required-by business time |

**Constraints:**

- `required_quantity > 0`

Material requirements should be generated from the product BOM and work-order quantity rather than independently random values.

---

## 8.6 `fact_inventory_snapshot`

**Grain:** one material × snapshot date/time per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `inventory_snapshot_id` | varchar(48) PK | Yes | Stable snapshot ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `material_id` | varchar(32) FK | Yes | Material |
| `snapshot_at` | timestamptz | Yes | Inventory snapshot business time |
| `on_hand_quantity` | numeric(14,4) | Yes | Physical stock |
| `reserved_quantity` | numeric(14,4) | Yes | Reserved stock |

**Constraints:**

- `on_hand_quantity >= 0`
- `reserved_quantity >= 0`
- `reserved_quantity <= on_hand_quantity`

**Do not store derived `material_availability` or `material_availability_ratio`.**

---

## 8.7 `fact_quality_inspection`

**Grain:** one quality inspection event per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `inspection_id` | varchar(48) PK | Yes | Stable inspection ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `work_order_id` | varchar(40) FK | Yes | Work order |
| `operation_id` | varchar(48) FK nullable | No | Optional related operation |
| `inspection_at` | timestamptz | Yes | Inspection business time |
| `inspection_type` | varchar(20) | Yes | Inspection class |
| `inspected_quantity` | integer | Yes | Inspected quantity |
| `passed_quantity` | integer | Yes | Passed quantity |
| `failed_quantity` | integer | Yes | Failed quantity |
| `defect_category` | varchar(40) nullable | No | Synthetic defect class when applicable |
| `severity` | varchar(16) nullable | No | Synthetic severity |
| `result` | varchar(8) | Yes | `PASS` or `FAIL` |

**Constraints:**

- `inspected_quantity > 0`
- `passed_quantity >= 0`
- `failed_quantity >= 0`
- `passed_quantity + failed_quantity = inspected_quantity`
- `result = 'PASS'` implies `failed_quantity = 0`
- `result = 'FAIL'` implies `failed_quantity > 0`

---

## 8.8 `fact_rework`

**Grain:** one rework event per row.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `rework_id` | varchar(48) PK | Yes | Stable rework ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `inspection_id` | varchar(48) FK | Yes | Triggering inspection |
| `work_order_id` | varchar(40) FK | Yes | Work order |
| `work_center_id` | varchar(32) FK | Yes | Rework work center |
| `rework_start_at` | timestamptz | Yes | Rework start |
| `rework_end_at` | timestamptz | Yes | Rework end |
| `rework_quantity` | integer | Yes | Reworked quantity |
| `rework_reason` | varchar(80) | Yes | Synthetic reason category |

**Constraints:**

- `rework_quantity > 0`
- `rework_start_at <= rework_end_at`
- `rework_start_at >= related inspection_at`
- `rework_quantity <= related inspection.failed_quantity`

---

## 8.9 `fact_delivery`

**Grain:** one actual delivery event per row.

A sales order may have one or more delivery events.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `delivery_id` | varchar(48) PK | Yes | Stable delivery ID |
| `dataset_version_id` | varchar(64) FK | Yes | Dataset version |
| `sales_order_id` | varchar(40) FK | Yes | Sales order |
| `delivery_at` | timestamptz | Yes | Actual delivery event time |
| `delivered_quantity` | integer | Yes | Quantity delivered in event |

**Constraints:**

- `delivered_quantity > 0`
- `delivery_at >= related sales_order.order_at`
- cumulative delivered quantity must not exceed sales-order quantity

**Week 3 derivation:**

- final delivery time = latest delivery event required to fulfill the ordered quantity;
- delay status is derived from final delivery time versus promised delivery time.

---

# 9. Raw Facts vs Derived Metrics / 原始事实与派生指标边界

Week 2 stores **raw operational facts** only.

| Store in Week 2 | Derive later |
|---|---|
| `promised_delivery_at`, `delivery_at` | `is_delayed`, delay days, On-Time Delivery, Delay Rate |
| `actual_start_at`, `actual_end_at` | Cycle Time |
| operation timing | Queue Time, WIP, utilization |
| `promised_receipt_at`, `actual_receipt_at` | Supplier On-Time Rate, supplier delay days |
| inventory and material requirement quantities | Material Availability |
| inspection passed/failed quantities | FPY |
| inspection + rework events | Rework Rate |
| raw operational facts | Delivery Risk probability |

The following must not exist in Week 2 operational tables:

```text
is_delayed
delay_days
delivery_delay_rate
supplier_risk_score
supplier_on_time_rate
material_availability_ratio
first_pass_yield
rework_rate
delivery_risk_probability
true_root_cause
scenario_id
scenario_name
```

---

# 10. Future ML Availability / 未来机器学习可用性

Every field must be documented with one of the following semantic availability classes. The implementation does not need to physically store this label in every row; it must remain part of the canonical documentation and future feature contract.

| Class | Meaning |
|---|---|
| `ORDER_CREATION` | Known when the customer order is created |
| `PRE_PRODUCTION` | Known before production starts |
| `DURING_PRODUCTION` | Becomes available only after the event has actually occurred |
| `POST_OUTCOME_ONLY` | Known only after completion/delivery; unsafe for early prediction |

### Examples

| Field | Availability | Future ML rule |
|---|---|---|
| `product_id` | `ORDER_CREATION` | Safe |
| `order_quantity` | `ORDER_CREATION` | Safe |
| `priority` | `ORDER_CREATION` | Safe |
| `promised_delivery_at` | `ORDER_CREATION` | Safe |
| planned work-order dates | `PRE_PRODUCTION` | Safe after planning |
| open purchase orders | `PRE_PRODUCTION` / event-dependent | Use only if existing at as-of time |
| `actual_receipt_at` | `DURING_PRODUCTION` | Use only after receipt event |
| inspection result | `DURING_PRODUCTION` | Use only after inspection |
| rework event | `DURING_PRODUCTION` | Use only after rework starts |
| `actual_end_at` | `POST_OUTCOME_ONLY` for early prediction | Prohibited before completion |
| final delivery time | `POST_OUTCOME_ONLY` | Target/outcome only |

---

# 11. Time Semantics / 时间语义

- Business event timestamps are timezone-aware.
- Synthetic business schedules are generated using the `Asia/Shanghai` business timezone.
- Persisted timestamps should be normalized through the database/ORM as timezone-aware values.
- Week 2 must not use the wall-clock current time to determine generated business outcomes.
- `generated_at` is a technical metadata timestamp and must not influence deterministic business-content hashing.
- Future As-of Date logic must use event availability, not final outcome data.

---

# 12. Synthetic Dataset Profiles / 合成数据配置

The four-month plan requires a 12–18 month dataset with 8,000–20,000 orders, 20–50 products, and 15–30 suppliers for the project dataset. Week 2 freezes three profiles to make local tests and CI practical.

| Profile | Business Coverage | Orders | Products | Materials | Suppliers | Customers | Work Centers |
|---|---:|---:|---:|---:|---:|---:|---:|
| `test` | 3 months | 150 | 12 | 25 | 8 | 15 | 4 |
| `ci` | 6 months | 800 | 20 | 50 | 12 | 30 | 6 |
| `demo` | 18 months | 12,000 | 30 | 80 | 24 | 60 | 8 |

These are synthetic project assumptions, not real enterprise counts.

---

# 13. Deterministic Generation Contract / 可复现生成契约

A canonical dataset is determined by:

```text
generator_version
+ profile
+ seed
+ scenario_configuration
```

Required property:

```text
same inputs → same canonical business content → same content_hash
```

Requirements:

- one explicit seeded random generator is passed through generation modules;
- no hidden global random state;
- stable generation order;
- stable IDs;
- canonical sort order before hashing/export;
- technical `generated_at` excluded from `content_hash`;
- scenario configuration participates in deterministic generation;
- different seed should produce a different content hash in normal cases.

Recommended fixed demo seed:

```text
20260824
```

---

# 14. Hidden Ground Truth Scenarios / 隐藏业务事件

Ground Truth scenarios are **probabilistic interventions**, not labels written directly onto operational rows.

## 14.1 Scenario A — Supplier Performance Degradation

**ID:** `SCN_SUPPLIER_DEGRADATION`

```text
Supplier reliability ↓
→ Late material receipt ↑
→ Material availability ↓
→ Production waiting ↑
→ Cycle time ↑
→ Delivery delay ↑
```

Initial synthetic assumptions:

- affected suppliers: 2;
- affected critical materials: 5;
- active period: approximately business months 5–8 of the demo dataset;
- late-receipt probability: baseline + 25 percentage points;
- additional receipt delay: 3–8 business days.

Expected directional effects in same-seed baseline-vs-injected comparison:

- affected supplier on-time performance decreases;
- affected material late receipts increase;
- downstream production waiting / delivery-delay signals increase.

---

## 14.2 Scenario B — Quality Deterioration

**ID:** `SCN_QUALITY_DETERIORATION`

```text
Quality stability ↓
→ Inspection failure ↑
→ Rework ↑
→ Production cycle time ↑
→ Delivery delay ↑
```

Initial synthetic assumptions:

- affected product models: 2;
- affected constrained production/assembly work center: 1;
- active period: approximately business months 9–11;
- inspection-failure probability: about 2.2× relevant baseline;
- rework probability after eligible failures: +30 percentage points;
- rework duration: +20% to +50% relative to baseline rework duration.

Expected directional effects:

- inspection failure increases for affected entities;
- rework frequency/duration increases;
- affected cycle-time and delay signals worsen.

---

## 14.3 Scenario C — Production Load Surge

**ID:** `SCN_CAPACITY_SURGE`

```text
Order volume ↑
→ Work-center load ↑
→ Queue time ↑
→ WIP ↑
→ Cycle time ↑
→ Delivery delay ↑
```

Initial synthetic assumptions:

- affected constrained work centers: 2;
- active period: approximately business months 13–15;
- relevant order-arrival volume: +50%;
- affected queue-time multiplier: approximately 1.7× baseline.

Expected directional effects:

- target work-center queue/load signals increase;
- WIP / elapsed production time increase;
- downstream delay signal increases.

---

# 15. Hidden Ground Truth Isolation Contract / 隐藏真相隔离契约

## Runtime-safe public manifest

Recommended:

```text
data/synthetic/dataset_manifest.json
```

Allowed fields:

- dataset version;
- seed;
- generator version;
- profile;
- period;
- row counts;
- content hash;
- generation/config metadata that does not reveal scenario truth.

It must not contain:

- scenario IDs or names;
- affected supplier/product/work-center identities;
- root-cause labels;
- expected causal chain;
- evaluation answers.

## Hidden manifest

Required path:

```text
data/hidden_ground_truth/scenario_manifest.yaml
```

Only test/evaluation tooling may read this file.

The following runtime components must not import, mount, read, parse, or expose it:

- API;
- worker runtime;
- analytics runtime;
- future ML runtime;
- future RAG runtime;
- future LLM/orchestration runtime.

Week 2 must include an implementation-level guard demonstrating that application package code does not depend on `data/hidden_ground_truth/`.

`.dockerignore` or equivalent build-context protection should prevent hidden ground truth from being copied into runtime images.

---

# 16. Data Quality Contract / 数据质量契约

## 16.1 Referential Integrity

Required orphan count: **0**.

At minimum:

- sales order → customer exists;
- sales order → product exists;
- BOM → product/material exists;
- purchase order → supplier/material exists;
- work order → sales order/product exists;
- operation → work order/work center exists;
- material requirement → work order/material exists;
- inventory snapshot → material exists;
- inspection → work order exists;
- optional inspection operation → operation exists;
- rework → inspection/work order/work center exists;
- delivery → sales order exists.

---

## 16.2 Temporal Integrity

At minimum:

```text
sales_order.order_at < sales_order.promised_delivery_at

purchase_order.ordered_at < purchase_order.promised_receipt_at
purchase_order.actual_receipt_at IS NULL
  OR purchase_order.actual_receipt_at >= purchase_order.ordered_at

work_order.planned_start_at < work_order.planned_end_at
work_order.actual_start_at IS NULL
  OR work_order.actual_end_at IS NULL
  OR work_order.actual_start_at <= work_order.actual_end_at

operation.planned_start_at < operation.planned_end_at
operation.actual_start_at IS NULL
  OR operation.actual_end_at IS NULL
  OR operation.actual_start_at <= operation.actual_end_at

quality_inspection.inspection_at >= related work_order.actual_start_at
  when the work order has started

rework.rework_start_at >= related inspection.inspection_at
rework.rework_start_at <= rework.rework_end_at

delivery.delivery_at >= related sales_order.order_at
```

---

## 16.3 Quantity Integrity

At minimum:

```text
sales_order.order_quantity > 0

purchase_order.ordered_quantity > 0
0 <= purchase_order.received_quantity <= purchase_order.ordered_quantity

work_order.planned_quantity > 0
0 <= work_order.completed_quantity <= work_order.planned_quantity

material_requirement.required_quantity > 0

inventory_snapshot.on_hand_quantity >= 0
0 <= inventory_snapshot.reserved_quantity <= inventory_snapshot.on_hand_quantity

inspection.inspected_quantity > 0
inspection.passed_quantity + inspection.failed_quantity
  = inspection.inspected_quantity

rework.rework_quantity > 0
rework.rework_quantity <= related inspection.failed_quantity

delivery.delivered_quantity > 0
cumulative delivery quantity <= related order quantity
```

---

## 16.4 Reproducibility Integrity

Required:

- same profile + seed + generator version + scenario config → same content hash;
- repeated database load must not silently duplicate the active dataset;
- `generated_at` must not change content hash;
- row ordering must not change content hash;
- generator must expose dataset version and seed in the public manifest.

---

## 16.5 Scenario Integrity

Scenario acceptance must use **same-seed baseline versus injected datasets**, not single-row labels.

Required comparisons:

### Supplier scenario

- affected supplier on-time performance decreases;
- affected material late-receipt frequency/delay increases.

### Quality scenario

- affected inspection-failure rate increases;
- affected rework frequency or rework time increases.

### Capacity scenario

- affected work-center queue/load signal increases;
- affected WIP / production elapsed-time signal increases.

Scenario tests must tolerate stochastic variation while remaining deterministic under the fixed seed.

---

# 17. Week 2 Deliverables / 第二周交付

The Week 2 implementation must ultimately produce:

```text
docs/03_data_contracts.md
docs/sprints/W02_industrial_data_foundation.md

SQLAlchemy manufacturing models
Alembic Week 2 migration(s)
Synthetic data generator
Dataset profiles
Dataset/public manifest
Hidden scenario manifest
Scenario injection modules
Data-quality validation
Data-quality report
Unit tests
PostgreSQL integration tests
CI seed/data-quality smoke
```

---

# 18. Explicit Week 2 Non-goals / Week 2 明确不做

Do not implement:

- On-Time Delivery metric;
- Delay Rate;
- Cycle Time metric;
- WIP analytics;
- Material Availability metric;
- Supplier On-Time Rate;
- FPY;
- Rework Rate;
- Analytics API;
- Plotly business charts;
- Streamlit business dashboard;
- feature engineering;
- ML training/inference;
- embeddings;
- vector retrieval;
- RAG;
- LLM API calls;
- agent orchestration;
- LangChain;
- LangGraph;
- real ERP/MES integration;
- predictive maintenance;
- computer vision;
- a second database or message broker.

---

# 19. Contract Conflict Policy / 契约冲突规则

If implementation reveals that a contract is technically impossible, inconsistent, or insufficient:

1. stop the affected implementation path;
2. report the exact conflict;
3. show the minimal proposed contract change;
4. do not silently change the schema or business semantics;
5. require explicit approval before continuing.

---

# 20. Contract Freeze Statement / 契约冻结声明

This document is the Week 2 data-semantic source of truth.

When committed together with `docs/sprints/W02_industrial_data_foundation.md`, Week 2 may transition to:

```text
WEEK 2 CONTROL CONTRACTS FROZEN
IMPLEMENTATION STATUS: NOT STARTED
CODEX READINESS: READY FOR IMPLEMENTATION
```

Week 2 is **not complete** merely because this contract is frozen.
