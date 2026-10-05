# FlowLens W03-C03 Architecture and Compatibility V3

## 1. Pipeline

```text
C02 EvidenceBundle + DecisionContext
  -> C03 binding / trust / temporal / conflict validation
  -> deterministic evidence indexes
  -> eight independent Signal evaluations
  -> SignalBundle
  -> fixed-template structured DiagnosisRecord
  -> STOP
```

C03 never calls the C02 database adapter.

## 2. Public runtime APIs

```text
build_signal_bundle(bundle: EvidenceBundle, context: DecisionContext) -> SignalBundle

build_diagnosis(
    bundle: EvidenceBundle,
    context: DecisionContext,
    signals: SignalBundle,
) -> DiagnosisRecord

evaluate_c03(
    bundle: EvidenceBundle,
    context: DecisionContext,
) -> tuple[SignalBundle, DiagnosisRecord]
```

The engine accepts no threshold override, policy callback, runtime JSON path, Engine, Session,
filesystem handle, network handle, scenario object, HGT, model or clock.

## 3. Authorized source structure

```text
c03_policy.py
  closed reason/statement/limitation constants and pure policy metadata

c03_validation.py
  C03BuildError, binding/trust/temporal/conflict validation, deterministic evidence indexes

signals.py
  build_signal_bundle

diagnosis.py
  build_diagnosis + evaluate_c03
```

No new public artifact schema.

## 4. Version compatibility

Keep:

```text
DecisionRun.contract_bundle_version = w03-c01-v1
existing C01 *.v1 artifact schemas
existing C02 context schema/policy
existing tool_registry_version
```

C03 provenance adds VersionRef entries only.

Every Signal includes `C03_POLICY_V1` in reason codes because C01 Signal has no policy-version field
and reason codes are part of Signal identity.

## 5. Runtime product meaning

```text
ACTIVE
= an authorized versioned rule has a positive witness

INACTIVE
= this specific indicator is absent in the admitted observation scope
  (not an all-clear business conclusion)

UNKNOWN
= the observation scope/evidence does not support the indicator answer

BLOCKED_*
= invalid/conflicting input prevents successful C03 output
```

## 6. Key capability boundaries

```text
CAPACITY_PRESSURE:
UNKNOWN-only in v1

QUEUE_DELAY:
start-slippage proxy only

DELIVERY_RISK:
narrow deterministic commitment warning, not forecast probability

route variance:
not a C03 Signal

quality/rework:
no formal release inference

procurement/inventory:
no target-order allocation inference
```

## 7. No raw Snapshot bypass

C03 does not need `StateSnapshot` as a runtime reasoning input.
The closed C02 layer already converts the immutable observation world into EvidenceBundle and DecisionContext.

C03 validates their bindings, but it does not reconstruct C02 or query raw facts again.
