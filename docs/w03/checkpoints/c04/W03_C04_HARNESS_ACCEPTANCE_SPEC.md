# W03-C04 Harness Acceptance Specification

The C04 harness must enforce and evidence:

1. Exact four-family registry, fixed profiles and canonical set ordering.
2. Fail-closed rebuilding of supplied C03 SignalBundle and DiagnosisRecord.
3. Relevance metadata without causal claims; capacity retains
   `C04_QUEUE_DELAY_NOT_CAPACITY_PROOF`.
4. Neutral `NO_ACTION` success and baseline measurements.
5. Earlier-as-of closed-window rejection with zero adapter calls.
6. Dataset binding, stored/recomputed hash checks and hard baseline-mutation detection.
7. HGT-free import and execution, including construction traps and static source audit.
8. Canonical business compatibility with all accepted W2 scenario modes and unchanged legacy
   HGT behavior and public imports.
9. Baseline immutability and detached ORM objects.
10. Repeated and fresh-process deterministic replay.
11. Independent semantic business diff, ownership-field exclusion and new Capacity-row inclusion.
12. Exact raw measurement names, units and deterministic values.
13. Expected scenario preconditions degrade to `UNAVAILABLE`.
14. Unexpected scenario errors are visible as sanitized `FAILED` results.
15. No database, filesystem, network, model, subprocess, random, wall-clock or protected-HGT
    capability.
16. Fresh `import flowlens.decision` remains free of SQLAlchemy, DB, scenario and HGT imports.
17. All accepted C01/C02/C03 and W2 scenario regressions remain green.

No existing frozen assertion may be weakened, deleted, rewritten or skipped.
