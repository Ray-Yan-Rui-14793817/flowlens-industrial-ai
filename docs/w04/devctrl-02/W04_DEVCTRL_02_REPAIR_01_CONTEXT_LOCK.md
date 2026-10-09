# W04-DEVCTRL-02 Repair-01 Context Lock

Locked on 2026-10-09 before changing either test. All activation facts were independently read from local Git, the direct origin refs and GitHub API/native logs.

## Contract provenance

| Read contract | Raw-file SHA-256 |
|---|---|
| FLOWLENS_W04_DEVCTRL_02_POST_122_CUTOVER_TASK_V2_2_1.md | a882f0a2b3e091267737a84d86a386177223c1db1f22808b7706994315999139 |
| FLOWLENS_W04_DEVCTRL_02_POST_122_CODEX_PROMPT_V2_2_1.md | 3d9169d0e7cea52e5400f269e11644340e5c933705129ab2ab585304be405867 |

V2.2.1 is normative. Referenced V2.2 task/design/review were read completely. Completed Stage A is retained unchanged.

## Fresh activation

```text
REPOSITORY: Ray-Yan-Rui-14793817/flowlens-industrial-ai
VISIBILITY: PUBLIC
BRANCH: feat/w04-evidence-investigation
HEAD / TRACKING FEATURE HEAD / DIRECT ORIGIN FEATURE HEAD / PR HEAD:
9d5b6e3baea1a860446b70d9b254cc3dc41815a4
INDEX / WORKTREE: CLEAN
PR #7: OPEN / DRAFT / UNMERGED
MAIN / PR BASE: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
MANIFEST: C01-C07 CLOSED
C08: ABSENT / NOT AUTHORIZED
```

| Immutable stage | SHA | Native CI |
|---|---|---|
| C07 closeout | f50d6c6f8eeacd9df3320dc4a8c6269aa6caa3a5 | #120 / 37800395278 / SUCCESS |
| Stage A | 4a5ab37251c1fecff4291ae6198e03c847cf8735 | #121 / 37882221740 / SUCCESS |
| B1 Attempt 1 | 9d5b6e3baea1a860446b70d9b254cc3dc41815a4 | #122 / 37889883403 / COMPLETED FAILURE |

## #122 complete root-failure audit

Actual class/proof: I / FULL_EXACT_SHA. Legacy non-integration: 2807 collected, 2802 passed, 3 skipped, 2 failed; no errors, xfails or xpasses. Integration: 70 collected/passed, all other outcomes zero.

Only independent root failures:

- tests/test_investigation_evidence_queries.py::test_n52_committed_source_governance_and_frozen_blobs (legacy Quality and shadow shard 1).
- tests/test_investigation_summary.py::test_s52_frozen_upstream_w03_dependencies_and_control_bytes_unchanged (legacy Quality and shadow shard 2).

Legacy Quality job 113688201992 failed only Run complete test suite. Shadow shard 1 job 113688383015 and shard 2 job 113688382952 failed their assigned execution steps with the same two tests. Aggregate 113697257630 rejected SHARDS_RESULT=failure. Equivalence 113730543824 rejected LEGACY_RESULT=failure. Missing downstream output uploads and Verification 113732189469 are consequences, not new independent roots. Static, integration, shards 0/3 and Compose succeeded. W03 job 113730543832 proved 38 selectors / 85 cases / PASS with the frozen manifest. Publication was skipped.

#122 ran 05:42:46Z to Verification completion 08:14:49Z; the API final update was 08:14:50Z. Legacy Quality was 2h26m50s and its complete non-integration step was 2h20m14s. This was deliberately a dual legacy/shadow equivalence run. The longest parallel shadow shard was 34m10s; steady-state cutover performance must be measured at B2.

## Exact node identities

Fresh locked local collection independently matched native #122:

| Marker | Nodes | Canonical sorted-node SHA-256 |
|---|---:|---|
| not integration | 2807 | 4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d |
| integration | 70 | bdcb72ebf947f5599d9e6cecf9bc29e65e9cb063daa03a715b41f5399ecf581c |

Entry no-loss: PASS. All 2726 entry nodes, digest 0089b5889f7de2dbe637ddef3774966ae07f6cf6d6518f2648f20e47ccbaa4a7, remain. No repair node addition/removal/rename/parameterization/skip/xfail is authorized. Baseline raw-file digest remains 535dd95d2af064402a5b4892a2aa3b690ee092e7148aea1c4299b00ca95af102. B1 plan digest bb1358327b6c13ebcc52ff92516be38e9c66d34c61c9e1e554f5f1aeccca30e5; canonical weights digest 7a1009504357be3b9c7b312186aa29badd6bf65818925cc8d31cc19523856fc9.

## Historical lifecycle anchors

| Reference | Exact Git object |
|---|---|
| C04 closeout | 783234ac0ca1ba5c2b33d46f8576a12c2184114c |
| C04 closeout:.github/workflows/ci.yml | 14c826b122b7103953e8b4539981004241205ba4 |
| HEAD:scripts/ci/verify_w04_source_evolution.py | 4efaefed505e24796a0c2fa545ce4b7eb252d70a |
| C07 entry | e372b0d8ab038eda936d3a3b9ce4d77bfc8fce29 |
| C07 closeout | f50d6c6f8eeacd9df3320dc4a8c6269aa6caa3a5 |
| C07 entry and closeout:.github/workflows | a87993148e099c6a175c013e2a7cdd7128f183d2 |
| C07 entry and closeout:scripts/ci | b8ded9847fa8c23309bbd1af11847c8b27666685 |

Both closeouts independently passed git merge-base --is-ancestor against current HEAD. Current B1 control objects below are separate authorized DEVCTRL objects and are not blessed as historical C04/C07 replacements.

## B1 exact nine-path delta

```text
.github/workflows/ci.yml
docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json
scripts/ci/plan_non_integration_shards.py
scripts/ci/pytest_outcome_receipt.py
scripts/ci/run_non_integration_shard.py
scripts/ci/verify_non_integration_shards.py
tests/test_c09_ci_gate.py
tests/test_ci_change_classifier.py
tests/test_ci_test_sharding.py
```

## Frozen current Git identities

SHA-256 uses committed bytes returned by git show. Directory rows use the Git tree listing rather than recursive file-content hashing. Repair must retain every row except the two explicitly authorized test bodies.

| Path | Git object | Committed-byte SHA-256 |
|---|---|---|
| .github/workflows/ci.yml | c591750f0029cf39b73e1c38b75299159172f0a6 | 4bfb471a9eeeb43cdf533e3771ba395553bc3a6a6a7b7cf2ec0125fe9bfdc047 |
| apps | 597399c7919982e9b2d54fc8b58fe6784cfe8585 | 3d7c1905261a51745e2e11360646dd770d4838e8a947dab961628738f4125a41 |
| docker-compose.yml | 5a0b6e8486edc69f9f79c7e1345a842aa412983c | 827802a6a94162d61f5469f56d7e50d393d7338ed0806c2f01c6816f4a4596e7 |
| docs/w03 | cb81e388c6c44a9900575ef2e72161dc0205be94 | 83aec6565172563cf44c689ec605542635f20ae10f73cae7e226caf0b507356b |
| docs/w03/checkpoints/c09/specs/c09_gate_manifest.json | b2a03f3295c162a639eb99dbd87b4a636c3b1e85 | bce35059fdaeb49a5598b3144f481996774bbaee68fcc3096d621a1296ebd990 |
| docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json | 3a173837de8ea3888de7f9a7de0fd4e34b7f0a5b | 5cff9d7e6d4b77bf4e274253d30ba34dc2688ea98832e0ce93c6b8a62b0e3b73 |
| docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json | b18fd5e5a52b0b83578a3bceab68e8752fc6e290 | 9a18cf6dae4bfa97b09349c4677b58317dc8ffccccb18ad22b55cc405057e0af |
| docs/w04/devctrl-02/W04_DEVCTRL_02_ENTRY_TEST_BASELINE.json | 222d3f8fe6eaacc6013259a68498a399f44af144 | 535dd95d2af064402a5b4892a2aa3b690ee092e7148aea1c4299b00ca95af102 |
| migrations | c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433 | 4849f31bdea2095abc03b6d7316b1387a9d384ee306c3cd0ea3843d8aab6c96d |
| pyproject.toml | 318bbc0a858f760e6c4d7a2d3fdbfcc111febb77 | 51484d6fe8e5f42658c09dda3bd3654954bbfe77fc8bed8fdb67ca74bbbda746 |
| scripts/ci | 974a7c15a26946e071c3eae634fe67e23970adff | 41a75ccd663d4adb668549698fc967fd2d2526175183a474e93aeef8bbeebb31 |
| scripts/ci/plan_non_integration_shards.py | e177912304a7046753a8475ae5dfccd1aa2ee658 | 426c2dc9f7b371b7ac4028478f044ca2c1eb26f8c1a3a5a16a57a9a909a1ba38 |
| scripts/ci/pytest_outcome_receipt.py | fd2d9824fea5fa92147ed7b66f8ebaccb7ecd42a | 94831c7cb987affcd59f4aad9a9f186af778153dc13f2ad8626479f8c6b91bc3 |
| scripts/ci/run_non_integration_shard.py | a1e90ce98c9bf2874e57e2a2a149f9f84b3b0b2a | 16efe5484d5193a118c4da065919b98b7339599445eba40e9b31ade7e4a0817a |
| scripts/ci/run_w03_ai_loop_gate.py | c533928e584335437ae8a902fcab4faab64ae8ef | ee420e8be33f63e2882ebbee3a441b82fe3b933bc8973a48c0ac610e922314a7 |
| scripts/ci/verify_non_integration_shards.py | 7cfd8db41f0a542fc3562582f7b5362c36574ace | 930e2fa91ca9cad43b3f90be45ad5072d7722750b3ff89fd2365f8790badd95d |
| scripts/ci/verify_w04_source_evolution.py | 4efaefed505e24796a0c2fa545ce4b7eb252d70a | aa21c0f7f35ba743d91e15503caf6678d0073588859107b68fd18f2f78ae28f8 |
| src | 32856501648e4fea75489be8dd467553e9888fd1 | 6fc574261a79c16619508811f318356fb7f44c273dfb85a31474ce462052c96e |
| tests/test_c09_ci_gate.py | b9ce3c07bea285b4e551fc92d4ab6e5e58a41cc4 | c8828838cc6dbe26efc941086e99043b82c45e5d2891b44961ad12b87e372f6c |
| tests/test_ci_change_classifier.py | 635e632a71c2d8aed15c6ff885932bc513e6a74b | 810ab329c5b6526a7609b50256a00edd5a8ddc7c75886bb83765c401a2cba258 |
| tests/test_ci_publication_gate.py | ea7f8fb5c99b8bf52598b5d1db240aa650595600 | a1b3796739a05ea643fd84c62e4ab4965dac44ecabb44658c014efa8a43fc956 |
| tests/test_ci_test_sharding.py | 9a752a2811f616b7d56a03cf4b789733ef85e64f | 8d2591cd38b19c2f6056736f880005bddc5f4af093222b33081a4c8102842c30 |
| tests/test_investigation_evidence_queries.py | 54f43e27ce42c0ae6ea903d7b278b916748f40ed | 120911577aaeb40bb1fe9491616fa6f8616a2c9956485fd2865a3f9d001adb98 |
| tests/test_investigation_summary.py | 6d23ffe9fb3e13c5aa2d9350c865342a54d2c5b9 | 4ed71203b4ad9dee79c5c55e24df19358ed84038eb96c54ccc7bfa80a59b0ab9 |
| uv.lock | 619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a | 887747a11dd1f3e27692586636b9061b5993dbc2969d80da7cbdcbe045ac80b0 |

## C01-C07 manifest-declared frozen source

| Checkpoint | State / freeze SHA | Source path | Blob |
|---|---|---|---|
| W04-C01 | CLOSED / 084c2fea93d0e021994de015c986de9ff92bf9a3 | src/flowlens/investigation/__init__.py | c23929f85dccd78bc72ef3b2b1415c6e8eaf0452 |
| W04-C01 | CLOSED / 084c2fea93d0e021994de015c986de9ff92bf9a3 | src/flowlens/investigation/contracts.py | 0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e |
| W04-C01 | CLOSED / 084c2fea93d0e021994de015c986de9ff92bf9a3 | src/flowlens/investigation/enums.py | 9c818780423f32f144b18666784ebc9ea3abdccc |
| W04-C02 | CLOSED / 18648915414a26dddbdc904965663730ea631cf2 | src/flowlens/investigation/c02_binding.py | 5f0af237ed465fa83e5a3b84954512b1f3125551 |
| W04-C03 | CLOSED / 42047bcfe6591f7c9ed9b0034bd94467401ba72f | src/flowlens/investigation/c03_planning.py | 21d0055e12d86e6333a836d363d6e266cb0fcbd7 |
| W04-C04 | CLOSED / 6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1 | src/flowlens/investigation/c04_navigation.py | 98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4 |
| W04-C04 | CLOSED / 6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1 | src/flowlens/investigation/c04_queries.py | dc22c7e532a4b62ccfffec2210bc2a6306d97234 |
| W04-C04 | CLOSED / 6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1 | src/flowlens/investigation/c04_registry.py | fbe6f0603d7b0634426ac0034033089eb55af4d7 |
| W04-C05 | CLOSED / 3386b2637f0b0e3f0972a07ee0bea4ad8181cb5f | src/flowlens/investigation/c05_findings.py | 31384426ba9c733bc5bdbf3b09a3d206c8182586 |
| W04-C06 | CLOSED / de02e49af9ada512ff52afdcc5f72620c4f220af | src/flowlens/investigation/c06_human.py | 021f5b72254c87c5b965500727a67001a47ef0bd |
| W04-C06 | CLOSED / de02e49af9ada512ff52afdcc5f72620c4f220af | src/flowlens/investigation/c06_policy.py | 8cfea031eaa764d871822c2e12de019ed3ebc3b9 |
| W04-C06 | CLOSED / de02e49af9ada512ff52afdcc5f72620c4f220af | src/flowlens/investigation/c06_store.py | e99d5d4c36db1dd3ed11c40ff9bbc5b01663ae9a |
| W04-C07 | CLOSED / c86f7af2370f315b8b7310008521f08ceade6d97 | src/flowlens/investigation/c07_policy.py | c969c4bbf33910fab6ffb36c3bfe184fd42c74c9 |
| W04-C07 | CLOSED / c86f7af2370f315b8b7310008521f08ceade6d97 | src/flowlens/investigation/c07_provider.py | 56ecb9f3d7b5a1917a2354572e8c946f07eb759d |
| W04-C07 | CLOSED / c86f7af2370f315b8b7310008521f08ceade6d97 | src/flowlens/investigation/c07_summary.py | 3d561da7ab625421bbcf2dcb3785f8fae792cbff |

## Read-only public CI boundary

Root permissions remain contents: read. No pull_request_target, secrets-dependent proof, OPENAI_API_KEY, write token scopes, repository mutation or cross-run artifact ingestion. Artifact actions remain immutable SHA pinned, same-run, exact-name and exact-HEAD bound. Repair changes no workflow or scripts/ci byte.

## Exact repair allowlist and stops

```text
docs/w04/devctrl-02/W04_DEVCTRL_02_REPAIR_01_AUTHORIZATION.md
docs/w04/devctrl-02/W04_DEVCTRL_02_REPAIR_01_CONTEXT_LOCK.md
tests/test_investigation_evidence_queries.py
tests/test_investigation_summary.py
```

```text
W04_DEVCTRL_02_REPAIR_01_WAITING_FOR_B1_TERMINAL
W04_DEVCTRL_02_REPAIR_01_CONTEXT_CHANGED
W04_DEVCTRL_02_REPAIR_01_NODESET_DRIFT
W04_DEVCTRL_02_REPAIR_01_SCOPE_VIOLATION
W04_DEVCTRL_02_REPAIR_01_CI_FAILED
```

No generic repair or second repair commit is authorized. Preserve all runtime/W03/dependency/migration/manifest and Stage A evidence. B1R must pass its own complete native proof before B2. Final authority ends at REVIEW_READY; review/acceptance pending, no closeout/DEVCTRL-03/C08/merge/branch deletion/main write/history rewrite.
