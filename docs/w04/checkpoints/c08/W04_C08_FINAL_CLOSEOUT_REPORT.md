# W04-C08 Immutable Final Closeout Report

Authored on 2026-10-12 (Asia/Shanghai), before the candidate and real final closeout commits. This report records supplied review/acceptance and measured completed upstream/Prep evidence. Future generated commit/run values remain pending and belong in the final handoff; this report will not be amended after push.

```text
REPORT_STAGE = PRE-COMMIT / PRE-CLOSEOUT-CI
FINAL_CLOSEOUT_SHA = NOT YET CREATED
FINAL_CLOSEOUT_CI = PENDING
EFFECTIVE C08 CLOSURE = PENDING OWN-SHA FULL CI AND FINAL SYNCHRONIZATION
GPT_INDEPENDENT_IMPLEMENTATION_REVIEW = PASS
HUMAN_C08_ACCEPTANCE = ACCEPTED
C08_CLOSEOUT_AUTHORIZATION = APPROVED
C08 SOURCE FREEZE = 1fa7b505980c1efc1b3725cd57a9732e254bccdf
```

## Authority and complete accepted chain

The Human reviewed and accepts the independent ChatGPT PASS: Critical, High and Blocking Medium findings NONE; blocking findings 0; closeout readiness READY. The exact Human request is materialized in W04_C08_HUMAN_ACCEPTANCE.md, raw SHA-256 `5f6d43d65cfb6024460f4a1283311c5416c31cc821b7b868441cb6ba07c29e1a` / 17020 bytes. CLOSEOUT-V1 is `bd1b9fb49b274f115ff9aba1db3f73f94ddcf3f4cf23cd3eb63cabe9f6ca593e` / 15643 bytes. These supplied decisions authorize the exact two-phase execution, not a new Codex acceptance decision.

| Anchor | SHA | Native proof |
|---|---|---|
| Entry | `9afc4bd047bd4e52dfc4956f16e6420b3762301f` | #126 / 38114263650 / SUCCESS |
| Stage A | `b9f6f65e4a4f251d09e3303727ac24ae006edefe` | #127 / 38120061431 / FAILURE; legacy manifest immutability assertion |
| Stage-A Repair-01 | `a58a2a1a46bca7da1bf5056bff196ef7417e3b6c` | #128 / 38145924993 / SUCCESS |
| Stage B / accepted source freeze | `1fa7b505980c1efc1b3725cd57a9732e254bccdf` | #129 / 38153792599 / SUCCESS / I / FULL_EXACT_SHA |
| Stage C original | `9c3276dd301357fb7e351ef38a3e95b14a9be254` | #130 / 38158707170 / FAILURE; report EOF whitespace only |
| Stage-C Repair-01 / REVIEW_READY | `72de21ffc38629c94af19f73a72791cec6eebc24` | #131 / 38190417996 / SUCCESS / P / PUBLICATION_EXACT_SHA |
| Closeout-Prep-01 | `0047bb942e8e4227af8d6fb5c9a4763688a22aab` | #132 / 38200544252 / SUCCESS / I / FULL_EXACT_SHA |


The Stage-C original failure was one extra LF at EOF. Its single bounded repair removed only that byte. The development-round report remains immutable at blob `263d9ff634afc97cb695c31b4e7a00204895f4cf`.

## Prep-01 measured proof

Exactly one file changed: `tests/test_investigation_replay.py`; final Prep test blob `f3716aaa46f39c3aaf858b24bc0b1833fb0b28ba`. R43 keeps its original selector/signature/decorators and all upstream/protected assertions, admits only exact AUTHORIZED or exact CLOSED lifecycle states, and binds HEAD plus accepted Stage-B source identity. Node delta: 0 added / 0 removed / 0 renamed. All other test function bodies, manifest/runtime/planner/weights/workflow/timeouts/dependencies/schema/migrations remain unchanged.

Local focused R43/source-evolution: 128 PASS / 220.54s. Completed full replay proof: 167 PASS / pytest wall 1347.78s / exit 0, with no failures/errors/skips; durable JUnit SHA-256 `2260c460e061674be6e3c1ed5310e32fef4240e61286395d89876b2110a29994`. An earlier full invocation was interrupted without a terminal result and is not counted as completed proof. Ruff whole repository and strict mypy (`mypy .`, 175 files) PASS.

Prep native #132: all 15 required full-route jobs SUCCESS; Publication SKIPPED under I / FULL_EXACT_SHA. Measured outcomes: 2997 selected / 2994 passed / exactly 3 accepted skipped / failed, error, xfail and xpass all 0. Exact union, exact once and entry no-loss PASS. Integration 70 PASS. W03 38 selectors / 85 cases PASS at exact Prep SHA.

Node digest remains `9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a`; all original 2807 #126 entry nodes retained, entry digest `4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d`. Selected files 63. Prep plan SHA-256 `99d5c25805edf5904acde6b4fda39f92883c9f4323990aa0547f675b4580ca43`, schema `w04-devctrl02-non-integration-plan-v2`.

Accepted skip set remains exactly `tests/test_investigation_human_store.py::test_j40_j45_windows_junction_surfaces_fail_closed` with `[case]`, `[locks]`, `[root]`; digest `1524192888846ac2a7b1908212650648a38816aa72d458add70868c24d08a767`. Integration digest remains `bdcb72ebf947f5599d9e6cecf9bc29e65e9cb063daa03a715b41f5399ecf581c`.

The three weight seals remain base `315675b184abd56422f469a44da5f840b40d82c3cfb272d46873afd7a8adacca`, bootstrap `36f1d85e34344afee1f7e76b066427e4f40314c68f1d564340d82cc4dd44becb`, effective `352e6e1060bc1c2d5ce9a36fcad6cb9941e373bfae3da4d8a326d26a0d1f01c6`; effective total 7733.243s. Seven file-atomic deterministic LPT shards, all current timeouts and the workflow DAG remain unchanged.

## Frozen product and protected boundaries

| Path | Accepted runtime blob |
|---|---|
| src/flowlens/investigation/c08_policy.py | `273d288cf4b0e55b646cd2e6751f0259e463a5ff` |
| src/flowlens/investigation/c08_replay.py | `4fa391cf751377305315b7de8303ce94e6eb6c6e` |

R01-R46 product proof is PRESERVED / PASS from accepted #129 and unchanged runtime. Its full direct selector map, identity/core/presentation proofs, stable public errors and honest limitations remain in W04_C08_R_DEVELOPMENT_ROUND_REPORT.md. Only R43 lifecycle admission was generalized under the separate Prep authorization.

Frozen-artifact replay only; no current evidence refresh; no DB/network/filesystem/environment/clock/random/journal/provider capability; no runtime HGT or evaluation truth; no operational mutation or action authority; no causal/model-accuracy claim; no re-running Human decisions. Human notes remain non-evidence. Deterministic authority is independent of optional LLM wording; all three valid presentation modes preserve the replay core/ID. Source/runtime semantics, C01-C07, W03, dependencies, migrations and schemas remain unchanged.

Fifteen C01-C07 source blobs and 21 protected Git objects match the frozen baseline. The exact object snapshots and unchanged five C08 control/evidence files are recorded in the closeout context lock. The historical Compose GitGuardian alert is independent of C08; no Compose/env/credential/history change was made.

## Intended exact governance close and remaining own-SHA gates

Only C08 changes AUTHORIZED -> CLOSED, with source_freeze_sha `1fa7b505980c1efc1b3725cd57a9732e254bccdf` and the two accepted blobs above. Do not use Stage-C/repair/Prep/candidate/final-closeout SHAs as the runtime freeze. Preserve every C01-C07 object, schema/policy/W03 baseline/source root/checkpoint order; C09 remains absent. Intended final manifest: C01-C08 CLOSED, AUTHORIZED none, C09 ABSENT.

Exact six-path scope:

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c08/W04_C08_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md
docs/w04/checkpoints/c08/W04_C08_HUMAN_ACCEPTANCE.md
docs/w04/checkpoints/c08/W04_C08_CLOSEOUT_AUTHORIZATION.md
docs/w04/checkpoints/c08/W04_C08_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/checkpoints/c08/W04_C08_FINAL_CLOSEOUT_REPORT.md
```

Before primary mutation, a disposable full-history committed candidate must pass R43 CLOSED, all source-evolution tests and the production verifier with all eight checkpoints CLOSED and no AUTHORIZED checkpoint. It must have exactly these six file changes and unchanged protected trees; it is never pushed and is deleted after proof. Candidate-generated values are not yet created at this report's authoring cutoff.

Apply byte-for-byte these same files to freshly synchronized clean Prep HEAD, create one normal final commit with subject `docs(w04-c08): close protected investigation replay`, rerun the same committed-head tests/verifier, then push once. Require the NEW closeout SHA's own full native SUCCESS: Classify, Static/Plan, Integration/Data, shards 0-6, Aggregate, Quality, Compose, W03 and Verification; Publication follows full-route policy. Require the same 2997/2994/3 zero-failure envelope, integration 70, W03 38/85, R43 CLOSED and source evolution C01-C08 CLOSED / AUTHORIZED none. No retry/rerun/repair/re-weight/timeout change is authorized on failure.

Only after that gate and final local/tracking/direct-origin/PR HEAD equality, 0/0 and clean tree/index may W04_C08_CLOSEOUT_COMPLETE become effective. Main/base must remain `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`; PR #7 remains OPEN / DRAFT / UNMERGED.

## Accepted deferred item and terminal boundary

The Human accepts the #129 shard-1 job duration of 3176s against the unchanged 3300s timeout: 124s headroom, approximately 3.8%. The C08 JUnit duration sum is 3082.523s versus the sealed bootstrap scheduling weight of 1061.491s. This is NON-BLOCKING FOLLOW-UP engineering work, deferred to separate authorization. No re-weight, timeout, retry, shard topology or workflow change is authorized by this closeout.

C09, PR ready/merge, branch deletion and main write remain NOT AUTHORIZED. Stop after the final verified/synchronized C08 closeout handoff. No other checkpoint or CI engineering work begins under this authorization.
