"""Public metadata/report serialization, with no operational-row serialization."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from flowlens.data.generation import GeneratedDataset
from flowlens.data.generation.canonical import CANONICAL_TABLE_ORDER, normalize_scalar
from flowlens.data.quality import QualityResult

DEFAULT_OUTPUT_DIRECTORY = Path("data/synthetic")


def public_manifest(dataset: GeneratedDataset) -> dict[str, object]:
    """Explicit allowlist; never ORM __dict__ or an evaluation object."""
    metadata = dataset.dataset_version
    return {
        "dataset_version_id": metadata.dataset_version_id,
        "profile": metadata.profile,
        "seed": metadata.seed,
        "generator_version": metadata.generator_version,
        "period_start": normalize_scalar(metadata.period_start),
        "period_end": normalize_scalar(metadata.period_end),
        "generated_at": normalize_scalar(metadata.generated_at),
        "row_count_total": metadata.row_count_total,
        "row_counts_by_table": {
            name: len(dataset.rows_by_table[name]) for name in CANONICAL_TABLE_ORDER
        },
        "content_hash": metadata.content_hash,
    }


def quality_report(dataset: GeneratedDataset, result: QualityResult) -> dict[str, object]:
    categories: dict[str, object] = {}
    for category in sorted({check.category for check in result.checks}):
        checks = [check for check in result.checks if check.category == category]
        categories[category] = {
            "status": "FAIL" if any(check.violations for check in checks) else "PASS",
            "checks_total": len(checks),
            "checks_failed": sum(check.violations > 0 for check in checks),
        }
    return {
        "status": result.status,
        "dataset": public_manifest(dataset),
        "checks_total": len(result.checks),
        "checks_failed": sum(check.violations > 0 for check in result.checks),
        "categories": categories,
        "checks": [
            {
                "category": check.category,
                "name": check.name,
                "status": check.status,
                "violations": check.violations,
                "detail": "Integrity violations counted; no row identities are published."
                if check.violations
                else "No violations.",
            }
            for check in result.checks
        ],
    }


def quality_markdown(dataset: GeneratedDataset, result: QualityResult) -> str:
    manifest = public_manifest(dataset)

    def safe(value: object) -> str:
        return (
            json.dumps(value, ensure_ascii=True)
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("|", "&#124;")
            .replace("`", "&#96;")
        )

    lines = ["# Public data quality", "", f"Status: {result.status}", ""]
    for name in (
        "dataset_version_id",
        "profile",
        "period_start",
        "period_end",
        "row_count_total",
        "content_hash",
    ):
        lines.append(f"- {name}: {safe(manifest[name])}")
    lines.extend(["", "## Integrity categories", ""])
    for category in sorted({check.category for check in result.checks}):
        checks = [check for check in result.checks if check.category == category]
        failed = sum(check.violations > 0 for check in checks)
        lines.append(
            f"- {category}: {'FAIL' if failed else 'PASS'} ({failed}/{len(checks)} failed)"
        )
    failures = [check for check in result.checks if check.violations]
    if failures:
        lines.extend(["", "## Failed checks", ""])
        lines.extend(
            f"- {check.name}: {check.violations} integrity violation(s)." for check in failures
        )
    return "\n".join(lines) + "\n"


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
    ).encode("utf-8")


def publish_artifacts(
    dataset: GeneratedDataset, result: QualityResult, directory: Path = DEFAULT_OUTPUT_DIRECTORY
) -> None:
    """Publish complete files by atomic replacement after database work finishes.

    Reports (including FAIL) are refreshed; a manifest is published only on PASS.
    Files are individually atomic, not a cross-file/database transaction. Rerun
    validate to recover publication after a filesystem failure.
    """
    payloads = {
        "data_quality_report.json": _json_bytes(quality_report(dataset, result)),
        "data_quality_report.md": quality_markdown(dataset, result).encode("utf-8"),
    }
    if result.passed:
        payloads["dataset_manifest.json"] = _json_bytes(public_manifest(dataset))
    directory.mkdir(parents=True, exist_ok=True)
    staged: list[tuple[Path, Path]] = []
    try:
        for name, payload in payloads.items():
            with tempfile.NamedTemporaryFile(
                prefix=".c05-", suffix=".tmp", dir=directory, delete=False
            ) as stream:
                temporary = Path(stream.name)
                staged.append((temporary, directory / name))
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        for temporary, destination in staged:
            os.replace(temporary, destination)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
