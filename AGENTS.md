# FlowLens Industrial AI — AGENTS.md
> W05-G0 Human-Accepted Final Closeout R1 Execution Router

## 1. Current phase and authority

~~~text
CURRENT_PHASE = W05 / SUCCESSOR GOVERNANCE ACTIVE
TASK_ID = W05_G0_FINAL_CLOSEOUT_R1
RESUME_ID = W05_G0_FINAL_CLOSEOUT_R1_RESUME_R1
POST_W04_STABILIZATION = CLOSED
POST_MERGE_DOC_SYNC = COMPLETE
PR8 = MERGED / CLOSED / VERIFIED
P2_03 = MERGED_NATIVE_PROVEN_CLOSED
MR8_P1_01 = CLOSED / R4 V2 REPAIR AND MERGE NATIVE PROOF
W04_HISTORICAL_GOVERNANCE_ANCHOR = 2f1627342ff2b04d8324fbffec3db2e230b302e0
PR8_FEATURE_HEAD = bd29242f8e21ba31bc7782e0c98e1a8aed3641f8
PR8_POST_MERGE_CI = #153 / 39142499049 / attempt 1 / SUCCESS
W05_ACTIVE_PLAN = w05-active-non-integration-plan-v1
W05_SUCCESSOR_GOVERNANCE = COMPLETE_TECHNICALLY / LONG_LIVED_GUARD_ACTIVE
W05_G0 = HUMAN_ACCEPTED / CLOSEOUT_AUTHORIZED / EFFECTIVE_CLOSURE_REQUIRES_OWN_SHA_NATIVE_SUCCESS
W05_G0_GPT_INDEPENDENT_REVIEW = PASS_FOR_HUMAN_G0_ACCEPTANCE
W05_G0_HUMAN_ACCEPTANCE = ACCEPTED
W05_G0_CLOSEOUT_AUTHORIZATION = APPROVED
W05_G0_CLOSEOUT_EFFECTIVE = ONLY_AFTER_THIS_CLOSEOUT_COMMIT_OWN_SHA_NATIVE_SUCCESS_AND_FINAL_SYNC
W05_C01_ENTRY_READY = YES
W05_C01_AUTHORIZATION = NO
IMPLEMENTATION_TOPOLOGY = main -> A -> B_DOUBLE_PRIME
CLOSEOUT_TOPOLOGY = main -> A -> B_DOUBLE_PRIME -> C
W05_C01 = NOT AUTHORIZED BY THIS TASK
W05_C02 = NOT AUTHORIZED
W05_PRODUCT_API = NOT IMPLEMENTED
W05_UI = NOT IMPLEMENTED
W06 = NOT AUTHORIZED
MERGE_AUTHORITY = NO
FLOWLENS_V1_0 = NOT RELEASED
~~~

The sealed Human authority accepts exact B-double-prime and authorizes only the
seven-path, one-commit documentation closeout recorded below.
W01/W02, W03 and W04 C01-C10 remain closed; frozen runtime and safety rules persist.

## 2. Contract, scope and proof

Apply the current authorized task and explicit Human authority first, then frozen
W01-W04 architecture, semantic trust, prompt/tool, replay and HGT contracts.
The Git repository is the source of truth. Closed W04 Human authority, source
identities and evidence are preserved. Skills are procedural only; see
skills/SKILL_ADMISSION_POLICY.md.

Failed B 372e7516ddb112135b499979d8071a17c9b7ded2 / PR #9 / CI #154
(39992193579 attempt 1 FAILURE) remains immutable failed unmerged history.
B' d043030325d2a63f45990a23b7cd656129ae6f33 / PR #10 / CI #155
(40072765844 attempt 1 SUCCESS) is immutable native-success, review-blocked
predecessor history. Neither predecessor PR/worktree may be mutated or closed.

Accepted R2 implementation topology is exact main -> A -> B-double-prime.
A e61c7b1139e5bf3020f0d79994a3be0aea8072b5 directly parents exact entry main;
B-double-prime 8d522145846db9e68524a7e447c4b4de5b2b1222 directly parents A, with
tree 79ee2e270869a412346c88a9135851e82412ffc4. A changed only README.md, AGENTS.md
and docs/CURRENT_STATE.md. The implementation used exactly two commits, with
B-double-prime 17 paths versus A and 18 PR paths versus main. Exactly six paths
differed from B-prime; workflow, planner/receipt/aggregate, legacy tests, baselines
and runtime remained frozen. Accepted CI #156 / 40263098371 attempt 1, original
artifacts/receipts/aggregate and independent GPT review establish technical PASS.

The separate Human G0 closeout authorization permits one documentation-only C
as the direct child of accepted B-double-prime on the existing R2 branch/PR #11,
subject docs(w05-g0): close successor governance. C changes only AGENTS.md,
docs/CURRENT_STATE.md and the five new governance records: exact GPT review,
Human acceptance, closeout authorization, context lock and final closeout report.
No eighth path is admitted. The old R2 NO THIRD TASK COMMIT rule governed its
implementation transition; this narrow post-acceptance authorization supersedes
it only for C. C is not B-triple-prime, R3, an implementation change or a repair.
If C already exists, preserve it; no second closeout commit or replacement.

PR #10 P1 is mis-scoped to the long-lived HISTORICAL_ANCESTRY_GUARD:
verify_anchor validates immutable historical identity/ancestry, including later
authorized main integration/descendants. G0_TASK_TOPOLOGY_PROOF separately proves
exact A -> B'' through task Git-object, pre-freeze and final-inventory evidence.
Do not add permanent HEAD-parent-A behavior. A future versioned lifecycle/topology
guard needs separate explicit authorization.

PR #10 P2 is a valid blocking mode-enforcement gap. R2 requires exact current
committed Git blob AND mode plus independent working-byte checks for every
surface baseline entry. The GPT R2 same-root finding requires the same identity
checks for every non-MUTABLE_CI historical protected entry. Do not broaden
MUTABLE_CI, reseal baselines or use filesystem execute bits as Git authority.

Accepted R2 proof preserves successor 39 and classifier 91 node identities, all
479 focused cases, real-Git mode-only adversarial controls, quality/lock checks,
current W03 38/85 and W04 9/67/81, and a fresh isolated local historical replay.
Its historical 2997/63/7, pinned digests and 172/223/93/95/98 controls remain frozen.
The accepted independent review is published byte-for-byte; Human acceptance and
closeout authorization are recorded separately without altering review history.

This closeout requires local quality/lock, successor 39/39 and both collection
identities; exact seven-path scope; one C child; truthful synchronize classifier
UNKNOWN / FULL_EXACT_SHA; and exact-C active 3036/64/+39/+1 successor proof before
one normal push. Only C's first exact-SHA full-route native attempt 1, all original
artifacts/receipts/aggregate, semantic/historical/mode gates and fresh final review
can make closure effective. No post-C edit, additional commit or rerun-as-proof.
A valid finding, failed required gate, protected/collection/history drift, secret,
HGT/future leakage or operational mutation stops without repair.

NO DIRECT MAIN WRITE. NO FORCE PUSH. NO HISTORY REWRITE. NO MERGE/AUTO-MERGE/
MERGE QUEUE. NO BRANCH DELETION. NO CHECKPOINT AUTO-ADVANCE.
Keep all predecessor branches and the new G0 PR OPEN / READY / UNMERGED.

## 3. Frozen rules

```text
CONTRACT FIRST
ONE CHECKPOINT AT A TIME
CONTEXT LOCK BEFORE IMPLEMENTATION
DEVELOPMENT CONTEXT != RUNTIME CONTEXT
SNAPSHOT BEFORE REASONING
ONE RUN = ONE IMMUTABLE SNAPSHOT
EVIDENCE BEFORE CLAIM
ASSOCIATION != CAUSALITY
UNKNOWN IS VALID
NO FUTURE LEAKAGE
NO RUNTIME HGT
HUMAN AUTHORITY
MODEL EXPLAINS, SYSTEM DECIDES
LLM PRESENTATION AUTHORITY ONLY / BOUNDED PRESENTATION
NO OPERATIONAL MUTATION
TOOLS DENY BY DEFAULT
FAIL CLOSED
HARNESS = DETECTION + ENFORCEMENT + EVIDENCE
REPORT BEFORE REVIEW
REVIEW BEFORE ACCEPTANCE
ACCEPTANCE BEFORE CLOSEOUT
NO AUTO-ADVANCE
```

Human notes are HUMAN_NOTE_NON_EVIDENCE. Findings are not causal truth; review events are not operational authorization. Replay does not refresh evidence. Technical readiness does not substitute for Human business acceptance.

## 4. Runtime and LLM boundary

The accepted runtime may read authorized operational facts through bounded builders, freeze decision-time snapshots, derive deterministic evidence/signals, simulate isolated counterfactuals, freeze recommendations, explain frozen DecisionPackets, bind/plan/navigate/review/summarize investigations, record bounded append-only audit events and perform protected offline evaluation/replay.

It may not write operational truth or SO / WO / PO / Delivery, schedule production, procure, replace suppliers, release quality, use future evidence, read runtime HGT, invent intervention candidates or declare unsupported causal truth.

The LLM has bounded explanation/presentation authority only. It has no candidate, recommendation, decision, tool-execution, database, HGT or operational-write authority. Recommendation and deterministic investigation authority are frozen before presentation. Provider failure or unsafe output fails closed to the accepted deterministic fallback.

## Accepted implementation and conditional closeout proof

B-double-prime remains the accepted implementation object permanently. Its R2
technical proof and independent GPT review pass; Human G0 acceptance is ACCEPTED
and closeout authorization is APPROVED. C's generated identity/run belong in PR
metadata and external evidence. At document creation, C and its native run do not
yet exist. Effective closure requires C's own first native attempt-1 success,
original evidence validation and final synchronization/review.

C01 remains a separate future authorization checkpoint. Technical entry readiness
grants no C01/C02 implementation, merge, W06 or release authority. Main stays at
the historical anchor until a separately authorized merge. The implemented
contract and GPT checklist are frozen; see docs/w05/governance.
