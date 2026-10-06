# W04-C03 Context Lock — V1

```text
TASK: W04-C03 — Investigation Question Registry + Deterministic Planning
DESIGN: W04_C03_GPT_DESIGN_MASTER_V1
GPT DEEP DESIGN REVIEW: R1 / PASS
HUMAN IMPLEMENTATION AUTHORIZATION: APPROVED
ENTRY SHA: dd21e238e6047ed8181d8aaa3636eb4feca2763a
BRANCH: feat/w04-evidence-investigation
PR #7: OPEN / DRAFT / UNMERGED
C02 CLOSEOUT CI: #97 / 37401818390 / SUCCESS
ENTRY WORKTREE / INDEX: CLEAN
W03 VERIFIED MAIN: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
C01 / DEVCTRL / C02: CLOSED / VERIFIED
CONTEXT LOCK: PASS
C03 CLOSEOUT: NOT AUTHORIZED
W04-C04: NOT AUTHORIZED
```

The Human's pasted C03 request supplies authorization. The attached task and
Design Master define the exact authorized contract; attachment prose does not
independently grant additional authority. Preflight read HEAD, branch, status
and 30-commit history. Fresh PR metadata and exact-head CI #97 matched entry.
Classify selected C / FULL_EXACT_SHA; Classify, Quality, Compose, frozen W03 and
Verification succeeded; Publication skipped. The five handoff manifest byte
counts and SHA-256 declarations matched. Read-only independent compatibility
audits found no conflict with frozen C01/C02 or packet-contained W03 semantics.

| Normative handoff | SHA-256 |
|---|---|
| Task V1 | `9c3bae788bc14ad6090fa41c8b77ed6bdb3236c0fe4503834222a1362f8f22d9` |
| Design Master V1 | `9c3bed3cce430f26c37468828a775bf628af905ffee0519227ea3f59ecb51a44` |
| Deep Review R1 | `429ad5a2d65efdb425b279684e3b88945036ecaff09a65e45786f4f0df4f8d99` |
| Human authorization | `89b9b5db6d39fed8d71e3312f31cf86ff20dd83ff2f386b22345af65e8c3322d` |
| Prompt V1 | `eaaaf712ee23e54fa2643c969bc32f139fa0f47f9e04531c4251ea31cf001d8f` |

## Frozen source identities

C01 source freeze: `084c2fea93d0e021994de015c986de9ff92bf9a3`.
C02 source freeze: `18648915414a26dddbdc904965663730ea631cf2`.
Both CLOSED entries must remain exactly unchanged.

| Source | Entry Git blob OID |
|---|---|
| `investigation/__init__.py` | `c23929f85dccd78bc72ef3b2b1415c6e8eaf0452` |
| `investigation/contracts.py` | `0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e` |
| `investigation/enums.py` | `9c818780423f32f144b18666784ebc9ea3abdccc` |
| `investigation/c02_binding.py` | `5f0af237ed465fa83e5a3b84954512b1f3125551` |
| `decision/contracts.py` | `44a742b7420a1c1e595b4dbeedd0249c9417e545` |
| `decision/c06_validation.py` | `9fabdf1ed67a02b768db9ecfaf4e84f5ddd67bb4` |
| `decision/c03_policy.py` | `cda8d73e32afaaf201c2c4532b76b9f2636b9757` |
| `decision/diagnosis.py` | `e6c3c00a7b09f915fbed702eb12090f3aac2acaf` |
| `decision/enums.py` | `ed6facf95de4d05ef6c917f4122162c10c23a68c` |
| `decision/primitives.py` | `cbfdf81b4305f805ee865664d1652fd6d3bc8b4d` |
| `decision/serialization.py` | `306742a2e6cd546288c20fdc82d15d075168235e` |

All paths in this table are below `src/flowlens/`. Entry source manifest SHA-256
is `09136cc51ec27d5d5c26e03d83077b3a611e9e7462b3df4508e7421a6d374758`.
Its schema is `w04-source-evolution-manifest-v1`, policy `W04-DEVCTRL-01`, W03
baseline as above and source root `src/flowlens/investigation`. Stage A appends
only C03 / AUTHORIZED / null freeze, authorizing `c03_planning.py` / null blob.
The source and harness remain absent until Stage A exact-SHA Verification PASS.

## Frozen input and artifact envelopes

DecisionPacket fields remain `packet_id`, `schema_version`, `run`, `snapshot`,
`evidence`, `signals`, `diagnosis`, `candidates`, `simulations`, `recommendation`,
`uncertainties`, `limitations`, `provenance`.

InvestigationCase init fields remain `schema_version`,
`source_decision_packet_id`, `source_decision_packet_hash`, `decision_run_id`,
`subject_type`, `subject_id`, `as_of_time`, `opened_at`, `opened_by`,
`risk_families`, `source_signal_ids`, `source_diagnosis_id`,
`source_recommendation_id`. C02 projects only ACTIVE/UNKNOWN family and signal
IDs, binds the complete canonical packet hash and fixes ORDER subject, binder
identity and both timestamps to the run boundary. Thus C03 also requires the
packet for each retained signal's ACTIVE/UNKNOWN distinction.

Question init fields: `schema_version`, `case_id`, `question_code`,
`trigger_refs`, `required_evidence_families`, `allowed_traversal_families`,
`allowed_trust_classes`, `as_of_time`, `forbidden_inference_codes`.
Step init fields: `schema_version`, `case_id`, `question_id`, `ordinal`,
`depends_on_step_ids`, `expected_evidence_families`.
Plan init fields: `schema_version`, `case_id`, `as_of_time`,
`planner_contract_version`, `steps`.
Their respective fixed schema versions are investigation-question.v1,
investigation-step.v1 and investigation-plan.v1. C01 owns frozen/slotted models,
exact immutable tuples, sorted unique set fields, full canonical envelopes and
derived `content_hash` / `artifact_id`. Empty question/step tuples and empty
plans are legal. Validation must preserve original derived claims: revalidate
detached questions and each detached step before a detached plan, structurally
validate originals, then compare complete original/revalidated/expected bytes.

## Frozen W03 semantics and bounded registry

Validation order: exact DecisionPacket, unchanged `validate_c05_packet`, exact
InvestigationCase, unchanged C02 exact binding, packet-contained W03 semantic
consistency, then projection. No Signals/Diagnosis evidence rebuilding.
SignalState is ACTIVE / INACTIVE / UNKNOWN. SignalTypes are exactly the eight
rows below, in ascending `.value` order. ClaimType remains FACT_CLAIM,
DERIVED_CLAIM, ASSOCIATIVE_CLAIM, UNCERTAINTY_STATEMENT.

| SignalType | Policy entities (evidence = traversal) | ACTIVE claim | Trust values |
|---|---|---|---|
| CAPACITY_PRESSURE | dim_work_center, fact_operation | prohibited in v1 | DIRECT_FACT, UNKNOWN |
| DELIVERY_RISK | fact_delivery, fact_sales_order, fact_work_order | DERIVED_CLAIM | DERIVED_FACT, DIRECT_FACT, UNKNOWN |
| MATERIAL_TIMING_RISK | fact_material_requirement, fact_purchase_order | ASSOCIATIVE_CLAIM | ASSOCIATIVE_EVIDENCE, DIRECT_FACT, UNKNOWN |
| QUALITY_DISPOSITION_UNKNOWN | fact_quality_inspection, fact_rework | DERIVED_CLAIM | DERIVED_FACT, DIRECT_FACT, UNKNOWN |
| QUALITY_FAILURE | fact_quality_inspection | FACT_CLAIM | DIRECT_FACT, UNKNOWN |
| QUEUE_DELAY | fact_operation | DERIVED_CLAIM | DERIVED_FACT, DIRECT_FACT, UNKNOWN |
| REWORK_PRESENT | fact_quality_inspection, fact_rework | FACT_CLAIM | DIRECT_FACT, UNKNOWN |
| SUPPLIER_LATE_RECEIPT | fact_material_requirement, fact_purchase_order | ASSOCIATIVE_CLAIM | ASSOCIATIVE_EVIDENCE, DIRECT_FACT, UNKNOWN |

TrustLevel's fifth frozen value FORBIDDEN_INFERENCE is never allowed. Registry
is an immutable MappingProxyType with frozen policy members, exactly eight
keys. Forbidden codes are the sorted unique union of COMMON_LIMITATION_CODES
(C03_CLOSED_WORLD_OBSERVATION_ASSUMPTION, C03_INACTIVE_NOT_ALL_CLEAR,
C03_RULE_BASED_NOT_CAUSAL) and each frozen domain_limitation_codes tuple.

Exactly one ordered signal per family. DELIVERY_RISK ACTIVE takes problem-code
precedence (DELIVERY_COMMITMENT_WARNING), then any ACTIVE
(OBSERVED_DELIVERY_RISK_INDICATORS), else
INSUFFICIENT_EVIDENCE_FOR_RISK_ASSESSMENT. INACTIVE has no claim; ACTIVE/UNKNOWN
has exactly one `C03_<family>_<state>_V1` claim, frozen policy statement/type,
and evidence IDs/limitations equal to the signal. UNKNOWN uses
UNCERTAINTY_STATEMENT. Supporting signal IDs are all eight sorted IDs;
affected_path is exactly fact_sales_order/run.order_id; reason codes are the
sorted signal reason-code union plus C03_STRUCTURED_NOT_CAUSAL.

UNKNOWN requires exactly its C03_UNKNOWN_<family> uncertainty with
INSUFFICIENT_EVIDENCE, frozen unknown statement and signal refs. Partial ACTIVE
requires C03_PARTIAL_<family>, same status/refs and message: `A positive witness
exists, but some rule-relevant evidence is incomplete.` Other inherited
uncertainties are preserved without context reconstruction.

Selected questions are only non-INACTIVE, ordered by family value; codes are
`W04_C03_<family>_<state>`. Sorted trigger refs contain diagnosis ID, signal ID,
canonical claim code, and applicable UNKNOWN/PARTIAL uncertainty code. Questions
copy exact case identity/time and registry policy tuples. The planner first
requires complete canonical equality with this projection, then constructs one
step per question, ordinals 1..N, exact expected families, empty dependencies,
and fixed planner version `w04-c03-v1`. Public failures are only the five stable
C03 codes specified in the Design Master; inherited exception text is suppressed.

## Proof and completion boundary

Exactly six total paths, split 3 authorization / 2 implementation / 1 report.
Stage A must independently pass committed source verification, frozen controls
and native exact-SHA Verification before code creation. Stage B requires
P01-P40, frozen C01/C02, DEVCTRL, W03 core/F01-F10 (38 selectors / 85 cases),
full non-integration/integration, Ruff, strict mypy, lock, Compose and exact-SHA
Verification. Stage C is report-only with exact-SHA publication proof. Expected
routing is A C/FULL, B I/FULL, C P/PUBLICATION; record actual classifications.

No W03/C01/C02, CI/classifier/verifier, dependency or seventh-path change. No
clock/random/UUID, DB/SQL, filesystem/network/subprocess/tool/model authority,
HGT/evaluation execution, EvidenceQuerySpec construction, source adapters,
traversal or operational mutation in runtime. Development subprocess/Git/CI
proof is separate from runtime authority. The accepted Windows CRLF raw-byte
test failures and unavailable local Docker/database are recorded as local proof
limits; native Linux CI supplies required full proof. Stop at REVIEW_READY,
pending independent GPT review and Human acceptance; C03 closure/C04/merge are
not authorized.
