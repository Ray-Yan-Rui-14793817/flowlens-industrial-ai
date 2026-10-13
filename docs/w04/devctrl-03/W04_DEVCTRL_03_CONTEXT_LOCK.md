# W04-DEVCTRL-03 context lock

STATE: LOCKED BEFORE IMPLEMENTATION; native proof for the new commit is pending.

Human authorization: V1 plus Clarification-01; both exact raw task seals verified.
Fresh origin fetch and direct-origin reads passed before repository writes.

| Preflight | Locked result |
|---|---|
| local / tracking / direct-origin / PR head | a18e7f0733079ecc9aebdd94458625011e2f93f9 |
| branch | feat/w04-evidence-investigation |
| PR #7 | OPEN / DRAFT / UNMERGED |
| main / PR base | af61bdfd5f7cf7961811c4c2dc8e554dd7eed509 |
| index / worktree; ahead / behind | CLEAN; 0 / 0 |
| latest feature native proof | #133 / 38205524984 / SUCCESS / C / FULL_EXACT_SHA |
| source-evolution manifest | C01-C08 CLOSED; AUTHORIZED none; C09 ABSENT |

## Exact Stage-A scope

- `.github/workflows/ci.yml`
- `scripts/ci/plan_non_integration_shards.py`
- `tests/test_ci_test_sharding.py`
- `tests/test_investigation_replay.py`
- `docs/w04/devctrl-03/W04_DEVCTRL_03_AUTHORIZATION.md`
- `docs/w04/devctrl-03/W04_DEVCTRL_03_CONTEXT_LOCK.md`
- `docs/w04/devctrl-03/W04_DEVCTRL_03_MEASURED_SHARD_WEIGHTS.json`

An eighth path is forbidden. Stage B permits only
`docs/w04/devctrl-03/W04_DEVCTRL_03_R_DEVELOPMENT_ROUND_REPORT.md`.

## Accepted measurement provenance

The previous attempt independently downloaded, sealed and derived the following
three native aggregate artifacts. The Human accepted those measurements in
Clarification-01. This continuation verified the unchanged ZIP, JUnit, receipt
and saved derivation seals and reused the measurements without re-deriving or
reinterpreting them.

Saved derivation SHA-256:
`676da9ab5981e6b81d4d3fc0e0d093f0437cc2849e3d6b5af2f9d0bfafd780ca`.

- #129 / 38153792599, HEAD `1fa7b505980c1efc1b3725cd57a9732e254bccdf`, aggregate artifact 11708692092; ZIP `cea81ba21787d1c8e8d32591a36ef6a6336e163c6c135bb2b26d608ca6122685`; JUnit `0c4f2633c1e43fe6c2f3e868b59eb7509c1f7393d001cf038650d655a7564875`; receipt seal `d0b14deb926bc021dddf2a88c68de506079f5c87889528024e304c1413c5b675`; plan `bd2c2c6bf0839bb98f42009f31c86232e68cfe481df3c46f381dfc7224d11a92`.
- #132 / 38200544252, HEAD `0047bb942e8e4227af8d6fb5c9a4763688a22aab`, aggregate artifact 11725204097; ZIP `c0721ca64c9d2e59e59560681c5531e840768a623ed4ee07b612104002ad9c58`; JUnit `d2f5ea4e07c48ff1891cd45cd51a3056f96d538d6916a98470c4dbab6258a4de`; receipt seal `f848f66caa0c4fde2bc4d1ab463dc658709af8e57aea5aeaac72ddcdeac132e5`; plan `99d5c25805edf5904acde6b4fda39f92883c9f4323990aa0547f675b4580ca43`.
- #133 / 38205524984, HEAD `a18e7f0733079ecc9aebdd94458625011e2f93f9`, aggregate artifact 11727789439; ZIP `d4329c5f686d3ec027b8b3aace75f58d4614225f286e629dbedb0664d7b1c1c8`; JUnit `a18e886433b2d737ac071bfbb5959d8c76349633923eb998b41cc58bee4846e5`; receipt seal `3762f815e9cee1bf5773ea10092fd02d86a89c27a662e74ee37cd954bf0fb78a`; plan `45b28233eb71574b78ae737366bbdd5561a2a8e6ed28dae5cff81fd453a38c36`.

Each proves 2997 selected / 2994 passed / 3 accepted skipped / 0 failed, error,
xfail or xpass; 63 files; entry no-loss, exact union and exact once PASS.

Current node digest:
`9d0d6fad74a8336b6dfd32004eb13e71409f1649f1422a866cb77c13842a2a6a`.
Entry #126 no-loss baseline remains 2807 nodes / 62 files and digest
`4f74c17af44363fe14bbda36dd4bb5f2166162d941291bf8e383a29532349c3d`.
No nodes may be added, removed or renamed during DEVCTRL-03.

## Active measured contract

Exact median of per-file JUnit testcase-duration sums from successful full exact-SHA runs #129, #132 and #133, in that order, with identical 2997-node collection. Integer millisecond arithmetic; no averaging, smoothing or overrides.

Measured self-seal: `a4558bd57d259a573cf305fd03dc1968fe6c5ac98b7b280c328332ac3816a851`.
Measured per-file evidence digest: `02f10337b19aa1e895a2bae6e4edb734abf379f55764133c07d4a0679871d9b7`.
Measured effective millisecond digest: `cb646fa14756be9ea598c26309d291684f520dc76286416e28ddcc40f111f0cd`.

Old effective scheduling total: 7733.243s. New exact median total: 9645.665s.
The old #122 base and C08 bootstrap files remain immutable historical evidence.
Neither contributes to active scheduling.

Hot-file samples in #129/#132/#133 order: 3082.523 / 2040.544 / 1658.888s.
Median: 2040.544s; observed maximum: 3082.523s.

New plan schema: `w04-devctrl03-non-integration-plan-v1`.
Seven file-atomic deterministic LPT shards; descending milliseconds then path;
lowest-load then lowest-ID shard tie-break. No hard-coded file assignments.
Exact 63-file model; missing/extra/unmodeled files fail closed.

LPT estimates: 2040.544 / 1784.313 / 1624.916 / 1056.117 /
1046.586 / 1046.586 / 1046.603s.
The replay, human-store, summary and findings files become singleton shards
0 through 3 naturally.

Historical maxima: #129 3143.457 -> 3082.523s;
#132 2235.256 -> 2040.544s; #133 2181.682 -> 1784.313s. No regression.

## Workflow and C08 harness exception

Only the non-integration job timeout changes: 55 -> 65 minutes.
Seven shards, fail-fast=false, max-parallel=7, job/step topology and all action
pins remain exact. R43 removes only the old workflow-tree equality from its
generic protected tuple and substitutes byte-exact derivation from the
DEVCTRL-03 entry workflow. Both trees must have exactly ci.yml. R46 requires
the new active schema and measured self-seal; all native checks remain.

Worst observed file 3082.523s + maximum observed job overhead 46.440s =
3128.963s isolated floor estimate. The 55-minute ceiling has 171.037s
(~5.2% of its ceiling) remaining; 65 minutes has 771.037s (~24.6% of the
observed floor). Runner variance and file atomicity remain. Native Stage A
must succeed with longest shard job strictly below 3300s.

C08 runtime source freeze remains
`1fa7b505980c1efc1b3725cd57a9732e254bccdf`. Source blobs:
`273d288cf4b0e55b646cd2e6751f0259e463a5ff` and
`4fa391cf751377305315b7de8303ce94e6eb6c6e`.

## Protected entry Git objects

| Path | Entry Git object |
|---|---|
| `src` | `db9ce58336ff8ae4d4e051fa58f687d23db27987` |
| `docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json` | `8a4555dba4bfbe6556f19413d323f8b1761ebd54` |
| `docs/w04/checkpoints/c01` | `158218fdd671c197e9f386315e64994fdc289675` |
| `docs/w04/checkpoints/c02` | `2645a039994d69535e465d3534cfd0ede72e09ca` |
| `docs/w04/checkpoints/c03` | `f62d380d020d04bc99a3fbc04eed93c6bc9123ad` |
| `docs/w04/checkpoints/c04` | `2b65286564703849b82c3edf9ecc0d0f6cab0755` |
| `docs/w04/checkpoints/c05` | `deeeb975873ea690ca10a5ad14243754340763fd` |
| `docs/w04/checkpoints/c06` | `a71b2a38cee9fe7ff837324593e72dd51f2ea46a` |
| `docs/w04/checkpoints/c07` | `6811f6b7540b248324b495e0d631004f5bbaf3b6` |
| `docs/w04/checkpoints/c08` | `f47ae8e4304c9bf638aad7030b6ce04d341ce077` |
| `docs/w04/devctrl-02/W04_CI_TEST_SHARD_WEIGHTS.json` | `93ebe129f9345ea540b5e06aef053f2a62bb0846` |
| `docs/w03` | `cb81e388c6c44a9900575ef2e72161dc0205be94` |
| `migrations` | `c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433` |
| `apps` | `597399c7919982e9b2d54fc8b58fe6784cfe8585` |
| `pyproject.toml` | `318bbc0a858f760e6c4d7a2d3fdbfcc111febb77` |
| `uv.lock` | `619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a` |
| `docker-compose.yml` | `5a0b6e8486edc69f9f79c7e1345a842aa412983c` |
| `scripts/ci/classify_change.py` | `fd9e99c6b55b85f184198c51f0f97ba16323ce32` |
| `scripts/ci/verify_publication.py` | `8f97a117f936d9dce91957f7b44551acb5d5c2b6` |
| `scripts/ci/run_w03_ai_loop_gate.py` | `c533928e584335437ae8a902fcab4faab64ae8ef` |
| `scripts/ci/run_non_integration_shard.py` | `dc4dc3a5ede99832d67a5682a7186aeb0d58c9a6` |
| `scripts/ci/pytest_outcome_receipt.py` | `c7873d5fa29dc7cef2a85a9d307d16b8d099474b` |
| `scripts/ci/verify_non_integration_shards.py` | `a375a1d461ae0bf49752716791db6b79c16be38b` |
| `scripts/ci/verify_w04_source_evolution.py` | `4efaefed505e24796a0c2fa545ce4b7eb252d70a` |

All other tracked paths also remain unchanged under the exact allowlist.
No src, checkpoint evidence, manifest, dependency, migration, schema, data,
evaluation, HGT, W03 or product-runtime change is authorized.

## Proof and completion boundary

Run V1 CI/source-evolution tests, Clarification-01 R43/R46 controls and full
167-case C08 replay proof; Ruff and strict mypy; exact 2997-node / 63-file plan;
node-set and protected-object comparison; git diff --check.

R43 validates committed HEAD bytes, so before the implementation-branch commit
these Git-aware tests run in a disposable full-history local clone with the
exact seven candidate files committed there. That clone is never pushed.
The feature branch receives exactly one normal Stage-A commit and one push.

After Stage-A native SUCCESS: capture actual seven timings; verify all full
gates and 2997/2994/3, integration 70, W03 38/85; require longest job <55m;
rerun R46 with original real native ZIP artifacts and exact run/head metadata.
Only then publish the sole Stage-B report and wait for its own native SUCCESS.

Final boundary: W04_DEVCTRL_03_REVIEW_READY; independent GPT review PENDING;
Human acceptance PENDING; DEVCTRL-03 closeout NOT AUTHORIZED.
C09, merge and main write remain NOT AUTHORIZED.
