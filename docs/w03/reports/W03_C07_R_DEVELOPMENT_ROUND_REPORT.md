# W03-C07 Development Round Report

## 1. Report Metadata

| Item | Verified value |
|---|---|
| Task | `W03-C07-I/H/R` — protected offline recommendation evaluation |
| Repair task | `W03-C07-REPAIR-01` — test/replay-harness semantic repair |
| Round entry SHA | `6e44af5159af50f4e69871425fed462ccb80adf9` |
| Original implementation SHA / repair entry SHA | `90f159bf444bd1a0541fbc7fdb48188825ac53e4` |
| Accepted repair SHA | `3c5df35528fbe9cd0f77d299a394da265d7ec9db` |
| Branch | `feat/w03-ai-decision-loop` |
| Main baseline | `9d18ddde9fe933952a2661ee1419f13c8577605d` |
| Draft PR | [#6](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/pull/6) |
| Date | 2026-09-28 |

```text
W03-C07 HUMAN IMPLEMENTATION AUTHORIZATION: APPROVED
PRE-REPORT SEMANTIC AUDIT: W03_C07_REPLAY_PROOF_MISMATCH
W03-C07-REPAIR-01 HUMAN AUTHORIZATION: APPROVED
REPAIR SCOPE: TEST / REPLAY HARNESS ONLY
```

## 2. Starting Baseline and Evidence History

The C07 round began at the published C06 closeout SHA
`6e44af5159af50f4e69871425fed462ccb80adf9`. Original C07 implementation SHA
`90f159bf444bd1a0541fbc7fdb48188825ac53e4` passed exact-SHA
[Run #69 / `36377688015`](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/36377688015)
as `I / FULL_EXACT_SHA`.

Before report publication, the required semantic audit returned
`W03_C07_REPLAY_PROOF_MISMATCH`. The evaluator/runtime implementation was not
found defective. The defect was that the real six-case replay path constructed
decision evidence from family-selected test fixtures, so the passed run did
not prove that actual W2 baseline/scenario business rows flowed through C01-C05.

The Product Owner authorized the bounded `W03-C07-REPAIR-01` test/replay
harness repair. Repair SHA
`3c5df35528fbe9cd0f77d299a394da265d7ec9db` passed exact-SHA
[Run #70 / `36424098689`](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/36424098689)
as `I / FULL_EXACT_SHA`.

## 3. Round Objective

Preserve the frozen C07 protected evaluation contract while proving that each
required W2 replay packet is derived from the real supplied
`GeneratedDataset` business rows. Runtime HGT remains prohibited; protected
HGT is used only for offline case selection and C07 evaluation after the C01-C05
`DecisionPacket` is frozen.

## 4. Authorized Repair Scope

Repair SHA `3c5df35...` changed exactly:

```text
tests/test_c07_replay.py
tests/test_c07_harness.py
tests/test_c07_policy.py
tests/test_c07_recommendation.py
```

Repair classification:

```text
REPAIR SCOPE: TEST / REPLAY HARNESS ONLY
RUNTIME SOURCE CHANGES: NONE
EVALUATOR SOURCE CHANGES: NONE
CONTRACT / POLICY VERSION CHANGES: NONE
W2 SCENARIO / HGT SOURCE CHANGES: NONE
SCHEMA / MIGRATION / DEPENDENCY CHANGES: NONE
CI / CONTROL-PLANE CHANGES: NONE
```

## 5. Explicit Non-Goals

The repair does not change C01-C06 runtime source, the C07 evaluator, the W2
generator/scenarios/HGT, dataset hashing, schemas, migrations, dependencies,
CI, Docker/Compose, API, worker, PR state, C08, or operational truth. It does
not force descriptive metrics to become positive and does not reinterpret
business accuracy.

## 6. Repaired Real Replay Dataflow

| Dataflow stage | Exact supplying path |
|---|---|
| Execute frozen scenario | `apply_scenario(...)` via `replay_case(...)` |
| Choose protected evaluation order | sorted HGT-affected order selection in `replay_case(...)`; neutral uses one deterministic common order |
| Build actual order closure | `_order_closure(dataset, order_id)` |
| Resolve actual source IDs | `_record_id(entity, row)` |
| Extract whitelisted actual row values | `_record(entity, row)` using frozen `SOURCE_FIELDS` |
| Perform temporal projection | `_packet_from_records(...)` calls unchanged `project_record(...)` with dataset `period_start`, common `as_of_time`, and actual SalesOrder `order_at` |
| Build frozen C02 state/evidence | unchanged `build_state_snapshot(...)`, `build_evidence_bundle(...)`, and `build_decision_context(...)` |
| Build frozen C03 reasoning artifacts | unchanged `evaluate_c03(...)` |
| Build frozen C04 candidates/simulations | unchanged `build_candidate_set(...)` and `build_simulation_bundle(...)` |
| Build frozen C05 output | unchanged `build_decision_packet(...)` |
| Run protected C07 evaluator | protected evaluation in `replay_case(...)`, only after packet construction |

The real builder is `packet_from_dataset(dataset, order_id, as_of_time)`. Its
signature accepts only ordinary runtime inputs. It does not accept or consult
`HiddenGroundTruth`, `ScenarioResult`, `ScenarioType`, expected intervention
family, expected signal, recommendation, or truth mode when constructing
runtime facts.

## 7. Actual Dataset Closure

For the selected Sales Order, `_order_closure(...)` selects the actual order,
all directly bound Work Orders, Operations, Material Requirements, Quality
Inspections, Rework rows and Deliveries, plus Purchase Orders and Inventory
Snapshots associated through the actual required material IDs. Every emitted
source identifier is the corresponding real row identity. No arbitrary Sales
Order ID is rewritten and no procurement-to-order allocation is fabricated.

The actual selected `SalesOrder.order_at` supplies `target_order_at`. The
unchanged `project_record(...)` temporal gate decides which whitelisted fields
are available at the paired common `as_of_time`.

## 8. Separation of Real and Adversarial Fixtures

The six real W2 replays use `packet_from_dataset(...)` only. Synthetic packets
remain available solely through clearly named `adversarial_packet_fixture(...)`
and `_adversarial_records_for_order(...)` for bounded negative/fail-closed
tests. Outputs from those helpers are not counted as real replay evidence.

The former `test_c05_policy.neutral_records` and
`test_c05_policy.records_for_active` helpers are absent from the real six-case
packet path.

## 9. Mandatory Replay-Proof Guards

| Guard | Result |
|---|---|
| R1-G1 — every snapshot source row exists in its supplied dataset | PASS |
| R1-G2 — every projected source value matches the corresponding row attribute | PASS |
| R1-G3 — actual selected SalesOrder `order_at` drives temporal projection | PASS |
| R1-G4 — no family/scenario/HGT/truth input to the real packet builder | PASS / ABSENT |
| R1-G5 — no synthetic C05 fixture helper in the real replay | PASS / ABSENT |
| R1-G6 — baseline and scenario packets are independently dataset-derived | PASS |
| R1-G7 — HGT remains post-freeze and protected | PASS |
| R1-G8 — canonical baseline/scenario business payloads remain immutable | PASS |

```text
REAL DATASET -> PACKET BINDING: PASS
ACTUAL SOURCE-RECORD IDENTITY: PASS
ACTUAL SOURCE-FIELD VALUE BINDING: PASS
ACTUAL SALES ORDER ORDER_AT: PASS
EXPECTED-FAMILY INJECTION: ABSENT
SYNTHETIC C05 FIXTURE HELPERS IN SIX-CASE REPLAY: ABSENT
PAIRED BASELINE/SCENARIO DATASET DERIVATION: PASS
HGT PRE-PACKET / RUNTIME ACCESS: NONE
HGT PROTECTED EVALUATION ACCESS: YES / OFFLINE ONLY
DATASET MUTATION: NONE
```

## 10. Six-Case Descriptive Metric Matrix

These values are frozen-policy measurements, not aggregate scores or claims of
business accuracy. `None` means the metric is not applicable under the frozen
policy.

| Replay | Cause direction | Candidate relevance | Recommendation coverage | False positive | Neutral stability | Disposition | Selected family | Truth mode |
|---|---:|---:|---:|---:|---:|---|---|---|
| Supplier effectful | `None` | `True` | `False` | `False` | `None` | `NO_RECOMMENDATION` | `None` | `EFFECTFUL_OBSERVABLE` |
| Quality effectful | `True` | `True` | `False` | `False` | `None` | `NO_RECOMMENDATION` | `None` | `EFFECTFUL_OBSERVABLE` |
| Capacity combined | `None` | `True` | `True` | `False` | `None` | `INVESTIGATION_ONLY` | `CAPACITY_INTERVENTION` | `EFFECTFUL_OBSERVABLE` |
| Capacity arrival-only | `None` | `None` | `None` | `None` | `None` | `INVESTIGATION_ONLY` | `CAPACITY_INTERVENTION` | `EFFECTFUL_NOT_OBSERVABLE` |
| Capacity queue-only | `None` | `True` | `True` | `False` | `None` | `INVESTIGATION_ONLY` | `CAPACITY_INTERVENTION` | `EFFECTFUL_OBSERVABLE` |
| Capacity neutral | `None` | `None` | `None` | `False` | `True` | `INVESTIGATION_ONLY` | `CAPACITY_INTERVENTION` | `NEUTRAL_CONTROL` |

Expected scenario-family bounds remain `SUPPLIER_INTERVENTION`,
`QUALITY_INTERVENTION`, `CAPACITY_INTERVENTION`,
`CAPACITY_INTERVENTION`, `CAPACITY_INTERVENTION`, and `None` respectively.
Those expected values are protected evaluation inputs only and do not enter
packet construction. `CAPACITY_PRESSURE` remains `UNKNOWN`.

## 11. Required Replay Evidence

```text
six real W2 replay cases: PASS
same-process replay: PASS
fresh-process replay: PASS
H1-H38: PASS
R1-G1 through R1-G8: PASS
```

The H1-H38 adversarial matrix remains complete and uniquely addressed. No row
was removed, relabeled N/A, or weakened.

## 12. Harness and Engineering Results

| Gate | Result |
|---|---|
| Focused repaired C07 | 75 passed |
| C06 regression | 66 passed |
| C05 regression | 98 passed |
| C04 regression | 31 passed |
| C03 regression | 77 passed |
| C02 regression | 26 passed |
| C01 regression | 39 passed |
| W2 scenario/HGT regression | 154 passed |
| Local non-integration | 764 passed; 48 deselected |
| PostgreSQL / integration, remote | 48 passed; 764 deselected |
| Ruff | PASS |
| Strict mypy | PASS; 124 source files |
| `git diff --check` | PASS |
| `docker compose config --quiet` | PASS |

The only pytest warning is the existing Starlette/httpx deprecation warning;
it does not change the results. Guarded local PostgreSQL integration was not
run because the established database safety variables were unset. Remote
exact-SHA CI supplied the authoritative integration result.

## 13. Runtime and Evaluator Source Integrity

The following remained byte-identical to the repair entry SHA:

```text
src/flowlens/evaluation/c07_policy.py
src/flowlens/evaluation/c07_validation.py
src/flowlens/evaluation/c07_recommendation.py
src/flowlens/evaluation/c07_replay.py
src/flowlens/decision/*
src/flowlens/data/*
```

The repair changes no runtime/evaluator behavior. It changes what the test
harness proves by binding the runtime builders to real W2 business rows.

## 14. HGT Isolation Verification

**EVALUATED:** PASS. Protected HGT may select the offline test case/order and
is supplied to the protected C07 evaluator only after both C01-C05 packets are
frozen. It is not accepted by, imported into, or consulted by
`packet_from_dataset(...)` or the unchanged C01-C05 builder chain. Fresh
runtime import/capability audits pass.

## 15. Temporal and Future-Leakage Verification

**EVALUATED:** PASS. Each paired baseline/scenario replay uses one identical,
deterministic `as_of_time` inside both dataset horizons and not earlier than
the actual selected Sales Order `order_at`. Admission remains controlled by
the unchanged C02 projection semantics. No future or HGT field is projected
into runtime evidence.

## 16. Operational Mutation Verification

**EVALUATED:** PASS / NONE. Packet construction and evaluation leave canonical
baseline and scenario business payloads byte-identical. There is no SO, WO,
PO, Delivery, production, procurement, supplier, quality, API, worker, schema,
database, filesystem, network, model, or operational write capability.

## 17. Determinism and Replay Result

| Property | Result |
|---|---|
| Deterministic protected order selection | PASS |
| Paired common decision time | PASS |
| Baseline packet independently built from baseline rows | PASS |
| Scenario packet independently built from scenario rows | PASS |
| Scenario-created arrival-only has no fake baseline packet | PASS |
| Same-process canonical replay | PASS |
| Fresh-process/hash-seed replay | PASS |
| Dataset immutability | PASS |

## 18. Repair Exact-SHA CI Evidence

[Run #70 / `36424098689`](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/36424098689)
proved repair SHA `3c5df35528fbe9cd0f77d299a394da265d7ec9db`:

```text
Classify change: SUCCESS
Class / gate: I / FULL_EXACT_SHA
Quality gate: SUCCESS
Integration: 48 PASS / 764 DESELECTED
Non-integration: 764 PASS / 48 DESELECTED
Ruff: PASS
Mypy: PASS
Docker Compose smoke: SUCCESS
Publication proof: SKIPPED
Verification gate: SUCCESS
Workflow: SUCCESS
```

## 19. Separate Report Publication Proof

This report and `docs/CURRENT_STATE.md` are the entire authorized publication
commit. Its immutable SHA must classify `P / PUBLICATION_EXACT_SHA`, pass
Publication proof and Verification, and skip Quality and Docker Compose. Its
own SHA and CI run cannot be embedded in the same commit; the final Codex
handoff records them after the publication gate.

## 20. Git / GitHub State Before Report Delta

Local HEAD, tracking HEAD, direct-remote branch head and PR #6 head matched
repair SHA `3c5df35528fbe9cd0f77d299a394da265d7ec9db`; the working tree was clean
and synchronization was `0 / 0`. Main remained
`9d18ddde9fe933952a2661ee1419f13c8577605d`. PR #6 remained open, draft and
unmerged with auto-merge absent/disabled.

## 21. Known Limitations

1. C07 produces `RecommendationEvaluation` only; `OutcomeEvaluation` remains
   deferred.
2. Metrics are categorical measurements of the frozen packet/replay state and
   are not causal or outcome claims.
3. `EFFECTFUL_NOT_OBSERVABLE` correctly yields non-applicable metrics where
   the effect is outside the frozen decision-time observation boundary.
4. The protected HGT plane remains offline test/evaluation infrastructure and
   is not a runtime capability.

## 22. Newly Discovered Debt and Resolution

The pre-report audit found one replay-proof defect: family-specific synthetic
fixtures made the real replay circular. `W03-C07-REPAIR-01` resolves it in the
test/replay harness only. No runtime or evaluator source defect was found.

## 23. Findings by Severity

```text
BLOCKER: NONE OBSERVED AFTER REPAIR
HIGH: NONE OBSERVED AFTER REPAIR
MEDIUM: NONE OBSERVED AFTER REPAIR
LOW: NONE OBSERVED AFTER REPAIR
RESOLVED PRE-REPORT FINDING: W03_C07_REPLAY_PROOF_MISMATCH
```

These are Codex implementation/harness results, not an independent GPT C07
review or Human acceptance.

## 24. Reviewer Questions

1. Does the repaired six-case harness prove actual W2 row-to-packet binding
   without expected-family or HGT leakage?
2. Are baseline/scenario row closure, source identity/value binding and actual
   `SalesOrder.order_at` use complete and faithful to frozen C02 semantics?
3. Does the separation between real replay and adversarial synthetic fixtures
   preserve H1-H38 without circular positive evidence?
4. Are `False` and `None` descriptive metrics recorded faithfully without
   being treated as gate failures or business-accuracy claims?
5. Is HGT demonstrably unavailable until protected offline evaluation?

## 25. Current Status

```text
W03-C07: IMPLEMENTED / REPLAY-PROOF REPAIRED / CODEX VERIFIED / PENDING GPT REVIEW
ORIGINAL IMPLEMENTATION SHA: 90f159bf444bd1a0541fbc7fdb48188825ac53e4
ORIGINAL IMPLEMENTATION CI: RUN #69 / 36377688015 / PASS / I / FULL_EXACT_SHA
PRE-REPORT AUDIT: W03_C07_REPLAY_PROOF_MISMATCH
REPAIR SHA: 3c5df35528fbe9cd0f77d299a394da265d7ec9db
REPAIR CI: RUN #70 / 36424098689 / PASS / I / FULL_EXACT_SHA
GPT C07 REVIEW: PENDING
HUMAN C07 ACCEPTANCE: PENDING
C07 CLOSED: NO
C08 AUTHORIZED: NO
STATUS: REVIEW_READY — EFFECTIVE ONLY AFTER THIS REPORT COMMIT'S PUBLICATION GATE
```

## 26. Next Authorized Action

After this report commit receives successful exact-SHA publication proof and
final synchronization passes, the next action is **GPT C07 independent
review**. No C08 work is authorized.

## Machine-readable harness summary

```json
{
  "round_id": "W03-C07",
  "task": "W03-C07-I/H/R",
  "repair_task": "W03-C07-REPAIR-01",
  "round_entry_sha": "6e44af5159af50f4e69871425fed462ccb80adf9",
  "original_implementation_sha": "90f159bf444bd1a0541fbc7fdb48188825ac53e4",
  "repair_sha": "3c5df35528fbe9cd0f77d299a394da265d7ec9db",
  "pre_report_audit": "W03_C07_REPLAY_PROOF_MISMATCH",
  "repair_scope": "TEST_REPLAY_HARNESS_ONLY",
  "runtime_source_changes": "NONE",
  "evaluator_source_changes": "NONE",
  "proof": {
    "real_dataset_to_packet_binding": "PASS",
    "actual_source_record_identity": "PASS",
    "actual_source_field_value_binding": "PASS",
    "actual_sales_order_order_at": "PASS",
    "expected_family_injection": "ABSENT",
    "synthetic_c05_helpers_in_real_replay": "ABSENT",
    "baseline_scenario_independent_derivation": "PASS",
    "hgt_pre_freeze_runtime_access": "NONE",
    "hgt_protected_evaluation_access": "YES_OFFLINE_ONLY",
    "dataset_mutation": "NONE",
    "same_process_replay": "PASS",
    "fresh_process_replay": "PASS",
    "h1_h38": "PASS",
    "r1_g1_g8": "PASS"
  },
  "engineering": {
    "focused_c07": "PASS: 75",
    "c06_regression": "PASS: 66",
    "c05_regression": "PASS: 98",
    "c04_regression": "PASS: 31",
    "c03_regression": "PASS: 77",
    "c02_regression": "PASS: 26",
    "c01_regression": "PASS: 39",
    "w2_regression": "PASS: 154",
    "remote_integration": "PASS: 48 / 764 deselected",
    "non_integration": "PASS: 764 / 48 deselected",
    "ruff": "PASS",
    "mypy": "PASS: 124 source files",
    "compose_config": "PASS"
  },
  "ci": {
    "original_run_number": 69,
    "original_run_id": 36377688015,
    "repair_run_number": 70,
    "repair_run_id": 36424098689,
    "class": "I",
    "gate": "FULL_EXACT_SHA",
    "quality_gate": "PASS",
    "docker_compose_smoke": "PASS",
    "publication_proof": "SKIPPED",
    "verification_gate": "PASS"
  },
  "review": {
    "gpt_c07": "PENDING",
    "human_c07_acceptance": "PENDING",
    "c07_closed": false,
    "c08_authorized": false,
    "review_ready_effective_after_report_publication": true
  }
}
```
