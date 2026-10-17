# W04-C08 Final Closeout Authorization

Recorded on 2026-10-12 (Asia/Shanghai). Authority: the supplied Human acceptance/closeout request and CLOSEOUT-V1, not a new Codex review decision.

```text
DECISION = APPROVED
C08_CLOSEOUT_AUTHORIZATION = APPROVED
TASK VERSION = CLOSEOUT-V1
TASK RAW SHA-256 = bd1b9fb49b274f115ff9aba1db3f73f94ddcf3f4cf23cd3eb63cabe9f6ca593e
HUMAN REQUEST RAW SHA-256 = 5f6d43d65cfb6024460f4a1283311c5416c31cc821b7b868441cb6ba07c29e1a
SUCCESSFUL PREP-01 SHA = 0047bb942e8e4227af8d6fb5c9a4763688a22aab
SUCCESSFUL PREP-01 CI = #132 / 38200544252 / SUCCESS / I / FULL_EXACT_SHA
ACCEPTED C08 SOURCE FREEZE = 1fa7b505980c1efc1b3725cd57a9732e254bccdf
FINAL_CLOSEOUT_SHA = NOT YET CREATED
FINAL_CLOSEOUT_CI = PENDING
```

Phase 1 is complete with its own full native SUCCESS. The Human explicitly authorizes automatic continuation to Phase 2 without another checkpoint. Final effectiveness requires the new final closeout commit's own full native SUCCESS and clean final synchronization.

## Exact six-path scope

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c08/W04_C08_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md
docs/w04/checkpoints/c08/W04_C08_HUMAN_ACCEPTANCE.md
docs/w04/checkpoints/c08/W04_C08_CLOSEOUT_AUTHORIZATION.md
docs/w04/checkpoints/c08/W04_C08_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/checkpoints/c08/W04_C08_FINAL_CLOSEOUT_REPORT.md
```

Only C08 transitions AUTHORIZED -> CLOSED. Its freeze SHA is the accepted Stage B value above and its two blob OIDs are the accepted runtime blobs below. Preserve all C01-C07 objects and manifest schema/policy/root/order; do not append C09.

| Path | Git blob OID |
|---|---|
| src/flowlens/investigation/c08_policy.py | `273d288cf4b0e55b646cd2e6751f0259e463a5ff` |
| src/flowlens/investigation/c08_replay.py | `4fa391cf751377305315b7de8303ce94e6eb6c6e` |

## Required execution

Before primary mutation, use a disposable full-history clone at exact successful Prep HEAD, apply these same six intended files and create one local candidate commit. Never push that candidate. Require R43 CLOSED, the source-evolution suite and production verifier to pass, with exact six-path delta and protected objects unchanged. Delete the disposable workspace after proof.

Re-fetch and verify primary Prep HEAD, clean 0/0 state and unchanged PR/main. Apply byte-for-byte the same six files. Create exactly one normal final commit with subject `docs(w04-c08): close protected investigation replay`. Before the single normal push, rerun R43/source-evolution tests and the production verifier against the real committed HEAD. Require the new SHA's own full exact-SHA native CI and final clean 0/0 synchronization.

## Forbidden scope and hard stops

No Phase-2 runtime/test/planner/workflow/weights/timeout/topology/dependency/schema/migration/W03/C01-C07 change. Existing five C08 control/evidence files and the Prep test remain frozen. No amend/rebase/reset/force push/history rewrite, retry/rerun/repair commit, credential cleanup, C09, PR ready/merge, branch deletion or main write.

Context or protected-object drift, decision inconsistency or scope violation stops execution. Any candidate proof failure is `W04_C08_CLOSEOUT_REQUIRES_GPT_CLARIFICATION`; any final native failure is `W04_C08_CLOSEOUT_CI_FAILED`; synchronization failure is `W04_C08_CLOSEOUT_SYNC_FAILED`. No automatic repair or replacement closeout commit.

The Human accepts the #129 shard-1 job duration of 3176s against the unchanged 3300s timeout: 124s headroom, approximately 3.8%. The C08 JUnit duration sum is 3082.523s versus the sealed bootstrap scheduling weight of 1061.491s. This is NON-BLOCKING FOLLOW-UP engineering work, deferred to separate authorization. No re-weight, timeout, retry, shard topology or workflow change is authorized by this closeout.
