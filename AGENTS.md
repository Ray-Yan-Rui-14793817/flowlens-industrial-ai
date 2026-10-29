# AGENTS - C01 recovery R3 A1

~~~text
CURRENT_WORKSTREAM = W05-C01 / PRODUCT SURFACE CONTRACT RECOVERY
CURRENT_TASK = W05_C01_PREFREEZE_STOP_RECOVERY_RESUME_R3_TASK_AMENDMENT_A1
CURRENT_TASK_PARENT = W05_C01_PREFREEZE_STOP_RECOVERY_RESUME_R3
C01_RECOVERY_ENTRY_G3 = 01be49cf51a45b8ea1b0910cb8c615a1dfc441c5
C01_RECOVERY_ENTRY_G3_TREE = 5e47b452d57be9de0bc138fe019b76598c0a2c37
C01_RECOVERY_EXECUTION = AUTHORIZED_BY_CURRENT_TASK
C01_SOURCE_ADMISSION_AT_PARENT = ADMISSION_STAGED
C01_TARGET_SOURCE_ADMISSION = BOOTSTRAP_MATERIALIZED
C01_CLOSEOUT_AUTHORIZATION = NO
C02_AUTHORIZATION = NO
MERGE_AUTHORITY = NO
W06_AUTHORIZATION = NO
FLOWLENS_V1_0_RELEASE_AUTHORITY = NO
HUMAN_DISPOSITION = PASS
A1_HUMAN_ACCEPTANCE = ACCEPTED
C01_RECOVERY_R3_A1_EXECUTION_AUTHORIZATION = APPROVED_FOR_THIS_TASK_ONLY
CURRENT_C01_IMPLEMENTATION_TECHNICAL_STATE = PENDING_CANDIDATE_PROOF
CURRENT_C01_HTTP_API = NOT_IMPLEMENTED
CURRENT_C01_UI = NOT_IMPLEMENTED
C01_PRESERVED_CANDIDATE = SEALED_15_PATHS_UNCOMMITTED_PREDECESSOR
OLD_C01_R1 = STOPPED_PREFREEZE_W04_INVARIANT_FAILURE
PARENT_R3_REVIEW_R1 = PASS_REVOKED_BY_NEW_EVIDENCE
DEEP_REVIEW_R2 = CONTROLLING_FINDING_SOURCE
~~~

The current Human-authorized task is the exact A1 C01 recovery/materialization contract.
Read docs/w05/c01/W05_C01_AUTHORIZATION_CONTRACT.md and W05_C01_CONTEXT_LOCK.md before work.
This frozen source projection records authorization and proof requirements at authoring time;
actual shadow, exact-head, native and terminal-review results belong to external evidence.
They are pending here. No implementation completion, Human implementation acceptance or closeout
is inferred from this document. Preserve the old C01 candidate/worktree and all failed history.

## Frozen G0 projection

THIS TASK below refers to preserved G0, not the current C01 recovery task.
~~~text
CURRENT_PHASE = W05 / SUCCESSOR GOVERNANCE ACTIVE
POST_W04_STABILIZATION = CLOSED
POST_MERGE_DOC_SYNC = COMPLETE
PR8 = MERGED / CLOSED / VERIFIED
P2_03 = MERGED_NATIVE_PROVEN_CLOSED
W04_HISTORICAL_GOVERNANCE_ANCHOR = 2f1627342ff2b04d8324fbffec3db2e230b302e0
W05_ACTIVE_PLAN = w05-active-non-integration-plan-v1
W05_C01 = NOT AUTHORIZED BY THIS TASK
W05_PRODUCT_API = NOT IMPLEMENTED
W05_UI = NOT IMPLEMENTED
W06 = NOT AUTHORIZED
FLOWLENS_V1_0 = NOT RELEASED
~~~

## Preserved G0 and G3 chronology

G0 effective external closure from C2 CI159 attempt1 and terminal reviews is preserved.
PR12/PR13 remain ready/open/unmerged. G3 is the sole child of C2, tree
5e47b452d57be9de0bc138fe019b76598c0a2c37, PR14 ready/open/unmerged, four commits/31 files.
G3 CI160 run40827247539 attempt1 SUCCESS and measured UNKNOWN/FULL_EXACT_SHA R46 PASS are
predecessor evidence, not substitutes for C01-I proof. R1/R2 compatibility repairs and earlier
R3/A1 STOP records remain sealed and unaccepted. The separate G3 proof-controller recovery
completed native proof and review with the invalid false-ancestry P1 preserved unedited.

## Current bounded execution

Exactly15 repository paths may change from G3: eight verified recovered bytes and seven rebased
governance files. Product source/tests and the three semantic documents never change after recovery.
The seven governance documents may be corrected only before freeze. No sixteenth path is authorized.
G3 policy v2 preexists with no product source. It admits exactly100644 __init__.py/contracts.py/
projection.py under src/flowlens/product in one initial materialization. The policy, compatibility
verifier, W05 successor verifier, B36 file and R46 replay file stay exact G3 blobs/modes; R43,
the R46 test body/fixture and all historical W04/W03/runtime objects remain unchanged.
Source must move from staged at G3 to BOOTSTRAP_MATERIALIZED at each exact committed proof head.
No same-commit self-authorization, fourth source path, policy drift or uncommitted source drift.

Proof order: product-only prefreeze quality/schema/six vectors/capability and dual-plane checks;
freeze all candidate/docs/harness bytes; create disposable SHADOW_C01_I with sole G3 parent;
full shadow proof; one actual C01-I with exact shadow tree and sole G3 parent; fresh exact-head
proof; one normal push/new ready PR to main; first exact-C01-I opened nativeattempt1; measured
R46 on original C01-I archives; reports before terminal review; zero unresolved VALID findings.
Do not run committed-source W04/B36 acceptance against the uncommitted candidate. First material
formal failure after freeze requires sealed STOP, no patch/retry, replacement or second commit.
External infrastructure interruption may resume only with the same frozen bytes.

Each complete raw plan validates its own exact head/seal. For comparison remove exactly head_sha
and plan_sha256; every other field, including complete files/shards/weights/collections, must equal.
Rebind materialization_sha/expected_head/head_sha/proof_sha256 truthfully to each validated head.
Do not require raw seals or shadow/actual SHAs to equal or differ. Successor and current-plan counts
are measured dynamically. Product126/126 has zero skip/xfail/xpass; classifier91, W03 38/85,
current and historical W04 9/67/81 remain mandatory. Native17 required jobs SUCCESS, Publication
SKIPPED; seven partitions/exact aggregate and exactly the three frozen global Linux junction skips.
Actual UNKNOWN/FULL_EXACT_SHA/ambiguous_event remains truthful, with new measured GITHUB_NATIVE R46.

All proof databases must be isolated task-owned _test databases; no inherited GIT_CONFIG overrides.
Use only command-local controller Git configuration. No HTTP/UI/application service/DB persistence,
provider/network/file/environment/random/wall-clock/runtime HGT or operational action in product code.
ProductCaseView is an immutable transport-neutral read model. Production / Delivery Operations
Manager; offline/shadow/human-in-loop; separate Decision/Investigation Human review planes;
HUMAN_NOTE_NON_EVIDENCE; canonical schema/vectors; no inferred causal/probability/risk authority.

No predecessor PR mutation, main write, merge, auto-merge, queue, branch deletion, C01 closeout,
C02, W06, release or automatic advancement. Success enables C01 closeout design/review entry only.

CONTRACT FIRST. SNAPSHOT BEFORE REASONING. ONE RUN=ONE IMMUTABLE SNAPSHOT. EVIDENCE BEFORE CLAIM.
ASSOCIATION != CAUSALITY. UNKNOWN IS VALID. NO FUTURE LEAKAGE. NO RUNTIME HGT. HUMAN AUTHORITY.
MODEL EXPLAINS, SYSTEM DECIDES. LLM PRESENTATION AUTHORITY ONLY. NO OPERATIONAL MUTATION.
TOOLS DENY BY DEFAULT. FAIL CLOSED. HARNESS=DETECTION+ENFORCEMENT+EVIDENCE. REPORT BEFORE REVIEW.
REVIEW BEFORE ACCEPTANCE. ACCEPTANCE BEFORE CLOSEOUT. NO AUTO-ADVANCE.
Human notes remain HUMAN_NOTE_NON_EVIDENCE.
