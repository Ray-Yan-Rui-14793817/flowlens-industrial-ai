# FlowLens Industrial AI — W03-C08 Grounding and Fallback Policy

## Acceptance gate

A provider result is accepted only when the exact schema and section order pass,
all evidence/reason references are allowed, recommendation meaning is unchanged,
no unknown identifier is referenced, no causal/root-cause upgrade occurs, no
probability/confidence/guarantee is claimed, every numeric/date/time claim is
traceable to canonical context, unknowns remain unresolved, simulation is not
presented as operational efficacy, limitations are preserved, and packet bytes
are unchanged.

HGT, evaluation output, operational mutation, tool requests, file/database/RAG
requests, quality release, and order-specific procurement allocation are always
rejected.

## Retry and fallback

```text
valid schema + valid grounding
  -> BOUNDED_LLM

schema invalid only
  -> exactly one schema-repair call
  -> valid + grounded: BOUNDED_LLM + C08_SCHEMA_REPAIR_USED
  -> otherwise: DEGRADED_TEMPLATE

provider timeout/refusal/exception
  -> DEGRADED_TEMPLATE

grounding/unsupported/injection failure
  -> no repair
  -> DEGRADED_TEMPLATE

model disabled or API key absent
  -> DETERMINISTIC_TEMPLATE
```

Provider calls never exceed two. SDK retries are zero. Fallback output is a
byte-deterministic, packet-only rendering of the same five final sections and
never changes the recommendation.
