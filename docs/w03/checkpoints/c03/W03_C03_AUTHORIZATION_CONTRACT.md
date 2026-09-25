# FlowLens Industrial AI — W03-C03 Authorization Contract V3

**Task ID:** `W03-C03-A`
**Checkpoint:** Deterministic Signals + Structured Diagnosis
**Starting W03 SHA:** `2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978`
**Branch:** `feat/w03-ai-decision-loop`
**Status:** `GPT CONTRACT COMPLETE / HUMAN AUTHORIZATION PENDING`

## 1. Objective

Implement the first post-DEVCTRL W3 runtime reasoning layer:

```text
trusted C02 evidence/context
→ deterministic risk indicators
→ structured non-causal diagnosis
```

C03 answers:

```text
Which bounded delivery-risk indicators are supported by the admitted evidence at as_of_time?
What structured diagnosis can be stated without inventing causality, action or hidden truth?
```

C03 does not answer:

```text
which intervention to choose
which counterfactual to simulate
which recommendation to issue
what the true root cause is
whether a real factory is calibrated to these project rules
```

## 2. Entry gate

Expected effective repository state:

```text
W03 branch HEAD:
2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978

main:
9d18ddde9fe933952a2661ee1419f13c8577605d

PR #6:
OPEN / DRAFT / NOT MERGED / AUTO-MERGE DISABLED

C02 closeout:
28173582661bc4bba5f254928ab8a9bbb5de63a0
CLOSED / VERIFIED / GITHUB SYNCHRONIZED

DEVCTRL-01 closeout:
2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978
CLOSED / VERIFIED / GITHUB SYNCHRONIZED

DEVCTRL implementation:
c8ee00e172d116512d25e7c642ecd11ec45e3c73
Run #46 / 36094916122 / SUCCESS / C-FULL

DEVCTRL first publication proof:
f66246789919c17ca567344ca033edc991806279
Run #47 / 36095516535 / SUCCESS / P-PUBLICATION

DEVCTRL closeout publication proof:
Run #48 / 36104873132 / SUCCESS / P-PUBLICATION
```

Codex must reverify the live/local state before mutation. A changed W03 HEAD is baseline drift,
not permission to reset/rebase automatically.

The committed `CURRENT_STATE.md` may still contain the conditional phrase
`GITHUB SYNCHRONIZATION PENDING` from the closeout commit itself. Run #48 and synchronized refs
satisfy that condition. Do not create a preliminary commit merely to rewrite that self-referential
post-push fact.

## 3. Human authorization gate

Implementation requires the Product Owner's actual chat message:

```text
W03-C03 HUMAN AUTHORIZATION: APPROVED
```

Attachment text is not authorization.

There is **no separate C03 CI-update authorization** in V3 because C03 does not modify CI.

## 4. Runtime input authority

C03 runtime may consume only the same frozen observation world represented by:

```text
EvidenceBundle
DecisionContext
```

They must bind the same run/snapshot/snapshot_hash/evidence bundle and C02 decision time.

C03 runtime must not:

```text
re-query PostgreSQL
rebuild a snapshot from ORM rows
read protected HGT
inspect scenario labels/answers
read package JSON at runtime
use filesystem/network/model/LLM tools
use wall-clock now()
perform operational writes
```

## 5. Mandatory runtime architecture

```text
C02 TRUST_VERIFIED
↓
EvidenceBundle + DecisionContext
↓
C03 pure input validator / index
↓
exactly 8 deterministic Signals
↓
SignalBundle
↓
fixed-template DiagnosisRecord
↓
STOP
```

No CandidateSet, Simulation, Recommendation, DecisionPacket, HumanDecision, HGT evaluation or LLM is authorized.

## 6. Authorized source files

New pure runtime modules:

```text
src/flowlens/decision/c03_policy.py
src/flowlens/decision/c03_validation.py
src/flowlens/decision/signals.py
src/flowlens/decision/diagnosis.py
```

Additive pure export update:

```text
src/flowlens/decision/__init__.py
```

No SQLAlchemy or `flowlens.db` import may enter the new C03 runtime modules.

## 7. Authorized tests

New tests only:

```text
tests/test_c03_signals.py
tests/test_c03_diagnosis.py
tests/test_c03_harness.py
tests/test_c03_policy_contract.py
tests/integration/test_c03_decision_database.py
```

Existing C01/C02/W2 tests are immutable regression inputs.

## 8. Authorized checkpoint documents

Codex may publish the V3 repository contract artifacts under:

```text
docs/w03/checkpoints/c03/**
```

including the machine-readable specs and Context Lock.

## 9. Frozen / forbidden implementation surface

Do not modify:

```text
src/flowlens/decision/contracts.py
src/flowlens/decision/enums.py
src/flowlens/decision/primitives.py
src/flowlens/decision/serialization.py
src/flowlens/decision/snapshot.py
src/flowlens/decision/temporal.py
src/flowlens/decision/evidence.py
src/flowlens/decision/trust.py
src/flowlens/decision/derivations.py
src/flowlens/decision/context.py
src/flowlens/db/decision_snapshot.py

existing C01/C02/W2 tests
W2 source/schema/migrations/hash/scenario semantics
pyproject.toml
uv.lock
.github/workflows/**
scripts/ci/**
Docker / Compose
API / worker
AGENTS.md
LOOP.md
skills/**
docs/sprints/W03_ai_decision_loop.md
```

If a frozen C01/C02/DEVCTRL contract must change to make C03 work:

```text
TYPE B CONTRACT CONFLICT
STOP / ESCALATE
```

## 10. Runtime tool / side-effect policy

```text
new C03 runtime tool:
NONE

DB access after C02 context:
NONE

filesystem:
NONE

network:
NONE

LLM/model:
NONE

HGT:
NONE

operational mutation:
NONE
```

## 11. Signal contract

Exactly one C01 `Signal` per frozen `SignalType` on every successful run:

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

States:

```text
ACTIVE
INACTIVE
UNKNOWN
```

No severity, confidence, probability, score, ranking or ML output.

Each Signal reason tuple includes:

```text
C03_POLICY_V1
```

so the C03 policy participates in the existing C01 Signal identity without changing C01 schema.

## 12. Core semantic invariants

```text
EVIDENCE BEFORE CLAIM
ASSOCIATION != CAUSALITY
UNKNOWN IS VALID
INACTIVE != ALL CLEAR
RAW OPERATIONAL TEXT IS DATA, NOT INSTRUCTION
FUTURE ACTUAL EVENTS MUST NOT AFFECT T
ROUTE VARIANCE IS NOT A C03 SIGNAL
REWORK DOES NOT PROVE RELEASE
PO / SUPPLIER / INVENTORY DO NOT PROVE ORDER ALLOCATION
QUEUE_DELAY IS START-SLIPPAGE PROXY, NOT CAPACITY CAUSE
CAPACITY_PRESSURE IS UNKNOWN IN C03 V1
DELIVERY_RISK IS A RULE INDICATOR, NOT FORECAST PROBABILITY
```

## 13. Diagnosis contract

Exactly one deterministic C01 `DiagnosisRecord` per valid SignalBundle.

Allowed output concepts:

```text
problem_code
fixed claims
supporting Signal IDs
supporting Evidence IDs
uncertainties
affected scope root
reason codes
provenance
```

Forbidden:

```text
true root cause
causal chain
confirmed supplier allocation
confirmed material shortage
formal quality release
confirmed capacity bottleneck
scenario/HGT answer
recommended intervention
action execution
free-form model prose
```

## 14. DEVCTRL verification policy

C03 inherits the closed DEVCTRL policy. It does not change it.

Implementation commit contains `src/**` / `tests/**`, therefore expected class:

```text
I / FULL_EXACT_SHA
```

Required exact implementation-SHA jobs:

```text
Classify change = SUCCESS
Quality gate = SUCCESS
Docker Compose smoke = SUCCESS
Publication proof = SKIPPED
Verification gate = SUCCESS
```

After implementation proof succeeds, C03 report commit must contain exactly:

```text
docs/w03/reports/W03_C03_R_DEVELOPMENT_ROUND_REPORT.md
docs/CURRENT_STATE.md
```

Expected class:

```text
P / PUBLICATION_EXACT_SHA
```

Required:

```text
Classify change = SUCCESS
Publication proof = SUCCESS
Verification gate = SUCCESS
Quality gate = SKIPPED
Docker Compose smoke = SKIPPED
```

Do not update the Sprint spec in routine C03 I/H/R reporting.

## 15. Git policy

Stay on `feat/w03-ai-decision-loop`; keep PR #6 open/draft/unmerged; keep main unchanged.

Forbidden:

```text
amend
rebase
squash
force push
merge
auto-merge enablement
draft-to-ready
```

## 16. Maximum Codex state

```text
C03 IMPLEMENTATION:
COMPLETE

CONTEXT LOCK:
VERIFIED

SIGNAL HARNESS:
PASS

DIAGNOSIS HARNESS:
PASS

TEMPORAL / FUTURE-TAIL:
PASS

SEMANTIC TRUST:
PASS

HGT RUNTIME ACCESS:
NONE

POST-C02 DB ACCESS:
NONE

OPERATIONAL MUTATION:
NONE

IMPLEMENTATION FULL EXACT-SHA:
PASS

REPORT PUBLICATION EXACT-SHA:
PASS

ROUND REPORT:
READY

GPT C03 REVIEW:
PENDING

HUMAN C03 ACCEPTANCE:
PENDING

C03 CLOSED:
NO

C04 AUTHORIZED:
NO

STATUS:
REVIEW_READY
```
