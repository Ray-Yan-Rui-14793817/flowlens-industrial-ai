# W03-DEVCTRL-01 Change-Class Contract

## Deterministic classes

| Class | Meaning | Remote gate |
|---|---|---|
| `P` | narrow publication/evidence delta | `PUBLICATION_EXACT_SHA` |
| `C` | development control-plane delta | `FULL_EXACT_SHA` |
| `I` | runtime/test implementation delta | `FULL_EXACT_SHA` |
| `F` | foundation-critical delta | `FULL_EXACT_SHA` |

## Publication allowlist

Only:

```text
docs/w03/reports/**
docs/CURRENT_STATE.md
```

A delta is `P` iff every changed path is inside the allowlist.

## Control paths

Examples:

```text
.github/workflows/**
scripts/ci/**
AGENTS.md
LOOP.md
skills/**
docs/w03/checkpoints/**
docs/w03/AI_LOOP_CONSTITUTION.md
docs/w03/SEMANTIC_TRUST_CONTRACT.md
docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md
docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md
docs/w03/LOOP_EXECUTION_STATE_MACHINE.md
docs/w03/FAILURE_AND_DEGRADATION_POLICY.md
docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md
docs/sprints/**
docs/context/**
```

## Implementation paths

```text
src/**
tests/**
```

For classifier precedence, normal product tests are `I`. DEVCTRL's own CI-control tests
are treated as `C` only because their path set is explicitly frozen by this task.

## Foundation paths

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

## Precedence

```text
F > I > C > P
```

But all non-P classes map to full verification, so precedence must never reduce proof.

Unknown path:

```text
UNKNOWN
→ FULL_EXACT_SHA
```

## Current-delta source

For `pull_request/synchronize`:

```text
verified event BEFORE source head
→
verified event AFTER/current PR source head
```

If unavailable or invalid:

```text
UNKNOWN / FULL
```

Do not classify from:

```text
commit message
file extension
cumulative main...feature diff
model judgment
```

## Machine output

Classifier must produce at least:

```json
{
  "class": "P|C|I|F|UNKNOWN",
  "gate": "PUBLICATION_EXACT_SHA|FULL_EXACT_SHA",
  "base_sha": "...",
  "head_sha": "...",
  "changed_paths": [],
  "reason_codes": []
}
```

Output must be deterministic for the same Git tree/delta.
