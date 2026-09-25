# FlowLens W03-C03 Input and Evidence Contract V3

## 1. Accepted runtime input

Exactly:

```text
EvidenceBundle
DecisionContext
```

Both must be the closed C02 typed artifacts for the same observation world.

## 2. Binding gate

Before rule evaluation require:

```text
bundle.run_id == context.run_id
bundle.snapshot_id == context.snapshot_id
bundle.snapshot_hash == context.snapshot_hash
bundle.evidence_bundle_id == context.evidence_bundle_id
```

Require every bundle Evidence to have:

```text
item.run_id == context.run_id
item.snapshot_id == context.snapshot_id
item.as_of_time == context.as_of_time
item.available_at <= context.as_of_time
item.observed_at is None or item.observed_at <= context.as_of_time
```

Require:

```text
set(context.selected_evidence_ids)
== set(all bundle evidence IDs)
```

and the context direct/derived/associative partitions must exactly match the actual Evidence trust levels.

Require:

```text
context.uncertainties == bundle.uncertainties
```

under canonical tuple equality.

## 3. Trust gate

No selected Evidence may have:

```text
UNKNOWN
FORBIDDEN_INFERENCE
```

Every context conflict is currently a critical unresolved C02 conflict. If any exists:

```text
C03_CRITICAL_CONFLICT
BLOCKED_TRUST
no SignalBundle
no DiagnosisRecord
```

C03 does not silently choose one parent relation.

## 4. Evidence semantic key

Build a deterministic index by:

```text
(source_entity, source_record_id, source_field)
```

A duplicate semantic key is:

```text
C03_DUPLICATE_EVIDENCE_KEY
BLOCKED_CONTRACT
```

even if artifact IDs differ.

C02 derivation record IDs are treated with their known exact prefixes; do not perform unsafe arbitrary string splitting.

## 5. Error vocabulary

Closed C03 input errors:

```text
C03_BINDING_MISMATCH / BLOCKED_CONTRACT
C03_NONCANONICAL_C02_CONTEXT / BLOCKED_CONTRACT
C03_DUPLICATE_EVIDENCE_KEY / BLOCKED_CONTRACT
C03_TEMPORAL_INPUT_INVALID / BLOCKED_TEMPORAL
C03_UNTRUSTED_FACT_INPUT / BLOCKED_TRUST
C03_CRITICAL_CONFLICT / BLOCKED_TRUST
C03_RULE_INPUT_INVALID / BLOCKED_CONTRACT
C03_SIGNAL_POLICY_MISMATCH / BLOCKED_CONTRACT
```

Invalid type, impossible quantity, naive time or inconsistent required field is not ordinary UNKNOWN.

Missing rule-relevant evidence inside an otherwise valid C02 observation world is normally an explicit Signal `UNKNOWN`.

## 6. Relationship / trust use

```text
SalesOrder / WorkOrder / Operation / MaterialRequirement / QualityInspection / Rework / Delivery
→ DIRECT_FACT

C02 direct-only derivation
→ DERIVED_FACT

PurchaseOrder / Supplier / Inventory target relevance
→ ASSOCIATIVE_EVIDENCE

C02 derivation with associative input
→ ASSOCIATIVE_EVIDENCE
```

A direct fact about a PO does not make the PO-to-target-order relationship direct.

## 7. Deterministic support set S(t)

For each Signal, use all selected Evidence in the rule's authorized entity scope plus the specified C02 derivations.

For procurement signals, retain only POs whose `material_id` matches an observed target MaterialRequirement.

Use the same deterministic scope for ACTIVE, INACTIVE and UNKNOWN so a negative conclusion remains auditable.

No C03-generated Evidence object is authorized.

## 8. Quantity arithmetic

Use exact runtime types:

```text
int quantities where C02 exposes int
finite Decimal for PO/material quantities
```

Reject bool-as-int coercion and impossible used quantities.

For PO outstanding quantity:

```text
if eligible actual_receipt_at exists:
    require eligible received_quantity
    outstanding = ordered_quantity - received_quantity
else:
    outstanding = ordered_quantity
```

Require:

```text
ordered_quantity > 0
0 <= received_quantity <= ordered_quantity
```

No stock netting or allocation arithmetic.

## 9. Temporal arithmetic

Compare aware datetime instants directly.

Late/overdue uses strict:

```text
>
```

not `>=`.

A future plan/commitment may be valid evidence if already available under C02.
A future actual event may not be admitted.

## 10. Operational text

`rework_reason` is data, not instruction.
It may exist in Evidence but cannot alter rules, reason codes, fixed statements, tool access or control flow.
