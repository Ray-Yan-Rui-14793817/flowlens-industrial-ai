# FlowLens W04-C01 GPT Clarification-01

## W03 C09 Source-Freeze Compatibility at the W04 Boundary

```text
PROJECT: FlowLens Industrial AI
SPRINT: W04 — Evidence-Grounded Investigation Loop
CHECKPOINT: W04-C01 — Immutable Investigation Contracts
CLARIFICATION: W04-C01-CLARIFICATION-01

ORIGINAL C01 IMPLEMENTATION SHA:
084c2fea93d0e021994de015c986de9ff92bf9a3

CLARIFICATION CLASS:
HARNESS / REGRESSION-COMPATIBILITY ONLY

RUNTIME REPAIR:
NOT AUTHORIZED

W04-C02+:
NOT AUTHORIZED
```

## 1. Finding

Codex correctly stopped after discovering a conflict between:

1. the authorized W04-C01 additive source namespace; and
2. an existing W03 C09 regression assertion that requires the entire `src/`
   tree to remain unchanged relative to the final W03 anchor.

This is a harness compatibility defect at the W03→W04 boundary, not evidence
that the W04-C01 runtime contracts are out of scope.

## 2. Normative Interpretation

For W04-C01, the invariant:

`W03 source remains frozen`

means:

- every source path that existed under `src/` at the verified W03 main anchor
  remains unchanged and undeleted;
- post-W03 additive source is permitted only when explicitly authorized by the
  current checkpoint.

It does NOT mean that no later sprint may ever add a source file under `src/`.

## 3. Exact W04-C01 Additive Allowlist

The only allowed source additions for W04-C01 are exactly:

```text
src/flowlens/investigation/__init__.py
src/flowlens/investigation/contracts.py
src/flowlens/investigation/enums.py
```

No other post-W03 source addition is authorized.

No pre-existing W03 source file may be modified, deleted, renamed, or replaced.

## 4. Required Harness Semantics

Repair the stale C09 source-freeze assertion so it proves BOTH:

### A. W03 baseline preservation

For every source path present under `src/` at:

```text
af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
```

the current state has no modification, deletion, rename, or replacement.

### B. Exact W04-C01 additive boundary

The set of paths added under `src/` after the W03 anchor equals exactly the
three-file allowlist above.

Unexpected addition → FAIL.
Missing authorized addition → FAIL.
Modification/deletion/rename of a W03 baseline source path → FAIL.

## 5. Preferred Mechanism

Prefer Git semantic diff/tree information rather than raw working-tree byte
comparison.

Semantics equivalent to:

```text
git diff --name-status --no-renames <W03_ANCHOR> -- src
```

are acceptable if the test fails closed unless all source changes are exact
authorized additions.

Do not weaken this to a broad `src/flowlens/investigation/**` allowlist.

## 6. Frozen W03 C09 Proof Remains Intact

This clarification does NOT authorize changes to:

```text
docs/w03/checkpoints/c09/specs/c09_gate_manifest.json
scripts/ci/run_w03_ai_loop_gate.py
the 38 frozen C09 selectors
the 10 parameterized-selector identity
the 85 expanded C09 cases
F01-F10 semantics
W03 runtime
W03 contracts
W03 trust semantics
```

If the stale assertion is itself a frozen selector, preserve the selector name
and repair only its internal repository-boundary assertion.

## 7. Runtime Freeze

Do not modify the original C01 runtime implementation at:

```text
084c2fea93d0e021994de015c986de9ff92bf9a3
```

Do not amend that commit.

Repair must be a new commit on the same W04 branch.

No `src/**` change is authorized by this clarification.

## 8. CRLF Clarification

Two locally reported non-integration failures were identified as CRLF
working-tree byte differences.

Do not modify unrelated W03 tests/source for those failures.

If exact-SHA Linux CI does not reproduce them:

```text
record as LOCAL_ENVIRONMENT_ONLY / CRLF
do not repair them
```

If exact-SHA Linux CI reproduces them:

```text
STOP
request a separate GPT clarification with exact selectors and paths
```

## 9. Repair Change Allowlist

Authorized mutation is limited to:

```text
the exact C09 test file containing the stale whole-src assertion
an optional minimal helper in the same test/harness area if strictly necessary
W04-C01 clarification/repair documentation
W04_C01_R_DEVELOPMENT_ROUND_REPORT.md update
```

Not authorized:

```text
any src/** change
W03 gate manifest change
W03 gate runner change
classifier change
CI workflow change
dependency/lockfile change
W04-C02+ code
```

## 10. Post-Repair Proof

At the repair SHA, prove:

```text
W04 H01-H40: PASS
same-process determinism: PASS
fresh-process determinism: PASS

W03 core contract regression: PASS
W03 C09 F01-F10: PASS
W03 frozen selectors: 38 PASS
W03 expanded cases: 85 PASS

Ruff: PASS
strict mypy: PASS
dependency lock: PASS
Docker Compose: PASS
repository Verification: PASS
```

Run the full non-integration suite.

Any new non-CRLF failure is blocking.

## 11. Evidence Chain

Preserve both stages:

```text
ORIGINAL IMPLEMENTATION SHA:
084c2fea93d0e021994de015c986de9ff92bf9a3

ORIGINAL EXACT-SHA CI:
Run #87 / <final result>

GPT CLARIFICATION:
W04-C01-CLARIFICATION-01

REPAIR SHA:
<new sha>

REPAIR EXACT-SHA CI:
<new run/result>

RUNTIME CHANGE IN REPAIR:
NONE

W03 RUNTIME CHANGE:
NONE
```

## 12. Authority State

```text
GPT CLARIFICATION-01:
ISSUED

BOUNDED HARNESS REPAIR:
GPT-APPROVED IN SCOPE

HUMAN REPAIR AUTHORIZATION:
REQUIRED BEFORE MUTATION

GPT INDEPENDENT REVIEW:
NOT YET STARTED

HUMAN C01 ACCEPTANCE:
PENDING

C01 CLOSEOUT:
NOT AUTHORIZED

W04-C02:
NOT AUTHORIZED
```
