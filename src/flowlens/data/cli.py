"""Baseline-first local workflow: python -m flowlens.data.cli generate|validate."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from flowlens.config import Settings
from flowlens.data.artifacts import DEFAULT_OUTPUT_DIRECTORY, publish_artifacts
from flowlens.data.generation import (
    DEFAULT_DEMO_SEED,
    GenerationConfig,
    GenerationProfile,
    generate_baseline,
)
from flowlens.data.persistence import DatasetLoadError, persist_dataset, read_active_dataset
from flowlens.data.quality import validate_dataset
from flowlens.db import create_database_engine


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Public synthetic manufacturing data workflow")
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="Generate and atomically load a baseline")
    generate.add_argument(
        "--profile", choices=[profile.value for profile in GenerationProfile], required=True
    )
    generate.add_argument("--seed", type=int, default=DEFAULT_DEMO_SEED)
    generate.add_argument("--period-start", type=date.fromisoformat, required=True)
    generate.add_argument("--generator-version", required=True)
    validate = commands.add_parser("validate", help="Validate the active database dataset")
    for command in (generate, validate):
        command.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        config = None
        if args.command == "generate":
            config = GenerationConfig(
                profile=GenerationProfile(args.profile),
                seed=args.seed,
                period_start=args.period_start,
                generator_version=args.generator_version,
                generated_at=datetime.now(UTC),
            )
        settings = Settings()
    except (ValidationError, ValueError, TypeError):
        print(
            "Invalid generation inputs or database settings; check configuration.", file=sys.stderr
        )
        return 1
    engine: Engine | None = None
    try:
        engine = create_database_engine(settings)
        if config is not None:
            persist_dataset(engine, generate_baseline(config))
        dataset = read_active_dataset(engine)
        result = validate_dataset(dataset)
        publish_artifacts(dataset, result, args.output_dir)
        print(f"Public data quality: {result.status}")
        return 0 if result.passed else 1
    except DatasetLoadError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (SQLAlchemyError, ValueError):
        print(
            "Database workflow failed; verify connectivity and the approved Alembic head.",
            file=sys.stderr,
        )
        return 1
    except OSError:
        print(
            "Public artifact publication failed. Database state may be committed; "
            "correct the output path and rerun validate.",
            file=sys.stderr,
        )
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
