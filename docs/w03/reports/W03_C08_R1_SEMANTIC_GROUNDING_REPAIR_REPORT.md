# W03-C08 R1 Semantic Grounding Repair Report

## 1. Report Metadata

| Item | Verified value |
|---|---|
| Repair task | `W03-C08-REPAIR-01` |
| Repair authorization | `W03-C08-REPAIR-01 HUMAN REPAIR AUTHORIZATION: APPROVED` |
| Contract | `W03-C08-A-v1` / frozen |
| Branch | `feat/w03-ai-decision-loop` |
| Main baseline | `9d18ddde9fe933952a2661ee1419f13c8577605d` |
| Draft PR | [#6](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/pull/6) |
| Original C08 implementation SHA | `4e999faea8ec78539c800f67d7c901421848b3ab` |
| Original implementation CI | Run #73 / `36518365941` / PASS / `I / FULL_EXACT_SHA` |
| Original C08 publication SHA | `6e88bedc884f211f4826f4bb82e96d9c86411ec0` |
| Original publication CI | Run #74 / `36520572239` / PASS / `P / PUBLICATION_EXACT_SHA` |
| GPT C08 Independent Review R1 | `REPAIR REQUIRED` |
| Repair implementation SHA | `eefca6322ae3fdf3aa652edc77703189e5c35c95` |
| Repair implementation CI | Run #75 / `37185441717` / PASS / `I / FULL_EXACT_SHA` |
| Date | 2026-10-04 |

## 2. Authority and Boundary

The Product Owner authorized only the bounded semantic-grounding repair identified
by GPT C08 Independent Review R1. This repair did not reopen the original C08
implementation, C01-C07 semantics, the frozen provider or model policy, or the
runtime prompt and schemas. It did not authorize C09.

The accepted implementation commit was not amended, rebased, squashed or
replaced. The original C08 implementation and publication history remains intact.

## 3. GPT R1 Findings

GPT C08 Independent Review R1 returned `REPAIR REQUIRED` with four findings:

- **HIGH-01** — provider text was not mechanically grounded to exact
  `ExplanationContextV1` facts;
- **MEDIUM-01** — causal, probability and efficacy paraphrases could bypass the
  finite lexical patterns;
- **MEDIUM-02** — numeric and temporal validation used global token membership
  rather than exact field binding;
- **MEDIUM-03** — `UNKNOWN` and `INSUFFICIENT_EVIDENCE` resolution paraphrases
  could bypass the narrow phrase detector.

```text
HIGH-01: CLOSED
MEDIUM-01: CLOSED
MEDIUM-02: CLOSED
MEDIUM-03: CLOSED
```

## 4. Exact Repair Scope

Repair SHA `eefca6322ae3fdf3aa652edc77703189e5c35c95` changed exactly:

```text
src/flowlens/decision/c08_validation.py
tests/test_c08_explanation.py
tests/test_c08_harness.py
tests/test_c08_validation.py
```

No other implementation, dependency, schema, prompt, provider, model, CI,
control-plane or operational path changed.

## 5. Repair Design

The accepted `BOUNDED_LLM` path now uses a deterministic, closed,
section-specific statement grammar. Every accepted provider statement must match
an exact grammar statement derived from `ExplanationContextV1`. Variable tokens
are bound to the corresponding context field, and evidence/reason references
must equal the references mechanically attached to the parsed statements.

The four sections admit only these bounded statement families:

1. frozen recommendation disposition, selected candidate identity/family/registry
   and exact candidate order;
2. diagnosis problem code, claim code/type, signal type/state and exact evidence
   object facts;
3. simulation candidate/family/status, exact measurement name/value/unit and the
   fixed modeled-comparison boundary;
4. uncertainty code/status, limitation code and fixed Human-review wording.

Residual or arbitrary prose is a nonrepairable grounding failure. Exact
numeric/time values bind to the represented measurement or evidence field, not a
global context token set. `UNKNOWN` and `INSUFFICIENT_EVIDENCE` have no accepted
resolved/known/clear/confirmed/understood grammar variant.

## 6. Fallback and Provider-Call Semantics

| Condition | Verified behavior |
|---|---|
| Valid mechanically grounded provider output | `BOUNDED_LLM` |
| Schema-only first failure | Exactly one repair call permitted |
| Maximum provider calls | `2` |
| First grounding/semantic failure | No schema repair; `DEGRADED_TEMPLATE` |
| Second-call invalid or ungrounded result | `DEGRADED_TEMPLATE` |
| Expected provider transport/refusal | `DEGRADED_TEMPLATE` |
| Unexpected `RuntimeError` / `AssertionError` | Propagates to test/CI failure |
| SDK automatic retries | `0` |

## 7. Adversarial Semantic Matrix

| Case | Observed result |
|---|---|
| Closed section-specific statement grammar | PASS |
| Arbitrary unsupported prose | REJECTED / NONREPAIRABLE |
| Causal paraphrases (`led to`, `resulted from`, `because of`) | REJECTED / NONREPAIRABLE |
| Probability/efficacy paraphrases (`likely`, `chance`) | REJECTED / NONREPAIRABLE |
| `UNKNOWN` / `INSUFFICIENT_EVIDENCE` resolution paraphrases | REJECTED / NONREPAIRABLE |
| Numeric cross-field rebinding using a real context token | REJECTED |
| Temporal cross-field rebinding using a real context token | REJECTED |
| Allowlisted evidence ID attached to unrelated prose | REJECTED |
| Valid mechanically grounded provider output | `BOUNDED_LLM` |
| Schema-only repair | MAXIMUM TWO PROVIDER CALLS |
| Grounding failure | NO SCHEMA REPAIR |
| Same/fresh-process degraded fallback | PASS |
| Packet immutability | PASS |
| Recommendation immutability | PASS |

The mandatory post-CI semantic audit reran this matrix against exact repair SHA
`eefca6322ae3fdf3aa652edc77703189e5c35c95` and observed:

```text
POST-CI SEMANTIC AUDIT: 28 / 28 PASS
```

## 8. Local Validation Evidence

| Gate | Observed result |
|---|---|
| Complete C08 suite, including H01-H46 and R1 hardening | 92 passed |
| Focused R1 semantic matrix before commit | 28 passed |
| Focused R1 semantic matrix after exact-SHA CI | 28 passed |
| C07 regression | 75 passed |
| C06 regression | 66 passed |
| C05 regression | 98 passed |
| C04 regression | 31 passed |
| C03 regression | 77 passed; 5 safely guarded PostgreSQL skips |
| C02 regression | 26 passed |
| C01 regression | 39 passed / unchanged |
| W2 scenario/HGT regression set | 173 passed |
| Complete non-integration suite | 856 passed; 48 deselected; 1 existing warning |
| Guarded local PostgreSQL integration | NOT RUN — safety variables unset and Docker engine pipe absent |
| Ruff | PASS |
| Strict mypy | PASS / 137 source files |
| Dependency lock | PASS / 43 packages resolved with CI-pinned `uv 0.12.5` |
| OpenAI SDK | `2.54.0` installed and locked |
| `git diff --check` | PASS |
| Docker Compose configuration | PASS |
| Authorized-path audit | PASS / 4 changed paths, all authorized |
| Prompt hash / byte length | PASS / 2479 bytes / `426b061d79d2a8dfa4ac2959a604e77e6ef8dbcc04759bf7860ec9f012d185fc` |
| Embedded/published output schema equality | PASS |

The warning is the pre-existing Starlette/httpx deprecation warning and does
not alter any result.

## 9. Exact-SHA CI Evidence

[Run #75 / `37185441717`](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37185441717)
proved exact repair SHA `eefca6322ae3fdf3aa652edc77703189e5c35c95`:

```text
Class: I / FULL_EXACT_SHA
Exact source head: PASS
Integration: 48 PASS / 856 DESELECTED / 1 EXISTING WARNING
Non-integration: 856 PASS / 48 DESELECTED / 1 EXISTING WARNING
Ruff: PASS
Mypy: PASS / 137 SOURCE FILES
Docker Compose: PASS
Dependency lock: PASS / 43 PACKAGES
Verification: PASS
Publication proof: SKIPPED
```

## 10. Frozen Contract Audit

```text
RUNTIME SYSTEM PROMPT CHANGE: NONE
PROMPT VERSION / SHA CHANGE: NONE
CONTEXT SCHEMA CHANGE: NONE
OUTPUT SCHEMA CHANGE: NONE
PROVIDER / MODEL CHANGE: NONE
DEPENDENCY CHANGE: NONE
C01-C07 SEMANTIC CHANGE: NONE
OPERATIONAL MUTATION: NONE
C09 WORK: NONE
```

The runtime prompt remains exactly 2479 UTF-8 bytes with SHA-256
`426b061d79d2a8dfa4ac2959a604e77e6ef8dbcc04759bf7860ec9f012d185fc`.
Provider `OpenAI`, requested model `gpt-5.6-terra`, reasoning effort `none`,
output/token/timeout settings, public context/output schemas and all version
values remain unchanged.

## 11. Safety and Immutability

The repair adds no provider tool, database, filesystem, network, retrieval, HGT
or operational-write authority. The provider remains explanation-only. Packet
bytes and the frozen recommendation remain unchanged across valid, rejected,
fallback and schema-repair paths. No quality release, procurement allocation,
scheduling, supplier replacement or other operational mutation is authorized or
performed.

## 12. Known Limitation

Accepted `BOUNDED_LLM` wording is intentionally constrained to a closed
packet-derived statement grammar; expressive paraphrase breadth is traded for
mechanical grounding and fail-closed semantics.

## 13. Git / GitHub Synchronization Before Publication

Immediately before this two-file publication delta:

```text
local HEAD = eefca6322ae3fdf3aa652edc77703189e5c35c95
tracking HEAD = eefca6322ae3fdf3aa652edc77703189e5c35c95
direct remote W03 HEAD = eefca6322ae3fdf3aa652edc77703189e5c35c95
PR #6 HEAD = eefca6322ae3fdf3aa652edc77703189e5c35c95
working tree = CLEAN
ahead / behind = 0 / 0
main = 9d18ddde9fe933952a2661ee1419f13c8577605d / UNCHANGED
PR #6 = OPEN / DRAFT / NOT MERGED
auto-merge = ABSENT / DISABLED
```

This report and `docs/CURRENT_STATE.md` are the exact authorized publication
paths. The publication commit SHA, `P / PUBLICATION_EXACT_SHA` run and final
post-publication synchronization are immutable post-push facts and are recorded
in the final Codex handoff.

## 14. Findings by Severity

```text
BLOCKER: NONE OBSERVED
HIGH: NONE OPEN — R1 HIGH-01 CLOSED
MEDIUM: NONE OPEN — R1 MEDIUM-01 / MEDIUM-02 / MEDIUM-03 CLOSED
LOW: NONE OBSERVED
POST-CI SEMANTIC AUDIT: 28 / 28 PASS
```

These are Codex repair and harness results. They are not GPT C08 R2 re-review or
Human acceptance.

## 15. Current Status

```text
TASK: W03-C08-REPAIR-01
GPT C08 R1: REPAIR REQUIRED
REPAIR IMPLEMENTATION SHA: eefca6322ae3fdf3aa652edc77703189e5c35c95
REPAIR IMPLEMENTATION CI: RUN #75 / 37185441717 / PASS / I / FULL_EXACT_SHA
POST-CI SEMANTIC AUDIT: 28 / 28 PASS
REPAIR REPORT PUBLICATION EXACT-SHA: PENDING ON THIS COMMIT
GPT C08 R2 RE-REVIEW: PENDING
HUMAN C08 ACCEPTANCE: PENDING
C08 CLOSED: NO
C09 AUTHORIZED: NO
NEXT: GPT W03-C08 INDEPENDENT RE-REVIEW R2
STATUS: REVIEW_READY_FOR_GPT_R2 ONLY AFTER PUBLICATION GATE
```

Do not begin C09. Do not self-review or Human-accept C08. Do not close C08.
