# FlowLens Industrial AI — W03-C06 Human Decision Contract

```text
schema_version = human-decision-event.v1
policy_version = w03-c06-human-v1
producer = flowlens.decision.c06_human
producer_version = w03-c06-human-v1
```

## Frozen schema and vocabulary

C06 uses the unchanged C01 `HumanDecisionEvent` with exactly these fields:

```text
decision_event_id
schema_version
run_id
packet_id
decision
actor_id
decided_at
accepted_reason_codes
rejected_reason_codes
comment
investigation_priority
previous_event_id
provenance
```

The only decisions are `ACCEPT`, `REJECT`, and `DEFER`. Existing events are
never edited or deleted by C06. The unique chain tail is the current Human
review outcome; every earlier event remains immutable history.

## Packet binding

C06 accepts only `decision-packet.v1` produced by
`flowlens.decision.c05_packet@w03-c05-packet-v1`. The packet's exact C05
provenance and nested C01 bindings must be canonical. Current valid dispositions
are `NO_ACTION`, `NO_RECOMMENDATION`, `INVESTIGATION_ONLY`, and
`DEFER_TO_HUMAN`. `CANDIDATE_RECOMMENDED` is rejected as noncanonical C05 v1.

## Human annotations

Both reason-code tuples may be empty. Each must be a sorted unique subset of
`packet.recommendation.reason_codes`, and their intersection must be empty.
Omitted codes are not explicitly adjudicated; they are not implicitly rejected.

`actor_id` is caller-supplied, opaque, nonempty and stripped. C06 supplies no
authentication, authorization, SSO, RBAC or identity directory.

`decided_at` is caller-supplied and timezone-aware. It must not precede
`packet.run.as_of_time`; a chained event must not precede its parent. C06 does
not read or compare the host wall clock.

`comment` is untrusted inert audit text. Shell, SQL, prompt, JSON-tool, HGT-like
or operational language remains text and cannot affect behavior.
`investigation_priority` is an opaque audit label with no ranking, SLA, routing,
candidate-preference, execution or permission meaning.

## Exact provenance

```text
producer = flowlens.decision.c06_human
producer_version = w03-c06-human-v1
source_refs = ()
implementation_sha = None
contract_versions =
  w03-c01 / v1
  w03-c05-packet / v1
  w03-c06-human / v1
  w03-c06-workflow / v1
```

First-event `input_artifact_ids` is `(packet.packet_id,)`. Later-event inputs
are the sorted tuple of packet ID and previous event ID.
