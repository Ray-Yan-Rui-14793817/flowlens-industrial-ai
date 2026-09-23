# FlowLens Industrial AI

FlowLens Industrial AI is an evidence-grounded decision-intelligence platform for an
industry-inspired high-voltage electrical equipment manufacturing scenario.

## Development baseline

W01-C01 supports Python 3.12 and uses
[uv](https://docs.astral.sh/uv/) for dependency management.

Install uv using its official installation guide, then verify it is available:

```bash
uv --version
```

Install the locked project and development dependencies:

```bash
uv sync
```

Run the test and quality checks:

```bash
uv run pytest
uv run ruff check .
uv run mypy .
```

Copy `.env.example` to `.env` for local configuration. Never commit `.env` or real
credentials.

## Week 1 local runtime

The local runtime uses PostgreSQL 17 with pgvector, the FastAPI service, and a minimal
worker placeholder. Docker with Compose support is required. The API and worker use the
Compose service name `postgres` internally; host-side Python commands use the
`localhost` URL in `.env.example`.

Validate, build, and start the complete development stack:

```bash
docker compose config
docker compose up --build -d
docker compose ps
```

The expected services are `postgres` (healthy), `api` (running), and `worker` (running).
The API is published only to localhost by default. Verify its database-backed health:

```bash
curl http://127.0.0.1:8000/health
```

A healthy database returns HTTP 200 and:

```json
{"status":"ok","service":"flowlens-api","database":"ok"}
```

If PostgreSQL becomes unavailable after startup, the API remains reachable and returns
HTTP 503 with `database` set to `unavailable`.

Apply the approved Alembic chain (pgvector infrastructure and the 16 canonical
Week 2 manufacturing tables):

```bash
uv run alembic heads
uv run alembic upgrade head
```

Run the real database integration checks only against a dedicated test database. The
safety gate requires `FLOWLENS_APP_ENVIRONMENT=test` and a database name ending in
`_test`; it refuses other targets before applying Alembic migrations:

```bash
FLOWLENS_APP_ENVIRONMENT=test \
FLOWLENS_DATABASE_URL=postgresql+psycopg://flowlens:flowlens@localhost:5432/flowlens_test \
  uv run pytest -m integration
```

The default test command remains safe without PostgreSQL; database integration tests are
reported as skipped when `FLOWLENS_DATABASE_URL` is not configured.

Stop the development containers without deleting the persistent PostgreSQL volume:

```bash
docker compose stop
```

Week 1 delivered infrastructure only. Week 2 adds the frozen manufacturing data
foundation; business analytics, ML, RAG, LLM and agent functionality remain out of scope.

## Week 2 local data workflow (C05)

Configure `FLOWLENS_DATABASE_URL` using the existing settings, and apply
`uv run alembic upgrade head` to your intended development/test database first.
The CLI does not create schemas or apply migrations. Never point acceptance tests
at a development database containing data you want to keep.

The initial public CLI generates **baselines only**. Choose one profile for an
empty database; the following are alternatives, not sequential replacement commands:

```bash
uv run python -m flowlens.data.cli generate --profile test --period-start 2026-01-01 --generator-version 0.1.0-c03
uv run python -m flowlens.data.cli generate --profile ci --period-start 2026-01-01 --generator-version 0.1.0-c03
uv run python -m flowlens.data.cli generate --profile demo --period-start 2026-01-01 --generator-version 0.1.0-c03
uv run python -m flowlens.data.cli validate
```

These profile/date/version arguments are exercised against PostgreSQL by C05
acceptance tests. `--period-start`, `--generator-version` and `--profile` are
required. `--seed` defaults to the existing C03 value `20260824`; `generated_at`
uses execution time solely as provenance and does not affect business content/hash.
Profiles retain the frozen C03 sizes: test (3 months / 150 sales orders), ci
(6 months / 800), demo (18 months / 12,000).

`generate` checks public integrity before mutation, batch-inserts one complete
dataset in one transaction, verifies the readback before commit, then validates
the committed snapshot and publishes public artifacts. Any existing DatasetVersion
causes an explicit nonzero failure with no new rows. Concurrent loads serialize
under PostgreSQL table locks (30-second lock-wait timeout). There is no merge,
upsert, delete, replacement or `--replace` path. Use a separate empty database
for another dataset. The reusable `persist_dataset(engine, GeneratedDataset)`
also accepts finalized scenario business datasets without receiving HGT.

`validate` reads a consistent, read-only database snapshot and checks all frozen
FKs/keys, temporal and quantity rules, ownership, counts and the existing canonical
hash. It neither repairs data nor evaluates scenario truth. Missing/multiple
DatasetVersions fail clearly. Integrity failure writes FAIL reports and exits 1;
success exits 0. Errors are redacted rather than printing connection parameters.

Default outputs (relative to the command's working directory):

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

C05 checks (integration requires a dedicated, initially empty PostgreSQL `_test`
database and `FLOWLENS_APP_ENVIRONMENT=test`; fixtures clean only their own datasets):

```bash
uv run pytest tests/test_data_workflow.py
uv run pytest tests/integration/test_data_workflow_database.py
uv run pytest -m "not integration"
uv run pytest -m integration
uv run ruff check .
uv run mypy .
```

C05 is closed and verified. C06 adds Week 2 CI-profile generation, persistence,
public data-quality smoke and acceptance automation using the existing C05 CLI.
The Quality gate uses separate logical databases on the same PostgreSQL service:
`flowlens_test` for integration/full pytest and `flowlens_ci_profile_test` for the
populated CI smoke. Public smoke artifacts use runner-temporary storage and are
removed after verification; protected HGT is not generated by the public workflow.
The Week 1 Docker Compose smoke remains a separate required regression gate.

Week 2 Industrial Data Foundation is COMPLETE / CLOSED / VERIFIED. C06 exact-SHA
GitHub CI is VERIFIED; independent review passed, and Product-Owner acceptance
is ACCEPTED WITH DOCUMENTED LIMITATIONS. C06 is CLOSED / VERIFIED; known
limitations remain documented. Week 3 is NOT STARTED / NOT AUTHORIZED. The next
checkpoint is a Week 3 architecture / AI-readiness / semantic-trust
authorization review only.
