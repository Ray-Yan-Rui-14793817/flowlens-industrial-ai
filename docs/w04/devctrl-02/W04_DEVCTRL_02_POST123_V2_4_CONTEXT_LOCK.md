# W04-DEVCTRL-02 POST123 V2.4 Context Lock

Locked on 2026-10-09 before implementation. Fresh remote fetch, direct-origin refs, GitHub API/native terminal logs, complete current contract/control reads and clean local Git inspection independently established every activation fact.

## Activation

```text
REPOSITORY: Ray-Yan-Rui-14793817/flowlens-industrial-ai
VISIBILITY: PUBLIC
BRANCH: feat/w04-evidence-investigation
LOCAL / TRACKING / DIRECT ORIGIN FEATURE / PR #7 HEAD:
76a5f207a343c673382490bba0c489cb8b667af6
REPAIR-01 PARENT:
9d5b6e3baea1a860446b70d9b254cc3dc41815a4
PR #7: OPEN / DRAFT / UNMERGED
MAIN / TRACKING MAIN / DIRECT ORIGIN MAIN / PR BASE:
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
WORKTREE / INDEX: CLEAN
C01-C07: CLOSED
C08: ABSENT / NOT AUTHORIZED
TASK VERSION: V2.4 / EXPLICITLY HUMAN APPROVED
TASK RAW SHA-256:
ea7ea2cc8a92e421ca4101104885e5d4442a42ef7d7269ecca56db8bd7d8d2df
```

| Native baseline | Source SHA | Terminal conclusion |
|---|---|---|
| #120 / 37800395278 | f50d6c6f8eeacd9df3320dc4a8c6269aa6caa3a5 | SUCCESS |
| #121 / 37882221740 | 4a5ab37251c1fecff4291ae6198e03c847cf8735 | SUCCESS |
| #122 / 37889883403 | 9d5b6e3baea1a860446b70d9b254cc3dc41815a4 | FAILURE |
| #123 / 37909569704 | 76a5f207a343c673382490bba0c489cb8b667af6 | COMPLETED / CANCELLED |

#123 native Legacy Quality job 113751237843 succeeded: integration 70 passed (335.45s); complete non-integration 2804 passed / 3 accepted skipped (8371.29s), zero failed/error/xfail/xpass. Both Repair-01 assertions passed in the complete legacy run. Ruff, strict mypy (172 source files), lock (43 packages) and W03 (job 113801318753) succeeded. Shard 2 hit its 60-minute job timeout; missing shard evidence caused downstream aggregate/equivalence/Verification failure. This is not a new deterministic test regression.

## Exact coverage

Fresh independent local collect-only retained:

| Marker | Count | Canonical sorted-node SHA-256 |
|---|---:|---|
| not integration | 2807 | 4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d |
| integration | 70 | bdcb72ebf947f5599d9e6cecf9bc29e65e9cb063daa03a715b41f5399ecf581c |

Selected non-integration files: exactly 62. Entry no-loss PASS: all 2726 frozen entry nodes, digest 0089b5889f7de2dbe637ddef3774966ae07f6cf6d6518f2648f20e47ccbaa4a7. Entry baseline raw bytes remain 535dd95d2af064402a5b4892a2aa3b690ee092e7148aea1c4299b00ca95af102.

Accepted Linux skip digest: 1524192888846ac2a7b1908212650648a38816aa72d458add70868c24d08a767 (the case/locks/root Windows junction checks). Native #123 passed-set digest: b8264ccb9cf6f71357aef371c6749211ecf5dc20acfc3019f0516657005154b0; non-integration six-outcome map digest f38fb0268e32b045113ef57684057ae102edb12e5e32de855c0e504d1418ff9b. Integration map digest 39c51cd99dd731256261b320d0c8b2ef1e05bc178eb339590afbf274d5492469.

## Frozen scheduling provenance and diagnosis

#122 and #123 used identical four file/node partitions. #122 pytest times were approximately 33m18s, 24m15s, 25m05s and 28m40s; #123 approximately 33m17s, 15m30s, >59m53s/cancelled and 28m14s. Shard-2 runner speed contamination reached roughly 2.48x. Progress-line timestamps can wrap and misattribute completion, so neither V1 progress timing nor anomalous #123 timing is authoritative.

Authoritative static timing source: complete #122 / 37889883403 / 9d5b6e3baea1a860446b70d9b254cc3dc41815a4 JUnit testcase time sums. The four downloaded artifacts were inspected in memory; their JUnit digests, canonical receipt seals, exact 2807-node union and all 62 normative file sums matched. Receipt SHA-256 below denotes the canonical receipt seal, not the raw pretty-printed JSON file hash.

| Shard | Artifact id | JUnit SHA-256 | Receipt seal SHA-256 | Nodes / pass / fail / skip |
|---:|---:|---|---|---|
| 0 | 11599246530 | 918de4087d4622c2cbfeed583776e1cbf4bbc3ab70578b8c4530fe08b87fe106 | 6cb9d27982bfd9478fd7918262b0a756c5bfa5601f5f3e024e66d234b20b018c | 1048 / 1048 / 0 / 0 |
| 1 | 11598633083 | 9608e3b41422757f4a5a905d77b4db0c02a385ed0bb1f3a700beacc3a9f49d82 | 6a8630750230b19462ad7d1891599225900f75b8e35ec159f2a0cd6f16eb7d3d | 946 / 945 / 1 / 0 |
| 2 | 11598796165 | c9f70254d377aaf5a5ce18a5e889677d490a29105c8fc58dae2259a4d6a4bf8a | 0655fc87660d9e762f5032504bcb3f61ddbb45d0cdfaa96481d74e1e4d82426d | 511 / 507 / 1 / 3 |
| 3 | 11598701090 | ec12a3579bfbf3b77ebf19e9af3fc08722d967775757ca42d46d6785403066b6 | 684d1e424e0fe39fb929eb3e0688a937c178f123ef9232e6b9e779467e60818c | 302 / 302 / 0 / 0 |

Total 6671.752s / 111.196m. #122's two historical governance failures do not invalidate complete timing evidence; zero errors/xfails/xpasses. Historical artifacts are static scheduling evidence only, never current runtime proof.

Seven is the minimum fixed file-atomic LPT topology robust under the observed 2.48x envelope: six predicts ~45.95m; seven ~43.87m. Eight provides no smaller lower bound because findings alone weighs 1061.491s. Expected seven nominal loads: 1061.491, 1014.403, 919.267, 919.131, 919.138, 919.131, 919.191 seconds.

During local plan validation, exact millisecond arithmetic exposed one inconsistency in §4.1: shards 3 and 5 tie at 919.131s, so the zero-time tests/test_c06_policy.py belongs to the lowest id, shard 3. Before committing, the Human explicitly approved this exact tie behavior and recording the example correction. Corrected file counts: 1,1,10,15,10,14,11. All other 61 file assignments, all weights, all nominal loads, node identities, scopes and gates remain unchanged.

## Protected current Git objects

| Path | Git object |
|---|---|
| src | 32856501648e4fea75489be8dd467553e9888fd1 |
| apps | 597399c7919982e9b2d54fc8b58fe6784cfe8585 |
| migrations | c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433 |
| docs/w03 | cb81e388c6c44a9900575ef2e72161dc0205be94 |
| pyproject.toml | 318bbc0a858f760e6c4d7a2d3fdbfcc111febb77 |
| uv.lock | 619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a |
| docker-compose.yml | 5a0b6e8486edc69f9f79c7e1345a842aa412983c |
| W04 source-evolution manifest | 3a173837de8ea3888de7f9a7de0fd4e34b7f0a5b |
| scripts/ci/classify_change.py | fd9e99c6b55b85f184198c51f0f97ba16323ce32 |
| scripts/ci/verify_publication.py | 8f97a117f936d9dce91957f7b44551acb5d5c2b6 |
| scripts/ci/run_w03_ai_loop_gate.py | c533928e584335437ae8a902fcab4faab64ae8ef |
| W03 C09 manifest | b2a03f3295c162a639eb99dbd87b4a636c3b1e85 |
| tests/test_investigation_evidence_queries.py | c1fd71becfbd1d772e5952cc92d2eabbf94d4530 |
| tests/test_investigation_summary.py | ea9bb7001540c024b75a2c27e606a263c69c7aea |

All 15 manifest-declared C01-C07 source blobs, all other runtime/source tests, historical Repair-01/Stage A governance, dependencies and HGT/data authority remain frozen. Only the two scopes below can change.

## Exact scopes and gates

R2:

```text
.github/workflows/ci.yml
docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json
docs/w04/devctrl-02/W04_DEVCTRL_02_POST123_V2_4_AUTHORIZATION.md
docs/w04/devctrl-02/W04_DEVCTRL_02_POST123_V2_4_CONTEXT_LOCK.md
scripts/ci/plan_non_integration_shards.py
scripts/ci/pytest_outcome_receipt.py
scripts/ci/run_non_integration_shard.py
scripts/ci/verify_non_integration_shards.py
tests/test_ci_test_sharding.py
tests/test_c09_ci_gate.py
tests/test_ci_change_classifier.py
```

R2 commit: ci(w04-devctrl-02): harden sharding against runner variance. Own terminal native full equivalence PASS and longest shadow shard <=45m are required before B2.

B2:

```text
.github/workflows/ci.yml
tests/test_ci_test_sharding.py
tests/test_c09_ci_gate.py
tests/test_ci_change_classifier.py
```

B2 commit: ci(w04-devctrl-02): cut over to seven-shard exact-SHA proof. Own terminal native PASS, proof <=60m hard / <=45m target / <=35m stretch, active required duration sum <=197m14s hard. Workflow created-to-Verification-complete and earliest required actual job start-to-Verification-complete are separate metrics; queue/start delay is reported separately.

```text
W04_DEVCTRL_02_POST123_V24_CONTEXT_CHANGED
W04_DEVCTRL_02_POST123_V24_SCOPE_VIOLATION
W04_DEVCTRL_02_POST123_V24_NODESET_DRIFT
W04_DEVCTRL_02_POST123_V24_WEIGHT_EVIDENCE_INVALID
W04_DEVCTRL_02_POST123_V24_R2_CI_FAILED
W04_DEVCTRL_02_POST123_V24_TARGET_NOT_MET
W04_DEVCTRL_02_POST123_V24_B2_CI_FAILED
W04_DEVCTRL_02_POST123_V24_PERFORMANCE_HARD_FAIL
W04_DEVCTRL_02_POST123_V24_REQUIRES_GPT_CLARIFICATION
```

Public CI remains contents: read, exact HEAD, immutable action pins, same-run exact-name artifacts, no secrets or operational authority. No new dependency, node change, file splitting, fallback weight, retry/rerun, continue-on-error or cancel-in-progress. No B3, Stage C, C08, closeout, DEVCTRL-03, merge, branch deletion, main write or history rewrite. Maximum status REVIEW_READY_POST123_V24; GPT review/Human acceptance pending.

