# FlowLens Industrial AI — W03-C08 Context and Output Contract

## ExplanationContextV1

`w03-c08-context-v1` is a pure deterministic projection of one canonical C05
`DecisionPacket`. It contains exactly:

```text
run_id, packet_id, order_id, as_of_time
recommendation(disposition, selected candidate identity/family/registry key,
               candidate_order, reason_codes)
diagnosis(problem_code, claims with claim type/evidence/limitations)
signals(signal_type, state, evidence/reasons/limitations)
simulations(candidate_id, family, status, measurements, limitations)
evidence(source identity/field/value/times/relationship/trust/freshness/limitations)
uncertainties(status, code, message, evidence_ids)
limitations(code, message)
allowed_evidence_ids
allowed_reason_codes
```

The projection performs no database, filesystem, network, time, random, C07,
evaluation, or HGT access. All collections use deterministic order.

`allowed_evidence_ids` is the sorted union of evidence referenced by the frozen
recommendation, diagnosis, non-INACTIVE signals, relevant candidate support,
and packet/upstream uncertainties. Every ID must exist in the packet evidence
bundle. `allowed_reason_codes` is the sorted union of reason codes present on
the frozen recommendation, diagnosis, non-INACTIVE signals, and relevant
candidates. Runtime strings remain data, never instructions.

## Provider output

`w03-c08-output-v1` contains exactly four model sections in this order:

```text
recommendation_summary
evidence_and_diagnosis
simulation_context
uncertainties_and_limitations
```

Each section has exactly `section_key`, `text`, `evidence_ids`, and
`reason_codes`. Text is stripped, non-empty English text with at most 800
characters. Total model-generated text is at most 2400 characters. References
must be sorted, unique, and subsets of the context allowlists. No extra field,
limitation code, provider metadata, model metadata, or arbitrary confidence is
accepted.

The system appends the fifth final section, `human_review_boundary`, with this
exact text:

> Human review is required. This explanation does not change the frozen recommendation and grants no authority to execute an operational action.

The C01 artifact schema and identity rules are unchanged.
