# FlowLens Industrial AI — AGENTS.md
> Post-W04 Stabilization Repository Execution Router

This router records the bounded Human-authorized
POST_W04_P2_03_PR8_MERGE_LIFECYCLE_REPAIR_R4_V2 scope. W04 integration is
complete. R4 V2 repairs PR #8 merge topology only; it grants no PR merge,
W05 implementation, successor-governance transition or v1.0 release authority.

## 1. Current phase

~~~text
PROJECT = FlowLens Industrial AI
CURRENT_PHASE = POST-W04 STABILIZATION / PR #8 MERGE-LIFECYCLE REPAIR R4 V2
PRIMARY_LOOP = Order Delivery Risk Decision Loop + Evidence-grounded Investigation
MODE = OFFLINE / SHADOW / HUMAN-IN-THE-LOOP
CORE = DETERMINISTIC-FIRST
W01 / W02 = CLOSED / VERIFIED
W03 = MERGED / CLOSED / VERIFIED
W03_MAIN_BASE = af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
W04 = MERGED / CLOSED / VERIFIED
W04_C01_C10 = CLOSED / VERIFIED
W04_C10 = CLOSED / VERIFIED / GITHUB_SYNCHRONIZED
HUMAN_W04_SPRINT_ACCEPTANCE = ACCEPTED
PR7 = MERGED
PR7_MERGE_SHA = b2b582541d38180c3bf8360699e6df271979829a
PR7_POST_MERGE_CI = #149 / 39008095313 / attempt 1 / SUCCESS
PR7_POST_MERGE_ROUTE = UNKNOWN / FULL_EXACT_SHA
P2_01 = ACCEPTED_LIMITATION / RESOLVED THREAD
P2_02 = ACCEPTED_LIMITATION / RESOLVED THREAD
P2_03 = FUNCTIONAL HARDENING AND R2 FEATURE PROOF COMPLETE / PR8 MERGE CLOSURE PENDING
PR8 = OPEN / READY / UNMERGED
R1_HARDENING_SHA = e2606585829153a2f69c9628c916cf42dcc1b926
R1_DOC_SYNC_SHA = ca2506115b282d9569c3f7c35da266927a39520f
CI150 = #150 / 39017960719 / attempt 1 / FAILURE
CI150_FAILURE = stale C09 publication-verifier historical freeze / nonintegration shard 5
R2_REPAIR_SHA = e706e1f8ed920af0e840fbb9e97725d47d79a2c6
CI151 = #151 / 39030171133 / attempt 1 / SUCCESS / exact e706 historical proof
R3 = REVIEW DISPOSITION AND PR EVIDENCE SYNC COMPLETE / BOTH KNOWN P1 THREADS RESOLVED
MR8_P1_01 = VALID MERGE BLOCKER / e706 normal merge exceeds strict source row count
R4_V2 = CURRENT SEPARATELY AUTHORIZED THREE-PATH MERGE-LIFECYCLE REPAIR
R4_NATIVE_PROOF = PENDING THIS COMMIT'S OWN FIRST EXACT-SHA RUN
W05_SUCCESSOR_GOVERNANCE_REQUIRED = YES
W05_CI_PLANNER_EVOLUTION_REQUIRED_IF_TEST_COLLECTION_CHANGES = YES
W05_DEPENDENCY_MIGRATION_FREEZE_EVOLUTION_REQUIRED_IF_CHANGED = YES
R4_CLAIMS_W05_READY = NO
P2_03_CLOSURE = REQUIRES STABILIZATION PR PROOF AND LATER MERGE / POST-MERGE PROOF
STABILIZATION_BRANCH = fix/post-w04-p2-03-stabilization / RETAINED
STABILIZATION_PR_MERGE = NOT AUTHORIZED
W05 = NOT AUTHORIZED
FLOWLENS_V1_0 = NOT RELEASED
FEATURE_BRANCH = feat/w04-evidence-investigation / RETAINED
~~~

CI #149 proves 2997 selected / 2994 passed / 3 accepted Linux skips, zero adverse
outcomes, entry no-loss / exact union / exact once, Integration 70, W03 38/85 and
W04 9/67/81 PASS at the exact PR #7 merge SHA. Sprint Final 985f666 / CI #147 and
governance repair ecd591f / CI #148 are historical accepted proof identities.
P2-03 was accepted for PR #7 merge with repair required before W05; its resolved
review thread does not itself establish completion of this stabilization.

## 2. Repository source of truth and authority

The Git repository is the source of truth. Read the current explicitly authorized
task and active Human request first. The active task is
POST_W04_P2_03_PR8_MERGE_LIFECYCLE_REPAIR_R4_V2, based on exact main
b2b582541d38180c3bf8360699e6df271979829a and entry PR #8 head
e706e1f8ed920af0e840fbb9e97725d47d79a2c6. Its explicit Human authorization
supersedes the prior task boundary only for this exact three-path repair,
disposable merge simulations, future-compatibility audit, one push and
post-success PR body synchronization. R4 V2 supersedes the earlier R4 design.

CI #150 remains historical attempt-1 FAILURE. CI #151 remains immutable
attempt-1 SUCCESS for exact e706; after this repair it is historical proof,
not current-head proof. R3 resolved PRRT_kwDOT4LAIc6teu85 as repaired/native-proven
and PRRT_kwDOT4LAIc6tf4bs as a review-environment topology mismatch. R3 changed
no source. MR8-P1-01 is a separate valid merge blocker: a normal e706 merge
adds a fourth post-base revision that the pre-R4 validator rejects.

Original W04 Human authority remains preserved in
docs/w04/W04_SPRINT_HUMAN_ACCEPTANCE_AND_AUTHORIZATION.md; historical closeout,
readiness and review records remain immutable.

Apply this order within the frozen W1/W2/W3 architecture and safety invariants:

1. Current authorized task contract and explicit Human authority, including exact
   scope, commit topology, proof identities and stop conditions.
2. Frozen upstream contracts: docs/w03/AI_LOOP_CONSTITUTION.md,
   docs/sprints/W03_ai_decision_loop.md, semantic trust, context/material,
   prompt/tool, state-machine, failure/degradation and harness/reporting contracts,
   plus frozen W1/W2 contracts.
3. W04 checkpoint contracts and accepted Human decisions;
   docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json binds closed C01-C08 source.
   C09/C10 have no runtime source-evolution entry by design.
4. Immutable C10 closeout records under docs/w04/checkpoints/c10/, the Sprint
   independent review, original Human authority and closeout context lock.
5. Immutable Sprint Final/readiness reports, historical PR #7 review dispositions,
   merge topology and exact merge-SHA CI #149 evidence.
6. The current projection of docs/CURRENT_STATE.md, this router and README;
   historical snapshots and chat remain historical evidence.

Lower-authority material cannot weaken an invariant or grant new checkpoint,
merge or release authority. Project skills are procedural automation, governed by
skills/SKILL_ADMISSION_POLICY.md. No skill may change permissions, admit runtime
HGT or self-approve review, acceptance or closeout.

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

## 5. Baseline and current-task freeze

Do not reopen W01/W02/W03 or C01-C10. Preserve operational schema, Alembic
semantics, canonical dataset hashes, deterministic generator semantics,
Supplier/Quality/Capacity scenario semantics, HGT identity/isolation and accepted
historical evidence.

Preserve the exact immutable R1/R2 source rows above main:
e2606585829153a2f69c9628c916cf42dcc1b926 (hardening);
ca2506115b282d9569c3f7c35da266927a39520f (documentation);
e706e1f8ed920af0e840fbb9e97725d47d79a2c6 (R2 proof-closure repair).

R4 V2 authorizes one single-parent child of e706, subject
ci(post-w04): admit PR #8 merge lifecycle, with exactly three M paths:
scripts/ci/verify_w04_investigation_gate_contract.py;
AGENTS.md; docs/CURRENT_STATE.md. Do not edit README or add pytest nodes.

Validate explicit-tip source history as exact States 0-4. Pin all first three
SHAs; admit only the exact fourth repair shape. Discover PR #8 integration
independently: two parents in main/R4 order, main exactly b2b582, feature exactly
the validated R4 tip, identical feature/merge trees and empty feature-to-merge
diff, reachable from HEAD and at most one anchor. Do not pin merge subject.
No recursive anchor/hardening discovery or arbitrary fourth/fifth premerge row.

Before integration, source tip is HEAD. After a validated integration, source
tip remains the anchor's second parent; validate base..R4, not merge/descendant
row count. Keep W04_POST_MERGE_INTEGRATED and emit separate P2 lifecycle states:
P2_03_PR8_PREMERGE_REPAIR, P2_03_PR8_MERGED_MAIN,
P2_03_POST_PR8_INTEGRATED. Later non-protected descendants are not rejected solely
because history is longer; dedicated protected guards still apply.

Through PR #8 closure, classifier/publication and their two R1 tests remain
byte/tree-identical to e260; C09 test to e706; verifier to the validated R4.
Before integration, AGENTS/CURRENT_STATE also match R4. Merge-tree equality
preserves those bytes at integration. After validated integration, lifecycle
README/AGENTS/CURRENT_STATE may evolve. Preserve the full historical verifier
source chain before admitting literal R4 units/connectors; no broad hash bypass.
Preserve original 172 controls, 223 shell cases, P2 93 and R2 95 controls, adding
bounded R4 helper/real-Git controls without recursively running the semantic gate.

Runtime src, dependencies/lock, migrations/schema, apps, workflow, planner,
W03/W04 runners, gate/source-evolution manifests, C01-C10 evidence, historical
closeout files, datasets and .gitattributes remain unchanged in R4.

R4 establishes merge topology continuity only. Current W04 planning still
requires 2997 exact nodes / 63 files / 7 shards and frozen node/file/weights
identities. Current C09 still freezes pyproject.toml, uv.lock, docker-compose.yml,
migrations and apps. W05 changes to collection, dependencies, migrations/apps,
CI or planner require a separate explicitly Human-authorized successor contract:
retain old SHA evidence/history, prove replacement guards and record a new
baseline/version. R4 does not perform that transition or claim W05 readiness.
These assets are not declared impossible to evolve under that future authority.

A contract conflict, semantic/product decision, extra tracked path, possible live
secret/private key, HGT/future leakage, operational mutation or unauthorized
action requires STOP and a separate GPT/Human decision. Local R4 candidates may
be rebuilt before final freeze/push. After freeze, no amend/rebase. A failed
pre-push synthetic merge, first native R4 proof or NEW P0/P1 requires STOP;
no automatic repair, replacement head or rerun-as-proof is authorized.

## 6. Git, verification and completion

~~~text
NO DIRECT MAIN WRITE
NO FORCE PUSH
NO R1 HISTORY REWRITE
NO AMEND / REBASE AFTER R4 FREEZE
NO STABILIZATION PR MERGE / AUTO-MERGE / MERGE QUEUE
NO P1 THREAD RESOLUTION
NO FEATURE-BRANCH DELETION
NO CHECKPOINT AUTO-ADVANCE
~~~

Use the clean full-history LF stabilization branch at entry e706. Preserve the
retained W04 branch. Require Ruff, strict mypy, lock consistency, diff/scope,
all three unchanged focused CI test files, committed-head full W04 governance,
93/95/R4 controls and frozen W04 9/67/81 semantic proof.

The legacy collection remains 2997 nodes / 63 files / 7 shards. Node digest:
9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a.
File digest:
890fdd5c30c7e2a1e90da8cb8b7123937d3356f1d519f82dff4a941f13659fd7.
Weights digest:
a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851.
Workflow, planner, weights, timeouts and semantic manifests are fixed for R4.

Before push, construct an exact normal two-parent merge in disposable full Git
history and run the full governance verifier once there, once at a lifecycle-docs
descendant and once at a later benign two-parent docs merge. Require PASS and
source tip pinned to R4. Prove hostile topologies/protected drifts reject, a
non-protected descendant remains topologically admissible, and the separate
future W05 legacy-freeze audit is recorded. Never push synthetic commits.

After all local/simulation/audit proof, freeze the sole R4 child and push once
normally to PR #8. Its FIRST exact R4 pull_request/synchronize run must be
attempt 1, C / FULL_EXACT_SHA, SUCCESS; Publication proof SKIPPED. Require all
mandatory jobs, 2997/2994/3 with zero adverse outcomes, no-loss/exact-union/
exact-once, Integration 70, W03 38/85, W04 9/67/81 and 93/95/R4 controls.
Do not rerun a failed native run or automatically repair a published head.

Only after native success, synchronize PR body preserving R1/R2/R3 evidence,
R4 exact proof, merge/descendant simulations and the successor-governance
boundary. Refetch all reviews; NEW P0/P1 requires STOP. Keep clean synchronized
local/tracking/direct-origin/PR heads, main unchanged b2b582, branches retained,
and PR OPEN / READY / UNMERGED with auto-merge absent. Package evidence outside
the repository and stop at IMPLEMENTED_PROVEN_AWAITING_FINAL_REVIEW.

PR #8 merge requires a new independent merge review and explicit Human
authorization. W05 requires separate successor-governance and implementation
authority after stabilization closure. FlowLens v1.0 remains NOT RELEASED.
