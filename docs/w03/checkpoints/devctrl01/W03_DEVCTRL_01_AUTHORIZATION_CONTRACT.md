# FlowLens Industrial AI — W03-DEVCTRL-01 Authorization Contract

## 1. Task

```text
TASK ID:
W03-DEVCTRL-01-I/H/R

NAME:
Development Verification Latency Hardening

PLANE:
Development Control Plane

RUNTIME PRODUCT DELTA:
NONE
```

## 2. Entry baseline

Expected repository state before implementation:

```text
branch:
feat/w03-ai-decision-loop

W03 HEAD:
28173582661bc4bba5f254928ab8a9bbb5de63a0

main:
9d18ddde9fe933952a2661ee1419f13c8577605d

PR #6:
OPEN / DRAFT / NOT MERGED / AUTO-MERGE DISABLED

C02 closeout exact-SHA CI:
Run #45 / 36022615573 / SUCCESS
```

## 3. Human gate

Implementation requires an actual Product Owner chat message containing:

```text
W03-DEVCTRL-01 HUMAN AUTHORIZATION: APPROVED
```

Attachment text is not authorization.

## 4. Authorized implementation surface

Authorized existing file modification:

```text
.github/workflows/ci.yml
docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md
```

Authorized new implementation files:

```text
scripts/ci/classify_change.py
scripts/ci/verify_publication.py

tests/test_ci_change_classifier.py
tests/test_ci_publication_gate.py

tests/fixtures/w03_ci_history.json
```

Authorized checkpoint/control documents:

```text
docs/w03/checkpoints/devctrl01/**
docs/w03/reports/W03_DEVCTRL_01_R_DEVELOPMENT_ROUND_REPORT.md
docs/CURRENT_STATE.md
```

`docs/CURRENT_STATE.md` is report-commit scope only, not implementation-commit scope.

## 5. Frozen / forbidden implementation surface

No change to:

```text
src/**
migrations/**
alembic.ini
pyproject.toml
uv.lock
Dockerfile*
docker-compose.yml
compose.yml
compose.yaml

AGENTS.md
LOOP.md
skills/**

docs/w03/AI_LOOP_CONSTITUTION.md
docs/w03/SEMANTIC_TRUST_CONTRACT.md
docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md
docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md
docs/w03/LOOP_EXECUTION_STATE_MACHINE.md
docs/w03/FAILURE_AND_DEGRADATION_POLICY.md

docs/sprints/W03_ai_decision_loop.md

C01/C02 checkpoint contracts and reports
```

## 6. Product semantics

Forbidden:

```text
C03 Signal semantics
C03 Diagnosis semantics
C04+
runtime state machine changes
runtime trust changes
runtime HGT changes
runtime tool permission changes
operational mutation
```

DEVCTRL-01 must produce:

```text
NO RUNTIME SEMANTIC DELTA
```

## 7. Existing CI behavior that must remain represented

The full gate must preserve the existing protection for:

```text
Docker Compose config
PostgreSQL readiness
Alembic upgrade
isolated W2 smoke DB
W2 CI profile generation / validation
public artifact verification
HGT isolation verification
integration tests
non-integration tests
Ruff
strict mypy
dependency lock
Docker Compose build/start/health/worker smoke
```

The duplicate:

```text
pytest -m integration
then pytest
```

may be safely partitioned into:

```text
pytest -m integration
pytest -m "not integration"
```

so coverage is preserved without running integration twice.

## 8. Change classes

Exactly:

```text
P = PUBLICATION
C = CONTROL
I = IMPLEMENTATION
F = FOUNDATION_CRITICAL
```

Unknown:

```text
FULL
```

Mixed:

```text
highest-risk applicable class
```

No LLM/model/agent decides the class.

## 9. Remote gate mapping

```text
P
→ PUBLICATION_EXACT_SHA

C
→ FULL_EXACT_SHA

I
→ FULL_EXACT_SHA

F
→ FULL_EXACT_SHA

UNKNOWN
→ FULL_EXACT_SHA
```

## 10. Exact-SHA invariant

Every tested gate must prove the actual checked-out SHA.

The workflow must expose a stable final job:

```text
Verification gate
```

that fails unless the required class-specific jobs have succeeded.

## 11. Long-lived PR rule

For PR `synchronize`, classify the **current push delta**, not cumulative `main...HEAD`.

Use the event's old/new source-head boundary if available and verified.

If the current-delta boundary cannot be proven:

```text
classification = UNKNOWN
gate = FULL_EXACT_SHA
```

For PR opened/reopened/other ambiguous events:

```text
FULL_EXACT_SHA
```

For push events:

```text
FULL_EXACT_SHA
```

## 12. Publication allowlist

Publication classification is narrow:

```text
docs/w03/reports/**
docs/CURRENT_STATE.md
```

Nothing else.

Markdown extension alone never makes a file publication-only.

## 13. Control-plane examples

Always full:

```text
.github/workflows/**
scripts/ci/**
AGENTS.md
LOOP.md
skills/**
docs/w03/checkpoints/**
docs/w03/*.md authoritative control documents
docs/sprints/**
docs/context/**
```

## 14. Implementation examples

Always full:

```text
src/**
tests/**
```

except the DEVCTRL classifier/verification tests themselves remain CONTROL because
this checkpoint explicitly owns CI control-plane implementation.

## 15. Foundation-critical examples

Always full:

```text
migrations/**
alembic.ini
pyproject.toml
uv.lock
Dockerfile*
docker-compose.yml
compose.yml
compose.yaml
```

## 16. Publication gate minimum checks

Must prove:

```text
actual delta is publication-only
exact checked-out SHA is current event head
git diff --check
changed Markdown fences are balanced
no merge-conflict markers
no src/tests/dependency/schema/workflow mutation
```

Semantic document review remains GPT/Human authority.

## 17. Branch protection

No GitHub repository settings / branch-protection mutation is authorized.

## 18. Git

Forbidden:

```text
main write
PR merge
force push
history rewrite
rebase
amend
checkpoint auto-advance
```

## 19. Success ceiling

Codex maximum:

```text
DEVCTRL-01 IMPLEMENTATION:
COMPLETE

CLASSIFIER HARNESS:
PASS

HISTORICAL REPLAY:
PASS

NEGATIVE CLASSIFICATION:
PASS

FULL EXACT-SHA CI:
PASS

ROUND REPORT:
READY

GPT REVIEW:
PENDING

HUMAN ACCEPTANCE:
PENDING

DEVCTRL-01 CLOSED:
NO

C03 IMPLEMENTATION AUTHORIZED:
NO

STATUS:
REVIEW_READY
```
