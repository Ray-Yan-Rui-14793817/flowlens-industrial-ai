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

# 15A. W02-C04 Deterministic Scenario Transformation Contract

This section freezes the W02-C04 engineering contract. C04 is an in-memory,
deterministic transformation layer with this dependency direction:

```text
C02 canonical schema
        ↓
C03 deterministic baseline
        ↓
C04 deterministic scenario transformation
        ↓
Scenario Dataset + separate Hidden Ground Truth
```

C04 scenario logic must remain separate from
`src/flowlens/data/generation/generator.py`. Business-data persistence remains
deferred to W02-C05.

## 15A.1 Frozen scenario inventory

C04 implements exactly these three scenario families:

1. `SCN_SUPPLIER_DEGRADATION`
2. `SCN_QUALITY_DETERIORATION`
3. `SCN_CAPACITY_SURGE`

No additional scenario family is authorized in C04.

## 15A.2 Baseline immutability and scenario dataset identity

C04 must never mutate or share mutable SQLAlchemy ORM row instances with the
input C03 `GeneratedDataset`. It must:

- fully detach/copy the complete business-row graph;
- copy `DatasetVersion` metadata separately;
- share neither ORM rows nor SQLAlchemy instrumentation state;
- transform only the cloned graph;
- finalize a new scenario dataset.

The input baseline must remain canonical-content identical before and after
`apply_scenario(...)`.

A scenario output must not reuse the baseline `dataset_version_id`. Its
scenario namespace is the lowercase SHA-256 digest of a canonical identity
payload containing:

```text
baseline_dataset_version_id
scenario_type
scenario_version
scenario_seed
canonical scenario configuration
```

The scenario dataset identifier is:

```text
dsv_<first 32 lowercase hexadecimal characters of scenario namespace>
```

Every cloned business row references that new dataset identifier.
Scenario-only rows use deterministic identifiers derived from the scenario
namespace and stable ordinals or stable source identities. Comparable
baseline-derived entity IDs may remain unchanged when no new entity is
created. UUID4, wall-clock identity, system entropy, database defaults, and
mutable global counters are prohibited.

For the scenario `DatasetVersion`:

- `dataset_version_id`: new deterministic scenario identifier;
- `seed`: preserve the baseline generation seed;
- `generator_version`: preserve the baseline generator version;
- `profile`, `period_start`, `period_end`: preserve baseline values;
- `generated_at`: technical provenance only and excluded from scenario
  selection, scenario/HGT identity, business content, and hashes;
- `content_hash`: recompute from finalized scenario business rows;
- `row_count_total`: recompute from finalized scenario business rows.

Scenario labels and HGT must not be stored by overloading C02 metadata columns.

## 15A.3 Canonical finalization

The mandatory finalization flow is:

```text
baseline
→ full detached clone
→ deterministic intervention
→ required cross-table coherence propagation
→ canonicalize_rows()
→ recompute row_count_total
→ canonical_content_hash()
→ construct new DatasetVersion
→ construct scenario GeneratedDataset-compatible result
→ attach separate Hidden Ground Truth to ScenarioResult
```

C04 reuses the C03 canonicalization/hash convention. A transformed dataset may
never retain the baseline `content_hash`.

## 15A.4 Window, eligibility, determinism, and temporal causality

Every scenario window is an aware `Asia/Shanghai` interval:

```text
[window_start, window_end)
```

`window_start` is inclusive, `window_end` is exclusive, and
`window_start < window_end`. Both boundaries must lie inside the baseline
business period. Invalid windows are rejected, not clamped.

Scenario month N begins at `Asia/Shanghai` 00:00 on
`add_calendar_months(period_start, N - 1)`. Default DEMO windows are:

- supplier degradation: `[month_5_start, month_9_start)`;
- quality deterioration: `[month_9_start, month_12_start)`;
- capacity surge: `[month_13_start, month_16_start)`.

Shorter profiles must receive an explicit valid window or reject the default.

Primary eligibility timestamps are:

- supplier: `purchase_order.ordered_at`;
- quality: `quality_inspection.inspection_at`;
- capacity: `sales_order.order_at`.

Facts strictly before scenario eligibility remain unchanged. Opening inventory
is unchanged by every scenario. Downstream consequences may extend beyond
`window_end` when their source intervention became eligible inside the window.
Later events must not alter earlier selection or outcomes through shared RNG
consumption.

Selection is independent from C03 RNG state:

1. build semantically eligible candidates;
2. sort by stable primary identifier;
3. rank/select using SHA-256 over scenario identity plus entity/event identity;
4. transform in stable order.

Per-entity hash-derived values are preferred. A scenario-local RNG is allowed
only when necessary, seeded from canonical scenario identity and consumed in
stable order. C03 RNG state must never be continued or consumed.

## 15A.5 Supplier degradation

Frozen default configuration:

```text
affected_supplier_count = 2
affected_critical_material_count = 5
late_probability_delta = 0.25
additional_delay_business_days_min = 3
additional_delay_business_days_max = 8
```


### 15A.5.1 Critical-material semantics and supplier-first target graph

`Material.criticality` is the authoritative entity-level classification. A
Supplier Degradation material is critical exactly when:

```text
Material.criticality IN ("HIGH", "CRITICAL")
```

`ProductMaterial.is_critical` is a BOM-edge consistency attribute, not a
second material classification. A BOM edge used for downstream impact must
agree with the authoritative classification; a contradiction rejects the
affected candidate graph rather than being silently repaired.

Build eligible supplier/material edges from baseline PurchaseOrders whose
`ordered_at` is in `[window_start, window_end)`, whose supplier, material,
`actual_receipt_at`, and `promised_receipt_at` exist, and whose material is
authoritatively critical and participates in at least one real baseline
BOM/material-requirement chain. An edge exists only when at least one such PO
exists for that supplier/material pair.

Selection is supplier first, material second:

1. Rank candidate suppliers independently by the full canonical scenario
   identity, purpose `supplier-target`, and `supplier_id`; sort by
   `(hash, supplier_id)` and select exactly `affected_supplier_count`.
2. From materials joined by actual eligible PO edges to a selected supplier,
   rank independently with purpose `supplier-material-target` and
   `material_id`; sort by `(hash, material_id)` and select exactly
   `affected_critical_material_count`.
3. The final graph contains every actual eligible PO edge whose supplier and
   material endpoints are both selected. It is not a fabricated Cartesian
   product.

Every selected supplier and material must have at least one final edge. The
relevant PO population is exactly the eligible PO rows on this final graph.
Insufficient candidates or a disconnected selected node rejects the scenario.

### 15A.5.2 Business-day arithmetic

For `add_business_days(timestamp, N)`, `N` is a positive integer, the starting
calendar day does not count, and counting begins on the next day. Monday
through Friday count; Saturday and Sunday do not. Week 2 models no public
holiday calendar, Chinese statutory holidays, or substitute working weekends.
The calculation preserves aware `Asia/Shanghai` semantics and the original
local wall-clock time. For example, Friday 18:00 plus one business day is
Monday 18:00; plus three is Wednesday 18:00; Saturday 18:00 plus one is Monday
18:00. No calendar dependency is authorized.

### 15A.5.3 Late-rate materialization

A relevant baseline PO is late exactly when:

```text
actual_receipt_at > promised_receipt_at
```

Status does not define lateness. Let `N` be the relevant final-graph PO count
and `L0` its baseline-late count. Using exact `Decimal`-compatible arithmetic:

```text
p0 = L0 / N
p1 = min(1, p0 + late_probability_delta)
L1 = min(N, ceil(N * p1))
K  = max(0, L1 - L0)
```

Existing late POs remain late. Create exactly `K` additional late outcomes.
This observed baseline is authoritative; C03 private probability tuning,
binary-float decisions, C03 RNG continuation, and wall-clock entropy are
prohibited.

### 15A.5.4 Late-event and delay selection

Potential new-late candidates are relevant baseline non-late POs. A candidate
is materializable only when at least one integer `D` in the configured
inclusive delay range satisfies:

```text
add_business_days(baseline_actual_receipt_at, D) > promised_receipt_at
```

Rank candidates independently with purpose `supplier-late-event` and
`purchase_order_id`; select exactly the first `K` by `(hash,
purchase_order_id)`. For each selected PO, find the smallest configured
`D_min_effective` that makes it late, derive a separate SHA-256 value with
purpose `supplier-delay-days`, map it uniformly onto the inclusive integer
interval `[D_min_effective, additional_delay_business_days_max]`, and set:

```text
scenario_actual_receipt_at =
    add_business_days(baseline_actual_receipt_at, D)
```

Preserve quantities and status unless the minimum C02 coherence adjustment is
required; no fabricated `LATE` status is permitted. Fewer than `K`
materializable candidates rejects rather than underfilling or widening the
configured range.

### 15A.5.5 Shortage transition and exact actual-chain propagation

There is intentionally no MaterialRequirement-to-PurchaseOrder FK. A newly
created shortage exists for each matching link satisfying:

```text
material_requirement.material_id == purchase_order.material_id
AND baseline_actual_receipt_at <= material_requirement.need_by_at
AND scenario_actual_receipt_at > material_requirement.need_by_at
```

`need_by_at` is the shortage eligibility threshold, not the production shift
anchor. For an affected work order, both `actual_start_at` and `actual_end_at`
must exist. Collect every scenario-delayed receipt causing such a transition
for one of its material requirements and calculate:

```text
required_material_available_at = MAX(scenario_actual_receipt_at)
causal_shift = max(
    timedelta(0),
    required_material_available_at - work_order.actual_start_at,
)
```

Multiple shortages collapse to this single maximum availability boundary;
never sum them or use `scenario_receipt - need_by_at` as the shift. If
`causal_shift > 0`, shift by exactly that same duration the work-order actual
start/end, every operation actual start/end, all inspections for the work
order, both timestamps of its existing reworks, and all deliveries for the
associated sales order. Preserve durations, ordering, relative spacing,
planned timestamps, quantities, master data, opening inventory, pre-window
facts, and unrelated work orders. An affected chain without complete actual
work-order timing rejects.

### 15A.5.6 Supplier HGT causal-chain contract

The only Supplier relationship strings are:

```text
degrades_purchase_order_receipt
creates_material_shortage
sets_work_order_material_delay
shifts_operation_actual_window
shifts_inspection_time
shifts_existing_rework_window
shifts_delivery_time
```

Create exactly the applicable actual-effect links:

- selected `dim_supplier` → each changed `fact_purchase_order`:
  `degrades_purchase_order_receipt`;
- each changed PO → every `fact_material_requirement` whose receipt crosses
  `need_by_at`: `creates_material_shortage`, including non-binding shortages;
- each binding maximum-availability material requirement → its shifted
  `fact_work_order`: `sets_work_order_material_delay`; include every exact
  tie, only when `causal_shift > 0`;
- shifted work order → each actually shifted `fact_operation`:
  `shifts_operation_actual_window`;
- shifted work order → each actually shifted `fact_quality_inspection`:
  `shifts_inspection_time`;
- shifted work order → each actually shifted baseline-derived `fact_rework`:
  `shifts_existing_rework_window`;
- shifted work order → each actually shifted `fact_delivery`:
  `shifts_delivery_time`.

Supplier Degradation never creates Rework rows. Selected materials are already
represented in HGT targets and the real PO relationship; no redundant
Material-to-PO causal edge is recorded.

## 15A.6 Quality deterioration

Frozen default configuration:

```text
affected_product_count = 2
affected_work_center_count = 1
failure_probability_multiplier = 2.2
rework_probability_delta = 0.30
rework_duration_multiplier_min = 1.2
rework_duration_multiplier_max = 1.5
```


### 15A.6.1 Work-center-first product target graph

Start from inspections whose `inspection_at` is in `[window_start,
window_end)`. Resolve the product through inspection → work order →
`product_id`. Resolve work center from the referenced operation when
`operation_id` is present, requiring that operation to belong to the same work
order. When it is absent, use the final valid operation for the work order:
highest `sequence_number`, with `operation_id` as deterministic tie-break. An
unresolvable inspection is not materializable and is excluded; an insufficient
remaining population rejects.

Each resolved inspection contributes one actual `(product_id,
work_center_id)` edge. Rank work centers first with purpose
`quality-work-center-target`, sort by `(hash, work_center_id)`, and select
exactly `affected_work_center_count`. Then rank products connected by an actual
eligible edge to a selected work center with purpose `quality-product-target`,
sort by `(hash, product_id)`, and select exactly `affected_product_count`.
The final graph contains every eligible inspection whose resolved product and
work center are both selected, never a Cartesian product. Every selected node
must occur on a final edge.

### 15A.6.2 Relevant baseline and failure target

The relevant population is exactly the final graph's eligible inspections.
A coherent baseline failure has `result == "FAIL"` and
`failed_quantity > 0`; a coherent PASS has `result == "PASS"` and
`failed_quantity == 0`. Reject incoherent input rather than reinterpret it.

Let `N` be the relevant inspection count and `F0` the baseline FAIL count.
Using exact Decimal-compatible arithmetic:

```text
pf0 = F0 / N
pf1 = min(1, pf0 * failure_probability_multiplier)
F1  = min(N, ceil(N * pf1))
KF  = max(0, F1 - F0)
```

Existing FAIL events remain FAIL. Rank relevant PASS inspections independently
with purpose `quality-failure-event` and `inspection_id`, and select exactly
`KF`. `F0 == 0`, insufficient PASS rows, or an empty population rejects. C03's
private global failure tuning is never a C04 baseline.

### 15A.6.3 PASS-to-FAIL mutation

For every selected PASS inspection set:

```text
failed_quantity = 1
passed_quantity = inspected_quantity - 1
result = "FAIL"
```

Choose defect category and severity independently per inspection using
separate SHA-256 values with purposes `quality-defect-category` and
`quality-severity`. Allowed existing operational vocabularies are:

```text
defect_category: DIMENSIONAL, SURFACE, ASSEMBLY, ELECTRICAL
severity: LOW, MEDIUM, HIGH
```

### 15A.6.4 Rework probability and selection

A relevant baseline FAIL inspection is reworked when at least one baseline
Rework references its `inspection_id`. Let `R0` be the number of such unique
baseline FAIL inspections and:

```text
pr0 = R0 / F0
pr1 = min(1, pr0 + rework_probability_delta)
FS  = resulting relevant FAIL count
R1  = min(FS, ceil(FS * pr1))
KR  = max(0, R1 - existing_rework_count_among_resulting_failures)
```

Rank resulting FAIL inspections without existing rework independently with
purpose `quality-rework-event` and `inspection_id`; select exactly `KR`.
Insufficient candidates reject. C03's private rework tuning is prohibited.

### 15A.6.5 Existing and new affected Rework rows

Every baseline Rework is in the scenario-affected existing set exactly when it
references an inspection in the final selected graph/window, that inspection
is a coherent baseline FAIL, and the Rework belongs to the same work order.
Every such row receives duration deterioration; the set is not limited to
newly converted failures or an arbitrary subset. Reworks outside this set are
unchanged.

For each newly required Rework, create exactly one row for the selected
resulting FAIL inspection. Use its `inspection_id` and `work_order_id`; use the
resolved inspection operation's work center or the same final-valid-operation
fallback as target-graph construction. Set `rework_quantity` equal to
`failed_quantity`. Choose from the existing operational reasons, independently
with purpose `quality-rework-reason`:

```text
SYNTHETIC_DIMENSIONAL_ADJUSTMENT
SYNTHETIC_ASSEMBLY_CORRECTION
SYNTHETIC_SURFACE_REFINISH
```

The start is `inspection_at` plus a deterministic whole-hour offset from the
inclusive range 1–6, selected with purpose `quality-rework-start`.

### 15A.6.6 Scenario-created Rework identity

Existing baseline-derived Rework IDs remain unchanged. A new Rework ID is
determined by its selected inspection and the full 64-character scenario
namespace; no ordinal, position, counter, C03 ID factory, RNG, UUID, database
sequence, or wall clock is authorized.

Construct this exact logical payload:

```json
{
  "inspection_id": "<selected inspection_id>",
  "purpose": "scenario-rework-id",
  "scenario_namespace": "<full 64-character canonical scenario namespace>"
}
```

Serialize with `json.dumps(payload, ensure_ascii=True, separators=(",", ":"),
sort_keys=True)`, UTF-8 encode it, and calculate the lowercase SHA-256
hexadecimal digest. The final identifier is:

```text
rework_id = "rw_" + digest[:45]
len(rework_id) == 48
```

At most one new Rework exists per selected inspection. A collision with any
existing Rework ID rejects explicitly; no suffix, ordinal, or rehash repair is
allowed. Input order, unrelated inspections, and `generated_at` cannot change
the ID; scenario namespace or inspection identity may change it.

### 15A.6.7 Rework duration

For an affected existing Rework preserve `rework_start_at`. Its baseline
duration is `rework_end_at - rework_start_at`. Select a multiplier
independently with purpose `quality-rework-duration` from the configured
inclusive Decimal range at 0.01 resolution. The default discrete set is 1.20,
1.21, ..., 1.50. Round the multiplied duration upward to a whole second and
set:

```text
scenario_rework_end_at = rework_start_at + new_duration
```

For a new Rework, use the median valid baseline Rework duration in the final
selected quality graph as its reference, using the arithmetic mean of the two
middle durations when the count is even, then apply the same multiplier and
rounding rule. No valid reference duration rejects; no global duration or C03
private duration generation may be substituted.

### 15A.6.8 Work-order completion and delivery propagation

For each affected work order:

```text
required_rework_completion_at =
    MAX(rework_end_at across its scenario-affected reworks)
```

When this exceeds baseline `work_order.actual_end_at`, set actual end to that
timestamp. Do not move actual start, planned timestamps, or operations: quality
is a post-inspection effect. With no scenario-affected Rework, timing is
unchanged.

For the associated sales order, sort deliveries by `(delivery_at,
delivery_id)`. If no delivery precedes the required completion, leave all
unchanged. Otherwise calculate `delivery_shift =
required_rework_completion_at - earliest_delivery_at` and shift every delivery
by that same duration, preserving order, spacing, and quantities.

### 15A.6.9 Quality HGT causal-chain contract

The only Quality relationship strings are:

```text
degrades_quality_inspection
extends_existing_rework_duration
creates_scenario_rework
extends_work_order_completion
shifts_delivery_time
```

Create exactly the applicable actual-effect links:

- resolved selected `dim_work_center` → each inspection actually converted
  PASS-to-FAIL: `degrades_quality_inspection`;
- relevant inspection → each existing Rework whose duration actually
  increases: `extends_existing_rework_duration`; the source inspection may be
  unchanged;
- selected resulting FAIL inspection → its new canonical R2 Rework:
  `creates_scenario_rework`, exactly once per new Rework;
- each Rework tying at the maximum required completion and extending the
  baseline work-order actual end → that `fact_work_order`:
  `extends_work_order_completion`; non-binding shorter Reworks are excluded;
- extended work order → every actually shifted delivery:
  `shifts_delivery_time`.

### 15A.6.10 Shared deterministic failure and HGT semantics

All entity/event choices use the full canonical scenario identity and a
distinct stable purpose. At minimum the purposes are `supplier-target`,
`supplier-material-target`, `supplier-late-event`, `supplier-delay-days`,
`quality-work-center-target`, `quality-product-target`,
`quality-failure-event`, `quality-defect-category`, `quality-severity`,
`quality-rework-event`, `quality-rework-start`, `quality-rework-reason`, and
`quality-rework-duration`. Construct semantic candidates, deduplicate by
stable primary identity, compute hashes independently per entity, sort by
`(hash, stable_primary_id)`, and select the required cardinality. List
position, mutable counters, shared RNG, C03 RNG, database/iteration order, and
wall-clock entropy are prohibited.

Every probability-to-count conversion uses exact arithmetic and mathematical
ceiling. Any insufficient graph/population or inability to materialize the
configured count exactly rejects; do not reduce counts, widen windows, select
unrelated entities, change configuration/schema, or import private C03 tuning.

HGT target identities are stable sorted unions: selected suppliers plus
selected critical materials for Supplier, and selected products plus selected
work centers for Quality. No table-name prefixes are added. HGT
`affected_entities_by_table` includes only rows whose business-semantic fields
actually change or that are newly created; clone-only `dataset_version_id`
replacement, canonicalization, metadata/hash/count recomputation, and selected
target dimensions do not make a row affected. Supplier keys may be
`fact_purchase_order`, `fact_work_order`, `fact_operation`,
`fact_quality_inspection`, `fact_rework`, and `fact_delivery`; Quality keys may
be `fact_quality_inspection`, `fact_rework`, `fact_work_order`, and
`fact_delivery`. IDs are unique and stable sorted.

`CausalLink` uses only applicable canonical physical table names from
`dim_supplier`, `dim_material`, `dim_product`, `dim_work_center`,
`fact_purchase_order`, `fact_material_requirement`, `fact_work_order`,
`fact_operation`, `fact_quality_inspection`, `fact_rework`, and
`fact_delivery`. Add links only for the frozen actual relationships above, not
for cloning, selection bookkeeping, generic FK edges, or eligible/selected but
unchanged rows. Unchanged rows may be sources only where explicitly authorized.
Relationship tokens are exact, lowercase, case-sensitive API values; no
synonyms are allowed. Build a semantic set and rely on immutable HGT
deduplication/sorting, never insertion order.

Every modified Supplier PO and PASS-to-FAIL inspection is the target of
exactly one root link. Every new Rework exists in scenario business rows and
the affected map and is the target of exactly one
`creates_scenario_rework` link. Every causal target that is a changed/new row
appears in the affected map, and no causal ID may reference a nonexistent
entity.

Target IDs, affected maps, every CausalLink table/entity field, and the exact
relationship token participate in canonical HGT hashing. `generated_at` does
not. Reordering input rows cannot change the causal set or `hgt_hash`.
Scenarios are independently applied to the original C03 baseline and never
stacked.

Always preserve inspection quantity balance, PASS/FAIL coherence,
`rework_quantity <= failed_quantity`, valid rework chronology, and every C02
constraint. Operational fields may contain legitimate failure/rework facts,
but never scenario, root-cause, anomaly, affected, evaluation, or expected
causal-answer labels. HGT remains separate from business rows.

## 15A.7 Capacity surge

Frozen default configuration:

```text
affected_work_center_count = 2
arrival_volume_multiplier = 1.5
queue_time_multiplier = 1.7
```

### 15A.7.1 Target graph and exact baseline population

Baseline Sales Order window eligibility is determined exclusively by
`fact_sales_order.order_at` in the aware `Asia/Shanghai` half-open interval
`[window_start, window_end)`. A baseline Sales Order is an arrival candidate
only when it has an actual canonical WorkOrder/Operation path and at least one
linked Operation references an eligible Work Center.

Candidate Work Centers are exactly the distinct Work Centers referenced by
Operations reachable from those candidate Sales Orders. Unused master-data
Work Centers and synthetic candidates are prohibited. Rank candidate
`work_center_id` values independently using the full scenario namespace,
purpose `capacity-work-center`, and the ID; sort by `(hash, work_center_id)`
and select exactly `affected_work_center_count`. Insufficient candidates,
duplicates, clamping, or fallback selection reject the scenario.

After selection, a baseline Sales Order belongs to the selected Capacity graph
exactly when:

- its `order_at` is in the scenario window;
- at least one Operation on one of its actual Work Orders references a selected
  Work Center; and
- it contains a reusable canonical thread consisting of the Sales Order, at
  least one Work Order, at least one Operation, every Material Requirement
  owned by the reused Work Order graph, at least one Quality Inspection
  required by the source thread, and at least one Delivery. Rework is optional.

The authoritative baseline arrival population is:

```text
N = count(distinct qualifying baseline sales_order_id)
```

`N == 0` rejects. `N` is never derived from quantities or from counts of Work
Orders, Operations, Work Centers, Material Requirements, or Deliveries.

### 15A.7.2 Added arrivals and source templates

Capacity arrival volume creates additional Sales Order rows; it never scales
the quantity of an existing or new order. Using exact Decimal-compatible
arithmetic and mathematical ceiling:

```text
added_order_count = ceil(N * (arrival_volume_multiplier - 1))
```

A negative result rejects rather than clamps. Existing Sales Order quantities
remain unchanged, and row-count increase plus quantity scaling is prohibited.

Rank the `N` qualifying source Sales Orders independently using the full
scenario namespace, purpose `capacity-arrival-template`, and baseline
`sales_order_id`; sort by `(hash, sales_order_id)` to form the stable sequence
`S[0], ..., S[N-1]`. For zero-based added-arrival ordinal `i`:

```text
source_order = S[i mod N]
```

Each new Sales Order copies all non-identity business attributes from its real
source template, including customer, product, quantity, priority, status, and
promised-delivery semantics. Its `order_at` is exactly the source
`sales_order.order_at`, so it remains inside the scenario window. Shared
timestamps are valid; deterministic IDs break ties. Input row order, arbitrary
master-data selection, private C03 tuning, and C03 RNG continuation are not
permitted.

### 15A.7.3 Complete scenario-only thread and initial chronology

Every added Sales Order clones the complete owned canonical source topology:

```text
SalesOrder
→ WorkOrder(s)
→ Operation(s)
→ MaterialRequirement(s)
→ QualityInspection(s)
→ optional Rework(s)
→ Delivery row(s)
```

Work Order count, Operation count, routing, Work Center assignment, sequence,
Material Requirement structure, inspection structure, optional Rework
structure, Delivery structure, and all business quantities are copied exactly.
Do not perform a second BOM explosion, invent routing or Work Centers, or use
private C03 RNG. Baseline Purchase Orders are not cloned; dedicated
supplemental procurement follows Section 15A.7.5.

Before queue intervention, every planned and actual timestamp in the new
thread equals its corresponding source timestamp. Customer promise timestamps
remain unchanged after intervention. A source template or scenario input that
cannot supply the complete required thread or the completion anchors required
below rejects explicitly.

### 15A.7.4 Scenario-created identity and C02 compatibility

For every scenario-created row, construct the exact semantic payload below,
serialize it with `json.dumps(payload, ensure_ascii=True,
separators=(",", ":"), sort_keys=True)`, UTF-8 encode it, and calculate the
lowercase SHA-256 hexadecimal digest. The payload's fixed `purpose` value is
the purpose separator. The canonical digest algorithm is common; only the
persisted prefix and schema-compatible digest truncation are entity-specific.

```text
SalesOrder:
{"arrival_ordinal": i,
 "purpose": "capacity-sales-order",
 "scenario_namespace": scenario_namespace,
 "source_sales_order_id": source_sales_order_id}

WorkOrder:
{"purpose": "capacity-work-order",
 "scenario_namespace": scenario_namespace,
 "scenario_sales_order_id": scenario_sales_order_id,
 "source_work_order_id": source_work_order_id}

Operation:
{"purpose": "capacity-operation",
 "scenario_namespace": scenario_namespace,
 "scenario_work_order_id": scenario_work_order_id,
 "source_operation_id": source_operation_id}

MaterialRequirement:
{"purpose": "capacity-material-requirement",
 "scenario_namespace": scenario_namespace,
 "scenario_work_order_id": scenario_work_order_id,
 "source_material_requirement_id": source_material_requirement_id}

PurchaseOrder:
{"purpose": "capacity-supplemental-purchase-order",
 "scenario_material_requirement_id": scenario_material_requirement_id,
 "scenario_namespace": scenario_namespace,
 "supplier_id": supplier_id}

QualityInspection:
{"purpose": "capacity-quality-inspection",
 "scenario_namespace": scenario_namespace,
 "scenario_work_order_id": scenario_work_order_id,
 "source_inspection_id": source_inspection_id}

Rework:
{"purpose": "capacity-rework",
 "scenario_inspection_id": scenario_inspection_id,
 "scenario_namespace": scenario_namespace,
 "source_rework_id": source_rework_id}

Delivery:
{"purpose": "capacity-delivery",
 "scenario_namespace": scenario_namespace,
 "scenario_sales_order_id": scenario_sales_order_id,
 "source_delivery_id": source_delivery_id}
```

The persisted identity matrix is frozen as follows:

| Entity | PK | Prefix | Digest characters | Final length | C02 PK capacity | Referencing FK capacity | Result |
|---|---|---:|---:|---:|---:|---:|---|
| SalesOrder | `sales_order_id` | `so_` | 37 | 40 | 40 | 40 | PASS |
| WorkOrder | `work_order_id` | `wo_` | 37 | 40 | 40 | 40 | PASS |
| PurchaseOrder | `purchase_order_id` | `po_` | 37 | 40 | 40 | N/A | PASS |
| Operation | `operation_id` | `op_` | 45 | 48 | 48 | 48 | PASS |
| MaterialRequirement | `material_requirement_id` | `mr_` | 45 | 48 | 48 | N/A | PASS |
| QualityInspection | `inspection_id` | `qi_` | 45 | 48 | 48 | 48 | PASS |
| Rework | `rework_id` | `rw_` | 45 | 48 | 48 | N/A | PASS |
| Delivery | `delivery_id` | `dl_` | 45 | 48 | 48 | N/A | PASS |

The 40-character representations are exactly `so_ + digest[:37]`, `wo_ +
digest[:37]`, and `po_ + digest[:37]`. The 48-character representations are
the applicable prefix plus `digest[:45]`. Do not globally reduce IDs to 40
characters or alter the separately frozen Quality scenario Rework identity.

Every collision with an existing or already generated ID is an explicit
rejection. UUIDs, Python `hash()`, wall-clock or `generated_at` input, random
suffixes, silent regeneration, payload mutation, input-order-dependent
ordinals, and C03 RNG are prohibited. Business rows and HGT use the identical
persisted identities.

### 15A.7.5 Dedicated supplemental procurement

Opening inventory and every baseline Purchase Order remain unchanged. Every
scenario-created Material Requirement receives exactly one dedicated
scenario-only supplemental Purchase Order; new demand never steals or
reallocates baseline supply. The supplemental ordered and received quantities
both equal that Material Requirement's `required_quantity`, with no weekly
bucket or cross-requirement aggregation.

The decision time is the scenario Sales Order's `order_at`. A supplier is
eligible exactly when the baseline dataset contains an actual historical
Purchase Order for the same `material_id` whose `ordered_at <= decision_time`.
Rank distinct eligible `supplier_id` values independently using the full
scenario namespace, purpose `capacity-supplemental-supplier`, and supplier ID;
sort by `(hash, supplier_id)` and select the first. No eligible supplier
rejects.

For each supplemental Purchase Order:

```text
material_id          = scenario MaterialRequirement.material_id
ordered_at           = decision_time
promised_receipt_at  = scenario MaterialRequirement.need_by_at
actual_receipt_at    = scenario MaterialRequirement.need_by_at
ordered_quantity     = scenario MaterialRequirement.required_quantity
received_quantity    = scenario MaterialRequirement.required_quantity
status               = "RECEIVED"
```

`need_by_at` must be strictly later than decision time or the scenario
rejects. Capacity adds no Supplier Degradation intervention, and baseline
Purchase Orders are never modified.

### 15A.7.6 Queue population, delay, and operation propagation

An Operation in the scenario dataset is queue-eligible exactly
when its Work Center is selected, its Sales Order belongs to the selected graph
(including a scenario-created arrival), and its pre-intervention
`actual_start_at` is in `[window_start, window_end)`. Baseline-derived cloned
and scenario-created Operations are both eligible. Pre-window Operations are
immutable for this queue intervention.

For each queue-eligible Operation:

```text
baseline_planned_operation_duration = planned_end_at - planned_start_at
additional_queue_delay =
    ceil_to_whole_seconds(
        baseline_planned_operation_duration
        * (queue_time_multiplier - 1)
    )
```

Missing or non-positive planned duration, a negative queue delay, or missing
actual timestamps required for propagation rejects. Do not derive the delay
from actual runtime. The delay is inserted immediately before execution:
planned timestamps remain fixed, while both `actual_start_at` and
`actual_end_at` move by the same accumulated delay. Operation duration is
unchanged; stochastic rounding and wall-clock behavior are prohibited.

Within each Work Order, process Operations in canonical
`(sequence_number, operation_id)` order while maintaining cumulative queue
delay. When a queue-eligible Operation is reached, add its own delay before shifting
that Operation. Every later Operation receives the accumulated delay; a later
queue-eligible Operation adds its own delay first. Already-late Operations use the
same additive rule, with no clamping to planned or promised times.

### 15A.7.7 Work Order and downstream temporal propagation

After Operation propagation, recompute each participating Work Order:

```text
actual_start_at = min(resulting Operation.actual_start_at)
actual_end_at   = max(resulting Operation.actual_end_at)
WORK_ORDER_COMPLETION_DELTA =
    resulting actual_end_at - pre-intervention actual_end_at
```

Planned Work Order timestamps remain unchanged unless required solely to
preserve an already-frozen C02 invariant. A Work Order without computable
Operation bounds or a required pre-intervention completion anchor rejects.
Shift each linked Quality Inspection `inspection_at` and each linked Rework
`rework_start_at` and `rework_end_at` by that Work Order's nonzero completion
delta. Preserve event durations, relative ordering, and all planned fields.

Delivery has only `sales_order_id`, so individual Work Order deltas are never
added independently. For every affected Sales Order:

```text
PRE_ORDER_COMPLETION_AT =
    max(pre-intervention actual completion of every owned Work Order
        in the cloned/selected graph)

POST_ORDER_COMPLETION_AT =
    max(resulting actual completion of every owned Work Order
        after queue propagation and Work Order bound recomputation)

ORDER_COMPLETION_DELTA =
    POST_ORDER_COMPLETION_AT - PRE_ORDER_COMPLETION_AT

scenario_delivery_at =
    baseline_or_cloned_delivery_at + ORDER_COMPLETION_DELTA
```

Apply `ORDER_COMPLETION_DELTA` exactly once to every Delivery owned by the
Sales Order. All such Deliveries receive the same delta, preserving their
relative order. Do not sum Work Order deltas, shift once per Work Order, or use
the maximum individual delta in place of the order-level completion anchors.
Multiple Work Orders are valid. A negative order delta or a participating
Sales Order without at least one computable Work Order completion anchor
rejects. When `ORDER_COMPLETION_DELTA == 0`, Delivery timestamps remain
unchanged and no delivery-shift business effect is recorded. Customer
`promised_delivery_at` remains unchanged.

### 15A.7.8 Targets and affected entities

Capacity never mutates Work Center master fields. HGT `target_entity_ids` is
exactly the stable sorted selected `work_center_id` set. Products, Customers,
Sales Orders, and Work Orders are not automatically targets.

Dataset-version-only differences never make a row affected. Every
scenario-created business row is affected. A baseline-derived row is affected
only when a Capacity intervention changes a business-semantic field. The exact
affected-table allowlist is:

```text
fact_sales_order
fact_work_order
fact_operation
fact_material_requirement
fact_purchase_order
fact_quality_inspection
fact_rework
fact_delivery
```

`dim_work_center` is not affected. IDs within each table are unique and stable
sorted.

### 15A.7.9 Capacity HGT causal-chain contract

The only Capacity relationship strings are:

```text
receives_added_sales_order_arrival
creates_work_order
creates_operation
creates_material_requirement
creates_supplemental_procurement
creates_quality_inspection
creates_rework
creates_delivery
adds_operation_queue_delay
shifts_downstream_operation
shifts_work_order_completion
shifts_inspection_time
shifts_rework_window
shifts_delivery_time
```

Construct a semantic edge set and canonicalize it through the existing HGT
path; insertion and input order never define output. Emit exactly the
applicable actual-effect links:

- each selected Work Center traversed by a new thread → that scenario Sales
  Order: `receives_added_sales_order_arrival`, once per actual pair;
- scenario Sales Order → each owned scenario Work Order:
  `creates_work_order`, once per created Work Order;
- scenario Work Order → each owned scenario Operation:
  `creates_operation`, once per created Operation;
- scenario Work Order → each owned scenario Material Requirement:
  `creates_material_requirement`, once per created Material Requirement;
- scenario Material Requirement → its dedicated supplemental Purchase Order:
  `creates_supplemental_procurement`, exactly once;
- for each scenario Quality Inspection whose `operation_id` is non-null, its
  corresponding scenario Operation → the inspection; otherwise its
  corresponding scenario Work Order → the inspection:
  `creates_quality_inspection`, exactly once per created inspection;
- scenario Quality Inspection → each owned scenario Rework:
  `creates_rework`, once per created Rework;
- scenario Sales Order → each owned scenario Delivery:
  `creates_delivery`, once per created Delivery;
- selected Work Center → each queue-eligible Operation at that center whose
  `additional_queue_delay > 0`: `adds_operation_queue_delay`, exactly once;
  emit none when its own `additional_queue_delay == 0`;
- each directly delayed Operation → each later Operation whose actual timing
  changes from that source Operation's accumulated delay contribution:
  `shifts_downstream_operation`, once per actual causal pair;
- the single canonical causally binding Operation defined below → each Work
  Order whose completion changes: `shifts_work_order_completion`, exactly once
  per shifted Work Order;
- each shifted Work Order → each linked inspection whose time moves:
  `shifts_inspection_time`, once per actual pair;
- each shifted Work Order → each linked Rework whose window moves:
  `shifts_rework_window`, once per actual pair;
- each Work Order whose completion changes and whose Sales Order has a nonzero
  `ORDER_COMPLETION_DELTA` → each of that order's shifted Deliveries:
  `shifts_delivery_time`, once per actual pair. These causal edges do not
  reapply or multiply the single order-level timestamp delta.

For `creates_quality_inspection`, Operation is the canonical parent whenever
the scenario inspection's `operation_id` is non-null; Work Order is the sole
fallback when it is null. Never emit both, use a baseline parent when the
scenario-side parent exists, or select by iteration order. A missing canonical
scenario parent or a parent that cannot participate consistently in the
affected/HGT graph rejects.

For a Work Order whose resulting completion differs from its pre-intervention
completion, build the binding candidate set from its Operations whose
resulting `actual_end_at` equals the recomputed Work Order completion and whose
actual timing changed because of Capacity propagation. One candidate is
selected directly. For multiple candidates, select the final one by the
already-frozen `(sequence_number, operation_id)` order, equivalently the
maximum canonical tuple. Emit exactly one selected scenario Operation → Work
Order `shifts_work_order_completion` edge. Emit none when completion is
unchanged; a changed completion without a qualifying binding Operation
rejects.

Every causal source and target resolves either in
`affected_entities_by_table` or, only for a selected unchanged Work Center, in
`target_entity_ids`. Do not add generic FK, cloning, selection-bookkeeping, or
unchanged-row links. Table names, entity IDs, target IDs, affected maps, and
exact case-sensitive relationship tokens participate in canonical HGT hashing.
No relationship string, source fallback, tie rule, cardinality, or ordering is
implementation-defined.

### 15A.7.10 Finalization and immutability

Capacity reuses the single C04-BC canonical row ordering, row count, business
content hash, scenario DatasetVersion identity, HGT identity/hash, and
`ScenarioResult` binding. It does not introduce a second canonicalizer or
hash/identity algorithm. `generated_at` remains excluded from every business,
scenario, and HGT identity/hash.

The original baseline business payload, content hash, row count, and
DatasetVersion ID remain unchanged. Baseline and scenario share no ORM row or
SQLAlchemy instrumentation, and applying the in-memory scenario attaches no
rows to a database session. The accepted limitation remains: finalized
`GeneratedDataset` objects contain mutable detached ORM rows, so caller
mutation after finalization can stale a previously stored hash.

### 15A.7.11 R3 zero-delay queue and HGT semantics

W02-C04-F-AR1 found one residual conflict: the valid
`queue_time_multiplier == 1` yields zero additional queue delay, but the
previous eligibility wording implied a mandatory queue edge even for an
unchanged baseline Operation. W02-C04-F-A-R3 resolves only that conflict.

**R3-D1 — Eligibility is not an effect.** The predicate in Section 15A.7.6
selects candidates for queue transformation. Eligibility alone never makes a
baseline Operation affected, mutated, causally changed, or entitled to an
`adds_operation_queue_delay` edge. The materialized delay determines the
direct queue effect.

**R3-D2 — Positive-delay-only cardinality.** For each queue-eligible Operation
with `additional_queue_delay > 0`, shift its actual start and end by the same
additional delay, include it in affected business rows, and emit exactly one
selected Work Center → Operation `adds_operation_queue_delay` edge. Preserve
the already-frozen cumulative and downstream propagation rules. With
`additional_queue_delay == 0`, that direct intervention leaves actual and
planned timestamps and processing duration unchanged, emits no queue edge,
and does not make an unchanged baseline Operation affected solely through
eligibility. An independently realized upstream propagation effect still
follows Section 15A.7.6; zero own delay cannot fabricate a direct queue edge.
Negative queue delay is prohibited by the frozen configuration domain.

**R3-D3 — Creation differs from queue delay.** A scenario-created Operation
remains affected even with zero queue delay because creation itself is a
business effect. It participates in its frozen creation/digital-thread
topology, but receives no `adds_operation_queue_delay` edge for zero delay.
Row creation effect is not queue delay effect.

**R3-D4 — Targets differ from affected entities.** Selected unchanged Capacity
Work Centers remain the stable sorted `target_entity_ids`, including when
some or all eligible baseline Operations receive zero delay and are absent
from the affected map. Target membership never implies affected membership.

**R3-D5 — Arrival-only configuration.** `arrival_volume_multiplier > 1` with
`queue_time_multiplier == 1` is valid. Create the frozen additional Sales
Orders, complete threads, dedicated supplemental procurement, and applicable
creation/thread edges. Do not emit zero-delay queue edges or queue-derived
temporal-shift edges when no such effect materializes.

**R3-D6 — Queue-only configuration.** `arrival_volume_multiplier == 1` with
`queue_time_multiplier > 1` is valid. It creates zero additional arrival
threads. Qualifying Operations and downstream facts may change under the
frozen queue/temporal rules; HGT records only actually materialized effects.

**R3-D7 — Fully neutral configuration.** Both multipliers equal to `1` remain
valid; do not tighten config validation to avoid this boundary. Subject to
the unchanged target-graph and input-validity gates, Capacity creates zero
new arrival rows, makes zero queue or other business-field mutations, and
emits zero queue edges. No unchanged baseline row becomes affected solely
because it was eligible. Preserve baseline business content; do not normalize
timestamps merely to manufacture a propagation effect. Selected Work Centers
remain valid targets. With no created or mutated business facts, the affected
map is `{}` and the causal chain is empty (`[]` in the canonical payload).
Only tables with actually affected IDs belong in the Capacity affected map;
do not add empty-table placeholders. This uses the existing HGT foundation,
which permits an empty map and chain, and the existing C04 scenario
identity/provenance remains distinct. `generated_at` stays provenance-only.

**R3-D8 — No fake evidence.** Never create zero-duration or eligibility-only
queue edges, synthetic timestamp changes, or fake affected membership to
satisfy edge cardinality. HGT describes realized effects, not candidates.

For fixed inputs, all four arrival/queue combinations use the same frozen
target selection, persisted row IDs, relationship vocabulary, endpoint rules,
and sorted/deduplicated semantic edge set. Their applicable effects uniquely
determine the canonical HGT payload, `hgt_hash`, and `hgt_id`; no alternative
zero-delay edge or affected-membership choice is permitted.

R3 leaves F8-R1 identities, target graph, exact `N`, Work Center selection,
arrival count, template ranking/cycling, copied business attributes, complete
thread cloning, supplemental procurement, queue arithmetic/rounding,
operation ordering, cumulative propagation, Work Order bounds, R2-D1 Delivery
propagation, R2-D2 inspection parent/fallback, R2-D3 binding Operation/tie rule,
and all other Capacity HGT vocabulary/topology unchanged. C02, C03, Supplier,
Quality, and common C04 identity/finalization behavior remain unchanged.

## 15A.8 Hidden Ground Truth schema, identity, and serialization

HGT is not business data. It remains outside C02 tables/models, canonical
business hashing, raw rows, public manifests, and all normal
API/worker/analytics/ML/RAG/LLM runtime paths. The scenario business dataset
must be analyzable without HGT.

The exact Week 2 HGT record schema is:

```text
schema_version
scenario_id
scenario_type
scenario_version
scenario_seed
baseline_dataset_version_id
scenario_dataset_version_id
window_start
window_end
parameters
target_entity_ids
affected_entities_by_table
causal_chain
hgt_id
hgt_hash
```

`schema_version` is an explicit immutable version string. `scenario_id` is the
deterministic scenario identity. `target_entity_ids` is a stable sorted list.
`affected_entities_by_table` maps business table names to stable sorted
affected row IDs. `parameters` contains canonical scenario-specific
configuration. `causal_chain` records deterministic evaluation truth about
actual injected links.

Scenario identity is:

```text
scenario_id = "scn_" + first 32 characters of scenario namespace
```

The canonical HGT base payload contains all HGT fields except `hgt_id` and
`hgt_hash`. Then:

```text
hgt_hash = full lowercase SHA-256 hexadecimal digest of canonical HGT payload
hgt_id = "hgt_" + first 32 characters of hgt_hash
```

`generated_at` participates in none of `scenario_id`, `hgt_id`, `hgt_hash`, or
business `content_hash`.

Normal `apply_scenario(...)` behavior is in-memory and never automatically
writes the protected manifest. An explicitly requested evaluation path may
materialize `data/hidden_ground_truth/scenario_manifest.yaml` as canonical
UTF-8 JSON text, which is valid YAML 1.2. Serialization uses stable key/list
ordering, LF endings, and no wall-clock timestamps. No PyYAML dependency is
authorized.

The following fields remain prohibited in normal C02 business rows:

```text
scenario_id
scenario_name
scenario_type
root_cause
true_root_cause
is_affected
is_anomaly
injected_failure
target_label
expected_causal_chain
affected entity lists
HGT parameters or causal labels
```

### 15A.8.1 G-A2 protected manifest structure and existing-file policy

W02-C04-G-A1 stopped safely on two product decisions: fixed-manifest
cardinality/envelope and existing-file/repeated-write behavior. The following
ChatGPT/human-owned G-A2 decisions resolve those two blockers. They freeze the
future C04-G artifact policy only; no serializer implementation is authorized
by this documentation checkpoint.

**G-A2-D1 — Collection envelope and exact records.** The artifact remains
`data/hidden_ground_truth/scenario_manifest.yaml`. Despite its suffix, its
content is canonical UTF-8 JSON text valid as YAML 1.2, with stable key/list
ordering, LF endings, and no wall-clock timestamps. No PyYAML dependency or
separate YAML serialization implementation is authorized.

The manifest is a deterministic collection, not a single-HGT document. Its
envelope is `{"records": [<complete HGT record>, ...]}` (schematic). The
top-level object contains exactly one product-defined field: `records`.
Each item is one complete finalized HiddenGroundTruth representation containing
exactly the 15 fields listed in Section 15A.8, including `hgt_id` and `hgt_hash`.
Do not add, remove, reinterpret, or recalculate those fields.

Week 2 adds no manifest metadata: no `generated_at`, `created_at`,
`manifest_id`, `manifest_hash`, `writer_version`, `tool_version`, debug
metadata, explanatory text, root-cause text, user labels, or provenance
extensions. `generated_at` remains DatasetVersion provenance and is absent
from both the protected HGT record and HGT semantic identity.

**G-A2-D2 — Record ordering.** Before publication, order `records`
lexicographically by `(scenario_id, hgt_id)`. Ordering must not depend on
invocation order, filesystem order, dictionary insertion order, process hash
seed, wall clock, `generated_at`, machine, working directory, or OS path
separator. Existing HGT canonicalization remains authoritative inside each
record; no second HGT canonicalizer is authorized.

**G-A2-D3 — Writer input.** One explicit writer invocation takes one finalized
HiddenGroundTruth input and safely integrates that record into the protected
collection. Normal `apply_scenario()` never implicitly writes the manifest.
`apply_scenario()` and `ScenarioResult` remain unchanged; scenario
implementations must not become aware of manifest collection management.

**G-A2-D4 — Missing file.** If the protected file is absent, create a manifest
whose `records` collection contains exactly the supplied complete HGT record,
using the frozen canonical serialization rules.

**G-A2-D5 — New record in a valid manifest.** If a valid manifest exists and
the incoming `hgt_id` is absent, preserve every existing valid record, add the
incoming complete record, sort by `(scenario_id, hgt_id)`, deterministically
serialize the entire resulting manifest, and publish that complete manifest.
No earlier record may be silently removed because a later scenario is written.
Supplier followed by Capacity retains both; Capacity followed by Supplier
must produce semantically and byte-wise equivalent canonical manifest content.

**G-A2-D6 — Identical repeated write.** If the same `hgt_id` is present and the
incoming complete HGT record is semantically identical, the operation is
idempotent: no duplicate record, semantic manifest change, identity change,
HGT hash change, or HGT ID change. The writer may avoid rewriting when
canonical bytes are already identical; the mandatory outcome is semantic
idempotence.

**G-A2-D7 — HGT identity collision or inconsistency.** If the same `hgt_id`
exists but the incoming complete record differs in semantic content, reject
without mutating the existing manifest. This is an HGT integrity violation.
Do not replace, mutate, suffix, regenerate, merge fields, create a duplicate,
or automatically assign a different ID.

**G-A2-D8 — Malformed or incompatible existing manifest.** Reject existing
content that is not valid canonical-compatible JSON, lacks the required
top-level `records` collection, contains malformed HGT records or duplicate
conflicting HGT identities, violates the frozen schema, or cannot be safely
interpreted under this contract. Do not automatically migrate, repair, coerce,
or destructively replace it. Failure preserves the original artifact unchanged.

**G-A2-D9 — Non-destructive collection update.** New HGT records never
destructively replace unrelated existing records. This semantic rule is
distinct from publication mechanics: a temporary file, validation, and atomic
filesystem replacement may publish the complete new manifest. Atomic
replacement does not authorize semantic deletion or replacement of existing
HGT records. Detailed temporary-file mechanics remain an engineering choice
subject to these frozen semantics.

**G-A2-D10 — Protected path.** The normal Week 2 path is exactly
`data/hidden_ground_truth/scenario_manifest.yaml`; arbitrary caller-controlled
destinations are not permitted. Protect the authorized artifact root against
path traversal, symlink indirection, and unexpected alternate roots. Never
overwrite source files, baseline or scenario business datasets, repository
code, schema files, or migrations.

**Identity preservation.** Serialize existing finalized HGT without changing
`scenario_id`, the HGT semantic payload, `hgt_hash`, `hgt_id`, DatasetVersion
identity, or business content hashes. Do not recalculate business semantics
or introduce a second HGT identity system. A whole-file checksum computed by
an implementation or external tool is not `hgt_hash`. Week 2 requires no
manifest-level semantic identity system.

**Business/runtime isolation.** The artifact is evaluation-only and remains
outside ordinary ORM facts, public business API payloads, runtime scenario
consumers, API/worker runtime images, baseline/scenario business datasets,
business hashes, and user-visible operational labels. Add no HGT or
intervention labels to business data. `ScenarioResult.ground_truth` remains
logically distinct from `ScenarioResult.dataset`.

**Unchanged implementation boundaries.** C04-G consumes finalized HGT and
must not reopen Supplier, Quality, or Capacity behavior, F8-R1 identities,
R2 propagation, R3 zero-delay semantics, scenario mathematics, affected-entity
semantics, causal relationships, or HGT canonicalization. PostgreSQL is not
required for C04-G implementation or unit acceptance; C04-H is not a
prerequisite. Database-backed scenario acceptance remains C04-H. No C02/C03
change, migration, dependency, or database persistence is authorized.

## 15A.9 Scope boundaries and implementation sequence

C04 may create legitimate raw operational facts but must not materialize
derived delay, supplier, availability, quality, WIP, cycle-time, risk,
prediction, diagnosis, or explanation fields.

C04 remains business-data persistence-neutral. It adds no repository, loader,
save/upsert/replace/duplicate policy, CLI, Data Quality engine, business report
writer, analytics, ML, RAG, LLM, or Agent capability. PostgreSQL is used only
for compatibility/integration testing. The protected HGT artifact is not C05
business persistence.

C02 schema change: **NO**. New migration: **NO**. New dependency: **NO**.

Approved sequence:

1. C04-A — contract freeze and Entry-Gate resolution;
2. C04-B — typed configurations, HGT model, deterministic identity;
3. C04-C — detached cloning and scenario finalization;
4. C04-D — supplier degradation;
5. C04-E — quality deterioration;
6. C04-F — capacity surge and complete added-order propagation;
7. C04-G — HGT serialization/isolation and label-leakage guards;
8. C04-H — PostgreSQL compatibility, directional-effect tests, C03
   regression, and full quality gates.

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
