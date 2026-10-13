# W04-DEVCTRL-03 Human authorization and Clarification-01

Task: measured re-weight and shard resilience. Scope: CI engineering and the
explicit C08 harness compatibility exception. C08 remains CLOSED.

Repository: Ray-Yan-Rui-14793817/flowlens-industrial-ai.
Branch: feat/w04-evidence-investigation. PR: #7, OPEN / DRAFT / UNMERGED.

Entry HEAD: `a18e7f0733079ecc9aebdd94458625011e2f93f9`.
Entry CI: #133 / 38205524984 / SUCCESS / C / FULL_EXACT_SHA.
Main / PR base: `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`.

The Human invokes V1 and Clarification-01 together. Clarification-01 supersedes
V1 only at its explicit conflicts: exactly seven Stage-A paths are authorized,
including the bounded existing C08 R43/R46 harness changes.

Stage A: one normal commit/push, subject `ci(w04): apply measured shard weights`.
Stage B: only after full native CI, resilience and real-native R46 PASS; one
report-only normal commit/push, subject
`docs(w04): publish measured shard resilience proof`.
No automatic native-CI rerun or repair is authorized.

GPT independent review: PENDING. Human acceptance: PENDING.
DEVCTRL-03 closeout: NOT AUTHORIZED. C09, PR merge and main write: NOT AUTHORIZED.

## Exact task and Human-request provenance

- Base task V1: `FLOWLENS_W04_DEVCTRL_03_MEASURED_REWEIGHT_SHARD_RESILIENCE_TASK_V1.md`, 17740 raw bytes; SHA-256 `54395514fabd6498d59dee57e1374f3f3638b40a8c31bac29bcb0e6e46683ea7`.
- Clarification-01: `FLOWLENS_W04_DEVCTRL_03_CLARIFICATION_01_HARNESS_AUTHORIZATION.md`, 7779 raw bytes; SHA-256 `683320441e5f6945030a935e245781454e007d841eb45f6bd826b6ebb078762f`.
- Base Human request: `已粘贴的文本.txt`, 10303 raw bytes; SHA-256 `0bfabfc485349307d51ae55ed75f6f2130145b714e06c75645c2dba8263130ea`.
- Clarification Human request: `已粘贴的文本.txt`, 7568 raw bytes; SHA-256 `579ec0f089d9a99e4364112e29b3900d4b7dd3fa6f435ff068f90d4848518e0a`.

The following Human requests preserve every character, with CRLF normalized to LF
for repository Markdown. Their raw seals above refer to the original files.

## Base Human authorization

```text
W04-DEVCTRL-03 — MEASURED RE-WEIGHT & SHARD RESILIENCE AUTHORIZATION

Execute exactly:

FLOWLENS_W04_DEVCTRL_03_MEASURED_REWEIGHT_SHARD_RESILIENCE_TASK_V1.md

TASK VERSION:
V1

TASK RAW SHA-256:
54395514fabd6498d59dee57e1374f3f3638b40a8c31bac29bcb0e6e46683ea7

Repository:
Ray-Yan-Rui-14793817/flowlens-industrial-ai

Branch:
feat/w04-evidence-investigation

PR:
#7

Required current HEAD:

a18e7f0733079ecc9aebdd94458625011e2f93f9

Required current native proof:

#133 / 38205524984 / SUCCESS
C / FULL_EXACT_SHA

Main / PR base:

af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

==================================================
AUTHORIZATION
==================================================

I authorize W04-DEVCTRL-03:

Measured Re-weight & Shard Resilience.

This is CI engineering only.

W04-C08 is CLOSED and MUST NOT be reopened or modified.

W04-C09 remains NOT AUTHORIZED.

The task goal is:

1. replace the stale active #122 + C08-bootstrap scheduling model with
   measured 63-file weights derived from successful full runs #129, #132
   and #133;

2. preserve seven-shard file-atomic deterministic LPT;

3. increase only the non-integration shard timeout from 55 minutes to
   65 minutes for measured resilience;

4. validate the change with its own full exact-SHA CI;

5. publish a measured resilience report;

6. STOP at W04_DEVCTRL_03_REVIEW_READY.

==================================================
PREFLIGHT
==================================================

Read the complete attached task first.

Verify the exact task SHA-256:

54395514fabd6498d59dee57e1374f3f3638b40a8c31bac29bcb0e6e46683ea7

Fetch fresh refs.

Require:

local HEAD ==
tracking feature HEAD ==
direct origin feature HEAD ==
PR #7 HEAD ==
a18e7f0733079ecc9aebdd94458625011e2f93f9

branch ==
feat/w04-evidence-investigation

PR #7 ==
OPEN / DRAFT / UNMERGED

main/base ==
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

worktree/index ==
CLEAN

latest feature CI ==
#133 / 38205524984 / SUCCESS

manifest ==
C01-C08 CLOSED
AUTHORIZED none
C09 ABSENT

If any differs:

STOP

W04_DEVCTRL_03_CONTEXT_CHANGED

==================================================
SOURCE EVIDENCE
==================================================

Use exactly these three successful full runs:

#129 / 38153792599
HEAD:
1fa7b505980c1efc1b3725cd57a9732e254bccdf

aggregate artifact:
11708692092

JUnit SHA-256:
0c4f2633c1e43fe6c2f3e868b59eb7509c1f7393d001cf038650d655a7564875

receipt seal:
d0b14deb926bc021dddf2a88c68de506079f5c87889528024e304c1413c5b675


#132 / 38200544252
HEAD:
0047bb942e8e4227af8d6fb5c9a4763688a22aab

aggregate artifact:
11725204097

JUnit SHA-256:
d2f5ea4e07c48ff1891cd45cd51a3056f96d538d6916a98470c4dbab6258a4de

receipt seal:
f848f66caa0c4fde2bc4d1ab463dc658709af8e57aea5aeaac72ddcdeac132e5


#133 / 38205524984
HEAD:
a18e7f0733079ecc9aebdd94458625011e2f93f9

aggregate artifact:
11727789439

JUnit SHA-256:
a18e886433b2d737ac071bfbb5959d8c76349633923eb998b41cc58bee4846e5

receipt seal:
3762f815e9cee1bf5773ea10092fd02d86a89c27a662e74ee37cd954bf0fb78a

All three must prove:

2997 selected
2994 passed
3 accepted skipped
0 failed/error/xfail/xpass

node digest:
9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a

63 selected files

entry no-loss PASS
exact union PASS
exact once PASS

If the source evidence differs:

STOP

W04_DEVCTRL_03_EVIDENCE_MISMATCH

==================================================
MEASURED WEIGHT DERIVATION
==================================================

Create:

docs/w04/devctrl-03/W04_DEVCTRL_03_MEASURED_SHARD_WEIGHTS.json

Do NOT modify:

docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json

or:

docs/w04/checkpoints/c08/W04_C08_CI_BOOTSTRAP_WEIGHTS.json

Those remain immutable historical evidence.

For each of the 63 current test files:

- sum exact JUnit testcase time attributes per source run;
- retain millisecond precision;
- obtain exactly three samples in order #129/#132/#133;
- scheduling weight = exact median of the three;
- observed_max = max of the three;
- no averaging;
- no smoothing;
- no guessed override.

Expected total median scheduling weight:

9645.665 seconds

Required hot-file result:

tests/test_investigation_replay.py

samples:
3082.523
2040.544
1658.888

median:
2040.544

observed max:
3082.523

==================================================
PLANNER
==================================================

Preserve:

SHARD_COUNT = 7
file atomic = true
deterministic LPT = true
fail-fast = false
max-parallel = 7

Do not hard-code file-to-shard assignments.

The measured model must naturally produce:

2040.544
1784.313
1624.916
1056.117
1046.586
1046.586
1046.603

with the first four heavy singleton files:

test_investigation_replay.py
test_investigation_human_store.py
test_investigation_summary.py
test_investigation_findings.py

Use a new measured planner schema consistent with the attached contract.

No default weight for unknown files.

Missing/extra/unmodeled files fail closed.

No node ID addition, deletion or rename.

==================================================
HISTORICAL SIMULATION
==================================================

Before committing, replay the proposed assignment against the measured file
durations from all three source runs.

Current maximum pytest times:

#129 = 3143.457
#132 = 2235.256
#133 = 2181.682

Required proposed-plan maxima:

#129 = 3082.523
#132 = 2040.544
#133 = 1784.313

No source run may regress.

==================================================
SHARD RESILIENCE
==================================================

Change only:

non-integration shard timeout:

55 minutes
->
65 minutes

Reason:

worst observed hot file =
3082.523s

maximum observed job overhead =
46.440s

isolated observed floor =
3128.963s

55m headroom =
~5.2%

65m headroom =
~24.6%

Do not change any other timeout.

Do not change shard count.

Do not change max-parallel.

Do not introduce node-level sharding.

==================================================
IMPLEMENTATION ALLOWLIST
==================================================

Exactly:

.github/workflows/ci.yml
scripts/ci/plan_non_integration_shards.py
tests/test_ci_test_sharding.py

docs/w04/devctrl-03/W04_DEVCTRL_03_AUTHORIZATION.md
docs/w04/devctrl-03/W04_DEVCTRL_03_CONTEXT_LOCK.md
docs/w04/devctrl-03/W04_DEVCTRL_03_MEASURED_SHARD_WEIGHTS.json

No seventh path.

If another CI runtime script genuinely requires modification:

STOP

W04_DEVCTRL_03_REQUIRES_GPT_CLARIFICATION

Do not silently widen scope.

==================================================
PROTECTED BOUNDARY
==================================================

Do not modify:

src/**
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c01/**
docs/w04/checkpoints/c02/**
docs/w04/checkpoints/c03/**
docs/w04/checkpoints/c04/**
docs/w04/checkpoints/c05/**
docs/w04/checkpoints/c06/**
docs/w04/checkpoints/c07/**
docs/w04/checkpoints/c08/**

dependencies
migrations
schema
W03 semantics
product runtime

C01-C08 must remain CLOSED.

C09 must remain ABSENT.

==================================================
LOCAL PROOF
==================================================

Derive measured evidence directly from downloaded artifacts.

Verify:

measured total =
9645.665s

exact 63 files

exact historical simulation results

exact measured LPT totals

Then run at minimum:

python -B -m pytest \
  tests/test_ci_test_sharding.py \
  tests/test_w04_source_evolution.py \
  -p no:cacheprovider

Run required Ruff and strict mypy.

Require:

git diff --check PASS

current collection =
2997 nodes / 63 files

no test node addition/removal/rename

only non-integration timeout changes to 65

==================================================
STAGE A
==================================================

Commit subject exactly:

ci(w04): apply measured shard weights

One normal commit.
One normal push.

Wait for its own exact-SHA native CI.

Require full-route SUCCESS:

Classify
Static/Plan
Integration/Data
all seven non-integration shards
Aggregate
Quality
Compose
W03
Verification

Require:

2997 selected
2994 passed
3 accepted skipped
0 failed/error/xfail/xpass

entry no-loss PASS
exact union PASS
exact once PASS

integration =
70 passed

W03 =
38 selectors / 85 cases PASS

C01-C08 =
CLOSED

C09 =
ABSENT

Capture actual seven shard job and pytest durations.

Additional resilience criterion:

LONGEST SHARD JOB < 55 MINUTES

The new timeout remains 65 minutes.

If CI succeeds but longest shard job is >=55 minutes:

STOP

W04_DEVCTRL_03_RESILIENCE_TARGET_MISSED

Do not automatically increase timeout or split tests.

If CI fails:

STOP

W04_DEVCTRL_03_STAGE_A_CI_FAILED

No automatic rerun or repair.

==================================================
STAGE B REPORT
==================================================

Only after Stage A SUCCESS and resilience target PASS, create exactly:

docs/w04/devctrl-03/W04_DEVCTRL_03_R_DEVELOPMENT_ROUND_REPORT.md

Record the complete measured evidence, historical simulation, actual new plan,
new CI timing and limitations.

Commit subject exactly:

docs(w04): publish measured shard resilience proof

One normal commit/push.

Wait for its own native CI.

Native classifier is authoritative.

Require terminal SUCCESS.

==================================================
TERMINAL
==================================================

Then report:

W04_DEVCTRL_03_REVIEW_READY

Required state:

C01-C08 = CLOSED
C09 = NOT AUTHORIZED

measured weights = ACTIVE
non-integration timeout = 65m
shards = 7
max-parallel = 7
file atomicity = PRESERVED

GPT independent review = PENDING
Human acceptance = PENDING
DEVCTRL-03 closeout = NOT AUTHORIZED

PR #7 = OPEN / DRAFT / UNMERGED
PR merge = NOT AUTHORIZED
main write = NOT AUTHORIZED

STOP.

Do not begin C09.
```

## Clarification-01 Human authorization

```text
W04-DEVCTRL-03 CLARIFICATION-01 — C08 HARNESS COMPATIBILITY AUTHORIZATION

Continue the previously authorized:

W04-DEVCTRL-03 — Measured Re-weight & Shard Resilience

Base task:

FLOWLENS_W04_DEVCTRL_03_MEASURED_REWEIGHT_SHARD_RESILIENCE_TASK_V1.md

Apply additionally:

FLOWLENS_W04_DEVCTRL_03_CLARIFICATION_01_HARNESS_AUTHORIZATION.md

CLARIFICATION RAW SHA-256:

683320441e5f6945030a935e245781454e007d841eb45f6bd826b6ebb078762f

The clarification supersedes the base task only where the two contracts
explicitly conflict.

Repository:
Ray-Yan-Rui-14793817/flowlens-industrial-ai

Branch:
feat/w04-evidence-investigation

PR:
#7

Required unchanged current HEAD:

a18e7f0733079ecc9aebdd94458625011e2f93f9

Required current CI:

#133 / 38205524984 / SUCCESS

I confirm the previous hard stop was correct.

No repository mutation occurred.
No commit occurred.
No push occurred.

The measured evidence already validated by the previous attempt is accepted:

source runs:
#129 / #132 / #133

63 files

median total:
9645.665s

hot-file samples:
3082.523 / 2040.544 / 1658.888

new LPT:
2040.544
1784.313
1624.916
1056.117
1046.586
1046.586
1046.603

historical proposed maxima:

#129 = 3082.523s
#132 = 2040.544s
#133 = 1784.313s

Do not repeat or reinterpret these measurements unless an exact evidence
integrity check fails.

==================================================
ADDITIONAL HARNESS-ONLY AUTHORIZATION
==================================================

Authorize exactly one additional Stage-A path:

tests/test_investigation_replay.py

This is a C08 HARNESS-ONLY exception.

C08 remains:

CLOSED

Do NOT modify:

src/flowlens/investigation/c08_policy.py
src/flowlens/investigation/c08_replay.py

Do NOT change:

C08 replay semantics
C08 receipt semantics
C08 error semantics
C08 capability boundaries
C08 source freeze
C08 manifest state
C08 test-node set
C08 skips / xfails

Within tests/test_investigation_replay.py, modify only:

- constants/helpers strictly required for DEVCTRL-03 compatibility
- existing R43
- existing R46 native-proof assertions/helpers

No other R01-R46 semantic change is authorized.

==================================================
REVISED EXACT STAGE-A ALLOWLIST
==================================================

Exactly seven paths:

.github/workflows/ci.yml

scripts/ci/plan_non_integration_shards.py

tests/test_ci_test_sharding.py

tests/test_investigation_replay.py

docs/w04/devctrl-03/W04_DEVCTRL_03_AUTHORIZATION.md

docs/w04/devctrl-03/W04_DEVCTRL_03_CONTEXT_LOCK.md

docs/w04/devctrl-03/W04_DEVCTRL_03_MEASURED_SHARD_WEIGHTS.json

An eighth path is forbidden.

If an eighth path becomes necessary:

STOP

W04_DEVCTRL_03_SCOPE_VIOLATION

==================================================
R43 CLARIFICATION
==================================================

Keep selector:

test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged

Do not rename, delete, skip, xfail or parameterize it.

Preserve all existing C01-C08 lifecycle/source assertions.

Remove ONLY:

.github/workflows

from the generic ENTRY_SHA byte-equality protected-path tuple.

Do not remove any other frozen path.

Replace that over-broad workflow assertion with an exact DEVCTRL-03 delta guard.

Freeze:

DEVCTRL_03_ENTRY_SHA =
a18e7f0733079ecc9aebdd94458625011e2f93f9

Prove both entry and current workflow trees contain exactly:

.github/workflows/ci.yml

Read DEVCTRL_03_ENTRY_SHA:.github/workflows/ci.yml.

Derive the only authorized current workflow bytes by applying exactly:

non-integration job:

timeout-minutes: 55
->
timeout-minutes: 65

Require that target occurrence is unique in its exact job context.

Require current HEAD ci.yml equals the derived expected file byte-for-byte.

Also require:

shard count = 7
fail-fast = false
max-parallel = 7

No other timeout changes.
No action pin changes.
No job changes.
No step changes.
No workflow path additions/deletions.

Do NOT replace this with a broad "workflow may differ" allowance.

==================================================
R46 CLARIFICATION
==================================================

Keep selector:

test_r46_stage_b_exact_sha_full_native_ci

Preserve:

FULL_EXACT_SHA validation
exact run/head binding
required jobs
artifact ZIP integrity
current exact collection
entry no-loss
63 files
aggregate reconstruction
receipt validation
3 accepted skips
0 failed/error/xfail/xpass
integration 70
W03 validation

Change only the old active planner identity assertions.

Authorize new active schema:

w04-devctrl03-non-integration-plan-v1

The real-native branch must validate the new plan using:

planner.validate_plan(plan, weights, baseline, head)

and must additionally bind the exact DEVCTRL-03 measured-weight
evidence/self-seal.

Do NOT accept arbitrary old and new schemas simultaneously.

After DEVCTRL-03 Stage A, R46 real-native proof should accept exactly the new
active planner contract.

If legacy base/bootstrap fields are removed, validate the new measured fields.

If compatibility fields remain, prove explicitly that they are provenance-only
and no longer participate in active scheduling.

Do NOT retain obsolete bootstrap scheduling merely to make old assertions pass.

==================================================
PROOF
==================================================

Run in addition to all original V1 proof steps:

python -B -m pytest \
  tests/test_investigation_replay.py::test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged \
  tests/test_investigation_replay.py::test_r46_native_full_proof_gate_rejects_incomplete_or_wrong_sha_controls \
  tests/test_investigation_replay.py::test_r46_stage_b_exact_sha_full_native_ci \
  tests/test_ci_test_sharding.py \
  tests/test_w04_source_evolution.py \
  -p no:cacheprovider

Then:

python -B -m pytest \
  tests/test_investigation_replay.py \
  -p no:cacheprovider

Require:

0 test nodes added
0 test nodes removed
0 test nodes renamed

R01-R46 preserved

git diff --check PASS

C08 runtime blobs unchanged:

273d288cf4b0e55b646cd2e6751f0259e463a5ff

4fa391cf751377305315b7de8303ce94e6eb6c6e

manifest:

C01-C08 CLOSED
C09 ABSENT

==================================================
STAGE A
==================================================

The Stage-A commit remains exactly:

ci(w04): apply measured shard weights

One normal commit.
One normal push.

No separate repair/prep commit is required because the repository remained
untouched before clarification.

Execute the rest of V1 exactly.

After Stage-A native full CI SUCCESS, rerun R46 with the REAL Stage-A native
artifacts.

Require real-native R46 PASS against the new measured planner.

If it fails:

STOP

W04_DEVCTRL_03_R46_NATIVE_PROOF_FAILED

Do not weaken R46 automatically.

==================================================
TERMINAL
==================================================

Continue to the original V1 Stage-B report only after all Stage-A requirements
pass.

Final terminal remains:

W04_DEVCTRL_03_REVIEW_READY

C01-C08 CLOSED

C09 NOT AUTHORIZED

GPT independent review PENDING

Human acceptance PENDING

DEVCTRL-03 closeout NOT AUTHORIZED

PR #7 OPEN / DRAFT / UNMERGED

STOP.

Do not start C09.
```
