# FlowLens Industrial AI — W03-C01-A Core AI Loop Contracts Authorization

**Task:** `W03-C01-A`
**Checkpoint:** `W03-C01 — Core AI Loop Contracts`
**GPT architecture/contract decision:** `PASS FOR HUMAN AUTHORIZATION`
**Human implementation authorization:** `PENDING`

## 1. Objective

Freeze the smallest stable immutable type system that every later W03 decision-loop
checkpoint can depend on without granting later capabilities early.

C01 is a contract/type checkpoint, not a business-logic checkpoint.

## 2. Frozen G0 invariants

```text
CONTRACT FIRST
ONE CHECKPOINT AT A TIME
CONTEXT LOCK BEFORE IMPLEMENTATION
DEVELOPMENT CONTEXT != RUNTIME CONTEXT
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

## 3. C01 architecture decisions

### C01-D01 — Implementation style

Use standard-library immutable contracts:

```text
@dataclass(frozen=True, slots=True, kw_only=True)
enum.StrEnum
```

No new dependency is needed.

### C01-D02 — Package boundary

C01 may create only:

```text
src/flowlens/decision/
```

Recommended layout:

```text
__init__.py
enums.py
primitives.py
contracts.py
serialization.py
```

`RecommendationEvaluation` / `OutcomeEvaluation` are schemas only; behavior remains C07.
`ExplanationRecord` is a schema only; LLM behavior remains C08.

### C01-D03 — Deep immutability

Published artifact fields may use immutable scalars and tuples.

Forbidden as published artifact fields:

```text
list
dict
set
mutable ORM objects
database sessions
```

Use typed immutable `NamedValue` tuples instead of free mutable maps.

### C01-D04 — StateSnapshot scope

C01 freezes the StateSnapshot envelope, identity and serialization contract only.

C02 remains responsible for actual snapshot population, `as_of_time`/`available_at`
source rules, freshness thresholds, Semantic Trust mapping, unknown propagation,
context reduction, builder behavior and real snapshot construction.

### C01-D05 — Semantic Trust boundary

C01 exposes the frozen TrustLevel vocabulary but assigns no real W2 fact to a trust
class. C02 owns that mapping.

### C01-D06 — DecisionPacket is pre-human-decision

`DecisionPacket` is immutable and produced before Human decision.

It must not contain a mutable `human_decision` field.

Human authority is represented separately by append-only `HumanDecisionEvent`.

### C01-D07 — Recommendation structure only

C01 may carry disposition, selected candidate reference, candidate order, policy
version, score-component envelope, reason codes, evidence references, uncertainties
and limitations.

C01 must not define scoring formulas, thresholds, candidate preference, tie handling,
NO_ACTION policy or NO_RECOMMENDATION business rules. Those belong to C05.

No arbitrary confidence score is introduced.

### C01-D08 — Signal structure only

Freeze the existing signal vocabulary:

```text
SUPPLIER_LATE_RECEIPT
MATERIAL_TIMING_RISK
QUALITY_FAILURE
REWORK_PRESENT
QUALITY_DISPOSITION_UNKNOWN
QUEUE_DELAY
CAPACITY_PRESSURE
DELIVERY_RISK
```

C03 owns triggers, thresholds, required evidence, allowed trust, unknown behavior,
reason semantics and forbidden inference.

### C01-D09 — Intervention families only

```text
NO_ACTION
SUPPLIER_INTERVENTION
QUALITY_INTERVENTION
CAPACITY_INTERVENTION
```

No registry or scenario mapping until C04.

### C01-D10 — Evaluation schemas grant no runtime HGT access

Evaluation types are protected-plane schemas only. No HGT import/read/evaluator
behavior is authorized in C01.

## 4. Authorized source files

```text
src/flowlens/decision/__init__.py
src/flowlens/decision/enums.py
src/flowlens/decision/primitives.py
src/flowlens/decision/contracts.py
src/flowlens/decision/serialization.py

tests/test_decision_contracts.py
tests/test_decision_serialization.py
```

Governance/evidence:

```text
docs/w03/checkpoints/c01/*
docs/w03/reports/W03_C01_R_DEVELOPMENT_ROUND_REPORT.md
docs/CURRENT_STATE.md
```

## 5. Non-goals

```text
NO DecisionContext implementation
NO StateSnapshot Builder
NO database query/persistence
NO SQLAlchemy model
NO Alembic migration
NO signal calculation
NO diagnosis engine
NO candidate registry
NO scenario adapter
NO simulation execution
NO scoring/recommendation algorithm
NO human workflow persistence
NO HGT evaluator
NO LLM adapter/prompt runtime
NO agent/RAG/vector search
NO runtime capability registry implementation
NO API/worker behavior change
NO dependency/CI workflow change
```

## 6. Tool permissions

Development tools within scope:

```text
repository filesystem
pytest
Ruff
mypy
existing PostgreSQL regression when safe
Docker / Compose
Git / GitHub
existing Draft PR #6
existing GitHub Actions CI
```

Runtime tool capability added by C01: `NONE`.

## 7. Auto-repair

Codex may repair Type-A implementation failures inside authorized files.

It must stop for:

```text
TYPE B — CONTRACT CONFLICT
TYPE C — SEMANTIC / PRODUCT DECISION
TYPE D — SAFETY BOUNDARY VIOLATION
```

## 8. Acceptance boundary

Implementation requires:

```text
all C01 artifacts exist
deep immutability
closed enums match frozen vocabularies
deterministic artifact IDs
deterministic canonical serialization
naive datetimes rejected
float payloads rejected
Evidence enforces available_at <= as_of_time
bundle/reference consistency
DecisionPacket has no human-decision mutation field
runtime artifacts expose no HGT/scenario-truth/root-cause field
decision package imports no DB/HGT/runtime-LLM dependency
focused tests pass
regression passes
Ruff / strict mypy / git diff --check pass
exact implementation SHA CI passes
Development Round Report exists
```

Maximum Codex status:

```text
STATUS = REVIEW_READY
GPT REVIEW = PENDING
HUMAN ACCEPTANCE = PENDING
CHECKPOINT CLOSED = NO
```

## 9. GPT verdict

```text
W03-C01-A GPT CONTRACT DESIGN:
COMPLETE

CONTRACT BLOCKER:
NONE

READY FOR HUMAN IMPLEMENTATION AUTHORIZATION:
YES

HUMAN AUTHORIZATION:
PENDING
```
