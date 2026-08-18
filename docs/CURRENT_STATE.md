# FlowLens Industrial AI — Current State / 当前状态
**Last Updated / 最后更新:** 2026-08-18

**Sprint / Sprint:** Week 2 — Industrial Data Foundation

**Current Project Phase / 当前阶段:** WEEK 2 IN PROGRESS

**Implementation Status / 工程实现状态:** IN PROGRESS

**Codex Readiness / Codex 开发就绪:** READY FOR W02-C04-DE IMPLEMENTATION AUTHORIZATION

**Week 1 Baseline / Week 1 基线:** CLOSED / VERIFIED

> Important / 重要：Week 1 remains CLOSED / VERIFIED, and the Week 2 Data Contract and Sprint Spec remain frozen. W02-C01, W02-C02, and W02-C03 are CLOSED / VERIFIED. W02-C04-A is CLOSED / VERIFIED / GITHUB SYNCHRONIZED. W02-C04-BC established and R1-hardened the verified scenario foundation; C04-D/E/F/G/H have NOT started. Persistence and data-quality engineering also remain unimplemented. Week 2 must **not** be described as COMPLETE. / Week 1 保持 CLOSED / VERIFIED，Week 2 Data Contract 与 Sprint Spec 保持冻结。W02-C01、W02-C02 与 W02-C03 已 CLOSED / VERIFIED。W02-C04-A 已 CLOSED / VERIFIED / GITHUB SYNCHRONIZED。W02-C04-BC 已建立并完成 R1 加固及验证；C04-D/E/F/G/H 尚未开始。持久化和数据质量工程也尚未实现。不得将 Week 2 描述为 COMPLETE。

---

## 1. 当前已冻结内容 / Frozen Control-State Decisions

### Product / 产品

**中文**

- 项目：FlowLens Industrial AI
- 行业域：High-voltage Electrical Equipment Manufacturing inspired scenario
- 首个纵向场景：Production Delivery Intelligence
- Primary User：Production / Delivery Operations Manager
- 核心问题：Why are production orders delayed, and how can data and AI support earlier intervention?
- 决策问题：How can an operations manager identify delivery-risk signals early enough to decide where investigation or intervention should begin?

**English**

- Project: FlowLens Industrial AI
- Domain: high-voltage electrical equipment manufacturing inspired scenario
- First vertical: Production Delivery Intelligence
- Primary user: Production / Delivery Operations Manager
- Core question: Why are production orders delayed, and how can data and AI support earlier intervention?
- Decision question: How can an operations manager identify delivery-risk signals early enough to decide where investigation or intervention should begin?

---

## 2. 已冻结文档 / Frozen Documents

Current control documents:

- `docs/00_project_charter.md`
- `docs/01_scope.md`
- `docs/02_architecture.md`
- `docs/03_data_contracts.md`
- `docs/sprints/W02_industrial_data_foundation.md`
- `AGENTS.md`

Historical closed sprint specification:

- `docs/sprints/W01_project_foundation.md`

**中文**

当前控制文档冻结 Week 2 的业务目标、数据契约、范围、架构边界和工程执行规则。Week 1 Sprint Spec 作为已关闭 Sprint 的历史证据保留。Codex 不得为了实现方便静默修改这些约束。

**English**

The current control documents freeze the Week 2 business goal, data contract, scope, architecture boundaries, and engineering execution rules. The Week 1 Sprint Spec remains as historical evidence for the closed sprint. Codex must not silently alter these constraints for implementation convenience.

---

## 3. 历史实现里程碑 / Historical Implementation Milestones

Week 1 was delivered through seven reviewed, linear checkpoints:

1. `8a762c1` — Python engineering baseline
2. `1bb9980` — PostgreSQL, pgvector, SQLAlchemy, and Alembic foundation
3. `7eb6c06` — FastAPI runtime, database-aware health endpoint, and worker placeholder
4. `6260198` — GitHub Actions quality gate
5. `337e0b2` — Week 1 acceptance record
6. `13a9de1` — pre-merge health, migration-safety, and Compose corrections
7. `5f06774` — CI environment-isolation correction

---

## 4. 最终验收能力 / Final Accepted Week 1 Capabilities

- Python 3.12 project foundation
- uv dependency locking
- canonical environment-backed Settings
- PostgreSQL 17 infrastructure
- pgvector availability and extension enablement
- SQLAlchemy engine, session, and connectivity foundation
- Alembic migration foundation
- FastAPI application runtime
- database-aware `/health` contract
- brokerless long-running worker placeholder
- Docker Compose development runtime
- unit testing
- real PostgreSQL integration testing
- Ruff
- strict mypy
- GitHub Actions quality gate

One-command startup and repeatable quality checks are verified.

---

## 5. Week 1 未实现能力 / Week 1 Non-Capabilities

Week 1 does **not** include:

- manufacturing domain schemas
- manufacturing business entities
- synthetic industrial data
- manufacturing metrics
- analytics
- dashboards
- feature engineering
- machine learning
- embeddings
- vector search
- semantic retrieval
- RAG
- LLM integration
- prompts
- agents
- LangChain
- LangGraph
- Redis
- Celery
- Kafka
- RabbitMQ
- ERP integration
- MES integration
- production deployment
- continuous deployment

pgvector is infrastructure-only. Its presence does **not** mean that embedding,
vector-search, semantic-search, retrieval, or RAG functionality exists.

---

## 6. 最终验收与合并证据 / Final Acceptance and Merge Evidence

### Implementation Merge / 实现合并

- Implementation PR: `#2`
- PR status: `MERGED`
- Final reviewed feature SHA: `5f06774c67e691ed5838f81d6d949818470e2b83`
- Final exact-SHA PR CI: workflow `CI`, run `31889122831`, run #7, `success`
- Week 1 implementation merge commit: `254c713dda8e921deed9b27cb6d17555ca4ddf8c`
- Post-merge main CI: workflow `CI`, run `31889922557`, run #8, `success`

### Final Quality State / 最终质量状态

| Quality gate / 质量门 | Result / 结果 |
|---|---|
| Docker Compose configuration validation | PASS |
| PostgreSQL 17 runtime | PASS |
| pgvector availability and enablement | PASS |
| Online Alembic migration | PASS |
| Integration pytest | PASS — 4 passed, 0 failed, 0 skipped |
| Full pytest | PASS — 23 passed, 0 failed |
| Ruff | PASS |
| Strict mypy | PASS |
| uv lock verification | PASS |
| Final exact-SHA PR CI | PASS |
| Post-merge main CI | PASS |

**WEEK 1 STATUS:** `CLOSED`

**IMPLEMENTATION STATUS:** `COMPLETE`

**POST-MERGE VERIFICATION:** `PASS`

---

## 7. Known Limitations / 已知限制

- MINOR: FastAPI TestClient currently emits a third-party Starlette/httpx
  deprecation warning; test correctness is unaffected.
- INFORMATIONAL: In the Codex Windows host, Docker Compose Build/Bake can emit
  a session-header warning when the workspace path contains non-ASCII
  characters. Compose configuration and startup are verified, and the same
  repository quality gate passed independently on GitHub-hosted Ubuntu.
- INFORMATIONAL: The Codex sandbox could not write its local pytest cache;
  tests still executed and passed.

---

## 8. W01-H01 Compose CI Hardening / Compose CI 硬化

**Status:** `PASS`

A dedicated GitHub Actions job now performs a full Docker Compose smoke gate:
it validates Compose configuration, builds the API and Worker images, starts
PostgreSQL/API/Worker, waits with bounded readiness checks, verifies the exact
database-backed `/health` contract, confirms that the Worker remains running,
captures service diagnostics on failure, and always tears down containers and
volumes.

The same path passed locally against an isolated Compose project, including
pgvector enablement, online Alembic migration, database integration tests, the
full pytest suite, Ruff, strict mypy, and uv lock verification. GitHub Actions
CI run `31931161755` (run #11) passed both `Quality gate` and
`Docker Compose smoke` for implementation commit
`0fba880f20daba160140885b87fe344e8544efc0`. No Week 2 business or AI
capability is introduced by this hardening task.

---

## 9. Week 2 Control-State Transition / 第二周控制状态切换

**WEEK 2 STATUS:** `CONTROL CONTRACTS FROZEN`

**IMPLEMENTATION STATUS:** `NOT STARTED`

**CODEX READINESS:** `READY FOR IMPLEMENTATION`

**WEEK 1 BASELINE:** `CLOSED / VERIFIED`

Frozen contracts:

- `docs/03_data_contracts.md`
- `docs/sprints/W02_industrial_data_foundation.md`

The next authorized engineering work is Week 2 Industrial Data Foundation implementation under those frozen contracts.

Authorized future Week 2 work includes:

- SQLAlchemy manufacturing metadata/models;
- Alembic manufacturing schema;
- deterministic synthetic-data generation;
- dataset profiles/versioning;
- three approved scenario injectors;
- Hidden Ground Truth isolation;
- data-quality validation;
- Week 2 tests and CI validation.

No Week 2 implementation capability is claimed by this control-state transition itself.

Week 3 Analytics remains unauthorized until Week 2 is implemented, reviewed, accepted, and closed.

---

## 10. Gate 状态 / Gate Status

**Current Gate:** W02-C04-BC — Integrated Scenario Foundation
**Status:** `CLOSED / VERIFIED`

**W02-G0:** `PASS`

The Week 2 data contract, Sprint Spec, scope boundaries, scenario definitions,
Hidden Ground Truth isolation rules, and acceptance criteria are frozen.

**W02-C04-A:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04 Scenario Inventory:** `FROZEN — 3 FAMILIES`

**W02-C04-BC:** `IMPLEMENTED / R1 HARDENED / VERIFIED`

**W02-C04-BC-R1 Targeted ChatGPT Re-review:** `PASS`

**W02-C04-BC Final Closeout:** `AUTHORIZED`

**W02-C04-D/E/F/G/H:** `NOT STARTED`

**Next Engineering Checkpoint:** W02-C04-DE — SUPPLIER + QUALITY SCENARIO IMPLEMENTATION

**C04-DE Implementation:** `NOT STARTED`

C04-DE requires separate explicit implementation authorization. Week 3
remains unauthorized.

---

## 11. W02-C01 SQLAlchemy Domain Foundation / SQLAlchemy 领域基础

**Status:** `CLOSED / VERIFIED`

W02-C01 established and verified:

- one canonical SQLAlchemy 2.x declarative `Base`;
- one canonical `Base.metadata` object;
- explicit Alembic-compatible naming rules for `ix`, `uq`, `ck`, `fk`, and `pk`;
- the public `from flowlens.data import Base` capability boundary;
- Alembic `target_metadata` identity with `Base.metadata`;
- side-effect-free data-boundary import behavior;
- preservation of the Week 1 `0001_enable_pgvector` migration as `head`;
- an empty canonical metadata table collection pending W02-C02.

Closeout evidence on 2026-08-17:

- Codex implementation verification: `PASS`;
- ChatGPT Contract / Scope / Architecture / Source Review: `PASS`;
- human closeout authorization: `APPROVED`;
- full pytest with PostgreSQL: `PASS — 28 passed, 0 failed, 0 skipped`;
- PostgreSQL integration pytest: `PASS — 4 passed`;
- Ruff, strict mypy, uv lock, Docker Compose configuration, and Alembic checks: `PASS`.

**W02-C02 Status:** `CLOSED / VERIFIED`

**W02-C03 Status:** `CLOSED / VERIFIED`

**Next Engineering Checkpoint:** W02-C04-B IMPLEMENTATION AUTHORIZATION

W02-C04 implementation remains not started and requires explicit W02-C04-B
implementation authorization.

---

## 12. W02-C02 Canonical Manufacturing Schema + Alembic / 制造 Schema 与 Alembic

**Status:** `CLOSED / VERIFIED`

W02-C02 established the frozen Week 2 physical-schema baseline:

- 16 canonical tables;
- 130 frozen columns;
- 16 primary keys;
- 34 foreign keys;
- 3 explicit unique constraints;
- 45 explicitly named check constraints;
- one canonical SQLAlchemy `Base.metadata` shared with Alembic;
- migration chain `0001_enable_pgvector` → `0002_industrial_data_foundation`;
- verified upgrade, downgrade to Week 1, and re-upgrade behavior while preserving pgvector.

C03 populates this canonical schema rather than redesigning it. Synthetic
business schedules must use `Asia/Shanghai` with timezone-aware persistence.
Cross-table temporal and quantity rules remain mandatory W02-C05 data-quality
validation responsibilities.

**W02-C03 Status:** `CLOSED / VERIFIED`

**Next Engineering Checkpoint:** W02-C04-B IMPLEMENTATION AUTHORIZATION

**W02-C04 Status:** `NOT STARTED`

**W02-C04 Readiness:** `CONTRACT FROZEN — READY FOR IMPLEMENTATION AUTHORIZATION`

W02-C04 implementation requires separate explicit W02-C04-B authorization.

---

## 13. W02-C03 Deterministic Baseline Generator / 确定性基线生成器

**Status:** `CLOSED / VERIFIED`

W02-C03 established and verified:

- deterministic in-memory baseline synthetic industrial data generation;
- frozen `test`, `ci`, and `demo` profiles;
- stable deterministic identifiers and row ordering;
- deterministic business-row counting and canonical SHA-256 content hashing;
- timezone-aware `Asia/Shanghai` business timestamps;
- a coherent order-to-delivery manufacturing digital thread;
- master-policy-based, time-causal initial inventory;
- time-causal weekly-bucket procurement using only eligible known demand;
- compatibility with the frozen C02 PostgreSQL schema and Alembic head
  `0002_industrial_data_foundation`.

W02-C03-R1 repaired and verified temporal causality for initial inventory and
procurement. Focused generation tests, PostgreSQL compatibility, the full test
suite, Ruff, strict mypy, dependency-lock verification, and Docker Compose
configuration all passed during final closeout.

Accepted non-blocking limitations:

- `GeneratedDataset` contains mutable SQLAlchemy ORM rows, so caller mutation
  after generation can stale the stored content hash;
- no fixed cross-process golden hash fixture exists yet;
- procurement remains a simplified deterministic weekly-bucket synthetic
  baseline rather than full MRP or requirement-level PO allocation.

**W02-C04 Status:** `NOT STARTED`

**Next Engineering Checkpoint:** W02-C04-B IMPLEMENTATION AUTHORIZATION

---

## 14. W02-C04-A Scenario Contract Freeze / 场景契约冻结

**W02-C04 Entry Gate:** `REVIEWED`

**Original Entry-Gate Result:** `CONDITIONAL — CONTRACT CLARIFICATION REQUIRED`

**ChatGPT Contract Resolution:** `ACCEPTED`

**Entry-Gate Contract Gaps:** `RESOLVED BY W02-C04-A`

**W02-C04-A Status:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

W02-C04-A froze:

- exactly three scenario families: supplier degradation, quality
  deterioration, and capacity surge;
- full detached baseline cloning and deterministic scenario identity;
- canonical scenario re-finalization and hash recomputation;
- aware `Asia/Shanghai` scenario windows and temporal-causality rules;
- supplier, quality, and capacity downstream propagation semantics;
- the HGT schema, deterministic identity/hash, protected serialization, and
  label-leakage prohibitions;
- the C04/C05 and Analytics/ML/RAG/LLM/Agent boundaries.

Control decisions:

```text
C02 schema change: NO
New Alembic migration: NO
New Python dependency: NO
Authorized scenario families: 3
```

No C04 Python implementation, tests, or HGT manifest exist at this checkpoint.

**W02-C04 Foundation Status:** `SEE W02-C04-BC CLOSEOUT BELOW`

---

## 15. W02-C04-BC Integrated Scenario Foundation / 集成场景基础

**W02-C04-BC:** `IMPLEMENTED / R1 HARDENED / VERIFIED`

**W02-C04-BC-R1 Targeted ChatGPT Re-review:** `PASS`

**W02-C04-BC Final Closeout:** `AUTHORIZED`

Verified foundation guarantees:

- exactly three frozen scenario families;
- typed immutable scenario configuration and aware `Asia/Shanghai` windows;
- one canonical deterministic SHA-256 scenario identity contract;
- HGT semantic and cryptographic binding to validated scenario configuration;
- complete detached baseline cloning with independent ORM instrumentation;
- canonical scenario reordering, recounting, rehashing, and new
  `DatasetVersion` finalization;
- full baseline immutability and `generated_at` identity/hash isolation;
- unchanged C03 deterministic generation regression behavior.

Implementation state:

```text
W02-C04-D: NOT STARTED
W02-C04-E: NOT STARTED
W02-C04-F: NOT STARTED
W02-C04-G: NOT STARTED
W02-C04-H: NOT STARTED
```

Accepted remaining limitations:

- finalized `GeneratedDataset` instances contain mutable detached ORM rows, so
  caller mutation after finalization can stale the stored content hash;
- protected HGT file serialization remains deferred to W02-C04-G;
- PostgreSQL scenario compatibility verification remains deferred to W02-C04-H.

**Next Engineering Checkpoint:** W02-C04-DE — SUPPLIER + QUALITY SCENARIO IMPLEMENTATION

**C04-DE Implementation:** `NOT STARTED`
