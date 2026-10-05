# FlowLens Industrial AI — W03-C09 CI / Regression Contract

```text
checkpoint = W03-C09
contract_version = W03-C09-A-v1.1
ci_gate_version = w03-c09-ai-loop-gate-v1
manifest_schema = w03-c09-regression-manifest-v1.1
```

## 1. Purpose

Make the frozen Week 3 trust gates an explicit exact-SHA CI proof without
changing runtime behavior.

```text
ENGINEERING PROOF
+
SEMANTIC PROOF
+
EXACT-SHA CONJUNCTION
=
C09 CODEX VERIFICATION
```

## 2. Stable job contract

Add exactly one non-publication job:

```text
job id = w03-ai-loop-gate
name = W03 AI loop gate
```

The job must use the same exact source-head expression as the existing Quality
and Compose jobs and must independently verify checked-out HEAD equality.

The job is required when the classifier output is not `P` and skipped when it
is `P`.

## 3. No replacement of existing proof

Do not remove, rename, bypass, or weaken:

```text
Classify change
Quality gate
Docker Compose smoke
Publication proof
Verification gate
```

Do not remove any existing Quality step or reduce the full pytest partitions.

## 4. Environment

Reuse only the current pinned development stack:

```text
ubuntu-latest
Python 3.12
uv 0.12.5
pgvector/pgvector:0.8.6-pg17-bookworm
existing checkout/setup-python/setup-uv action SHAs
uv sync --frozen
alembic upgrade head
```

No live LLM/provider network call. No new GitHub Action. No new dependency.

## 5. Regression manifest

The exact V1 manifest is supplied in `specs/c09_gate_manifest.json`.

Rules:

```text
schema/version exact
family IDs exact and unique
family order deterministic
pytest function selectors exact and unique within the complete manifest
all targets under tests/
no shell expansion
no wildcard
no -k
no marker-based broad selection
no external command encoded in the manifest
```

Each target object freezes an exact function selector and its expanded pytest
case count. Parameterized expansion is explicitly permitted and required. The
manifest freezes 38 selectors and exactly 85 expanded cases. A selector removed
or renamed, an expanded count mismatch, partial parameter execution, or any
silent substitution must fail the C09 job.

## 6. Gate runner output

The gate runner must write deterministic JSON to an explicitly supplied
runner-temporary output path and print the same semantic summary to stdout.

Minimum envelope:

```json
{
  "schema_version": "w03-c09-gate-summary-v1",
  "gate_version": "w03-c09-ai-loop-gate-v1",
  "implementation_sha": "<40 lowercase hex>",
  "manifest_sha256": "<64 lowercase hex>",
  "families": [
    {
      "id": "F01 CORE_CONTRACTS",
      "status": "PASS",
      "selectors": 3,
      "tests": 3
    }
  ],
  "overall": "PASS"
}
```

Allowed family status is only `PASS` in a successful run. Any incomplete family
must terminate the job nonzero rather than emit a successful partial summary.

## 7. Critical-test outcome rules

For every family:

```text
collected cases per selector = selector.expected_cases
family collected cases = family.expected_cases
global collected cases = 85
failed = 0
errors = 0
skipped = 0
xfail = 0
xpass = 0
pytest exit = 0
```

A missing selector, collection error, expanded-count drift, or partial parameter execution is a hard failure.

Warnings may be reported but may not be rewritten into semantic PASS evidence.
Existing accepted third-party warnings are not C09 semantic failures unless they
cause a test failure under the existing suite policy.

## 8. Verification-gate integration

Extend the existing `verification-gate` dependency list with `w03-ai-loop-gate`.

Required final truth table:

| Change class | Quality | Compose | W03 AI loop gate | Publication | Verification |
|---|---|---|---|---|---|
| P | skipped | skipped | skipped | success | success |
| C | success | success | success | skipped | success |
| I | success | success | success | skipped | success |
| F | success | success | success | skipped | success |
| UNKNOWN | success | success | success | skipped | success |

Any missing/failed/cancelled required job fails Verification.

## 9. C09 unit/contract tests

`tests/test_c09_ci_gate.py` must independently prove at minimum:

```text
strict manifest schema
exact family set
exact 38-selector / 85-expanded-case totals
no duplicate selector
invalid path rejection
wildcard/flag/shell-token rejection
missing target rejection
zero-test rejection
failure/error rejection
skip/xfail rejection
exact-head mismatch rejection
stable deterministic summary ordering
workflow contains the W03 job
workflow uses non-P/P scheduling correctly
verification-gate requires W03 job success/skipped according to class
existing Quality/Compose/Publication job names remain present
no new action pin or dependency surface is required
```

Tests must exercise the actual gate-runner implementation where practical, not
only duplicate its logic.

## 10. Stop conditions

Stop for GPT/Human architecture review if implementation would require:

```text
runtime source change
semantic test weakening
new dependency/action/image
classifier semantic change
branch-trigger broadening
schema/migration change
C08 prompt/provider/model change
operational write
C10 business-acceptance logic
```
