# FlowLens Industrial AI — W03-C02 DecisionContext, Conflict & Derivation Contract

**Contract:** `w03-c02-context.v1`

## 1. C02 artifact flow

```text
StateSnapshot
↓
source Evidence
↓
C02 derivations
↓
EvidenceBundle
↓
EvidenceConflict detection
↓
DecisionContext
```

No stage after StateSnapshot may read PostgreSQL.

## 2. Derivation registry

Registry version:

```text
w03-c02-derivations.v1
```

### D01 — delivered quantity

```text
id = c02.delivered_quantity_as_of.v1
target = target SalesOrder
output field = delivered_quantity_as_of
type = int
```

Definition:

```text
sum(Delivery.delivered_quantity Evidence admitted at or before as_of_time)
```

If no eligible Delivery exists:

```text
0
```

Inputs include target order identity/order quantity Evidence plus eligible Delivery
quantity Evidence so the derived Evidence remains evidence-grounded.

### D02 — remaining quantity

```text
id = c02.remaining_quantity_as_of.v1
output = remaining_quantity_as_of
```

Definition:

```text
order_quantity - delivered_quantity_as_of
```

If negative:

```text
BLOCKED_CONTRACT
```

### D03 — delivery state

```text
id = c02.delivery_state_as_of.v1
```

```text
delivered == 0
→ NOT_DELIVERED_AS_OF

0 < delivered < order_quantity
→ PARTIALLY_DELIVERED_AS_OF

delivered == order_quantity
→ DELIVERED_AS_OF

delivered > order_quantity
→ BLOCKED_CONTRACT
```

### D04 — WorkOrder state

```text
id = c02.work_order_state_as_of.v1
target = each target WorkOrder
```

Use admitted events only:

```text
eligible actual_end_at exists
→ COMPLETED_AS_OF

else eligible actual_start_at exists
→ IN_PROGRESS_AS_OF

else
→ NOT_STARTED_AS_OF
```

The implementation MUST NOT inspect a future actual timestamp to distinguish the last case.

### D05 — Operation state

```text
id = c02.operation_state_as_of.v1
target = each target Operation
```

Same rule as WorkOrder:

```text
COMPLETED_AS_OF
IN_PROGRESS_AS_OF
NOT_STARTED_AS_OF
```

using admitted events only.

### D06 — PurchaseOrder receipt state

```text
id = c02.purchase_order_receipt_state_as_of.v1
target = each admitted associated PurchaseOrder
```

```text
no eligible actual_receipt_at
→ NOT_RECEIVED_AS_OF

eligible receipt and received_quantity < ordered_quantity
→ PARTIALLY_RECEIVED_AS_OF

eligible receipt and received_quantity == ordered_quantity
→ RECEIVED_AS_OF

received_quantity > ordered_quantity
→ BLOCKED_CONTRACT
```

Trust:

```text
ASSOCIATIVE_EVIDENCE
```

because target-order relevance remains associative.

### D07 — unresolved failed quantity

```text
id = c02.unresolved_failed_quantity_as_of.v1
target = each eligible QualityInspection
```

Definition:

```text
max(
  inspection.failed_quantity
  - sum(eligible linked Rework.rework_quantity),
  0
)
```

If positive, emit `QUALITY_DISPOSITION_UNKNOWN`.

This arithmetic does not infer scrap, concession, replacement or final release.

## 3. Derived Evidence convention

Derived Evidence:

```text
source_entity = "c02_derivation"

source_record_id =
derivation_id + "|" + target_record_id

source_field =
the frozen output field

observed_at = None
available_at = DecisionRun.as_of_time
freshness_status = NOT_APPLICABLE
```

Trust:

```text
all relevant inputs DIRECT
→ DERIVED_FACT
relationship = DERIVED_FROM_DIRECT

any relevant input ASSOCIATIVE
→ ASSOCIATIVE_EVIDENCE
relationship = DERIVED_FROM_ASSOCIATIVE
```

Limitations from associative inputs are inherited and deterministically deduplicated.

Derived Evidence may not consume `UNKNOWN` or `FORBIDDEN_INFERENCE` as if they were facts.

## 4. EvidenceConflict

Immutable C02 type:

```text
@dataclass(frozen=True, slots=True, kw_only=True)

conflict_id: str
schema_version: str
run_id: str
snapshot_id: str
conflict_code: str
evidence_ids: tuple[str, ...]
critical: bool
resolution_status: str
message: str
provenance: ArtifactProvenance
```

Required:

```text
schema_version = evidence-conflict.v1
resolution_status = UNRESOLVED
evidence_ids sorted/unique/nonempty
all evidence IDs exist in EvidenceBundle
```

Identity:

```text
conflict_id =
"conf_" + sha256_hex(
  {
    "artifact_kind": "evidence-conflict",
    "schema_version": "evidence-conflict.v1",
    "identity": {
      "run_id": ...,
      "snapshot_id": ...,
      "conflict_code": ...,
      "evidence_ids": ...,
      "critical": ...,
      "resolution_status": "UNRESOLVED"
    }
  }
)
```

Message/provenance are not semantic identity.

## 5. Conflict registry v1

### WORK_ORDER_PRODUCT_MISMATCH

When an admitted WorkOrder.product_id differs from target SalesOrder.product_id.

Evidence:

```text
SalesOrder.product_id
WorkOrder.product_id
```

Critical:

```text
YES
```

### INSPECTION_OPERATION_WORK_ORDER_MISMATCH

When an eligible inspection has non-null `operation_id`, but the referenced admitted
Operation belongs to a different WorkOrder than the inspection.

Critical:

```text
YES
```

### REWORK_INSPECTION_WORK_ORDER_MISMATCH

When eligible Rework.work_order_id differs from the WorkOrder of its referenced
Inspection.

Critical:

```text
YES
```

No automatic conflict resolution is authorized.

## 6. DecisionContext v1

Immutable C02 type:

```text
@dataclass(frozen=True, slots=True, kw_only=True)

context_id: str
schema_version: str
run_id: str
order_id: str

snapshot_id: str
snapshot_hash: str
evidence_bundle_id: str
as_of_time: datetime

selected_evidence_ids: tuple[str, ...]
direct_evidence_ids: tuple[str, ...]
derived_evidence_ids: tuple[str, ...]
associative_evidence_ids: tuple[str, ...]

uncertainties: tuple[Uncertainty, ...]
conflicts: tuple[EvidenceConflict, ...]
limitations: tuple[Limitation, ...]

context_policy_version: str
provenance: ArtifactProvenance
```

Required constants:

```text
schema_version = decision-context.v1
context_policy_version = w03-c02-context.v1
```

## 7. DecisionContext selection

C02 v1 performs no arbitrary truncation.

```text
selected_evidence_ids =
all EvidenceBundle Evidence whose trust_level is one of:
DIRECT_FACT
DERIVED_FACT
ASSOCIATIVE_EVIDENCE
```

Partition:

```text
direct_evidence_ids
= trust == DIRECT_FACT

derived_evidence_ids
= trust == DERIVED_FACT

associative_evidence_ids
= trust == ASSOCIATIVE_EVIDENCE
```

Required:

```text
partition sets pairwise disjoint

union(partitions)
== selected_evidence_ids

all IDs exist in EvidenceBundle

no Evidence with UNKNOWN/FORBIDDEN_INFERENCE is selected
```

## 8. Context uncertainty / limitation projection

```text
DecisionContext.uncertainties
=
EvidenceBundle.uncertainties
```

sorted/deduplicated without semantic weakening.

Context limitations include deterministic union of:

```text
global C02 context limitations
selected Evidence limitations
```

No limitation may be silently dropped.

## 9. DecisionContext identity

```text
context_id =
"ctx_" + full lowercase SHA-256 digest
```

Canonical identity object:

```text
{
  "artifact_kind": "decision-context",
  "schema_version": "decision-context.v1",
  "identity": {
    "run_id": ...,
    "order_id": ...,
    "snapshot_id": ...,
    "snapshot_hash": ...,
    "evidence_bundle_id": ...,
    "as_of_time": ...,
    "selected_evidence_ids": ...,
    "direct_evidence_ids": ...,
    "derived_evidence_ids": ...,
    "associative_evidence_ids": ...,
    "uncertainties": ...,
    "conflict_ids": ...,
    "limitations": ...,
    "context_policy_version": "w03-c02-context.v1"
  }
}
```

Use the existing C01 canonical serializer / `sha256_hex`.

Do not modify the C01 serialization prefix registry merely to add C02 IDs.

## 10. Provenance

DecisionContext provenance:

```text
input_artifact_ids includes:
snapshot_id
evidence_bundle_id
all conflict_ids

contract_versions includes:
w03-c02-v1
w03-c02-source-matrix.v1
w03-c02-trust-matrix.v1
w03-c02-derivations.v1
w03-c02-context.v1
```

Source refs are the deterministic union of selected Evidence provenance source refs.

## 11. Replay

For the same:

```text
DecisionRun
StateSnapshot
EvidenceBundle
C02 policy versions
implementation behavior
```

require:

```text
same conflicts
same DecisionContext
same context_id
same canonical bytes
```

No wall clock or random value may participate.

## 12. Cross-dataset future-tail metamorphic proof

Because C01 binds dataset hash into run/snapshot identity, cross-dataset IDs are expected
to differ.

A future-tail metamorphic test must compare a normalized semantic view:

```text
SnapshotEntry:
source_entity
source_record_id
source_field
value
observed_at
available_at

Evidence:
source_entity
source_record_id
source_field
value
observed_at
available_at
relationship_type
trust_level
freshness_status
limitations

Uncertainty:
status
code
message
semantic source references after ID normalization

Derived output:
derivation id / target / value / trust / limitations
```

Strip:

```text
dataset_version
dataset_hash
run_id
snapshot_id
snapshot_hash
artifact IDs
implementation SHA
```

Future-only changes after T MUST NOT change the normalized visible semantic projection at T.
