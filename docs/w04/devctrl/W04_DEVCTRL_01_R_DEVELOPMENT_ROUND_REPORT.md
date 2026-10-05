# W04-DEVCTRL-01 Development Round Report

Date: 2026-10-05 (Asia/Shanghai).

```text
TASK: W04-DEVCTRL-01 — W04 Source Evolution + Verification Latency Hardening
HUMAN AUTHORIZATION: APPROVED
ENTRY SHA: e95a94152e7b57dd1cdbef95c16ef496a419906e
IMPLEMENTATION SHA: edb073efb6034a10978083685ff997a5b0b24904
W03 VERIFIED MAIN: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
C01 SOURCE FREEZE: 084c2fea93d0e021994de015c986de9ff92bf9a3
BRANCH: feat/w04-evidence-investigation
IMPLEMENTATION COMMIT: ci(w04): govern source evolution and proof routing
NORMAL PUSH: COMPLETE
CHANGE CLASS: I
PROOF CLASS: FULL_EXACT_SHA
IMPLEMENTATION EXACT-SHA CI: #91 / 37312046687 / SUCCESS
PR #7: OPEN / DRAFT / UNMERGED
IMPLEMENTATION: COMPLETE
HARNESS: PASS — exact-SHA Linux CI
CI: PASS
STATUS: REVIEW_READY
REVIEW_READY: YES
CHECKPOINT CLOSED: NO
```

The authorized control work is implemented and its exact-SHA full proof passed.
This report records implementation evidence for independent GPT review and Human
DEVCTRL acceptance. It grants no checkpoint acceptance, closeout, merge or C02
authority.

## 1. Authorization, entry and context lock

The Human's pasted request is the implementation authorization. The ZIP supplies
the normative design material; its documents do not independently grant broader
actions. The read order was GPT Design Master V1, Design Review R1, Human
Authorization Approved, and Codex Task V1, followed by applicable repository
controls. Design Review R1 was PASS / APPROVED FOR CODEX IMPLEMENTATION.

The approval and pre-implementation inspection are materialized in
`W04_DEVCTRL_01_HUMAN_AUTHORIZATION.md` and `W04_DEVCTRL_01_CONTEXT_LOCK.md`.
The context lock records the package digests, baseline Git blobs, C01 source
tuple, classifier byte freeze, frozen W03 gate and existing Verification routing.
The entry worktree/index were clean, branch and PR matched the task, and C01
closeout CI #90 / 37297604459 was SUCCESS at the entry SHA.

The normative master and actual Git tree use `__init__.py`. The pasted request's
`init.py` transcription was resolved by its explicit normative-master precedence,
with the three specified Git blob OIDs verified before implementation.

No runtime context, dataset, scenario, prompt registry or tool registry was
created or changed. Disposable Git repositories exercise negative controls.

## 2. Exact changed files and protected materials

The implementation commit changes exactly these nine authorized files:

| Path | Result |
|---|---|
| docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json | Initial versioned, CLOSED C01 manifest |
| scripts/ci/verify_w04_source_evolution.py | Standard-library deterministic source verifier |
| scripts/ci/classify_change.py | Narrow W04 publication and namespace classification |
| tests/test_w04_source_evolution.py | Source/manifest transition and negative controls |
| tests/test_ci_change_classifier.py | W04 grammar, routing and W03 history replay |
| tests/test_ci_publication_gate.py | W04 real-Git publication/content/boundary controls |
| tests/test_c09_ci_gate.py | Bounded update inside the preserved compatibility selector |
| docs/w04/devctrl/W04_DEVCTRL_01_HUMAN_AUTHORIZATION.md | Human authorization record |
| docs/w04/devctrl/W04_DEVCTRL_01_CONTEXT_LOCK.md | Pre-implementation context lock |

A separate publication commit adds only this tenth authorized path:
`docs/w04/devctrl/W04_DEVCTRL_01_R_DEVELOPMENT_ROUND_REPORT.md`.
It follows implementation CI success and does not amend the implementation.
Its exact publication SHA and CI result are supplied in the final handoff,
avoiding a self-referential commit identity inside this document.

Entry-to-implementation Git diffs are empty for `src/**`, `apps/**`,
`migrations/**`, `.github/workflows/**`, the publication verifier, W03 runner and
manifest, `pyproject.toml`, `uv.lock` and `docker-compose.yml`.
W03-to-implementation source additions remain exactly the accepted C01 trio.

| Protected file | Unchanged Git blob |
|---|---|
| scripts/ci/verify_publication.py | 8f97a117f936d9dce91957f7b44551acb5d5c2b6 |
| .github/workflows/ci.yml | 14c826b122b7103953e8b4539981004241205ba4 |
| docs/w03/checkpoints/c09/specs/c09_gate_manifest.json | b2a03f3295c162a639eb99dbd87b4a636c3b1e85 |
| scripts/ci/run_w03_ai_loop_gate.py | c533928e584335437ae8a902fcab4faab64ae8ef |
| pyproject.toml | 318bbc0a858f760e6c4d7a2d3fdbfcc111febb77 |
| uv.lock | 619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a |
| docker-compose.yml | 5a0b6e8486edc69f9f79c7e1345a842aa412983c |

No W1/W2 schema, migration, hash, generator, scenario or HGT-isolation contract
changed. No operational truth was mutated and no runtime HGT was read.

## 3. Manifest and source-evolution verifier

Manifest schema is `w04-source-evolution-manifest-v1`, policy is
`W04-DEVCTRL-01`, root is `src/flowlens/investigation`, and W03 baseline is
`af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`. It contains only CLOSED W04-C01,
frozen at `084c2fea93d0e021994de015c986de9ff92bf9a3`. No C02 paths were added.

| C01 path | Frozen Git blob OID |
|---|---|
| src/flowlens/investigation/__init__.py | c23929f85dccd78bc72ef3b2b1415c6e8eaf0452 |
| src/flowlens/investigation/contracts.py | 0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e |
| src/flowlens/investigation/enums.py | 9c818780423f32f144b18666784ebc9ea3abdccc |

The generic API is
`verify_source_evolution(manifest_path, expected_head, repo)`; the CLI accepts
`--manifest`, `--expected-head`, `--repo` and optional `--output-json`.
The implementation uses only the standard library.

The verifier rejects duplicate keys, invalid constants/encoding, schema drift,
unknown ids/states, invalid SHA grammar, duplicate/reordered checkpoints,
non-normalized/duplicate/out-of-root paths, wrong HEAD and missing/non-ancestor
W03 baseline. Paths are literal Git inputs. It binds the committed manifest to
HEAD, permits only the exact C01 bootstrap before the first manifest commit, and
rejects alternate manifest paths and uncommitted authority substitution.

Every reachable manifest version and every parent transition in the post-W03
Git DAG are validated. CLOSED entries and AUTHORIZED path lists are immutable;
new entries append as AUTHORIZED; AUTHORIZED may close once. Deletion/recreation,
downgrade, reassignment and conflicting-merge bypasses fail.

At exact final HEAD, all W03 baseline source blobs/types/modes remain frozen and
all added source paths must be represented exactly once. CLOSED files must match
their freeze commit and final HEAD; AUTHORIZED paths may be absent or present.
Non-regular Git entries and directory masquerades fail. Staged, unstaged,
untracked and hidden tracked-content drift fail. HEAD and manifest bytes are
rechecked after proof to detect concurrent changes.

Output is deterministic, with ordered paths and a digest of accepted Git bytes,
so CRLF checkout does not alter the committed manifest identity. Optional output
must be outside the repository; stale PASS is invalidated before proof starts.

**Precise boundary:** source membership/preservation is checked at final HEAD,
and CLOSED identity at freeze and final HEAD. Historical enforcement validates
manifest versions/transitions; it does not require every intermediate historical
source tree to pass. Manifest JSON alone does not establish Human approval.

At the implementation SHA the source proof is PASS, with only the three C01
additions and no AUTHORIZED checkpoint. Manifest SHA-256:
`86b45a8f09c5ca58d5f151fad2d80266a395fea566dc25a635b41a22bc6169fd`.

## 4. Classifier, publication routing and C09 compatibility

Only Markdown basenames under `docs/w04/` matching these four grammars are P:

```text
*_R_DEVELOPMENT_ROUND_REPORT.md
*_GPT_INDEPENDENT_REVIEW_R<number>.md
*_GPT_INDEPENDENT_DEEP_REVIEW_R<number>.md
*_FINAL_CLOSEOUT_REPORT.md
```

Other `docs/w04/**` paths are C; `src/flowlens/investigation/**` is I.
Existing foundation F and malformed/unrecognized UNKNOWN semantics remain.
Normalized namespace rules precede generic foundation-basename rules.
Mixed deltas use the existing conservative ranking; UNKNOWN dominates.
Push, unproven and ambiguous boundaries remain full proof.

| Actual class | Proof |
|---|---|
| P with verified publication-only delta | PUBLICATION_EXACT_SHA |
| C / I / F / UNKNOWN, push or ambiguous boundary | FULL_EXACT_SHA |

Implementation CI measured **I / FULL_EXACT_SHA**, with reason
`verified_source_head_delta`, for the exact entry-to-implementation nine-file
delta. The task's advisory C expectation was not forced: ordinary new verifier
and C09 tests retain the existing `tests/** => I` behavior.

`verify_publication.py` is byte-for-byte unchanged and receives the narrow W04
grammar through its existing shared-helper import. Real-Git tests reject mixed
control/source/unknown paths, invalid boundaries, whitespace, conflicts,
unbalanced fences and other unsafe publication content.

The C09 selector remains
`test_classifier_publication_and_runtime_frozen_materials_unchanged`.
Only its body changes: classifier byte freeze and C01-local three-path assertion
are removed; the generic source verifier is called. Publication verifier,
pyproject, lock and Compose W03 freezes, plus migrations/apps freezes, remain.

Workflow change: NONE. W03 runner/manifest change: NONE. Frozen selector identities,
F01-F10 semantics, 38 selectors, 10 parameterized selectors and 85 expanded cases
remain unchanged. Existing Verification remains authoritative:
P requires Publication SUCCESS and heavy jobs SKIPPED; other classes require
Quality/Compose/W03 SUCCESS and Publication SKIPPED.

## 5. D01-D36 coverage

All rows PASS. D01-D26 selectors are in `tests/test_w04_source_evolution.py`;
the `test_dNN_*` names map directly to each numbered control. Counts below are
measured expanded cases, not forecast design counts.

| ID | Requirement and observed coverage | Cases |
|---|---|---:|
| D01 | Exact schema, keys at every level and top-level values | 10 |
| D02 | Duplicate keys, invalid constants, encoding and JSON roots rejected | 11 |
| D03 | Exact W03 baseline SHA | 1 |
| D04 | Exact W04 source root | 4 |
| D05 | Checkpoint id/state vocabulary, freeze/blob grammar and AUTHORIZED nulls | 22 |
| D06 | Checkpoint ordering and uniqueness | 2 |
| D07 | Path normalization/namespace plus literal Unicode, space and bracket Git inputs | 16 |
| D08 | Duplicate paths across checkpoints rejected | 2 |
| D09 | Exact C01 bootstrap; no future bootstrap; manifest tree cannot masquerade as absent | 4 |
| D10 | Exact C01 source freeze SHA | 1 |
| D11 | Exact C01 Git blob OIDs | 1 |
| D12 | CLOSED immutability, including restored illegal side-branch history | 2 |
| D13 | AUTHORIZED path immutability and conflicting merge rejection | 5 |
| D14 | AUTHORIZED closes once; freeze must be a commit, not annotated-tag OID | 2 |
| D15 | CLOSED downgrade rejected | 1 |
| D16 | Entry deletion and manifest deletion/recreation rejected | 3 |
| D17 | New checkpoints append as AUTHORIZED | 2 |
| D18 | Exact HEAD and concurrent HEAD/manifest-change fail-closed controls | 6 |
| D19 | Baseline exists and is ancestor | 2 |
| D20 | W03 source modification/deletion/rename/mode/type drift rejected | 5 |
| D21 | Unexpected source additions rejected | 2 |
| D22 | Authorized absence/presence; no uncommitted/alternate policy or parent-tree bypass | 5 |
| D23 | CLOSED file exists at freeze and final HEAD | 2 |
| D24 | CLOSED blob/mode frozen; non-regular Git entries rejected | 6 |
| D25 | Staged/unstaged/untracked and assume-unchanged/skip-worktree content drift rejected | 5 |
| D26 | Deterministic output, real CRLF clone, CLI failure/output boundary and stale-PASS invalidation | 5 |
| D27 | Four narrow W04 publication grammars classify P | classifier/publication matrices |
| D28 | Manifest, authorization, context lock and other W04 documents classify C | classifier/publication mixed controls |
| D29 | Investigation source namespace classifies I | classifier path/delta matrices |
| D30 | Foundation paths preserve F | classifier path/delta matrices |
| D31 | Malformed and unrecognized paths remain UNKNOWN | classifier malformed/path matrices |
| D32 | Mixed-class ranking preserves full proof | classifier mixed/delta matrices |
| D33 | Push and ambiguous/unproven boundaries require full proof | classifier real-Git boundary controls |
| D34 | Publication proof accepts only exact safe W04 report deltas | real-Git publication/content/boundary matrices |
| D35 | Accepted W03 classification semantics preserved | actual Git-history replay |
| D36 | Generic C09 compatibility and unchanged authoritative W03/Verification gate | affected selector, protected blobs and exact-SHA 38/85 gate |

D01-D26 total 127 cases. The three concurrency cases counted under D18 also
support D26 and are not counted twice. D27-D35 share the 90 classifier and 35
publication cases; D36 adds the one affected C09 case to the focused pack.

Relevant D27-D35 selectors include
`test_w04_path_grammar_and_control_boundary`,
`test_w04_malformed_paths_rejected_by_shared_helper`,
`test_w04_current_git_delta_routes_each_class`,
`test_w04_publication_ambiguous_boundary_keeps_full`,
`test_accepted_w03_history_replays_from_actual_git_diffs`,
`test_w04_narrow_report_grammars_pass_exact_publication`,
`test_w04_report_mixed_delta_rejects_publication`,
`test_w04_publication_content_defects_fail` and
`test_w04_publication_invalid_boundary_rejected`.

## 6. Measured collection and focused/regression results

Actual pytest collection and AST counting excluding fixtures agree.
The `test_dataset` fixture is not counted as a test function.

| Scope | Test functions | Parameterized functions | Expanded cases | Result |
|---|---:|---:|---:|---|
| Source-evolution suite | 52 | 27 | 127 | 127 PASS |
| Classifier suite | 11 | 6 | 90 | 90 PASS |
| Publication suite | 11 | 6 | 35 | 35 PASS |
| Affected C09 selector | 1 | 0 | 1 | PASS |
| Focused DEVCTRL pack | 75 | 39 | 253 | ALL PASS |
| Full C09 suite | 22 | 10 | 79 | Local 78 PASS / 1 accepted CRLF digest failure; all cases pass in Linux full CI |
| W04-C01 H01-H40 | 40 | 26 | 426 | 426 PASS |
| W03 core contracts + serialization | 16 | 2 | 39 | 39 PASS |
| Frozen W03 gate | 38 selectors | 10 | 85 | Exact-SHA Linux ALL PASS |
| Whole repository | 536 | 158 | 1615 | Linux 1567 non-integration + 48 integration PASS |

The focused pack is source + classifier + publication + the affected C09 selector.
The whole-repository 1615 cases split into 1567 non-integration and 48 integration.
Regression scopes overlap and must not be summed as independent coverage.

Local source suite: 127 passed in 204.27s. Classifier/publication: 125 passed.
C01/core: 465 combined passes. Corrected CRLF fixture and affected C09:
2 passes in 12.11s. Ruff passed, strict mypy passed in 145 files, and offline
`uv lock --check` passed with 43 packages.

Final local full non-integration at the committed implementation SHA:
**1565 passed / 2 accepted Windows CRLF digest failures / 48 deselected /
1 existing warning in 978.73s**. No DEVCTRL implementation test failed.

## 7. Exact-SHA CI, quality and frozen gate

Authoritative implementation proof:
[CI #91 / 37312046687 — SUCCESS](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37312046687).

Every executing source job checks
`edb073efb6034a10978083685ff997a5b0b24904`.

| Job / proof | Actual result |
|---|---|
| Classify change | SUCCESS; I / FULL_EXACT_SHA; exact e95a9415… → edb073ef… delta |
| Database integration | 48 passed / 1567 deselected / 1 existing warning in 158.22s |
| Complete non-integration | 1567 passed / 48 deselected / 1 existing warning in 759.66s |
| Ruff | All checks passed |
| Strict mypy | No issues in 145 source files |
| uv lock --check | PASS; 43 packages |
| Docker Compose smoke | SUCCESS; config/build/stack/PostgreSQL/API health/worker checks |
| W03 AI loop gate | SUCCESS; exact SHA, all F01-F10, 38 selectors / 85 cases |
| Publication proof | SKIPPED, required for this full-proof route |
| Verification gate | SUCCESS; Classify/Quality/Compose/W03 SUCCESS, Publication SKIPPED |

The W03 summary binds the implementation SHA and unchanged manifest SHA-256
`bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990`.
No frozen case was skipped, xfailed, substituted or removed in native CI.

| Family | Selectors | Cases | Native result |
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

Report-only publication will use the unchanged P route and final Verification.
That separate proof attests the report commit; it does not replace this immutable
implementation-SHA full proof. No latency benchmark or weakened full-proof
requirement is claimed.

## 8. Warnings, limitations and repaired tooling

1. Windows checkout CRLF causes two pre-existing raw-byte digest assertions:
   `tests/test_c06_harness.py::test_frozen_c01_and_c05_sources_match_context_lock`
   and `tests/test_c09_ci_gate.py::test_frozen_manifest_schema_families_counts_and_content`.
   For both failing files, CRLF-normalized worktree bytes equal committed Git
   bytes, whose digests match the frozen expectations. Source/manifests were
   preserved. Both assertions pass in exact-SHA Linux CI.

2. Local database integration collected 48 cases and skipped them because
   `FLOWLENS_DATABASE_URL` was absent. Local Docker daemon was unavailable.
   Compose configuration passed locally, with a Docker config access warning.
   The local frozen runner correctly failed on F09's six database skips after
   F01-F08's 59 passes; F10 was not executed in that local run. Native CI supplies
   all 48 integration passes, complete Compose proof and all 85 frozen passes.

3. The first local full regression process loaded the earlier CRLF fixture
   before its correction and ended 1564 passed / 3 failed / 48 deselected.
   The additional DEVCTRL fixture failure was repaired with a fresh CRLF clone,
   then verified by targeted, complete source-suite, final full-local and Linux
   CI runs. It is absent from the final committed-SHA local result.

4. An initial uv invocation encountered an existing interpreter-environment
   mismatch and transiently disrupted local cached tooling. Installed files
   were restored from the existing lock/cache; all 42 locked registry packages
   plus the project were verified, with 5451 RECORD-file checks and no hash
   defects. A transient early local gate import failure was rerun after repair.
   No dependency version, lock file or repository source changed. Final proof
   uses the restored environment and clean native CI.

5. One existing Starlette/httpx deprecation warning appears in local and native
   suites. No dependency change is authorized or needed for this task.

6. Automatic approval review initially rejected normal push because destination
   ownership/trust was not yet established. Authenticated GitHub identity matched
   the private repository owner, and admin/push permissions plus the expected PR
   and branch were verified. The same normal push was then approved and
   succeeded. There was no bypass, force push or history rewrite.

7. The actual I class differs from the advisory C expectation for the documented
   ordinary-test reason. C01 filename transcription is resolved as recorded in
   section 1. No broader publication grammar, workflow change, gate change,
   runtime change, extra dependency or C02 implementation was required.

Detailed local artifacts are outside the repository under
`C:/Users/C/.codex/visualizations/2026/10/05/01a10bf5-3ae7-7491-9f19-60fdbbf997c4/`,
including `nonintegration-final-local.log`,
`w03-gate-local-restored.log`, `w03-gate-local-restored.json`,
`c09-local.log`, `source-evolution-implementation.json` and the reviewed
`W04_DEVCTRL_01_IMPLEMENTATION.patch`. Git history, committed controls and native
CI are the authoritative shared evidence.

## 9. Review boundary and final substantive states

Internal parallel technical audits found no unresolved implementation blocker.
They are development checks, not the formal GPT independent review. Human
implementation approval is distinct from Human DEVCTRL acceptance.
PR #7 remains open/draft/unmerged and the feature branch is retained.
No next checkpoint is started.

```text
RUNTIME SOURCE CHANGE:
NONE
WORKFLOW CHANGE:
NONE
W03 FROZEN GATE CHANGE:
NONE
OPERATIONAL MUTATION:
NONE
GPT INDEPENDENT REVIEW:
PENDING
HUMAN DEVCTRL ACCEPTANCE:
PENDING
DEVCTRL CLOSEOUT:
NOT AUTHORIZED
W04-C02:
NOT AUTHORIZED
```
