# FlowLens Industrial AI — W03 AI Loop Constitution

**Task:** W03-G0-GPT-02\
**Status:** FROZEN FOR G0 HUMAN REVIEW\
**Baseline:** `main@9d18ddde9fe933952a2661ee1419f13c8577605d`\
**Scope:** Week 3 — Industrial AI Decision Loop Foundation

---

## 1. Purpose

This Constitution is the highest-level Week 3 AI Loop control contract.

It governs:

- GPT architecture and authorization work;
- Codex implementation work;
- runtime Decision Loop behavior;
- Context and Material boundaries;
- Prompt and Tool boundaries;
- Harness and Evaluation requirements;
- Human decision authority;
- checkpoint review and closeout.

If a lower-level Week 3 document conflicts with this Constitution, the conflict must be surfaced and implementation must stop until explicitly resolved.

---

## 2. Authority Order

For Week 3 work, use this precedence:

```text
1. Current authorized task contract
2. W03 AI Loop Constitution
3. W03 Sprint Specification
4. W03 Semantic Trust Contract
5. W03 Context / Material Contract
6. W03 Prompt / Tool Contract
7. W03 Loop State Machine / Failure Policy
8. W03 Harness / Reporting Specification
9. Frozen W1/W2 contracts and architecture
10. CURRENT_STATE
11. Most recent closed Round Report
12. Historical reports / chat
```

A current task may narrow a higher-level contract, but may not silently weaken it.

---

## 3. Constitutional Rules

### C-01 — CONTRACT FIRST

**Rule**

```text
No implementation before an explicit authorized contract exists.
```

**Rationale:** W3 contains semantic and safety boundaries that cannot be delegated to implementation convenience.

**Applies to:** GPT, Codex, runtime components.

**Enforcement:** checkpoint authorization gate.

**Violation:** implementation is not reviewable; stop.

**Exception:** none. Contract changes require a separate authorized architecture decision.

---

### C-02 — ONE CHECKPOINT AT A TIME

**Rule**

```text
authorize → implement → verify → report → review → accept → close
```

before the next checkpoint.

**Enforcement:** `CHECKPOINT_CLOSED == YES` is required before next implementation authorization.

**Violation:** next checkpoint remains unauthorized.

---

### C-03 — CONTEXT LOCK BEFORE IMPLEMENTATION

Every implementation round must freeze:

```text
baseline SHA
contract versions/hashes
dataset version/hash
scenario config/version
prompt version/hash when applicable
tool registry version
allowed / forbidden sources
authorized / forbidden files
expected context delta
```

If context changes outside the authorized delta:

```text
ROUND NOT CLOSEABLE
```

---

### C-04 — DEVELOPMENT CONTEXT != RUNTIME CONTEXT

Development information must never automatically become runtime evidence.

Development-only information includes:

```text
test expected results
scenario truth
HGT descriptions
review comments
implementation instructions
developer reasoning
Codex prompts
```

Runtime AI may receive only Runtime-Safe material explicitly admitted into `DecisionContext`.

---

### C-05 — SNAPSHOT BEFORE REASONING

Every Decision Run binds:

```text
order_id
as_of_time
```

and produces one immutable `StateSnapshot` before downstream reasoning.

Signal, Diagnosis, Scoring and LLM explanation may not independently re-query live operational facts for the same run.

---

### C-06 — ONE RUN = ONE IMMUTABLE OBSERVATION WORLD

After snapshot freeze:

```text
snapshot_id
snapshot_hash
```

identify the operational observation world for the run.

Downstream artifacts must derive from that world.

Mutation creates a new run, not a modified old run.

---

### C-07 — EVIDENCE BEFORE CLAIM

Every material runtime claim must be traceable to:

```text
reason_code
evidence_id(s)
source
timestamp
relationship type
trust level
limitations
```

Ungrounded claims are invalid.

---

### C-08 — ASSOCIATION != CAUSALITY

Associative evidence may support investigation or risk context.

It may not be silently upgraded into:

```text
direct relationship
causal truth
root cause
confirmed allocation
formal release
```

---

### C-09 — UNKNOWN IS VALID

The system must preserve explicit uncertainty.

Valid states include:

```text
UNKNOWN
INSUFFICIENT_EVIDENCE
ASSOCIATIVE_ONLY
UNRESOLVED_DISPOSITION
```

Unknowns are not data-cleaning errors to be hidden.

---

### C-10 — TOOLS DENY BY DEFAULT

No capability is callable unless explicitly registered and authorized for:

```text
caller
loop stage
input type
data class
side-effect class
```

Unregistered capability = unavailable capability.

---

### C-11 — MODEL EXPLAINS, SYSTEM DECIDES

For W3 v0:

```text
LLM recommendation authority = NONE
LLM candidate-creation authority = NONE
LLM operational action authority = NONE
```

Recommendation must be frozen before LLM explanation.

---

### C-12 — NO RUNTIME HGT

HGT is authorized only in the Evaluation Plane.

HGT is forbidden from:

```text
StateSnapshot
DecisionContext
Evidence
Signal
Diagnosis
Candidate Selection
Recommendation
LLM Context
Public Artifact
Operational Database
```

HGT discovered in runtime input is a hard safety failure.

---

### C-13 — NO FUTURE LEAKAGE

All runtime evidence must satisfy:

```text
available_at <= as_of_time
```

Where freshness matters, evidence must also satisfy the applicable staleness policy.

---

### C-14 — NO OPERATIONAL MUTATION

W3 v0 may:

```text
READ
DERIVE
SIMULATE IN ISOLATION
RECOMMEND
EXPLAIN
RECORD HUMAN REVIEW EVENTS
EVALUATE OFFLINE
```

W3 v0 may not write or execute operational business actions.

---

### C-15 — HUMAN DECISION AUTHORITY

```text
AI recommendation != executed action
```

Human decision values:

```text
ACCEPT
REJECT
DEFER
```

Human decision must be recorded as an append-only event.

---

### C-16 — HARNESS = DETECTION + ENFORCEMENT

A Harness gate is incomplete if it can detect a violation but does not define the system response.

Every gate must define:

```text
condition
oracle
PASS behavior
FAIL behavior
```

---

### C-17 — REPORT BEFORE REVIEW

Every implementation checkpoint must produce a Development Round Report after exact implementation evidence exists.

No report:

```text
NOT REVIEW READY
```

---

### C-18 — REVIEW + HUMAN ACCEPTANCE BEFORE CLOSEOUT

Codex cannot self-approve.

Required order:

```text
Codex implementation/report
↓
GPT independent review
↓
Human acceptance
↓
closeout
```

No automatic checkpoint advancement.

---

## 4. W3 v0 Fixed Product Boundary

```text
PRIMARY LOOP:
ORDER DELIVERY RISK DECISION LOOP

MODE:
OFFLINE / SHADOW / HUMAN-IN-THE-LOOP

CORE DECISION LOGIC:
DETERMINISTIC-FIRST

LLM ROLE:
BOUNDED EXPLANATION

LLM TOOLS:
NONE IN W3 V0

OPERATIONAL WRITE:
NONE

RUNTIME HGT:
NONE

HUMAN FINAL AUTHORITY:
REQUIRED
```

---

## 5. Frozen W1/W2 Inheritance

Week 3 must not silently change:

```text
C02 operational schema
migration semantics
C03 deterministic generation
canonical dataset hashing
Supplier scenario semantics
Quality scenario semantics
Capacity scenario semantics
HGT identity/isolation
C05 persistence/publication semantics
C06 accepted evidence and acceptance semantics
```

A genuine incompatibility requires a separate architecture decision.

---

## 6. Exception Policy

Exceptions are not handled through ad-hoc code changes.

Required sequence:

```text
BLOCKER OBSERVED
↓
GPT architecture review
↓
explicit options / impact
↓
Human decision
↓
new authorized contract delta
↓
implementation
```

Until approved, frozen contracts remain authoritative.

---

## 7. Constitution Exit Status

```text
CONSTITUTION:
FROZEN FOR G0 REVIEW

IMPLEMENTATION AUTHORIZATION:
NO

NEXT:
SEMANTIC TRUST CONTRACT
```

---

## 8. Repository Execution Projection

### C-19 — REPOSITORY PROJECTION MUST MATCH GOVERNANCE

The persistent repository execution surfaces must reflect the active governance phase.

Required projection surfaces:

```text
AGENTS.md
LOOP.md
skills/ policy
```

They are not independent semantic authorities.

They must route to, and remain consistent with, the authoritative W03 control documents.

A stale repository instruction that contradicts the authorized sprint state blocks Codex implementation entry.

---

### C-20 — SKILLS AUTOMATE PROCEDURE, NOT AUTHORITY

Project-local Skills may standardize repeated procedures.

They may not:

```text
change contracts
change semantic truth
change tool permissions
access runtime HGT
authorize implementation
approve review
accept business outcomes
close checkpoints
```

G0 authorizes Skill admission policy only.

No executable project Skill is required for W03-C01 entry.
