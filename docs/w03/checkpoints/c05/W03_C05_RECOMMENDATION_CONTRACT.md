# FlowLens Industrial AI — W03-C05 Recommendation Contract

```text
schema_version = recommendation-record.v1
policy_version = w03-c05-decision-v1
producer = flowlens.decision.c05_recommendation
producer_version = w03-c05-decision-v1
```

C05 uses the frozen C01 `RecommendationRecord` unchanged.

## Disposition and selected candidate

```text
NO_ACTION           → canonical NO_ACTION candidate
INVESTIGATION_ONLY  → exactly one selected active non-NO_ACTION candidate
NO_RECOMMENDATION   → selected_candidate_id = None
DEFER_TO_HUMAN      → selected_candidate_id = None
```

`CANDIDATE_RECOMMENDED` is prohibited in v1. A selected intervention family is
only a bounded investigation focus under observed evidence and the frozen
stress comparison.

## Evidence grounding

Supporting Evidence IDs are sorted and canonical:

```text
INVESTIGATION_ONLY = diagnosis evidence ∪ selected candidate evidence
NO_ACTION          = diagnosis evidence
DEFER_TO_HUMAN     = diagnosis evidence ∪ every active candidate evidence
NO_RECOMMENDATION  = diagnosis evidence ∪ every active candidate evidence
```

Every ID must exist in the supplied `EvidenceBundle`. Scenario entities and HGT
are never Evidence.

## Uncertainties

Recommendation uncertainties are the deterministic sorted union of upstream
`EvidenceBundle` and `DiagnosisRecord` uncertainties plus applicable fixed C05
uncertainties:

```text
C05_TOP_TIE                         UNRESOLVED_DISPOSITION
C05_PARTIAL_ACTIVE_COMPARISON       UNRESOLVED_DISPOSITION
C05_INSUFFICIENT_RECOMMENDATION_BASIS INSUFFICIENT_EVIDENCE
```

Upstream uncertainty is never removed; `CAPACITY_PRESSURE` uncertainty remains
visible.

## Limitations and reason codes

The closed code sets and fixed messages are in
`specs/limitation_codes.json` and `specs/reason_codes.json`. Recommendation
limitations include the deterministic union of upstream candidate/simulation
limitations and applicable C05 limitations. They must preserve association,
quality-finality, queue/capacity and stress-probe boundaries.

## Identity and provenance

Identity uses the existing C01 `RecommendationRecord` identity contract.
Provenance input IDs include the run, snapshot, EvidenceBundle, SignalBundle,
DiagnosisRecord, CandidateSet and SimulationBundle. Contract versions include
C01, C02, C03, C04, C05 decision and C05 evaluation v1. No database, session,
tool, model, HGT or wall-clock provenance is permitted.
