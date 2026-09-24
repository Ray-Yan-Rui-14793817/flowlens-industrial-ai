# FlowLens Industrial AI — W03-G0 Authorization Package V2

**Baseline:** `main@9d18ddde9fe933952a2661ee1419f13c8577605d`

---

## 1. Complete G0 Scope

```text
G0-GPT-01
Architecture Baseline

G0-GPT-02
AI Loop Constitution

G0-GPT-03
Semantic Trust

G0-GPT-04
Context / Material

G0-GPT-05
Prompt / Tool

G0-GPT-06
State Machine / Failure

G0-GPT-07
Harness / Reporting

G0-GPT-08
Sprint / Checkpoint Package

G0-R1
Repository Execution Projection
```

---

## 2. G0-R1 Projection Files

```text
AGENTS.md
LOOP.md
skills/README.md
skills/SKILL_ADMISSION_POLICY.md
W03_G0_R1_REPOSITORY_EXECUTION_PROJECTION.md
```

Their roles:

```text
AGENTS.md
= persistent W3 agent router

LOOP.md
= thin loop/index router

skills/
= procedural admission policy only
```

---

## 3. Important Skills Decision

G0 does **not** authorize creation of executable project Skills.

Current policy:

```text
G0:
policy only

C01:
no project Skill required

C02:
no project Skill required by default

post-C02:
review stable repeated workflows for Skill packaging
```

This prevents procedural automation from becoming a competing source of semantic authority.

---

## 4. Human Approval Meaning

If the Product Owner approves G0 V2, this authorizes the next **publication/transition step**, not unrestricted implementation.

Authorized transition:

```text
publish G0 governance docs
update AGENTS.md
add LOOP.md
add skills governance policy
update CURRENT_STATE
verify publication
close G0
create feat/w03-ai-decision-loop
begin W03-C01-A
```

It does not authorize:

```text
C01 implementation before C01-A
schema changes
new migrations
LLM SDK
agents
RAG
runtime LLM tools
operational writes
```

---

## 5. Current Status

```text
G0 GPT AUTHORING:
COMPLETE

G0-R1 PROJECTION DESIGN:
COMPLETE

G0 GPT FINAL REVIEW V2:
PASS FOR HUMAN APPROVAL

HUMAN APPROVAL:
PENDING

REPOSITORY PUBLICATION:
PENDING

G0 CLOSED:
NO

W03 IMPLEMENTATION:
NOT AUTHORIZED
```
