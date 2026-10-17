# FlowLens Industrial AI — AGENTS.md
> Post-W04 Stabilization Repository Execution Router

This router records the bounded Human-authorized POST_W04_P2_03_STABILIZATION_RECOVERY_R2
scope. W04 integration is complete. This task grants no stabilization PR merge,
W05 implementation or FlowLens v1.0 release authority.

## 1. Current phase

~~~text
PROJECT = FlowLens Industrial AI
CURRENT_PHASE = POST-W04 STABILIZATION / P2-03 R2 RECOVERY
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
P2_03 = R1 HARDENING PRESERVED / R2 REPAIR IN CURRENT TREE
PR8 = OPEN / READY / UNMERGED
R1_HARDENING_SHA = e2606585829153a2f69c9628c916cf42dcc1b926
R1_DOC_SYNC_SHA = ca2506115b282d9569c3f7c35da266927a39520f
CI150 = #150 / 39017960719 / attempt 1 / FAILURE
CI150_FAILURE = stale C09 publication-verifier historical freeze / nonintegration shard 5
R2_P1_TOPOLOGY_FINDING = OPEN / repair in current R2 tree
R2_REPAIR = separately Human-authorized recovery / native proof pending
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
POST_W04_P2_03_STABILIZATION_RECOVERY_R2, based on exact main
b2b582541d38180c3bf8360699e6df271979829a and entry PR #8 head
ca2506115b282d9569c3f7c35da266927a39520f. NEW separate Human authorization
supersedes R1's "no repair after push" stop boundary solely for this exact recovery.
R1 CI #150 remains attempt-1 FAILURE; R2 does not retroactively change its evidence.
The known P1 thread PRRT_kwDOT4LAIc6teu85 remains unresolved pending independent
review. This authorization permits one evidence reply after native success,
but grants no thread-resolution or merge authority.
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

Preserve the exact two immutable R1 commits above main:
e2606585829153a2f69c9628c916cf42dcc1b926 (five-file hardening) followed by
ca2506115b282d9569c3f7c35da266927a39520f (three-document synchronization).

R2 authorizes exactly one single-parent child of ca250611, subject
ci(post-w04): repair stabilization proof closure, with exactly four M paths:
scripts/ci/verify_w04_investigation_gate_contract.py;
tests/test_c09_ci_gate.py; AGENTS.md; docs/CURRENT_STATE.md.

The sole C09 test-body evolution is
test_classifier_publication_and_runtime_frozen_materials_unchanged. Keep its
name/signature/decorators, pyproject/lock/Compose historical freezes,
migrations/apps no-drift and source-evolution proof. Pin publication verifier
to exact e260. Classifier, publication verifier and their two R1 test files
remain byte-identical to e260.

Validate the entire ordered post-base history: exact hardening, optionally exact
ca250 documentation child, optionally the single exact R2 repair child. Reject
every other descendant, wrong metadata or non-M path status. Preserve the
historical verifier-source chain, original 93 P2 controls and frozen test nodes.
After R2, freeze the four repair paths to its validated committed revision.

Preserve runtime src, dependencies/lock, migrations/schema, workflow, W03/W04
runners, gate/source-evolution manifests, C01-C10 evidence, historical closeout
files, dataset, README and .gitattributes. No broad source exemption is authorized.

A contract conflict, semantic/product decision, extra tracked path, possible live
secret/private key, HGT/future leakage, operational mutation or unauthorized
action requires STOP and a separate GPT/Human decision. Local R2 candidates may
be rebuilt before freeze/push. After push, failed native proof or a NEW P0/P1
finding requires STOP; no automatic further repair or rerun-as-proof.

## 6. Git, verification and completion

~~~text
NO DIRECT MAIN WRITE
NO FORCE PUSH
NO R1 HISTORY REWRITE
NO AMEND / REBASE AFTER R2 FREEZE
NO STABILIZATION PR MERGE / AUTO-MERGE / MERGE QUEUE
NO P1 THREAD RESOLUTION
NO FEATURE-BRANCH DELETION
NO CHECKPOINT AUTO-ADVANCE
~~~

Resume the clean full-history LF stabilization workspace at ca250611. Preserve
the retained W04 branch. Require the formerly failing C09 selector, all three
focused governance test files, Ruff, strict mypy, lock consistency, diff/scope
checks, full committed-head W04 governance, original 93 plus deterministic R2
controls and frozen W04 9/67/81 semantic proof.

The collection remains 2997 nodes / 63 files / 7 shards. Node digest:
9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a.
Weights digest:
a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851.
Workflow topology, weights, timeouts and semantic manifests remain fixed.

Freeze the repair SHA after complete local proof. Push the one exact child once
normally to existing PR #8. Its FIRST exact repair-head pull_request/synchronize
run must be attempt 1, I / FULL_EXACT_SHA, SUCCESS; Publication proof SKIPPED.
Require all mandatory jobs, 2997/2994/3 with zero adverse outcomes, entry no-loss /
exact union / exact once, Integration 70, W03 38/85, W04 9/67/81, original
93 P2 controls/e260 and new R2 controls/exact repair SHA. Do not rerun CI #150
or substitute a rerun of a failed repair-head run.

Only after native success, synchronize PR metadata preserving #150 failure and
reply once with evidence to the known P1 thread. Leave it unresolved for NEW
independent review. Require clean synchronized local/tracking/direct-origin/PR
heads, unchanged main b2b582541d38180c3bf8360699e6df271979829a, retained branches
and PR OPEN / READY / UNMERGED with auto-merge absent. Package evidence outside
the repository and stop at repaired/proven awaiting independent review.

Stabilization merge requires new explicit Human authorization. W05 requires
completed stabilization proof/merge and separate authorization. FlowLens v1.0
remains NOT RELEASED.
