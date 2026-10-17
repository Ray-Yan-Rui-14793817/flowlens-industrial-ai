# W04-C01 Codex Compatibility Repair Task V1

```text
TASK: W04-C01-REPAIR-01
PARENT IMPLEMENTATION SHA:
084c2fea93d0e021994de015c986de9ff92bf9a3

GPT AUTHORITY:
W04-C01-CLARIFICATION-01

REPAIR TYPE:
HARNESS-ONLY

RUNTIME MUTATION:
PROHIBITED

HUMAN REPAIR AUTHORIZATION:
REQUIRED BEFORE MUTATION
```

Read `W04_C01_GPT_CLARIFICATION_01.md` as normative.

## Preflight

Run:

```bash
git status --short
git rev-parse HEAD
git branch --show-current
git log --oneline --decorate -n 20
```

Confirm the branch contains:

```text
084c2fea93d0e021994de015c986de9ff92bf9a3
```

Do not amend it.

Record final status of original Exact-SHA CI Run #87 if available.

Verify explicit Human authorization for:

```text
W04-C01-REPAIR-01
```

If absent, stop with:

```text
W04_C01_REPAIR_01_HUMAN_AUTHORIZATION_REQUIRED
```

## Locate exact stale assertion

Locate the C09 test/selector that rejects W04 source additions because it
requires the whole `src/` tree to equal the W03 anchor.

Record:

```text
test file
test selector
line/range
current semantics
whether selector is frozen in C09 manifest
```

Do not modify the C09 manifest.

## Required repair

New invariant:

```text
All source paths existing at the W03 anchor remain unchanged/undeleted.

The exact only W04-C01 additions under src/ are:
- src/flowlens/investigation/__init__.py
- src/flowlens/investigation/contracts.py
- src/flowlens/investigation/enums.py
```

Use Git semantic diff/tree comparison where possible.

Fail on:

```text
M/D/R/C for W03 baseline source
unexpected A path
missing expected C01 A path
```

Preserve selector name if frozen.

## Hard boundary

Do not modify:

```text
src/**
docs/w03/checkpoints/c09/specs/c09_gate_manifest.json
scripts/ci/run_w03_ai_loop_gate.py
.github/workflows/**
scripts/ci/classify_change.py
dependencies/lockfile
```

## CRLF failures

Do not repair unrelated CRLF-only local failures.

If exact-SHA Linux CI passes those selectors, record them as local-only.

If exact-SHA Linux CI fails them, stop for separate GPT clarification.

## Proof after repair

Run:

```text
affected C09 selector
full W03 C09 gate
38 frozen selectors / 85 expanded cases
W04 H01-H40
W03 core regression
full non-integration suite
Ruff
strict mypy
dependency verification
Docker Compose
repository Verification
```

Any unexpected non-CRLF failure blocks completion.

## Commit / CI

Create a NEW repair commit.

Do not amend the original implementation SHA.

Push the same W04 branch / update draft PR #7.

Obtain exact-SHA CI for the repair SHA.

## Report

Update:

```text
docs/w04/checkpoints/c01/W04_C01_R_DEVELOPMENT_ROUND_REPORT.md
```

with original implementation + Clarification-01 + repair evidence.

Final handoff must include:

```text
W04-C01 REPAIR-01 COMPLETE

ORIGINAL IMPLEMENTATION SHA:
084c2fea93d0e021994de015c986de9ff92bf9a3

ORIGINAL CI #87:
<result>

GPT CLARIFICATION:
W04-C01-CLARIFICATION-01

REPAIR SHA:
<sha>

REPAIR CHANGE:
HARNESS ONLY

AFFECTED C09 SELECTOR:
<selector>

W03 BASELINE SOURCE PRESERVATION:
PASS

W04-C01 EXACT ADDITIVE SOURCE ALLOWLIST:
PASS

W04 H01-H40:
PASS

W03 C09 F01-F10 / 38 / 85:
PASS

FULL NON-INTEGRATION:
<result>

CRLF LOCAL-ONLY:
<none or exact selectors>

RUFF:
PASS

STRICT MYPY:
PASS

DEPENDENCY VERIFY:
PASS

DOCKER / VERIFICATION:
PASS

REPAIR EXACT-SHA CI:
<run/result>

RUNTIME CHANGE IN REPAIR:
NONE

W03 RUNTIME CHANGE:
NONE

GPT INDEPENDENT REVIEW:
PENDING

HUMAN C01 ACCEPTANCE:
PENDING

C01 CLOSEOUT:
NOT AUTHORIZED

W04-C02:
NOT AUTHORIZED
```
