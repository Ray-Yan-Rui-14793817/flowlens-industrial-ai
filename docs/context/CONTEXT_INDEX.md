# FlowLens — Context Index

**Scope:** W03 development and runtime context governance\
**Status:** W03 CLOSED / VERIFIED / GITHUB SYNCHRONIZED; C10 CLOSED; PR #6 merge AUTHORIZED / PENDING PRE-MERGE FULL PROOF; post-W03 implementation NOT AUTHORIZED

---

## 1. Development Authority Order

1. Current Task Contract
2. `docs/w03/AI_LOOP_CONSTITUTION.md`
3. `docs/sprints/W03_ai_decision_loop.md`
4. `docs/w03/SEMANTIC_TRUST_CONTRACT.md`
5. `docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md`
6. `docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md`
7. `docs/w03/LOOP_EXECUTION_STATE_MACHINE.md`
8. `docs/w03/FAILURE_AND_DEGRADATION_POLICY.md`
9. `docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md`
10. Frozen W1/W2 project/data contracts
11. `docs/CURRENT_STATE.md`
12. Most recent closed W03 Round Report
13. Historical reports
14. Chat history

---

## 2. Core Frozen W1/W2 Sources

Expected authoritative sources include:

```text
docs/00_project_charter.md
docs/01_scope.md
docs/02_architecture.md
docs/03_data_contracts.md
docs/sprints/W02_industrial_data_foundation.md
AGENTS.md
docs/CURRENT_STATE.md
```

These remain upstream constraints unless a separately authorized decision changes them.

---

## 3. W03 Control Documents

```text
docs/w03/AI_LOOP_CONSTITUTION.md
docs/w03/SEMANTIC_TRUST_CONTRACT.md
docs/w03/CONTEXT_AND_MATERIAL_MANAGEMENT.md
docs/w03/PROMPT_AND_TOOL_EXECUTION_CONTRACT.md
docs/w03/LOOP_EXECUTION_STATE_MACHINE.md
docs/w03/FAILURE_AND_DEGRADATION_POLICY.md
docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md
docs/sprints/W03_ai_decision_loop.md
docs/context/CONTEXT_INDEX.md
docs/context/MATERIAL_REGISTRY.md
```

---

## 4. Runtime Context Rule

Runtime Decision Context must not load this Context Index as model evidence.

This index is a development/control-plane artifact.

Runtime input is built only through authorized runtime builders.

---

## 5. Historical Context Policy

Closed Round Reports are the preferred compressed history.

Do not load all historical chats by default.

Recommended checkpoint context:

```text
Constitution
Sprint Spec
Current State
Most Recent Closed Round Report
Current Task Contract
```

---

## 6. Current Baseline

```text
main:
9d18ddde9fe933952a2661ee1419f13c8577605d

Week 2:
CLOSED / VERIFIED / MERGED

Week 3 implementation / evidence work:
COMPLETE

C01-C09:
CLOSED / VERIFIED / GITHUB SYNCHRONIZED

GPT C10 Review R1:
PASS FOR HUMAN W03-C10 BUSINESS ACCEPTANCE REVIEW

Human C10 acceptance:
ACCEPTED

W03 final closeout:
EFFECTIVE — Run #84 / 37254705531 / PASS and final synchronization

W03:
CLOSED / VERIFIED / GITHUB SYNCHRONIZED

C10:
CLOSED

GPT merge review:
PASS FOR HUMAN W03 PR #6 MERGE AUTHORIZATION

Human merge authorization:
APPROVED — W03 PR #6 MERGE AUTHORIZATION: APPROVED

PR #6 merge:
AUTHORIZED / PENDING PRE-MERGE FULL PROOF

Feature branch:
RETAINED

Post-W03 implementation:
NOT AUTHORIZED

NEXT:
PR #6 MERGE COMMIT + POST-MERGE MAIN VERIFICATION
```
