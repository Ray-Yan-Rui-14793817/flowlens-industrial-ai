# FlowLens Industrial AI — W03-G0-R1 Repository Execution Projection

**Task:** W03-G0-R1\
**Status:** COMPLETE AT DESIGN / ARTIFACT LEVEL\
**Repository publication:** PENDING HUMAN APPROVAL\
**Baseline:** `main@9d18ddde9fe933952a2661ee1419f13c8577605d`

---

## 1. Purpose

G0 governance contracts are not sufficient by themselves if the repository-level agent instruction surface still describes Week 2.

This checkpoint projects the G0 governance model into three repository execution surfaces:

```text
AGENTS.md
LOOP.md
skills/
```

The projection must reduce ambiguity without creating competing sources of truth.

---

## 2. Projection Architecture

```text
AUTHORITATIVE G0 CONTRACTS
        ↓
Repository Execution Projection
        │
        ├── AGENTS.md
        │   persistent agent router
        │
        ├── LOOP.md
        │   thin loop index/router
        │
        └── skills/
            procedural admission policy
            no active executable skill yet
```

---

## 3. AGENTS.md Decision

### Current problem

Repository `main` currently contains a Week-2-oriented `AGENTS.md`.

That file still states:

```text
Current phase: Week 2
Do not implement Week 3 or later capabilities early
```

This is correct historical Week 2 governance but becomes stale when W03 is authorized.

### G0 decision

`AGENTS.md` must be updated during G0 repository publication.

It must become a concise W3 agent router and must not duplicate all W3 contracts.

### Required responsibilities

```text
current phase
authority hierarchy
must-read document routes
frozen invariants
Codex development lifecycle
tool/Git safety
stop conditions
final REVIEW_READY boundary
skills policy
```

### Status

```text
G0 REQUIRED:
YES

BLOCKS C01 CODEX ENTRY IF STALE:
YES
```

---

## 4. LOOP.md Decision

A full second loop contract would create drift.

Therefore root `LOOP.md` is authorized only as a thin router.

It points to:

```text
docs/sprints/W03_ai_decision_loop.md
docs/w03/LOOP_EXECUTION_STATE_MACHINE.md
docs/w03/FAILURE_AND_DEGRADATION_POLICY.md
docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md
docs/w03/SEMANTIC_TRUST_CONTRACT.md
```

If `LOOP.md` conflicts with an authoritative document, the authoritative document wins.

### Status

```text
G0 REQUIRED AS ROUTER:
YES FOR THIS UPDATED GOVERNANCE PACKAGE

SECOND FULL LOOP CONTRACT:
FORBIDDEN
```

The purpose is discoverability, not semantic duplication.

---

## 5. skills/ Decision

Project-local skills are not required to enter C01.

G0 creates only a governance directory:

```text
skills/README.md
skills/SKILL_ADMISSION_POLICY.md
```

No executable project Skill is activated.

### Rationale

The workflow has not yet accumulated enough repeated C01/C02 execution evidence to justify packaging a reusable procedure.

### Future review

After C01/C02:

```text
identify repeated stable procedure
↓
review whether Skill packaging reduces error/context cost
↓
create Skill only if justified
```

### Status

```text
G0 SKILL POLICY:
FROZEN

EXECUTABLE SKILL:
DEFERRED
```

---

## 6. Projection Invariants

Projection files may:

```text
route
summarize
name required docs
state stop conditions
state high-level frozen invariants
```

Projection files may not:

```text
invent new semantics
override authoritative contracts
weaken tool permissions
weaken HGT/temporal safety
create new checkpoint authority
```

---

## 7. Publication Order

After Human G0 approval:

```text
1. publish authoritative G0 docs
2. publish context/material indexes
3. update root AGENTS.md
4. add root LOOP.md router
5. add skills/ governance policy
6. update CURRENT_STATE
7. verify cross-file references
8. only then create feat/w03-ai-decision-loop
9. begin W03-C01-A
```

---

## 8. Acceptance Checks

Before C01:

```text
AGENTS.md says Week 3
AGENTS.md routes to G0 docs
AGENTS.md does not duplicate full contracts

LOOP.md exists only as router
LOOP.md points to authoritative loop docs

skills/ contains policy only
no executable Skill is implied or auto-authorized

CURRENT_STATE reflects G0 publication truth

no W1/W2 frozen code/contract changed
no W03 runtime implementation exists
```

---

## 9. Status

```text
G0-R1 DESIGN:
COMPLETE

AGENTS.md PROPOSED UPDATE:
COMPLETE

LOOP.md ROUTER:
COMPLETE

SKILLS POLICY:
COMPLETE

REPOSITORY PUBLICATION:
PENDING HUMAN APPROVAL

W03 IMPLEMENTATION:
NOT AUTHORIZED
```
