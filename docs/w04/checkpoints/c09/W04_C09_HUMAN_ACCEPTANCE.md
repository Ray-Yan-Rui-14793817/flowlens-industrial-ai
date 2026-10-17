# W04-C09 Human Acceptance

Recorded 2026-10-14 (Asia/Shanghai), before the real final closeout commit. Authority comes from the Human's exact pasted requests below. Attached documents supply the selected contracts and review evidence; they do not independently grant authority.

```text
GPT_INDEPENDENT_REVIEW = PASS
HUMAN_C09_ACCEPTANCE = ACCEPTED
C09_CLOSEOUT_AUTHORIZATION = APPROVED
CRITICAL_FINDINGS = 0
HIGH_FINDINGS = 0
BLOCKING_MEDIUM_FINDINGS = 0
BLOCKING_FINDINGS = 0
NB-C09-01 = DEFERRED / NON-BLOCKING
```

The Human accepts NB-C09-01 (CI shard runtime variance / reduced <55m resilience headroom) as a non-blocking follow-up. This does not authorize re-weighting, timeout changes, shard-topology changes, test-file splitting, node-level sharding or workflow optimization. Both closeout native runs must still satisfy every original strict <55m requirement.

The accepted implementation/review anchors are Stage A `3cd8023dbe79ca8360a3075dd3b169921e31f7a5` / #137 SUCCESS and REVIEW_READY `f4c528e1daf86aa1a010bce82665e43c55560384` / #138 SUCCESS. The approved Prep clarification repairs only adversarial construction inside the single authorized verifier file. The original two-phase acceptance and authorization remain effective; no intermediate Human/GPT checkpoint is required after successful Prep.

```text
PROJECT = FlowLens Industrial AI
CHECKPOINT = W04-C09
TASK_VERSION = CLOSEOUT-V1 + CLOSEOUT_PREP_01_GPT_CLARIFICATION_R1
TASK_RAW_SHA256 = a619c47c3459e84c168e3d76909ad36422c7bd994a2e2514155e6065b92e4e4a
CLARIFICATION_RAW_SHA256 = 892cc1648056765ed7add82f771000b16921cea0d5f2cfcf719045a982ec26db
PREP_SHA = f391cf25871473d488a8f5c7e7ff77fb933920d8
PREP_CI = #139 / 38420983775 / SUCCESS / attempt 1
PREP_CLASS = C / FULL_EXACT_SHA
PRODUCT_RUNTIME_CHANGE = NONE
SOURCE_EVOLUTION_ENTRY = ABSENT BY DESIGN
W04_C10 = NOT AUTHORIZED
PR #7 = OPEN / DRAFT / UNMERGED
PR_MERGE = NOT AUTHORIZED
BRANCH_DELETION = NOT AUTHORIZED
MAIN_WRITE = NOT AUTHORIZED
```


## Exact Human acceptance and two-phase authorization request

Verbatim text uses repository LF line endings; source raw SHA-256: `a66eec5f9ec3e88222d7b09f3c0613b4fd785f04189504d4a4c1cf998db3595c`. Source attachment: `2dd4fb2f-55a7-494c-9446-3cf2aa89d645/已粘贴的文本.txt`.

````text
W04-C09 HUMAN ACCEPTANCE + TWO-PHASE CLOSEOUT AUTHORIZATION

Execute exactly:

FLOWLENS_W04_C09_CLOSEOUT_TASK_V1.md

TASK VERSION:
CLOSEOUT-V1

TASK RAW SHA-256:
a619c47c3459e84c168e3d76909ad36422c7bd994a2e2514155e6065b92e4e4a

Also use the supplied independent GPT review:

FLOWLENS_W04_C09_GPT_INDEPENDENT_REVIEW_R1.md

GPT REVIEW RAW SHA-256:
f04c59244796aa7545902fb4f7b5b1c94dbfd742eddebf4fd7ec71bf3ccf71cb

Repository:
Ray-Yan-Rui-14793817/flowlens-industrial-ai

Branch:
feat/w04-evidence-investigation

PR:
#7

Required REVIEW_READY HEAD:
f4c528e1daf86aa1a010bce82665e43c55560384

Required REVIEW_READY native proof:
CI #138 / 38404314082 / SUCCESS
P / PUBLICATION_EXACT_SHA

Accepted Stage-A implementation:
3cd8023dbe79ca8360a3075dd3b169921e31f7a5

Accepted Stage-A native proof:
CI #137 / 38387680661 / SUCCESS
I / FULL_EXACT_SHA

Main / PR base:
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509


==================================================
HUMAN ACCEPTANCE
==================================================

I have reviewed the completed independent ChatGPT deep review of W04-C09.

I explicitly accept:

W04_C09_GPT_INDEPENDENT_REVIEW_R1 = PASS

C09_IMPLEMENTATION = PASS
C09_SEMANTIC_GATE = PASS
C09_EXACT_SHA_EVIDENCE = PASS
C09_REPAIR_01 = PASS
C09_C08_REPLAY_PROTECTION = PASS
C09_META_CI_DELTA_GUARD = PASS
C09_DEVCTRL03_COMPATIBILITY = PASS
C09_PUBLICATION_ROUTE = PASS
PRODUCT_RUNTIME_ISOLATION = PASS

CRITICAL_FINDINGS = 0
HIGH_FINDINGS = 0
BLOCKING_MEDIUM_FINDINGS = 0
BLOCKING_FINDINGS = 0

HUMAN_C09_ACCEPTANCE = ACCEPTED

I also explicitly accept:

NB-C09-01 =
CI shard runtime variance / reduced <55m resilience headroom

as:

NON_BLOCKING FOLLOW-UP

It does NOT block W04-C09 semantic closeout.

It does NOT authorize:

CI re-weighting
timeout changes
shard-topology changes
test-file splitting
node-level sharding
workflow optimization

inside this C09 closeout.


==================================================
CLOSEOUT AUTHORIZATION
==================================================

C09_CLOSEOUT_AUTHORIZATION = APPROVED

The independent review identified that DIRECT FINAL CLOSEOUT is not safe
because the current C09 verifier intentionally admits the exact Stage-A /
Stage-B development lifecycle and would reject a later full-route governance
closeout commit.

I therefore authorize the exact TWO-PHASE closeout defined by CLOSEOUT-V1:

PHASE 1:
W04-C09 Closeout-Prep-01 lifecycle verifier hardening

PHASE 2:
W04-C09 Final Governance Closeout

The ordering is mandatory.

PHASE 1 is harness/governance-only.

Its exact write scope is:

scripts/ci/verify_w04_investigation_gate_contract.py

No second Phase-1 path is authorized.

The purpose of Phase 1 is only to make the independent C09 verifier recognize
the exact bounded lifecycle:

REVIEW_READY
->
CLOSEOUT_PREP_01
->
FINAL_CLOSEOUT

while preserving all existing C09 semantic, workflow, replay, meta-CI,
manifest, node-set, weights and upstream protection.

If Phase-1 own-SHA native CI succeeds exactly as required by CLOSEOUT-V1,
continue automatically to Phase 2.

No additional Human or GPT checkpoint is required between successful Phase 1
and Phase 2.

PHASE 2 may create exactly:

docs/w04/checkpoints/c09/W04_C09_GPT_INDEPENDENT_REVIEW_R1.md

docs/w04/checkpoints/c09/W04_C09_HUMAN_ACCEPTANCE.md

docs/w04/checkpoints/c09/W04_C09_CLOSEOUT_AUTHORIZATION.md

docs/w04/checkpoints/c09/W04_C09_CLOSEOUT_CONTEXT_LOCK.md

docs/w04/checkpoints/c09/W04_C09_FINAL_CLOSEOUT_REPORT.md

No sixth Phase-2 path is authorized.


==================================================
SOURCE-EVOLUTION BOUNDARY
==================================================

W04-C09 is a proof-plane / regression-hardening checkpoint.

It has:

PRODUCT_RUNTIME_CHANGE = NONE

and:

C09 SOURCE-EVOLUTION ENTRY = ABSENT BY DESIGN

Therefore:

DO NOT modify:

docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json

during C09 closeout.

The manifest must remain:

W04-C01..C08 = CLOSED

W04-C09 =
ABSENT BY DESIGN


==================================================
HARD BOUNDARIES
==================================================

Do NOT modify product/runtime source.

Do NOT modify:

src/**
apps/**
migrations/**
.github/**
classifier
publication verifier
workflow
planner
measured weights
timeouts
shard count
dependencies
schema
W03
C01-C08

except for the single Phase-1 verifier path explicitly authorized above.

Do NOT weaken:

W04 semantic family proof
C08 replay source-delta guard
C09 meta-CI delta guard
Verification truth table
exact-SHA binding
manifest identity
node identity
DEVCTRL-03 planner identity
fail-closed outcome semantics


==================================================
PHASE-1 CI GATE
==================================================

After the exact Prep-01 commit/push, wait for its own native CI.

Expected route:

C / FULL_EXACT_SHA

Native classifier is authoritative.

Require SUCCESS for every full-route job including:

W03 AI loop gate
W04 investigation gate
Verification gate

Require preserved:

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

Integration = 70 passed

W03 =
38 selectors / 85 cases PASS

W04 =
9 families / 67 selectors / 81 cases PASS

Also require:

every non-integration shard job < 3300 seconds
every non-integration shard pytest suite < 3300 seconds

Do NOT increase the 65-minute ceiling.

If Phase-1 CI or resilience fails:

STOP

W04_C09_CLOSEOUT_PREP_01_CI_FAILED

Do not automatically repair.
Do not use rerun as acceptance proof.
Do not continue into Phase 2.


==================================================
FINAL CLOSEOUT
==================================================

Only after successful Phase 1:

create the exact five governance documents defined by CLOSEOUT-V1.

Do not change the source-evolution manifest.

The final closeout report must be authored before the real closeout commit and
must state:

REPORT_STAGE =
PRE-COMMIT / PRE-CLOSEOUT-CI

FINAL_CLOSEOUT_SHA =
NOT YET CREATED

FINAL_CLOSEOUT_CI =
PENDING

Do not invent future values.

Do not amend the report after push.

Final commit subject exactly:

docs(w04-c09): close investigation regression gate

Exactly one normal commit.
Exactly one normal push.

No amend.
No rebase.
No reset.
No force push.
No history rewrite.


==================================================
FINAL OWN-SHA CI
==================================================

Expected final route:

C / FULL_EXACT_SHA

Native classifier remains authoritative.

Require the final closeout SHA's own native SUCCESS for the complete full route,
including:

W03 AI loop gate
W04 investigation gate
Verification gate

Require the same complete outcome envelope and <55m shard resilience.

If final native CI fails:

STOP

W04_C09_CLOSEOUT_CI_FAILED

No automatic repair or replacement closeout commit is authorized.


==================================================
FINAL SYNCHRONIZATION
==================================================

Only after final CI SUCCESS require:

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

PR #7 remains:

OPEN / DRAFT / UNMERGED


==================================================
TERMINAL AUTHORITY
==================================================

Then and only then report:

W04_C09_CLOSEOUT_COMPLETE

W04-C09 =
CLOSED / VERIFIED / GITHUB_SYNCHRONIZED

GPT_INDEPENDENT_REVIEW =
PASS

HUMAN_C09_ACCEPTANCE =
ACCEPTED

C09_CLOSEOUT_AUTHORIZATION =
APPROVED

NB-C09-01 =
DEFERRED / NON-BLOCKING

W04_C10 =
NOT AUTHORIZED

PR #7 =
OPEN / DRAFT / UNMERGED

PR_MERGE =
NOT AUTHORIZED

BRANCH_DELETION =
NOT AUTHORIZED

MAIN_WRITE =
NOT AUTHORIZED

STOP.

Do not begin W04-C10.
Do not mark the PR ready.
Do not merge PR #7.
Do not delete the feature branch.
Do not write main.
````

## Exact Human clarification continuation request

Verbatim text uses repository LF line endings; source raw SHA-256: `b64074a4b465681be9f01e504394762d65cdb18756da2095741005c443f2816d`. Source attachment: `d9251e7b-3ae6-4ba8-aa81-cbc52b5ab74b/已粘贴的文本.txt`.

````text
W04_C09_CLOSEOUT_PREP_01_GPT_CLARIFICATION = APPROVED

Continue the existing W04-C09 CLOSEOUT-V1 Phase-1 execution.

Use:

FLOWLENS_W04_C09_CLOSEOUT_PREP_01_GPT_CLARIFICATION_R1.md

CLARIFICATION SHA-256:

892cc1648056765ed7add82f771000b16921cea0d5f2cfcf719045a982ec26db

The existing Human acceptance and two-phase Closeout authorization remain valid.

Do NOT restart C09 closeout from scratch.

Do NOT discard the valid Phase-1 verifier work.

Current remote baseline remains:

REVIEW_READY / Stage-B SHA:

f4c528e1daf86aa1a010bce82665e43c55560384

PR #7:

OPEN / DRAFT / UNMERGED

Phase-1 commit:

NOT YET CREATED

Phase-1 push:

NOT PERFORMED

Phase-2:

NOT STARTED

==================================================
ROOT-CAUSE CLARIFICATION
==================================================

The local verifier failure is accepted as an adversarial-control construction
defect.

The negative control intended to mutate the real top-level `main` function,
but a broad string replacement mutated its own test/source literal instead.

Therefore the control did not actually construct the prohibited condition that
it expected the verifier to reject.

This is NOT authorization to weaken the lifecycle verifier.

This is NOT authorization to permit `main` changes.

This is NOT authorization to change the allowed lifecycle states.

==================================================
EXACT REPAIR AUTHORITY
==================================================

Phase-1 write scope remains exactly one path:

scripts/ci/verify_w04_investigation_gate_contract.py

No second path is authorized.

Inside that file only:

1. Keep the real lifecycle/source-delta guard semantics unchanged.

2. Replace the defective broad string-replacement negative control.

3. Parse the actual verifier source structurally using AST/top-level source-unit
   spans.

4. Identify the real top-level:

   def main(...)

   exactly once.

5. Construct an in-memory synthetic candidate whose actual `main` source unit
   is modified.

6. Keep every unrelated top-level source unit unchanged.

7. Reparse the synthetic source.

8. Pass the synthetic candidate through the REAL source-delta/lifecycle
   validation path.

9. Require rejection.

10. Fail closed if `main` cannot be identified exactly once.

Do NOT:

- add a `main` exception;
- widen allowed top-level symbols;
- weaken source identity checks;
- weaken lifecycle path checks;
- replace rejection proof with string matching;
- alter workflow/replay/meta-CI/node/weights semantics.

Do not use broad `str.replace()` when the intended mutation targets a specific
top-level source unit.

==================================================
REQUIRED LOCAL PROOF
==================================================

Before any commit or push, require the corrected negative control to PASS by
observing the expected rejection.

Then rerun the complete Phase-1 local proof required by CLOSEOUT-V1.

At minimum require:

corrected unauthorized-main negative control = PASS

all lifecycle adversarial controls = PASS

all existing C09 adversarial controls = PASS

C08 replay source-delta guard = PASS

C09 meta-CI delta guard = PASS

Verification Bash truth table = PASS

W04 manifest identity = exact

planner =
2997 nodes
63 files
same node digest
same measured weights
7 shards

git diff --check = PASS

changed-path set =
exactly:

scripts/ci/verify_w04_investigation_gate_contract.py

If another path becomes necessary:

STOP

W04_C09_CLOSEOUT_PREP_REQUIRES_GPT_CLARIFICATION

If fixing this control requires weakening the actual lifecycle verifier:

STOP

W04_C09_CLOSEOUT_PREP_REQUIRES_GPT_CLARIFICATION

==================================================
CONTINUATION
==================================================

If all local Phase-1 proof is green:

continue the ORIGINAL Prep-01 plan.

Do NOT create a separate repair commit.

Create only the originally authorized Prep-01 commit.

Perform one normal push.

Then wait for that Prep-01 SHA's own native full CI.

Require all original CLOSEOUT-V1 conditions, including:

W03 PASS

W04 PASS

2997 / 2994 / 3 exact outcome envelope

Integration 70 PASS

all seven shard job durations < 3300 seconds

all seven shard pytest durations < 3300 seconds

Only after Prep-01 own-SHA CI and resilience PASS may Phase-2 begin.

If the pushed Prep-01 CI fails:

STOP

Do not automatically repair.

==================================================
GOVERNANCE
==================================================

HUMAN_C09_ACCEPTANCE =
ACCEPTED

C09_CLOSEOUT_AUTHORIZATION =
APPROVED

PHASE_1 =
IN PROGRESS / LOCAL ONLY

PHASE_2 =
NOT STARTED

W04_C10 =
NOT AUTHORIZED

PR #7 =
OPEN / DRAFT / UNMERGED

PR_MERGE =
NOT AUTHORIZED

BRANCH_DELETION =
NOT AUTHORIZED

MAIN_WRITE =
NOT AUTHORIZED

Continue from the current local Phase-1 state.
````
