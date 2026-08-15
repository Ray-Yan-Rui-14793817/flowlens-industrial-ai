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

## PostgreSQL foundation

W01-C02 provides one local PostgreSQL 17 service with pgvector available. Docker with
Compose support is required. The container variables and `FLOWLENS_DATABASE_URL` in
`.env` must describe the same local database.

The example URL uses `localhost` for commands run from the development host. A future
Compose-managed application container would instead use the service DNS name `postgres`;
that application-container setup is not implemented in C02.

Validate and start the database service:

```bash
docker compose config
docker compose pull
docker compose up -d postgres
docker compose ps
```

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
