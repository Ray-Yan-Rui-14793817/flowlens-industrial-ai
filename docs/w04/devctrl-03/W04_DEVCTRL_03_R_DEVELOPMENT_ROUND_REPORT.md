# W04-DEVCTRL-03 development round report

## Result and publication boundary

Stage A completed under V1 plus Human Clarification-01: measured 63-file weights
are active, seven file-atomic deterministic LPT shards are preserved, and only
the non-integration timeout changed from 55 to 65 minutes. Its own full native
CI #134 / 38352852439 succeeded at
`3f633fcd993b4f188ab01f04356670737524b5ad`.

Longest actual shard job: **1841s (30m41s)**, strictly below 3300s (55m).
Headroom under the 3900s (65m) ceiling: **2059s (34m19s)**.
Real-native R46 passed using all ten original exact-SHA artifacts.

C01-C08 remain CLOSED and unchanged in lifecycle/runtime/source-freeze semantics.
C09 remains ABSENT / NOT AUTHORIZED. Product runtime change: NONE.

This report is the sole Stage-B candidate, written after Stage-A native SUCCESS,
resilience PASS and real-native R46 PASS. Its own commit SHA does not yet exist
at authoring time; its native publication CI is PENDING. No future SHA or CI
success is claimed here. After that commit's own native terminal SUCCESS, the
final Human handoff records the actual published SHA/run and
`W04_DEVCTRL_03_REVIEW_READY`, without amending this report.

Independent GPT review: PENDING. Human acceptance: PENDING.
DEVCTRL-03 closeout: NOT AUTHORIZED. PR #7 remains OPEN / DRAFT / UNMERGED.
C09, PR merge and main write: NOT AUTHORIZED.

## Authorization and entry context

Repository: Ray-Yan-Rui-14793817/flowlens-industrial-ai.
Branch: feat/w04-evidence-investigation. PR: #7.

- V1 raw SHA-256: `54395514fabd6498d59dee57e1374f3f3638b40a8c31bac29bcb0e6e46683ea7`.
- Clarification-01 raw SHA-256: `683320441e5f6945030a935e245781454e007d841eb45f6bd826b6ebb078762f`.
- Entry local/tracking/direct-origin/PR head: `a18e7f0733079ecc9aebdd94458625011e2f93f9`.
- Entry native proof: #133 / 38205524984 / SUCCESS / C / FULL_EXACT_SHA.
- Main / PR base: `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`.
- Entry index/worktree CLEAN, ahead/behind 0/0; PR OPEN / DRAFT / UNMERGED.
- Manifest: C01-C08 CLOSED; AUTHORIZED none; C09 ABSENT.

Fresh refs and PR metadata were rechecked before Stage-A commit/push and before
report creation. At report creation all four feature heads equal Stage A,
main/base remain unchanged, and the index/worktree are CLEAN.

The Human accepted the independently derived measurements from the previous
read-only attempt. This continuation verified their original ZIP/JUnit/receipt
and saved derivation seals and reused them without reinterpretation.
Saved full derivation SHA-256:
`676da9ab5981e6b81d4d3fc0e0d093f0437cc2849e3d6b5af2f9d0bfafd780ca`.

## Three-run source evidence

All three successful full runs have exactly 2997 selected / 2994 passed /
3 accepted skipped / 0 failed, error, xfail or xpass; 63 files; entry no-loss,
exact union and exact once PASS. Current node digest:
`9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a`.

The #126 entry no-loss baseline remains 2807 nodes / 62 files, digest
`4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d`.

### Source #129

Run: [129 / 38153792599](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38153792599).
HEAD: `1fa7b505980c1efc1b3725cd57a9732e254bccdf`. Aggregate artifact: `11708692092`.

- ZIP SHA-256: `cea81ba21787d1c8e8d32591a36ef6a6336e163c6c135bb2b26d608ca6122685`.
- Aggregate JUnit SHA-256: `0c4f2633c1e43fe6c2f3e868b59eb7509c1f7393d001cf038650d655a7564875`.
- Aggregate receipt self-seal: `d0b14deb926bc021dddf2a88c68de506079f5c87889528024e304c1413c5b675`.
- Plan self-seal: `bd2c2c6bf0839bb98f42009f31c86232e68cfe481df3c46f381dfc7224d11a92`.

### Source #132

Run: [132 / 38200544252](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38200544252).
HEAD: `0047bb942e8e4227af8d6fb5c9a4763688a22aab`. Aggregate artifact: `11725204097`.

- ZIP SHA-256: `c0721ca64c9d2e59e59560681c5531e840768a623ed4ee07b612104002ad9c58`.
- Aggregate JUnit SHA-256: `d2f5ea4e07c48ff1891cd45cd51a3056f96d538d6916a98470c4dbab6258a4de`.
- Aggregate receipt self-seal: `f848f66caa0c4fde2bc4d1ab463dc658709af8e57aea5aeaac72ddcdeac132e5`.
- Plan self-seal: `99d5c25805edf5904acde6b4fda39f92883c9f4323990aa0547f675b4580ca43`.

### Source #133

Run: [133 / 38205524984](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38205524984).
HEAD: `a18e7f0733079ecc9aebdd94458625011e2f93f9`. Aggregate artifact: `11727789439`.

- ZIP SHA-256: `d4329c5f686d3ec027b8b3aace75f58d4614225f286e629dbedb0664d7b1c1c8`.
- Aggregate JUnit SHA-256: `a18e886433b2d737ac071bfbb5959d8c76349633923eb998b41cc58bee4846e5`.
- Aggregate receipt self-seal: `3762f815e9cee1bf5773ea10092fd02d86a89c27a662e74ee37cd954bf0fb78a`.
- Plan self-seal: `45b28233eb71574b78ae737366bbdd5561a2a8e6ed28dae5cff81fd453a38c36`.

## Exact measured derivation and active identity

Exact median of per-file JUnit testcase-duration sums from successful full exact-SHA runs #129, #132 and #133, in that order, with identical 2997-node collection. Integer millisecond arithmetic; no averaging, smoothing or overrides.

Each file has exactly three raw per-run samples in #129/#132/#133 order. Every
sample is the sum of exact JUnit testcase `time` attributes for that file,
using integer millisecond arithmetic. Scheduling cost is the exact median;
observed maximum is the exact maximum. All 63 file records and all source
identities are sealed. No average, smoothing, guessed override or default
unknown-file weight exists.

Old active model: #122 base 6671.752s + C08 bootstrap 1061.491s = 7733.243s.
New active median model: **9645.665s / 9645665ms**.

The immutable historical files remain unchanged:
`docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json` and
`docs/w04/checkpoints/c08/W04_C08_CI_BOOTSTRAP_WEIGHTS.json`. They no longer
participate in active scheduling. Existing historical validators remain
available solely for their evidence checks. A CI test traps any active-plan
read of either historical file.

Active evidence:
`docs/w04/devctrl-03/W04_DEVCTRL_03_MEASURED_SHARD_WEIGHTS.json`.
Schema: `w04-devctrl03-measured-shard-weights-v1`.

- Measured self-seal: `a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851`.
- Raw active evidence SHA-256: `6af36a1a7ff8cf68e2715f6477d864b333b4417b942fc683eb38aa71012d59c3`.
- Active evidence Git blob: `558f1a3ba2de948a18232ce4fca90be9447aec81`.
- Effective integer-millisecond digest: `cb646fa14756be9ea598c26309d291684f520dc76286416e28ddcc40f111f0cd`.
- Exact selected-file digest: `890fdd5c30c7e2a1e90da8cb8b7123937d3356f1d519f82dff4a941f13659fd7`.

Hot file `tests/test_investigation_replay.py`: samples
3082.523 / 2040.544 / 1658.888s; median 2040.544s; observed maximum 3082.523s.

## Full 63-file evidence and old/new assignments

All durations below are seconds with exact millisecond precision. Old assignments
are the common frozen #129/#132/#133 plan; new assignments are the actual Stage-A
measured plan. The code computes them from deterministic LPT and does not
hard-code file destinations.

| File | #129 | #132 | #133 | Median | Observed max | Old shard | New shard |
|---|---:|---:|---:|---:|---:|---:|---:|
| `tests/integration/test_database.py` | 0.005 | 0.004 | 0.004 | 0.004 | 0.005 | 1 | 5 |
| `tests/test_alembic.py` | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 | 1 | 5 |
| `tests/test_api.py` | 0.092 | 0.087 | 0.075 | 0.087 | 0.092 | 1 | 5 |
| `tests/test_c03_diagnosis.py` | 3.192 | 3.170 | 3.358 | 3.192 | 3.358 | 0 | 4 |
| `tests/test_c03_harness.py` | 7.200 | 4.735 | 3.825 | 4.735 | 7.200 | 1 | 5 |
| `tests/test_c03_policy_contract.py` | 0.002 | 0.001 | 0.000 | 0.001 | 0.002 | 1 | 4 |
| `tests/test_c03_signals.py` | 12.144 | 12.166 | 5.815 | 12.144 | 12.166 | 6 | 4 |
| `tests/test_c04_harness.py` | 7.544 | 15.777 | 16.430 | 15.777 | 16.430 | 2 | 5 |
| `tests/test_c04_registry.py` | 1.038 | 2.565 | 2.513 | 2.513 | 2.565 | 3 | 6 |
| `tests/test_c04_scenario_adapter_compat.py` | 2.318 | 2.438 | 1.529 | 2.318 | 2.438 | 6 | 4 |
| `tests/test_c04_simulation.py` | 22.245 | 16.708 | 13.470 | 16.708 | 22.245 | 1 | 6 |
| `tests/test_c05_harness.py` | 26.741 | 62.897 | 64.731 | 62.897 | 64.731 | 2 | 6 |
| `tests/test_c05_packet.py` | 27.496 | 18.798 | 21.255 | 21.255 | 27.496 | 4 | 6 |
| `tests/test_c05_policy.py` | 26.328 | 17.831 | 14.689 | 17.831 | 26.328 | 1 | 4 |
| `tests/test_c05_recommendation.py` | 13.437 | 31.724 | 32.035 | 31.724 | 32.035 | 2 | 5 |
| `tests/test_c06_harness.py` | 1.413 | 3.311 | 3.392 | 3.311 | 3.392 | 2 | 4 |
| `tests/test_c06_human.py` | 34.253 | 65.279 | 35.806 | 35.806 | 65.279 | 5 | 6 |
| `tests/test_c06_policy.py` | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1 | 4 |
| `tests/test_c06_store.py` | 63.651 | 42.609 | 47.428 | 47.428 | 63.651 | 4 | 5 |
| `tests/test_c07_harness.py` | 130.383 | 242.578 | 132.577 | 132.577 | 242.578 | 5 | 6 |
| `tests/test_c07_policy.py` | 303.579 | 305.650 | 150.216 | 303.579 | 305.650 | 6 | 6 |
| `tests/test_c07_recommendation.py` | 71.597 | 166.506 | 162.077 | 162.077 | 166.506 | 3 | 5 |
| `tests/test_c07_replay.py` | 212.777 | 145.247 | 157.283 | 157.283 | 212.777 | 4 | 5 |
| `tests/test_c08_context.py` | 4.011 | 2.757 | 2.903 | 2.903 | 4.011 | 4 | 5 |
| `tests/test_c08_explanation.py` | 38.616 | 74.500 | 40.154 | 40.154 | 74.500 | 5 | 5 |
| `tests/test_c08_harness.py` | 6.128 | 11.840 | 6.551 | 6.551 | 11.840 | 5 | 6 |
| `tests/test_c08_prompt.py` | 0.001 | 0.000 | 0.000 | 0.000 | 0.001 | 1 | 4 |
| `tests/test_c08_provider.py` | 1.770 | 1.180 | 1.380 | 1.380 | 1.770 | 4 | 6 |
| `tests/test_c08_template.py` | 4.387 | 9.497 | 9.342 | 9.342 | 9.497 | 3 | 5 |
| `tests/test_c08_validation.py` | 49.086 | 114.707 | 112.157 | 112.157 | 114.707 | 3 | 5 |
| `tests/test_c09_ci_gate.py` | 5.144 | 5.203 | 5.350 | 5.203 | 5.350 | 0 | 5 |
| `tests/test_capacity_scenario.py` | 21.484 | 33.628 | 31.304 | 31.304 | 33.628 | 3 | 6 |
| `tests/test_ci_change_classifier.py` | 0.330 | 0.471 | 0.351 | 0.351 | 0.471 | 5 | 6 |
| `tests/test_ci_publication_gate.py` | 0.848 | 1.101 | 1.128 | 1.101 | 1.128 | 2 | 4 |
| `tests/test_ci_test_sharding.py` | 45.723 | 47.403 | 24.738 | 45.723 | 47.403 | 6 | 6 |
| `tests/test_config.py` | 0.003 | 0.003 | 0.003 | 0.003 | 0.003 | 1 | 5 |
| `tests/test_data.py` | 0.538 | 0.527 | 0.444 | 0.527 | 0.538 | 1 | 5 |
| `tests/test_data_workflow.py` | 8.155 | 13.169 | 9.467 | 9.467 | 13.169 | 5 | 6 |
| `tests/test_db.py` | 0.048 | 0.080 | 0.071 | 0.071 | 0.080 | 3 | 6 |
| `tests/test_decision_context.py` | 0.897 | 0.896 | 0.956 | 0.897 | 0.956 | 0 | 6 |
| `tests/test_decision_contracts.py` | 0.124 | 0.228 | 0.130 | 0.130 | 0.228 | 5 | 4 |
| `tests/test_decision_evidence.py` | 2.102 | 2.120 | 1.076 | 2.102 | 2.120 | 6 | 5 |
| `tests/test_decision_serialization.py` | 0.041 | 0.028 | 0.034 | 0.034 | 0.041 | 4 | 5 |
| `tests/test_decision_snapshot.py` | 0.102 | 0.068 | 0.085 | 0.085 | 0.102 | 4 | 4 |
| `tests/test_decision_temporal.py` | 1.731 | 3.351 | 1.819 | 1.819 | 3.351 | 5 | 5 |
| `tests/test_generation.py` | 2.085 | 1.937 | 1.657 | 1.937 | 2.085 | 1 | 6 |
| `tests/test_hgt_serialization.py` | 2.858 | 5.353 | 4.650 | 4.650 | 5.353 | 3 | 6 |
| `tests/test_investigation_case_binding.py` | 41.577 | 28.557 | 31.310 | 31.310 | 41.577 | 4 | 5 |
| `tests/test_investigation_contracts.py` | 9.522 | 9.581 | 9.962 | 9.581 | 9.962 | 0 | 4 |
| `tests/test_investigation_evidence_navigation.py` | 86.739 | 87.463 | 42.194 | 86.739 | 87.463 | 6 | 6 |
| `tests/test_investigation_evidence_queries.py` | 30.778 | 72.483 | 70.781 | 70.781 | 72.483 | 3 | 5 |
| `tests/test_investigation_findings.py` | 1047.130 | 1056.117 | 1118.079 | 1056.117 | 1118.079 | 0 | 3 |
| `tests/test_investigation_human.py` | 418.256 | 988.390 | 1009.817 | 988.390 | 1009.817 | 2 | 4 |
| `tests/test_investigation_human_store.py` | 754.561 | 1825.750 | 1784.313 | 1784.313 | 1825.750 | 3 | 1 |
| `tests/test_investigation_planning.py` | 440.169 | 296.938 | 324.618 | 324.618 | 440.169 | 4 | 5 |
| `tests/test_investigation_replay.py` | 3082.523 | 2040.544 | 1658.888 | 2040.544 | 3082.523 | 1 | 0 |
| `tests/test_investigation_summary.py` | 1624.916 | 1633.554 | 769.713 | 1624.916 | 1633.554 | 6 | 2 |
| `tests/test_investigation_summary_provider.py` | 280.209 | 530.744 | 282.198 | 282.198 | 530.744 | 5 | 6 |
| `tests/test_models.py` | 0.441 | 0.384 | 0.367 | 0.384 | 0.441 | 4 | 5 |
| `tests/test_scenario_interventions.py` | 25.929 | 26.132 | 26.950 | 26.132 | 26.950 | 0 | 5 |
| `tests/test_scenarios.py` | 0.817 | 1.417 | 1.405 | 1.405 | 1.417 | 3 | 4 |
| `tests/test_w04_source_evolution.py` | 7.094 | 7.339 | 4.665 | 7.094 | 7.339 | 6 | 4 |
| `tests/test_worker.py` | 0.003 | 0.003 | 0.002 | 0.003 | 0.003 | 1 | 4 |

## Actual measured LPT structure

Active plan schema: `w04-devctrl03-non-integration-plan-v1`.
Plan self-seal: `06a0acc265d70ffb1d22ceb196bd72436b94ea960ba767a595f3467fb376d2f4`.
This exact plan was produced independently locally and by native Static/Plan.

Seven shards; marker `not integration`; file atomic; descending exact
milliseconds then path; shard tie-break lowest current load then lowest ID.
Fail-fast remains false and max-parallel remains 7. Missing/extra/unmodeled
files or any addition/removal/rename from the exact current node collection
fail closed. The original C08 two-file authorized-addition and entry no-loss
guards are preserved.

| Shard | Estimated seconds | Files | Nodes | Singleton file |
|---|---:|---:|---:|---|
| 0 | 2040.544 | 1 | 167 | `tests/test_investigation_replay.py` |
| 1 | 1784.313 | 1 | 111 | `tests/test_investigation_human_store.py` |
| 2 | 1624.916 | 1 | 128 | `tests/test_investigation_summary.py` |
| 3 | 1056.117 | 1 | 188 | `tests/test_investigation_findings.py` |
| 4 | 1046.586 | 16 | 842 | See complete assignment table above |
| 5 | 1046.586 | 24 | 687 | See complete assignment table above |
| 6 | 1046.603 | 19 | 874 | See complete assignment table above |

Legacy base/bootstrap fields are removed from the active plan. It binds
`weights_sha256`, `measured_weights_sha256`,
`measured_file_weights_sha256` and `measured_total_weight_milliseconds`.
The unmodified shard runner, outcome recorder and aggregate verifier consume
the new contract through `planner.validate_plan`; no semantic weakening or
eighth implementation path was needed.

## Historical shadow simulation

Simulation replays the proposed file assignments against every source run's
exact per-file testcase-duration sums. Current maxima are the source runs'
actual JUnit suite times; proposed maxima are the required modeled file sums.
Suite/setup overhead and changed runner contention are not predicted.

| Source | Current maximum pytest seconds | Proposed maximum seconds | Reduction seconds | Result |
|---|---:|---:|---:|---|
| #129 | 3143.457 | 3082.523 | 60.934 | PASS / no regression |
| #132 | 2235.256 | 2040.544 | 194.712 | PASS / no regression |
| #133 | 2181.682 | 1784.313 | 397.369 | PASS / no regression |

## Bounded timeout resilience

Only `.github/workflows/ci.yml` non-integration timeout changes 55 -> 65 minutes.
No other timeout, action pin, job, step, topology, transport name, service or
dependency changed. Both entry and current workflow trees contain only ci.yml.

Worst observed file 3082.523s + maximum observed job overhead 46.440s =
3128.963s isolated hot-file floor estimate.

- 55m = 3300s: 171.037s remaining (~5.2% of that ceiling).
- 65m = 3900s: 771.037s remaining (~24.6% over the observed floor).

The ceiling change does not speed a successful run; it adds bounded failure
headroom while preserving file atomicity. The observed Stage-A longest job
1841s leaves 1459s before 55m and 2059s before 65m. All seven jobs satisfy the
strict <55m acceptance criterion.

## Stage-A native exact-SHA proof

Commit: `3f633fcd993b4f188ab01f04356670737524b5ad`.
Parent: `a18e7f0733079ecc9aebdd94458625011e2f93f9`.
Subject: `ci(w04): apply measured shard weights`.
Exactly one feature-branch normal commit and one normal push; exactly seven paths.

Native run: [#134 / 38352852439 / SUCCESS](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38352852439).
Actual classifier: I / FULL_EXACT_SHA; exact before/after boundary and seven
authorized changed paths. Test paths select I under the unchanged classifier.
All 15 required full-route jobs succeeded: Classify, Static/Plan, Integration/Data,
seven shards, Aggregate, Quality, Compose, W03 and Verification.
Publication proof was SKIPPED according to that route. Run attempt = 1.

Ruff PASS; strict mypy PASS for 175 source files; dependency lock remains frozen.
Current collection 2997 nodes / 63 files / unchanged digest; 2994 passed /
3 accepted skipped / 0 failed, error, xfail or xpass. Entry no-loss, exact union
and exact once PASS. Integration 70 passed / all other outcomes 0.
W03 native F01-F10: 38 selectors / 85 cases / PASS at the exact Stage-A SHA.

| Shard | Job ID | Selected | Passed | Skipped | Exact pytest seconds | Actual job seconds |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 115149203099 | 167 | 167 | 0 | 1771.625 | 1806 |
| 1 | 115149203206 | 111 | 108 | 3 | 1805.821 | 1841 |
| 2 | 115149203066 | 128 | 128 | 0 | 1014.785 | 1049 |
| 3 | 115149203196 | 188 | 188 | 0 | 837.641 | 873 |
| 4 | 115149203242 | 842 | 842 | 0 | 1061.719 | 1094 |
| 5 | 115149203173 | 687 | 687 | 0 | 704.773 | 742 |
| 6 | 115149203165 | 874 | 874 | 0 | 700.520 | 735 |

Pytest seconds above come from original per-shard JUnit testsuite `time`
attributes, preserving three decimals. Job seconds come from the native API
`completed_at - started_at` timestamps, including setup and teardown.
The accepted skips are the three existing Linux junction-surface cases:
`test_j40_j45_windows_junction_surfaces_fail_closed[case]`, `[locks]`, `[root]`
in `tests/test_investigation_human_store.py`; skip digest remains
`1524192888846ac2a7b1908212650648a38816aa72d458add70868c24d08a767`.

- Aggregate JUnit SHA-256: `88bbc3b23a5f968a1acbbdf6b07a5682cd71bcb50fd3c7cda3f9a3e85faca0f9`.
- Aggregate receipt self-seal: `9eaff4a9f55adf332866c0504ea5404240d9e1f1cb347cd6f37f288573917c68`.
- Real-native metadata raw SHA-256: `2a6c4640a23b3f9dd26192eb08528482ccd30a240d253b61bbb200b37673d3bd`.

| Original artifact | ID | ZIP SHA-256 |
|---|---:|---|
| integration-data | 11791572768 | `66fc6b12643646db013b2b4ab8e923178348c65daf33a180a86c8ac4f8b44492` |
| nonint-aggregate | 11792667613 | `58f05a676fc5485f68afd50cbd82895658cdaad4d0024cbd0ebd9403a0d54cd8` |
| plan | 11791821692 | `79edbbfcb2a260175cfc0979292e4b4ac73513b0905f83ddf97d5bd4b5b54ec6` |
| shard-0 | 11792158111 | `9ea30ed77f86b31876750b45745c7bf4e8aca35db9331f37686597fb966cbd0d` |
| shard-1 | 11792408620 | `3757c7edb7d662f6cd0e23b22ba6ac77a90e9516995959430d383f3195cb4d6d` |
| shard-2 | 11791739605 | `eec2a2bc8b2765fb70fc36887aa5949962f7b4a011f4c0a0d5ce3eaf397962c7` |
| shard-3 | 11792346053 | `c1820df84ee68b20e150fc5da3d15e1522dd1ca42938be93596d901a28060251` |
| shard-4 | 11792316377 | `c179a740ca420a689d45e2d4461a92dd0134ea15751164ba55f1abc7f07f455b` |
| shard-5 | 11792390385 | `c2df0503e6222515fad91e1c8ab23777334c259c9a256546f0edced10270f5af` |
| shard-6 | 11792475197 | `f3cd901ebb1e3e6e34c83350e7072886b7b5287737dcc2657bf7a2f839dde70f` |

All ten original ZIPs were downloaded, their native digests matched, and only
the expected plan/receipt/JUnit members were read. Run/head binding, per-shard
receipts and aggregate coverage were verified. Nothing was regenerated as
source evidence or substituted for a native artifact.

## C08 harness compatibility and local proof

Clarification-01 adds only `tests/test_investigation_replay.py` to Stage-A scope.
Only existing R43, existing R46 and the strictly required new helper/constant
changed. All other existing C08 function ASTs, arguments and decorators are
identical; R01-R46 remain present; node additions/removals/renames = 0.

- R43 removes only `.github/workflows` from the generic C08-entry freeze tuple.
  Its dedicated DEVCTRL-03 guard reads a18e7f0 entry Git bytes, requires both
  workflow trees contain exactly ci.yml, uniquely locates the non-integration
  job and timeout, and requires current HEAD bytes equal only the derived
  55 -> 65 delta. Every other frozen path and lifecycle/source assertion remains.
- Seventeen read-only negative controls reject other timeout/action changes,
  shard count, fail-fast/max-parallel changes, job/step changes, extra/deleted/
  renamed workflow paths, extra whitespace, duplicate job and duplicate timeout.
- R46 real-native proof accepts exactly the new active planner schema and
  measured evidence self-seal/63-file model; no arbitrary old+new schema acceptance.
  Exact native metadata, FULL_EXACT_SHA, required jobs, original ZIP integrity,
  current collection, entry no-loss, aggregate reconstruction, all receipt and
  outcome checks, integration 70 and W03 controls are preserved.

Committed-HEAD local proof used an unpushed full-history disposable clone at
`894459e27147afd7315895b45a5a0d68804fade8`. Its seven Git blobs matched the actual
Stage-A commit exactly. The clone was deleted after its proof logs/JUnit were
retained; it is not a feature-branch prep/repair commit.

Local proof:

- Clarification focused combination: 243 passed, 334.465s wall time.
- Complete C08 replay: 167 passed, 1217.31s pytest / 1217.980s wall time.
- Actual committed feature-head R43/R46 controls: 13 passed, 13.63s pytest.
- Real-native R46 after #134 terminal SUCCESS: 1 passed, pytest exit 0,
  18.031s wall time, no skip/error/failure.
- Ruff PASS; strict mypy 175 files PASS; git diff --check PASS.
- One local precommit CI assertion initially compared the historical bootstrap
  to #126, before that file existed. It was corrected to the DEVCTRL-03 entry;
  the complete candidate proof passed. No native CI rerun or repair occurred.
- An attempted primary CRLF -> LF normalization was rejected by automatic
  approval review before execution. Primary raw CRLF remained intact; the
  disposable clone used the original Git LF blob plus the sole authorized
  timeout edit. Filtered Git blobs proved identical.
- A console-encoding error occurred while displaying the successful real-native
  R46 log after pytest returned 0. Saved exit JSON and JUnit independently
  confirmed 1/1 PASS; no test rerun or assertion weakening occurred.

Focused JUnit SHA-256: `fc3cd871fefd47215f6839890035bda42eda48f893900b1836f82be06f8bcf54`.
Full C08 JUnit SHA-256: `4b1f6a590ac2f97b53a1fe3e2482d77778cafcbec1bb3b1e62807b5ec98fb070`.
Real-native R46 JUnit SHA-256: `09aff6555b455f36acdd3fda12f41d1b7f1a704834da2ee90d1f6fb1aa7444be`.

## Protected product and governance boundaries

All seven Stage-A paths match the tested candidate. All other 473 previously
tracked paths were checked unchanged. Source, manifest, C01-C08 checkpoint docs,
historical weights, dependencies, migrations/schema, data/evaluation/HGT,
W03 semantics and product runtime remain unchanged.

C08 source freeze remains `1fa7b505980c1efc1b3725cd57a9732e254bccdf`; its runtime
blobs remain `273d288cf4b0e55b646cd2e6751f0259e463a5ff` and
`4fa391cf751377305315b7de8303ce94e6eb6c6e`. Stage-B product proof #129 remains
UNCHANGED / SUCCESS. The CI-harness exception does not reopen C08.

## Limitations and final review boundary

- Three-run sample only; this is a bounded measured scheduling model.
- GitHub-hosted runner variance remains; successful timings do not establish
  a guaranteed future bound or isolate a causal speedup from scheduling alone.
- The file-atomic hot-file floor remains.
- Timeout is a resilience ceiling, not a performance optimization.
- No node-level split was performed.
- Future C09 growth requires new measurement and explicit authorization,
  not guessed weights or reuse of an obsolete bootstrap.
- Native artifacts have bounded GitHub retention; their IDs and all relevant
  seals are recorded here for timely independent verification.

Publication candidate state: Stage A COMPLETE / full native CI SUCCESS /
resilience PASS / real-native R46 PASS; this report's own native CI PENDING.
After its own terminal native SUCCESS: W04_DEVCTRL_03_REVIEW_READY.
GPT independent review PENDING; Human acceptance PENDING;
DEVCTRL-03 closeout NOT AUTHORIZED; C09 NOT AUTHORIZED.
PR #7 OPEN / DRAFT / UNMERGED. PR merge / main write NOT AUTHORIZED.
Stop for independent ChatGPT review.
