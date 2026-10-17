# W04-C09 Two-Phase Closeout Authorization

Recorded 2026-10-14 (Asia/Shanghai). This document records the Human-approved CLOSEOUT-V1 task and subsequent approved Prep clarification. It does not expand their scope.

```text
C09_CLOSEOUT_AUTHORIZATION = APPROVED
CLOSEOUT_MODE = TWO_PHASE
PHASE_1 = VERIFIED OWN-SHA FULL CI
PHASE_2 = FIVE GOVERNANCE FILES ONLY
GPT_INDEPENDENT_REVIEW = PASS
HUMAN_C09_ACCEPTANCE = ACCEPTED
NB-C09-01 = DEFERRED / NON-BLOCKING
```

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


Phase 1 is one normal commit/push, subject `ci(w04-c09): admit bounded closeout lifecycle`, parent exactly REVIEW_READY. Its only delta is `scripts/ci/verify_w04_investigation_gate_contract.py`, Git blob `22d23c06dfa69e7d0d8036041f353d05f8dd2462`. The own-SHA [native run](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38420983775) passed all 16 full-route jobs, with Publication skipped. Original-artifact reaggregation confirms 2997 selected / 2994 passed / 3 accepted skipped, no adverse outcomes, entry no-loss, exact union, exact once, integration 70, W03 38/85 and W04 9 families / 67 selectors / 81 cases. Every shard job and pytest suite was strictly below 3300 seconds.

Phase 2 is exactly five new files:

```text
docs/w04/checkpoints/c09/W04_C09_GPT_INDEPENDENT_REVIEW_R1.md
docs/w04/checkpoints/c09/W04_C09_HUMAN_ACCEPTANCE.md
docs/w04/checkpoints/c09/W04_C09_CLOSEOUT_AUTHORIZATION.md
docs/w04/checkpoints/c09/W04_C09_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/checkpoints/c09/W04_C09_FINAL_CLOSEOUT_REPORT.md
```

The Phase-1 verifier is frozen during Phase 2. Final subject is exactly `docs(w04-c09): close investigation regression gate`, one normal real commit/push. A disposable full-history candidate is tested first and never pushed. The same five intended file bytes must then be applied to the freshly revalidated primary Prep checkout. Before push, the committed-head verifier and focused regression proof must pass.

Effective closure is conditional on the real final SHA's own C / FULL_EXACT_SHA CI SUCCESS, the complete unchanged outcome envelope, both strict <55m resilience checks and fresh clean four-head synchronization. No automatic repair, rerun-as-proof or replacement closeout commit is authorized after a pushed native failure. C10, PR ready/merge, branch deletion, main write and history rewrite remain unauthorized.

## Selected source contracts

| Source | Raw SHA-256 |
|---|---|
| FLOWLENS_W04_C09_CLOSEOUT_TASK_V1.md | `a619c47c3459e84c168e3d76909ad36422c7bd994a2e2514155e6065b92e4e4a` |
| FLOWLENS_W04_C09_CLOSEOUT_PREP_01_GPT_CLARIFICATION_R1.md | `892cc1648056765ed7add82f771000b16921cea0d5f2cfcf719045a982ec26db` |
| FLOWLENS_W04_C09_GPT_INDEPENDENT_REVIEW_R1.md | `f04c59244796aa7545902fb4f7b5b1c94dbfd742eddebf4fd7ec71bf3ccf71cb` |
| Human acceptance / closeout authorization request | `a66eec5f9ec3e88222d7b09f3c0613b4fd785f04189504d4a4c1cf998db3595c` |
| Human clarification continuation request | `b64074a4b465681be9f01e504394762d65cdb18756da2095741005c443f2816d` |

The Human request is recorded verbatim in W04_C09_HUMAN_ACCEPTANCE.md. The supplied independent review is preserved as an unchanged source prefix in W04_C09_GPT_INDEPENDENT_REVIEW_R1.md. No Codex self-acceptance or new review conclusion is substituted.
