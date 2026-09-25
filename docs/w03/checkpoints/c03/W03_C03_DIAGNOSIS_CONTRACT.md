# FlowLens W03-C03 Diagnosis Contract V3

## 1. Purpose

`DiagnosisRecord` is structured synthesis of deterministic indicators and uncertainties.
It is not a root-cause engine and does not produce action/recommendation/LLM prose.

`build_diagnosis(bundle, context, signals)` must recompute the canonical current C03 SignalBundle
from the same bound inputs and reject a stale/tampered supplied SignalBundle:

```text
C03_SIGNAL_POLICY_MISMATCH / BLOCKED_CONTRACT
```

## 2. problem_code precedence

```text
DELIVERY_RISK ACTIVE
→ DELIVERY_COMMITMENT_WARNING

else any other ACTIVE Signal
→ OBSERVED_DELIVERY_RISK_INDICATORS

else
→ INSUFFICIENT_EVIDENCE_FOR_RISK_ASSESSMENT
```

No `RISK_FREE`, `ALL_CLEAR`, `ROOT_CAUSE` or causal problem code.

## 3. Claims

Iterate Signals sorted by `signal_type.value`.

Emit one DiagnosisClaim for every:

```text
ACTIVE signal
UNKNOWN signal
```

No claim for an INACTIVE signal.

Claim code:

```text
C03_<SignalType>_<ACTIVE|UNKNOWN>_V1
```

Claim statement is the exact fixed policy statement from `signal_policy.json` compiled into `c03_policy.py`.
No runtime file read.

Claim evidence/limitations copy the corresponding Signal evidence/limitations.

## 4. Claim types

ACTIVE:

```text
SUPPLIER_LATE_RECEIPT
MATERIAL_TIMING_RISK
→ ASSOCIATIVE_CLAIM

QUALITY_FAILURE
REWORK_PRESENT
→ FACT_CLAIM

QUALITY_DISPOSITION_UNKNOWN
QUEUE_DELAY
DELIVERY_RISK
→ DERIVED_CLAIM
```

`CAPACITY_PRESSURE` has no ACTIVE v1 claim.

Every UNKNOWN claim:

```text
UNCERTAINTY_STATEMENT
```

No claim may upgrade associative support into fact/causality.

## 5. supporting_signal_ids

Include all eight Signal IDs, sorted unique.

This records the complete bounded assessment, including INACTIVE results, without creating claims for them.

## 6. supporting_evidence_ids

Sorted union of:

```text
all Signal.evidence_ids
all Evidence IDs referenced by DecisionContext uncertainties
```

Every ID must exist in the bound EvidenceBundle and DecisionContext selected set.

## 7. Uncertainty preservation

Start with every C02 `DecisionContext.uncertainties` unchanged.

For each UNKNOWN Signal add:

```text
status = INSUFFICIENT_EVIDENCE
code = C03_UNKNOWN_<SignalType>
message = fixed unknown statement
evidence_ids = Signal.evidence_ids
```

For each ACTIVE Signal containing `C03_INPUT_INCOMPLETE`, add:

```text
status = INSUFFICIENT_EVIDENCE
code = C03_PARTIAL_<SignalType>
message = "A positive witness exists, but some rule-relevant evidence is incomplete."
evidence_ids = Signal.evidence_ids
```

Sort/deduplicate by the frozen C01 uncertainty key.

Never remove `QUALITY_FINALITY_UNKNOWN`, inventory/procurement uncertainty or other C02 uncertainty because a C03 Signal is positive/negative.

## 8. affected_path

Use only the scoped evaluation root:

```text
(
  EntityRef(entity_type="fact_sales_order", entity_id=context.order_id),
)
```

C01 stores a tuple, not a branching causal graph. Detailed operational entities remain referenced through Evidence.

Do not flatten PO/WO/Operation rows into a fake causal path.

## 9. Diagnosis reason codes

Sorted union of all eight Signal reason codes plus:

```text
C03_STRUCTURED_NOT_CAUSAL
```

## 10. Provenance

```text
producer = flowlens.decision.diagnosis
producer_version = w03-c03-v1
input_artifact_ids = evidence_bundle_id + context_id + signal_bundle_id
source_refs = deterministic union of supporting Evidence source refs
implementation_sha = None
```

Contract versions include C01, C02, C02-context, C03, C03-signals and C03-diagnosis.

## 11. Determinism

Same:

```text
EvidenceBundle
DecisionContext
C03 policy
```

must yield the same SignalBundle/DiagnosisRecord canonical bytes and IDs.

No wall clock, randomness, HGT, model or external service.

## 12. Required semantic examples

```text
fully delivered + historical failed inspection
→ DELIVERY_RISK INACTIVE
→ QUALITY_FAILURE ACTIVE claim remains
→ QUALITY_FINALITY_UNKNOWN remains
→ no all-clear / release statement

associated PO lateness
→ associative claim only
→ no supplier-caused-delay statement

critical C02 conflict
→ BLOCKED_TRUST
→ no successful SignalBundle/Diagnosis

only inactive observable signals + CAPACITY unknown
→ INSUFFICIENT_EVIDENCE_FOR_RISK_ASSESSMENT
→ not risk-free
```
