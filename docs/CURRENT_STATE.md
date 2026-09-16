# FlowLens Industrial AI — Current State / 当前状态
**Last Updated / 最后更新:** 2026-09-16

**Sprint / Sprint:** Week 2 — Industrial Data Foundation

**Current Project Phase / 当前阶段:** WEEK 2 IN PROGRESS

**Implementation Status / 工程实现状态:** IN PROGRESS

**Codex Readiness / Codex 开发就绪:** READY FOR CHATGPT W02-C04-G-A1-R2 FINAL IMPLEMENTATION AUTHORIZATION RE-REVIEW

**Week 1 Baseline / Week 1 基线:** CLOSED / VERIFIED

> Important / 重要：Week 1 and all previously closed Week 2 checkpoints remain verified. W02-C04-F remains CLOSED / VERIFIED / GITHUB SYNCHRONIZED; Capacity Surge remains IMPLEMENTED / CODEX VERIFIED / CHATGPT REVIEWED / HUMAN APPROVED. After G-A2, G-A1-R1 stopped safely on existing identical-duplicate HGT policy. G-A3 records the supplied ChatGPT/human uniqueness decision only; it does not authorize C04-G implementation. C04-G, C04-H, and C05 have NOT started. Week 3 remains NOT AUTHORIZED / NOT STARTED. Current status is in Sections 10 and 23; earlier checkpoint states and next-step labels remain historical records. Week 2 is not COMPLETE. / 历史已关闭检查点及 C04-F 状态保持不变。G-A2 后，G-A1-R1 因现有清单中相同 HGT 重复项策略不明确而安全停止。G-A3 仅记录 ChatGPT/人工批准的身份唯一性决策，不授权 C04-G 实现。C04-G、C04-H、C05 尚未开始；Week 3 尚未授权或开始。当前状态以第 10、23 节为准，历史记录保留；Week 2 尚未完成。

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

**Current Gate:** W02-C04-G-A3 — Existing HGT Identity Uniqueness Policy Freeze
**Status:** `CONTRACT CLARIFICATION COMPLETE / VERIFIED`

**W02-G0:** `PASS`

The Week 2 data contract, Sprint Spec, scope boundaries, scenario definitions,
Hidden Ground Truth isolation rules, and acceptance criteria are frozen.

**W02-C04-A:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04 Scenario Inventory:** `FROZEN — 3 FAMILIES`

**W02-C04-BC:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-BC-R1 Targeted ChatGPT Re-review:** `PASS`

**W02-C04-BC Final Closeout:** `AUTHORIZED`

**W02-C04-DE-A:** `SUPERSEDED AFTER SAFE CONTRACT STOP`

**W02-C04-DE-A-R1:** `SUPERSEDED AFTER SAFE FINAL RESIDUAL AUDIT STOP`

**W02-C04-DE-A-R2:** `CONTRACT FREEZE COMPLETE / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-D:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-E:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-DE-R1:** `HARDENING VERIFIED`

**ChatGPT W02-C04-DE Final Targeted Re-review:** `PASS`

**W02-C04-DE:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-F-A:** `SUPERSEDED AFTER SAFE STOP`

**W02-C04-F-A-R1:** `SUPERSEDED AFTER SAFE FINAL-AUDIT STOP`

**W02-C04-F-A-R2:** `CONTRACT FREEZE COMPLETE / VERIFIED`

**W02-C04-F-A-R3:** `CONTRACT CLARIFICATION COMPLETE / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-F-AR2:** `AUTHORIZED / VERIFIED`

**W02-C04-F ChatGPT Implementation Review:** `PASS`

**W02-C04-F Human Closeout Approval:** `AUTHORIZED`

**W02-C04-F:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-G-A1:** `BLOCKED — RESOLVED BY A2 EXCEPT FOR THE LATER R1 RESIDUAL AUDIT`

**W02-C04-G-A2:** `CONTRACT CLARIFICATION COMPLETE / VERIFIED`

**W02-C04-G-A1-R1:** `BLOCKED SAFELY — EXISTING IDENTICAL-DUPLICATE POLICY; RESIDUAL CLOSED BY G-A3`

**W02-C04-G-A3:** `CONTRACT CLARIFICATION COMPLETE / VERIFIED`

**W02-C04-G:** `NOT STARTED / NOT AUTHORIZED BY THIS DOCUMENTATION TASK`

**W02-C04-H:** `NOT STARTED`

**W02-C05:** `NOT STARTED`

**Next Engineering Checkpoint:** CHATGPT W02-C04-G-A1-R2 FINAL IMPLEMENTATION AUTHORIZATION RE-REVIEW

**W02-C04-F Implementation:** `IMPLEMENTED / CODEX VERIFIED / CHATGPT REVIEWED / HUMAN APPROVED`

**Reviewed Implementation Commit:** `0e58880aaada7c393ee6ea1e185cf295884d96c7`

**Contract Blockers:** `A1-R1 RESIDUAL CLOSED BY G-A3; FINAL AUTHORIZATION RE-REVIEW PENDING`

Week 3 remains `NOT AUTHORIZED / NOT STARTED`.

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

**Next Engineering Checkpoint:** CHATGPT W02-C04-F IMPLEMENTATION REVIEW

W02-C04-D/E remain closed and verified. W02-C04-F is implemented and Codex
verified, pending ChatGPT review. W02-C04-G/H remain not started.

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

**Next Engineering Checkpoint:** CHATGPT W02-C04-F IMPLEMENTATION REVIEW

**W02-C04 Status:** `D/E CLOSED / VERIFIED — F IMPLEMENTED / CODEX VERIFIED / PENDING CHATGPT REVIEW — G/H NOT STARTED`

**W02-C04 Readiness:** `READY FOR C04-F IMPLEMENTATION REVIEW`

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

**W02-C04 Status:** `D/E CLOSED / VERIFIED — F IMPLEMENTED / CODEX VERIFIED / PENDING CHATGPT REVIEW — G/H NOT STARTED`

**Next Engineering Checkpoint:** CHATGPT W02-C04-F IMPLEMENTATION REVIEW

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

**W02-C04-BC:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

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

Implementation state at W02-C04-BC closeout:

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

**Next Engineering Checkpoint at W02-C04-BC closeout:** W02-C04-DE IMPLEMENTATION RE-AUTHORIZATION

**C04-DE Implementation:** `NOT STARTED`

---

## 16. W02-C04-DE-A-R2 Final Materialization Contract Freeze

**W02-C04-A:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-BC:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-DE-A:** `SUPERSEDED AFTER SAFE CONTRACT STOP`

**W02-C04-DE-A-R1:** `SUPERSEDED AFTER SAFE FINAL RESIDUAL AUDIT STOP`

**W02-C04-DE-A-R2:** `CONTRACT FREEZE COMPLETE / VERIFIED / GITHUB SYNCHRONIZED`

DE-A-R2 consolidates the complete Supplier and Quality materialization
semantics, the exact scenario-created Rework identity, and the canonical HGT
causal-chain vocabulary/topology. The final implementation-readiness audit
records:

```text
SUPPLIER IMPLEMENTABLE WITHOUT NEW PRODUCT DECISION: YES
QUALITY IMPLEMENTABLE WITHOUT NEW PRODUCT DECISION: YES
SCENARIO REWORK IDENTITY FULLY FROZEN: YES
HGT CAUSAL CHAIN FULLY FROZEN: YES
REMAINING BLOCKER: NONE
```

Implementation state at the W02-C04-DE-A-R2 contract-freeze checkpoint:

```text
W02-C04-D: NOT STARTED
W02-C04-E: NOT STARTED
W02-C04-F: NOT STARTED
W02-C04-G: NOT STARTED
W02-C04-H: NOT STARTED
```

No Supplier or Quality Python behavior, test, migration, dependency, HGT
manifest, persistence, analytics, ML, RAG, LLM, or Agent capability was added
by this documentation-only contract checkpoint.

**Next Engineering Checkpoint at W02-C04-DE-A-R2 closeout:** W02-C04-DE IMPLEMENTATION RE-AUTHORIZATION

---

## 17. W02-C04-DE Supplier + Quality Final Closeout / Supplier + Quality 最终关闭

**W02-C04-A:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-BC:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-DE-A-R2:** `CONTRACT FREEZE COMPLETE / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-D:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-E:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**W02-C04-DE-R1:** `HARDENING VERIFIED`

**ChatGPT W02-C04-DE Final Targeted Re-review:** `PASS`

**W02-C04-DE:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

Supplier Degradation and Quality Deterioration are implemented under the
frozen C04 contract. Deterministic selection and materialization, detached
scenario finalization, baseline immutability, generated-at isolation, and HGT
referential integrity are verified. No C02 schema, Alembic migration,
dependency, or C03 generator change was required. / Supplier Degradation 与
Quality Deterioration 已按冻结的 C04 契约完成实现。确定性选择与物化、分离式场景
终结、基线不可变性、generated-at 隔离及 HGT 引用完整性均已验证。无需修改 C02
Schema、Alembic migration、依赖或 C03 generator。

Accepted remaining limitations:

- finalized `GeneratedDataset` objects still contain mutable detached ORM rows;
  caller mutation after finalization can stale the stored content hash;
- protected HGT file serialization remains deferred to W02-C04-G;
- PostgreSQL scenario compatibility and database-dependent acceptance remain
  deferred to W02-C04-H.

```text
W02-C04-F implementation: NOT STARTED
W02-C04-G: NOT STARTED
W02-C04-H: NOT STARTED
Week 3: NOT AUTHORIZED / NOT STARTED
```

**Next Engineering Checkpoint:** CHATGPT W02-C04-F IMPLEMENTATION AUTHORIZATION RE-REVIEW

---

## 18. W02-C04-F-A-R2 Capacity Surge Final Contract Freeze

**W02-C04-F-A:** `SUPERSEDED AFTER SAFE STOP`

**W02-C04-F-A-R1:** `SUPERSEDED AFTER SAFE FINAL-AUDIT STOP`

**W02-C04-F-A-R2:** `CONTRACT FREEZE COMPLETE / VERIFIED`

W02-C04-F-A stopped safely because the first Capacity decision pack's
universal 48-character identity representation exceeded the frozen
`varchar(40)` capacities of SalesOrder, WorkOrder, and PurchaseOrder.
W02-C04-F-A-R1 preserved C02 through capacity-aware 40/48-character persisted
SHA-256 representations and stopped safely on three final delivery/HGT
ambiguities. W02-C04-F-A-R2 resolves those residual decisions and preserves
the full F1–F21 contract.

The historical R2 audit records (the later AR1 zero-delay finding and R3
resolution are recorded in Section 19):

```text
CAPACITY TARGET GRAPH FULLY FROZEN: YES
EXACT N FULLY FROZEN: YES
NEW ARRIVAL COUNT FULLY FROZEN: YES
SOURCE TEMPLATE RULE FULLY FROZEN: YES
NEW THREAD CONSTRUCTION FULLY FROZEN: YES
SCENARIO ROW IDENTITIES FULLY FROZEN: YES
IDENTIFIER PK/FK CAPACITY COMPATIBILITY: PASS
SUPPLEMENTAL PROCUREMENT FULLY FROZEN: YES
QUEUE / TEMPORAL PROPAGATION FULLY FROZEN: YES
ORDER-LEVEL DELIVERY PROPAGATION FULLY FROZEN: YES
CAPACITY HGT FULLY FROZEN: YES
C02 SCHEMA COMPATIBILITY: PASS
C03 PRIVATE TUNING REQUIRED: NO
C03 RNG CONTINUATION REQUIRED: NO
NEW PRODUCT DECISION REQUIRED: NO
CAPACITY IMPLEMENTABLE WITHOUT NEW PRODUCT DECISION: YES
REMAINING BLOCKER: NONE
```

R2 freezes one SalesOrder-level Delivery delta across multiple Work Orders,
the Operation-primary/WorkOrder-fallback parent for every created Quality
Inspection, and one canonical final binding Operation for each shifted Work
Order. No C02 schema, ORM, migration, dependency, Python source, test, Docker,
CI, C03, Supplier, or Quality behavior changed.

Accepted remaining limitations:

- finalized `GeneratedDataset` objects contain mutable detached ORM rows, so
  caller mutation after finalization can stale the stored content hash;
- protected HGT serialization remains deferred to W02-C04-G and is not
  complete;
- PostgreSQL C04 scenario compatibility and database-dependent acceptance
  remain deferred to W02-C04-H and are not complete.

```text
W02-C04-F implementation: NOT STARTED
W02-C04-G: NOT STARTED
W02-C04-H: NOT STARTED
Week 3: NOT AUTHORIZED / NOT STARTED
```

**Next Engineering Checkpoint:** CHATGPT W02-C04-F IMPLEMENTATION AUTHORIZATION RE-REVIEW

---

## 19. W02-C04-F-A-R3 Zero-Delay HGT Contract Clarification

**Status:** `CONTRACT CLARIFICATION COMPLETE / VERIFIED`

Starting checkpoint verified on 2026-09-15: feature branch
`feat/w02-industrial-data-foundation`, local/tracking/direct remote/PR #5 head
`80cb49001f388b927c10d09479773b186518795b`, clean working tree, and main/merge
base `311bad46c40ce365b726c2f7e918c5a65daa2ad9`. Draft PR #5 was open, draft,
not merged, with auto-merge disabled.

AR1 stopped implementation authorization on one edge case missed by the R2
audit: `queue_time_multiplier == 1` is valid and produces zero queue delay,
but prior wording implied an obligatory queue edge for eligible unchanged
Operations. R3 resolves this in data-contract Section 15A.7.11: eligibility
alone is not an effect; a direct queue edge exists exactly once only for
positive additional delay. Creation remains an independent effect, while
selected Work Centers remain targets without becoming affected rows.

Arrival-only, queue-only, and fully neutral configurations remain valid
under the unchanged input gates. Neutral Capacity has no new business rows,
no business-field mutations, an empty affected map, and an empty causal
chain; scenario identity/provenance remains distinct. An in-memory diagnostic
confirmed that the existing config and HGT foundation accept the neutral
configuration, zero delay, empty collections, and reproducible HGT IDs/hashes.
No protected HGT file was generated.

```text
ZERO-DELAY QUEUE EFFECT SEMANTICS FULLY FROZEN: YES
QUEUE EDGE CARDINALITY FULLY FROZEN: YES
QUEUE ELIGIBILITY VS AFFECTED SEMANTICS FULLY FROZEN: YES
SCENARIO-CREATED OPERATION ZERO-DELAY SEMANTICS FULLY FROZEN: YES
ARRIVAL-ONLY CONFIGURATION FULLY FROZEN: YES
QUEUE-ONLY CONFIGURATION FULLY FROZEN: YES
FULLY NEUTRAL CONFIGURATION FULLY FROZEN: YES
EMPTY AFFECTED MAP ALLOWED BY EXISTING HGT FOUNDATION: YES
EMPTY CAUSAL CHAIN ALLOWED BY EXISTING HGT FOUNDATION: YES
CAPACITY HGT IMPLEMENTABLE WITHOUT NEW PRODUCT DECISION: YES
CAPACITY IMPLEMENTABLE WITHOUT NEW PRODUCT DECISION: YES
REMAINING CONTRACT BLOCKER: NONE
```

The four arrival/queue boundary cases have canonical targets, actual-effect
affected maps, endpoint IDs, vocabulary, link cardinality, and HGT hashes/IDs.
F8-R1, R2-D1/D2/D3, all previous graph/count/template/procurement/queue rules,
C02, C03, Supplier, Quality, and common C04 identity/finalization are unchanged.

Validation executed before this state update:

- focused scenario/intervention/generation pytest: **48 passed**;
- full pytest: **78 passed, 9 skipped, 1 warning**; database-dependent tests
  require `FLOWLENS_DATABASE_URL`; existing Starlette/httpx deprecation warning;
- `ruff check .`: **PASS**;
- established strict `mypy .`: **PASS**, 47 source files;
- `docker compose config --quiet`: **PASS**, exit 0, with Docker config-file
  access warnings;
- `flowlens-uv.exe lock --check`: **ENVIRONMENT-BLOCKED**, uv cache
  `sdists-v9/.git` access denied; dependencies and lock remain unchanged;
- contract/sprint diff whitespace, balanced fences, conflict-marker,
  accidental debug/TODO/FIXME/HACK, and secret-pattern scans: **PASS**.

Only the data contract, Sprint Spec, and this state record are changed by R3.
No source, test, schema/model, migration, dependency, Docker/CI, persistence,
PostgreSQL behavior, or protected HGT serialization is added. The accepted
mutable-detached-row limitation remains; C04-G serialization and C04-H
database acceptance remain deferred.

```text
C04-F IMPLEMENTATION: NOT STARTED / NOT AUTHORIZED
C04-G: NOT STARTED
C04-H: NOT STARTED
Week 3: NOT AUTHORIZED / NOT STARTED
```

This is contract clarification, not permission to implement Capacity.

**Next Engineering Checkpoint:** W02-C04-F-AR2 FINAL IMPLEMENTATION AUTHORIZATION RE-REVIEW

---

## 20. W02-C04-F-I Capacity Surge Implementation

**W02-C04-F-AR2:** `AUTHORIZED / VERIFIED`

**W02-C04-F:** `IMPLEMENTED / CODEX VERIFIED / PENDING CHATGPT REVIEW`

Starting feature HEAD was `cad7acb0174a377f00656761340b01bf648789c1`, verified
equal to tracking, direct remote, and Draft PR #5. Main/merge base remained
`311bad46c40ce365b726c2f7e918c5a65daa2ad9`; the branch was 11 ahead / 0 behind
main and clean before implementation.

Implemented only:

- `src/flowlens/data/scenarios/capacity.py`: private deterministic Capacity
  injector; real target graph, exact order population and template cycling,
  complete added threads, F8-R1 IDs/FKs, historical supplemental procurement,
  queue accumulation, WorkOrder/inspection/Rework propagation, R2-D1 order-level
  Delivery delta, R2-D2/D3 causal parents, R3 neutral semantics, and exact HGT;
- `src/flowlens/data/scenarios/application.py`: Capacity dispatch through the
  existing detached-cloning/finalization/ScenarioResult pipeline;
- `tests/test_capacity_scenario.py`: 41 cases covering the A–AO implementation
  matrix, all four multiplier modes, independent identity/field/causal-edge
  expectations, boundary and rejection cases, and a full real DEMO baseline;
- `tests/test_scenario_interventions.py`: replace the obsolete Capacity
  NotImplementedError expectation with successful queue-only dispatch while
  preserving all Supplier, Quality, and business-day assertions;
- this current-state record, updated only after validation passed.

All new source threads are copied before any source-derived timing is shifted.
Existing foundation primitives supply independent ORM cloning, purpose-separated
ranking, duration rounding, canonical row sorting/counting/hashing, DatasetVersion
finalization, HGT identity, and ScenarioResult binding. No common foundation
module or public scenario API changed.

Verification executed on 2026-09-15 with existing `.venv/Scripts` executables:

| Command | Result |
|---|---|
| `python -B -m pytest -p no:cacheprovider tests/test_capacity_scenario.py` | 41 passed |
| `python -B -m pytest -p no:cacheprovider tests/test_scenario_interventions.py tests/test_scenarios.py tests/test_generation.py` | 48 passed |
| `python -B -m pytest -p no:cacheprovider` | 119 passed, 9 skipped, 1 warning |
| `ruff check .` | PASS |
| `mypy .` | PASS, 49 source files |
| `git diff --check` | PASS |
| `docker compose config --quiet` | PASS, exit 0; Docker config-file access warnings |
| `flowlens-uv.exe lock --check` | ENVIRONMENT-BLOCKED: existing uv cache `sdists-v9/.git` access denied |

The nine skips require `FLOWLENS_DATABASE_URL`. The warning is the existing
Starlette/httpx deprecation. No non-database test was skipped, disabled,
deleted, or weakened. Initial development runs exposed a test expectation
arithmetic error and two unsuitable success-smoke windows; these were corrected
without changing frozen behavior. The final successful runs above supersede
those failures.

Verified outcomes:

- exact eight-family IDs fit existing PK/FK lengths; collisions reject;
- full copied topology and rewritten FKs match independent expectations;
- selected targets are distinct from actually affected rows;
- zero direct delay produces no queue edge; creation remains an independent
  effect; fully neutral Capacity has an empty affected map and causal chain;
- multiple WorkOrders shift each Delivery once by the order-level anchor delta;
- immutable baseline payload/hash/count/ID, independent ORM instrumentation,
  session-free operation, repeated application, input ordering, and generated-at
  isolation are preserved;
- default Capacity runs on the 12,000-order, 18-month C03 DEMO baseline;
- Supplier, Quality, C03, and existing foundation regressions pass.

Targeted contract audits also pass without source corrections. Section 15A.7.1
requires copying every owned Material Requirement, not a minimum Material
Requirement count or per-WorkOrder coverage; it requires at least one Quality
Inspection across the reusable thread, not per WorkOrder. All owned Operations
and required completion anchors remain validated. The existing HGT foundation
sorts and deduplicates targets, affected IDs, and causal links before canonical
hashing; no additional canonicalizer is needed. All checks were rerun before
repository closeout with the results above, including the lock-check limitation.

Known limitations and boundaries:

- Early added arrivals can legitimately reject when no same-material supplier
  PO predates the order decision time. This frozen rejection is tested; no
  fallback supplier, future information, or altered selection is used.
- Finalized detached ORM rows remain mutable by callers, as previously accepted.
- C04-G protected HGT serialization/isolation and C04-H PostgreSQL acceptance
  remain deferred. This task generates no protected HGT files and adds no
  persistence, database sessions, or database-dependent scenario behavior.
- Frozen data/Sprint contracts, C02 models/schema, migrations, dependencies,
  C03, Supplier/Quality behavior, Docker, and CI are unchanged.

```text
C04-F: IMPLEMENTED / CODEX VERIFIED / PENDING CHATGPT REVIEW
C04-F CLOSED: NO
C04-G: NOT STARTED
C04-H: NOT STARTED
C05: NOT STARTED
Week 3: NOT AUTHORIZED / NOT STARTED
CONTRACT CONFLICT: NONE
```

**Next Engineering Checkpoint:** CHATGPT W02-C04-F IMPLEMENTATION REVIEW

---

## 21. W02-C04-F Final Closeout

**Task:** `W02-C04-F-C1`

**Status:** `CLOSED / VERIFIED / GITHUB SYNCHRONIZED`

**Capacity Surge:** `IMPLEMENTED / CODEX VERIFIED / CHATGPT REVIEWED / HUMAN APPROVED`

**Reviewed Implementation Commit:** `0e58880aaada7c393ee6ea1e185cf295884d96c7`

**ChatGPT Implementation Review:** `PASS`

**Human Closeout Approval:** `AUTHORIZED`

The human owner supplied the independent ChatGPT review PASS and explicitly
authorized this documentation-only closeout on 2026-09-15. Contract conformance,
business semantics, test adequacy, and scope control passed with no blocker,
high, or medium finding. No code correction, reimplementation, or contract
reopening is required. The reviewed implementation remains unchanged.

Verified capabilities:

- deterministic Capacity target graph and exact qualifying SalesOrder population `N`;
- deterministic arrival count, template ranking/cycling, and complete digital-thread cloning;
- F8-R1 schema-compatible generated identities and collision rejection;
- deterministic, historically eligible supplemental procurement;
- queue arithmetic, cumulative temporal propagation, and WorkOrder completion recomputation;
- R2-D1 SalesOrder-level Delivery propagation;
- R2-D2 QualityInspection parent and R2-D3 binding Operation semantics;
- R3 zero-delay, arrival-only, queue-only, combined, and neutral behavior;
- deterministic HGT targets, affected maps, causal topology, and canonicalization;
- baseline immutability, generated_at isolation, and input-order independence;
- full 12,000-order DEMO execution and Supplier / Quality / C03 regression preservation.

The reviewed implementation evidence in Section 20 remains authoritative:
41 Capacity tests passed; 48 scenario/generation regression tests passed;
full pytest had 119 passed, 9 database-dependent skips, and one existing
deprecation warning. Ruff, strict mypy (49 files), and Compose configuration
passed. These implementation/infrastructure checks were not rerun for this
documentation-only closeout. Closeout validation checks the complete state diff,
single-file scope, whitespace, Markdown fences, prohibited artifacts, reviewed
implementation immutability, and Git/PR synchronization.

Accepted deferred boundaries:

- protected HGT serialization/isolation remains deferred to C04-G;
- PostgreSQL scenario acceptance and applicable database-dependent tests remain deferred to C04-H;
- mutable detached ORM rows can stale a stored hash after caller mutation; this limitation remains accepted;
- uv lock verification remains environment-blocked by the documented cache-access limitation;
- the existing Starlette/httpx deprecation and Docker config-access warnings remain documented.

Earlier checkpoint states, including Section 20's pending-review state, remain
historical evidence. This section and Section 10 define the current state.
Closing C04-F does not close Week 2 or authorize later implementation.

```text
W02-C04-F: CLOSED / VERIFIED / GITHUB SYNCHRONIZED
CONTRACT BLOCKER: NONE
C04-G: NOT STARTED
C04-H: NOT STARTED
C05: NOT STARTED
Week 3: NOT AUTHORIZED / NOT STARTED
```

**Next Engineering Checkpoint:** CHATGPT W02-C04-G IMPLEMENTATION AUTHORIZATION / CONTRACT REVIEW

---

## 22. W02-C04-G-A2 Protected HGT Manifest Policy Freeze

**W02-C04-G-A1:** `BLOCKED — RESOLVED BY A2 CONTRACT DECISIONS`

**W02-C04-G-A2:** `CONTRACT CLARIFICATION COMPLETE / VERIFIED`

Starting checkpoint on 2026-09-16: feature branch
`feat/w02-industrial-data-foundation`, clean working tree, and matching local,
tracking, direct remote, and Draft PR #5 HEAD
`b393c5d955bc8e036289f5aedae2cb04067635b3`. Main/merge base remained
`311bad46c40ce365b726c2f7e918c5a65daa2ad9`; feature was 13 ahead / 0 behind
main and 0 ahead / 0 behind tracking. PR #5 was open/draft/not merged with
auto-merge disabled.

A1 was a read-only authorization review and stopped without changing the
repository. Its two blockers were fixed-manifest cardinality/envelope and
existing-file/repeated-write behavior. ChatGPT/human ownership now resolves
both through G-A2-D1–D10 in data-contract Section 15A.8.1:

- only `records` at the manifest top level, containing complete existing HGT
  records; no extra metadata or provenance fields;
- lexicographic record ordering by `(scenario_id, hgt_id)`;
- one explicit writer invocation receives one finalized HGT;
- absent file creates a one-record collection;
- a new HGT ID preserves existing records, inserts, sorts, and publishes;
- an identical repeated HGT is idempotent without duplicate records;
- same ID with different semantic content rejects without mutation;
- malformed/incompatible existing content rejects without repair or mutation;
- collection updates retain unrelated records even when publication uses
  atomic filesystem replacement;
- the fixed protected path rejects traversal, symlink escape, and unexpected
  alternate roots; arbitrary normal-path destinations are prohibited.

The existing HGT object supplies all 15 record fields and canonical
targets/affected IDs/causal links. Its semantic payload and HGT IDs/hashes
remain authoritative; collection ordering introduces no second identity
system. `generated_at` stays DatasetVersion-only provenance. A whole-file
checksum is not `hgt_hash`. `apply_scenario()` and `ScenarioResult` do not
change, and scenario execution never automatically writes the manifest.

Only the data contract, Sprint Spec, and this state record are changed.
Historical Sections 11–21 remain intact. No source, test, schema/model,
migration, dependency, Docker/Compose, CI, business persistence, or generated
artifact is changed. C04-F remains closed and its reviewed implementation
commit remains `0e58880aaada7c393ee6ea1e185cf295884d96c7`.

The editing state was CONTRACT FREEZE IN PROGRESS. After documentation
validation on 2026-09-16, the freeze transitioned to COMPLETE / VERIFIED.
The 14-question zero-ambiguity audit passes: collection/envelope/record
schema/order, missing/new/identical/conflicting/malformed input behavior,
non-destructive updates, explicit-only writing, identity preservation, and
the PostgreSQL/scenario-business boundaries all match the supplied decisions.
Exactly three authorized documentation files changed. Complete-diff review,
whitespace, Markdown fences/structure, conflict-marker, accidental debug,
and secret-pattern scans passed; historical Sections 11–21 were preserved.
No expensive scenario generation or implementation/infrastructure test suite
was rerun for this contract-only checkpoint. No HGT artifact was generated.

The accepted mutable-detached-row and uv cache-access limitations remain.
Protected serialization is still unimplemented; PostgreSQL scenario
acceptance remains C04-H. Neither PostgreSQL nor C04-H is required before
C04-G implementation or unit acceptance. This freeze is not implementation
authorization.

```text
C04-G implementation: NOT STARTED
C04-H: NOT STARTED
C05: NOT STARTED
Week 3: NOT AUTHORIZED / NOT STARTED
```

**Next Engineering Checkpoint:** CHATGPT W02-C04-G-A1-R1 FINAL IMPLEMENTATION AUTHORIZATION RE-REVIEW

---

## 23. W02-C04-G-A3 Existing HGT Identity Uniqueness Policy Freeze

**W02-C04-G-A3:** `CONTRACT CLARIFICATION COMPLETE / VERIFIED`

**A1-R1 Residual Blocker:** `CLOSED BY G-A3 CONTRACT DECISION`

Baseline verified on 2026-09-16: clean feature branch
`feat/w02-industrial-data-foundation`; local, tracking, direct remote, and
Draft PR #5 HEAD matched `6be8d1b793e60a62d33fa3e1cc566590beff43e9`.
Main/merge base remained `311bad46c40ce365b726c2f7e918c5a65daa2ad9`;
feature was 14 ahead / 0 behind main and 0 ahead / 0 behind tracking.
PR #5 was open/draft/not merged with auto-merge disabled.

**Historical safe stop — W02-C04-G-A1-R1:** `BLOCKED SAFELY — RESIDUAL EXISTING IDENTICAL-DUPLICATE POLICY`.
The read-only review confirmed the G-A2 envelope and incoming-write rules,
but existing identical duplicate HGT records had no explicit validity outcome.
It made no repository mutation and granted no implementation authorization.
Original A1 blockers and the G-A2 freeze remain recorded in Section 22;
Sections 11–22 are preserved as historical evidence.

ChatGPT/human ownership now supplies only the residual uniqueness decision,
recorded as G-A3-D1–D4 in data-contract Section 15A.8.2. Existing identical
and conflicting duplicate `hgt_id` values both invalidate the manifest.
Validate the whole existing collection before incoming-record logic; reject
duplicates without integration, deduplication, repair, or replacement, leaving
the original artifact byte-for-byte unchanged. Do not create a temporary
repaired collection for publication. Diagnostic/in-memory parsing is allowed
without mutating repository, business, or scenario state.

A valid manifest has only the top-level `records` field, zero or more complete
valid 15-field HGT records, unique IDs, and lexicographic `(scenario_id, hgt_id)`
ordering when canonically published. Uniqueness is validity, not normalization.
Incoming identical content remains idempotent for a valid collection with
exactly one matching record; conflicting incoming content rejects unchanged.

```text
EXISTING IDENTICAL DUPLICATE HGT IDS: REJECT WITHOUT MUTATION
EXISTING CONFLICTING DUPLICATE HGT IDS: REJECT WITHOUT MUTATION
COLLECTION-WIDE HGT_ID UNIQUENESS: REQUIRED
AUTOMATIC DEDUPLICATION: PROHIBITED
INCOMING IDENTICAL REPEAT: IDEMPOTENT WHEN EXISTING MANIFEST IS OTHERWISE VALID AND CONTAINS EXACTLY ONE MATCHING RECORD
C04-G implementation: NOT STARTED / NOT AUTHORIZED BY THIS DOCUMENTATION TASK
C04-H: NOT STARTED
C05: NOT STARTED
Week 3: NOT AUTHORIZED / NOT STARTED
```

No new HGT or manifest-level identity algorithm is introduced. HGT IDs/hashes,
scenario identity, business hashes, protected-path/runtime isolation,
`apply_scenario()`, and `ScenarioResult` remain unchanged. Supplier, Quality,
Capacity, F8-R1, R2/R3, C02, and C03 are not reopened; C04-F remains closed.
PostgreSQL, C04-H, and C05 are not C04-G prerequisites; no dependency is required.
The accepted mutable-detached-row and uv cache-access limitations remain.

This checkpoint changes only the data contract, Sprint Spec, and current-state
documentation. No serializer, tests, manifest, source/schema/migration,
dependency, Docker, or CI change is authorized. On 2026-09-16, documentation
validation passed: exact three-file scope, whitespace, Markdown fence/structure,
conflict-marker, accidental-addition and secret-pattern scans, complete diff
review, and historical checkpoint preservation. The original contract/Sprint
content outside the new G-A3 sections and current-state Sections 11–22 remain
unchanged. All 20 zero-ambiguity questions have the supplied answers. After
these checks, G-A3 transitioned from IN PROGRESS to COMPLETE / VERIFIED.
No expensive scenario generation or implementation tests were rerun; no
serializer, test, or protected artifact was created. This contract completion
does not grant implementation authorization.

**Next Engineering Checkpoint:** CHATGPT W02-C04-G-A1-R2 FINAL IMPLEMENTATION AUTHORIZATION RE-REVIEW
