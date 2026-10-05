# FlowLens Industrial AI — W03-C08 Context Lock

```text
context_lock_status = LOCKED
checkpoint = W03-C08
task = W03-C08-I/H/R
contract_version = W03-C08-A-v1
locked_at = 2026-09-28 Asia/Shanghai
```

## Entry and governance state

```text
branch = feat/w03-ai-decision-loop
entry_sha = c89a2cc5b24a53897ec0d8085293445c18fd2675
tracking_sha = c89a2cc5b24a53897ec0d8085293445c18fd2675
direct_remote_sha = c89a2cc5b24a53897ec0d8085293445c18fd2675
main_sha = 9d18ddde9fe933952a2661ee1419f13c8577605d
pr = 6 / OPEN / DRAFT / NOT MERGED / AUTO-MERGE ABSENT
ahead_behind = 0/0
worktree = CLEAN
c07_closeout_run = 72 / 36432458433 / SUCCESS
c07_closeout_sha = c89a2cc5b24a53897ec0d8085293445c18fd2675
human_authorization = W03-C08 HUMAN AUTHORIZATION: APPROVED
```

C07 closeout changed only `docs/CURRENT_STATE.md` and C07 governance/report
paths. No pre-existing C08 implementation was observed.

## Frozen hashes at entry

| Material | SHA-256 |
|---|---|
| Codex execution task | `b3b7fce36f70979333e46db16d1090bcb098f0d0d1bea4654ed4e5cdb2d3f3eb` |
| GPT contract freeze | `db1237f53952d9ea458694afbe66dc23a27b0d4b9ec8c159cc652d6e9cac1b9f` |
| Runtime prompt bytes | `426b061d79d2a8dfa4ac2959a604e77e6ef8dbcc04759bf7860ec9f012d185fc` |
| AI Loop Constitution | `48702680c6403e3cabfb7e774db72f88cdaabb165899d78d1893cf0373a0ceed` |
| W03 sprint specification | `50df977eae7342fe9e668680ce14f66c2e1a7c3cc29c9f97bf9290f357501de4` |
| Semantic Trust Contract | `184d4bbd1ca26f37887525bef0417295da4ddeff6eb7db3b25e0ddabb5fc646d` |
| Context/Material Contract | `cb4a0de4d0fe2ef9231cf6e579c1a557129ab097572e29a0addb43172a52dd8a` |
| Prompt/Tool Contract | `6eaec8e2a918665ac6b21b22a83e6133bd2e827288433d451e0b8beb4381c9b4` |
| Loop State Machine | `aa291f3d3a8c273a5c8175b9ae5fe58471bd3cba8662c1253de499cd3e5f860d` |
| Failure/Degradation Policy | `164afc436c4f00104690d02a4b7b7cea223e7ebe7b74d4a3a164159ee22223ad` |
| Harness/Reporting Spec | `a02b5c9146780558be304f081bf231c46d9d817ef16df80a44f6f90c16debb33` |
| Context Index | `86ab221d6ccc967b0c6419b1a024430740a2bda4bb16e8c42aebbd1c98f43a35` |
| Material Registry | `a3d721c65f4a3142596ed2109c54f23818efb85748ffed9015dd2bf9ce951e11` |
| LOOP router | `1850365277f65bbba1637381c37474a853e07b1c1510b6ce30293395cd949e99` |

## Frozen upstream implementation

```text
C01 ExplanationRecord schema = explanation-record.v1
C01 contracts.py sha256 = 6179428829f2c23217e76de71a6a3c8769af3fe6253b6fb7d624e80107054134
C05 packet producer = flowlens.decision.c05_packet
C05 packet policy = w03-c05-packet-v1
C05 c05_packet.py sha256 = b98d4034f05ff102c136468be4f80eb069d4ab1ee40f58ed1a976a64e4d3b83c
C05 c05_policy.py sha256 = 2eaddd341deb3384cd045db59a8bc73adc2d38f22d0ac6f2886b0e767d746643
C05 c05_recommendation.py sha256 = 423c8076c4049e7395203fd5f125120d68122d52d943b51bd12fb4492f088a48
C05 c05_validation.py sha256 = e0bcc49283d97cad51b1c62a9bbc9380d81e1caf084761b27f7ee466a2601bb5
```

## Runtime contract

```text
prompt = w03-c08-runtime-prompt-v1 / 426b061d79d2a8dfa4ac2959a604e77e6ef8dbcc04759bf7860ec9f012d185fc
context = w03-c08-context-v1
output = w03-c08-output-v1
explainer = w03-c08-explainer-v1
template = w03-c08-template-v1
provider = OpenAI Responses API
model = gpt-5.6-terra
reasoning = none
tools/retrieval/streaming = none/none/off
max_output_tokens = 1200
timeout_seconds = 15
sdk_retries = 0
max_provider_calls = 2
```

```text
context_contract_sha256 = c54d6bf8f6143251273ea4a39a08efba7c8702547de4af37995936c7f83ae7fa
output_schema_sha256 = 23f552351e211bfa10bdda9fe385a38a951b9fc59392dc511c68dcb593710964
```

## Sources and delta

Allowed runtime source: exactly one canonical C05 DecisionPacket and only its
deterministic projection. Forbidden runtime sources: C07/evaluation/HGT,
database/session/engine, filesystem/repository, retrieval/RAG, live operational
state, ambient development context, time, and random state.

Authorized files are exactly those in `specs/authorized_paths.json`. Forbidden
files include C01 core contracts/enums/primitives/serialization, C07, evaluation,
W2 scenario/data/HGT, database/migrations, C05 policy, C06 semantics, CI
architecture, API/UI, main, and C09.

Expected context delta: publish the C08 contract package, update the W03 sprint
status, add the seven C08 runtime modules, add only C08 settings, add only the
official OpenAI SDK and lock resolution, add seven C08 test modules, and—only
after exact implementation proof—publish the C08 Development Round Report and
CURRENT_STATE update.

Dependency delta: official `openai` Python SDK only; the exact version is to be
resolved and locked by `uv` during implementation. No dataset, scenario,
database, schema, migration, tool-registry, C01, C05, C06, or C07 delta is
authorized.
