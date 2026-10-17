# W04-C09 V1.1 — Harness Specification

| Control | Detection | Enforcement | Evidence |
|---|---|---|---|
| F01 C01_CONTRACTS_IDENTITY | Exact manifest targets and frozen leaf counts | One isolated pytest subprocess, PASS-only complete setup/call/teardown; exit zero | Canonical sealed family PASS (6/6) |
| F02 C02_CASE_BINDING_TEMPORAL | Exact manifest targets and frozen leaf counts | One isolated pytest subprocess, PASS-only complete setup/call/teardown; exit zero | Canonical sealed family PASS (6/6) |
| F03 C03_PLANNING_DETERMINISM | Exact manifest targets and frozen leaf counts | One isolated pytest subprocess, PASS-only complete setup/call/teardown; exit zero | Canonical sealed family PASS (6/6) |
| F04 C04_AUTHORIZED_NAVIGATION_READ_ONLY | Exact manifest targets and frozen leaf counts | One isolated pytest subprocess, PASS-only complete setup/call/teardown; exit zero | Canonical sealed family PASS (9/14) |
| F05 C05_FINDINGS_CONFLICT_UNCERTAINTY | Exact manifest targets and frozen leaf counts | One isolated pytest subprocess, PASS-only complete setup/call/teardown; exit zero | Canonical sealed family PASS (7/7) |
| F06 C06_HUMAN_AUTHORITY_AUDIT | Exact manifest targets and frozen leaf counts | One isolated pytest subprocess, PASS-only complete setup/call/teardown; exit zero | Canonical sealed family PASS (10/10) |
| F07 C07_SUMMARY_GROUNDING | Exact manifest targets and frozen leaf counts | One isolated pytest subprocess, PASS-only complete setup/call/teardown; exit zero | Canonical sealed family PASS (10/10) |
| F08 C08_PROTECTED_REPLAY | Exact manifest targets and frozen leaf counts | One isolated pytest subprocess, PASS-only complete setup/call/teardown; exit zero | Canonical sealed family PASS (8/17) |
| F09 SOURCE_EVOLUTION_GOVERNANCE | Exact manifest targets and frozen leaf counts | One isolated pytest subprocess, PASS-only complete setup/call/teardown; exit zero | Canonical sealed family PASS (5/5) |
| Manifest identity | Strict JSON keys/types; raw/canonical hashes; exact family order | Reject drift, duplicates, nonfinite JSON and non-function selectors | Pinned manifest raw/content hashes |
| C08 replay source | AST identities and complete top-level source spans at exact entry | Only authorized R43/R46 symbols may differ; imports, docstring, decorators and damage list frozen | Independent source-delta guard PASS |
| Workflow truth | Exact entry-to-current block transformation and actual Bash status truth table | Only new W04 job plus Verification conjunction; require W03+W04 non-P, skip both P | Independent adversarial contract verifier PASS |
| Family isolation | Actual runner subprocess orchestration and two fresh-process isolation probes | No shared pytest process; only current family selectors; neutralized addopts | Nine isolated native family PASS results |
| Summary integrity | Canonical bytes and omitted-field SHA-256 self-seal | Invalidate stale output before proof; reject wrong HEAD/local output | Summary self-seal and exact raw SHA-256 |
| DEVCTRL-03 collection | Fresh actual collection and active measured plan | 2997/63 with frozen digests, weights, schema, seven shards and unchanged timeouts | Planner proof and exact zero node delta |
| Real native proof | Exact-SHA run/jobs and 11 original ZIP digests; summary bytes | Retain W03 38/85, 2997/2994/3, integration 70 and exact union/once/no-loss | R46 GITHUB_NATIVE PASS |
| Resilience | Seven job timestamp deltas and seven native suite times | Every job and pytest suite <3300s; no automatic re-weight/topology/timeout repair | Durations, longest shards, headroom to 55m/65m |
| Authority/scope | Frozen objects and exact Stage-A/Stage-B path sets | No runtime capability, source entry, acceptance, closeout, C10, merge or main write | Exact changed-path proof; report-only P publication |

Independent controls execute actual runner functions/CLI and workflow shell. Temporary adversarial pytest files live outside the repository and do not add nodes to the active 2997-node collection. Control/fixture proof is never substituted for native evidence. Failure hard stops follow the authorization contract.

## Repair-01 meta-CI proof

| Control | Detection | Enforcement | Evidence |
|---|---|---|---|
| Exact 14-path authorization | Pinned allowlist in JSON and independent verifier | Reject any 15th Stage-A path and mixed report delta | Scope proof PASS |
| Classifier meta-CI file | AST identities and source-exact top-level spans against entry | Exactly one existing function changes only the required needs literal; all other units unchanged | C09_META_CI_DELTA_GUARD PASS |
| W03 meta-CI file | Same structural/source-exact comparison | Exactly two existing functions receive only approved job-set, dependency/binding and W04 wrong-status additions; complete W03 proof retained | C09_META_CI_DELTA_GUARD PASS |
| Guard adversaries | Unrelated body, new/renamed test, import, decorator and parameter mutations in each file | Reject all mutations; do not add any repository pytest node | Independent controls PASS |
| Repair regression | Three repaired selectors and both full files | All PASS, followed by every required V1.1 local proof | Local native pytest/JUnit evidence |
