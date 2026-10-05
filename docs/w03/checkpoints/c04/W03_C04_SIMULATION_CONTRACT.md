# W03-C04 Simulation Contract

```text
scenario_adapter_version = w03-c04-scenario-adapter-v1
measurement_schema_version = w03-c04-measurements-v1
automatic_retry_count = 0
```

Every `SimulationBundle` has exactly one result per registry candidate in canonical
`(candidate_id, simulation_id)` order.

`NO_ACTION` always succeeds, uses no scenario engine, has no scenario identity, has no affected
entities, and reports baseline target-order measurements. If a baseline is absent, the three
stress probes are `UNAVAILABLE` with `C04_SIMULATION_BASELINE_NOT_SUPPLIED`.

Before a stress probe can run, dataset version binding, stored and recomputed canonical hashes,
the full-period end instant in Asia/Shanghai, and all frozen event/actual timestamp ceilings must
match the DecisionRun. Gate failure produces deterministic `UNAVAILABLE` results without calling
the adapter. W2 precondition insufficiency maps to
`C04_SCENARIO_PRECONDITION_UNAVAILABLE`; an unexpected post-gate engine error maps to `FAILED`
with `C04_SCENARIO_EXECUTION_FAILED` and no exception text.

Successful stress probes contain the W2 scenario identity and scenario business hash,
independently computed affected entities, and only the raw measurements in
`specs/measurement_schema.json`. They contain no HGT-derived value, score, confidence,
probability, ranking, recommendation, utility or benefit assertion.

Baseline canonical hash, row counts, scalar payload, ORM values and session-detachment state are
captured before and verified after each probe. C04-induced mutation hard-fails as
`C04_BASELINE_MUTATION`.
