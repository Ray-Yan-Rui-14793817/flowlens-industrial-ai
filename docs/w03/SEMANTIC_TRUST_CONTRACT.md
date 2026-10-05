# FlowLens Industrial AI — W03 Semantic Trust Contract

**Task:** W03-G0-GPT-03\
**Status:** FROZEN FOR G0 HUMAN REVIEW\
**Baseline:** `main@9d18ddde9fe933952a2661ee1419f13c8577605d`

---

## 1. Purpose

This contract defines what FlowLens may treat as fact, derivation, association, uncertainty, or prohibited inference.

The goal is not to maximize certainty.

The goal is to ensure that every decision-relevant statement carries an explicit and reviewable semantic strength.

---

## 2. Trust Vocabulary

### DIRECT_FACT

A relationship or value explicitly represented by the authorized operational model.

Examples:

```text
WorkOrder.sales_order_id → SalesOrder
SalesOrder.product_id → Product
QualityInspection.work_order_id → WorkOrder
```

Allowed:

```text
state direct relationship
derive contract-authorized properties
support high-confidence reasoning
```

Forbidden:

```text
claim facts beyond the represented relationship
```

---

### DERIVED_FACT

A deterministic calculation from authorized facts using a versioned rule.

Requirements:

```text
derivation_id
derivation_version
input evidence IDs
as_of_time
deterministic output
```

Examples:

```text
days_to_promised_delivery
queue_delay_seconds
delivered_quantity_sum
```

A derived fact is not a new observed business event.

---

### ASSOCIATIVE_EVIDENCE

Evidence related through business key, material, time, route, or other bounded association without a direct modeled relationship.

Allowed:

```text
support investigation
support bounded risk context
contribute to a rule explicitly authorized to use associative evidence
```

Forbidden:

```text
direct allocation claim
causal assertion
root-cause assertion
formal business-status assertion
```

---

### UNKNOWN

The available data does not establish a valid answer.

Unknown is a first-class semantic result.

It must not be replaced with a guessed default.

---

### FORBIDDEN_INFERENCE

A conclusion that the current evidence model does not authorize.

Examples:

```text
specific PO definitely supplied a specific WorkOrder
rework means formal quality release
failed quantity was scrapped without a scrap record
route variance automatically means process anomaly
scenario label reveals true runtime cause
```

A `FORBIDDEN_INFERENCE` must never be converted into a Signal, Diagnosis claim, recommendation reason, or LLM explanation.

---

## 3. Evidence Contract

Every Evidence item must support at least:

```text
evidence_id
source_entity
source_record_id
source_field
value

observed_at
available_at

relationship_type
trust_level
freshness_status

limitations
provenance
```

Optional future fields may be added only if they do not weaken the above semantics.

---

## 4. Temporal Semantic Rules

A runtime evidence item is eligible only when:

```text
available_at <= as_of_time
```

Freshness is separate from future leakage.

Minimum freshness vocabulary:

```text
FRESH
STALE
EXPIRED
UNKNOWN
NOT_APPLICABLE
```

Numeric freshness thresholds are checkpoint-specific and must be authorized in C02 when actual source semantics are known.

A stale item may remain visible as evidence but may not be represented as current fact when the contract says current-state evidence is required.

---

## 5. Week 2 Semantic Backlog Mapping

### ST-01 — Rework does not prove release

```text
Rework recorded
→ DIRECT_FACT

Formal post-rework release
→ UNKNOWN
```

Required runtime field:

```text
quality_finality = UNKNOWN
```

unless an explicit release event exists in future authorized data.

---

### ST-02 — Procurement evidence is associative

```text
PurchaseOrder → Material
DIRECT_FACT

PurchaseOrder → Supplier
DIRECT_FACT

MaterialRequirement → WorkOrder
DIRECT_FACT

MaterialRequirement → a specific PurchaseOrder
NOT DIRECT
```

A PO selected by material/time proximity is:

```text
ASSOCIATIVE_EVIDENCE
```

Required limitation language:

```text
does not establish order-specific allocation
```

---

### ST-03 — Inventory snapshot is time-bounded evidence

An InventorySnapshot directly records a quantity at its observation time.

It does not automatically prove availability at later WorkOrder execution.

Required semantics:

```text
observed inventory quantity
= DIRECT_FACT AT SNAPSHOT TIME

later production availability
= ASSOCIATIVE / STALENESS-CONSTRAINED
```

---

### ST-04 — Route variance is context, not automatically risk

Week 2 observed a material number of orders outside a strict preferred-route heuristic.

W3 G0 freezes:

```text
ROUTE_VARIANCE
= OBSERVED CONTEXT
```

Whether it becomes a Signal is a C03 semantic decision.

It must not be treated as anomaly solely because it differs from a preferred route.

Use actual recorded operation sequence.

---

### ST-05 — Failed quantity disposition gap

Where failed quantity is not fully explained by recorded rework:

```text
QUALITY_DISPOSITION_GAP = TRUE
quality_disposition = UNKNOWN
```

Forbidden guesses:

```text
scrap
replacement
concession
implicit rework
```

---

## 6. Claim Policy

Every structured Diagnosis or Recommendation reason must be one of:

```text
FACT_CLAIM
DERIVED_CLAIM
ASSOCIATIVE_CLAIM
UNCERTAINTY_STATEMENT
```

Rules:

- `FACT_CLAIM` requires DIRECT_FACT evidence.
- `DERIVED_CLAIM` requires a versioned deterministic derivation.
- `ASSOCIATIVE_CLAIM` must visibly preserve associative language.
- `UNCERTAINTY_STATEMENT` must preserve unknown/insufficient status.
- causal or root-cause language is forbidden unless a future explicit causal contract authorizes it.

---

## 7. Signal Semantics Boundary

G0 authorizes the signal vocabulary, not every threshold.

Initial vocabulary:

```text
SUPPLIER_LATE_RECEIPT
MATERIAL_TIMING_RISK
QUALITY_FAILURE
REWORK_PRESENT
QUALITY_DISPOSITION_UNKNOWN
QUEUE_DELAY
CAPACITY_PRESSURE
DELIVERY_RISK
```

C03 must freeze for each Signal:

```text
trigger
required evidence
allowed trust levels
forbidden inference
reason code
unknown behavior
```

Codex cannot invent thresholds or business semantics.

---

## 8. Diagnosis Semantics

Diagnosis is structured synthesis, not free-form causal truth.

Required concepts:

```text
problem
supporting_signals
supporting_evidence
uncertainties
affected_path
reason_codes
```

Diagnosis must not access HGT.

Diagnosis must not convert:

```text
association → causality
unknown → fact
context → anomaly
```

---

## 9. Recommendation Semantics

A Recommendation may only reference:

```text
authorized CandidateSet
SimulationBundle
approved scoring/decision policy
explicit uncertainties
```

Recommendation must not imply that a simulated intervention will certainly succeed operationally.

Recommended wording family:

```text
recommended for human investigation
preferred under current modeled evidence
no recommendation due to insufficient evidence
no action favored under current modeled comparison
```

---

## 10. Semantic Conflict Resolution

If evidence conflicts:

```text
do not silently pick the convenient item
```

Instead record:

```text
conflict = TRUE
conflicting_evidence_ids
resolution_status
```

If a critical conflict remains unresolved:

```text
NO_RECOMMENDATION or DEFER
```

according to the checkpoint-specific abstention policy.

---

## 11. Semantic Trust Gate

The Semantic Trust Gate must reject any runtime artifact that:

- presents associative evidence as direct;
- hides an explicit unknown;
- contains a forbidden inference;
- removes required limitation metadata;
- makes an unsupported causal claim;
- uses evidence unavailable at decision time.

---

## 12. G0 Status

```text
SEMANTIC TRUST VOCABULARY:
FROZEN

W2 SEMANTIC BACKLOG TREATMENT:
FROZEN

SIGNAL THRESHOLDS:
DEFERRED TO C03 AUTHORIZATION

NUMERIC STALENESS THRESHOLDS:
DEFERRED TO C02 AUTHORIZATION

IMPLEMENTATION:
NOT AUTHORIZED
```
