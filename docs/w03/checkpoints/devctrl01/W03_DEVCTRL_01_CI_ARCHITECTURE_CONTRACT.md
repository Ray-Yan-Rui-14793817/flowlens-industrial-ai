# W03-DEVCTRL-01 CI Architecture Contract

## Target architecture

Keep one workflow:

```text
.github/workflows/ci.yml
```

Do not add a second AI/product workflow in DEVCTRL-01.

Target job graph:

```text
classify-change
        |
        +---- P ----------------→ publication-proof
        |
        +---- C/I/F/UNKNOWN ----→ Quality gate
                               → Docker Compose smoke

all paths
        ↓
Verification gate
```

## Stable final evidence job

Required final job name:

```text
Verification gate
```

It must use `if: always()` and fail unless the class-required jobs reached an allowed
successful state.

Examples:

```text
P:
classification success
publication-proof success
quality skipped
compose skipped
→ Verification gate PASS

I:
classification success
quality success
compose success
publication skipped
→ Verification gate PASS
```

Unexpected cancellation/failure/missing required result:

```text
Verification gate FAIL
```

## Exact checkout

For PR jobs that perform proof:

```text
ref = github.event.pull_request.head.sha
fetch-depth = 0 where history/delta is required
```

Verify:

```text
git rev-parse HEAD == expected source head
```

For push:

```text
git rev-parse HEAD == github.sha
```

## Full gate

Preserve existing `Quality gate` and `Docker Compose smoke`.

Quality gate may remove duplicate integration execution by changing:

```text
pytest -m integration
pytest
```

to:

```text
pytest -m integration
pytest -m "not integration"
```

No other reduction in full proof is authorized.

## Publication proof

Required job name:

```text
Publication proof
```

At minimum:

```text
re-run/verify classifier result is P
verify exact head
git diff --check
run scripts/ci/verify_publication.py over actual changed paths
```

No PostgreSQL, W2 data generation, full pytest, image build, or Compose runtime is
required for a proven P delta.

## Pull-request current delta

The classifier must use the actual source-head transition for the current synchronize
event when the event payload safely exposes it.

If this cannot be established:

```text
FULL
```

## Push behavior

Current push triggers may remain unchanged in DEVCTRL-01.

Any push event:

```text
FULL
```

This prevents publication optimization from being inferred without a prior PR-head
boundary.

## Concurrency

Do NOT introduce cancellation behavior that can cancel a still-required implementation
exact-SHA proof before its Round Report exists.

Concurrency optimization is optional and not required by DEVCTRL-01 v1.

## Workflow changes are control-plane changes

The DEVCTRL implementation commit changes `.github/workflows/ci.yml`.

Therefore its own initial remote proof must run the full path.

## Publication report after implementation

The DEVCTRL Round Report commit should contain only:

```text
docs/w03/reports/W03_DEVCTRL_01_R_DEVELOPMENT_ROUND_REPORT.md
docs/CURRENT_STATE.md
```

It is the first intended real `P` consumer of the new publication path.

That publication commit must receive:

```text
Publication proof = PASS
Verification gate = PASS
```

and must not run the heavy Quality/Compose jobs if classification works as designed.
