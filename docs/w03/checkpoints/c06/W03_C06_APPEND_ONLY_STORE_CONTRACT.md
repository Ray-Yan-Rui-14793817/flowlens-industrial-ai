# FlowLens Industrial AI — W03-C06 Append-Only Store Contract

```text
store_version = w03-c06-store-v1
purpose = non-operational Human review audit journal
append_only = API-ENFORCED
```

## Root and layout

The caller supplies a trusted absolute pre-existing directory. C06 rejects a
relative path, missing path or non-directory and never derives the root from
CWD, environment discovery, packet text, actor, comment or priority.

```text
<root>/
  .locks/
    <packet_id>.lock/
  <packet_id>/
    <decision_event_id>.json
```

Only validated C01 artifact IDs become path components. Each event file is
exactly `canonical_json_bytes(event) + b"\n"`: UTF-8, canonical C01 JSON, one
terminal LF, no BOM, envelope, header, pretty printing or extra bytes.

## Locking and append

The per-packet lock directory is acquired by atomic directory creation. An
existing lock fails closed with `C06_STORE_BUSY`; there is no wait, retry,
stale-age heuristic, host-clock inspection or automatic stale-lock deletion.

While holding the lock, C06 validates the complete existing chain, derives the
unique tail, validates the proposed next event, and either confirms an exact
retry or stages/fsyncs/renames one new final event. Existing final event files
are never rewritten. Best-effort failure cleanup may remove only the operation's
own pending file; any stale pending artifact makes the journal dirty and fails
closed.

Exact same event ID and bytes is idempotent success with no mutation. Same ID
and different bytes is `C06_EVENT_ID_COLLISION`.

## Narrow readback and integrity

Only C06-specific `HumanDecisionEvent` readback is authorized. It reconstructs
the event, C01 provenance/version values, enum and aware datetime, then requires
byte equality with canonical reconstruction plus one LF.

Unknown/missing fields, float, naive or noncanonical datetime, invalid enum or
provenance, wrong schema/ID/filename, noncanonical JSON, invalid UTF-8, BOM,
missing/multiple LF, unexpected files, missing parents, multiple roots, forks,
cycles, cross-run/cross-packet links and time regression all fail closed without
repair, normalization, reordering, deduplication or historical mutation.

## Honest limitations

C06 is API-append-only and chain-validating, not hardware/WORM storage. Root
protection, retention, encryption and key management are deployment concerns.
External deletion of a terminal event is not provable without an external
anchor. A crash can leave a stale lock/pending artifact requiring explicit
operator recovery. C06 provides neither distributed consensus nor cross-machine
writer coordination.
