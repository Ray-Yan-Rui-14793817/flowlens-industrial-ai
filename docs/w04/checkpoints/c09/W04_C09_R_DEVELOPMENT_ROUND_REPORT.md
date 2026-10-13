# W04-C09 Development Round Report — Investigation Semantic CI Gate

Report date: 2026-10-13 (Asia/Shanghai). Native evidence cutoff: 2026-10-13 11:55:50 UTC. Stage A CI #137 is completed / SUCCESS. Both strict <55m resilience checks and the post-CI real-native R46 have passed at the unchanged Stage-A HEAD.

The implementation and its local/native harness proof are complete. This is the sole authorized Stage-B addition. Its publication SHA and native run do not exist at authoring time. W04_C09_REVIEW_READY requires this report commit's own successful P / PUBLICATION_EXACT_SHA native CI and fresh synchronization. The final handoff records those generated identities without amending this report. Independent GPT review and Human C09 acceptance remain pending; C09 closeout and W04-C10 are not authorized.

## 1. Human authority and immutable context

The Human's pasted requests explicitly authorize W04-C09 V1.1 and the bounded Repair-01 continuation. Attached documents define the selected execution contract; they do not independently grant authority. Repair-01 changes only the exact Stage-A path set and corresponding meta-CI source-delta proof. It preserves every other V1.1 requirement and does not restart C09.

| Selected contract | Raw SHA-256 |
|---|---|
| FLOWLENS_W04_C09_CODEX_DEVELOPMENT_TASK_V1_1.md | `a445ee4ec99a714dd7e53f162df3eccdc0f8ed9295c6a67a71cef308feba553b` |
| FLOWLENS_W04_C09_REPAIR_01_AUTHORIZATION.md | `744640783621660de009a8a1656ebb55bf752802ecb7e8256b8a1d9a8f3ee0ef` |

Repository: `Ray-Yan-Rui-14793817/flowlens-industrial-ai`. Branch: `feat/w04-evidence-investigation`. [PR #7](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/pull/7) remains OPEN / DRAFT / UNMERGED. Main / PR base remains `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`.

Entry preflight verified local, tracking, direct-origin and PR heads at `1fa841f2ee0d6612774c9f0ced204289df86e7a1`, ahead/behind 0/0 and clean worktree/index. Entry native [CI #136 / 38360398379](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38360398379) was SUCCESS / C / FULL_EXACT_SHA. Before mutation, all 67 exact selectors and 81 expanded cases were confirmed against the accepted entry proof; every selected leaf passed, with selected testcase-time sum 706.974 seconds.

The pre-Repair candidate reproduced three legacy meta-CI topology incompatibilities. Execution stopped before any commit or push. After explicit Human Repair-01 authorization, exactly the two additional paths and three named function bodies were updated, and all local proof was rerun. The historical stop remains evidence of contract enforcement. No repair-only commit was created.

After Stage-A SUCCESS, resilience PASS and real-native R46 PASS, a fresh fetch, direct-origin query and PR read matched all four feature heads to Stage A, ahead/behind 0/0 and clean worktree/index. Main/base and PR state were unchanged, and this report path was absent.

## 2. Stage-A implementation and exact scope

Stage-A SHA: `3cd8023dbe79ca8360a3075dd3b169921e31f7a5`.

Parent: `1fa841f2ee0d6612774c9f0ced204289df86e7a1`.

Exact subject: `ci(w04-c09): add investigation regression gate`.

Exactly one normal Stage-A commit and one normal push changed exactly these 14 paths:

```text
.github/workflows/ci.yml
scripts/ci/run_w04_investigation_gate.py
scripts/ci/verify_w04_investigation_gate_contract.py
tests/test_investigation_replay.py
docs/w04/checkpoints/c09/W04_C09_AUTHORIZATION_CONTRACT.md
docs/w04/checkpoints/c09/W04_C09_HUMAN_AUTHORIZATION.md
docs/w04/checkpoints/c09/W04_C09_CONTEXT_LOCK.md
docs/w04/checkpoints/c09/W04_C09_CI_REGRESSION_CONTRACT.md
docs/w04/checkpoints/c09/W04_C09_HARNESS_SPEC.md
docs/w04/checkpoints/c09/W04_C09_GPT_REVIEW_CHECKLIST.md
docs/w04/checkpoints/c09/specs/c09_gate_manifest.json
docs/w04/checkpoints/c09/specs/authorized_paths.json
tests/test_ci_change_classifier.py
tests/test_c09_ci_gate.py
```

All 14 committed Git blobs matched the validated candidate blobs. No 15th Stage-A path changed. Stage B authorizes only this report, with exact subject `docs(w04-c09): publish regression-hardening proof` and one normal commit/push.

The new `w04-investigation-gate` job inherits the accepted W03 setup pattern, pinned actions/runtime and isolated PostgreSQL test service. It runs the independent C09 contract verifier, then nine fresh semantic-family subprocesses, then uploads the single sealed summary on success. Its timeout is 30 minutes. Existing full jobs and workflow triggers remain source-identical apart from the authorized Verification dependency/result conjunction. The native classifier, publication verifier, W03 runner and DEVCTRL planner were not changed.

The runner enforces exact manifest bytes/content, exact implementation HEAD, strict JSON structure and frozen selector/case counts. It neutralizes pytest addopts and plugin autoload, validates each family's exact collection before execution, and accepts only successful setup/call/teardown leaves with exit zero. Deselection, skip, xfail, xpass, failure and error cannot produce a semantic PASS. Each family gets a fresh process in manifest order. Prior PASS output is invalidated before validation. Summary output is canonical, has a content self-seal, and contains the required deterministic fields without timings, node lists or mutable diagnostics.

Repair-01 changes only:

| Existing function | Exact bounded update |
|---|---|
| `test_workflow_routes_all_classes_to_a_stable_fail_closed_gate` | Add W04 to the exact Verification needs expectation; preserve all existing classifier/path/publication checks. |
| `test_workflow_one_job_exact_schedule_source_manifest_and_environment` | Add W04 to the exact job set; preserve the complete W03 job proof. |
| `test_verification_runs_actual_shell_truth_table` | Add exact W04 dependency/result binding, P=skipped, full=success, and W04 adversarial wrong-status cases; preserve every prior result check. |

Both meta-CI files are guarded against exact entry AST identities and complete top-level source spans. Imports, docstrings, assignments, helpers, fixtures, all other tests, function names, decorators, signatures and parameterization remain entry-identical. Each file has negative controls for unrelated test-body mutation, new test, rename, import, decorator and parameter-list mutation. C09_META_CI_DELTA_GUARD = PASS. The C08 replay guard likewise restricts changes to the V1.1 named top-level units and preserves every other entry source span. C08_REPLAY_HARNESS_DELTA_GUARD = PASS.

## 3. Local proof after Repair-01

Local environment: Windows, Python 3.12.14, pytest 9.1.1 and uv 0.12.5. Database-dependent tests used a dedicated test-only PostgreSQL container. No production database or operational truth was accessed for mutation.

| Required local proof | Result |
|---|---|
| Three authorized repair selectors | 3 PASS, 13.04s |
| Complete classifier and legacy W03 CI meta files | 170 PASS, 59.49s, in the LF validation mirror |
| Independent C09 verifier | PASS: 150 adversarial controls and 223 actual Bash truth-table cases |
| C08 replay and C09 meta-CI source-delta guards | PASS in primary checkout and LF mirror |
| Nine independent family subprocesses | 9/9 PASS; 67 selectors / 81 cases |
| R43 and both R46 fixture/control selectors | PASS in the required focused/full suites |
| Complete `tests/test_investigation_replay.py` | 167 PASS, 1337.72s |
| Focused R43/R46, source-evolution and CI-sharding regression group | 243 PASS, 346.47s |
| Ruff | PASS |
| Strict mypy | PASS, 177 source files |
| Dependency lock | PASS, 43 packages, no lock/dependency changes |
| Active planner and node/parameter identity | PASS: 2997 nodes / 63 files / exact unchanged digests / 7 shards |
| Candidate and commit Git blob equality | 14/14 MATCH |
| Exact path guard and `git diff --check` | PASS |

The primary Windows checkout's complete meta-file run was 169 PASS with one pre-existing raw-byte CRLF difference for the frozen W03 manifest. That historical manifest was not modified and its raw-byte assertion was not weakened. The complete proof was rerun in a disposable full-history LF clone at the entry HEAD with all 14 candidate Git blobs identical to the primary candidate. The clone received no commits or pushes. All 170 meta cases passed there; native Linux Stage-A proof subsequently passed the same complete files. LF candidate source, committed Git source and native CI are consistent.

The uncommitted local candidate gate summary identifies the entry HEAD as required by its local execution. Its self-seal is `6aeb3e8e4c4ee0b01b35150f0993addeb332415d8210ba53e5216c8280c1fe2e`; its raw-file SHA-256 is `aea5718a2d1afcf229fca79968a1ae32c9fda24799a0df5e4f45f9c7b94cc117`. Native Stage-A summary identities below provide the committed implementation proof.

No pytest nodes were added, removed or renamed, and no parameter expansion changed. The replay, classifier and legacy W03 meta files retain 167, 91 and 79 cases respectively.

## 4. Stage-A exact-SHA native CI

Native [CI #137 / 38387680661](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38387680661), attempt 1, pull_request event, ran at exact Stage-A SHA `3cd8023dbe79ca8360a3075dd3b169921e31f7a5` and completed SUCCESS. The authoritative native classifier reported I / FULL_EXACT_SHA, entry base and exactly the 14 authorized changed paths.

All 16 required full-route jobs succeeded: Classify, Static and plan, Integration and data, seven Non-integration shards, Non-integration aggregate, Quality, Docker Compose smoke, W03 AI loop gate, W04 investigation gate and Verification. Publication proof was SKIPPED. No rerun or post-push repair was needed.

| Native proof | Exact outcome |
|---|---|
| Non-integration | 2997 selected / 2994 PASS / 3 accepted Linux SKIP / 0 failed, error, xfail, xpass |
| Entry no-loss / exact union / exact once | PASS |
| Integration | 70 selected / 70 PASS / no skip or adverse outcome |
| W03 semantic gate | 10 families / 38 selectors / 85 cases PASS |
| W04 semantic gate | 9 families / 67 selectors / 81 cases PASS |
| Native independent C09 verifier | PASS: 150 adversarial controls / 223 actual Bash truth cases |
| Native C08 replay / C09 meta-CI guards | PASS / PASS |

The original aggregate JUnit SHA-256 is `7cc8c2b7908288f4e3ad425976336ab39ee4481c6b97878b99f70856f0483dbf`; aggregate receipt self-seal is `91e6dbc12365663b95027c8ad709c01ff62ee6cb491d57e024291d0e15eacbe0`. The original integration JUnit SHA-256 is `6f27ae7cd79c32c4ce5a60b0f4e760190937ddbd7d0c37175afcee4cd30dea92`; integration receipt self-seal is `80b6530ae8f0655173748791adb036f15dbc2a0ac466081b4043ce388904e914`. Both receipts bind the native plan seal `9da284a8208d20508eb5b7cf83d1f8ce16b9958d6fed6ccf1ed14e3a516993b6` and exact Stage-A HEAD.

## 5. W04 manifest, isolated families and sealed summary

Gate: `w04-c09-investigation-gate-v1`. Manifest schema: `w04-c09-regression-manifest-v1`.

Manifest raw-file SHA-256: `d7526f78b3301332983e626dd102f3f57f52f2926d3130741b6e8a447bf0bbd1`.

Manifest canonical-content SHA-256: `937179ae935b1361c5bfd5114825cc6fdd51a9aad5cfeffdc012bb3a4652e8ad`.

The committed manifest exactly matches V1.1 Appendix A, including UTF-8 / LF bytes, entry anchors, family order, selectors and expanded counts.

| Family | Selectors | Cases | Native result |
|---|---:|---:|---|
| F01 C01_CONTRACTS_IDENTITY | 6 | 6 | PASS |
| F02 C02_CASE_BINDING_TEMPORAL | 6 | 6 | PASS |
| F03 C03_PLANNING_DETERMINISM | 6 | 6 | PASS |
| F04 C04_AUTHORIZED_NAVIGATION_READ_ONLY | 9 | 14 | PASS |
| F05 C05_FINDINGS_CONFLICT_UNCERTAINTY | 7 | 7 | PASS |
| F06 C06_HUMAN_AUTHORITY_AUDIT | 10 | 10 | PASS |
| F07 C07_SUMMARY_GROUNDING | 10 | 10 | PASS |
| F08 C08_PROTECTED_REPLAY | 8 | 17 | PASS |
| F09 SOURCE_EVOLUTION_GOVERNANCE | 5 | 5 | PASS |
| Total | 67 | 81 | 9/9 PASS |

FAMILY_SUBPROCESS_ISOLATION = PASS in local and native independent proof.

Native artifact: `w04-c09-gate-3cd8023dbe79ca8360a3075dd3b169921e31f7a5`, ID `11808836203`.

Exact ZIP contents: one file, `w04-c09-gate-summary.json`. Original ZIP SHA-256: `17d5938643a1091b3dd94cffe1451fced3151f3012469d65606e2f9bcb245b52`.

Summary canonical self-seal: `36cb9b6f380f419c01540d7a122fc8a124a88a93697435a3d7ecb33387c9a660`.

Summary raw-file SHA-256: `790de629efc2dd5e3b0500b0fcbd4c99466c8add4b0a9dfcbd40a41658f6b395`.

The original downloaded summary bytes validate against the exact manifest and Stage-A HEAD, match the summary emitted in the native job log, and satisfy canonical-byte and self-seal checks.

## 6. DEVCTRL-03 resilience and immutable planner contract

Active plan schema remains `w04-devctrl03-non-integration-plan-v1`: 2997 nodes, 63 files, 7 shards, max-parallel 7, fail-fast false and unchanged 65-minute shard timeout ceiling.

Node digest: `9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a`.

File digest: `890fdd5c30c7e2a1e90da8cb8b7123937d3356f1d519f82dff4a941f13659fd7`.

Measured weights self-seal: `a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851`. Planner source, measured weights, assignment method and all DEVCTRL-03 evidence remain entry-identical. Repair-01 admitted zero new nodes and zero parameter changes.

Every job duration below comes from its own GitHub native started_at/completed_at timestamps. Every pytest duration comes from the original suite time in that shard's downloaded JUnit ZIP; each ZIP digest and receipt/JUnit binding was verified first.

| Shard | Native job ID | Job seconds | Pytest suite seconds |
|---:|---:|---:|---:|
| 0 | 115263719069 | 3002 | 2967.373 |
| 1 | 115263718959 | 1837 | 1806.656 |
| 2 | 115263719014 | 1079 | 1040.479 |
| 3 | 115263719163 | 1077 | 1041.055 |
| 4 | 115263718934 | 1097 | 1059.878 |
| 5 | 115263718948 | 1684 | 1639.077 |
| 6 | 115263719105 | 1183 | 1130.858 |

Longest job: shard 0, 3002 seconds (50m 02s). Longest pytest: shard 0, 2967.373 seconds (49m 27.373s).

| Threshold | Job headroom (seconds) | Pytest headroom (seconds) |
|---|---:|---:|
| 55m resilience threshold (3300s) | 298 | 332.627 |
| 65m timeout ceiling (3900s) | 898 | 932.627 |

DEVCTRL03_RESILIENCE_LT_55M = PASS: both maxima are strictly below 3300 seconds. No reweighting, timeout increase, shard topology change, test-file split or node-level sharding was performed.

## 7. Eleven original artifacts and post-CI real-native R46

Exactly 11 native artifacts were downloaded from #137, attempt 1, and each original ZIP's SHA-256 matched GitHub's digest. All artifact metadata binds the same run ID and exact Stage-A HEAD. The roles below expand to `w04-devctrl02-<role>-3cd8023dbe79ca8360a3075dd3b169921e31f7a5`, except W04 gate, whose exact name is recorded above.

| Role | Artifact ID | Original ZIP SHA-256 |
|---|---:|---|
| plan | 11807137395 | `316649d3cca6eee2141747c7faa0f67f612ebd189fe8fb5a1377dda362eadddd` |
| integration-data | 11807123944 | `0ca7cfd61b12dc70b779e1162dfd40c5aaac43c874a701f10e812144206bdb86` |
| nonint-aggregate | 11810642322 | `967c514be34df37c80cd207644bb69727a585b166aa430f955a52b47048ecd8a` |
| shard-0 | 11810437370 | `1f891d6bbab9694d3f00284c8e11978011c69d4daf4639f2f8556b7eb7fb35fa` |
| shard-1 | 11808723048 | `cd8573e698fcc15b42dff09b27131deb3e5730ea098b634e919d8ebabcf392d6` |
| shard-2 | 11808715822 | `45e224572e30a0fa96fcaf051b6801916f1584acd573654d7a7af9656dec61e9` |
| shard-3 | 11808321408 | `006fbc4cb7b794dfb12882ec94cc29a075582fa613c5ed52afc7c78248325745` |
| shard-4 | 11808571306 | `24f60ff20a4e48ffbc79ff226dacf76e8ba8d91b117e2a789f4e1e69b9a51537` |
| shard-5 | 11808717610 | `f87d38346f2929777f594573bec2fdd3dbef673377d6909b0827789dcbf9562d` |
| shard-6 | 11808456660 | `4a534fbcc295fbe33f11c0e3330acbf3233f9037d2f5bc60157226e6f92ff4aa` |
| w04-gate | 11808836203 | `17d5938643a1091b3dd94cffe1451fced3151f3012469d65606e2f9bcb245b52` |

Only after native SUCCESS and both resilience checks passed, `test_r46_stage_b_exact_sha_full_native_ci` was rerun at Stage-A HEAD with `FLOWLENS_C08_NATIVE_PROOF` set to actual GitHub-native evidence. It passed: 1 case / 14.99s. REAL_NATIVE_R46 = PASS.

The proof validates run/attempt/event/head/job results, exact 11-artifact names and original ZIP digests, W03 38/85, exact W04 summary bytes/self-seal/raw SHA, native plan/weights and current collection. It reaggregates all seven native shard receipts/JUnit files, proves entry no-loss, exact union, exact once and the full outcome envelope, compares rebuilt outcomes with the native aggregate, and verifies integration 70 with no skip. Original downloaded bytes remain unchanged. Historical R46 selector naming is preserved; its current real-evidence HEAD is the C09 Stage-A SHA.

Post-R46 C08 replay, C09 meta-CI and workflow source guards were independently rerun and remained PASS. R43's frozen upstream checks passed locally and in the native semantic/full suites.

Local retained proof directory: `C:\Users\C\AppData\Local\Temp\flowlens-w04-c09-v11-1fa841f2`. It contains entry/local proof, candidate/commit blob records, native run/jobs/artifact metadata, all 11 original ZIPs and their extracted original files, exact resilience calculations, real-native R46 JUnit and post-native source guards. This local path is supplementary review evidence; Git commit identities and the native run/artifact identities above are the repository proof anchors. Temporary signed transfer URLs are transport metadata, not repository evidence.

## 8. Frozen product and checkpoint boundaries

C01-C08 remain CLOSED / unchanged. Their frozen source Git blobs and all protected checkpoint documents are identical to entry. Source-evolution manifest raw SHA-256 remains `d22a12306f8fe98952b9e35a5f166f29fee968c9aedcff27511da59889c20c2d`, byte-identical to entry. C09's source-evolution entry is ABSENT BY DESIGN because this checkpoint adds a CI proof plane without runtime source evolution.

There is no product/runtime source, app, dependency, lock, schema, migration, provider/model, HGT or operational mutation change. `src/**`, `apps/**`, `migrations/**`, `pyproject.toml`, `uv.lock`, `docker-compose.yml`, the classifier, publication verifier, W03 runner and accepted W03/DEVCTRL/C01-C08 evidence are unchanged. Development test-database setup does not write operational truth. No main write, merge, PR-ready transition, auto-merge, branch deletion, force push, amend, rebase, reset or history rewrite occurred.

## 9. Known limitations and independent reviewer questions

The critical semantic pack intentionally selects a subset of the full suite. C09 duplicates selected accepted tests as an explicit semantic proof; it admits no new pytest nodes. GitHub artifact retention is bounded; the W04 summary upload uses 14-day retention. GitHub-hosted runner timing variance remains, and the <55m rule protects the accepted resilience class without providing a deterministic performance guarantee. C09 does not prove production UI/usability or business acceptance. C10 remains a separate, unauthorized checkpoint.

Independent GPT review should assess:

1. Whether the exact manifest, fresh-family execution and collection/leaf outcome controls prevent partial, stale or falsely passing semantic summaries.
2. Whether the new workflow job and fail-closed Verification truth table preserve every full/publication boundary and accepted W03 proof.
3. Whether the C08 replay and Repair-01 meta-CI AST/source-span guards admit only the explicitly authorized existing function changes, including negative controls and zero node/parameter delta.
4. Whether the eleven original artifact bindings, reaggregation, summary seals and recorded native timings prove the exact Stage-A implementation and both resilience thresholds.
5. Whether the exact path set, frozen source/blob identities and report-only Stage B preserve C01-C08, DEVCTRL-03, product/runtime isolation and all Human authority boundaries.

## 10. Publication requirement and terminal boundary

Stage B must be exactly this file, one normal commit/push, subject `docs(w04-c09): publish regression-hardening proof`. Its own native classifier is authoritative and must report P / PUBLICATION_EXACT_SHA. Classify, Publication and Verification must succeed; all heavy/full jobs, including W03 and W04 gates, must be SKIPPED. That native run and final four-head synchronization are pending at this report's immutable authoring point and are recorded in the final handoff after completion.

After those final proofs, the implementation-round status is at most W04_C09_REVIEW_READY: implementation COMPLETE, harness PASS, exact-SHA native CI PASS, real-native R46 PASS, both source-delta guards PASS and DEVCTRL-03 resilience PASS. GPT independent review and Human C09 acceptance remain PENDING. C09 CLOSEOUT = NOT AUTHORIZED. W04-C10 = NOT AUTHORIZED. PR #7 remains OPEN / DRAFT / UNMERGED. PR merge, branch deletion and main write remain NOT AUTHORIZED.
