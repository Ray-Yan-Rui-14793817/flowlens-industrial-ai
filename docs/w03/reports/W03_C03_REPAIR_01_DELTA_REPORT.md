# FlowLens W03-C03-REPAIR-01 Delta Report

## 1. Status and authority

```text
TASK: W03-C03-REPAIR-01
HUMAN REPAIR AUTHORIZATION: APPROVED
REPAIR ENTRY SHA: 1971a24e633af28d8b401db3ab207342d2f56408
REPAIR IMPLEMENTATION SHA: 398ecde6f35fdd5773e6b4bb29ed5b9d0a662991
STATUS: REVIEW_READY_FOR_GPT_RE_REVIEW AFTER PUBLICATION EXACT-SHA PROOF
```

This report records the bounded C03 repair requested after GPT independent
review R1. It is not a C03 closeout, Human acceptance, or C04 authorization.
The frozen C01, C02, DEVCTRL and C03 semantic boundaries remain unchanged.

The implementation commit changed exactly:

```text
src/flowlens/decision/c03_validation.py
tests/test_c03_harness.py
tests/test_c03_signals.py
```

No schema, migration, dependency, CI/control-plane, Docker, Sprint, C01/C02,
runtime HGT, database-access, network/model, operational-write, or C04 surface
changed.

## 2. HIGH-01 — conflict canonicality and fail-closed behavior

### Root cause

The pre-repair C03 validator bound `DecisionContext.context_id` only to the
ordered conflict IDs. A frozen `EvidenceConflict` could be mutated after
construction with `object.__setattr__`; mutations to `critical`,
`resolution_status`, `conflict_code`, or supporting evidence could therefore
leave the context identity unchanged. In particular, changing `critical` to
`False` allowed a real critical conflict to evade the trust block.

### Exact fix

C03 now independently revalidates every received C02 conflict before using it.
The validator requires:

```text
schema_version == evidence-conflict.v1
run_id == context.run_id
snapshot_id == context.snapshot_id
conflict_code in the frozen three-code allowlist
critical is True
resolution_status == UNRESOLVED
evidence_ids non-empty, sorted and unique
evidence_ids subset of the selected EvidenceBundle
conflict_id exactly recomputed from the frozen conflict identity
```

The frozen conflict identity contains `run_id`, `snapshot_id`,
`conflict_code`, `evidence_ids`, `critical`, and `resolution_status`.
Noncanonical or tampered conflicts fail closed as:

```text
C03_NONCANONICAL_C02_CONTEXT / BLOCKED_CONTRACT
```

Canonical critical unresolved conflicts continue to fail as:

```text
C03_CRITICAL_CONFLICT / BLOCKED_TRUST
```

The tamper harness covers all five required mutations:

```text
critical True -> False
resolution_status UNRESOLVED -> RESOLVED
conflict_code mutation
conflict_id mutation
evidence_ids mutation
```

All three canonical C02 conflict codes retain the required trust-block outcome:

```text
WORK_ORDER_PRODUCT_MISMATCH
INSPECTION_OPERATION_WORK_ORDER_MISMATCH
REWORK_INSPECTION_WORK_ORDER_MISMATCH
-> C03_CRITICAL_CONFLICT / BLOCKED_TRUST
```

## 3. MEDIUM-01 — cross-dataset normalized future-tail replay

The test fixture now accepts explicit `dataset_version` and `dataset_hash`
values without changing its defaults. Paired datasets use different ownership
and hash identities, contain different future tails after cutoff T, and retain
the same admitted observation history through T. Cross-dataset comparisons do
not require run, snapshot, Evidence, Signal, SignalBundle, or Diagnosis IDs to
match.

Signal normalization compares:

```text
signal_type
state
reason_codes
semantic Evidence references
limitations
```

Diagnosis normalization compares:

```text
problem_code
claim code, type and fixed statement
semantic Evidence references
uncertainties and their semantic Evidence references
affected_path
reason_codes
```

The paired complete-dataset tail changes cover future Delivery,
Inspection/Rework, PO receipt/quantity, WorkOrder actuals, Operation actuals,
and Inventory. Dedicated paired cases prove equivalent semantics when runtime
inventory, quality, or procurement evidence is missing. A paired critical
conflict case proves the same `C03_CRITICAL_CONFLICT / BLOCKED_TRUST` outcome
under different dataset identities and future tails. Existing route-variance
and operational-text negative packs remain intact.

```text
CROSS-DATASET FUTURE-TAIL: PASS
MISSING INVENTORY METAMORPHIC: PASS
MISSING QUALITY METAMORPHIC: PASS
MISSING PROCUREMENT METAMORPHIC: PASS
CRITICAL-CONFLICT CROSS-DATASET OUTCOME: PASS
```

## 4. LOW-01 — fully-qualified forbidden source/import audit

The runtime AST/source harness now resolves complete import namespaces,
including `from package import member` forms, and rejects the forbidden
surfaces rather than checking only the first path segment. Its negative pack
explicitly exercises:

```text
sqlalchemy
psycopg
flowlens.db and flowlens.db.*
flowlens.data.scenarios and flowlens.data.scenarios.*
flowlens.data.scenarios.ground_truth
openai, httpx, requests, urllib and socket
filesystem reader/writer surfaces
subprocess and shell surfaces
randomness
wall-clock calls
dynamic code/import surfaces
```

The authorized safe `flowlens.decision.*` imports remain permitted. Current C03
runtime source remains free of database, scenario/HGT, filesystem, network,
model/LLM, subprocess/shell, random, wall-clock, and operational-mutation
capability.

## 5. Local verification evidence

| Gate | Result |
|---|---|
| Focused C03 | 77 / 77 passed |
| Frozen C01 regression | 39 / 39 passed |
| Frozen C02 regression | 26 / 26 passed |
| Full non-integration | 494 passed / 48 deselected / 0 failed |
| Guarded PostgreSQL C03 | 5 / 5 passed |
| Ruff | PASS |
| Strict mypy | PASS — 90 source files |
| `git diff --check` | PASS |
| Docker Compose configuration | PASS |

The non-integration suite emitted only the existing Starlette/httpx deprecation
warning. The guarded PostgreSQL proof used a dedicated empty `_test` database;
all five tests passed and the temporary database was removed and verified
absent afterward.

## 6. Exact implementation-SHA CI proof

Exact-SHA [CI Run #51](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/36142738931)
(`36142738931`) proved commit
`398ecde6f35fdd5773e6b4bb29ed5b9d0a662991`:

| DEVCTRL field | Exact result |
|---|---|
| Classify change | SUCCESS |
| Class | `I` |
| Gate | `FULL_EXACT_SHA` |
| Quality gate | SUCCESS |
| Docker Compose smoke | SUCCESS |
| Publication proof | SKIPPED |
| Verification gate | SUCCESS |
| Workflow conclusion | SUCCESS |

The classifier bound the exact base
`1971a24e633af28d8b401db3ab207342d2f56408`, exact head
`398ecde6f35fdd5773e6b4bb29ed5b9d0a662991`, and exactly the three authorized
implementation/test paths listed above.

## 7. Repository and review boundary

At publication entry:

```text
main: 9d18ddde9fe933952a2661ee1419f13c8577605d / UNCHANGED
PR #6: OPEN / DRAFT / NOT MERGED
auto-merge: DISABLED / NONE
GPT C03 REVIEW: R1 REPAIR REQUIRED / RE-REVIEW PENDING
HUMAN C03 ACCEPTANCE: PENDING
C03 CLOSED: NO
C04 AUTHORIZED: NO
```

This report and `docs/CURRENT_STATE.md` are the exact two-file publication
delta. The report commit's own SHA and `P / PUBLICATION_EXACT_SHA` result are
intentionally recorded in the final Codex handoff after CI, not written back
through an additional commit.
