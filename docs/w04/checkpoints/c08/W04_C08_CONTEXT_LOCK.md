# W04-C08 Context Lock

Locked before implementation on 2026-10-11 (Asia/Shanghai). All activation facts were independently verified before repository content writes. Local collection used Python 3.12 / pytest 9.1.1, -B and no cache provider. Native #126 supplied current exact-SHA outcomes; the direct origin/main refs, PR metadata, run number/status and classifier were freshly read. C01-C07 CLOSED entries and both freeze/entry source blobs match. DEVCTRL-02 closure is effective through its own #126 terminal SUCCESS and synchronized heads.

Task raw SHA-256: c63a71cdf1a1a66ec75aabf3ae2d56d0f98b73ff2ba03894997971c09f80e106; raw byte size: 37097.

```json
{
  "status": "LOCKED",
  "entry_sha": "9afc4bd047bd4e52dfc4956f16e6420b3762301f",
  "tracking_feature_head": "9afc4bd047bd4e52dfc4956f16e6420b3762301f",
  "direct_origin_feature_head": "9afc4bd047bd4e52dfc4956f16e6420b3762301f",
  "pr_7_head": "9afc4bd047bd4e52dfc4956f16e6420b3762301f",
  "branch": "feat/w04-evidence-investigation",
  "main_and_pr_base": "af61bdfd5f7cf7961811c4c2dc8e554dd7eed509",
  "pr_state": "OPEN / DRAFT / UNMERGED",
  "worktree_and_index": "CLEAN",
  "tracking_ahead_behind": [
    0,
    0
  ],
  "entry_ci": {
    "run_number": 126,
    "run_id": 38114263650,
    "head_sha": "9afc4bd047bd4e52dfc4956f16e6420b3762301f",
    "status": "completed",
    "conclusion": "success",
    "class": "C",
    "proof": "FULL_EXACT_SHA",
    "url": "https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/38114263650"
  },
  "devctrl_02": "CLOSED / VERIFIED / GITHUB SYNCHRONIZED",
  "c08_at_entry": "ABSENT",
  "c01_c07_source_freezes": [
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
  ],
  "entry_proof": {
    "schema_version": "w04-c08-entry-test-baseline-v1",
    "entry_sha": "9afc4bd047bd4e52dfc4956f16e6420b3762301f",
    "pytest_version": "9.1.1",
    "marker_expression": "not integration",
    "selected_node_count": 2807,
    "nodeids_sha256": "4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d",
    "selected_file_count": 62,
    "selected_files_sha256": "72f381af0f729834fc58920eec74f2ef1a6f9fb0991c7489350412fdfcf7366a",
    "baseline_run_number": 126,
    "baseline_run_id": 38114263650
  },
  "nonintegration_passed": 2804,
  "accepted_linux_skips": 3,
  "integration_selected_and_passed": 70,
  "integration_nodeids_sha256": "bdcb72ebf947f5599d9e6cecf9bc29e65e9cb063daa03a715b41f5399ecf581c",
  "base_weights_sha256": "315675b184abd56422f469a44da5f840b40d82c3cfb272d46873afd7a8adacca",
  "bootstrap_sha256": "36f1d85e34344afee1f7e76b066427e4f40314c68f1d564340d82cc4dd44becb",
  "effective_file_weights_sha256": "352e6e1060bc1c2d5ce9a36fcad6cb9941e373bfae3da4d8a326d26a0d1f01c6",
  "protected_git_objects": {
    ".github/workflows/ci.yml": "68671597decb139416072346010efb23b6e639a3",
    "scripts/ci/classify_change.py": "fd9e99c6b55b85f184198c51f0f97ba16323ce32",
    "scripts/ci/verify_publication.py": "8f97a117f936d9dce91957f7b44551acb5d5c2b6",
    "scripts/ci/verify_w04_source_evolution.py": "4efaefed505e24796a0c2fa545ce4b7eb252d70a",
    "scripts/ci/pytest_outcome_receipt.py": "c7873d5fa29dc7cef2a85a9d307d16b8d099474b",
    "scripts/ci/run_non_integration_shard.py": "dc4dc3a5ede99832d67a5682a7186aeb0d58c9a6",
    "scripts/ci/verify_non_integration_shards.py": "a375a1d461ae0bf49752716791db6b79c16be38b",
    "docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json": "93ebe129f9345ea540b5e06aef053f2a62bb0846",
    "docs/w04/devctrl-02/W04_DEVCTRL_02_ENTRY_TEST_BASELINE.json": "222d3f8fe6eaacc6013259a68498a399f44af144",
    "src/flowlens/decision": "71eddb93cfee5c5e5822d6598ef2f4a1f63648df",
    "src/flowlens/evaluation": "1a474ebe5c80bd771591a17c359c299266081580",
    "src/flowlens/data": "d5679d706ed19b0802441b1002af5e5e23513edc",
    "src/flowlens/db": "a3b774f3bcc322ee19951c92948501315b0e7cb2",
    "src/flowlens/api": "4d0f47613296d871f70e2dfdab6f21f31b42663a",
    "src/flowlens/worker": "a66b83c427082a9f07394dba21508f62bf4e0fcc",
    "docs/w03": "cb81e388c6c44a9900575ef2e72161dc0205be94",
    "migrations": "c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433",
    "apps": "597399c7919982e9b2d54fc8b58fe6784cfe8585",
    "pyproject.toml": "318bbc0a858f760e6c4d7a2d3fdbfcc111febb77",
    "uv.lock": "619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a",
    "docker-compose.yml": "5a0b6e8486edc69f9f79c7e1345a842aa412983c",
    "tests/test_investigation_summary.py": "ea9bb7001540c024b75a2c27e606a263c69c7aea",
    "tests/test_investigation_summary_provider.py": "7cbcdf22221a625c0a8c58d407114487d00d3424",
    "AGENTS.md": "173a9a8c3f3ac3e2c964f52fd8a7551bc48d5241",
    "LOOP.md": "7276d50e499bc48b67c5619aaa26f09c46bb7b7e",
    "docs/CURRENT_STATE.md": "dea24153ea5c0283e890acbcf4929ff8fc9f927a",
    "docs/context/CONTEXT_INDEX.md": "05c5390950ac8e3f1e7e606b76c1f7f7601af389",
    "docs/context/MATERIAL_REGISTRY.md": "01f22882e0fc328e9e2af7327c4a7c8bc2160bf6"
  },
  "stage_a_allowlist": [
    "docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json",
    "docs/w04/checkpoints/c08/W04_C08_HUMAN_AUTHORIZATION.md",
    "docs/w04/checkpoints/c08/W04_C08_CONTEXT_LOCK.md",
    "docs/w04/checkpoints/c08/W04_C08_ENTRY_TEST_BASELINE.json",
    "docs/w04/checkpoints/c08/W04_C08_CI_BOOTSTRAP_WEIGHTS.json"
  ],
  "stage_b_allowlist": [
    "src/flowlens/investigation/c08_policy.py",
    "src/flowlens/investigation/c08_replay.py",
    "tests/test_investigation_replay.py",
    "scripts/ci/plan_non_integration_shards.py",
    "tests/test_ci_test_sharding.py"
  ],
  "stage_c_allowlist": [
    "docs/w04/checkpoints/c08/W04_C08_R_DEVELOPMENT_ROUND_REPORT.md"
  ],
  "stop_codes": [
    "W04_C08_CONTEXT_CHANGED",
    "W04_C08_ENTRY_BASELINE_DRIFT",
    "W04_C08_SCOPE_VIOLATION",
    "W04_C08_MANIFEST_DRIFT",
    "W04_C08_CI_ADMISSION_DRIFT",
    "W04_C08_PROTECTED_BOUNDARY_VIOLATION",
    "W04_C08_REQUIRES_GPT_CLARIFICATION",
    "W04_C08_STAGE_A_CI_FAILED",
    "W04_C08_STAGE_B_CI_FAILED",
    "W04_C08_STAGE_C_CI_FAILED",
    "W04_C08_SYNC_FAILED"
  ]
}
```

Runtime C08 admits frozen artifacts only. No HGT, live provider, database refresh, journal/filesystem/environment/clock/random access, operational mutation, dependency/schema/migration change, upstream semantic repair, history rewrite or main write is authorized. Stage A/B/C SHAs and CI results do not yet exist and are not forecast here. Native failure stops without an automatic pushed repair.
