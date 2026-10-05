# FlowLens Industrial AI — W03-C06 Authorization Contract

```text
task = W03-C06-I/H/R
checkpoint = W03-C06 — Human Decision Workflow
contract_version = W03-C06-A-v1
human_implementation_authorization = APPROVED
product_mode = OFFLINE / SHADOW / HUMAN-IN-THE-LOOP
operational_mutation = PROHIBITED
runtime_hgt = PROHIBITED
c07 = NOT AUTHORIZED
c08 = NOT AUTHORIZED
```

## Authorized result

C06 may consume exactly one immutable canonical C05 `DecisionPacket`, validate
the frozen packet boundary, build one deterministic C01 `HumanDecisionEvent`,
and append it to a dedicated Human-review audit journal. C06 records Human
authority; it does not execute a recommendation or change the packet.

Policy versions are frozen as:

```text
human_decision_policy_version = w03-c06-human-v1
human_decision_store_version = w03-c06-store-v1
human_decision_workflow_version = w03-c06-workflow-v1
producer = flowlens.decision.c06_human
producer_version = w03-c06-human-v1
```

The C01 `HumanDecisionEvent` schema, identity algorithm, canonical JSON and
`HumanDecisionType` values remain unchanged. C05 recommendation and packet
semantics remain unchanged.

## Decision boundary

```text
ACCEPT = accept the exact frozen packet disposition as the current review outcome
REJECT = do not accept the exact frozen packet disposition
DEFER = deliberately defer the Human review outcome
```

None of these values executes a candidate, chooses an alternative, reranks,
reruns simulation, rewrites the packet, or mutates operational state. A later
decision is a new event referencing the current unique tail.

## Runtime capability boundary

Allowed runtime capability is pure validation/event construction plus bounded
read and append-only write access beneath one explicitly supplied trusted
absolute pre-existing journal root. C06 has no PostgreSQL, SQLAlchemy engine or
session, operational database write, HGT, scenario, network, model, LLM,
subprocess, random, ambient-clock, C07, C08, or operational-action capability.

## Lifecycle

```text
Context Lock
→ implementation + complete H1-H22 harness
→ implementation commit
→ I / FULL_EXACT_SHA
→ Development Round Report + CURRENT_STATE
→ report commit
→ P / PUBLICATION_EXACT_SHA
→ final synchronization
→ REVIEW_READY
→ STOP
```

GPT C06 review and Human C06 acceptance remain pending. C06 is not closed and
C07 is not authorized.
