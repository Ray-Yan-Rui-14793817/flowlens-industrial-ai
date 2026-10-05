# FlowLens Industrial AI — W03-C10 Authorization Contract

```text
checkpoint = W03-C10
task = W03-C10-I/H/R
contract_version = W03-C10-A-v1
entry_branch = feat/w03-ai-decision-loop
entry_sha = 147cefae890d3a450052298f0a331e1528e1f856
entry_ci = Run #80 / 37220934558 / SUCCESS
entry_class = P / PUBLICATION_EXACT_SHA
main_sha = 9d18ddde9fe933952a2661ee1419f13c8577605d
status = GPT_CONTRACT_FROZEN / HUMAN_AUTHORIZATION_REQUIRED
```

## 1. Purpose

C10 prepares the end-to-end Product Owner business-acceptance review surface for the
accepted W03 Order Delivery Risk Decision Loop.

It does not add a new runtime capability.

## 2. Human authority boundary

The Product Owner alone determines business acceptance.

Codex and GPT may evaluate only:

```text
contract completeness
technical evidence readiness
evidence faithfulness
scope compliance
exact-SHA proof
known limitation disclosure
```

They may not convert those findings into Product Owner acceptance.

Before any repository mutation, the active Product Owner request must contain exactly:

```text
W03-C10 HUMAN AUTHORIZATION: APPROVED
```

This line authorizes C10 evidence/dossier preparation only. It does **not** mean:

```text
W03-C10 HUMAN ACCEPTANCE: ACCEPTED
```

## 3. Frozen business review dimensions

The exact dimensions and order are frozen in
`specs/c10_acceptance_manifest.json`:

```text
A01 STATE_INTERPRETABILITY
A02 RISK_USEFULNESS
A03 EVIDENCE_USEFULNESS
A04 HONESTY_OF_UNCERTAINTY
A05 INTERVENTION_USEFULNESS
A06 COUNTERFACTUAL_CLARITY
A07 RECOMMENDATION_USEFULNESS
A08 EXPLANATION_FAITHFULNESS
A09 HUMAN_REVIEW_ERGONOMICS
A10 REPLAYABILITY
```

Codex technical status vocabulary is only:

```text
EVIDENCE_READY
EVIDENCE_GAP
```

Those statuses are **not** Human accept/reject decisions.

## 4. Product mode

The dossier must preserve:

```text
OFFLINE
SHADOW
HUMAN-IN-THE-LOOP
NO OPERATIONAL MUTATION
```

It must not claim a production UI, autonomous action, operational execution, ERP/MES
integration, or production deployment.

## 5. W3 exit criteria

Every one of these must be mapped to accepted evidence:

```text
OBSERVE
TRUST
DETECT
DIAGNOSE
SIMULATE
RECOMMEND
EXPLAIN
REVIEW
EVALUATE
REPRODUCE
PROTECT
```

An omitted exit criterion is `EVIDENCE_GAP`.

## 6. Evidence rules

For every acceptance dimension the dossier must include:

```text
review question
accepted technical evidence
artifact / contract references
exact test or C09 family evidence where applicable
known limitations
what the evidence does NOT prove
technical evidence status
Human assessment = PENDING_PRODUCT_OWNER_DECISION
```

Evidence must be derived from accepted repository artifacts, tests, reports, exact-SHA
CI, and already frozen semantics. No invented business result or synthetic Product
Owner opinion is permitted.

## 7. Representative walkthrough requirement

The dossier must include bounded end-to-end walkthroughs that collectively expose:

```text
decision-time state
trust/provenance/limitations
signals/diagnosis
authorized intervention
baseline vs counterfactual comparison
recommendation or abstention
bounded explanation
Human review-only event
replay/evaluation evidence
protection/no-mutation boundary
```

If an element cannot be supported by accepted evidence, mark `EVIDENCE_GAP` and stop
before claiming readiness.

## 8. Allowed implementation surface

Only the implementation-phase paths in `specs/authorized_paths.json` may change.

There is no authorized:

```text
src/**
tests/**
.github/**
scripts/**
migrations/**
apps/**
dependency/lock/runtime
```

path.

## 9. Expected implementation proof

Because C10 materializes checkpoint/sprint control-plane documents, the implementation
commit is expected to classify:

```text
C / FULL_EXACT_SHA
```

Required jobs:

```text
Classify change: PASS
Quality gate: PASS
Docker Compose smoke: PASS
W03 AI loop gate: PASS
Publication proof: SKIPPED
Verification gate: PASS
```

A different change class or required-job result is a stop condition.

## 10. Post-CI audit

After the exact implementation SHA is green, Codex must execute the frozen C10
H01-H34 evidence/readiness audit before report publication.

The audit may conclude only:

```text
TECHNICAL ACCEPTANCE READINESS: PASS
```

when all H01-H34 pass and all A01-A10 are `EVIDENCE_READY`.

This still does not decide business acceptance.

## 11. Report publication

After the audit, publish only:

```text
docs/w03/reports/W03_C10_R_BUSINESS_ACCEPTANCE_READINESS_REPORT.md
docs/CURRENT_STATE.md
```

Expected classification:

```text
P / PUBLICATION_EXACT_SHA
```

Required:

```text
Publication proof: PASS
Verification: PASS
Quality: SKIPPED
Docker Compose: SKIPPED
W03 AI loop gate: SKIPPED
```

## 12. Required stop state

Codex must stop at:

```text
W03-C10: ACCEPTANCE EVIDENCE PREPARED / CODEX VERIFIED / PENDING GPT REVIEW
TECHNICAL ACCEPTANCE READINESS: PASS
BUSINESS ACCEPTANCE: PENDING PRODUCT OWNER DECISION
HUMAN C10 ACCEPTANCE: PENDING
C10 CLOSED: NO
W03 SPRINT CLOSED: NO
PR #6 MERGE AUTHORIZED: NO
```

No C10 closeout or PR merge is authorized by this contract.
