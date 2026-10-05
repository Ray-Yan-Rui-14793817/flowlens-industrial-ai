# W04-DEVCTRL-01 Context Lock

Date: 2026-10-05 (Asia/Shanghai). Context locked before implementation.

```text
CONTEXT: LOCKED
TASK: W04-DEVCTRL-01
ENTRY SHA: e95a94152e7b57dd1cdbef95c16ef496a419906e
W03 VERIFIED MAIN: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
C01 SOURCE FREEZE: 084c2fea93d0e021994de015c986de9ff92bf9a3
BRANCH: feat/w04-evidence-investigation
ENTRY WORKTREE / INDEX: CLEAN
PR #7: OPEN / DRAFT / UNMERGED
C01 CLOSEOUT CI: #90 / 37297604459 / SUCCESS
W04-C02: NOT AUTHORIZED
```

Read order: supplied GPT Design Master V1, GPT Design Review R1, Human
Authorization Approved, Codex Task V1; then repository AGENTS/LOOP, applicable
W03 control contracts, current classifier/publication verifier/tests, C09
manifest/runner/test, workflow, and accepted C01 closeout evidence.
The current task explicitly authorizes the bounded post-W03 control work.

## Normative package identities

These are SHA-256 digests of the original ZIP entry bytes. The external package
is read as task material and is not copied into additional repository paths.

| Document | SHA-256 |
|---|---|
| W04_DEVCTRL_01_GPT_DESIGN_MASTER_V1.md | `183625bc709d98ed9ce0385623490124cb0c384e449aaf690c3cc850466c6334` |
| W04_DEVCTRL_01_GPT_DESIGN_REVIEW_R1.md | `74360f87672b2f9a588a27059f7220dfa62b8e08f0535c8c2ccff5f34dcf812e` |
| W04_DEVCTRL_01_HUMAN_AUTHORIZATION_APPROVED.md | `93895fdf28c76f9857d652add8552d9b995a8f0da8e5141828c23ad6a7f76990` |
| W04_DEVCTRL_01_CODEX_TASK_V1.md | `dbfa649a74ab757579cd93b3e1b1e21f13704f4a9330dc144ae0dd17075a7074` |

## Inspected repository controls

Git blob identities bind committed content without platform newline ambiguity.

| Path | Entry Git blob |
|---|---|
| scripts/ci/classify_change.py | `353df45732e77831a3ad92bf6f9a072db7ce3425` |
| scripts/ci/verify_publication.py | `8f97a117f936d9dce91957f7b44551acb5d5c2b6` |
| tests/test_ci_change_classifier.py | `fd3af7526c1d46301b6bf1f3ea55e94d10fbcf33` |
| tests/test_ci_publication_gate.py | `1c0edea523a058b2b0544dc9efb0ccf9af4c0461` |
| tests/test_c09_ci_gate.py | `952cef18bd31829c9897e2dca20df5499f5d6643` |
| .github/workflows/ci.yml | `14c826b122b7103953e8b4539981004241205ba4` |
| docs/w03/checkpoints/c09/specs/c09_gate_manifest.json | `b2a03f3295c162a639eb99dbd87b4a636c3b1e85` |
| scripts/ci/run_w03_ai_loop_gate.py | `c533928e584335437ae8a902fcab4faab64ae8ef` |

The C09 selector
`test_classifier_publication_and_runtime_frozen_materials_unchanged` currently
freezes `classify_change.py`, `verify_publication.py`, `pyproject.toml`, `uv.lock`
and `docker-compose.yml` to W03 C09 entry. Its hardcoded source addition tuple is:

```text
src/flowlens/investigation/__init__.py
src/flowlens/investigation/contracts.py
src/flowlens/investigation/enums.py
```

The normative master and actual Git tree use `__init__.py`; the pasted prompt's
`init.py` transcription is resolved by its explicit normative-master instruction.
Actual C01 source-freeze blobs match all three normative OIDs. All W03 source,
migrations and applications are unchanged against W03 main.

The frozen W03 gate remains F01-F10 / 38 selectors / 85 expanded cases, including
10 parameterized selectors. Runner and manifest identities stay unchanged.

Classifier currently recognizes W03 publication/control paths and generic
source/tests. W04 docs currently fall through to UNKNOWN. It uses only verified
PR synchronize source-head before/after deltas; push/ambiguous boundaries require
FULL_EXACT_SHA. Shared `is_publication_path` is imported by the unchanged
publication verifier, which scans Git content and rejects unsafe boundaries,
non-regular files, whitespace errors, conflicts and unbalanced Markdown fences.

Workflow Verification always runs. P requires Publication SUCCESS and
Quality/Compose/W03 SKIPPED. C/I/F/UNKNOWN require Quality/Compose/W03 SUCCESS
and Publication SKIPPED. Every proof checks exact source HEAD. No workflow
change or proof-strength reduction is authorized or needed.

## Authorized delta and exclusions

```text
docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json
scripts/ci/verify_w04_source_evolution.py
scripts/ci/classify_change.py
tests/test_w04_source_evolution.py
tests/test_ci_change_classifier.py
tests/test_ci_publication_gate.py
tests/test_c09_ci_gate.py
docs/w04/devctrl/W04_DEVCTRL_01_HUMAN_AUTHORIZATION.md
docs/w04/devctrl/W04_DEVCTRL_01_CONTEXT_LOCK.md
docs/w04/devctrl/W04_DEVCTRL_01_R_DEVELOPMENT_ROUND_REPORT.md
```

No runtime source, migrations/apps, dependencies, workflow, W03 manifest/runner,
W1/W2 semantics, runtime HGT, operational facts or C02 implementation changes.
Dataset/scenario/prompt/tool registry changes: NONE; no runtime context is built.
Negative controls use disposable Git repositories and isolated test resources.
Accepted Windows CRLF digest failures remain untouched and must be reported
separately from authoritative exact-SHA Linux CI evidence.

Required proof: D01-D36; focused tests; full C09; W04 H01-H40; W03 core;
F01-F10/38/85; full non-integration/integration; Ruff; strict mypy; dependency
lock; Docker Compose; repository Verification and exact-SHA CI. Counts are
measured after collection. Finish at REVIEW_READY; acceptance/closeout and C02
remain unauthorized.
