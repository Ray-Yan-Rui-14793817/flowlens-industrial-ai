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
is **FlowLens v1.0**; **FlowLens v1.0 is NOT RELEASED**. The repository contains
the verified W01/W02 foundations, merged W03 decision loop and complete W04
C01-C10 investigation workflow. W04 C01-C10 are implemented, independently
reviewed, Human accepted and CLOSED / VERIFIED within the accepted scope.

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

The W04 engineering workflow now includes deterministic investigation summary,
protected replay, regression hardening and completed W04 Human business acceptance.
The implemented surfaces remain Python modules and tested engineering workflows;
product packaging and release require separate scope and acceptance.

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
  -> Investigation Summary                        [W04-C07: CLOSED / VERIFIED]
  -> Protected Investigation Replay                [W04-C08: CLOSED / VERIFIED]
  -> W04 Regression Hardening                      [W04-C09: CLOSED / VERIFIED]
  -> W04 Business Acceptance                       [W04-C10: CLOSED / VERIFIED]
```

W03 provides bounded explanation of frozen DecisionPackets, Human decision recording
and protected offline evaluation/deterministic decision replay. W04 adds its own
deterministic investigation summary, bounded optional LLM presentation and protected
replay of frozen investigation artifacts. Replay does not refresh evidence.

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
| W04-C07 | Deterministic summary, bounded optional LLM presentation and deterministic fallback | CLOSED / VERIFIED |
| W04-C08 | Protected deterministic investigation replay with frozen context and authority | CLOSED / VERIFIED |
| W04-C09 | Semantic regression, source guards and meta-CI hardening | CLOSED / VERIFIED |
| W04-C10 | Independent review, explicit Human business acceptance and governance closeout | CLOSED / VERIFIED |

W03 Human decision outcomes are `ACCEPT`, `REJECT` and `DEFER`. W04 Human
investigation outcomes are `SUPPORTED_FINDING_RECORDED`, `NO_SUPPORTED_FINDING`,
`MORE_EVIDENCE_REQUIRED`, `DEFER` and `INVESTIGATION_REVIEW_COMPLETE`. These record
review state within their contracts; they do not execute a recommendation, establish
causal truth or authorize operational follow-up. Human notes are
`HUMAN_NOTE_NON_EVIDENCE` and cannot become evidence.

C01 contracts now support the accepted C02-C08 execution path. C09/C10 provide
regression and governance/business-acceptance evidence; they introduce no new
investigation runtime source. There is no completed product UI or production
SaaS deployment.

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
  write capability. W03 supports bounded explanation with deterministic fallback;
  W04-C07 permits only bounded presentation of the frozen deterministic summary.
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

C07 optional provider output is constrained by frozen grounding references and a
positive grammar. Unsafe, unavailable or invalid output returns the complete
deterministic fallback; LLM wording is not byte-deterministic. CI uses fake
providers/clients and does not establish live provider availability or actual
model-output distributions. Human note text is excluded from provider data and
grounding. C08 replay preserves the original evidence/time boundary.

## Architecture

| Plane | Existing implementation | Boundary |
|---|---|---|
| Local runtime | [FastAPI](src/flowlens/api/), [worker placeholder](src/flowlens/worker/), [database utilities](src/flowlens/db/), [settings](src/flowlens/config.py) | Development infrastructure and health checks |
| Industrial data | [Data modules](src/flowlens/data/), [Alembic migrations](migrations/) | Frozen schema, deterministic development/test data and validation |
| Decision | [Decision modules](src/flowlens/decision/) | Snapshot-first deterministic decision loop and bounded explanation |
| Investigation | [Investigation modules](src/flowlens/investigation/) | Exact packet binding, planning, authorized navigation, findings, Human review, summary and protected replay through C08 |
| Protected evaluation | [Evaluation modules](src/flowlens/evaluation/) | Offline W03 evaluation/replay; no runtime HGT |
| Development verification | [CI scripts](scripts/ci/), [tests](tests/), [native workflow](.github/workflows/ci.yml) | Exact-SHA proof and source/semantic safety enforcement |

The W04 implementation is in `c02_binding.py`, `c03_planning.py`,
`c04_registry.py`, `c04_queries.py`, `c04_navigation.py`, `c05_findings.py`,
`c06_human.py`, `c06_policy.py`, `c06_store.py`, `c07_summary.py`, `c07_policy.py`,
`c07_provider.py`, `c08_policy.py` and `c08_replay.py` under
`src/flowlens/investigation/`. These modules extend the frozen W03 baseline.
Operational reads, local audit persistence and protected offline evaluation have
separate authority boundaries; none grants operational write-back.

## Current Development Status

**Verified baseline as of 2026-10-22 (Asia/Shanghai). Current phase:
POST-W04 STABILIZATION CLOSED / W05-G0 SUCCESSOR GOVERNANCE NEXT.**

- **W01/W02:** CLOSED / VERIFIED; schema, canonical hashes, deterministic generator
  semantics and HGT isolation preserved.
- **W03:** MERGED / CLOSED / VERIFIED through PR #6, merge
  af61bdfd5f7cf7961811c4c2dc8e554dd7eed509, exact-main CI #86 / 37261505402.
- **W04:** MERGED / CLOSED / VERIFIED through PR #7, merge
  b2b582541d38180c3bf8360699e6df271979829a, exact-main CI #149 / 39008095313.
  C01-C10 remain CLOSED / VERIFIED. The W04 feature branch is retained.
- **PR #8:** MERGED / CLOSED / VERIFIED at
  2f1627342ff2b04d8324fbffec3db2e230b302e0; feature head
  bd29242f8e21ba31bc7782e0c98e1a8aed3641f8 is retained.
  [Post-merge CI #153 / 39142499049](https://github.com/Ray-Yan-Rui-14793817/flowlens-industrial-ai/actions/runs/39142499049):
  attempt 1 SUCCESS, UNKNOWN / FULL_EXACT_SHA / push_full.
- **P2-03:** MERGED_NATIVE_PROVEN_CLOSED. Publication deletion hardening and R4
  merge-lifecycle repair are integrated. **MR8-P1-01: CLOSED**, repaired by R4 V2
  and proven by the normal merge and its first native run.
- **Historical proof:** 2997 non-integration nodes / 2994 passed / 3 accepted
  Linux skips, 63 files / 7 shards; zero adverse outcomes; no-loss / exact union /
  exact once PASS. Integration 70; W03 38/85; W04 9/67/81;
  governance 172/223/93/95/98 PASS at the merge anchor.
- **POST_W04_STABILIZATION:** CLOSED. **POST_MERGE_DOC_SYNC:** COMPLETE.
- **W05 successor governance:** NEXT / NOT ACTIVE in this documentation commit.
  The separately Human-authorized W05-G0 task permits only its bounded governance
  transition. This README records Commit A; the current router and state
  projection carry the later Commit B governance status.
- **W05-C01/C02, product API/UI, W06 and release:** NOT AUTHORIZED by G0;
  product API/UI NOT IMPLEMENTED; FlowLens v1.0 NOT RELEASED.
- **P2-01/P2-02:** preserved accepted limitations. No product runtime change.

Historical C10, Sprint Prep/Final, PR #7 and PR #8 evidence remains immutable.
The source-evolution manifest continues to freeze closed C01-C08 runtime source.
No historical conditional report is rewritten as if it anticipated later proof.

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
| `FULL_EXACT_SHA` (C / I / F / UNKNOWN) | Classify, Static and plan, Integration and data, all seven non-integration shards, Non-integration aggregate, Quality, Compose, W03, W04 and Verification | Publication proof |
| `PUBLICATION_EXACT_SHA` (P) | Classify change, Publication proof, Verification gate | Full-route static/integration/shard/aggregate/Quality/Compose/W03/W04 jobs |

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
src/flowlens/investigation/   W04 contracts and C02-C08 runtime implementation
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

W04 and Post-W04 stabilization are MERGED / CLOSED / VERIFIED. W05-G0 is a
separately authorized governance-only transition, beginning with this post-merge
documentation synchronization. Successor governance is not active in Commit A.
The current router/state projection records subsequent governance proof.
Analytics, product packaging, API/UI, ML, production readiness and release each
require separate scope and Human authority. G0 grants no merge authority.
FlowLens v1.0 remains NOT RELEASED.

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
  [C05](docs/w04/checkpoints/c05/W04_C05_FINAL_CLOSEOUT_REPORT.md),
  [C06](docs/w04/checkpoints/c06/W04_C06_FINAL_CLOSEOUT_REPORT.md),
  [C07](docs/w04/checkpoints/c07/W04_C07_FINAL_CLOSEOUT_REPORT.md),
  [C08](docs/w04/checkpoints/c08/W04_C08_FINAL_CLOSEOUT_REPORT.md),
  [C09](docs/w04/checkpoints/c09/W04_C09_FINAL_CLOSEOUT_REPORT.md) and
  [C10](docs/w04/checkpoints/c10/W04_C10_FINAL_CLOSEOUT_REPORT.md).
- [C06 development report and accepted limitations](docs/w04/checkpoints/c06/W04_C06_R_DEVELOPMENT_ROUND_REPORT.md),
  [independent implementation review](docs/w04/checkpoints/c06/W04_C06_GPT_INDEPENDENT_IMPLEMENTATION_REVIEW_R1.md)
  and [Human acceptance](docs/w04/checkpoints/c06/W04_C06_HUMAN_ACCEPTANCE.md).
- [W04 Sprint independent review](docs/w04/W04_GPT_INDEPENDENT_DEEP_REVIEW_R1.md),
  [original Human acceptance/authorization](docs/w04/W04_SPRINT_HUMAN_ACCEPTANCE_AND_AUTHORIZATION.md),
  [Sprint context lock](docs/w04/W04_SPRINT_CLOSEOUT_CONTEXT_LOCK.md),
  [Sprint Final report](docs/w04/W04_SPRINT_FINAL_CLOSEOUT_REPORT.md) and
  [PR #7 readiness report](docs/w04/W04_PR7_READINESS_REPORT.md).
- [C07 summary/provider boundaries](docs/w04/checkpoints/c07/W04_C07_R_DEVELOPMENT_ROUND_REPORT.md)
  and [C08 protected replay evidence](docs/w04/checkpoints/c08/W04_C08_R_DEVELOPMENT_ROUND_REPORT.md).
- [Context index](docs/context/CONTEXT_INDEX.md),
  [material registry](docs/context/MATERIAL_REGISTRY.md), [execution router](AGENTS.md),
  [development loop](LOOP.md) and [skill admission policy](skills/SKILL_ADMISSION_POLICY.md).

Current authorized task contracts govern execution. Historical documents retain
their original dates, scope, limitations and authority boundaries.
