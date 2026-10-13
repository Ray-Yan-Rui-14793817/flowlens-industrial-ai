# W04-C09 V1.1 — Context Lock

LOCKED BEFORE IMPLEMENTATION. All facts observed at the authorized entry; subsequent implementation/run identities belong in the development report.

```text
TASK_VERSION: V1.1
TASK_RAW_SHA256: a445ee4ec99a714dd7e53f162df3eccdc0f8ed9295c6a67a71cef308feba553b
LOCAL_HEAD = TRACKING_FEATURE_HEAD = DIRECT_ORIGIN_FEATURE_HEAD = PR_7_HEAD:
1fa841f2ee0d6612774c9f0ced204289df86e7a1
BRANCH: feat/w04-evidence-investigation
PR_7: OPEN / DRAFT / UNMERGED; auto-merge absent
MAIN = ORIGIN_MAIN = DIRECT_ORIGIN_MAIN = PR_BASE:
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
AHEAD_BEHIND: 0/0
WORKTREE_INDEX: CLEAN
FRESH_FETCH: PASS
LATEST_FEATURE_CI: #136 / 38360398379 / SUCCESS / attempt 1
CLASS: C / FULL_EXACT_SHA
C01-C08: CLOSED
C09_SOURCE_ENTRY: ABSENT BY DESIGN
C10: NOT AUTHORIZED
```

## Frozen baseline

```json
{
  "nodes": 2997,
  "node_digest": "9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a",
  "files": 63,
  "file_digest": "890fdd5c30c7e2a1e90da8cb8b7123937d3356f1d519f82dff4a941f13659fd7",
  "weights_digest": "a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851",
  "plan_schema": "w04-devctrl03-non-integration-plan-v1",
  "protected_blobs": {
    ".github/workflows/ci.yml": "beb565ae91b4c65880d34fac92b22577de41963d",
    "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json": "8a4555dba4bfbe6556f19413d323f8b1761ebd54",
    "docs/w04/devctrl-03/W04_DEVCTRL_03_MEASURED_SHARD_WEIGHTS.json": "558f1a3ba2de948a18232ce4fca90be9447aec81",
    "scripts/ci/plan_non_integration_shards.py": "ad1922003ebf07f11d10186b4aa136a0d7b125f1",
    "tests/test_investigation_replay.py": "27a46638518c1c7a4ddddac0d0978e08cffe3fca"
  }
}
```

Seven whole-file shards; non-integration timeout 65m; max-parallel 7; fail-fast false. Native acceptance additionally requires every shard job and pytest suite strictly below 3300s.

## C01-C08 source blobs

| Checkpoint | Source path | Frozen blob |
|---|---|---|
| W04-C01 / CLOSED | `src/flowlens/investigation/__init__.py` | `c23929f85dccd78bc72ef3b2b1415c6e8eaf0452` |
| W04-C01 / CLOSED | `src/flowlens/investigation/contracts.py` | `0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e` |
| W04-C01 / CLOSED | `src/flowlens/investigation/enums.py` | `9c818780423f32f144b18666784ebc9ea3abdccc` |
| W04-C02 / CLOSED | `src/flowlens/investigation/c02_binding.py` | `5f0af237ed465fa83e5a3b84954512b1f3125551` |
| W04-C03 / CLOSED | `src/flowlens/investigation/c03_planning.py` | `21d0055e12d86e6333a836d363d6e266cb0fcbd7` |
| W04-C04 / CLOSED | `src/flowlens/investigation/c04_navigation.py` | `98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4` |
| W04-C04 / CLOSED | `src/flowlens/investigation/c04_queries.py` | `dc22c7e532a4b62ccfffec2210bc2a6306d97234` |
| W04-C04 / CLOSED | `src/flowlens/investigation/c04_registry.py` | `fbe6f0603d7b0634426ac0034033089eb55af4d7` |
| W04-C05 / CLOSED | `src/flowlens/investigation/c05_findings.py` | `31384426ba9c733bc5bdbf3b09a3d206c8182586` |
| W04-C06 / CLOSED | `src/flowlens/investigation/c06_human.py` | `021f5b72254c87c5b965500727a67001a47ef0bd` |
| W04-C06 / CLOSED | `src/flowlens/investigation/c06_policy.py` | `8cfea031eaa764d871822c2e12de019ed3ebc3b9` |
| W04-C06 / CLOSED | `src/flowlens/investigation/c06_store.py` | `e99d5d4c36db1dd3ed11c40ff9bbc5b01663ae9a` |
| W04-C07 / CLOSED | `src/flowlens/investigation/c07_policy.py` | `c969c4bbf33910fab6ffb36c3bfe184fd42c74c9` |
| W04-C07 / CLOSED | `src/flowlens/investigation/c07_provider.py` | `56ecb9f3d7b5a1917a2354572e8c946f07eb759d` |
| W04-C07 / CLOSED | `src/flowlens/investigation/c07_summary.py` | `3d561da7ab625421bbcf2dcb3785f8fae792cbff` |
| W04-C08 / CLOSED | `src/flowlens/investigation/c08_policy.py` | `273d288cf4b0e55b646cd2e6751f0259e463a5ff` |
| W04-C08 / CLOSED | `src/flowlens/investigation/c08_replay.py` | `4fa391cf751377305315b7de8303ce94e6eb6c6e` |

Source-evolution manifest raw SHA-256: `d22a12306f8fe98952b9e35a5f166f29fee968c9aedcff27511da59889c20c2d`. Every source blob verified against Git entry HEAD.

## Native selector baseline

The original #136 aggregate/integration ZIP digests matched the freshly fetched GitHub artifact identities. Native JUnit hashes match the frozen manifest. Exact leaf counts and PASS-only terminal outcomes were checked for every target.

| Family | Selectors | Expanded cases | #136 testcase seconds |
|---|---:|---:|---:|
| F01 C01_CONTRACTS_IDENTITY | 6 | 6 | 0.257 |
| F02 C02_CASE_BINDING_TEMPORAL | 6 | 6 | 7.378 |
| F03 C03_PLANNING_DETERMINISM | 6 | 6 | 23.508 |
| F04 C04_AUTHORIZED_NAVIGATION_READ_ONLY | 9 | 14 | 27.987 |
| F05 C05_FINDINGS_CONFLICT_UNCERTAINTY | 7 | 7 | 41.617 |
| F06 C06_HUMAN_AUTHORITY_AUDIT | 10 | 10 | 127.789 |
| F07 C07_SUMMARY_GROUNDING | 10 | 10 | 49.092 |
| F08 C08_PROTECTED_REPLAY | 8 | 17 | 428.535 |
| F09 SOURCE_EVOLUTION_GOVERNANCE | 5 | 5 | 0.811 |

Totals: 9 families / 67 exact selectors / 81 expanded cases; 706.974s. Selected failure/error/skip/xfail/xpass = 0. Fresh active collection: 2997 nodes / 63 files; same canonical node/file digests; unchanged active weights and seven-shard planner contract.

## Exact path scope

```json
{
  "stage_a": [
    ".github/workflows/ci.yml",
    "scripts/ci/run_w04_investigation_gate.py",
    "scripts/ci/verify_w04_investigation_gate_contract.py",
    "tests/test_investigation_replay.py",
    "docs/w04/checkpoints/c09/W04_C09_AUTHORIZATION_CONTRACT.md",
    "docs/w04/checkpoints/c09/W04_C09_HUMAN_AUTHORIZATION.md",
    "docs/w04/checkpoints/c09/W04_C09_CONTEXT_LOCK.md",
    "docs/w04/checkpoints/c09/W04_C09_CI_REGRESSION_CONTRACT.md",
    "docs/w04/checkpoints/c09/W04_C09_HARNESS_SPEC.md",
    "docs/w04/checkpoints/c09/W04_C09_GPT_REVIEW_CHECKLIST.md",
    "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json",
    "docs/w04/checkpoints/c09/specs/authorized_paths.json"
  ],
  "stage_b": [
    "docs/w04/checkpoints/c09/W04_C09_R_DEVELOPMENT_ROUND_REPORT.md"
  ]
}
```

## Hard stops

```text
W04_C09_CONTEXT_CHANGED
W04_C09_HUMAN_AUTHORIZATION_REQUIRED
W04_C09_SELECTOR_BASELINE_MISMATCH
W04_C09_NODESET_DRIFT
W04_C09_SCOPE_VIOLATION
W04_C09_PROTECTED_OBJECT_DRIFT
W04_C09_GATE_CONTRACT_FAILED
W04_C09_C08_HARNESS_DELTA_VIOLATION
W04_C09_STAGE_A_CI_FAILED
W04_C09_DEVCTRL03_RESILIENCE_REGRESSION
W04_C09_R46_NATIVE_PROOF_FAILED
W04_C09_STAGE_B_CI_FAILED
W04_C09_SYNC_FAILED
W04_C09_REQUIRES_GPT_CLARIFICATION
```

Any requirement for runtime source change, new test node admission, dependency,
migration, provider/model behavior, source-manifest mutation, unrelated C08
replay-test body mutation, DEVCTRL-03 re-weight/timeout/topology change or C10
behavior is a contract conflict.

Stop rather than infer authority.


## Repair-01 resumption context lock

LOCKED BEFORE THE TWO ADDITIONAL FILE CHANGES. Base V1.1 remains authoritative; its 12-path Stage-A limit is amended to exactly 14 by the approved Repair-01 addendum.

```text
REPAIR-01 HUMAN AUTHORIZATION: APPROVED
REPAIR-01 RAW SHA-256: 744640783621660de009a8a1656ebb55bf752802ecb7e8256b8a1d9a8f3ee0ef
LOCAL / TRACKING / DIRECT-ORIGIN / PR HEAD:
1fa841f2ee0d6612774c9f0ced204289df86e7a1
MAIN / DIRECT ORIGIN MAIN / PR BASE:
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
PR #7: OPEN / DRAFT / UNMERGED; auto-merge absent
LATEST NATIVE CI: #136 / 38360398379 / SUCCESS
AHEAD / BEHIND: 0/0
INDEX: CLEAN
WORKTREE: retained authorized 12-path candidate, unstaged
RETAINED CANDIDATE BLOBS: 12/12 IDENTICAL TO STOPPED CANDIDATE
ADDITIONAL TWO META-CI FILES: ENTRY-IDENTICAL BEFORE REPAIR
```

The previous three failures are approved meta-CI topology compatibility failures. The only new test-body authority covers one existing classifier workflow test and two existing W03 meta-CI tests. Imports, docstrings, assignments, fixtures, helpers, all other tests, names, decorators and parameter lists remain entry-identical. No node/parameter expansion is admitted.

Effective exact path sets:

```json
{
  "checkpoint": "W04-C09",
  "schema_version": "w04-c09-authorized-paths-v1",
  "stage_a": [
    ".github/workflows/ci.yml",
    "scripts/ci/run_w04_investigation_gate.py",
    "scripts/ci/verify_w04_investigation_gate_contract.py",
    "tests/test_investigation_replay.py",
    "docs/w04/checkpoints/c09/W04_C09_AUTHORIZATION_CONTRACT.md",
    "docs/w04/checkpoints/c09/W04_C09_HUMAN_AUTHORIZATION.md",
    "docs/w04/checkpoints/c09/W04_C09_CONTEXT_LOCK.md",
    "docs/w04/checkpoints/c09/W04_C09_CI_REGRESSION_CONTRACT.md",
    "docs/w04/checkpoints/c09/W04_C09_HARNESS_SPEC.md",
    "docs/w04/checkpoints/c09/W04_C09_GPT_REVIEW_CHECKLIST.md",
    "docs/w04/checkpoints/c09/specs/c09_gate_manifest.json",
    "docs/w04/checkpoints/c09/specs/authorized_paths.json",
    "tests/test_ci_change_classifier.py",
    "tests/test_c09_ci_gate.py"
  ],
  "stage_b": [
    "docs/w04/checkpoints/c09/W04_C09_R_DEVELOPMENT_ROUND_REPORT.md"
  ],
  "task_version": "V1.1",
  "repair_01_sha256": "744640783621660de009a8a1656ebb55bf752802ecb7e8256b8a1d9a8f3ee0ef"
}
```

No 15th Stage-A path. No repair-only commit. Original Stage-A subject and single commit/push remain unchanged. All V1.1 native CI, <55m resilience, 11-artifact real-native R46 and report-only Stage-B requirements remain authoritative.
