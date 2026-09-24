# FlowLens Industrial AI — W03 Sprint Specification

**Task:** W03-G0-GPT-08\
**Sprint:** Week 3 — Industrial AI Decision Loop Foundation\
**Baseline:** `main@9d18ddde9fe933952a2661ee1419f13c8577605d`\
**G0 Status:** READY FOR GPT FINAL REVIEW / HUMAN APPROVAL\
**Implementation:** NOT YET AUTHORIZED

---

## 1. Sprint Goal

Transform the verified Week 2 industrial-data/scenario foundation into one bounded, reproducible and human-reviewable decision loop:

# Order Delivery Risk Decision Loop

Week 3 must prove:

```text
OBSERVE
TRUST
DETECT
DIAGNOSE
SIMULATE
RECOMMEND
EXPLAIN
REVIEW
EVALUATE
REPRODUCE
PROTECT
```

---

## 2. Product Mode

```text
OFFLINE
SHADOW
HUMAN-IN-THE-LOOP
NO OPERATIONAL MUTATION
```

---

## 3. Runtime Architecture

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
Candidate Evaluation
↓
RecommendationRecord
↓
DecisionPacket
↓
Bounded Explanation
↓
HumanDecisionEvent
↓
Offline Evaluation / Replay
```

---

## 4. Sprint Non-Goals

```text
multi-agent
autonomous scheduling
automatic procurement
automatic supplier replacement
automatic quality release
self-retraining
memory agents
free-form LLM tools
mandatory vector DB
mandatory RAG
operational writes
ERP/MES integration
production deployment
factory-wide optimization
multiple business decision loops
```

---

## 5. Branch Policy

After G0 Human Approval only:

```text
main@9d18ddde9fe933952a2661ee1419f13c8577605d
↓
create feat/w03-ai-decision-loop
```

The older historical W2 branch must not be reused.

No force push.

No direct silent write to main.

---

## 6. Checkpoint Lifecycle

Every checkpoint:

```text
Cxx-A — GPT Architecture / Contract Authorization
↓
Human Authorization
↓
Context Lock
↓
Cxx-I — Codex Implementation
↓
Cxx-H — Harness Verification
↓
Exact-SHA CI
↓
Cxx-R — Development Round Report
↓
GPT Independent Review
↓
Human Acceptance
↓
Cxx-C — Closeout
↓
Next checkpoint
```

---

# 7. W03-C01 — Core AI Loop Contracts

## Goal

Define immutable runtime artifact schemas and the core type system.

## GPT Authorization Scope

Freeze semantic contracts for:

```text
DecisionRun
StateSnapshot
Evidence
EvidenceBundle
Signal
SignalBundle
DiagnosisRecord
InterventionCandidate
CandidateSet
SimulationResult
SimulationBundle
RecommendationRecord
DecisionPacket
ExplanationRecord
HumanDecisionEvent
RecommendationEvaluation
OutcomeEvaluation
```

Also freeze:

```text
artifact IDs
artifact versions
provenance
serialization
enums
state/status vocabularies
```

## Codex Scope

Implement types/contracts/tests only after authorization.

## Non-goals

```text
signal business thresholds
recommendation policy
LLM integration
ML
agents
schema migration
```

## Exit

Contracts serialize/validate deterministically and preserve frozen invariants.

---

# 8. W03-C02 — StateSnapshot + DecisionContext + Semantic Trust

## Goal

Build one decision-time order state without leakage.

## GPT Authorization Scope

Freeze:

```text
snapshot fields
as_of_time semantics
available_at semantics
freshness thresholds
trust mapping
unknown propagation
context reduction
```

## Codex Scope

Implement:

```text
StateSnapshot Builder
Evidence Builder
DecisionContext
Semantic Trust classification
snapshot identity/hash
```

## Harness

```text
future leakage
HGT leakage
provenance
staleness
trust correctness
determinism
replay
```

---

# 9. W03-C03 — Deterministic Signals + Diagnosis

## Goal

Detect delivery-risk evidence without free-form causal inference.

## GPT Authorization Scope

For each Signal freeze:

```text
trigger
required evidence
allowed trust levels
unknown behavior
reason code
forbidden inference
```

Signal vocabulary:

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

Freeze Diagnosis semantics.

## Codex Scope

Implement deterministic signal/diagnosis engine and tests.

---

# 10. W03-C04 — Intervention Registry + Scenario Adapter

## Goal

Connect authorized interventions to Week 2 scenario engine.

## GPT Authorization Scope

Freeze families:

```text
NO_ACTION
SUPPLIER_INTERVENTION
QUALITY_INTERVENTION
CAPACITY_INTERVENTION
```

Freeze allowed Candidate → Scenario mappings.

## Codex Scope

Implement registry, validation, adapters and isolated simulation wrappers.

## Harness

```text
registry-only candidates
baseline immutability
no operational mutation
scenario determinism
neutral stability
```

---

# 11. W03-C05 — Counterfactual Evaluation + Recommendation + DecisionPacket

## Goal

Close the deterministic decision loop through recommendation.

## GPT Authorization Scope

Freeze:

```text
evaluation dimensions
decision/scoring semantics
tie handling
abstention
NO_ACTION behavior
NO_RECOMMENDATION behavior
DecisionPacket semantics
```

G0 explicitly does not prescribe an arbitrary numeric confidence score.

## Codex Scope

Implement candidate evaluation, deterministic recommendation and DecisionPacket.

---

# 12. W03-C06 — Human Decision Workflow

## Goal

Record human authority without executing recommendations.

## GPT Authorization Scope

Freeze:

```text
ACCEPT
REJECT
DEFER
```

and `HumanDecisionEvent` semantics.

## Codex Scope

Implement append-only human decision records/workflow.

## Non-goal

Operational execution.

---

# 13. W03-C07 — Offline HGT Evaluation

## Goal

Evaluate frozen recommendations without leaking HGT into runtime.

## GPT Authorization Scope

Freeze metrics such as:

```text
cause-direction correctness
candidate relevance
recommendation coverage
false positives
neutral stability
```

## Codex Scope

Implement isolated Evaluation Plane and replay evaluation.

## Hard Rule

Runtime code cannot depend on HGT input.

---

# 14. W03-C08 — Bounded LLM Explanation

## Goal

Add human-readable explanation without adding decision authority.

## GPT Authorization Scope

Freeze actual:

```text
runtime system prompt
prompt version/hash
input schema
output schema
allowed claims
forbidden claims
fallback
injection handling
provider/model policy
```

## Runtime Policy

```text
LLM TOOL ACCESS = NONE
LLM DB ACCESS = NONE
LLM HGT ACCESS = NONE
LLM RECOMMENDATION AUTHORITY = NONE
```

## Codex Scope

Implement adapter/schema/explainer, validation and fallback.

---

# 15. W03-C09 — AI Loop CI / Regression Hardening

## Goal

Make all Week 3 trust gates reproducible in CI.

## GPT Authorization Scope

Audit capability coverage.

## Codex Scope

Integrate:

```text
engineering tests
semantic gates
temporal/HGT gates
counterfactual isolation
determinism/replay
abstention
LLM grounding/schema
negative/adversarial pack
```

---

# 16. W03-C10 — Business Acceptance & Closeout

## Goal

Perform end-to-end Product Owner acceptance.

Review:

```text
state interpretability
risk usefulness
evidence usefulness
honesty of uncertainty
intervention usefulness
counterfactual clarity
recommendation usefulness
explanation faithfulness
human-review ergonomics
replayability
```

C10 requires Human acceptance.

Codex cannot determine business acceptance.

---

## 17. Roles

### GPT

```text
architecture
contracts
semantics
prompt/tool policy
harness specification
authorization design
independent review
```

### Codex

```text
implementation
tests
harness code
adapters
CI
authorized Git
Round Reports
```

### Human

```text
business interpretation
final authorization
final acceptance
```

---

## 18. Stop Conditions

Immediately stop a checkpoint for:

```text
contract conflict
semantic/product decision not authorized
schema/migration change requirement
canonical hash change requirement
scenario semantic change requirement
HGT leakage
future leakage
operational mutation
unauthorized tool access
scope expansion into another business loop
```

---

## 19. W3 Exit Criteria

```text
OBSERVE:
order state reconstructed at as_of_time

TRUST:
direct/derived/associative/unknown/forbidden distinguished

DETECT:
Supplier/Quality/Capacity/Delivery signals supported

DIAGNOSE:
structured evidence-backed diagnosis

SIMULATE:
baseline vs authorized counterfactual

RECOMMEND:
deterministic RecommendationRecord + DecisionPacket

EXPLAIN:
grounded bounded explanation

REVIEW:
Human ACCEPT / REJECT / DEFER

EVALUATE:
protected offline evaluation

REPRODUCE:
stable deterministic replay

PROTECT:
no HGT leakage
no future leakage
no operational mutation
no unauthorized capability
```

---

## 20. G0 Gate

Before C01 implementation:

```text
G0 documents complete
GPT G0 final review PASS FOR HUMAN APPROVAL
Human G0 approval YES
```

Only then create the W03 feature branch.

---

## 21. Current Status

```text
G0 AUTHORING:
COMPLETE

GPT FINAL REVIEW:
PENDING IN SEPARATE REVIEW ARTIFACT

HUMAN G0 APPROVAL:
PENDING

W03 BRANCH:
NOT CREATED

C01 IMPLEMENTATION:
NOT AUTHORIZED
```

---

## 22. G0-R1 Repository Projection Requirement

Before G0 can be closed and before `feat/w03-ai-decision-loop` can be created, repository execution surfaces must be aligned:

```text
AGENTS.md
→ updated to W3 concise router

LOOP.md
→ added as thin router only

skills/
→ policy directory only; no executable project Skill required

CURRENT_STATE
→ updated to the true post-G0 publication state
```

Therefore the final G0 sequence is:

```text
G0 Architecture Contracts
↓
G0-R1 Repository Execution Projection
↓
GPT Final Re-review
↓
Human Approval
↓
Repository Publication
↓
Publication Verification
↓
G0 CLOSED
↓
Create W03 Feature Branch
↓
W03-C01-A
```
