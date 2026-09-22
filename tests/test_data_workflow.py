"""C05 public quality, artifact and CLI acceptance without a database."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from flowlens.data import Base, artifacts, cli
from flowlens.data.generation import (
    BUSINESS_TIMEZONE,
    GeneratedDataset,
    GenerationConfig,
    GenerationProfile,
    generate_baseline,
)
from flowlens.data.generation.canonical import canonical_content_hash
from flowlens.data.models import DatasetVersion, Operation, PurchaseOrder, SalesOrder
from flowlens.data.persistence import row_values
from flowlens.data.quality import validate_dataset
from flowlens.data.scenarios import CapacitySurgeConfig, apply_scenario


@pytest.fixture(scope="module")
def baseline() -> GeneratedDataset:
    return generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.TEST,
            seed=20260824,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=datetime(2026, 8, 24, tzinfo=UTC),
        )
    )


@pytest.fixture
def dataset(baseline: GeneratedDataset) -> GeneratedDataset:
    return GeneratedDataset(
        DatasetVersion(**row_values(baseline.dataset_version)),
        {
            name: tuple(type(row)(**row_values(row)) for row in values)
            for name, values in baseline.rows_by_table.items()
        },
    )


def _failed(dataset: GeneratedDataset) -> set[str]:
    result = validate_dataset(dataset)
    assert not result.passed
    return {check.name for check in result.checks if check.violations}


def test_valid_dataset_and_hash_order_provenance(dataset: GeneratedDataset) -> None:
    result = validate_dataset(dataset)
    assert result.passed and len(result.checks) == 144
    assert len({check.name for check in result.checks}) == len(result.checks)
    dataset.dataset_version.generated_at += timedelta(days=3)
    reordered = GeneratedDataset(
        dataset.dataset_version,
        {
            name: tuple(reversed(values))
            for name, values in reversed(list(dataset.rows_by_table.items()))
        },
    )
    assert validate_dataset(reordered) == result
    assert canonical_content_hash(reordered.rows_by_table) == dataset.content_hash


@pytest.mark.parametrize(
    ("table", "column"),
    [
        (table.name, fk.parent.name)
        for table in Base.metadata.sorted_tables
        for fk in sorted(table.foreign_keys, key=lambda item: item.parent.name)
    ],
)
def test_every_frozen_foreign_key(dataset: GeneratedDataset, table: str, column: str) -> None:
    setattr(dataset.rows_by_table[table][0], column, "missing-public-reference")
    assert f"{table}.{column}" in _failed(dataset)


@pytest.mark.parametrize(
    ("table", "column", "value", "check"),
    [
        ("dim_product", "standard_cycle_hours", Decimal(0), "product.cycle_hours"),
        ("dim_product", "product_family", "INVALID", "product.enums"),
        ("dim_material", "standard_lead_time_days", 0, "material.lead_time"),
        ("dim_material", "criticality", "INVALID", "material.criticality"),
        ("dim_work_center", "daily_capacity_hours", Decimal(0), "work_center.capacity"),
        ("dim_work_center", "process_type", "INVALID", "work_center.process"),
        ("bridge_product_material", "quantity_per_unit", Decimal(0), "bom.quantity"),
        ("fact_sales_order", "order_quantity", 0, "sales.quantity"),
        ("fact_sales_order", "priority", "INVALID", "sales.enums"),
        ("fact_sales_order", "status", "INVALID", "sales.enums"),
        ("fact_purchase_order", "ordered_quantity", Decimal(0), "purchase.quantity"),
        ("fact_purchase_order", "received_quantity", Decimal(-1), "purchase.quantity"),
        ("fact_purchase_order", "received_quantity", Decimal(9999999), "purchase.quantity"),
        ("fact_work_order", "planned_quantity", 0, "work.quantity"),
        ("fact_work_order", "completed_quantity", -1, "work.quantity"),
        ("fact_work_order", "completed_quantity", 99999, "work.quantity"),
        ("fact_work_order", "status", "INVALID", "work.status"),
        ("fact_operation", "sequence_number", 0, "operation.sequence"),
        ("fact_material_requirement", "required_quantity", Decimal(0), "requirement.quantity"),
        ("fact_inventory_snapshot", "on_hand_quantity", Decimal(-1), "inventory.quantity"),
        ("fact_inventory_snapshot", "reserved_quantity", Decimal(-1), "inventory.quantity"),
        ("fact_inventory_snapshot", "reserved_quantity", Decimal(99999999), "inventory.quantity"),
        ("fact_quality_inspection", "inspected_quantity", 0, "inspection.balance"),
        ("fact_quality_inspection", "passed_quantity", -1, "inspection.balance"),
        ("fact_quality_inspection", "failed_quantity", -1, "inspection.balance"),
        ("fact_quality_inspection", "result", "INVALID", "inspection.result"),
        ("fact_rework", "rework_quantity", 0, "rework.quantity"),
        ("fact_rework", "rework_quantity", 999999, "rework.within_failed"),
        ("fact_delivery", "delivered_quantity", 0, "delivery.quantity"),
        ("fact_delivery", "delivered_quantity", 999999, "delivery.cumulative"),
    ],
)
def test_quantity_and_domain_rules(
    dataset: GeneratedDataset, table: str, column: str, value: object, check: str
) -> None:
    setattr(dataset.rows_by_table[table][0], column, value)
    assert check in _failed(dataset)


@pytest.mark.parametrize(
    ("table", "column", "reference", "check"),
    [
        ("fact_sales_order", "promised_delivery_at", "order_at", "sales.window"),
        ("fact_purchase_order", "promised_receipt_at", "ordered_at", "purchase.promised"),
        ("fact_purchase_order", "actual_receipt_at", "ordered_at", "purchase.actual"),
        ("fact_work_order", "planned_end_at", "planned_start_at", "fact_work_order.planned_window"),
        ("fact_work_order", "actual_end_at", "actual_start_at", "fact_work_order.actual_window"),
        ("fact_operation", "planned_end_at", "planned_start_at", "fact_operation.planned_window"),
        ("fact_operation", "actual_end_at", "actual_start_at", "fact_operation.actual_window"),
        ("fact_rework", "rework_end_at", "rework_start_at", "rework.window"),
    ],
)
def test_temporal_windows(
    dataset: GeneratedDataset, table: str, column: str, reference: str, check: str
) -> None:
    row = next(row for row in dataset.rows_by_table[table] if getattr(row, reference) is not None)
    setattr(row, column, getattr(row, reference) - timedelta(seconds=1))
    assert check in _failed(dataset)


@pytest.mark.parametrize(
    ("table", "field", "check"),
    [
        ("fact_quality_inspection", "inspection_at", "inspection.after_work_start"),
        ("fact_rework", "rework_start_at", "rework.after_inspection"),
        ("fact_delivery", "delivery_at", "delivery.after_order"),
    ],
)
def test_cross_table_time(dataset: GeneratedDataset, table: str, field: str, check: str) -> None:
    for row in dataset.rows_by_table[table]:
        setattr(row, field, datetime(1900, 1, 1, tzinfo=UTC))
    assert check in _failed(dataset)


@pytest.mark.parametrize(
    "value",
    [Decimal("NaN"), Decimal("Infinity"), Decimal("0.00001"), Decimal("10000000000"), 1.5, None],
)
def test_invalid_numeric_transport(dataset: GeneratedDataset, value: object) -> None:
    cast(PurchaseOrder, dataset.rows_by_table["fact_purchase_order"][0]).ordered_quantity = cast(
        Decimal, value
    )
    assert "fact_purchase_order.scalar_types" in _failed(dataset)


def test_naive_timestamp_and_count_hash_failures(dataset: GeneratedDataset) -> None:
    dataset.dataset_version.row_count_total += 1
    dataset.dataset_version.content_hash = "0" * 64
    assert {"row_count_total", "canonical_content_hash"} <= _failed(dataset)
    cast(SalesOrder, dataset.rows_by_table["fact_sales_order"][0]).order_at = datetime(2026, 1, 1)
    assert "fact_sales_order.scalar_types" in _failed(dataset)


def test_key_uniqueness_and_table_shape(dataset: GeneratedDataset) -> None:
    rows = dict(dataset.rows_by_table)
    rows["dim_product"] += (rows["dim_product"][0],)
    assert "dim_product.primary_key" in _failed(GeneratedDataset(dataset.dataset_version, rows))
    rows.pop("fact_delivery")
    assert _failed(GeneratedDataset(dataset.dataset_version, rows)) == {"business_table_set"}


def test_public_artifacts_exact_allowlist_and_repeat(
    dataset: GeneratedDataset, tmp_path: Path
) -> None:
    result = validate_dataset(dataset)
    artifacts.publish_artifacts(dataset, result, tmp_path)
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    artifacts.publish_artifacts(dataset, result, tmp_path)
    assert before == {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    manifest = json.loads(before["dataset_manifest.json"])
    assert set(manifest) == {
        "dataset_version_id",
        "profile",
        "seed",
        "generator_version",
        "period_start",
        "period_end",
        "generated_at",
        "row_count_total",
        "row_counts_by_table",
        "content_hash",
    }
    assert sum(manifest["row_counts_by_table"].values()) == dataset.row_count_total
    report = json.loads(before["data_quality_report.json"])
    assert report["status"] == "PASS" and report["checks_failed"] == 0
    assert report["checks_total"] == len(report["checks"]) == 144
    assert all(check["status"] == "PASS" for check in report["checks"])
    assert "Status: PASS" in before["data_quality_report.md"].decode()


def test_failed_reports_do_not_publish_success_manifest(
    dataset: GeneratedDataset, tmp_path: Path
) -> None:
    dataset.dataset_version.row_count_total += 1
    result = validate_dataset(dataset)
    artifacts.publish_artifacts(dataset, result, tmp_path)
    assert not (tmp_path / "dataset_manifest.json").exists()
    assert json.loads((tmp_path / "data_quality_report.json").read_bytes())["status"] == "FAIL"
    assert (
        "row_count_total: 1 integrity violation"
        in (tmp_path / "data_quality_report.md").read_text()
    )


def test_publication_failure_preserves_complete_files(
    dataset: GeneratedDataset, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = validate_dataset(dataset)
    artifacts.publish_artifacts(dataset, result, tmp_path)
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}

    def fail(source: object, destination: object) -> None:
        raise OSError("injected publication failure")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(OSError):
        artifacts.publish_artifacts(dataset, result, tmp_path)
    assert before == {path.name: path.read_bytes() for path in tmp_path.iterdir()}


def test_scenario_business_input_has_no_public_truth(baseline: GeneratedDataset) -> None:
    scenario = apply_scenario(
        baseline,
        CapacitySurgeConfig(
            scenario_version="1.0.0",
            scenario_seed=20260901,
            window_start=datetime(2026, 1, 15, tzinfo=BUSINESS_TIMEZONE),
            window_end=datetime(2026, 2, 15, tzinfo=BUSINESS_TIMEZONE),
        ),
        generated_at=datetime(2026, 8, 24, tzinfo=UTC),
    )
    result = validate_dataset(scenario.dataset)
    assert result.passed
    public = json.dumps(
        artifacts.quality_report(scenario.dataset, result)
    ) + artifacts.quality_markdown(scenario.dataset, result)
    truth = scenario.ground_truth
    for value in (
        truth.hgt_id,
        truth.hgt_hash,
        truth.scenario_id,
        truth.scenario_type.value,
        *truth.target_entity_ids,
    ):
        assert value not in public
    for values in truth.affected_entities_by_table.values():
        assert not any(value in public for value in values)
    assert not any(
        word in public for word in ("hgt_", "scenario_", "causal_chain", "true_root_cause")
    )


def test_public_imports_do_not_load_evaluation_code() -> None:
    script = (
        "import sys; import flowlens.data.cli; "
        "assert not any(m.startswith('flowlens.data.scenarios') for m in sys.modules)"
    )
    subprocess.run([sys.executable, "-c", script], check=True, capture_output=True)


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["generate"],
        ["generate", "--replace"],
        ["generate", "--scenario", "capacity"],
        ["validate", "--replace"],
    ],
)
def test_cli_rejects_missing_or_forbidden_arguments(arguments: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        cli.main(arguments)
    assert error.value.code == 2


def test_cli_settings_error_is_redacted(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("FLOWLENS_DATABASE_URL", "private-connection-secret")
    monkeypatch.setenv("FLOWLENS_APP_ENVIRONMENT", "invalid-private-value")
    assert cli.main(["validate"]) == 1
    assert "private" not in capsys.readouterr().err


def test_public_boundary_rejects_non_dataset() -> None:
    with pytest.raises(TypeError, match="GeneratedDataset"):
        validate_dataset(cast(GeneratedDataset, object()))


@pytest.mark.parametrize(
    "url",
    [
        "private-connection-secret",
        "unknown-driver://secret@host/db",
        "postgresql+psycopg://user:secret@localhost:bad-port/db",
    ],
)
def test_cli_engine_configuration_error_is_redacted(
    url: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("FLOWLENS_DATABASE_URL", url)
    monkeypatch.setenv("FLOWLENS_APP_ENVIRONMENT", "test")
    assert cli.main(["validate"]) == 1
    output = capsys.readouterr()
    assert "secret" not in output.err and "Traceback" not in output.err


@pytest.mark.parametrize(
    ("table", "field"),
    [
        ("dim_product", "product_code"),
        ("dim_material", "material_code"),
        ("fact_operation", "sequence_number"),
    ],
)
def test_explicit_unique_constraints(dataset: GeneratedDataset, table: str, field: str) -> None:
    first, second = dataset.rows_by_table[table][:2]
    setattr(second, field, getattr(first, field))
    if table == "fact_operation":
        cast(Operation, second).work_order_id = cast(Operation, first).work_order_id
    assert any(check.startswith("uq_") for check in _failed(dataset))


def test_nullable_times_and_inspection_result_boundaries(dataset: GeneratedDataset) -> None:
    from flowlens.data.models import Operation, QualityInspection, WorkOrder

    operation = cast(Operation, dataset.rows_by_table["fact_operation"][0])
    operation.actual_start_at = operation.actual_end_at = None
    work = cast(WorkOrder, dataset.rows_by_table["fact_work_order"][0])
    work.actual_start_at = None
    work.actual_end_at = datetime(2026, 3, 1, tzinfo=UTC)
    assert "work.end_requires_start" in _failed(dataset)
    work.actual_end_at = None
    inspection = cast(QualityInspection, dataset.rows_by_table["fact_quality_inspection"][0])
    inspection.result = "PASS"
    inspection.failed_quantity = 1
    inspection.passed_quantity = inspection.inspected_quantity - 1
    assert "inspection.result" in _failed(dataset)
    inspection.result = "FAIL"
    inspection.failed_quantity = 0
    inspection.passed_quantity = inspection.inspected_quantity
    assert "inspection.result" in _failed(dataset)
