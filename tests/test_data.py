"""Tests for the canonical SQLAlchemy domain metadata foundation."""

import os
import runpy
import subprocess
import sys
from contextlib import nullcontext
from pathlib import Path

import pytest
from alembic import context as alembic_context
from sqlalchemy import MetaData

from flowlens.config import get_settings
from flowlens.data import Base
from flowlens.data.base import Base as ImplementationBase

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NAMING_KEYS = {"ix", "uq", "ck", "fk", "pk"}


def test_canonical_base_is_exposed_from_data_boundary() -> None:
    assert Base is ImplementationBase
    assert isinstance(Base.metadata, MetaData)
    assert Base.metadata is ImplementationBase.metadata


def test_canonical_metadata_has_complete_naming_convention() -> None:
    naming_convention = Base.metadata.naming_convention

    assert EXPECTED_NAMING_KEYS <= naming_convention.keys()
    assert naming_convention["ix"]
    assert naming_convention["uq"]
    assert naming_convention["ck"]
    assert naming_convention["fk"]
    assert naming_convention["pk"]


def test_canonical_metadata_has_no_manufacturing_models_yet() -> None:
    assert not Base.metadata.tables


def test_data_boundary_import_has_no_database_side_effects() -> None:
    environment = os.environ.copy()
    environment.pop("FLOWLENS_DATABASE_URL", None)
    script = """
import alembic.command
import psycopg
import sqlalchemy
import sqlalchemy.orm

def unexpected_side_effect(*args, **kwargs):
    raise AssertionError("flowlens.data import triggered a database side effect")

alembic.command.upgrade = unexpected_side_effect
psycopg.connect = unexpected_side_effect
sqlalchemy.create_engine = unexpected_side_effect
sqlalchemy.MetaData.create_all = unexpected_side_effect
sqlalchemy.orm.sessionmaker = unexpected_side_effect

from flowlens.data import Base

assert not Base.metadata.tables
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_alembic_uses_canonical_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    configured: dict[str, object] = {}

    def capture_configuration(**kwargs: object) -> None:
        configured.update(kwargs)

    monkeypatch.setenv(
        "FLOWLENS_DATABASE_URL",
        "postgresql+psycopg://flowlens:flowlens@localhost:5432/flowlens",
    )
    monkeypatch.setattr(alembic_context, "is_offline_mode", lambda: True)
    monkeypatch.setattr(alembic_context, "configure", capture_configuration)
    monkeypatch.setattr(alembic_context, "begin_transaction", nullcontext)
    monkeypatch.setattr(alembic_context, "run_migrations", lambda: None)
    get_settings.cache_clear()

    try:
        namespace = runpy.run_path(str(PROJECT_ROOT / "migrations" / "env.py"))
    finally:
        get_settings.cache_clear()

    assert namespace["target_metadata"] is Base.metadata
    assert configured["target_metadata"] is Base.metadata
