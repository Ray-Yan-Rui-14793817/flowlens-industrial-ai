# FlowLens W03-C04-R1 Harness Repair Report

## 1. Status and authority

```text
TASK: W03-C04-R1
TASK TYPE: REVIEW REPAIR / HARNESS EVIDENCE HARDENING
HUMAN AUTHORIZATION: APPROVED
ENTRY SHA: 4e9a52af845d44e0166a855e9d4c0259bca4be7b
PRIOR C04 IMPLEMENTATION SHA: 62405d7169b1aaea321290749395ab077792f86f
REPAIR IMPLEMENTATION SHA: ae54dbc23effedf59566306d209a03b7290a299e
STATUS: REVIEW_READY_FOR_GPT_R2 ONLY AFTER PUBLICATION EXACT-SHA PROOF
```

The Product Owner authorized this bounded test/harness-first repair after GPT
independent review R1. It closes four verification-evidence gaps without
changing frozen C04 product semantics, C03 semantics, W2 scenarios, HGT,
schema, migrations, dependencies, CI/control-plane, or C05 capability.

Accepted prior evidence remains immutable:

| Evidence | Exact value |
|---|---|
| C04 implementation | `62405d7169b1aaea321290749395ab077792f86f` |
| Implementation proof | [Run #55 / `36227210323`](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/36227210323) — `I / FULL_EXACT_SHA` — PASS |
| C04 report publication | `4e9a52af845d44e0166a855e9d4c0259bca4be7b` |
| Publication proof | [Run #56 / `36227742782`](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/36227742782) — `P / PUBLICATION_EXACT_SHA` — PASS |
| Frozen main | `9d18ddde9fe933952a2661ee1419f13c8577605d` |

## 2. Read-only preflight and exact scope

Before mutation, local HEAD, tracking HEAD, direct-remote W03 HEAD and PR #6
HEAD all equaled the entry SHA. The worktree was clean, tracking was `0/0`,
main matched the frozen SHA, no merge/rebase/cherry-pick/revert/bisect state was
active, and PR #6 was open, draft, unmerged, with auto-merge absent. Runs #55
and #56 retained their successful exact-SHA classifications and gates.

The repair implementation commit changes exactly:

```text
tests/test_c04_harness.py
tests/test_c04_scenario_adapter_compat.py
tests/test_c04_simulation.py
```

Runtime source changes are **NONE**. The historical
`W03_C04_R_DEVELOPMENT_ROUND_REPORT.md` remains unchanged. No existing frozen
assertion was weakened, deleted, rewritten, skipped, or xfailed.

## 3. R1-MEDIUM-01 — successful non-NO_ACTION C04 paths

The real C04 wrapper now runs one deterministic closed fixture through the
canonical `CandidateSet -> _scenario_config -> apply_scenario_business_only ->
SimulationResult -> SimulationBundle` path. No production function is patched,
no gate is bypassed, and canonical candidate parameters are unchanged.

| Family | Status | Scenario hash | Independent affected count |
|---|---|---|---:|
| Supplier | `SUCCEEDED` | `f35069b129ad027f5872346c500adb3f1550fb95f4e78c958d16bc602e3e7da2` | 23 |
| Quality | `SUCCEEDED` | `7ca057b804feb7b1c25296651b1f1b1d13b8d39bcedea4203f16ab72f4c16a8d` | 8 |
| Capacity | `SUCCEEDED` | `d124be53d41476f9e156bead59766a7440ba28eebf90f80bf06204d1f1e51d7f` | 2241 |

Every result proves a non-null deterministic scenario identity/hash, the exact
ten-name/unit measurement schema, sorted affected entities, candidate/run/
snapshot binding, canonical bundle ordering, stable replay, and baseline
immutability. `NO_ACTION` remains neutral and successful with no scenario
identity or affected entities.

```text
R1-MEDIUM-01: CLOSED
SUPPLIER SUCCESS PATH: PASS
QUALITY SUCCESS PATH: PASS
CAPACITY SUCCESS PATH: PASS
```

## 4. R1-MEDIUM-02 — successful SimulationBundle replay

The same deterministic inputs produce byte-identical canonical
`SimulationBundle` serialization twice in-process. Two independent fresh
Python interpreters rebuild the inputs and complete successful bundle without
loading `flowlens.data.scenarios.ground_truth`; both emit the same SHA-256 as
the local process:

```text
SimulationBundle ID:
simb_0a89c98da0245936e488ec559a43f32cb8e0429505b5738a53d96eef54ef5140

Canonical SHA-256:
5ef21167086d7798ba44418274eacd9e2c87d90e13b037f701aa97894d8050c7
```

Subprocess capability exists only in the test harness. The C04 runtime import
and execution surfaces remain subprocess-free and HGT-free.

```text
R1-MEDIUM-02: CLOSED
SAME-PROCESS SIMULATIONBUNDLE REPLAY: PASS
FRESH-PROCESS SIMULATIONBUNDLE REPLAY: PASS
```

## 5. R1-LOW-01 — Capacity-created semantic rows

An accepted deterministic Capacity combined-mode transformation creates rows
in eight business tables. The harness independently derives ownership-free
primary business keys from baseline and scenario datasets, without HGT or the
runtime diff implementation:

| Table | Independently observed new rows |
|---|---:|
| `fact_sales_order` | 1 |
| `fact_purchase_order` | 2 |
| `fact_work_order` | 2 |
| `fact_operation` | 6 |
| `fact_material_requirement` | 2 |
| `fact_quality_inspection` | 4 |
| `fact_rework` | 2 |
| `fact_delivery` | 2 |

Every independently observed new key is present in
`semantic_affected_entities`. The prior proof that dataset-ownership-only
changes produce an empty diff remains intact.

```text
R1-LOW-01: CLOSED
CAPACITY-CREATED-ROW SEMANTIC DIFF: PASS
```

## 6. R1-LOW-02 — Capacity adapter compatibility matrix

Business-only adapter equivalence with legacy `apply_scenario()` is now
explicitly proved for all accepted Capacity modes:

| Mode | Arrival | Queue | Result |
|---|---:|---:|---|
| Combined | `1.5` | `1.7` | PASS |
| Arrival-only | `1.5` | `1.0` | PASS |
| Queue-only | `1.0` | `1.7` | PASS |
| Neutral | `1.0` | `1.0` | PASS |

Each mode compares scenario dataset ID, content hash, row count and canonical
business payload, and proves baseline immutability. Legacy repeated execution
also retains exact scenario ID, HGT ID, HGT hash, canonical HGT payload and
business dataset identity/content behavior. HGT remains confined to the legacy
compatibility-test boundary.

```text
R1-LOW-02: CLOSED
CAPACITY FOUR-MODE ADAPTER COMPATIBILITY: PASS
```

## 7. Local verification

| Gate | Result |
|---|---|
| Focused C04 | 31 passed |
| C03 regression | 77 passed |
| C02 regression | 26 passed |
| C01 regression | 39 passed |
| W2 regression | 154 passed |
| Full non-integration | 525 passed; 48 deselected; one existing Starlette/httpx warning |
| Local PostgreSQL | Not run: `FLOWLENS_DATABASE_URL` and `FLOWLENS_APP_ENVIRONMENT` were unset |
| Exact-SHA CI PostgreSQL partition | 48 passed; 525 deselected |
| Exact-SHA CI complete non-integration suite | 525 selected and passed |
| Ruff, whole repository | PASS |
| Strict mypy, whole repository | PASS — 98 source files |
| `git diff --check` / staged diff check | PASS |
| `docker compose config --quiet` | PASS |

Existing C04 typed error handling, sanitization, baseline-mutation hard fail,
closed-observation zero-call gates, exact candidate-to-config binding, HGT-free
runtime, pure decision import, capability denial, frozen source hashes, and all
accepted C01/C02/C03/W2 regressions remain green.

## 8. Exact repair implementation proof

[Run #57](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/36244584464)
proved exact repair SHA `ae54dbc23effedf59566306d209a03b7290a299e`:

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

The classifier bound base `4e9a52af845d44e0166a855e9d4c0259bca4be7b`,
head `ae54dbc23effedf59566306d209a03b7290a299e`, and exactly the three
authorized test paths.

## 9. Publication and review boundary

This report and `docs/CURRENT_STATE.md` are the exact two-file publication
delta. The publication commit SHA and `P / PUBLICATION_EXACT_SHA` result are
recorded in the final Codex handoff after CI; they cannot be embedded in the
same immutable commit.

```text
MAIN: 9d18ddde9fe933952a2661ee1419f13c8577605d / UNCHANGED
PR #6: OPEN / DRAFT / NOT MERGED
AUTO-MERGE: ABSENT / DISABLED
GPT C04 R2 RE-REVIEW: PENDING
HUMAN C04 ACCEPTANCE: PENDING
C04 CLOSED: NO
C05 AUTHORIZED: NO
STATUS: REVIEW_READY_FOR_GPT_R2 ONLY AFTER PUBLICATION EXACT-SHA PROOF
```
