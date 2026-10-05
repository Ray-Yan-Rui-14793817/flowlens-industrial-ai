# FlowLens W03-C03 Identity, Provenance and Replay V3

## 1. Reuse C01 identity exactly

Do not modify C01 schemas or serializers.

Signal identity remains the existing C01 identity:

```text
run_id
snapshot_id
signal_type
state
evidence_ids
reason_codes
```

Every Signal includes `C03_POLICY_V1` so policy participation is identity-visible.

SignalBundle identity remains the ordered Signal IDs.
DiagnosisRecord identity remains the frozen C01 Diagnosis identity.

## 2. Signal provenance

```text
producer = flowlens.decision.signals
producer_version = w03-c03-v1
input_artifact_ids = (EvidenceBundle.evidence_bundle_id, DecisionContext.context_id)
source_refs = deterministic union of supporting Evidence source refs
implementation_sha = None
```

Contract versions include:

```text
w03-c01/v1
w03-c02/v1
w03-c02-context/v1
w03-c03/v1
w03-c03-signals/v1
```

SignalBundle provenance additionally references all Signal IDs.

## 3. Fixed-input replay

Same bound C02 artifacts and policy:

```text
same Signal IDs
same SignalBundle ID
same Diagnosis ID
same canonical bytes
```

Input evidence ordering must not change output.

## 4. Future-tail metamorphic replay

Two complete datasets may have different dataset hashes while sharing identical authorized history through T.
Artifact IDs can differ because upstream snapshot identity binds dataset ownership/hash.

Therefore compare normalized C03 semantics, not cross-dataset artifact IDs.

Normalize:

```text
Signal:
signal_type
state
reason codes
semantic Evidence keys
limitations

Diagnosis:
problem_code
claim code/type/statement
semantic Evidence references
uncertainties
affected_path
reason codes
```

Required future-tail families include:

```text
future delivery
future inspection/rework
future PO receipt/quantity
future WorkOrder/Operation actual events
future inventory
missing inventory
missing quality
missing procurement
critical conflict (compare same BLOCKED_TRUST outcome)
```

Changing a plan field already available at T is not a valid future-only mutation.

## 5. No self-referential SHA

Implementation SHA and CI proof belong in the later Development Round Report.
Do not put an unknown future commit SHA into content that is part of that same commit.
