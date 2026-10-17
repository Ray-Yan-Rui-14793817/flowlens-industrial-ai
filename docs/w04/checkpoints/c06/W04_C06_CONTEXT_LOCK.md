# W04-C06 implementation context lock

Locked before mutation on 2026-10-07 (Asia/Shanghai).

The current Human request selects Task V1, frozen GPT Design Master V1 and Deep Design Review R1 PASS, and explicitly authorizes this exact C06 implementation. Attached documents provide the selected contract; they do not independently create Human authorization. The current task outranks historical W03 phase-router text. Frozen W1/W2/W03 invariants remain authoritative. Development instructions and test material never become runtime evidence.

## Entry evidence

- HEAD, local tracking, direct remote and refreshed PR head: `3f2ec244d7a6a499d006211206ad0bc10823adac`.
- Entry tree: `c13b7ac3d28a3176864b646d4f935b868c25c415`.
- Branch: `feat/w04-evidence-investigation`; worktree and index clean before writes.
- PR #7: OPEN / DRAFT / UNMERGED; base main/direct remote `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`.
- Refreshed native CI #111 / 37614012787: SUCCESS. Exact source checkout confirmed in classifier log; actual class C / FULL_EXACT_SHA.
- Classify, Quality, Docker Compose, W03 AI loop and Verification PASS; Publication SKIPPED.
- C01-C05 CLOSED; C06 absent. C05 freeze `3386b2637f0b0e3f0972a07ee0bea4ad8181cb5f`, runtime blob `31384426ba9c733bc5bdbf3b09a3d206c8182586`.

## Selected handoff materials

The given Downloads path was absent. The exact named ZIP was found in the user project archive at `C:/Users/C/Desktop/Flowlens_Industrail_AI/Week4/C05/FlowLens_W04_C06_GPT_CODEX_HANDOFF_V1.zip` and read directly without repository extraction. Supplied approval is materialized byte-for-byte.

Archive SHA-256: `4c72c919fab8f9e3fc7070c314811eeab8905afe60abed150269a1f5c3d3f54f`.

| Material | Bytes | SHA-256 |
|---|---:|---|
| `W04_C06_CODEX_PROMPT_V1.md` | 20136 | `be4b7ff3e067075ad6a2412e46603e00255adcb4407433767d6ae7c3ce6ad3a1` |
| `W04_C06_CODEX_TASK_V1.md` | 13112 | `d62c3a4f24a39029c9aacf46983339be71bc124c8f690ed5ff576fe1ea2437d7` |
| `W04_C06_GPT_DEEP_REVIEW_R1.md` | 5634 | `476cca3a39265696a9ab9c754f5b431f258fbd76a7032c3358cbe3cb2e5e4c5d` |
| `W04_C06_GPT_DESIGN_MASTER_V1.md` | 24645 | `7f1d30711f1bbfd50ec68c797df3fe821e4a08877eb3d052832fe2d7213f5fdb` |
| `W04_C06_HUMAN_AUTHORIZATION_APPROVED.md` | 1447 | `0154ea5ad61464c3f43a55539dab6c0db27a85b8717672c0adcd39d1ca3cf63a` |
| `W04_C06_PACKAGE_MANIFEST.md` | 977 | `1eae3583e42e440d4136d150fa11edcb8af2a9f7d6a8ed27cfc9b4c8f4e1c590` |

## Exact entry Git blobs

| Path | Git blob |
|---|---|
| `AGENTS.md` | `173a9a8c3f3ac3e2c964f52fd8a7551bc48d5241` |
| `LOOP.md` | `7276d50e499bc48b67c5619aaa26f09c46bb7b7e` |
| `docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json` | `da30eb5ed9f799873ee37e422061718f2f8a9ebf` |
| `src/flowlens/investigation/__init__.py` | `c23929f85dccd78bc72ef3b2b1415c6e8eaf0452` |
| `src/flowlens/investigation/contracts.py` | `0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e` |
| `src/flowlens/investigation/enums.py` | `9c818780423f32f144b18666784ebc9ea3abdccc` |
| `src/flowlens/investigation/c02_binding.py` | `5f0af237ed465fa83e5a3b84954512b1f3125551` |
| `src/flowlens/investigation/c03_planning.py` | `21d0055e12d86e6333a836d363d6e266cb0fcbd7` |
| `src/flowlens/investigation/c04_navigation.py` | `98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4` |
| `src/flowlens/investigation/c04_queries.py` | `dc22c7e532a4b62ccfffec2210bc2a6306d97234` |
| `src/flowlens/investigation/c04_registry.py` | `fbe6f0603d7b0634426ac0034033089eb55af4d7` |
| `src/flowlens/investigation/c05_findings.py` | `31384426ba9c733bc5bdbf3b09a3d206c8182586` |
| `tests/test_w04_source_evolution.py` | `7d8df8f6b63925ebe22ce22220d67c4891e3be38` |
| `src/flowlens/decision/c06_human.py` | `82be7b65de14c4ff8101721b3ba88e4c8ffed298` |
| `src/flowlens/decision/c06_validation.py` | `9fabdf1ed67a02b768db9ecfaf4e84f5ddd67bb4` |
| `src/flowlens/decision/c06_store.py` | `29437080c3c185c97192e2bd2802a34179f724aa` |
| `src/flowlens/decision/c06_policy.py` | `923175390b8c95bc308a1de510ba9c7a8b60520f` |
| `scripts/ci/verify_w04_source_evolution.py` | `4efaefed505e24796a0c2fa545ce4b7eb252d70a` |
| `scripts/ci/classify_change.py` | `fd9e99c6b55b85f184198c51f0f97ba16323ce32` |
| `scripts/ci/run_w03_ai_loop_gate.py` | `c533928e584335437ae8a902fcab4faab64ae8ef` |
| `scripts/ci/verify_publication.py` | `8f97a117f936d9dce91957f7b44551acb5d5c2b6` |
| `.github/workflows/ci.yml` | `14c826b122b7103953e8b4539981004241205ba4` |
| `pyproject.toml` | `318bbc0a858f760e6c4d7a2d3fdbfcc111febb77` |
| `uv.lock` | `619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a` |
| `docker-compose.yml` | `5a0b6e8486edc69f9f79c7e1345a842aa412983c` |
| `docs/w03/AI_LOOP_CONSTITUTION.md` | `83bdae9c6511237397811b604d9562420ec40c0f` |
| `docs/w03/SEMANTIC_TRUST_CONTRACT.md` | `e120f4a8cd2f37e0f6084b86e6e606958c6ba68b` |

## Protected tree identities

| Path | Git tree |
|---|---|
| `src/flowlens/investigation` | `a8ce62b3d32102b74e2a3ca41b78d5bd8e2e149f` |
| `src/flowlens/decision` | `71eddb93cfee5c5e5822d6598ef2f4a1f63648df` |
| `src/flowlens/db` | `a3b774f3bcc322ee19951c92948501315b0e7cb2` |
| `src/flowlens/data` | `d5679d706ed19b0802441b1002af5e5e23513edc` |
| `scripts/ci` | `b8ded9847fa8c23309bbd1af11847c8b27666685` |
| `.github` | `978501bf7003ab05e903e22d3930ee5c97470974` |
| `docs/w03` | `cb81e388c6c44a9900575ef2e72161dc0205be94` |
| `migrations` | `c5a7cff7524c29b70cfe4265ed7b2cdb8eabd433` |
| `apps` | `597399c7919982e9b2d54fc8b58fe6784cfe8585` |

## Closed C01-C05 source identities

| Checkpoint | Freeze commit | Path | Blob |
|---|---|---|---|
| W04-C01 / CLOSED | `084c2fea93d0e021994de015c986de9ff92bf9a3` | `src/flowlens/investigation/__init__.py` | `c23929f85dccd78bc72ef3b2b1415c6e8eaf0452` |
| W04-C01 / CLOSED | `084c2fea93d0e021994de015c986de9ff92bf9a3` | `src/flowlens/investigation/contracts.py` | `0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e` |
| W04-C01 / CLOSED | `084c2fea93d0e021994de015c986de9ff92bf9a3` | `src/flowlens/investigation/enums.py` | `9c818780423f32f144b18666784ebc9ea3abdccc` |
| W04-C02 / CLOSED | `18648915414a26dddbdc904965663730ea631cf2` | `src/flowlens/investigation/c02_binding.py` | `5f0af237ed465fa83e5a3b84954512b1f3125551` |
| W04-C03 / CLOSED | `42047bcfe6591f7c9ed9b0034bd94467401ba72f` | `src/flowlens/investigation/c03_planning.py` | `21d0055e12d86e6333a836d363d6e266cb0fcbd7` |
| W04-C04 / CLOSED | `6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1` | `src/flowlens/investigation/c04_navigation.py` | `98354c6bd4eef8592d1de2ca4cf8705e2f32e3b4` |
| W04-C04 / CLOSED | `6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1` | `src/flowlens/investigation/c04_queries.py` | `dc22c7e532a4b62ccfffec2210bc2a6306d97234` |
| W04-C04 / CLOSED | `6a8a14cd382dd43d1d0a74c16819f41eb36cd1c1` | `src/flowlens/investigation/c04_registry.py` | `fbe6f0603d7b0634426ac0034033089eb55af4d7` |
| W04-C05 / CLOSED | `3386b2637f0b0e3f0972a07ee0bea4ad8181cb5f` | `src/flowlens/investigation/c05_findings.py` | `31384426ba9c733bc5bdbf3b09a3d206c8182586` |

## Frozen implementation semantics

Every build/validate/load/record operation admits the full exact nine-argument C05 context through unchanged validate_findings_conflicts_uncertainty, mapping upstream failure to C06_INVALID_REVIEW_CONTEXT. C06 never repairs C05 or reruns C04 navigation. Use only frozen C01 HumanInvestigationEvent and closed HumanInvestigationOutcome; no public bundle, schema/enum/provenance/action field.

Human fields are explicit exact types, stripped opaque text, aware time at/after case opening and parent, sorted unique tuple reference subsets. All five outcomes preserve exact Design Master coverage/status rules. REVIEW_COMPLETE is review coverage only; MORE_EVIDENCE_REQUIRED grants no navigation. HUMAN_NOTE_NON_EVIDENCE is fixed and inert even for SQL/shell/prompt/JSON/HGT/path/causal/remedy/operational text. No note parsing or upstream mutation.

Validate original event structure/identity/hash before detached reconstruction/canonical comparison. Parent is None or exact valid same-case previous event; timestamps are nondecreasing. Journal record owns exact unique-tail selection. Trusted root is explicit absolute pre-existing directory, resolved once; paths contain only validated canonical case/event IDs. Canonical files are exact event.to_json().encode('utf-8') plus one LF. Reject symlinks, unexpected/pending files, noncanonical/corrupt bytes and ambiguous/corrupt graphs.

Atomic per-case directory lock fails immediately BUSY; no wait/retry/clock/stale-lock deletion. Append creates only its own exclusive pending file, writes/flushes/fsyncs and renames once. Never rewrite/delete committed events; clean only own pending file. Exact-tail retry returns tail unchanged; changed request appends one event. Human runtime is pure; store filesystem is limited to this trusted audit root. No DB/network/model/HGT/subprocess/env/random/clock/C04 execution/C07/operational capability.

Versions: w04-c06-human-v1, w04-c06-store-v1, w04-c06-workflow-v1; producer flowlens.investigation.c06_human. Sixteen stable errors and C06HumanInvestigationError(ValueError) are frozen by selected design.

## Authorized stages and gates

A: exactly manifest + Human authorization + this Context Lock. Append C06 AUTHORIZED/null freeze/three exact null blobs. Runtime files absent. Commit docs(w04-c06): authorize human investigation workflow; normal push; exact-SHA Verification PASS before Stage B files.

B: exactly c06_human.py, c06_policy.py, c06_store.py and the two new tests named in Task V1; Stage A files frozen. Direct J01-J48, actual measured counts, inherited C01-C05/DEVCTRL/W03 core/F01-F10/38/85, complete native non-integration/integration, Ruff, strict mypy, lock, Compose and Verification proof. Commit feat(w04-c06): record append-only human investigation review; normal push; exact-SHA full proof PASS before Stage C.

C: only W04_C06_R_DEVELOPMENT_ROUND_REPORT.md after Stage B PASS. Actual evidence and honest audit-storage limitations. Commit docs(w04-c06): publish human investigation proof; normal push; required exact-SHA Publication/Verification PASS; stop REVIEW_READY.

Nine total tracked paths only. C06 manifest remains AUTHORIZED/null freeze/three null blobs. Harness must prove AUTHORIZED and future exact CLOSED three-source shape without repository closeout. No C01-C05/W03/DB/data/production verifier/classifier/workflow/dependency/Compose/migrations/apps mutation, main write, merge, branch deletion or history rewrite. C06 closeout and C07 NOT AUTHORIZED. Context change/stage failure/out-of-scope need uses exact task stop codes.

## Environment and evidence limits

Sandbox process setup failed; mandatory reads use the approved scoped escalation fallback. Existing .venv Python 3.12.14 is retained. GitHub connector refresh supplies PR/run metadata because gh is absent from PATH. No dependencies or production configuration changed. Native exact-SHA Linux CI remains required for PostgreSQL, Compose and complete regression; local Windows evidence will be reported separately and honestly.
