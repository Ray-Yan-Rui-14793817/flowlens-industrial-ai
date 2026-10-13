# W04-C09 — Authorization Contract

EFFECTIVE AUTHORITY: base V1.1 plus approved Repair-01. The effective Stage-A set is exactly 14 paths; the original 12-path text is preserved below as historical base-task content. Repair-01 changes only that scope and the corresponding meta-CI source-delta proof.

Current authorized task: V1.1 only. Raw task SHA-256: `a445ee4ec99a714dd7e53f162df3eccdc0f8ed9295c6a67a71cef308feba553b`. V1 is superseded and supplies no authority.

```text
checkpoint = W04-C09
title = W04 Regression Hardening
runtime capability change = NONE
source evolution entry = ABSENT BY DESIGN
gate = w04-c09-investigation-gate-v1
selectors/cases = 67 / 81
C10 = NOT AUTHORIZED
```

The following is the complete Human-authorized V1.1 task, preserved as normative contract content.

# FlowLens Industrial AI — W04-C09 Codex Development Task V1.1

## 0. Identity

```text
PROJECT:
FlowLens Industrial AI

CHECKPOINT:
W04-C09

TITLE:
W04 Regression Hardening / Investigation Semantic CI Gate

TASK:
W04-C09-I/H/R

TASK VERSION:
V1.1

REPOSITORY:
Ray-Yan-Rui-14793817/flowlens-industrial-ai

BRANCH:
feat/w04-evidence-investigation

PR:
#7

ENTRY HEAD:
1fa841f2ee0d6612774c9f0ced204289df86e7a1

ENTRY NATIVE CI:
#136 / 38360398379 / SUCCESS

ENTRY CLASS:
C / FULL_EXACT_SHA

MAIN / PR BASE:
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
```

This is a development/CI proof-plane checkpoint.

C09 adds **no new investigation runtime capability**.

C01-C08 product/runtime semantics are frozen.

W04-C10 is not authorized.

---

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

# 2. GPT architecture decision

The C09 design deliberately adds **zero new pytest node IDs**.

This is mandatory because W04-DEVCTRL-03 closed with an exact active scheduler
model of:

```text
2997 non-integration nodes
63 non-integration files

node digest:
9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a

weights digest:
a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851

plan schema:
w04-devctrl03-non-integration-plan-v1

shards:
7

timeout:
65m
```

Therefore C09 MUST NOT create a new pytest contract-test module.

The C09 runner and its independent adversarial contract verifier live under
`scripts/ci/`, outside pytest collection.

`tests/test_investigation_replay.py` may change only as an existing-node,
harness-only compatibility evolution for R43/R46. No selector or parameter
expansion may be added, removed or renamed.

If current pytest collection changes at all:

```text
W04_C09_NODESET_DRIFT
```

STOP.

## Required non-regression hardening added in V1.1

V1.1 closes two proof-quality gaps identified by independent GPT design review.

### A. Preserve DEVCTRL-03 resilience, not only its configuration

The C09 Stage-A native run must keep the accepted DEVCTRL-03 resilience target:

```text
max non-integration shard job duration < 3300s / 55m
max non-integration shard pytest duration < 3300s / 55m
```

The existing 65m timeout remains an emergency execution ceiling, not the
performance acceptance threshold.

A successful CI run that needs 55-65 minutes for any non-integration shard is
a C09 regression and must stop.

### B. Preserve the C08 replay proof bodies, not only the node set

The independent C09 contract verifier must compare
`tests/test_investigation_replay.py` against this exact C09 entry SHA:

```text
1fa841f2ee0d6612774c9f0ced204289df86e7a1
```

All unrelated top-level imports, assignments, functions, classes, decorators
and test bodies must remain source-identical.

Only the explicitly authorized R43/R46 meta-CI symbols may differ.

This turns:

```text
NODESET PRESERVED
```

into the stronger invariant:

```text
C08 PRODUCT SOURCE = UNCHANGED
C08 SEMANTIC TEST BODIES = UNCHANGED
C08 META-CI HARNESS = BOUNDED AUTHORIZED EVOLUTION
```

# 3. Frozen entry evidence

The C09 critical pack was independently derived from the successful #136 native
JUnit evidence at the entry SHA.

```text
NON-INTEGRATION:
2997 selected
2994 passed
3 accepted skipped
0 failed
0 error
0 xfail
0 xpass

NON-INTEGRATION JUNIT SHA-256:
65fc4dde578be989650d41e4bbe291ed3dd6502c6daceb427f3b17333418888d

INTEGRATION:
70 passed

INTEGRATION JUNIT SHA-256:
f76dcf2286467ba16ae40572ef8e8ccb27884e2a068fd65f3cb70643c394d6c8

SOURCE EVOLUTION MANIFEST SHA-256:
d22a12306f8fe98952b9e35a5f166f29fee968c9aedcff27511da59889c20c2d
```

The critical C09 pack freezes:

```text
families:
9

selectors:
67

expanded cases:
81
```

Measured #136 testcase-time sum for the selected critical pack:

```text
706.974 seconds
~11m47s testcase time
```

The C09 gate job timeout is therefore fixed at:

```text
30 minutes
```

This does not authorize changing any existing timeout.

---

## DEVCTRL-03 accepted resilience baseline

The latest closed DEVCTRL-03 proof is #136 / 38360398379 at the C09 entry.

Observed #136 non-integration shard job durations:

```text
shard 0 = 1934s
shard 1 = 824s
shard 2 = 858s
shard 3 = 687s
shard 4 = 1101s
shard 5 = 1699s
shard 6 = 1598s

longest = 1934s / 32m14s
```

C09 does not require matching or improving those individual values. GitHub-hosted
runner variance is expected.

C09 does require preserving the accepted resilience class:

```text
every non-integration shard job < 3300s
every non-integration shard pytest suite < 3300s
```

No re-weight, timeout increase, shard split or node-level sharding is authorized
by C09 if this target is missed.


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

# 13. Stage-A exact allowlist

Exactly these 12 paths may change/create:

```text
.github/workflows/ci.yml

scripts/ci/run_w04_investigation_gate.py
scripts/ci/verify_w04_investigation_gate_contract.py

tests/test_investigation_replay.py

docs/w04/checkpoints/c09/W04_C09_AUTHORIZATION_CONTRACT.md
docs/w04/checkpoints/c09/W04_C09_HUMAN_AUTHORIZATION.md
docs/w04/checkpoints/c09/W04_C09_CONTEXT_LOCK.md
docs/w04/checkpoints/c09/W04_C09_CI_REGRESSION_CONTRACT.md
docs/w04/checkpoints/c09/W04_C09_HARNESS_SPEC.md
docs/w04/checkpoints/c09/W04_C09_GPT_REVIEW_CHECKLIST.md
docs/w04/checkpoints/c09/specs/c09_gate_manifest.json
docs/w04/checkpoints/c09/specs/authorized_paths.json
```

A 13th path requires:

```text
W04_C09_SCOPE_VIOLATION
```

STOP.

---

# 14. Frozen / forbidden surfaces

Do not modify:

```text
src/**
migrations/**
apps/**
pyproject.toml
uv.lock
docker-compose.yml

scripts/ci/classify_change.py
scripts/ci/verify_publication.py
scripts/ci/plan_non_integration_shards.py
scripts/ci/pytest_outcome_receipt.py
scripts/ci/run_non_integration_shard.py
scripts/ci/verify_non_integration_shards.py
scripts/ci/run_w03_ai_loop_gate.py
scripts/ci/verify_w04_source_evolution.py

docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c01/**
docs/w04/checkpoints/c02/**
docs/w04/checkpoints/c03/**
docs/w04/checkpoints/c04/**
docs/w04/checkpoints/c05/**
docs/w04/checkpoints/c06/**
docs/w04/checkpoints/c07/**
docs/w04/checkpoints/c08/**
docs/w04/devctrl/**
docs/w04/devctrl-02/**
docs/w04/devctrl-03/**

docs/w03/**
```

No dependency/action/image/model/provider/schema/migration change.

No live OpenAI call.

No secret use.

No HGT runtime access.

No operational mutation.

No C10 work.

No PR ready/merge/main write/branch deletion.

---

# 15. Governance documents

## `W04_C09_AUTHORIZATION_CONTRACT.md`

Materialize this frozen C09 architecture and authority boundary.

Required:

```text
checkpoint = W04-C09
title = W04 Regression Hardening
runtime capability change = NONE
source evolution entry = ABSENT BY DESIGN
gate = w04-c09-investigation-gate-v1
selectors/cases = 67 / 81
C10 = NOT AUTHORIZED
```

## `W04_C09_HUMAN_AUTHORIZATION.md`

Record the actual Human prompt authorizing this V1.1 implementation.

Do not invent acceptance or closeout.

## `W04_C09_CONTEXT_LOCK.md`

Record fresh entry identities before mutation:

```text
all four feature heads
PR state
main/base
clean tree/index
ahead/behind
#136 identity
workflow/planner/weights blobs
source-evolution manifest blob/hash
C01-C08 source blobs
2997 node digest
63-file digest
exact Stage-A allowlist
hard stops
```

## `W04_C09_CI_REGRESSION_CONTRACT.md`

Record Sections 1, 4-12 as normative implementation behavior.

## `W04_C09_HARNESS_SPEC.md`

Map every semantic family plus workflow/harness safety controls to
detection + enforcement + evidence.

## `W04_C09_GPT_REVIEW_CHECKLIST.md`

Require independent post-implementation review of:

```text
exact SHA/run
67/81 manifest identity
per-family PASS
no selector/count drift
new job exact scheduling
verification conjunction
W03 gate unchanged
2997/63 DEVCTRL-03 preservation
R43/R46 bounded harness evolution
C01-C08 source/blob freeze
manifest byte identity
no runtime/dependency/schema/provider/HGT/operational change
Stage-B report-only publication
C10 absent
```

## `authorized_paths.json`

Freeze exact Stage-A and Stage-B path sets.

---

# 16. Preflight

Before repository write, fresh-fetch and require:

```text
local HEAD ==
tracking feature HEAD ==
direct origin feature HEAD ==
PR #7 HEAD ==
1fa841f2ee0d6612774c9f0ced204289df86e7a1

branch =
feat/w04-evidence-investigation

PR #7 =
OPEN / DRAFT / UNMERGED

main/base =
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

ahead/behind =
0/0

worktree/index =
CLEAN

latest feature CI =
#136 / 38360398379 / SUCCESS

classifier =
C / FULL_EXACT_SHA
```

Require:

```text
C01-C08 CLOSED
C09 source entry absent
C10 absent
```

Require DEVCTRL-03 current settings:

```text
weights ACTIVE
weights digest =
a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851

2997 nodes
63 files
7 shards
65m
max-parallel 7
fail-fast false
```

If any fact differs:

```text
W04_C09_CONTEXT_CHANGED
```

STOP.

---

# 17. Human implementation gate

Do not mutate repository until the active Human request contains exactly:

```text
W04-C09 HUMAN AUTHORIZATION: APPROVED
```

The prompt may additionally bind this task SHA.

This authorization is for C09 implementation/evidence only.

It is not C09 Human acceptance and not closeout authority.

---

# 18. Baseline selector proof before mutation

Before any write, verify Appendix A against exact entry HEAD.

Using exact #136 artifacts or a fresh entry checkout, require:

```text
67 exact selectors exist
81 expanded cases exactly
no selected leaf skipped/xfail/xpass/failed/error in #136
```

Require the family totals in Section 4.

Require selected #136 testcase-time sum:

```text
706.974s
```

If selectors/counts differ:

```text
W04_C09_SELECTOR_BASELINE_MISMATCH
```

STOP.

Do not silently choose replacement selectors.

---

# 19. Local implementation proof

Before Stage-A commit:

1. verify manifest raw SHA and canonical content SHA;
2. run the independent contract verifier;
3. require its C08 replay-harness source-delta guard PASS;
4. run the C09 gate against exact current HEAD using a test PostgreSQL database;
5. require nine independent family subprocesses;
6. require 9/9 family PASS, 67 selectors, 81 cases;
7. verify the generated gate summary canonical self-seal;
8. record the local raw SHA-256 of the summary bytes;
9. run R43;
10. run both R46 selectors in fixture/control mode;
11. run full `tests/test_investigation_replay.py`;
12. run `tests/test_w04_source_evolution.py`;
13. run `tests/test_ci_test_sharding.py`;
14. run Ruff;
15. run strict mypy;
16. run dependency lock check;
17. run active planner and require:
    - 2997 nodes,
    - same node digest,
    - 63 files,
    - same measured weights,
    - same seven-shard plan contract;
18. verify `tests/test_investigation_replay.py` node IDs and parameter expansion
    are byte-for-byte/collection-identical to entry;
19. `git diff --check` PASS;
20. exact changed paths <= 12-path Stage-A allowlist.

No pytest node addition/removal/rename is permitted.

No unrelated C08 replay-test body change is permitted.

# 20. Stage-A implementation commit

Exact subject:

```text
ci(w04-c09): add investigation regression gate
```

One normal commit.

One normal push.

No amend/rebase/reset/force push/history rewrite.

Expected classifier:

```text
I / FULL_EXACT_SHA
```

because `tests/test_investigation_replay.py` changes.

Native classifier is authoritative.

---

# 21. Stage-A exact-SHA CI acceptance

Require Stage-A SHA's own terminal native SUCCESS.

Required jobs:

```text
Classify change
Static and plan
Integration and data
Non-integration / shard 0
Non-integration / shard 1
Non-integration / shard 2
Non-integration / shard 3
Non-integration / shard 4
Non-integration / shard 5
Non-integration / shard 6
Non-integration aggregate
Quality gate
Docker Compose smoke
W03 AI loop gate
W04 investigation gate
Verification gate
```

Publication proof must be SKIPPED.

Require full outcome envelope:

```text
2997 selected
2994 passed
3 accepted skipped
0 failed/error/xfail/xpass

entry no-loss PASS
exact union PASS
exact once PASS

integration 70 passed

W03:
38 selectors / 85 cases PASS

W04 C09 gate:
9 families
67 selectors
81 cases
PASS
summary self-seal PASS
```

Require exact W04 gate artifact:

```text
w04-c09-gate-<STAGE_A_SHA>
```

and exact summary content identities.

## DEVCTRL-03 resilience non-regression

After Stage-A terminal SUCCESS, calculate exact native durations before allowing
Stage B.

From GitHub job timestamps capture all seven:

```text
ACTUAL_SHARD_JOB_SECONDS[0..6]
```

From the seven native shard JUnit artifacts capture all seven exact pytest suite
durations:

```text
ACTUAL_SHARD_PYTEST_SECONDS[0..6]
```

Require:

```text
max(ACTUAL_SHARD_JOB_SECONDS) < 3300
max(ACTUAL_SHARD_PYTEST_SECONDS) < 3300
```

Also report:

```text
LONGEST_SHARD_JOB
LONGEST_SHARD_PYTEST
HEADROOM_TO_55M
HEADROOM_TO_65M
```

The accepted rule is:

```text
55m = resilience performance threshold
65m = execution timeout ceiling
```

A native run can be terminal SUCCESS and still fail C09 acceptance if a shard
is between 55m and 65m.

If either 55m threshold is missed:

```text
W04_C09_DEVCTRL03_RESILIENCE_REGRESSION
```

STOP.

Do not automatically re-weight, increase timeout, change shard count, split test
files or introduce node-level sharding.

If Stage-A native CI itself fails:

```text
W04_C09_STAGE_A_CI_FAILED
```

STOP.

No automatic post-push repair.

# 22. Post-CI real-native R46 proof

After Stage-A CI terminal SUCCESS **and** the DEVCTRL-03 resilience
non-regression check passes:

1. fetch the actual Stage-A run metadata/jobs;
2. download all original native artifacts;
3. download `w04-c09-gate-<STAGE_A_SHA>`;
4. verify its GitHub artifact ZIP digest;
5. parse exact gate summary bytes;
6. verify `summary_sha256`;
7. record the raw summary-file SHA-256;
8. construct exact GitHub-native proof metadata;
9. rerun:

```text
test_r46_stage_b_exact_sha_full_native_ci
```

with real native evidence enabled.

Require PASS.

Require artifact count exactly:

```text
11
```

and the W04 gate summary exact.

Require the C08 replay-harness source-delta guard still PASS at the Stage-A SHA.

If it fails:

```text
W04_C09_R46_NATIVE_PROOF_FAILED
```

STOP.

# 23. Stage-B development report

Only after Stage-A native SUCCESS, DEVCTRL-03 resilience PASS and
real-native R46 PASS, create exactly:

```text
docs/w04/checkpoints/c09/W04_C09_R_DEVELOPMENT_ROUND_REPORT.md
```

No other path.

Report:

```text
entry SHA/run
Stage-A SHA/run/class
exact changed paths
manifest raw/canonical hashes
9 family summary
67 selectors / 81 cases
nine-family subprocess isolation PASS
W04 gate artifact identity
W04 gate summary self-seal
W04 gate summary raw SHA-256
W03 38/85
2997/2994/3
integration 70
R43 PASS
C08 replay-harness source-delta guard PASS
real-native R46 PASS
DEVCTRL-03 collection/weights unchanged
actual shard job seconds 0..6
actual shard pytest seconds 0..6
longest shard job
longest shard pytest
headroom to 55m
headroom to 65m
DEVCTRL-03 resilience target <55m PASS
C01-C08 source/blob freeze
source-evolution manifest byte identity
no runtime/source/dependency/schema/provider/HGT/operational change
known limitations
GPT reviewer questions
C10 NOT AUTHORIZED
```

Required known limitations:

```text
critical semantic pack is intentionally a subset of the full suite
C09 duplicates selected accepted tests as an explicit semantic proof
no new pytest nodes were admitted
artifact retention is bounded by GitHub retention
GitHub-hosted runner timing variance remains
the <55m rule protects the accepted resilience class but is not a deterministic performance guarantee
C09 does not prove production UI/usability or business acceptance
C10 remains separate
```

Exact subject:

```text
docs(w04-c09): publish regression-hardening proof
```

One normal commit/push.

Expected route:

```text
P / PUBLICATION_EXACT_SHA
```

Native classifier authoritative.

Require:

```text
Classify SUCCESS
Publication SUCCESS
Verification SUCCESS

heavy/full jobs SKIPPED
W03 AI loop gate SKIPPED
W04 investigation gate SKIPPED
```

# 24. Terminal state

After Stage-B native SUCCESS and fresh synchronization, report:

```text
W04_C09_REVIEW_READY
```

Required state:

```text
C09 IMPLEMENTATION = COMPLETE
C09 HARNESS = PASS
C09 NATIVE CI = PASS
C09 REAL-NATIVE R46 = PASS
C09 C08-HARNESS DELTA GUARD = PASS
C09 DEVCTRL-03 RESILIENCE = PASS

GPT INDEPENDENT REVIEW = PENDING
HUMAN C09 ACCEPTANCE = PENDING
C09 CLOSEOUT = NOT AUTHORIZED

C01-C08 SOURCE EVOLUTION = CLOSED / UNCHANGED
C09 SOURCE EVOLUTION ENTRY = ABSENT BY DESIGN

DEVCTRL-03 =
2997 nodes / 63 files / measured weights unchanged /
7 shards / 65m ceiling / <55m resilience target preserved

W04-C10 = NOT AUTHORIZED

PR #7 = OPEN / DRAFT / UNMERGED
PR MERGE = NOT AUTHORIZED
BRANCH DELETION = NOT AUTHORIZED
MAIN WRITE = NOT AUTHORIZED
```

STOP.

Do not begin C10.

# 25. Hard stops

```text
W04_C09_CONTEXT_CHANGED
W04_C09_HUMAN_AUTHORIZATION_REQUIRED
W04_C09_SELECTOR_BASELINE_MISMATCH
W04_C09_NODESET_DRIFT
W04_C09_SCOPE_VIOLATION
W04_C09_PROTECTED_OBJECT_DRIFT
W04_C09_GATE_CONTRACT_FAILED
W04_C09_C08_HARNESS_DELTA_VIOLATION
W04_C09_STAGE_A_CI_FAILED
W04_C09_DEVCTRL03_RESILIENCE_REGRESSION
W04_C09_R46_NATIVE_PROOF_FAILED
W04_C09_STAGE_B_CI_FAILED
W04_C09_SYNC_FAILED
W04_C09_REQUIRES_GPT_CLARIFICATION
```

Any requirement for runtime source change, new test node admission, dependency,
migration, provider/model behavior, source-manifest mutation, unrelated C08
replay-test body mutation, DEVCTRL-03 re-weight/timeout/topology change or C10
behavior is a contract conflict.

Stop rather than infer authority.

# 26. Required final Codex handoff

```text
W04_C09_REVIEW_READY

TASK_VERSION:
V1.1

ENTRY_HEAD:
1fa841f2ee0d6612774c9f0ced204289df86e7a1

ENTRY_CI:
#136 / 38360398379 / SUCCESS

STAGE_A_SHA:
<actual>

STAGE_A_CI:
#<number> / <id> / SUCCESS

STAGE_A_CLASS:
<actual>

W04_GATE:
w04-c09-investigation-gate-v1

MANIFEST_RAW_SHA256:
d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1

MANIFEST_CONTENT_SHA256:
937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad

FAMILIES:
9 / 9 PASS

SELECTORS_CASES:
67 / 81 PASS

FAMILY_SUBPROCESS_ISOLATION:
PASS

W04_GATE_ARTIFACT:
w04-c09-gate-<STAGE_A_SHA>

W04_GATE_SUMMARY_SELF_SEAL:
<actual>

W04_GATE_SUMMARY_RAW_SHA256:
<actual>

NONINTEGRATION:
2997 selected
2994 passed
3 accepted skipped
0 failed/error/xfail/xpass
entry no-loss PASS
exact union PASS
exact once PASS

ACTUAL_SHARD_JOB_SECONDS:
<0..6>

ACTUAL_SHARD_PYTEST_SECONDS:
<0..6>

LONGEST_SHARD_JOB:
<actual>

LONGEST_SHARD_PYTEST:
<actual>

HEADROOM_TO_55M:
<actual>

HEADROOM_TO_65M:
<actual>

DEVCTRL03_RESILIENCE_LT_55M:
PASS

INTEGRATION:
70 passed

W03:
38 selectors / 85 cases PASS

R43:
PASS

C08_REPLAY_HARNESS_DELTA_GUARD:
PASS

REAL_NATIVE_R46:
PASS

DEVCTRL_03:
2997 nodes / 63 files
weights unchanged
7 shards
65m ceiling
<55m resilience preserved

SOURCE_EVOLUTION:
C01-C08 CLOSED / unchanged
C09 entry absent by design
manifest byte-identical

PRODUCT_RUNTIME_CHANGE:
NONE

STAGE_B_SHA:
<actual>

STAGE_B_CI:
#<number> / <id> / SUCCESS

STAGE_B_CLASS:
<actual>

FINAL_SYNC:
local/tracking/direct-origin/PR = Stage-B SHA
ahead/behind 0/0
worktree/index CLEAN

GPT_INDEPENDENT_REVIEW:
PENDING

HUMAN_C09_ACCEPTANCE:
PENDING

C09_CLOSEOUT:
NOT AUTHORIZED

W04_C10:
NOT AUTHORIZED

PR #7:
OPEN / DRAFT / UNMERGED

PR_MERGE / BRANCH_DELETION / MAIN_WRITE:
NOT AUTHORIZED
```

Stop and return this handoff for independent ChatGPT review.

# Appendix A — Exact `c09_gate_manifest.json`

```json
{
  "schema_version": "w04-c09-regression-manifest-v1",
  "gate_version": "w04-c09-investigation-gate-v1",
  "checkpoint": "W04-C09",
  "contract_entry_sha": "1fa841f2ee0d6612774c9f0ced204289df86e7a1",
  "selector_semantics": "EXACT_FUNCTION_SELECTOR_WITH_FROZEN_EXPANDED_CASE_COUNT",
  "baseline": {
    "run_number": 136,
    "run_id": 38360398379,
    "nonintegration_node_count": 2997,
    "nonintegration_nodeids_sha256": "9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a",
    "nonintegration_file_count": 63,
    "nonintegration_junit_sha256": "65fc4dde578be989650d41e4bbe291ed3dd6502c6daceb427f3b17333418888d",
    "integration_case_count": 70,
    "integration_junit_sha256": "f76dcf2286467ba16ae40572ef8e8ccb27884e2a068fd65f3cb70643c394d6c8",
    "source_evolution_manifest_sha256": "d22a12306f8fe98952b9e35a5f166f29fee968c9aedcff27511da59889c20c2d",
    "devctrl03_weights_sha256": "a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851",
    "devctrl03_plan_schema": "w04-devctrl03-non-integration-plan-v1",
    "nonintegration_timeout_minutes": 65,
    "shard_count": 7
  },
  "total_selectors": 67,
  "total_cases": 81,
  "families": [
    {
      "id": "F01 C01_CONTRACTS_IDENTITY",
      "expected_cases": 6,
      "targets": [
        {
          "selector": "tests/test_investigation_contracts.py::test_h15_case_cannot_open_before_decision_time",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_contracts.py::test_h23_evidence_availability_is_bounded_by_as_of",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_contracts.py::test_h29_unknown_requires_uncertainty_and_unresolved_requires_basis",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_contracts.py::test_h36_no_transitive_db_network_model_tool_or_hgt_capability_imports",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_contracts.py::test_h37_exact_w03_trust_and_serialization_framework_reused",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_contracts.py::test_h40_contract_construction_and_parse_perform_no_external_io",
          "expected_cases": 1
        }
      ]
    },
    {
      "id": "F02 C02_CASE_BINDING_TEMPORAL",
      "expected_cases": 6,
      "targets": [
        {
          "selector": "tests/test_investigation_case_binding.py::test_b03_b10_b17_b18_exact_projection_and_public_constants",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_case_binding.py::test_b04_hashes_complete_packet_including_provenance_excluded_from_packet_id",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_case_binding.py::test_b22_future_evidence_observation_survives_w03_and_fails_c02",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_case_binding.py::test_b33_c01_case_wire_identity_and_immutability_remain_exact",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_case_binding.py::test_b34_runtime_imports_and_ast_have_no_external_or_execution_capabilities",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_case_binding.py::test_b36_c01_frozen_blobs_and_committed_source_governance_pass",
          "expected_cases": 1
        }
      ]
    },
    {
      "id": "F03 C03_PLANNING_DETERMINISM",
      "expected_cases": 6,
      "targets": [
        {
          "selector": "tests/test_investigation_planning.py::test_p04_missing_family_passes_inherited_boundary_but_fails_semantics",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_planning.py::test_p11_supporting_signals_are_all_eight_not_only_active",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_planning.py::test_p14_p15_unrelated_inherited_uncertainties_are_preserved",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_planning.py::test_p32_p33_p34_p35_exact_dependency_free_plan_projection",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_planning.py::test_p23_p39_forbidden_inference_question_cannot_be_constructed_or_submitted",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_planning.py::test_p40_runtime_ast_and_fresh_import_have_no_execution_capabilities",
          "expected_cases": 1
        }
      ]
    },
    {
      "id": "F04 C04_AUTHORIZED_NAVIGATION_READ_ONLY",
      "expected_cases": 14,
      "targets": [
        {
          "selector": "tests/test_investigation_evidence_queries.py::test_n04_n06_exact_immutable_registry_and_field_partition",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_evidence_queries.py::test_n07_n13_n14_exact_projection_count_and_order",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_evidence_queries.py::test_n13_zero_step_plan_has_zero_queries",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_evidence_queries.py::test_n18_no_query_language_or_resource_arguments",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_evidence_navigation.py::test_n39_future_plans_remain_known_values",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_evidence_navigation.py::test_n46_duplicate_joins_and_row_order_do_not_change_evidence",
          "expected_cases": 1
        },
        {
          "selector": "tests/integration/test_investigation_evidence_navigation_database.py::test_n19_n24_n32_n43_n51_all_adapters_native_replay_and_zero_mutation",
          "expected_cases": 1
        },
        {
          "selector": "tests/integration/test_investigation_evidence_navigation_database.py::test_n35_n37_actual_future_values_are_sql_masked_and_not_emitted",
          "expected_cases": 6
        },
        {
          "selector": "tests/integration/test_investigation_evidence_navigation_database.py::test_n21_native_hash_context_failure_is_read_only",
          "expected_cases": 1
        }
      ]
    },
    {
      "id": "F05 C05_FINDINGS_CONFLICT_UNCERTAINTY",
      "expected_cases": 7,
      "targets": [
        {
          "selector": "tests/test_investigation_findings.py::test_k12_same_process_determinism_and_immutability",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_findings.py::test_k15_actual_c04_typed_and_wire_parity",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_findings.py::test_k17_empty_evidence_never_negative_proof",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_findings.py::test_k20_association_never_causal",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_findings.py::test_k38_support_contradiction_conflict",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_findings.py::test_k41_forbidden_codes_preserved_exactly",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_findings.py::test_k47_runtime_ast_and_fresh_import",
          "expected_cases": 1
        }
      ]
    },
    {
      "id": "F06 C06_HUMAN_AUTHORITY_AUDIT",
      "expected_cases": 10,
      "targets": [
        {
          "selector": "tests/test_investigation_human.py::test_j02_frozen_schema_vocabulary_versions_and_errors",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_human.py::test_j12_note_class_is_fixed_and_tamper_rejected",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_human.py::test_j14_supported_outcome_requires_reviewed_supported_finding",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_human.py::test_j15_no_supported_requires_global_complete_review_without_support",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_human.py::test_j21_first_none_later_exact_parent_and_wrong_parent_rejected",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_human.py::test_j23_deterministic_multievent_chain_preserves_originals",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_human_store.py::test_j29_three_event_chain_preserves_all_prior_bytes",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_human_store.py::test_j41_busy_lock_rejects_immediately_and_preserves_operator_state",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_human_store.py::test_j44_public_journal_surface_has_no_history_edit_or_parent_override",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_human_store.py::test_j46_j47_store_runtime_ast_and_fresh_import_isolation",
          "expected_cases": 1
        }
      ]
    },
    {
      "id": "F07 C07_SUMMARY_GROUNDING",
      "expected_cases": 10,
      "targets": [
        {
          "selector": "tests/test_investigation_summary.py::test_s05_s13_frozen_six_sections_and_deterministic_authority",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_summary.py::test_s10_s18_uncertainty_preserves_every_type_and_forbidden_inference",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_summary.py::test_s11_latest_human_metadata_is_chain_tail_without_authority_upgrade",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_summary.py::test_s14_s15_zero_conflicts_and_uncertainty_are_explicit",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_summary.py::test_s51_frozen_versions_prompt_bytes_schema_and_error_vocabulary",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_summary_provider.py::test_s38_provider_receives_only_exact_deterministic_baseline_section_data",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_summary_provider.py::test_s41_absent_provider_and_explicit_fallback_do_not_call_transport",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_summary_provider.py::test_s46_existing_number_and_time_cannot_be_rebound_to_another_field",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_summary_provider.py::test_s49_unexpected_validation_error_degrades_without_second_call",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_summary_provider.py::test_s51_actual_transport_source_has_only_bounded_sdk_and_single_auth_read",
          "expected_cases": 1
        }
      ]
    },
    {
      "id": "F08 C08_PROTECTED_REPLAY",
      "expected_cases": 17,
      "targets": [
        {
          "selector": "tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_replay.py::test_r11_r16_receipt_versions_source_core_id_and_full_hash",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_replay.py::test_r20_coherent_presentation_claim_still_recomputes_supplied_chain",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_replay.py::test_r36_every_public_stage_failure_suppresses_protected_upstream_text",
          "expected_cases": 10
        },
        {
          "selector": "tests/test_investigation_replay.py::test_r37_r39_same_process_bytes_and_all_inputs_unchanged",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_replay.py::test_r40_r41_runtime_ast_public_signature_and_fresh_import_are_protected",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_replay.py::test_r39_r40_r42_live_external_traps_no_refresh_or_operational_mutation",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_investigation_replay.py::test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged",
          "expected_cases": 1
        }
      ]
    },
    {
      "id": "F09 SOURCE_EVOLUTION_GOVERNANCE",
      "expected_cases": 5,
      "targets": [
        {
          "selector": "tests/test_w04_source_evolution.py::test_d12_previous_closed_freeze_is_immutable",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_w04_source_evolution.py::test_d14_authorized_to_closed_transition_passes_once",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_w04_source_evolution.py::test_d17_new_checkpoint_must_begin_authorized",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_w04_source_evolution.py::test_d26_output_is_deterministic_and_sorted",
          "expected_cases": 1
        },
        {
          "selector": "tests/test_w04_source_evolution.py::test_d26_cli_outputs_same_deterministic_json_and_fails_closed",
          "expected_cases": 1
        }
      ]
    }
  ]
}
```

# Approved Repair-01 addendum

Actual Human Repair-01 authorization is recorded in W04_C09_HUMAN_AUTHORIZATION.md. Addendum raw SHA-256: `744640783621660de009a8a1656ebb55bf752802ecb7e8256b8a1d9a8f3ee0ef`. This addendum overrides only the Stage-A path authorization and corresponding meta-CI source-delta proof. All other base V1.1 requirements remain unchanged. The following is the complete approved addendum.

# FlowLens Industrial AI — W04-C09 Repair-01 Clarification & Authorization Addendum

## 0. Identity

PROJECT: FlowLens Industrial AI
CHECKPOINT: W04-C09 — Regression Hardening / Investigation Semantic CI Gate
BASE TASK: `FLOWLENS_W04_C09_CODEX_DEVELOPMENT_TASK_V1_1.md`
BASE TASK SHA-256: `a445ee4ec99a714dd7e53f162df3eccdc0f8ed9295c6a67a71cef308feba553b`
ADDENDUM: Repair-01
REPOSITORY: `Ray-Yan-Rui-14793817/flowlens-industrial-ai`
BRANCH: `feat/w04-evidence-investigation`
PR: `#7`
C09 ENTRY HEAD: `1fa841f2ee0d6612774c9f0ced204289df86e7a1`

This addendum does not supersede V1.1 as a whole.

It changes only the Stage-A path authorization and the corresponding meta-CI
source-delta proof described below.

All other V1.1 requirements, hard stops, exact-SHA proof, resilience threshold,
R43/R46 controls, Stage-A/Stage-B sequencing, C10 prohibition, PR/main
boundaries and closeout boundaries remain authoritative.

---

## 1. GPT clarification result

Result:

`W04_C09_REPAIR_01_GPT_CLARIFICATION = APPROVED_FOR_HUMAN_AUTHORIZATION`

Reason:

The proposed W04-C09 workflow intentionally adds a new required job
`w04-investigation-gate` and extends the final Verification conjunction.

Two pre-existing meta-CI regression files contain frozen assertions about the
pre-C09 workflow topology:

1. `tests/test_ci_change_classifier.py`
2. `tests/test_c09_ci_gate.py`

The observed three failures are expected compatibility failures of those
meta-CI assertions, not product/runtime failures and not evidence that the C09
semantic-gate implementation is invalid.

The repair is necessary so the historical meta-CI proofs assert the new
authorized topology rather than the old topology.

This repair MUST NOT weaken those files generally.

---

## 2. Exact additional Stage-A paths

V1.1 Stage-A changes from 12 authorized paths to exactly 14.

Add only:

```text
tests/test_ci_change_classifier.py
tests/test_c09_ci_gate.py
```

No 15th Stage-A path is authorized.

The Stage-A allowlist in:

```text
docs/w04/checkpoints/c09/specs/authorized_paths.json
scripts/ci/verify_w04_investigation_gate_contract.py
```

must be updated from 12 to 14 consistently.

Any other path remains a scope violation.

---

## 3. Exact allowed test-function deltas

### 3.1 `tests/test_ci_change_classifier.py`

Only this existing test function may change:

```text
test_workflow_routes_all_classes_to_a_stable_fail_closed_gate
```

Required semantic update:

- preserve all existing assertions;
- update the frozen Verification `needs:` expectation so it includes exactly
  `w04-investigation-gate` in the authorized final dependency list;
- do not rename the function;
- do not parameterize it;
- do not add/remove pytest nodes;
- do not weaken classifier/path/publication assertions.

Every other top-level unit in this file must remain source-identical to the C09
entry SHA.

### 3.2 `tests/test_c09_ci_gate.py`

Only these two existing test functions may change:

```text
test_workflow_one_job_exact_schedule_source_manifest_and_environment
test_verification_runs_actual_shell_truth_table
```

Required semantic updates:

#### A. `test_workflow_one_job_exact_schedule_source_manifest_and_environment`

- preserve the existing W03 job proof;
- update the exact workflow job-set expectation to include exactly
  `w04-investigation-gate`;
- do not remove any previously required job;
- do not rename the test;
- do not add parameterization;
- do not weaken the W03 job assertions.

#### B. `test_verification_runs_actual_shell_truth_table`

- extend the exact Verification `needs:` expectation with
  `w04-investigation-gate`;
- require exact `W04_RESULT` binding from
  `needs['w04-investigation-gate'].result`;
- for `P`, require W04 result `skipped`;
- for every non-`P` full route, require W04 result `success`;
- include `W04_RESULT` in the adversarial wrong-status truth-table matrix;
- preserve all existing checks for Classify, Static, Integration,
  Non-integration, Quality, Compose, W03 and Publication;
- do not rename or parameterize the test.

Every other top-level unit in this file must remain source-identical to the C09
entry SHA.

---

## 4. New meta-CI source-delta guard

Extend:

```text
scripts/ci/verify_w04_investigation_gate_contract.py
```

with source-delta guards for both newly authorized test files.

Use the same structural principle as the existing replay-harness guard:

```text
entry source = git show <C09_ENTRY_SHA>:<path>
current source = working tree / Stage-A source
parse with ast
compare top-level source spans
do not rely on line numbers
```

For `tests/test_ci_change_classifier.py`, authorized top-level delta set is
exactly:

```text
test_workflow_routes_all_classes_to_a_stable_fail_closed_gate
```

For `tests/test_c09_ci_gate.py`, authorized top-level delta set is exactly:

```text
test_workflow_one_job_exact_schedule_source_manifest_and_environment
test_verification_runs_actual_shell_truth_table
```

All imports, module docstrings, module assignments, fixtures, helper functions,
other tests, decorators and parameter lists must remain entry-identical.

The verifier must include negative controls proving an unrelated function body,
import, decorator, parameter list, function name or new test cannot be changed
without failure.

Required proof state:

```text
C09_META_CI_DELTA_GUARD = PASS
```

---

## 5. Node-set and DEVCTRL-03 constraints

This Repair-01 authorizes source-body changes only.

It authorizes:

```text
0 new pytest nodes
0 removed pytest nodes
0 renamed pytest nodes
0 parameter-expansion changes
```

After Repair-01, still require:

```text
2997 non-integration nodes
63 non-integration files

node digest =
9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a

weights digest =
a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851

plan schema =
w04-devctrl03-non-integration-plan-v1

shards =
7

timeout ceiling =
65m

Stage-A resilience acceptance =
every shard job <55m
every shard pytest <55m
```

If the node digest or parameter expansion changes:

`W04_C09_NODESET_DRIFT`

STOP.

---

## 6. Forbidden repair behavior

Repair-01 does NOT authorize changes to:

```text
scripts/ci/classify_change.py
scripts/ci/run_w03_ai_loop_gate.py
scripts/ci/verify_publication.py
scripts/ci/plan_non_integration_shards.py
src/**
apps/**
migrations/**
pyproject.toml
uv.lock
docker-compose.yml
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c01/**
docs/w04/checkpoints/c02/**
docs/w04/checkpoints/c03/**
docs/w04/checkpoints/c04/**
docs/w04/checkpoints/c05/**
docs/w04/checkpoints/c06/**
docs/w04/checkpoints/c07/**
docs/w04/checkpoints/c08/**
docs/w04/devctrl/**
docs/w04/devctrl-02/**
docs/w04/devctrl-03/**
docs/w03/**
```

Do not change W03 semantic gate behavior.

Do not change the classifier to make these tests pass.

Do not delete or skip the failing meta-CI tests.

Do not replace exact assertions with permissive membership checks where the
contract requires an exact set or exact truth table.

Do not use `xfail`, `skip`, marker filtering or deselection as repair.

---

## 7. Required repair proof before Stage-A commit

After the three bounded test-body updates, require:

```text
test_workflow_routes_all_classes_to_a_stable_fail_closed_gate = PASS

test_workflow_one_job_exact_schedule_source_manifest_and_environment = PASS

test_verification_runs_actual_shell_truth_table = PASS

C09_META_CI_DELTA_GUARD = PASS

C08_REPLAY_HARNESS_DELTA_GUARD = PASS
```

Then rerun every V1.1 local proof, including:

```text
independent C09 contract verifier PASS
9 isolated family subprocesses PASS
9/9 semantic families PASS
67 selectors / 81 cases PASS
summary self-seal PASS
R43 PASS
R46 fixture/control PASS
full tests/test_investigation_replay.py PASS
tests/test_w04_source_evolution.py PASS
tests/test_ci_test_sharding.py PASS
Ruff PASS
strict mypy PASS
dependency lock PASS
active planner 2997 nodes / 63 files / same digest / same weights / 7 shards
git diff --check PASS
```

Also require the relevant complete meta-CI files to pass:

```text
tests/test_ci_change_classifier.py PASS
tests/test_c09_ci_gate.py PASS
```

No Stage-A commit/push may occur before all required local proof is green.

---

## 8. Human repair authorization gate

Do not make the two newly authorized file changes until the Human supplies:

```text
W04-C09 REPAIR-01 HUMAN AUTHORIZATION: APPROVED
```

This authorization allows only the exact two added paths and three existing
test-function deltas described in this addendum.

It does not authorize C09 acceptance, C09 closeout, C10, PR merge, branch
deletion or main write.

---

## 9. Stage-A continuation

After Human Repair-01 authorization and successful local proof, continue the
existing V1.1 Stage-A sequence.

The Stage-A commit subject remains unchanged:

```text
ci(w04-c09): add investigation regression gate
```

There is still exactly one Stage-A implementation commit and one normal push.

The expected native route remains:

```text
I / FULL_EXACT_SHA
```

The 14-path authorization does not change Stage-B.

---

## 10. Terminal interpretation

This repair does not reset C09 and does not create a new checkpoint.

It is a bounded clarification of the already-authorized W04-C09 Stage-A
implementation.

After successful Stage A, resilience proof, real-native R46 and Stage B, the
terminal state remains:

```text
W04_C09_REVIEW_READY
```

with GPT independent implementation review and Human acceptance still pending.

W04-C10 remains NOT AUTHORIZED.
