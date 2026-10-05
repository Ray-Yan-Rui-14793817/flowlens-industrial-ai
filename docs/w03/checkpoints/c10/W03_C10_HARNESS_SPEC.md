# FlowLens Industrial AI — W03-C10 Harness Specification

C10 is an acceptance-readiness/evidence harness. It must never substitute technical
proof for Product Owner business acceptance.

```text
H01 exact C10 entry branch/head/main/PR/Run #80 preflight
H02 exact Human implementation authorization before mutation
H03 package checksums and C10 contract projection verified
H04 Context Lock published LOCKED before dossier/sprint write
H05 implementation paths exactly equal authorized C10 control-plane set

H06 A01 state identity/time/trust/provenance/limitation evidence present
H07 A01 unresolved/unknown state is not hidden
H08 A02 signals/diagnosis are evidence-linked and investigation-oriented
H09 A02 no unsupported causal/root-cause upgrade
H10 A03 evidence traceability/trust/availability/limitations visible
H11 A04 UNKNOWN/conflict/insufficiency preserved
H12 A04 abstention/degraded explanation states visibly bounded
H13 A05 only authorized intervention families represented
H14 A05 no intervention is represented as operational execution
H15 A06 baseline and counterfactual are clearly separated
H16 A06 modeled outcomes are not represented as guarantees
H17 A07 recommendation basis/reasons/uncertainty surfaced
H18 A07 no recommendation implies execution authority
H19 A08 explanation is packet-grounded and authority-preserving
H20 A08 grounding/injection failure and degraded fallback boundaries surfaced
H21 A09 DecisionPacket/Explanation/HumanDecisionEvent review surface documented
H22 A09 ACCEPT/REJECT/DEFER remains append-only review-only authority
H23 A10 replay identities and deterministic-first boundary surfaced
H24 A10 evaluation/HGT isolation and no feedback into original recommendation surfaced

H25 all 11 W3 exit criteria mapped with no omission
H26 all 10 dimensions have concrete accepted evidence anchor(s)
H27 every dimension states what evidence does NOT prove
H28 every dimension Human assessment remains PENDING_PRODUCT_OWNER_DECISION
H29 no numeric business score/weight/automatic acceptance policy introduced

H30 exact-SHA C10 implementation CI: C / FULL_EXACT_SHA with Quality PASS
H31 exact-SHA C10 implementation CI: Compose + W03 AI loop gate + Verification PASS
H32 no src/tests/workflow/dependency/schema/migration/API/worker/Docker/runtime semantic change
H33 no live provider call/secret read/runtime HGT/operational mutation/PR merge/C10 auto-accept
H34 final technical readiness is PASS only when H01-H34 and A01-A10 evidence readiness all pass
```

## Technical outcome vocabulary

Allowed:

```text
Axx: EVIDENCE_READY
Axx: EVIDENCE_GAP

TECHNICAL ACCEPTANCE READINESS: PASS
TECHNICAL ACCEPTANCE READINESS: FAIL
```

Forbidden for Codex:

```text
Axx: ACCEPTED
BUSINESS ACCEPTANCE: PASS
W03-C10 HUMAN ACCEPTANCE: ACCEPTED
C10 CLOSED: YES
```

## Required evidence walkthroughs

The dossier must include W01-W06 from the Business Acceptance Specification.
Each walkthrough must reference existing accepted repository evidence rather than
inventing a new Product Owner scenario or business result.

## Publication condition

No C10 readiness report may be published until:

```text
implementation exact-SHA FULL proof = PASS
H01-H34 = 34/34 PASS
A01-A10 = 10/10 EVIDENCE_READY
```

Even then Human business acceptance remains pending.
