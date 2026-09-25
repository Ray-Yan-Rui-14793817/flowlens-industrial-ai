# FlowLens W03-C03 Signal Rulebook V3

**Policy:** `w03-c03-v1`

This is a deterministic project policy, not a learned or factory-calibrated model.

## 1. Common bundle rules

Return exactly one Signal for every frozen SignalType, sorted by `signal_type.value`.

Every `reason_codes` tuple includes:

```text
C03_POLICY_V1
```

No severity/confidence/probability/score exists.

Generic per-scope aggregation:

```text
positive witness exists
→ ACTIVE

else empty/incomplete required scope
→ UNKNOWN

else
→ INACTIVE
```

If a positive witness exists while another relevant scope item is incomplete, remain ACTIVE and add:

```text
C03_INPUT_INCOMPLETE
C03_SCOPE_PARTIALLY_OBSERVED
```

Positive evidence does not erase uncertainty.

Optional future-masked actual fields are not automatically malformed; their absence can be meaningful under the rule.

Every Signal inherits:

```text
supporting Evidence limitations
DecisionContext limitations
rule-specific C03 limitations
C03_RULE_BASED_NOT_CAUSAL
C03_INACTIVE_NOT_ALL_CLEAR
C03_CLOSED_WORLD_OBSERVATION_ASSUMPTION
```

sorted/unique.

---

## 2. SUPPLIER_LATE_RECEIPT

Meaning: observed lateness inside the **material-associated** PurchaseOrder set, not target-order supplier causation.

Scope:

```text
target MaterialRequirement material IDs
+ admitted POs sharing those material IDs
```

Required per PO:

```text
purchase_order_id
material_id
ordered_quantity
promised_receipt_at
actual_receipt_at when admitted
received_quantity when actual receipt is admitted
```

Positive witnesses:

```text
eligible actual_receipt_at > promised_receipt_at
→ C03_PO_RECEIPT_LATE

outstanding_quantity > 0 and as_of_time > promised_receipt_at
→ C03_PO_OUTSTANDING_OVERDUE
```

No associated PO scope:

```text
UNKNOWN / C03_PO_EVIDENCE_MISSING
```

Complete nonempty scope with no positive witness:

```text
INACTIVE / C03_NO_OBSERVED_PO_LATENESS
```

Required limitation:

```text
C03_ASSOCIATION_NOT_ALLOCATION
```

---

## 3. MATERIAL_TIMING_RISK

Meaning: associative procurement timing warning relative to direct MaterialRequirement `need_by_at`.

Required:

```text
MaterialRequirement.material_requirement_id
MaterialRequirement.material_id
MaterialRequirement.need_by_at
associated PO timing/quantity fields
```

For every valid MR/PO pair, positive witnesses:

```text
eligible actual_receipt_at > need_by_at
→ C03_RECEIPT_AFTER_NEED_BY

outstanding_quantity > 0 and promised_receipt_at > need_by_at
→ C03_OUTSTANDING_PROMISE_AFTER_NEED_BY

outstanding_quantity > 0 and as_of_time > need_by_at
→ C03_NEED_BY_PASSED_WITH_OUTSTANDING_PO
```

No MaterialRequirement:

```text
UNKNOWN / C03_REQUIREMENT_EVIDENCE_MISSING
```

A requirement with no associated PO:

```text
UNKNOWN / C03_PO_FOR_REQUIREMENT_MISSING
```

Any positive witness:

```text
ACTIVE
```

No witness and complete MR/PO scope:

```text
INACTIVE / C03_NO_ASSOCIATED_TIMING_WARNING
```

Inventory does **not** cancel or activate this signal. Fresh inventory does not prove allocation/consumption;
stale inventory does not turn procurement timing into a different signal.

Required limitations:

```text
C03_ASSOCIATION_NOT_ALLOCATION
C03_NOT_MATERIAL_AVAILABILITY
C03_OBSERVED_HISTORY_NOT_CURRENT_CAUSE
```

---

## 4. QUALITY_FAILURE

Meaning: direct eligible inspection records a positive failed quantity.

Scope:

```text
fact_quality_inspection
```

Positive witness:

```text
failed_quantity > 0
→ ACTIVE / C03_RECORDED_FAILED_QUANTITY
```

No inspection:

```text
UNKNOWN / C03_INSPECTION_EVIDENCE_MISSING
```

Observed inspections all have `failed_quantity == 0`:

```text
INACTIVE / C03_NO_FAILURE_IN_OBSERVED_INSPECTIONS
```

Do not use descriptive/result text as a substitute for failed-quantity accounting.
Do not infer release.

---

## 5. REWORK_PRESENT

Meaning: eligible positive-quantity Rework is recorded as of the cutoff.

Positive witness:

```text
rework_quantity > 0
→ ACTIVE / C03_RECORDED_REWORK
```

No rework but at least one eligible inspection establishes observation scope:

```text
INACTIVE / C03_NO_REWORK_IN_OBSERVED_RECORDS
```

Neither inspection nor rework:

```text
UNKNOWN / C03_REWORK_OBSERVATION_SCOPE_MISSING
```

`rework_end_at` is not required for presence. Completed rework remains historical rework.
`rework_reason` never changes policy.

Required limitation:

```text
C03_REWORK_NOT_RELEASE
```

---

## 6. QUALITY_DISPOSITION_UNKNOWN

Meaning: the frozen C02 failed-quantity accounting leaves a positive unresolved disposition gap.

Use exact C02 derivation:

```text
c02.unresolved_failed_quantity_as_of.v1|<inspection_id>
unresolved_failed_quantity_as_of
```

For any observed inspection:

```text
value > 0
→ ACTIVE / C03_FAILED_QUANTITY_DISPOSITION_GAP
```

No inspections:

```text
UNKNOWN / C03_INSPECTION_EVIDENCE_MISSING
```

All observed inspections have exact derived value `0`:

```text
INACTIVE / C03_NO_OBSERVED_DISPOSITION_GAP
```

Missing required derivation is UNKNOWN only if the C02 observation remains otherwise valid; invalid type/negative value is a contract error.

INACTIVE here does not close C02 `QUALITY_FINALITY_UNKNOWN`.

---

## 7. QUEUE_DELAY

C03 v1 meaning:

```text
operation start-slippage proxy
```

It is **not** measured queue residence time and not capacity causality.

Scope: admitted Operations.

Positive witnesses:

```text
eligible actual_start_at > planned_start_at
→ C03_OPERATION_START_SLIPPAGE

actual_start_at not admitted/visible
and as_of_time > planned_start_at
→ C03_OPERATION_START_OVERDUE
```

No Operations:

```text
UNKNOWN / C03_OPERATION_EVIDENCE_MISSING
```

Complete operation scope with no positive witness:

```text
INACTIVE / C03_NO_OBSERVED_START_SLIPPAGE
```

Equality at planned start is not late.

Required limitation:

```text
C03_START_SLIPPAGE_NOT_QUEUE_MEASUREMENT
```

Do not derive preferred-route anomalies, predecessor-duration queue time or capacity cause.

---

## 8. CAPACITY_PRESSURE

C03 v1 always returns:

```text
UNKNOWN / C03_CAPACITY_SCOPE_INSUFFICIENT
```

Reason: the order-centric C02 input lacks complete competing workload, shift/calendar and allocatable capacity context.

WorkCenter `daily_capacity_hours`, one order's duration, queue warning or scenario label cannot turn this signal ACTIVE/INACTIVE.

Required limitation:

```text
C03_CAPACITY_NOT_IDENTIFIABLE
```

---

## 9. DELIVERY_RISK

Meaning: narrow deterministic delivery-commitment warning, **not** calibrated prediction.

Required:

```text
SalesOrder.promised_delivery_at
exact C02 remaining_quantity_as_of
```

`remaining_quantity_as_of < 0` is a contract error.

Evaluate ordered rules:

### D1 — fulfilled

```text
remaining_quantity_as_of == 0
→ INACTIVE / C03_DELIVERY_FULFILLED_AS_OF
```

This wins even when historical upstream warnings remain.

### D2 — overdue commitment

```text
remaining_quantity_as_of > 0
and as_of_time > promised_delivery_at
→ ACTIVE / C03_UNFULFILLED_COMMITMENT_OVERDUE
```

Equality at promise is not overdue.

### D3 — incomplete plan beyond commitment

For any WorkOrder with exact C02 state:

```text
state in {{NOT_STARTED_AS_OF, IN_PROGRESS_AS_OF}}
and planned_end_at > promised_delivery_at
```

with remaining quantity > 0:

```text
ACTIVE / C03_INCOMPLETE_PLAN_AFTER_COMMITMENT
```

If D2 and D3 both apply, retain both positive codes.

### D4 — no authorized forecast conclusion

Otherwise:

```text
UNKNOWN / C03_DELIVERY_FORECAST_UNSUPPORTED
```

If a required WO plan/state is incomplete also add:

```text
C03_INPUT_INCOMPLETE
```

DELIVERY_RISK does **not** aggregate other Signal states, use weights, produce confidence, or infer on-time probability.

Required limitation:

```text
C03_RULE_INDICATOR_NOT_FORECAST
```

---

## 10. Route variance

```text
ROUTE_VARIANCE:
CONTEXT ONLY / NOT A C03 SIGNAL
```

Recorded Operations may support timing observations. Preferred-route deviation alone has zero C03 signal effect.

---

## 11. Boundary rules

```text
actual receipt == promise
→ not late

no receipt and as_of == promise
→ not overdue

need_by == promise == as_of
→ equality alone not a positive material witness

actual start == planned start
→ not late

planned start == as_of with actual start absent
→ not overdue

remaining > 0 and as_of == promised delivery
→ DELIVERY_RISK UNKNOWN unless D3 applies

full delivery
→ DELIVERY_RISK INACTIVE

capacity context incomplete
→ CAPACITY_PRESSURE UNKNOWN always
```
