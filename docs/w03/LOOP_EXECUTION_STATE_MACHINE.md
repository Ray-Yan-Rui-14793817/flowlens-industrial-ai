# FlowLens Industrial AI — W03 Loop Execution State Machine

**Task:** W03-G0-GPT-06A\
**Status:** FROZEN FOR G0 HUMAN REVIEW\
**Baseline:** `main@9d18ddde9fe933952a2661ee1419f13c8577605d`

---

## 1. Purpose

The Runtime Decision Loop is a state machine, not an informal function pipeline.

Every transition must have:

```text
preconditions
input artifacts
output artifacts
allowed caller
success state
failure state
```

Runtime state and Evaluation state are intentionally separated so protected HGT cannot flow back into runtime recommendation.

---

## 2. Runtime Decision States

```text
CREATED
↓
SNAPSHOT_BUILDING
↓
SNAPSHOT_READY
↓
TRUST_CHECKING
↓
TRUST_VERIFIED
↓
SIGNALS_READY
↓
DIAGNOSIS_READY
↓
CANDIDATES_READY
↓
SIMULATION_READY
↓
RECOMMENDATION_READY
↓
PACKET_READY
↓
EXPLANATION_READY
↓
HUMAN_PENDING
↓
HUMAN_DECIDED
↓
RUNTIME_COMPLETE
```

---

## 3. Evaluation Plane States

Recommendation evaluation is a sidecar plane.

It may begin only after the RecommendationRecord is frozen.

```text
EVAL_NOT_STARTED
↓
RECOMMENDATION_EVAL_READY
↓
RECOMMENDATION_EVALUATED
```

Outcome/feedback evaluation is later:

```text
OUTCOME_PENDING
↓
OUTCOME_AVAILABLE
↓
OUTCOME_EVALUATED
```

Protected HGT is available only inside these evaluation states.

Evaluation output may be recorded for learning/audit, but may not retroactively alter the already-frozen RecommendationRecord for the original run.

---

## 4. Runtime Artifacts

```text
DecisionRun
StateSnapshot
EvidenceBundle
SignalBundle
DiagnosisRecord
CandidateSet
SimulationBundle
RecommendationRecord
DecisionPacket
ExplanationRecord
HumanDecisionEvent
```

Evaluation artifacts:

```text
RecommendationEvaluation
OutcomeEvaluation
FeedbackRecord
```

Each artifact is immutable after publication.

Corrections create a new version or new run.

---

## 5. State Transition Table

| From | To | Required condition | Primary output |
|---|---|---|---|
| CREATED | SNAPSHOT_BUILDING | order_id + as_of_time valid | DecisionRun |
| SNAPSHOT_BUILDING | SNAPSHOT_READY | temporal/HGT/context gates pass | StateSnapshot |
| SNAPSHOT_READY | TRUST_CHECKING | snapshot frozen | Evidence candidates |
| TRUST_CHECKING | TRUST_VERIFIED | semantic trust gate pass | EvidenceBundle |
| TRUST_VERIFIED | SIGNALS_READY | signal contract available | SignalBundle |
| SIGNALS_READY | DIAGNOSIS_READY | grounded signals | DiagnosisRecord |
| DIAGNOSIS_READY | CANDIDATES_READY | registry policy passes | CandidateSet |
| CANDIDATES_READY | SIMULATION_READY | permitted candidates evaluated | SimulationBundle |
| SIMULATION_READY | RECOMMENDATION_READY | decision/scoring policy passes or abstains | RecommendationRecord |
| RECOMMENDATION_READY | PACKET_READY | packet schema/provenance pass | DecisionPacket |
| PACKET_READY | EXPLANATION_READY | template or LLM explanation valid | ExplanationRecord |
| EXPLANATION_READY | HUMAN_PENDING | human-review package complete | review package |
| HUMAN_PENDING | HUMAN_DECIDED | ACCEPT/REJECT/DEFER event recorded | HumanDecisionEvent |
| HUMAN_DECIDED | RUNTIME_COMPLETE | append-only event persisted | final runtime state |

---

## 6. Hard Runtime Failure States

```text
BLOCKED_CONTEXT
BLOCKED_TEMPORAL
BLOCKED_HGT
BLOCKED_TRUST
BLOCKED_CONTRACT
```

These are fail-closed.

No recommendation is produced.

---

## 7. Bounded / Degraded States

```text
BLOCKED_INSUFFICIENT_EVIDENCE
SIMULATION_PARTIAL
SIMULATION_FAILED
NO_RECOMMENDATION
EXPLANATION_DEGRADED
```

These may produce a human-reviewable packet only when the Failure Policy explicitly allows it.

A degraded packet must expose the degraded state.

---

## 8. Snapshot Rule

At `SNAPSHOT_READY`:

```text
snapshot_id
snapshot_hash
as_of_time
dataset_version
dataset_hash
```

are frozen.

Downstream components may not mutate the snapshot.

---

## 9. Recommendation Freeze

At `RECOMMENDATION_READY`:

```text
RecommendationRecord
```

is immutable.

The LLM may not change:

```text
selected_candidate
candidate ordering
score
reason-code family
uncertainty status
```

---

## 10. Human Decision Event

Human decisions are append-only events.

A later decision creates a new event.

Example:

```text
event 1: DEFER
event 2: ACCEPT
```

Do not overwrite the first event.

---

## 11. No Operational Execution State

W3 deliberately contains no:

```text
EXECUTING
PROCUREMENT_WRITE
SCHEDULE_WRITE
SUPPLIER_SWITCH
QUALITY_RELEASE
DELIVERY_UPDATE
```

state.

Recommendation ends at human review / recorded decision.

Operational execution belongs outside W3 v0.

---

## 12. Replay Rule

A deterministic replay binds:

```text
dataset version/hash
snapshot id/hash
code version
feature version
signal version
scenario version
decision-policy version
tool-registry version
```

Expected:

```text
same deterministic inputs
→ same deterministic artifacts
```

LLM explanation requires semantic reproducibility rather than byte identity.

---

## 13. Status

```text
RUNTIME STATE MACHINE:
FROZEN

EVALUATION PLANE:
SEPARATED

IMMUTABLE ARTIFACT MODEL:
FROZEN

OPERATIONAL EXECUTION STATE:
ABSENT BY DESIGN

IMPLEMENTATION:
NOT AUTHORIZED
```
