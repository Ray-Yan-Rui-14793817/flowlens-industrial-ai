# FlowLens Industrial AI — Scope / 项目范围
**Version / 版本:** v0.1  
**Phase / 阶段:** Week 1 — Project Foundation

---

## 1. 范围原则 / Scope Principle

**中文**

FlowLens v1 的范围控制遵循：

**P0 必须完成 → P1 有价值但可裁剪 → P2 作品集优化 → Explicit Non-goals 明确不做**

四个月内优先保证：

- 可运行；
- 可测试；
- 可复现；
- 可演示；
- 可解释。

不以框架数量、Agent 数量或技术复杂度作为项目质量指标。

**English**

FlowLens v1 uses the following scope discipline:

**P0 must-have → P1 valuable but cuttable → P2 portfolio polish → Explicit non-goals**

Within four months, priority is given to:

- runnable;
- testable;
- reproducible;
- demonstrable;
- explainable.

Framework count, number of agents, and architectural complexity are not measures of project quality.

---

# 2. P0 — 必须完成 / Must Have

## P0.1 Industrial Data Foundation / 工业数据底座

**中文**

必须建立：

- Synthetic industrial dataset；
- 12–18 个月制造时间跨度；
- 固定 random seed；
- 场景注入机制；
- Hidden Ground Truth；
- 外键与数据质量检查；
- 数据版本与可复现能力。

**English**

Must include:

- synthetic industrial dataset;
- 12–18 months of manufacturing time coverage;
- fixed random seed;
- scenario injection mechanism;
- hidden ground truth;
- referential-integrity and data-quality checks;
- dataset versioning and reproducibility.

---

## P0.2 Manufacturing Analytics / 制造分析

**中文**

至少支持统一定义和确定性计算：

- On-Time Delivery
- Delay Rate
- Cycle Time
- WIP
- Material Availability
- Supplier On-Time Rate
- FPY
- Rework Rate

每个结果必须有：

- canonical definition；
- time range；
- filters；
- sample size；
- limitations；
- evidence_id。

**English**

At minimum, support canonical definitions and deterministic calculation of:

- On-Time Delivery;
- Delay Rate;
- Cycle Time;
- WIP;
- Material Availability;
- Supplier On-Time Rate;
- FPY;
- Rework Rate.

Each result must include:

- canonical definition;
- time range;
- filters;
- sample size;
- limitations;
- evidence_id.

---

## P0.3 Delivery Risk Prediction / 延期风险预测

**中文**

对单张生产订单输出：

- `delay_probability`
- `risk_level`
- `top_risk_signals`
- `data_as_of_date`
- `model_version`

必须采用 As-of Date 设计，并防止未来信息泄漏。

**English**

For each production order, output:

- `delay_probability`
- `risk_level`
- `top_risk_signals`
- `data_as_of_date`
- `model_version`

The prediction design must use an as-of date and prevent future-information leakage.

---

## P0.4 Evidence-Grounded Investigation / 基于证据的调查

**中文**

必须能够组合：

**Analytics + ML + Industrial Knowledge**

并输出：

- Observed Facts
- Hypotheses
- Contradicting Evidence
- Unknowns
- Next Investigation

关键结论必须可追溯 Evidence。

**English**

Must combine:

**Analytics + ML + Industrial Knowledge**

and output:

- Observed Facts;
- Hypotheses;
- Contradicting Evidence;
- Unknowns;
- Next Investigation.

Important claims must be traceable to evidence.

---

## P0.5 Process & Transformation / 流程与转型

**中文**

至少形成：

**Process Bottleneck → Technology Fit → AI Opportunity → ROI → Human Approval → Mock Action**

Technology Fit 必须能够区分：

- API / SQL
- Rule Automation
- ML
- RAG
- GenAI
- Human + AI
- Human Only

系统不得把所有流程默认推荐成 LLM。

**English**

At minimum, support:

**Process Bottleneck → Technology Fit → AI Opportunity → ROI → Human Approval → Mock Action**

Technology Fit must distinguish:

- API / SQL;
- rule automation;
- ML;
- RAG;
- GenAI;
- Human + AI;
- Human Only.

The system must not recommend an LLM for every process.

---

## P0.6 Evaluation / 评估

**中文**

必须建立：

- deterministic numeric validation；
- ML regression checks；
- retrieval evaluation；
- citation evaluation；
- unsupported claim evaluation；
- security tests；
- hidden-ground-truth isolation tests；
- tool failure recovery tests。

**English**

Must include:

- deterministic numeric validation;
- ML regression checks;
- retrieval evaluation;
- citation evaluation;
- unsupported-claim evaluation;
- security tests;
- hidden-ground-truth isolation tests;
- tool-failure recovery tests.

---

## P0.7 Deployable Demo / 可部署演示

**中文**

最终必须支持：

- 一条命令启动；
- 固定 Demo seed；
- README；
- API 文档；
- 可复现 Demo path；
- 最终回归测试；
- 明确 Known Limitations。

**English**

The final project must support:

- one-command startup;
- fixed demo seed;
- README;
- API documentation;
- reproducible demo path;
- final regression tests;
- explicit known limitations.

---

# 3. P1 — 有价值但可裁剪 / Valuable but Cuttable

**中文**

P0 稳定后再考虑：

- Hybrid retrieval 高级优化；
- 更丰富 Dashboard drill-down；
- 更强 Evidence filtering；
- 更精细 Process visualization；
- 第二个 Investigation Case；
- 更丰富 manufacturing scenarios；
- 更强 observability；
- 更完善 ROI scenario interaction；
- 更复杂失败恢复体验。

**English**

Consider only after P0 is stable:

- advanced hybrid retrieval;
- richer dashboard drill-downs;
- stronger evidence filtering;
- more refined process visualization;
- a second investigation case;
- additional manufacturing scenarios;
- stronger observability;
- richer ROI scenario interaction;
- more advanced failure-recovery UX.

---

# 4. P2 — Portfolio Polish / 作品集优化

**中文**

时间充分时再考虑：

- Next.js 前端重构；
- 多模型横向比较；
- 高级 BPMN/流程编辑器；
- 精细动画和视觉设计；
- 多 Provider 接入；
- 更复杂 ROI 可视化；
- 更完整企业级权限 UI。

**English**

Only consider if time remains:

- Next.js frontend refactor;
- multi-model comparison;
- advanced BPMN/process editor;
- polished animation and visual design;
- multiple provider integrations;
- more complex ROI visualization;
- richer enterprise-permission UI.

---

# 5. Explicit Non-goals / 明确不做

## 5.1 Real ERP/MES Integration / 真实 ERP/MES 集成

**中文**

v1 不连接真实 SAP、ERP 或 MES，不进行生产系统写回。使用 synthetic/mock integration。

**English**

Version 1 does not connect to real SAP, ERP, or MES systems and does not write back into production systems. Use synthetic/mock integrations.

---

## 5.2 Predictive Maintenance / 预测性维护

**中文**

不研究设备剩余寿命、传感器异常或设备故障预测。

**English**

Do not implement remaining-useful-life estimation, sensor anomaly detection, or machine-failure prediction.

---

## 5.3 Computer Vision / 计算机视觉

**中文**

不做缺陷图像识别、摄像头管线或视觉检测。

**English**

Do not implement defect-image recognition, camera pipelines, or visual inspection.

---

## 5.4 Multi-Agent

**中文**

Month 3 首版采用受控 Single Orchestrator。不得为了“更 AI”提前做 Agent swarm。

**English**

The first Month 3 version uses a controlled single orchestrator. Do not build an agent swarm for novelty.

---

## 5.5 Fine-tuning

**中文**

v1 不进行基础模型训练或 LLM fine-tuning。

**English**

Version 1 does not train foundation models or fine-tune LLMs.

---

## 5.6 Multi-Industry Platform

**中文**

第一版不建设通用行业平台。行业范围保持在高压电气装备制造参考场景。

**English**

Version 1 is not a generic multi-industry platform. Keep the domain focused on the high-voltage electrical equipment manufacturing inspired scenario.

---

## 5.7 Production-Grade Enterprise IAM

**中文**

不实现完整企业级 SSO、多租户计费和复杂 IAM。仅在项目需要时实现最小权限与 mock/basic authorization。

**English**

Do not implement full enterprise SSO, multi-tenant billing, or complex IAM. Only implement minimum authorization controls needed by the project.

---

# 6. Week 1 Scope / 第一周范围

## Allowed / 允许

- Git repository initialization
- Python project environment
- FastAPI skeleton
- PostgreSQL + pgvector infrastructure
- SQLAlchemy
- Alembic
- Docker Compose
- Worker placeholder
- `/health` API
- pytest
- lint
- type checking
- `.env.example`
- basic CI
- AGENTS.md
- repository documentation

## Prohibited / 禁止

- manufacturing synthetic data
- manufacturing domain schema
- metric implementation
- analytics features
- ML
- feature engineering
- RAG
- embeddings
- vector search
- LLM integration
- agent orchestration
- business dashboard functionality

---

# 7. Scope Change Policy / 范围变更规则

**中文**

任何新增功能必须回答：

1. 它属于 P0、P1 还是 P2？
2. 它解决什么 Business Goal？
3. 是否会推迟当前 Gate？
4. 是否需要新依赖或新基础设施？
5. 是否可以用更简单的方式完成？
6. 是否已写入 Sprint Spec 或 ADR？

默认原则：

> **如果当前 P0 不依赖它，就不在当前 Sprint 增加。**

**English**

Any proposed new capability must answer:

1. Is it P0, P1, or P2?
2. What business goal does it solve?
3. Will it delay the current gate?
4. Does it require new dependencies or infrastructure?
5. Can the same goal be achieved more simply?
6. Has it been documented in the Sprint Spec or an ADR?

Default rule:

> **If the current P0 does not depend on it, do not add it to the current sprint.**
