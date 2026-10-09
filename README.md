# FlowLens Industrial AI

Human-in-the-loop industrial decision and investigation intelligence for
evidence-grounded delivery-risk operations.

## What is FlowLens?

FlowLens helps a Production / Delivery Operations Manager move from an order's
delivery-risk signal to an evidence-grounded decision and a bounded investigation.
It preserves the original decision-time context, makes the basis of each finding
inspectable, and records Human review without changing operational systems.

The current engineering scenario is industry-inspired high-voltage electrical
equipment manufacturing, using deterministic synthetic data. The product direction
is **FlowLens v1.0**; **v1.0 is not yet released**. The repository contains the
verified W01/W02 foundations, merged W03 decision loop, and W04 investigation
capabilities through C06. W04 C07-C10 remain planned and unimplemented.

Product mode: **OFFLINE / SHADOW / HUMAN-IN-THE-LOOP / DETERMINISTIC-FIRST /
NO OPERATIONAL MUTATION**.

## The Problem

A delivery-risk alert alone does not tell an operations manager which historical
facts support it, which records disagree, or what remains unknown. Supplier timing,
material requirements, production queues, quality inspections and deliveries can
provide different kinds of evidence with different time and trust boundaries.

FlowLens makes those boundaries explicit. It supports investigation of the facts
available at the decision time, rather than promoting associations into causes or
turning a recommendation into an automatic operational action.

## Primary User

**Production / Delivery Operations Manager**, reviewing order-delivery risk and
deciding whether the available evidence is sufficient for Human-led follow-up.

## FlowLens v1.0 User Story

> When FlowLens identifies a delivery-risk decision, I want to open a bounded
> investigation that preserves the exact decision-time context, guides me through
> only authorized historical evidence, and distinguishes supported findings,
> contradictions, conflicts and uncertainty. I want to record my Human review
> state so I can request more evidence, defer the case, complete the review, or
> consider a separate Human-led follow-up, with a reproducible investigation and
> without FlowLens changing operational systems.

This is the intended product journey. Investigation summary, protected W04 replay
and end-to-end W04 business acceptance are still planned.

## How FlowLens Works

```text
Operational Facts (W02 foundation; bounded W03 reads)
  -> Decision-Time Snapshot
  -> Semantic Trust
  -> Risk Signals
  -> Diagnosis
  -> Bounded Counterfactual Simulation
  -> Deterministic Recommendation
  -> DecisionPacket                              [W03: IMPLEMENTED / VERIFIED]
  -> InvestigationCase                           [W04-C02: IMPLEMENTED / VERIFIED]
  -> Deterministic Investigation Plan             [W04-C03: IMPLEMENTED / VERIFIED]
  -> Authorized Evidence Navigation               [W04-C04: IMPLEMENTED / VERIFIED]
  -> Findings / Conflicts / Uncertainty            [W04-C05: IMPLEMENTED / VERIFIED]
  -> Human Investigation Review                   [W04-C06: IMPLEMENTED / VERIFIED]
  -> Investigation Summary                        [W04-C07: PLANNED / NOT IMPLEMENTED]
  -> Protected Investigation Replay                [W04-C08: PLANNED / NOT IMPLEMENTED]
  -> W04 Regression Hardening                      [W04-C09: PLANNED / NOT IMPLEMENTED]
  -> W04 Business Acceptance                       [W04-C10: PLANNED / NOT IMPLEMENTED]
```

W03 already provides bounded explanation of frozen DecisionPackets, Human decision
recording, and protected offline evaluation/deterministic decision replay. These
are separate from the unfinished W04 investigation summary and investigation replay.

## Current Capabilities

| Layer | Verified capabilities | Status |
|---|---|---|
| W01 engineering foundation | Python 3.12, uv, FastAPI, PostgreSQL 17, pgvector infrastructure, Docker Compose, Alembic, worker placeholder, local health checks and test-database safety | CLOSED / VERIFIED |
| W02 industrial data foundation | 16 canonical manufacturing tables, deterministic synthetic data, test/ci/demo profiles, validation, quality reports, scenario foundation, protected HGT isolation and CI | COMPLETE / CLOSED / VERIFIED; independent review passed; Product-Owner acceptance ACCEPTED WITH DOCUMENTED LIMITATIONS |
| W03 order-delivery-risk decision loop | Decision-Time State, semantic trust, signals, diagnosis, bounded counterfactual stress probes, deterministic recommendation, DecisionPacket, bounded explanation, Human decision, offline evaluation and deterministic replay | MERGED / CLOSED / VERIFIED |
| W04-C01 | Immutable investigation contracts, identities and closed vocabularies | CLOSED / VERIFIED |
| W04-C02 | Exact DecisionPacket-to-InvestigationCase binding | CLOSED / VERIFIED |
| W04-C03 | Deterministic investigation questions and planning | CLOSED / VERIFIED |
| W04-C04 | Closed-registry, read-only historical evidence navigation | CLOSED / VERIFIED |
| W04-C05 | Supported/contradicted/unresolved/unknown findings, explicit conflicts and uncertainty | CLOSED / VERIFIED |
| W04-C06 | Human investigation review events and bounded append-only audit journal | CLOSED / VERIFIED |

W03 Human decision outcomes are `ACCEPT`, `REJECT` and `DEFER`. W04 Human
investigation outcomes are `SUPPORTED_FINDING_RECORDED`, `NO_SUPPORTED_FINDING`,
`MORE_EVIDENCE_REQUIRED`, `DEFER` and `INVESTIGATION_REVIEW_COMPLETE`. These record
review state within their contracts; they do not execute a recommendation, establish
causal truth or authorize operational follow-up. Human notes are
`HUMAN_NOTE_NON_EVIDENCE` and cannot become evidence.

C01's structural contracts and enums do not make future C07/C08 execution available.
The implemented surfaces are Python modules and tested engineering workflows;
there is no completed product UI or production SaaS deployment.

## Evidence, Trust and Safety

- **Evidence before claims.** Each run preserves one immutable decision-time
  snapshot, exact source identities, provenance, freshness and explicit trust levels.
- **No future leakage.** Investigation remains bound to the original packet and
  its decision-time cutoff; later evidence cannot silently enter that context.
- **Unknown remains unknown.** Missing evidence is not negative proof. Stale,
  conflicting, unresolved and associative evidence remains explicit.
- **Association is not causality.** Conflicts are not silently resolved, and the
  system does not declare an unsupported automatic root cause. Counterfactual
  stress probes are bounded simulations, not proof of real intervention effects.
- **Authorized reads only.** W04 navigation uses a closed source/query registry,
  bounded traversal and read-only PostgreSQL transactions. It is not unrestricted
  database exploration or ERP/MES integration.
- **System recommendation, bounded model explanation.** The deterministic
  recommendation is frozen before explanation. The LLM has no recommendation or
  candidate authority, tool execution, database access, HGT access or operational
  write capability. W03 supports bounded explanation with deterministic fallback.
- **Protected evaluation.** Hidden Ground Truth (HGT) remains isolated from runtime
  and public artifacts. Synthetic scenario answers are not operational facts.
- **Human authority is final.** FlowLens records decisions and review events but
  does not alter production schedules, purchase orders, supplier assignments,
  quality release decisions, ERP records or MES records.

Synthetic, industry-inspired data verifies engineering contracts and scenario
behavior; it does not establish real-factory accuracy, predictive ML performance or
causal effectiveness. Frozen W1/W2 schema, hashes and scenario semantics remain
protected. Accepted limitations remain in the linked checkpoint evidence.

C06 audit persistence is API-enforced append-only storage under a pre-existing
trusted absolute filesystem root. It does not provide hardware WORM, protection
from a hostile filesystem administrator, external terminal-event deletion detection
without an external anchor, distributed consensus or cross-machine writer
coordination. Root permissions, retention and encryption are deployment concerns.
`actor_id` is a supplied audit field; C06 supplies no authentication/SSO/RBAC.
Crash-created lock/pending state requires explicit operator recovery; there is no
automatic stale-lock deletion or history-edit API.

## Architecture

| Plane | Existing implementation | Boundary |
|---|---|---|
| Local runtime | [FastAPI](src/flowlens/api/), [worker placeholder](src/flowlens/worker/), [database utilities](src/flowlens/db/), [settings](src/flowlens/config.py) | Development infrastructure and health checks |
| Industrial data | [Data modules](src/flowlens/data/), [Alembic migrations](migrations/) | Frozen schema, deterministic development/test data and validation |
| Decision | [Decision modules](src/flowlens/decision/) | Snapshot-first deterministic decision loop and bounded explanation |
| Investigation | [Investigation modules](src/flowlens/investigation/) | Exact packet binding, planning, authorized navigation, findings and Human review through C06 |
| Protected evaluation | [Evaluation modules](src/flowlens/evaluation/) | Offline W03 evaluation/replay; no runtime HGT |
| Development verification | [CI scripts](scripts/ci/), [tests](tests/), [native workflow](.github/workflows/ci.yml) | Exact-SHA proof and source/semantic safety enforcement |

The W04 implementation is in `c02_binding.py`, `c03_planning.py`,
`c04_registry.py`, `c04_queries.py`, `c04_navigation.py`, `c05_findings.py`,
`c06_human.py`, `c06_policy.py` and `c06_store.py` under
`src/flowlens/investigation/`. These modules extend the frozen W03 baseline.
Operational reads, local audit persistence and protected offline evaluation have
separate authority boundaries; none grants operational write-back.

## Current Development Status

**Verified baseline as of 2026-10-08 (Asia/Shanghai):**

- **W01/W02:** CLOSED / VERIFIED. W01 delivered infrastructure; W02 delivered the
  industrial data foundation. Their historical non-goals describe those phases,
  not a restriction on the W03 capabilities subsequently implemented.
- **W03:** MERGED / CLOSED / VERIFIED via [PR #6](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/pull/6).
  Main merge SHA: `af61bdfd5f7cf7961811c4c2dc8e554dd7eed509`.
  [Main post-merge CI #86 / 37261505402](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37261505402): PASS.
  W03 C10 independent review passed, Human acceptance is ACCEPTED and final
  closeout is effective. Historical pre-merge closeout proof:
  [CI #84 / 37254705531](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37254705531)
  at `a24e2e0587f11114edd5718eb10081797e303087`, followed by final synchronization
  and the separately Human-authorized PR #6 merge.
- **W04-C01 through C06:** CLOSED / VERIFIED in the
  [source-evolution manifest](docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json).
  C06 final closeout SHA: `145ac72626899dc30bcff437685b4698b8edacb4`.
  [Exact-SHA CI #115 / 37735563458](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/37735563458):
  COMPLETED / SUCCESS; Classify, Quality, Docker Compose, W03 AI loop and
  Verification passed; Publication was skipped under the full verification route.
- **W04 integration:** branch `feat/w04-evidence-investigation` is retained;
  [PR #7](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/pull/7)
  is OPEN / DRAFT / UNMERGED. W04 is not merged into main.
- **W04-C07 through C10:** PLANNED / NOT IMPLEMENTED. This documentation refresh
  does not authorize C07, merge PR #7 or reopen a checkpoint.
- **FlowLens v1.0:** NOT YET RELEASED. W04 subflow verification is not end-to-end
  v1.0 business acceptance.

Historical router/control snapshots and immutable reports retain the state at which
they were authored. Their pre-commit CI fields do not replace the actual subsequent
exact-SHA proof linked above; their history is not backfilled by this README.

## Quick Start

Use Python 3.12 and [uv](https://docs.astral.sh/uv/) for dependency management.
Install uv using its official installation guide, then verify availability and
install the locked project and development dependencies:

```bash
uv --version
uv sync
```

Copy [`.env.example`](.env.example) to `.env` for local configuration. Never commit
`.env` or real credentials. The example host-side PostgreSQL URL uses `localhost`;
the API and worker use the Compose service name `postgres` internally.

Docker with Compose support is required. The local runtime uses PostgreSQL 17 with
pgvector, FastAPI and a minimal worker placeholder. Validate, build and start it:

```bash
docker compose config
docker compose up --build -d
docker compose ps
```

Expected services: `postgres` (healthy), `api` (running), `worker` (running).
The API is published only to localhost by default. Verify database-backed health:

```bash
curl http://127.0.0.1:8000/health
```

A healthy database returns HTTP 200 with:

```json
{"status":"ok","service":"flowlens-api","database":"ok"}
```

If PostgreSQL becomes unavailable after startup, the API remains reachable and
returns HTTP 503 with `database` set to `unavailable`.

Apply the approved Alembic chain: `0001_enable_pgvector` then
`0002_industrial_data_foundation` (the 16 canonical manufacturing tables):

```bash
uv run alembic heads
uv run alembic upgrade head
```

Stop the development containers without deleting the persistent PostgreSQL volume:

```bash
docker compose stop
```

This starts engineering infrastructure, not an end-to-end investigation UI.

## Synthetic Data and Validation

Configure `FLOWLENS_DATABASE_URL` and apply `uv run alembic upgrade head` to the
intended isolated development/test database first. The CLI does not create schemas
or apply migrations. Never point acceptance tests at a development database
containing data you want to keep. Synthetic loading writes only the selected local
development/test dataset; it does not authorize operational business write-back.

The public CLI generates **baselines only**. Choose one profile for an **empty
database**; these are alternatives, not sequential replacement commands:

```bash
uv run python -m flowlens.data.cli generate --profile test --period-start 2026-01-01 --generator-version 0.1.0-c03
uv run python -m flowlens.data.cli generate --profile ci --period-start 2026-01-01 --generator-version 0.1.0-c03
uv run python -m flowlens.data.cli generate --profile demo --period-start 2026-01-01 --generator-version 0.1.0-c03
uv run python -m flowlens.data.cli validate
```

These profile/date/version arguments are exercised against PostgreSQL by W02-C05
acceptance tests. `--period-start`, `--generator-version` and `--profile` are required.
`--seed` defaults to `20260824`; `generated_at` uses execution time solely as
provenance and does not affect business content/hash.

| Profile | Period | Sales orders |
|---|---|---|
| `test` | 3 months | 150 |
| `ci` | 6 months | 800 |
| `demo` | 18 months | 12,000 |

`generate` checks public integrity before mutation, batch-inserts one complete
dataset in one transaction, verifies readback before commit, then validates the
committed snapshot and publishes public artifacts. Any existing DatasetVersion
causes an explicit nonzero failure with no new rows. Concurrent loads serialize
under PostgreSQL table locks (30-second lock-wait timeout). There is no merge,
upsert, delete, replacement or `--replace` path. Use a separate empty database for
another dataset. The reusable `persist_dataset(engine, GeneratedDataset)` also
accepts finalized scenario business datasets without receiving HGT.

`validate` reads a consistent, read-only database snapshot and checks all frozen
FKs/keys, temporal and quantity rules, ownership, counts and the existing canonical
hash. It neither repairs data nor evaluates scenario truth. Missing/multiple
DatasetVersions fail clearly. Integrity failure writes FAIL reports and exits 1;
success exits 0. Errors are redacted rather than printing connection parameters.

Default outputs, relative to the command's working directory:

- `data/synthetic/dataset_manifest.json`: allowlisted dataset metadata and table counts.
- `data/synthetic/data_quality_report.json`: aggregate check/category results.
- `data/synthetic/data_quality_report.md`: concise identity, coverage and failure summary.

Use `--output-dir PATH` on either command to choose another public output directory.
No operational IDs, intervention configuration, affected entities, causal chains,
root causes, scenario labels or HGT hashes are published. The public path imports
no scenario/evaluation modules and does not read the protected HGT directory.
Generated defaults and temporary publication files are narrowly Git-ignored.

Files are staged completely, flushed and individually atomically replaced;
filesystem publication is **not** a transaction with the database or across files.
If publication fails after commit, the command exits nonzero but data stays loaded:
correct the path and rerun `validate`, which refreshes reports and the manifest on
PASS. A FAIL validation does not refresh the manifest; consult the current reports.
An interrupted multi-file publication may leave different report generations until
the next successful validation. No success artifacts are published by a failed load.

## Testing and Verification

Run the existing test and quality checks:

```bash
uv run pytest
uv run ruff check .
uv run mypy .
```

The default test command remains safe without PostgreSQL; database integration
tests are skipped when `FLOWLENS_DATABASE_URL` is not configured. To run real
database integration, provision a **dedicated, initially empty test database**.
The safety gate requires `FLOWLENS_APP_ENVIRONMENT=test` and a database name ending
in `_test`; it refuses other targets before applying Alembic migrations.
The environment assignment below uses Bash syntax:

```bash
FLOWLENS_APP_ENVIRONMENT=test \
FLOWLENS_DATABASE_URL=postgresql+psycopg://flowlens:flowlens@localhost:5432/flowlens_test \
  uv run pytest -m integration
```

W02-C05 workflow checks (database fixtures clean only their own datasets):

```bash
uv run pytest tests/test_data_workflow.py
uv run pytest tests/integration/test_data_workflow_database.py
uv run pytest -m "not integration"
uv run pytest -m integration
uv run ruff check .
uv run mypy .
```

W02-C06 CI runs profile generation, persistence and public quality smoke using the
same CLI. The Quality gate uses separate logical databases on one PostgreSQL
service: `flowlens_test` for tests and `flowlens_ci_profile_test` for populated CI
smoke. Public smoke artifacts use temporary runner storage and are removed after
verification; the public workflow does not generate protected HGT. The W01 Docker
Compose smoke remains a separate regression gate.

The [native change classifier](scripts/ci/classify_change.py) determines required
proof from the actual verified delta. A README-only change does not automatically
qualify for publication-only verification:

| Required proof | Required successful jobs | Expected skipped jobs |
|---|---|---|
| `FULL_EXACT_SHA` (C / I / F / UNKNOWN) | Classify change, Quality gate, Docker Compose smoke, W03 AI loop gate, Verification gate | Publication proof |
| `PUBLICATION_EXACT_SHA` (P) | Classify change, Publication proof, Verification gate | Quality gate, Docker Compose smoke, W03 AI loop gate |

Proof must bind the exact source-head SHA, and the overall workflow must complete
successfully. An earlier green run cannot verify a new commit. The frozen W03 gate
and [W04 source-evolution verifier](scripts/ci/verify_w04_source_evolution.py)
preserve accepted source and semantic boundaries. Implementation evidence, independent
GPT review, Human acceptance and closeout are distinct stages; green CI alone does
not authorize a next checkpoint or establish v1.0 business acceptance.

## Repository Structure

```text
apps/api/                     API container definition
apps/worker/                  Worker container definition
src/flowlens/api/             FastAPI application and health endpoint
src/flowlens/worker/          Worker placeholder
src/flowlens/db/              PostgreSQL utilities and canonical models
src/flowlens/data/            Generation, scenarios, persistence and quality
src/flowlens/decision/        W03 decision loop and bounded explanation
src/flowlens/evaluation/      Protected offline W03 evaluation/replay
src/flowlens/investigation/   W04 investigation contracts and C02-C06 implementation
migrations/                  Approved Alembic chain
scripts/ci/                  Native classification and verification tools
tests/                       Unit, safety, semantic and integration harnesses
docs/sprints/                Historical sprint contracts
docs/w03/                    Frozen decision-loop controls and checkpoint evidence
docs/w04/                    Investigation checkpoint evidence and source manifest
docs/context/                Context index and material registry
skills/                      Procedural automation admission policy
AGENTS.md                    Repository execution router
LOOP.md                      Development loop controls
```

## Roadmap

The remaining W04 product journey is planned; none of these checkpoints is
implemented or authorized by this README refresh:

| Checkpoint | Planned work | Current state |
|---|---|---|
| W04-C07 | Faithful investigation summary | NOT IMPLEMENTED |
| W04-C08 | Protected investigation replay | NOT IMPLEMENTED |
| W04-C09 | W04 regression hardening and system gate | NOT IMPLEMENTED |
| W04-C10 | W04 business acceptance | NOT IMPLEMENTED |

End-to-end product packaging remains future work requiring its own scope and
acceptance. W03's existing explanation/replay does not close these W04 gaps.

## Explicit Non-Capabilities

FlowLens v1.0 is not an autonomous industrial operations system. Current verified
capabilities do not include automatic scheduling, procurement, supplier replacement,
quality release, or modification of SO / WO / PO / Delivery or ERP/MES records.

The repository does not establish completed ERP/MES integration, production
SaaS/deployment, a polished investigation UI, predictive ML or factory-wide
optimization. pgvector infrastructure does not imply an implemented RAG product.
Unrestricted LLM tools, LLM recommendations, runtime HGT access, future evidence and
unsupported causal declarations remain prohibited.

## Development Evidence and Documentation

Existing history and technical controls remain accessible:

- [Project charter](docs/00_project_charter.md), [historical scope](docs/01_scope.md),
  [foundation architecture](docs/02_architecture.md) and [data contracts](docs/03_data_contracts.md).
- [W01 project foundation](docs/sprints/W01_project_foundation.md) and
  [W02 industrial data foundation](docs/sprints/W02_industrial_data_foundation.md),
  including frozen schema, scenario rules and historical checkpoint records.
- [W03 sprint](docs/sprints/W03_ai_decision_loop.md),
  [AI loop constitution](docs/w03/AI_LOOP_CONSTITUTION.md),
  [semantic trust contract](docs/w03/SEMANTIC_TRUST_CONTRACT.md),
  [execution state machine](docs/w03/LOOP_EXECUTION_STATE_MACHINE.md),
  [failure/degradation policy](docs/w03/FAILURE_AND_DEGRADATION_POLICY.md) and
  [harness/reporting specification](docs/w03/AI_LOOP_HARNESS_AND_REPORTING_SPEC.md).
- [W03 checkpoint contracts](docs/w03/checkpoints/),
  [immutable review and closeout reports](docs/w03/reports/),
  [W03 final closeout](docs/w03/reports/W03_C10_C1_W03_FINAL_CLOSEOUT.md) and
  [PR #6 merge preparation](docs/w03/reports/W03_PR6_MERGE_PREPARATION.md).
- [W04 checkpoint evidence](docs/w04/checkpoints/),
  [source-evolution manifest](docs/w04/W04_SOURCE_EVOLUTION_MANIFEST.json) and
  [development-control evidence](docs/w04/devctrl/).
  Individual closeouts: [C01](docs/w04/checkpoints/c01/W04_C01_FINAL_CLOSEOUT_REPORT.md),
  [C02](docs/w04/checkpoints/c02/W04_C02_FINAL_CLOSEOUT_REPORT.md),
  [C03](docs/w04/checkpoints/c03/W04_C03_FINAL_CLOSEOUT_REPORT.md),
  [C04](docs/w04/checkpoints/c04/W04_C04_FINAL_CLOSEOUT_REPORT.md),
  [C05](docs/w04/checkpoints/c05/W04_C05_FINAL_CLOSEOUT_REPORT.md) and
  [C06](docs/w04/checkpoints/c06/W04_C06_FINAL_CLOSEOUT_REPORT.md).
- [C06 development report and accepted limitations](docs/w04/checkpoints/c06/W04_C06_R_DEVELOPMENT_ROUND_REPORT.md),
  [independent implementation review](docs/w04/checkpoints/c06/W04_C06_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md)
  and [Human acceptance](docs/w04/checkpoints/c06/W04_C06_HUMAN_ACCEPTANCE.md).
- [Context index](docs/context/CONTEXT_INDEX.md),
  [material registry](docs/context/MATERIAL_REGISTRY.md), [execution router](AGENTS.md),
  [development loop](LOOP.md) and [skill admission policy](skills/SKILL_ADMISSION_POLICY.md).

Current authorized task contracts govern execution. Historical documents retain
their original dates, scope, limitations and authority boundaries.
