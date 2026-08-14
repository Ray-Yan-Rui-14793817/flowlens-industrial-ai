# FlowLens Industrial AI — Architecture v0.1 / 架构 v0.1
**Version / 版本:** v0.1  
**Phase / 阶段:** Week 1 — Project Foundation

---

## 1. 架构目标 / Architecture Goal

**中文**

Week 1 的架构目标不是一次性设计完整生产系统，而是建立一个能够支持未来四个月能力叠加的简单、清晰、可测试基础。

架构优先级：

1. 简单；
2. 可复现；
3. 可测试；
4. 契约清晰；
5. 支持逐步叠加 Analytics、ML、RAG 和 Transformation；
6. 不提前引入无必要复杂度。

**English**

The Week 1 architecture goal is not to design the full production system at once. It is to establish a simple, clear, and testable foundation that can support progressive capability growth over four months.

Architecture priorities:

1. simplicity;
2. reproducibility;
3. testability;
4. clear contracts;
5. progressive addition of analytics, ML, RAG, and transformation;
6. no unnecessary complexity introduced early.

---

## 2. Logical Architecture / 逻辑架构

```text
┌─────────────────────────────────────────────┐
│                  Web / UI                   │
│                                             │
│ Month 1: Streamlit-ready operations UI      │
│ Month 2+: risk / investigation workspaces   │
└──────────────────────┬──────────────────────┘
                       │ HTTP
                       ▼
┌─────────────────────────────────────────────┐
│                 FastAPI API                 │
│                                             │
│ Routing / Validation / Application API      │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              Domain Capabilities            │
│                                             │
│ data                                        │
│ analytics           [Month 1]               │
│ ml                  [Month 2]               │
│ knowledge           [Month 3]               │
│ evidence            [Month 3]               │
│ orchestration       [Month 3]               │
│ process             [Month 4]               │
│ transformation      [Month 4]               │
│ roi                 [Month 4]               │
│ governance          [cross-cutting]         │
└──────────────────────┬──────────────────────┘
                       │
                 SQLAlchemy / Repositories
                       │
                       ▼
┌─────────────────────────────────────────────┐
│           PostgreSQL + pgvector             │
│                                             │
│ Structured industrial data                  │
│ Analytics evidence                          │
│ Predictions                 [later]          │
│ Documents / embeddings      [later]          │
│ Investigation / audit logs  [later]          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│              Worker Placeholder             │
│                                             │
│ Week 1: process starts and stays healthy    │
│ Later: ingestion / offline jobs             │
└─────────────────────────────────────────────┘
```

---

## 3. Week 1 实际启用模块 / Week 1 Active Components

**中文**

Week 1 只实现：

- FastAPI API skeleton；
- PostgreSQL；
- pgvector extension 可用；
- SQLAlchemy 基础；
- Alembic 基础；
- Docker Compose；
- Worker placeholder；
- pytest；
- lint；
- type checking；
- basic CI；
- `/health` endpoint。

未来模块可以保留目录位置，但不得提前实现业务能力。

**English**

Week 1 implements only:

- FastAPI API skeleton;
- PostgreSQL;
- pgvector extension availability;
- SQLAlchemy foundation;
- Alembic foundation;
- Docker Compose;
- worker placeholder;
- pytest;
- lint;
- type checking;
- basic CI;
- `/health` endpoint.

Future module locations may exist, but their business capabilities must not be implemented early.

---

## 4. Architectural Principles / 架构原则

### A01 — Modular Monolith First

**中文**

第一版采用模块化单体。只有当明确 P0 场景无法合理完成时，才考虑新的独立服务。

**English**

Use a modular monolith for version 1. Consider additional services only if a concrete P0 use case cannot reasonably be supported otherwise.

---

### A02 — One PostgreSQL

**中文**

第一版使用一个 PostgreSQL 实例承载结构化业务数据和后续 Evidence/Embedding 等数据。避免过早增加多个数据库。

**English**

Use one PostgreSQL instance for structured business data and later evidence/embedding data. Avoid introducing multiple databases prematurely.

---

### A03 — pgvector Prepared, Not Used Yet

**中文**

Week 1 可以安装并验证 pgvector extension，但不得创建 embedding pipeline 或 retrieval 功能。

**English**

Week 1 may install and verify the pgvector extension, but must not implement embedding pipelines or retrieval.

---

### A04 — Deterministic Business Logic

**中文**

指标、统计、ROI 等业务数字必须由 Python/SQL 可复现地计算。未来 LLM 只能调用确定性工具并解释结果。

**English**

Metrics, statistics, ROI, and other business numbers must be reproducibly calculated with Python/SQL. Future LLM components may call deterministic tools and explain their results.

---

### A05 — Contract-First

**中文**

Sprint Spec、数据契约、Metric Catalog、API Schema 和 Evidence Schema 优先于实现。下游代码不得静默改变上游契约。

**English**

Sprint specifications, data contracts, metric catalogs, API schemas, and evidence schemas take precedence over implementation. Downstream code must not silently redefine upstream contracts.

---

### A06 — Progressive Capability

**中文**

系统能力按顺序叠加：

**Data → Analytics → ML → RAG → Orchestration → Transformation**

后续阶段建立在前一阶段的稳定契约上，而不是每月重写架构。

**English**

Capabilities are added progressively:

**Data → Analytics → ML → RAG → Orchestration → Transformation**

Later phases build on stable contracts from earlier phases rather than rewriting the architecture every month.

---

### A07 — Evidence Lineage

**中文**

从 Week 3 开始，关键结果必须能够追踪到 Analytics、ML 或 Document evidence。Week 1 需要为后续该能力保留清晰模块边界。

**English**

From Week 3 onward, important outputs must be traceable to analytics, ML, or document evidence. Week 1 should preserve clear module boundaries for this capability.

---

## 5. API Boundary / API 边界

### `GET /health`

**中文**

Week 1 冻结第一个 API Contract。

健康状态不仅要检查 FastAPI 进程，也要反映数据库连接状态。

**English**

Week 1 freezes the first API contract.

Health status must reflect not only whether FastAPI is alive but also whether the database is reachable.

### Healthy Response

```json
{
  "status": "ok",
  "service": "flowlens-api",
  "database": "ok"
}
```

HTTP: `200`

### Database Unavailable

```json
{
  "status": "degraded",
  "service": "flowlens-api",
  "database": "unavailable"
}
```

HTTP: `503`

**中文**

实现可以增加不会破坏该契约的字段，但必须保证上述核心字段和语义稳定。

**English**

Implementation may add fields that do not break this contract, but the core fields and semantics above must remain stable.

---

## 6. Database Boundary / 数据库边界

**中文**

Week 1：

允许：

- PostgreSQL 容器；
- pgvector extension；
- SQLAlchemy engine/session；
- Alembic configuration；
- 最小基础连接验证。

禁止：

- 自行定义完整制造业务表；
- 自行决定 production_order、supplier、material、quality、work_center 字段；
- 生成制造 Synthetic Data。

完整制造业务 Data Contract 在 Week 2 冻结后再实现。

**English**

Week 1:

Allowed:

- PostgreSQL container;
- pgvector extension;
- SQLAlchemy engine/session;
- Alembic configuration;
- minimal connectivity verification.

Prohibited:

- defining the full manufacturing business schema;
- inventing fields for production orders, suppliers, materials, quality, or work centers;
- generating synthetic manufacturing data.

The full manufacturing data contract is implemented only after it is frozen in Week 2.

---

## 7. Worker Boundary / Worker 边界

**中文**

Week 1 的 Worker 是占位服务，只需：

- 正常读取配置；
- 容器可以启动；
- 进程保持健康。

不得因 Worker 提前引入 Redis、Celery、Kafka、RabbitMQ 等基础设施。

**English**

The Week 1 worker is a placeholder service. It only needs to:

- load configuration correctly;
- start successfully in its container;
- remain healthy.

Do not introduce Redis, Celery, Kafka, RabbitMQ, or similar infrastructure just because a worker exists.

---

## 8. Repository Module Boundary / 仓库模块边界

推荐结构 / Recommended structure:

```text
flowlens-industrial-ai/
├── AGENTS.md
├── README.md
├── CHANGELOG.md
├── docs/
│   ├── 00_project_charter.md
│   ├── 01_scope.md
│   ├── 02_architecture.md
│   ├── CURRENT_STATE.md
│   ├── adr/
│   └── sprints/
├── apps/
│   ├── api/
│   ├── web/
│   └── worker/
├── src/
│   ├── data/
│   ├── analytics/
│   ├── ml/
│   ├── knowledge/
│   ├── evidence/
│   ├── orchestration/
│   ├── process/
│   ├── transformation/
│   ├── roi/
│   └── governance/
├── tests/
├── evals/
├── data/
│   ├── synthetic/
│   ├── documents/
│   └── hidden_ground_truth/
├── migrations/
├── docker-compose.yml
└── pyproject.toml
```

**中文**

Week 1 不要求所有未来目录都包含实现代码。空目录是否提交由工程实现决定，但不得为了目录完整而提前加入业务逻辑。

**English**

Week 1 does not require future directories to contain implementation code. Whether empty directories are committed is an engineering choice, but no business logic should be added merely to make the tree look complete.

---

## 9. Dependency Policy / 依赖策略

**中文**

新增依赖必须满足至少一个条件：

- 当前 Week 1 P0 明确需要；
- 显著减少重复实现；
- 是所选框架的标准依赖；
- 有明确维护和测试价值。

禁止仅因“以后可能会用到”加入大型依赖。

**English**

A dependency may be added only if at least one of the following is true:

- a current Week 1 P0 requirement needs it;
- it meaningfully reduces duplicate implementation;
- it is a standard dependency of the selected framework;
- it has clear maintainability or testing value.

Do not add large dependencies merely because they might be useful later.

---

## 10. Architecture Decision Records / 架构决策记录

**中文**

以下类型的改变需要 ADR：

- 引入新的主要框架；
- 修改主数据库；
- 从 modular monolith 转向多服务；
- 引入 queue/broker；
- 修改数据契约原则；
- 修改 Evidence 架构；
- 引入新 LLM orchestration framework。

**English**

Create an ADR for changes such as:

- introducing a major new framework;
- changing the primary database;
- moving from a modular monolith to multiple services;
- introducing a queue/broker;
- changing data-contract principles;
- changing the evidence architecture;
- introducing a new LLM orchestration framework.
