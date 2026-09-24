# FlowLens Industrial AI — W03 AI Loop Harness & Reporting Specification

**Task:** W03-G0-GPT-07\
**Status:** FROZEN FOR G0 HUMAN REVIEW\
**Baseline:** `main@9d18ddde9fe933952a2661ee1419f13c8577605d`

---

## 1. Principle

```text
MODEL IS NOT THE SYSTEM BOUNDARY
HARNESS IS THE SYSTEM BOUNDARY
```

and:

```text
NO NEW AI CAPABILITY
WITHOUT A CORRESPONDING HARNESS GATE
```

Harness means:

```text
DETECTION + ENFORCEMENT + EVIDENCE
```

---

## 2. Three Harness Layers

### Engineering Test Harness

```text
pytest
PostgreSQL integration
Ruff
strict mypy
uv lock
Docker Compose
GitHub Actions
```

---

### AI Evaluation Harness

Minimum families:

```text
Temporal leakage
HGT leakage
Evidence grounding
Reason-code correctness
Feature determinism
Scenario direction
Neutral-case stability
Abstention behavior
Replay determinism
Model-output schema
Unsupported causal claims
Prompt-injection resistance when LLM exists
```

---

### Runtime Safety Harness

Pre-reasoning:

```text
Semantic Trust Gate
↓
Temporal Gate
↓
HGT Gate
↓
Evidence Gate
```

Post-model:

```text
Output Schema Gate
↓
Grounding Gate
↓
Unsupported-Claim Gate
↓
Human Review
```

---

## 3. Capability Proof Matrix

| Capability | Invariant | Required proof | Failure action |
|---|---|---|---|
| Snapshot | no future/HGT facts | temporal + HGT tests | abort |
| Snapshot | stable identity | replay/hash test | fail |
| Evidence | provenance complete | provenance completeness | reject evidence |
| Semantic Trust | association stays association | semantic fixtures | reject claim |
| Signal | deterministic | replay/direction tests | fail signal stage |
| Diagnosis | evidence-backed | claim/evidence coverage | reject diagnosis |
| CandidateSet | registry only | registry allowlist test | reject candidate |
| Simulation | baseline immutable | before/after canonical comparison | hard fail |
| Simulation | expected direction | golden scenario tests | fail candidate/scenario |
| Recommendation | authorized inputs only | provenance + replay | reject recommendation |
| Recommendation | abstains when required | negative fixtures | fail policy |
| LLM explanation | no new facts | grounding/claim diff | discard explanation |
| LLM explanation | schema valid | schema validator | retry/fallback |
| Tool call | authorized caller/stage | permission tests | deny + audit |
| Human decision | no automatic execution | state-machine test | hard fail |
| HGT evaluator | HGT isolated | dependency/import/runtime tests | hard fail |

---

## 4. Positive Golden Pack

Reuse Week 2 deterministic scenarios:

```text
baseline
supplier degradation
quality deterioration
capacity surge
neutral control
```

Expected directions:

```text
supplier degradation
→ supplier-related evidence/risk increases where contractually supported

quality deterioration
→ quality/rework evidence increases

capacity surge
→ capacity/queue evidence increases

neutral
→ no false escalation
```

Runtime Decision Loop must not receive the scenario label.

HGT is read only by the Evaluation Harness.

---

## 5. Negative / Adversarial Pack

At minimum:

```text
missing critical evidence
conflicting evidence
future-dated evidence
stale evidence
HGT injected into runtime input
unknown quality disposition

no valid candidate
all candidates fail
equal candidates

scenario adapter error
simulation timeout
baseline mutation attempt

unauthorized tool request
wrong-stage tool call
tool timeout

malformed LLM output
invented evidence
invented candidate
unsupported causal claim
recommendation drift
prompt injection attempt
```

---

## 6. Gate Enforcement

Examples:

```text
Temporal Gate FAIL
→ ABORT

HGT Gate FAIL
→ ABORT

Semantic Trust FAIL
→ reject claim / no recommendation

Grounding FAIL
→ reject claim

Unauthorized Tool
→ deny + audit

Simulation isolation FAIL
→ ABORT candidate/run according to scope

LLM schema FAIL
→ bounded retry → fallback

LLM grounding FAIL
→ discard explanation → fallback
```

---

## 7. Replay Requirements

Deterministic layer:

```text
same dataset
same snapshot
same config
same code/contracts
=
same deterministic output
```

Record:

```text
dataset version/hash
snapshot id/hash
feature version
signal version
scenario version
decision-policy version
tool-registry version
implementation SHA
```

LLM explanation does not require byte identity.

It must preserve:

```text
same evidence IDs
same frozen recommendation
same allowed reason-code family
same output schema
no unsupported claims
```

Goal:

```text
semantic reproducibility
```

---

## 8. Exact-SHA Rule

CI evidence is valid only for the exact implementation SHA under review.

Older successful CI does not prove a newer implementation.

Round Report must cite the implementation SHA and observed CI run.

---

## 9. Development Round Report

Required for every implementation checkpoint.

Sections:

```text
1. Report Metadata
2. Starting Baseline
3. Round Objective
4. Authorized Scope
5. Explicit Non-Goals
6. Architecture / Contract Changes
7. Implementation Summary
8. Changed Files
9. Development Context Manifest
10. Runtime Data / Evidence Inputs
11. Semantic Trust Decisions
12. Harness Results
13. AI Evaluation Results
14. HGT Isolation Verification
15. Temporal Leakage Verification
16. Operational Mutation Verification
17. Determinism / Replay Result
18. CI Evidence
19. Git / GitHub State
20. Known Limitations
21. Newly Discovered Debt
22. Findings by Severity
23. Reviewer Questions
24. Current Status
25. Next Authorized Action
```

---

## 10. Fact Labels

Round Reports use:

```text
OBSERVED
DERIVED
EVALUATED
```

Do not present a derived interpretation as an observed command/test result.

---

## 11. Machine-Readable Harness Summary

Recommended shape:

```json
{
  "round_id": "W03-CXX",
  "implementation_sha": "...",
  "dataset_hash": "...",
  "snapshot_hash": "...",
  "engineering": {
    "pytest": "PASS",
    "ruff": "PASS",
    "mypy": "PASS"
  },
  "semantic": {
    "evidence_provenance": "PASS",
    "temporal_leakage": "PASS",
    "hgt_leakage": "PASS",
    "uncertainty_preservation": "PASS"
  },
  "loop": {
    "determinism": "PASS",
    "replay": "PASS",
    "operational_mutation": "NONE"
  }
}
```

---

## 12. Review Boundary

Codex Round Report may end only at:

```text
IMPLEMENTATION: COMPLETE
HARNESS: PASS
CI: PASS
CHATGPT REVIEW: PENDING
HUMAN ACCEPTANCE: PENDING
CHECKPOINT CLOSED: NO
STATUS: REVIEW_READY
```

Codex must not claim:

```text
CHATGPT REVIEW: PASS
HUMAN ACCEPTANCE: ACCEPTED
CHECKPOINT CLOSED: YES
```

---

## 13. Report Git Workflow

```text
IMPLEMENTATION COMMIT
↓
PUSH
↓
EXACT-SHA CI
↓
HARNESS EVIDENCE
↓
ROUND REPORT
↓
REPORT COMMIT
↓
GPT INDEPENDENT REVIEW
↓
HUMAN ACCEPTANCE
↓
CLOSEOUT COMMIT
```

The report must not be fabricated before exact implementation/CI evidence exists.

---

## 14. Checkpoint Evidence Bundle

Each checkpoint has:

```text
Implementation Artifact
+
Evidence Artifact
+
Governance Artifact
```

Where:

```text
Implementation Artifact
= implementation SHA

Evidence Artifact
= Round Report + Harness + exact-SHA CI

Governance Artifact
= GPT Review + Human Acceptance + closeout SHA
```

---

## 15. Status

```text
HARNESS ARCHITECTURE:
FROZEN

CAPABILITY PROOF MODEL:
FROZEN

POSITIVE GOLDEN PACK:
FROZEN AT FAMILY LEVEL

NEGATIVE PACK:
FROZEN AT FAMILY LEVEL

REPORT FORMAT:
FROZEN

EXACT TEST IMPLEMENTATION:
DEFERRED TO CHECKPOINTS

IMPLEMENTATION:
NOT AUTHORIZED
```

---

## 16. Repository Projection Gate

Before the first W03 Codex implementation checkpoint, verify:

```text
AGENTS.md phase == Week 3
AGENTS.md references current W03 control docs
LOOP.md is router-only
skills/ contains no unauthorized executable capability
CURRENT_STATE reflects actual G0 publication state
```

Failure:

```text
C01 IMPLEMENTATION ENTRY DENIED
```

This is a governance/preflight gate, not a runtime AI gate.
