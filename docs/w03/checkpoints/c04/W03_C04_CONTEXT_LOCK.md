# W03-C04 Context Lock

```text
checkpoint_id = W03-C04
context_lock_status = LOCKED
locked_at = 2026-09-26 Asia/Shanghai

branch = feat/w03-ai-decision-loop
baseline_sha = 1c0f4de6f897d9e377fba63891773bb5970e74b7
tracking_sha = 1c0f4de6f897d9e377fba63891773bb5970e74b7
direct_remote_sha = 1c0f4de6f897d9e377fba63891773bb5970e74b7
main_sha = 9d18ddde9fe933952a2661ee1419f13c8577605d
pr_6 = OPEN / DRAFT / NOT MERGED
c03_closeout_sha = 1c0f4de6f897d9e377fba63891773bb5970e74b7
run_53 = 36220108789 / PASS / P / PUBLICATION_EXACT_SHA
```

## Authoritative material hashes before implementation

| Path | SHA-256 |
|---|---|
| `AGENTS.md` | `ceb3c166e2d4d2782688d668121bfb1de6ec69bd9d3513cb4d63bc4d9f165c76` |
| `LOOP.md` | `1850365277f65bbba1637381c37474a853e07b1c1510b6ce30293395cd949e99` |
| `docs/w03/AI_LOOP_CONSTITUTION.md` | `48702680c6403e3cabfb7e774db72f88cdaabb165899d78d1893cf0373a0ceed` |
| `docs/sprints/W03_ai_decision_loop.md` | `aed067e6532effe434ab0338fdc2ec9a8455dca761385f78bcce51298617410a` |
| `docs/w03/SEMANTIC_TRUST_CONTRACT.md` | `184d4bbd1ca26f37887525bef0417295da4ddeff6eb7db3b25e0ddabb5fc646d` |
| `docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md` | `cb4a0de4d0fe2ef9231cf6e579c1a557129ab097572e29a0addb43172a52dd8a` |
| `docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md` | `6eaec8e2a918665ac6b21b22a83e6133bd2e827288433d451e0b8beb4381c9b4` |
| `docs/w03/LOOP_EXECUTION_STATE_MACHINE.md` | `aa291f3d3a8c273a5c8175b9ae5fe58471bd3cba8662c1253de499cd3e5f860d` |
| `docs/w03/FAILURE_AND_DEGRADATION_POLICY.md` | `164afc436c4f00104690d02a4b7b7cea223e7ebe7b74d4a3a164159ee22223ad` |
| `docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md` | `a02b5c9146780558be304f081bf231c46d9d817ef16df80a44f6f90c16debb33` |
| standalone `W03_C04_CODEX_EXECUTION_TASK_V1.md` | `f225cb694c3428a42aef75872db044f7539b0b706a8cc00563c1bb7c11c430b4` |

Accepted checkpoint evidence includes C01, C02 and C03 authorization contracts, Context Locks,
harness specifications, review checklists, Human authorizations and final closeout reports. Their
authorization-contract hashes are respectively
`59ae4bfb60c4f8a0136b7dc3256f0dbfe30283d83f9013a1fb600b35273974fc`,
`ef4578c0e0e4e275b45b549eba242c5a52af571c3c270e7b5c75869f0ccf6a99`, and
`bbd0d9ec34427c67de4e8769b247619f739fe4167ae3ba35656eda7ede0cbdd9`.

## W2 pre-refactor source hashes

| Path | SHA-256 |
|---|---|
| `scenarios/__init__.py` | `75a9bf790f2639de22b595ef93b2d792f40773aee66dd9143f432827c34a9da9` |
| `scenarios/application.py` | `720173de2705aa61bc3b7aa239a5532110c0ec4473fa79bb0afe4d09f55e34dc` |
| `scenarios/transformer.py` | `6e3ce2abea4721c1470e785f436d7af6960d6b79b2d91ab55c866c137c7507f5` |
| `scenarios/supplier.py` | `f4adcaede53feb6accafd485a7e893dbb9c4e25d18308f4d7e09257bc030af0c` |
| `scenarios/quality.py` | `c925a56c58ac03543e99441e18c05febfc668978cc6776e258a8e4c43523894e` |
| `scenarios/capacity.py` | `19d13b895869c853379f04ee9e8fd975e479130c3a4d0f87a587113b51b0ee8b` |
| immutable `scenarios/config.py` | `2ec47cdcab56bc5d1439a37a5a29e2c0362bd98bfe2675234eeb726bef84a35c` |
| immutable `scenarios/ground_truth.py` | `6b6671d568b404506da094785e8bde461d54a3754b7884f9f9311f4ac4f0a01e` |

## Acceptance fixture and versions

```text
profile = TEST
seed = 20260824
period_start = 2026-01-01
period_end = 2026-03-31
generator_version = 0.1.0-c03
dataset_version = dsv_9c21c51c1ed71921e43f30da7afab559
dataset_hash = bb08255c0bed5836d2a985b85bded5dc0fe5386af16939c891d520bed10d9416
row_count_total = 2199

registry_version = w03-c04-registry-v1
adapter_version = w03-c04-scenario-adapter-v1
stress_scenario_version = w03-c04-stress-v1
measurement_schema_version = w03-c04-measurements-v1
```

Allowed runtime sources are canonical C02 artifacts, canonical C03 artifacts, the immutable
DecisionRun/StateSnapshot and an explicitly supplied in-memory GeneratedDataset. Forbidden
sources include database/persistence, files, network, models, subprocess, random, wall clock,
HGT and future facts.

Authorized and forbidden files are exactly those in `specs/authorized_paths.json` and the
authorization contract. The expected context delta is limited to C04 checkpoint documents,
status-only Sprint normalization, the three C04 decision modules, the smallest compatible W2
adapter/lazy-import refactor, and the four new C04 test modules.

## Human Authorization

The Product Owner explicitly stated `W03-C04 HUMAN AUTHORIZATION: APPROVED` and directed exact
execution of the standalone through `REVIEW_READY`, with main unchanged and PR #6 kept open,
draft and unmerged. No Human acceptance, closeout or C05 authorization was granted.
