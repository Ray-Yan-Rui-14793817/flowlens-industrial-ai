# W04-C08 Human Implementation Authorization

Date: 2026-10-11 (Asia/Shanghai).

GPT C08 ARCHITECTURE / CONTRACT REVIEW R1 = PASS
HUMAN C08 IMPLEMENTATION AUTHORIZATION = APPROVED
AUTHORIZED THROUGH = REVIEW_READY
C08 CLOSEOUT = NOT AUTHORIZED
C09 = NOT AUTHORIZED
PR MERGE = NOT AUTHORIZED

Task: FLOWLENS_W04_C08_CODEX_TASK_V1.md
Task version: V1
Task raw byte size: 37097
Task raw SHA-256: c63a71cdf1a1a66ec75aabf3ae2d56d0f98b73ff2ba03894997971c09f80e106

The following is the Human-supplied exact approval text. The current authorization supersedes historical C08-not-authorized status only within this task scope.

```text
W04-C08 HUMAN IMPLEMENTATION AUTHORIZATION

You are now responsible for implementing:

FlowLens Industrial AI
W04-C08 — Protected Investigation Replay

I explicitly authorize execution of:

FLOWLENS_W04_C08_CODEX_TASK_V1.md

TASK VERSION:
V1

TASK RAW SHA-256:
c63a71cdf1a1a66ec75aabf3ae2d56d0f98b73ff2ba03894997971c09f80e106

Repository:
Ray-Yan-Rui-14793817/flowlens-industrial-ai

Branch:
feat/w04-evidence-investigation

PR:
#7

Required entry HEAD:

9afc4bd047bd4e52dfc4956f16e6420b3762301f

Entry native proof:

CI #126 / 38114263650 / SUCCESS
C / FULL_EXACT_SHA

Main / PR base:

af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

GPT C08 architecture / contract review R1:

PASS

I explicitly authorize W04-C08 implementation through REVIEW_READY only,
under the exact scope, stage gates, mutation allowlists, commit messages,
proof matrix, CI admission evolution, stop codes, and terminal boundary
defined in the attached V1 task.

This authorization does NOT authorize:

- C08 closeout
- W04-C09
- W04-C10
- DEVCTRL-03
- PR ready-for-review transition
- PR merge / auto-merge
- branch deletion
- main write
- history rewrite
- new dependency
- migration/schema mutation
- runtime HGT access
- operational mutation
- live provider calls
- upstream C01-C07 semantic repair

Before any repository write:

1. Read the complete attached task.
2. Verify its exact raw SHA-256 is:

   c63a71cdf1a1a66ec75aabf3ae2d56d0f98b73ff2ba03894997971c09f80e106

3. Fetch fresh remote refs.

4. Verify exactly:

local HEAD ==
tracking feature HEAD ==
direct origin feature HEAD ==
PR #7 HEAD ==
9afc4bd047bd4e52dfc4956f16e6420b3762301f

branch ==
feat/w04-evidence-investigation

PR #7 ==
OPEN / DRAFT / UNMERGED

main / PR base ==
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

worktree/index ==
CLEAN

latest feature CI ==
#126 / 38114263650 / SUCCESS

5. Verify source-evolution manifest:

W04-C01..C07 = CLOSED
W04-C08 = ABSENT

6. Verify current exact entry test proof:

non-integration selected = 2807

node digest =
4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d

selected files = 62

selected-file digest =
72f381af0f729834fc58920eec74f2ef1a6f9fb0991c7489350412fdfcf7366a

integration = 70

If any activation fact differs:

STOP

W04_C08_CONTEXT_CHANGED

Do not infer equivalence and do not repair.

--------------------------------------------------
STAGE A
--------------------------------------------------

Execute only the Stage A allowlist:

docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c08/W04_C08_HUMAN_AUTHORIZATION.md
docs/w04/checkpoints/c08/W04_C08_CONTEXT_LOCK.md
docs/w04/checkpoints/c08/W04_C08_ENTRY_TEST_BASELINE.json
docs/w04/checkpoints/c08/W04_C08_CI_BOOTSTRAP_WEIGHTS.json

Append exactly:

W04-C08
state = AUTHORIZED
source_freeze_sha = null

source paths:

src/flowlens/investigation/c08_policy.py
src/flowlens/investigation/c08_replay.py

both blob_oid = null

Do not alter C01-C07.

Create the exact C08 entry test baseline from the entry SHA.

Required:

2807 nodes
62 files

node SHA-256:
4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d

file SHA-256:
72f381af0f729834fc58920eec74f2ef1a6f9fb0991c7489350412fdfcf7366a

Create the exact one-file C08 CI bootstrap evidence.

Authorized file:

tests/test_investigation_replay.py

bootstrap weight:

1061.491 seconds

basis:

MAX_FROZEN_JUNIT_FILE_WEIGHT

basis file:

tests/test_investigation_findings.py

bootstrap SHA-256:

36f1d85e34344afee1f7e76b066427e4f40314c68f1d564340d82cc4dd44becb

Do not change the accepted DEVCTRL-02 base weights JSON.

Stage A commit subject exactly:

docs(w04-c08): authorize protected investigation replay

Normal push only.

Wait for the exact Stage A SHA native CI terminal result.

Require SUCCESS.

Expected route:

C / FULL_EXACT_SHA

Actual classifier is authoritative.

If Stage A CI fails:

STOP

W04_C08_STAGE_A_CI_FAILED

No automatic pushed repair.

--------------------------------------------------
STAGE B
--------------------------------------------------

Only after Stage A exact-SHA SUCCESS and fresh revalidation.

Exact Stage B allowlist:

src/flowlens/investigation/c08_policy.py
src/flowlens/investigation/c08_replay.py
tests/test_investigation_replay.py
scripts/ci/plan_non_integration_shards.py
tests/test_ci_test_sharding.py

No sixth path.

Implement the exact Protected Investigation Replay contract from V1.

Core semantics:

- replay frozen artifacts
- never refresh current operational evidence
- never query PostgreSQL
- never read C06 journal
- never call C07 provider
- never read HGT
- never import evaluation truth into runtime
- never use current clock/random
- never perform operational mutation
- never interpret Human note_text as evidence

Public functions:

replay_investigation(...)
validate_investigation_replay(...)

Implement immutable InvestigationReplayReceipt.

Authoritative replay identity must be based on:

validated source chain
+
fresh C07 DETERMINISTIC summary
+
frozen C08 limitations

It MUST NOT depend on optional C07 presentation wording.

Therefore valid:

DETERMINISTIC
DEGRADED_FALLBACK
BOUNDED_LLM

presentations of the exact same investigation must produce the same:

replay_core_sha256
replay_id

but may produce different full receipt_sha256.

Do not call a provider while replaying a BOUNDED_LLM summary.

Implement all C08-R01 through C08-R46 direct proofs.

No proof may exist only as prose.

--------------------------------------------------
C08 CI ADMISSION
--------------------------------------------------

The CI change is checkpoint admission, NOT a new optimization round.

Preserve:

SHARD_COUNT = 7
fail-fast = false
max-parallel = 7
all current timeouts
workflow DAG
artifact naming
terminal-outcome semantics
accepted skip policy

Do not modify .github/workflows/ci.yml.

Move the active no-loss floor to the new C08 #126 baseline.

Only post-entry test-node additions from:

tests/test_investigation_replay.py
tests/test_ci_test_sharding.py

are allowed.

Every other added-node file must fail closed.

Keep the accepted base weights evidence unchanged:

315675b184abd56422f469a44da5f840b40d82c3cfb272d46873afd7a8adacca

Use plan schema:

w04-devctrl02-non-integration-plan-v2

Bind:

bootstrap_weights_sha256 =
36f1d85e34344afee1f7e76b066427e4f40314c68f1d564340d82cc4dd44becb

effective_file_weights_sha256 =
352e6e1060bc1c2d5ce9a36fcad6cb9941e373bfae3da4d8a326d26a0d1f01c6

effective scheduling total =
7733.243 seconds

selected non-integration files =
63

The new test file must be assigned by deterministic LPT.
Do not hard-code its shard.

Unknown/unmodeled additional files must still fail closed.

Do not modify:

docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json

--------------------------------------------------
STAGE B LOCAL PROOF
--------------------------------------------------

At minimum run:

python -B -m pytest \
  tests/test_investigation_replay.py \
  tests/test_ci_test_sharding.py \
  tests/test_w04_source_evolution.py \
  -p no:cacheprovider

and C07 summary regression:

python -B -m pytest \
  tests/test_investigation_summary.py \
  tests/test_investigation_summary_provider.py \
  -p no:cacheprovider

Run required Ruff / strict mypy / repository control checks.

No live provider call.

No operational DB target.

Stage B commit subject exactly:

feat(w04-c08): add protected investigation replay

Normal push only.

Wait for exact Stage B SHA CI.

Require:

Classify = SUCCESS
Static/Plan = SUCCESS
Integration/Data = SUCCESS
all 7 non-integration shards = SUCCESS
Aggregate = SUCCESS
Quality = SUCCESS
Compose = SUCCESS
W03 = SUCCESS
Verification = SUCCESS
Publication = SKIPPED

Entry no-loss:

all original 2807 nodes remain present

All new non-integration nodes must come only from:

tests/test_investigation_replay.py
tests/test_ci_test_sharding.py

Integration must remain:

70 passed

No new C08 skip is expected.

failed = 0
error = 0
xfail = 0
xpass = 0

exact union = PASS
exact once = PASS
entry no-loss = PASS

Report actual new total node count and all seven shard durations.

Do NOT add a performance optimization commit.

If Stage B CI fails:

STOP

W04_C08_STAGE_B_CI_FAILED

Do not create an automatic repair commit.

--------------------------------------------------
STAGE C
--------------------------------------------------

Only after exact Stage B CI SUCCESS.

Create exactly:

docs/w04/checkpoints/c08/W04_C08_R_DEVELOPMENT_ROUND_REPORT.md

Nothing else.

The report must include the complete measured evidence required by V1:

- exact Stage A/B SHAs/runs
- exact source blobs
- R01-R46 selector map
- test counts
- new non-integration total/digest
- preserved 2807 entry no-loss
- integration 70
- planner v2 evidence
- actual shard durations
- replay identity semantics
- all three C07 presentation modes
- protected boundary evidence
- stable errors
- C01-C07/W03/dependency/schema freeze
- honest limitations

Stage C commit subject exactly:

docs(w04-c08): publish protected replay proof

Normal push only.

Wait for exact Stage C SHA CI.

Expected:

P / PUBLICATION_EXACT_SHA

Actual classifier controls.

Require terminal SUCCESS.

--------------------------------------------------
TERMINAL BOUNDARY
--------------------------------------------------

After Stage C native SUCCESS:

STOP at:

W04_C08_REVIEW_READY

Required state:

W04-C08 = REVIEW_READY
manifest C08 = AUTHORIZED

GPT_INDEPENDENT_IMPLEMENTATION_REVIEW = PENDING
HUMAN_C08_ACCEPTANCE = PENDING
C08_CLOSEOUT = NOT AUTHORIZED

W04-C09 = NOT AUTHORIZED

PR #7 = OPEN / DRAFT / UNMERGED
PR_MERGE = NOT AUTHORIZED
MAIN_WRITE = NOT AUTHORIZED

Return the complete final handoff required by Section 16 of V1.

Do not begin C08 closeout.
Do not begin C09.
```
