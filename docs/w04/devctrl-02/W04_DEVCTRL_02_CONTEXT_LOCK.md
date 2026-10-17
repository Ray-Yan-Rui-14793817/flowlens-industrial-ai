# W04-DEVCTRL-02 V2.1 Context Lock

Locked on 2026-10-09 (Asia/Shanghai) before CI implementation. Current Human execution approval and the exact V2.1 task outrank historical phase snapshots without weakening any frozen invariant. The full task was read before repository writes.

## Verified read-only activation

- Local HEAD, tracking feature HEAD and refreshed PR #7 head: f50d6c6f8eeacd9df3320dc4a8c6269aa6caa3a5.
- Branch: feat/w04-evidence-investigation.
- Entry index/worktree: CLEAN; git status --short empty.
- Refreshed PR #7: OPEN / DRAFT / UNMERGED.
- Main / PR base / merge base: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509.
- C07 closeout native CI: #120 / 37800395278 / completed SUCCESS.
- Actual classifier: C / FULL_EXACT_SHA, verified source-head delta.
- Classify, Quality, Compose, W03 and Verification: SUCCESS; Publication: SKIPPED.
- Native #120 non-integration: 2723 passed / 3 skipped / 70 deselected; 4054.76s.
- Native #120 integration: 70 passed / 2726 deselected; 192.78s.
- Native #120 Ruff PASS; strict mypy PASS / 167 files; lock PASS / 43 packages.
- Native #120 W03 F01-F10 PASS / 38 selectors / 85 cases; exact closeout implementation_sha.
- Source-evolution manifest: C01-C07 CLOSED; C07 source freeze c86f7af2370f315b8b7310008521f08ceade6d97; C08 absent.
- All manifest-declared C01-C07 source blob identities independently match entry HEAD.

Entry log:

```text
f50d6c6 docs(w04-c07): close grounded investigation summary
30f0ca9 docs(w04-c07): publish investigation summary proof
c86f7af feat(w04-c07): render grounded investigation summaries
a44e06b docs(w04-c07): authorize grounded investigation summary
e372b0d docs(v1): refresh product-centered README
```

## Entry non-integration baseline

Exact live entry collection: marker "not integration", pytest 9.1.1, 2726 nodes in 61 files. Two fresh Python processes collected identical sorted exact node lists before the baseline was written.

- Node-list SHA-256: 0089b5889f7de2dbe637ddef3774966ae07f6cf6d6518f2648f20e47ccbaa4a7.
- Selected-file-list SHA-256: f252f29b1999267ef1d2f3117f45579c094da3b9001cf34c1e07b524a418480e.
- Canonical digest input: UTF-8 JSON, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False; no trailing newline in digest input.
- Entry baseline file: W04_DEVCTRL_02_ENTRY_TEST_BASELINE.json.
- Accepted migration baseline identity in JSON: #118 / 37773147744. Entry closeout CI is independently bound above to #120.
- Local collection uses the existing locked Python 3.12 environment without cache writes or test execution. Pytest matches the accepted native runs; Python patch versions can differ within 3.12.
- Lifecycle: entry node set SUBSET OF current at every B1/B2/B3 full route. Pre-entry node deletion or rename is forbidden.
- Current minus entry may only add authorized DEVCTRL-02 controls/harness nodes in tests/test_ci_test_sharding.py, tests/test_c09_ci_gate.py, tests/test_ci_change_classifier.py and, at B3, tests/test_ci_publication_gate.py.
- This migration guard is mandatory through B3; it is not a permanent restriction on later separately authorized C08+ evolution.

## Accepted #118 performance and scheduling baseline

#118 / 37773147744 / c86f7af2370f315b8b7310008521f08ceade6d97 / SUCCESS. Workflow/proof approximately 2h31m17s; active required job-duration sum approximately 151m43s; Quality approximately 145m22s. Non-integration 2723 passed / 3 skipped / 70 deselected, authoritative pytest runtime 8308.68s. Integration 70 passed, 345.02s. W03 38/85, Ruff, strict mypy 167 files, lock 43 packages, Compose and Verification PASS.

Correct V2.1 derivation: each displayed pytest file progress timestamp completes THAT file. First weight is first completion minus the non-integration step start; every following weight is current completion minus previous completion. Exact #118 step start: 2026-10-08T12:00:51.4824948Z. Reconstructed all 61 observable file weights from the original native Quality log. Their scheduling sum is 8310.1685965s; pytest's 8308.68s remains authoritative suite runtime. Correct deterministic four-way LPT schedules approximately 2077.55s per shard (34.63m). These are scheduling weights, not observed new-job runtime or an SLO claim. Stage B1 will freeze the weights in its only allowed JSON. #120 timing is secondary runner-speed context only.

## Frozen Git object identities

SHA-256 values use committed Git bytes, avoiding CRLF checkout ambiguity. Directory entries below are Git tree identities; their SHA-256 is the Git tree listing returned by git show, not a recursive file-content digest.

| Path | Git object | Committed-byte SHA-256 |
|---|---|---|
| .github/workflows/ci.yml | 14c826b122b7103953e8b4539981004241205ba4 | b85a29c06a0028559bbc594b39d45feeb322d05b80761f05dc721792280a17e1 |
| scripts/ci/classify_change.py | fd9e99c6b55b85f184198c51f0f97ba16323ce32 | b8bced1cd32690495620c19fe3c47086ab2ba05959ba9e3cf11053fdb9fc9f6a |
| scripts/ci/verify_publication.py | 8f97a117f936d9dce91957f7b44551acb5d5c2b6 | be0e9fae4eb64745f0e7ac70abb8b6247bbc0c377e93ea35f628b85623dfe20a |
| scripts/ci/run_w03_ai_loop_gate.py | c533928e584335437ae8a902fcab4faab64ae8ef | ee420e8be33f63e2882ebbee3a441b82fe3b933bc8973a48c0ac610e922314a7 |
| docs/w03/checkpoints/c09/specs/c09_gate_manifest.json | b2a03f3295c162a639eb99dbd87b4a636c3b1e85 | bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990 |
| tests/test_c09_ci_gate.py | 543a3f67a0bba867c4b092b0d64fb415b61e1400 | bf1f80f8f9143b3ea1371001d3c26dfabc8dfd625e789602e548c2eea9d8dfa7 |
| tests/test_ci_change_classifier.py | 4c023bb7a2e066466810cc2b95be18b3db837fe2 | 740ae69dabff6d26f27a3562cb35fd887629c844324f9667f5b203295e44a5b1 |
| tests/test_ci_publication_gate.py | ea7f8fb5c99b8bf52598b5d1db240aa650595600 | a1b3796739a05ea643fd84c62e4ab4965dac44ecabb44658c014efa8a43fc956 |
| docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json | 3a173837de8ea3888de7f9a7de0fd4e34b7f0a5b | 5cff9d7e6d4b77bf4e274253d30ba34dc2688ea98832e0ce93c6b8a62b0e3b73 |
| pyproject.toml | 318bbc0a858f760e6c4d7a2d3fdbfcc111febb77 | 51484d6fe8e5f42658c09dda3bd3654954bbfe77fc8bed8fdb67ca74bbbda746 |
| uv.lock | 619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a | 887747a11dd1f3e27692586636b9061b5993dbc2969d80da7cbdcbe045ac80b0 |
| docker-compose.yml | 5a0b6e8486edc69f9f79c7e1345a842aa412983c | 827802a6a94162d61f5469f56d7e50d393d7338ed0806c2f01c6816f4a4596e7 |
| migrations | c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433 | 4849f31bdea2095abc03b6d7316b1387a9d384ee306c3cd0ea3843d8aab6c96d |
| apps | 597399c7919982e9b2d54fc8b58fe6784cfe8585 | 3d7c1905261a51745e2e11360646dd770d4838e8a947dab961628738f4125a41 |
| src | 32856501648e4fea75489be8dd467553e9888fd1 | 6fc574261a79c16619508811f318356fb7f44c273dfb85a31474ce462052c96e |
| docs/w03 | cb81e388c6c44a9900575ef2e72161dc0205be94 | 83aec6565172563cf44c689ec605542635f20ae10f73cae7e226caf0b507356b |
| src/flowlens/investigation/__init__.py | c23929f85dccd78bc72ef3b2b1415c6e8eaf0452 | 4339c0bdc33b013843e5cc20c079894db5830f4c55762d09bef2fedd4b4e0707 |
| src/flowlens/investigation/contracts.py | 0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e | 3f038f2727653fdee10e2f82fd1788de1d7267cce59d020aab046e0f690ae533 |
| src/flowlens/investigation/enums.py | 9c818780423f32f144b18666784ebc9ea3abdccc | b0d49a0f707304f8615f4366562e557f61a0abf1fa394dc464b380af3b40a25b |
| src/flowlens/investigation/c02_binding.py | 5f0af237ed465fa83e5a3b84954512b1f3125551 | e8c20196a034887af45af68f107fab24cf314dfeac67026aead65e5ed94037b8 |
| src/flowlens/investigation/c03_planning.py | 21d0055e12d86e6333a836d363d6e266cb0fcbd7 | f31c64c58ec05e9ea6358cfdf02552ca97ae5065ec8d093fdb8541ad380a7174 |
| src/flowlens/investigation/c04_navigation.py | 98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4 | f9517010c35da8b7e72a1d1c29a9dfadc225f3713cc64e3454d9087349241d9e |
| src/flowlens/investigation/c04_queries.py | dc22c7e532a4b62ccfffec2210bc2a6306d97234 | d3423110ca9b32369c7ad95f104d203937a531b1b25bf896bf885be5e22f80fe |
| src/flowlens/investigation/c04_registry.py | fbe6f0603d7b0634426ac0034033089eb55af4d7 | 0cff3b87ca3e2e8326ae0bdce0b5fb49a74fa35c8a2beb8e7a812d4124f9462f |
| src/flowlens/investigation/c05_findings.py | 31384426ba9c733bc5bdbf3b09a3d206c8182586 | c0d0ada8bc57dc7f42f095f2c99e9621802ba47bab73d84f9f46ab6c548803c4 |
| src/flowlens/investigation/c06_human.py | 021f5b72254c87c5b965500727a67001a47ef0bd | 4054b2c512220498c61dd5f717e2f10ddb19f1ef56142ef5ad52c13472fdce73 |
| src/flowlens/investigation/c06_policy.py | 8cfea031eaa764d871822c2e12de019ed3ebc3b9 | 29bfb74b0087fff271f1f4625b8b163f18c0351c420c172966aadfe8e4283e6a |
| src/flowlens/investigation/c06_store.py | e99d5d4c36db1dd3ed11c40ff9bbc5b01663ae9a | e34d25ef3ca5a113c299f7009df5d0b47c3b1b8244f604fa6897ac3de4c6aa55 |
| src/flowlens/investigation/c07_policy.py | c969c4bbf33910fab6ffb36c3bfe184fd42c74c9 | 5de7f6bae5e815886052a61ec9237e57543e984a3f7e548247e89cb14f10446d |
| src/flowlens/investigation/c07_provider.py | 56ecb9f3d7b5a1917a2354572e8c946f07eb759d | 07a68dcd434bef71b4c6b9cc908a9648278a1218537eaa2e3c970cf38a2c547f |
| src/flowlens/investigation/c07_summary.py | 3d561da7ab625421bbcf2dcb3785f8fae792cbff | c01b03f1a9822f0000b98475507bcc1b366fd0fa6eaebdd90b9f41608bb330e7 |

## Exact stage allowlists

### Stage A

```text
docs/w04/devctrl-02/W04_DEVCTRL_02_HUMAN_AUTHORIZATION.md
docs/w04/devctrl-02/W04_DEVCTRL_02_CONTEXT_LOCK.md
docs/w04/devctrl-02/W04_DEVCTRL_02_ENTRY_TEST_BASELINE.json
```

### Stage B1

```text
.github/workflows/ci.yml
scripts/ci/plan_non_integration_shards.py
scripts/ci/run_non_integration_shard.py
scripts/ci/verify_non_integration_shards.py
scripts/ci/pytest_outcome_receipt.py
tests/test_ci_test_sharding.py
tests/test_c09_ci_gate.py
tests/test_ci_change_classifier.py
docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json
```

### Stage B2

```text
.github/workflows/ci.yml
tests/test_c09_ci_gate.py
tests/test_ci_change_classifier.py
```

### Stage B3

```text
scripts/ci/classify_change.py
scripts/ci/verify_publication.py
tests/test_ci_change_classifier.py
tests/test_ci_publication_gate.py
```

### Stage C

```text
docs/w04/devctrl-02/W04_DEVCTRL_02_R_DEVELOPMENT_ROUND_REPORT.md
```

Stage A creates exactly three tracked paths. B1 retains the legacy authoritative proof and may only instrument its pytest executions for exact terminal outcomes. B1 classifier and publication behavior remain unchanged. B2 permits topology/harness changes only; a B1 helper defect requires separate repair authorization. B3 permits no workflow changes. Stage C creates only its development report after B3 native PASS.

## Forbidden mutation surface

All paths outside the active-stage allowlist are forbidden. In particular: src/**; migrations/**; apps/**; pyproject.toml; uv.lock; docker-compose.yml; .env.example; AGENTS.md; LOOP.md; docs/w03/**; docs/sprints/**; docs/context/**; docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json; C01-C07 contracts, runtime source, tests outside the exact control allowlists and historical reports; scripts/ci/run_w03_ai_loop_gate.py; scripts/ci/verify_w04_source_evolution.py; tests/fixtures/w03_ci_history.json. Classifier/publication behavior changes are authorized only at B3. No protected runtime/HGT material may enter public evidence.

## Proof and transport requirements

Exact source SHA in every proof runner. File-atomic scheduling, exactly four shards, fail-fast false and max-parallel 4. Current node union exact, pairwise intersections empty, each node exactly once. Legacy/shadow same-SHA integration and non-integration coverage AND passed/skipped/xfail/xpass/failed/error maps must be identical; successful migration has zero failures/errors. No new or disappeared accepted skip may pass silently.

Repository-owned receipts bind head, role, marker, shard, plan/weights/assigned/collected/JUnit/receipt digests and exact six terminal-outcome lists/counts. Setup/teardown failure is ERROR; call/assertion failure is FAILED. Transport names bind exact HEAD and role/shard; missing/duplicate/ambiguous evidence fails closed. Existing pinned actions remain authorized; only pinned upload-artifact/download-artifact are newly authorized.

B1 legacy Quality timeout semantics remain unchanged. Shadow timeouts: static 15m, integration 25m, shard 60m, aggregate 10m, equivalence 10m. B2: static 15m, integration 25m, shard 55m, aggregate 10m, Quality 5m, W03 15m, Verification 5m; Compose remains <=15m. W03 runner/manifest and Compose body are preserved.

## Performance metric definitions

- WORKFLOW_ELAPSED: workflow created/start context to Verification completion.
- PROOF_EXECUTION_ELAPSED: first required proof job actual start to Verification completion.
- ACTIVE_REQUIRED_JOB_DURATION_SUM: sum of actual durations of required executed proof jobs.
- Report observable queue/start delay separately.
- Proof execution <=60m HARD; <=45m TARGET; <=35m STRETCH.
- Required job-duration budget <=1.30 times #118, approximately 197m14s.
- Workflow >60m due demonstrable external queue while proof <=60m is external queue contamination, not an architecture hard failure.
- Proof >60m stops. Target miss <=60m may continue honestly to B3. No fifth shard.

## Hard stops and repository workflow

```text
W04_DEVCTRL_02_WAITING_FOR_C07_CLOSEOUT
W04_DEVCTRL_02_CONTEXT_CHANGED
W04_DEVCTRL_02_BASELINE_DRIFT
W04_DEVCTRL_02_SCOPE_VIOLATION
W04_DEVCTRL_02_SHADOW_EQUIVALENCE_FAILED
W04_DEVCTRL_02_PERFORMANCE_HARD_FAIL
W04_DEVCTRL_02_EXTERNAL_QUEUE_CONTAMINATION
W04_DEVCTRL_02_REQUIRES_GPT_CLARIFICATION
W04_DEVCTRL_02_STAGE_A_CI_FAILED
W04_DEVCTRL_02_STAGE_B1_CI_FAILED
W04_DEVCTRL_02_STAGE_B2_CI_FAILED
W04_DEVCTRL_02_STAGE_B3_CI_FAILED
W04_DEVCTRL_02_STAGE_C_CI_FAILED
```

Every stage uses one new commit and normal push, checks status/diff --check/exact stage delta, and waits for exact-SHA native Verification PASS. No amend/rebase/reset/force push/history rewrite/main write. A pushed-stage failure stops with SHA/run/classification/failed job/step/log evidence; no repair commit.

Stop at REVIEW_READY: GPT independent review and Human acceptance PENDING; DEVCTRL-02 closeout, C08, PR merge and branch deletion NOT AUTHORIZED. PR #7 remains OPEN / DRAFT / UNMERGED.

## Local process constraint

Default sandbox process startup failed with helper_unknown_error: setup refresh had errors. Scoped tool escalation is used for authorized read/write/verification commands; this changes no task permission or runtime boundary. GitHub connectors provide native evidence because gh is absent from PATH.
