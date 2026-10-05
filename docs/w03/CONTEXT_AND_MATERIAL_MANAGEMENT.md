# FlowLens Industrial AI — W03 Context & Material Management Contract

**Task:** W03-G0-GPT-04\
**Status:** FROZEN FOR G0 HUMAN REVIEW\
**Baseline:** `main@9d18ddde9fe933952a2661ee1419f13c8577605d`

---

## 1. Purpose

This contract controls what information is available to:

1. developers and reviewers; and
2. the Runtime Decision Loop.

The central rule is:

```text
DEVELOPMENT CONTEXT
!=
RUNTIME DECISION CONTEXT
```

---

## 2. Context Domains

### DevelopmentContextManifest

Authorized consumers:

```text
GPT architecture/review
Codex implementation
Human technical review
```

May contain:

```text
architecture
contracts
task instructions
test expectations
scenario documentation
Round Reports
CI evidence
historical implementation evidence
review comments
```

Development context is never automatically runtime-safe.

---

### DecisionContextManifest

Authorized consumers:

```text
deterministic Runtime Decision Loop
bounded LLM explainer
```

May contain only:

```text
authorized operational facts
authorized deterministic derivations
Evidence
Signals
Semantic Trust flags
explicit uncertainties
provenance
as_of_time
snapshot identity
```

Forbidden:

```text
HGT
scenario labels
true root cause
expected evaluation output
developer review comments
Codex prompt text
test oracle answers
historical chat
```

---

## 3. Context Hierarchy

### L0 — Constitution

Always authoritative:

```text
AI Loop Constitution
HGT policy
No Operational Mutation
Human Authority
```

### L1 — Sprint

```text
W3 scope
architecture
semantic trust
prompt/tool policy
harness policy
```

### L2 — Task

```text
task ID
baseline SHA
allowed files
input/output contract
non-goals
acceptance tests
stop conditions
```

### L3 — Runtime Evidence

```text
StateSnapshot
EvidenceBundle
SignalBundle
DecisionContext
```

### L4 — Historical

```text
W1/W2 closeouts
old Round Reports
historical chat
```

L4 is read only on demand.

---

## 4. Context Source Priority

For development decisions:

```text
1. Current Task Contract
2. W03 AI Loop Constitution
3. W03 Sprint Spec
4. W03 Semantic Trust Contract
5. W03 Context / Material Contract
6. W03 Prompt / Tool Contract
7. W03 State Machine / Failure Policy
8. W03 Harness / Reporting Spec
9. Frozen W1/W2 contracts
10. CURRENT_STATE
11. Most Recent Closed Round Report
12. Historical reports
13. Chat history
```

Repository control documents outrank conversational memory.

---

## 5. Context Capsule

Every Codex task receives a bounded capsule:

```text
TASK ID
CURRENT BASELINE
CURRENT BRANCH
AUTHORIZED CHECKPOINT

AUTHORITATIVE DOCS
FROZEN INVARIANTS

INPUT CONTRACT
OUTPUT CONTRACT

AUTHORIZED FILES
FORBIDDEN FILES

NON-GOALS

SEMANTIC TRUST RULES
TOOL PERMISSIONS

HARNESS REQUIREMENTS
ACCEPTANCE TESTS

AUTO-REPAIR PERMISSIONS
GIT RULES
STOP CONDITIONS

EXPECTED FINAL STATUS
```

Do not provide full W1/W2 chat history by default.

---

## 6. Context Lock

Before any implementation write, record:

```text
checkpoint_id

baseline_branch
baseline_sha

authoritative_doc_versions
authoritative_doc_hashes

dataset_version
dataset_hash

scenario_version
scenario_config

model_config

prompt_version
prompt_hash

tool_registry_version

allowed_sources
forbidden_sources

authorized_files
forbidden_files

expected_context_delta
```

No Context Lock:

```text
NO IMPLEMENTATION
```

---

## 7. Context Delta

At the end of an implementation round record:

```text
changed_contracts
changed_sources
changed_assumptions
changed_tool_permissions
changed_context_materials
changed_runtime_inputs
```

Rule:

```text
actual_delta ⊆ authorized_delta
```

Otherwise:

```text
ROUND NOT CLOSEABLE
```

---

## 8. Material Classes

### AUTHORITATIVE

Version-controlled control material.

Examples:

```text
contracts
architecture
ADR
sprint specs
decision rules
schema definitions
```

---

### RUNTIME_SAFE

Material eligible for Runtime Decision Context after validation.

Examples:

```text
operational facts
authorized derived metrics
StateSnapshot
Evidence
DecisionContext
public runtime-safe manifest
```

Runtime-safe does not mean automatically relevant; it must still satisfy decision-time and trust rules.

---

### PROTECTED

Never available to normal runtime reasoning.

Examples:

```text
HGT
scenario answer
true root cause
hidden labels
evaluation-only annotations
```

---

### EPHEMERAL

Normally not version-controlled.

Examples:

```text
raw LLM outputs
debug logs
temporary reports
local DB
model cache
pytest cache
large eval traces
temporary artifacts
```

---

## 9. Material Registry Schema

Each registered material should support:

```text
material_id
name
type
source
version
hash
owner

runtime_allowed
evaluation_allowed
publication_allowed
training_allowed

authoritative
protected
synthetic
external

retention_policy
notes
```

---

## 10. Decision-Time Snapshot Policy

Every Decision Run must bind:

```text
order_id
as_of_time
dataset_version
dataset_hash
```

Snapshot construction must:

1. query only authorized operational facts;
2. exclude facts not yet available at `as_of_time`;
3. classify freshness;
4. attach provenance;
5. attach semantic trust;
6. freeze the resulting snapshot.

After freeze:

```text
StateSnapshot is immutable
```

Downstream runtime components operate on `snapshot_id` / `snapshot_hash`.

---

## 11. Freshness / Staleness Policy

Minimum states:

```text
FRESH
STALE
EXPIRED
UNKNOWN
NOT_APPLICABLE
```

The framework is frozen here.

Numeric thresholds are source-specific and must be authorized in C02.

A stale item may be retained as historical/associative context when allowed, but it cannot be silently represented as current state.

---

## 12. Context Reduction Policy

If Runtime Decision Context must be reduced, use deterministic priority:

```text
P0 — order identity / delivery commitment / as_of_time
P1 — direct facts tied to active risk path
P2 — explicit unknown/conflict evidence
P3 — deterministic derived facts and active signals
P4 — associative evidence relevant to active path
P5 — lower-value historical context
```

Never drop:

```text
evidence IDs referenced by a claim
trust labels
limitations
unknowns
as_of_time
snapshot identity
provenance needed for replay
```

Reduction must be:

```text
deterministic
versioned
auditable
replayable
```

---

## 13. Runtime Text Safety

Any future free text from:

```text
supplier notes
operator comments
quality comments
documents
RAG
external text
```

must be treated as:

```text
UNTRUSTED DATA
NOT INSTRUCTION
```

Such content cannot override system or contract instructions.

W3 v0 does not require external RAG.

---

## 14. Publication Boundary

Protected material may never be included in:

```text
public artifact
runtime DecisionPacket
LLM context
human-facing explanation
```

unless a future contract explicitly changes the classification.

---

## 15. Status

```text
DEV / RUNTIME CONTEXT SEPARATION:
FROZEN

CONTEXT CAPSULE:
FROZEN

CONTEXT LOCK / DELTA:
FROZEN

MATERIAL CLASSES:
FROZEN

STALENESS FRAMEWORK:
FROZEN

NUMERIC FRESHNESS THRESHOLDS:
DEFERRED TO C02

IMPLEMENTATION:
NOT AUTHORIZED
```

---

## 16. Repository Projection Context

The following are Development-Control materials, not Runtime Decision evidence:

```text
AGENTS.md
LOOP.md
skills/README.md
skills/SKILL_ADMISSION_POLICY.md
```

Classification:

```text
AGENTS.md:
AUTHORITATIVE ROUTER / DEVELOPMENT ONLY

LOOP.md:
AUTHORITATIVE ROUTER / DEVELOPMENT ONLY

skills/* governance:
AUTHORITATIVE PROCEDURAL POLICY / DEVELOPMENT ONLY
```

They must never be injected as operational evidence into `DecisionContext`.

A future Skill may read control documents for development procedure execution, but that does not make the documents runtime evidence.
