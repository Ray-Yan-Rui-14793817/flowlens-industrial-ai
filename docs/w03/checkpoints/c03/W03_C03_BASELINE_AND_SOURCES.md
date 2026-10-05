# FlowLens W03-C03 Baseline and Decision Provenance V3

## 1. Verified post-DEVCTRL baseline

GPT normalized C03 after DEVCTRL-01 final closeout.

```text
repository:
Ray-Yan-Rui-14793817/flowlens-industrial-ai

branch:
feat/w03-ai-decision-loop

W03 HEAD / PR #6 HEAD:
2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978

main:
9d18ddde9fe933952a2661ee1419f13c8577605d

PR #6:
OPEN / DRAFT / NOT MERGED / AUTO-MERGE NONE

DEVCTRL closeout Run #48:
36104873132 / SUCCESS

Run #48 jobs:
Classify change SUCCESS
Publication proof SUCCESS
Quality gate SKIPPED
Docker Compose smoke SKIPPED
Verification gate SUCCESS
```

## 2. Closed upstream runtime authority

```text
C01 immutable artifacts/contracts:
CLOSED

C02 StateSnapshot / Evidence / Semantic Trust / DecisionContext:
CLOSED

DEVCTRL deterministic verification control plane:
CLOSED
```

C03 may consume but not rewrite those boundaries.

## 3. Actual source/code surfaces audited by GPT

The V3 design was checked against the current branch implementations of:

```text
src/flowlens/decision/enums.py
src/flowlens/decision/primitives.py
src/flowlens/decision/contracts.py
src/flowlens/decision/snapshot.py
src/flowlens/decision/temporal.py
src/flowlens/decision/trust.py
src/flowlens/decision/derivations.py
src/flowlens/decision/evidence.py
src/flowlens/decision/context.py
src/flowlens/db/decision_snapshot.py
.github/workflows/ci.yml
```

and the authoritative G0/C02 W03 contracts.

## 4. Compatibility facts used by C03

- C01 already freezes all eight `SignalType` values and the three `SignalState` values.
- C01 `Signal` identity includes `run_id`, `snapshot_id`, `signal_type`, `state`, `evidence_ids`, `reason_codes`.
- C01 `DiagnosisRecord` already contains claims, supporting IDs, uncertainties, affected_path and reason_codes.
- `DecisionRun.contract_bundle_version` is still structurally frozen as `w03-c01-v1`; C03 must not change it.
- C02 DecisionContext is lossless over runtime-admitted Evidence and partitions direct/derived/associative trust.
- C02 PO/Supplier/Inventory relevance to the target order is associative.
- C02 masks future actual WorkOrder/Operation/PO/Rework fields and excludes future deliveries/inspections/inventory.
- C02 admits future plan/commitment values when their plan record is already available.
- C02 has no plant-wide competing workload/shift/calendar model, so real capacity pressure is not identifiable.
- Existing DEVCTRL `ci.yml` already classifies change risk and enforces a stable `Verification gate`.

## 5. C02 fields intentionally used by C03

Examples include:

```text
SalesOrder:
promised_delivery_at

WorkOrder:
planned_end_at
c02.work_order_state_as_of.v1

Operation:
planned_start_at
actual_start_at when admitted

MaterialRequirement:
material_id
need_by_at

PurchaseOrder:
material_id
ordered_quantity
promised_receipt_at
actual_receipt_at when admitted
received_quantity when admitted

QualityInspection:
failed_quantity

Rework:
rework_quantity

C02 derivations:
remaining_quantity_as_of
unresolved_failed_quantity_as_of
```

C03 does not depend on raw mutable W2 status columns.

## 6. Synthetic-project policy boundary

The C03 rules are project policies for the deterministic synthetic industrial environment.
They are not claimed as empirical factory thresholds, calibrated ML, SLA measurements or production readiness.
