# FlowLens Industrial AI — AGENTS.md
> W04 Final Repository Execution Router

This router records the Human-authorized W04 Sprint Final Closeout / PR #7 Readiness boundary. It grants no additional implementation or merge authority.

## 1. Current phase

```text
PROJECT = FlowLens Industrial AI
CURRENT_PHASE = W04 SPRINT FINAL CLOSEOUT / PR #7 READINESS
PRIMARY_LOOP = Order Delivery Risk Decision Loop + Evidence-grounded Investigation
MODE = OFFLINE / SHADOW / HUMAN-IN-THE-LOOP
CORE = DETERMINISTIC-FIRST
W01 / W02 = CLOSED / VERIFIED
W03 = MERGED / CLOSED / VERIFIED
W03_MAIN_BASE = af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
W04_C01_C10 = CLOSED / VERIFIED
W04_C10 = CLOSED / VERIFIED / GITHUB_SYNCHRONIZED
HUMAN_W04_SPRINT_ACCEPTANCE = ACCEPTED
SPRINT_CLOSEOUT_PREP = COMPLETE / OWN-SHA CI #146 SUCCESS / attempt 1
SPRINT_FINAL_CLOSEOUT = EFFECTIVE ONLY AFTER THIS COMMIT'S OWN NATIVE CI AND FOUR-HEAD SYNCHRONIZATION PASS
PR7 = W04 INTEGRATION PR
PR7_READINESS = AUTHORIZED AFTER SPRINT FINAL OWN-SHA PROOF
PR7_MERGE = NOT AUTHORIZED
POST-W04_IMPLEMENTATION = NOT AUTHORIZED
W05 = NOT AUTHORIZED
FLOWLENS_V1_0 = NOT RELEASED
FEATURE_BRANCH = feat/w04-evidence-investigation / RETAINED
```

The generated Sprint Final SHA/native run and actual PR Ready transition are recorded after proof in the final handoff and PR metadata. Pre-commit conditional fields are not permission to infer a successful run or a merge.

## 2. Repository source of truth and authority

The Git repository is the source of truth. Read the current explicitly authorized task first. The active closeout contract is W04-SPRINT-FINAL-CLOSEOUT-PR7-READINESS-V1, continued by RESUME_FROM_PREP146_TASK_V1. Original Human authority is preserved in `docs/w04/W04_SPRINT_HUMAN_ACCEPTANCE_AND_AUTHORIZATION.md`; a resume prompt does not replace it.

Apply this order within the frozen W1/W2/W3 architecture and safety invariants:

1. Current authorized task contract and explicit Human authority, including its exact scope, hashes and stop conditions.
2. Frozen upstream contracts: `docs/w03/AI_LOOP_CONSTITUTION.md`, `docs/sprints/W03_ai_decision_loop.md`, semantic trust, context/material, prompt/tool, loop state-machine, failure/degradation and harness/reporting contracts, plus frozen W1/W2 contracts.
3. W04 checkpoint authorization/contracts and accepted Human decisions; `docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json` binds closed C01-C08 source identities. C09/C10 have no runtime source-evolution entry by design.
4. W04 C10 final closeout records under `docs/w04/checkpoints/c10/`, including its independent review, Human acceptance, authorization, context lock and final report.
5. `docs/w04/W04_GPT_INDEPENDENT_DEEP_REVIEW_R1.md`, the original Human sprint authority record and `docs/w04/W04_SPRINT_CLOSEOUT_CONTEXT_LOCK.md`.
6. `docs/w04/W04_SPRINT_FINAL_CLOSEOUT_REPORT.md` and `docs/w04/W04_PR7_READINESS_REPORT.md`, interpreted with their own-SHA proof conditions.
7. The current top projection of `docs/CURRENT_STATE.md` and README. Historical sections, reports and chat remain historical evidence.

Lower-authority material cannot silently weaken an invariant or grant new checkpoint/merge authority. Project skills are procedural automation, not architectural truth; see `skills/SKILL_ADMISSION_POLICY.md`. No skill may change permissions, admit runtime HGT or self-approve review/acceptance/closeout.

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

Do not reopen W01/W02/W03 or C01-C10. Preserve operational schema, Alembic semantics, canonical dataset hashes, deterministic generator semantics, Supplier/Quality/Capacity scenario semantics, HGT identity/isolation and accepted historical evidence.

For this Sprint Final task, only the exact eight documentation paths in `W04_SPRINT_CLOSEOUT_CONTEXT_LOCK.md` may change. Preserve all src, tests, workflows, scripts/ci, dependencies/lock, migrations/schema, source-evolution manifest, C01-C10 evidence, C10 closeout files and .gitattributes. The successful Prep verifier is frozen. Do not create another Prep or rerun #146 as substitute proof.

A contract conflict, semantic/product decision, protected baseline change, possible live secret/private key, HGT/future leakage, operational mutation or unauthorized action requires STOP and a separate GPT/Human decision. Under the current task, a failed candidate or native gate also requires STOP; no automatic repair, replacement Final or rerun-as-proof is authorized.

## 6. Git, verification and completion

```text
NO DIRECT MAIN WRITE
NO FORCE PUSH
NO HISTORY REWRITE
NO AMEND / REBASE / DESTRUCTIVE RESET
NO MERGE / AUTO-MERGE / MERGE QUEUE
NO FEATURE-BRANCH DELETION
NO CHECKPOINT AUTO-ADVANCE
```

The existing Prep is `c8b29cbcffe1886412de4a31b75905f6397043fb`, native #146 / 38735686969, C / FULL_EXACT_SHA, attempt 1 SUCCESS. Final must be its single-parent child with subject `docs(w04): close sprint and prepare PR #7 review`, exactly three modified and five added authorized paths, and committed-head `W04_SPRINT_FINAL_CLOSEOUT`.

Require a disposable full-history LF candidate, exact frozen bytes/scope, Ruff, strict mypy, whitespace/security proof and unchanged source evolution before primary application. Apply only proven bytes, create one normal Final commit and push once. Its own attempt-1 UNKNOWN / FULL_EXACT_SHA run must prove 2997/2994/3 with zero adverse outcomes, no-loss/exact-union/exact-once, Integration 70, W03 38/85, W04 9/67/81 and every shard job/pytest <3300s. Classifier, topology, weights and timeouts remain frozen.

After native success, require clean local/tracking/direct-origin/PR heads equal to Final, 0/0 and unchanged main/base. Only then update PR #7 title/body and Draft -> Ready. Keep it OPEN / UNMERGED, auto-merge absent/disabled and the feature branch retained.

Stop at W04_SPRINT_FINAL_CLOSEOUT_COMPLETE + PR #7 READY FOR HUMAN MERGE REVIEW. PR merge requires a separate independent GPT merge review and explicit Human authorization. POST-W04 IMPLEMENTATION and W05 remain NOT AUTHORIZED.
