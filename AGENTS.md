# FlowLens Industrial AI — AGENTS.md
> Post-W04 Stabilization Repository Execution Router

This router records the bounded Human-authorized POST_W04_P2_03_STABILIZATION_R1
scope. W04 integration is complete. This task grants no stabilization PR merge,
W05 implementation or FlowLens v1.0 release authority.

## 1. Current phase

~~~text
PROJECT = FlowLens Industrial AI
CURRENT_PHASE = POST-W04 STABILIZATION / P2-03 GOVERNANCE HARDENING
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
P2_03 = HARDENING PRESENT IN CURRENT TREE
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
POST_W04_P2_03_STABILIZATION_R1, based on exact main
b2b582541d38180c3bf8360699e6df271979829a. Its exact two-commit scope supersedes
the historical Sprint Final documentation-only scope for this task alone.
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

Only the following two single-parent commits are authorized above exact entry
main b2b582541d38180c3bf8360699e6df271979829a:

1. Subject: ci(post-w04): harden publication deletion governance. Parent: exact
   entry main. Exactly five modified paths: scripts/ci/classify_change.py;
   scripts/ci/verify_publication.py;
   scripts/ci/verify_w04_investigation_gate_contract.py;
   tests/test_ci_change_classifier.py; tests/test_ci_publication_gate.py.
2. Subject: docs: synchronize W04 merged state. Parent: the validated hardening
   commit. Exactly three modified paths: README.md; AGENTS.md;
   docs/CURRENT_STATE.md.

Classifier/publication changes admit only verified synchronize publication A/M
status to light proof; all non-A/M publication deltas route full and missing
head content is rejected. W04 governance first validates the historical source
chain, admits the exact five-file hardening child and freezes those five blobs
for descendants. The test-source evolution is limited to the four task-named
existing function bodies; names, signatures, decorators, parameter lists and
all other top-level source spans remain fixed. No new pytest node is authorized.

Preserve all runtime src, dependencies/lock, migrations/schema, workflow,
W03/W04 runners, W04 gate manifest, source-evolution manifest, C01-C10 evidence,
historical closeout files, dataset and .gitattributes. No broad protected-path
exemption is permitted.

A contract conflict, semantic/product decision, extra tracked path, possible live
secret/private key, HGT/future leakage, operational mutation or unauthorized
action requires STOP and a separate GPT/Human decision. Local candidates may be
iterated only before their required freeze. After push, native failure or a new
P0/P1 finding requires STOP; no automatic repair, rerun-as-proof or scope expansion.

## 6. Git, verification and completion

~~~text
NO DIRECT MAIN WRITE
NO FORCE PUSH
NO DESTRUCTIVE RESET OF HUMAN WORK
NO AMEND / REBASE AFTER FREEZE
NO STABILIZATION PR MERGE / AUTO-MERGE / MERGE QUEUE
NO FEATURE-BRANCH DELETION
NO CHECKPOINT AUTO-ADVANCE
~~~

Use a new clean full-history LF clone/worktree rooted at exact entry main and the
required stabilization branch. Preserve the retained W04 feature branch. Require
focused classifier/publication tests, Ruff, strict mypy, lock consistency,
whitespace/scope checks, full W04 governance, W04 9/67/81 semantic proof and the
frozen 2997-node / 63-file / 7-shard plan at the required commit boundaries.
Freeze the hardening SHA after Commit-1 proof, then freeze the final SHA after
Commit-2 proof. The final history contains exactly those two commits.

The frozen node digest is
9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a;
the frozen weights digest is
a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851.
Classifier/publication source guards evolve only within this authorized task;
workflow topology, weights, timeouts and semantic manifests remain fixed.

After complete local proof, push once normally and create one Ready PR to main.
Its first exact final-head pull_request/opened run must be attempt 1,
UNKNOWN / FULL_EXACT_SHA and SUCCESS: all mandatory jobs, 2997/2994/3 with zero
failed/error/xfail/xpass, no-loss / exact union / exact once, Integration 70,
W03 38/85, W04 9/67/81, and the exact hardening SHA plus actual P2-03 control
count. An earlier green SHA or a rerun cannot substitute for this proof.

Finally require unchanged main at b2b582541d38180c3bf8360699e6df271979829a,
clean synchronized local/tracking/direct-origin/PR final heads, branch retained,
and PR OPEN / READY / UNMERGED with auto-merge absent. Package evidence outside
the repository. Stop at implemented/proven awaiting independent review. Any
stabilization merge requires new explicit Human authorization. W05 additionally
requires completed stabilization proof/merge and separate explicit authorization;
FlowLens v1.0 remains NOT RELEASED.
