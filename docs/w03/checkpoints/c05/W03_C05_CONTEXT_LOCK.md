# W03-C05 Context Lock

```text
checkpoint_id = W03-C05
context_lock_status = LOCKED
locked_at = 2026-09-27 Asia/Shanghai

branch = feat/w03-ai-decision-loop
baseline_sha = c47c6e6d2088bf024ee7bccb9c6e8746c1e49466
tracking_sha = c47c6e6d2088bf024ee7bccb9c6e8746c1e49466
direct_remote_sha = c47c6e6d2088bf024ee7bccb9c6e8746c1e49466
main_sha = 9d18ddde9fe933952a2661ee1419f13c8577605d
pr_6 = OPEN / DRAFT / NOT MERGED
c04_closeout_sha = c47c6e6d2088bf024ee7bccb9c6e8746c1e49466
run_59 = 36247768789 / PASS / P / PUBLICATION_EXACT_SHA
```

The pre-flight found a clean synchronized branch, zero ahead/behind, no in-progress Git
operation, and no baseline drift. Run 59 classified the exact C04 closeout SHA as publication
class `P`; its required classification, publication-proof, and verification jobs passed.

## Authoritative material hashes before source/test implementation

| Path | SHA-256 |
|---|---|
| standalone `W03_C05_CODEX_EXECUTION_TASK_V1.md` | `8870ebbad384d100f481199f3d9c600367abeaca6fdf7db5d52eb78dbdbd6dda` |
| actual pasted Human authorization | `a3ee4b6ed4e52a490dd489ca1ff67a6a3e19f388cce24ef6c8509152931e7f7b` |
| `AGENTS.md` | `ceb3c166e2d4d2782688d668121bfb1de6ec69bd9d3513cb4d63bc4d9f165c76` |
| `LOOP.md` | `1850365277f65bbba1637381c37474a853e07b1c1510b6ce30293395cd949e99` |
| `docs/CURRENT_STATE.md` | `775cbece8a912a55f8cae4a6e8edb56ecf8794f22137d2cf8f618e2d2c10bfc8` |
| `docs/sprints/W03_ai_decision_loop.md` after status-only normalization | `01603b5be107e903a5e9f3032d5adb54840e280204e10f22856e2b384008a7a0` |
| `docs/w03/AI_LOOP_CONSTITUTION.md` | `48702680c6403e3cabfb7e774db72f88cdaabb165899d78d1893cf0373a0ceed` |
| `docs/w03/SEMANTIC_TRUST_CONTRACT.md` | `184d4bbd1ca26f37887525bef0417295da4ddeff6eb7db3b25e0ddabb5fc646d` |
| `docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md` | `cb4a0de4d0fe2ef9231cf6e579c1a557129ab097572e29a0addb43172a52dd8a` |
| `docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md` | `6eaec8e2a918665ac6b21b22a83e6133bd2e827288433d451e0b8beb4381c9b4` |
| `docs/w03/LOOP_EXECUTION_STATE_MACHINE.md` | `aa291f3d3a8c273a5c8175b9ae5fe58471bd3cba8662c1253de499cd3e5f860d` |
| `docs/w03/FAILURE_AND_DEGRADATION_POLICY.md` | `164afc436c4f00104690d02a4b7b7cea223e7ebe7b74d4a3a164159ee22223ad` |
| `docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md` | `a02b5c9146780558be304f081bf231c46d9d817ef16df80a44f6f90c16debb33` |

## Published C05 governance artifacts

| Path | SHA-256 |
|---|---|
| `W03_C05_AUTHORIZATION_CONTRACT.md` | `6c16eb4d1683da090879f3d4b451756a367d287bffb68e5869849b4804edbda6` |
| `W03_C05_HUMAN_AUTHORIZATION.md` | `027a17c5345df65a9c4d4922ff44dc04070d651eb718df0ab1f89969cbd0e777` |
| `W03_C05_EVALUATION_POLICY.md` | `81f589b832699052b703e4d8ad8946f3432941b8989b48ee7ed25ba8b72a43e6` |
| `W03_C05_RECOMMENDATION_CONTRACT.md` | `66630fcef9575800196f50df6cdec83340ffb180ab18c2385fe8af832a51756e` |
| `W03_C05_DECISION_PACKET_CONTRACT.md` | `eb7b08171c4630089b6bc2bb71de9d8390b1985d89b48cf93f05d33be038f0ad` |
| `W03_C05_HARNESS_ACCEPTANCE_SPEC.md` | `4e195c38a7e4d8cae186950ec487cec6d0dbd93447443ce700f940702e867cd8` |
| `W03_C05_GPT_REVIEW_CHECKLIST.md` | `5ec25a74a1b705a886209bea309fee84b2b8441de2c44ef1c3a47266f87957ce` |
| `W03_C05_DEVCTRL_INTEGRATION_CONTRACT.md` | `22eec24d19018f2df11aecd9095ad30588a171441f5b7570fd032eae7dd1303c` |
| `specs/authorized_paths.json` | `a903bded3896c4763427eed7ff0158806161f5146ef74d08946a3c1d0431e98a` |
| `specs/evaluation_policy.json` | `a4977639b1354d6c0c687777f603fff5f03f2a13fb5ccf9946f73398229027d8` |
| `specs/score_component_schema.json` | `20a5526a47710f3c195b09db40f5f94ff9fa5cae09e120b9b02cdfbc83717e79` |
| `specs/reason_codes.json` | `0e9e2b41353ac7e7b32d815c2ecc92238488a1100f5ff6e91bbb9d50ea43be3c` |
| `specs/limitation_codes.json` | `d687c286f0488e7433d218b59732c5f8ade18c417b4bd0e0dfbc2155a747058e` |

## Accepted upstream checkpoint evidence

| Checkpoint | Authorization | Context Lock | Independent R2 | Final closeout |
|---|---|---|---|---|
| C01 | `59ae4bfb60c4f8a0136b7dc3256f0dbfe30283d83f9013a1fb600b35273974fc` | `e5169a04f3adada650e585f2759f6fd032428e8b937dda6661003e9b17c0129c` | `dd441737cf7e34009254e7a3c7faf8af7ddf426f0061fea5e1818098087b7af0` | `dd36c0035402bcbc7f903f687376290560ffed9f19e34b9b7055eba521856249` |
| C02 | `ef4578c0e0e4e275b45b549eba242c5a52af571c3c270e7b5c75869f0ccf6a99` | `a0800c591bdf86b94f5523556b4e915ac84ffc479bf751aafc9626578abd93d9` | `87e02a259eb0f0c9ffa58aab73d706db4f21dd4c914bb88cfd130768d7f5add9` | `be01babfaeec82de206178d148ec5db4db9f34b05e1c47101e67b4e7b9bb1a65` |
| C03 | `bbd0d9ec34427c67de4e8769b247619f739fe4167ae3ba35656eda7ede0cbdd9` | `55c58e45b86b6a164bf90ba388bf1b34c7cb7b631cc0cc56735645086e8003a1` | `798c67b01375acea2043b6cc876746eef1f64c1f92b942493bd3479db51d05e4` | `ad536acdf423f58cc7a41f34a0a2b5e4903e9d45a9e25a48780467dd883760f1` |
| C04 | `046343de0b89cbf1d41d082a624d5cb645b2a360952e6787983b623d45c1caca` | `fc778ad6cfc441d50d5788083057d0b42fbf94e391ba8ff97e3653a811f431fa` | `853a87906d1d1404d490d883d8a9675c616bb6a18839963594c546ee9d61974b` | `d2a3f8dfbad91bade570b24b86ff122f0913749b25de32bd8a3efa4170da304c` |

The accepted C04 implementation SHA is
`62405d7169b1aaea321290749395ab077792f86f`; its R1 repair SHA is
`ae54dbc23effedf59566306d209a03b7290a299e`; its R1 report SHA is
`933aada93d1db91cce0165e794d41dc759d8dc74`; and its final closeout SHA is
`c47c6e6d2088bf024ee7bccb9c6e8746c1e49466`.

## Frozen policy versions

```text
decision_policy_version = w03-c05-decision-v1
evaluation_schema_version = w03-c05-evaluation-v1
packet_policy_version = w03-c05-packet-v1
recommendation_schema_version = recommendation-record.v1
```

No wall-clock versioning is permitted.

## Runtime source and path boundary

Allowed runtime inputs are only explicitly supplied canonical in-memory C01/C02/C03/C04
artifacts: `DecisionRun`, `StateSnapshot`, `EvidenceBundle`, `DecisionContext`, `SignalBundle`,
`DiagnosisRecord`, `CandidateSet`, and `SimulationBundle`. C05 consumes the frozen C04 simulation
results and must not execute scenarios.

Forbidden runtime sources and capabilities are post-C02 database reads, filesystem, network,
models, subprocess, random, wall clock, scenario execution, runtime HGT, future evidence, and
operational mutation. The LLM has no role in evaluation, recommendation, ranking, tie-breaking,
or packet assembly.

Authorized implementation and report paths and frozen paths are exactly those in
`specs/authorized_paths.json`. In particular, C01-C04 source/tests, W2 sources, package exports,
dependencies, CI/workflows, and `main` remain frozen. C06-C08 and all closeout actions are outside
this authorization.

## Human Authorization

The Product Owner's actual authorization message states exactly
`W03-C05 HUMAN AUTHORIZATION: APPROVED` and directs execution of W03-C05-I/H/R exactly according
to the standalone task through `REVIEW_READY`. It does not grant Human acceptance, closeout,
PR merge, or C06 authorization.
