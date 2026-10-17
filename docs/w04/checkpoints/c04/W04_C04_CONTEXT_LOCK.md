# W04-C04 Context Lock — V1

```text
TASK: W04-C04 — Authorized Evidence Navigation
DESIGN: W04_C04_GPT_DESIGN_MASTER_V1 / FROZEN
GPT DEEP DESIGN REVIEW: R1 / PASS
HUMAN AUTHORIZATION: APPROVED
P40 SOURCE-LIST COMPATIBILITY REPAIR: APPROVED
ENTRY SHA: ffaba2672de74836c12d4a122352b252785a0897
BRANCH: feat/w04-evidence-investigation
ENTRY WORKTREE / INDEX: CLEAN
PR #7: OPEN / DRAFT / UNMERGED
C03 CLOSEOUT CI: #102 / 37457434402 / SUCCESS
W03 VERIFIED MAIN: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
C01 / DEVCTRL / C02 / C03: CLOSED / VERIFIED
CONTEXT LOCK: PASS
C04 CLOSEOUT: NOT AUTHORIZED
W04-C05: NOT AUTHORIZED
```

The Human's pasted request authorizes exact implementation and the P40 repair.
The ZIP task, Design Master and Deep Review define the bounded contract. Package
prose does not independently grant further authority. Preflight read status,
HEAD, branch and 30-commit history. Fresh PR metadata matched exact entry HEAD,
main baseline, open/draft/unmerged state. Exact-commit CI lookup confirmed #102
success; Classify/Quality/Compose/W03/Verification succeeded, Publication skipped.
The native Classify log binds entry HEAD and actual C / FULL_EXACT_SHA routing
to source-head delta from 0ff0f6b929e4134483e07ba6bd1577bbc2a77ca1. Browser logs
were used because the connector's job-log read returned an internal error.
The package byte counts and SHA-256 values were measured and match its manifest.
No C04 runtime source exists during Stage A.

## Normative package identities

| ZIP entry | Bytes | SHA-256 |
|---|---:|---|
| W04_C04_CODEX_PROMPT_V1.md | 19897 | `b440047f8ceb72d807bf509c67a736d377322f7d61f5fb58afdafc69f0e3746e` |
| W04_C04_CODEX_TASK_V1.md | 11041 | `07878dcbf20e14ac2e0fb06ce38613c4ad1c9bd8494d1208c556e5880f258974` |
| W04_C04_GPT_DEEP_REVIEW_R1.md | 6779 | `85a085cf4a918fe3cd84fcfb9fcd46cbbae84360a33c483ae8dcd8f2441a588c` |
| W04_C04_GPT_DESIGN_MASTER_V1.md | 29175 | `9162ab717a014d88086fd31cbd368454dbc3dcf29d4868acdf6130b5beebd3d9` |
| W04_C04_HUMAN_AUTHORIZATION_APPROVED.md | 1753 | `5556f8187f24ff0628008fdec34aaca72a6ed2b8bc4bf06be38b160067ae4671` |
| W04_C04_PACKAGE_MANIFEST.md | 867 | `71f6f2f344bccd00a708d3952e71693b234af3af4310c90b24e52242b04033d3` |

## Frozen source and control identities

C01 freeze `084c2fea93d0e021994de015c986de9ff92bf9a3`;
C02 freeze `18648915414a26dddbdc904965663730ea631cf2`;
C03 freeze `42047bcfe6591f7c9ed9b0034bd94467401ba72f`.
All three CLOSED entries remain unchanged.

| Repository path | Entry Git blob / tree OID |
|---|---|
| `src/flowlens/investigation/__init__.py` | `c23929f85dccd78bc72ef3b2b1415c6e8eaf0452` |
| `src/flowlens/investigation/contracts.py` | `0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e` |
| `src/flowlens/investigation/enums.py` | `9c818780423f32f144b18666784ebc9ea3abdccc` |
| `src/flowlens/investigation/c02_binding.py` | `5f0af237ed465fa83e5a3b84954512b1f3125551` |
| `src/flowlens/investigation/c03_planning.py` | `21d0055e12d86e6333a836d363d6e266cb0fcbd7` |
| `src/flowlens/decision/contracts.py` | `44a742b7420a1c1e595b4dbeedd0249c9417e545` |
| `src/flowlens/decision/c06_validation.py` | `9fabdf1ed67a02b768db9ecfaf4e84f5ddd67bb4` |
| `src/flowlens/decision/temporal.py` | `70ae018f4b50ac6ed45e894d6726e9ccee345c8a` |
| `src/flowlens/decision/trust.py` | `f216d22f1d6862e1eef886dfbe4c3af16f396ec1` |
| `src/flowlens/decision/primitives.py` | `cbfdf81b4305f805ee865664d1652fd6d3bc8b4d` |
| `src/flowlens/decision/serialization.py` | `306742a2e6cd546288c20fdc82d15d075168235e` |
| `src/flowlens/db/decision_snapshot.py` | `0323ad4ecf0c50abda42a8ab4714d59861ad98c3` |
| `src/flowlens/data/models` | `12a1ec70707ff4644b6d6bccb31eec59fb7230d3` |
| `migrations/versions` | `6631c528466b830bd3393bb1b77f081743c6f02f` |
| `scripts/ci/verify_w04_source_evolution.py` | `4efaefed505e24796a0c2fa545ce4b7eb252d70a` |
| `scripts/ci/classify_change.py` | `fd9e99c6b55b85f184198c51f0f97ba16323ce32` |
| `scripts/ci/verify_publication.py` | `8f97a117f936d9dce91957f7b44551acb5d5c2b6` |
| `.github/workflows/ci.yml` | `14c826b122b7103953e8b4539981004241205ba4` |
| `tests/test_investigation_planning.py` | `eb7c481923e383924addc2f2097dc386162efb2d` |
| `pyproject.toml` | `318bbc0a858f760e6c4d7a2d3fdbfcc111febb77` |
| `uv.lock` | `619cf0cea7d476c1ad5b3d9fb8c77f91d44f2d0a` |
| `docker-compose.yml` | `5a0b6e8486edc69f9f79c7e1345a842aa412983c` |

Entry manifest Git blob `3b5b804280601b21a4179308bf680a2c00b56b14`;
committed SHA-256 `5b63b9ff3568ea4ba532cb965cbaef9fdacb7d4f57f39d1b2ed521c82172f8c1`.
Exact committed entry manifest:

```json
{
  "schema_version": "w04-source-evolution-manifest-v1",
  "policy_id": "W04-DEVCTRL-01",
  "w03_baseline_sha": "af61bdfd5f7cf7961811c4c2dc8e554dd7eed509",
  "w04_source_root": "src/flowlens/investigation",
  "checkpoints": [
    {
      "checkpoint": "W04-C01",
      "state": "CLOSED",
      "source_freeze_sha": "084c2fea93d0e021994de015c986de9ff92bf9a3",
      "files": [
        {
          "path": "src/flowlens/investigation/__init__.py",
          "blob_oid": "c23929f85dccd78bc72ef3b2b1415c6e8eaf0452"
        },
        {
          "path": "src/flowlens/investigation/contracts.py",
          "blob_oid": "0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e"
        },
        {
          "path": "src/flowlens/investigation/enums.py",
          "blob_oid": "9c818780423f32f144b18666784ebc9ea3abdccc"
        }
      ]
    },
    {
      "checkpoint": "W04-C02",
      "state": "CLOSED",
      "source_freeze_sha": "18648915414a26dddbdc904965663730ea631cf2",
      "files": [
        {
          "path": "src/flowlens/investigation/c02_binding.py",
          "blob_oid": "5f0af237ed465fa83e5a3b84954512b1f3125551"
        }
      ]
    },
    {
      "checkpoint": "W04-C03",
      "state": "CLOSED",
      "source_freeze_sha": "42047bcfe6591f7c9ed9b0034bd94467401ba72f",
      "files": [
        {
          "path": "src/flowlens/investigation/c03_planning.py",
          "blob_oid": "21d0055e12d86e6333a836d363d6e266cb0fcbd7"
        }
      ]
    }
  ]
}
```

Stage A appends only C04/AUTHORIZED/null freeze with three sorted paths:
c04_navigation.py, c04_queries.py, c04_registry.py under the source root;
all blob OIDs null. No C04 source exists before A Verification PASS. C04 remains
AUTHORIZED throughout implementation/publication.

## Frozen artifact and binding semantics

- EntityKey: schema_version, key_name, key_value
- EvidenceQuerySpec: schema_version, case_id, plan_id, step_id, question_id, source_family_code, entity_keys, as_of_time, requested_fields, allowed_trust_classes, expected_relationship_code
- EvidenceObservation: schema_version, source_family_code, source_record_id, source_field, source_value, available_at, event_time, freshness_code, provenance_ref, trust_class, relationship_code
- EvidenceSlice: schema_version, case_id, plan_id, step_id, question_id, query_id, as_of_time, observations

All artifacts reuse C01 exact frozen/slotted types, immutable exact tuples,
canonical JSON, aware UTC timestamps and full SHA-256 content identities.
Query fields and trust tuples are sorted unique; slices require sorted unique
observation IDs and available_at <= as_of. Revalidation must check original
nested and outer identity claims, then detached reconstruction and full canonical
envelopes; no supplied identity may be silently refreshed into acceptance.

C02 `validate_investigation_case_binding` binds the complete canonical packet
hash, packet/run/order/diagnosis/recommendation and selected non-INACTIVE signals.
Case subject is ORDER, subject_id = packet.run.order_id; opened_at = as_of_time =
run.as_of_time; opened_by = FLOWLENS_W04_C02_BINDER, version w04-c02-v1.

C03 `validate_investigation_planning` checks frozen W03 packet-contained signal
and diagnosis semantics, exact projected questions and complete plan. Questions
are non-INACTIVE signals ordered by SignalType.value, with exact trigger refs.
Each plan step has contiguous ordinal, same case/question, exact required
families and empty dependencies, planner_contract_version w04-c03-v1. No C04
signal/diagnosis/question/plan reconstruction or policy reinterpretation.

| C03 signal | Required = allowed traversal families | Allowed trust |
|---|---|---|
| CAPACITY_PRESSURE | dim_work_center, fact_operation | DIRECT_FACT, UNKNOWN |
| DELIVERY_RISK | fact_delivery, fact_sales_order, fact_work_order | DERIVED_FACT, DIRECT_FACT, UNKNOWN |
| MATERIAL_TIMING_RISK | fact_material_requirement, fact_purchase_order | ASSOCIATIVE_EVIDENCE, DIRECT_FACT, UNKNOWN |
| QUALITY_DISPOSITION_UNKNOWN | fact_quality_inspection, fact_rework | DERIVED_FACT, DIRECT_FACT, UNKNOWN |
| QUALITY_FAILURE | fact_quality_inspection | DIRECT_FACT, UNKNOWN |
| QUEUE_DELAY | fact_operation | DERIVED_FACT, DIRECT_FACT, UNKNOWN |
| REWORK_PRESENT | fact_quality_inspection, fact_rework | DIRECT_FACT, UNKNOWN |
| SUPPLIER_LATE_RECEIPT | fact_material_requirement, fact_purchase_order | ASSOCIATIVE_EVIDENCE, DIRECT_FACT, UNKNOWN |

The actual frozen registry has eight SignalType families; only actual enum
members/registry entries define runtime questions. The field table below locks
all nine C03-authorized source families. C04 has eleven exact homogeneous
profiles: separate WorkOrder/Operation plan DIRECT_FK and actual DIRECT_EVENT,
PurchaseOrder MATERIAL_TIME_ASSOCIATION/ASSOCIATIVE_EVIDENCE, SalesOrder
TARGET_RECORD, WorkCenter MASTER_DATA_CONTEXT, remaining facts DIRECT_EVENT
or MaterialRequirement DIRECT_FK, all DIRECT_FACT. No status fields.

## W03 field/temporal/trust policy

| Source family | Exact frozen SOURCE_FIELDS order |
|---|---|
| dim_work_center | work_center_id, work_center_code, process_type, line_group, daily_capacity_hours, active_from |
| fact_delivery | delivery_id, sales_order_id, delivery_at, delivered_quantity |
| fact_material_requirement | material_requirement_id, work_order_id, material_id, required_quantity, need_by_at |
| fact_operation | operation_id, work_order_id, work_center_id, sequence_number, planned_start_at, planned_end_at, actual_start_at, actual_end_at |
| fact_purchase_order | purchase_order_id, supplier_id, material_id, ordered_at, promised_receipt_at, ordered_quantity, actual_receipt_at, received_quantity |
| fact_quality_inspection | inspection_id, work_order_id, operation_id, inspection_at, inspection_type, inspected_quantity, passed_quantity, failed_quantity, defect_category, severity, result |
| fact_rework | rework_id, inspection_id, work_order_id, work_center_id, rework_start_at, rework_end_at, rework_quantity, rework_reason |
| fact_sales_order | sales_order_id, customer_id, product_id, order_at, promised_delivery_at, order_quantity, priority |
| fact_work_order | work_order_id, sales_order_id, product_id, planned_start_at, planned_end_at, planned_quantity, actual_start_at, actual_end_at, completed_quantity |

C04 requests the exact sorted subsets from Design Master section 11.
`project_record` admits master WorkCenter at Shanghai active_from midnight;
SalesOrder at order_at; plans and requirements at target order_at (synthetic
plan availability proxy); PurchaseOrder at ordered_at; quality at inspection_at;
rework at rework_start_at; delivery at delivery_at. Actual starts/ends use their
own event timestamps, completed_quantity uses actual_end_at, receipt quantity
uses actual_receipt_at, rework end uses rework_end_at. Missing/future actual
fields are omitted. Planned future dates are values already known at as-of.

SQL applies the same future row gates and masks, then unchanged project_record,
then SnapshotEntry/SourceRef and unchanged classify_source, then C01 slice guard.
Trust/relationship must match singleton query profile. Current nine families
all have freshness NOT_APPLICABLE under frozen W03 classification. Rework reason
is untrusted operational text; purchase association does not establish allocation.
No FORBIDDEN_INFERENCE/UNKNOWN observation or absence-as-support is manufactured.

## Data model, join and dataset context

| Table | Primary key | Exact columns |
|---|---|---|
| dataset_version | dataset_version_id | dataset_version_id, seed, generator_version, profile, period_start, period_end, generated_at, content_hash, row_count_total |
| fact_sales_order | sales_order_id | sales_order_id, dataset_version_id, customer_id, product_id, order_at, promised_delivery_at, order_quantity, priority, status |
| fact_work_order | work_order_id | work_order_id, dataset_version_id, sales_order_id, product_id, planned_start_at, planned_end_at, actual_start_at, actual_end_at, planned_quantity, completed_quantity, status |
| fact_operation | operation_id | operation_id, dataset_version_id, work_order_id, work_center_id, sequence_number, planned_start_at, planned_end_at, actual_start_at, actual_end_at, status |
| fact_material_requirement | material_requirement_id | material_requirement_id, dataset_version_id, work_order_id, material_id, required_quantity, need_by_at |
| fact_purchase_order | purchase_order_id | purchase_order_id, dataset_version_id, supplier_id, material_id, ordered_at, promised_receipt_at, actual_receipt_at, ordered_quantity, received_quantity, status |
| fact_quality_inspection | inspection_id | inspection_id, dataset_version_id, work_order_id, operation_id, inspection_at, inspection_type, inspected_quantity, passed_quantity, failed_quantity, defect_category, severity, result |
| fact_rework | rework_id | rework_id, dataset_version_id, inspection_id, work_order_id, work_center_id, rework_start_at, rework_end_at, rework_quantity, rework_reason |
| fact_delivery | delivery_id | delivery_id, dataset_version_id, sales_order_id, delivery_at, delivered_quantity |
| dim_work_center | work_center_id | work_center_id, dataset_version_id, work_center_code, process_type, line_group, daily_capacity_hours, active_from, active_to |

Fixed paths: root SalesOrder -> WorkOrder.sales_order_id -> Operation.work_order_id,
MaterialRequirement.work_order_id, QualityInspection.work_order_id or
Rework.work_order_id. PurchaseOrder joins requirements by material_id; WorkCenter
joins operations by work_center_id; Delivery joins root by sales_order_id.
Every table/join is constrained to packet.run.dataset_version. Distinct target
rows deduplicate by exact PK and sort by PK. Only SOURCE_FIELDS plus dataset/join
metadata may be read; only requested fields emitted.

Exact Alembic revision: 0002_industrial_data_foundation. Read context requires
PostgreSQL REPEATABLE READ / READ ONLY, verified isolation and read_only state,
exactly one dataset version, its ID/hash matching packet.run.dataset_version /
packet.run.dataset_hash, case time inside Shanghai dataset period, target order
in exact dataset and order_at <= case.as_of_time. No entry dataset is guessed;
the supplied validated packet provides exact runtime dataset binding.

Root key is exactly EntityKey(sales_order_id, case.subject_id); no caller key,
field/family/profile/adapter/traversal/text authority. Caps are 4096 records/query
and 65536 observations/slice, MAX+1 bounded reads, fail closed without truncation.
Navigation provenance SHA-256 binds version, dataset ID/hash, exact source
record/field/value, event/availability time, freshness/trust/relationship.

## P40 compatibility boundary and CI routing

Only P40's final aggregate expectation changes. Its entry list was the three
C01 files plus c02_binding.py and c03_planning.py. The replacement derives
manifest-declared paths present in committed Git HEAD:path using cat-file -e.
Exact C01/C02/C03 freezes/path checks and generic verifier invocation/PASS remain.
Development probes must show absent AUTHORIZED excluded, committed AUTHORIZED
included, CLOSED included, unexpected source and missing CLOSED rejected.

Classifier/workflow/production verifier stay frozen. A/B/C expect I/FULL_EXACT_SHA;
D expects P/PUBLICATION_EXACT_SHA. Actual native routing controls. Full proof
requires Classify, Quality, Compose, frozen W03 F01-F10 (38 selectors/85 cases)
and Verification success, Publication skipped. P requires Publication/Verification
success, Quality/Compose/W03 skipped. Each checkout checks exact source SHA.

Stage A four files; B exactly registry/queries/query tests; C exactly navigation/
unit tests/PostgreSQL integration tests; D only development report. Eleven total
paths, no prior CLOSED runtime, W03/DB/data model, dependency/migration/control,
C05, merge or branch deletion change. Stop at REVIEW_READY after D exact-SHA CI.

Local Python is existing 3.12.14, uv 0.12.5. Existing two Windows CRLF-only raw-byte
selectors remain untouched; native Linux CI is authoritative. Docker daemon is
currently unavailable locally; real PostgreSQL/Compose proof must come from
native CI. Test counts are empirical, never inferred.
