# FlowLens Industrial AI — W03-C02 Context Lock

checkpoint_id: W03-C02
context_lock_status: LOCKED
locked_on: 2026-09-24
human_authorization: APPROVED — explicit Product Owner chat message, 2026-09-24

## Verified entry state

| Item | Verified value |
|---|---|
| Branch | `feat/w03-ai-decision-loop` |
| Local HEAD / tracking / direct remote / PR #6 head | `c626126a81fe07b5d1f670deaeaadc809f6bea55` |
| `origin/main` / direct remote main / PR #6 base | `9d18ddde9fe933952a2661ee1419f13c8577605d` |
| Working tree before C02 documents | clean; 0 ahead / 0 behind |
| Git operation in progress | none |
| PR #6 | open, draft, not merged; GitHub shows a disabled merge action and no enabled auto-merge action |
| C01 closeout CI | run #38, ID `35987268646`, success, C01 SHA |
| C02 implementation before lock | absent |

The ZIP manifest hashes matched all 17 enclosed payloads; the Master contained
all 18 ZIP artifacts (including the manifest). The separately attached execution
prompt SHA-256 matched the ZIP copy. `git fetch origin`, direct `git ls-remote`,
and GitHub PR/CI reads supplied the entry evidence.

## Golden development dataset

Generated in memory with the frozen W2 generator. `generated_at` is generation
provenance and is not a business `available_at` value.

| Field | Value |
|---|---|
| profile | `test` |
| seed | `20260824` |
| period_start | `2026-01-01` |
| period_end | `2026-03-31` |
| generator_version | `0.1.0-c03` |
| dataset_version_id | `dsv_9c21c51c1ed71921e43f30da7afab559` |
| content_hash | `bb08255c0bed5836d2a985b85bded5dc0fe5386af16939c891d520bed10d9416` |
| row_count_total | `2199` |

## Scenario development fixtures

These configurations and dataset hashes are development context. C02 runtime
receives only eligible operational facts from the business dataset; it never
receives scenario labels, protected ground truth, affected-entity answers, or
causal-chain answers. All windows use Asia/Shanghai and version `1.0.0`.

| Fixture | Seed | Window `[start, end)` | Parameters | Namespace | Business dataset version / hash |
|---|---:|---|---|---|---|
| Supplier degradation | 20260901 | `2026-01-15` to `2026-02-12` | supplier count 2; critical material count 5; late delta 0.25; delay 3–8 business days | `f85cade4cb57abec3a930b0e87ef25408f94b24a2b8e45cb44f50949c7a47b52` | `dsv_f85cade4cb57abec3a930b0e87ef2540` / `682dc4238ad146724068116b0e2ca93b291029670b537ecf9b7693e09a6ff3cb` |
| Quality deterioration | 2 | `2026-01-01` to `2026-03-31T23:59:59` | product count 2; center count 1; failure multiplier 2.2; rework delta 0.30; duration multiplier 1.2–1.5 | `fe333de5c5b8aa8d5b58fdfd99653816da72719e341178b4ef1cb87d6f7f0f33` | `dsv_fe333de5c5b8aa8d5b58fdfd99653816` / `ef52d548ec704e21c5a4e0a034ac79d1167277fcd2e148253d08c5d069089093` |
| Capacity surge combined | 20260901 | `2026-01-15` to `2026-02-12` | center count 2; arrival multiplier 1.5; queue multiplier 1.7 | `65eb6fd0b8bd841942769412bc65c81948785307836939f4bf5a404147c5a2fd` | `dsv_65eb6fd0b8bd841942769412bc65c819` / `f4b9848fb98ac834056e560e1dde690a0b3982a1ed5f8469b9a8157775106cee` |
| Capacity surge neutral | 20260901 | `2026-01-15` to `2026-02-12` | center count 2; arrival multiplier 1; queue multiplier 1 | `3f2a2b67753e483677bc0088c659b016199d997b87a068b0491d3ab5725a3516` | `dsv_3f2a2b67753e483677bc0088c659b016` / `d6c31ab8d68d9c4b1a735cfb4adea71931766907cc78db55763514d6cdb562e6` |

## Runtime capability and context boundary

- `tool_registry_version = w03-c02-tools.v1`.
- `flowlens.db.decision_snapshot` is the sole DB-capable C02 runtime adapter:
  PostgreSQL, `REPEATABLE READ`, `READ ONLY`, one transaction per snapshot.
- Pure Snapshot Assembler, Temporal Projector, Evidence Builder, Semantic Trust
  Classifier, Derivation Engine, and DecisionContext Builder have no DB access.
- HGT, operational write, runtime filesystem/network, LLM and model tools: none.
- `model_config`, `runtime_prompt_version`, `runtime_prompt_hash`:
  `NOT_APPLICABLE`.

Allowed sources are the current repository, frozen G0/C01/W2 contracts,
the C02 authorization package, W2 business datasets for development tests,
guarded PostgreSQL test database, and GitHub PR/CI evidence. Forbidden runtime
sources include protected HGT, scenario labels/answers, prompt text, test
oracles, unrelated files, secrets, and production databases.

Authorized implementation paths are the six new pure decision modules,
`src/flowlens/db/decision_snapshot.py`, additive DB-free
`src/flowlens/decision/__init__.py` exports, the five C02 test files, C02
checkpoint documents, the later Round Report, and `docs/CURRENT_STATE.md`
only in the report commit. Frozen C01 kernel/tests, W2 source/schema/hash and
scenario semantics, dependencies, CI workflows, AGENTS.md, LOOP.md, and skills/
are excluded.

Expected Context Delta: C02 contracts and Context Lock, pure observation
modules, one read-only DB adapter, bounded operational-field runtime input,
and later report/state evidence. No schema, migration, dependency, operational
mutation, runtime HGT, LLM, or C03 capability change.

## Authoritative repository document SHA-256

| Path | SHA-256 |
|---|---|
| `AGENTS.md` | `ceb3c166e2d4d2782688d668121bfb1de6ec69bd9d3513cb4d63bc4d9f165c76` |
| `LOOP.md` | `1850365277f65bbba1637381c37474a853e07b1c1510b6ce30293395cd949e99` |
| `docs/CURRENT_STATE.md` | `72408de650cfea18a58747d876ae74214fbafa34667083b54a5604fc0b36596d` |
| `docs/sprints/W03_ai_decision_loop.md` | `f69b9702b37e3c6d59947e4f6f0923e893b9f50acd5be235b705955c986bb86e` |
| `docs/w03/AI_LOOP_CONSTITUTION.md` | `48702680c6403e3cabfb7e774db72f88cdaabb165899d78d1893cf0373a0ceed` |
| `docs/w03/SEMANTIC_TRUST_CONTRACT.md` | `184d4bbd1ca26f37887525bef0417295da4ddeff6eb7db3b25e0ddabb5fc646d` |
| `docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md` | `cb4a0de4d0fe2ef9231cf6e579c1a557129ab097572e29a0addb43172a52dd8a` |
| `docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md` | `6eaec8e2a918665ac6b21b22a83e6133bd2e827288433d451e0b8beb4381c9b4` |
| `docs/w03/LOOP_EXECUTION_STATE_MACHINE.md` | `aa291f3d3a8c273a5c8175b9ae5fe58471bd3cba8662c1253de499cd3e5f860d` |
| `docs/w03/FAILURE_AND_DEGRADATION_POLICY.md` | `164afc436c4f00104690d02a4b7b7cea223e7ebe7b74d4a3a164159ee22223ad` |
| `docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md` | `74dcc0552595c3c0d368fa527c1b85b34f299ba943bdf16b75407c0a71e1a82a` |
| `docs/03_data_contracts.md` | `baa598d25988ba016d5f9dcd55f95a7838cead60cb01402b53ac4f3b91707ca2` |
| `docs/w03/checkpoints/c01/W03_C01_CORE_ARTIFACT_CONTRACTS.md` | `44e239781eb9c0886f65290ebcfd6aa4b32b0efb2d370a5ed876bef9e56e801d` |
| `docs/w03/checkpoints/c01/W03_C01_IDENTITY_PROVENANCE_SERIALIZATION.md` | `98a05a823f745fff2a83f85fb230cbf1e7518464d9b918cbd7c3b635db6976c3` |
| `docs/w03/reports/W03_C01_C1_FINAL_CLOSEOUT.md` | `dd36c0035402bcbc7f903f687376290560ffed9f19e34b9b7055eba521856249` |

## Frozen C01 code and test SHA-256

| Path | SHA-256 |
|---|---|
| `src/flowlens/decision/contracts.py` | `6179428829f2c23217e76de71a6a3c8769af3fe6253b6fb7d624e80107054134` |
| `src/flowlens/decision/enums.py` | `0f7ea7e059f79df84ca3f312bd354829a00794f602f302584c4f7abdc66c35d6` |
| `src/flowlens/decision/primitives.py` | `58eb6bb0f371ee02343e4bbd8ca5d664eebe6d28322552f246cf7455d99ff2ab` |
| `src/flowlens/decision/serialization.py` | `508194080ba1537931365fb68f17b6c49f2ae58549c794a683e3fa582bc4cfd3` |
| `tests/test_decision_contracts.py` | `c899e806845a2bb5f2fd19742fa25a1472b031c62b7bf9cbdf75c95ec538e0c1` |
| `tests/test_decision_serialization.py` | `e191905cd139bc3932bed4d39f1eb1ac28e80d3176968ba114fa116e30966ac1` |

## C02 input SHA-256

| Input | SHA-256 |
|---|---|
| `docs/w03/checkpoints/c02/W03_C02_ARCHITECTURE_SEMANTIC_FREEZE.md` | `9464ee61e4f7c3f6e72c28650c160e6facb2d7b37750a4cebb38c0468135dd28` |
| `docs/w03/checkpoints/c02/W03_C02_AUTHORIZATION_CONTRACT.md` | `d6fc11cb4961a13ece39595a3d80a73cbaadcf5fefeaf8a0843f5c584b058289` |
| `docs/w03/checkpoints/c02/W03_C02_DECISION_CONTEXT_DERIVATION_CONTRACT.md` | `0f3454a4ae0a09ce74a36cd6abfb993de7ca48896a92813757d7ceba973b9b58` |
| `docs/w03/checkpoints/c02/W03_C02_EVIDENCE_TRUST_FRESHNESS_MATRIX.md` | `6d56cf2ba18fe077aa2802142f745f99b5e1aee5b22a215382c31d3bda5fa3df` |
| `docs/w03/checkpoints/c02/W03_C02_GPT_FINAL_ZERO_AMBIGUITY_AUDIT.md` | `0cca92ac096806ae5abc4225fb41376bc2f1c8dd729174a17a5988c246b063e2` |
| `docs/w03/checkpoints/c02/W03_C02_GPT_REVIEW_CHECKLIST.md` | `0b4e2f673e3da403641527322fe43b67ee9cdfd56dc54f187fb075628cc5ffc8` |
| `docs/w03/checkpoints/c02/W03_C02_HARNESS_ACCEPTANCE_SPEC.md` | `311f25a70c023b7864e45ddfbeeee8272640aa07afcfcfef51feba5fb8f40834` |
| `docs/w03/checkpoints/c02/W03_C02_HUMAN_AUTHORIZATION.md` | `8663c4e52af417b6dc1e592fece7fd5e1061489eede6ed8c48b89f9dcc37ad89` |
| `docs/w03/checkpoints/c02/W03_C02_POSTGRES_SNAPSHOT_ISOLATION_CONTRACT.md` | `23d8a62af4fb9d434ddf71de0d142ea2853e422d8d82f13834e92c1a3e28632b` |
| `docs/w03/checkpoints/c02/W03_C02_SOURCE_FIELD_SNAPSHOT_MATRIX.md` | `49fe98e7bede89c7bcf03f6db919a50ae00825faa34130b3c7fe49a4d71b3f39` |
| `C:\Users\C\Downloads\FlowLens_W03_C02_GPT_COMPLETE_MASTER.md` | `0b72419f9d12ab08cc7c14924754b63f03dd41d018118c08f9ff6611b4b47bc7` |
| `C:\Users\C\Downloads\FlowLens_W03_C02_GPT_Authorization_Package.zip` | `918dea33a4e554c3a29d0b1e1b3d5c67ed0e6649db706b5de06283d29853d25c` |
| `C:\Users\C\Downloads\W03_C02_CODEX_EXECUTION_PROMPT.md` | `57bad61a3ef89e5c3ee5e51e266cb6b22c37f593b44d10fdb138e0766a691eb0` |
