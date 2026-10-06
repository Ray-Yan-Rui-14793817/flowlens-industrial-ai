# W04-C02 Development Round Report — V2

W04-C02 IMPLEMENTATION COMPLETE — REVIEW_READY.
The frozen W03 C05 DecisionPacket now binds deterministically to the frozen C01
InvestigationCase. Exact packet/case validation rejects structural, identity,
provenance, future-information and binding tampering. Native exact-SHA full proof
passed before this report was created. C02 remains AUTHORIZED for independent
review and Human acceptance.

## 1. Authority, entry and clarification

```text
TASK: W04-C02 / V2
CLARIFICATION: W04-C02-CLARIFICATION-01 / APPLIED
HUMAN AUTHORIZATION: APPROVED
REPAIR AUTHORIZATION: APPROVED
ENTRY SHA: ae88a9b1be74bc379140b59a15d6dd9cb714912f
ENTRY CI: #93 / 37321990473 / SUCCESS
ENTRY WORKTREE: CLEAN
BRANCH: feat/w04-evidence-investigation
PR #7: OPEN / DRAFT / UNMERGED
IMPLEMENTATION: COMPLETE
STATUS: REVIEW_READY
```

The Human's pasted V2 request authorized implementation and the narrow D01
repair. The attached V2 task defines the scope; unchanged V1 requirements remain
normative. The repository entry, branch, clean worktree, 30-commit history, PR
metadata and CI #93 were checked before mutation. The preceding V1 clarification
probes were read-only and produced no commit or push.

Normative task V2 SHA-256:
`b5e23dffbbf044f87919efbb72fa95f6d5cab9279740096b83a3ce85d564e148`.
Unchanged task V1 SHA-256:
`51ecd2bf9db109b2451d812946450e6751d2e030478b71375278d22c8a5289fe`.

W04-C02-CLARIFICATION-01 was applied as follows:

| Clarification | Applied behavior and evidence |
|---|---|
| CL-01 | Only D01's final whole-manifest comparison was replaced by exact checkpoint-0 equality with the frozen C01 bootstrap. Existing constants, parser, transition, history, unexpected-source and CLOSED-immutability controls remain intact. The verifier is unchanged. |
| CL-02 | NO_ACTION, NO_RECOMMENDATION, INVESTIGATION_ONLY and DEFER_TO_HUMAN are accepted. CANDIDATE_RECOMMENDED is reserved and rejected by the unchanged frozen W03 C05 validator as C02_INVALID_DECISION_PACKET. |
| CL-03 | Exact packet type precedes frozen W03 validation; frozen validation failure maps to C02_INVALID_DECISION_PACKET. Only surviving future observational/source timestamps reach the C02 guard and map to C02_FUTURE_INFORMATION. |

## 2. Commits, exact-SHA proof and ordering

| Stage | Exact SHA | Actual class / proof | Native CI |
|---|---|---|---|
| Entry | `ae88a9b1be74bc379140b59a15d6dd9cb714912f` | Previously closed DEVCTRL publication | [#93 / 37321990473 — SUCCESS](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37321990473) |
| A: authorization + D01 repair | `89a872c9837136a18b7465da7f1c680c454866d6` | I / FULL_EXACT_SHA | [#94 / 37349061475 — SUCCESS](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37349061475) |
| B: runtime + harness | `18648915414a26dddbdc904965663730ea631cf2` | I / FULL_EXACT_SHA | [#95 / 37353463408 — SUCCESS](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37353463408) |

Stage A is the direct child of entry; Stage B is the direct child of Stage A.
Both were committed separately and pushed normally on the authorized branch.
No amendment after CI evidence, force push, main write or history rewrite occurred.

Stage A changed exactly four paths: the manifest, C02 Human Authorization,
C02 Context Lock and `tests/test_w04_source_evolution.py`. The new runtime file
was absent from the filesystem, index and Stage A commit. Strict parsing and
pending transition checks preceded that commit. After committing, the unchanged
generic verifier and affected C09 source-governance selector passed against the
committed HEAD. Native Verification #94 passed before any Stage B source creation.

V2's advisory expectation for Stage A was C. The unchanged classifier actually
selected I because the generic D01 test path classifies I; its three control
documents classify C. The recorded classification uses the exact four-path
entry-to-A delta and reason `verified_source_head_delta`. This routing difference
was documented in the context lock; the full required proof passed.

Stage B changed exactly two new paths: the binder and its harness. Its classifier
records base `89a872c9837136a18b7465da7f1c680c454866d6`, head
`18648915414a26dddbdc904965663730ea631cf2`, those exact two paths, I /
FULL_EXACT_SHA and reason `verified_source_head_delta`.
The manifest and repaired D01 test did not change during Stage B.

| Job | Stage A job ID / result | Stage B job ID / result |
|---|---|---|
| Classify change | 111894984500 / SUCCESS | 111909823423 / SUCCESS |
| Docker Compose smoke | 111895047439 / SUCCESS | 111909919039 / SUCCESS |
| Quality gate | 111895047553 / SUCCESS | 111909919267 / SUCCESS |
| Publication proof | 111895049421 / SKIPPED | 111909922230 / SKIPPED |
| W03 AI loop gate | 111900861153 / SUCCESS | 111923047488 / SUCCESS |
| Verification gate | 111902378776 / SUCCESS | 111925376075 / SUCCESS |

Stage B Verification and the complete run were confirmed successful before this
report was created. Stage C publishes only this report, with P /
PUBLICATION_EXACT_SHA expected from the unchanged routing. The report's own
future commit SHA and publication result cannot be embedded in its immutable
prepublication contents. The final Codex handoff will attest the actual Stage C
SHA, classification, run/job IDs and result after normal push and exact-SHA proof.
This report does not claim a publication result that had not yet occurred.

## 3. Runtime contract and exact projection

The only runtime addition is:
`src/flowlens/investigation/c02_binding.py`.
Its Stage B Git blob is `5f0af237ed465fa83e5a3b84954512b1f3125551`.
No C01 package re-export or source modification was needed.

Public API:

```python
class C02BindingError(ValueError): ...
def build_investigation_case(packet: DecisionPacket) -> InvestigationCase: ...
def validate_investigation_case_binding(
    packet: DecisionPacket, case: InvestigationCase,
) -> None: ...
```

Constants are exactly `C02_BINDING_POLICY_VERSION = "w04-c02-v1"`,
`C02_SUBJECT_TYPE = "ORDER"` and
`C02_OPENED_BY = "FLOWLENS_W04_C02_BINDER"`.
Public failure codes are `C02_INVALID_DECISION_PACKET`,
`C02_FUTURE_INFORMATION` and `C02_CASE_BINDING_MISMATCH`.
The exception's `code` and text expose the stable C02 code; frozen W03 exception
text is suppressed.

Both APIs first require exact DecisionPacket type and reuse
`flowlens.decision.c06_validation.validate_c05_packet` unchanged. The builder
then applies the temporal guard, hashes the complete
`flowlens.decision.serialization.canonical_json_bytes(packet)` with SHA-256 and
constructs the frozen C01 case. The lowercase digest includes all canonical
packet fields, IDs and provenance. A real provenance-only change that preserves
W03 packet_id still changes this digest and invalidates the old case binding.

| Case field | Exact source/value |
|---|---|
| schema_version | investigation-case.v1 |
| source_decision_packet_id | packet.packet_id |
| source_decision_packet_hash | sha256(canonical_json_bytes(packet)).hexdigest() |
| decision_run_id | packet.run.run_id |
| subject_type | ORDER |
| subject_id | packet.run.order_id |
| as_of_time | packet.run.as_of_time |
| opened_at | packet.run.as_of_time |
| opened_by | FLOWLENS_W04_C02_BINDER |
| risk_families | Sorted unique signal_type.value for non-INACTIVE signals |
| source_signal_ids | Sorted unique signal_id for the same non-INACTIVE signals |
| source_diagnosis_id | packet.diagnosis.diagnosis_id |
| source_recommendation_id | packet.recommendation.recommendation_id |

ACTIVE and UNKNOWN are retained; INACTIVE is excluded. UNKNOWN is preserved
without becoming causal support. All-INACTIVE and empty signal bundles produce
valid empty tuples. Logical opening time is inherited; no current clock is read.
C01 supplies the unchanged content_hash, artifact_id and canonical wire envelope.

The binding validator applies the same packet path, requires exact case type,
constructs a detached C01 copy with `dataclasses.replace`, validates original
structure including derived identity types, and compares the complete original,
reconstructed and expected canonical case envelopes. It returns None on exact
match. Wrong packet/run/subject/references, stale content_hash/artifact_id,
identical-value StrEnum claims and malformed tuples are rejected without
overwriting the caller's identity claims. C01 rejects malformed init fields
before canonical traversal, including a tuple subclass with a hostile iterator.

## 4. Temporal, determinism and capability proof

All eight observation/availability surfaces are checked against the packet's
decision cutoff using actual UTC instants: snapshot entry observed_at and
available_at; its SourceRef observed_at and available_at; Evidence observed_at
and available_at; packet provenance SourceRef observed_at and available_at.
None observations and exact-cutoff timestamps are valid.

Future snapshot entry/source-ref availability and Evidence availability fail
frozen W03 structural validation first and produce INVALID. The harness proves
that future snapshot/source observations, Evidence observations and canonical
packet-source provenance observations/availability survive W03 validation before
C02 rejects them as FUTURE. Modeled counterfactual future measurements remain
eligible. Equivalent offsets produce identical bytes; a DST-fold fixture proves
ordering by UTC instant rather than ambiguous local wall time.

Same-process repetition preserves case JSON, content_hash, artifact_id and packet
hash and leaves packet/case inputs unchanged. Real fresh Python processes with
PYTHONHASHSEED values 0, 1, 73 and 123456 produce identical outputs.

Runtime imports and execution are pure. AST/import checks, a fresh-process module
inventory and active denial traps with negative controls cover clock,
randomness/UUID, filesystem, socket/network, subprocess, SQLite/database and
external execution capabilities. No model/tool, HGT/evaluation, operational
write, question registry, investigation planning or evidence traversal was added.
InvestigationQuestion, InvestigationStep, InvestigationPlan and EvidenceQuerySpec
constructors are actively denied during both APIs. Development-only Git and
subprocesses in the harness are distinct from runtime capabilities.

## 5. B01–B36 matrix and measured counts

The committed harness has **31 test functions, 13 parameterized functions and
76 expanded pytest cases**. These are measured collection/AST counts, not
preassigned totals. All 76 pass in the Stage B native complete non-integration
suite. Precommit focused execution passed 75 cases with only HEAD-dependent B36
excluded; after commit, B36 and the affected C09 selector passed together, and
both also passed in exact-SHA CI.

All function names below refer to `tests/test_investigation_case_binding.py`.

| Contract | Function | Cases | Result |
|---|---|---:|---|
| B01 | test_b01_exact_packet_type_rejects_untrusted_values_and_subclasses | 1 | PASS |
| B02 | test_b02_frozen_validator_is_reused_once_and_internal_failures_are_hidden | 1 | PASS |
| B03, B05–B10, B17–B18 | test_b03_b10_b17_b18_exact_projection_and_public_constants | 1 | PASS |
| B04 | test_b04_hashes_complete_packet_including_provenance_excluded_from_packet_id | 1 | PASS |
| B11–B13 | test_b11_b13_signal_state_projection_does_not_upgrade_unknown | 3 | PASS |
| B14–B15 | test_b14_b15_signal_families_and_ids_are_sorted_unique_and_share_selection | 1 | PASS |
| B16 | test_b16_empty_retained_signals_are_valid | 2 | PASS |
| B19 canonical four | test_b19_all_four_real_c05_dispositions_remain_eligible | 4 | PASS |
| B19 reserved rejection | test_b19_reserved_disposition_is_structural_but_not_canonical_c05 | 1 | PASS |
| B20 observations | test_b20_future_snapshot_observations_survive_w03_and_fail_c02 | 2 | PASS |
| B21 availability | test_b21_future_snapshot_availability_is_owned_by_frozen_w03 | 2 | PASS |
| B22 | test_b22_future_evidence_observation_survives_w03_and_fails_c02 | 1 | PASS |
| B23 | test_b23_future_evidence_availability_is_owned_by_frozen_w03 | 1 | PASS |
| B24 provenance | test_b24_future_canonical_packet_source_refs_fail_c02 | 2 | PASS |
| B20–B24 valid cutoff/None | test_b20_b24_none_observations_and_exact_boundary_are_valid | 1 | PASS |
| B24 modeled future | test_b24_future_counterfactual_measurement_is_not_observational_source_truth | 1 | PASS |
| B25 equivalent instants | test_b25_timezone_equivalent_instants_have_identical_canonical_outputs | 2 | PASS |
| B25 DST fold | test_b25_dst_fold_future_observation_compares_actual_utc_instants | 1 | PASS |
| B26 | test_b26_same_process_is_deterministic_and_validation_preserves_input | 1 | PASS |
| B27–B28 | test_b27_b28_real_fresh_process_and_hash_seeds_are_identical | 4 | PASS |
| B29 | test_b29_packet_structural_tampering_is_rejected | 6 | PASS |
| B30 | test_b30_packet_provenance_boundary_tampering_is_rejected | 9 | PASS |
| B31–B32 | test_b31_b32_complete_case_semantic_mismatches_rejected | 12 | PASS |
| B31, B33 derived identities/types | test_b31_b33_original_derived_identity_claims_and_exact_types_revalidated | 4 | PASS |
| B31 structure/type | test_b31_case_structure_and_exact_type_rejected_without_mutating_claims | 6 | PASS |
| B31 hostile iterator | test_b31_hostile_tuple_iterator_is_rejected_before_caller_hooks | 1 | PASS |
| B33 | test_b33_c01_case_wire_identity_and_immutability_remain_exact | 1 | PASS |
| B09, B34 execution traps | test_b34_live_capability_denials_and_negative_controls | 1 | PASS |
| B34 import/AST | test_b34_runtime_imports_and_ast_have_no_external_or_execution_capabilities | 1 | PASS |
| B35 | test_b35_planning_artifact_constructors_are_denied | 1 | PASS |
| B36 | test_b36_c01_frozen_blobs_and_committed_source_governance_pass | 1 | PASS |
| Total | 31 functions / 13 parameterized | 76 | PASS |

B36 preserves the exact frozen C01 blobs and C02 registered source path while
delegating append-only history and lifecycle decisions to the unchanged generic
verifier. It does not permanently assert C02 AUTHORIZED or prohibit later
authorized checkpoints. The present C02 AUTHORIZED state is separately proven
by the actual committed manifest and stage audits.

| Measured scope | Functions | Parameterized functions | Expanded cases | Stage B result |
|---|---:|---:|---:|---|
| C02 binding | 31 | 13 | 76 | PASS |
| C01 H01–H40 | 40 | 26 | 426 | PASS |
| DEVCTRL source evolution | 52 | 27 | 127 | PASS |
| Change classifier | 11 | 6 | 90 | PASS |
| Publication proof suite | 11 | 6 | 35 | PASS |
| W03 core contracts + serialization | 16 | 2 | 39 | PASS |
| Whole repository | 567 | 171 | 1691 | 1643 non-integration + 48 integration PASS in native CI |

Frozen W03 F01–F10 remains 38 selectors, 10 parameterized selectors and
85 expanded cases. The counts above are not added together as independent whole
suite runs; regression scopes and the W03 gate intentionally overlap.

## 6. Regressions, quality and native evidence

Stage A focused source-evolution, classifier, publication, C01 and W03 core
execution passed 717 cases. Its committed source verifier passed, followed by
the affected C09 selector. Local Ruff, strict mypy (145 files) and offline lock
check passed. Native #94 passed 1567 non-integration and 48 integration cases,
Ruff, mypy, lock, Compose, frozen W03 38/85 and Verification.

Stage B local focused C02 execution passed 75/75 selected cases; committed B36
plus C09 passed 2/2. C01 and W03 core passed 465 cases together. The unchanged
source verifier passed at the committed implementation HEAD. Global Ruff,
strict mypy (147 files) and offline lock check (43 packages) passed.

| Stage B proof | Command/job and actual result |
|---|---|
| Local non-integration | `.venv/Scripts/python.exe -B -m pytest -m 'not integration' -q`: 1641 passed, 2 accepted CRLF digest failures, 48 deselected, 1 warning; 944.27 seconds |
| Local integration | `.venv/Scripts/python.exe -B -m pytest -m integration -q`: 48 skipped, 1643 deselected, 1 warning; no configured FLOWLENS_DATABASE_URL |
| Native non-integration | Quality job 111909919267: 1643 passed, 48 deselected, 1 warning; 1542.04 seconds |
| Native integration | Same exact-SHA Quality job: 48 passed, 1643 deselected, 1 warning; 231.81 seconds |
| Ruff | Local and exact-SHA native PASS: All checks passed |
| Strict mypy | Local and exact-SHA native PASS: no issues in 147 source files |
| Dependency lock | Local offline and exact-SHA native PASS: 43 packages; pyproject.toml and uv.lock unchanged |
| Docker Compose | Local configuration exit 0; native Compose smoke SUCCESS with build, PostgreSQL readiness, API health, worker liveness and teardown |
| W03 F01–F10 | Exact-SHA job 111923047488: all families PASS, 38 selectors / 85 cases |
| Verification | Job 111925376075 SUCCESS after Classify, Quality, Compose and W03 SUCCESS |

The native Quality/W03 jobs each verify EXPECTED_HEAD as
`18648915414a26dddbdc904965663730ea631cf2`. Frozen W03 summary records this same
implementation SHA, overall PASS and manifest SHA-256
`bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990`.

| W03 family | Selectors | Cases | Result |
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

## 7. Source governance, scope and limitations

The generic source verifier passes at Stage B with W04-C01 CLOSED, W04-C02
AUTHORIZED and exactly four investigation-source additions relative to W03:
the three frozen C01 files and the single authorized C02 binder. Its committed
manifest SHA-256 is
`3ee551a97cc4eb88bf4fa719180cd44b048ff316a85715be4c860de621029175`.
C02 source_freeze_sha and blob_oid remain null; no closeout transition occurred.

| Frozen C01 path | Unchanged Git blob OID |
|---|---|
| src/flowlens/investigation/__init__.py | c23929f85dccd78bc72ef3b2b1415c6e8eaf0452 |
| src/flowlens/investigation/contracts.py | 0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e |
| src/flowlens/investigation/enums.py | 9c818780423f32f144b18666784ebc9ea3abdccc |

The complete V2 delta including this report is exactly seven authorized paths:

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c02/W04_C02_HUMAN_AUTHORIZATION.md
docs/w04/checkpoints/c02/W04_C02_CONTEXT_LOCK.md
tests/test_w04_source_evolution.py
src/flowlens/investigation/c02_binding.py
tests/test_investigation_case_binding.py
docs/w04/checkpoints/c02/W04_C02_R_DEVELOPMENT_ROUND_REPORT.md
```

W03 source/contracts/policy, C01 source, the generic verifier, classifier,
workflow, other existing tests, dependencies, Compose, migrations and apps are
unchanged. No operational mutation occurred. No additional runtime file, C03
code, review/acceptance record, closeout, PR merge or branch deletion was made.

Known limitations and warnings:

1. The local Windows complete suite fails only the two previously accepted
   raw-byte CRLF selectors:
   `tests/test_c06_harness.py::test_frozen_c01_and_c05_sources_match_context_lock`
   and
   `tests/test_c09_ci_gate.py::test_frozen_manifest_schema_families_counts_and_content`.
   Their files and frozen Git identities are unchanged. Both pass in native
   exact-SHA Linux CI #95. This remains LOCAL_ENVIRONMENT_ONLY / CRLF under the
   accepted C01 clarification and DEVCTRL AL-D04; no newline/source/test repair
   was made. No other local full-suite failure occurred.
2. Local integration skipped all 48 cases because FLOWLENS_DATABASE_URL was not
   configured. The local Docker daemon was unavailable; Compose configuration
   validated with Docker config read warnings. Native exact-SHA CI supplies
   actual integration and running Compose proof, not a local service claim.
3. Local and native test commands retain the existing StarletteDeprecationWarning
   about httpx with TestClient. Normal Git LF-to-CRLF warnings also occurred.
   No dependency change was authorized or made.
4. Ordinary precommit harness defects were repaired within the new test file,
   including typing/fixture issues and a stale B36 lifecycle assumption. The
   final measured harness, global quality checks and exact-SHA CI pass.
   Stage A's actual I routing is the sole advisory class difference; no scope
   expansion or semantic exception was used.

## 8. Review boundary

Codex code/harness audits and CI are development evidence. They do not constitute
the pending independent GPT checkpoint review or Human C02 acceptance.
PR #7 remains draft/open/unmerged, and the feature branch is retained.

```text
GPT INDEPENDENT REVIEW: PENDING
HUMAN C02 ACCEPTANCE: PENDING
C02 CLOSEOUT: NOT AUTHORIZED
C02 MANIFEST STATE: AUTHORIZED
W04-C03: NOT AUTHORIZED
```
