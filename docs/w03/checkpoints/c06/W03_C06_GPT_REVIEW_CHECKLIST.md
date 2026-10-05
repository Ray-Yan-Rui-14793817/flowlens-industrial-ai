# FlowLens Industrial AI — W03-C06 GPT Review Checklist

The later independent GPT review must verify at minimum:

1. The C01 `HumanDecisionEvent` schema and identity rules were not modified.
2. ACCEPT/REJECT/DEFER match the frozen semantics.
3. ACCEPT never becomes operational execution.
4. REJECT never chooses an alternate candidate.
5. DEFER and later correction are append-only events.
6. Reason fields are bounded to C05 recommendation reason codes.
7. Comment and priority are non-authoritative audit metadata.
8. Explicit `decided_at` has no ambient-clock dependency.
9. Same-run/same-packet chain rules hold.
10. Unique-tail, no-fork and no-cycle rules hold.
11. Event identity/canonical serialization match unchanged C01 rules.
12. The store is API-append-only and exact retry is idempotent.
13. Deserialization is narrow to `HumanDecisionEvent`.
14. Malformed/corrupt stores fail closed without normalization.
15. Filesystem access is limited to the trusted audit root.
16. No DB/HGT/network/model/scenario/subprocess/random/wall-clock capability exists.
17. No operational mutation exists.
18. C05 remains immutable and canonical.
19. C07/C08 were not started.
20. Complete regression evidence is intact.

Allowed outcomes are:

```text
PASS FOR HUMAN C06 ACCEPTANCE
REPAIR REQUIRED
BLOCKED
```

GPT review must not close C06.
