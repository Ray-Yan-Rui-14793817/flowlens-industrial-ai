# W01 — Project Foundation / 项目基础 Sprint Spec
**Task ID:** `W01-PROJECT-FOUNDATION`  
**Sprint:** Week 1  
**Planned Dates / 计划日期:** 2026-08-17 → 2026-08-23  
**Stage / 阶段:** DESCRIBE  
**Owner Model / 协作模型:** ChatGPT defines → Codex implements → Human approves

---

## 1. Business Goal / 业务目标

**中文**

在不实现制造分析、ML、RAG 或 LLM 的前提下，为 FlowLens Industrial AI 建立一个可复现、可测试、可一条命令启动的工程基础。

Week 1 的价值不是交付业务功能，而是确保未来每一个 Sprint 都在同一套项目目标、范围、架构和质量规则上继续开发。

**English**

Establish a reproducible, testable, one-command engineering foundation for FlowLens Industrial AI without implementing manufacturing analytics, ML, RAG, or LLM capabilities.

The value of Week 1 is not business functionality. It is to ensure every later sprint builds on the same project goals, scope, architecture, and quality rules.

---

## 2. Product Context / 产品背景

**中文**

FlowLens Industrial AI 是一个面向高压电气装备制造参考场景的 evidence-grounded Industrial AI Decision Intelligence 项目。

首个纵向场景：

**Production Delivery Intelligence**

Primary User：

**Production / Delivery Operations Manager**

核心问题：

> **Why are production orders delayed, and how can data and AI support earlier intervention?**

决策问题：

> **How can an operations manager identify delivery-risk signals early enough to decide where investigation or intervention should begin?**

**English**

FlowLens Industrial AI is an evidence-grounded Industrial AI Decision Intelligence project for a high-voltage electrical equipment manufacturing inspired scenario.

First vertical:

**Production Delivery Intelligence**

Primary user:

**Production / Delivery Operations Manager**

Core question:

> **Why are production orders delayed, and how can data and AI support earlier intervention?**

Decision question:

> **How can an operations manager identify delivery-risk signals early enough to decide where investigation or intervention should begin?**

---

## 3. Technical Goal / 技术目标

**中文**

建立以下工程能力：

- Git repository baseline；
- Python project environment；
- FastAPI skeleton；
- PostgreSQL + pgvector；
- SQLAlchemy；
- Alembic；
- Docker Compose；
- Worker placeholder；
- `/health` endpoint；
- pytest；
- lint；
- type checking；
- `.env.example`；
- basic CI；
- repository documentation。

完成后应支持：

> **one-command startup + repeatable quality checks**

**English**

Establish:

- Git repository baseline;
- Python project environment;
- FastAPI skeleton;
- PostgreSQL + pgvector;
- SQLAlchemy;
- Alembic;
- Docker Compose;
- worker placeholder;
- `/health` endpoint;
- pytest;
- lint;
- type checking;
- `.env.example`;
- basic CI;
- repository documentation.

The result should support:

> **one-command startup + repeatable quality checks**

---

## 4. Mandatory Inputs / 必须读取的输入

Codex must read before making changes:

1. `AGENTS.md`
2. `docs/00_project_charter.md`
3. `docs/01_scope.md`
4. `docs/02_architecture.md`
5. `docs/CURRENT_STATE.md`
6. `docs/sprints/W01_project_foundation.md`

**中文**

若这些文件之间存在冲突，或与现有代码冲突，不得自行猜测。必须报告 conflict。

**English**

If these files conflict with one another or with existing code, do not guess. Report the conflict.

---

## 5. Required Repository Foundation / 必需仓库基础

Recommended baseline:

```text
flowlens-industrial-ai/
├── AGENTS.md
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
│
├── docs/
│   ├── 00_project_charter.md
│   ├── 01_scope.md
│   ├── 02_architecture.md
│   ├── CURRENT_STATE.md
│   ├── adr/
│   └── sprints/
│       └── W01_project_foundation.md
│
├── apps/
│   ├── api/
│   ├── web/
│   └── worker/
│
├── src/
├── tests/
└── migrations/
```

**中文**

具体 Python package 布局可以由 Codex 按合理工程惯例调整，但不得违反 `02_architecture.md` 的模块边界。

**English**

The exact Python package layout may be adapted using reasonable engineering conventions, but it must not violate the module boundaries in `02_architecture.md`.

---

## 6. Required API Contract / 必需 API 契约

### Endpoint

`GET /health`

### Healthy

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

健康检查必须反映数据库连接状态，不允许数据库不可用时仍返回完全 healthy。

**English**

The health endpoint must reflect database connectivity. It must not report fully healthy status when the database is unavailable.

---

## 7. Infrastructure Requirements / 基础设施要求

### PostgreSQL + pgvector

**中文**

要求：

- PostgreSQL container；
- pgvector extension available；
- persistent local volume；
- environment-variable configuration；
- 最小连接验证。

Week 1 不得实现 embedding 或 vector retrieval。

**English**

Required:

- PostgreSQL container;
- pgvector extension available;
- persistent local volume;
- environment-variable configuration;
- minimal connectivity verification.

Do not implement embeddings or vector retrieval in Week 1.

### Worker Placeholder

**中文**

Worker 仅作为 placeholder：

- 能加载配置；
- 能正常启动；
- 能保持运行/健康。

不得引入 Redis、Celery、Kafka、RabbitMQ。

**English**

The worker is only a placeholder:

- loads configuration;
- starts successfully;
- remains running/healthy.

Do not introduce Redis, Celery, Kafka, or RabbitMQ.

---

## 8. Required Tests / 必需测试

### Unit Tests

至少验证：

- application configuration loads；
- health response schema。

### Integration Tests

至少验证：

- API can connect to PostgreSQL；
- `/health` returns `200` when DB is healthy；
- database-unavailable path is handled correctly。

### Infrastructure Check

至少运行：

```bash
docker compose config
```

并验证配置有效。

**English**

At minimum, verify:

Unit:
- application configuration loads;
- health response schema.

Integration:
- API can connect to PostgreSQL;
- `/health` returns `200` when the database is healthy;
- the database-unavailable path is handled correctly.

Infrastructure:
- run `docker compose config`;
- verify the Compose configuration is valid.

---

## 9. Required Quality Gates / 必需质量门

**中文**

Codex 必须实际运行并返回结果：

- pytest；
- lint；
- type checking；
- Docker Compose startup / configuration checks。

具体 lint/type-check 工具允许由 Codex选择，但必须：

- 写入项目配置；
- 写入 AGENTS 或 README 命令；
- CI 使用同一套检查。

**English**

Codex must actually run and return results for:

- pytest;
- lint;
- type checking;
- Docker Compose startup/configuration checks.

Codex may choose the lint/type-check tools, but they must be:

- configured in the project;
- documented in AGENTS or README;
- executed consistently in CI.

---

## 10. Files Allowed to Change / 允许修改范围

Week 1 may change:

```text
AGENTS.md
README.md
.env.example
.gitignore
docker-compose.yml
pyproject.toml

apps/
src/
tests/
migrations/

docs/CURRENT_STATE.md
docs/adr/
```

**中文**

以下控制文档属于已批准业务契约。若 Codex 认为需要修改，应先报告 conflict：

```text
docs/00_project_charter.md
docs/01_scope.md
docs/02_architecture.md
docs/sprints/W01_project_foundation.md
```

**English**

The following control documents are approved contracts. If Codex believes they need changes, report a conflict first:

```text
docs/00_project_charter.md
docs/01_scope.md
docs/02_architecture.md
docs/sprints/W01_project_foundation.md
```

---

## 11. Non-goals / 非目标

Week 1 must not implement:

- Synthetic manufacturing data
- Manufacturing domain schema
- Manufacturing metrics
- Business dashboard functionality
- ML
- Feature engineering
- RAG
- Embeddings
- Vector search
- LLM API calls
- Agents
- Prompt engineering
- ERP integration
- MES integration
- Computer vision
- Predictive maintenance
- Multi-agent architecture
- Fine-tuning

**中文**

特别要求：不得自行开始 Week 2。

**English**

Special requirement: do not automatically begin Week 2.

---

## 12. Known Risks / 已知风险

Codex should actively check for:

1. scope creep;
2. unnecessary dependency additions;
3. premature manufacturing schema design;
4. secret leakage;
5. platform-specific setup that harms reproducibility;
6. Docker startup instability;
7. false-positive health checks;
8. tests that only exercise code but not required behavior;
9. architecture changes not documented in ADR;
10. updates to `CURRENT_STATE.md` that overstate actual completion.

---

## 13. Acceptance Criteria / 验收标准

A Week 1 implementation passes only when all are true:

- [ ] `docker compose up` can start the required Week 1 services.
- [ ] API container starts successfully.
- [ ] PostgreSQL starts successfully.
- [ ] pgvector extension is available.
- [ ] Worker placeholder starts successfully.
- [ ] `GET /health` returns HTTP 200 with healthy DB connectivity.
- [ ] DB-unavailable path is handled and does not falsely report healthy.
- [ ] SQLAlchemy configuration works.
- [ ] Alembic configuration is initialized and usable.
- [ ] pytest passes.
- [ ] lint passes.
- [ ] type checking passes.
- [ ] `.env.example` exists.
- [ ] secrets are not committed.
- [ ] basic CI is present and uses the documented checks.
- [ ] no Week 2 manufacturing schema is introduced.
- [ ] no ML/RAG/LLM functionality is introduced.
- [ ] `docs/CURRENT_STATE.md` is updated only after checks pass.
- [ ] known limitations are documented.

---

## 14. Return Format / Codex 返回格式

Codex must return exactly the following sections:

### 1. Files Changed
List every changed file.

### 2. Design Decisions
Explain engineering decisions such as:
- package layout;
- dependency manager;
- lint tool;
- type checker;
- test structure.

### 3. Commands Run
Provide exact commands.

### 4. Test and Quality Results
Report results for:
- pytest;
- lint;
- type checking;
- Docker Compose checks.

### 5. Acceptance Criteria Status
Mark each criterion:
- PASS
- FAIL
- NOT RUN

### 6. Known Limitations
List remaining limitations.

### 7. Contract Conflicts
Explicitly report any contract conflict. If none, say `None`.

### 8. Recommended Next Step
Recommend only. Do not begin Week 2.

---

## 15. Definition of Ready / 开发就绪条件

**中文**

本 Sprint 在以下条件满足后可交给 Codex：

- Project Charter 已冻结；
- Scope 已冻结；
- Architecture v0.1 已冻结；
- AGENTS 规则已冻结；
- Acceptance Criteria 已冻结；
- Non-goals 已冻结；
- 当前状态记录为 `READY FOR CODEX IMPLEMENTATION`。

**English**

This sprint is ready for Codex when:

- Project Charter is frozen;
- Scope is frozen;
- Architecture v0.1 is frozen;
- AGENTS rules are frozen;
- Acceptance Criteria are frozen;
- Non-goals are frozen;
- current state is recorded as `READY FOR CODEX IMPLEMENTATION`.

---

## 16. Definition of Done / 完成条件

**中文**

只有在实际运行测试、质量检查和 Docker 验证并取得结果后，Week 1 才能完成。不得根据代码外观或聊天描述声称完成。

**English**

Week 1 is complete only after tests, quality checks, and Docker verification are actually executed and results are recorded. Completion must not be claimed based on code appearance or chat descriptions.

---

## 17. Recommended Codex Task Prompt / 推荐 Codex 执行提示词

```text
Read AGENTS.md and docs/sprints/W01_project_foundation.md before making changes.

Also read:
- docs/00_project_charter.md
- docs/01_scope.md
- docs/02_architecture.md
- docs/CURRENT_STATE.md

Task:
Implement the Week 1 Project Foundation exactly as defined in W01.

Required:
1. Stay within Week 1 scope.
2. Build the FastAPI, PostgreSQL + pgvector, SQLAlchemy, Alembic, Docker Compose,
   worker placeholder, tests, lint, type checking, .env.example, and basic CI foundation.
3. Implement the frozen GET /health contract.
4. Do not create manufacturing domain tables.
5. Do not add synthetic data, analytics, ML, RAG, embeddings, LLMs, or agents.
6. Do not silently modify approved business contracts.
7. Run the required checks.
8. Update docs/CURRENT_STATE.md only after the checks pass.

Return:
- Files Changed
- Design Decisions
- Commands Run
- Test and Quality Results
- Acceptance Criteria Status
- Known Limitations
- Contract Conflicts
- Recommended Next Step

Do not begin Week 2.
```
