# W04-C01 Development Round Report — Implementation + Clarification-01 + Repair-01

Date: 2026-10-05 (Asia/Shanghai).

```text
TASK: W04-C01 — Immutable Investigation Contracts
TASK VERSION: V2
AUTHORIZATION STATUS: AUTHORIZED
AUTHORIZATION RECORD PATH: docs/w04/checkpoints/c01/W04_C01_HUMAN_AUTHORIZATION.md
BASE SHA: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
ENTRY SHA: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
ENTRY BRANCH / WORKTREE: main / CLEAN
BRANCH: feat/w04-evidence-investigation
ORIGINAL IMPLEMENTATION SHA: 084c2fea93d0e021994de015c986de9ff92bf9a3
ORIGINAL EXACT-SHA CI: #87 / 37274660663 / FAILURE
GPT CLARIFICATION: W04-C01-CLARIFICATION-01 / ISSUED
HUMAN REPAIR-01 AUTHORIZATION: AUTHORIZED — direct Human reply 确认授权
REPAIR SHA: b7cebe71346050ee2f817905d600c23a26542b7e
REPAIR EXACT-SHA CI: #88 / 37278703544 / PASS
CHANGE CLASS: UNKNOWN
PROOF CLASS: FULL_EXACT_SHA
CONTRACT LAYER: IMPLEMENTED / COMMITTED / NORMAL PUSH COMPLETE
REPAIR CHANGE: HARNESS ONLY / COMMITTED / NORMAL PUSH COMPLETE
REQUIRED FULL PROOF: PASS
STATUS: W04-C01 REPAIR-01 COMPLETE / REVIEW_READY
REVIEW_READY: YES
```

The original C01 runtime implementation remains unchanged. Clarification-01 and
explicit Human Repair-01 authorization resolved the previously reported C09
boundary conflict. The bounded repair is committed and pushed on the same W04
branch; complete repair-SHA proof passed. No checkpoint acceptance,
closeout, merge or W04-C02 advancement is claimed.

## Original blocker and preserved stop history

The original exact implementation-SHA repository-wide regression failed the existing C09
`tests/test_c09_ci_gate.py::test_classifier_publication_and_runtime_frozen_materials_unchanged`
assertion at line 522:

```python
assert not git("diff", "--name-only", gate.ENTRY, "HEAD", "--", "src", "migrations", "apps")
```

`gate.ENTRY` is `d71d5baeb0862f2706358c26e182554b3807e8f6`. The actual
output contains only the three newly authorized W04 source files:

```text
src/flowlens/investigation/__init__.py
src/flowlens/investigation/contracts.py
src/flowlens/investigation/enums.py
```

The earlier control-file comparisons in that test passed. Its repository-wide
source freeze rejected this authorized C01 addition, independently of the
Windows line-ending failures below. The selector was reproduced after the
implementation commit. A change to the existing C09 harness was outside V2's
allowlist, so Codex correctly stopped with
`W04_C01_REQUIRES_GPT_CLARIFICATION`. At that stop, no skip, test edit, classifier
change, frozen hash change or CI policy change was made.

GPT subsequently issued `W04-C01-CLARIFICATION-01`, authorizing only the stale
whole-source boundary assertion repair. The first repair handoff stopped with
`W04_C01_REPAIR_01_HUMAN_AUTHORIZATION_REQUIRED` because the package authorization
record was a template. The direct Human reply `确认授权` explicitly authorized
the pending `W04-C01-REPAIR-01`; that decision was materialized and read back in
`W04_C01_REPAIR_01_HUMAN_AUTHORIZATION.md` before repair mutation.

```text
ORIGINAL STOP MUTATION STATUS: seven authorized implementation/contract files committed and pushed;
                               prior development report remained uncommitted
RUNTIME / SOURCE MUTATION IN REPAIR: NONE
ORIGINAL IMPLEMENTATION COMMIT AMENDED: NO
NO FURTHER SCOPE EXPANSION: YES
```

## Files changed

Implementation commit (seven additions, no edits to existing files):

- `docs/w04/checkpoints/c01/W04_C01_HUMAN_AUTHORIZATION.md`
- `docs/w04/checkpoints/c01/W04_C01_CONTEXT_LOCK.md`
- `docs/w04/checkpoints/c01/W04_C01_CODEX_DEVELOPMENT_TASK_V2.md`
- `src/flowlens/investigation/__init__.py`
- `src/flowlens/investigation/contracts.py`
- `src/flowlens/investigation/enums.py`
- `tests/test_investigation_contracts.py`

The original staged diff allowlist and `git diff --cached --check` passed before
commit. The original implementation SHA was preserved without amendment.

Repair commit `b7cebe71346050ee2f817905d600c23a26542b7e` is a new child of the
original implementation and contains exactly five bounded files:

- `tests/test_c09_ci_gate.py`
- `docs/w04/checkpoints/c01/W04_C01_GPT_CLARIFICATION_01.md`
- `docs/w04/checkpoints/c01/W04_C01_CODEX_COMPATIBILITY_REPAIR_TASK_V1.md`
- `docs/w04/checkpoints/c01/W04_C01_REPAIR_01_HUMAN_AUTHORIZATION.md`
- `docs/w04/checkpoints/c01/W04_C01_REPAIR_01_CONTEXT_LOCK.md`

No `src/**`, frozen C09 manifest, gate runner, classifier, workflow, dependency,
lockfile, migration or application file changed in the repair. The same W04
branch and draft PR #7 contain the repair commit. This combined evidence report
is published separately as authorized documentation evidence; it is not part
of the repair SHA or its exact-SHA CI run. It does not alter the implementation
or repair commits.

## W03 reuse and context lock

- Model framework: `src/flowlens/decision/primitives.py` — `Validated`, strict
  structural/deep validation, frozen/slots/keyword-only dataclasses, `ScalarValue`,
  `validate_sorted_unique`, `validate_sha256`, `validate_artifact_id`.
- Serializer/hash: `src/flowlens/decision/serialization.py` — exact public
  `canonical_primitive`, `canonical_json_bytes`, `canonical_json_text`, `sha256_hex`.
- Identity: W03's `{artifact_kind, schema_version, identity}` canonical envelope
  and prefix plus full lowercase 64-character digest. W03's `derive_artifact_id`
  kind registry is closed. The new W04-only prefix map follows the existing pure
  extension in `src/flowlens/decision/context.py`; no W03 helper was modified.
- Trust: exact canonical `src/flowlens/decision/enums.py::TrustLevel`, retaining
  `DIRECT_FACT`, `DERIVED_FACT`, `ASSOCIATIVE_EVIDENCE`, `UNKNOWN`,
  `FORBIDDEN_INFERENCE`. No parallel trust taxonomy.
- Timestamp: existing aware-datetime validation and canonical UTC timestamps
  with six fractional digits and terminal `Z`.
- Full locked paths, authorization readback, parent/history checks and chosen
  structural conventions are in `W04_C01_CONTEXT_LOCK.md`.

All three V2 ZIP entry hashes matched their manifest. The repository task copy
matches SHA-256 `de4b95e794201050e07e552140dedc247f45196edc113ee87c5607d062fd15c4`.
The Human authorization was materialized/read back before code mutation.
No post-anchor commits or unexplained entry runtime changes existed.

## Contracts, values and enums

Top-level artifacts: `InvestigationCase`, `InvestigationQuestion`,
`InvestigationStep`, `InvestigationPlan`, `EvidenceQuerySpec`, `EvidenceSlice`,
`FindingRecord`, `ConflictRecord`, `UncertaintyRegister`,
`InvestigationSummaryRecord`, `HumanInvestigationEvent`.

Supporting values: `EntityKey`, `EvidenceObservation`, `UncertaintyItem`,
`SummarySectionRecord`. All 15 declared models share the immutable identity
framework and `<artifact-kind>.v1` schema. Identity fields are constructor-derived;
parsing validates caller-supplied serialized IDs/hashes, including nested objects.
Derived identities are recursively excluded from digest input.

Closed enums: `FindingStatus`, `ConflictType`, `UncertaintyType`,
`HumanInvestigationOutcome`, `SummaryRendererMode`, exactly as frozen by V2.

Set-like tuples use W03 sorted-and-unique validation; ordered plan steps and
summary sections retain order. Code-like keys are ASCII identifiers bounded to
128 characters. Tuple and nested-model subclasses that can add mutable public
state are rejected. Caller data is structurally validated before hashing.

## H01–H40 evidence

Each selector below is in `tests/test_investigation_contracts.py`. Function and
parameterization counts were measured from the final AST; expanded counts were
measured from actual pytest collection and execution, not predeclared.

| Frozen gate | Requirement | Result | Expanded cases | Actual test function |
|---|---|---|---:|---|
| H01 | top-level artifact assignment mutation rejected | PASS | 15 | `test_h01_top_level_assignment_rejected` |
| H02 | nested public collections are immutable | PASS | 15 | `test_h02_nested_public_collections_immutable` |
| H03 | undeclared/extra fields rejected | PASS | 15 | `test_h03_extra_missing_and_duplicate_wire_fields_rejected` |
| H04 | schema/version contract stable | PASS | 15 | `test_h04_schema_version_stable_and_closed` |
| H05 | canonical serialization deterministic in same process | PASS | 15 | `test_h05_same_process_canonical_determinism` |
| H06 | canonical serialization/hash deterministic in fresh process | PASS | 3 | `test_h06_fresh_process_determinism` |
| H07 | serialize → parse → serialize preserves identity | PASS | 15 | `test_h07_serialize_parse_serialize_identity` |
| H08 | supplied mismatching hash/id rejected | PASS | 30 | `test_h08_supplied_mismatching_identity_rejected` |
| H09 | payload mutation changes hash/id | PASS | 15 | `test_h09_semantic_mutation_changes_identity` |
| H10 | no random/clock/uuid identity generation | PASS | 1 | `test_h10_identity_has_no_random_clock_process_or_hash_dependency` |
| H11 | naive datetime rejected | PASS | 9 | `test_h11_naive_business_timestamps_rejected` |
| H12 | timezone-equivalent instants follow W03 canonical convention | PASS | 15 | `test_h12_equivalent_timezones_reuse_w03_convention` |
| H13 | blank/invalid code-like values rejected | PASS | 138 | `test_h13_blank_or_executable_code_values_rejected` |
| H14 | duplicate set-like references rejected | PASS | 27 | `test_h14_duplicate_set_like_references_rejected` |
| H15 | InvestigationCase opened_at < as_of_time rejected | PASS | 1 | `test_h15_case_cannot_open_before_decision_time` |
| H16 | InvestigationPlan step ordinals contiguous when non-empty | PASS | 4 | `test_h16_plan_ordinals_contiguous` |
| H17 | plan dependency on same/future step rejected | PASS | 3 | `test_h17_plan_dependencies_only_reference_earlier_steps` |
| H18 | plan dependency cycles impossible/rejected | PASS | 1 | `test_h18_plan_cycles_and_executable_dependencies_rejected` |
| H19 | EvidenceQuerySpec has no executable-query escape field | PASS | 12 | `test_h19_query_has_no_executable_escape_fields` |
| H20 | EvidenceQuerySpec requires entity keys and requested fields | PASS | 3 | `test_h20_query_required_nonempty_collections` |
| H21 | EvidenceQuerySpec rejects FORBIDDEN trust | PASS | 2 | `test_h21_forbidden_trust_not_allowed` |
| H22 | EvidenceSlice permits explicit empty result | PASS | 1 | `test_h22_empty_evidence_result_remains_explicit` |
| H23 | EvidenceSlice rejects available_at > as_of_time | PASS | 1 | `test_h23_evidence_availability_is_bounded_by_as_of` |
| H24 | EvidenceSlice rejects duplicate observations | PASS | 1 | `test_h24_duplicate_observations_rejected` |
| H25 | EvidenceSlice rejects FORBIDDEN usable observation | PASS | 5 | `test_h25_forbidden_observation_cannot_enter_usable_slice` |
| H26 | Finding supporting/contradicting sets disjoint | PASS | 1 | `test_h26_finding_support_and_contradiction_disjoint` |
| H27 | SUPPORTED finding requires supporting evidence | PASS | 1 | `test_h27_supported_finding_requires_support` |
| H28 | CONTRADICTED finding requires contradicting evidence | PASS | 1 | `test_h28_contradicted_finding_requires_contradiction` |
| H29 | UNKNOWN finding requires explicit uncertainty | PASS | 1 | `test_h29_unknown_requires_uncertainty_and_unresolved_requires_basis` |
| H30 | ConflictRecord requires >=2 unique evidence refs | PASS | 3 | `test_h30_conflict_requires_two_unique_evidence_refs` |
| H31 | UncertaintyRegister preserves items and permits empty register | PASS | 1 | `test_h31_uncertainty_register_preserves_items_and_empty_is_legal` |
| H32 | HumanInvestigationOutcome is closed | PASS | 5 | `test_h32_closed_outcomes_and_all_structural_enums` |
| H33 | Human note is fixed-class NON_EVIDENCE | PASS | 4 | `test_h33_human_note_fixed_non_evidence_class` |
| H34 | no operational-action fields in HumanInvestigationEvent | PASS | 7 | `test_h34_human_events_have_no_operational_action_fields` |
| H35 | summary text is presentation-only and structurally grounded by refs | PASS | 3 | `test_h35_summary_text_retains_grounding_without_truth_authority` |
| H36 | contract module has no DB/network/model/subprocess capability imports | PASS | 1 | `test_h36_no_transitive_db_network_model_tool_or_hgt_capability_imports` |
| H37 | canonical W03 trust type reused when available | PASS | 1 | `test_h37_exact_w03_trust_and_serialization_framework_reused` |
| H38 | all public artifacts round-trip through canonical serializer | PASS | 7 | `test_h38_all_public_artifacts_canonical_roundtrip_with_w03_scalars` |
| H39 | all set-like collections have deterministic canonical order | PASS | 27 | `test_h39_set_like_order_is_deterministic_and_ordered_sequences_preserved` |
| H40 | contract construction performs no external I/O | PASS | 1 | `test_h40_contract_construction_and_parse_perform_no_external_io` |

```text
TEST FUNCTION COUNT: 40
PARAMETERIZED FUNCTION COUNT: 26
EXPANDED PYTEST CASE COUNT: 426
SAME-PROCESS DETERMINISM: PASS — all 15 models
FRESH-PROCESS DETERMINISM: PASS — all 15 models under PYTHONHASHSEED 0, 1, 34567
```

## Original implementation local commands and results

| Gate | Command | Actual result |
|---|---|---|
| Focused H01–H40 | `.venv\Scripts\python.exe -m pytest tests\test_investigation_contracts.py -q` | PASS: 426 passed in 4.93s; final harness agent run also 426 passed in 5.15s |
| Focused collection | `.venv\Scripts\python.exe -m pytest tests\test_investigation_contracts.py --collect-only -q` | 426 collected; exit 0 |
| Relevant W03 core regression | `.venv\Scripts\python.exe -m pytest tests\test_decision_contracts.py tests\test_decision_serialization.py -q` | PASS: 39 passed in 0.99s |
| Non-integration standard equivalent | `.venv\Scripts\python.exe -m pytest -m 'not integration' -q` | FAIL: 3 failed, 1358 passed, 48 deselected, 1 warning in 712.06s |
| Ruff | `.venv\Scripts\ruff.exe check .` | PASS |
| Strict mypy | `.venv\Scripts\python.exe -m mypy .` | PASS: 143 source files; project strict configuration retained |
| Dependency lock | `.venv\Scripts\flowlens-uv.exe --cache-dir 'C:\Users\C\.codex\visualizations\2026\10\05\01a10aa7-60f0-7b73-a51a-5dd065738c0e\uv-cache' lock --check --offline --no-python-downloads --python .venv\Scripts\python.exe` | PASS: 43 packages resolved; dependency and lock files unchanged |
| Compose configuration | `docker compose config --quiet` | PASS: exit 0; Docker config permission warnings retained |
| Local Docker readiness | `docker info --format '{{.ServerVersion}}'` | FAIL: Docker daemon named pipe absent |
| Local complete Compose smoke | Existing workflow's full smoke sequence | NOT RUN: no local Docker daemon; remote smoke passed on implementation SHA |
| Local W03 F01–F10 execution | `scripts/ci/run_w03_ai_loop_gate.py` full sequence | NOT RUN locally: no configured PostgreSQL test service; original repository-native CI F01–F10 subsequently passed |
| Repository Verification gate | `.github/workflows/ci.yml::verification-gate` | Original exact-SHA CI #87: FAILURE; Quality failed the stale C09 assertion |

The existing Python 3.12.14 virtual environment is used directly for local tests,
lint and typing. Initial uv cache/interpreter discovery attempts were blocked by
local cache permissions/managed-interpreter discovery. The final command above
uses an allowed task cache and explicit interpreter and passes without syncing
or changing dependencies. A uv `--no-sync` runner probe also warned that the
existing environment was created with 3.12.13 and currently runs 3.12.14.

### Original local failures and baseline preservation

1. `tests/test_c06_harness.py::test_frozen_c01_and_c05_sources_match_context_lock`
   fails a raw working-copy byte digest due to CRLF. All five protected W03
   source Git blobs exactly match the accepted SHA-256 values. Replacing CRLF
   with LF in memory exactly reproduces those Git blobs. No source was rewritten.
2. `tests/test_c09_ci_gate.py::test_frozen_manifest_schema_families_counts_and_content`
   fails the raw manifest digest due to CRLF: worktree
   `8e762cafd5bcddefca143da2f826090cd95a1f43e8b3f01e6f616208c317f6b8`,
   frozen Git blob
   `bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990`.
   Git blob and in-memory newline normalization checks pass. Manifest content,
   selectors, counts and accepted byte digest were not changed.
3. `tests/test_c09_ci_gate.py::test_classifier_publication_and_runtime_frozen_materials_unchanged`
   fails because of the three authorized new W04 modules. This is the actual
   contract/allowlist blocker and will not be removed by Linux line endings.

The full local suite began over the final staged source/test content, completed
at the implementation SHA, and did not overlap any source/test edit. The
blocking assertion was separately reproduced after commit with:

```text
.venv\Scripts\python.exe -m pytest tests\test_c09_ci_gate.py::test_classifier_publication_and_runtime_frozen_materials_unchanged -q
RESULT: 1 failed in 0.45s
```

At the original implementation SHA,
`git diff --exit-code af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
084c2fea93d0e021994de015c986de9ff92bf9a3 --
src/flowlens/decision tests/test_c09_ci_gate.py scripts/ci .github pyproject.toml
uv.lock migrations apps docker-compose.yml` returns 0. Existing W03 runtime,
contracts, harness, classifier, workflow, foundation and operational schema are
unchanged at that stage. No unsupported baseline repair was attempted before
Clarification-01 and Human Repair-01 authorization.

## Original exact-SHA CI final result

Draft PR: [#7](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/pull/7).

Exact original implementation source:
`084c2fea93d0e021994de015c986de9ff92bf9a3`.
[CI Run #87 / 37274660663](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37274660663)
completed with **FAILURE**. The original report had recorded an in-progress
observation; the final result is retained here as the original evidence stage.
The run was triggered by the PR. The frozen workflow has no feature-branch push
trigger, and no trigger or CI policy was changed.

| Original job / step | Final result |
|---|---|
| Classify change (111648945410) | PASS; original observed classification `UNKNOWN / FULL_EXACT_SHA`, reason `ambiguous_event`, exact original implementation head |
| Quality gate (111648977558) | FAILURE: non-integration suite had 1 failed, 1360 passed, 48 deselected, 1 warning in 1484.83s; the sole failure was the stale affected C09 selector |
| Database integration within Quality | PASS: 48 passed, 1361 deselected, 1 warning in 234.97s |
| Ruff / strict mypy / lock within original CI | NOT EXECUTED after the preceding Quality failure; the original local passes above are separate evidence |
| Docker Compose smoke (111648977613) | PASS, including build, startup, PostgreSQL readiness, API health, Worker liveness and teardown |
| Publication proof | SKIPPED, as required for full proof |
| W03 AI loop F01–F10 | PASS: frozen 38 selectors / 85 expanded cases |
| Repository Verification | FAILURE because Quality failed; no original full-proof success claimed |

The two Windows CRLF byte-digest selectors did **not** fail in exact-SHA Linux
CI: the only Linux non-integration failure was the stale source-boundary
assertion. Their status is `LOCAL_ENVIRONMENT_ONLY / CRLF`. They remain
unchanged; no line-ending normalization, expected hash substitution or unrelated
harness repair was performed.

## Clarification-01 and Repair-01 context lock

Normative repository copies:

- `W04_C01_GPT_CLARIFICATION_01.md`, SHA-256
  `0362682d1b52f641ccfeac6512709a6dca1fe50109b054423bc670479b357b62`.
- `W04_C01_CODEX_COMPATIBILITY_REPAIR_TASK_V1.md`, SHA-256
  `f41e6fb6c6519fe4cea3dc2ece915be1c3ae43fa7fca5bc4256d3d1f29787336`.

Both package entry hashes were verified before repair. Human authorization
source is the direct reply `确认授权`; the dedicated authorization record was
materialized/read back before mutation. The repair context lock records the
entry SHA as the original implementation, branch
`feat/w04-evidence-investigation`, clean tracked entry worktree, and only the
prior report as an untracked entry delta.

The affected selector is:

```text
tests/test_c09_ci_gate.py::test_classifier_publication_and_runtime_frozen_materials_unchanged
```

Its original stale assertion was line 522. This selector is **not** in the
frozen 38-selector C09 manifest; its existing name remains unchanged. The
manifest, 38 selector identities, 10 parameterized-selector identities, 85
expanded cases, gate runner and F01–F10 semantics were not modified.

The repair changes only the stale whole-source boundary logic within that
existing test. The earlier protected control-file comparisons and the original
`migrations` / `apps` freeze against `gate.ENTRY` remain intact.

The source boundary now compares exact NUL-delimited Git
`--name-status --no-renames -z` output from W03 main anchor
`af61bdfd5f7cf7961811c4c2dc8e554dd7eed509` to `HEAD`. Accepted output is exactly
three `A` records, in Git path order:

```text
src/flowlens/investigation/__init__.py
src/flowlens/investigation/contracts.py
src/flowlens/investigation/enums.py
```

Any baseline modification, deletion, type or mode change fails. Rename
detection is disabled, so a rename exposes a deletion and addition and fails.
Unexpected and missing additions also fail. Additional checks reject tracked
source differences from `HEAD` and non-ignored untracked source paths. Git tree
semantics avoid raw CRLF working-copy digest comparison.

Read-only source preservation checks passed: the repair has no source delta
relative to the original implementation, and the anchor-to-repair source delta
contains exactly the three authorized additions. The original implementation
commit is the repair commit's parent and was not amended. The repair commit
contains exactly the five bounded test/documentation files listed above.

## Repair boundary negative proof

A read-only audit executed the **actual repaired selector body** from its AST in
13 disposable temporary Git repositories. Only the hardcoded W03 anchor was
rebound in memory to each synthetic fixture baseline SHA; the assertion body
was unchanged. Fixture protected control files were present at the baseline.
The production source, tests, documents and repository Git state were not
mutated by these probes, and no pytest selectors were added.

| Synthetic Git fixture | Actual repaired selector result |
|---|---|
| Exact three authorized source additions | PASS: accepted |
| Unexpected added source path | PASS: rejected |
| Missing authorized addition | PASS: rejected |
| Modified baseline source | PASS: rejected |
| Deleted baseline source | PASS: rejected |
| Renamed baseline source | PASS: rejected |
| Baseline regular-file to symlink type replacement | PASS: rejected |
| Baseline executable-mode change | PASS: rejected |
| Tracked working-tree source modification | PASS: rejected |
| Staged source modification | PASS: rejected |
| Untracked non-ignored source addition | PASS: rejected |
| Modified migration | PASS: rejected |
| Modified application source | PASS: rejected |

Probe result: **13 / 13 PASS**, process exit 0. Example fixture root:
`C:\Users\C\AppData\Local\Temp\flowlens-repair01-final-audit-2rre9r67`;
fixture baseline paths were `src/baseline.py`, `migrations/baseline.py` and
`apps/baseline.py`. Every temporary repository was automatically removed.

## Repair local verification

| Repair proof | Command / mechanism | Current result |
|---|---|---|
| Affected selector + W04 H01–H40 + W03 core | `.venv\Scripts\python.exe -m pytest tests/test_c09_ci_gate.py::test_classifier_publication_and_runtime_frozen_materials_unchanged tests/test_investigation_contracts.py tests/test_decision_contracts.py tests/test_decision_serialization.py -q` | PASS: 466 passed in 6.56s = 1 affected selector + 426 W04 cases + 39 W03 core cases |
| Same-process and fresh-process determinism | H05 and H06 in the combined run above | PASS; original H01–H40 identities/counts and runtime implementation retained |
| Full non-integration | `.venv\Scripts\python.exe -m pytest -m 'not integration' -q` | LOCAL_ENVIRONMENT_ONLY / CRLF: 2 failed, 1359 passed, 48 deselected, 1 warning in 2061.03s; only the two exact byte-digest selectors below failed. Exact repair-SHA Linux CI: PASS, 1361 passed |
| Ruff | `.venv\Scripts\ruff.exe check .` | PASS |
| Strict mypy | `.venv\Scripts\python.exe -m mypy .` | PASS: 143 source files; strict configuration unchanged |
| Dependency verification | Repository lock check with explicit existing interpreter and task cache | PASS: 43 packages; dependency / lock files unchanged |
| Compose configuration | `docker compose config --quiet` | PASS |
| Local full W03 F01–F10 / 38 / 85 | Existing repository-native gate runner | NOT RUN locally: no configured local PostgreSQL test service; exact repair-SHA native Linux CI gate PASS, 38 selectors / 85 cases |
| Local full Compose smoke | Existing full smoke sequence | NOT RUN locally: Docker daemon absent; exact repair-SHA remote Compose smoke PASS |
| Repository Verification | Existing `.github/workflows/ci.yml::verification-gate` | PASS: exact repair-SHA aggregate completed successfully |

The lack of a local Docker daemon or PostgreSQL test service is recorded as an
execution limitation. Native full-gate and full Compose evidence come from the
existing exact-SHA CI workflow. No mock substitute, skipped frozen selector,
policy change, dependency addition or local runtime repair was introduced.

The original two CRLF-only local selectors remain:

```text
tests/test_c06_harness.py::test_frozen_c01_and_c05_sources_match_context_lock
tests/test_c09_ci_gate.py::test_frozen_manifest_schema_families_counts_and_content
```

Both were the only failures in the completed local repair run; no unexpected
non-CRLF failure occurred. Both passed in original and repair exact-SHA Linux
CI. Their source and manifest Git blobs remain unchanged, so no unrelated CRLF
repair was made. The local suite ran after the repair commit, at that exact
HEAD, without overlapping any source or test edit. The documentation report
update did not change the tested source or HEAD.

## Repair exact-SHA CI final result

Exact repair source: `b7cebe71346050ee2f817905d600c23a26542b7e`.
[CI Run #88 / 37278703544](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37278703544)
completed with **SUCCESS**. Its exact source head is the repair SHA;
its classifier base is the original implementation SHA. The same branch and
draft PR #7 were updated through a normal push, preserving the original commit.

| Repair job | Final result |
|---|---|
| Classify change (111661453079) | PASS: actual `UNKNOWN / FULL_EXACT_SHA`; verified reason codes `["unknown_or_empty_delta"]`; exact repair source head |
| Quality gate (111661487404) | PASS: Linux non-integration 1361 passed, 48 deselected, 1 warning in 1079.22s; integration 48 passed, 1361 deselected, 1 warning in 187.37s; Ruff PASS, strict mypy PASS (143 source files), dependency lock PASS (43 packages) |
| Docker Compose smoke (111661487488) | PASS |
| Publication proof | SKIPPED, as required for full proof |
| W03 AI loop gate (111668205564) | PASS: F01–F10, frozen 38 selectors / 85 expanded cases; summary implementation SHA equals exact repair SHA; frozen manifest byte digest retained |
| Repository Verification (111670231015) | PASS: complete repository aggregate |

The actual classifier output is preserved without forcing or changing policy.
All required proof jobs and the repository Verification aggregate have final
passing evidence. Job logs explicitly show checkout and expected HEAD as
`b7cebe71346050ee2f817905d600c23a26542b7e`. The full Linux suite includes the
repaired selector, H01–H40 and W03 core regression without skips or changes to
the frozen proof policy.

The native gate command retained by CI is:

```text
uv run python scripts/ci/run_w03_ai_loop_gate.py
  --manifest docs/w03/checkpoints/c09/specs/c09_gate_manifest.json
  --expected-head b7cebe71346050ee2f817905d600c23a26542b7e
  --output-json $RUNNER_TEMP/w03-ai-loop-gate.json
```

Its final JSON summary was read back and verified, not inferred from an earlier
run. Manifest SHA-256 is
`bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990`;
`overall` is `PASS`, with the exact repair implementation SHA and these results:

| Frozen family | Selectors | Expanded cases | Repair-SHA result |
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

## Warnings, limitations and scope

Known warnings remain: existing Starlette/httpx TestClient deprecation; local
Docker configuration read-permission warnings; uv cache/interpreter discovery
warnings; normal Windows Git LF-to-CRLF checkout warnings. No dependency or
baseline change was made to address these warnings.

Known limitations:

- Repair-01 is review-ready. Independent GPT review, Human C01 acceptance and
  closeout remain separate authorization boundaries.
- Canonical Decimal/date/datetime scalar values are W03 JSON strings. Parsing
  preserves canonical bytes/identity and does not infer their original Python
  scalar subtype. Typed business timestamps retain aware-datetime validation.
- Reference existence, registry business meaning, source-row binding, causal
  grounding, journal persistence/chain behavior and summary prose grammar remain
  deferred to the explicitly unauthorized later checkpoints.
- Summary text and Human notes are presentation/audit data only. C01 constructs
  no findings, plans, queries, interventions or operational execution behavior.

```text
SCOPE DEVIATIONS: NONE
ORIGINAL IMPLEMENTATION PRESERVED: YES
RUNTIME CHANGE IN REPAIR: NONE
W03 RUNTIME CHANGE: NONE
W03 BASELINE SOURCE PRESERVATION: PASS
W04-C01 EXACT ADDITIVE SOURCE ALLOWLIST: PASS
W04 H01-H40: PASS
SAME-PROCESS / FRESH-PROCESS DETERMINISM: PASS
W03 CORE REGRESSION: PASS
REPAIR W03 F01-F10 / 38 / 85: PASS
REPAIR FULL NON-INTEGRATION: PASS — exact-SHA Linux CI, 1361 passed
CRLF LOCAL-ONLY: the two exact selectors listed above; unchanged / no Linux reproduction
RUFF: PASS
STRICT MYPY: PASS
DEPENDENCY VERIFY: PASS
REPAIR DOCKER COMPOSE SMOKE: PASS
REPAIR REPOSITORY VERIFICATION: PASS
REPAIR EXACT-SHA CI: #88 / 37278703544 / PASS
OPERATIONAL MUTATION: NONE
DB ACCESS: NONE
NETWORK ACCESS: NONE
MODEL/LLM ACCESS: NONE
TOOL EXECUTION: NONE
GPT INDEPENDENT REVIEW: PENDING
HUMAN C01 ACCEPTANCE: PENDING
C01 CLOSEOUT: NOT AUTHORIZED
W04-C02: NOT AUTHORIZED
```

Runtime capability statements describe the unchanged contract layer.
Development Git, GitHub evidence inspection, synthetic temporary Git probes and
existing CI verification are separate from runtime capability. Human Repair-01
authorization permits only this bounded repair and its proof; it does not grant
C01 acceptance, closeout, merge or checkpoint advancement.
