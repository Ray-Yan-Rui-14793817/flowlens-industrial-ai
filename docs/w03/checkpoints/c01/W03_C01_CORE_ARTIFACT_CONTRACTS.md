# FlowLens Industrial AI — W03-C01 Core Artifact Contracts

**Checkpoint:** `W03-C01`
**Contract bundle:** `w03-c01-v1`
**Purpose:** immutable schemas only; no business-loop implementation

## 1. Global rules

Every C01 artifact must be immutable, keyword-only, slots-enabled, validated,
deterministically serializable, provenance-aware, and free of mutable aggregate
containers.

Allowed scalar values:

```text
None
bool
int
str
Decimal
date
timezone-aware datetime
```

Forbidden semantic values:

```text
float
naive datetime
arbitrary object
ORM row
database session
bytes payload
```

Corrections create a new artifact/run or a new append-only HumanDecisionEvent.

## 2. Support types

### VersionRef

```text
name: str
version: str
```

### EntityRef

```text
entity_type: str
entity_id: str
```

This does not imply causal relationship.

### SourceRef

```text
source_entity: str
source_record_id: str
source_field: str
observed_at: datetime | None
available_at: datetime
```

### ArtifactProvenance

```text
producer: str
producer_version: str
input_artifact_ids: tuple[str, ...]
source_refs: tuple[SourceRef, ...]
contract_versions: tuple[VersionRef, ...]
implementation_sha: str | None
```

`implementation_sha` is a Git object ID: 40 lowercase hexadecimal characters
for the current repository, or 64 lowercase hexadecimal characters for a Git
SHA-256 repository. It is distinct from the 64-character artifact and dataset
SHA-256 digests.

Provenance must not contain HGT payload, scenario answer, true root cause,
reviewer reasoning or Codex prompt text.

### Limitation

```text
code: str
message: str
```

### Uncertainty

```text
status: UncertaintyStatus
code: str
message: str
evidence_ids: tuple[str, ...]
```

Frozen `UncertaintyStatus`:

```text
UNKNOWN
INSUFFICIENT_EVIDENCE
ASSOCIATIVE_ONLY
UNRESOLVED_DISPOSITION
```

### NamedValue

```text
name: str
value: ScalarValue
unit: str | None
```

Structural envelope only for candidate parameters, simulation measurements,
future score components and evaluation metrics.

### SnapshotEntry

```text
entry_key: str
entity: EntityRef
field: str
value: ScalarValue
observed_at: datetime | None
available_at: datetime
source_ref: SourceRef
```

C02 owns which W2 records become entries.

### DiagnosisClaim

```text
claim_code: str
claim_type: ClaimType
statement: str
evidence_ids: tuple[str, ...]
limitations: tuple[Limitation, ...]
```

Frozen `ClaimType`:

```text
FACT_CLAIM
DERIVED_CLAIM
ASSOCIATIVE_CLAIM
UNCERTAINTY_STATEMENT
```

### ExplanationSection

```text
section_key: str
text: str
```

C08 owns the final section vocabulary.

## 3. Frozen enums

### TrustLevel

```text
DIRECT_FACT
DERIVED_FACT
ASSOCIATIVE_EVIDENCE
UNKNOWN
FORBIDDEN_INFERENCE
```

### FreshnessStatus

```text
FRESH
STALE
EXPIRED
UNKNOWN
NOT_APPLICABLE
```

### SignalType

```text
SUPPLIER_LATE_RECEIPT
MATERIAL_TIMING_RISK
QUALITY_FAILURE
REWORK_PRESENT
QUALITY_DISPOSITION_UNKNOWN
QUEUE_DELAY
CAPACITY_PRESSURE
DELIVERY_RISK
```

### SignalState

```text
ACTIVE
INACTIVE
UNKNOWN
```

C03 defines when each applies.

### InterventionFamily

```text
NO_ACTION
SUPPLIER_INTERVENTION
QUALITY_INTERVENTION
CAPACITY_INTERVENTION
```

### SimulationStatus

```text
SUCCEEDED
UNAVAILABLE
FAILED
```

### RecommendationDisposition

```text
CANDIDATE_RECOMMENDED
NO_ACTION
NO_RECOMMENDATION
INVESTIGATION_ONLY
DEFER_TO_HUMAN
```

C05 defines the rules selecting a disposition.

### ExplanationMode

```text
DETERMINISTIC_TEMPLATE
BOUNDED_LLM
DEGRADED_TEMPLATE
```

C01 adds no LLM capability.

### HumanDecisionType

```text
ACCEPT
REJECT
DEFER
```

### EvaluationStatus

```text
PENDING
COMPLETED
FAILED
```

### DecisionRunState

```text
CREATED
SNAPSHOT_BUILDING
SNAPSHOT_READY
TRUST_CHECKING
TRUST_VERIFIED
SIGNALS_READY
DIAGNOSIS_READY
CANDIDATES_READY
SIMULATION_READY
RECOMMENDATION_READY
PACKET_READY
EXPLANATION_READY
HUMAN_PENDING
HUMAN_DECIDED
RUNTIME_COMPLETE

BLOCKED_CONTEXT
BLOCKED_TEMPORAL
BLOCKED_HGT
BLOCKED_TRUST
BLOCKED_CONTRACT

BLOCKED_INSUFFICIENT_EVIDENCE
SIMULATION_PARTIAL
SIMULATION_FAILED
NO_RECOMMENDATION
EXPLANATION_DEGRADED
```

The enum does not implement transitions.

### EvaluationState

```text
EVAL_NOT_STARTED
RECOMMENDATION_EVAL_READY
RECOMMENDATION_EVALUATED
OUTCOME_PENDING
OUTCOME_AVAILABLE
OUTCOME_EVALUATED
```

## 4. Artifact contracts

### 4.1 DecisionRun

Schema: `decision-run.v1`

```text
run_id: str
schema_version: str
order_id: str
as_of_time: datetime
dataset_version: str
dataset_hash: str
contract_bundle_version: str
tool_registry_version: str
provenance: ArtifactProvenance
```

Rules:

- timezone-aware `as_of_time`;
- dataset hash is 64 lowercase hex;
- C01 bundle is `w03-c01-v1`;
- no HGT/scenario-label field;
- immutable identity artifact does not carry a mutable current-state field.

### 4.2 StateSnapshot

Schema: `state-snapshot.v1`

```text
snapshot_id: str
schema_version: str
run_id: str
order_id: str
as_of_time: datetime
dataset_version: str
dataset_hash: str
snapshot_hash: str
entries: tuple[SnapshotEntry, ...]
unknowns: tuple[Uncertainty, ...]
provenance: ArtifactProvenance
```

Rules:

- immutable observation envelope;
- `snapshot_hash` represents semantic observation payload, not developer metadata;
- every snapshot-level `Uncertainty` must have `evidence_ids == ()`, because
  the snapshot is frozen before Evidence IDs exist;
- every entry must satisfy `available_at <= as_of_time`;
- real W2→snapshot mapping and Semantic Trust mapping remain C02;
- no HGT.

### 4.3 Evidence

Schema: `evidence.v1`

```text
evidence_id: str
schema_version: str
run_id: str
snapshot_id: str
source_entity: str
source_record_id: str
source_field: str
value: ScalarValue
observed_at: datetime | None
available_at: datetime
as_of_time: datetime
relationship_type: str
trust_level: TrustLevel
freshness_status: FreshnessStatus
limitations: tuple[Limitation, ...]
provenance: ArtifactProvenance
```

Hard validation:

```text
available_at <= as_of_time
```

C02 owns real trust/freshness mapping.

### 4.4 EvidenceBundle

Schema: `evidence-bundle.v1`

```text
evidence_bundle_id: str
schema_version: str
run_id: str
snapshot_id: str
snapshot_hash: str
evidence: tuple[Evidence, ...]
uncertainties: tuple[Uncertainty, ...]
provenance: ArtifactProvenance
```

Every Evidence must match run/snapshot. Evidence is canonical by `evidence_id`;
duplicates reject.

### 4.5 Signal

Schema: `signal.v1`

```text
signal_id: str
schema_version: str
run_id: str
snapshot_id: str
signal_type: SignalType
state: SignalState
evidence_ids: tuple[str, ...]
reason_codes: tuple[str, ...]
limitations: tuple[Limitation, ...]
provenance: ArtifactProvenance
```

No trigger/threshold semantics in C01.

### 4.6 SignalBundle

Schema: `signal-bundle.v1`

```text
signal_bundle_id: str
schema_version: str
run_id: str
snapshot_id: str
signals: tuple[Signal, ...]
provenance: ArtifactProvenance
```

Duplicate `SignalType` rejects. Canonical order is `signal_type.value`.

### 4.7 DiagnosisRecord

Schema: `diagnosis-record.v1`

```text
diagnosis_id: str
schema_version: str
run_id: str
snapshot_id: str
problem_code: str
claims: tuple[DiagnosisClaim, ...]
supporting_signal_ids: tuple[str, ...]
supporting_evidence_ids: tuple[str, ...]
uncertainties: tuple[Uncertainty, ...]
affected_path: tuple[EntityRef, ...]
reason_codes: tuple[str, ...]
provenance: ArtifactProvenance
```

`affected_path` preserves semantic order. C03 owns actual diagnosis construction.

### 4.8 InterventionCandidate

Schema: `intervention-candidate.v1`

```text
candidate_id: str
schema_version: str
run_id: str
family: InterventionFamily
registry_key: str
parameters: tuple[NamedValue, ...]
supporting_evidence_ids: tuple[str, ...]
reason_codes: tuple[str, ...]
limitations: tuple[Limitation, ...]
provenance: ArtifactProvenance
```

`registry_key` is structural only. C04 owns registry authorization/mapping.

### 4.9 CandidateSet

Schema: `candidate-set.v1`

```text
candidate_set_id: str
schema_version: str
run_id: str
snapshot_id: str
diagnosis_id: str
candidates: tuple[InterventionCandidate, ...]
provenance: ArtifactProvenance
```

Candidates share the run. Duplicate candidate IDs reject. Canonical set order is
candidate ID; this does not imply recommendation ranking.

### 4.10 SimulationResult

Schema: `simulation-result.v1`

```text
simulation_id: str
schema_version: str
run_id: str
candidate_id: str
status: SimulationStatus
baseline_snapshot_id: str
baseline_snapshot_hash: str
scenario_id: str | None
scenario_hash: str | None
affected_entities: tuple[EntityRef, ...]
measurements: tuple[NamedValue, ...]
limitations: tuple[Limitation, ...]
provenance: ArtifactProvenance
```

No HGT/true-cause field. Scenario execution remains C04.

### 4.11 SimulationBundle

Schema: `simulation-bundle.v1`

```text
simulation_bundle_id: str
schema_version: str
run_id: str
snapshot_id: str
results: tuple[SimulationResult, ...]
provenance: ArtifactProvenance
```

Canonical order is `(candidate_id, simulation_id)`.

### 4.12 RecommendationRecord

Schema: `recommendation-record.v1`

```text
recommendation_id: str
schema_version: str
run_id: str
snapshot_id: str
diagnosis_id: str
candidate_set_id: str
simulation_bundle_id: str
policy_version: str
disposition: RecommendationDisposition
selected_candidate_id: str | None
candidate_order: tuple[str, ...]
score_components: tuple[NamedValue, ...]
reason_codes: tuple[str, ...]
supporting_evidence_ids: tuple[str, ...]
uncertainties: tuple[Uncertainty, ...]
limitations: tuple[Limitation, ...]
provenance: ArtifactProvenance
```

`candidate_order` preserves semantic order. When `selected_candidate_id` is
present, it must occur in `candidate_order`. This is structural only: C01
defines no formula, scale or confidence score. C05 owns
scoring/ranking/tie/abstention rules.

### 4.13 DecisionPacket

Schema: `decision-packet.v1`

```text
packet_id: str
schema_version: str
run: DecisionRun
snapshot: StateSnapshot
evidence: EvidenceBundle
signals: SignalBundle
diagnosis: DiagnosisRecord
candidates: CandidateSet
simulations: SimulationBundle
recommendation: RecommendationRecord
uncertainties: tuple[Uncertainty, ...]
limitations: tuple[Limitation, ...]
provenance: ArtifactProvenance
```

Cross-artifact invariants:

```text
all nested run IDs == run.run_id
all snapshot-bound artifacts == snapshot.snapshot_id
snapshot_hash references agree
recommendation references nested diagnosis/candidate/simulation artifacts
```

Critical:

```text
DecisionPacket has NO human_decision field.
```

### 4.14 ExplanationRecord

Schema: `explanation-record.v1`

```text
explanation_id: str
schema_version: str
run_id: str
packet_id: str
mode: ExplanationMode
explainer_version: str
sections: tuple[ExplanationSection, ...]
referenced_evidence_ids: tuple[str, ...]
reason_codes: tuple[str, ...]
limitations: tuple[Limitation, ...]
provenance: ArtifactProvenance
```

C01 provides no explainer. C08 owns prompt/provider/model/output behavior.

### 4.15 HumanDecisionEvent

Schema: `human-decision-event.v1`

```text
decision_event_id: str
schema_version: str
run_id: str
packet_id: str
decision: HumanDecisionType
actor_id: str
decided_at: datetime
accepted_reason_codes: tuple[str, ...]
rejected_reason_codes: tuple[str, ...]
comment: str | None
investigation_priority: str | None
previous_event_id: str | None
provenance: ArtifactProvenance
```

Append-only. DEFER then ACCEPT creates two events. No overwrite API in C01.

### 4.16 RecommendationEvaluation

Schema: `recommendation-evaluation.v1`

```text
recommendation_evaluation_id: str
schema_version: str
run_id: str
recommendation_id: str
status: EvaluationStatus
evaluator_version: str
metrics: tuple[NamedValue, ...]
reason_codes: tuple[str, ...]
limitations: tuple[Limitation, ...]
provenance: ArtifactProvenance
```

Protected evaluation-plane schema only. Recommendation is already frozen.
C07 owns actual HGT access and metrics.

### 4.17 OutcomeEvaluation

Schema: `outcome-evaluation.v1`

```text
outcome_evaluation_id: str
schema_version: str
run_id: str
packet_id: str
human_decision_event_id: str
status: EvaluationStatus
evaluator_version: str
metrics: tuple[NamedValue, ...]
reason_codes: tuple[str, ...]
limitations: tuple[Limitation, ...]
provenance: ArtifactProvenance
```

Schema only; later outcome semantics are outside C01.

## 5. Runtime vs evaluation boundary

Runtime-safe:

```text
DecisionRun
StateSnapshot
Evidence
EvidenceBundle
Signal
SignalBundle
DiagnosisRecord
InterventionCandidate
CandidateSet
SimulationResult
SimulationBundle
RecommendationRecord
DecisionPacket
ExplanationRecord
HumanDecisionEvent
```

Protected evaluation:

```text
RecommendationEvaluation
OutcomeEvaluation
```

Evaluation artifacts must never be nested in `DecisionPacket`.

## 6. Deferred responsibilities

C02: snapshot population, DecisionContext, trust/freshness mapping, unknown propagation.
C03: signal triggers/thresholds and diagnosis business semantics.
C04: registry, candidate→scenario mapping and simulation execution.
C05: scoring/ranking/tie/abstention/recommendation/packet assembly behavior.
C06: HumanDecision storage/workflow.
C07: HGT evaluation behavior and metrics.
C08: bounded LLM explanation behavior.
