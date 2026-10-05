# FlowLens Industrial AI — W03-C10 Evidence Matrix

This matrix freezes the minimum technical evidence classes for each Human review
dimension. It is not a Product Owner scorecard.

| ID | Dimension | Primary accepted evidence | C09 regression anchors | Human judgement |
|---|---|---|---|---|
| A01 | State interpretability | C01 contracts; C02 StateSnapshot/DecisionContext/EvidenceBundle | F01, F02 | PENDING |
| A02 | Risk usefulness | C03 deterministic Signals + DiagnosisRecord | F03 | PENDING |
| A03 | Evidence usefulness | C02 trust/provenance/available-at rules; C03 evidence-backed diagnosis | F02, F03 | PENDING |
| A04 | Honesty of uncertainty | C02 UNKNOWN/conflict; C05 abstention; C08 fail-closed grounding/degradation | F02, F05, F08 | PENDING |
| A05 | Intervention usefulness | C04 registry + scenario adapter; C05 candidate/recommendation boundary | F04, F05 | PENDING |
| A06 | Counterfactual clarity | C04 baseline/counterfactual/neutral semantics; C07 replay evaluation | F04, F07 | PENDING |
| A07 | Recommendation usefulness | C05 RecommendationRecord + DecisionPacket + tie/abstention policy | F05 | PENDING |
| A08 | Explanation faithfulness | C08 bounded explanation, grounding, injection, fallback | F08, F10 | PENDING |
| A09 | Human-review ergonomics | C06 append-only HumanDecisionEvent; DecisionPacket + ExplanationRecord review surface | F06 | PENDING |
| A10 | Replayability | C07 replay/HGT isolation; C09 exact-SHA regression proof | F07, F09, F10 | PENDING |

## Required system-level anchors

Every dossier must also reference:

```text
C09 implementation SHA:
f214b20e54e2ff6ad3c1227ebb53e4aadaa204c9

C09 exact-SHA CI:
Run #78 / 37216528805 / PASS

C09 W03 AI loop gate:
F01-F10 / 38 selectors / 85 expanded cases / PASS

C09 post-CI audit:
H01-H42 / 42 OF 42 PASS

C09 report publication:
330241be4039711e32d631a6d83eb36edd1f2888
Run #79 / 37218374366 / PASS

C09 final closeout:
147cefae890d3a450052298f0a331e1528e1f856
Run #80 / 37220934558 / PASS
```

## Evidence boundary

`EVIDENCE_READY` means the technical evidence needed for Human review exists and is
faithfully surfaced.

It does not mean:

```text
useful enough
acceptable enough
ready for production
approved for merge
business accepted
```

Those are Product Owner/governance decisions outside Codex authority.
