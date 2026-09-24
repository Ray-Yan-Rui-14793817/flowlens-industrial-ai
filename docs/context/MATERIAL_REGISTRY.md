# FlowLens — W03 Material Registry

**Status:** G0 initial registry\
**Purpose:** classify materials before runtime or evaluation use.

Legend:

```text
A = AUTHORITATIVE
R = RUNTIME_SAFE candidate
P = PROTECTED
E = EPHEMERAL
```

| Material | Class | Runtime | Evaluation | Publication | Training | Notes |
|---|---|---:|---:|---:|---:|---|
| Project Charter | A | No | Yes | Yes | No | development authority |
| Scope / Architecture docs | A | No | Yes | Yes | No | development authority |
| W2 Data Contract | A | No | Yes | Yes | No | runtime builders implement it; model does not ingest doc by default |
| W03 Constitution | A | No | Yes | Yes | No | control plane |
| W03 Semantic Trust Contract | A | No | Yes | Yes | No | control plane |
| W03 Context/Material Contract | A | No | Yes | Yes | No | control plane |
| W03 Prompt/Tool Contract | A | No | Yes | Yes | No | control plane |
| W03 State Machine / Failure Policy | A | No | Yes | Yes | No | control plane |
| W03 Harness Spec | A | No | Yes | Yes | No | control plane |
| W03 Sprint Spec | A | No | Yes | Yes | No | control plane |
| Operational DB facts | R | Yes, through authorized builder | Yes | No by default | No | decision-time filtered |
| StateSnapshot | R | Yes | Yes | bounded | No | immutable per run |
| EvidenceBundle | R | Yes | Yes | bounded | No | contains trust/provenance |
| SignalBundle | R | Yes | Yes | bounded | No | deterministic |
| DiagnosisRecord | R | Yes | Yes | bounded | No | no HGT |
| SimulationBundle | R | Yes | Yes | bounded | No | counterfactual only |
| RecommendationRecord | R | Yes | Yes | bounded | No | frozen before LLM |
| DecisionPacket | R | Yes | Yes | bounded | No | primary human-review packet |
| Public manifest | R | Yes if relevant | Yes | Yes | No | must remain HGT-free |
| HGT | P | No | Yes | No | No in W3 | evaluation only |
| Scenario label / true cause | P | No | Yes | No | No in W3 | never runtime input |
| Evaluation-only annotations | P | No | Yes | No | No in W3 | protected plane |
| Raw LLM output | E | No direct reuse | Yes for debugging | No by default | No | validate before any surfaced use |
| Debug logs | E | No | Yes | No by default | No | may contain operational details |
| Local DB | E | No | Test only | No | No | not an authoritative material |
| pytest/cache/model cache | E | No | No | No | No | not version-controlled |
| Development Round Report | A | No | Yes | Yes | No | development evidence, not runtime evidence |
| Chat history | E/Historical | No | Development only | No | No | lowest authority |

---

## Registry Rules

1. `runtime_allowed=true` does not bypass `as_of_time`, trust, or freshness checks.
2. Protected material must never be copied into runtime-safe artifacts.
3. Development artifacts are not runtime evidence.
4. New material requires explicit classification before use.
5. External material is not required in W3 v0.
6. HGT is never training material in W3.
