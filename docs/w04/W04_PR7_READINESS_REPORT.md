# W04 PR #7 Readiness Report

Authored from the recovered successful Prep #146 boundary and before the Sprint Final commit. This is a pre-commit readiness design/entry record, not an assertion that Draft -> Ready has already occurred.

## Verified entry

```text
REPOSITORY = Ray-Yan-Rui-14793817/flowlens-industrial-ai
PR = #7
HEAD_BRANCH = feat/w04-evidence-investigation
HEAD_SHA = c8b29cbcffe1886412de4a31b75905f6397043fb
BASE_BRANCH = main
BASE_SHA = af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
STATE = OPEN
DRAFT = TRUE
MERGED = FALSE
MERGEABLE = TRUE
AUTO_MERGE = ABSENT / DISABLED
ENTRY_TITLE = W04-C01: immutable investigation contracts
ENTRY_BODY = STALE C01-ONLY PROJECTION
ENTRY_COMMITS = 60
ENTRY_CHANGED_FILES = 177
ENTRY_DIFF = +62636 / -153
PREP_CI = #146 / 38735686969 / SUCCESS / attempt 1
PREP_CLASS = C / FULL_EXACT_SHA
PREP_LIFECYCLE = W04_SPRINT_CLOSEOUT_PREP_01
```

The original Human accepted W04 C01-C10 and the Sprint closeout design, and approved PR7_READINESS_AUTHORIZATION. Its complete source is preserved in `W04_SPRINT_HUMAN_ACCEPTANCE_AND_AUTHORIZATION.md`, original raw SHA-256 `e165fa2945ce0cf0c8fc230cb5faf5f65d7ce3021af8817bd0830168a61a3f5d`. The resume continues that authorization; it does not authorize merge or replace the original message.

The independent Sprint review at `W04_GPT_INDEPENDENT_DEEP_REVIEW_R1.md` is byte-identical to the supplied source, raw SHA-256 `061fc3f41659499fc7e1069345abe7b1d0feeab65504eb79e48b6a929665de59`. It passes readiness design and explicitly withholds merge authority.

## Required proof before metadata transition

```text
SPRINT_FINAL_SHA = GENERATED POST-COMMIT / NOT YET CREATED
SPRINT_FINAL_NATIVE_CI = GENERATED POST-COMMIT / PENDING
EXPECTED_CLASS = UNKNOWN / FULL_EXACT_SHA
REQUIRED_ATTEMPT = 1
REQUIRED_RESULT = SUCCESS
REQUIRED_LIFECYCLE = W04_SPRINT_FINAL_CLOSEOUT
```

Final must be one direct child of the successful Prep with exact subject `docs(w04): close sprint and prepare PR #7 review` and exactly the eight authorized documentation paths. The Prep verifier and every protected implementation/checkpoint object remain frozen. A fresh full-history LF candidate must pass all local gates before primary application; one normal Final commit/push follows. No repair, replacement Final, amend or rerun-as-proof is authorized after a failed gate.

Require the new Final's own original ZIP/log/JUnit proof: 2997 selected / 2994 passed / 3 accepted skips; zero failed/error/xfail/xpass; entry no-loss, exact union and exact once PASS; Integration 70; W03 38/85; W04 9/67/81; W04_SPRINT_FINAL_CLOSEOUT; all shard job/pytest <3300s. Publication is skipped under the unchanged full route.

The read-only current-tree/reachable-history security audit must pass with no live external credential or private key. Known local/test defaults and synthetic fixtures retain their proven non-external dispositions. No source-history rewrite is permitted.

## Authorized PR metadata transition

Only after Final native SUCCESS and fresh synchronization require:

```text
LOCAL_HEAD = TRACKING_HEAD = DIRECT_ORIGIN_HEAD = PR7_HEAD = ACTUAL_SPRINT_FINAL_SHA
AHEAD_BEHIND = 0/0
WORKTREE_INDEX = CLEAN
MAIN_BASE = af61bdfd5f7cf7961811c4c2dc8e554dd7eed509 / UNCHANGED
MERGEABLE = TRUE
```

Set the exact title:

```text
W04: evidence-grounded investigation workflow (C01-C10)
```

Replace the C01-only body with a complete W04 review surface containing these sections:

1. Summary.
2. Primary User / User Story.
3. Delivered W04 C01-C10.
4. Authority / Safety Boundaries.
5. Exact-SHA Verification.
6. C10 + W04 Sprint Closeout.
7. Security / Secret Review.
8. Known Non-blocking Limitations.
9. Review Notes for the Large PR.
10. Merge Boundary.

The body must contain the actual generated Final SHA and its own actual native CI run, along with Prep #146, accepted metrics, lifecycle, immutable source identities, security disposition and deferred debt. No pre-commit placeholder may be presented as completed native proof.

Then mark Draft -> Ready for review. Do not request/submit an independent review on behalf of a reviewer, merge, enable auto-merge, enter merge queue or delete the feature branch.

## Final-state proof and stop

Re-read PR and Git state after title/body and Ready transition. Require:

```text
PR7_STATE = OPEN
PR7_DRAFT = FALSE
PR7_MERGED = FALSE
PR7_MERGEABLE = TRUE
PR7_BASE = main
PR7_BASE_SHA = af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
PR7_HEAD_SHA = ACTUAL_SPRINT_FINAL_SHA
PR7_TITLE = W04: evidence-grounded investigation workflow (C01-C10)
PR7_AUTO_MERGE = ABSENT / DISABLED
FEATURE_BRANCH = RETAINED
LOCAL_TRACKING_DIRECT_ORIGIN_PR = SYNCHRONIZED / CLEAN / 0/0
```

A changed main/base requires W04_PR7_READINESS_BASE_DRIFT STOP. A failed transition/state proof requires W04_PR7_READINESS_TRANSITION_FAILED STOP. Native/local proof failure also stops without repair or rerun-as-proof.

Only after these checks may the post-CI handoff declare W04_SPRINT_FINAL_CLOSEOUT_COMPLETE and PR #7 OPEN / READY / UNMERGED. W04 C01-C10 remain CLOSED / VERIFIED; FlowLens v1.0 remains NOT RELEASED.

PR merge review is PENDING INDEPENDENT GPT REVIEW + HUMAN AUTHORIZATION. Merge, auto-merge, merge queue, branch deletion, main write, W05 and post-W04 implementation remain NOT AUTHORIZED. Readiness does not grant those powers.

## Reviewability and preserved limitations

The PR is a large W04 integration history. Review C01-C08 implementation/source evolution, C09 regression enforcement, C10 acceptance and the two Sprint lifecycle/governance commits as distinct evidence layers. Do not squash, rebase or rewrite accepted history inside this task. The supplied review's 59-commit entry and this recovered 60-commit Prep entry are historical observations; actual Final PR size belongs in the post-CI body/handoff.

Keep C06 local-journal/authentication limits, bounded optional LLM/fallback limits, synthetic-data and offline/shadow boundaries explicit. Findings/association are not causal truth, Human notes are not evidence, replay is not evidence refresh and no operational intervention is executed.

Carry NB-C09-01, NB-C10-ENV-01, NB-W04-CI-01, NB-W04-GOV-01, NB-W04-PR-SIZE-01 and NB-W04-CI-02 without repair. The Node.js 20 -> 24 artifact-action warning is maintenance debt; workflow/action pins remain frozen.
