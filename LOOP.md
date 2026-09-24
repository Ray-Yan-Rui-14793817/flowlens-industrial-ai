# FlowLens Industrial AI — LOOP.md
> Thin Loop Router / 薄层 Loop 路由文件

**Activation:** Effective after W03-G0 human approval and repository publication.

This file is intentionally **not** a second AI Loop contract.

Its purpose is to route developers, Codex and reviewers to the authoritative loop documents without duplicating them.

---

## 1. Development Control Loop

Authoritative sprint/checkpoint workflow:

```text
docs/sprints/W03_ai_decision_loop.md
```

High-level flow:

```text
GPT Contract Authorization
↓
Human Authorization
↓
Context Lock
↓
Codex Implementation
↓
Harness
↓
Exact-SHA CI
↓
Development Round Report
↓
GPT Independent Review
↓
Human Acceptance
↓
Closeout
↓
Next Checkpoint
```

No checkpoint auto-advance.

---

## 2. Runtime Decision Loop

Authoritative runtime state machine:

```text
docs/w03/LOOP_EXECUTION_STATE_MACHINE.md
```

High-level flow:

```text
Operational Facts
↓
Decision-Time Snapshot
↓
Semantic Trust / Evidence
↓
Signals
↓
Diagnosis
↓
Authorized Candidates
↓
Counterfactual Simulation
↓
RecommendationRecord
↓
DecisionPacket
↓
Bounded Explanation
↓
HumanDecisionEvent
```

Protected offline evaluation is a separate plane.

---

## 3. Failure / Degradation

Authoritative failure policy:

```text
docs/w03/FAILURE_AND_DEGRADATION_POLICY.md
```

Core rule:

```text
trust / temporal / HGT / mutation violation
→ FAIL CLOSED
```

---

## 4. Harness

Authoritative proof and reporting policy:

```text
docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md
```

Core rule:

```text
NO NEW AI CAPABILITY
WITHOUT A CORRESPONDING HARNESS GATE
```

---

## 5. Semantic Meaning

Authoritative semantic contract:

```text
docs/w03/SEMANTIC_TRUST_CONTRACT.md
```

Core rule:

```text
ASSOCIATION != CAUSALITY
UNKNOWN IS VALID
```

---

## 6. Context / Prompt / Tool

```text
docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md
docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md
```

Core runtime rule:

```text
ONE RUN = ONE IMMUTABLE SNAPSHOT

MODEL EXPLAINS
SYSTEM DECIDES

TOOLS DENY BY DEFAULT
```

---

## 7. Conflict Rule

If this router and an authoritative control document differ:

```text
AUTHORITATIVE CONTROL DOCUMENT WINS
```

This file must be corrected; it must not become a competing source of truth.
