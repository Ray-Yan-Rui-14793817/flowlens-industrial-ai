# W04-C09 — Human Authorization

Actual active Human prompt, verbatim below. Implementation/evidence authority ends at W04_C09_REVIEW_READY; acceptance and closeout remain pending.

```text
W04-C09 HUMAN AUTHORIZATION: APPROVED

Execute exactly:

FLOWLENS_W04_C09_CODEX_DEVELOPMENT_TASK_V1_1.md

TASK VERSION:
V1.1

TASK RAW SHA-256:
a445ee4ec99a714dd7e53f162df3eccdc0f8ed9295c6a67a71cef308feba553b

The previous W04-C09 V1 task is SUPERSEDED.

Do not execute, merge, reconcile or infer authority from V1.
V1.1 is the sole authoritative W04-C09 implementation contract.

Repository:
Ray-Yan-Rui-14793817/flowlens-industrial-ai

Branch:
feat/w04-evidence-investigation

PR:
#7

Required entry HEAD:

1fa841f2ee0d6612774c9f0ced204289df86e7a1

Required entry native CI:

#136 / 38360398379 / SUCCESS

Required entry class:

C / FULL_EXACT_SHA

Main / PR base:

af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

==================================================
AUTHORIZATION
==================================================

I authorize:

W04-C09 — W04 Regression Hardening /
Investigation Semantic CI Gate

TASK:
W04-C09-I/H/R

Authorization ends at:

W04_C09_REVIEW_READY

This is implementation/evidence authority only.

It does NOT authorize:

Human C09 acceptance
C09 closeout
W04-C10
PR ready-for-review transition
PR merge
auto-merge
branch deletion
main write
history rewrite

==================================================
PRODUCT BOUNDARY
==================================================

C09 is a CI / semantic proof-plane checkpoint.

It adds no investigation runtime capability.

Do not modify:

src/**
migrations/**
apps/**
dependencies
schema
product runtime
provider/model policy
HGT authority
operational behavior

C01-C08 remain CLOSED.

The W04 source-evolution manifest remains byte-identical.

C09 source-evolution entry remains:

ABSENT BY DESIGN

C10 remains:

NOT AUTHORIZED

==================================================
DEVCTRL-03 IMMUTABILITY
==================================================

Preserve exactly:

2997 non-integration nodes
63 files

node digest:

9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a

weights seal:

a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851

plan schema:

w04-devctrl03-non-integration-plan-v1

shards:

7

timeout:

65m

max-parallel:

7

fail-fast:

false

ZERO pytest nodes may be added, removed or renamed.

ZERO parameter expansion may change.

If collection changes:

STOP

W04_C09_NODESET_DRIFT

Do NOT re-weight.
Do NOT alter planner.
Do NOT admit a new pytest module.
Do NOT change shard topology.

==================================================
DEVCTRL-03 RESILIENCE — V1.1 HARDENING
==================================================

Preserving configuration alone is insufficient.

After Stage-A native CI SUCCESS, obtain the actual seven
non-integration job durations from GitHub job timestamps.

Also obtain all seven exact pytest suite durations from the native
shard JUnit artifacts.

Require:

max(shard job seconds) < 3300

AND

max(shard pytest seconds) < 3300

Interpretation:

55m = accepted resilience threshold
65m = execution timeout ceiling

A native SUCCESS between 55m and 65m is NOT acceptable C09 evidence.

Report:

ACTUAL_SHARD_JOB_SECONDS[0..6]

ACTUAL_SHARD_PYTEST_SECONDS[0..6]

LONGEST_SHARD_JOB

LONGEST_SHARD_PYTEST

HEADROOM_TO_55M

HEADROOM_TO_65M

If either threshold fails:

STOP

W04_C09_DEVCTRL03_RESILIENCE_REGRESSION

Do NOT automatically:
re-weight,
raise timeout,
increase shards,
split tests,
or introduce node-level sharding.

==================================================
C09 SEMANTIC GATE
==================================================

Create exactly one new CI semantic job:

job id:
w04-investigation-gate

job name:
W04 investigation gate

gate version:
w04-c09-investigation-gate-v1

manifest:
w04-c09-regression-manifest-v1

summary:
w04-c09-gate-summary-v1

Timeout:
30m

Required exact pack:

9 families
67 exact selectors
81 expanded cases

Manifest raw SHA-256:

d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1

Manifest canonical content SHA-256:

937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad

No selector substitution.

No count weakening.

==================================================
FAMILY PROCESS ISOLATION — V1.1
==================================================

The C09 runner must execute the nine semantic families as:

NINE SEPARATE PYTEST SUBPROCESSES

in exact manifest order.

Each process receives only that family's exact selectors.

Do not execute all 67 selectors inside one shared pytest process.

Require independently:

collection exact
case count exact
exit code zero
terminal PASS only

for every family.

This prevents cross-family global state, monkeypatch or fixture leakage.

==================================================
SUMMARY SEAL — V1.1
==================================================

The gate summary must be deterministic canonical JSON.

No:
clock
timestamp
random
environment-dependent field

Include:

summary_sha256

as a canonical self-seal computed with that field omitted.

Post-CI evidence must also record the raw SHA-256 of the exact summary bytes.

Real-native R46 must verify:

artifact ZIP digest
summary raw SHA
summary self-seal
exact semantic content

==================================================
C08 REPLAY HARNESS PROTECTION — V1.1
==================================================

tests/test_investigation_replay.py may change only for bounded R43/R46
meta-CI compatibility.

The independent verifier must compare it against:

C09_ENTRY_SHA =
1fa841f2ee0d6612774c9f0ced204289df86e7a1

Use AST/top-level source-span comparison.

Do NOT rely on line numbers.

All unrelated:

imports
module docstring
assignments
functions
classes
decorators
pytest parameterization
test bodies

must remain source-identical to entry.

Only the exact symbols authorized by the task may differ.

In particular:

R01-R42 semantic proof bodies MUST NOT change.

Unrelated R43/R46 support code MUST NOT change.

R46 damage parameter list MUST NOT change.

R43/R46 selector names MUST NOT change.

If an additional replay-test symbol appears necessary:

STOP

W04_C09_REQUIRES_GPT_CLARIFICATION

Do not silently widen the harness exception.

==================================================
R43
==================================================

Keep selector unchanged:

test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged

For minimal delta, retain helper symbol:

_devctrl03_workflow_delta_guard

but evolve it into the exact C09-aware workflow guard.

It must prove:

current workflow jobs =
C09 entry workflow jobs
+
exactly one new job:
w04-investigation-gate

All existing job blocks except Verification must remain byte-identical.

Verification may change only for the exact W04 dependency/result/truth-table
conjunction.

No workflow trigger change.

No existing timeout change.

No W03 change.

No action-pin change.

No hidden workflow file.

==================================================
R46
==================================================

Keep existing R46 selectors and parameter lists unchanged.

Full-route exact job set now includes:

W04 investigation gate

Require its metadata:

implementation_sha = exact Stage-A SHA

gate_version =
w04-c09-investigation-gate-v1

overall =
PASS

families =
9

selectors =
67

tests =
81

manifest_content_sha256 =
937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad

summary_sha256 =
VALID

Real-native proof requires:

existing 10 DEVCTRL native artifacts
+
w04-c09-gate-<STAGE_A_SHA>

exact artifact count:
11

Retain:

2997 / 63 planner proof
2994 passed / 3 accepted skipped
integration 70
W03 38 selectors / 85 cases PASS

==================================================
WORKFLOW TRUTH
==================================================

For non-P routes:

W03 = SUCCESS
W04 = SUCCESS
Publication = SKIPPED

Verification requires both W03 and W04.

For P route:

W03 = SKIPPED
W04 = SKIPPED
Publication = SUCCESS
heavy/full jobs = SKIPPED
Verification = SUCCESS

The independent verifier must adversarially execute the actual Verification
truth table, not merely grep YAML strings.

==================================================
STAGE-A SCOPE
==================================================

Exactly the 12 Stage-A paths in V1.1 are authorized.

A 13th path is forbidden.

If required:

STOP

W04_C09_SCOPE_VIOLATION

Do not modify:

src/**
source-evolution manifest
C01-C08 checkpoint files
DEVCTRL-03 files
planner
weights
classifier
publication verifier
W03 gate runner
dependencies
migrations
schema

==================================================
PREFLIGHT
==================================================

Before mutation:

read the entire V1.1 task.

Verify task SHA:

a445ee4ec99a714dd7e53f162df3eccdc0f8ed9295c6a67a71cef308feba553b

Fresh-fetch refs.

Require:

local HEAD ==
tracking feature HEAD ==
direct-origin HEAD ==
PR #7 HEAD ==
1fa841f2ee0d6612774c9f0ced204289df86e7a1

PR #7 =
OPEN / DRAFT / UNMERGED

main/base =
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

ahead/behind =
0/0

worktree/index =
CLEAN

latest native CI =
#136 / 38360398379 / SUCCESS

C01-C08 =
CLOSED

C09 source entry =
ABSENT

C10 =
NOT AUTHORIZED

If anything differs:

STOP

W04_C09_CONTEXT_CHANGED

==================================================
BASELINE PROOF
==================================================

Before writes verify Appendix A exactly:

67 selectors exist

81 expanded cases

9 families

all selected #136 leaves PASS

0 failed
0 error
0 skipped
0 xfail
0 xpass

#136 selected semantic-pack testcase-time sum:

706.974s

If mismatch:

STOP

W04_C09_SELECTOR_BASELINE_MISMATCH

Do not select replacements.

==================================================
LOCAL PROOF
==================================================

Execute every V1.1 local proof before commit.

Require at minimum:

manifest raw/canonical identity PASS

independent C09 contract verifier PASS

C08 replay-harness source-delta guard PASS

nine isolated family subprocesses PASS

9 / 9 families PASS

67 / 81 PASS

summary self-seal PASS

R43 PASS

R46 fixture/control PASS

full tests/test_investigation_replay.py PASS

tests/test_w04_source_evolution.py PASS

tests/test_ci_test_sharding.py PASS

Ruff PASS

strict mypy PASS

dependency lock PASS

active plan:
2997 nodes
63 files
same digest
same weights
7 shards

ZERO pytest node delta

ZERO unauthorized C08 replay-harness body delta

git diff --check PASS

==================================================
STAGE A
==================================================

Commit subject exactly:

ci(w04-c09): add investigation regression gate

One normal commit.
One normal push.

No amend.
No rebase.
No reset.
No force push.
No history rewrite.

Expected:

I / FULL_EXACT_SHA

Native classifier is authoritative.

Wait for its own native exact-SHA CI.

Require:

Classify SUCCESS
Static/Plan SUCCESS
Integration/Data SUCCESS
all seven shards SUCCESS
Aggregate SUCCESS
Quality SUCCESS
Compose SUCCESS
W03 SUCCESS
W04 investigation gate SUCCESS
Verification SUCCESS
Publication SKIPPED

Require:

2997 selected
2994 passed
3 accepted skipped
0 failed/error/xfail/xpass

entry no-loss PASS
exact union PASS
exact once PASS

integration 70 PASS

W03:
38 / 85 PASS

W04:
9 families
67 selectors
81 cases
PASS

Then perform the V1.1 <55m resilience check.

If native CI fails:

STOP

W04_C09_STAGE_A_CI_FAILED

No automatic post-push repair.

==================================================
REAL-NATIVE R46
==================================================

Only after:

Stage-A SUCCESS
+
resilience <55m PASS

download exact native evidence.

Require 11 artifacts.

Validate W04 artifact ZIP.

Validate summary raw SHA.

Validate summary self-seal.

Rerun real-native:

test_r46_stage_b_exact_sha_full_native_ci

Require PASS.

Require C08 replay-harness source-delta guard still PASS.

If failure:

STOP

W04_C09_R46_NATIVE_PROOF_FAILED

==================================================
STAGE B
==================================================

Only after all Stage-A proof passes create exactly:

docs/w04/checkpoints/c09/W04_C09_R_DEVELOPMENT_ROUND_REPORT.md

Nothing else.

The report must include the V1.1 additional evidence:

C08 replay-harness delta guard PASS

family-process isolation PASS

summary self-seal

summary raw SHA

seven shard job durations

seven shard pytest durations

longest shard job

longest shard pytest

headroom to 55m

headroom to 65m

DEVCTRL-03 resilience <55m PASS

Exact commit subject:

docs(w04-c09): publish regression-hardening proof

One normal commit.
One normal push.

Expected:

P / PUBLICATION_EXACT_SHA

Require:

Classify SUCCESS
Publication SUCCESS
Verification SUCCESS

full/heavy jobs SKIPPED
W03 SKIPPED
W04 investigation gate SKIPPED

==================================================
TERMINAL
==================================================

After Stage-B native SUCCESS and final synchronization return:

W04_C09_REVIEW_READY

Required:

C09 IMPLEMENTATION = COMPLETE
C09 HARNESS = PASS
C09 NATIVE CI = PASS
C09 REAL_NATIVE_R46 = PASS
C09 C08-HARNESS DELTA GUARD = PASS
C09 DEVCTRL-03 RESILIENCE = PASS

GPT INDEPENDENT REVIEW = PENDING

HUMAN C09 ACCEPTANCE = PENDING

C09 CLOSEOUT = NOT AUTHORIZED

C01-C08 =
CLOSED / UNCHANGED

C09 SOURCE EVOLUTION ENTRY =
ABSENT BY DESIGN

W04-C10 =
NOT AUTHORIZED

PR #7 =
OPEN / DRAFT / UNMERGED

PR MERGE =
NOT AUTHORIZED

BRANCH DELETION =
NOT AUTHORIZED

MAIN WRITE =
NOT AUTHORIZED

Return the COMPLETE handoff defined by V1.1.

STOP.

Do not start C10.
Do not close C09.
Do not merge PR #7.
```

# Actual Human Repair-01 authorization

Verbatim active Human resumption prompt. Acceptance and closeout remain pending.

```text
W04-C09 REPAIR-01 HUMAN AUTHORIZATION: APPROVED

Resume the existing W04-C09 V1.1 execution.

Authoritative base task remains:

FLOWLENS_W04_C09_CODEX_DEVELOPMENT_TASK_V1_1.md

BASE TASK SHA-256:

a445ee4ec99a714dd7e53f162df3eccdc0f8ed9295c6a67a71cef308feba553b

Additional bounded clarification is:

FLOWLENS_W04_C09_REPAIR_01_AUTHORIZATION.md

REPAIR-01 SHA-256:

744640783621660de009a8a1656ebb55bf752802ecb7e8256b8a1d9a8f3ee0ef

The Repair-01 addendum changes only the Stage-A path authorization
and corresponding meta-CI source-delta proof.

All other V1.1 requirements remain authoritative.

Do NOT restart C09 from scratch.

Do NOT discard the valid existing 12-path candidate work.

==================================================
GPT CLARIFICATION
==================================================

The three reproduced failures are accepted as expected meta-CI
contract-compatibility failures caused by the authorized addition of:

w04-investigation-gate

and the authorized extension of the final Verification conjunction.

This is NOT authorization to weaken CI tests.

This is NOT authorization to modify the classifier.

This is NOT authorization to modify W03 semantics.

==================================================
ADDITIONAL STAGE-A PATH AUTHORIZATION
==================================================

Extend Stage-A from exactly 12 paths to exactly 14 paths.

Add only:

tests/test_ci_change_classifier.py

tests/test_c09_ci_gate.py

No 15th Stage-A path is authorized.

Update both:

docs/w04/checkpoints/c09/specs/authorized_paths.json

and:

scripts/ci/verify_w04_investigation_gate_contract.py

to bind the exact 14-path set.

==================================================
EXACT ALLOWED DELTA — test_ci_change_classifier.py
==================================================

Only this existing function may change:

test_workflow_routes_all_classes_to_a_stable_fail_closed_gate

Required change:

update the exact Verification needs expectation to include:

w04-investigation-gate

Preserve all prior required dependencies.

Do not rename the test.

Do not add parameterization.

Do not weaken any classifier/path/publication assertion.

Every other top-level unit in this file must remain source-identical
to C09 entry:

1fa841f2ee0d6612774c9f0ced204289df86e7a1

==================================================
EXACT ALLOWED DELTA — test_c09_ci_gate.py
==================================================

Only these existing functions may change:

test_workflow_one_job_exact_schedule_source_manifest_and_environment

test_verification_runs_actual_shell_truth_table

For:

test_workflow_one_job_exact_schedule_source_manifest_and_environment

update only the exact workflow job-set contract so the job set includes:

w04-investigation-gate

Preserve the complete existing W03 job proof.

For:

test_verification_runs_actual_shell_truth_table

extend the exact Verification dependency contract with:

w04-investigation-gate

Require:

W04_RESULT:
${{ needs['w04-investigation-gate'].result }}

For P route:

W04_RESULT = skipped

For every non-P full route:

W04_RESULT = success

Add W04_RESULT to the adversarial wrong-status matrix.

Preserve every existing check for:

Classify
Static
Integration
Non-integration
Quality
Compose
W03
Publication

Do not rename either test.

Do not change their parameterization.

==================================================
META-CI SOURCE DELTA GUARD
==================================================

Extend:

scripts/ci/verify_w04_investigation_gate_contract.py

with AST/top-level source-span guards for both added files.

Use exact entry:

1fa841f2ee0d6612774c9f0ced204289df86e7a1

For:

tests/test_ci_change_classifier.py

authorize exactly one changed top-level function:

test_workflow_routes_all_classes_to_a_stable_fail_closed_gate

For:

tests/test_c09_ci_gate.py

authorize exactly:

test_workflow_one_job_exact_schedule_source_manifest_and_environment

test_verification_runs_actual_shell_truth_table

Everything else must remain entry-identical.

Guard:

imports
module docstring
assignments
helpers
fixtures
all other tests
decorators
parameter lists
function names

Add adversarial negative controls proving failure on:

unrelated test-body mutation
new test
renamed test
import mutation
decorator mutation
parameter-list mutation

Required result:

C09_META_CI_DELTA_GUARD = PASS

==================================================
NODESET BOUNDARY
==================================================

Repair-01 authorizes:

0 added pytest nodes
0 removed pytest nodes
0 renamed pytest nodes
0 parameter-expansion changes

Still require:

2997 non-integration nodes

63 files

node digest:

9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a

weights digest:

a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851

7 shards

65m timeout ceiling

If nodes/parameters change:

STOP

W04_C09_NODESET_DRIFT

==================================================
FORBIDDEN REPAIR
==================================================

Do NOT modify:

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

source-evolution manifest

C01-C08 checkpoint evidence

DEVCTRL-03 evidence

W03 evidence

Do NOT:

skip the three failing tests
xfail them
delete them
rename them
weaken exact-set assertions into permissive checks
change classifier behavior merely to make them pass

==================================================
REPAIR LOCAL PROOF
==================================================

After the exact three test-body updates require:

test_workflow_routes_all_classes_to_a_stable_fail_closed_gate
PASS

test_workflow_one_job_exact_schedule_source_manifest_and_environment
PASS

test_verification_runs_actual_shell_truth_table
PASS

Then require complete:

tests/test_ci_change_classifier.py
PASS

tests/test_c09_ci_gate.py
PASS

C09_META_CI_DELTA_GUARD
PASS

C08_REPLAY_HARNESS_DELTA_GUARD
PASS

Then rerun the full V1.1 local proof.

At minimum:

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

planner:
2997 nodes
63 files
same node digest
same weights
7 shards

git diff --check PASS

==================================================
STAGE A
==================================================

Do not create a repair-only commit.

This Repair-01 remains part of the same original C09 Stage-A implementation.

The exact Stage-A commit subject remains:

ci(w04-c09): add investigation regression gate

Exactly one normal Stage-A commit.

Exactly one normal push.

Expected:

I / FULL_EXACT_SHA

Native classifier remains authoritative.

Do not push until all local Repair-01 + V1.1 proof is green.

After native Stage-A SUCCESS, still require the original V1.1:

<55m shard-job resilience proof

<55m shard-pytest resilience proof

11-artifact real-native R46

C08 replay-harness delta proof

W04 gate exact summary proof

==================================================
BOUNDARIES
==================================================

This Repair-01 does NOT authorize:

C09 Human acceptance
C09 closeout
W04-C10
PR ready
PR merge
auto-merge
branch deletion
main write
history rewrite

Continue only until:

W04_C09_REVIEW_READY

Then STOP and return the complete handoff to ChatGPT for independent
implementation deep review.
```
