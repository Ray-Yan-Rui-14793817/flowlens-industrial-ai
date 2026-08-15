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
