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
建立 Del…6573 tokens truncated…orchestration framework。

**English**

Create an ADR for changes such as:

- introducing a major new framework;
- changing the primary database;
- moving from a modular monolith to multiple services;
- introducing a queue/broker;
- changing data-contract principles;
- changing the evidence architecture;
- introducing a new LLM orchestration framework.
