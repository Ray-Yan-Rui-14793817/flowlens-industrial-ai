# W04-C10 Human Implementation Authorization

```text
HUMAN IMPLEMENTATION AUTHORIZATION = APPROVED
HUMAN BUSINESS ACCEPTANCE = PENDING
HUMAN_C10_ACCEPTANCE = PENDING
GPT_INDEPENDENT_C10_REVIEW = PENDING
C10 CLOSEOUT AUTHORIZATION = NOT GRANTED
W04 SPRINT CLOSEOUT = NOT AUTHORIZED
PR #7 = OPEN / DRAFT / UNMERGED
PR READY / MERGE / AUTO-MERGE = NOT AUTHORIZED
BRANCH DELETION / MAIN WRITE / POST-W04 IMPLEMENTATION = NOT AUTHORIZED
```

The exact original Human prompt is preserved below as supplied text (UTF-8 text, displayed with LF line breaks). The raw source digest retains byte identity. Later approvals resume the same bounded design; they decide no business acceptance.

## Original V1.1 Human request

Raw source SHA-256: `e17e5c0900e3d80579e885bdaaa22bf5bab67fbfbb7c28cc3f9e03d415eb3677`.

```text
W04-C10 HUMAN IMPLEMENTATION AUTHORIZATION: APPROVED

Execute exactly:

FLOWLENS_W04_C10_CODEX_DEVELOPMENT_TASK_V1_1.md

TASK VERSION:
W04-C10-A-V1.1

TASK RAW SHA-256:
15f8c1ddd8a423edccb0fb2f927675b609a5b6177427f61e643bfb964c7314d4

This V1.1 task SUPERSEDES:

FLOWLENS_W04_C10_CODEX_DEVELOPMENT_TASK_V1.md

Superseded V1 SHA-256:
4ed5f9de6e0dd10bb985a0e882f4a441a517fd0c07ed88818728484f748a7775

Do not execute the superseded V1 contract.


Repository:
Ray-Yan-Rui-14793817/flowlens-industrial-ai

Branch:
feat/w04-evidence-investigation

PR:
#7

Required entry HEAD:
d33ee858fca8caaceba2ce60c045f7e4213c631a

Required entry native proof:
CI #140 / 38436850640 / SUCCESS / attempt 1
C / FULL_EXACT_SHA

Required main / PR base:
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509


==================================================
AUTHORIZATION SCOPE
==================================================

I explicitly authorize the bounded W04-C10 V1.1 sequence:

C09 FINAL
->
C10 BOOTSTRAP-01
->
BOOTSTRAP OWN-SHA FULL CI
->
C10 STAGE A
->
STAGE-A OWN-SHA FULL CI
->
H01-H44 / A01-A10 POST-CI AUDIT
->
C10 STAGE B
->
STAGE-B COMMITTED-HEAD LIFECYCLE PROOF
->
STAGE-B OWN-SHA PUBLICATION CI
->
FINAL SYNCHRONIZATION
->
W04_C10_REVIEW_READY
->
STOP

This authorization includes the exact Bootstrap-01 verifier handoff
defined by the V1.1 task.

It does NOT authorize any wider C09 repair or semantic change.


==================================================
BOOTSTRAP-01
==================================================

Bootstrap-01 may modify exactly:

scripts/ci/verify_w04_investigation_gate_contract.py

No second path is authorized.

Exact commit subject:

ci(w04-c10): admit bounded acceptance lifecycle

Bootstrap must be a direct single-parent child of:

d33ee858fca8caaceba2ce60c045f7e4213c631a

The purpose is ONLY to extend the accepted C09 lifecycle verifier from:

C09 Stage A
-> REVIEW_READY
-> C09 Closeout-Prep-01
-> C09 Final

to additionally admit exactly:

C09 Final
-> C10_BOOTSTRAP_01
-> C10_STAGE_A
-> C10_REVIEW_READY

Preserve all existing C09 semantic, workflow, replay,
meta-CI, manifest, collection, outcome, weights,
W03 and W04 regression controls.

Do not modify C09 checkpoint documents.

Do not modify runtime source, tests, workflow,
classifier, publication verifier, planner, weights,
timeouts, dependencies, schema or migrations.

Use the disposable full-history candidate procedure
defined in V1.1 before changing the primary checkout.

Do not push a failing Bootstrap candidate.


==================================================
BOOTSTRAP LOCAL PROOF
==================================================

Require the complete V1.1 local proof,
including committed-head verifier controls,
negative lifecycle/source adversaries,
meta-CI/replay/source-evolution suites,
Ruff, strict mypy and git diff --check.

Require unchanged:

2997 nodes
63 selected files
node digest
weights digest
7-shard topology
65m ceiling

If Bootstrap requires semantic widening or local proof fails:

STOP

W04_C10_BOOTSTRAP_REQUIRES_GPT_CLARIFICATION

Do not guess.
Do not silently repair.
Do not push.


==================================================
BOOTSTRAP NATIVE CI
==================================================

After the real Bootstrap commit and normal push:

Expected classification:

C / FULL_EXACT_SHA

The native classifier is authoritative.

Require complete full-route SUCCESS.

Require again:

2997 selected
2994 passed
3 accepted skipped

failed/error/xfail/xpass = 0

entry no-loss = PASS
exact union = PASS
exact once = PASS

Integration = 70 PASS
W03 = 38 selectors / 85 cases PASS
W04 = 9 families / 67 selectors / 81 cases PASS

Require verifier lifecycle:

C10_BOOTSTRAP_01

If Bootstrap native CI fails:

STOP

W04_C10_BOOTSTRAP_CI_FAILED

No rerun-as-proof.
No replacement Bootstrap commit.
No automatic repair.


==================================================
C10 STAGE A
==================================================

Only after Bootstrap own-SHA SUCCESS and fresh
four-head synchronization may Stage A begin.

Create exactly the eleven C10 files defined in V1.1.

No existing repository file may change.

In particular the Bootstrap verifier must remain
byte-for-byte frozen.

Exact Stage-A commit subject:

docs(w04-c10): prepare investigation business acceptance

Stage A must be a direct child of the successful Bootstrap SHA.

Exactly one normal commit.
Exactly one normal push.

Expected classification:

C / FULL_EXACT_SHA


==================================================
STAGE-A NATIVE PROOF
==================================================

Require Stage-A own-SHA full CI SUCCESS:

Classify
Static / Plan
Integration / Data
Shard 0..6
Aggregate
Quality
Compose
W03 AI loop gate
W04 investigation gate
Verification

Publication = SKIPPED

Require:

2997 / 2994 / 3
zero adverse outcomes
Integration 70
W03 38 / 85
W04 9 / 67 / 81
exact union
exact once
entry no-loss

Require verifier lifecycle:

C10_STAGE_A

If Stage-A CI fails:

STOP

W04_C10_STAGE_A_CI_FAILED

Do not automatically repair.


==================================================
POST-CI ACCEPTANCE-READINESS AUDIT
==================================================

After Stage-A native SUCCESS require:

H01-H44 = 44 / 44 PASS

A01-A10 = 10 / 10 EVIDENCE_READY

TECHNICAL_ACCEPTANCE_READINESS = PASS

Retain the machine-readable local audit artifact
required by V1.1 in the temporary proof workspace.

Do not commit that temporary audit artifact.

This result is technical readiness only.

It is NOT:

W04-C10 HUMAN ACCEPTANCE: ACCEPTED


==================================================
C10 STAGE B
==================================================

Only after the complete Stage-A and H01-H44/A01-A10
gates pass, create exactly:

docs/w04/checkpoints/c10/W04_C10_R_DEVELOPMENT_ROUND_REPORT.md

No second Stage-B path is authorized.

Exact Stage-B commit subject:

docs(w04-c10): publish business acceptance readiness proof

Stage B must be a direct child of Stage A.


==================================================
MANDATORY PRE-PUSH STAGE-B LIFECYCLE PROOF
==================================================

Create the Stage-B commit locally.

DO NOT PUSH YET.

Run the unchanged Bootstrap verifier against the
committed Stage-B HEAD.

It must PASS and report:

C10_REVIEW_READY

Also require:

Bootstrap verifier blob = unchanged

C09 final five governance files = unchanged

Stage-A eleven C10 files = unchanged

Stage-B delta =
exactly one added development-round report

git diff --check = PASS

If this proof fails:

STOP

W04_C10_STAGE_B_LIFECYCLE_FAILED

Do not amend automatically.
Do not push.
Return for GPT clarification.


==================================================
STAGE-B NATIVE CI
==================================================

Only after the local committed-head lifecycle proof passes,
perform one normal push.

Expected classification:

P / PUBLICATION_EXACT_SHA

Require:

Classify = SUCCESS
Publication proof = SUCCESS
Verification = SUCCESS

Static / Plan = SKIPPED
Integration / Data = SKIPPED
Shard 0..6 = SKIPPED
Aggregate = SKIPPED
Quality = SKIPPED
Compose = SKIPPED
W03 gate = SKIPPED
W04 gate = SKIPPED

overall = SUCCESS

If Stage-B native CI fails:

STOP

W04_C10_STAGE_B_CI_FAILED


==================================================
HARD PRODUCT BOUNDARIES
==================================================

PRODUCT_RUNTIME_CHANGE = NONE

Do NOT modify:

src/**
tests/**
.github/**
apps/**
migrations/**
pyproject.toml
uv.lock
docker-compose.yml

docs/w03/**

docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json

docs/w04/checkpoints/c01/**
docs/w04/checkpoints/c02/**
docs/w04/checkpoints/c03/**
docs/w04/checkpoints/c04/**
docs/w04/checkpoints/c05/**
docs/w04/checkpoints/c06/**
docs/w04/checkpoints/c07/**
docs/w04/checkpoints/c08/**
docs/w04/checkpoints/c09/**

docs/w04/devctrl/**
docs/w04/devctrl-02/**
docs/w04/devctrl-03/**

README.md
AGENTS.md
docs/CURRENT_STATE.md
docs/context/**
docs/sprints/**

Other than the explicitly authorized Bootstrap verifier,
do NOT modify scripts/**.

Do NOT modify:

workflow
classifier
publication verifier
W04 runner
planner
measured weights
timeouts
shard topology
test nodes
test parameterization


==================================================
SOURCE-EVOLUTION BOUNDARY
==================================================

Do NOT add C09 or C10 to:

docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json

C01-C08 must remain the exact eight CLOSED entries.

C09 = ABSENT BY DESIGN
C10 = ABSENT BY DESIGN


==================================================
BUSINESS ACCEPTANCE AUTHORITY
==================================================

Codex and GPT may establish only:

TECHNICAL_ACCEPTANCE_READINESS = PASS / FAIL

A01-A10 =
EVIDENCE_READY / EVIDENCE_GAP

Human assessment must remain:

PENDING_PRODUCT_OWNER_DECISION

Do not fill or auto-complete:

W04_C10_HUMAN_ACCEPTANCE_FORM.md

Do not infer:

W04-C10 HUMAN ACCEPTANCE: ACCEPTED


==================================================
STALE PROJECTION BOUNDARY
==================================================

README.md
docs/CURRENT_STATE.md
PR #7 title/body

are not authoritative current W04-state sources for C10.

Do not repair them in this task.

Use exact Git/PR state and accepted checkpoint/closeout
evidence as the authoritative current-state basis.


==================================================
NOT AUTHORIZED
==================================================

C10_CLOSEOUT = NOT AUTHORIZED

W04_SPRINT_CLOSEOUT = NOT AUTHORIZED

PR #7 READY = NOT AUTHORIZED

PR #7 MERGE = NOT AUTHORIZED

AUTO-MERGE = NOT AUTHORIZED

BRANCH DELETION = NOT AUTHORIZED

MAIN WRITE = NOT AUTHORIZED

POST-W04 IMPLEMENTATION = NOT AUTHORIZED

Do not edit PR #7 title/body.


==================================================
FAIL-CLOSED RULE
==================================================

Any V1.1 stop code means STOP.

DO NOT GUESS THE CONTRACT.
DO NOT WIDEN SCOPE.
DO NOT SILENTLY REPAIR SEMANTICS.
DO NOT AMEND.
DO NOT REBASE.
DO NOT RESET.
DO NOT FORCE PUSH.

A second pushed repair commit requires a new,
separate explicit Human repair authorization.


==================================================
EXPECTED TERMINAL HANDOFF
==================================================

After Stage-B native SUCCESS and final synchronization,
report:

W04_C10_REVIEW_READY

W04-C10 =
ACCEPTANCE EVIDENCE PREPARED /
CODEX VERIFIED /
PENDING GPT REVIEW

TECHNICAL_ACCEPTANCE_READINESS =
PASS

A01-A10 =
10 / 10 EVIDENCE_READY

H01-H44 =
44 / 44 PASS

BUSINESS_ACCEPTANCE =
PENDING PRODUCT OWNER DECISION

GPT_INDEPENDENT_C10_REVIEW =
PENDING

HUMAN_C10_ACCEPTANCE =
PENDING

C10_CLOSEOUT =
NOT AUTHORIZED

W04_SPRINT_CLOSEOUT =
NOT AUTHORIZED

PR #7 =
OPEN / DRAFT / UNMERGED

PR_READY =
NOT AUTHORIZED

PR_MERGE =
NOT AUTHORIZED

AUTO_MERGE =
NOT AUTHORIZED

BRANCH_DELETION =
NOT AUTHORIZED

MAIN_WRITE =
NOT AUTHORIZED

POST-W04_IMPLEMENTATION =
NOT AUTHORIZED

STOP.

Return the complete:

- Bootstrap SHA / verifier blob / CI run and classifier
- Stage-A SHA / CI run and classifier
- Stage-B SHA / CI run and classifier
- exact changed paths for every phase
- Bootstrap adversarial/source-span proof
- 2997/2994/3 result
- Integration 70
- W03 38/85
- W04 9/67/81
- H01-H44 results
- A01-A10 results
- C10_REVIEW_READY committed-head verifier result
- final four-head synchronization state
- all non-blocking observations

Do not self-review.
Do not begin C10 closeout.
Do not begin W04 sprint closeout.
Do not begin PR readiness or merge preparation.
```

## R1 clarification approval

Raw source SHA-256: `188a4efcbfa8a33b73f516a272755863e1686af4089240ae6dbb2ce8b3208e69`.

```text
W04-C10 BOOTSTRAP GPT CLARIFICATION R1: APPROVED

Execute exactly:

FLOWLENS_W04_C10_BOOTSTRAP_CLARIFICATION_R1.md

CLARIFICATION:
W04-C10-BOOTSTRAP-CLARIFICATION-R1

CLARIFICATION RAW SHA-256:
8438d86dd144728f8f8714eccacfaae47ba629fa0476cb34cb430b6b750d4d3c

Base contract remains:

FLOWLENS_W04_C10_CODEX_DEVELOPMENT_TASK_V1_1.md

BASE TASK VERSION:
W04-C10-A-V1.1

BASE TASK RAW SHA-256:
15f8c1ddd8a423edccb0fb2f927675b609a5b6177427f61e643bfb964c7314d4


==================================================
CURRENT STOP IS ACCEPTED
==================================================

Accepted stop:

W04_C10_BOOTSTRAP_REQUIRES_GPT_CLARIFICATION

Do NOT repair repository semantics yet.

Do NOT modify the failing test.

Do NOT modify the existing Bootstrap commit.


==================================================
FROZEN REAL BOOTSTRAP
==================================================

Existing local unpushed Bootstrap SHA:

a34a84b97681f24bf6df1fed1a80825ae32decfa

Required parent:

d33ee858fca8caaceba2ce60c045f7e4213c631a

Required subject:

ci(w04-c10): admit bounded acceptance lifecycle

Required sole delta:

M scripts/ci/verify_w04_investigation_gate_contract.py

Required verifier blob:

d93ac951544f4d25dbb90540ab11f887d8010e60

Required verifier raw SHA-256:

c9ce7e57278856541b202abc14652757a12b20d13b8a6db7469e694b55c50391

Do not amend, replace or recreate this commit.


==================================================
ACCEPTED PROOF FLOOR
==================================================

The following existing evidence is accepted:

Disposable candidate:
602 / 602 PASS
Ruff PASS
strict mypy PASS / 177 files
diff-check PASS
commit-diff-check PASS

Candidate verifier blob =
real Bootstrap verifier blob =
d93ac951544f4d25dbb90540ab11f887d8010e60

Real committed-head verifier:
PASS / C10_BOOTSTRAP_01

Legacy adversarial controls:
172 PASS

C10 adversarial controls:
32 PASS

Actual Bash truth cases:
223 PASS

Collection:
2997 nodes
63 files
7 shards

node digest:
9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a

weights digest:
a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851

Real Bootstrap read-only source-evolution diagnostic:
PASS


==================================================
UNRESOLVED FAILURE
==================================================

The previous real local suite observed F at:

tests/test_c09_ci_gate.py::
test_classifier_publication_and_runtime_frozen_materials_unchanged

However:

traceback = NOT GENERATED
JUnit = NOT GENERATED
root cause = UNCONFIRMED

Therefore this clarification does NOT classify the failure yet.

Do not assume CRLF.
Do not assume repository regression.

Diagnose it.


==================================================
PHASE 1 — EXACT FAILURE DIAGNOSIS
==================================================

Preserve primary HEAD and worktree unchanged.

Run the exact failing selector read-only with:

-vv
--tb=long
-p no:cacheprovider
--junitxml=<temporary path>

Use isolated TEMP/TMP.

Do not interrupt after observing F.
Capture the exact failing assertion and traceback.

Independently evaluate every assertion in that test.

For:

scripts/ci/verify_publication.py
pyproject.toml
uv.lock
docker-compose.yml

record:

HEAD blob OID
gate.ENTRY blob OID
filtered worktree hash
raw SHA-256
Path.read_text comparison against gate.ENTRY
LF/CRLF/CR counts
UTF-8 BOM presence
git attributes

Also record:

verify_source_evolution result
manifest committed blob
manifest filtered worktree hash
manifest raw SHA-256

git diff --name-status gate.ENTRY HEAD -- migrations apps

git status
core.autocrlf
core.eol
core.safecrlf

Classify the exact failed assertion as:

FROZEN_TEXT_COMPARISON
SOURCE_EVOLUTION
MIGRATIONS_APPS_DIFF
OTHER

If no exact root cause can be captured:

STOP

W04_C10_BOOTSTRAP_R1_ROOT_CAUSE_UNRESOLVED


==================================================
PHASE 2 — EXACT REAL-SHA CLEAN CLONE
==================================================

Create a NEW temporary full-history clone from the
current local repository.

Do not modify the primary checkout.

Before checkout configure the clone:

core.autocrlf = false
core.eol = lf

Checkout DETACHED exact:

a34a84b97681f24bf6df1fed1a80825ae32decfa

Require:

HEAD =
a34a84b97681f24bf6df1fed1a80825ae32decfa

worktree =
CLEAN

verifier blob =
d93ac951544f4d25dbb90540ab11f887d8010e60

No replacement commit may be created.


==================================================
PHASE 3 — EXACT COMMIT / TREE / SCOPE PROOF
==================================================

Require:

parent =
d33ee858fca8caaceba2ce60c045f7e4213c631a

subject =
ci(w04-c10): admit bounded acceptance lifecycle

delta =
M scripts/ci/verify_w04_investigation_gate_contract.py

Record:

real Bootstrap tree OID
entry tree OID
verifier blob OID

If the old disposable candidate object is still reachable,
also compare its tree OID against the real Bootstrap tree OID.

Candidate tree equality is supplementary only.


==================================================
PHASE 4 — EXACT SELECTOR ON REAL SHA
==================================================

In the LF full-history clone at exact a34a... run:

tests/test_c09_ci_gate.py::
test_classifier_publication_and_runtime_frozen_materials_unchanged

Require:

1 PASS

Retain stdout/stderr and JUnit.

If it fails:

STOP

W04_C10_BOOTSTRAP_R1_REAL_SHA_SELECTOR_FAILED

Do NOT repair.


==================================================
PHASE 5 — COMPLETE REAL-SHA LOCAL PROOF
==================================================

Only after the exact selector passes, run the COMPLETE
V1.1 Bootstrap local proof in the same exact-real-SHA clone.

Require:

602 / 602 PASS

Ruff PASS

strict mypy PASS

git diff --check HEAD^ HEAD PASS

verifier lifecycle =
C10_BOOTSTRAP_01

legacy controls =
172 PASS

C10 controls =
32 PASS

Bash truth =
223 PASS

2997 nodes
63 files
7 shards

node digest unchanged
weights digest unchanged
source-evolution PASS

The proof MUST be bound to:

a34a84b97681f24bf6df1fed1a80825ae32decfa

The old disposable candidate proof alone is not sufficient.


==================================================
CLASSIFICATION RULE
==================================================

You may classify:

ENVIRONMENT_ONLY_LOCAL_PROOF_VARIANCE

ONLY IF:

- exact real Bootstrap scope is correct
- real verifier/source-span proof passes
- exact selector passes at real SHA in LF clone
- complete 602 suite passes at real SHA in LF clone
- Ruff/mypy/diff-check pass
- protected identities remain unchanged
- zero tracked files changed during diagnosis

Retain the original Windows failure evidence.

Do not erase or rewrite it.


If exact-real-SHA clean clone reproduces the failure:

STOP

W04_C10_BOOTSTRAP_R1_REPOSITORY_OR_CONTRACT_FAILURE

Return to GPT.
No repair is authorized.


==================================================
CONDITIONAL PUSH AUTHORIZATION
==================================================

If and only if:

W04_C10_BOOTSTRAP_R1_DIAGNOSTIC = PASS

CLASSIFICATION =
ENVIRONMENT_ONLY_LOCAL_PROOF_VARIANCE

REAL_SHA_CLEAN_CLONE_COMPLETE_PROOF =
PASS

then I authorize ONE normal push of the EXISTING,
UNCHANGED commit:

a34a84b97681f24bf6df1fed1a80825ae32decfa

Immediately before push require primary:

HEAD =
a34a84b97681f24bf6df1fed1a80825ae32decfa

worktree/index =
CLEAN

ahead/behind =
1/0

verifier blob =
d93ac951544f4d25dbb90540ab11f887d8010e60

NO new commit.
NO amend.
NO rebase.
NO reset.
NO force push.


==================================================
BOOTSTRAP NATIVE CI
==================================================

After the one allowed push, resume the existing V1.1
Bootstrap own-SHA native-CI gate.

Expected native classification:

C / FULL_EXACT_SHA

Require complete full-route SUCCESS and the original
V1.1 proof envelope.

If native CI fails:

STOP

W04_C10_BOOTSTRAP_CI_FAILED

Do not rerun as substitute proof.
Do not create a repair commit.


==================================================
STAGE A REMAINS LOCKED
==================================================

Do NOT begin C10 Stage A until:

Bootstrap pushed
AND
Bootstrap own-SHA native CI SUCCESS
AND
classifier C / FULL_EXACT_SHA
AND
fresh four-head synchronization PASS

Then resume V1.1 exactly from Stage A.


==================================================
HARD BOUNDARIES
==================================================

NO tracked-file mutation during clarification

NO test modification

NO C09 modification

NO source-evolution modification

NO workflow modification

NO runtime/source modification

NO new commit

NO amend

NO rebase

NO reset

NO force push

NO automatic repair

NO Stage A before Bootstrap native SUCCESS

NO Human C10 acceptance

NO C10 closeout

NO W04 sprint closeout

NO PR-ready

NO PR merge

NO branch deletion

NO main write


==================================================
RETURN
==================================================

Before push, produce:

W04_C10_BOOTSTRAP_R1_DIAGNOSTIC

STOPPED_FAILURE_EXACT_ASSERTION = ...
PRIMARY_ENVIRONMENT_FACTS = ...

REAL_BOOTSTRAP_SHA =
a34a84b97681f24bf6df1fed1a80825ae32decfa

REAL_BOOTSTRAP_TREE_OID = ...

REAL_VERIFIER_BLOB =
d93ac951544f4d25dbb90540ab11f887d8010e60

REAL_SHA_SELECTOR =
PASS / FAIL

REAL_SHA_COMPLETE_SUITE =
602/602 PASS or FAIL

RUFF =
PASS / FAIL

MYPY =
PASS / FAIL

DIFF_CHECK =
PASS / FAIL

CLASSIFICATION =
ENVIRONMENT_ONLY_LOCAL_PROOF_VARIANCE
or
REPOSITORY_OR_CONTRACT_FAILURE

TRACKED_FILE_MUTATION_DURING_DIAGNOSIS =
NONE

PUSH_AUTHORIZED_BY_R1 =
YES / NO

If YES, perform the one authorized normal push,
wait for native CI, and return the native run,
classifier, job results and synchronization state.

If NO, STOP and return to GPT.
```

## R2 clarification approval

Raw source SHA-256: `1e53f1b6cc724a5ffaf24e65fd46751d323a117e1de55ae3970099b44bf9b303`.

```text
W04-C10 BOOTSTRAP GPT CLARIFICATION R2: APPROVED

Execute exactly:

FLOWLENS_W04_C10_BOOTSTRAP_CLARIFICATION_R2.md

THIS CLARIFICATION:
W04-C10-BOOTSTRAP-CLARIFICATION-R2

R2 RAW SHA-256:
d1b57a41a7f71f994256be719feaa21f21b552ee4b53ad1c0549a87f1dc75e44

Base task remains:

FLOWLENS_W04_C10_CODEX_DEVELOPMENT_TASK_V1_1.md

BASE TASK VERSION:
W04-C10-A-V1.1

BASE TASK RAW SHA-256:
15f8c1ddd8a423edccb0fb2f927675b609a5b6177427f61e643bfb964c7314d4

Prior clarification remains accepted evidence:

FLOWLENS_W04_C10_BOOTSTRAP_CLARIFICATION_R1.md

R1 RAW SHA-256:
8438d86dd144728f8f8714eccacfaae47ba629fa0476cb34cb430b6b750d4d3c


==================================================
ACCEPT R1 STOP
==================================================

Accepted previous stop:

W04_C10_BOOTSTRAP_R1_ROOT_CAUSE_UNRESOLVED

Do NOT erase, rewrite or downgrade the original F.

R1 established:

primary standalone selector = 1 PASS
retained real-SHA standalone selector = 1 PASS

four frozen text comparisons = PASS
source evolution = PASS
migrations/apps diff = EMPTY
source-span proof = PASS
protected Git identities = PASS
tracked-file mutation = NONE

The original full-suite F remains preserved but
its exact assertion was not reproduced.

This is NOT permission to repair.


==================================================
FROZEN REAL BOOTSTRAP
==================================================

REAL_BOOTSTRAP_SHA:

a34a84b97681f24bf6df1fed1a80825ae32decfa

PARENT:

d33ee858fca8caaceba2ce60c045f7e4213c631a

SUBJECT:

ci(w04-c10): admit bounded acceptance lifecycle

TREE:

2a647344aee164e84745db8b1de5219d0c366543

VERIFIER BLOB:

d93ac951544f4d25dbb90540ab11f887d8010e60

VERIFIER RAW SHA-256:

c9ce7e57278856541b202abc14652757a12b20d13b8a6db7469e694b55c50391

SOLE COMMIT DELTA:

M scripts/ci/verify_w04_investigation_gate_contract.py


Do not modify, amend, replace or recreate this commit.


==================================================
R2 PURPOSE
==================================================

R2 authorizes controlled whole-suite reproduction.

It supersedes only the R1 rule that blocked the
new LF exact-real-SHA clone when the original F
could not be reproduced standalone.

No repository repair is authorized.


==================================================
PHASE A — PRIMARY COMPLETE 602-SUITE
==================================================

At exact:

a34a84b97681f24bf6df1fed1a80825ae32decfa

run the exact V1.1 suite in its original file order:

tests/test_ci_change_classifier.py
tests/test_ci_publication_gate.py
tests/test_ci_test_sharding.py
tests/test_c09_ci_gate.py
tests/test_investigation_replay.py
tests/test_w04_source_evolution.py

Do not reorder.

Do not use xdist.

Do not use --lf / --ff / cache.

Before running, collect the exact ordered 602 node IDs
and SHA-256 the ordered node list.

Require:

602 collected.

Run once using:

-vv
--tb=long
-p no:cacheprovider
--junitxml=<temporary R2 path>
--basetemp=<isolated R2 temp>

with isolated TEMP/TMP.

DO NOT Ctrl-C after observing F.

If failure occurs, allow pytest to produce the exact
traceback/JUnit and record the exact assertion.

Do NOT repair.

If the complete suite passes, record:

PRIMARY_FULL_SUITE = 602 / 602 PASS

This pass alone is not substitute acceptance proof.


==================================================
PHASE B — RETAINED REAL-SHA CHECKOUT
==================================================

If the retained R1 real-SHA checkout is still provably:

HEAD =
a34a84b97681f24bf6df1fed1a80825ae32decfa

tree =
2a647344aee164e84745db8b1de5219d0c366543

verifier blob =
d93ac951544f4d25dbb90540ab11f887d8010e60

worktree CLEAN

then run the exact same ordered 602-suite once.

If the retained checkout cannot be independently
validated, mark it UNAVAILABLE.

Do not trust an ambiguous retained checkout.


==================================================
PHASE C — NEW LF FULL-HISTORY REAL-SHA CLONE
==================================================

Create a NEW temporary full-history clone from the
current local repository.

Do not modify the primary checkout.

Inside that new clone set before checkout:

core.autocrlf = false
core.eol = lf

Checkout detached exact:

a34a84b97681f24bf6df1fed1a80825ae32decfa

Require:

HEAD =
a34a84b97681f24bf6df1fed1a80825ae32decfa

TREE =
2a647344aee164e84745db8b1de5219d0c366543

VERIFIER BLOB =
d93ac951544f4d25dbb90540ab11f887d8010e60

WORKTREE =
CLEAN


Run the R1 assertion diagnostic again.

Run standalone:

tests/test_c09_ci_gate.py::
test_classifier_publication_and_runtime_frozen_materials_unchanged

Require:

1 PASS


Then run the exact ordered 602-suite.

Also run:

python -B scripts/ci/verify_w04_investigation_gate_contract.py

python -B -m ruff check .

python -B -m mypy .

git diff --check HEAD^ HEAD


Require:

602 / 602 PASS

Ruff PASS

strict mypy PASS

diff-check PASS

C10_BOOTSTRAP_01

172 legacy controls PASS

32 C10 controls PASS

223 Bash truth cases PASS

2997 nodes

63 files

7 shards

node digest =
9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a

weights digest =
a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851

source evolution PASS


If this clean exact-real-SHA proof fails:

STOP:

W04_C10_BOOTSTRAP_R2_REAL_SHA_CLEAN_CLONE_FAILED

NO repair.
NO push.


==================================================
OPTIONAL ORDER-INTERACTION DIAGNOSIS
==================================================

Only if:

PRIMARY COMPLETE SUITE FAILS

AND

NEW LF REAL-SHA COMPLETE SUITE PASSES

perform read-only bounded prefix/bisection diagnostics
to determine whether preceding tests/modules are required
to reproduce:

tests/test_c09_ci_gate.py::
test_classifier_publication_and_runtime_frozen_materials_unchanged

Do not edit tests.

Do not edit repository files.

Record any minimal reproducing prefix and exact assertion.


==================================================
CLASSIFICATION
==================================================

Use exactly one classification.


1.

REPOSITORY_OR_CONTRACT_FAILURE

if the new LF exact-real-SHA clone fails any required
selector/suite/verifier/source/identity proof.

PUSH_AUTHORIZED_BY_R2 = NO


2.

CHECKOUT_OR_PROCESS_ENVIRONMENT_VARIANCE

only if the primary failure is reproducible with an
exact assertion, while at least two independently
validated exact-real-SHA clean contexts PASS and
the difference is attributable to environment or
process/test-order state.


3.

NONREPRODUCIBLE_LOCAL_EXECUTION_ANOMALY

only if all are true:

R1 standalone primary = PASS
R1 standalone retained = PASS

R2 primary complete 602 = PASS

R2 new LF real-SHA standalone = PASS
R2 new LF real-SHA 602 = PASS

R2 verifier = PASS
Ruff = PASS
mypy = PASS
diff-check = PASS
source evolution = PASS

ordered 602-node digest identical

real Bootstrap identities unchanged

protected Git identities PASS

tracked-file mutation = NONE

If retained Phase B was available, it must PASS too.

The original F must remain recorded.

Do not claim its root cause was discovered.


4.

UNRESOLVED_INCONSISTENT_EVIDENCE

for all other result patterns.

PUSH_AUTHORIZED_BY_R2 = NO


==================================================
CONDITIONAL PUSH AUTHORIZATION
==================================================

Only classifications:

CHECKOUT_OR_PROCESS_ENVIRONMENT_VARIANCE

or

NONREPRODUCIBLE_LOCAL_EXECUTION_ANOMALY

may authorize continuation.

The new LF exact-real-SHA complete proof MUST PASS.

Then I authorize exactly ONE normal push of the
EXISTING unchanged Bootstrap commit:

a34a84b97681f24bf6df1fed1a80825ae32decfa

Immediately before push require:

HEAD =
a34a84b97681f24bf6df1fed1a80825ae32decfa

tree =
2a647344aee164e84745db8b1de5219d0c366543

verifier blob =
d93ac951544f4d25dbb90540ab11f887d8010e60

worktree/index =
CLEAN

ahead/behind =
1/0

NO new commit.
NO amend.
NO rebase.
NO reset.
NO force push.


==================================================
NATIVE CI
==================================================

After that single allowed normal push, wait for the
native CI bound to exact:

a34a84b97681f24bf6df1fed1a80825ae32decfa

Require:

attempt 1
SUCCESS

classifier:

C / FULL_EXACT_SHA

Require all V1.1 mandatory full-route proof.

Do not manually rerun as substitute proof.


If native CI fails:

STOP:

W04_C10_BOOTSTRAP_NATIVE_CI_FAILED

Do not repair.


==================================================
STAGE A
==================================================

Stage A remains locked until:

R2 classification accepted
AND
new LF exact-real-SHA complete proof PASS
AND
existing Bootstrap SHA pushed unchanged
AND
Bootstrap native CI attempt 1 SUCCESS
AND
classifier C / FULL_EXACT_SHA
AND
local/tracking/direct-origin/PR HEAD all equal a34a...
AND
ahead/behind 0/0
AND
worktree/index CLEAN


Only then resume original V1.1 at C10 Stage A.


==================================================
HARD BOUNDARIES
==================================================

NO tracked-file changes

NO test edits

NO workflow edits

NO source/runtime edits

NO C09 edits

NO manifest edits

NO new commit

NO amend

NO rebase

NO reset

NO force push

NO automatic repair

NO Stage A before Bootstrap native SUCCESS

NO Human C10 acceptance

NO C10 closeout

NO W04 closeout

NO PR ready/merge

NO branch deletion

NO main write


==================================================
RETURN
==================================================

Before any push return:

W04_C10_BOOTSTRAP_R2_DIAGNOSTIC

REAL_BOOTSTRAP_SHA =
a34a84b97681f24bf6df1fed1a80825ae32decfa

REAL_BOOTSTRAP_TREE =
2a647344aee164e84745db8b1de5219d0c366543

REAL_VERIFIER_BLOB =
d93ac951544f4d25dbb90540ab11f887d8010e60

R1_ORIGINAL_F =
PRESERVED

R1_STANDALONE_PRIMARY =
1 PASS

R1_STANDALONE_RETAINED =
1 PASS

PRIMARY_ORDERED_COLLECTION =
602 / <sha256>

PRIMARY_FULL_SUITE =
PASS / FAIL

PRIMARY_EXACT_FAILURE =
<assertion or NONE>

RETAINED_FULL_SUITE =
PASS / FAIL / UNAVAILABLE

NEW_LF_REAL_SHA_SELECTOR =
PASS / FAIL

NEW_LF_ORDERED_COLLECTION =
602 / <sha256>

NEW_LF_FULL_SUITE =
PASS / FAIL

NEW_LF_VERIFIER =
PASS / FAIL

RUFF =
PASS / FAIL

MYPY =
PASS / FAIL

DIFF_CHECK =
PASS / FAIL

SOURCE_EVOLUTION =
PASS / FAIL

CLASSIFICATION =
REPOSITORY_OR_CONTRACT_FAILURE
or
CHECKOUT_OR_PROCESS_ENVIRONMENT_VARIANCE
or
NONREPRODUCIBLE_LOCAL_EXECUTION_ANOMALY
or
UNRESOLVED_INCONSISTENT_EVIDENCE

TRACKED_FILE_MUTATION_R2 =
NONE

PUSH_AUTHORIZED_BY_R2 =
YES / NO

If YES:
perform the single authorized normal push,
wait for native CI,
and return native run/classifier/jobs/synchronization.

If NO:
STOP and return to GPT.
```

## Continuation V1 approval

Raw source SHA-256: `e477b62e339617f15b9fcf772fc910f8d2d64e725ddff25c5adde584b82d0756`.

```text
W04-C10 CONTINUATION AUTHORIZATION: APPROVED

Resume and execute exactly:

FLOWLENS_W04_C10_CONTINUATION_TASK_V1.md

TASK VERSION:
W04-C10-CONTINUATION-V1

TASK RAW SHA-256:
7cd20e05b5eac4350d9fcfdf02bec6cd59daaaa345d30fa748e108ed86bbcc8b


BASE CONTRACT:

FLOWLENS_W04_C10_CODEX_DEVELOPMENT_TASK_V1_1.md

BASE RAW SHA-256:
15f8c1ddd8a423edccb0fb2f927675b609a5b6177427f61e643bfb964c7314d4


R1:

FLOWLENS_W04_C10_BOOTSTRAP_CLARIFICATION_R1.md

R1 RAW SHA-256:
8438d86dd144728f8f8714eccacfaae47ba629fa0476cb34cb430b6b750d4d3c


R2:

FLOWLENS_W04_C10_BOOTSTRAP_CLARIFICATION_R2.md

R2 RAW SHA-256:
d1b57a41a7f71f994256be719feaa21f21b552ee4b53ad1c0549a87f1dc75e44


==================================================
RESUME — DO NOT RESTART BLINDLY
==================================================

This is a continuation after model/capacity interruption.

First locate the existing R2 temporary proof workspace.

Do NOT rerun completed phases merely because the
conversation/session was interrupted.

Inventory and SHA-256 all existing proof artifacts.

A completed phase is valid only when its generated:

receipt
JUnit
stdout/stderr
result JSON
identity snapshot

exists, parses, is bound to the exact Bootstrap
SHA/tree/blob, and proves zero tracked-file mutation.

If an evidence artifact is missing, resume from the
earliest incomplete phase.

Do NOT manufacture evidence from source-code assertions.


==================================================
FROZEN BOOTSTRAP
==================================================

Existing unpushed Bootstrap SHA:

a34a84b97681f24bf6df1fed1a80825ae32decfa

Parent:

d33ee858fca8caaceba2ce60c045f7e4213c631a

Subject:

ci(w04-c10): admit bounded acceptance lifecycle

Tree:

2a647344aee164e84745db8b1de5219d0c366543

Verifier blob:

d93ac951544f4d25dbb90540ab11f887d8010e60

Verifier raw SHA-256:

c9ce7e57278856541b202abc14652757a12b20d13b8a6db7469e694b55c50391

Sole Bootstrap delta:

M scripts/ci/verify_w04_investigation_gate_contract.py


DO NOT:

modify it
amend it
replace it
recreate it
create Repair-01


==================================================
REMOTE ENTRY
==================================================

Before Bootstrap push require remote:

tracking HEAD =
direct-origin HEAD =
PR #7 HEAD =

d33ee858fca8caaceba2ce60c045f7e4213c631a


main/base:

af61bdfd5f7cf7961811c4c2dc8e554dd7eed509


PR #7:

OPEN / DRAFT / UNMERGED


entry CI:

#140 / 38436850640 / SUCCESS / attempt 1


primary local:

ahead/behind = 1/0
worktree/index = CLEAN


If any context changed:

STOP:

W04_C10_CONTINUATION_CONTEXT_DRIFT


==================================================
R2 PROOF RULE
==================================================

The source code of:

build_r2_diagnostic.py
run_r2_suite.py
r2_receipt.py
context-lock-r2.json

is NOT proof of the outcomes encoded in those files.

Only generated execution evidence counts.

Require the real:

suite-result JSONs
ordered-node receipts
JUnit XML
stdout/stderr
new-LF complete proof
independent adjudication
protected-identity audit
source-span proof
source-evolution proof
final r2-diagnostic JSON/MD


==================================================
R2 COLLECTION
==================================================

Exact ordered suite:

tests/test_ci_change_classifier.py
tests/test_ci_publication_gate.py
tests/test_ci_test_sharding.py
tests/test_c09_ci_gate.py
tests/test_investigation_replay.py
tests/test_w04_source_evolution.py


Require:

602 nodes

ordered digest:

0992906515ae9f5dfc463d9f55902538570586f3e2fd08c262af0b18b319002c


All compared contexts must have the same digest.


==================================================
R2 ACCEPTABLE RESULT
==================================================

Require new LF exact-real-SHA proof:

HEAD =
a34a84b97681f24bf6df1fed1a80825ae32decfa

tree =
2a647344aee164e84745db8b1de5219d0c366543

verifier blob =
d93ac951544f4d25dbb90540ab11f887d8010e60

standalone selector =
PASS

complete suite =
602 / 602 PASS

verifier =
PASS / C10_BOOTSTRAP_01

Ruff =
PASS

strict mypy =
PASS

diff-check =
PASS

source evolution =
PASS

legacy adversarial controls =
172 PASS

C10 controls =
32 PASS

Bash truth =
223 PASS

2997 nodes
63 files
7 shards

node digest =
9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a

weights digest =
a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851


==================================================
WINDOWS PRIMARY FAILURE
==================================================

If the primary Windows complete suite reproduces only:

tests/test_c09_ci_gate.py::
test_frozen_manifest_schema_families_counts_and_content

with raw manifest SHA mismatch, retain that failure.

Do not modify:

.gitattributes
test_c09_ci_gate.py
C09 manifest
W03 gate
workflow
global Git config


If exact Git identities are unchanged and clean LF
exact-SHA contexts pass, record:

NB-C10-ENV-01

C09 frozen raw-byte manifest assertion is
checkout-line-ending sensitive in the primary Windows
worktree; committed Git identity and clean LF/native
Linux proof remain authoritative.

Do NOT classify it as a product regression.


==================================================
R2G GATE
==================================================

Require:

R2G01 Bootstrap identity exact
R2G02 verifier identity exact
R2G03 sole delta exact
R2G04 original R1 evidence preserved
R2G05 ordered 602 identity frozen
R2G06 generated evidence exists
R2G07 new LF standalone PASS
R2G08 new LF 602 PASS
R2G09 verifier/Ruff/mypy/diff/source proof PASS
R2G10 source-span/protected identities PASS
R2G11 zero tracked mutation
R2G12 allowed R2 classification

R2G01-R2G12 =
12 / 12 PASS


Allowed classifications:

CHECKOUT_OR_PROCESS_ENVIRONMENT_VARIANCE

or

NONREPRODUCIBLE_LOCAL_EXECUTION_ANOMALY


The following MUST STOP:

REPOSITORY_OR_CONTRACT_FAILURE

UNRESOLVED_INCONSISTENT_EVIDENCE


==================================================
BOOTSTRAP PUSH
==================================================

Only after R2 and R2G01-R2G12 PASS:

recheck primary:

HEAD =
a34a84b97681f24bf6df1fed1a80825ae32decfa

tree =
2a647344aee164e84745db8b1de5219d0c366543

verifier blob =
d93ac951544f4d25dbb90540ab11f887d8010e60

worktree/index =
CLEAN

ahead/behind =
1/0


Then perform exactly ONE normal push of the
EXISTING unchanged Bootstrap commit.

NO new commit.
NO amend.
NO rebase.
NO reset.
NO force push.


==================================================
BOOTSTRAP NATIVE CI
==================================================

Wait for native CI on exact:

a34a84b97681f24bf6df1fed1a80825ae32decfa

Require:

attempt 1
SUCCESS

classifier:

C / FULL_EXACT_SHA


Require complete full route:

Classify SUCCESS
Static/Plan SUCCESS
Integration/Data SUCCESS
Shard 0..6 SUCCESS
Aggregate SUCCESS
Quality SUCCESS
Compose SUCCESS
W03 SUCCESS
W04 SUCCESS
Verification SUCCESS
Publication SKIPPED


Require:

2997 selected
2994 passed
3 accepted skipped

zero failed/error/xfail/xpass

entry no-loss PASS
exact union PASS
exact once PASS

Integration 70 PASS
W03 38 / 85 PASS
W04 9 / 67 / 81 PASS

lifecycle =
C10_BOOTSTRAP_01


Native GitHub CI is authoritative over local Windows
raw-byte checkout representation.


If native CI fails:

STOP:

W04_C10_BOOTSTRAP_NATIVE_CI_FAILED


==================================================
STAGE A UNLOCK
==================================================

Only after native Bootstrap SUCCESS require:

local HEAD =
tracking HEAD =
direct-origin HEAD =
PR #7 HEAD =
a34a84b97681f24bf6df1fed1a80825ae32decfa

ahead/behind =
0/0

worktree/index =
CLEAN


Then:

STAGE_A_UNLOCKED = YES


==================================================
C10 STAGE A
==================================================

Resume the original V1.1 contract.

Create exactly the eleven authorized C10 Stage-A paths.

No existing repository path may change.

Bootstrap verifier must remain byte-identical.

Exact subject:

docs(w04-c10): prepare investigation business acceptance

One normal commit.
One normal push.


Expected native classification:

C / FULL_EXACT_SHA

Require attempt 1 full-route SUCCESS.


==================================================
C10 ACCEPTANCE READINESS
==================================================

Preserve V1.1 exactly:

A01-A10 in frozen order

W01-W08 in frozen order

BIND
PLAN
NAVIGATE
FIND
CONFLICT
REVIEW
SUMMARIZE
REPLAY
REGRESS
PROTECT


Every Human judgement remains:

PENDING_PRODUCT_OWNER_DECISION


Require after Stage-A CI:

H01-H44 =
44 / 44 PASS

A01-A10 =
10 / 10 EVIDENCE_READY

R2G01-R2G12 =
12 / 12 PASS

TECHNICAL_ACCEPTANCE_READINESS =
PASS


Do NOT fill the Human Acceptance Form.


==================================================
C10 STAGE B
==================================================

Only after all previous gates pass create exactly:

docs/w04/checkpoints/c10/
W04_C10_R_DEVELOPMENT_ROUND_REPORT.md

Exact subject:

docs(w04-c10): publish business acceptance readiness proof


Before Stage-B push:

run the unchanged Bootstrap verifier against the
committed Stage-B HEAD.

Require:

C10_REVIEW_READY

Stage-B delta =
exactly one added report

git diff --check =
PASS


Then one normal push.


Expected native classification:

P / PUBLICATION_EXACT_SHA

Require:

Classify SUCCESS
Publication SUCCESS
Verification SUCCESS

all heavy/full jobs SKIPPED
W03 SKIPPED
W04 SKIPPED

attempt 1
overall SUCCESS


==================================================
FINAL STATE
==================================================

Require final:

local HEAD =
tracking HEAD =
direct-origin HEAD =
PR #7 HEAD =
Stage-B SHA

ahead/behind =
0/0

worktree/index =
CLEAN

main/base unchanged

PR #7 =
OPEN / DRAFT / UNMERGED


Return:

W04_C10_REVIEW_READY

BOOTSTRAP_R2 = PASS
BOOTSTRAP_NATIVE_CI = PASS
R2G01-R2G12 = 12/12 PASS
H01-H44 = 44/44 PASS
A01-A10 = 10/10 EVIDENCE_READY

TECHNICAL_ACCEPTANCE_READINESS = PASS

BUSINESS_ACCEPTANCE =
PENDING PRODUCT OWNER DECISION

GPT_INDEPENDENT_C10_REVIEW =
PENDING

HUMAN_C10_ACCEPTANCE =
PENDING

C10_CLOSEOUT =
NOT AUTHORIZED

W04_SPRINT_CLOSEOUT =
NOT AUTHORIZED

PR #7 =
OPEN / DRAFT / UNMERGED

PR_READY / PR_MERGE / AUTO_MERGE =
NOT AUTHORIZED

BRANCH_DELETION / MAIN_WRITE =
NOT AUTHORIZED

POST-W04_IMPLEMENTATION =
NOT AUTHORIZED


STOP.

Return the full evidence bundle to ChatGPT for
independent deep C10 review.

Do NOT begin C10 closeout.
```
