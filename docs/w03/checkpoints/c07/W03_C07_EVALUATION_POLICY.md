# FlowLens Industrial AI — W03-C07 Evaluation Policy

## Frozen boundary

C07 produces the unchanged C01 `recommendation-evaluation.v1` artifact after a
C05 recommendation is frozen. Successful canonical inputs emit
`EvaluationStatus.COMPLETED`. Invalid or inconsistent inputs fail closed and do
not produce an accepted evaluation artifact.

`OutcomeEvaluation` is deferred. `HumanDecisionEvent` is not an operational
business outcome.

## Truth modes and families

Exactly three truth modes exist:

```text
NEUTRAL_CONTROL
EFFECTFUL_OBSERVABLE
EFFECTFUL_NOT_OBSERVABLE
```

Family mapping is frozen:

```text
SCN_SUPPLIER_DEGRADATION -> SUPPLIER_INTERVENTION
SCN_QUALITY_DETERIORATION -> QUALITY_INTERVENTION
SCN_CAPACITY_SURGE -> CAPACITY_INTERVENTION
```

Neutral means all HGT affected-entity tuples and the causal chain are empty.
Target IDs alone do not make a scenario effectful.

## Cause direction

Supplier uses `SUPPLIER_LATE_RECEIPT` and `MATERIAL_TIMING_RISK`. Quality uses
`QUALITY_FAILURE` and `REWORK_PRESENT`; `QUALITY_DISPOSITION_UNKNOWN` alone is
not proof. An `INACTIVE -> ACTIVE` transition on an expected signal is `TRUE`.
A comparable unsaturated pair with no expected active scenario signal and no
expected unknown is `FALSE`. Saturation or uncertainty is not applicable.

Capacity never promotes `CAPACITY_PRESSURE`; its scenario state must remain
`UNKNOWN`. Queue-observable Capacity requires `QUEUE_DELAY INACTIVE -> ACTIVE`.
Capacity arrival-only truth without an order-level realized queue effect is
`EFFECTFUL_NOT_OBSERVABLE` and is not a C03 false negative.

## Descriptive metrics

For observable truth, candidate relevance requires the expected family,
`C04_RELEVANT_SIGNAL_ACTIVE`, and the matching C05 `relevance_class=ACTIVE`.

The recommendation review-set is:

```text
INVESTIGATION_ONLY = selected family
DEFER_TO_HUMAN = all ACTIVE non-NO_ACTION families
NO_RECOMMENDATION = empty
NO_ACTION = NO_ACTION
```

Recommendation coverage is expected-family membership in that set.

False positives are baseline-delta aware. For observable truth, they are new
active non-expected families. For neutral truth, any new active family is a
false positive. Non-observable truth is not applicable.

Neutral stability compares semantic recommendation projections, not IDs. The
projection contains disposition, selected family, candidate-order family
sequence, all C05 score-component name/value pairs, reason codes, uncertainty
semantic tuples, limitation semantic tuples, and supporting-evidence count.

## Exact metric envelope

Metrics contain exactly the sorted names and types in
`specs/c07_metric_schema.json`. No float, aggregate score, accuracy,
probability, confidence, utility, benefit or causal-confidence metric exists.

Reason codes and limitations are exactly the frozen machine-readable
vocabularies. All completed evaluations include `C07_POLICY_V1` and
`C07_PROTECTED_EVALUATION_ONLY`.

## Provenance

```text
producer = flowlens.evaluation.c07_recommendation
producer_version = w03-c07-evaluator-v1
source_refs = ()
implementation_sha = None
```

Input artifact IDs are the sorted unique scenario packet/recommendation IDs and
the paired baseline packet/recommendation IDs when a baseline packet exists.
Contract versions include C01, C05 packet, C07 evaluation, C07 metrics, and the
actual supplied W2 HGT schema version.
