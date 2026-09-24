# FlowLens W03 — Skill Admission Policy

**Status:** G0 governance policy\
**Scope:** future project-local reusable Skill procedures

---

## 1. Admission Preconditions

A project Skill may be proposed only when at least one of the following is true:

1. the same bounded procedure has been executed successfully in at least two reviewed checkpoints; or
2. a repetitive safety-critical procedure materially benefits from standardized execution; or
3. the Product Owner explicitly authorizes earlier packaging.

---

## 2. Every Skill Must Declare

```text
skill purpose
trigger conditions
authoritative docs
inputs
outputs
allowed tools
forbidden tools
side effects
stop conditions
failure behavior
tests
version
```

---

## 3. Skills Are Procedural, Not Semantic Authorities

A Skill must reference authoritative contracts.

It must not duplicate or redefine:

```text
AI Loop Constitution
Semantic Trust Contract
Prompt / Tool permissions
State Machine
Failure Policy
Sprint authorization
```

---

## 4. Hard Prohibitions

No project Skill may:

```text
weaken HGT isolation
admit future evidence
write operational truth
expand runtime tool permissions
change frozen W1/W2 contracts
authorize itself
approve its own review
close a checkpoint
auto-advance to the next checkpoint
```

---

## 5. Skill Change Control

A Skill change that affects behavior covered by an authoritative contract must be treated as:

```text
CONTRACT-AFFECTING CHANGE
```

and requires the corresponding GPT/Human review.

---

## 6. Current Decision

```text
G0:
POLICY ONLY

C01:
NO SKILL REQUIRED

C02:
NO SKILL REQUIRED BY DEFAULT

POST-C02:
REVIEW FOR STABLE REUSABLE PROCEDURES
```
