# FlowLens Industrial AI — W03-C07 Replay and Harness Specification

## Required replay matrix

The protected harness executes:

1. Supplier Degradation — effectful;
2. Quality Deterioration — effectful;
3. Capacity Surge — combined arrival and queue;
4. Capacity Surge — arrival-only;
5. Capacity Surge — queue-only;
6. Capacity Surge — fully neutral.

Existing-order cases use the lexicographically smallest affected Sales Order
that exists in the baseline and build paired baseline/scenario C01-C05 packets
for the same order and decision time. Scenario-created arrival cases build only
the scenario packet and retain the baseline dataset for identity proof. Neutral
replay uses one deterministic order present in both datasets.

HGT is withheld from all C01-C06 builders. The evaluator receives finalized
in-memory inputs only.

## H1-H38 enforcement matrix

```text
H1  forged scenario packet provenance
H2  forged C05 recommendation provenance
H3  CANDIDATE_RECOMMENDED forged disposition
H4  scenario packet dataset ID mismatch
H5  scenario packet dataset hash mismatch
H6  mutable-row stale scenario content hash
H7  baseline dataset ID mismatch
H8  baseline dataset stale content hash
H9  HGT scenario dataset mismatch
H10 HGT baseline dataset mismatch
H11 HGT hgt_hash / hgt_id integrity tamper
H12 HGT affected ID missing from scenario dataset
H13 effectful existing-order packet not HGT-affected
H14 wrong baseline packet order
H15 wrong baseline packet as_of_time
H16 fabricated baseline packet for scenario-created order
H17 missing baseline packet for required paired mode
H18 supplier expected-signal direction mismatch
H19 quality expected-signal direction mismatch
H20 Capacity queue truth without QUEUE_DELAY direction
H21 CAPACITY_PRESSURE promoted from UNKNOWN
H22 arrival-only Capacity incorrectly scored observable
H23 new non-expected active-family false positive
H24 neutral new-family false escalation
H25 neutral recommendation semantic drift
H26 metric envelope missing/extra/duplicate/wrong type/float
H27 reason-code vocabulary drift
H28 limitation removal
H29 same-process replay nondeterminism
H30 fresh-process replay nondeterminism
H31 runtime import graph reaches evaluation/HGT
H32 Evaluation artifact inserted into DecisionPacket
H33 C07 mutates runtime packet/artifact
H34 C07 mutates baseline/scenario business rows
H35 filesystem/network/model/subprocess/random/wall-clock capability
H36 DB/SQLAlchemy session/query/write capability
H37 protected-manifest read/write capability
H38 C08/LLM explanation capability
```

Every harness row defines detection, rejection/enforcement, and test evidence.
Tests do not weaken upstream assertions.

## Determinism and capability gates

Same canonical inputs must yield byte-identical artifacts and the same C01 ID
in-process, in fresh processes, under different hash seeds, and under different
input insertion order. Evaluator source has no DB, filesystem, manifest,
network, model, tool, subprocess, random, clock, scenario-execution or
operational-write capability.

Normal fresh imports of `flowlens`, `flowlens.decision`, `flowlens.api`, and
`flowlens.worker` must not load `flowlens.evaluation` or HGT modules.

## Engineering proof

Focused C07, accepted C01-C06/W2 regressions, the full non-integration suite,
Ruff, strict mypy, `git diff --check`, and Docker Compose configuration are
required locally. Guarded PostgreSQL integration runs only when the established
task-safe environment already exists. Remote exact-SHA CI is authoritative.
