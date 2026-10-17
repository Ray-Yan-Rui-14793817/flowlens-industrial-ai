# W04 Sprint Human Acceptance and Authorization

Original Human authority source raw SHA-256: `e165fa2945ce0cf0c8fc230cb5faf5f65d7ce3021af8817bd0830168a61a3f5d`.

The complete original authorization follows verbatim with repository LF line endings. Original CRLF bytes are preserved in the evidence ZIP at inputs/HUMAN_AUTHORIZATION_RAW.txt. This is the original Sprint acceptance/closeout and PR-readiness authority; the resume message is a continuation and is not substituted for it. Merge, main write and W05 authority remain ungranted.

<!-- ORIGINAL_HUMAN_MESSAGE_BEGIN -->
````text
W04 SPRINT FINAL CLOSEOUT + PR #7 READINESS
HUMAN AUTHORIZATION: APPROVED


Execute exactly:

FLOWLENS_W04_SPRINT_FINAL_CLOSEOUT_PR7_READINESS_TASK_V1.md

TASK VERSION:

W04-SPRINT-FINAL-CLOSEOUT-PR7-READINESS-V1

TASK RAW SHA-256:

6648278c758ab4c73d18615c405c2280b84ab43ded08a45a3ccb354496a3455f


Use the supplied independent GPT review:

FLOWLENS_W04_SPRINT_FINAL_REVIEW_R1.md

GPT REVIEW RAW SHA-256:

061fc3f41659499fc7e1069345abe7b1d0feeab65504eb79e48b6a929665de59


Repository:

Ray-Yan-Rui-14793817/flowlens-industrial-ai

Branch:

feat/w04-evidence-investigation

PR:

#7


==================================================
HUMAN ACCEPTANCE
==================================================

I have reviewed the completed W04 C01-C10 development,
the C10 Final Closeout,
the W04 deep review,
and the W04 Sprint Final Closeout / PR Readiness design.

I explicitly accept:

W04_SPRINT_FINAL_REVIEW = ACCEPTED

W04_CORE_IMPLEMENTATION = PASS

W04_C01_C10 = CLOSED / VERIFIED

W04_SPRINT_CLOSEOUT_DESIGN = PASS

IMPLEMENTATION_REPAIR_REQUIRED = NO


I explicitly authorize:

W04_SPRINT_CLOSEOUT_AUTHORIZATION = APPROVED

PR7_READINESS_AUTHORIZATION = APPROVED


This authorization DOES NOT authorize:

PR #7 merge

auto-merge

merge queue

branch deletion

main write

W05 implementation

post-W04 implementation


==================================================
FROZEN ENTRY
==================================================

Require exactly:

C10 FINAL HEAD:

232bfb390babce30417b8cdb9a6660663eb3c3f1


C10 final native CI:

#145 / 38709171796

SUCCESS / attempt 1

C / FULL_EXACT_SHA


main/base:

af61bdfd5f7cf7961811c4c2dc8e554dd7eed509


PR #7:

OPEN / DRAFT / UNMERGED

mergeable = TRUE


local / tracking / direct-origin / PR HEAD:

232bfb390babce30417b8cdb9a6660663eb3c3f1


ahead/behind:

0/0


worktree/index:

CLEAN


If any identity changed:

STOP:

W04_SPRINT_FINAL_CONTEXT_DRIFT


==================================================
PHASE 0 — READ-ONLY FINAL AUDIT
==================================================

Before any repository mutation:

verify all C01-C08 frozen source identities.

Verify:

docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json

is byte-identical and unchanged.

Verify C09/C10 remain governance-only and introduce
no new source-evolution entry.


Reconfirm accepted engineering proof:

2997 selected
2994 passed
3 accepted Linux skipped

0 failed
0 error
0 xfail
0 xpass

entry no-loss PASS
exact union PASS
exact once PASS

Integration 70 PASS

W03:
38 selectors / 85 cases PASS

W04:
9 families / 67 selectors / 81 cases PASS


==================================================
SECURITY / SECRET READINESS
==================================================

Perform a read-only current-tree and reachable-history
security scan.

Do NOT add a new repository dependency.

Check at minimum for:

private key material

tracked .env files

known GitHub token prefixes

AWS access-key prefixes

Slack token prefixes

OpenAI/API-key style prefixes

other high-confidence live credential material


Do NOT print full candidate secret values.


The previously observed Generic Password in local
Docker Compose / PostgreSQL configuration may only be
classified as:

DEVELOPMENT_TEST_DEFAULT / NON-EXTERNAL

if inspection proves that it is only a local/test
fallback and does not authenticate an external service.


If any candidate could be a live external credential
or private key:

STOP:

W04_SPRINT_FINAL_SECURITY_INCIDENT


Do NOT rewrite history automatically.


==================================================
PHASE 1 — SPRINT CLOSEOUT PREP
==================================================

Current verifier intentionally rejects commits after:

C10_FINAL_CLOSEOUT


Therefore implement the bounded lifecycle:

C10_FINAL_CLOSEOUT

->

W04_SPRINT_CLOSEOUT_PREP_01

->

W04_SPRINT_FINAL_CLOSEOUT


Phase 1 may modify exactly:

scripts/ci/verify_w04_investigation_gate_contract.py


No second path.


Exact subject:

ci(w04): admit sprint closeout lifecycle


Parent:

232bfb390babce30417b8cdb9a6660663eb3c3f1


Preserve all previous:

C09 lifecycle controls
C10 lifecycle controls
C10 Repair-01 audit
C08 replay controls
C09 meta-CI controls
source-span guards
self-source guards
source-evolution guards
collection semantics
node/weight identities


Do NOT weaken any existing gate.


==================================================
PHASE 1 DISPOSABLE PROOF
==================================================

Build a NEW disposable full-history LF candidate.

Require:

exact parent

exact one-path delta

exact subject

git diff --check PASS

Ruff PASS

strict mypy PASS

source-span/self-source PASS

source-evolution PASS

committed-head verifier:

W04_SPRINT_CLOSEOUT_PREP_01


Run the protected ordered suite:

tests/test_ci_change_classifier.py

tests/test_ci_publication_gate.py

tests/test_ci_test_sharding.py

tests/test_c09_ci_gate.py

tests/test_investigation_replay.py

tests/test_w04_source_evolution.py


Require:

602 collected

ordered digest:

0992906515ae9f5dfc463d9f55902538570586f3e2fd08c262af0b18b319002c

602 / 602 PASS

tracked-file mutation NONE


If any local proof fails:

STOP:

W04_SPRINT_CLOSEOUT_PREP_LOCAL_PROOF_FAILED


No automatic repair.


==================================================
PHASE 1 REAL PREP
==================================================

Only after local candidate PASS:

revalidate primary

apply exact proven verifier bytes

create ONE normal commit

perform ONE normal push


Require native:

C / FULL_EXACT_SHA

attempt 1

SUCCESS


Require:

2997 / 2994 / 3

0 adverse outcomes

entry no-loss PASS

exact union PASS

exact once PASS

Integration 70

W03 38/85

W04 9/67/81

W04_SPRINT_CLOSEOUT_PREP_01 PASS

all shard job and pytest durations <3300 seconds


If native Prep fails:

STOP.

Do not rerun as substitute proof.


==================================================
PHASE 2 — SPRINT FINAL CLOSEOUT
==================================================

Only after Prep native SUCCESS.


Final commit may modify exactly:

README.md

AGENTS.md

docs/CURRENT_STATE.md


and may add exactly:

docs/w04/W04_GPT_INDEPENDENT_DEEP_REVIEW_R1.md

docs/w04/W04_SPRINT_HUMAN_ACCEPTANCE_AND_AUTHORIZATION.md

docs/w04/W04_SPRINT_CLOSEOUT_CONTEXT_LOCK.md

docs/w04/W04_SPRINT_FINAL_CLOSEOUT_REPORT.md

docs/w04/W04_PR7_READINESS_REPORT.md


Exactly 8 paths total.

No ninth path.


Exact subject:

docs(w04): close sprint and prepare PR #7 review


==================================================
GPT REVIEW RECORD
==================================================

The repository copy of:

W04_GPT_INDEPENDENT_DEEP_REVIEW_R1.md

must be byte-identical to the supplied review.

Required SHA-256:

061fc3f41659499fc7e1069345abe7b1d0feeab65504eb79e48b6a929665de59


==================================================
HUMAN AUTHORITY RECORD
==================================================

Preserve this entire Human authorization message
verbatim in:

docs/w04/
W04_SPRINT_HUMAN_ACCEPTANCE_AND_AUTHORIZATION.md


Record its raw SHA-256.

Do not replace it with a Codex summary.


==================================================
README
==================================================

Update README so it truthfully states:

W04 C01-C10 implemented / verified / closed

C07 summary implemented

C08 protected replay implemented

C09 regression hardening implemented

C10 business acceptance completed

W04 remains:

OFFLINE
SHADOW
HUMAN-IN-THE-LOOP
DETERMINISTIC-FIRST
NO OPERATIONAL MUTATION


FlowLens v1.0 remains:

NOT RELEASED


Do not claim:

production SaaS deployment

real ERP/MES integration

authentication/RBAC completion

causal effectiveness

automatic operational intervention


==================================================
CURRENT_STATE
==================================================

Normalize only the current-state projection to W04.

Preserve historical sections as history.

The current state must communicate:

W03 =
MERGED / CLOSED / VERIFIED

W04 C01-C10 =
CLOSED / VERIFIED

C10 =
CLOSED / VERIFIED / GITHUB_SYNCHRONIZED

W04 Sprint Final Closeout =
conditional on this final commit's own native proof

PR #7 =
W04 integration PR

PR merge =
NOT AUTHORIZED

W05 =
NOT AUTHORIZED

FlowLens v1.0 =
NOT RELEASED


Do not invent the future final SHA/run.


==================================================
AGENTS.md
==================================================

Replace the stale W03-current execution router
with the W04-final execution router.

It must preserve core rules:

EVIDENCE BEFORE CLAIM

ASSOCIATION != CAUSALITY

UNKNOWN IS VALID

NO FUTURE LEAKAGE

NO RUNTIME HGT

HUMAN AUTHORITY

LLM PRESENTATION AUTHORITY ONLY

NO OPERATIONAL MUTATION

FAIL CLOSED

NO AUTO-ADVANCE


It must explicitly state:

W04 C01-C10 CLOSED

POST-W04 IMPLEMENTATION NOT AUTHORIZED

W05 NOT AUTHORIZED

PR #7 MERGE NOT AUTHORIZED


==================================================
HARD PHASE-2 FREEZE
==================================================

Do NOT modify:

src/**

tests/**

.github/workflows/**

scripts/ci/**

pyproject.toml

uv.lock

migrations/**

schema

docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json

any C01-C10 checkpoint evidence

any C10 closeout file

.gitattributes


==================================================
PHASE 2 CANDIDATE
==================================================

Build a disposable candidate rooted at the exact
successful Prep SHA.

Require:

exact 8-path delta

exact subject

Prep verifier blob unchanged

GPT review byte-identical

Human message verbatim

source evolution byte-identical

src/tests/workflow/dependencies/migrations unchanged

git diff --check PASS

Ruff PASS

strict mypy PASS

security readiness PASS


Committed-head verifier must return:

W04_SPRINT_FINAL_CLOSEOUT


If candidate fails:

STOP:

W04_SPRINT_FINAL_CANDIDATE_PROOF_FAILED


==================================================
PHASE 2 REAL FINAL
==================================================

Only after candidate PASS:

apply exact proven bytes to freshly revalidated primary

create ONE normal final commit

run committed-head verifier

require:

W04_SPRINT_FINAL_CLOSEOUT

perform ONE normal push


Because README.md intentionally remains fail-closed
under the current classifier, expected native class is:

UNKNOWN / FULL_EXACT_SHA


Do NOT modify the classifier to change this result.


Require:

attempt 1

SUCCESS


Require again:

2997 selected
2994 passed
3 accepted skips

0 failed/error/xfail/xpass

entry no-loss PASS
exact union PASS
exact once PASS

Integration 70

W03 38/85

W04 9/67/81

W04_SPRINT_FINAL_CLOSEOUT PASS

all shard job and pytest durations <3300 seconds


If native Final fails:

STOP.


==================================================
PHASE 3 — PR #7 READINESS
==================================================

Only after Final native SUCCESS.

Require:

local HEAD
=
tracking HEAD
=
direct-origin HEAD
=
PR #7 HEAD
=
SPRINT_FINAL_SHA

ahead/behind 0/0

worktree/index CLEAN

main/base unchanged:

af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

PR mergeable TRUE


If main/base changed:

STOP:

W04_PR7_READINESS_BASE_DRIFT


Set exact PR title:

W04: evidence-grounded investigation workflow (C01-C10)


Replace the old C01-only PR body with a complete
W04 body containing:

Summary

Primary User / User Story

Delivered W04 C01-C10

Authority / Safety Boundaries

Exact-SHA Verification

C10 + W04 Sprint Closeout

Security / Secret Review

Known Non-blocking Limitations

Review Notes for the Large PR

Merge Boundary


The body must include the actual generated
Sprint Final SHA and native CI.


Then change:

PR #7 Draft

->

READY FOR REVIEW


Do NOT merge.

Do NOT enable auto-merge.

Do NOT enter merge queue.

Do NOT delete branch.


==================================================
FINAL PR STATE
==================================================

Require:

PR #7 state = OPEN

draft = FALSE

merged = FALSE

mergeable = TRUE

base = main

base SHA =
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509

head SHA =
SPRINT_FINAL_SHA

title =
W04: evidence-grounded investigation workflow (C01-C10)

auto-merge =
ABSENT / DISABLED


Then declare:

W04_SPRINT_FINAL_CLOSEOUT_COMPLETE

W04 =
CLOSED / VERIFIED / GITHUB SYNCHRONIZED

W04_C01_C10 =
CLOSED

W04_SECRET_READINESS =
PASS / NO LIVE SECRET IDENTIFIED

PR #7 =
OPEN / READY / UNMERGED

PR MERGE REVIEW =
PENDING GPT REVIEW + HUMAN AUTHORIZATION


==================================================
CARRY FORWARD NON-BLOCKING DEBT
==================================================

Retain without repair:

NB-C09-01

NB-C10-ENV-01

NB-W04-CI-01

NB-W04-GOV-01

NB-W04-PR-SIZE-01


==================================================
NOT AUTHORIZED
==================================================

PR merge

auto-merge

merge queue

branch deletion

main write

W05 implementation

post-W04 implementation


==================================================
OUTPUT POLICY
==================================================

Return only:

ONE compact W04 Sprint Final handoff

and

ONE consolidated evidence ZIP
with an internal SHA-256 manifest.


Do not expose hundreds of temporary helper files.


STOP after:

W04_SPRINT_FINAL_CLOSEOUT_COMPLETE

PR #7 READY FOR HUMAN MERGE REVIEW
````
<!-- ORIGINAL_HUMAN_MESSAGE_END -->
