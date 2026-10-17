# W04-DEVCTRL-02 Closeout Context Lock

Locked at 2026-10-11T13:11:13+08:00, before any closeout document write. The complete CLOSEOUT-V1 task and Human authorization were read; the task's raw SHA-256 matched. Fresh git fetch, independent direct-origin refs, GitHub PR metadata and native run metadata established the following activation.

```text
TASK: W04-DEVCTRL-02 FINAL DOCUMENTATION-ONLY CLOSEOUT
TASK VERSION: CLOSEOUT-V1
TASK RAW SHA-256:
457402af772c183e12eced80b1191f015a59369f41f42b1f679ac44f7b0514e0
CONTEXT: LOCKED
ENTRY / REVIEW-READY SHA:
d4af04d898c144462ebc8497bf540d84f2003a91
BRANCH:
feat/w04-evidence-investigation
PR #7:
OPEN / DRAFT / UNMERGED
MAIN / PR BASE:
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
R2:
a026d6a4625c3d9287a558fb2726e362a3ea02fc / #124 / SUCCESS
B2:
d4af04d898c144462ebc8497bf540d84f2003a91 / #125 / SUCCESS
GPT INDEPENDENT REVIEW:
PASS
HUMAN ACCEPTANCE:
ACCEPTED
CLOSEOUT AUTHORIZATION:
APPROVED
```

## Verified activation

Local HEAD, tracking feature HEAD, direct origin feature HEAD and PR #7 HEAD all equal the entry SHA. Local main, tracking main, direct origin main and PR base equal the frozen main/base. Tracking ahead/behind is 0/0; worktree/index is CLEAN. PR #7 is OPEN / DRAFT / UNMERGED.

R2 #124 / 37935157006 and B2 #125 / 37955158260 are completed SUCCESS at their own accepted SHAs, attempt 1. #125 is the latest feature-branch CI; no newer feature commit or CI exists. All five allowed paths are absent at entry. All 14 protected Git objects below match the task's expected entry identities.

## Frozen proof identities

```text
NONINT COLLECTED NODE COUNT:
2807
NONINT COLLECTED NODE SHA-256:
4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d
NONINT PASSED NODE SHA-256:
b8264ccb9cf6f71357aef371c6749211ecf5dc20acfc3019f0516657005154b0
ACCEPTED SKIP NODE SHA-256:
1524192888846ac2a7b1908212650648a38816aa72d458add70868c24d08a767
NONINT OUTCOME MAP SHA-256:
f38fb0268e32b045113ef57684057ae102edb12e5e32de855c0e504d1418ff9b
INTEGRATION NODE COUNT:
70
INTEGRATION NODE SHA-256:
bdcb72ebf947f5599d9e6cecf9bc29e65e9cb063daa03a715b41f5399ecf581c
INTEGRATION OUTCOME MAP SHA-256:
39c51cd99dd731256261b320d0c8b2ef1e05bc178eb339590afbf274d5492469
ENTRY BASELINE NODE SHA-256:
0089b5889f7de2dbe637ddef3774966ae07f6cf6d6518f2648f20e47ccbaa4a7
B2 PLAN SHA-256:
a43ddf58d48939d7efbd54c10cc75a8bb65edea267043fae19c85a9b55538159
WEIGHTS SHA-256:
315675b184abd56422f469a44da5f840b40d82c3cfb272d46873afd7a8adacca
```

R2 same-SHA equivalence passed before B2 authoritative cutover. Exact coverage is 2807 non-integration selected / 2804 passed / exactly three accepted Linux skips, integration 70 passed, and zero failed/error/xfail/xpass. Seven-shard union, exactly once and entry no-loss passed. W03 retained 38 selectors / 85 cases and manifest digest bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990.

## Protected entry Git objects

| Path | Verified entry Git object |
|---|---|
| `src` | `32856501648e4fea75489be8dd467553e9888fd1` |
| `apps` | `597399c7919982e9b2d54fc8b58fe6784cfe8585` |
| `migrations` | `c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433` |
| `docs/w03` | `cb81e388c6c44a9900575ef2e72161dc0205be94` |
| `scripts/ci` | `bf3871e60a40db1fa378f36f9febdfc1ffe6efe3` |
| `tests` | `f37efadb30dfc61e05811e80ff130d9f749b7911` |
| `.github` | `d85309ff678a4a17dafad77d3cac748822257a9b` |
| `pyproject.toml` | `318bbc0a858f760e6c4d7a2d3fdbfcc111febb77` |
| `uv.lock` | `619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a` |
| `docker-compose.yml` | `5a0b6e8486edc69f9f79c7e1345a842aa412983c` |
| `docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json` | `3a173837de8ea3888de7f9a7de0fd4e34b7f0a5b` |
| `docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json` | `93ebe129f9345ea540b5e06aef053f2a62bb0846` |
| `docs/w04/devctrl-02/W04_DEVCTRL_02_POST123_V2_4_AUTHORIZATION.md` | `3a0108b87c528bce2bcf4a43343fbb5a93ff9724` |
| `docs/w04/devctrl-02/W04_DEVCTRL_02_POST123_V2_4_CONTEXT_LOCK.md` | `726150c295255d13c93986d84574544f75e8e57b` |

Every other entry Git object outside the exact five-file allowlist is also protected. Existing authorization/context/Repair-01/POST123 V2.4 evidence must remain immutable.

## Exact closeout allowlist

```text
docs/w04/devctrl-02/W04_DEVCTRL_02_GPT_INDEPENDENT_REVIEW_R1.md
docs/w04/devctrl-02/W04_DEVCTRL_02_HUMAN_ACCEPTANCE.md
docs/w04/devctrl-02/W04_DEVCTRL_02_CLOSEOUT_AUTHORIZATION.md
docs/w04/devctrl-02/W04_DEVCTRL_02_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/devctrl-02/W04_DEVCTRL_02_FINAL_CLOSEOUT_REPORT.md
```

Exact subject: docs(w04-devctrl-02): close resilient exact-SHA CI optimization. Exactly one direct child of the entry SHA and one normal feature push are authorized.

Forbidden mutation surface:

```text
.github/**
scripts/ci/**
tests/**
src/**
apps/**
migrations/**
docs/w03/**
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/**
docs/w04/devctrl/**
docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json
existing DEVCTRL-02 authorization/context/repair/POST123 V2.4 documents
docs/CURRENT_STATE.md
pyproject.toml
uv.lock
docker-compose.yml
README.md
AGENTS.md
LOOP.md
every other path outside the exact five-file allowlist
```

Runtime/product source, operational truth, dependencies, migrations/schema, W03 semantics, C01-C07 frozen source, HGT isolation, data authority, test nodes and CI/classifier/publication behavior must remain unchanged.

## Expected classifier and native closeout proof

The GPT review and final-closeout report basenames classify P; Human acceptance, closeout authorization and context lock classify C. The combined verified source-head delta therefore expects C / FULL_EXACT_SHA. The native classifier is authoritative and remains unchanged; ambiguous event boundaries retain full proof.

The closeout SHA does not exist at lock time. Its own native run must reach terminal SUCCESS with:

```text
Classify change = SUCCESS
Static and plan = SUCCESS
Integration and data = SUCCESS
Non-integration shard 0 = SUCCESS
Non-integration shard 1 = SUCCESS
Non-integration shard 2 = SUCCESS
Non-integration shard 3 = SUCCESS
Non-integration shard 4 = SUCCESS
Non-integration shard 5 = SUCCESS
Non-integration shard 6 = SUCCESS
Non-integration aggregate = SUCCESS
Quality gate = SUCCESS
Docker Compose smoke = SUCCESS
W03 AI loop gate = SUCCESS
Verification gate = SUCCESS
Publication proof = SKIPPED
```

Require exact 2807/2804/3 non-integration outcomes, integration 70 passed, zero failed/error/xfail/xpass and exact union/exact once/entry no-loss PASS. Record actual workflow elapsed, proof execution elapsed, active duration sum, queue/start delay and longest shard honestly; no new closeout latency SLO or optimization stage is authorized.

Only after native success verify local/tracking/direct-origin/PR head equality to the generated closeout SHA, ahead/behind 0/0, CLEAN worktree/index, frozen main/base and OPEN / DRAFT / UNMERGED PR #7. Actual future SHA/run values will be supplied in the final handoff without amending the committed pre-CI report.

## Hard stops and terminal authority

```text
W04_DEVCTRL_02_CLOSEOUT_CONTEXT_CHANGED
W04_DEVCTRL_02_CLOSEOUT_SCOPE_VIOLATION
W04_DEVCTRL_02_CLOSEOUT_PROTECTED_OBJECT_DRIFT
W04_DEVCTRL_02_CLOSEOUT_DECISION_INCONSISTENCY
W04_DEVCTRL_02_CLOSEOUT_REQUIRES_GPT_CLARIFICATION
W04_DEVCTRL_02_CLOSEOUT_CI_FAILED
W04_DEVCTRL_02_CLOSEOUT_SYNC_FAILED
```

On any activation/scope/protected-object/decision/CI/synchronization failure, stop at the corresponding code. No automatic repair, replacement commit or rerun. Ambiguity outside the contract requires fail-closed clarification.

B3 / Stage C are superseded by POST123 V2.4 and not executed. W04-C08, DEVCTRL-03, PR ready-for-review, merge/auto-merge, branch deletion, main write and history rewrite are not authorized. Stop after final closeout synchronization and handoff.
