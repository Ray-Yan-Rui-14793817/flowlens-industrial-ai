# FlowLens Industrial AI — W03-C05 Evaluation Policy

```text
decision_policy_version = w03-c05-decision-v1
evaluation_schema_version = w03-c05-evaluation-v1
```

## Candidate population and relevance

The exact canonical C04 families are evaluated:

```text
NO_ACTION
SUPPLIER_INTERVENTION
QUALITY_INTERVENTION
CAPACITY_INTERVENTION
```

`NO_ACTION` relevance is `BASELINE`. A non-`NO_ACTION` family is `ACTIVE` iff
its canonical candidate contains `C04_RELEVANT_SIGNAL_ACTIVE`; otherwise its
relevance is `NOT_ESTABLISHED`. C05 does not re-infer relevance.

## Target-order stress comparison

Compare each successful non-`NO_ACTION` result with successful `NO_ACTION` using
only:

```text
target_delivered_quantity                              lower = worse
target_remaining_quantity                              higher = worse
target_delivery_lag_seconds                            higher = worse
target_failed_quantity                                 higher = worse
target_rework_quantity                                 higher = worse
target_max_operation_start_slippage_seconds            higher = worse
target_max_work_order_completion_slippage_seconds      higher = worse
```

Per metric: `None/None = EQUAL`; exactly one `None = NOT_COMPARABLE`; otherwise
apply the frozen direction to obtain `WORSE`, `EQUAL` or `BETTER`.

Aggregate classes:

```text
WORSENED       at least one WORSE and no BETTER
UNCHANGED      comparable metrics exist and all are EQUAL
MIXED          at least one WORSE and at least one BETTER
IMPROVED       at least one BETTER and no WORSE
NOT_COMPARABLE no metric is comparable
```

`affected_entity_count`, `business_row_count_delta`, `target_last_delivery_at`,
scenario identity and HGT do not influence the decision.

## Active-family availability

```text
all active simulations UNAVAILABLE/FAILED
→ NO_RECOMMENDATION

some active SUCCEEDED and some active UNAVAILABLE/FAILED
→ DEFER_TO_HUMAN

any active successful MIXED/IMPROVED
→ DEFER_TO_HUMAN
```

When every active family succeeds and none is `MIXED`/`IMPROVED`:

```text
exactly one WORSENED
→ select it / INVESTIGATION_ONLY

more than one WORSENED
→ DEFER_TO_HUMAN

no WORSENED and exactly one active family
→ select it / INVESTIGATION_ONLY

no WORSENED and multiple active families
→ DEFER_TO_HUMAN
```

Candidate/family order never resolves a semantic tie.

## Strict neutral `NO_ACTION`

`NO_ACTION` is selected only when `DELIVERY_RISK == INACTIVE`, every material
non-capacity signal is `INACTIVE`, no intervention family is active, the
`NO_ACTION` simulation succeeded, and no unresolved critical recommendation
uncertainty exists. `CAPACITY_PRESSURE == UNKNOWN` alone does not block this
neutral result.

## `NO_RECOMMENDATION`

Use when the safe deterministic basis is insufficient, including
`DELIVERY_RISK == UNKNOWN`, material uncertainty that blocks neutral state,
active delivery risk without active intervention relevance, absent canonical
comparison material, or no successful active-family simulation.

## Categorical evaluation envelope

`RecommendationRecord.score_components` contains exactly four categorical
components per family and five policy-summary facts. Names are sorted ascending.
Values use only `bool`, `int` and categorical `str`; no float is allowed. The
exact schema is `specs/score_component_schema.json`.

## Candidate order

The order contains all four IDs exactly once. Semantic groups are:

1. active non-`NO_ACTION` families;
2. `NO_ACTION` baseline;
3. non-active non-`NO_ACTION` families.

Within a group, `SUCCEEDED` precedes `UNAVAILABLE`, which precedes `FAILED`.
For successful active families, stress order is `WORSENED`, `UNCHANGED`,
`NOT_COMPARABLE`, `MIXED`, `IMPROVED`. Candidate ID orders only exact ties for
serialization and never selects a winner.
