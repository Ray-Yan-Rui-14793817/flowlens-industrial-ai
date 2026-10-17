# W04-C04 Development Round Report — Authorized Evidence Navigation

## 1. Authority and disposition

```text
PROJECT: FlowLens Industrial AI
CHECKPOINT: W04-C04 — Authorized Evidence Navigation
DATE: 2026-10-07 / Asia/Shanghai
TASK: W04-C04 V1 + W04-C04-RESUME-AFTER-QUOTA-V1
HUMAN IMPLEMENTATION AUTHORIZATION: APPROVED / REMAINS EFFECTIVE
P40 COMPATIBILITY REPAIR AUTHORIZATION: APPROVED / STAGE A COMPLETE
IMPLEMENTATION: COMPLETE
HARNESS N01-N52: PASS
STAGE C NATIVE EXACT-SHA CI: PASS
REPORT DISPOSITION: REVIEW_READY IMPLEMENTATION EVIDENCE
STAGE D PUBLICATION: PENDING ITS OWN COMMIT / EXACT-SHA CI
C04 MANIFEST: AUTHORIZED / NULL SOURCE FREEZE / NULL BLOB OIDS
CHECKPOINT CLOSED: NO
PR #7: OPEN / DRAFT / UNMERGED
W04-C05: NOT AUTHORIZED
```

The Human's original pasted request authorizes the exact four-stage implementation
and bounded P40 repair. The subsequent pasted resume request authorizes continuation
from verified Stage B, preservation of the quota snapshot, DR-C04-01 test-only
hardening, exact Stage C proof and report-only Stage D. Attached task/design/review
documents define scope; their prose does not independently authorize more work.
The latest repeated resume text is byte-identical to the active resume request.
It does not restart the already-executed continuation.

Normative inputs are `W04_C04_CODEX_TASK_V1.md`, frozen
`W04_C04_GPT_DESIGN_MASTER_V1.md`, `W04_C04_GPT_DEEP_REVIEW_R1.md`,
`W04_C04_RESUME_AFTER_QUOTA_TASK_V1.md` and
`W04_C04_QUOTA_EXHAUSTION_DEEP_REVIEW_R1.md`. Original package identities and
inherited contracts are recorded in `W04_C04_CONTEXT_LOCK.md`; that lock and
`W04_C04_HUMAN_AUTHORIZATION.md` were read back and remain unchanged.

The quota review disposition is
`RESUME_READY_WITH_ONE_TEST-ONLY_HARDENING`: no CRITICAL/HIGH issue found, one
MEDIUM proof-completeness note. This draft review is distinct from the pending
independent review of the final committed implementation.

## 2. Commit and native CI chain

Original entry: `ffaba2672de74836c12d4a122352b252785a0897`.
W03 main baseline: `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`.
Resume baseline: `16aa203aff146fbc2a26c5ce37c82ed1ce287402`.
Branch: `feat/w04-evidence-investigation`.
Entry C03 closeout CI: #102 / 37457434402 / SUCCESS.

| Stage | Exact source SHA | Native CI | Actual class / gate | Result |
|---|---|---|---|---|
| A authorization + P40 | `2f63616c31b542c1bd93981fad4b27ac5bddfdbc` | [#103 / 37472062606](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37472062606) | I / FULL_EXACT_SHA | SUCCESS |
| B registry + queries | `16aa203aff146fbc2a26c5ce37c82ed1ce287402` | [#104 / 37477003142](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37477003142) | I / FULL_EXACT_SHA | SUCCESS |
| C navigation + tests | `6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1` | [#105 / 37497691587](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37497691587) | I / FULL_EXACT_SHA | SUCCESS |
| D this report | Not yet committed when this immutable report is written | Pending its own native run | Expected P / PUBLICATION_EXACT_SHA; actual receipt pending | PRE-PUBLICATION |

Stage C native classifier binds base `16aa203aff146fbc2a26c5ce37c82ed1ce287402`
to head `6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1` and exactly the three C paths
below, with reason `verified_source_head_delta`. Native Classify logs establish
actual routing; it is not inferred from filenames. No implementation commit was
amended. Each later stage began only after the preceding exact-SHA Verification
passed. Stage A/B were not repeated or amended during resume.

This report cannot contain its own future commit SHA/run result. Its publication
commit, actual class and exact-SHA publication/Verification receipt must be given
in the final handoff after that run completes; no post-CI amend is planned.

### Historical Stage A/B native proof

| Stage | Non-integration | Integration | Ruff | Strict mypy | Dependency lock | Compose / W03 / Verification |
|---|---|---|---|---|---|---|
| A | 1830 passed / 48 deselected / 1 warning / 1004.51 s | 48 passed / 1830 deselected / 1 warning / 137.31 s | PASS | PASS / 149 files | PASS / 43 packages | PASS / PASS 38/85 / PASS |
| B | 1922 passed / 48 deselected / 1 warning / 1622.47 s | 48 passed / 1922 deselected / 1 warning / 189.25 s | PASS | PASS / 152 files | PASS / 43 packages | PASS / PASS 38/85 / PASS |

Publication was SKIPPED in both full routes. These are historical verified
receipts, retained rather than rerun during resume.

### Stage A P40 compatibility repair

Only P40's final aggregate source-list expectation changed: it now sorts
manifest-declared paths for which committed `HEAD:path` exists, using
`git cat-file -e`. Worktree-only/untracked presence does not confer authorization.
Earlier exact C01/C02/C03 state/freeze/path/blob checks, generic verifier invocation
and verifier PASS assertion remain intact. An AST comparison verified that only
the final assertion changed.

Seven disposable Git probes passed: CLOSED bootstrap included; absent AUTHORIZED
excluded; worktree-only source excluded; committed AUTHORIZED included; later
CLOSED included; unexpected source rejected; missing CLOSED source rejected.
No production verifier/classifier/workflow changed.

## 3. Quota resume and exact source protection

Resume preflight verified clean tracked worktree/index, the three intended
untracked C files, local HEAD and origin feature HEAD equal to Stage B, the
expected branch, PR open/draft/unmerged and #104 SUCCESS. Before any edit, all
seven frozen Stage A/B blobs and all three quota-snapshot byte identities matched.
No reset, rebase, checkout-away, discard, history rewrite or force push occurred.

| Frozen Stage A/B path | Git blob, unchanged at Stage C |
|---|---|
| `docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json` | `cb562431242c5c6851aa6bb42f959c8fe7e0a7f3` |
| `tests/test_investigation_planning.py` | `2f326879b87fffcd1385a9188cf92ac40f4779b8` |
| `docs/w04/checkpoints/c04/W04_C04_CONTEXT_LOCK.md` | `ec0f6539987872bc2134505f919ceac7907922ed` |
| `docs/w04/checkpoints/c04/W04_C04_HUMAN_AUTHORIZATION.md` | `ee5d8490e9bfdc5f36d6d21620d953e66131ae1c` |
| `src/flowlens/investigation/c04_queries.py` | `dc22c7e532a4b62ccfffec2210bc2a6306d97234` |
| `src/flowlens/investigation/c04_registry.py` | `fbe6f0603d7b0634426ac0034033089eb55af4d7` |
| `tests/test_investigation_evidence_queries.py` | `54f43e27ce42c0ae6ea903d7b278b916748f40ed` |

| Quota Stage C draft | Snapshot Git blob | Snapshot SHA-256 |
|---|---|---|
| `src/flowlens/investigation/c04_navigation.py` | `98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4` | `f9517010c35da8b7e72a1d1c29a9dfadc225f3713cc64e3454d9087349241d9e` |
| `tests/test_investigation_evidence_navigation.py` | `ba0d3c9f89e8f2e83a58eba0ede81568f0ba9129` | `aad094f4bebabb10ddb68d06df809336259277d5e76de596614396d76cd0ea48` |
| `tests/integration/test_investigation_evidence_navigation_database.py` | `fab7e9180e19635eb886624d98c759a669ded5ec` | `ab9f85545a03dadadcf5f0c238684be9d49533abdbd9585ab57cfb78e57146bb` |

DR-C04-01 added one navigation unit test plus an explicit registry import. It
asserts all nine exact traversal-code values and identical ordered keys of
`_TABLES`, `_TRAVERSALS`, `_OWNERS`, the registry and a literal expected map.
Removing only that insertion/import reproduces the original unit-test SHA-256.
The final unit-test blob is `74e15223abc0accdfd3cb569764f9f94d5f3d70e`.
Runtime and integration-test bytes remain exactly equal to the quota snapshot.
The hardening passes; it exposed no Stage B mismatch.

Stage C adds exactly three files / 2257 lines, relative to Stage B:

```text
src/flowlens/investigation/c04_navigation.py                       483 lines
tests/test_investigation_evidence_navigation.py                  1019 lines
tests/integration/test_investigation_evidence_navigation_database.py 755 lines
```

The current three C04 runtime blobs are registry
`fbe6f0603d7b0634426ac0034033089eb55af4d7`, queries
`dc22c7e532a4b62ccfffec2210bc2a6306d97234`, and navigation
`98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4`. These are implementation evidence
identities, not accepted closeout freezes.

C01 freeze `084c2fea93d0e021994de015c986de9ff92bf9a3`, C02 freeze
`18648915414a26dddbdc904965663730ea631cf2` and C03 freeze
`42047bcfe6591f7c9ed9b0034bd94467401ba72f` and their CLOSED manifest entries remain
exact. Twenty-one inherited source/control blob or tree identities were checked
against the context lock. No W03/DB/data-model/schema/migration/dependency/control
path changed. Stage D is solely this report. Original task total is eleven
allowlisted paths; resume adds the three C files and this report only.

Resume package SHA-256 identities measured and matched its manifest:

| Artifact | SHA-256 |
|---|---|
| Quota-exhaustion Deep Review R1 | `ba9c4a42a31d62b30a66db87571634de01798d3f3e32877f16e0441c5f3e7008` |
| Resume Task V1 | `e6609d1a3fc87fd0b538b9c5cc763b20c14f3f95ee2c35666bb7e700184a2785` |
| Resume Prompt V1 | `88cf5bddfc6ebaa45ccab5e3c19f814660e8e6f874e0d6faa6efb8effe208f46` |

## 4. Closed registry, root and deterministic queries

Versions are `w04-c04-source-registry-v1`, `w04-c04-query-v1` and
`w04-c04-navigation-v1`. Registry/profile mappings are immutable, closed and
validated against frozen W03 `SOURCE_FIELDS`; exactly nine families and eleven
relationship-homogeneous profiles exist. No raw status field is requested.
Inventory, supplier/material master and product-material bridge families are
unregistered and rejected.

The root is exactly `EntityKey(key_name="sales_order_id",
key_value=case.subject_id)` in a singleton tuple. Callers supply no independent
key, family, field, traversal, relationship, trust, SQL, URL or path authority.

Query construction validates exact DecisionPacket, frozen `validate_c05_packet`,
exact C02 case/binding, exact question tuple/plan and C03 planning in that order.
Each query binds case/plan/step/question artifact IDs and case as-of, exact
profile fields, singleton trust and relationship. Families must be both required
and allowed by the frozen question, with profile trust allowed by that question.
Order is step ordinal, question family tuple order, then fixed profile order.
No new question, signal, diagnosis, candidate or recommendation is derived.

Validation rechecks original nested and outer identities, detached reconstruction
and complete canonical expected queries. Injection, omission, duplication,
reorder, field/key/profile/timing/binding changes are rejected. Same-process,
fresh-process and PYTHONHASHSEED 0/1/14793817 outputs match. Stage B has no database
or resource capability.

### Exact eleven profile field allowlists

Every tuple below is sorted; a family's profiles together partition its frozen
SOURCE_FIELDS.
Trust is DIRECT_FACT except the purchase profile, which is ASSOCIATIVE_EVIDENCE.

| Family/profile | Relationship | Exact requested fields |
|---|---|---|
| fact_sales_order | TARGET_RECORD | customer_id, order_at, order_quantity, priority, product_id, promised_delivery_at, sales_order_id |
| fact_work_order plan | DIRECT_FK | planned_end_at, planned_quantity, planned_start_at, product_id, sales_order_id, work_order_id |
| fact_work_order actual | DIRECT_EVENT | actual_end_at, actual_start_at, completed_quantity |
| fact_operation plan | DIRECT_FK | operation_id, planned_end_at, planned_start_at, sequence_number, work_center_id, work_order_id |
| fact_operation actual | DIRECT_EVENT | actual_end_at, actual_start_at |
| fact_material_requirement | DIRECT_FK | material_id, material_requirement_id, need_by_at, required_quantity, work_order_id |
| fact_purchase_order | MATERIAL_TIME_ASSOCIATION | actual_receipt_at, material_id, ordered_at, ordered_quantity, promised_receipt_at, purchase_order_id, received_quantity, supplier_id |
| fact_quality_inspection | DIRECT_EVENT | defect_category, failed_quantity, inspected_quantity, inspection_at, inspection_id, inspection_type, operation_id, passed_quantity, result, severity, work_order_id |
| fact_rework | DIRECT_EVENT | inspection_id, rework_end_at, rework_id, rework_quantity, rework_reason, rework_start_at, work_center_id, work_order_id |
| fact_delivery | DIRECT_EVENT | delivered_quantity, delivery_at, delivery_id, sales_order_id |
| dim_work_center | MASTER_DATA_CONTEXT | active_from, daily_capacity_hours, line_group, process_type, work_center_code, work_center_id |

### Exact nine adapters and traversal codes

SO denotes root SalesOrder, WO WorkOrder, OP Operation and MR MaterialRequirement.
Each join key is fixed: WO.sales_order_id=SO.sales_order_id; OP/MR/QI/RW.work_order_id
=WO.work_order_id; PO.material_id=MR.material_id; Delivery.sales_order_id=SO.sales_order_id;
WorkCenter.work_center_id=OP.work_center_id. The purchase path establishes an
association, not material allocation or causality.

| Family | Exact target PK | Traversal code | Fixed path |
|---|---|---|---|
| dim_work_center | work_center_id | ORDER_WORK_ORDER_OPERATION_WORK_CENTER | SO → WO → OP → WorkCenter |
| fact_delivery | delivery_id | ORDER_DELIVERY | SO → Delivery |
| fact_material_requirement | material_requirement_id | ORDER_WORK_ORDER_MATERIAL_REQUIREMENT | SO → WO → MR |
| fact_operation | operation_id | ORDER_WORK_ORDER_OPERATION | SO → WO → OP |
| fact_purchase_order | purchase_order_id | ORDER_WORK_ORDER_MATERIAL_PURCHASE_ASSOCIATION | SO → WO → MR → PurchaseOrder |
| fact_quality_inspection | inspection_id | ORDER_WORK_ORDER_QUALITY_INSPECTION | SO → WO → QualityInspection |
| fact_rework | rework_id | ORDER_WORK_ORDER_REWORK | SO → WO → Rework |
| fact_sales_order | sales_order_id | ORDER_TARGET | SO |
| fact_work_order | work_order_id | ORDER_WORK_ORDER | SO → WO |

## 5. Source context, read-only execution and temporal admission

`c04_navigation.py` is the sole C04 DB reader. It accepts a PostgreSQL Engine and
validated inherited inputs, opens one REPEATABLE READ transaction, executes fixed
`SET TRANSACTION READ ONLY`, and verifies SHOW isolation=`repeatable read` and
SHOW read_only=`on` before source reads. No caller SQL text is accepted.

The context gate requires exactly Alembic revision
`0002_industrial_data_foundation`, exactly one dataset_version row, packet dataset
ID/hash equality, exact date bounds containing as-of under frozen W03 policy,
and the exact target order in that dataset with aware order_at <= as-of.
Source exceptions are translated to stable C04 codes without exposing SQL/error
details. Query validation precedes connecting, including empty-plan execution.

Each SELECT is a fixed SQLAlchemy expression, DISTINCT, target-PK ordered and
limited to 4097 (=4096+1). Every joined owner table has an exact packet dataset
predicate; the root order/time predicates are fixed. The reader requests frozen
SOURCE_FIELDS plus dataset/join metadata, never raw status. Target rows are
deduplicated by PK; conflicting duplicates fail closed. Only the query's requested
projected fields are exposed.

| Source | SQL future row filter / actual mask |
|---|---|
| SO | order_at <= as-of |
| WO / OP | CASE admits actual_start_at/actual_end_at by their respective events; completed_quantity by WO.actual_end_at |
| PO | ordered_at <= as-of; receipt/received quantity masked by actual_receipt_at |
| QI | inspection_at <= as-of |
| RW | rework_start_at <= as-of; rework_end_at independently masked by its event |
| Delivery | delivery_at <= as-of |
| WorkCenter | active_from <= Shanghai as-of date |
| Plans / MR | Future planned values remain valid when already available under frozen target-order availability policy |

SQL gates are followed by unchanged W03 `project_record`, unchanged
`classify_source`, and frozen C01 observation/slice admission. Available/event
timestamps are aware and cannot exceed as-of; native equality-boundary cases are
admitted. Planned future dates are field values, not future observation times.
Missing/future actual values are omitted, preserving accepted W03 semantics.

## 6. Observation identity, trust, empty evidence and replay

Each observation's source_record_id is the exact target PK, source_field is an
exact requested field and source_value is the unaltered projected scalar.
event_time=projected observed_at; available_at=projected available_at; freshness,
relationship and trust come from W03 classification. Relationship and singleton
trust must match the query exactly; FORBIDDEN_INFERENCE is never emitted. All
current nine-family fields classify freshness NOT_APPLICABLE under frozen policy.

Provenance is `c04prov_` plus canonical SHA-256 over
navigation_contract_version, dataset_version, dataset_hash, source_family_code,
source_record_id, source_field, source_value, event_time, available_at,
freshness_code, trust_class and relationship_code. It binds policy and source
content, not invented causality; a reused observation retains the same identity.

One C01 EvidenceSlice is built per query, preserving query order and exact
case/plan/step/question/query/as-of refs. Observations are unique and sorted by
artifact_id. No-row/no-admissible-field queries yield bound empty slices; zero
queries yield an empty slice tuple after context validation. No UNKNOWN/default
observation, support, placeholder, FindingRecord, conflict or uncertainty artifact
is synthesized.

Caps are 4096 records/query and 65536 observations/slice, failing closed without
truncation. Validation re-executes exact queries in a new read-only transaction,
revalidates original nested/outer identities and compares complete canonical
slices. Rehashed value/provenance/ref/time/trust/relationship/freshness/identity
forgeries are rejected. Frozen C01 canonical scalar JSON behavior is retained:
Decimal/date/datetime source values become canonical strings on decoding; valid
wire roundtrips therefore compare canonically, without new type tags or hashes.
Execution itself retains the projected native scalar. Unit and native PG tests
prove the valid roundtrip and forged canonical-content rejection separately.

## 7. N01-N52 measured proof matrix

Q = `tests/test_investigation_evidence_queries.py`;
U = `tests/test_investigation_evidence_navigation.py`;
PG = `tests/integration/test_investigation_evidence_navigation_database.py`.
Names below are actual pytest function names; expanded parameters supply the
matrices. All Q/U/PG cases passed in Stage C native CI.

| ID | Requirement / actual proof function(s) | Result |
|---|---|---|
| N01 | Exact packet/W03 validator: Q:test_n01_packet_exact_type_and_frozen_validation; U:test_n01_n18_public_navigation_validates_before_connect | PASS |
| N02 | Exact C02 case binding: Q:test_n02_case_binding_is_exact | PASS |
| N03 | Exact frozen questions/plan: Q:test_n03_exact_frozen_questions_and_plan; Q:test_n01_n03_error_precedence | PASS |
| N04 | Nine immutable families: Q:test_n04_n06_exact_immutable_registry_and_field_partition | PASS |
| N05 | Eleven homogeneous profiles: Q:test_n04_n06_exact_immutable_registry_and_field_partition; PG:test_n19_n24_n32_n43_n51_all_adapters_native_replay_and_zero_mutation | PASS |
| N06 | Exact SOURCE_FIELDS partitions/status excluded: Q:test_n04_n06_exact_immutable_registry_and_field_partition | PASS |
| N07 | Exact singleton root: Q:test_n07_n13_n14_exact_projection_count_and_order | PASS |
| N08 | Unknown/nonplan family rejection: Q:test_n08_unregistered_and_nonplan_families_rejected | PASS |
| N09 | Extra/wrong root key rejection: Q:test_n09_exact_root_key_only | PASS |
| N10 | Field widening/subset/reorder rejection: Q:test_n10_exact_fields_cannot_be_changed | PASS |
| N11 | Relationship mismatch rejection: Q:test_n11_relationship_cannot_be_changed | PASS |
| N12 | Trust mismatch/widening/forbidden rejection: Q:test_n12_trust_cannot_be_widened_reclassified_or_forged | PASS |
| N13 | Exact count/real signal selection/zero plan: Q:test_n07_n13_n14_exact_projection_count_and_order; Q:test_n13_only_profiles_selected_by_real_frozen_signals; Q:test_n13_zero_step_plan_has_zero_queries | PASS |
| N14 | Stable order and tuple rejection: Q:test_n14_exact_query_tuple; Q:test_n07_n13_n14_exact_projection_count_and_order | PASS |
| N15 | Same-process determinism/input preservation: Q:test_n15_repeated_queries_preserve_input_and_full_envelope | PASS |
| N16 | Fresh-process/hashseed determinism: Q:test_n16_fresh_process_and_hashseed_determinism | PASS |
| N17 | Query/subclass/nested identity tamper: Q:test_n17_original_and_nested_identities_and_bindings | PASS |
| N18 | No query language/resource authority: Q:test_n18_no_query_language_or_resource_arguments; U:test_n18_unavailable_source_has_stable_error; U:test_n18_n52_runtime_ast_imports_and_public_boundary | PASS |
| N19 | RR/RO enforced: U:test_n19_fail_closed_transaction_state; PG:test_n19_n24_n32_n43_n51_all_adapters_native_replay_and_zero_mutation | PASS |
| N20 | Exact schema revision: U:test_n20_n22_source_context_must_match_exactly; actual PG context gate | PASS |
| N21 | Exact dataset/hash: U:test_n20_n22_source_context_must_match_exactly; PG:test_n21_native_hash_context_failure_is_read_only | PASS |
| N22 | Exact target order/time: U:test_n20_n22_source_context_must_match_exactly; native bound target reads | PASS |
| N23 | Every joined owner scoped in U:test_n23_n33_all_nine_adapters_have_fixed_owned_bounded_sql; bad rows in U:test_n23_n41_bad_source_records_fail_closed; native context rejection in PG:test_n23_foreign_owned_join_row_cannot_enter_a_single_dataset_context | PASS / bounded interpretation below |
| N24 | SO adapter: U:test_n23_n33_all_nine_adapters_have_fixed_owned_bounded_sql; PG all-adapters test | PASS |
| N25 | WO adapter/profile split: same U adapter matrix; PG all-adapters test | PASS |
| N26 | OP adapter/profile split: same U adapter matrix; PG all-adapters test | PASS |
| N27 | MR adapter: same U adapter matrix; PG all-adapters test | PASS |
| N28 | PO associative material path: same U adapter matrix; PG all-adapters test | PASS |
| N29 | QI adapter: same U adapter matrix; PG all-adapters test | PASS |
| N30 | RW adapter: same U adapter matrix; PG all-adapters test | PASS |
| N31 | Delivery adapter: same U adapter matrix; PG all-adapters test | PASS |
| N32 | WorkCenter adapter: same U adapter matrix; PG all-adapters test | PASS |
| N33 | Fixed/bounded traversal: U:test_n23_n33_all_nine_adapters_have_fixed_owned_bounded_sql; U:test_n52_navigation_capability_audit_negative_controls | PASS |
| N34 | Real 4097-row unit overflow and scaled observation cap: U:test_n34_real_record_cap_and_scaled_observation_cap; PG:test_n34_native_bounded_query_and_scaled_cap_failure | PASS |
| N35 | WO/OP future masks + projector second gate: U:test_n35_n37_sql_mask_and_frozen_second_gate; PG:test_n35_n37_actual_future_values_are_sql_masked_and_not_emitted | PASS |
| N36 | PO future receipt/quantity masks: same U/PG future-mask matrices | PASS |
| N37 | RW future end mask: same U/PG future-mask matrices | PASS |
| N38 | Future event/master exclusion: U:test_n38_future_event_or_master_rows_produce_no_observations; PG:test_n38_event_rows_after_decision_time_are_excluded_in_sql | PASS |
| N39 | Known future plan values: U:test_n39_future_plans_remain_known_values; PG:test_n39_n47_n49_known_future_plan_and_empty_actual_profiles | PASS |
| N40 | Availability/event guard and equality boundary: U:test_n40_projection_cannot_bypass_temporal_or_source_binding; PG:test_n40_exact_event_time_boundary_is_admitted | PASS |
| N41 | Exact PK: U:test_n40_n44_exact_source_field_provenance_and_w03_classification; U:test_n23_n41_bad_source_records_fail_closed; PG independent oracle | PASS |
| N42 | Exact requested field/projected value: U:test_n40_n44_exact_source_field_provenance_and_w03_classification; PG independent oracle | PASS |
| N43 | Exact provenance hash: U:test_n40_n44_exact_source_field_provenance_and_w03_classification; PG:test_n19_n24_n32_n43_n51_all_adapters_native_replay_and_zero_mutation | PASS |
| N44 | Frozen W03 trust/relationship/freshness: U:test_n40_n44_exact_source_field_provenance_and_w03_classification; U:test_n44_n45_classification_cannot_upgrade_or_change_authority; PG independent oracle | PASS |
| N45 | No FORBIDDEN observation: U:test_n44_n45_classification_cannot_upgrade_or_change_authority | PASS |
| N46 | Sorted unique observations/deduped joins: U:test_n46_duplicate_joins_and_row_order_do_not_change_evidence; PG full canonical oracle | PASS |
| N47 | Bound empty evidence: U:test_n47_n49_empty_is_exactly_bound_and_never_synthetic; PG:test_n39_n47_n49_known_future_plan_and_empty_actual_profiles | PASS |
| N48 | No synthetic UNKNOWN/support/finding: U:test_n47_n49_empty_is_exactly_bound_and_never_synthetic; U runtime capability audit | PASS |
| N49 | Exact slice refs/as-of: U:test_n47_n49_empty_is_exactly_bound_and_never_synthetic; U:test_n50_all_original_and_rehashed_navigation_tamper_rejected; PG empty/known-plan test | PASS |
| N50 | Original/rehash tamper rejection: Q:test_n17_original_and_nested_identities_and_bindings; U:test_n50_all_original_and_rehashed_navigation_tamper_rejected; PG:test_n50_rehashed_native_evidence_is_rejected_without_mutation; valid C01 wire test separate | PASS |
| N51 | Replay/input/count/business-payload preservation/read-only SQL: U:test_n51_repeatable_read_replay_preserves_inputs_and_source_payload; PG:test_n19_n24_n32_n43_n51_all_adapters_native_replay_and_zero_mutation | PASS |
| N52 | AST/fresh imports/live capability blockers with negative controls; Q:test_n52_lifecycle_harness_accepts_authorized_and_future_closed; Q:test_n52_committed_source_governance_and_frozen_blobs; production source verifier | PASS |

DR-C04-01 additionally passes
U:test_dr_c04_01_exact_traversal_codes_and_adapter_registry_order.

For N23, the native second-dataset fixture proves fail-closed source-context
behavior before adapter queries execute. It does not independently prove that
its foreign WO was filtered during a post-join execution. The separate compiled
SQL proof establishes dataset predicates on every joined owner, while normal
native all-adapter reads prove the registered graph. No stronger claim is made.

## 8. Empirical test counts and local continuation proof

Function/decorator counts were measured from ASTs; expanded counts were measured
with pytest collection, not invented from N labels. Integration collection was
measured even where local execution legitimately skipped.

| C04 module | Test functions | Parameterized functions | Expanded cases | Native result |
|---|---:|---:|---:|---|
| Query/governance Q | 23 | 13 | 92 | PASS |
| Navigation U including DR-C04-01 | 22 | 13 | 124 | PASS |
| PostgreSQL PG | 9 | 5 | 22 | PASS |
| Total | 54 | 31 | 238 | PASS |

Local resume precommit invocation combined U, Q excluding committed-source
governance and C03 planning excluding P40: 401 passed / 2 deselected / 341.83 s.
That is U124 + Q91 + planning186. Final DR-C04-01 alone passed after its explicit
import fix. Ruff passed; requested three-file strict mypy passed; offline lock
check resolved 43 packages using the existing Python 3.12.14/uv 0.12.5 environment.
No dependency was installed or changed.

After committing C, N52 + P40 + complete source-evolution suite passed:
129 passed / 217.29 s. Worktree/index were clean and the B→C delta was exactly
three paths before push. The production verifier with expected head
`6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1` returned PASS, included all three
authorized C04 sources, preserved C01-C03 CLOSED sources and had no unexpected
source. Manifest SHA-256 is
`7e6d1b5c8cc86725c399dae7b421076a5cf53af830145dd0b7978058a5ab18eb`.

Before interruption, unit/registry focused proof passed 214 cases with one
committed-head governance case deferred. Offline real business fixtures and a
separate expected-result implementation matched complete canonical slices across
11 all-family/future-gate scenarios. These are local proofs, distinct from native
PostgreSQL acceptance. Resume added only the traversal audit.

## 9. Stage C native proof and regressions

Native Linux Python 3.12.14 collected 2116 cases. The integration and
non-integration selections are disjoint; deselected counts reflect that split.
There were no failures, execution skips, xfails or xpasses in either selection.

| Proof | Actual result |
|---|---|
| Integration | 70 passed / 2046 deselected / 1 warning / 337.93 s |
| New C04 PostgreSQL cases | 22 passed within the 70; all nine families/eleven profiles exercised |
| Non-integration | 2046 passed / 70 deselected / 1 warning / 2406.19 s |
| Ruff | All checks passed |
| Strict mypy | Success / 155 source files |
| Dependency lock | PASS / 43 packages |
| Docker Compose | PASS / build, stack, PostgreSQL, API health and Worker proof |
| W03 frozen gate | F01-F10 PASS / 38 selectors / 85 cases |
| Verification | PASS / class-specific exact-SHA proof |
| Publication | SKIPPED as required for I / FULL_EXACT_SHA |

The native PG oracle reads business-only fixture rows, uses the fixed in-memory
order-rooted graph and frozen W03 projector/classifier, and computes its own
provenance/slices. Runtime SELECT SQL is captured separately from isolated test
setup/cleanup DML. Four fresh RR/RO transactions in the replay test preserve
canonical slices, input bytes, row counts, content hash and canonical business
payload. Future masks/exclusion, inclusive boundaries, empty actual evidence,
context mismatch, scaled caps and rehashed forgeries all passed. No runtime
INSERT/UPDATE/DELETE/MERGE/DDL or raw status access occurred.

| Existing regression suite | Test functions | Parameterized functions | Expanded cases | Stage C result |
|---|---:|---:|---:|---|
| C01 H01-H40 contracts | 40 | 26 | 426 | PASS |
| C02 B01-B36 case binding | 31 | 13 | 76 | PASS |
| C03 P01-P40 planning | 41 | 25 | 187 | PASS |
| DEVCTRL source evolution | 52 | 27 | 127 | PASS |
| DEVCTRL change classifier | 11 | 6 | 90 | PASS |
| DEVCTRL publication gate | 11 | 6 | 35 | PASS |
| W03 core contracts + serialization | 16 | 2 | 39 | PASS |

These suites passed in the complete native selection with no exclusions.
Prior C01/C02/C03 frozen source bytes and accepted W1/W2/W03 semantics remain
unchanged; only the authorized historical Stage A P40 aggregate repair differs
from original entry test bytes.

| Frozen W03 family | Selectors | Expanded cases | Result |
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
| Total | 38 | 85 | PASS |

Native summary gate version is `w03-c09-ai-loop-gate-v1`, implementation SHA
is the exact Stage C SHA, and frozen manifest SHA-256 is
`bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990`.

Stage C native job receipts:

| Job | ID | Result |
|---|---:|---|
| [Classify change](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37497691587/job/112386357804) | 112386357804 | SUCCESS |
| [Quality gate](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37497691587/job/112386411047) | 112386411047 | SUCCESS |
| [Docker Compose smoke](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37497691587/job/112386411062) | 112386411062 | SUCCESS |
| Publication proof | 112386413354 | SKIPPED |
| [W03 AI loop gate](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37497691587/job/112407259192) | 112407259192 | SUCCESS |
| [Verification gate](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37497691587/job/112410075349) | 112410075349 | SUCCESS |

## 10. Warnings, limits and deviations

- Local Windows lacks an authorized PostgreSQL test URL and a usable Docker
  daemon. Its 22 legitimate PG skips are not acceptance. Native Linux PG70 and
  Compose SUCCESS provide the required proof.
- The sole native warning in each Quality test selection is the existing
  Starlette/httpx deprecation. Dependencies remain frozen; no upgrade was made.
- Existing Windows CRLF raw-byte limitations in the frozen C06/C09 selectors
  remain unchanged. Native Linux exact-SHA proof is authoritative. Git staging
  emitted ordinary LF→CRLF worktree warnings; staged Python bytes matched the
  reviewed snapshot, and frozen source OIDs remain exact.
- During original Stage A local control proof, B36 was inadvertently included
  before the manifest was committed and rejected the dirty worktree as designed:
  978 passed / 1 failed / 1 deselected. Postcommit affected checks passed, and
  native Stage A passed completely. No verifier/test weakening repaired it.
- Before interruption, a fake-row serializer test helper required tuple conversion;
  integration tests were made self-contained after standalone import collection
  failed. Those reviewed C draft fixes are preserved. Resume's initial mypy audit
  reference used a non-exported module alias; the single new test now imports the
  registry explicitly. No runtime or Stage B repair occurred during resume.
- N34's unit test exercises actual 4097 distinct records. Native record cap is
  scaled to 1 and observation cap to 5 to prove failure on the isolated fixture.
  The v1 largest 11-field profile × 4096 rows = 45056 observations is below the
  fixed 65536 ceiling, so the observation guard is explicitly tested by scaling;
  no claim of natural native 65537-observation execution is made.
- N23's native context rejection and compiled per-owner dataset proof are
  distinct, as required by quota review R1. C01 scalar wire normalization is
  inherited unchanged, with canonical equality rather than new typed wire rules.
- Repeated reads are deterministic for unchanged authorized source content;
  a later source change can legitimately cause replay validation to reject an
  older slice. This is a bounded offline/shadow reader, not an operational writer.

Scope deviations: NONE. Frozen architecture/schema/hash/scenario semantics:
UNCHANGED. Production verifier/classifier/workflow change: NONE. Runtime HGT,
model/tool/filesystem/subprocess authority, C05 artifacts, operational mutation,
PR merge and branch deletion: NONE. Full implementation/harness evidence is
provided for independent review; it does not authorize closeout or acceptance.

```text
GPT INDEPENDENT IMPLEMENTATION REVIEW:
PENDING

HUMAN C04 ACCEPTANCE:
PENDING

C04 CLOSEOUT:
NOT AUTHORIZED

C04 MANIFEST STATE:
AUTHORIZED

W04-C05:
NOT AUTHORIZED
```
