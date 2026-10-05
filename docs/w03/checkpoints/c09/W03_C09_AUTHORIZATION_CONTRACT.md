# FlowLens Industrial AI — W03-C09 Authorization Contract

```text
checkpoint = W03-C09
task = W03-C09-I/H/R
contract_version = W03-C09-A-v1.1
base_contract = W03-C09-A-v1
clarification = W03-C09-CONTRACT-CLARIFICATION-01
entry_branch = feat/w03-ai-decision-loop
entry_sha = d71d5baeb0862f2706358c26e182554b3807e8f6
main_sha = 9d18ddde9fe933952a2661ee1419f13c8577605d
status = GPT_CONTRACT_FROZEN / HUMAN_AUTHORIZATION_REQUIRED
```

## Authorized outcome

C09 hardens the **development/CI proof plane** for the already accepted W03
Order Delivery Risk Decision Loop. It adds no new runtime reasoning capability.

The authorized outcome is one explicit, named, versioned, exact-SHA-bound CI
semantic regression gate that consolidates the accepted C01-C08 trust and safety
proofs while preserving all existing engineering gates.

```text
job id = w03-ai-loop-gate
job name = W03 AI loop gate
gate_version = w03-c09-ai-loop-gate-v1
manifest_schema = w03-c09-regression-manifest-v1.1
```

## Human gate

This GPT contract is complete but does **not** itself authorize repository
mutation. Implementation may begin only when the Product Owner separately
supplies this exact line in the active Codex request:

```text
W03-C09 HUMAN AUTHORIZATION: APPROVED
```

Because Clarification-01 was issued after the base Human Authorization, Codex
may resume repository mutation only when the active Product Owner request also
contains:

```text
W03-C09 CONTRACT CLARIFICATION-01: APPROVED
```

Once both gates are present, this amended contract authorizes only
`W03-C09-I/H/R`.

## Frozen proof scheduling

```text
P / PUBLICATION_EXACT_SHA
-> W03 AI loop gate SKIPPED

C / I / F / UNKNOWN / FULL_EXACT_SHA
-> W03 AI loop gate REQUIRED
```

The stable final `Verification gate` must require the C09 gate in every non-P
proof and require it to be skipped for P-only proof.

## Frozen semantic families

```text
F01 CORE_CONTRACTS
F02 TEMPORAL_SEMANTIC_TRUST
F03 SIGNAL_DIAGNOSIS_FAIL_CLOSED
F04 COUNTERFACTUAL_ISOLATION
F05 RECOMMENDATION_ABSTENTION
F06 HUMAN_AUTHORITY_AUDIT
F07 PROTECTED_EVALUATION_REPLAY
F08 LLM_GROUNDING_SCHEMA_INJECTION
F09 REAL_DATASET_BINDING_DIRECTION
F10 RUNTIME_CAPABILITY_ISOLATION
```

The exact **test-function selectors and frozen expanded case counts** are
frozen in `specs/c09_gate_manifest.json`. The manifest contains 38 selectors
covering exactly 85 expanded pytest cases. Missing, renamed, count-drifted,
skipped, xfailed, xpassed, errored, failed, or partially collected critical
targets are hard failures. Critical selectors may not be silently substituted
with weaker checks. Parameterized expansion is required, not rejected.

## Allowed implementation surface

Exactly the implementation-phase paths in `specs/authorized_paths.json` may
change. There is no authorized `src/**` path.

C09 may add:

```text
one CI semantic gate job
one development-plane gate runner
one C09 CI-contract test module
one frozen semantic manifest
C09 checkpoint governance files
bounded W03 Sprint status normalization
```

After exact implementation proof, only the C09 Development Round Report and
`docs/CURRENT_STATE.md` may be published in the separate report commit.

## Preserved proof infrastructure

C09 must not remove, rename, bypass, or weaken:

```text
Classify change
Quality gate
Docker Compose smoke
Publication proof
Verification gate
full integration pytest partition
full non-integration pytest partition
Ruff
strict mypy
uv lock --check
```

No GitHub trigger broadening is authorized.

## Frozen environment

Reuse only the current pinned development environment:

```text
ubuntu-latest
Python 3.12
uv 0.12.5
current pinned checkout/setup-python/setup-uv actions
pgvector/pgvector:0.8.6-pg17-bookworm
uv sync --frozen
existing Alembic head
```

No new dependency, GitHub Action, image, model, provider, secret, schema, or
migration is authorized. No live OpenAI call is permitted.

## Runtime and semantic non-goals

C09 must not change:

```text
C01 artifact schemas / identity
C02 snapshot / evidence / trust semantics
C03 signal / diagnosis semantics
C04 candidate / scenario / simulation semantics
C05 recommendation / DecisionPacket semantics
C06 HumanDecisionEvent / append-only workflow semantics
C07 evaluator / HGT / replay semantics
C08 prompt bytes/hash, context/output schemas, provider/model policy, fallback,
    grounding grammar, recommendation boundary
Week 2 data, scenario, HGT, schema, migration, persistence or hashing semantics
API / worker runtime behavior
Docker / Compose runtime semantics
operational data
```

C10 business acceptance is not part of C09.

## Stop conditions

Stop without adapting the contract if implementation requires any of:

```text
runtime source change
existing semantic expectation weakening
critical test deletion/skip/xfail/substitution
new dependency/action/image
classifier semantic change
branch-trigger broadening
schema/migration change
C08 prompt/provider/model change
runtime HGT access
live model call
operational write
C10 work
PR merge / draft-to-ready / auto-merge
```

## Expected implementation proof

The authorized delta includes `tests/test_c09_ci_gate.py`, so the implementation
commit is expected to classify `I / FULL_EXACT_SHA` and must show:

```text
Classify change: PASS
Quality gate: PASS
Docker Compose smoke: PASS
W03 AI loop gate: PASS
Publication proof: SKIPPED
Verification gate: PASS
```

Codex may then publish the report-only commit, expected as
`P / PUBLICATION_EXACT_SHA`, and must stop at `PENDING GPT REVIEW`.

C10 remains unauthorized.
