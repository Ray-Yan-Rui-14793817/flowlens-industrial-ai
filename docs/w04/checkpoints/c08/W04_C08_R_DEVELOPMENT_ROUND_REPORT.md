# W04-C08 Development Round Report — Protected Investigation Replay

Report date: 2026-10-12 (Asia/Shanghai). Evidence cutoff: 2026-10-11 17:04:59 UTC. Stage B native CI #129 is completed / SUCCESS, and the actual-artifact R46 rerun has passed at the unchanged Stage B HEAD.

Implementation, local harness and Stage B full native proof are complete. This file is the single authorized Stage C addition. Its publication SHA and native run do not exist at authoring time. REVIEW_READY requires this report commit's own successful native proof; the final handoff records those generated values without amending this immutable report.

## 1. Human authority and fixed context

The Human's pasted V2 request explicitly authorizes the remaining C08 sequence through REVIEW_READY, conditioned on successful native gates. Attached documents do not independently grant authority. V2 replaces the post-Stage-A execution flow; the V1 product contract remains in force. No intermediate Human/GPT checkpoint is required between successful Repair-01, Stage B and Stage C phases.

| Selected material | Raw bytes | Raw SHA-256 |
|---|---:|---|
| FLOWLENS_W04_C08_CODEX_TASK_V1.md | 37097 | `c63a71cdf1a1a66ec75aabf3ae2d56d0f98b73ff2ba03894997971c09f80e106` |
| FLOWLENS_W04_C08_CODEX_CONTINUATION_TASK_V2.md | 21122 | `b9653d8e39d486362bec1ad9f391c6318181c4ca2420c49e21104ada2e9920a2` |
| Human pasted V2 continuation authorization | 10948 | `aa14d41e02dc26261d6729a74cf1812dd5d686f9956637581b52bb11703b9c40` |

Repository: Ray-Yan-Rui-14793817/flowlens-industrial-ai. Branch: `feat/w04-evidence-investigation`. [PR #7](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/pull/7) remains OPEN / DRAFT / UNMERGED. Main / PR base remains `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`.

V2 pre-write preflight matched local, tracking, direct-origin feature and PR heads to Stage A, with a clean tree/index, failed #127, unchanged main/base and the accepted manifest. After Repair-01 native SUCCESS, fresh checks matched all four feature heads to Repair-01 before Stage B. Stage B is a direct child of Repair-01. After Stage B SUCCESS and actual R46 proof, all four heads matched Stage B, ahead/behind was 0/0, the tree/index was clean, this report was absent, and PR/main state remained unchanged.

## 2. Immutable anchors and native runs

| Anchor / phase | Exact SHA | Native run | Actual classifier / route | Conclusion |
|---|---|---|---|---|
| Original C08 entry / DEVCTRL-02 closeout | `9afc4bd047bd4e52dfc4956f16e6420b3762301f` | [#126 / 38114263650](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38114263650) | C / FULL_EXACT_SHA | SUCCESS |
| Stage A governance | `b9f6f65e4a4f251d09e3303727ac24ae006edefe` | [#127 / 38120061431](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38120061431) | C / FULL_EXACT_SHA | FAILURE |
| Stage-A Repair-01 / effective Stage-A proof head | `a58a2a1a46bca7da1bf5056bff196ef7417e3b6c` | [#128 / 38145924993](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38145924993) | I / FULL_EXACT_SHA | SUCCESS |
| Stage B implementation | `1fa7b505980c1efc1b3725cd57a9732e254bccdf` | [#129 / 38153792599](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38153792599) | I / FULL_EXACT_SHA | SUCCESS |

### Exact #127 root cause and bounded repair

The only actual test failure was `tests/test_ci_test_sharding.py::test_workflow_exact_transport_timeout_and_no_runtime_dependency_mutation`. Its historical frozen-path tuple required `docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json` to remain byte-identical to the old DEVCTRL planner entry. Stage A legitimately appended C08 AUTHORIZED, so that obsolete assertion conflicted with checkpoint governance evolution.

Shard 2 selected 814 cases: 810 passed, 1 failed, 3 accepted skips. Static/Plan, Integration 70, the other six shards, Compose and W03 38 selectors / 85 cases passed. Aggregate, Quality and Verification failed downstream; Publication was skipped. C08 runtime implementation had not begun.

Repair-01 removed only that manifest path from the legacy byte-immutability tuple and added one concise comment directing manifest lifecycle enforcement to the unchanged source-evolution verifier/tests. It did not change that test's name/node ID/parameterization, any other protected path, manifest, planner, weights, workflow or timeouts.

Exact repair subject: `test(w04-c08): align CI guard with manifest evolution`. Exactly one path: `tests/test_ci_test_sharding.py`. The failing selector passed locally; the required CI-sharding/source-evolution group passed 207 tests. One normal commit and push produced Repair-01.

#128's 15 required full-route jobs all succeeded; Publication was skipped. Native outcomes were 2807 selected / 2804 passed / exactly 3 accepted skips / 0 failed, error, xfail or xpass. Integration passed 70 in 318.23s. W03 passed 38 selectors / 85 cases. Exact union, exact once and entry no-loss passed. Its original downloaded plan's complete 2807-node list exactly matched the committed C08 #126 baseline, although the then-historical planner receipt retained its older entry digest. Stage B is the authorized switch to the exact #126 active floor.

## 3. Exact paths, subjects and source identities

Stage A subject: `docs(w04-c08): authorize protected investigation replay`. Its accepted five paths were:

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c08/W04_C08_HUMAN_AUTHORIZATION.md
docs/w04/checkpoints/c08/W04_C08_CONTEXT_LOCK.md
docs/w04/checkpoints/c08/W04_C08_ENTRY_TEST_BASELINE.json
docs/w04/checkpoints/c08/W04_C08_CI_BOOTSTRAP_WEIGHTS.json
```

Those files were preserved through Repair-01 and Stage B. Stage B subject: `feat(w04-c08): add protected investigation replay`. One normal commit/push changed exactly five paths, with 2094 insertions and 37 deletions:

| Stage-B path | Measured Git blob OID at Stage B |
|---|---|
| `scripts/ci/plan_non_integration_shards.py` | `1df96ebca619d08812550276c023582ee758bcb6` |
| `src/flowlens/investigation/c08_policy.py` | `273d288cf4b0e55b646cd2e6751f0259e463a5ff` |
| `src/flowlens/investigation/c08_replay.py` | `4fa391cf751377305315b7de8303ce94e6eb6c6e` |
| `tests/test_ci_test_sharding.py` | `a7f1ad76443ad65790613f73a837c0f3c2f4d350` |
| `tests/test_investigation_replay.py` | `015b150b650ff22277d73148b1f8283ac76327e8` |

The two C08 runtime source OIDs are therefore `273d288cf4b0e55b646cd2e6751f0259e463a5ff` and `4fa391cf751377305315b7de8303ce94e6eb6c6e`. These are review evidence; the manifest's C08 freeze SHA and blob OIDs remain null because closeout is not authorized.

Stage C exact subject is `docs(w04-c08): publish protected replay proof`; its sole allowed path is `docs/w04/checkpoints/c08/W04_C08_R_DEVELOPMENT_ROUND_REPORT.md`. No Stage-A governance document is rewritten by this report.

No main write, merge, branch deletion, amend, rebase, reset, force push, history rewrite, dependency/schema/migration change or pushed native-failure repair occurred.

## 4. Local proof and actual test counts

Local environment: Windows / Python 3.12.14 / pytest 9.1.1; -B and no pytest cache provider. The frozen source-evolution controls require a clean source tree. Required precommit suites therefore ran in a private, unpushed validation fixture, with final fixture SHA `ead9aae62537d8f25d3709fe53050fb4e5007271`. All five prospective Git blobs and raw working-file bytes matched the final Stage-B files. Fixture commits are test setup, and are absent from the production feature history.

| Required local proof | Result |
|---|---|
| Replay + CI sharding + source-evolution suites | 397 passed; exit 0; no failures/errors/skips; pytest wall 1594.07s; JUnit suite 1588.278s |
| Frozen C07 summary + provider regression suites | 266 passed; exit 0; no failures/errors/skips; JUnit suite 1369.412s |
| Corrected fresh-import selector + 24 negative controls | 25 passed |
| Ruff whole repository | PASS |
| Strict mypy whole configured source/test tree | PASS / 175 files |
| Dependency lock with existing interpreter | PASS / same 43 packages |
| Exact changed-path set and git diff --check | PASS |
| Production source-evolution verifier at exact Stage-B SHA | PASS |

The first 397-case local run had 396 passes and one new fresh-import test defect. Windows' unchanged frozen temporal dependency initializes `ZoneInfo("Asia/Shanghai")` through tzdata resource loading, which indirectly imports stdlib random. A standalone import of frozen C07 reproduced that load; importing C08 afterwards added only its two modules. The corrected test compares C08 additions against the verified frozen C07 baseline, still rejects every protected DB/HGT/journal/provider/network module in the complete module set, and retains direct random-import/call AST negative controls and live replay random-call traps. The runtime source and frozen upstream source were unchanged. The complete 397-case suite then passed.

| Test file | Test functions | Parameterized functions | Expanded selected cases | Added cases versus #126 |
|---|---:|---:|---:|---:|
| tests/test_investigation_replay.py | 26 | 17 | 167 | 167 |
| tests/test_ci_test_sharding.py | 29 | 10 | 103 | 23 |
| Total authorized post-entry additions | — | — | 190 | 190 |

C08 has 9 nonparameterized cases plus 158 parameter expansions. Counts were measured from the actual AST, collection and native JUnit, not requirement-row counts. All 80 original CI-sharding node IDs remain. No new skip/xfail marker was introduced.

Local required JUnit SHA-256: `62ecc7b71aa03b4c2a798d0707a3b8731660b20a76274fda6e1a41e35fcb5069`. C07 regression JUnit SHA-256: `693bdd5bbecab453b11afc977c1ab3c67353e73a413d808fd69a995f2f4be4e0`.

## 5. Stage B full native proof and admission

Native environment: Linux / Python 3.12.15 / pytest 9.1.1. Actual classifier binds Repair-01 as before SHA and Stage B as head, with exactly the five implementation paths and reason `verified_source_head_delta`.

SUCCESS jobs: Classify change; Static and plan; Integration and data; Non-integration shards 0..6; Non-integration aggregate; Quality gate; Docker Compose smoke; W03 AI loop gate; Verification gate. Publication proof: SKIPPED as required by I / FULL_EXACT_SHA. All 16 job records bind the exact Stage-B head.

| Native measurement | Result |
|---|---|
| Original selected nodes / file count | 2807 / 62 |
| Original node digest | `4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d` |
| Original selected-file digest | `72f381af0f729834fc58920eec74f2ef1a6f9fb0991c7489350412fdfcf7366a` |
| Current nonintegration selected / files | 2997 / 63 |
| Current nonintegration node digest | `9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a` |
| Current passed / skipped | 2994 / 3 |
| Failed / error / xfail / xpass | 0 / 0 / 0 / 0 |
| Entry no-loss / exact union / exact once | PASS / PASS / PASS |
| Authorized added nodes | 190; exactly the two allowed test files |
| Integration | 70 passed; no skips or other nonpass outcomes; 322.53s pytest wall |
| Integration node digest | `bdcb72ebf947f5599d9e6cecf9bc29e65e9cb063daa03a715b41f5399ecf581c` |
| Native Ruff / strict mypy / lock | PASS / 175 files PASS / 43 packages unchanged |
| W03 gate | F01-F10 PASS; 38 selectors / 85 cases; exact Stage-B implementation_sha |

The exact accepted Linux skip set remains:

```text
tests/test_investigation_human_store.py::test_j40_j45_windows_junction_surfaces_fail_closed[case]
tests/test_investigation_human_store.py::test_j40_j45_windows_junction_surfaces_fail_closed[locks]
tests/test_investigation_human_store.py::test_j40_j45_windows_junction_surfaces_fail_closed[root]
```

Skip-set digest: `1524192888846ac2a7b1908212650648a38816aa72d458add70868c24d08a767`. They occur in shard 3; C08 has 167 native passes and zero skips/failures/errors.

### Exact admission and measured durations

Plan schema: `w04-devctrl02-non-integration-plan-v2`. Active floor: committed C08 #126 baseline, entry `9afc4bd047bd4e52dfc4956f16e6420b3762301f`. Original frozen DEVCTRL weights remain byte-identical. Effective total: 7,733,243 integer milliseconds. Scheduling preserves deterministic file-atomic LPT, descending weight/path ordering and lowest-index minimum-load tie-breaking. C08 landed on shard 1 through that algorithm. Unknown/unmodeled files and additions outside the two allowed files fail closed.

| Bound digest | Value |
|---|---|
| `base_weights_sha256` | `315675b184abd56422f469a44da5f840b40d82c3cfb272d46873afd7a8adacca` |
| `bootstrap_weights_sha256` | `36f1d85e34344afee1f7e76b066427e4f40314c68f1d564340d82cc4dd44becb` |
| `effective_file_weights_sha256` | `352e6e1060bc1c2d5ce9a36fcad6cb9941e373bfae3da4d8a326d26a0d1f01c6` |
| `native plan_sha256` | `bd2c2c6bf0839bb98f42009f31c86232e68cfe481df3c46f381dfc7224d11a92` |

The existing seven shards, fail-fast=false, max-parallel=7, workflow DAG, timeouts, artifact names, terminal outcome semantics, accepted skips, integration selection and W03 gate remain unchanged.

Job seconds are measured from final GitHub started_at/completed_at timestamps; pytest seconds come from native job logs. Estimate seconds are fixed scheduling weights, not measured runtime.

| Shard | Selected | Passed | Skipped | Files | Estimate seconds | Actual job seconds | Actual pytest seconds | Native result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | 712 | 712 | 0 | 6 | 1104.721 | 1133 | 1093.49 | SUCCESS |
| 1 | 285 | 285 | 0 | 14 | 1104.704 | 3176 | 3143.46 | SUCCESS |
| 2 | 217 | 217 | 0 | 6 | 1104.862 | 505 | 468.97 | SUCCESS |
| 3 | 398 | 395 | 3 | 10 | 1104.732 | 971 | 938.58 | SUCCESS |
| 4 | 369 | 369 | 0 | 10 | 1104.747 | 832 | 794.23 | SUCCESS |
| 5 | 469 | 469 | 0 | 9 | 1104.742 | 544 | 502.04 | SUCCESS |
| 6 | 547 | 547 | 0 | 8 | 1104.735 | 2129 | 2086.53 | SUCCESS |

Native C08's own 167 JUnit testcase durations sum to 3082.523s. Its 1061.491s bootstrap weight is conservative admission evidence derived from the largest frozen historical file weight; it is not measured C08 runtime and does not predict the observed duration. No weights, timeouts or scheduling policy were retuned.

## 6. R01-R46 direct selector map

Selectors below select every parameter expansion of the named function. All rows have direct passing selectors in local/native proof. R46 additionally has the post-terminal real-evidence rerun described below.

| Requirement | Direct passing selectors | Result |
|---|---|---|
| R01 | `tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order` | PASS |
| R02 | `tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order`<br>`tests/test_investigation_replay.py::test_r02_r05_r10_nested_original_identity_precedes_frozen_reconstruction` | PASS |
| R03 | `tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order` | PASS |
| R04 | `tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order` | PASS |
| R05 | `tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order`<br>`tests/test_investigation_replay.py::test_r02_r05_r10_nested_original_identity_precedes_frozen_reconstruction` | PASS |
| R06 | `tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order` | PASS |
| R07 | `tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order` | PASS |
| R08 | `tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order` | PASS |
| R09 | `tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order` | PASS |
| R10 | `tests/test_investigation_replay.py::test_r01_r10_original_chain_uses_frozen_validators_in_order`<br>`tests/test_investigation_replay.py::test_r02_r05_r10_nested_original_identity_precedes_frozen_reconstruction` | PASS |
| R11 | `tests/test_investigation_replay.py::test_r11_r16_receipt_versions_source_core_id_and_full_hash` | PASS |
| R12 | `tests/test_investigation_replay.py::test_r11_r16_receipt_versions_source_core_id_and_full_hash` | PASS |
| R13 | `tests/test_investigation_replay.py::test_r11_r16_receipt_versions_source_core_id_and_full_hash` | PASS |
| R14 | `tests/test_investigation_replay.py::test_r11_r16_receipt_versions_source_core_id_and_full_hash` | PASS |
| R15 | `tests/test_investigation_replay.py::test_r11_r16_receipt_versions_source_core_id_and_full_hash` | PASS |
| R16 | `tests/test_investigation_replay.py::test_r11_r16_receipt_versions_source_core_id_and_full_hash` | PASS |
| R17 | `tests/test_investigation_replay.py::test_r17_r19_metadata_only_immutable_receipt_preserves_exact_orders` | PASS |
| R18 | `tests/test_investigation_replay.py::test_r17_r19_metadata_only_immutable_receipt_preserves_exact_orders` | PASS |
| R19 | `tests/test_investigation_replay.py::test_r17_r19_metadata_only_immutable_receipt_preserves_exact_orders` | PASS |
| R20 | `tests/test_investigation_replay.py::test_r20_receipt_original_claims_must_recompute_exactly`<br>`tests/test_investigation_replay.py::test_r20_coherent_presentation_claim_still_recomputes_supplied_chain` | PASS |
| R21 | `tests/test_investigation_replay.py::test_r21_r25_valid_modes_and_wording_share_deterministic_authority_without_provider` | PASS |
| R22 | `tests/test_investigation_replay.py::test_r21_r25_valid_modes_and_wording_share_deterministic_authority_without_provider` | PASS |
| R23 | `tests/test_investigation_replay.py::test_r21_r25_valid_modes_and_wording_share_deterministic_authority_without_provider` | PASS |
| R24 | `tests/test_investigation_replay.py::test_r21_r25_valid_modes_and_wording_share_deterministic_authority_without_provider` | PASS |
| R25 | `tests/test_investigation_replay.py::test_r21_r25_valid_modes_and_wording_share_deterministic_authority_without_provider` | PASS |
| R26 | `tests/test_investigation_replay.py::test_r26_presentation_never_upgrades_findings_or_uncertainty` | PASS |
| R27 | `tests/test_investigation_replay.py::test_r27_invalid_original_packet_is_rejected` | PASS |
| R28 | `tests/test_investigation_replay.py::test_r28_original_case_identity_and_exact_projection` | PASS |
| R29 | `tests/test_investigation_replay.py::test_r29_questions_plan_and_nested_original_dependencies` | PASS |
| R30 | `tests/test_investigation_replay.py::test_r30_exact_query_order_keys_and_registry_projection` | PASS |
| R31 | `tests/test_investigation_replay.py::test_r31_captured_evidence_binding_provenance_trust_and_future_time` | PASS |
| R32 | `tests/test_investigation_replay.py::test_r32_findings_conflicts_and_nested_uncertainty_are_rederived` | PASS |
| R33 | `tests/test_investigation_replay.py::test_r09_r33_nonempty_exact_order_human_chain_and_opaque_note_authority` | PASS |
| R34 | `tests/test_investigation_replay.py::test_r10_r34_original_summary_and_coherently_rehashed_presentation_tamper` | PASS |
| R35 | `tests/test_investigation_replay.py::test_r35_exact_envelope_rejects_subclasses_mutable_collections_and_foreign_enums` | PASS |
| R36 | `tests/test_investigation_replay.py::test_r36_every_public_stage_failure_suppresses_protected_upstream_text` | PASS |
| R37 | `tests/test_investigation_replay.py::test_r37_r39_same_process_bytes_and_all_inputs_unchanged` | PASS |
| R38 | `tests/test_investigation_replay.py::test_r38_actual_frozen_wire_replay_is_identical_across_fresh_hash_seeds` | PASS |
| R39 | `tests/test_investigation_replay.py::test_r37_r39_same_process_bytes_and_all_inputs_unchanged`<br>`tests/test_investigation_replay.py::test_r39_r40_r42_live_external_traps_no_refresh_or_operational_mutation` | PASS |
| R40 | `tests/test_investigation_replay.py::test_r40_r41_runtime_ast_public_signature_and_fresh_import_are_protected`<br>`tests/test_investigation_replay.py::test_r40_r41_capability_audit_rejects_negative_controls`<br>`tests/test_investigation_replay.py::test_r39_r40_r42_live_external_traps_no_refresh_or_operational_mutation` | PASS |
| R41 | `tests/test_investigation_replay.py::test_r40_r41_runtime_ast_public_signature_and_fresh_import_are_protected`<br>`tests/test_investigation_replay.py::test_r40_r41_capability_audit_rejects_negative_controls`<br>`tests/test_investigation_replay.py::test_r39_r40_r42_live_external_traps_no_refresh_or_operational_mutation` | PASS |
| R42 | `tests/test_investigation_replay.py::test_r39_r40_r42_live_external_traps_no_refresh_or_operational_mutation` | PASS |
| R43 | `tests/test_investigation_replay.py::test_r43_authorized_two_source_paths_and_every_closed_upstream_object_unchanged` | PASS |
| R44 | `tests/test_ci_test_sharding.py::test_c08_r44_active_entry_is_exact_native_126` | PASS |
| R45 | `tests/test_ci_test_sharding.py::test_c08_r45_sealed_bootstrap_effective_weights_and_no_mutation`<br>`tests/test_ci_test_sharding.py::test_c08_r45_bootstrap_tamper_fails_closed`<br>`tests/test_ci_test_sharding.py::test_c08_r45_only_exact_two_files_may_add_nodes`<br>`tests/test_ci_test_sharding.py::test_c08_r45_effective_selection_fails_closed`<br>`tests/test_ci_test_sharding.py::test_c08_r45_actual_collection_has_no_loss_and_only_two_added_node_files` | PASS |
| R46 | `tests/test_investigation_replay.py::test_r46_native_full_proof_gate_rejects_incomplete_or_wrong_sha_controls`<br>`tests/test_investigation_replay.py::test_r46_stage_b_exact_sha_full_native_ci` | PASS |

### Actual R46 proof, rather than an asynchronous-run claim

The normal local/CI invocation of the R46 selector uses explicitly labeled FIXTURE metadata solely as gate controls. Its 11 negative cases reject wrong/pending/failed runs, missing/duplicate/wrong-head jobs, inappropriate Publication outcome, wrong classifier and incorrect W03 binding/counts. Those controls do not claim an asynchronous workflow has completed.

After #129 completed / SUCCESS at unchanged Stage-B HEAD, `tests/test_investigation_replay.py::test_r46_stage_b_exact_sha_full_native_ci` was rerun with `FLOWLENS_C08_NATIVE_PROOF` pointing to measured GITHUB_NATIVE metadata and the ten original artifacts. It passed one case in 15.91s, exit 0.

That rerun checked exact run/head/class/jobs/W03, all ZIP digests against GitHub artifact metadata, the original plan against current collection and the committed baseline, all seven original receipt/JUnit pairs, reaggregation through the unchanged frozen verifier, exact terminal-set equivalence with the original native aggregate, the exact three accepted skips, and the original integration receipt/JUnit with 70 passes.

Temporary real-proof JSON raw SHA-256: `de0df64de3b22d0b28fccede66a1a0477c44cac3de9851fb9c0346adbdcb03e2`. The proof and original ZIPs are retained under `C:/Users/C/AppData/Local/Temp/flowlens-c08-v2-20261011-a58a2a1/`, outside the source repository. Download URLs are transient and are not publication evidence.

All artifacts below belong to #129 / 38153792599 and the exact Stage-B SHA. Full names are `w04-devctrl02-<role>-1fa7b505980c1efc1b3725cd57a9732e254bccdf`.

| Original artifact role | GitHub artifact ID | Original ZIP SHA-256 |
|---|---:|---|
| integration-data | 11707437946 | `4178a447511ce918edb7eb5a88a0ff978d4f561b364f1c86bdaa6d0fa52d1a7f` |
| nonint-aggregate | 11708692092 | `cea81ba21787d1c8e8d32591a36ef6a6336e163c6c135bb2b26d608ca6122685` |
| plan | 11707960511 | `4af967bdf0f2d36a2f678f46db860b1f3f9d95ab1a62ea781069e26ab2361ad5` |
| shard-0 | 11708446476 | `70c1fd67454a688485fdfe64aa7baf521e28dbc7343471669f328225eaffca46` |
| shard-1 | 11708668545 | `9146a58fa567ee8376feee44b5e5e797c5cf49f039835e6c7ee072568084e34c` |
| shard-2 | 11708460252 | `c2dce8943d0f4ed54790238054b66c5e8bc89cb0e1293838618691e77e157be5` |
| shard-3 | 11708042144 | `fa2f5035149ff1a2a97d5c37bef10e3410acbf4679a0e30ebff1c713f8a7fc69` |
| shard-4 | 11707807948 | `b428df7948aa509cea8d174da94d03aaafbbd7cdbae85c33770689013b96373d` |
| shard-5 | 11707627829 | `c4e4ca728b490724bf5ba28a11de595b71451625086ef96ef0b9d9b44141a1cf` |
| shard-6 | 11708533352 | `c0ea61f68158b606fb48de69cc74203359887e15b7a9cd3488d6c2a1663ee645` |

## 7. Replay semantics and protected boundary

The public replay API accepts only the eleven frozen artifact-chain inputs; validation adds only the immutable receipt. It exposes no engine/connection/path/journal/provider/model/HGT/scenario/evaluation/current-time/callback/tool/mutable-operational-context parameter.

Original exact dataclass/enum/tuple envelopes and nested identities are checked before frozen validators can reconstruct projections. Admission runs in normative order: original DecisionPacket and C02 case; C03 questions/plan; pure C04 query specifications; captured evidence admission; C05 findings/conflicts/register; exact-order nonempty C06 Human chain; original supplied C07 summary; then a freshly regenerated C07 DETERMINISTIC summary with provider=None. Replay reuses the frozen validators and does not repair evidence or settle uncertainty.

`source_chain_sha256` binds canonical validated bytes of packet, case, questions, plan, queries, slices, findings, conflicts, uncertainty register and Human events. It excludes the presented summary. Core SHA-256 binds exactly the C08 contract version, source-chain digest, authoritative deterministic summary ID/content hash and fixed limitation tuple. `replay_id = "ireplay_" + replay_core_sha256`.

The supplied summary contributes presented ID/content hash/mode to the full receipt audit hash. Valid DETERMINISTIC, DEGRADED_FALLBACK and BOUNDED_LLM presentations, including alternate valid bounded wording, have the same core/replay ID for the same frozen chain; full receipt hashes can differ. Normal, unknown, conflict and empty-evidence shapes were directly exercised. Presentation cannot change authoritative findings, uncertainty, conflicts or Human references. BOUNDED_LLM validation invokes no provider.

The receipt is frozen/slotted, with all derived fields init=False and a closed validating factory. It contains versions, hashes, artifact IDs, presentation mode and fixed limitations, with exact admitted tuple orders. It contains no SQL, raw evidence, Human note text, provider text, HGT, credentials or operational payload. Receipt validation checks the original structure/self-seals, recomputes the complete replay and compares exact canonical bytes. Coherently rehashed false presentation claims are rejected.

AST/public-signature/fresh-import checks, 24 capability-audit negative controls and live execution traps directly cover DB/SQL, network, filesystem, environment, clock/random/secrets, journal, provider, navigation, HGT/scenarios/evaluation and operational mutation. Captured inputs and changed-after-capture database control states prove replay does not reread current data and preserves input bytes. Windows' accepted frozen timezone import behavior is accounted for as described in section 4; no C08 random/clock or filesystem invocation is admitted.

Public replay/validation failures expose only the nine stable C08 codes, with suppressed upstream diagnostic context. Tests inject protected-looking upstream text and reject original/coherent tamper, subclasses, mutable collections and foreign enums across every stage. Human notes stay opaque non-evidence, and the original Human chain is validated without rerunning decisions or reading/recording journal storage.

## 8. Frozen upstream objects and governance state

All 15 runtime source blobs declared by C01-C07 remain equal to their accepted manifest freeze OIDs. Closed checkpoint entries are unchanged from entry. The original C07 summary/provider tests also remain frozen. The production source-evolution verifier at exact Stage B returns PASS, C01-C07 CLOSED, only C08 AUTHORIZED, the exact two C08 source paths, and unchanged W03 baseline `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`. Manifest raw SHA-256 remains `ce937430acfd667734c367a57375ba31e2e4b15daab8fae87621aab496d00835`.

The following Git objects are equal at entry and Stage B:

| Protected path / tree | Preserved Git object OID |
|---|---|
| `.env.example` | `95384f33192966dc4b1900bf38e3366e8650a06d` |
| `.github` | `d85309ff678a4a17dafad77d3cac748822257a9b` |
| `apps` | `597399c7919982e9b2d54fc8b58fe6784cfe8585` |
| `docker-compose.yml` | `5a0b6e8486edc69f9f79c7e1345a842aa412983c` |
| `docs/w03` | `cb81e388c6c44a9900575ef2e72161dc0205be94` |
| `docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json` | `93ebe129f9345ea540b5e06aef053f2a62bb0846` |
| `migrations` | `c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433` |
| `pyproject.toml` | `318bbc0a858f760e6c4d7a2d3fdbfcc111febb77` |
| `scripts/ci/classify_change.py` | `fd9e99c6b55b85f184198c51f0f97ba16323ce32` |
| `scripts/ci/pytest_outcome_receipt.py` | `c7873d5fa29dc7cef2a85a9d307d16b8d099474b` |
| `scripts/ci/run_non_integration_shard.py` | `dc4dc3a5ede99832d67a5682a7186aeb0d58c9a6` |
| `scripts/ci/verify_non_integration_shards.py` | `a375a1d461ae0bf49752716791db6b79c16be38b` |
| `scripts/ci/verify_publication.py` | `8f97a117f936d9dce91957f7b44551acb5d5c2b6` |
| `scripts/ci/verify_w04_source_evolution.py` | `4efaefed505e24796a0c2fa545ce4b7eb252d70a` |
| `src/flowlens/api` | `4d0f47613296d871f70e2dfdab6f21f31b42663a` |
| `src/flowlens/data` | `d5679d706ed19b0802441b1002af5e5e23513edc` |
| `src/flowlens/db` | `a3b774f3bcc322ee19951c92948501315b0e7cb2` |
| `src/flowlens/decision` | `71eddb93cfee5c5e5822d6598ef2f4a1f63648df` |
| `src/flowlens/evaluation` | `1a474ebe5c80bd771591a17c359c299266081580` |
| `src/flowlens/worker` | `a66b83c427082a9f07394dba21508f62bf4e0fcc` |
| `uv.lock` | `619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a` |

The complete 2807-node no-loss proof and unchanged 70 integration selection protect accepted upstream tests, while native W03 gate independently retains all ten families. Operational schema, Alembic semantics, canonical dataset hashing, deterministic generation, Supplier/Quality/Capacity scenarios and HGT identity/isolation remain unchanged.

Manifest: C01-C07 CLOSED / C08 AUTHORIZED; C08 source_freeze_sha=null and both blob_oid=null; C09 ABSENT / NOT AUTHORIZED. Neither this report nor technical harness success records Human acceptance or checkpoint closeout.

The historical GitGuardian Generic Password occurrence in old Compose history at commit prefix 7eb6c06 is the Human-triaged local-development PostgreSQL default/fallback. It was not introduced by C08 and did not cause #127. Compose/.env.example, credentials, GitHub secrets and historical Git data were not changed.

## 9. Honest limitations and terminal boundary

- This is frozen-artifact replay integrity only, with no current evidence refresh.
- It makes no causal or model-accuracy claim and reads no runtime HGT.
- It creates no operational action authority and performs no operational mutation.
- Human decisions are not rerun; Human notes are not evidence.
- Deterministic replay authority is independent of optional LLM wording.
- The bootstrap weight is admission evidence, not measured C08 runtime or a runtime estimate guarantee.
- The tests prove the stated artifact/capability boundaries over the exercised cases; they do not accept business outcomes or authorize the next checkpoint.

At this immutable report's cutoff: implementation COMPLETE; local/native harness PASS; Stage B exact-SHA CI PASS; actual R46 proof PASS. Stage C publication proof is still required before the final handoff may declare `W04_C08_REVIEW_READY`.

GPT independent implementation review: PENDING. Human C08 acceptance: PENDING. C08 closeout: NOT AUTHORIZED. C09: NOT AUTHORIZED. PR #7: OPEN / DRAFT / UNMERGED. PR merge and main write: NOT AUTHORIZED. After this report's own exact-SHA native SUCCESS, stop at REVIEW_READY and wait for independent ChatGPT deep review.
