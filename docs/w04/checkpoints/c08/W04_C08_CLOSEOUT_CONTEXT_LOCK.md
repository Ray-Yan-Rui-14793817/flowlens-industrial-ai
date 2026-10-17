# W04-C08 Closeout Context Lock

Snapshot after Prep-01 native SUCCESS and before Phase-2 mutation. Observed UTC: 2026-10-12T04:29:50.596281+00:00. Asia/Shanghai: 2026-10-12T12:29:50.596281+08:00.

```text
LOCAL HEAD = 0047bb942e8e4227af8d6fb5c9a4763688a22aab
TRACKING FEATURE HEAD = 0047bb942e8e4227af8d6fb5c9a4763688a22aab
DIRECT ORIGIN FEATURE HEAD = 0047bb942e8e4227af8d6fb5c9a4763688a22aab
PR #7 HEAD = 0047bb942e8e4227af8d6fb5c9a4763688a22aab
BRANCH = feat/w04-evidence-investigation
PR #7 = OPEN / DRAFT / UNMERGED
MAIN / PR BASE = af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
WORKTREE / INDEX = CLEAN
AHEAD / BEHIND = 0/0
STAGE-B CI = #129 / 38153792599 / SUCCESS / I / FULL_EXACT_SHA
REVIEW_READY CI = #131 / 38190417996 / SUCCESS / P / PUBLICATION_EXACT_SHA
PREP-01 CI = #132 / 38200544252 / SUCCESS / I / FULL_EXACT_SHA
C08 SOURCE FREEZE = 1fa7b505980c1efc1b3725cd57a9732e254bccdf
CURRENT MANIFEST = C01-C07 CLOSED / C08 AUTHORIZED / C09 ABSENT
CURRENT C08 source_freeze_sha = null
CURRENT C08 blob_oid values = null
PREP TEST BLOB = f3716aaa46f39c3aaf858b24bc0b1833fb0b28ba
FINAL_CLOSEOUT_SHA = NOT YET CREATED
FINAL_CLOSEOUT_CI = PENDING
```

Accepted runtime identity:

| Path | Git blob OID |
|---|---|
| src/flowlens/investigation/c08_policy.py | `273d288cf4b0e55b646cd2e6751f0259e463a5ff` |
| src/flowlens/investigation/c08_replay.py | `4fa391cf751377305315b7de8303ce94e6eb6c6e` |

## Current immutable C01-C07 entries

```json
[
  {
    "checkpoint": "W04-C01",
    "state": "CLOSED",
    "source_freeze_sha": "084c2fea93d0e021994de015c986de9ff92bf9a3",
    "files": [
      {
        "path": "src/flowlens/investigation/__init__.py",
        "blob_oid": "c23929f85dccd78bc72ef3b2b1415c6e8eaf0452"
      },
      {
        "path": "src/flowlens/investigation/contracts.py",
        "blob_oid": "0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e"
      },
      {
        "path": "src/flowlens/investigation/enums.py",
        "blob_oid": "9c818780423f32f144b18666784ebc9ea3abdccc"
      }
    ]
  },
  {
    "checkpoint": "W04-C02",
    "state": "CLOSED",
    "source_freeze_sha": "18648915414a26dddbdc904965663730ea631cf2",
    "files": [
      {
        "path": "src/flowlens/investigation/c02_binding.py",
        "blob_oid": "5f0af237ed465fa83e5a3b84954512b1f3125551"
      }
    ]
  },
  {
    "checkpoint": "W04-C03",
    "state": "CLOSED",
    "source_freeze_sha": "42047bcfe6591f7c9ed9b0034bd94467401ba72f",
    "files": [
      {
        "path": "src/flowlens/investigation/c03_planning.py",
        "blob_oid": "21d0055e12d86e6333a836d363d6e266cb0fcbd7"
      }
    ]
  },
  {
    "checkpoint": "W04-C04",
    "state": "CLOSED",
    "source_freeze_sha": "6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1",
    "files": [
      {
        "path": "src/flowlens/investigation/c04_navigation.py",
        "blob_oid": "98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4"
      },
      {
        "path": "src/flowlens/investigation/c04_queries.py",
        "blob_oid": "dc22c7e532a4b62ccfffec2210bc2a6306d97234"
      },
      {
        "path": "src/flowlens/investigation/c04_registry.py",
        "blob_oid": "fbe6f0603d7b0634426ac0034033089eb55af4d7"
      }
    ]
  },
  {
    "checkpoint": "W04-C05",
    "state": "CLOSED",
    "source_freeze_sha": "3386b2637f0b0e3f0972a07ee0bea4ad8181cb5f",
    "files": [
      {
        "path": "src/flowlens/investigation/c05_findings.py",
        "blob_oid": "31384426ba9c733bc5bdbf3b09a3d206c8182586"
      }
    ]
  },
  {
    "checkpoint": "W04-C06",
    "state": "CLOSED",
    "source_freeze_sha": "de02e49af9ada512ff52afdcc5f72620c4f220af",
    "files": [
      {
        "path": "src/flowlens/investigation/c06_human.py",
        "blob_oid": "021f5b72254c87c5b965500727a67001a47ef0bd"
      },
      {
        "path": "src/flowlens/investigation/c06_policy.py",
        "blob_oid": "8cfea031eaa764d871822c2e12de019ed3ebc3b9"
      },
      {
        "path": "src/flowlens/investigation/c06_store.py",
        "blob_oid": "e99d5d4c36db1dd3ed11c40ff9bbc5b01663ae9a"
      }
    ]
  },
  {
    "checkpoint": "W04-C07",
    "state": "CLOSED",
    "source_freeze_sha": "c86f7af2370f315b8b7310008521f08ceade6d97",
    "files": [
      {
        "path": "src/flowlens/investigation/c07_policy.py",
        "blob_oid": "c969c4bbf33910fab6ffb36c3bfe184fd42c74c9"
      },
      {
        "path": "src/flowlens/investigation/c07_provider.py",
        "blob_oid": "56ecb9f3d7b5a1917a2354572e8c946f07eb759d"
      },
      {
        "path": "src/flowlens/investigation/c07_summary.py",
        "blob_oid": "3d561da7ab625421bbcf2dcb3785f8fae792cbff"
      }
    ]
  }
]
```

## Protected Git objects

```json
{
  ".env.example": "95384f33192966dc4b1900bf38e3366e8650a06d",
  ".github": "d85309ff678a4a17dafad77d3cac748822257a9b",
  "apps": "597399c7919982e9b2d54fc8b58fe6784cfe8585",
  "docker-compose.yml": "5a0b6e8486edc69f9f79c7e1345a842aa412983c",
  "docs/w03": "cb81e388c6c44a9900575ef2e72161dc0205be94",
  "docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json": "93ebe129f9345ea540b5e06aef053f2a62bb0846",
  "migrations": "c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433",
  "pyproject.toml": "318bbc0a858f760e6c4d7a2d3fdbfcc111febb77",
  "scripts/ci/classify_change.py": "fd9e99c6b55b85f184198c51f0f97ba16323ce32",
  "scripts/ci/pytest_outcome_receipt.py": "c7873d5fa29dc7cef2a85a9d307d16b8d099474b",
  "scripts/ci/run_non_integration_shard.py": "dc4dc3a5ede99832d67a5682a7186aeb0d58c9a6",
  "scripts/ci/verify_non_integration_shards.py": "a375a1d461ae0bf49752716791db6b79c16be38b",
  "scripts/ci/verify_publication.py": "8f97a117f936d9dce91957f7b44551acb5d5c2b6",
  "scripts/ci/verify_w04_source_evolution.py": "4efaefed505e24796a0c2fa545ce4b7eb252d70a",
  "src/flowlens/api": "4d0f47613296d871f70e2dfdab6f21f31b42663a",
  "src/flowlens/data": "d5679d706ed19b0802441b1002af5e5e23513edc",
  "src/flowlens/db": "a3b774f3bcc322ee19951c92948501315b0e7cb2",
  "src/flowlens/decision": "71eddb93cfee5c5e5822d6598ef2f4a1f63648df",
  "src/flowlens/evaluation": "1a474ebe5c80bd771591a17c359c299266081580",
  "src/flowlens/worker": "a66b83c427082a9f07394dba21508f62bf4e0fcc",
  "uv.lock": "619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a"
}
```

## Existing immutable C08 evidence/control objects

```json
{
  "docs/w04/checkpoints/c08/W04_C08_CI_BOOTSTRAP_WEIGHTS.json": "ae581500ad4d6a746e161db29e2ecdc077c2a73c",
  "docs/w04/checkpoints/c08/W04_C08_CONTEXT_LOCK.md": "a914d44fad2d2fe4a9c49f9dd9b8afef997dae27",
  "docs/w04/checkpoints/c08/W04_C08_ENTRY_TEST_BASELINE.json": "8896d9e7af04bb936400e0544f11e4fad367b234",
  "docs/w04/checkpoints/c08/W04_C08_HUMAN_AUTHORIZATION.md": "653a819596b450c5ef80784a72db693bc7b4ba5e",
  "docs/w04/checkpoints/c08/W04_C08_R_DEVELOPMENT_ROUND_REPORT.md": "263d9ff634afc97cb695c31b4e7a00204895f4cf"
}
```

Current manifest blob: `409cd4b600b902cafd0ba7b907968b8775062056`. The only intended manifest differences are C08 state CLOSED, the Stage-B source freeze SHA and its two accepted source blob OIDs. Its C01-C07 prefix and all other fields remain unchanged.

## Exact allowlist

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c08/W04_C08_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md
docs/w04/checkpoints/c08/W04_C08_HUMAN_ACCEPTANCE.md
docs/w04/checkpoints/c08/W04_C08_CLOSEOUT_AUTHORIZATION.md
docs/w04/checkpoints/c08/W04_C08_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/checkpoints/c08/W04_C08_FINAL_CLOSEOUT_REPORT.md
```

Hard stops: context/scope/protected-object/decision drift; candidate proof failure; final native CI failure; synchronization failure. No seventh path or unauthorized checkpoint advance. The final authorization document binds the exact failure codes and required gates. Source runtime, tests, scripts/CI, workflow, weights/timeouts, dependencies/schema/migrations and W03 remain frozen during Phase 2.
