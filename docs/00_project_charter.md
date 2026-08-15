# FlowLens Industrial AI — Project Charter / 项目章程
**Version / 版本:** v0.1  
**Phase / 阶段:** Week 1 — Project Foundation  
**Domain / 行业域:** High-voltage Electrical Equipment Manufacturing  
**Primary Vertical / 首个纵向场景:** Production Delivery Intelligence

---

## 1. 项目使命 / Project Mission

**中文**

FlowLens Industrial AI 是一个面向高压电气装备制造参考场景的、以证据为基础的工业 AI 决策智能平台。项目首个纵向闭环聚焦 **Production Delivery Intelligence（生产交付智能）**。

项目通过四个阶段逐步建立能力：

**DESCRIBE → PREDICT → INVESTIGATE → TRANSFORM**

最终目标是把工业数据、制造分析、交付风险预测、企业知识和 LLM 驱动的调查工作流连接成一条可演示、可复现、可审计的决策支持闭环。

**English**

FlowLens Industrial AI is an evidence-grounded Industrial AI Decision Intelligence platform for a high-voltage electrical equipment manufacturing inspired scenario. Its first vertical focuses on **Production Delivery Intelligence**.

The project develops through four capability stages:

**DESCRIBE → PREDICT → INVESTIGATE → TRANSFORM**

The final goal is to connect industrial data, manufacturing analytics, delivery-risk prediction, enterprise knowledge, and LLM-driven investigation workflows into one demonstrable, reproducible, and auditable decision-support loop.

---

## 2. 项目定位 / Product Positioning

**中文**

FlowLens 不应被描述为“制造业 Chatbot”。

推荐项目表述：

> **An evidence-grounded Industrial AI Decision Intelligence platform integrating manufacturing analytics, delivery-risk prediction, enterprise knowledge retrieval, and LLM-driven investigation workflows.**

系统强调三个原则：

1. 业务数字由 SQL/Python 确定性计算。
2. 重要结论必须能够回溯 Evidence。
3. LLM 负责理解、编排、综合和解释，而不是凭空计算或制造事实。

**English**

FlowLens should not be described as a “manufacturing chatbot.”

Preferred positioning:

> **An evidence-grounded Industrial AI Decision Intelligence platform integrating manufacturing analytics, delivery-risk prediction, enterprise knowledge retrieval, and LLM-driven investigation workflows.**

The system follows three core principles:

1. Business numbers are calculated deterministically with SQL/Python.
2. Important claims must be traceable to evidence.
3. The LLM understands, orchestrates, synthesizes, and explains; it does not invent calculations or facts.

---

## 3. 行业与数据边界 / Domain and Data Boundary

**中文**

项目使用高压电气装备制造作为行业背景。第一版以 **synthetic / anonymized / industry-inspired** 数据和流程为主，不声称使用某家真实企业的正式生产数据、商业机密或正式部署环境。

后续如使用真实企业材料，必须满足：

- 已授权；
- 已脱敏；
- 不含商业机密；
- 在项目说明中清楚标注来源和限制。

**English**

The project uses high-voltage electrical equipment manufacturing as its industry context. Version 1 primarily uses **synthetic / anonymized / industry-inspired** data and processes and must not claim to use the official production data, trade secrets, or deployed environment of a real company.

If real enterprise materials are used later, they must be:

- authorized;
- de-identified;
- free of trade secrets;
- clearly documented with source and limitations.

---

## 4. 核心业务问题 / Core Business Question

**中文**

首个核心业务问题：

> **为什么生产订单发生延期，数据和 AI 如何帮助管理人员更早介入？**

英文冻结为：

> **Why are production orders delayed, and how can data and AI support earlier intervention?**

为了支撑四个月路线，该问题拆为三个层次：

### DESCRIBE
**What is happening to production delivery performance?**

### PREDICT
**Which production orders are at risk of delay before the delay occurs?**

### INVESTIGATE / TRANSFORM
**What evidence should operations managers investigate, and where should intervention begin?**

**English**

The first core business question is:

> **Why are production orders delayed, and how can data and AI support earlier intervention?**

To support the four-month roadmap, this is decomposed into three levels:

### DESCRIBE
**What is happening to production delivery performance?**

### PREDICT
**Which production orders are at risk of delay before the delay occurs?**

### INVESTIGATE / TRANSFORM
**What evidence should operations managers investigate, and where should intervention begin?**

---

## 5. 决策问题 / Decision Problem

**中文**

FlowLens 的核心价值不只是解释历史，而是帮助管理人员决定“从哪里开始调查或介入”。

冻结的 Decision Problem：

> **How can an operations manager identify delivery-risk signals early enough to decide where investigation or intervention should begin?**

系统后续需要帮助用户在以下方向中定位信号：

- Supplier
- Material
- Production Capacity / WIP
- Cycle Time
- Quality / Rework
- Relevant SOP / policy

**English**

FlowLens is not only intended to explain history. Its value is to help managers decide where investigation or intervention should begin.

Frozen decision problem:

> **How can an operations manager identify delivery-risk signals early enough to decide where investigation or intervention should begin?**

Future versions should help users locate signals across:

- suppliers;
- materials;
- production capacity / WIP;
- cycle time;
- quality / rework;
- relevant SOPs or policies.

---

## 6. Primary Persona / 核心用户

### Production / Delivery Operations Manager

**中文**

第一版核心用户是生产/交付运营经理。其主要关注：

- 总体交付表现是否恶化；
- 哪些订单、产品或时间段异常；
- 延期风险是否与供应商、物料、产能或质量信号同时出现；
- 哪些订单应优先调查；
- 结论的数据证据是什么；
- 是否需要进一步人工干预。

**English**

The primary user for version 1 is the Production / Delivery Operations Manager. Key concerns include:

- whether overall delivery performance is deteriorating;
- which orders, products, or periods are abnormal;
- whether delay risk co-occurs with supplier, material, capacity, or quality signals;
- which orders should be investigated first;
- what evidence supports the conclusion;
- whether human intervention is required.

---

## 7. Secondary Personas / 次要用户

### Production Planner

**中文**
关注 WIP、Work Center Load、Cycle Time、计划执行和生产拥堵。

**English**
Focuses on WIP, work-center load, cycle time, schedule execution, and production congestion.

### Procurement / Supplier Manager

**中文**
关注物料可用性、采购进度、供应商准时交付和供应商表现变化。

**English**
Focuses on material availability, procurement progress, supplier on-time delivery, and supplier performance deterioration.

### Quality Manager

**中文**
关注 FPY、检验失败、返工、质量异常与交付风险信号。

**English**
Focuses on FPY, inspection failures, rework, quality abnormalities, and delivery-risk signals.

---

## 8. Value Proposition / 价值主张

**中文**

FlowLens 帮助制造运营团队更早发现交付表现恶化，将交付问题与物料、供应商、生产负载和质量信号关联起来，并通过可追踪证据支持进一步调查和干预。

**English**

FlowLens helps manufacturing operations teams detect delivery-performance deterioration earlier, relate delivery problems to material, supplier, production-load, and quality signals, and support further investigation and intervention with traceable evidence.

---

## 9. 四阶段路线 / Four-Stage Capability Roadmap

### Month 1 — DESCRIBE
**中文**
建立工业数据底座、统一 Metric Layer、确定性制造分析和 Operations Dashboard。目标是在完全没有 LLM 的情况下准确描述“发生了什么”。

**English**
Build the industrial data foundation, canonical metric layer, deterministic manufacturing analytics, and operations dashboard. The goal is to accurately describe what happened without any LLM.

### Month 2 — PREDICT
**中文**
建立 Delivery Risk 特征流水线、基线模型、Calibration、Threshold 和 Explainability，对单张生产订单输出延期概率和风险信号。

**English**
Build the delivery-risk feature pipeline, baseline models, calibration, thresholds, and explainability to produce delay probability and risk signals for individual production orders.

### Month 3 — INVESTIGATE
**中文**
建立 Industrial RAG、Evidence Layer 和受控 LLM Orchestrator，把 Analytics、ML 和 SOP 连接成调查工作流。

**English**
Build Industrial RAG, the Evidence Layer, and a controlled LLM Orchestrator that combines analytics, ML, and SOPs into an investigation workflow.

### Month 4 — TRANSFORM
**中文**
建立流程瓶颈分析、Technology Fit、AI Opportunity、ROI、Human-in-the-loop 和可部署 Release。

**English**
Build process-bottleneck analysis, technology fit, AI opportunities, ROI, human-in-the-loop approval, and a deployable release.

---

## 10. 项目成功标准 / Project Success Criteria

**中文**

项目成功不以功能数量为标准，而以是否形成一条完整纵向闭环为标准。

必须满足：

- 从工业数据到 Dashboard 的分析链路可复现；
- Delivery Risk 模型无明显数据泄漏；
- 关键业务数字由 SQL/Python 计算；
- Observed Fact、Hypothesis、Unknown、Recommendation 分离；
- 重要结论能够通过 Evidence ID 追踪来源；
- LLM 工具失败时不得伪造结果；
- 最终 Demo 能稳定从“发现异常”走到“调查、转型、审批”。

**English**

Success is not measured by feature count but by whether one complete vertical loop is achieved.

The project must ensure:

- reproducible industrial data-to-dashboard analytics;
- no obvious data leakage in delivery-risk modeling;
- important business numbers are calculated with SQL/Python;
- observed facts, hypotheses, unknowns, and recommendations are separated;
- important claims are traceable through evidence IDs;
- LLM tool failures do not result in fabricated outputs;
- the final demo can reliably move from anomaly detection to investigation, transformation, and approval.

---

## 11. Week 1 目标 / Week 1 Goal

**中文**

Week 1 不实现制造业务功能。目标是冻结项目边界，并建立可一键启动、持续测试、可被后续 Sprint 复用的工程基础。

Week 1 完成后，任何后续 Codex 任务都不应该再需要自行猜测：

- FlowLens 是什么产品；
- 首个业务问题是什么；
- 谁是核心用户；
- 当前允许做什么；
- 当前禁止做什么；
- 架构边界是什么；
- 完成任务需要提供哪些验证证据。

**English**

Week 1 does not implement manufacturing business functionality. Its goal is to freeze project boundaries and establish a one-command, continuously testable engineering foundation reusable by later sprints.

After Week 1, future Codex tasks should not need to guess:

- what FlowLens is;
- what the first business problem is;
- who the primary user is;
- what is currently allowed;
- what is currently prohibited;
- what the architecture boundary is;
- what evidence is required to claim task completion.
