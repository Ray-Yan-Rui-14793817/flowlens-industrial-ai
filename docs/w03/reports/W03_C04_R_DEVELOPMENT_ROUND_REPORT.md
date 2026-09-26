# W03-C04 Development Round Report

## 1. Status and authority

| Item | Verified value |
|---|---|
| Task | W03-C04-I/H/R — Intervention Registry and Counterfactual Simulation |
| Starting C03 closeout SHA | `1c0f4de6f897d9e377fba63891773bb5970e74b7` |
| Initial implementation SHA | `fb478e107106e7177e4a6245159d97c72b343a35` |
| Final implementation SHA | `62405d7169b1aaea321290749395ab077792f86f` |
| Branch | `feat/w03-ai-decision-loop` |
| Main baseline | `9d18ddde9fe933952a2661ee1419f13c8577605d` |
| Draft PR | [#6](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/pull/6) |
| Final implementation exact-SHA CI | [Run #55 / `36227210323`](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/36227210323) — success |
| Date | 2026-09-26 |

The Product Owner's implementation authorization remains:

```text
W03-C04 HUMAN AUTHORIZATION: APPROVED
```

The later quota-recovery authorization explicitly resumed the same authorized
lifecycle without discarding valid work. The read-only recovery audit
classified the durable state as **A**: no C04 commit or C04 CI proof existed,
but all uncommitted work was authorized, the Context Lock remained `LOCKED`,
the frozen source hashes matched, no Git operation was active, and local,
tracking, direct-remote and PR heads were synchronized at the starting SHA.

```text
QUOTA RECOVERY: RESUMED
C04 IMPLEMENTATION: COMPLETE
CONTEXT LOCK: VERIFIED
STATUS: REVIEW_READY ONLY AFTER REPORT PUBLICATION GATE
```

## 2. Context Lock and baseline

The [C04 Context Lock](../checkpoints/c04/W03_C04_CONTEXT_LOCK.md) was
published before source or test implementation and remained `LOCKED`
throughout recovery and final verification. It records the authority stack,
authorized paths, accepted development fixture, runtime permissions, frozen
scenario sources and Product Owner authorization.

The frozen W2 development dataset recorded by the lock is:

```text
dataset_version_id: dsv_9c21c51c1ed71921e43f30da7afab559
content_hash: bb08255c0bed5836d2a985b85bded5dc0fe5386af16939c891d520bed10d9416
row_count_total: 2199
period_end: 2026-03-31
```

The immutable scenario source hashes remained exact:

| Frozen source | Context Lock SHA-256 |
|---|---|
| `src/flowlens/data/scenarios/config.py` | `2ec47cdcab56bc5d1439a37a5a29e2c0362bd98bfe2675234eeb726bef84a35c` |
| `src/flowlens/data/scenarios/ground_truth.py` | `6b6671d568b404506da094785e8bde461d54a3754b7884f9f9311f4ac4f0a01e` |

The cross-platform harness also verifies the normalized Git blob hashes so
the byte proof is stable across LF and CRLF checkouts. No config semantics,
HGT identity, HGT hash or HGT payload changed.

## 3. Authorized implementation delta

The initial implementation commit changed exactly these 27 authorized paths:

```text
docs/sprints/W03_ai_decision_loop.md
docs/w03/checkpoints/c04/W03_C04_ARCHITECTURE_AND_COMPATIBILITY.md
docs/w03/checkpoints/c04/W03_C04_AUTHORIZATION_CONTRACT.md
docs/w03/checkpoints/c04/W03_C04_CONTEXT_LOCK.md
docs/w03/checkpoints/c04/W03_C04_DEVCTRL_INTEGRATION_CONTRACT.md
docs/w03/checkpoints/c04/W03_C04_GPT_REVIEW_CHECKLIST.md
docs/w03/checkpoints/c04/W03_C04_HARNESS_ACCEPTANCE_SPEC.md
docs/w03/checkpoints/c04/W03_C04_HUMAN_AUTHORIZATION.md
docs/w03/checkpoints/c04/W03_C04_REGISTRY_AND_MAPPING_CONTRACT.md
docs/w03/checkpoints/c04/W03_C04_SIMULATION_CONTRACT.md
docs/w03/checkpoints/c04/specs/authorized_paths.json
docs/w03/checkpoints/c04/specs/measurement_schema.json
docs/w03/checkpoints/c04/specs/registry_policy.json
src/flowlens/data/scenarios/__init__.py
src/flowlens/data/scenarios/application.py
src/flowlens/data/scenarios/capacity.py
src/flowlens/data/scenarios/quality.py
src/flowlens/data/scenarios/runtime_adapter.py
src/flowlens/data/scenarios/supplier.py
src/flowlens/data/scenarios/transformer.py
src/flowlens/decision/c04_registry.py
src/flowlens/decision/c04_simulation.py
src/flowlens/decision/c04_validation.py
tests/test_c04_harness.py
tests/test_c04_registry.py
tests/test_c04_scenario_adapter_compat.py
tests/test_c04_simulation.py
```

The separate normal repair commit changed only
`tests/test_c04_harness.py` to make the frozen-source byte proof portable
across GitHub's LF checkout and the locked Windows CRLF representation. It did
not change source, contracts or semantics. No commit was amended or rewritten.

There is no C01/C02/C03 source drift, schema or migration change, dependency
or lock-file change, CI/control-plane change, Docker/Compose change, API or
worker change, recommendation/scoring capability, or C05 source.

## 4. Registry and scenario mapping

The registry deterministically emits exactly four candidates for canonical
C03 inputs. Relevance affects fixed reason codes only; it does not suppress a
family and does not establish causality.

| Family | Registry key | Frozen execution mapping |
|---|---|---|
| `NO_ACTION` | `c04.no-action.v1` | Baseline identity comparator; no scenario call |
| `SUPPLIER_INTERVENTION` | `c04.supplier-stress-probe.v1` | `SupplierDegradationConfig` |
| `QUALITY_INTERVENTION` | `c04.quality-stress-probe.v1` | `QualityDeteriorationConfig` |
| `CAPACITY_INTERVENTION` | `c04.capacity-stress-probe.v1` | `CapacitySurgeConfig` |

Every non-NO_ACTION config is reconstructed directly from the canonical
candidate parameters. The harness proves exact field binding for all three
families, including scenario version, deterministic SHA-256-derived seed and
the full closed dataset window.

```text
CANDIDATE PARAMETER -> EXECUTED CONFIG BINDING: PASS
```

The three scenario families are stress probes for human investigation. They
do not claim intervention efficacy, improvement, probability, confidence,
root cause or operational action benefit. Every non-NO_ACTION candidate
explicitly states that frozen W2 scenario selection is not guaranteed to
target the current order.

## 5. Simulation and temporal boundary

`SimulationResult` and `SimulationBundle` are deterministic immutable
artifacts. `NO_ACTION` succeeds without the scenario engine and emits the
frozen raw ten-field measurement schema. Non-NO_ACTION execution is available
only when an already-materialized in-memory baseline:

- matches the DecisionRun dataset version and recomputed content hash;
- is observed exactly at the dataset's closed observation instant;
- contains no event timestamp after the DecisionRun `as_of_time`; and
- consists only of detached business rows.

Otherwise C04 returns `UNAVAILABLE` without calling the scenario engine. A
future-containing full dataset is never used at an earlier decision time.
The harness proves zero scenario calls for the earlier-as-of gate, binding and
hash failures, deterministic replay, cross-process replay, baseline
immutability, independent ownership-free affected-entity diff and exact
measurement names/units.

## 6. MEDIUM-01 typed failure boundary

The mandatory pre-review finding is closed with the compatibility-preserving
`ScenarioPreconditionUnavailable(ValueError)` type in the shared W2 scenario
transformer. Only genuine deterministic eligibility/precondition
insufficiency raises this subtype. Malformed topology, invalid timing,
duplicate identities and invariant violations remain ordinary unexpected
errors.

| Case | C04 result |
|---|---|
| Typed expected W2 precondition | `UNAVAILABLE / C04_SCENARIO_PRECONDITION_UNAVAILABLE` |
| Unexpected `ValueError` | `FAILED / C04_SCENARIO_EXECUTION_FAILED` |
| Unexpected `RuntimeError` or other exception | `FAILED / C04_SCENARIO_EXECUTION_FAILED` |
| Baseline mutation on any error path | hard fail `C04_BASELINE_MUTATION / BLOCKED_INTEGRITY` |

Arbitrary exception text is never placed in a SimulationResult, limitation or
serialized bundle.

```text
MEDIUM-01 OVERBROAD VALUEERROR CLASSIFICATION: CLOSED
EXPECTED PRECONDITION CLASSIFICATION: PASS
UNEXPECTED VALUEERROR: FAILED / SANITIZED
UNEXPECTED RUNTIMEERROR: FAILED / SANITIZED
BASELINE MUTATION ON ERROR PATH: HARD FAIL / PASS
```

## 7. HGT-free W2 compatibility adapter

The authorized non-semantic W2 refactor separates business transformation
effects from protected truth construction. The new runtime adapter returns
only `GeneratedDataset`; it never constructs or imports Hidden Ground Truth.
The package boundary is lazy, so importing `flowlens.decision`, the C04
runtime, scenario config or the runtime adapter does not eagerly import HGT.

The legacy public `apply_scenario()` API remains compatible. It constructs
HGT only at the legacy boundary from the same deterministic business effects.
Supplier, Quality and Capacity equivalence tests prove:

- exact scenario business payload, dataset ID, content hash and row count;
- unchanged repeatability and baseline isolation;
- unchanged legacy HGT scenario ID, HGT ID, HGT hash and canonical payload;
- no direct C04 runtime use of legacy `apply_scenario()`; and
- HGT remains absent from `sys.modules` during fresh-process runtime-adapter
  import and execution.

## 8. Harness and regression evidence

| Gate | Observed result |
|---|---|
| Focused C04 tests | 24 passed |
| C03 policy/signals/diagnosis/harness regression | 77 passed |
| Frozen C01 contracts/serialization regression | 39 passed |
| Frozen C02 snapshot/temporal/evidence/context regression | 26 passed |
| Frozen W2 scenarios/interventions/Capacity/HGT regression | 154 passed |
| Full local non-integration suite | 518 passed; 48 deselected; one existing Starlette/httpx warning |
| Guarded local PostgreSQL integration | Not run: `FLOWLENS_DATABASE_URL` was unset |
| Final exact-SHA CI integration partition | 48 passed; 518 deselected |
| Final exact-SHA CI non-integration partition | 518 selected and passed |
| Ruff, whole repository | PASS |
| Strict mypy, whole repository | PASS, 98 source files |
| `git diff --check` / staged diff check | PASS |
| `docker compose config --quiet` | PASS |

The H1-H17 harness covers exact registry cardinality, canonical C03 rebuild,
relevance-not-causality, neutral stability, closed-window zero calls,
baseline binding/hash, HGT-free import/execution, legacy W2 equivalence/HGT,
immutability, same- and cross-process determinism, independent semantic diff,
measurement schema, typed precondition, unexpected failure, capability
isolation and pure `flowlens.decision` import.

Initial Run #54 found only a Linux checkout newline assumption in the test
that reverified the Context Lock hashes. The resulting test-only repair is the
separate final implementation commit. Final Run #55 passed the complete exact
SHA workflow.

## 9. Safety boundary

```text
future leakage: NONE
baseline immutability: PASS
runtime HGT access: NONE
post-C02 DB access: NONE
filesystem/network/model access: NONE
subprocess/random/wall-clock access: NONE
operational mutation: NONE
recommendation/scoring/ranking: NONE
C05 capability: NONE
```

The runtime consumes only already-built decision artifacts and an optional
already-materialized in-memory baseline. It has no database session/query,
filesystem, network, model/LLM, subprocess, random, wall-clock or operational
write capability.

## 10. Final implementation exact-SHA proof

[Run #55](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/36227210323)
proved final implementation SHA
`62405d7169b1aaea321290749395ab077792f86f`:

```text
Classify change: SUCCESS
Class: I / FULL_EXACT_SHA
Quality gate: SUCCESS
Docker Compose smoke: SUCCESS
Publication proof: SKIPPED
Verification gate: SUCCESS
Workflow conclusion: SUCCESS
```

## 11. Separate report publication proof

This report and `docs/CURRENT_STATE.md` are the entire authorized report
commit. That immutable commit must classify `P / PUBLICATION_EXACT_SHA`, pass
Publication proof and Verification, and skip Quality and Compose. Its own SHA
and CI run cannot be embedded in the same commit; the final Codex handoff
records them after the publication gate.

## 12. Git and review boundary

Immediately before the report delta, local HEAD, tracking HEAD, direct remote
W03 HEAD and PR #6 HEAD were the final implementation SHA with `0 ahead / 0
behind`; the working tree was clean. Main remained
`9d18ddde9fe933952a2661ee1419f13c8577605d`. PR #6 remained open, draft and
unmerged. No merge, rebase, cherry-pick or auto-merge operation was active.

```text
GPT C04 REVIEW: PENDING
HUMAN C04 ACCEPTANCE: PENDING
C04 CLOSED: NO
C05 AUTHORIZED: NO
STATUS: REVIEW_READY ONLY AFTER REPORT PUBLICATION GATE
```

## Machine-readable harness summary

```json
{
  "round_id": "W03-C04",
  "starting_sha": "1c0f4de6f897d9e377fba63891773bb5970e74b7",
  "implementation_sha": "62405d7169b1aaea321290749395ab077792f86f",
  "recovery_state": "A",
  "engineering": {
    "focused_c04": "PASS: 24",
    "c03_regression": "PASS: 77",
    "c01_regression": "PASS: 39",
    "c02_regression": "PASS: 26",
    "w2_regression": "PASS: 154",
    "non_integration": "PASS: 518",
    "remote_integration": "PASS: 48",
    "ruff": "PASS",
    "mypy": "PASS: 98 source files",
    "git_diff_check": "PASS",
    "compose_config": "PASS"
  },
  "semantic": {
    "exact_four_family_registry": "PASS",
    "candidate_parameter_config_binding": "PASS",
    "closed_observation_gate": "PASS",
    "independent_business_diff": "PASS",
    "measurement_schema": "PASS",
    "legacy_w2_business_equivalence": "PASS",
    "legacy_hgt_preservation": "PASS",
    "medium_01": "CLOSED"
  },
  "safety": {
    "runtime_hgt_access": "NONE",
    "future_leakage": "NONE",
    "post_c02_db_access": "NONE",
    "filesystem_network_model_access": "NONE",
    "operational_mutation": "NONE",
    "c05_capability": "NONE"
  },
  "ci": {
    "run_id": 36227210323,
    "run_number": 55,
    "class": "I",
    "gate": "FULL_EXACT_SHA",
    "head_sha_matches": true,
    "quality_gate": "PASS",
    "docker_compose_smoke": "PASS",
    "publication_proof": "SKIPPED",
    "verification_gate": "PASS"
  }
}
```
