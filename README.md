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

Run the C01 test and quality checks:

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

Apply the infrastructure-only Alembic baseline, which enables the `vector` extension:

```bash
uv run alembic heads
uv run alembic upgrade head
```

Run the real database integration checks after PostgreSQL is healthy and `.env` is
configured:

```bash
uv run pytest -m integration
```

The default test command remains safe without PostgreSQL; database integration tests are
reported as skipped when `FLOWLENS_DATABASE_URL` is not configured.

Stop the development containers without deleting the persistent PostgreSQL volume:

```bash
docker compose stop
```

Week 1 contains infrastructure only. It does not include manufacturing schemas, business
analytics, ML, RAG, LLM, or agent functionality.
