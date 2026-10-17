# W04-C02 Context Lock — V2

```text
TASK: W04-C02
TASK VERSION: V2
CLARIFICATION: W04-C02-CLARIFICATION-01
HUMAN AUTHORIZATION: APPROVED
REPAIR AUTHORIZATION: APPROVED
ENTRY SHA: ae88a9b1be74bc379140b59a15d6dd9cb714912f
W03 VERIFIED MAIN: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
BRANCH: feat/w04-evidence-investigation
PR #7: OPEN / DRAFT / UNMERGED
DEVCTRL CLOSEOUT CI: #93 / 37321990473 / SUCCESS
ENTRY WORKTREE: CLEAN
W04-C01: CLOSED
W04-DEVCTRL-01: CLOSED
CONTEXT LOCK: PASS
C02 CLOSEOUT: NOT AUTHORIZED
W04-C03: NOT AUTHORIZED
```

Entry HEAD, branch, status and 30-commit history were read before mutation.
GitHub PR metadata matched the exact entry SHA and verified open/draft/unmerged
status at https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/pull/7.
The exact entry SHA has successful native CI #93 / 37321990473. The unchanged
generic source verifier passed at entry with only the three C01 additions.

Normative task V2 SHA-256:
`b5e23dffbbf044f87919efbb72fa95f6d5cab9279740096b83a3ce85d564e148`.
Unchanged V1 task SHA-256:
`51ecd2bf9db109b2451d812946450e6751d2e030478b71375278d22c8a5289fe`.
The Human's pasted V2 request supplies authorization; attached task material
defines the authorized contract. Repository invariants remain authoritative
within that scope.

## Source authorization and frozen C01

Manifest: `docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json`, schema
`w04-source-evolution-manifest-v1`, policy `W04-DEVCTRL-01`, W03 baseline
`af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`, root
`src/flowlens/investigation`.

The C01 CLOSED entry is preserved byte-for-byte in substance, with source freeze
`084c2fea93d0e021994de015c986de9ff92bf9a3` and exact Git blobs:

| C01 path | Blob OID |
|---|---|
| `src/flowlens/investigation/__init__.py` | `c23929f85dccd78bc72ef3b2b1415c6e8eaf0452` |
| `src/flowlens/investigation/contracts.py` | `0f66bd9a0b2f063b318bd6b9dcc47d63b9c83e7e` |
| `src/flowlens/investigation/enums.py` | `9c818780423f32f144b18666784ebc9ea3abdccc` |

Stage A appends only W04-C02 / AUTHORIZED / source_freeze_sha null, containing
`src/flowlens/investigation/c02_binding.py` / blob_oid null. This is exactly one
new runtime path. It must remain absent until Stage A Verification PASS.

CL-01 changes only the final normative D01 assertion to compare the first
parsed checkpoint with the exact bootstrap C01 checkpoint. Existing constants,
strict parsing, append-only history, state transition and immutable-source
tests are retained. The verifier itself remains unchanged.

## Frozen packet and case boundaries

`src/flowlens/decision/contracts.py` freezes DecisionPacket fields:
`packet_id`, `schema_version`, `run`, `snapshot`, `evidence`, `signals`,
`diagnosis`, `candidates`, `simulations`, `recommendation`, `uncertainties`,
`limitations`, `provenance`.

`src/flowlens/investigation/contracts.py` freezes InvestigationCase init fields:
`schema_version` (investigation-case.v1), `source_decision_packet_id`,
`source_decision_packet_hash`, `decision_run_id`, `subject_type`, `subject_id`,
`as_of_time`, `opened_at`, `opened_by`, `risk_families`, `source_signal_ids`,
`source_diagnosis_id`, `source_recommendation_id`. Derived fields are
`content_hash` and `artifact_id`. C01 owns structural validation, sorted unique
immutable tuples and its artifact identity envelope.

`flowlens.decision.c06_validation.validate_c05_packet` revalidates the frozen
nested packet structures/identities and exact C05 producer, version, input IDs,
source refs and contract versions. C02 requires exact DecisionPacket type and
calls this unchanged validator before its future guard. Frozen validation
failures map to the stable C02_INVALID_DECISION_PACKET code, without publishing
W03 exception text. No diagnosis or recommendation policy is rebuilt.

CL-02 canonical dispositions are NO_ACTION, NO_RECOMMENDATION,
INVESTIGATION_ONLY and DEFER_TO_HUMAN. CANDIDATE_RECOMMENDED remains reserved and
is rejected by frozen W03 validation.

`flowlens.decision.serialization.canonical_json_bytes` encodes all dataclass
fields with sorted JSON keys, compact UTF-8 and UTC aware timestamps with six
fractional digits and Z. Decimal normalization and W03 identity conventions
remain unchanged. source_decision_packet_hash is lowercase SHA-256 of the
complete canonical packet bytes, including its IDs and provenance.

SignalType values are SUPPLIER_LATE_RECEIPT, MATERIAL_TIMING_RISK,
QUALITY_FAILURE, REWORK_PRESENT, QUALITY_DISPOSITION_UNKNOWN, QUEUE_DELAY,
CAPACITY_PRESSURE and DELIVERY_RISK. SignalState values are ACTIVE, INACTIVE,
UNKNOWN. ACTIVE and UNKNOWN supply sorted unique signal family values and IDs;
INACTIVE is excluded. Empty projection tuples remain valid.

The case copies packet/run/order/diagnosis/recommendation identities exactly,
uses subject_type ORDER, opened_by FLOWLENS_W04_C02_BINDER, and sets both case
timestamps to run.as_of_time. The binding policy version is w04-c02-v1.

CL-03: snapshot entry/source-ref available_at and Evidence.available_at future
violations are rejected during frozen W03 validation as INVALID. After it
passes, C02 checks snapshot entry and source-ref observed_at/available_at,
Evidence observed_at/available_at and packet provenance source-ref
observed_at/available_at against run.as_of_time. None observed_at is valid;
surviving future values produce C02_FUTURE_INFORMATION. Modeled counterfactual
futures are not observational truth.

Binding validation requires exact InvestigationCase type, detached C01
reconstruction without mutating supplied fields/derived identity, and comparison
of the complete canonical original, revalidated and expected case envelopes.
Mismatch maps to C02_CASE_BINDING_MISMATCH. Directly invoking supplied case
__post_init__ would overwrite identity claims and is unsuitable.

## Proof routing and stage boundaries

Classifier: `scripts/ci/classify_change.py`; workflow:
`.github/workflows/ci.yml`; verifier:
`scripts/ci/verify_w04_source_evolution.py`; frozen W03 gate:
`scripts/ci/run_w03_ai_loop_gate.py` and
`docs/w03/checkpoints/c09/specs/c09_gate_manifest.json`.

The unchanged classifier selects I / FULL_EXACT_SHA for Stage A: the three
control documents classify C but the narrowly repaired generic test classifies
I. V2's expected C is advisory; actual classification must be recorded. Stage B
also selects I / FULL_EXACT_SHA. Stage C's report-only synchronize delta selects
P / PUBLICATION_EXACT_SHA. No classifier/workflow change is needed or authorized.

Stage A has exactly four paths (manifest, authorization, this context lock,
D01 test). Pending manifest strict parsing and transition preview do not claim
committed exact-HEAD proof. At its separate commit, run the unchanged verifier
and affected C09 source-governance selector; require native exact-SHA Quality,
Compose, frozen W03 F01–F10 (38 selectors / 85 cases) and Verification PASS
before any C02 source creation.

Stage B has exactly the new binder and B01–B36 harness. Run C02/C01/DEVCTRL/W03
focused regressions, complete non-integration/integration, Ruff, strict mypy,
dependency lock and full exact-SHA native CI. Stage C has only the development
report and requires native exact-SHA publication proof. No amend after CI
evidence, force push, main write, closeout or checkpoint auto-advance.

Runtime remains pure: no clock, randomness, filesystem, database, network,
subprocess, tools/model, HGT/evaluation, planning, evidence traversal or
operational mutation. Development Git/CI and test subprocesses are distinct
from runtime capabilities. Local Windows CRLF digest limitations and unavailable
Docker/database services must be reported; Linux native CI supplies authoritative
full proof. Dependencies and frozen controls remain untouched.
