# FlowLens W03-C03 Context Lock

```text
checkpoint_id: W03-C03
context_lock_status: LOCKED
human_authorization: APPROVED
locked_at: 2026-09-25 Asia/Shanghai
```

## 1. Entry state

The required read-only preflight completed before repository mutation.

| Check | Verified result |
|---|---|
| Repository | `Ray-Yan-Rui-14793817/flowlens-industrial-ai` |
| Branch | `feat/w03-ai-decision-loop` |
| Local HEAD | `2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978` |
| Tracking HEAD | `2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978` |
| Direct remote W03 HEAD | `2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978` |
| PR #6 HEAD | `2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978` |
| `origin/main` / direct remote main | `9d18ddde9fe933952a2661ee1419f13c8577605d` |
| Tracking divergence | `0 ahead / 0 behind` |
| Working tree at entry | clean |
| Merge / rebase / cherry-pick | none |
| PR #6 | `OPEN / DRAFT / NOT MERGED`; base `main`; no conflicts; auto-merge not configured |
| C02 closeout | `28173582661bc4bba5f254928ab8a9bbb5de63a0` |
| DEVCTRL-01 closeout | `2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978` |
| DEVCTRL Run #48 | `36104873132 / #48 / SUCCESS`; exact closeout head; Publication and Verification passed; Quality and Compose skipped |

The historical `GITHUB SYNCHRONIZATION PENDING` wording in the closeout commit is
resolved by Run #48 and the synchronized live refs. It is not baseline drift.

## 2. Human authorization and V3 inputs

Actual Product Owner message:

```text
W03-C03 HUMAN AUTHORIZATION: APPROVED
```

Package verification executed the supplied verifier and returned
`PACKAGE VERIFY PASS`.

| Input | SHA-256 |
|---|---|
| `FlowLens_W03_C03_GPT_Authorization_Package_V3.zip` | `f7c652f39a0a15bd485f9b537c80dda8e481d981c9060c2257a275c3c13b9c06` |
| `FlowLens_W03_C03_GPT_COMPLETE_MASTER_V3.md` | `b5c38b0e9576388fa336dc16589c8bd004c326d450f1103287218f4dd89d720d` |
| `W03_C03_CODEX_EXECUTION_PROMPT_V3.md` | `65e660aa3e018f2278c528ddf394e42d7d832e1a2319f2c4307618ca794a9a5e` |

Older C03/CI-update packages are superseded and are not execution inputs.

## 3. Governing repository materials

| Material | SHA-256 |
|---|---|
| `AGENTS.md` | `ceb3c166e2d4d2782688d668121bfb1de6ec69bd9d3513cb4d63bc4d9f165c76` |
| `LOOP.md` | `1850365277f65bbba1637381c37474a853e07b1c1510b6ce30293395cd949e99` |
| `docs/CURRENT_STATE.md` | `4c21ec883488b1d479e2b639b75f91ee38ec8b3a5c0994632edd7030d3c4d310` |
| `docs/sprints/W03_ai_decision_loop.md` | `aed067e6532effe434ab0338fdc2ec9a8455dca761385f78bcce51298617410a` |
| `docs/w03/AI_LOOP_CONSTITUTION.md` | `48702680c6403e3cabfb7e774db72f88cdaabb165899d78d1893cf0373a0ceed` |
| `docs/w03/SEMANTIC_TRUST_CONTRACT.md` | `184d4bbd1ca26f37887525bef0417295da4ddeff6eb7db3b25e0ddabb5fc646d` |
| `docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md` | `cb4a0de4d0fe2ef9231cf6e579c1a557129ab097572e29a0addb43172a52dd8a` |
| `docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md` | `6eaec8e2a918665ac6b21b22a83e6133bd2e827288433d451e0b8beb4381c9b4` |
| `docs/w03/LOOP_EXECUTION_STATE_MACHINE.md` | `aa291f3d3a8c273a5c8175b9ae5fe58471bd3cba8662c1253de499cd3e5f860d` |
| `docs/w03/FAILURE_AND_DEGRADATION_POLICY.md` | `164afc436c4f00104690d02a4b7b7cea223e7ebe7b74d4a3a164159ee22223ad` |
| `docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md` | `a02b5c9146780558be304f081bf231c46d9d817ef16df80a44f6f90c16debb33` |

## 4. Closed upstream checkpoint materials

### C01

| Material | SHA-256 |
|---|---|
| `W03_C01_AUTHORIZATION_CONTRACT.md` | `59ae4bfb60c4f8a0136b7dc3256f0dbfe30283d83f9013a1fb600b35273974fc` |
| `W03_C01_CONTEXT_LOCK.md` | `e5169a04f3adada650e585f2759f6fd032428e8b937dda6661003e9b17c0129c` |
| `W03_C01_CORE_ARTIFACT_CONTRACTS.md` | `44e239781eb9c0886f65290ebcfd6aa4b32b0efb2d370a5ed876bef9e56e801d` |
| `W03_C01_GPT_REVIEW_CHECKLIST.md` | `b7a809ecb597f14757a8b8d2f94f8afb56eabdf9ba3497797824eae9f48faa2f` |
| `W03_C01_HARNESS_ACCEPTANCE_SPEC.md` | `9bbc0031030e7293b3c36cf59c43f10d912740ee39e5e6fa29854b5472955ef9` |
| `W03_C01_HUMAN_AUTHORIZATION.md` | `2f381833660e4b23aabf917d8f7457c82e96d0f09c223eb8938928f8c0a6a347` |
| `W03_C01_IDENTITY_PROVENANCE_SERIALIZATION.md` | `98a05a823f745fff2a83f85fb230cbf1e7518464d9b918cbd7c3b635db6976c3` |
| `W03_C01_GPT_INDEPENDENT_REREVIEW_R2.md` | `dd441737cf7e34009254e7a3c7faf8af7ddf426f0061fea5e1818098087b7af0` |
| `W03_C01_C1_FINAL_CLOSEOUT.md` | `dd36c0035402bcbc7f903f687376290560ffed9f19e34b9b7055eba521856249` |

### C02

| Material | SHA-256 |
|---|---|
| `W03_C02_ARCHITECTURE_SEMANTIC_FREEZE.md` | `0da0b928a23943c8308e06c1864b893087338ae43ed4e058755a53b78d7f4973` |
| `W03_C02_AUTHORIZATION_CONTRACT.md` | `ef4578c0e0e4e275b45b549eba242c5a52af571c3c270e7b5c75869f0ccf6a99` |
| `W03_C02_CONTEXT_LOCK.md` | `a0800c591bdf86b94f5523556b4e915ac84ffc479bf751aafc9626578abd93d9` |
| `W03_C02_DECISION_CONTEXT_DERIVATION_CONTRACT.md` | `0f3454a4ae0a09ce74a36cd6abfb993de7ca48896a92813757d7ceba973b9b58` |
| `W03_C02_EVIDENCE_TRUST_FRESHNESS_MATRIX.md` | `6d56cf2ba18fe077aa2802142f745f99b5e1aee5b22a215382c31d3bda5fa3df` |
| `W03_C02_GPT_FINAL_ZERO_AMBIGUITY_AUDIT.md` | `2ff8393c3fa3a8d8ee1cb760c4085bc8e61f26b907e7b1a69d1c578fd26a89fa` |
| `W03_C02_GPT_REVIEW_CHECKLIST.md` | `0b4e2f673e3da403641527322fe43b67ee9cdfd56dc54f187fb075628cc5ffc8` |
| `W03_C02_HARNESS_ACCEPTANCE_SPEC.md` | `311f25a70c023b7864e45ddfbeeee8272640aa07afcfcfef51feba5fb8f40834` |
| `W03_C02_HUMAN_AUTHORIZATION.md` | `8663c4e52af417b6dc1e592fece7fd5e1061489eede6ed8c48b89f9dcc37ad89` |
| `W03_C02_POSTGRES_SNAPSHOT_ISOLATION_CONTRACT.md` | `23d8a62af4fb9d434ddf71de0d142ea2853e422d8d82f13834e92c1a3e28632b` |
| `W03_C02_SOURCE_FIELD_SNAPSHOT_MATRIX.md` | `4fb47ac8ba5c0734f0b01e4736970141ee8016f8bf1a03532dc476c36480c0b4` |
| `W03_C02_GPT_INDEPENDENT_REREVIEW_R2.md` | `87e02a259eb0f0c9ffa58aab73d706db4f21dd4c914bb88cfd130768d7f5add9` |
| `W03_C02_C1_FINAL_CLOSEOUT.md` | `be01babfaeec82de206178d148ec5db4db9f34b05e1c47101e67b4e7b9bb1a65` |

### DEVCTRL-01

| Material | SHA-256 |
|---|---|
| `W03_DEVCTRL_01_AUTHORIZATION_CONTRACT.md` | `6e968ba528fcaafa78c0eb96cb9c2ef495342b272e5df8619b63f4aed06fbe8a` |
| `W03_DEVCTRL_01_C03_TRANSITION_NOTICE.md` | `427feb973772ae030095f3c11ce57184836ebf4b7b87c45b816cbb67731eaa34` |
| `W03_DEVCTRL_01_CHANGE_CLASS_CONTRACT.md` | `12c6b9aee299fe1ba0f3c18e7cde235169cb675818d95bfb7e8e144f578ab1a4` |
| `W03_DEVCTRL_01_CI_ARCHITECTURE_CONTRACT.md` | `449c3e52bf8a358cc17230dc78200f00d6b2f6828e68634b457788eecf13c28c` |
| `W03_DEVCTRL_01_CONTEXT_LOCK.md` | `fc0b6a08449588a9b1e9429bb24aa5bc98bf5be272c31f2843e484f4fa62a4f7` |
| `W03_DEVCTRL_01_GPT_REVIEW_CHECKLIST.md` | `47effbba8b7b8f3f4d883a6fc5892193a45240b630a3f9fdabf5b8480d83c090` |
| `W03_DEVCTRL_01_HARNESS_ACCEPTANCE_SPEC.md` | `04c853ddaf82dac224a08f125946b85b05109509a7062d045cb797935621cb78` |
| `W03_DEVCTRL_01_HISTORICAL_REPLAY_MATRIX.md` | `6b26370054ab051dd7d98e162f31ef3cf512cc0bcff282ac9d5a09e58dc94aff` |
| `W03_DEVCTRL_01_HUMAN_AUTHORIZATION.md` | `7488fa25646d55f417cd6c7abc78a2710afe5eb72d60378192790936a55cad74` |
| `W03_DEVCTRL_01_NEGATIVE_CLASSIFIER_TEST_MATRIX.md` | `36c2f943281abb16ed9b8d413b03ee40ea1f620f0308b164098b66b788fb67a6` |
| `W03_DEVCTRL_01_GPT_INDEPENDENT_REVIEW_R1.md` | `e73bab3fe49f3844e2d5aaba84cfa5a00b5f2735c09937df84311a7b48c9b4fa` |
| `W03_DEVCTRL_01_C1_FINAL_CLOSEOUT.md` | `354cceef8f8fad3d609f9e4d5f2ca8fc6a623557e7ae9e2927b90080c42ca30c` |

## 5. Frozen source and control-plane hashes

| Material | SHA-256 |
|---|---|
| `src/flowlens/decision/__init__.py` | `2da24c3105522a2cecf292200282bfbcd4f215c813948d265612282877fe58de` |
| `src/flowlens/decision/context.py` | `385fe393e41e6c03d21028ed89a905f51dc432f386f839ee67ab4cbcac98a100` |
| `src/flowlens/decision/contracts.py` | `6179428829f2c23217e76de71a6a3c8769af3fe6253b6fb7d624e80107054134` |
| `src/flowlens/decision/derivations.py` | `a285d3975c90ad63e9cdb5835de55f6829104e052b39e9899115eb936b92c328` |
| `src/flowlens/decision/enums.py` | `0f7ea7e059f79df84ca3f312bd354829a00794f602f302584c4f7abdc66c35d6` |
| `src/flowlens/decision/evidence.py` | `1322b89352f4a792c5fac5d0a2a473776abc85d16d6413246ff2ef287ef844ba` |
| `src/flowlens/decision/primitives.py` | `58eb6bb0f371ee02343e4bbd8ca5d664eebe6d28322552f246cf7455d99ff2ab` |
| `src/flowlens/decision/serialization.py` | `508194080ba1537931365fb68f17b6c49f2ae58549c794a683e3fa582bc4cfd3` |
| `src/flowlens/decision/snapshot.py` | `d0aadff5c4305b6f6d0d56e8714ca147f24fafcac700477e5e0f73b37398cdb1` |
| `src/flowlens/decision/temporal.py` | `d043bc46ecfbc9910b63939ec90fe7901a81e8f70fcb058546929fcfc2c1379f` |
| `src/flowlens/decision/trust.py` | `70930d787ca52ceb56e5fe2c8aa825f122ee35f2bcee68c148f8229a7e016347` |
| `src/flowlens/db/decision_snapshot.py` | `d0a4cdd36fc5cf317bc61dd758dbc54734932618c3ba54bc7f01a73f87f2b147` |
| `.github/workflows/ci.yml` | `9dd1bebc7b6587b3890e3f6416e29a73dae30dc84694ad113b736719433bb9c9` |
| `scripts/ci/classify_change.py` | `71c4c4280f69a67e55595a6a61a5e834833c93340fc8f43fe58b7880f8dfc743` |
| `scripts/ci/verify_publication.py` | `be0e9fae4eb64745f0e7ac70abb8b6247bbc0c377e93ea35f628b85623dfe20a` |

All C01/C02 decision modules and the sole C02 database adapter above are frozen.
Only an additive, DB-free export change to `decision/__init__.py` is authorized.

## 6. Published C03 V3 contracts/specifications

The V3 `repo_docs/` and `specs/` artifacts were published under
`docs/w03/checkpoints/c03/`. They are content-identical to the verified package
except for Markdown trailing-whitespace normalization and completion of the
Human Authorization template with the actual Product Owner message.

| Material | SHA-256 |
|---|---|
| `W03_C03_ARCHITECTURE_AND_COMPATIBILITY.md` | `fafbb7bc3cf8710c10f0eef71df61daf219101aa8789af9a1c15e1bf1ee371b8` |
| `W03_C03_AUTHORIZATION_CONTRACT.md` | `bbd0d9ec34427c67de4e8769b247619f739fe4167ae3ba35656eda7ede0cbdd9` |
| `W03_C03_BASELINE_AND_SOURCES.md` | `34c470b82d62db159280d36bd6eef4f7c51c9accbc0d3747f3f518f65ac6dd27` |
| `W03_C03_DEVCTRL_INTEGRATION_CONTRACT.md` | `6e5935fb29d8162487b77cda34c41f6a18fae07ad99e3276393deddf60522aff` |
| `W03_C03_DIAGNOSIS_CONTRACT.md` | `0e8932dd3f6757398e3b5b50e491465348ea774dbffb1870400766745274d59b` |
| `W03_C03_GPT_FINAL_ZERO_AMBIGUITY_AUDIT.md` | `628921524de58941b63af59ae383bf1529a91a85a2e13145e6b4ccfe38bbdc62` |
| `W03_C03_GPT_REVIEW_CHECKLIST.md` | `1587396edf7ea8f9816deaf5515ebcba9dc0bd973dd1a153b6f0cc0dfa26cbd0` |
| `W03_C03_HARNESS_ACCEPTANCE_SPEC.md` | `bfc853c56ed419601ba8b435e328d65947c3eac859d6d0f3daddbfcefd18f71a` |
| `W03_C03_HUMAN_AUTHORIZATION.md` | `07a73fa7eb122844fe6f74a190461c4cf2c092bb39cbcb13f9195a7605338554` |
| `W03_C03_IDENTITY_AND_REPLAY.md` | `718023e3c35b2af0c73c77eca038f51ee6e2a6c600bfa423a08702f37f1644c2` |
| `W03_C03_INPUT_AND_EVIDENCE_CONTRACT.md` | `867a2f7fb0c835e09243ec103b8821138910ab5a8d5ff21149cb3ba590a8a239` |
| `W03_C03_SIGNAL_RULEBOOK.md` | `9a3bc4dbaf5197232baa2b03692908a0b031fae7c1029150ebc6ae7940313a21` |
| `W03_C03_SUPERSEDED_PACKAGE_NOTICE.md` | `d7adddfc1cf492fe2d5408ef20b3d22653e0ad58d1fcad85baff2daba0a701e4` |
| `specs/acceptance_vectors.json` | `04c62341a7e709045921a810c5ad3f1065f423e8a295fa7cd328f1b1b6ef3380` |
| `specs/authorized_paths.json` | `35d24e9fd4310f2b3a0067657a5961bb5ff65fb439d0956942f7a60e76b8af4f` |
| `specs/signal_policy.json` | `52673752334d7e6705f7c0a4251bcf4eb5a0245987a6fe0b1e39e97362e8728a` |

This Context Lock intentionally does not self-hash.

## 7. Golden development dataset reproduction

The deterministic in-memory generator was run with the frozen configuration:

| Field | Reproduced value |
|---|---|
| profile | `test` |
| seed | `20260824` |
| period_start | `2026-01-01` |
| period_end | `2026-03-31` |
| generator_version | `0.1.0-c03` |
| dataset_version_id | `dsv_9c21c51c1ed71921e43f30da7afab559` |
| content_hash | `bb08255c0bed5836d2a985b85bded5dc0fe5386af16939c891d520bed10d9416` |
| row_count_total | `2199` |

Result: `PASS`; the reproduced identity exactly matches the frozen C02 golden
development identity.

## 8. Runtime permissions and source boundary

```text
C03 runtime inputs: EvidenceBundle + DecisionContext only
C03 DB access after context: NONE
C03 filesystem: NONE
C03 network: NONE
C03 HGT/scenario label: NONE
C03 LLM/model: NONE
C03 operational write: NONE
C03 new runtime tool: NONE
```

Runtime implementation is limited to pure deterministic modules. It may not
import SQLAlchemy, `flowlens.db`, scenario/HGT modules, filesystem/network
clients, subprocess/shell, randomness or wall-clock `now()`.

## 9. Authorized and forbidden paths

The exhaustive implementation/report allowlist is the published
`specs/authorized_paths.json`.

Implementation-stage paths are limited to:

```text
docs/w03/checkpoints/c03/**
src/flowlens/decision/c03_policy.py
src/flowlens/decision/c03_validation.py
src/flowlens/decision/signals.py
src/flowlens/decision/diagnosis.py
src/flowlens/decision/__init__.py          # additive DB-free exports only
tests/test_c03_policy_contract.py
tests/test_c03_signals.py
tests/test_c03_diagnosis.py
tests/test_c03_harness.py
tests/integration/test_c03_decision_database.py
```

Later report-stage paths are limited to exactly:

```text
docs/w03/reports/W03_C03_R_DEVELOPMENT_ROUND_REPORT.md
docs/CURRENT_STATE.md
```

Frozen/forbidden paths include all C01/C02 runtime source/tests, the C02 DB
adapter, W2 source/schema/migrations/hash/scenario semantics, dependency files,
CI/workflow/scripts, Docker/Compose, API/worker, AGENTS.md, LOOP.md, skills and
the W03 Sprint specification.

## 10. Expected Context Delta

```text
C03 contracts/specs + this Context Lock
4 pure C03 runtime modules
optional additive DB-free decision exports
5 new C03 test files
later Round Report + CURRENT_STATE only

schema/migration: NONE
dependency: NONE
CI/control-plane code: NONE
new runtime tool: NONE
HGT runtime: NONE
operational mutation: NONE
C04+ capability: NONE
```

At lock time the actual repository delta contains only the authorized C03
checkpoint documents/specifications and this record. Therefore:

```text
actual_delta subset_of authorized_delta: PASS
context_lock_status: LOCKED
```

Runtime and test source writes are authorized only after this locked record.
