# FlowLens W03-C03 Harness and Acceptance Specification V3

## 1. Capability proof matrix

| Capability | Invariant | Proof | Failure |
|---|---|---|---|
| Input binding | bundle/context same observation world | negative binding tests | BLOCKED_CONTRACT |
| Temporal | no unavailable/future actual evidence | adversarial / future-tail | BLOCKED_TEMPORAL |
| Trust | no UNKNOWN/FORBIDDEN factual input | negative tests | BLOCKED_TRUST |
| Conflict | any critical unresolved C02 conflict blocks C03 | 3 conflict fixtures | BLOCKED_TRUST |
| Completeness | exactly 8 SignalTypes | set equality | fail |
| Determinism | same input/policy -> same bytes/IDs | replay | fail |
| Grounding | support IDs belong to context/bundle | reference audit | fail |
| Association | PO/material claims remain associative | claim tests | fail |
| Supplier | receipt/promise rules exact | boundary table | fail |
| Material | MR/PO need-by rules exact | boundary table | fail |
| Quality | positive failed quantity only | boundary tests | fail |
| Rework | positive recorded rework semantics | presence tests | fail |
| Disposition | C02 unresolved-failed derivation exact | derivation tests | fail |
| Queue | start-slippage proxy exact | equality / overdue tests | fail |
| Capacity | always UNKNOWN v1 | all-fixture assertion | fail |
| Delivery | fulfilled/overdue/incomplete-plan/UNKNOWN policy | decision table | fail |
| Diagnosis | fixed claims/uncertainties/root scope | exact-template tests | fail |
| Future-tail | future-only facts cannot change T semantics | metamorphic | abort |
| HGT | runtime source/import/access none | source/import audit | abort |
| Post-C02 DB | C03 source has no DB access | import/call audit | hard fail |
| Mutation | no operational write | DB before/after + source audit | hard fail |

## 2. Required test files

```text
tests/test_c03_policy_contract.py
tests/test_c03_signals.py
tests/test_c03_diagnosis.py
tests/test_c03_harness.py
tests/integration/test_c03_decision_database.py
```

The integration test may use the existing authorized C02 read-only PostgreSQL adapter to construct
C02 artifacts. C03 itself receives only `EvidenceBundle + DecisionContext`.

## 3. Supplier matrix

At minimum:

```text
receipt before promise -> INACTIVE
receipt exactly promise -> INACTIVE
receipt +1 microsecond -> ACTIVE
no receipt before/equal promise -> no overdue witness
outstanding +1 microsecond after promise -> ACTIVE
partial receipt with outstanding after promise -> ACTIVE
no associated PO -> UNKNOWN
association limitation preserved
```

## 4. Material timing matrix

```text
full receipt before/equal need_by -> no late witness
full receipt after need_by -> ACTIVE
outstanding promise after need_by -> ACTIVE
outstanding after need_by at T -> ACTIVE
no MR -> UNKNOWN
MR but no associated PO -> UNKNOWN
complete associated timing with no positive witness -> INACTIVE
fresh inventory cannot cancel warning
missing/stale inventory remains Diagnosis uncertainty but does not redefine the signal
```

## 5. Quality / Rework / disposition

```text
failed_quantity 0 -> QUALITY_FAILURE INACTIVE
failed_quantity >0 -> ACTIVE
no inspection -> QUALITY_FAILURE UNKNOWN

positive rework quantity -> REWORK_PRESENT ACTIVE
inspection scope + no rework -> INACTIVE
no inspection/rework scope -> UNKNOWN
rework_reason injection text has zero policy effect

unresolved_failed_quantity >0 -> QUALITY_DISPOSITION_UNKNOWN ACTIVE
all exact zeros -> INACTIVE
no inspection -> UNKNOWN
QUALITY_FINALITY_UNKNOWN is always preserved separately when C02 emitted it
```

## 6. Queue start-slippage

```text
actual_start < planned_start -> INACTIVE witness
actual_start == planned_start -> INACTIVE witness
actual_start > planned_start -> ACTIVE
actual_start absent and T > planned_start -> ACTIVE overdue-start witness
actual_start absent and T == planned_start -> not active
future planned start -> not active
no operations -> UNKNOWN
```

Always preserve the proxy limitation; never infer capacity cause.

## 7. Capacity

For every successful C03 fixture:

```text
CAPACITY_PRESSURE == UNKNOWN
reason includes C03_CAPACITY_SCOPE_INSUFFICIENT
```

## 8. Delivery decision table

```text
remaining == 0
→ INACTIVE

remaining > 0 and T > promised_delivery
→ ACTIVE

remaining > 0 and incomplete WO planned_end > promise
→ ACTIVE

remaining > 0 and T == promise with no D3 witness
→ UNKNOWN

remaining > 0 before due with no D3 witness
→ UNKNOWN

completed WO whose old plan exceeded promise
→ does not create current D3 witness
```

No other Signal state directly activates DELIVERY_RISK.

## 9. Diagnosis matrix

Prove:

```text
problem_code precedence exact
one claim per ACTIVE/UNKNOWN Signal
no claim for INACTIVE Signal
claim types exact
statements exact / no operational string interpolation
all eight supporting_signal_ids
supporting Evidence subset exact
C02 uncertainties preserved
C03 UNKNOWN/PARTIAL uncertainties deterministic
affected_path == target SalesOrder root only
same input -> same Diagnosis ID/bytes
```

## 10. Critical conflicts

Use all three closed C02 conflict codes:

```text
WORK_ORDER_PRODUCT_MISMATCH
INSPECTION_OPERATION_WORK_ORDER_MISMATCH
REWORK_INSPECTION_WORK_ORDER_MISMATCH
```

Every one must produce:

```text
C03_CRITICAL_CONFLICT / BLOCKED_TRUST
no successful SignalBundle
no DiagnosisRecord
```

## 11. Future-tail metamorphic pack

Reuse C02 future-tail construction.

Do not compare cross-dataset artifact IDs.
Compare normalized Signal/Diagnosis semantics at T.

Required future-only changes include delivery, inspection/rework, PO receipt/quantity,
WorkOrder/Operation actuals and inventory.

## 12. Scenario-backed development pack

Scenario business datasets may be used as development fixtures only.

Runtime input must not receive:

```text
scenario label/type
HGT
affected map
causal chain
true root cause
```

Direction smoke expectations:

```text
Supplier degradation:
at least one order shows Supplier lateness and/or Material timing ACTIVE from business facts

Quality deterioration:
at least one order shows Quality failure / Rework / Disposition-gap ACTIVE from business facts

Capacity combined:
at least one order shows QUEUE_DELAY ACTIVE from business timing facts

Capacity neutral:
scenario identity alone must not manufacture queue/start-slippage

CAPACITY_PRESSURE:
UNKNOWN in both capacity cases
```

Do not require DELIVERY_RISK to match hidden scenario truth.

## 13. Route-variance negative pack

Preferred-route deviation alone must not create any new C03 Signal outcome.
Actual recorded timing still counts normally.

## 14. Forbidden-inference pack

Prevent:

```text
PO supplied target WorkOrder
supplier caused target delay
fresh inventory proves allocation/availability
rework proves release
failed quantity implies scrap/concession
start slippage proves capacity bottleneck
capacity from daily_capacity_hours alone
scenario label/HGT supports runtime claim
operational text changes policy
```

## 15. Local engineering gates

Before implementation commit:

```text
pytest tests/test_c03_policy_contract.py tests/test_c03_signals.py tests/test_c03_diagnosis.py tests/test_c03_harness.py
pytest tests/test_decision_contracts.py tests/test_decision_serialization.py
pytest tests/test_decision_snapshot.py tests/test_decision_temporal.py tests/test_decision_evidence.py tests/test_decision_context.py
pytest -m "not integration"
ruff check .
mypy .
git diff --check
docker compose config --quiet
```

When safe guarded PostgreSQL is available:

```text
pytest tests/integration/test_c03_decision_database.py -m integration
```

Final remote authority is the inherited DEVCTRL exact-SHA gate.

## 16. Source/import audit

New C03 runtime source must not import/access:

```text
sqlalchemy
flowlens.db
flowlens.data.scenarios
flowlens.data.scenarios.ground_truth
openai/network clients
filesystem readers/writers
subprocess/shell
randomness
```

## 17. Expected Context Delta

```text
new C03 checkpoint docs/specs
c03_policy.py
c03_validation.py
signals.py
diagnosis.py
additive decision exports
5 C03 test files
later Round Report + CURRENT_STATE

schema/migration:
NONE

dependency:
NONE

CI/control-plane code:
NONE

new runtime tool:
NONE

HGT runtime:
NONE

operational mutation:
NONE

C04 capability:
NONE
```

Actual delta must be a subset.

## 18. Maximum Codex status

```text
STATUS:
REVIEW_READY

GPT C03 REVIEW:
PENDING

HUMAN C03 ACCEPTANCE:
PENDING

C03 CLOSED:
NO

C04 AUTHORIZED:
NO
```
