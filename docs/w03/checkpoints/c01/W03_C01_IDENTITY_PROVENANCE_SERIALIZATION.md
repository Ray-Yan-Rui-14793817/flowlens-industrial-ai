# FlowLens Industrial AI — W03-C01 Identity, Provenance & Serialization Contract

**Checkpoint:** `W03-C01`
**Contract bundle version:** `w03-c01-v1`

## 1. Identity principle

Artifact identity must be deterministic, replayable, independent of wall-clock
construction time, Python object address and hash randomization.

C01 does not use random UUIDs for deterministic runtime artifacts.

## 2. Artifact ID algorithm

```text
identity_object =
{
  "artifact_kind": <kind>,
  "schema_version": <schema>,
  "identity": <artifact-specific identity payload>
}

canonical_identity_bytes =
UTF-8(canonical JSON(identity_object))

digest =
sha256(canonical_identity_bytes).hexdigest()

artifact_id =
<prefix> + digest
```

Use the full 64 lowercase hexadecimal SHA-256 digest.

| Artifact | Prefix |
|---|---|
| DecisionRun | `run_` |
| StateSnapshot | `snap_` |
| Evidence | `ev_` |
| EvidenceBundle | `evb_` |
| Signal | `sig_` |
| SignalBundle | `sigb_` |
| DiagnosisRecord | `diag_` |
| InterventionCandidate | `cand_` |
| CandidateSet | `cset_` |
| SimulationResult | `sim_` |
| SimulationBundle | `simb_` |
| RecommendationRecord | `rec_` |
| DecisionPacket | `pkt_` |
| ExplanationRecord | `exp_` |
| HumanDecisionEvent | `hdec_` |
| RecommendationEvaluation | `reval_` |
| OutcomeEvaluation | `oeval_` |

No C01 artifact ID is persisted into the W2 operational schema.

## 3. Identity payloads

DecisionRun:

```text
order_id
as_of_time
dataset_version
dataset_hash
contract_bundle_version
tool_registry_version
```

StateSnapshot:

```text
run_id
snapshot_hash
```

Evidence:

```text
run_id
snapshot_id
source_entity
source_record_id
source_field
canonical value
observed_at
available_at
as_of_time
relationship_type
trust_level
freshness_status
```

EvidenceBundle:

```text
run_id
snapshot_id
snapshot_hash
ordered evidence IDs
ordered uncertainty payloads
```

Signal:

```text
run_id
snapshot_id
signal_type
state
ordered evidence IDs
ordered reason codes
```

SignalBundle:

```text
run_id
snapshot_id
ordered signal IDs
```

DiagnosisRecord:

```text
run_id
snapshot_id
problem_code
claims
supporting signal IDs
supporting evidence IDs
uncertainties
affected_path
reason_codes
```

InterventionCandidate:

```text
run_id
family
registry_key
parameters
supporting evidence IDs
reason codes
```

CandidateSet:

```text
run_id
snapshot_id
diagnosis_id
ordered candidate IDs
```

SimulationResult:

```text
run_id
candidate_id
status
baseline_snapshot_id
baseline_snapshot_hash
scenario_id
scenario_hash
affected entities
measurements
```

SimulationBundle:

```text
run_id
snapshot_id
ordered (candidate_id, simulation_id)
```

RecommendationRecord:

```text
run_id
snapshot_id
diagnosis_id
candidate_set_id
simulation_bundle_id
policy_version
disposition
selected_candidate_id
candidate_order
score_components
reason_codes
supporting evidence IDs
uncertainties
```

DecisionPacket:

```text
run_id
snapshot_id
evidence_bundle_id
signal_bundle_id
diagnosis_id
candidate_set_id
simulation_bundle_id
recommendation_id
packet uncertainties
packet limitations
```

ExplanationRecord:

```text
run_id
packet_id
mode
explainer_version
sections
referenced evidence IDs
reason codes
limitations
```

HumanDecisionEvent:

```text
run_id
packet_id
decision
actor_id
decided_at
accepted reason codes
rejected reason codes
comment
investigation priority
previous_event_id
```

RecommendationEvaluation:

```text
run_id
recommendation_id
status
evaluator_version
metrics
reason_codes
limitations
```

OutcomeEvaluation:

```text
run_id
packet_id
human_decision_event_id
status
evaluator_version
metrics
reason_codes
limitations
```

## 4. Snapshot hash

`snapshot_hash` represents the immutable semantic observation world.

Hash payload:

```text
order_id
as_of_time
dataset_version
dataset_hash
entries
unknowns
```

Snapshot-level `unknowns` are pre-Evidence observations: each must have
`evidence_ids == ()`. Evidence-linked uncertainties belong in downstream
artifacts. This prevents `snapshot_hash → snapshot_id → evidence_id` from
depending on a downstream Evidence ID.

Excluded:

```text
snapshot_id
snapshot_hash itself
implementation_sha
developer/reviewer comments
Codex prompt
HGT
scenario truth
wall-clock construction timestamp
```

Then `snapshot_id` derives from `run_id + snapshot_hash + schema_version`.

## 5. Canonical scalar normalization

Use the frozen W2 scalar semantics for supported scalar types:

```text
None → null
bool → JSON boolean
int → JSON integer
str → JSON string

Decimal
→ plain decimal string
→ no exponent
→ trailing zeroes removed
→ negative zero normalized to "0"

datetime
→ timezone-aware only
→ convert to UTC
→ ISO 8601 microseconds
→ terminal Z

date
→ ISO YYYY-MM-DD
```

Reject `float`.

Important:

```text
C01 ARTIFACT ID/HASH
!=
W2 CANONICAL DATASET HASH
```

Do not modify or substitute the W2 business hash algorithm.

## 6. Canonical JSON

```text
json.dumps(
    primitive_payload,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
```

Rules:

- `StrEnum` serializes to `.value`;
- dataclasses serialize by declared field names;
- tuples become JSON arrays;
- object keys sort lexicographically;
- no pretty-print whitespace in canonical bytes.

## 7. Ordering

Set-like tuples must be sorted and unique:

```text
reason_codes
non-semantic evidence ID sets
input_artifact_ids
contract_versions by (name, version)
source_refs by stable source tuple
limitations by (code, message)
```

Semantic-order tuples preserve order:

```text
affected_path
candidate_order
ExplanationRecord.sections
HumanDecision event chain
```

Bundle ordering:

```text
EvidenceBundle.evidence → evidence_id
SignalBundle.signals → signal_type.value
CandidateSet.candidates → candidate_id
SimulationBundle.results → (candidate_id, simulation_id)
```

## 8. Provenance rules

Allowed runtime provenance:

```text
producer
producer version
input artifact IDs
operational source refs
contract versions
implementation SHA
```

`implementation_sha` means a Git object ID, accepting 40 or 64 lowercase hex
characters. It is not validated as a fixed 64-character artifact/dataset
SHA-256 digest.

Forbidden runtime provenance:

```text
scenario label
true root cause
HGT record
expected test answer
reviewer comment
developer reasoning
Codex prompt text
```

Evaluation provenance remains protected and cannot enter DecisionPacket.

## 9. Versioning

C01 freezes `w03-c01-v1` and artifact `*.v1` schemas.

Any change in field meaning, required fields, identity fields or canonical serialization
requires a new schema version and explicit GPT/Human authorization.

Codex may not silently version-bump.

## 10. Validation

At minimum:

```text
IDs match expected prefix + 64 lowercase hex
hashes are 64 lowercase hex
implementation_sha, when present, is a 40- or 64-character lowercase Git object ID
required strings non-empty/stripped
datetimes timezone-aware
Evidence available_at <= as_of_time
StateSnapshot.unknowns[*].evidence_ids == ()
tuples deeply immutable
set-like tuples sorted/unique
bundle members share run/snapshot
DecisionPacket references are consistent
selected_candidate_id, when present, occurs in candidate_order
runtime artifacts have no protected HGT/scenario-truth field
```

## 11. Authorized serialization utilities

May include:

```text
canonical_primitive(value)
canonical_json_bytes(value)
canonical_json_text(value)
sha256_hex(value)
derive_artifact_id(kind, schema_version, identity_payload)
compute_snapshot_hash(snapshot_semantic_payload)
validate_artifact_id(...)
```

Not required:

```text
filesystem persistence
database persistence
generic JSON deserialization
API schema generation
network transport
```

If Codex believes deserialization is necessary, stop and escalate rather than expanding scope.
