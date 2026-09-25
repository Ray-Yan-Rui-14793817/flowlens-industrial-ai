# FlowLens W03-C03 DEVCTRL Integration Contract

## 1. Authority

DEVCTRL-01 closed at:

```text
2e84a6dfdbdbd81cf5ea9ad0b555fdf1707db978
Run #48 / 36104873132 / SUCCESS
```

C03 consumes that control plane; it does not redesign it.

## 2. Frozen CI/control files during C03

```text
.github/workflows/**
scripts/ci/**
docs/w03/checkpoints/devctrl01/**
```

No C03 CI helper or checkpoint-specific workflow is authorized.

## 3. Implementation classification

C03 implementation contains runtime/test files, so the deterministic classifier should route it:

```text
I / FULL_EXACT_SHA
```

Required exact implementation SHA:

```text
Classify change = SUCCESS
Quality gate = SUCCESS
Docker Compose smoke = SUCCESS
Publication proof = SKIPPED
Verification gate = SUCCESS
workflow conclusion = SUCCESS
```

If it routes to P:

```text
SAFETY FAILURE / STOP
```

## 4. Report publication classification

After full implementation proof, the report commit contains exactly:

```text
docs/w03/reports/W03_C03_R_DEVELOPMENT_ROUND_REPORT.md
docs/CURRENT_STATE.md
```

Expected:

```text
P / PUBLICATION_EXACT_SHA
```

Required:

```text
Classify change = SUCCESS
Publication proof = SUCCESS
Verification gate = SUCCESS
Quality gate = SKIPPED
Docker Compose smoke = SKIPPED
```

Do not update `docs/sprints/**` during ordinary C03 I/H/R reporting.

## 5. Local candidate gate before push

C03 still performs targeted local harnesses before the one implementation push:

```text
focused C03 unit tests
C01 regression
C02 regression
full non-integration
safe guarded C03 integration when available
Ruff
strict mypy
git diff --check
docker compose config --quiet
```

Use local verification for debugging. Do not intentionally use repeated GitHub pushes as the normal repair loop.

## 6. DEVCTRL failure boundary

If C03 code/tests fail inside authorized scope:

```text
Type A repair allowed
```

If the accepted classifier/workflow/publication verifier itself requires modification:

```text
STOP
DEVCTRL REPAIR REQUIRED
```

C03 may not silently reopen or weaken the control plane.

## 7. Closeout path later

After GPT review + Human C03 acceptance, a separately authorized closeout should again use only:

```text
docs/w03/reports/**
docs/CURRENT_STATE.md
```

so the closeout remains a P/publication proof unless a separately authorized control-document change is actually required.
