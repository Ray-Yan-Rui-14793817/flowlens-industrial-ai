# FlowLens Industrial AI — AGENTS.md
> Week 2 Industrial Data Foundation / 第二周工业数据基础规则

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

当前阶段：**Week 2 — Industrial Data Foundation**

**Week 1 — Project Foundation：CLOSED / POST-MERGE VERIFIED**

Week 2 建立：

- canonical manufacturing data contracts；
- manufacturing SQLAlchemy models；
- Alembic manufacturing schema；
- deterministic synthetic-data generation；
- dataset versioning；
- fixed random seed；
- scenario injection；
- Hidden Ground Truth isolation；
- referential / temporal / quantity data-quality validation；
- Week 2 unit / integration / CI validation。

已冻结的 Week 2 控制契约：

- `docs/03_data_contracts.md`
- `docs/sprints/W02_industrial_data_foundation.md`

所有 Week 2 实现必须遵守这些契约。不得提前实现 Week 3 或更晚阶段的能力。

**English**

Current phase: **Week 2 — Industrial Data Foundation**

**Week 1 — Project Foundation: CLOSED / POST-MERGE VERIFIED**

Week 2 establishes:

- canonical manufacturing data contracts;
- manufacturing SQLAlchemy models;
- Alembic manufacturing schema;
- deterministic synthetic-data generation;
- dataset versioning;
- fixed random seed;
- scenario injection;
- Hidden Ground Truth isolation;
- referential / temporal / quantity data-quality validation;
- Week 2 unit / integration / CI validation.

Frozen Week 2 control contracts:

- `docs/03_data_contracts.md`
- `docs/sprints/W02_industrial_data_foundation.md`

All Week 2 implementation must conform to those contracts. Do not implement Week 3 or later capabilities early.

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

第一版使用 PostgreSQL 作为主要数据库。Week 2 只能创建 `docs/03_data_contracts.md` 明确批准的制造 Schema。pgvector 仍然仅作为基础设施存在；Week 2 不得实现 Embedding、Vector Search、Semantic Retrieval 或 RAG。

**English**

Use PostgreSQL as the primary database. Week 2 may create only the manufacturing schema explicitly approved by `docs/03_data_contracts.md`. pgvector remains infrastructure-only; Week 2 must not implement embeddings, vector search, semantic retrieval, or RAG.

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

## 6. Week 2 禁止事项 / Week 2 Prohibitions

**中文**

Week 2 不得实现：

- Manufacturing metrics
- On-Time Delivery / Delay Rate
- Cycle Time / WIP analytics
- Material Availability metric
- Supplier On-Time Rate
- FPY / Rework Rate
- Analytics API
- Dashboard business functionality
- Plotly business analytics
- Feature engineering
- Delivery Risk ML
- Model training or inference
- Embeddings
- Vector search
- Semantic retrieval
- RAG
- LLM API calls
- Prompt engineering
- Agents
- LangChain
- LangGraph
- Real ERP / MES integration
- Predictive maintenance
- Computer vision
- Multi-agent systems
- Fine-tuning
- New message brokers
- Unnecessary distributed infrastructure

Week 2 operational tables 不得存储：

- `is_delayed`
- `delay_days`
- `delivery_delay_rate`
- `supplier_on_time_rate`
- `material_availability_ratio`
- `first_pass_yield`
- `rework_rate`
- `delivery_risk_probability`
- `scenario_id`
- `scenario_name`
- `true_root_cause`

**English**

Do not implement the following during Week 2:

- manufacturing metrics;
- On-Time Delivery / Delay Rate;
- Cycle Time / WIP analytics;
- Material Availability metric;
- Supplier On-Time Rate;
- FPY / Rework Rate;
- analytics API;
- dashboard business functionality;
- Plotly business analytics;
- feature engineering;
- Delivery Risk ML;
- model training or inference;
- embeddings;
- vector search;
- semantic retrieval;
- RAG;
- LLM API calls;
- prompt engineering;
- agents;
- LangChain;
- LangGraph;
- real ERP / MES integration;
- predictive maintenance;
- computer vision;
- multi-agent systems;
- fine-tuning;
- new message brokers;
- unnecessary distributed infrastructure.

Week 2 operational tables must not store:

- `is_delayed`
- `delay_days`
- `delivery_delay_rate`
- `supplier_on_time_rate`
- `material_availability_ratio`
- `first_pass_yield`
- `rework_rate`
- `delivery_risk_probability`
- `scenario_id`
- `scenario_name`
- `true_root_cause`

---

## 7. Week 2 允许事项 / Week 2 Allowed Work

**中文**

Week 2 可以实现：

- `docs/03_data_contracts.md` 批准的 manufacturing schema；
- canonical SQLAlchemy Base / metadata；
- manufacturing SQLAlchemy models；
- Alembic manufacturing-domain migrations；
- deterministic synthetic manufacturing data generator；
- test / ci / demo dataset profiles；
- fixed seed；
- dataset version；
- generator version；
- canonical content hashing；
- three approved scenario injectors；
- Hidden Ground Truth manifest / runtime isolation；
- referential integrity validation；
- temporal integrity validation；
- quantity integrity validation；
- reproducibility validation；
- scenario distribution validation；
- dataset manifest；
- data-quality report；
- Week 2 unit tests；
- PostgreSQL integration tests；
- Week 2 CI seed/data-quality smoke；
- required Week 2 documentation。

所有实现必须遵守：

- `docs/03_data_contracts.md`
- `docs/sprints/W02_industrial_data_foundation.md`

**English**

Week 2 may implement:

- the manufacturing schema approved by `docs/03_data_contracts.md`;
- canonical SQLAlchemy Base / metadata;
- manufacturing SQLAlchemy models;
- Alembic manufacturing-domain migrations;
- deterministic synthetic manufacturing data generator;
- test / ci / demo dataset profiles;
- fixed seed;
- dataset version;
- generator version;
- canonical content hashing;
- the three approved scenario injectors;
- Hidden Ground Truth manifest / runtime isolation;
- referential-integrity validation;
- temporal-integrity validation;
- quantity-integrity validation;
- reproducibility validation;
- scenario-distribution validation;
- dataset manifest;
- data-quality report;
- Week 2 unit tests;
- PostgreSQL integration tests;
- Week 2 CI seed/data-quality smoke;
- required Week 2 documentation.

All implementation must conform to:

- `docs/03_data_contracts.md`
- `docs/sprints/W02_industrial_data_foundation.md`

---

## 8. 数据与安全规则 / Data and Security Rules

**中文**

- 不得提交 `.env`、API key、密码或其他 secret。
- 必须提供 `.env.example`。
- Manufacturing tables 只能在冻结的数据契约明确规定时创建。
- 不得静默引入新的字段、业务标签、指标或语义。
- `data/hidden_ground_truth/` 必须与 runtime application code 隔离。
- API、Worker、Analytics、未来 ML、RAG 和 orchestration runtime code 不得读取 Hidden Ground Truth。
- Runtime Docker images 不得包含 Hidden Ground Truth。
- Public manifests 不得暴露 scenario names、affected entities、true root causes 或 evaluation answers。
- Synthetic assumptions 不得表述为浙江恒博的真实内部运营参数或真实生产数据。
- 不得引入真实 customer、supplier、employee、commercial 或 confidential identifiers。
- 不得在日志中输出敏感凭据。

**English**

- Never commit `.env`, API keys, passwords, or other secrets.
- Provide `.env.example`.
- Manufacturing tables may be created only when explicitly defined by the frozen data contract.
- Do not silently introduce new fields, business labels, metrics, or semantics.
- `data/hidden_ground_truth/` must remain isolated from runtime application code.
- API, Worker, Analytics, future ML, RAG, and orchestration runtime code must not read Hidden Ground Truth.
- Runtime Docker images must not contain Hidden Ground Truth.
- Public manifests must not reveal scenario names, affected entities, true root causes, or evaluation answers.
- Synthetic assumptions must not be represented as real Zhejiang Hengbo internal operating parameters or real production data.
- Do not introduce real customer, supplier, employee, commercial, or confidential identifiers.
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
