# FlowLens Industrial AI — AGENTS.md
> Week 3 Repository Agent Router / W03 仓库级 Agent 执行路由

**Activation:** This file becomes authoritative when the W03-G0 governance package is human-approved and published to the repository.

This file is intentionally concise. It is a persistent execution router, not the full Week 3 architecture specification.

---

## 1. Current Phase

```text
PROJECT:
FlowLens Industrial AI

PHASE:
Week 3 — Industrial AI Decision Loop Foundation

PRIMARY LOOP:
Order Delivery Risk Decision Loop

MODE:
OFFLINE / SHADOW / HUMAN-IN-THE-LOOP

CORE:
DETERMINISTIC-FIRST

OPERATIONAL MUTATION:
PROHIBITED

RUNTIME HGT:
PROHIBITED
```

Week 1 and Week 2 are closed baselines.

Do not reopen or silently reinterpret accepted W1/W2 contracts, history, schema, hashing, scenario semantics, or HGT isolation.

---

## 2. Repository Source of Truth

The Git repository is the source of truth.

For W03 work, read the current authorized task contract first, then the following control documents as applicable:

```text
docs/w03/AI_LOOP_CONSTITUTION.md
docs/sprints/W03_ai_decision_loop.md
docs/w03/SEMANTIC_TRUST_CONTRACT.md
docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md
docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md
docs/w03/LOOP_EXECUTION_STATE_MACHINE.md
docs/w03/FAILURE_AND_DEGRADATION_POLICY.md
docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md
docs/context/CONTEXT_INDEX.md
docs/context/MATERIAL_REGISTRY.md
LOOP.md
```

Frozen W1/W2 upstream contracts remain authoritative unless an explicitly authorized W03 architecture decision changes them.

Repository control documents outrank chat history.

---

## 3. Authority Hierarchy

```text
1. Current authorized task contract
2. AI_LOOP_CONSTITUTION.md
3. W03_ai_decision_loop.md
4. SEMANTIC_TRUST_CONTRACT.md
5. CONTEXT_AND_MATERIAL_MANAGEMENT.md
6. PROMPT_AND_TOOL_EXECUTION_CONTRACT.md
7. LOOP_EXECUTION_STATE_MACHINE.md
8. FAILURE_AND_DEGRADATION_POLICY.md
9. AI_LOOP_HARNESS_AND_REPORTING_SPEC.md
10. Frozen W1/W2 contracts
11. CURRENT_STATE.md
12. Most recent closed W03 Round Report
13. Historical reports / chat
```

A lower-authority source may narrow a task but may not silently weaken a higher-authority invariant.

---

## 4. W03 Frozen Invariants

Always preserve:

```text
CONTRACT FIRST
ONE CHECKPOINT AT A TIME

DEVELOPMENT CONTEXT != RUNTIME CONTEXT
CONTEXT LOCK BEFORE IMPLEMENTATION

SNAPSHOT BEFORE REASONING
ONE RUN = ONE IMMUTABLE SNAPSHOT

EVIDENCE BEFORE CLAIM
ASSOCIATION != CAUSALITY
UNKNOWN IS VALID

TOOLS DENY BY DEFAULT
MODEL EXPLAINS, SYSTEM DECIDES

NO RUNTIME HGT
NO FUTURE LEAKAGE
NO OPERATIONAL MUTATION

HUMAN DECISION AUTHORITY

HARNESS = DETECTION + ENFORCEMENT + EVIDENCE

REPORT BEFORE REVIEW
REVIEW BEFORE ACCEPTANCE
ACCEPTANCE BEFORE CLOSEOUT
NO CHECKPOINT AUTO-ADVANCE
```

---

## 5. W1/W2 Baseline Protection

Do not silently change:

```text
W2 operational schema
Alembic migration semantics
canonical dataset hash semantics
deterministic generator semantics
Supplier scenario semantics
Quality scenario semantics
Capacity scenario semantics
HGT identity/isolation
accepted Week 2 historical evidence
```

If implementation appears to require one of these changes:

```text
STOP
REPORT CONTRACT CONFLICT
WAIT FOR AUTHORIZATION
```

---

## 6. Runtime AI Boundary

W03 v0 Runtime AI may:

```text
READ authorized operational facts through bounded builders
BUILD decision-time snapshots
DERIVE deterministic evidence/signals
SIMULATE isolated counterfactuals
RECOMMEND for human review
EXPLAIN frozen DecisionPackets
RECORD HumanDecisionEvent
EVALUATE offline in the protected evaluation plane
```

W03 v0 Runtime AI may not:

```text
write operational truth
modify SO / WO / PO / Delivery
schedule production automatically
procure automatically
replace suppliers automatically
release quality automatically
read runtime HGT
use future evidence
invent intervention candidates
invent causal truth
```

---

## 7. LLM Boundary

For W03 v0:

```text
LLM ROLE:
EXPLAINER ONLY

LLM TOOL ACCESS:
NONE

LLM DATABASE ACCESS:
NONE

LLM HGT ACCESS:
NONE

LLM CANDIDATE AUTHORITY:
NONE

LLM RECOMMENDATION AUTHORITY:
NONE

LLM OPERATIONAL WRITE:
NONE
```

Recommendation must be frozen before LLM explanation.

---

## 8. Codex Development Workflow

For each implementation checkpoint:

```text
AUTHORIZED TASK CONTRACT
↓
PRE-FLIGHT / BASELINE CHECK
↓
CONTEXT LOCK
↓
IMPLEMENT ONLY AUTHORIZED SCOPE
↓
FOCUSED TESTS
↓
AUTO-REPAIR TYPE-A IMPLEMENTATION FAILURES ONLY
↓
INTEGRATION / REGRESSION
↓
SEMANTIC + SAFETY HARNESS
↓
IMPLEMENTATION COMMIT
↓
NORMAL PUSH
↓
EXACT-SHA CI
↓
DEVELOPMENT ROUND REPORT
↓
STOP AT REVIEW_READY
```

Codex must not self-authorize the next checkpoint.

---

## 9. Failure Handling

### AUTO-REPAIR ALLOWED

```text
ordinary implementation bug
typing error
serialization defect
test defect
bounded CI/config defect
```

### STOP / ESCALATE

```text
contract conflict
semantic/product decision
schema/migration change requirement
canonical hash change requirement
scenario semantic change requirement
new dependency outside authorization
```

### IMMEDIATE ABORT

```text
HGT runtime leakage
future leakage
operational mutation
protected material exposure
unauthorized tool/action
```

---

## 10. Git Rules

Unless the current task explicitly authorizes otherwise:

```text
NO DIRECT MAIN WRITE
NO FORCE PUSH
NO HISTORY REWRITE
NO W2 BRANCH REUSE FOR W3
NO CHECKPOINT AUTO-ADVANCE
```

W03 implementation branch:

```text
feat/w03-ai-decision-loop
```

may be created only after G0 Human Approval and repository publication authorization.

---

## 11. Skills Policy

Project-local `skills/` content is procedural automation, not architectural truth.

Rules:

```text
NO SKILL MAY OVERRIDE A CONTRACT
NO SKILL MAY CHANGE TOOL PERMISSIONS
NO SKILL MAY READ RUNTIME HGT
NO SKILL MAY AUTHORIZE A CHECKPOINT
NO SKILL MAY SELF-APPROVE REVIEW/CLOSEOUT
```

During G0:

```text
NO EXECUTABLE PROJECT SKILL IS REQUIRED
```

Skill candidates may be evaluated after repeated C01/C02 workflows demonstrate stable repetition.

See:

```text
skills/README.md
skills/SKILL_ADMISSION_POLICY.md
```

---

## 12. Completion Boundary

Codex final implementation-round status is at most:

```text
IMPLEMENTATION: COMPLETE
HARNESS: PASS
CI: PASS
CHATGPT REVIEW: PENDING
HUMAN ACCEPTANCE: PENDING
CHECKPOINT CLOSED: NO
STATUS: REVIEW_READY
```

A task is not closed until independent GPT review and Human acceptance are recorded.

---

## 13. When in Doubt

```text
DO NOT GUESS THE CONTRACT
DO NOT REPAIR SEMANTICS SILENTLY
DO NOT EXPAND SCOPE

STOP
SURFACE THE CONFLICT
ASK FOR ARCHITECTURE / PRODUCT DECISION
```
