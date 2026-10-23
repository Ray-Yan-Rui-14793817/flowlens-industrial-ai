# FlowLens Industrial AI — AGENTS.md
> W05-G0 Successor Governance Bootstrap Execution Router

## 1. Current phase and authority

~~~text
CURRENT_PHASE = W05 / SUCCESSOR GOVERNANCE ACTIVE
TASK_ID = W05_G0_SUCCESSOR_GOVERNANCE_RECOVERY_R2
POST_W04_STABILIZATION = CLOSED
POST_MERGE_DOC_SYNC = COMPLETE
PR8 = MERGED / CLOSED / VERIFIED
P2_03 = MERGED_NATIVE_PROVEN_CLOSED
MR8_P1_01 = CLOSED / R4 V2 REPAIR AND MERGE NATIVE PROOF
W04_HISTORICAL_GOVERNANCE_ANCHOR = 2f1627342ff2b04d8324fbffec3db2e230b302e0
PR8_FEATURE_HEAD = bd29242f8e21ba31bc7782e0c98e1a8aed3641f8
PR8_POST_MERGE_CI = #153 / 39142499049 / attempt 1 / SUCCESS
W05_ACTIVE_PLAN = w05-active-non-integration-plan-v1
W05_SUCCESSOR_GOVERNANCE = IMPLEMENTED / FIRST EXACT-HEAD NATIVE PROOF REQUIRED
W05_G0 = IMPLEMENTED / AWAITING LOCAL AND FIRST NATIVE PROOF
W05_C01 = NOT AUTHORIZED BY THIS TASK
W05_C02 = NOT AUTHORIZED
W05_PRODUCT_API = NOT IMPLEMENTED
W05_UI = NOT IMPLEMENTED
W06 = NOT AUTHORIZED
MERGE_AUTHORITY = NO
FLOWLENS_V1_0 = NOT RELEASED
~~~

The explicit Human W05-G0 authorization supersedes the former R4 execution
boundary only for this exact two-commit governance transition. W01/W02, W03 and
W04 C01-C10 remain closed. Runtime authority and frozen invariants below persist.

## 2. Contract, scope and proof

Apply the current authorized task and explicit Human authority first, followed
by frozen W01-W04 architecture, runtime, semantic trust, prompt/tool, replay and
HGT contracts. The Git repository is the source of truth. Original W04 Human
authority and source identities remain in docs/w04; accepted historical reports
are not rewritten. Skills are procedural only (skills/SKILL_ADMISSION_POLICY.md).

Use feat/w05-g0-successor-governance from exact main
2f1627342ff2b04d8324fbffec3db2e230b302e0. Recover the existing full-history
worktree under R2; preserve the exact existing Commit A.

Commit A: docs: synchronize PR #8 merged state
Exactly README.md, AGENTS.md and docs/CURRENT_STATE.md.

Commit B: ci(w05): activate successor governance baseline
Only .github/workflows/ci.yml; scripts/ci/{plan_non_integration_shards.py,
pytest_outcome_receipt.py,run_non_integration_shard.py,
verify_non_integration_shards.py,verify_w05_successor_governance.py};
tests/{test_ci_test_sharding.py,test_c09_ci_gate.py,test_investigation_replay.py,
test_w05_successor_governance.py}; docs/w05/governance/
{W05_G0_W04_HISTORICAL_BASELINE.json,W05_G0_ACTIVE_POLICY.json,
W05_G0_SURFACE_BASELINE.json,W05_G0_SUCCESSOR_GOVERNANCE_CONTRACT.md,
W05_G0_GPT_REVIEW_CHECKLIST.md}; AGENTS.md; docs/CURRENT_STATE.md.
No third commit. No README change in B.

Do not modify src, W03/W04 runners, the W04 governance verifier, historical
docs/w03 or docs/w04 evidence, pyproject.toml, uv.lock, Compose, migrations, apps,
source-evolution manifest or accepted operational data. Those dependency,
Compose, migration and app surfaces are frozen at G0 until explicit versioned
successor admission; they are not permanently immutable.

Historical W04 governance replays only at the exact anchor, preserving
2997 nodes / 63 files / 7 shards, all pinned digests and 172/223/93/95/98 controls.
Current W05 collects exact HEAD dynamically, keeps all historical nodes, permits
additions, uses seven deterministic file-atomic LPT shards, and proves current
exact union/once. Current W03 38/85 and W04 9/67/81 remain semantic regressions.

Ruff, strict mypy, lock, focused controls, current semantic gates, historical
governance replay and active plan proof precede the sole push. First exact
Commit-B native CI attempt 1 must pass. Native IDs belong in PR/external
evidence after they exist. Readiness does not grant C01 or merge authority.

Stop on changed entry main, required extra path, contract conflict, protected
baseline drift, HGT/future leakage, operational mutation or first native failure.
Never repair outside the task or rerun a failed native attempt as proof.

NO DIRECT MAIN WRITE. NO FORCE PUSH. NO HISTORY REWRITE. NO MERGE/AUTO-MERGE/
MERGE QUEUE. NO BRANCH DELETION. NO CHECKPOINT AUTO-ADVANCE.
Keep the G0 PR OPEN / READY / UNMERGED for independent review.

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

## Commit B proof condition

The active successor implementation exists in this branch. Native success is
not available at document authoring time. Only after all required local gates
and this exact Commit B's first attempt-1 full native CI succeed does its
effective projection become:
W05_SUCCESSOR_GOVERNANCE = IMPLEMENTED / NATIVE-PROVEN / AWAITING INDEPENDENT REVIEW.
Generated SHA/run IDs and the effective verdict belong in PR metadata and the
external Development Report. Until then no native-proven or C01-ready claim is
made. Main remains at the historical anchor until a separately authorized merge.

The implemented contract is docs/w05/governance/W05_G0_SUCCESSOR_GOVERNANCE_CONTRACT.md.
