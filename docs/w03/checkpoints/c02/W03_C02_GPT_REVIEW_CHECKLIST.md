# FlowLens Industrial AI — W03-C02 GPT Independent Review Checklist

**Use only after Codex returns `STATUS: REVIEW_READY`.**

## 1. Required evidence

```text
C02 authorization package
actual C02 Context Lock
implementation SHA
implementation diff
focused C02 results
C01 regression results
full/non-integration regression
PostgreSQL integration result
Harness summary
exact-SHA CI
Development Round Report
Git/PR state
```

Missing required evidence:

```text
NOT REVIEWABLE
```

## 2. Scope

Verify no unauthorized changes to:

```text
W1/W2 source semantics
W2 schema/migrations
W2 canonical hashing
scenario/HGT semantics
C01 kernel files
C01 tests
dependencies
CI workflow
Docker
API/worker
AGENTS.md
LOOP.md
skills/
```

`flowlens.decision.__init__.py` may contain additive DB-free exports only.

## 3. Architecture split

Required:

```text
flowlens.decision import
→ does not load flowlens.db / sqlalchemy / scenarios / openai

PostgreSQL adapter
→ src/flowlens/db/decision_snapshot.py

decision core
→ no SQLAlchemy/database import
```

Failure is HIGH/BLOCKING.

## 4. Source matrix

Review every admitted field against the frozen whitelist.

Particularly verify:

```text
status fields absent
future actual fields masked/excluded
generated_at absent
unrelated orders absent
procurement/inventory association only through MR material IDs
```

## 5. Temporal review

Verify:

```text
available_at exact
observed_at exact
event boundary equality accepted
one microsecond before excluded
as_of period bound
order_at bound
future-tail normalized metamorphic pass
```

Do not require cross-dataset artifact-ID equality.

## 6. Semantic Trust review

Verify:

```text
direct graph → DIRECT_FACT
PO/Supplier/Inventory → ASSOCIATIVE_EVIDENCE
derived association never upgraded
FORBIDDEN_INFERENCE not emitted
limitations present
UNKNOWN preserved
```

## 7. Inventory / quality

Verify exact:

```text
24h / 7d freshness boundaries
stale/expired limitation
missing inventory uncertainty
current availability unknown when no fresh evidence

quality finality unknown after inspection
failed quantity gap unknown
rework never implies release
```

## 8. DecisionContext

Verify:

```text
schema/version exact
all selected Evidence exists
partitions disjoint
union exact
uncertainties preserved
conflicts preserved
limitations preserved
deterministic ID/bytes
```

## 9. PostgreSQL safety

Verify:

```text
REPEATABLE READ
READ ONLY
explicit-column runtime queries
no status column selection
no DML
no mutation
one transaction
no DB after snapshot
```

## 10. HGT boundary

Verify new runtime source does not:

```text
import HGT
read protected manifest
use scenario label
use true root cause
```

Scenario fixtures may use business datasets only.

## 11. C02/C03 boundary

Reject implementation if C02 contains:

```text
risk thresholds
signal activation
diagnosis
route anomaly
candidate selection
simulation
scoring
recommendation
```

## 12. Allowed GPT outcomes

```text
PASS FOR HUMAN ACCEPTANCE
REPAIR REQUIRED
BLOCKED
```

GPT review does not close C02.

Only Human ACCEPT after GPT PASS may authorize future documentation-only C02 closeout.

C03 remains unauthorized until C02 is CLOSED.
