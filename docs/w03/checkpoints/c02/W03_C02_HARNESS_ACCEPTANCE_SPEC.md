# FlowLens Industrial AI — W03-C02 Harness & Acceptance Specification

**Contract:** `w03-c02-harness.v1`

## 1. Capability proof matrix

| Capability | Invariant | Required proof | Failure action |
|---|---|---|---|
| Entry gate | C01 closed baseline exact | preflight/Git evidence | stop |
| DB reader | `flowlens.db.decision_snapshot` only; REPEATABLE READ + READ ONLY | PostgreSQL integration | abort |
| Decision core import | `flowlens.decision` remains DB/SQLAlchemy-free | frozen C01 regression + subprocess import | hard fail |
| Source scope | order-centric explicit fields only | SQL/source audit | fail |
| Raw status exclusion | no non-bitemporal status enters runtime | negative tests / SQL audit | fail |
| Temporal projector | unavailable field never admitted | boundary tests | abort |
| SQL future masking | future actual values absent from Python projection | integration tests | abort |
| Snapshot | deterministic immutable identity | replay/hash tests | fail |
| HGT isolation | no protected source/import/read | source/import/runtime audit | abort |
| Evidence | exact source binding/provenance | completeness tests | reject |
| Trust | direct remains direct | semantic fixtures | reject |
| Trust | association never upgraded | adversarial fixtures | reject |
| Derivation | trust monotonic | direct/associative derivation tests | reject |
| Inventory freshness | 24h/7d boundaries exact | boundary tests | fail |
| Quality | rework never equals release | negative semantic tests | fail |
| Unknown | missing/stale/quality gaps explicit | fixture tests | fail |
| Conflict | contradictory direct paths preserved | conflict fixtures | fail |
| DecisionContext | exact trust partitions | context tests | fail |
| Context | no FORBIDDEN evidence | negative tests | fail |
| Replay | same dataset/run → same bytes/IDs | replay | fail |
| Future-tail metamorphic | future tail cannot change visible T semantics | normalized comparison | abort |
| Operational mutation | none | DB before/after + SQL audit | hard fail |

## 2. Required unit test files

Authorized:

```text
tests/test_decision_temporal.py
tests/test_decision_evidence.py
tests/test_decision_context.py
```

Suggested responsibility:

### test_decision_temporal.py

At minimum:

```text
master baseline/effective availability
plan proxy availability
future WorkOrder actual_start masked
future WorkOrder actual_end/completed masked
future Operation actual timestamps masked
future PO receipt/received quantity masked
future Rework end masked
future Delivery excluded
future Inspection excluded
future Inventory excluded

as_of == event time → admitted
as_of one microsecond before event → excluded

raw statuses never become SnapshotEntry
generated_at never becomes business available_at
```

### test_decision_evidence.py

At minimum:

```text
source Evidence mirrors SnapshotEntry exactly
relationship vocabulary exact
trust matrix exact
PO associative
Supplier associative
Inventory associative
BOM direct bridge
direct event trust
inventory 24h exact boundary
inventory >24h
inventory 7d exact boundary
inventory >7d
stale/expired limitations
plan proxy limitation
PO allocation limitation
inventory availability limitation
untrusted rework text limitation
no FORBIDDEN_INFERENCE runtime Evidence
uncertainty registry behavior
derivation trust monotonicity
```

### test_decision_context.py

At minimum:

```text
EvidenceConflict identity/replay
three frozen conflict codes
DecisionContext schema/version
all selected Evidence exists
partitions disjoint
partition union exact
conflicts reference bundle Evidence
uncertainties preserved
limitations preserved
context identity deterministic
same input → same bytes
changed evidence selection → changed context ID
FORBIDDEN/UNKNOWN trust cannot be selected
```

## 3. Required PostgreSQL integration file

```text
tests/integration/test_decision_snapshot_database.py
```

It must use the existing guarded PostgreSQL test pattern:

```text
FLOWLENS_APP_ENVIRONMENT=test
database name ends with _test
Alembic upgraded to head
refuse unexpected/nonempty target
cleanup only rows owned by the test
```

No production database use.

## 4. PostgreSQL integration cases

At minimum prove:

```text
one active dataset binding
no/multiple dataset failure
wrong dataset version/hash failure
target order missing failure
target order after as_of failure
as_of outside dataset period failure

REPEATABLE READ
READ ONLY

explicit runtime SQL has no DML
raw status columns not selected

target graph only
unrelated order data excluded

database content identical before/after build

StateSnapshot deterministic across repeat builds
EvidenceBundle deterministic
DecisionContext deterministic
```

## 5. Baseline golden pack

Use deterministic W2 generated/persisted operational data only.

No runtime HGT.

Required semantic cases:

### G1 — Pre-delivery target

Choose a target SalesOrder deterministically and set `as_of_time` before its first
eligible Delivery.

Prove:

```text
raw stored SalesOrder.status may be final
but
C02 delivery_state_as_of = NOT_DELIVERED_AS_OF
and future Delivery is absent from snapshot/evidence.
```

### G2 — Partial/full delivery

At an as_of after one or more delivery events, prove quantities/states from eligible
Delivery rows only.

### G3 — Production timing

For WorkOrder/Operation:

```text
before actual_start → NOT_STARTED_AS_OF
after start before end → IN_PROGRESS_AS_OF
after end → COMPLETED_AS_OF
```

No raw status use.

### G4 — Procurement association

For a target required Material with one or more POs:

```text
PO/Supplier Evidence = ASSOCIATIVE_EVIDENCE
PO_ALLOCATION_ASSOCIATIVE_ONLY present
no direct allocation claim
```

### G5 — Inventory staleness

Use exact 24h / 7d boundaries and prove limitation/uncertainty behavior.

### G6 — Quality

With eligible inspection/rework:

```text
QUALITY_FINALITY_UNKNOWN always preserved after inspection
unresolved failed quantity produces QUALITY_DISPOSITION_UNKNOWN
rework never creates release
```

## 6. Scenario-backed development pack

Scenario datasets may be used as development fixtures, but:

```text
runtime builder input = scenario business dataset only
ScenarioResult.ground_truth = NOT PASSED TO RUNTIME
scenario label = NOT PASSED TO RUNTIME
```

Required coverage:

```text
Supplier degradation business dataset
Quality deterioration business dataset
Capacity surge business dataset
Neutral capacity business dataset
```

C02 does not test "true cause". It tests only temporal/trust projection.

## 7. Future-tail metamorphic pack

Create two deterministic datasets/fixtures:

```text
A and B have identical authorized history through T
B differs only in fields/rows whose authorized available_at > T
```

Because their dataset hashes differ, do NOT compare artifact IDs.

Compare normalized visible semantics as frozen in the C02 context contract.

Required mutations include:

```text
future Delivery quantity/time
future Inspection result
future Rework
future PO receipt/received quantity
future WorkOrder actual completion
future Operation actual completion
future InventorySnapshot
```

Expected:

```text
normalized visible semantic projection at T = identical
```

Also require, independently:

```text
each dataset replay is deterministic inside itself
```

## 8. Adversarial semantic pack

At minimum:

```text
raw SalesOrder.status = DELIVERED before first delivery
raw WorkOrder.status = COMPLETED before actual_end
raw Operation.status = COMPLETED before actual_end
raw PurchaseOrder.status = RECEIVED before actual_receipt
```

These raw fields must have zero runtime effect.

Other cases:

```text
PO same material but no direct WorkOrder allocation
old inventory only
no inventory
no PO
no WorkOrder
no MaterialRequirement
inspection failure without rework
partial rework
full recorded rework but no release event
WorkOrder product conflict
Inspection/Operation parent conflict
Rework/Inspection parent conflict
```

## 9. HGT / protected-material pack

Prove new C02 source modules do not import or access:

```text
flowlens.data.scenarios.ground_truth
protected scenario manifest
data/hidden_ground_truth
scenario answer/label/root cause
```

Runtime SQL must touch no protected/HGT source.

## 10. Engineering gates

Before implementation commit:

```text
focused C02 pytest
existing C01 decision tests
pytest -m "not integration"
ruff check .
mypy .
git diff --check
docker compose config --quiet
dependency files unchanged
schema/migrations unchanged
```

When safe local PostgreSQL is available:

```text
pytest tests/integration/test_decision_snapshot_database.py -m integration
```

Final integration authority:

```text
exact implementation SHA on Draft PR #6 CI
Quality gate = SUCCESS
Docker Compose smoke = SUCCESS
```

## 11. No-new-capability audit

C02 must prove absence of:

```text
Signal Engine
Diagnosis Engine
risk thresholds
route anomaly classification
Candidate Registry
Scenario Adapter runtime
simulation execution
scoring
Recommendation Engine
HumanDecision persistence
HGT evaluator
LLM
RAG
agent
runtime filesystem/network
operational DB write
```

## 12. Context Delta

Expected:

```text
changed_contracts:
C02 contract package only

changed_sources:
new C02 decision observation modules + additive __init__ exports

changed_assumptions:
frozen C02 temporal/trust/freshness policies only

changed_tool_permissions:
Snapshot Builder READ_ONLY PostgreSQL capability added

changed_context_materials:
C02 checkpoint docs/report

changed_runtime_inputs:
PostgreSQL operational facts within frozen field whitelist

schema/migration:
NONE

dependency:
NONE

operational mutation:
NONE
```

Rule:

```text
actual_delta ⊆ authorized_delta
```

otherwise not review-ready.

## 13. Machine-readable summary template

```json
{
  "round_id": "W03-C02",
  "implementation_sha": "<sha>",
  "engineering": {
    "focused_pytest": "PASS",
    "c01_regression": "PASS",
    "non_integration_pytest": "PASS",
    "postgres_integration": "PASS",
    "ruff": "PASS",
    "mypy": "PASS",
    "git_diff_check": "PASS",
    "compose_config": "PASS"
  },
  "semantic": {
    "field_temporal_projection": "PASS",
    "raw_status_exclusion": "PASS",
    "future_tail_metamorphic": "PASS",
    "trust_mapping": "PASS",
    "association_preservation": "PASS",
    "inventory_freshness": "PASS",
    "quality_unknown_preservation": "PASS",
    "conflict_preservation": "PASS"
  },
  "safety": {
    "hgt_runtime_access": "NONE",
    "operational_mutation": "NONE",
    "post_snapshot_db_access": "NONE"
  },
  "loop": {
    "snapshot_replay": "PASS",
    "context_replay": "PASS"
  },
  "ci": {
    "run_id": "<id>",
    "head_sha_matches": true,
    "quality_gate": "PASS",
    "docker_compose_smoke": "PASS"
  }
}
```

## 14. Maximum Codex status

```text
C02 IMPLEMENTATION:
COMPLETE

CONTEXT LOCK:
VERIFIED

TEMPORAL HARNESS:
PASS

SEMANTIC TRUST HARNESS:
PASS

POSTGRES READ-ONLY HARNESS:
PASS

HGT ISOLATION:
PASS

OPERATIONAL MUTATION:
NONE

EXACT-SHA CI:
PASS

ROUND REPORT:
READY

GPT REVIEW:
PENDING

HUMAN ACCEPTANCE:
PENDING

C02 CLOSED:
NO

C03 AUTHORIZED:
NO

STATUS:
REVIEW_READY
```
