# FlowLens Industrial AI — W03-C05 DecisionPacket Contract

```text
schema_version = decision-packet.v1
packet_policy_version = w03-c05-packet-v1
producer = flowlens.decision.c05_packet
producer_version = w03-c05-packet-v1
```

C05 assembles exactly one frozen C01 `DecisionPacket` containing the exact
supplied immutable artifacts:

```text
DecisionRun
StateSnapshot
EvidenceBundle
SignalBundle
DiagnosisRecord
CandidateSet
SimulationBundle
RecommendationRecord
```

Nested artifacts are not rewritten.

Packet uncertainties are the deterministic sorted unique union of
`EvidenceBundle.uncertainties`, `DiagnosisRecord.uncertainties` and
`RecommendationRecord.uncertainties`.

Packet limitations are the deterministic sorted unique union of Evidence,
Signal, Diagnosis-claim, Candidate, Simulation and Recommendation limitations.
Degradation is never hidden.

The packet is valid for human review for `NO_ACTION`, `NO_RECOMMENDATION`,
`INVESTIGATION_ONLY` and `DEFER_TO_HUMAN` when every hard contract/safety gate
passes. Invalid canonical input, temporal/HGT/trust violations or malformed
C04 simulation material produce no RecommendationRecord or DecisionPacket.

The packet contains no `HumanDecisionEvent`, `ExplanationRecord`, evaluation
artifact, HGT, mutable execution state or operational action.

Packet identity uses the existing C01 contract. Provenance references every
nested artifact ID and the C05 packet policy; no ambient capability or time is
part of identity.
