"""Unit tests for the Alembic migration configuration."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_alembic_configuration_loads() -> None:
    config = Config(toml_file=str(PROJECT_ROOT / "pyproject.toml"))

    scripts = ScriptDirectory.from_config(config)

    assert Path(scripts.dir).resolve() == PROJECT_ROOT / "migrations"
    assert scripts.get_current_head() == "0001_enable_pgvector"
