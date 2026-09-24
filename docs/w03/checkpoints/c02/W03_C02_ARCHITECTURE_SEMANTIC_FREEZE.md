# FlowLens Industrial AI — W03-C02 Final Architecture & Semantic Freeze

**Task:** `W03-C02-A`
**Contract bundle:** `w03-c02-v1`
**Baseline:** `feat/w03-ai-decision-loop@c626126a81fe07b5d1f670deaeaadc809f6bea55`
**Status:** `GPT CONTRACT FREEZE COMPLETE / PASS FOR HUMAN IMPLEMENTATION AUTHORIZATION`

## 1. Objective

C02 establishes one immutable, temporally valid and semantically trusted observation
world for one target SalesOrder.

```text
DecisionRun(order_id, as_of_time, dataset binding)
↓
Snapshot Builder — READ ONLY
↓
authorized order-centric source graph
↓
field-level temporal projection
↓
StateSnapshot freeze
↓
Evidence Builder
↓
Semantic Trust classification
↓
C02 deterministic observation-state derivations
↓
EvidenceBundle
↓
DecisionContext
```

No component after StateSnapshot freeze may query the operational database for the
same run.

## 2. C02 constitutional invariants

```text
SNAPSHOT BEFORE REASONING
ONE RUN = ONE IMMUTABLE SNAPSHOT
EVIDENCE BEFORE CLAIM
ASSOCIATION != CAUSALITY
UNKNOWN IS VALID
NO FUTURE LEAKAGE
NO RUNTIME HGT
NO OPERATIONAL MUTATION
TOOLS DENY BY DEFAULT
MODEL EXPLAINS, SYSTEM DECIDES
```

C02-specific:

```text
RAW FINAL STATUS != HISTORICAL STATE
ROW EXISTENCE != FIELD AVAILABILITY
DATASET generated_at != BUSINESS available_at
SOURCE FACT STRENGTH != TARGET-ORDER RELATIONSHIP STRENGTH
DERIVATION MAY NOT UPGRADE ASSOCIATIVE INPUT TO DIRECT/DERIVED TRUST
STALE EVIDENCE MAY REMAIN VISIBLE BUT MUST NOT BECOME CURRENT FACT
FUTURE DATA MAY NOT CHANGE THE VISIBLE AS-OF SEMANTIC PROJECTION
```

## 3. Critical W2 limitation: not bitemporal

The W2 schema contains timestamps for plans and events but does not contain a complete
knowledge-time history for mutable-looking fields such as:

```text
SalesOrder.status
PurchaseOrder.status
WorkOrder.status
Operation.status
WorkOrder.completed_quantity
PurchaseOrder.received_quantity
```

Therefore C02 MUST NOT copy whole ORM rows into a historical snapshot.

C02 uses:

```text
FIELD-LEVEL TEMPORAL PROJECTION
```

Every admitted field has an explicit `available_at` rule.

## 4. as_of_time

Required:

```text
timezone-aware
DatasetVersion.period_start 00:00 Asia/Shanghai
    <= as_of_time
    <= DatasetVersion.period_end 23:59:59.999999 Asia/Shanghai

target SalesOrder.order_at <= as_of_time
```

W3 v0 treats the DatasetVersion period as the authorized offline decision horizon.

`DatasetVersion.generated_at` is generation provenance only and MUST NOT be used as
the business availability time of operational facts.

If `as_of_time` is outside the authorized period:

```text
BLOCKED_CONTEXT
```

If the target order exists but `order_at > as_of_time`:

```text
BLOCKED_TEMPORAL
```

## 5. Dataset binding

The Snapshot Builder must verify inside its read-only transaction:

```text
exactly one DatasetVersion row exists
DecisionRun.dataset_version == DatasetVersion.dataset_version_id
DecisionRun.dataset_hash == DatasetVersion.content_hash
Alembic revision == 0002_industrial_data_foundation
```

Every reachable row must have the same `dataset_version_id`.

Any mismatch is fail-closed.

The builder is not required to recompute the full W2 canonical business hash; W2
persistence/data-quality gates remain authoritative for stored content integrity.

## 6. Runtime database boundary

Only the C02 Snapshot Builder may read PostgreSQL.

Required transaction:

```text
isolation = REPEATABLE READ
transaction = READ ONLY
one transaction per snapshot build
no ORM/data mutation
no DML
no HGT/protected manifest access
```

After StateSnapshot returns:

```text
DATABASE ACCESS = NONE
```

for Evidence Builder, Semantic Trust, derivations and DecisionContext.

## 7. Authorized order-centric graph

Direct graph:

```text
SalesOrder
├── Customer
├── Product
│   └── ProductMaterial
│       └── Material
├── WorkOrder
│   ├── Operation
│   │   └── WorkCenter
│   ├── MaterialRequirement
│   │   └── Material
│   ├── QualityInspection
│   │   └── Rework
│   └── Rework
└── Delivery
```

Associative graph is admitted only through MaterialRequirement material IDs:

```text
MaterialRequirement → Material
                         ├── PurchaseOrder → Supplier
                         └── InventorySnapshot
```

Important:

```text
PurchaseOrder → Material = direct source relationship
MaterialRequirement → Material = direct source relationship
MaterialRequirement → a specific PurchaseOrder = NOT direct
InventorySnapshot → target WorkOrder availability = NOT direct
```

ProductMaterial is product/BOM context. It does not authorize order-specific
procurement allocation.

## 8. Raw status exclusion

The following fields MUST NOT enter StateSnapshot or EvidenceBundle in C02 v1:

```text
SalesOrder.status
PurchaseOrder.status
WorkOrder.status
Operation.status
```

The W2 schema does not provide status transition knowledge time.

C02 reconstructs bounded as-of observation states only from timestamp-eligible facts.

Cancellation semantics are not reconstructable in C02 v1. No cancellation inference
may be made from excluded raw status.

## 9. Master-data temporal policy

Business timezone:

```text
Asia/Shanghai
```

For Product, Customer, Supplier and WorkCenter, authorized master attributes become
available at:

```text
active_from 00:00 Asia/Shanghai
```

`active_to` is not emitted as C02 runtime evidence because W2 does not record when
that future/past master-data decision became known.

For Material and ProductMaterial, which lack effective-time fields:

```text
available_at = DatasetVersion.period_start 00:00 Asia/Shanghai
```

with an explicit synthetic baseline-availability limitation.

## 10. Synthetic planning availability proxy

W2 has no creation/release timestamp for WorkOrder, Operation or MaterialRequirement
planning data.

For C02 v1:

```text
WorkOrder plan/identity fields
Operation plan/identity fields
MaterialRequirement fields

available_at = target SalesOrder.order_at
observed_at = None
```

Every such Evidence item carries:

```text
SYNTHETIC_ORDER_PLAN_AVAILABILITY_PROXY
```

This is an explicit project policy, not an empirical factory claim.

## 11. Event temporal policy

```text
SalesOrder commitment fields
available_at = order_at
observed_at = order_at

PurchaseOrder order-side fields
available_at = ordered_at
observed_at = ordered_at

PurchaseOrder receipt-side fields
available only if actual_receipt_at <= as_of_time
available_at = actual_receipt_at
observed_at = actual_receipt_at

WorkOrder actual_start_at
available_at = actual_start_at

WorkOrder actual_end_at + completed_quantity
available_at = actual_end_at

Operation actual_start_at
available_at = actual_start_at

Operation actual_end_at
available_at = actual_end_at

InventorySnapshot fields
available_at = snapshot_at
observed_at = snapshot_at

QualityInspection fields
available_at = inspection_at
observed_at = inspection_at

Rework start-side fields
available_at = rework_start_at
observed_at = rework_start_at

Rework end field
available only if rework_end_at <= as_of_time
available_at = rework_end_at

Delivery fields
available_at = delivery_at
observed_at = delivery_at
```

## 12. Trust rules

`DIRECT_FACT` applies to authorized facts on the explicit target-order graph.

`DERIVED_FACT` applies only to deterministic C02 derivations whose relevant inputs
are all direct.

`ASSOCIATIVE_EVIDENCE` applies to target-order use of:

```text
PurchaseOrder
Supplier reached through an associated PurchaseOrder
InventorySnapshot
derivations whose input relevance is associative
```

Derivation trust is monotonic:

```text
DIRECT inputs only
→ DERIVED_FACT

any ASSOCIATIVE input
→ ASSOCIATIVE_EVIDENCE

UNKNOWN/FORBIDDEN input
→ derivation not emitted
```

No derivation may upgrade association into direct/derived trust.

## 13. Inventory freshness v1

For InventorySnapshot:

```text
age = as_of_time - snapshot_at

0 <= age <= 24 hours
→ FRESH

24 hours < age <= 7 days
→ STALE

age > 7 days
→ EXPIRED

snapshot_at > as_of_time
→ temporal violation / not admitted
```

If no eligible inventory snapshot exists:

```text
INSUFFICIENT_EVIDENCE
```

Other C02 source facts use:

```text
NOT_APPLICABLE
```

unless this contract explicitly says otherwise.

These thresholds are synthetic W3 safety thresholds, not empirical factory SLAs.

## 14. Quality uncertainty

W2 has no formal post-rework release event.

Therefore C02 never states formal release.

If at least one eligible inspection exists:

```text
QUALITY_FINALITY_UNKNOWN
status = UNKNOWN
```

If, for an eligible inspection:

```text
failed_quantity >
sum(rework_quantity for eligible linked rework events)
```

then:

```text
QUALITY_DISPOSITION_UNKNOWN
status = UNRESOLVED_DISPOSITION
```

Even when recorded rework covers failed quantity:

```text
quality_finality remains UNKNOWN
```

Forbidden guesses:

```text
scrap
replacement
concession
implicit release
implicit rework
```

## 15. Snapshot-level unknowns

StateSnapshot unknowns MUST have empty Evidence IDs, preserving the C01 no-cycle rule.

Allowed C02 snapshot-level unknown codes:

```text
WORK_ORDER_EVIDENCE_MISSING
MATERIAL_REQUIREMENT_EVIDENCE_MISSING
INVENTORY_EVIDENCE_MISSING
```

These are source-availability observations, not downstream conclusions.

## 16. C02 deterministic derivations

Authorized derivation registry:

```text
w03-c02-derivations.v1
```

Only:

```text
c02.delivered_quantity_as_of.v1
c02.remaining_quantity_as_of.v1
c02.delivery_state_as_of.v1
c02.work_order_state_as_of.v1
c02.operation_state_as_of.v1
c02.purchase_order_receipt_state_as_of.v1
c02.unresolved_failed_quantity_as_of.v1
```

No other derived feature is authorized in C02.

Risk/queue/capacity/supplier/material timing features remain C03.

## 17. Decision-time state vocabularies

Delivery:

```text
NOT_DELIVERED_AS_OF
PARTIALLY_DELIVERED_AS_OF
DELIVERED_AS_OF
```

WorkOrder / Operation:

```text
NOT_STARTED_AS_OF
IN_PROGRESS_AS_OF
COMPLETED_AS_OF
```

PurchaseOrder receipt:

```text
NOT_RECEIVED_AS_OF
PARTIALLY_RECEIVED_AS_OF
RECEIVED_AS_OF
```

These are deterministic observation-state strings, not Signal states.

## 18. Evidence relationship vocabulary

C02 v1 authorizes exactly:

```text
TARGET_RECORD
DIRECT_FK
DIRECT_BRIDGE
DIRECT_EVENT
DERIVED_FROM_DIRECT
DERIVED_FROM_ASSOCIATIVE
MATERIAL_TIME_ASSOCIATION
MASTER_DATA_CONTEXT
```

No new relationship string may be invented by implementation.

## 19. DecisionContext v1

C02 introduces an additive immutable runtime artifact:

```text
DecisionContext
schema_version = decision-context.v1

context_id
run_id
order_id
snapshot_id
snapshot_hash
evidence_bundle_id
as_of_time

selected_evidence_ids
direct_evidence_ids
derived_evidence_ids
associative_evidence_ids

uncertainties
conflicts
limitations

context_policy_version
provenance
```

Policy:

```text
context_policy_version = w03-c02-context.v1
```

C02 v1 performs no arbitrary token/count truncation.

Within the authorized field whitelist:

```text
selected_evidence_ids = all admitted Evidence with trust
DIRECT_FACT / DERIVED_FACT / ASSOCIATIVE_EVIDENCE
```

The three trust partitions are disjoint and their union equals selected evidence.

`FORBIDDEN_INFERENCE` is never selected.

LLM-specific reduction belongs to C08.

## 20. EvidenceConflict v1

C02 introduces:

```text
EvidenceConflict

conflict_id
schema_version = evidence-conflict.v1
run_id
snapshot_id
conflict_code
evidence_ids
critical
resolution_status
message
provenance
```

C02 v1:

```text
resolution_status = UNRESOLVED
```

Authorized conflict codes:

```text
WORK_ORDER_PRODUCT_MISMATCH
INSPECTION_OPERATION_WORK_ORDER_MISMATCH
REWORK_INSPECTION_WORK_ORDER_MISMATCH
```

All three are critical in v1.

Conflicts are preserved, never silently resolved.

## 21. Additive C02 identity

C01 serialization/identity files remain frozen.

C02-specific IDs use the existing canonical serializer + SHA-256 primitive:

```text
conflict_id =
"conf_" + sha256(canonical conflict identity object)

context_id =
"ctx_" + sha256(canonical context identity object)
```

Full 64 lowercase hex digest.

Context identity includes:

```text
run_id
order_id
snapshot_id
snapshot_hash
evidence_bundle_id
as_of_time
selected evidence IDs
three trust partitions
uncertainties
conflict IDs
limitations
context_policy_version
```

Provenance/implementation SHA is not part of semantic identity.

## 22. Future-tail metamorphic rule

C01 intentionally includes `dataset_hash` in StateSnapshot semantic identity.
Therefore two datasets that differ only after T have different dataset hashes and are
expected to have different:

```text
DecisionRun IDs
StateSnapshot IDs
snapshot_hash values
Evidence IDs
DecisionContext IDs
```

C02 MUST NOT incorrectly assert cross-dataset ID equality.

The temporal leakage proof is instead:

```text
Normalize away dataset/run/snapshot/artifact identity metadata.
Compare authorized visible source fields, availability, observed times,
trust, freshness, limitations, uncertainties and derived values through T.

Future-tail changes with available_at > T:
MUST NOT change that normalized visible semantic projection.
```

Inside one fixed dataset, ordinary replay still requires exact ID/hash/byte equality.

## 23. Runtime tool boundary

Authorized runtime capability:

```text
Snapshot Builder
side effect = READ_ONLY
PostgreSQL access = YES
HGT access = NO
operational write = NO
```

Pure deterministic capabilities:

```text
Temporal Projector
Evidence Builder
Semantic Trust Classifier
C02 Derivation Engine
DecisionContext Builder
```

Runtime LLM/tool access remains:

```text
NONE
```

## 24. C02 target source layout

C01 already proves that importing/scanning `flowlens.decision` is DB/SQLAlchemy-free.
C02 preserves that invariant by splitting pure semantics from the PostgreSQL adapter.

Pure additive decision source:

```text
src/flowlens/decision/
├── snapshot.py
├── temporal.py
├── evidence.py
├── trust.py
├── derivations.py
└── context.py
```

Sole C02 PostgreSQL adapter:

```text
src/flowlens/db/decision_snapshot.py
```

`src/flowlens/decision/__init__.py` may receive additive DB-free exports only.

The pure decision package MUST NOT import:

```text
flowlens.db
sqlalchemy
flowlens.data.scenarios
openai
```

The DB adapter may import SQLAlchemy and pure decision contracts. The decision package
may not import the adapter.

C01 kernel files remain frozen:

```text
contracts.py
enums.py
primitives.py
serialization.py
```

unless implementation discovers a genuine C01 contract blocker, in which case STOP.

## 25. Non-goals

```text
NO schema/migration change
NO dependency change
NO W2 canonical hash change
NO scenario semantic change
NO HGT runtime read
NO Signal thresholds
NO Signal Engine
NO Diagnosis Engine
NO route anomaly classification
NO Candidate Registry
NO Scenario Adapter
NO simulation execution
NO scoring/recommendation policy
NO HumanDecision persistence
NO HGT evaluator
NO LLM / RAG / agents
NO API/worker behavior change
NO operational mutation
```

## 26. Final C02-A status

```text
ARCHITECTURE:
FROZEN

TEMPORAL POLICY:
FROZEN

SOURCE GRAPH:
FROZEN

SEMANTIC TRUST:
FROZEN

FRESHNESS:
FROZEN

UNKNOWN POLICY:
FROZEN

DERIVATION REGISTRY:
FROZEN

DECISION CONTEXT:
FROZEN

DATABASE BOUNDARY:
FROZEN

C02 IMPLEMENTATION:
PENDING HUMAN AUTHORIZATION
```
