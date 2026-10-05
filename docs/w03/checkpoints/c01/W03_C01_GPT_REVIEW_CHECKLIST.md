# FlowLens Industrial AI — W03-C01 GPT Independent Review Checklist

**Use after Codex returns `STATUS: REVIEW_READY`.**

## 1. Evidence required

GPT review requires:

```text
W03-C01 authorization contract
actual Context Lock
implementation SHA
implementation diff
focused test results
full regression result
Harness summary
exact-SHA CI run
Development Round Report
Git/PR state
```

Missing required evidence means:

```text
REVIEW RESULT: NOT REVIEWABLE
```

## 2. Scope review

Verify no unauthorized changes to:

```text
W2 schema / migrations
W2 generator / canonical hash
W2 scenarios / HGT
data persistence
API / worker
dependencies
CI workflow
Docker
AGENTS / LOOP / G0 contracts
```

## 3. Contract review

For every artifact verify:

```text
schema matches C01
immutable
typed
deterministic identity
deterministic serialization
provenance present
mutable containers absent
implementation_sha accepts only 40/64-character lowercase Git OIDs
artifact/dataset/snapshot/scenario hashes remain 64-character SHA-256
```

## 4. Boundary review

Verify absence of:

```text
Snapshot Builder
DecisionContext
signal threshold/business detection
Diagnosis engine
Candidate registry behavior
Scenario adapter
scoring/recommendation behavior
HumanDecision persistence workflow
HGT evaluator
LLM
agent
runtime tool
```

## 5. Semantic review

Verify:

```text
TrustLevel exact G0 vocabulary
association not upgraded to causality
UNKNOWN vocabulary preserved
DecisionPacket contains no HumanDecision mutation
HumanDecisionEvent is append-only schema
Evaluation types remain protected-plane schemas
Recommendation structure invents no scoring semantics
selected_candidate_id, when present, occurs in candidate_order
```

## 6. Safety review

Verify:

```text
runtime HGT imports = NONE
runtime HGT fields = NONE
future-leakage structural gate enforced
StateSnapshot unknowns have no downstream Evidence IDs
operational mutation = NONE
DB side effect = NONE
external network capability = NONE
```

## 7. Determinism review

Require evidence for:

```text
same identity → same ID
changed identity → changed ID
same snapshot semantics → same snapshot hash
producer SHA change alone → same snapshot hash
same artifact → same canonical bytes
float rejected
naive datetime rejected
canonical bundle ordering stable
```

## 8. CI review

Exact implementation SHA must match successful CI:

```text
Quality gate: PASS
Docker Compose smoke: PASS
```

Older G0 CI is not C01 implementation evidence.

## 9. Allowed GPT outcomes

```text
PASS FOR HUMAN ACCEPTANCE
REPAIR REQUIRED
BLOCKED
```

Do not close C01 in the GPT review.

A repair remains within C01 under a bounded repair contract.

## 10. Human gate

After GPT PASS, Human may:

```text
ACCEPT
REJECT
DEFER
```

Only Human ACCEPT permits a future documentation-only `W03-C01-C1` closeout.

C02 remains unauthorized until C01 is CLOSED.
