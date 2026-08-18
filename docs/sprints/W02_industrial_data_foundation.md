# W02 — Industrial Data Foundation / 工业数据基础 Sprint Spec

**Task ID:** `W02-INDUSTRIAL-DATA-FOUNDATION`
**Sprint:** `Week 2`
**Planned Dates / 计划日期:** `2026-08-24 → 2026-08-30`
**Stage / 阶段:** `DESCRIBE`
**Status / 状态:** `FROZEN FOR CODEX IMPLEMENTATION`
**Owner Model / 协作模型:** `ChatGPT defines → Codex implements → ChatGPT reviews → Human approves`

---

## 1. Business Goal / 业务目标

### 中文

建立可复现的高压电气离散制造 Synthetic Industrial Dataset，使 FlowLens 后续能够在同一套可信数据语义上完成：

- Manufacturing Analytics；
- Operations Dashboard；
- Delivery Risk Prediction；
- Evidence-Grounded Investigation。

Week 2 的价值不是“生成大量随机数据”，而是建立一条可追踪的 **Order-to-Delivery Digital Thread**，并通过隐藏的概率场景制造真实可调查的运营异常。

### English

Build a reproducible synthetic high-voltage electrical-equipment manufacturing dataset that provides a stable semantic foundation for later analytics, delivery-risk prediction, and evidence-grounded investigation.

Week 2 must create a coherent Order-to-Delivery digital thread rather than unrelated random tables.

---

## 2. Technical Goal / 技术目标

Implement the frozen Week 2 data contract defined in:

```text
docs/03_data_contracts.md
```

Required engineering capabilities:

- SQLAlchemy manufacturing models;
- canonical SQLAlchemy metadata;
- Alembic manufacturing-domain migration;
- deterministic synthetic-data generator;
- `test`, `ci`, and `demo` dataset profiles;
- fixed random seed;
- dataset version and generator version;
- stable canonical content hashing;
- scenario injection;
- Hidden Ground Truth isolation;
- referential / temporal / quantity validation;
- data-quality report;
- unit and PostgreSQL integration tests;
- CI data-generation/data-quality smoke.

---

## 3. Product Context / 产品背景

FlowLens Industrial AI is an evidence-grounded Industrial AI Decision Intelligence project for a high-voltage electrical-equipment manufacturing inspired scenario.

First vertical:

> **Production Delivery Intelligence**

Primary user:

> **Production / Delivery Operations Manager**

Core question:

> **Why are production orders delayed, and how can data and AI support earlier intervention?**

Week 2 does not answer that question yet. It creates the data foundation required to answer it deterministically beginning in Week 3.

---

## 4. Mandatory Inputs / Codex 必须读取

Before modifying files, Codex must read in full:

1. `AGENTS.md`
2. `docs/00_project_charter.md`
3. `docs/01_scope.md`
4. `docs/02_architecture.md`
5. `docs/03_data_contracts.md`
6. `docs/CURRENT_STATE.md`
7. `docs/sprints/W01_project_foundation.md`
8. `docs/sprints/W02_industrial_data_foundation.md`

Also inspect the committed Week 1 implementation, migrations, tests, Docker files, CI workflow, package layout, and current branch state.

If these sources conflict, do not guess. Report a contract conflict.

---

## 5. Definition of Ready / 开发就绪条件

Codex implementation may begin only when all are true:

- [ ] Week 1 baseline is closed and verified.
- [ ] Current branch is the authorized Week 2 branch.
- [ ] `docs/03_data_contracts.md` is committed.
- [ ] `docs/sprints/W02_industrial_data_foundation.md` is committed.
- [ ] `AGENTS.md` identifies Week 2 as the current phase.
- [ ] `docs/CURRENT_STATE.md` records `WEEK 2 CONTROL CONTRACTS FROZEN`.
- [ ] Week 2 implementation status is not overstated as complete.
- [ ] data contract, scenarios, isolation rules, and acceptance criteria are frozen.

Expected pre-implementation state:

```text
Sprint: Week 2 — Industrial Data Foundation
Current Project Phase: WEEK 2 CONTROL CONTRACTS FROZEN
Implementation Status: NOT STARTED
Codex Readiness: READY FOR IMPLEMENTATION
Week 1 Baseline: CLOSED / VERIFIED
```

---

# 6. Required Canonical Data Model / 必需数据模型

Codex must implement the approved contract. It must not invent alternative naming without an approved ADR.

Required objects:

```text
dataset_version

dim_product
dim_material
dim_supplier
dim_customer
dim_work_center
bridge_product_material

fact_sales_order
fact_purchase_order
fact_work_order
fact_operation
fact_material_requirement
fact_inventory_snapshot
fact_quality_inspection
fact_rework
fact_delivery
```

Exact grain, fields, types, constraints, semantics, and forbidden derived fields are defined in `docs/03_data_contracts.md`.

---

# 7. Implementation Sequence / 工程执行顺序

Week 2 should be delivered linearly through the following checkpoints.

## W02-C01 — SQLAlchemy Domain Foundation

Required:

- create canonical declarative `Base`;
- add explicit SQLAlchemy naming convention for constraints;
- organize data models within the existing `src/flowlens/data` capability boundary;
- connect Alembic `target_metadata` to the canonical metadata;
- preserve Week 1 database / pgvector foundation;
- add metadata/model import tests.

Do not yet generate synthetic data in this checkpoint.

---

## W02-C02 — Canonical Manufacturing Schema + Alembic

Required:

- implement all approved Week 2 models;
- create Week 2 Alembic revision(s);
- add PK/FK/unique/check/index constraints required by the data contract;
- preserve the Week 1 pgvector migration;
- verify fresh database upgrade to `head`;
- verify downgrade to the Week 1 revision and re-upgrade to `head`;
- add PostgreSQL schema integration tests.

No analytics, ML, or RAG tables.

---

## W02-C03 — Deterministic Baseline Generator

Implement a baseline generator with no hidden disturbance enabled.

Recommended package boundary:

```text
src/flowlens/data/generation/
```

Required capabilities:

- one explicit seeded RNG passed through generator modules;
- stable deterministic identifiers;
- stable generation order;
- `test`, `ci`, `demo` profiles;
- dataset manifest;
- canonical content hash;
- generation of master data, BOM, orders, procurement, inventory, work orders, operations, quality, rework, and delivery;
- no use of wall-clock current time for generated business outcomes.

Generation must follow business dependencies rather than generating unrelated tables independently.

---

## W02-C04 — Scenario Injection + Hidden Ground Truth

Implement exactly the three frozen scenarios:

1. `SCN_SUPPLIER_DEGRADATION`
2. `SCN_QUALITY_DETERIORATION`
3. `SCN_CAPACITY_SURGE`

Requirements:

- scenarios are probabilistic interventions;
- scenario truth does not appear in operational tables;
- public manifest does not expose scenario answers;
- hidden manifest is stored only under:
  `data/hidden_ground_truth/scenario_manifest.yaml`;
- runtime application package code must not read hidden ground truth;
- runtime Docker images must not copy hidden ground truth;
- add isolation tests.

### W02-C04-A — Contract Freeze and Entry-Gate Resolution

**Status:** `CONTRACT FREEZE COMPLETE / VERIFIED`

The W02-C04 Entry-Gate review completed with an original result of
`CONDITIONAL — CONTRACT CLARIFICATION REQUIRED`. W02-C04-A resolves those gaps
and freezes:

- exactly the three scenario families listed above;
- an in-memory C03-baseline-to-C04-scenario transformation boundary;
- full detached baseline cloning with no shared mutable ORM rows;
- deterministic scenario dataset, scenario, and HGT identities;
- reuse of the C03 canonical ordering and SHA-256 business hash convention;
- aware `Asia/Shanghai` `[window_start, window_end)` scenario windows;
- the supplier material/time shortage-overlap association rule;
- the quality inspection/rework propagation rules;
- capacity surge as additional sales-order arrival rows, not quantity scaling;
- deterministic capacity queue pressure and complete added-order threads;
- the separated HGT schema and dependency-free protected serialization;
- label-leakage prohibitions and C04/C05/AI boundaries.

Schema, migration, and dependency decisions:

```text
C02 schema change: NO
New Alembic migration: NO
New Python dependency: NO
```

Approved future sequence:

1. C04-B — typed scenario configurations, HGT model, deterministic identity;
2. C04-C — full detached cloning and scenario finalization;
3. C04-D — supplier degradation;
4. C04-E — quality deterioration;
5. C04-F — capacity surge and complete added-order propagation;
6. C04-G — HGT serialization/isolation and label-leakage guards;
7. C04-H — PostgreSQL compatibility, directional-effect tests, C03
   regression, and full quality gates.

**W02-C04 implementation status:** `NOT STARTED`

**ChatGPT contract resolution:** `ACCEPTED`

**Entry-Gate contract gaps:** `RESOLVED BY W02-C04-A`

**Next checkpoint:** `W02-C04-B IMPLEMENTATION AUTHORIZATION`

---

## W02-C05 — Persistence, CLI, Data Quality, Reports

Provide a documented local workflow such as:

```bash
uv run python -m flowlens.data.cli generate --profile test --seed 20260824
uv run python -m flowlens.data.cli generate --profile ci --seed 20260824
uv run python -m flowlens.data.cli generate --profile demo --seed 20260824
uv run python -m flowlens.data.cli validate
```

Equivalent project commands are acceptable if documented and testable.

Required:

- persist generated data to PostgreSQL;
- prevent silent duplicate dataset loading;
- support documented replacement only in allowed development/test mode if implemented;
- generate public dataset manifest;
- generate machine-readable data-quality report;
- generate human-readable data-quality summary;
- validate all frozen data-quality rules.

Recommended outputs:

```text
data/synthetic/dataset_manifest.json
data/synthetic/data_quality_report.json
data/synthetic/data_quality_report.md
```

Generated bulk data files should not be committed unless explicitly required for the demo. Prefer reproducible generation from code + seed.

---

## W02-C06 — CI, Acceptance, Closeout

Extend quality automation so the Week 2 CI path validates at least:

```text
Alembic upgrade
→ generate CI profile
→ load CI dataset
→ data-quality validation
→ PostgreSQL integration tests
→ full pytest
→ Ruff
→ strict mypy
→ dependency-lock verification
```

If Docker/Compose runtime is changed, existing Week 1 Compose smoke must continue to pass.

Only after all Week 2 checks pass may `docs/CURRENT_STATE.md` transition from implementation-in-progress to acceptance/closed status.

---

# 8. Dataset Profiles / 数据规模

Implement exactly these default profiles unless a contract conflict is approved:

| Profile | Coverage | Orders | Products | Materials | Suppliers | Customers | Work Centers |
|---|---:|---:|---:|---:|---:|---:|---:|
| `test` | 3 months | 150 | 12 | 25 | 8 | 15 | 4 |
| `ci` | 6 months | 800 | 20 | 50 | 12 | 30 | 6 |
| `demo` | 18 months | 12,000 | 30 | 80 | 24 | 60 | 8 |

Default demo seed:

```text
20260824
```

These are synthetic project assumptions, not real enterprise counts.

---

# 9. Scenario Requirements / 场景要求

Scenario details are frozen in `docs/03_data_contracts.md`.

Codex must not replace the scenarios with simpler labels such as:

```text
scenario_id column
root_cause column
is_problem_order flag
```

Those would leak the evaluation answer.

Acceptance is based on deterministic **distributional effects** under same-seed baseline-vs-injected comparison.

---

# 10. Required Data Quality / 必需数据质量

Codex must implement automated checks for:

### Referential integrity

- orphan FK count = 0.

### Temporal integrity

- valid order, purchase, work-order, operation, inspection, rework, and delivery time orderings.

### Quantity integrity

- valid positive/nonnegative quantities;
- inspection pass + fail balance;
- rework cannot exceed related failures;
- cumulative deliveries cannot exceed order quantity.

### Reproducibility

- same generation inputs produce the same canonical content hash.

### Scenario integrity

- expected affected distributions move in the frozen directions when comparing same-seed baseline and injected datasets.

Full rules are defined in `docs/03_data_contracts.md`.

---

# 11. Required Tests / 必需测试

## Unit tests

At minimum:

- deterministic ID behavior;
- same input → same content hash;
- different seed → normally different content hash;
- generator profile configuration;
- BOM-derived material requirements;
- scenario injector deterministic behavior;
- data-quality rule pass/fail tests;
- public manifest excludes Ground Truth;
- runtime code has no Hidden Ground Truth dependency.

## PostgreSQL integration tests

At minimum:

- fresh `alembic upgrade head`;
- expected tables, constraints, and indexes exist;
- downgrade to Week 1 revision and re-upgrade;
- test-profile generation and database load;
- no orphan FKs;
- data-quality validation passes;
- duplicate dataset load is not silently accepted;
- hidden-ground-truth isolation remains intact.

## CI smoke

At minimum:

- generate/load `ci` profile;
- run data-quality validation;
- run integration tests;
- run existing repository quality checks.

---

# 12. Files Allowed to Change / 允许修改范围

Week 2 implementation may change:

```text
AGENTS.md
README.md
.gitignore
.dockerignore
pyproject.toml
uv.lock
docker-compose.yml
.github/workflows/ci.yml

src/flowlens/data/
tests/
migrations/

data/synthetic/
data/hidden_ground_truth/

docs/CURRENT_STATE.md
docs/adr/
```

The following files are frozen control contracts and must not be silently modified by implementation tasks:

```text
docs/00_project_charter.md
docs/01_scope.md
docs/02_architecture.md
docs/03_data_contracts.md
docs/sprints/W01_project_foundation.md
docs/sprints/W02_industrial_data_foundation.md
```

If implementation requires a control-contract change, report a conflict first.

---

# 13. Explicit Non-goals / 非目标

Week 2 must not implement:

- manufacturing metric calculations;
- On-Time Delivery / Delay Rate;
- Cycle Time / WIP analytics;
- Material Availability metric;
- Supplier On-Time Rate;
- FPY / Rework Rate;
- analytics tools or analytics API;
- business charts or dashboard;
- feature engineering;
- Delivery Risk ML;
- model training/inference;
- embeddings;
- vector search;
- RAG;
- LLM API calls;
- prompt engineering;
- agents or LangGraph;
- real ERP/MES integration;
- predictive maintenance;
- computer vision;
- multi-agent architecture;
- Fine-tuning;
- new message broker or microservice architecture.

---

# 14. Known Risks / 已知风险

Codex and ChatGPT review must actively check:

1. over-modeling the manufacturing domain;
2. storing Week 3 metrics inside Week 2 facts;
3. future-information leakage;
4. leaking scenario labels into operational data;
5. scenario effects that are unrealistically perfect;
6. scenario effects too weak to be detected in later analytics;
7. non-determinism caused by system time, unordered iteration, or global randomness;
8. dataset duplication on repeated runs;
9. broken downgrade/upgrade migration path;
10. hidden ground truth included in Docker image or runtime import path;
11. CI becoming impractically slow by using the full demo profile;
12. changes to Week 1 infrastructure that break existing health/Compose gates;
13. status documentation claiming Week 2 complete before actual acceptance.

---

# 15. Acceptance Criteria / 验收标准

Week 2 passes only when all are true:

- [ ] `docs/03_data_contracts.md` remains the implemented canonical contract.
- [ ] all required Week 2 tables exist in PostgreSQL.
- [ ] PK/FK/unique/check constraints required by the contract exist.
- [ ] `alembic upgrade head` succeeds from a clean Week 1-capable database.
- [ ] downgrade to the Week 1 revision and re-upgrade succeeds.
- [ ] `test`, `ci`, and `demo` profiles are implemented.
- [ ] the demo profile covers 18 months and the frozen default scale.
- [ ] same generator version + profile + seed + scenario config produces the same content hash.
- [ ] no orphan foreign keys exist.
- [ ] temporal-integrity checks pass.
- [ ] quantity-integrity checks pass.
- [ ] the three hidden scenarios create the expected directional distribution changes.
- [ ] scenario IDs / true root causes do not exist in operational tables.
- [ ] the public manifest does not reveal Hidden Ground Truth.
- [ ] runtime application code does not read `data/hidden_ground_truth/`.
- [ ] runtime Docker images do not include Hidden Ground Truth.
- [ ] dataset re-loading does not silently duplicate data.
- [ ] PostgreSQL integration tests pass.
- [ ] full pytest passes.
- [ ] Ruff passes.
- [ ] strict mypy passes.
- [ ] dependency lock verification passes.
- [ ] Week 1 `/health` and Compose quality gates remain passing.
- [ ] no Week 3 Analytics, ML, RAG, or LLM feature is introduced.
- [ ] `docs/CURRENT_STATE.md` accurately reflects actual status.
- [ ] known limitations are documented.

---

# 16. Manual Business Acceptance / 人工业务验收

Before Week 2 is closed, the Product Owner must be able to select a synthetic order and manually trace:

```text
Sales Order
→ Product
→ BOM / Material Requirement
→ Purchase / Inventory
→ Work Order
→ Operations / Work Centers
→ Quality / Rework
→ Delivery
```

The trace must be logically coherent.

Additionally, using the hidden evaluation-only manifest, the Product Owner / evaluation path must be able to verify that:

- supplier deterioration changes downstream operational signals;
- quality deterioration changes inspection/rework signals;
- capacity surge changes work-center load/queue signals.

The production application itself must not be given those answers.

---

# 17. Definition of Done / 完成条件

Week 2 is complete only after:

1. implementation is complete;
2. required automated tests are actually run;
3. CI passes;
4. PostgreSQL integration and migration checks pass;
5. scenario distribution checks pass;
6. Hidden Ground Truth isolation is verified;
7. manual digital-thread acceptance is completed;
8. ChatGPT performs the post-Codex contract review;
9. remaining issues are fixed or documented as accepted limitations;
10. `docs/CURRENT_STATE.md` records the real closed state.

Do not claim completion based on generated files, code appearance, or Codex summary alone.

---

# 18. Codex Return Format / Codex 返回格式

Every Week 2 Codex implementation checkpoint must return:

### 1. Baseline and Branch
- branch;
- starting SHA;
- working-tree state before changes.

### 2. Files Changed
List every changed/created/deleted file.

### 3. Contract Mapping
For each requirement, state where it was implemented.

### 4. Design Decisions
Explain implementation-level decisions only. Do not redefine business contracts.

### 5. Commands Run
Provide exact commands.

### 6. Test and Quality Results
Report exact results for:
- unit tests;
- PostgreSQL integration tests;
- migrations;
- data-quality validation;
- Ruff;
- strict mypy;
- lock verification;
- Compose checks when applicable.

### 7. Acceptance Criteria Status
Mark each relevant criterion:
- `PASS`
- `FAIL`
- `NOT RUN`
- `BLOCKED`

### 8. Hidden Ground Truth Isolation Evidence
Explain how runtime isolation was verified.

### 9. Known Limitations
List remaining limitations.

### 10. Contract Conflicts
If none, write:

```text
None
```

### 11. Recommended Next Step
Recommend the next authorized checkpoint only. Do not jump to Week 3.

---

# 19. Week 2 Closeout State / 完成后的状态

Only after final ChatGPT review and human approval should the repository state become:

```text
Sprint: Week 2 — Industrial Data Foundation
Current Project Phase: WEEK 2 CLOSED
Implementation Status: COMPLETE
Post-Merge Verification: PASS
Week 3 Status: NOT STARTED
```

Before implementation begins, the correct state is:

```text
Sprint: Week 2 — Industrial Data Foundation
Current Project Phase: WEEK 2 CONTROL CONTRACTS FROZEN
Implementation Status: NOT STARTED
Codex Readiness: READY FOR IMPLEMENTATION
Week 1 Baseline: CLOSED / VERIFIED
```
