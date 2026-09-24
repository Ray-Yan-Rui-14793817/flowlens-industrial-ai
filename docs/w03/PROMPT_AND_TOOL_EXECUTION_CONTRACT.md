# FlowLens Industrial AI — W03 Prompt & Tool Execution Contract

**Task:** W03-G0-GPT-05\
**Status:** FROZEN FOR G0 HUMAN REVIEW\
**Baseline:** `main@9d18ddde9fe933952a2661ee1419f13c8577605d`

---

## 1. Purpose

This contract separates:

```text
what a model may say
```

from:

```text
what a system capability may do
```

It governs both Development Prompts and future Runtime LLM prompts.

---

## 2. Prompt Classes

### DEVELOPMENT_PROMPT

Used for GPT/Codex development work.

May contain:

```text
architecture
contracts
test expectations
repository instructions
implementation instructions
```

It must follow the Context Capsule and current task authorization.

---

### RUNTIME_PROMPT

Used only by the future bounded LLM explanation layer.

It may receive only validated Runtime-Safe material.

Development-only material is forbidden.

---

## 3. Runtime LLM Role

W3 v0 freezes:

```text
LLM ROLE:
EXPLAINER ONLY
```

The model MAY:

```text
summarize DecisionPacket
explain evidence-backed Signals
explain the frozen Recommendation
compare authorized simulation outcomes
surface uncertainties / limitations
reference evidence IDs
```

The model MAY NOT:

```text
query the database
access HGT
invent evidence
invent root cause
change semantic trust
create intervention candidates
change scores
change recommendation
execute business actions
silently resolve UNKNOWN
```

Constitutional rule:

```text
MODEL EXPLAINS
SYSTEM DECIDES
```

---

## 4. Runtime Prompt Contract

Every runtime prompt version must define:

```text
role
authorized_inputs
forbidden_inputs
allowed_claims
forbidden_claims
output_schema
abstention_behavior
fallback_behavior
prompt_version
prompt_template_hash
context_schema_version
```

When introduced in C08, record additionally:

```text
provider
model
model version
temperature
schema version
retrieval scope
tool permissions
```

---

## 5. Prompt Instruction Hierarchy

Runtime instruction precedence:

```text
1. System safety / Constitution
2. Runtime Prompt Contract
3. Output Schema
4. Validated DecisionContext / DecisionPacket
5. Untrusted operational free text
```

Data content can never become higher-priority instruction.

---

## 6. Prompt Injection Boundary

All free text from operational or external sources is data.

Required conceptual wrapping:

```text
SYSTEM / CONTRACT INSTRUCTIONS
------------------------------
UNTRUSTED OPERATIONAL CONTENT
------------------------------
```

Injection attempts must not:

```text
change tool permissions
change recommendation
reveal protected context
override output schema
change trust classifications
```

C08 must add adversarial injection tests before LLM capability is trusted.

---

## 7. W3 v0 LLM Tool Policy

Freeze:

```text
LLM TOOL ACCESS = NONE
LLM DATABASE ACCESS = NONE
LLM FILESYSTEM ACCESS = NONE
LLM NETWORK ACCESS = NONE
LLM HGT ACCESS = NONE
LLM OPERATIONAL WRITE = NONE
```

This is intentional.

Runtime capability orchestration belongs to deterministic application code.

---

## 8. Runtime Capability Classes

```text
PURE
READ_ONLY
SIMULATION_ONLY
EVALUATION_ONLY
MUTATING
```

### PURE

No external state read/write.

Allowed only if registered.

### READ_ONLY

Reads bounded authorized runtime data.

In W3, live operational reads belong primarily to Snapshot Builder before snapshot freeze.

### SIMULATION_ONLY

May transform isolated counterfactual state.

Must never mutate baseline operational facts.

### EVALUATION_ONLY

May read protected evaluation material after recommendation freeze.

Cannot feed protected material back into runtime recommendation.

### MUTATING

Writes operational business state.

```text
FORBIDDEN IN W3 V0
```

---

## 9. Capability Registry Contract

Every callable capability must declare:

```text
tool_id
version

allowed_caller
allowed_loop_stage

input_schema
output_schema

side_effect_class
data_classification

snapshot_required

hgt_access
operational_write

deterministic
idempotent

timeout
retry_policy
max_calls

failure_behavior
audit_required
```

Rule:

```text
not explicitly registered
=
not callable
```

---

## 10. Caller Policy

Allowed callers may include:

```text
snapshot_builder
decision_orchestrator
evaluation_orchestrator
```

W3 v0 LLM is not a tool caller.

---

## 11. Snapshot Binding

After snapshot freeze, downstream runtime capability inputs must bind to:

```text
decision_run_id
snapshot_id
snapshot_hash
```

A tool must not silently fetch a newer operational world for the same run.

---

## 12. Development Tool Plane

Codex Development Plane may use, within task authorization:

```text
repository filesystem
tests
test PostgreSQL
Docker
Git
GitHub
CI
```

Development permissions do not imply runtime permissions.

---

## 13. Codex Development Tool Rules

Default restrictions:

```text
NO MAIN WRITE

NO FORCE PUSH

NO W2 HISTORY REWRITE

NO FROZEN CONTRACT EDIT
unless task explicitly authorizes it

NO SCHEMA / MIGRATION CHANGE
unless separately authorized

NO NEW DEPENDENCY
unless current task contract authorizes it

NO NETWORK SOURCE
unless current task contract authorizes it

NO SECRET READ
unless explicitly required and authorized

NO W03 CHECKPOINT AUTO-ADVANCE
```

Ordinary implementation bugs may be auto-repaired within scope.

Contract or semantic conflicts must stop.

---

## 14. Failure-Path Requirement

No new capability is allowed without:

```text
permission test
success-path test
failure-path test
audit behavior
```

Examples:

```text
new feature
→ temporal/leakage test

new risk score
→ direction/replay test

new tool
→ permission/failure-path test

new LLM explanation
→ schema/grounding/unsupported-claim/injection test
```

---

## 15. Tool Audit Event

A future tool audit record should include:

```text
decision_run_id
tool_id
tool_version
caller
stage

input_hash
output_hash

started_at
completed_at

status
failure_code

side_effect_class
snapshot_id

hgt_accessed
operational_write_attempted
```

---

## 16. Status

```text
RUNTIME LLM ROLE:
FROZEN — EXPLAINER ONLY

RUNTIME LLM TOOLS:
FROZEN — NONE

TOOL GOVERNANCE:
FROZEN — DENY BY DEFAULT

MUTATING TOOLS:
FORBIDDEN IN W3 V0

DEVELOPMENT TOOL PLANE:
SEPARATE FROM RUNTIME TOOL PLANE

ACTUAL C08 PROMPT TEXT:
DEFERRED TO C08 AUTHORIZATION

IMPLEMENTATION:
NOT AUTHORIZED
```

---

## 17. Repository Agent Instruction Surface

`AGENTS.md` is the persistent repository execution router.

Development prompts must not intentionally conflict with it.

If a task requires a contract-authorized exception, the exception must appear explicitly in the current Task Contract rather than relying on informal prompt wording.

`LOOP.md` is a routing/index surface only.

`skills/` content is procedural and cannot enlarge tool permissions beyond the current Task Contract.

---

## 18. Skill/Tool Boundary

A project Skill is not automatically a runtime Tool.

```text
Skill
= reusable development procedure

Runtime Tool
= registered runtime capability
```

They have separate permission models.

No Skill may create, register, or enable a Runtime Tool without an explicitly authorized contract change.
