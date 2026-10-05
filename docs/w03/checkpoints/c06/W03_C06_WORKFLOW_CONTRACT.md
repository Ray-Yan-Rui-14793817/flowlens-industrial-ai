# FlowLens Industrial AI — W03-C06 Workflow Contract

```text
workflow_version = w03-c06-workflow-v1
```

The bounded public surface is:

```python
build_human_decision_event(
    packet,
    *,
    decision,
    actor_id,
    decided_at,
    accepted_reason_codes=(),
    rejected_reason_codes=(),
    comment=None,
    investigation_priority=None,
    previous_event=None,
)

HumanDecisionJournal(root).load(packet)

HumanDecisionJournal(root).record(
    packet,
    *,
    decision,
    actor_id,
    decided_at,
    accepted_reason_codes=(),
    rejected_reason_codes=(),
    comment=None,
    investigation_priority=None,
)
```

`record()` acquires the packet lock, validates and loads the entire current
chain, supplies its unique tail to the deterministic builder, and persists at
most one new event in one bounded operation.

## Chain rules

```text
empty journal → previous_event_id = None
nonempty journal → previous_event_id = exact unique tail
same run and packet required
equal or later decided_at required
cross-chain, missing parent, multiple root, fork, cycle → reject
```

The workflow does not add mutable state to `DecisionRun` and does not claim a
complete runtime orchestrator. No CLI, endpoint, UI, LLM tool or operational
execution surface is introduced.
