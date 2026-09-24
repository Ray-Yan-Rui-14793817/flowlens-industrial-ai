# FlowLens Industrial AI — W03-C01 Harness & Acceptance Specification

**Checkpoint:** `W03-C01`

## 1. Capability proof matrix

| Capability | Invariant | Required proof | Failure action |
|---|---|---|---|
| Contract import | no DB/HGT/LLM side effect | import/dependency audit | hard fail |
| Frozen dataclasses | artifact immutable | mutation tests | fail |
| Deep immutability | no list/dict/set fields | field/type audit | fail |
| Enums | exact frozen vocabulary | exact-value tests | fail |
| Time safety | no naive datetime | negative constructor tests | reject |
| Evidence temporal rule | `available_at <= as_of_time` | boundary tests | reject |
| Scalar contract | no float | negative tests | reject |
| Artifact IDs | deterministic/prefix-bound | repeat/change tests | fail |
| Snapshot hash | stable observation identity | replay/hash tests | fail |
| Serialization | same object → same bytes | repeat/order tests | fail |
| Bundle identity | run/snapshot consistent | mismatch tests | reject |
| Packet consistency | nested references consistent | mismatch tests | reject |
| Human authority | packet has no human-decision mutation | schema test | hard fail |
| Human event | immutable append-only shape | mutation/chain tests | fail |
| HGT isolation | no runtime HGT fields/imports | schema/import/source audit | hard fail |
| Evaluation separation | eval artifacts absent from packet | schema test | hard fail |
| No operational mutation | no DB write behavior | import/source boundary | hard fail |
| Replay | same inputs → same IDs/bytes | replay test | fail |

## 2. Required focused tests

Authorized:

```text
tests/test_decision_contracts.py
tests/test_decision_serialization.py
```

Minimum test families:

- valid construction for every artifact/support type;
- frozen/keyword-only behavior;
- exact enum membership;
- naive datetime rejection;
- `available_at == as_of_time` accept;
- `available_at < as_of_time` accept;
- `available_at > as_of_time` reject;
- float rejection;
- deterministic IDs;
- wrong ID prefix/digest rejection;
- deterministic canonical JSON;
- Decimal and datetime canonicalization;
- snapshot hash stability;
- producer SHA change alone does not alter snapshot hash;
- semantic snapshot change alters snapshot hash;
- bundle run/snapshot mismatch rejection;
- duplicate bundle member rejection;
- packet cross-reference mismatch rejection;
- DecisionPacket has no human-decision field;
- HumanDecisionEvent references packet and is immutable;
- no runtime HGT fields/imports;
- import side-effect freedom;
- evaluation artifacts never nested into packet.

## 3. Engineering gates

Before implementation commit:

```text
focused C01 pytest
pytest -m "not integration"
ruff check .
mypy .
git diff --check
docker compose config --quiet
dependency files unchanged
```

Local integration may run when safely available. Final integration evidence is the
exact implementation SHA on existing Draft PR CI.

Require:

```text
Quality gate: SUCCESS
Docker Compose smoke: SUCCESS
```

## 4. No-new-capability audit

C01 must prove absence of:

```text
database decision query/write
StateSnapshot Builder
DecisionContext Builder
signal calculation
diagnosis engine
candidate registry
scenario execution
scoring
recommendation policy
human-action execution
HGT evaluation
LLM
agent
runtime tool
```

## 5. Context Delta

Expected:

```text
changed_contracts:
C01 contract package only

changed_sources:
src/flowlens/decision/* only

changed_assumptions:
NONE

changed_tool_permissions:
NONE

changed_context_materials:
C01 docs/report only

changed_runtime_inputs:
NONE
```

Rule:

```text
actual_delta ⊆ authorized_delta
```

otherwise the round is not closeable.

## 6. Machine-readable summary template

```json
{
  "round_id": "W03-C01",
  "implementation_sha": "<sha>",
  "engineering": {
    "focused_pytest": "PASS",
    "non_integration_pytest": "PASS",
    "ruff": "PASS",
    "mypy": "PASS",
    "git_diff_check": "PASS",
    "compose_config": "PASS"
  },
  "contracts": {
    "immutability": "PASS",
    "enum_exactness": "PASS",
    "artifact_identity": "PASS",
    "canonical_serialization": "PASS",
    "reference_consistency": "PASS",
    "human_event_separation": "PASS"
  },
  "semantic_safety": {
    "future_leakage_structural_gate": "PASS",
    "hgt_runtime_fields": "NONE",
    "runtime_hgt_imports": "NONE",
    "operational_mutation": "NONE"
  },
  "loop": {
    "replay": "PASS",
    "new_runtime_capability": "NONE"
  },
  "ci": {
    "run_id": "<id>",
    "head_sha_matches": true,
    "quality_gate": "PASS",
    "docker_compose_smoke": "PASS"
  }
}
```

## 7. Maximum Codex status

```text
IMPLEMENTATION: COMPLETE
CONTEXT LOCK: VERIFIED
CONTRACT PRESERVED: YES
HARNESS: PASS
EXACT-SHA CI: PASS
ROUND REPORT: READY
GPT REVIEW: PENDING
HUMAN ACCEPTANCE: PENDING
CHECKPOINT CLOSED: NO
STATUS: REVIEW_READY
```
