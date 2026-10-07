# FlowLens W04-C05 Development Round Report

Date: 2026-10-07. Branch: `feat/w04-evidence-investigation`.

Implementation: **COMPLETE / REVIEW_READY**, subject to the report publication
gate described below. Human C05 implementation authorization: **APPROVED**.
The supplied GPT deep design review R1 was PASS. This document does not perform
independent implementation review, Human acceptance, or checkpoint closeout.

## Authorized task and resulting behavior

The authorized task is W04-C05 — Findings / Conflicts / Uncertainty, from the
human-approved V1 handoff package. The pasted user request expressly adopts the
task, Design Master V1, and deep review R1; attachment contents were treated as
task material within that request, without granting additional authority.

The new pure module accepts the exact frozen W03 DecisionPacket and C01-C04
investigation artifacts. It validates their original envelopes, derives one
bounded FindingRecord per exact C03 question, records only the eleven approved
conflict classes, and projects a question-scoped UncertaintyRegister. It has no
database, navigation, model, Human-event, summary, or operational authority.

The only new runtime source is `src/flowlens/investigation/c05_findings.py`.
The only new harness is `tests/test_investigation_findings.py`. No package
initializer, frozen upstream source, existing test, or production control was
edited. The stale W03 phase statement in AGENTS.md was not changed; its authority
hierarchy places the current authorized task first, while all frozen W1/W2/W03
invariants remain protected.

## Exact source chain and native CI

| Boundary | Exact source SHA | Native CI | Actual classification / proof | Result |
|---|---|---|---|---|
| Entry | `783234ac0ca1ba5c2b33d46f8576a12c2184114c` | #107 / `37573283883` | C / FULL_EXACT_SHA | SUCCESS |
| Stage A | `ae7bda16d7bce15110948627f70ff450b8f911e9` | #108 / `37588123629` | C / FULL_EXACT_SHA | SUCCESS |
| Stage B | `3386b2637f0b0e3f0972a07ee0bea4ad8181cb5f` | #109 / `37598447727` | I / FULL_EXACT_SHA | SUCCESS |

[Entry CI](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37573283883),
[Stage A CI](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37588123629),
and [Stage B CI](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37598447727)
were checked against their exact commit identities. Classifier output, rather
than the anticipated class in the task prompt, controls the proof requirement.

Stage A changed exactly:

- `docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json`
- `docs/w04/checkpoints/c05/W04_C05_HUMAN_AUTHORIZATION.md`
- `docs/w04/checkpoints/c05/W04_C05_CONTEXT_LOCK.md`

Its commit message was `docs(w04-c05): authorize findings source`. The supplied
human approval was materialized byte-for-byte. C05 runtime/test files did not
exist before Stage A's exact-SHA Verification PASS.

Stage B changed exactly:

- `src/flowlens/investigation/c05_findings.py`
- `tests/test_investigation_findings.py`

Its commit message was
`feat(w04-c05): derive bounded findings conflicts uncertainty`.
Both commits were normally pushed to the existing feature branch. There was no
amend, rebase, force push, history rewrite, main write, merge, or branch deletion.

Committed Stage B source blob:
`31384426ba9c733bc5bdbf3b09a3d206c8182586`.
Committed Stage B test blob:
`73275b7194a171610e4a1d0cafec973279a12534`.

## Admission, provenance, and scalar semantics

Admission proceeds through the exact DecisionPacket and frozen W03
`validate_c05_packet`, exact C02 case binding, exact C03 question/plan binding,
and exact C04 query-set binding. Slices are exact tuples of exact EvidenceSlice
objects with exact nested EvidenceObservation tuples. Original structural and
derived identity claims are checked before detached reconstruction and full
canonical-envelope comparison. A tampered identity is never refreshed into
acceptance.

Every query/slice index binds the case, plan, step, question, query, and as-of
identities. Observations must match that query's family, requested field, single
allowed trust class, and expected relationship. Availability and event metadata
cannot exceed the decision cutoff. Freshness is an exact FreshnessStatus value.
Actual event scalar timestamps cannot conceal future events behind admissible
metadata. Known plans and commitments may point beyond the cutoff.

Each `c04prov_` digest is recomputed with the frozen canonical SHA-256 formula:
navigation contract version `w04-c04-navigation-v1`, packet dataset version and
hash, source family/record/field/raw value, event time, available time, freshness,
trust, and relationship. Typed values and their canonical wire strings retain
the same digest. This validates the artifact envelope; it does not establish
database truth or replace C04/C08 database replay. C05 never reruns navigation.

The private field decoder is closed by exact family/field pairs. It accepts aware
datetime values or canonical UTC datetime wire strings, finite nonnegative
Decimal values or their canonical wire strings, exact nonnegative integers
(excluding bool), and the evaluated material/result strings. There is no float
conversion or heuristic type inference. Naive timestamps, malformed/noncanonical
wire values, nonfinite Decimal strings, negative quantities, bool quantities,
and invalid result vocabulary fail with `C05_EVIDENCE_VALUE_INVALID`.

Explicit nulls are retained as uncertainty, with nullable actual timestamps
handled only where the approved predicate permits them. A missing field is
distinct from explicit `None`; missing receipt or delivery quantity never
becomes zero. The same exact observation can legitimately occur in multiple
question scopes.

The eleven stable public errors are exactly the task's closed surface:
`C05_INVALID_DECISION_PACKET`, `C05_CASE_BINDING_MISMATCH`,
`C05_PLANNING_BINDING_MISMATCH`, `C05_QUERY_SET_MISMATCH`,
`C05_EVIDENCE_SET_MISMATCH`, `C05_EVIDENCE_PROVENANCE_MISMATCH`,
`C05_EVIDENCE_VALUE_INVALID`, `C05_FINDING_SET_MISMATCH`,
`C05_CONFLICT_SET_MISMATCH`, `C05_UNCERTAINTY_REGISTER_MISMATCH`, and
`C05_OUTPUT_REFERENCE_MISMATCH`. Inherited exception details are suppressed.

## Finding and status policy

Questions bind through exactly one packet signal ID in their trigger refs;
`question_code` is not parsed. Findings preserve question order.

| SignalType | Exact finding code | Bounded predicate / boundary |
|---|---|---|
| SUPPLIER_LATE_RECEIPT | W04_C05_ASSOCIATED_RECEIPT_LATENESS | Associated actual receipt after promise, or explicit outstanding quantity after promise; complete associated evidence is required for contradiction. |
| MATERIAL_TIMING_RISK | W04_C05_ASSOCIATED_MATERIAL_TIMING_WARNING | Exact material-ID association; actual receipt after need-by, outstanding promised receipt after need-by, or outstanding quantity after need-by. Contradiction requires a complete associated PO scope for every requirement. |
| QUALITY_FAILURE | W04_C05_RECORDED_QUALITY_FAILURE | Recorded failed quantity greater than zero; contradiction requires nonempty complete inspection scope with all failed quantities zero. |
| REWORK_PRESENT | W04_C05_RECORDED_REWORK | Explicit rework quantity greater than zero; contradiction requires nonempty explicit rows all zero. No rows remain missing. |
| QUALITY_DISPOSITION_UNKNOWN | W04_C05_QUALITY_DISPOSITION_UNRESOLVED | Always UNKNOWN; PASS does not establish release or final disposition. |
| QUEUE_DELAY | W04_C05_START_SLIPPAGE_PROXY | Actual start after planned start, or explicit null actual start after planned start is due. This is a proxy, not measured queue duration or a capacity cause. |
| CAPACITY_PRESSURE | W04_C05_CAPACITY_PRESSURE_UNRESOLVED | Always UNKNOWN; order-centric work-center context does not establish complete competing workload or capacity allocation. |
| DELIVERY_RISK | W04_C05_DELIVERY_COMMITMENT_WARNING | Explicit complete delivery quantities establish remaining quantity before overdue/plan warning. Fulfillment contradiction requires explicit quantities proving delivered total at least order quantity. Empty delivery scope is missing. |

Inherited UNKNOWN is a hard gate: supporting and contradicting refs are empty,
even when additional fresh observations would otherwise satisfy a predicate.
Disposition and capacity also always remain UNKNOWN. Relevant conflicts keep an
ACTIVE finding UNRESOLVED. Otherwise admissible support precedes complete
contradiction without an evaluation gap, then UNRESOLVED. A positive witness may
coexist with explicit gaps elsewhere, retaining the corresponding uncertainty.
Explicit fulfillment does not depend on unrelated work-order fields.

Only DIRECT_FACT or ASSOCIATIVE_EVIDENCE with FRESH or NOT_APPLICABLE freshness
can support/contradict. STALE, EXPIRED, and UNKNOWN freshness contribute explicit
uncertainty. FORBIDDEN trust is rejected. Participating associative evidence
produces ASSOCIATIVE_ONLY context and may support only the two ASSOCIATED codes;
it never becomes allocation, causality, probability, remedy efficacy, or action
authority.

## Conflicts, uncertainty, and output validation

The only emitted conflict codes are:

- `C05_CONFLICT_DUPLICATE_FIELD_VALUE`
- `C05_CONFLICT_WORK_ORDER_ACTUAL_WINDOW`
- `C05_CONFLICT_OPERATION_ACTUAL_WINDOW`
- `C05_CONFLICT_REWORK_WINDOW`
- `C05_CONFLICT_PO_RECEIPT_BEFORE_ORDER`
- `C05_CONFLICT_DELIVERY_BEFORE_ORDER`
- `C05_CONFLICT_QUALITY_RESULT_QUANTITY`
- `C05_CONFLICT_PO_QUANTITY_EXCEEDS_ORDERED`
- `C05_CONFLICT_WO_COMPLETION_EXCEEDS_PLANNED`
- `C05_CONFLICT_DELIVERY_EXCEEDS_ORDER`
- `C05_CONFLICT_SUPPORT_VS_CONTRADICTION`

Temporal rules use TIMESTAMP_CONFLICT; logical/quantity rules use VALUE_CONFLICT.
Support-versus-contradiction uses DIRECT_VS_DIRECT when all witnesses are direct,
otherwise VALUE_CONFLICT. Reserved DIRECT_VS_DERIVED and IDENTITY_CONFLICT remain
unused. Planned/actual differences and different valid records alone are not
conflicts. There is no vote, confidence score, or automatic conflict resolution.

Every question has one FORBIDDEN_INFERENCE item preserving its exact frozen
forbidden codes and question identity. Additional types are bounded to
UNKNOWN_EVIDENCE, MISSING_EVIDENCE, STALE_EVIDENCE, CONFLICTING_EVIDENCE,
ASSOCIATIVE_ONLY, and UNRESOLVED_QUESTION. References are exact question-local
question/query/slice/observation/conflict IDs or frozen forbidden codes. Business
record IDs and invented references are not accepted. Registers are sorted unique
by artifact ID and remain bound to the case and exact questions.

The validator revalidates upstream inputs, rebuilds expected outputs, validates
original supplied finding/conflict/item/register envelopes, reconstructs nested
outputs, and compares complete canonical envelopes. It rejects omission,
injection, wrong status/code/order, cross-question references, and original
artifact ID/content hash tampering.

## Direct K01-K48 proof mapping

All listed proofs are direct tests in `tests/test_investigation_findings.py`.
The primary names below are `test_` functions; supplementary tests strengthen
K06, K07, K15, K20, K45, and K47. All cases passed in the native Stage B full
suite at the exact implementation SHA.

| Requirement | Primary test / proof | Result |
|---|---|---|
| K01 | k01_exact_w03_packet: exact type, identity, nested packet defects | PASS |
| K02 | k02_exact_case: exact case type, original identity, packet binding | PASS |
| K03 | k03_exact_planning: tuple, omission, order, question identity, plan | PASS |
| K04 | k04_exact_queries: exact query set, fields, order, identity | PASS |
| K05 | k05_exact_slices: one-to-one tuple/count/order/case/plan/query/time | PASS |
| K06 | k06_original_nested_identity; collection, identity-type and missing-slot attacks | PASS |
| K07 | k07_exact_observation_binding; hidden future actual scalar | PASS |
| K08 | k08_provenance_recomputation: digest/value/record/availability mutations | PASS |
| K09 | k09_signal_binding_without_question_code | PASS |
| K10 | k10_exact_eight_codes | PASS |
| K11 | k11_one_per_question, including the empty inactive projection | PASS |
| K12 | k12_same_process_determinism_and_immutability | PASS |
| K13 | k13_fresh_process_actual_wire_reparse | PASS |
| K14 | k14_multiple_hash_seeds: 1, 17, 123, plus default seed 0 in fresh-process proofs | PASS |
| K15 | k15_actual_c04_typed_and_wire_parity; closed scalar malformed matrix | PASS |
| K16 | k16_unknown_hard_gate_rejects_upgrade | PASS |
| K17 | k17_empty_evidence_never_negative_proof | PASS |
| K18 | k18_forbidden_trust_rejected | PASS |
| K19 | k19_freshness_eligibility: STALE/EXPIRED/UNKNOWN/NOT_APPLICABLE | PASS |
| K20 | k20_association_never_causal; associative trust promotion rejected | PASS |
| K21 | k21_supplier_support: late actual / outstanding after promise | PASS |
| K22 | k22_supplier_complete_contradiction | PASS |
| K23 | k23_supplier_incomplete: no PO, no match, missing/null values | PASS |
| K24 | k24_material_three_predicates and positive witness with gap | PASS |
| K25 | k25_material_complete_contradiction | PASS |
| K26 | k26_material_association_gaps | PASS |
| K27 | k27_quality_quantity: positive/zero/missing/null/different valid rows | PASS |
| K28 | k28_rework_explicit_rows: positive/zero/no rows/null | PASS |
| K29 | k29_disposition_always_unknown | PASS |
| K30 | k30_queue_proxy_support: late start / explicit not started | PASS |
| K31 | k31_queue_proxy_complete_scope and missing-field boundary | PASS |
| K32 | k32_capacity_always_unknown | PASS |
| K33 | k33_delivery_warning_support: overdue / plan with remaining | PASS |
| K34 | k34_delivery_fulfilled_contradiction, independent of unrelated fields | PASS |
| K35 | k35_delivery_never_default_zero | PASS |
| K36 | k36_closed_timestamp_conflicts: all five temporal rules | PASS |
| K37 | k37_closed_value_conflicts: quality result/sum, PO/WO/delivery quantities | PASS |
| K38 | k38_support_contradiction_conflict and duplicate-field conflict | PASS |
| K39 | k39_no_majority_vote_or_unknown_resolution | PASS |
| K40 | k40_bounded_uncertainty_projection: all seven types | PASS |
| K41 | k41_forbidden_codes_preserved_exactly | PASS |
| K42 | k42_conflicting_uncertainty_exact_refs | PASS |
| K43 | k43_register_sorted_case_question_integrity and wire roundtrip | PASS |
| K44 | k44_references_are_question_scoped: injected/cross-question/business refs | PASS |
| K45 | k45_output_tamper_rejected; missing register slots | PASS |
| K46 | k46_no_semantic_authority_expansion | PASS |
| K47 | capability AST negative controls, fresh import, live external capability denial | PASS |
| K48 | k48_committed_source_lifecycle_and_verifier: AUTHORIZED and real-identity CLOSED model | PASS |

Measured with Python AST and pytest collection after final file edits:

```text
TEST FUNCTIONS:             56
PARAMETERIZED FUNCTIONS:    32
EXPANDED CASES:             188
DIRECT REQUIREMENTS:        K01-K48 / 48
```

Fresh subprocesses actually receive serialized upstream inputs through stdin.
C01 artifacts are parsed with their real `from_json` readers. Legacy W03 packet
marshalling uses a test-only typed exemplar to reconstruct its declared field
types and assert the exact canonical packet bytes; it does not add a public W03
parser or use textual scalar heuristics. The scalar proof also runs the real
frozen C04 navigation with its existing test engine, consumes typed slices, then
compares reparsed wire slices and fresh-process outputs.

Capability proofs include source AST negative controls, a fresh runtime import
excluding DB/navigation/data/evaluation/model modules, and live denial of file,
network, subprocess, SQLite, navigation/connection, environment, entropy, and
time capabilities. Frozen structural type introspection remains unchanged;
C05 introduces no direct eval, exec, dynamic import, or time-now call.

## Regression and quality evidence

| Proof | Actual result |
|---|---|
| Local C05 semantic harness | 186 passed / 2 lifecycle cases deferred to committed state; 560.27s |
| Local committed K48 | 2 passed; both lifecycle shapes checked against real committed source identities |
| Final original-slot/reference/capability edge run | 44 passed; 124.79s |
| Local unchanged C01/C02/C03/C04/DEVCTRL pack | 1,029 passed / 3 committed-source checks deferred; 707.76s |
| Local committed B36/P40/N52 source proofs | 3 passed; 24.28s |
| Local W03 core contracts/serialization/context/evidence/snapshot/temporal | 65 passed; 4.34s |
| Unchanged production source-evolution verifier | PASS at exact Stage B SHA; nine registered added source paths |
| Native Stage B non-integration | 2,234 passed / 70 deselected / 1 warning; 3478.08s |
| Native Stage B integration | 70 passed / 2,234 deselected / 1 warning; 337.67s |
| Native Stage B Ruff | PASS |
| Native Stage B strict mypy | PASS / 157 source files |
| Native Stage B dependency lock | PASS / 43 packages |
| Native Stage B Docker Compose smoke | PASS |
| Native Stage B Verification | PASS |

Stage A's native full proof independently passed 2,046 non-integration and 70
integration cases, Ruff, strict mypy (155 files), lock (43 packages), Compose,
W03 gate, and Verification before implementation began. Local Stage A focused
evidence included 438 inherited planning/navigation/source-evolution cases,
719 contracts/binding/query/control cases, 65 W03 core cases, and exact committed
source proof. These are prior authorization proofs, not substitutes for Stage B.

Native Stage B W03 gate summary:

| Frozen family | Selectors | Cases | Result |
|---|---:|---:|---|
| F01 CORE_CONTRACTS | 3 | 3 | PASS |
| F02 TEMPORAL_SEMANTIC_TRUST | 3 | 7 | PASS |
| F03 SIGNAL_DIAGNOSIS_FAIL_CLOSED | 4 | 10 | PASS |
| F04 COUNTERFACTUAL_ISOLATION | 3 | 5 | PASS |
| F05 RECOMMENDATION_ABSTENTION | 4 | 11 | PASS |
| F06 HUMAN_AUTHORITY_AUDIT | 4 | 6 | PASS |
| F07 PROTECTED_EVALUATION_REPLAY | 3 | 11 | PASS |
| F08 LLM_GROUNDING_SCHEMA_INJECTION | 6 | 6 | PASS |
| F09 REAL_DATASET_BINDING_DIRECTION | 3 | 6 | PASS |
| F10 RUNTIME_CAPABILITY_ISOLATION | 5 | 20 | PASS |
| TOTAL | 38 | 85 | PASS |

The gate's implementation SHA is exactly
`3386b2637f0b0e3f0972a07ee0bea4ad8181cb5f`; frozen gate manifest SHA-256 is
`bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990`.
No protected evaluation material is included in this report.

## Source lifecycle and unchanged boundaries

Committed W04 manifest SHA-256:
`11f310234ac973b01ebad6c13a56b5c7fe13eb506db6d6b930e045ce88b10557`.
C01-C04 entries remain CLOSED and unchanged. C05 remains exactly
AUTHORIZED / null freeze / one null source blob at the authorized runtime path.
K48's CLOSED model is read-only test data with a real ancestor commit and exact
HEAD blob; it does not close the repository checkpoint.

The complete task delta is limited to the three Stage A paths, two Stage B paths,
and this one Stage C report. Runtime source change is C05 only. C01-C04 sources,
W03/DB/data models, operational schema, Alembic semantics, canonical hashing,
deterministic generator/scenario semantics, HGT identity/isolation, existing
tests, verifier/classifier/workflow, dependency files, and app/runtime routing
remain unchanged. Runtime operational mutation: NONE.

## Local limitations and resolved implementation defects

The local sandbox helper failed to spawn commands; scoped authorized commands
were executed through the approved escalation route. There was no automatic
approval-review rejection. Windows default pytest temporary/cache directories
denied access; reruns used fresh task-specific writable scratch directories and
disabled pytest's cache provider, without changing repository configuration.

The Docker executable was present but its local daemon was unavailable; uv was
not on the local command PATH. Native locked Linux CI supplies the real
PostgreSQL, dependency-lock, full regression, and Compose proof. No dependency
was installed or changed to work around local limitations.

Two inherited Windows CRLF-only full-regression comparisons were already known:
`test_c06_harness.py::test_frozen_c01_and_c05_sources_match_context_lock` and
`test_c09_ci_gate.py::test_frozen_manifest_schema_families_counts_and_content`.
Their frozen sources/tests were not edited. The local selected packs above
passed; the complete native Linux Stage B suite passed, including those tests.
This report does not claim a complete local Windows full-suite PASS.

Pre-push Type-A defects in the new files were repaired within scope, including a
negative test's wrong case field, ordinary imports/typing/style defects, closed
conflict-code error classification, and missing-original-slot handling. The
Stage A inherited-suite wrapper once used a stale entry expected SHA after the
authorized Stage A commit; its tests passed and a separate exact-Stage-A verifier
probe passed. This was resolved expected-SHA bookkeeping, not an external
context change or a relaxed proof requirement. Stage B received no source edits
after its push and native CI.

The native suites emitted one inherited Starlette/httpx deprecation warning per
test phase. It was non-failing; dependency/configuration changes were outside
this task and were not made. No architecture/product conflict or out-of-scope
repair was required.

## Stage C publication and review boundary

This report was created only after Stage B's exact-SHA Classify, Quality,
Compose, W03, and Verification all passed and its overall CI was SUCCESS.
Stage C changes this report path only, with commit message
`docs(w04-c05): publish findings proof`, followed by normal push.

The report's own commit SHA and workflow run do not yet exist inside the source
being committed. Its actual classifier result and exact-SHA Publication /
Verification must be checked after push and attested in the final handoff;
no future CI result is claimed here. No amend is needed to insert a circular
self-commit identity into the report.

PR #7 was refreshed at Stage B and is OPEN / DRAFT / UNMERGED, with exact Stage B
head. Main remains the accepted W03 baseline and the feature branch is retained.

```text
GPT INDEPENDENT IMPLEMENTATION REVIEW:
PENDING

HUMAN C05 ACCEPTANCE:
PENDING

C05 CLOSEOUT:
NOT AUTHORIZED

C05 MANIFEST STATE:
AUTHORIZED

W04-C06:
NOT AUTHORIZED
```
