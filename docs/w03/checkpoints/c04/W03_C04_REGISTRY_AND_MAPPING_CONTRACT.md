# W03-C04 Registry and Mapping Contract

```text
registry_version = w03-c04-registry-v1
stress_scenario_version = w03-c04-stress-v1
cardinality = 4
```

| Family | Registry key | W2 mapping |
|---|---|---|
| `NO_ACTION` | `c04.no-action.v1` | baseline identity |
| `SUPPLIER_INTERVENTION` | `c04.supplier-stress-probe.v1` | Supplier Degradation |
| `QUALITY_INTERVENTION` | `c04.quality-stress-probe.v1` | Quality Deterioration |
| `CAPACITY_INTERVENTION` | `c04.capacity-stress-probe.v1` | Capacity Surge |

`NO_ACTION` uses `mode=BASELINE_IDENTITY` and canonical Diagnosis supporting evidence. Other
candidates use the sorted union of evidence from their frozen signal groups. An active relevant
signal adds `C04_RELEVANT_SIGNAL_ACTIVE`; otherwise the complete candidate remains and adds
`C04_RELEVANCE_NOT_ESTABLISHED`. Relevance is not causality, ranking or permission to act.

The exact fixed scenario profiles and limitations are projected by
`specs/registry_policy.json`. Every stress probe retains
`C04_STRESS_PROBE_NOT_INTERVENTION_EFFICACY` and
`C04_SCENARIO_SCOPE_NOT_ORDER_TARGETED`.

Scenario windows cover the full closed dataset period. Seeds are the first 16 hexadecimal digits
of SHA-256(candidate_id), masked to 63 bits. No caller-selected runtime parameter is allowed.
