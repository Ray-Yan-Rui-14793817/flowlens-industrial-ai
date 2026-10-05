# W04-C01 Context Lock — V2

```text
TASK: W04-C01
TASK VERSION: V2
AUTHORIZATION: AUTHORIZED (repository record read back before code mutation)
BASE SHA: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
ENTRY SHA: af61bdfd5f7cf7961811c4c2dc8e554dd7eed509
ENTRY BRANCH: main
IMPLEMENTATION BRANCH: feat/w04-evidence-investigation
ENTRY WORKTREE: CLEAN
POST-ANCHOR COMMITS: NONE
CONTEXT LOCK: PASS
W04-C02+: NOT AUTHORIZED
```

The Human-issued normative task is `W04_C01_CODEX_DEVELOPMENT_TASK_V2.md`
from `FlowLens_W04_C01_CODEX_HANDOFF_V2.zip`, SHA-256
`de4b95e794201050e07e552140dedc247f45196edc113ee87c5607d062fd15c4`.
All three V2 manifest digests matched their archive entries.

| Convention | Locked repository source |
|---|---|
| W03-C01 contracts | `src/flowlens/decision/contracts.py` |
| Immutable model framework | `src/flowlens/decision/primitives.py`: frozen, slots, keyword-only dataclasses; `Validated` |
| Canonical serializer and SHA-256 | `src/flowlens/decision/serialization.py`: `canonical_primitive`, `canonical_json_bytes`, `sha256_hex` |
| Artifact identity convention | `docs/w03/checkpoints/c01/W03_C01_IDENTITY_PROVENANCE_SERIALIZATION.md`; `derive_artifact_id` in W03 serialization |
| Existing local identity extension | `src/flowlens/decision/context.py` |
| Canonical trust type | `src/flowlens/decision/enums.py`: `TrustLevel` |
| Scalar representation | `src/flowlens/decision/primitives.py`: `ScalarValue` |
| Datetime validation/normalization | W03 primitives' aware-datetime validation; serialization's UTC, six fractional digits, `Z` |
| Focused tests and fresh process convention | `tests/test_decision_contracts.py`, `tests/test_decision_serialization.py` |
| Ruff/strict mypy/pytest | `pyproject.toml` |
| Classifier | `scripts/ci/classify_change.py` |
| Frozen W03 semantic gate | `scripts/ci/run_w03_ai_loop_gate.py`, `docs/w03/checkpoints/c09/specs/c09_gate_manifest.json` |
| Repository Verification gate / Compose smoke | `.github/workflows/ci.yml`; `docker-compose.yml` |

W03's artifact-kind registry is closed. W04 will extend only its own kinds and
prefixes, preserving W03's `{artifact_kind, schema_version, identity}` envelope,
full digest, public hash/serializer helpers and prefix-plus-digest format. W03
code and registry remain frozen. Set-like tuples follow W03's sorted-and-unique
validation; ordered plan steps retain their semantic order. Trust names retain
the actual W03 enum values, including `FORBIDDEN_INFERENCE`.

Each declared model has schema `<artifact-kind>.v1` and derives its full
`content_hash` from that envelope; `artifact_id` is its W04 prefix plus the same
64-character digest. Prefixes are frozen in the new contract module. Both
supporting record types without required external refs (`EntityKey` and
`SummarySectionRecord`) use the same identity mechanism for a uniform round trip.
Identity fields are constructor-derived; parsing validates every supplied ID
and hash. Derived fields are recursively excluded from digest input.

Code-like keys use identifier-style ASCII values of at most 128 characters;
this is a structural bound, not a business registry. Caller types are validated
before canonicalization; tuple and nested model subclasses that could introduce
mutable public state are rejected. Scalar wire text follows W03's existing
Decimal/date/datetime normalization. Round trips preserve canonical bytes and
identity; recovering those source scalars' original Python subtype is outside
the untagged W03 wire convention. Business timestamp fields are parsed as aware
datetimes. Summary sections retain their declared order; grounding-ref tuples
may be empty because C01 freezes no prose grounding grammar or cardinality.

Planned code surface: `src/flowlens/investigation/{contracts,enums,__init__}.py`.
Planned focused harness: `tests/test_investigation_contracts.py`.
Allowed documentation: this checkpoint's authorization, normative task,
context lock and development round report only.

No source data, DB, HGT, network/model/tool capability or operational mutation
is needed by the contract layer. Development Git/CI verification is separate
from runtime artifact capability. No C02+ behavior is authorized.

The existing classifier treats W04 checkpoint documentation as `UNKNOWN`, so
the expected aggregate proof is `UNKNOWN / FULL_EXACT_SHA`; the actual event
classification must be reported. A feature push alone does not trigger this
workflow; a draft PR to `main` is needed for repository-native exact-SHA CI.
