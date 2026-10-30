# C01 recovery A1 authorization contract

TASK_ID = W05_C01_PREFREEZE_STOP_RECOVERY_RESUME_R3_TASK_AMENDMENT_A1
HUMAN_DISPOSITION = PASS
A1_HUMAN_ACCEPTANCE = ACCEPTED
C01_RECOVERY_R3_A1_EXECUTION_AUTHORIZATION = APPROVED_FOR_THIS_TASK_ONLY
C01_CLOSEOUT_AUTHORIZATION = NO
C02_AUTHORIZATION = NO
MERGE_AUTHORITY = NO
W06_AUTHORIZATION = NO
FLOWLENS_V1_0_RELEASE_AUTHORITY = NO

This task's pasted Human request authorizes the reviewed A1 execution. The earlier design/review's
NO-execution-at-design-time statements retain their historical meaning; the controlling task grants
execution now. The unamended R3 task is superseded and must not execute.

G3=01be49cf51a45b8ea1b0910cb8c615a1dfc441c5;
tree=5e47b452d57be9de0bc138fe019b76598c0a2c37; sole parent C2=2af8fcd9c3f2fce5121b1b7a3ecead6067eb8aec.
Controlling task SHA256 f627c4528fa6c9a7b458145405c50af24eb51ff954816a7174674f5e0ea5f46f;
A1 design10be32829b504c755dff3be712699c4e2314a4939d04ded4bb360812a2523d60;
A1 review425b68932b9ebaa5f04b0e62eac1a20b8d17b468d30371544fbb86238660f326;
Deep Review R2 c3b87ac8889a94c3536d28ea05ba9a5d735339f031fb2f34f93fbb0d6b263e3a.

Exact authorized delta from G3:

- AGENTS.md
- docs/CURRENT_STATE.md
- docs/w05/c01/W05_C01_AUTHORIZATION_CONTRACT.md
- docs/w05/c01/W05_C01_CONTEXT_LOCK.md
- docs/w05/c01/W05_C01_GPT_REVIEW_CHECKLIST.md
- docs/w05/c01/W05_C01_HARNESS_ACCEPTANCE_SPEC.md
- docs/w05/c01/W05_C01_PRODUCT_SURFACE_CONTRACT.md
- docs/w05/c01/W05_C01_PRODUCT_USER_JOURNEY_CONTRACT.md
- docs/w05/c01/W05_C01_SECONDARY_DESIGN_REVIEW_R1.md
- docs/w05/c01/W05_C01_V1_SCOPE_RECONCILIATION.md
- src/flowlens/product/__init__.py
- src/flowlens/product/contracts.py
- src/flowlens/product/projection.py
- tests/test_product_contracts.py
- tests/test_product_projection.py

Eight byte-exact paths derive only from the old sealed candidate ZIP/manifest; seven governance
documents rebase truthfully on G3. The original15-path worktree and old STOP stay unchanged.
The admitted source set is exactly src/flowlens/product/{__init__.py,contracts.py,projection.py},
regular100644, one first materialization. The preexisting immutable policy v2 seal is
2911ec2274c7f6710fb2d3425831a26549c9e93c9abfa280031d6393461e3568. No implementation may modify
that policy, either verifier, B36, R46, classifier, workflow, dependency or W04 governance.

No product redesign: immutable ProductCaseView, separate DecisionHumanReviewView and
InvestigationHumanReviewView, HUMAN_NOTE_NON_EVIDENCE, flowlens-product-case-view.v1 canonical
serialization/six vectors, offline/shadow/human-in-loop and Production / Delivery Operations
Manager. No HTTP/UI/application-service/DB/persistence, operational action, I/O, file/network/
provider/env/random/wall-clock/runtime-HGT capability, unsupported causal/probability/risk inference
or LLM decision/tool authority. Operational and downstream authority remain denied.

Prefreeze product proof precedes committed-source proof. All candidate/docs/harness bytes freeze;
first material formal acceptance failure requires sealed STOP without inline correction/retry.
Only complete shadow PASS permits one actual C01-I with the same tree and sole G3 parent.
Then fresh exact-head proof, one normal push/new ready/unmerged PR, first opened nativeattempt1,
new measured R46 from C01-I originals and zero unresolved VALID review findings. Each raw plan
validates its own head/seal; remove exactly head_sha/plan_sha256 only for full normalized comparison.
Source proof commit fields rebind truthfully. No shadow substitute for actual proof.

Completion is technical implementation readiness for separate closeout design/review only.
No closeout, C02, main write, predecessor mutation, merge/auto-merge/queue/branch deletion, W06,
release or automatic advancement is authorized. Reports precede review; acceptance precedes closeout.
