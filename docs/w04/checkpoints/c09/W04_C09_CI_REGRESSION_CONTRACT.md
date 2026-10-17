# W04-C09 V1.1 — CI Regression Contract

Normative behavior copied from the authorized task Sections 1 and 4-12. DEVCTRL-03 resilience additionally requires all seven native shard job and suite durations <3300s, with the 65m ceiling unchanged.

# 1. Product / engineering outcome

W04-C09 turns the accepted C01-C08 investigation semantics into one explicit,
named, exact-SHA-bound semantic regression gate:

```text
job id:
w04-investigation-gate

job name:
W04 investigation gate

gate version:
w04-c09-investigation-gate-v1

manifest schema:
w04-c09-regression-manifest-v1

summary schema:
w04-c09-gate-summary-v1
```

The new job consolidates critical accepted W04 proofs without replacing any
existing full-suite, W03, Compose, Quality, source-evolution or exact-SHA proof.

The C09 gate is required for every non-publication exact-SHA proof and skipped
for publication-only proof.

---

# 4. Critical semantic families

```text
F01 C01_CONTRACTS_IDENTITY
6 selectors / 6 cases

F02 C02_CASE_BINDING_TEMPORAL
6 selectors / 6 cases

F03 C03_PLANNING_DETERMINISM
6 selectors / 6 cases

F04 C04_AUTHORIZED_NAVIGATION_READ_ONLY
9 selectors / 14 cases

F05 C05_FINDINGS_CONFLICT_UNCERTAINTY
7 selectors / 7 cases

F06 C06_HUMAN_AUTHORITY_AUDIT
10 selectors / 10 cases

F07 C07_SUMMARY_GROUNDING
10 selectors / 10 cases

F08 C08_PROTECTED_REPLAY
8 selectors / 17 cases

F09 SOURCE_EVOLUTION_GOVERNANCE
5 selectors / 5 cases
```

The exact selectors/counts are frozen by Appendix A.

No selector substitution is permitted.

---

# 5. Exact regression manifest identity

Create exactly:

```text
docs/w04/checkpoints/c09/specs/c09_gate_manifest.json
```

Its exact raw UTF-8 bytes must equal Appendix A, including final LF.

Required raw SHA-256:

```text
d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1
```

Required canonical-content SHA-256:

```text
937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad
```

The runner must independently hard-code the canonical-content SHA-256 and reject
any semantic content change even if the JSON remains schema-valid.

---

# 6. Gate runner

Create:

```text
scripts/ci/run_w04_investigation_gate.py
```

Required properties:

1. fail closed;
2. exact expected HEAD required;
3. output file must be outside repository;
4. manifest schema/version/gate/checkpoint/entry/baseline exact;
5. canonical manifest content digest exact;
6. family set/order exact;
7. selectors exact and globally unique;
8. selector grammar is an exact pytest function selector under `tests/`;
9. no wildcard, `-k`, marker selection, shell token, class selector, parameter
   leaf selector or arbitrary CLI fragment in the manifest;
10. each selector must collect exactly its frozen expanded count;
11. family totals and global `67 / 81` totals exact;
12. execute the nine semantic families as **nine independent pytest subprocesses**
    in manifest order;
13. each family subprocess receives only that family's exact selectors;
14. neutralize repository `addopts` for both collection and execution;
15. each collected leaf receives a complete terminal call outcome;
16. failed/error/skipped/xfail/xpass/deselected/partial collection are hard
    failures;
17. every family subprocess exit code must be zero;
18. do not use broad marker/folder execution as semantic evidence;
19. output deterministic JSON with no clock/timestamp/random field;
20. successful output bytes are canonical UTF-8 JSON:
    `sort_keys=True`, compact separators, `allow_nan=False`, plus one final LF;
21. include a `summary_sha256` self-seal computed over the exact summary payload
    with the `summary_sha256` field omitted;
22. on failure, delete/replace any prior output before execution so a stale PASS
    can never remain usable as current evidence;
23. no live provider/model call;
24. no runtime HGT access;
25. no operational mutation.

The separate-family execution requirement is intentional. It prevents
cross-family monkeypatch/global-state/fixture leakage from turning one family's
accepted proof into another family's hidden prerequisite.

Minimum successful semantic summary:

```json
{
  "schema_version": "w04-c09-gate-summary-v1",
  "gate_version": "w04-c09-investigation-gate-v1",
  "implementation_sha": "<exact 40 lowercase hex>",
  "manifest_sha256": "d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1",
  "manifest_content_sha256": "937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad",
  "total_families": 9,
  "total_selectors": 67,
  "total_tests": 81,
  "families": [
    {
      "id": "F01 C01_CONTRACTS_IDENTITY",
      "status": "PASS",
      "selectors": 6,
      "tests": 6
    }
  ],
  "overall": "PASS",
  "summary_sha256": "<canonical self-seal>"
}
```

The real file contains all nine families in exact manifest order.

Print the same semantic content to stdout. The post-CI evidence process must also
record the raw SHA-256 of the generated summary file bytes.

# 7. Independent gate-contract verifier

Create:

```text
scripts/ci/verify_w04_investigation_gate_contract.py
```

This is an independent development-plane verifier for the new runner and
workflow contract. It is not a pytest test module.

It must test the actual runner functions/CLI wherever practical.

At minimum it must prove fail-closed behavior for:

```text
extra/missing root keys
extra/missing family keys
extra/missing target keys
duplicate JSON keys
NaN / Infinity / malformed JSON
wrong schema
wrong gate version
wrong checkpoint
wrong entry SHA
wrong baseline identity
wrong manifest raw/canonical digest
missing/reordered/unknown/duplicate family
duplicate selector across families
zero/noninteger/negative expected count
wildcards
-k / -m / pytest flags
shell metacharacters
class selectors
explicit parameter-leaf selectors
missing/renamed selector
collection error
count drift
partial parameter collection
failed case
setup error
teardown error
skip
xfail
xpass
wrong exact HEAD
stale PASS output
repository-local output path
nondeterministic summary ordering
wrong/missing summary self-seal
family subprocess ordering drift
family executed in a shared pytest process
```

It must also verify the workflow contract from actual
`.github/workflows/ci.yml` and prove:

```text
exactly one new job id = w04-investigation-gate
name = W04 investigation gate
needs = classify-change
P => skipped
non-P => required
timeout = 30m

existing W03 gate unchanged

verification-gate depends on both:
W03 AI loop gate
W04 investigation gate

P truth:
W03 skipped
W04 skipped
Publication success
heavy/full jobs skipped

non-P truth:
W03 success
W04 success
Publication skipped
required heavy/full jobs success
```

It must execute the actual verification shell truth table with adversarial
wrong statuses, not only grep for strings.

It must verify no new action pin/dependency/image is introduced.

It must verify the active DEVCTRL-03 collection contract remains exactly:

```text
2997 nodes
63 files
same node digest
same weights digest
same plan schema
7 shards
65m non-integration timeout
```

## C08 replay-harness source-delta guard

The verifier must also compare the current
`tests/test_investigation_replay.py` with the exact file at:

```text
C09_ENTRY_SHA =
1fa841f2ee0d6612774c9f0ced204289df86e7a1
```

The comparison must be structural and source-exact for all unrelated top-level
units. Do not rely on line numbers.

Parse both files with `ast` and map top-level source units by identity:

```text
imports
module docstring
FunctionDef / AsyncFunctionDef / ClassDef name
simple module assignment target name
```

All entry top-level units must be identical except this exact authorized set:

```text
DEVCTRL_03_ENTRY_SHA          # may remain or be retired only as part of R43 migration
C09_ENTRY_SHA                 # may be added
W04_C09_MANIFEST_CONTENT_SHA256  # may be added
FULL_JOBS

_devctrl03_workflow_delta_guard
test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged
_check_native_metadata
_native_metadata_fixture
_validate_w04_c09_gate_summary    # optional new helper
test_r46_stage_b_exact_sha_full_native_ci
```

No other top-level unit may be added, removed or changed.

In particular, all R01-R42 and unrelated R43/R46 support test bodies and all
decorators/parameter lists must remain source-identical.

The verifier must fail if:

```text
an unauthorized top-level symbol changes
an unauthorized symbol is added/removed
any unrelated test decorator changes
any unrelated test body changes
any import changes
module docstring changes
R46 damage parameter list changes
R43/R46 selector names change
```

This harness-delta guard is required both locally and in the new W04 gate job.

If the authorized implementation genuinely requires a different replay-test
symbol to change:

```text
W04_C09_REQUIRES_GPT_CLARIFICATION
```

STOP rather than widening the allowlist.

# 8. Workflow change

Modify:

```text
.github/workflows/ci.yml
```

Add exactly one new job:

```text
id:
w04-investigation-gate

name:
W04 investigation gate

needs:
classify-change

schedule:
same non-P condition as W03 AI loop gate

runs-on:
ubuntu-latest

timeout-minutes:
30
```

Reuse only current pinned:

```text
actions/checkout
actions/setup-python
astral-sh/setup-uv
actions/upload-artifact
pgvector/pgvector:0.8.6-pg17-bookworm
Python 3.12
uv 0.12.5
```

Use PostgreSQL test service because F04 includes native DB selectors.

Required steps:

```text
checkout exact source HEAD with fetch-depth 0
verify exact source HEAD
setup Python
setup uv
uv sync --frozen
verify PostgreSQL readiness
alembic upgrade head

run:
verify_w04_investigation_gate_contract.py

run:
run_w04_investigation_gate.py

upload:
w04-c09-gate-<exact HEAD>
```

Upload exactly the successful summary JSON using the already-pinned
`actions/upload-artifact` action.

No new GitHub Action is authorized.

---

# 9. Verification-gate integration

Do not modify Quality semantics.

Do not remove or weaken W03 gate.

Extend only final Verification conjunction.

Required non-P jobs:

```text
Classify change
Static and plan
Integration and data
seven non-integration shards
Non-integration aggregate
Quality gate
Docker Compose smoke
W03 AI loop gate
W04 investigation gate
Verification gate
```

Publication is skipped.

Required P route:

```text
Classify change = SUCCESS
Publication proof = SUCCESS
W03 AI loop gate = SKIPPED
W04 investigation gate = SKIPPED
full/heavy jobs = SKIPPED
Verification gate = SUCCESS
```

---

# 10. R43 harness-only compatibility evolution

Modify only the existing R43-related workflow helper/assertions inside:

```text
tests/test_investigation_replay.py
```

Keep selector name unchanged:

```text
test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged
```

Do not change its parameterization because it has none.

For the smallest possible replay-harness delta, retain the existing helper symbol
name:

```text
_devctrl03_workflow_delta_guard
```

but evolve its implementation from the DEVCTRL-03-only timeout proof into an
exact C09-aware workflow proof. The historical name is retained only to minimize
the C08 harness delta; its new docstring must state that it now enforces the
C09-authorized workflow evolution.

Add/use:

```text
C09_ENTRY_SHA =
1fa841f2ee0d6612774c9f0ced204289df86e7a1
```

The guard must prove:

1. entry workflow tree and current workflow tree each contain exactly
   `.github/workflows/ci.yml`;
2. parse top-level workflow job blocks deterministically;
3. current job IDs equal entry job IDs plus exactly
   `w04-investigation-gate`;
4. every pre-existing job block except `verification-gate` is byte-identical to
   C09 entry;
5. therefore the measured 65m non-integration job, W03 gate, static/plan,
   integration, shards, aggregate, Quality, Compose and classifier are unchanged;
6. the new W04 gate block matches the exact authorized C09 contract;
7. current `verification-gate` equals the entry verification block transformed
   only by the exact W04 dependency/result/truth-table additions;
8. no trigger change;
9. no action-pin change;
10. no hidden second workflow file.

Do not broadly allow workflow differences.

The independent source-delta guard in
`verify_w04_investigation_gate_contract.py` must additionally prove that this R43
change and the bounded R46 changes are the only semantic edits to
`tests/test_investigation_replay.py`.

# 11. R46 exact-SHA native proof evolution

Keep existing selector names and parameter lists unchanged:

```text
test_r46_native_full_proof_gate_rejects_incomplete_or_wrong_sha_controls

test_r46_stage_b_exact_sha_full_native_ci
```

Do not add/remove/rename parameter values because that would change the 2997-node
collection.

Update only the exact R46 meta-CI symbols allowed by the replay-harness
source-delta guard.

Required changes:

1. add `W04 investigation gate` to the exact full-job set;
2. keep Publication proof skipped for full route;
3. require W04 gate metadata:

```text
implementation_sha = exact proof HEAD
gate_version = w04-c09-investigation-gate-v1
overall = PASS
families = 9
selectors = 67
tests = 81
manifest_content_sha256 =
937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad
summary_sha256 = valid canonical self-seal
```

4. existing W03 proof remains `38 selectors / 85 cases PASS`;
5. post-CI real-native proof expects the existing ten DEVCTRL artifacts plus:

```text
w04-c09-gate-<HEAD>
```

for exactly 11 artifacts;
6. verify the W04 gate artifact ZIP digest against GitHub metadata;
7. parse and validate the exact summary JSON;
8. recompute and validate `summary_sha256`;
9. recompute and record the raw SHA-256 of the summary file bytes;
10. retain DEVCTRL-03 planner validation, 2997 collection, 63 files,
    2994 passed / 3 accepted skipped and integration 70 proof.

Do not change the existing parameterized damage list. New W04-specific adversarial
metadata checks belong in `verify_w04_investigation_gate_contract.py` so the
pytest node set remains unchanged.

The C08 replay-harness source-delta verifier must prove that no unrelated R01-R46
test body changed.

# 12. Source-evolution boundary

`docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json` must remain byte-identical.

C09 is a development/CI proof-plane checkpoint and adds no
`src/flowlens/investigation/**` source.

Therefore:

```text
C01-C08 =
CLOSED

C09 source-evolution entry =
ABSENT BY DESIGN
```

Do not append an empty/fake C09 source checkpoint.

Do not modify C08 source freeze or any C01-C08 blob.

---

## Repair-01 normative amendment

Stage A is exactly 14 paths, with only tests/test_ci_change_classifier.py and tests/test_c09_ci_gate.py added to the original set. Their three exact existing functions may evolve only for the new W04 job, Verification needs/result and actual wrong-status matrix. AST/source-span guards preserve every other top-level unit, all names, signatures, decorators and parameter lists against C09 entry. C09_META_CI_DELTA_GUARD must PASS locally and in the new gate job. All source/node/weights/resilience/exact-SHA and Stage-B boundaries are unchanged. Full approved addendum and raw identity are materialized in W04_C09_AUTHORIZATION_CONTRACT.md.
