# W04-C10 Authorization Contract

This is the selected projection of the explicitly approved V1.1 task, resumed under R1/R2 and Continuation V1. The supplied Human prompts authorize execution; attachment text alone supplies no independent authority. The original design, frozen baselines and all business-authority limits remain in force.

| Authority | Raw SHA-256 |
|---|---|
| V1.1 — FLOWLENS_W04_C10_CODEX_DEVELOPMENT_TASK_V1_1.md | `15f8c1ddd8a423edccb0fb2f927675b609a5b6177427f61e643bfb964c7314d4` |
| R1 — FLOWLENS_W04_C10_BOOTSTRAP_CLARIFICATION_R1.md | `8438d86dd144728f8f8714eccacfaae47ba629fa0476cb34cb430b6b750d4d3c` |
| R2 — FLOWLENS_W04_C10_BOOTSTRAP_CLARIFICATION_R2.md | `d1b57a41a7f71f994256be719feaa21f21b552ee4b53ad1c0549a87f1dc75e44` |
| Continuation V1 — FLOWLENS_W04_C10_CONTINUATION_TASK_V1.md | `7cd20e05b5eac4350d9fcfdf02bec6cd59daaaa345d30fa748e108ed86bbcc8b` |

```text
HUMAN IMPLEMENTATION AUTHORIZATION = APPROVED
HUMAN BUSINESS ACCEPTANCE = PENDING
HUMAN_C10_ACCEPTANCE = PENDING
GPT_INDEPENDENT_C10_REVIEW = PENDING
C10 CLOSEOUT AUTHORIZATION = NOT GRANTED
W04 SPRINT CLOSEOUT = NOT AUTHORIZED
PR #7 = OPEN / DRAFT / UNMERGED
PR READY / MERGE / AUTO-MERGE = NOT AUTHORIZED
BRANCH DELETION / MAIN WRITE / POST-W04 IMPLEMENTATION = NOT AUTHORIZED
```

## Frozen scope and sequence

C09 final `d33ee858fca8caaceba2ce60c045f7e4213c631a` -> one unchanged Bootstrap `a34a84b97681f24bf6df1fed1a80825ae32decfa` -> exact eleven added Stage-A files -> own-SHA full CI -> H01-H44/A01-A10/R2G01-R2G12 audit -> exactly one added Stage-B report -> committed-head C10_REVIEW_READY proof -> own-SHA Publication/Verification -> four-head synchronization -> W04_C10_REVIEW_READY STOP.

Every phase is a direct single-parent child. Stage A/B each allow exactly one normal commit/push. No amend, rebase, reset, force-push, silent repair, extra phase commit or checkpoint auto-advance is permitted. A failed required gate stops; a rerun cannot replace failed attempt 1.

Authorized paths are frozen by specs/authorized_paths.json. Existing runtime/tests/workflow/dependencies/schema/migrations/apps/W03/C01-C09 files and the source-evolution manifest must not change; the Bootstrap verifier is byte-frozen.

C10 adds only an evidence dossier. It supplies no production UI/UX proof, SaaS deployment, ERP/MES integration, automatic scheduling/procurement, supplier replacement, quality release, production write-back, root-cause certainty, intervention efficacy, causal or model-accuracy proof, live-provider requirement, runtime HGT access, Human-note-as-evidence, or automatic business acceptance. OFFLINE / SHADOW / HUMAN-IN-THE-LOOP / DETERMINISTIC-FIRST remains the product boundary.

## Selected contract projection

Canonical UTF-8 JSON (sorted keys, compact separators) projection SHA-256: `9224250085430f6a3818860b4736048378a6b3fdc4bc088e056329fed73c46d2`. This hashes only the task projection below; it changes no runtime or dataset hash semantics.

```json
{
  "bootstrap_sha": "a34a84b97681f24bf6df1fed1a80825ae32decfa",
  "bootstrap_subject": "ci(w04-c10): admit bounded acceptance lifecycle",
  "business_acceptance_authority": "HUMAN / PRODUCT OWNER ONLY",
  "continuation_version": "W04-C10-CONTINUATION-V1",
  "contract_version": "W04-C10-A-V1.1",
  "coverage_chain": [
    "BIND",
    "PLAN",
    "NAVIGATE",
    "FIND",
    "CONFLICT",
    "REVIEW",
    "SUMMARIZE",
    "REPLAY",
    "REGRESS",
    "PROTECT"
  ],
  "dimensions": [
    {
      "evidence_class": "C01 contracts + C02 exact binding.",
      "id": "A01",
      "name": "CASE_TRACEABILITY",
      "question": "Can the Product Owner see exactly which frozen DecisionPacket created the InvestigationCase, including identities and decision-time boundary, without packet mutation?"
    },
    {
      "evidence_class": "C03 planning.",
      "id": "A02",
      "name": "INVESTIGATION_PLAN_CLARITY",
      "question": "Does the deterministic investigation plan state what to investigate next without presenting questions as already-proven findings?"
    },
    {
      "evidence_class": "C04 registry/query/navigation.",
      "id": "A03",
      "name": "EVIDENCE_NAVIGATION_TRACEABILITY",
      "question": "Can the Product Owner inspect only authorized historical evidence with clear source/query identity, cutoff, trust and read-only boundaries?"
    },
    {
      "evidence_class": "C05 findings.",
      "id": "A04",
      "name": "FINDING_FAITHFULNESS",
      "question": "Are supported, contradicted, unresolved and unknown findings tied to actual evidence without silent causal or trust upgrades?"
    },
    {
      "evidence_class": "C05 plus upstream trust/temporal limits.",
      "id": "A05",
      "name": "CONFLICT_AND_UNCERTAINTY_HONESTY",
      "question": "Are disagreement, missing evidence, staleness and uncertainty kept visible rather than automatically resolved?"
    },
    {
      "evidence_class": "C06 policy/store/events.",
      "id": "A06",
      "name": "HUMAN_REVIEW_CONTROL",
      "question": "Can investigation review state be recorded with append-only history while Human notes remain non-evidence and no outcome becomes operational authority?"
    },
    {
      "evidence_class": "C07 deterministic summary/provider boundary.",
      "id": "A07",
      "name": "SUMMARY_FAITHFULNESS",
      "question": "Does the summary preserve case scope, findings, conflicts, uncertainty, Human review and authority boundaries, including safe fallback when bounded LLM presentation is unavailable or invalid?"
    },
    {
      "evidence_class": "C08 protected replay.",
      "id": "A08",
      "name": "REPLAYABILITY_AND_AUDITABILITY",
      "question": "Can the investigation be reproduced from frozen artifacts without refreshing evidence, re-running Human decisions or importing hidden/protected truth?"
    },
    {
      "evidence_class": "C09 semantic gate + C08 replay guard + C09 meta-CI/self-source guards + full-suite proof + W03 regression.",
      "id": "A09",
      "name": "REGRESSION_AND_PROTECTION_CONFIDENCE",
      "question": "Is the accepted W04 chain protected by exact-SHA semantic/lifecycle/replay/CI/outcome regression proof?"
    },
    {
      "evidence_class": "faithful synthesis of A01-A09 only.",
      "id": "A10",
      "name": "END_TO_END_INVESTIGATION_REVIEWABILITY",
      "question": "Can one bounded evidence-backed path be followed from frozen DecisionPacket to case, plan, navigation, findings, Human review, summary and replay while seeing limitations and non-authorities at every step?"
    }
  ],
  "entry_sha": "d33ee858fca8caaceba2ce60c045f7e4213c631a",
  "harness": [
    "H01 exact C09-final entry branch/head/main/PR/CI preflight preserved",
    "H02 exact Human V1.1 implementation authorization preceded mutation",
    "H03 V1.1 task hash and selected contract projection verified",
    "H04 Bootstrap is direct child of C09 final with exact subject and sole verifier delta",
    "H05 Bootstrap own-SHA classifier = C / FULL_EXACT_SHA and full native CI PASS",
    "H06 Bootstrap lifecycle/source-span/adversarial controls PASS",
    "H07 C09 anchors, semantic gate, replay/meta-CI/self-source protections preserved",
    "H08 Stage-A parent is exact successful Bootstrap SHA",
    "H09 Stage-A delta is exactly the 11 authorized added C10 files",
    "H10 Context Lock binds exact entry/Bootstrap/protected-object identities",
    "H11 A01 exact DecisionPacket -> InvestigationCase binding evidence present",
    "H12 A01 decision-time/identity invariants and no packet mutation surfaced",
    "H13 A02 deterministic plan/questions/order evidence present",
    "H14 A02 questions are not represented as findings",
    "H15 A03 closed source/query registry and read-only navigation evidence present",
    "H16 A03 temporal cutoff/trust/provenance/limitations surfaced",
    "H17 A04 supported/contradicted/unresolved/unknown finding evidence present",
    "H18 A04 no causal/root-cause/trust upgrade introduced",
    "H19 A05 conflict/missing/stale/uncertain states remain explicit",
    "H20 A05 no silent resolution or automatic confidence upgrade",
    "H21 A06 accepted Human review outcomes and append-only order surfaced",
    "H22 A06 Human notes remain non-evidence and review remains non-operational",
    "H23 A07 exact six-section deterministic summary evidence present",
    "H24 A07 optional bounded LLM remains presentation-only with safe fallback",
    "H25 A08 frozen-artifact replay identity/core evidence present",
    "H26 A08 no evidence refresh/Human-decision rerun/provider/DB/network/HGT authority",
    "H27 A09 C09 9-family/67-selector/81-case semantic gate evidence present",
    "H28 A09 C08 replay/C09 meta-CI/verifier-self guards surfaced",
    "H29 A09 full coverage/no-loss/exact-union/exact-once/W03 evidence surfaced",
    "H30 A10 W01-W08 synthesis uses only accepted evidence; no invented business outcome",
    "H31 A01-A10 exist exactly once and in frozen order",
    "H32 every Axx has an accepted anchor and explicit non-proof statement",
    "H33 every Axx Human assessment remains PENDING_PRODUCT_OWNER_DECISION",
    "H34 W01-W08 exist exactly once and in frozen order",
    "H35 BIND..PROTECT coverage is complete",
    "H36 no business score/weight/threshold/auto-acceptance policy introduced",
    "H37 Stage-A native classifier = C / FULL_EXACT_SHA",
    "H38 Stage-A full-route required jobs PASS; Publication SKIPPED",
    "H39 non-integration = 2997 selected / 2994 passed / exactly 3 accepted skipped / 0 adverse",
    "H40 integration = 70 PASS and W03 = 38 selectors / 85 cases PASS",
    "H41 W04 semantic gate = 9 families / 67 selectors / 81 cases PASS",
    "H42 node digest / weights digest / seven-shard topology / 65m ceiling unchanged",
    "H43 source manifest, C01-C08 source blobs, C09 closeout, Bootstrap verifier,\n    runtime/tests/workflow/dependencies unchanged",
    "H44 no live provider call, provider secret read, runtime HGT, operational mutation,\n    PR action, Human acceptance, C10 closeout, W04 closeout or post-W04 work occurred"
  ],
  "human_assessment": "PENDING_PRODUCT_OWNER_DECISION",
  "stage_a_paths": [
    "docs/w04/checkpoints/c10/W04_C10_AUTHORIZATION_CONTRACT.md",
    "docs/w04/checkpoints/c10/W04_C10_HUMAN_AUTHORIZATION.md",
    "docs/w04/checkpoints/c10/W04_C10_CONTEXT_LOCK.md",
    "docs/w04/checkpoints/c10/W04_C10_BUSINESS_ACCEPTANCE_SPEC.md",
    "docs/w04/checkpoints/c10/W04_C10_EVIDENCE_MATRIX.md",
    "docs/w04/checkpoints/c10/W04_C10_HUMAN_ACCEPTANCE_FORM.md",
    "docs/w04/checkpoints/c10/W04_C10_HARNESS_SPEC.md",
    "docs/w04/checkpoints/c10/W04_C10_GPT_REVIEW_CHECKLIST.md",
    "docs/w04/checkpoints/c10/W04_C10_BUSINESS_ACCEPTANCE_DOSSIER.md",
    "docs/w04/checkpoints/c10/specs/c10_acceptance_manifest.json",
    "docs/w04/checkpoints/c10/specs/authorized_paths.json"
  ],
  "stage_a_subject": "docs(w04-c10): prepare investigation business acceptance",
  "stage_b_path": "docs/w04/checkpoints/c10/W04_C10_R_DEVELOPMENT_ROUND_REPORT.md",
  "stage_b_subject": "docs(w04-c10): publish business acceptance readiness proof",
  "walkthroughs": [
    {
      "id": "W01",
      "name": "DecisionPacket -> InvestigationCase"
    },
    {
      "id": "W02",
      "name": "Investigation Plan"
    },
    {
      "id": "W03",
      "name": "Authorized Evidence Navigation"
    },
    {
      "id": "W04",
      "name": "Findings / Conflicts / Unknowns"
    },
    {
      "id": "W05",
      "name": "Human Investigation Review"
    },
    {
      "id": "W06",
      "name": "Investigation Summary"
    },
    {
      "id": "W07",
      "name": "Protected Replay"
    },
    {
      "id": "W08",
      "name": "Regression / Protection"
    }
  ]
}
```

Stop on context drift, repository/contract failure, unresolved R2 evidence, any failed local/native lifecycle gate, protected-path need or ambiguity requiring semantic/product authority. Source/runtime repair, C10 acceptance/closeout and W04 closeout require separate authorization.
