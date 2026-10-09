# W04-C07 Final Closeout Context Lock

Locked from the explicit Human closeout request on 2026-10-08 (Asia/Shanghai), after read-only preflight and before any primary repository mutation. Current approval covers only this six-path closeout and grants no C08 or operational authority. The independent GPT review remains supplied evidence rather than Codex self-review.

## Normative snapshots and authority

| Supplied material | Bytes | SHA-256 |
|---|---:|---|
| W04_C07_CLOSEOUT_TASK_V1.md | 13574 | 6ceb869364c725c40b4654f9704867962f11db5bb0ed042feffec5816c6206cc |
| W04_C07_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md | 4383 | 157b3723768fa87405838fa29d9b614b45ddd4175f58238113f57cfe1e3e4adc |
| W04_C07_HUMAN_ACCEPTANCE_ACCEPTED.md | 1027 | f9bc9b5a8815a4671c4fbfb8770a27d51f92e069e791654dacba159580f790f2 |

Pasted Human request: 17878 bytes; SHA-256 46110fa064951465584af10fbf3b83e6872c342eba89fea1ceff0b2584b18bea. GPT independent implementation review R1 PASS; Critical/High/Blocking Medium NONE. Human C07 acceptance ACCEPTED; decision ACCEPTED; readiness READY. Separate current Human closeout authorization APPROVED / decision APPROVED. Do not request another acceptance or approval within this unchanged scope.

## Verified execution entry and history

| Anchor | SHA | Native CI | Actual class / proof |
|---|---|---|---|
| C06 closeout | 145ac72626899dc30bcff437685b4698b8edacb4 | #115 / 37735563458 / SUCCESS | C / FULL_EXACT_SHA |
| C07 entry | e372b0d8ab038eda936d3a3b9ce4d77bfc8fce29 | #116 / 37749570874 / SUCCESS | UNKNOWN / FULL_EXACT_SHA |
| Stage A | a44e06bed9c3a0ce0ef1ec360777f067e68e26a9 | #117 / 37759205132 / SUCCESS | C / FULL_EXACT_SHA |
| Stage B | c86f7af2370f315b8b7310008521f08ceade6d97 | #118 / 37773147744 / SUCCESS | I / FULL_EXACT_SHA |
| Stage C | 30f0ca941e71750528710f38384bc7a24e1276f6 | #119 / 37794333565 / SUCCESS | P / PUBLICATION_EXACT_SHA |

Before mutation, local HEAD, origin tracking, direct remote feature head and refreshed PR #7 head all equal 30f0ca941e71750528710f38384bc7a24e1276f6; branch feat/w04-evidence-investigation; index and worktree CLEAN. PR OPEN / DRAFT / UNMERGED; base/main af61bdfd5f7cf7961811c4c2dc8e554dd7eed509. Direct remote main matches that accepted anchor. Local history is complete, not shallow.

Stage A is directly on C07 entry; Stage B directly on A; Stage C directly on B. Refreshed native #118 and #119 are overall SUCCESS. Stage C delta is exactly docs/w04/checkpoints/c07/W04_C07_R_DEVELOPMENT_ROUND_REPORT.md. Exact Stage A/B/C subjects are preserved:
- docs(w04-c07): authorize grounded investigation summary
- feat(w04-c07): render grounded investigation summaries
- docs(w04-c07): publish investigation summary proof

## Frozen accepted identities

Runtime source freeze is Stage B c86f7af2370f315b8b7310008521f08ceade6d97.

| Path | Git object |
|---|---|
| src/flowlens/investigation/c07_policy.py | c969c4bbf33910fab6ffb36c3bfe184fd42c74c9 |
| src/flowlens/investigation/c07_provider.py | 56ecb9f3d7b5a1917a2354572e8c946f07eb759d |
| src/flowlens/investigation/c07_summary.py | 3d561da7ab625421bbcf2dcb3785f8fae792cbff |

| Path | Git object |
|---|---|
| tests/test_investigation_summary.py | 6d23ffe9fb3e13c5aa2d9350c865342a54d2c5b9 |
| tests/test_investigation_summary_provider.py | 7cbcdf22221a625c0a8c58d407114487d00d3424 |

Stage C report Git blob: b1a56d399b203876ab2904b056a2c9e9b417c061. It is publication evidence only.

Entry governance blobs:

| Path | Git object |
|---|---|
| docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json | c11759236c6382b4cad1766092f11cf8bd20ce5c |
| docs/w04/checkpoints/c07/W04_C07_HUMAN_AUTHORIZATION.md | 903b3e985ac0428140bce252d8e540ac2ad66498 |
| docs/w04/checkpoints/c07/W04_C07_CONTEXT_LOCK.md | f988f89be26d0c0167b4370b5acb44bc7b233bd0 |

Entry manifest accepted Git-byte SHA-256: 4096431ab26b3a3a58e91a469fa3da4d23478ef9a7ad9e94f951d73fb6354a6e. Precondition: C07 AUTHORIZED / source_freeze_sha null / three blob_oid null; C08 absent. C01-C06 entries are CLOSED and unchanged against C07 entry.

Frozen C01-C06 manifest identities:

| Checkpoint | Source freeze | Source | Git blob |
|---|---|---|---|
| W04-C01 | 084c2fea93d0e021994de015c986de9ff92bf9a3 | src/flowlens/investigation/__init__.py | c23929f85dccd78bc72ef3b2b1415c6e8eaf0452 |
| W04-C01 | 084c2fea93d0e021994de015c986de9ff92bf9a3 | src/flowlens/investigation/contracts.py | 0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e |
| W04-C01 | 084c2fea93d0e021994de015c986de9ff92bf9a3 | src/flowlens/investigation/enums.py | 9c818780423f32f144b18666784ebc9ea3abdccc |
| W04-C02 | 18648915414a26dddbdc904965663730ea631cf2 | src/flowlens/investigation/c02_binding.py | 5f0af237ed465fa83e5a3b84954512b1f3125551 |
| W04-C03 | 42047bcfe6591f7c9ed9b0034bd94467401ba72f | src/flowlens/investigation/c03_planning.py | 21d0055e12d86e6333a836d363d6e266cb0fcbd7 |
| W04-C04 | 6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1 | src/flowlens/investigation/c04_navigation.py | 98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4 |
| W04-C04 | 6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1 | src/flowlens/investigation/c04_queries.py | dc22c7e532a4b62ccfffec2210bc2a6306d97234 |
| W04-C04 | 6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1 | src/flowlens/investigation/c04_registry.py | fbe6f0603d7b0634426ac0034033089eb55af4d7 |
| W04-C05 | 3386b2637f0b0e3f0972a07ee0bea4ad8181cb5f | src/flowlens/investigation/c05_findings.py | 31384426ba9c733bc5bdbf3b09a3d206c8182586 |
| W04-C06 | de02e49af9ada512ff52afdcc5f72620c4f220af | src/flowlens/investigation/c06_human.py | 021f5b72254c87c5b965500727a67001a47ef0bd |
| W04-C06 | de02e49af9ada512ff52afdcc5f72620c4f220af | src/flowlens/investigation/c06_policy.py | 8cfea031eaa764d871822c2e12de019ed3ebc3b9 |
| W04-C06 | de02e49af9ada512ff52afdcc5f72620c4f220af | src/flowlens/investigation/c06_store.py | e99d5d4c36db1dd3ed11c40ff9bbc5b01663ae9a |

Production controls / dependency / Compose blobs:

| Path | Git object |
|---|---|
| .github/workflows/ci.yml | 14c826b122b7103953e8b4539981004241205ba4 |
| docker-compose.yml | 5a0b6e8486edc69f9f79c7e1345a842aa412983c |
| pyproject.toml | 318bbc0a858f760e6c4d7a2d3fdbfcc111febb77 |
| scripts/ci/classify_change.py | fd9e99c6b55b85f184198c51f0f97ba16323ce32 |
| scripts/ci/run_w03_ai_loop_gate.py | c533928e584335437ae8a902fcab4faab64ae8ef |
| scripts/ci/verify_publication.py | 8f97a117f936d9dce91957f7b44551acb5d5c2b6 |
| scripts/ci/verify_w04_source_evolution.py | 4efaefed505e24796a0c2fa545ce4b7eb252d70a |
| uv.lock | 619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a |

Protected tree objects:

| Path | Git object |
|---|---|
| src | 32856501648e4fea75489be8dd467553e9888fd1 |
| tests | 551019c45262ed64834ba1d423549de318eb4453 |
| scripts/ci | b8ded9847fa8c23309bbd1af11847c8b27666685 |
| .github | 978501bf7003ab05e903e22d3930ee5c97470974 |
| docs/w03 | cb81e388c6c44a9900575ef2e72161dc0205be94 |
| migrations | c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433 |
| apps | 597399c7919982e9b2d54fc8b58fe6784cfe8585 |

Only C07 lifecycle fields may change. Preserve schema_version=w04-source-evolution-manifest-v1, policy_id=W04-DEVCTRL-01, w03_baseline_sha=af61bdfd5f7cf7961811c4c2dc8e554dd7eed509, w04_source_root=src/flowlens/investigation, checkpoint ordering and all C01-C06 entries. C07's exact final object binds CLOSED to Stage B and the three accepted runtime blobs.

## Bound execution and proof

Exact six-path allowlist:

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
docs/w04/checkpoints/c07/W04_C07_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md
docs/w04/checkpoints/c07/W04_C07_HUMAN_ACCEPTANCE.md
docs/w04/checkpoints/c07/W04_C07_CLOSEOUT_AUTHORIZATION.md
docs/w04/checkpoints/c07/W04_C07_CLOSEOUT_CONTEXT_LOCK.md
docs/w04/checkpoints/c07/W04_C07_FINAL_CLOSEOUT_REPORT.md
```

Forbidden mutation paths:

```text
src/**
tests/**
scripts/ci/**
.github/**
docs/w03/**
docs/w04/checkpoints/c01/**
docs/w04/checkpoints/c02/**
docs/w04/checkpoints/c03/**
docs/w04/checkpoints/c04/**
docs/w04/checkpoints/c05/**
docs/w04/checkpoints/c06/**
pyproject.toml
uv.lock
docker-compose.yml
migrations/**
apps/**
```

Existing W04_C07_HUMAN_AUTHORIZATION.md, W04_C07_CONTEXT_LOCK.md and W04_C07_R_DEVELOPMENT_ROUND_REPORT.md are frozen. No runtime/test/provider repair, verifier/classifier/workflow repair, upstream semantic change, dependency/migration/operational mutation, main write, merge, branch deletion, amend, rebase, reset, history rewrite, force push or W04-C08 work is authorized.

Use a disposable full-history local clone of the exact Stage C baseline. Apply only these six intended paths and create one local candidate commit directly on Stage C. Never push the disposable commit. Run the unchanged committed-head proof:

```text
python -B -m pytest tests/test_investigation_summary.py::test_s52_committed_source_lifecycle_and_unchanged_production_verifier tests/test_w04_source_evolution.py -p no:cacheprovider --basetemp <fresh-short-temporary-path>
python -B scripts/ci/verify_w04_source_evolution.py --manifest docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json --expected-head <ACTUAL_COMMITTED_HEAD> --repo .
```

Require C07 CLOSED, source freeze exactly Stage B, exact three runtime and two test blobs, C01-C06 unchanged, C08 absent, exact six-path delta, unchanged src/tests/scripts/ci/.github/dependencies, Stage B ancestry, Stage C directly on Stage B and candidate directly on Stage C. Remove the disposable clone after proof. Only then apply the same six files to a reverified clean primary Stage C checkout. Create one real commit and immediately rerun the same unchanged committed-head proof against REAL HEAD before normal push. A frozen-gate failure requires W04_C07_CLOSEOUT_REQUIRES_GPT_CLARIFICATION; no automatic repair.

The real closeout subject is docs(w04-c07): close grounded investigation summary; direct parent is exact Stage C. Normal feature push only. The unchanged native classifier controls the route; expected likely C / FULL_EXACT_SHA. Require the real closeout SHA's own full Classify/Quality/Compose/W03/Verification SUCCESS, Publication SKIPPED and overall SUCCESS. Its generated identity/result belongs in the final handoff, not an amendment of the immutable precommit report.

Hard stops:
- W04_C07_CLOSEOUT_CONTEXT_CHANGED
- W04_C07_CLOSEOUT_REQUIRES_GPT_CLARIFICATION
- W04_C07_CLOSEOUT_CI_FAILED

W04-C08 remains NOT AUTHORIZED. Do not merge PR #7 or delete the feature branch.
