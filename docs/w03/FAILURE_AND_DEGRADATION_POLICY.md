# FlowLens Industrial AI — W03 Failure, Retry, Degradation & Abstention Policy

**Task:** W03-G0-GPT-06B\
**Status:** FROZEN FOR G0 HUMAN REVIEW\
**Baseline:** `main@9d18ddde9fe933952a2661ee1419f13c8577605d`

---

## 1. Purpose

Failures must have deterministic system behavior.

A detected failure without a defined response is not a complete safety control.

---

## 2. Development Failure Classes

### TYPE A — IMPLEMENTATION FAILURE

Examples:

```text
bug
typing error
serialization defect
query defect
test failure
CI configuration defect
```

Policy:

```text
AUTO-REPAIR ALLOWED
```

within the authorized scope.

---

### TYPE B — CONTRACT CONFLICT

Examples:

```text
frozen contract cannot be implemented
schema cannot express authorized contract
two authoritative contracts conflict
scenario API cannot satisfy contract
```

Policy:

```text
STOP
ESCALATE
NO SILENT CONTRACT CHANGE
```

---

### TYPE C — SEMANTIC / PRODUCT DECISION

Examples:

```text
Should associative evidence affect supplier risk?
Should UNKNOWN suppress a recommendation?
Which intervention is operationally useful?
```

Policy:

```text
STOP
REVIEWER QUESTION
```

---

### TYPE D — SAFETY BOUNDARY VIOLATION

Examples:

```text
HGT runtime leakage
future leakage
operational mutation
protected material exposure
unauthorized tool access
```

Policy:

```text
IMMEDIATE ABORT
NOT REVIEW READY
```

---

## 3. Runtime Fail-Closed Conditions

| Failure | Required behavior |
|---|---|
| Context classification violation | abort run |
| Future evidence admitted | abort run |
| HGT admitted into runtime | abort run |
| Semantic trust cannot be established for critical claim | no recommendation / abort depending stage |
| Forbidden inference detected | reject artifact |
| Unauthorized tool request | deny + audit |
| Operational write attempted | deny + hard failure |

---

## 4. Runtime Degradation Conditions

### One candidate simulation fails

```text
candidate_status = UNAVAILABLE
```

Continue only if:

- at least one valid comparable candidate remains;
- the packet exposes the failed candidate;
- recommendation policy permits partial comparison.

---

### All candidate simulations fail

```text
NO_RECOMMENDATION
```

Do not fall back to guessed recommendation.

---

### LLM unavailable

Use:

```text
deterministic template explanation
```

Recommendation remains unchanged.

---

### LLM output schema invalid

Policy:

```text
one bounded repair/retry attempt
```

if C08 authorizes it.

If still invalid:

```text
discard LLM output
use deterministic template
EXPLANATION_DEGRADED
```

---

### LLM grounding / unsupported-claim gate fails

```text
discard explanation
use deterministic template
```

Do not repair by changing recommendation.

---

### Offline evaluator fails

```text
recommendation remains frozen
evaluation_status = FAILED or PENDING
```

Runtime decision artifact remains auditable.

---

## 5. Retry Policy

Retries must be:

```text
bounded
stage-specific
audited
non-mutating
```

No unbounded retry loops.

Default G0 policy:

- deterministic pure computation: one immediate deterministic rerun may be used only for infrastructure/transient execution failure, not logic disagreement;
- database read: bounded retry only if Snapshot Builder semantics remain identical and no partial snapshot is accepted;
- simulation: checkpoint-specific bounded retry;
- LLM: maximum one schema-repair retry in W3 v0;
- unauthorized action: never retry automatically.

Exact counts may be narrowed by checkpoint contract.

---

## 6. Abstention Policy

Abstention is a valid outcome.

Minimum policies:

### Critical direct evidence missing

```text
NO_RECOMMENDATION
or
DEFER_TO_HUMAN
```

### Only associative evidence supports a material causal claim

```text
INVESTIGATION_ONLY
```

Do not claim cause.

### Quality finality unknown

No recommendation that presumes formal release.

### Unresolved critical evidence conflict

```text
DEFER
```

or `NO_RECOMMENDATION`.

### No candidate materially improves the modeled outcome

```text
NO_ACTION
```

may be selected if the C05 policy authorizes it.

---

## 7. Confidence Semantics

W3 G0 does not authorize an arbitrary numeric confidence score.

Until a later contract defines calibration:

```text
confidence
```

must not imply statistical probability.

Use explicit evidence/trust/uncertainty states instead.

---

## 8. Error Visibility

Degraded or blocked states must be visible in:

```text
DecisionPacket
Round Report where applicable
audit logs
Harness Summary
```

The system must not report a clean PASS while hiding a degraded dependency.

---

## 9. Safety Recovery

A Safety Boundary Violation requires:

```text
stop
capture evidence
do not auto-close
do not auto-retry into a different semantic path
raise architecture/security review
```

---

## 10. Status

```text
DEVELOPMENT FAILURE TAXONOMY:
FROZEN

FAIL-CLOSED POLICY:
FROZEN

DEGRADATION POLICY:
FROZEN

ABSTENTION FRAMEWORK:
FROZEN

NUMERIC BUSINESS THRESHOLDS:
DEFERRED TO CHECKPOINT CONTRACTS

IMPLEMENTATION:
NOT AUTHORIZED
```
