# FlowLens Industrial AI — AGENTS.md
> Week 1 Project Foundation / 第一周项目基础规则

This file defines repository-wide rules for Codex and any engineering agent working in this repository.  
本文件定义 Codex 及任何工程代理在本仓库中必须遵守的全局规则。

---

## 1. 项目使命 / Project Mission

**中文**

FlowLens Industrial AI 是一个面向高压电气装备制造场景的、以证据为基础的工业 AI 决策智能平台。首个纵向闭环聚焦 **Production Delivery Intelligence（生产交付智能）**，逐步形成：

**DESCRIBE → PREDICT → INVESTIGATE → TRANSFORM**

系统的核心目标不是“做一个制造业聊天机器人”，而是通过确定性数据分析、延期风险预测、企业知识检索和受控 LLM 调查工作流，帮助制造运营人员更早识别交付风险信号、调查问题并形成可执行的改进建议。

**English**

FlowLens Industrial AI is an evidence-grounded Industrial AI Decision Intelligence platform for high-voltage electrical equipment manufacturing scenarios. Its first vertical focuses on **Production Delivery Intelligence** and evolves through:

**DESCRIBE → PREDICT → INVESTIGATE → TRANSFORM**

The goal is not to build a generic manufacturing chatbot. The system should combine deterministic analytics, delivery-risk prediction, enterprise knowledge retrieval, and controlled LLM investigation workflows to help manufacturing operations teams identify delivery-risk signals earlier, investigate problems, and generate actionable improvement recommendations.

---

## 2. 唯一事实源 / Source of Truth

**中文**

Git 仓库是唯一事实源。关键业务定义、数据契约、指标定义、架构决策、Sprint Spec、评估规则和当前状态必须写入仓库文档，而不能只存在于聊天记录中。

任何已批准的业务契约不得为了工程实现方便而被静默修改。若实现与契约冲突，Codex 必须报告冲突并等待确认。

**English**

The Git repository is the single source of truth. Business definitions, data contracts, metric definitions, architecture decisions, sprint specifications, evaluation rules, and current-state records must be stored in repository documents rather than only in chat history.

Approved business contracts must not be silently changed for implementation convenience. If implementation conflicts with a contract, Codex must report the conflict and wait for a decision.

---

## 3. 当前阶段 / Current Phase

**中文**

当前阶段：**Week 1 — Project Foundation**

Week 1 只建立可复现、可测试、可一键启动的工程基础。不得提前实现 Week 2 及以后功能。

**English**

Current phase: **Week 1 — Project Foundation**

Week 1 is limited to establishing a reproducible, testable, one-command engineering foundation. Do not implement Week 2 or later capabilities early.

---

## 4. 当前业务范围 / Current Business Scope

**中文**

- 行业域：高压电气装备制造参考场景
- 数据属性：Synthetic / anonymized / industry-inspired
- 首个业务场景：Production Delivery Intelligence
- Primary User：Production / Delivery Operations Manager
- 核心问题：**Why are production orders delayed, and how can data and AI support earlier intervention?**
- 决策问题：**How can an operations manager identify delivery-risk signals early enough to decide where investigation or intervention should begin?**

不得把模拟数据、模拟流程或行业参考内容描述为某家真实企业的生产数据或正式部署。

**English**

- Domain: high-voltage electrical equipment manufacturing inspired scenario
- Data status: synthetic / anonymized / industry-inspired
- First use case: Production Delivery Intelligence
- Primary user: Production / Delivery Operations Manager
- Core question: **Why are production orders delayed, and how can data and AI support earlier intervention?**
- Decision question: **How can an operations manager identify delivery-risk signals early enough to decide where investigation or intervention should begin?**

Do not describe synthetic data, synthetic processes, or industry-inspired materials as the production data or official deployment of a real company.

---

## 5. 架构原则 / Architecture Principles

### 5.1 Modular Monolith First

**中文**

优先使用模块化单体架构。除非存在明确的 P0 需求，否则不得主动引入微服务、Kafka、RabbitMQ、Kubernetes 或其他分布式复杂度。

**English**

Prefer a modular monolith. Do not introduce microservices, Kafka, RabbitMQ, Kubernetes, or other distributed-system complexity unless a concrete P0 requirement justifies it.

### 5.2 One Primary Database

**中文**

第一版使用 PostgreSQL 作为主要数据库。Week 1 可以启用 pgvector 扩展，但不得实现 Embedding、Vector Search 或 RAG。

**English**

Use PostgreSQL as the primary database. pgvector may be enabled in Week 1, but embeddings, vector search, and RAG must not be implemented yet.

### 5.3 Deterministic Numbers

**中文**

所有业务指标必须由 SQL 或 Python 确定性计算。未来的 LLM 只能理解、编排、综合和解释，不得成为数值事实来源。

**English**

All business metrics must be calculated deterministically with SQL or Python. Future LLM components may understand, orchestrate, synthesize, and explain, but must never become the source of numeric truth.

### 5.4 Evidence First

**中文**

后续所有重要 Observed Fact 必须能够追踪到数据、模型或文档证据。不得把没有证据支持的推测包装成事实。

**English**

Future observed facts must be traceable to data, model, or document evidence. Unsupported assumptions must never be presented as facts.

### 5.5 Correlation Is Not Causation

**中文**

使用“风险信号”“关联”“与……同时出现”等语言。除非有明确因果设计，否则不得使用“导致”“造成”等因果表述。

**English**

Use language such as “risk signal,” “association,” or “co-occurs with.” Do not use causal wording such as “caused” unless a valid causal design supports the claim.

### 5.6 Contracts Before Implementation

**中文**

数据契约、指标定义、API 契约或 Sprint Spec 一旦冻结，Codex 不得为了实现方便自行修改。若发现不可实现、矛盾或遗漏，应报告 conflict。

**English**

Once data contracts, metric definitions, API contracts, or sprint specifications are frozen, Codex must not modify them for convenience. If they are impossible, contradictory, or incomplete, report the conflict.

---

## 6. Week 1 禁止事项 / Week 1 Prohibitions

**中文**

Week 1 不得实现：

- Synthetic manufacturing data generation
- Manufacturing domain tables
- Manufacturing metrics
- Dashboard business functionality
- ML or feature engineering
- RAG
- Embeddings
- Vector search
- LLM API calls
- Agents
- LangChain
- LangGraph
- Prompt engineering
- ERP / MES integration
- Predictive maintenance
- Computer vision
- Multi-agent systems
- Fine-tuning

**English**

Do not implement the following during Week 1:

- Synthetic manufacturing data generation
- Manufacturing domain tables
- Manufacturing metrics
- Dashboard business functionality
- ML or feature engineering
- RAG
- Embeddings
- Vector search
- LLM API calls
- Agents
- LangChain
- LangGraph
- Prompt engineering
- ERP / MES integration
- Predictive maintenance
- Computer vision
- Multi-agent systems
- Fine-tuning

---

## 7. Week 1 允许事项 / Week 1 Allowed Work

**中文**

Week 1 可以实现：

- Python project setup
- FastAPI skeleton
- PostgreSQL + pgvector infrastructure
- SQLAlchemy setup
- Alembic setup
- Docker Compose
- Worker placeholder
- `/health` API
- pytest
- Lint
- Type checking
- `.env.example`
- basic CI
- repository documentation

**English**

Week 1 may implement:

- Python project setup
- FastAPI skeleton
- PostgreSQL + pgvector infrastructure
- SQLAlchemy setup
- Alembic setup
- Docker Compose
- Worker placeholder
- `/health` API
- pytest
- lint
- type checking
- `.env.example`
- basic CI
- repository documentation

---

## 8. 数据与安全规则 / Data and Security Rules

**中文**

- 不得提交 `.env`、API key、密码或其他 secret。
- 必须提供 `.env.example`。
- 后续 `data/hidden_ground_truth/` 必须与生产应用代码隔离。
- Production application code 不得读取 hidden ground truth。
- Week 1 不得创建完整制造业务 Schema。
- 不得在日志中输出敏感凭据。

**English**

- Never commit `.env`, API keys, passwords, or other secrets.
- Provide `.env.example`.
- Future `data/hidden_ground_truth/` must be isolated from production application code.
- Production application code must never read hidden ground truth.
- Do not create the full manufacturing business schema in Week 1.
- Do not log sensitive credentials.

---

## 9. 工程行为 / Engineering Behaviour

**中文**

每个 Codex 任务必须：

1. 先读取本文件和对应 Sprint Spec。
2. 在修改代码前检查现有仓库结构。
3. 只修改任务允许范围。
4. 不进行无关重构。
5. 不增加无明确理由的依赖。
6. 新增逻辑必须有适当测试。
7. 实际运行要求的测试和质量检查。
8. 不得隐藏失败结果。
9. 测试通过后再更新 `docs/CURRENT_STATE.md`。
10. 完成后返回变更摘要、命令、测试结果和已知限制。

**English**

Every Codex task must:

1. Read this file and the relevant Sprint Spec first.
2. Inspect the existing repository before editing.
3. Modify only the allowed scope.
4. Avoid unrelated refactoring.
5. Avoid adding dependencies without clear justification.
6. Add appropriate tests for new logic.
7. Actually run the required tests and quality checks.
8. Never hide failed results.
9. Update `docs/CURRENT_STATE.md` only after checks pass.
10. Return a change summary, commands run, test results, and known limitations.

---

## 10. Definition of Done

**中文**

任务只有在以下条件全部满足时才算完成：

- Acceptance Criteria 已满足。
- 必要单元/集成测试已新增或更新。
- pytest 通过。
- lint 通过。
- type checking 通过。
- Docker / infrastructure 检查按 Spec 通过。
- 未违反 Scope 与 Non-goals。
- 未静默修改业务契约。
- 必要文档已更新。
- `docs/CURRENT_STATE.md` 准确记录真实状态。
- 已知限制明确列出。

**English**

A task is complete only when:

- Acceptance criteria are satisfied.
- Required unit/integration tests are added or updated.
- pytest passes.
- lint passes.
- type checking passes.
- Docker/infrastructure checks required by the spec pass.
- Scope and non-goals are respected.
- No business contract is silently changed.
- Required documentation is updated.
- `docs/CURRENT_STATE.md` reflects the real state.
- Known limitations are explicitly listed.
