# W03-DEVCTRL-01 Harness and Acceptance Spec

## Layer A — Classifier unit tests

Prove:

```text
path classification
precedence
unknown fallback
publication allowlist
control Markdown is not P
mixed deltas
deterministic JSON output
```

## Layer B — Historical replay

Prove C01/C02 accepted history is classified according to the final class contract.

Historical replay may reveal that a former closeout touched an authoritative Sprint
document and is therefore FULL under the new policy. That is expected and not a failure
of the historical checkpoint.

## Layer C — Publication verifier

Prove:

```text
allowlisted P delta passes
source/test/workflow mixed delta fails
git diff whitespace errors fail
unbalanced Markdown fences fail
merge-conflict markers fail
```

## Layer D — Workflow static assertions

Verify `.github/workflows/ci.yml` contains:

```text
classify-change
Quality gate
Docker Compose smoke
Publication proof
Verification gate
```

Verify:

```text
P can reach publication proof
P does not execute Quality/Compose
C/I/F/UNKNOWN execute full gate
Verification gate is fail-closed
exact source-head checkout is verified
push is FULL
```

## Layer E — Local full regression

Before implementation push:

```text
pytest tests/test_ci_change_classifier.py tests/test_ci_publication_gate.py
pytest -m "not integration"
pytest -m integration     # when guarded local PostgreSQL is safely available
ruff check .
mypy .
uv lock --check
git diff --check
docker compose config --quiet
```

Do not use GitHub Actions as the normal debugging loop.

## Layer F — First remote proof

DEVCTRL implementation commit is CONTROL and therefore must receive:

```text
Quality gate = PASS
Docker Compose smoke = PASS
Verification gate = PASS
```

The implementation commit must not be accepted if the classifier accidentally routes
its workflow change to Publication.

## Layer G — First real publication proof

After the implementation exact-SHA full gate succeeds:

```text
Round Report + CURRENT_STATE only
→ P
```

Push a separate report commit.

Required:

```text
Publication proof = PASS
Verification gate = PASS
Quality gate = SKIPPED
Docker Compose smoke = SKIPPED
```

This is required evidence that the optimization actually works.

## Acceptance

DEVCTRL-01 is `REVIEW_READY` only after both are proven:

```text
CONTROL implementation SHA
→ FULL exact-SHA PASS

PUBLICATION report SHA
→ PUBLICATION exact-SHA PASS
```

Runtime source delta:

```text
NONE
```
