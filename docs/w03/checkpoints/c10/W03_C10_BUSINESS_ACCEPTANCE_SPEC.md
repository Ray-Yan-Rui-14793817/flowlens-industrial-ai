# FlowLens Industrial AI — W03-C10 Business Acceptance Specification

## 1. Purpose

C10 turns the accepted W03 technical evidence into a Product Owner review surface.

It answers:

```text
Is there enough faithful, end-to-end evidence for a Human to judge whether this
OFFLINE / SHADOW / HUMAN-IN-THE-LOOP decision loop is useful and trustworthy?
```

It does not answer the Product Owner's acceptance decision.

## 2. Decision-authority rule

```text
TECHNICAL EVIDENCE READINESS != BUSINESS ACCEPTANCE
```

Codex and GPT may mark only `EVIDENCE_READY` or `EVIDENCE_GAP`.

Every Human assessment remains:

```text
PENDING_PRODUCT_OWNER_DECISION
```

until the Product Owner reviews the dossier.

## 3. Frozen dimensions

| ID | Dimension | Product Owner review question |
|---|---|---|
| A01 | STATE_INTERPRETABILITY | Can I understand the decision-time order state, time boundary, trust, provenance, limitations and unresolved state? |
| A02 | RISK_USEFULNESS | Do the risk signals and structured diagnosis help me identify where investigation should begin without unsupported root-cause claims? |
| A03 | EVIDENCE_USEFULNESS | Is the evidence traceable, bounded, appropriately qualified and useful for investigation? |
| A04 | HONESTY_OF_UNCERTAINTY | Are UNKNOWN, conflict, insufficiency, abstention and degraded states visible rather than silently resolved? |
| A05 | INTERVENTION_USEFULNESS | Are authorized intervention families useful as bounded investigation options without implying execution? |
| A06 | COUNTERFACTUAL_CLARITY | Can I distinguish baseline from modeled counterfactual outcomes and limitations without reading simulations as guarantees? |
| A07 | RECOMMENDATION_USEFULNESS | Is the deterministic recommendation or abstention useful for Human review with reasons and uncertainty preserved? |
| A08 | EXPLANATION_FAITHFULNESS | Does the bounded explanation faithfully restate the packet without inventing facts or changing authority? |
| A09 | HUMAN_REVIEW_ERGONOMICS | Can I review and record ACCEPT / REJECT / DEFER at the artifact level without operational execution? |
| A10 | REPLAYABILITY | Can I audit/reproduce the run from frozen identities while evaluation/HGT stays isolated? |

## 4. Evidence-ready rule

A dimension is `EVIDENCE_READY` only when the dossier provides:

1. at least one concrete accepted artifact/contract/test/report anchor;
2. the relevant exact-SHA technical proof;
3. a clear statement of what the evidence proves;
4. a clear statement of what it does **not** prove;
5. relevant known limitations;
6. no unsupported business judgement.

Otherwise it is `EVIDENCE_GAP`.

One `EVIDENCE_GAP` means technical acceptance readiness is not PASS.

## 5. Required walkthroughs

The dossier must include concrete, repository-supported walkthroughs covering:

### W01 — State / Trust

Show decision-time identity, `as_of_time`, trust/provenance/limitations and at least
one uncertainty/conflict concept.

### W02 — Risk / Diagnosis

Show grounded signals, structured diagnosis, evidence linkage and no unsupported
causal/root-cause upgrade.

### W03 — Intervention / Counterfactual

Show an authorized candidate family, baseline/counterfactual separation, modeled
effect language and baseline immutability.

### W04 — Recommendation / Abstention

Show deterministic recommendation basis and an accepted abstention/neutral/unknown
path.

### W05 — Explanation / Human Review

Show bounded explanation faithfulness/degradation and the review-only
`ACCEPT / REJECT / DEFER` Human authority boundary.

### W06 — Replay / Protection

Show deterministic replay identities, evaluation/HGT isolation and no operational
mutation / unauthorized capability.

Codex may choose the concrete existing fixture/test/report evidence used for each
walkthrough, but may not invent outcomes.

## 6. W3 exit-criteria matrix

The dossier must account for every exit verb:

| Exit criterion | Primary C10 dimensions |
|---|---|
| OBSERVE | A01 |
| TRUST | A01, A03, A04 |
| DETECT | A02 |
| DIAGNOSE | A02, A03 |
| SIMULATE | A05, A06 |
| RECOMMEND | A07, A04 |
| EXPLAIN | A08, A04 |
| REVIEW | A09 |
| EVALUATE | A06, A10 |
| REPRODUCE | A10 |
| PROTECT | A03, A04, A08, A10 |

## 7. Explicit non-capabilities to disclose

C10 must surface, not hide:

```text
no operational execution
no autonomous scheduling/procurement/supplier replacement/quality release
no production deployment
no ERP/MES integration
no free-form LLM tool use
no runtime HGT
no automatic business acceptance
no production UI claim
```

The Human review surface is artifact-level W3 v0, not a claim of production UX.

## 8. Known accepted limitation handling

Known accepted limitations must be carried into the dossier where relevant, including:

```text
C08 closed packet-derived explanation grammar
existing Starlette/httpx deprecation warning
branch protection unchanged/outside C10 scope
```

A known limitation may be acceptable to the Product Owner, but Codex/GPT may not make
that business judgement.

## 9. Human acceptance

After Codex evidence preparation and GPT independent review, the Product Owner may
accept only by explicitly supplying:

```text
W03-C10 HUMAN ACCEPTANCE: ACCEPTED
```

Until then:

```text
BUSINESS ACCEPTANCE: PENDING
C10 CLOSED: NO
W03 SPRINT CLOSED: NO
PR #6 MERGE AUTHORIZED: NO
```
