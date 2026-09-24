# FlowLens Industrial AI — W03-G0-GPT-01 Architecture Baseline & Governance Boundary Review

**Task ID:** W03-G0-GPT-01\
**Track:** Week 3 GPT-side development\
**Mode:** Architecture / Governance / Read-only Review\
**Implementation:** NOT AUTHORIZED\
**Repository:** `Ray-Yan-Rui-14793817/flowlens-industrial-ai`\
**Verified main baseline:** `9d18ddde9fe933952a2661ee1419f13c8577605d`\
**Date:** 2026-09-24\

---

# 1. Task Purpose

This task is the first formal GPT-side Week 3 development checkpoint.

It does **not** implement the AI Decision Loop.

Its purpose is to freeze the architectural starting boundary for Week 3 so that later GPT authorization work and Codex implementation work operate from one consistent baseline.

The task answers:

1. What is already complete and frozen from Week 1–2?
2. What exactly is Week 3 allowed to build?
3. What is explicitly outside Week 3 v0?
4. What may be reused rather than redesigned?
5. Which unresolved semantic limitations must remain explicit?
6. What must be decided during the rest of W03-G0 before any implementation begins?
7. Under what conditions may W03-C01 implementation later be authorized?

---

# 2. Live Repository Verification

The repository was re-inspected before this review.

Observed state:

```text
DEFAULT BRANCH:
main

LATEST MAIN COMMIT:
9d18ddde9fe933952a2661ee1419f13c8577605d

LATEST MAIN COMMIT MESSAGE:
Merge pull request #5 ...
feat(w02): complete industrial data foundation

W03 BRANCH SEARCH:
NO W03 BRANCH FOUND

docs/CURRENT_STATE.md:
WEEK 2 CLOSED / VERIFIED / GITHUB SYNCHRONIZED
WEEK 3 NOT STARTED
WEEK 3 IMPLEMENTATION NOT AUTHORIZED
WEEK 3 AUTHORIZATION REVIEW READY
```

Architecture conclusion:

```text
LIVE REPOSITORY STATE
=
HANDOFF BASELINE CONSISTENT
```

No evidence was found that Week 3 implementation has already started.

Therefore:

```text
W03-G0 GPT GOVERNANCE WORK
MAY PROCEED

W03 IMPLEMENTATION
MAY NOT PROCEED YET
```

---

# 3. Frozen Week 1 Foundation

Week 1 remains an inherited engineering baseline.

Frozen / preserved capabilities include:

```text
Python application/package structure
PostgreSQL runtime
pgvector-enabled PostgreSQL infrastructure
SQLAlchemy
Alembic
FastAPI
worker baseline
Docker / Docker Compose
environment/settings conventions
pytest
PostgreSQL integration tests
Ruff
strict mypy
uv dependency lock
GitHub Actions
feature-branch workflow
```

Week 3 must not redesign these foundations merely for AI implementation convenience.

Week 3 may extend the application, but should treat Week 1 engineering foundations as stable infrastructure.

---

# 4. Frozen Week 2 Industrial Data Foundation

Week 2 is the trusted domain/data substrate for Week 3.

Frozen or inherited areas include:

```text
manufacturing operational schema
16-table operational model
migration semantics
deterministic synthetic generation
stable identifiers
Decimal handling
timezone-aware timestamps
dataset identity
canonical row ordering
canonical SHA-256 content hashing
dataset versioning
parent-before-child persistence
PostgreSQL acceptance
public data quality
CLI generation / validation
CI data acceptance
```

The default Week 3 rule is:

```text
DO NOT MODIFY C02 OPERATIONAL SCHEMA
```

unless a separately reviewed architecture blocker proves that the existing schema makes the authorized AI Loop impossible.

Week 3 must prefer an:

```text
APPLICATION-LEVEL SEMANTIC LAYER
```

over schema redesign.

---

# 5. Frozen Week 2 Scenario Foundation

Week 3 must reuse, not replace, the existing scenario semantics.

Existing scenario families:

```text
SUPPLIER DEGRADATION
QUALITY DETERIORATION
CAPACITY SURGE
```

They become the initial counterfactual simulation foundation.

Week 3 is allowed to create adapters around them.

Week 3 is not authorized to silently redefine:

```text
Supplier scenario behavior
Quality scenario behavior
Capacity scenario behavior
neutral-mode semantics
downstream propagation semantics
```

If incompatibility is discovered, Codex must stop and raise a contract blocker rather than alter scenario behavior.

---

# 6. Frozen Determinism and Canonicalization Boundary

Week 3 must reuse the existing Week 2 canonical identity foundation.

Frozen rules include:

```text
deterministic dataset generation
canonical row ordering
mapped-column ordering
Decimal normalization
UTC normalization
existing SHA-256 serialization
dataset version
dataset content hash
```

Explicit prohibition:

```text
NO SECOND COMPETING DATASET HASH ALGORITHM
```

Week 3 may introduce hashes for new Week 3 artifacts such as:

```text
snapshot_hash
context_hash
prompt_hash
artifact_hash
```

but these must not replace or reinterpret the canonical Week 2 dataset hash.

---

# 7. Protected HGT Boundary

The most important inherited safety invariant is:

```text
Operational Data != Hidden Ground Truth
```

HGT is authorized only for:

```text
offline evaluation
regression evaluation
causal-direction evaluation
```

HGT is forbidden from:

```text
StateSnapshot
DecisionContext
Evidence
Signal
Diagnosis
Candidate selection
Simulation input selection
Recommendation
LLM context
Public artifact
Operational database
```

Required direction:

```text
Operational Facts
        ↓
Runtime AI Decision Loop
        ↓
Recommendation
        ↓
Human / evaluation boundary
        ↓
HGT Evaluation
```

Architecture decision:

# AD-W03-001 — HGT remains outside the Runtime Decision Plane

**Status:** FROZEN

---

# 8. Week 2 Semantic Backlog Is Not a Week 2 Failure

Week 2 deliberately preserved several semantic limitations for Week 3.

They must not be silently repaired.

## 8.1 Post-rework release

Observed data does not include a formal post-rework release event.

Therefore:

```text
reworked
!=
formally released
```

Week 3 representation:

```text
quality_finality = UNKNOWN
```

---

## 8.2 Procurement / inventory relationship

Purchase Orders reference materials/suppliers, but do not directly allocate a particular PO to a particular Material Requirement / Work Order.

Therefore:

```text
MaterialRequirement → PurchaseOrder
NOT DIRECT
```

A relevant PO identified through material/time matching is:

```text
ASSOCIATIVE_EVIDENCE
```

not direct causal proof.

---

## 8.3 Route realism

A substantial subset of the synthetic population does not satisfy a strict preferred-route heuristic.

Week 3 must:

```text
USE ACTUAL RECORDED OPERATION SEQUENCE
```

and must not automatically convert route variation into an anomaly.

Initial semantic stance:

```text
ROUTE_VARIANCE = OBSERVED CONTEXT
```

Risk semantics remain a later W03-C03 decision.

---

## 8.4 Failed quantity / rework disposition gap

Some fully delivered orders contain failed quantities not completely explained by recorded rework.

Week 3 must not invent:

```text
scrap
replacement
concession
implicit rework
```

Initial representation:

```text
QUALITY_DISPOSITION_GAP = TRUE
quality_disposition = UNKNOWN
```

Architecture decision:

# AD-W03-002 — Semantic gaps are represented explicitly, not hidden by synthetic repair

**Status:** FROZEN

---

# 9. Week 3 Product Scope

Week 3 must remain narrow.

The single primary business loop is:

# Order Delivery Risk Decision Loop

It must eventually answer:

```text
1. What delivery risk exists for this order?
2. What evidence supports it?
3. What information is associative, uncertain or unknown?
4. What intervention candidates are authorized?
5. What happens under each permitted counterfactual?
6. Which candidate should be surfaced for human investigation?
7. What did the human decide?
8. How does protected HGT evaluate the recommendation offline?
```

Architecture decision:

# AD-W03-003 — Week 3 contains one primary decision loop

**Status:** FROZEN

No second business loop should be added during W3 unless separately authorized.

---

# 10. Week 3 v0 Product Mode

The first version is:

```text
OFFLINE
SHADOW
HUMAN-IN-THE-LOOP
```

The runtime may:

```text
READ authorized operational facts
BUILD an order-centric snapshot
CLASSIFY semantic trust
DETECT deterministic signals
BUILD structured diagnosis
SELECT from an authorized intervention registry
SIMULATE isolated counterfactuals
SCORE candidate outcomes
GENERATE a structured recommendation
EXPLAIN the recommendation
RECORD human ACCEPT / REJECT / DEFER
EVALUATE offline against protected HGT
REPLAY the decision
```

The runtime may not:

```text
modify SalesOrder
modify WorkOrder
modify PurchaseOrder
modify Delivery
perform automatic scheduling
perform automatic purchasing
replace suppliers automatically
perform automatic quality release
write operational truth
execute recommendations
```

Architecture decision:

# AD-W03-004 — W3 v0 is read / simulate / recommend, not execute

**Status:** FROZEN

---

# 11. Week 3 High-Level Runtime Architecture

Target architecture:

```text
PostgreSQL Operational Facts
            ↓
Decision-Time Snapshot Builder
            ↓
Immutable StateSnapshot
            ↓
Evidence / Semantic Trust Layer
            ↓
Deterministic Signal Detection
            ↓
Structured Diagnosis
            ↓
Authorized Intervention Registry
            ↓
Counterfactual Scenario Adapter
            ↓
Candidate Evaluation / Scoring
            ↓
RecommendationRecord
            ↓
DecisionPacket
            ↓
Bounded Explanation
            ↓
Human Decision Event
            ↓
Offline Evaluation Plane
            ↓
Feedback / Replay
```

This architecture is intentionally:

```text
evidence-first
deterministic-first
LLM-last
human-authoritative
```

Architecture decision:

# AD-W03-005 — Deterministic decision system precedes LLM explanation

**Status:** FROZEN

---

# 12. GPT / Codex / Human Separation

## GPT side

GPT is responsible for:

```text
architecture
contracts
semantic meaning
AI safety boundaries
context policy
material policy
prompt policy
tool policy
evaluation specification
checkpoint authorization design
independent implementation review
```

## Codex side

Codex is responsible for:

```text
implementation
tests
harness implementation
adapters
CI
authorized Git operations
Development Round Report generation
```

## Human / Product Owner

Human remains responsible for:

```text
business plausibility
risk usefulness
intervention usefulness
acceptable uncertainty
semantic interpretation
final checkpoint acceptance
```

Codex must never independently decide:

```text
what constitutes operational risk
what the true root cause is
what uncertainty is acceptable
whether a recommendation is operationally useful
```

Architecture decision:

# AD-W03-006 — Author, implementer, reviewer and approver remain separated

**Status:** FROZEN

---

# 13. Development Control Loop

Week 3 development uses:

```text
GPT Architecture / Contract Authorization
        ↓
Human Authorization
        ↓
Context Lock
        ↓
Codex Implementation
        ↓
Engineering Harness
        ↓
AI / Semantic Harness
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

Rules:

```text
NO REPORT
→ NOT REVIEW READY

NO GPT REVIEW
→ NOT HUMAN ACCEPTABLE

NO HUMAN ACCEPTANCE
→ NOT CLOSED

NO CLOSEOUT
→ NEXT CHECKPOINT NOT AUTHORIZED
```

Architecture decision:

# AD-W03-007 — No automatic checkpoint advancement

**Status:** FROZEN

---

# 14. Runtime Decision Loop and Development Loop Must Not Be Confused

Two different loops exist:

```text
DEVELOPMENT CONTROL LOOP
```

and:

```text
RUNTIME DECISION LOOP
```

Development materials such as:

```text
test expected outputs
scenario truth
review comments
implementation instructions
Codex prompts
```

must not automatically become runtime model context.

Architecture decision:

# AD-W03-008 — Development context and runtime context are separate trust domains

**Status:** FROZEN

This will be formalized during W03-G0-GPT-04.

---

# 15. Runtime Snapshot Boundary

Every future runtime Decision Run must bind:

```text
order_id
as_of_time
```

and create a frozen snapshot before downstream reasoning.

Required future rule:

```text
available_at <= as_of_time
```

for every runtime evidence item.

Downstream Signal / Diagnosis / Scoring / LLM components must not independently query live operational data for the same Decision Run.

Architecture decision:

# AD-W03-009 — One Decision Run operates on one immutable observation world

**Status:** FROZEN AT ARCHITECTURE LEVEL

Detailed fields and implementation contract remain for C01/C02.

---

# 16. LLM Boundary

Week 3 must not use:

```text
Database
↓
LLM
↓
Decision
```

Initial W3 LLM role:

```text
DecisionPacket
↓
Bounded LLM Explainer
↓
Structured Explanation
```

W3 v0 target permissions:

```text
LLM TOOL ACCESS = NONE
LLM DATABASE ACCESS = NONE
LLM HGT ACCESS = NONE
LLM OPERATIONAL WRITE = NONE
LLM CANDIDATE CREATION = NONE
LLM RECOMMENDATION AUTHORITY = NONE
```

Architecture decision:

# AD-W03-010 — Model explains; deterministic system decides

**Status:** FROZEN AT ARCHITECTURE LEVEL

Detailed prompt/tool contract remains for W03-G0-GPT-05 and C08.

---

# 17. Tool Boundary

Week 3 runtime capabilities will use:

```text
DENY BY DEFAULT
```

Initial capability classes:

```text
PURE
READ_ONLY
SIMULATION_ONLY
EVALUATION_ONLY
MUTATING
```

Architecture-level policy:

```text
PURE
allowed when explicitly registered

READ_ONLY
bounded and stage-authorized

SIMULATION_ONLY
isolated-state only

EVALUATION_ONLY
evaluation plane only

MUTATING
forbidden in W3 v0
```

Detailed tool registry semantics remain a later G0 task.

Architecture decision:

# AD-W03-011 — Tool permission is capability-based and deny-by-default

**Status:** FROZEN AT ARCHITECTURE LEVEL

---

# 18. Harness Boundary

Week 3 trust must not depend on model self-report or Codex self-report.

Three required layers:

```text
Engineering Test Harness
AI Evaluation Harness
Runtime Safety Harness
```

Minimum architectural gates:

```text
temporal leakage
HGT leakage
evidence provenance
semantic trust
unsupported causality
feature determinism
scenario direction
neutral stability
counterfactual isolation
no operational mutation
abstention
replay
output schema
grounding
```

Architecture decision:

# AD-W03-012 — Harness is the trust boundary

**Status:** FROZEN

Detailed capability-to-test matrix remains for W03-G0-GPT-07.

---

# 19. Explicit Week 3 Non-Goals

The following are outside the W3 v0 critical path:

```text
multi-agent architecture
autonomous operations
automatic scheduling
automatic purchasing
automatic supplier replacement
automatic quality release
self-retraining
memory agents
free-form tool use
vector DB as mandatory dependency
RAG as mandatory dependency
agentic operational writes
ERP integration
MES integration
production deployment
factory-wide optimization
multiple independent decision loops
```

They may be future extension points.

They must not become dependencies for W3 completion.

---

# 20. Scope-Creep Stop Rule

If a proposed W3 task requires any of the following, stop and request a separate architecture decision:

```text
change C02 operational schema
change migration semantics
change C03 canonical hashing
change existing scenario semantics
weaken HGT isolation
add operational writes
add autonomous action
add unrestricted LLM tools
add new business loop
silently repair Week 2 semantic backlog
change accepted Week 2 historical evidence
```

---

# 21. What W03-G0 Must Still Decide

W03-G0-GPT-01 freezes the architecture baseline, but G0 is not complete.

The following control domains remain open and must be completed before W03-C01 implementation authorization.

## G0-GPT-02 — AI Loop Constitution

Freeze:

```text
global W3 invariants
authority hierarchy
checkpoint governance
runtime safety principles
```

---

## G0-GPT-03 — Semantic Trust Contract

Freeze:

```text
trust vocabulary
allowed inference
forbidden inference
uncertainty propagation
semantic backlog treatment
```

---

## G0-GPT-04 — Context & Material Management

Freeze:

```text
DevelopmentContextManifest
DecisionContextManifest
Context hierarchy
Context Capsule
Context Lock
Context Delta
Material Registry
source priority
staleness policy
context reduction rules
```

---

## G0-GPT-05 — Prompt & Tool Execution Contract

Freeze:

```text
runtime LLM role
prompt hierarchy
allowed/forbidden inputs
allowed/forbidden claims
prompt version/hash
prompt injection boundary
tool capability classes
tool registry
tool permission matrix
failure paths
Codex development-tool policy
```

---

## G0-GPT-06 — Loop State Machine & Failure Policy

Freeze:

```text
runtime states
transition preconditions
failure states
retry rules
degraded-mode rules
fail-closed rules
abstention semantics
```

---

## G0-GPT-07 — Harness & Reporting Specification

Freeze:

```text
capability proof matrix
positive golden pack
negative/adversarial pack
detection rules
enforcement rules
Round Report schema
review evidence
```

---

## G0-GPT-08 — Sprint & Checkpoint Authorization Package

Freeze:

```text
C01-C10 scope
input/output contract per checkpoint
non-goals
acceptance criteria
stop conditions
expected final status
Git transition rules
```

---

# 22. Conditions for W03-C01 Authorization

W03-C01 implementation must not be authorized until all conditions below hold:

```text
G0-GPT-01 baseline review
COMPLETE

G0-GPT-02 constitution
FROZEN

G0-GPT-03 semantic trust
FROZEN

G0-GPT-04 context/material
FROZEN

G0-GPT-05 prompt/tool
FROZEN

G0-GPT-06 state-machine/failure
FROZEN

G0-GPT-07 harness/reporting
FROZEN

G0-GPT-08 sprint/checkpoint package
FROZEN

GPT G0 INDEPENDENT REVIEW
PASS

HUMAN G0 APPROVAL
YES
```

Only then:

```text
create feat/w03-ai-decision-loop
```

and begin:

```text
W03-C01-A
```

---

# 23. W03-G0-GPT-01 Findings

## BLOCKER

```text
NONE
```

for continuing GPT-side G0 design.

## HIGH

```text
NONE
```

at architecture baseline level.

## MEDIUM

The following are intentionally unresolved because they belong to later G0 tasks:

```text
formal semantic-trust rule table
context staleness thresholds
prompt contract
tool permission schema
runtime state transition table
retry/degradation policy
abstention thresholds
capability-test matrix
```

These are not implementation blockers yet because implementation remains unauthorized.

## LOW / INFORMATIONAL

```text
No W03 branch currently exists.
Current repository still identifies W3 as not started / not authorized.
The authoritative CURRENT_STATE document remains Week-2-oriented until a future authorized W03 governance publication.
```

---

# 24. Architecture Baseline Verdict

```text
W02 → W03 TRANSITION BASELINE:
VERIFIED

W03 PRIMARY LOOP:
FROZEN
ORDER DELIVERY RISK DECISION LOOP

W03 V0 MODE:
FROZEN
OFFLINE / SHADOW / HUMAN-IN-THE-LOOP

OPERATIONAL MUTATION:
PROHIBITED

RUNTIME HGT ACCESS:
PROHIBITED

FUTURE LEAKAGE:
PROHIBITED

W2 SCHEMA:
FROZEN BY DEFAULT

W2 CANONICAL HASHING:
FROZEN

W2 SCENARIO SEMANTICS:
FROZEN

SEMANTIC BACKLOG:
PRESERVE EXPLICITLY

DETERMINISTIC CORE:
REQUIRED

LLM ROLE:
EXPLANATION-ONLY TARGET

TOOL POLICY:
DENY-BY-DEFAULT TARGET

HUMAN FINAL AUTHORITY:
REQUIRED

CHECKPOINT AUTO-ADVANCE:
PROHIBITED
```

---

# 25. Task Status

```text
TASK:
W03-G0-GPT-01

STATUS:
COMPLETE

BASELINE:
VERIFIED

ARCHITECTURE BOUNDARY:
FROZEN FOR CONTINUATION OF G0

IMPLEMENTATION AUTHORIZATION:
NO

W03 BRANCH CREATION AUTHORIZATION:
NO

CODEX IMPLEMENTATION:
NOT AUTHORIZED

NEXT GPT TASK:
W03-G0-GPT-02
AI LOOP CONSTITUTION
```

---

# 26. Governing Principle

The outcome of this task is:

```text
FlowLens Week 3 will not begin by adding an LLM.

It will begin by defining a governed,
deterministic,
evidence-grounded,
replayable,
human-authoritative
industrial decision loop.

LLM capability is an optional bounded layer
inside that system,
not the system boundary itself.
```
