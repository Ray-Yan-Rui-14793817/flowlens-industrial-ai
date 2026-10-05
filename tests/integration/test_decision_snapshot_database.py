"""C02 PostgreSQL transaction, bounded graph, and zero-mutation acceptance."""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any, cast
from zoneinfo import ZoneInfo

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import event, func, select
from sqlalchemy.engine import Engine, make_url

from flowlens.config import Settings
from flowlens.data import Base
from flowlens.data.generation import (
    GeneratedDataset,
    GenerationConfig,
    GenerationProfile,
    generate_baseline,
)
from flowlens.data.generation.canonical import CANONICAL_TABLE_ORDER, canonical_business_payload
from flowlens.data.models import DatasetVersion, SalesOrder
from flowlens.data.persistence import persist_dataset, read_active_dataset, row_values
from flowlens.data.scenarios import (
    CapacitySurgeConfig,
    QualityDeteriorationConfig,
    SupplierDegradationConfig,
    apply_scenario,
)
from flowlens.data.scenarios.config import ScenarioConfig
from flowlens.db import create_database_engine
from flowlens.db.decision_snapshot import build_decision_snapshot
from flowlens.decision.context import build_decision_context
from flowlens.decision.contracts import DecisionRun
from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.primitives import ArtifactProvenance, VersionRef
from flowlens.decision.serialization import canonical_json_bytes, derive_artifact_id
from flowlens.decision.temporal import C02BuildError

pytestmark = pytest.mark.integration


def _source() -> GeneratedDataset:
    return generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.TEST,
            seed=20260824,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=datetime(2026, 8, 24, tzinfo=UTC),
        )
    )


def _counts(engine: Engine) -> dict[str, int]:
    with engine.connect() as connection:
        return {
            name: connection.execute(select(func.count()).select_from(table)).scalar_one()
            for name, table in Base.metadata.tables.items()
        }


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    try:
        settings = Settings()
    except ValidationError:
        if os.environ.get("FLOWLENS_DATABASE_URL"):
            raise
        pytest.skip("FLOWLENS_DATABASE_URL required for PostgreSQL C02 integration")
    url = make_url(settings.database_url.get_secret_value())
    if (
        settings.app_environment != "test"
        or url.get_backend_name() != "postgresql"
        or not url.database
        or not url.database.endswith("_test")
    ):
        raise RuntimeError(
            "C02 integration requires PostgreSQL test environment and '_test' database"
        )
    command.upgrade(Config(toml_file="pyproject.toml"), "head")
    target = create_database_engine(settings)
    try:
        assert all(count == 0 for count in _counts(target).values()), "Refuse nonempty test target"
        yield target
    finally:
        target.dispose()


@pytest.fixture
def source(engine: Engine) -> Iterator[GeneratedDataset]:
    assert all(count == 0 for count in _counts(engine).values()), "Refuse nonempty test target"
    generated = _source()
    persist_dataset(engine, generated)
    try:
        yield generated
    finally:
        with engine.begin() as connection:
            ids = set(connection.scalars(select(DatasetVersion.dataset_version_id)))
            assert ids <= {generated.dataset_version.dataset_version_id}, (
                "Unexpected dataset; refuse cleanup"
            )
            for name in (*reversed(CANONICAL_TABLE_ORDER), "dataset_version"):
                table = Base.metadata.tables[name]
                connection.execute(
                    table.delete().where(
                        table.c.dataset_version_id == generated.dataset_version.dataset_version_id
                    )
                )
        assert all(count == 0 for count in _counts(engine).values())


def _order(source: GeneratedDataset) -> SalesOrder:
    return cast(
        SalesOrder,
        min(source.rows_for("fact_sales_order"), key=lambda row: cast(SalesOrder, row).order_at),
    )


def _run(
    source: GeneratedDataset,
    as_of: datetime | None = None,
    order_id: str | None = None,
    dataset_hash: str | None = None,
) -> DecisionRun:
    order = _order(source)
    at = as_of or order.order_at
    identity = {
        "order_id": order_id or order.sales_order_id,
        "as_of_time": at,
        "dataset_version": source.dataset_version.dataset_version_id,
        "dataset_hash": dataset_hash or source.content_hash,
        "contract_bundle_version": "w03-c01-v1",
        "tool_registry_version": "w03-c02-tools.v1",
    }
    return DecisionRun(
        run_id=derive_artifact_id("decision-run", "decision-run.v1", identity),
        schema_version="decision-run.v1",
        provenance=ArtifactProvenance(
            producer="test",
            producer_version="v1",
            input_artifact_ids=(),
            source_refs=(),
            contract_versions=(VersionRef(name="w03-c01", version="v1"),),
            implementation_sha=None,
        ),
        order_id=order_id or order.sales_order_id,
        as_of_time=at,
        dataset_version=source.dataset_version.dataset_version_id,
        dataset_hash=dataset_hash or source.content_hash,
        contract_bundle_version="w03-c01-v1",
        tool_registry_version="w03-c02-tools.v1",
    )


def test_no_active_dataset_fails_closed(engine: Engine) -> None:
    with pytest.raises(C02BuildError, match="NO_ACTIVE_DATASET"):
        build_decision_snapshot(engine, _run(_source()))


def test_read_only_replay_and_bounded_sql(engine: Engine, source: GeneratedDataset) -> None:
    run = _run(source)
    before_counts = _counts(engine)
    before_business = canonical_business_payload(read_active_dataset(engine).rows_by_table)
    statements: list[str] = []

    def collect(
        _conn: Any,
        _cursor: Any,
        statement: str,
        _parameters: Any,
        _context: Any,
        _executemany: bool,
    ) -> None:
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", collect)
    try:
        snapshot = build_decision_snapshot(engine, run)
        replay = build_decision_snapshot(engine, run)
    finally:
        event.remove(engine, "before_cursor_execute", collect)
    assert snapshot == replay
    assert canonical_json_bytes(snapshot) == canonical_json_bytes(replay)
    assert statements.count("SET TRANSACTION READ ONLY") == 2
    assert statements.count("SHOW transaction_isolation") == 2
    assert statements.count("SHOW transaction_read_only") == 2
    assert not any(
        text.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE", "MERGE"))
        for text in statements
    )
    assert not any(
        "fact_sales_order.status" in text
        or "fact_work_order.status" in text
        or "fact_operation.status" in text
        or "fact_purchase_order.status" in text
        for text in statements
    )
    assert any("CASE WHEN" in text.upper() for text in statements)
    assert {entry.source_ref.source_entity for entry in snapshot.entries} <= {
        "dim_product",
        "dim_customer",
        "dim_work_center",
        "dim_material",
        "dim_supplier",
        "bridge_product_material",
        "fact_sales_order",
        "fact_work_order",
        "fact_operation",
        "fact_material_requirement",
        "fact_purchase_order",
        "fact_inventory_snapshot",
        "fact_quality_inspection",
        "fact_rework",
        "fact_delivery",
    }
    assert {
        entry.source_ref.source_record_id
        for entry in snapshot.entries
        if entry.source_ref.source_entity == "fact_sales_order"
    } == {run.order_id}
    bundle = build_evidence_bundle(snapshot)
    context = build_decision_context(snapshot, bundle)
    assert bundle == build_evidence_bundle(replay)
    assert context == build_decision_context(replay, bundle)
    assert _counts(engine) == before_counts
    assert canonical_business_payload(read_active_dataset(engine).rows_by_table) == before_business


def test_target_pre_delivery_and_binding_failures(engine: Engine, source: GeneratedDataset) -> None:
    run = _run(source)
    snapshot = build_decision_snapshot(engine, run)
    assert not [
        entry for entry in snapshot.entries if entry.source_ref.source_entity == "fact_delivery"
    ]
    derived = {
        item.source_field: item.value
        for item in build_evidence_bundle(snapshot).evidence
        if item.source_entity == "c02_derivation"
    }
    assert derived["delivery_state_as_of"] == "NOT_DELIVERED_AS_OF"
    bad_cases = (
        (_run(source, dataset_hash="0" * 64), "DATASET_BINDING_MISMATCH"),
        (_run(source, order_id="SO-UNKNOWN"), "TARGET_ORDER_NOT_FOUND"),
        (
            _run(source, as_of=_order(source).order_at - timedelta(microseconds=1)),
            "TARGET_ORDER_NOT_AVAILABLE",
        ),
        (_run(source, as_of=datetime(2025, 12, 31, tzinfo=UTC)), "AS_OF_OUTSIDE_DATASET_HORIZON"),
    )
    for bad_run, code in bad_cases:
        with pytest.raises(C02BuildError, match=code):
            build_decision_snapshot(engine, bad_run)
    assert row_values(read_active_dataset(engine).dataset_version) == row_values(
        source.dataset_version
    )


def test_multiple_active_datasets_fail_closed(engine: Engine, source: GeneratedDataset) -> None:
    second_values = row_values(_source().dataset_version)
    second_values["dataset_version_id"] = "dsv_c02_second_for_binding_test"
    table = Base.metadata.tables["dataset_version"]
    with engine.begin() as connection:
        connection.execute(table.insert(), second_values)
    try:
        with pytest.raises(C02BuildError, match="MULTIPLE_ACTIVE_DATASETS"):
            build_decision_snapshot(engine, _run(source))
    finally:
        with engine.begin() as connection:
            connection.execute(
                table.delete().where(
                    table.c.dataset_version_id == second_values["dataset_version_id"]
                )
            )


@pytest.mark.parametrize(
    ("scenario", "expected_hash"),
    (
        ("supplier", "682dc4238ad146724068116b0e2ca93b291029670b537ecf9b7693e09a6ff3cb"),
        ("quality", "ef52d548ec704e21c5a4e0a034ac79d1167277fcd2e148253d08c5d069089093"),
        ("capacity", "f4b9848fb98ac834056e560e1dde690a0b3982a1ed5f8469b9a8157775106cee"),
        ("neutral", "d6c31ab8d68d9c4b1a735cfb4adea71931766907cc78db55763514d6cdb562e6"),
    ),
)
def test_scenario_business_dataset_projection(
    engine: Engine, scenario: str, expected_hash: str
) -> None:
    """Runtime receives only persisted business data, never scenario answers."""
    assert all(count == 0 for count in _counts(engine).values()), "Refuse nonempty test target"
    zone = ZoneInfo("Asia/Shanghai")
    seed = 2 if scenario == "quality" else 20260901
    start = datetime(2026, 1, 1 if scenario == "quality" else 15, tzinfo=zone)
    end = (
        datetime(2026, 3, 31, 23, 59, 59, tzinfo=zone)
        if scenario == "quality"
        else datetime(2026, 2, 12, tzinfo=zone)
    )
    config: ScenarioConfig
    if scenario == "supplier":
        config = SupplierDegradationConfig(
            scenario_version="1.0.0", scenario_seed=seed, window_start=start, window_end=end
        )
    elif scenario == "quality":
        config = QualityDeteriorationConfig(
            scenario_version="1.0.0", scenario_seed=seed, window_start=start, window_end=end
        )
    else:
        config = CapacitySurgeConfig(
            scenario_version="1.0.0",
            scenario_seed=seed,
            window_start=start,
            window_end=end,
            arrival_volume_multiplier=Decimal("1.0" if scenario == "neutral" else "1.5"),
            queue_time_multiplier=Decimal("1.0" if scenario == "neutral" else "1.7"),
        )
    business = apply_scenario(
        _source(), config, generated_at=datetime(2026, 8, 24, tzinfo=UTC)
    ).dataset
    assert business.content_hash == expected_hash
    persist_dataset(engine, business)
    try:
        run = _run(business, as_of=datetime(2026, 2, 20, tzinfo=zone))
        snapshot = build_decision_snapshot(engine, run)
        bundle = build_evidence_bundle(snapshot)
        context = build_decision_context(snapshot, bundle)
        assert snapshot.dataset_hash == expected_hash
        assert all(entry.available_at <= run.as_of_time for entry in snapshot.entries)
        assert all(item.available_at <= run.as_of_time for item in bundle.evidence)
        assert context.run_id == run.run_id
        assert snapshot == build_decision_snapshot(engine, run)
    finally:
        with engine.begin() as connection:
            ids = set(connection.scalars(select(DatasetVersion.dataset_version_id)))
            assert ids <= {business.dataset_version.dataset_version_id}
            for name in (*reversed(CANONICAL_TABLE_ORDER), "dataset_version"):
                table = Base.metadata.tables[name]
                connection.execute(
                    table.delete().where(
                        table.c.dataset_version_id == business.dataset_version.dataset_version_id
                    )
                )
        assert all(count == 0 for count in _counts(engine).values())
