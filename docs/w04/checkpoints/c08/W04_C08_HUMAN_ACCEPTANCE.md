# W04-C08 Human Acceptance

Recorded on 2026-10-12 (Asia/Shanghai). Authority: the supplied Human acceptance/closeout request and CLOSEOUT-V1, not a new Codex review decision.

```text
GPT REVIEW = PASS
HUMAN_C08_ACCEPTANCE = ACCEPTED
DECISION = ACCEPTED
CLOSEOUT READINESS = READY
C08_CLOSEOUT_AUTHORIZATION = APPROVED
ACCEPTED SOURCE FREEZE = 1fa7b505980c1efc1b3725cd57a9732e254bccdf
REVIEW_READY HEAD = 72de21ffc38629c94af19f73a72791cec6eebc24
REVIEW_READY CI = #131 / 38190417996 / SUCCESS / P / PUBLICATION_EXACT_SHA
TASK VERSION = CLOSEOUT-V1
TASK RAW SHA-256 = bd1b9fb49b274f115ff9aba1db3f73f94ddcf3f4cf23cd3eb63cabe9f6ca593e
HUMAN REQUEST RAW BYTES = 17020
HUMAN REQUEST RAW SHA-256 = 5f6d43d65cfb6024460f4a1283311c5416c31cc821b7b868441cb6ba07c29e1a
```

The complete pasted Human request is reproduced below. Only its CRLF line endings are represented as LF for repository Markdown; every other character and all request text are preserved. The raw-byte seal above identifies the original attachment.

```text
W04-C08 HUMAN ACCEPTANCE + TWO-PHASE CLOSEOUT AUTHORIZATION

Execute exactly:

FLOWLENS_W04_C08_CLOSEOUT_TASK_V1.md

TASK VERSION:
CLOSEOUT-V1

TASK RAW SHA-256:
bd1b9fb49b274f115ff9aba1db3f73f94ddcf3f4cf23cd3eb63cabe9f6ca593e

Repository:
Ray-Yan-Rui-14793817/flowlens-industrial-ai

Branch:
feat/w04-evidence-investigation

PR:
#7

Required REVIEW_READY entry HEAD:

72de21ffc38629c94af19f73a72791cec6eebc24

Required REVIEW_READY native proof:

CI #131 / 38190417996 / SUCCESS
P / PUBLICATION_EXACT_SHA

Main / PR base:

af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

==================================================
HUMAN ACCEPTANCE
==================================================

I have reviewed the completed independent ChatGPT deep review of W04-C08.

I explicitly accept:

GPT_INDEPENDENT_IMPLEMENTATION_REVIEW = PASS

PRODUCT_CORRECTNESS = PASS
REPLAY_AUTHORITY_MODEL = PASS
TAMPER_RESISTANCE = PASS
CAPABILITY_ISOLATION = PASS
CI_EVIDENCE = PASS
STAGE_C_PUBLICATION = PASS
GOVERNANCE_BOUNDARY = PASS

BLOCKING_FINDINGS = 0

I explicitly accept the completed:

W04-C08 — Protected Investigation Replay

Accepted Stage-B implementation / source freeze:

1fa7b505980c1efc1b3725cd57a9732e254bccdf

Accepted native Stage-B proof:

CI #129 / 38153792599 / SUCCESS
I / FULL_EXACT_SHA

Accepted runtime source blobs:

src/flowlens/investigation/c08_policy.py
273d288cf4b0e55b646cd2e6751f0259e463a5ff

src/flowlens/investigation/c08_replay.py
4fa391cf751377305315b7de8303ce94e6eb6c6e

Accepted final publication/review-ready proof:

72de21ffc38629c94af19f73a72791cec6eebc24

CI #131 / 38190417996 / SUCCESS
P / PUBLICATION_EXACT_SHA

HUMAN_C08_ACCEPTANCE = ACCEPTED

I also accept the observed CI shard runtime headroom and C08 measured-weight
mismatch as a NON-BLOCKING FOLLOW-UP engineering item.

It does NOT block C08 semantic closeout.

It does NOT authorize CI re-weighting, timeout changes, shard-topology changes,
or workflow changes inside this closeout.

==================================================
CLOSEOUT AUTHORIZATION
==================================================

C08_CLOSEOUT_AUTHORIZATION = APPROVED

Execute the exact TWO-PHASE closeout defined by CLOSEOUT-V1:

PHASE 1:
W04-C08 Closeout-Prep-01 lifecycle harness hardening

PHASE 2:
W04-C08 Final Governance Closeout

The ordering is mandatory.

DO NOT perform the final manifest CLOSED transition before Phase-1 native CI
has completed successfully.

If Phase-1 native CI succeeds exactly as required, continue automatically to
Phase 2.

No additional Human/GPT checkpoint is required between successful Phase 1 and
Phase 2.

If any hard-stop condition occurs, STOP immediately.

==================================================
INITIAL PREFLIGHT
==================================================

Before any write:

1. Read the complete attached CLOSEOUT-V1 task.

2. Verify its exact raw SHA-256:

bd1b9fb49b274f115ff9aba1db3f73f94ddcf3f4cf23cd3eb63cabe9f6ca593e

3. Fetch fresh refs.

Require exactly:

local HEAD ==
tracking feature HEAD ==
direct origin feature HEAD ==
PR #7 HEAD ==
72de21ffc38629c94af19f73a72791cec6eebc24

branch ==
feat/w04-evidence-investigation

PR #7 ==
OPEN / DRAFT / UNMERGED

main / PR base ==
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

worktree/index ==
CLEAN

latest feature CI ==
#131 / 38190417996 / SUCCESS

#131 head ==
72de21ffc38629c94af19f73a72791cec6eebc24

#131 route ==
P / PUBLICATION_EXACT_SHA

Current manifest must be:

W04-C01..C07 = CLOSED

W04-C08 =
AUTHORIZED

W04-C08 source_freeze_sha =
null

W04-C08 blob_oid values =
null

W04-C09 =
ABSENT

Current C08 runtime Git blobs must be exactly:

c08_policy.py =
273d288cf4b0e55b646cd2e6751f0259e463a5ff

c08_replay.py =
4fa391cf751377305315b7de8303ce94e6eb6c6e

If any activation fact differs:

STOP

W04_C08_CLOSEOUT_CONTEXT_CHANGED

==================================================
PHASE 1 — CLOSEOUT-PREP-01
==================================================

This is NOT a C08 product/runtime repair.

The C08 runtime implementation is frozen and MUST NOT change.

The only issue being repaired is the R43 lifecycle test, which currently
hard-codes the AUTHORIZED manifest state and therefore cannot validate a
legitimate future CLOSED state.

Exact Phase-1 allowlist:

tests/test_investigation_replay.py

No second path.

Keep the existing selector exactly:

test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged

Do NOT:

- rename it
- delete it
- skip it
- xfail it
- parameterize it
- add another test node
- remove another test node

Freeze these values in the lifecycle proof:

C08_SOURCE_FREEZE_SHA =
1fa7b505980c1efc1b3725cd57a9732e254bccdf

C08_SOURCE_BLOBS:

src/flowlens/investigation/c08_policy.py =
273d288cf4b0e55b646cd2e6751f0259e463a5ff

src/flowlens/investigation/c08_replay.py =
4fa391cf751377305315b7de8303ce94e6eb6c6e

R43 must continue to prove:

- checkpoint ordering is exactly C01..C08
- C01-C07 are unchanged CLOSED entries
- C08 contains exactly the two expected runtime source paths
- current HEAD runtime blobs equal the accepted C08 blobs

R43 may admit EXACTLY two valid C08 lifecycle states:

--------------------------------
VALID STATE A — AUTHORIZED
--------------------------------

state =
AUTHORIZED

source_freeze_sha =
null

both blob_oid values =
null

--------------------------------
VALID STATE B — CLOSED
--------------------------------

state =
CLOSED

source_freeze_sha =
1fa7b505980c1efc1b3725cd57a9732e254bccdf

c08_policy.py blob_oid =
273d288cf4b0e55b646cd2e6751f0259e463a5ff

c08_replay.py blob_oid =
4fa391cf751377305315b7de8303ce94e6eb6c6e

For CLOSED state, also prove every manifest blob equals:

HEAD:<source path>

and:

1fa7b505980c1efc1b3725cd57a9732e254bccdf:<source path>

Any other combination of:

state
source_freeze_sha
blob_oid

must fail closed.

Do not weaken any C01-C07 or protected-object assertion.

==================================================
PHASE-1 LOCAL PROOF
==================================================

Run at minimum:

python -B -m pytest \
  tests/test_investigation_replay.py::test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged \
  tests/test_w04_source_evolution.py \
  -p no:cacheprovider

Then run:

python -B -m pytest \
  tests/test_investigation_replay.py \
  -p no:cacheprovider

Require:

0 test nodes added
0 test nodes removed
0 test nodes renamed

git diff --check = PASS

exact changed paths =
tests/test_investigation_replay.py

manifest =
UNCHANGED / C08 AUTHORIZED

C08 runtime blobs =
UNCHANGED

Do NOT modify:

src/**
scripts/**
.github/**
docs/**
planner weights
workflow
timeouts
dependencies
schema
migrations
W03
C01-C07

==================================================
PHASE-1 COMMIT
==================================================

Commit subject exactly:

test(w04-c08): allow exact closed replay lifecycle

Exactly one normal commit.

Exactly one normal push.

No amend.
No rebase.
No reset.
No force push.
No history rewrite.

==================================================
PHASE-1 NATIVE CI
==================================================

Wait for the Prep-01 SHA's own native CI to reach terminal state.

Expected route is full exact-SHA.
Actual native classifier is authoritative.

Require SUCCESS for all required full-route jobs:

Classify change
Static and plan
Integration and data
Non-integration shard 0
Non-integration shard 1
Non-integration shard 2
Non-integration shard 3
Non-integration shard 4
Non-integration shard 5
Non-integration shard 6
Non-integration aggregate
Quality gate
Docker Compose smoke
W03 AI loop gate
Verification gate

Require preserved outcome envelope:

2997 selected
2994 passed
3 accepted skipped

0 failed
0 error
0 xfail
0 xpass

entry no-loss = PASS
exact union = PASS
exact once = PASS

integration =
70 passed

W03 =
38 selectors / 85 cases PASS

Require:

runtime sources unchanged
manifest unchanged / C08 AUTHORIZED
planner unchanged
weights unchanged
workflow unchanged
timeouts unchanged
dependencies unchanged
schema/migrations unchanged

If Phase-1 native CI fails:

STOP

W04_C08_CLOSEOUT_PREP_01_CI_FAILED

DO NOT:

- retry/rerun as proof
- add repair commit
- increase timeout
- re-weight
- modify workflow
- continue into final closeout

If SUCCESS:

fetch fresh refs,
verify local/tracking/direct-origin/PR HEAD all equal Prep-01 SHA,
ahead/behind = 0/0,
worktree/index CLEAN,

then continue automatically to Phase 2.

==================================================
PHASE 2 — FINAL GOVERNANCE CLOSEOUT
==================================================

Before any Phase-2 write require:

all four feature heads ==
successful Prep-01 SHA

Prep-01 native CI ==
SUCCESS

worktree/index ==
CLEAN

PR #7 ==
OPEN / DRAFT / UNMERGED

main/base unchanged

C08 runtime blobs unchanged

manifest still =
C01-C07 CLOSED
C08 AUTHORIZED
C09 ABSENT

If any fact differs:

STOP

W04_C08_CLOSEOUT_FINAL_CONTEXT_CHANGED

==================================================
PHASE-2 EXACT ALLOWLIST
==================================================

Exactly six paths:

docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json

docs/w04/checkpoints/c08/W04_C08_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md

docs/w04/checkpoints/c08/W04_C08_HUMAN_ACCEPTANCE.md

docs/w04/checkpoints/c08/W04_C08_CLOSEOUT_AUTHORIZATION.md

docs/w04/checkpoints/c08/W04_C08_CLOSEOUT_CONTEXT_LOCK.md

docs/w04/checkpoints/c08/W04_C08_FINAL_CLOSEOUT_REPORT.md

No seventh path.

Existing C08 files remain immutable:

W04_C08_HUMAN_AUTHORIZATION.md
W04_C08_CONTEXT_LOCK.md
W04_C08_ENTRY_TEST_BASELINE.json
W04_C08_CI_BOOTSTRAP_WEIGHTS.json
W04_C08_R_DEVELOPMENT_ROUND_REPORT.md

The Phase-1 test file is also frozen during Phase 2.

==================================================
MANIFEST TRANSITION
==================================================

Perform exactly:

W04-C08:

AUTHORIZED
->
CLOSED

source_freeze_sha:

1fa7b505980c1efc1b3725cd57a9732e254bccdf

runtime blobs:

src/flowlens/investigation/c08_policy.py =
273d288cf4b0e55b646cd2e6751f0259e463a5ff

src/flowlens/investigation/c08_replay.py =
4fa391cf751377305315b7de8303ce94e6eb6c6e

Do NOT use:

Stage-C SHA
Stage-C Repair SHA
Prep SHA
Final Closeout SHA

as the C08 source freeze.

The source freeze is the accepted Stage-B runtime implementation SHA only:

1fa7b505980c1efc1b3725cd57a9732e254bccdf

Preserve every C01-C07 manifest object exactly.

Do not append C09.

==================================================
CLOSEOUT GOVERNANCE DOCUMENTS
==================================================

Create exactly:

W04_C08_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md

W04_C08_HUMAN_ACCEPTANCE.md

W04_C08_CLOSEOUT_AUTHORIZATION.md

W04_C08_CLOSEOUT_CONTEXT_LOCK.md

W04_C08_FINAL_CLOSEOUT_REPORT.md

The GPT review document must record the supplied independent ChatGPT review,
not a Codex self-review.

Record:

GPT_INDEPENDENT_IMPLEMENTATION_REVIEW = PASS
CRITICAL = NONE
HIGH = NONE
BLOCKING MEDIUM = NONE
CLOSEOUT READINESS = READY

The Human acceptance document must record this exact pasted Human authorization.

Record:

HUMAN_C08_ACCEPTANCE = ACCEPTED
C08_CLOSEOUT_AUTHORIZATION = APPROVED

Record the CI shard headroom/re-weight issue only as:

NON_BLOCKING FOLLOW-UP

Do not solve it in this closeout.

The final closeout report must be authored PRE-COMMIT.

It must state:

REPORT_STAGE =
PRE-COMMIT / PRE-CLOSEOUT-CI

FINAL_CLOSEOUT_SHA =
NOT YET CREATED

FINAL_CLOSEOUT_CI =
PENDING

Do not invent future generated values.

Do not amend the report after push to insert generated SHA/run.

==================================================
DISPOSABLE CANDIDATE PROOF
==================================================

Before modifying the primary checkout:

create a disposable full-history clone/worktree at exact successful Prep-01 HEAD.

Apply exactly the six final-closeout files.

Create one LOCAL candidate commit.

Never push the disposable candidate.

Run:

python -B -m pytest \
  tests/test_investigation_replay.py::test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged \
  tests/test_w04_source_evolution.py \
  -p no:cacheprovider

Then run:

python -B scripts/ci/verify_w04_source_evolution.py \
  --manifest docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json \
  --expected-head <DISPOSABLE_CANDIDATE_SHA> \
  --repo .

Require:

C01-C08 = CLOSED

AUTHORIZED checkpoints =
none

C09 =
ABSENT

C08 source_freeze_sha =
1fa7b505980c1efc1b3725cd57a9732e254bccdf

C08 blobs =
exact accepted blobs

R43 CLOSED lifecycle =
PASS

source-evolution suite =
PASS

production source-evolution verifier =
PASS

exact candidate delta =
six authorized Phase-2 paths

src/tests/scripts/ci/.github/dependencies/schema/migrations =
UNCHANGED

git diff --check =
PASS

Delete the disposable proof workspace after proof.

If any candidate proof fails:

STOP

W04_C08_CLOSEOUT_REQUIRES_GPT_CLARIFICATION

Do not automatically repair.

==================================================
REAL FINAL CLOSEOUT COMMIT
==================================================

Re-fetch and verify the primary checkout remains:

successful Prep-01 HEAD
clean
0/0 synchronized

Apply byte-for-byte the same six intended final-closeout files.

Commit subject exactly:

docs(w04-c08): close protected investigation replay

Exactly one normal commit.

No amend.
No rebase.
No reset.
No force push.

Before push, rerun:

R43
tests/test_w04_source_evolution.py
production verify_w04_source_evolution.py

against the real committed HEAD.

Require exact six-path commit delta.

Only then perform one normal push.

==================================================
FINAL OWN-SHA CI
==================================================

Expected native class:

C / FULL_EXACT_SHA

Native classifier is authoritative.

Require the NEW final closeout SHA's own terminal SUCCESS:

Classify change = SUCCESS
Static and plan = SUCCESS
Integration and data = SUCCESS
Non-integration shard 0 = SUCCESS
Non-integration shard 1 = SUCCESS
Non-integration shard 2 = SUCCESS
Non-integration shard 3 = SUCCESS
Non-integration shard 4 = SUCCESS
Non-integration shard 5 = SUCCESS
Non-integration shard 6 = SUCCESS
Non-integration aggregate = SUCCESS
Quality gate = SUCCESS
Docker Compose smoke = SUCCESS
W03 AI loop gate = SUCCESS
Verification gate = SUCCESS

Require:

2997 selected
2994 passed
3 accepted skipped

0 failed
0 error
0 xfail
0 xpass

entry no-loss = PASS
exact union = PASS
exact once = PASS

integration =
70 passed

W03 =
38 selectors / 85 cases PASS

R43 CLOSED lifecycle =
PASS

source evolution =
C01-C08 CLOSED
AUTHORIZED checkpoints = none

Do NOT relax the 55-minute timeout.

If any native gate fails:

STOP

W04_C08_CLOSEOUT_CI_FAILED

No retry/rerun.
No repair commit.
No replacement closeout commit.
No timeout increase.
No re-weight.
No workflow change.

==================================================
FINAL SYNCHRONIZATION
==================================================

Only after final native SUCCESS require:

local HEAD ==
tracking feature HEAD ==
direct origin feature HEAD ==
PR #7 HEAD ==
FINAL_CLOSEOUT_SHA

ahead/behind =
0/0

worktree/index =
CLEAN

main/base remains:

af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

PR #7 =
OPEN / DRAFT / UNMERGED

manifest =
C01-C08 CLOSED
AUTHORIZED = none
C09 ABSENT

==================================================
TERMINAL BOUNDARY
==================================================

Then and only then report:

W04_C08_CLOSEOUT_COMPLETE

W04-C08 =
CLOSED / VERIFIED / GITHUB SYNCHRONIZED

GPT_INDEPENDENT_IMPLEMENTATION_REVIEW =
PASS

HUMAN_C08_ACCEPTANCE =
ACCEPTED

C08_SOURCE_FREEZE =
1fa7b505980c1efc1b3725cd57a9732e254bccdf

C08_RUNTIME_BLOBS:

c08_policy.py =
273d288cf4b0e55b646cd2e6751f0259e463a5ff

c08_replay.py =
4fa391cf751377305315b7de8303ce94e6eb6c6e

MANIFEST =
C01-C08 CLOSED
C09 ABSENT

W04-C09 =
NOT AUTHORIZED

CI_REWEIGHT / TIMEOUT_CHANGE =
NOT AUTHORIZED

PR #7 =
OPEN / DRAFT / UNMERGED

PR_MERGE =
NOT AUTHORIZED

BRANCH_DELETION =
NOT AUTHORIZED

MAIN_WRITE =
NOT AUTHORIZED

Return the complete final handoff defined by CLOSEOUT-V1.

STOP.

Do not begin W04-C09.
Do not merge PR #7.
```

## Accepted deferred engineering item

The Human accepts the #129 shard-1 job duration of 3176s against the unchanged 3300s timeout: 124s headroom, approximately 3.8%. The C08 JUnit duration sum is 3082.523s versus the sealed bootstrap scheduling weight of 1061.491s. This is NON-BLOCKING FOLLOW-UP engineering work, deferred to separate authorization. No re-weight, timeout, retry, shard topology or workflow change is authorized by this closeout.

Acceptance binds the Stage-B implementation/source blobs and #129 full native proof, plus Stage-C Repair-01 #131 publication proof. It grants exactly the two-phase closeout in CLOSEOUT-V1. C09, PR ready/merge, branch deletion and main write remain unauthorized.
