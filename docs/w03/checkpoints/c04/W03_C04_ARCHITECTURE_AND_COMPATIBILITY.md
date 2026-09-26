# W03-C04 Architecture and Compatibility

## Runtime flow

```text
EvidenceBundle + DecisionContext + canonical SignalBundle + canonical DiagnosisRecord
  -> exact four-candidate registry
  -> CandidateSet (canonical set order, never ranking)
  -> NO_ACTION baseline measurement
  -> closed-observation gate for three stress probes
  -> HGT-free detached W2 business transform
  -> independent business diff + raw measurements
  -> SimulationBundle
```

The runtime accepts only already-materialized in-memory data. It does not open an engine,
connection or session, query persistence, read files, call a model or inspect protected truth.

## HGT-free boundary

`apply_scenario_business_only(baseline, config, generated_at=...)` returns only a
`GeneratedDataset`. Import and execution of this path must not load, construct, read, hash,
serialize or return `HiddenGroundTruth`. The scenario package preserves its public API lazily so
that legacy imports continue to work without forcing HGT into the C04 import graph.

## W2 compatibility oracle

For Supplier Degradation, Quality Deterioration, and Capacity combined, arrival-only,
queue-only and neutral cases:

```text
legacy apply_scenario(...).dataset == business-only dataset
```

Equality is canonical business equality. Legacy HGT IDs, hashes and payloads remain unchanged;
baseline data remains detached and unchanged. Any inability to preserve these properties is a
contract conflict, not permission to change W2 semantics.
