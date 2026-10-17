"""C04 native PostgreSQL proof over business-only, isolated deterministic fixtures."""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, time, timedelta
from typing import cast

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import event, select
from sqlalchemy.engine import Engine, make_url
from test_decision_snapshot_database import _counts, _run, _source

from flowlens.config import Settings
from flowlens.data import Base
from flowlens.data.generation import GeneratedDataset
from flowlens.data.generation.canonical import CANONICAL_TABLE_ORDER, canonical_business_payload
from flowlens.data.models import DatasetVersion, SalesOrder, WorkOrder
from flowlens.data.persistence import persist_dataset, read_active_dataset, row_values
from flowlens.db import create_database_engine
from flowlens.decision.c04_registry import build_candidate_set
from flowlens.decision.c04_simulation import build_simulation_bundle
from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.context import build_decision_context
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.diagnosis import evaluate_c03
from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.primitives import EntityRef, ScalarValue, SnapshotEntry, SourceRef
from flowlens.decision.serialization import canonical_json_bytes, sha256_hex
from flowlens.decision.snapshot import build_state_snapshot, source_unknowns
from flowlens.decision.temporal import BUSINESS_TIMEZONE, SOURCE_FIELDS, project_record
from flowlens.decision.trust import classify_source
from flowlens.investigation import c04_navigation as navigation
from flowlens.investigation.c02_binding import build_investigation_case
from flowlens.investigation.c03_planning import (
    build_investigation_plan,
    build_investigation_questions,
)
from flowlens.investigation.c04_queries import C04EvidenceError, build_evidence_query_specs
from flowlens.investigation.contracts import (
    EvidenceObservation,
    EvidenceQuerySpec,
    EvidenceSlice,
    InvestigationCase,
    InvestigationPlan,
    InvestigationQuestion,
)

type Inputs = tuple[
    DecisionPacket,
    InvestigationCase,
    tuple[InvestigationQuestion, ...],
    InvestigationPlan,
]
EXPECTED_KEYS = {
    "dim_work_center": "work_center_id",
    "fact_delivery": "delivery_id",
    "fact_material_requirement": "material_requirement_id",
    "fact_operation": "operation_id",
    "fact_purchase_order": "purchase_order_id",
    "fact_quality_inspection": "inspection_id",
    "fact_rework": "rework_id",
    "fact_sales_order": "sales_order_id",
    "fact_work_order": "work_order_id",
}
EXPECTED_PROFILES = tuple(EXPECTED_KEYS)

pytestmark = pytest.mark.integration


def _error(action: Callable[[], object], code: str) -> None:
    with pytest.raises(C04EvidenceError) as caught:
        action()
    assert caught.value.code == str(caught.value) == code


@pytest.fixture(scope="module")
def engine() -> Iterator[Engine]:
    try:
        settings = Settings()
    except ValidationError:
        if os.environ.get("FLOWLENS_DATABASE_URL"):
            raise
        pytest.skip("FLOWLENS_DATABASE_URL required for PostgreSQL C04 integration")
    url = make_url(settings.database_url.get_secret_value())
    if (
        settings.app_environment != "test"
        or url.get_backend_name() != "postgresql"
        or not url.database
        or not url.database.endswith("_test")
    ):
        raise RuntimeError(
            "C04 integration requires PostgreSQL test environment and '_test' database"
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
                "Refuse unexpected cleanup"
            )
            for name in (*reversed(CANONICAL_TABLE_ORDER), "dataset_version"):
                table = Base.metadata.tables[name]
                connection.execute(
                    table.delete().where(
                        table.c.dataset_version_id == generated.dataset_version.dataset_version_id,
                    )
                )
        assert all(count == 0 for count in _counts(engine).values())


def _business_rows(source: GeneratedDataset) -> dict[str, tuple[dict[str, ScalarValue], ...]]:
    return {
        family: tuple(
            {name: cast(ScalarValue, value) for name, value in row_values(row).items()}
            for row in source.rows_for(family)
        )
        for family in EXPECTED_PROFILES
    }


def _graph(
    source: GeneratedDataset,
    root: str,
) -> dict[str, tuple[dict[str, ScalarValue], ...]]:
    rows = _business_rows(source)
    version = source.dataset_version.dataset_version_id
    owned = {
        family: tuple(row for row in records if row["dataset_version_id"] == version)
        for family, records in rows.items()
    }
    work = tuple(row for row in owned["fact_work_order"] if row["sales_order_id"] == root)
    work_ids = {row["work_order_id"] for row in work}
    operations = tuple(row for row in owned["fact_operation"] if row["work_order_id"] in work_ids)
    requirements = tuple(
        row for row in owned["fact_material_requirement"] if row["work_order_id"] in work_ids
    )
    materials = {row["material_id"] for row in requirements}
    centers = {row["work_center_id"] for row in operations}
    selected = {
        "fact_sales_order": tuple(
            row for row in owned["fact_sales_order"] if row["sales_order_id"] == root
        ),
        "fact_work_order": work,
        "fact_operation": operations,
        "fact_material_requirement": requirements,
        "fact_purchase_order": tuple(
            row for row in owned["fact_purchase_order"] if row["material_id"] in materials
        ),
        "fact_quality_inspection": tuple(
            row for row in owned["fact_quality_inspection"] if row["work_order_id"] in work_ids
        ),
        "fact_rework": tuple(
            row for row in owned["fact_rework"] if row["work_order_id"] in work_ids
        ),
        "fact_delivery": tuple(
            row for row in owned["fact_delivery"] if row["sales_order_id"] == root
        ),
        "dim_work_center": tuple(
            row for row in owned["dim_work_center"] if row["work_center_id"] in centers
        ),
    }
    return {
        family: tuple(sorted(records, key=lambda row: str(row[EXPECTED_KEYS[family]])))
        for family, records in selected.items()
    }


def _inputs_for(
    source: GeneratedDataset,
    root: str,
    as_of: datetime,
    *,
    dataset_hash: str | None = None,
) -> Inputs:
    # Use actual target facts and the frozen public W03 builders. The intentionally
    # incomplete decision-time snapshot selects all C03 source families without
    # HGT selection, signal replacement or changes to any accepted rule.
    order = next(
        cast(SalesOrder, row)
        for row in source.rows_for("fact_sales_order")
        if cast(SalesOrder, row).sales_order_id == root
    )
    fields = row_values(order)
    run = _run(source, as_of, root, dataset_hash)
    projected = project_record(
        "fact_sales_order",
        root,
        {name: cast(ScalarValue, fields[name]) for name in SOURCE_FIELDS["fact_sales_order"]},
        as_of_time=as_of,
        period_start=source.dataset_version.period_start,
        target_order_at=order.order_at,
    )
    snapshot = build_state_snapshot(run, projected, source_unknowns(0, 0, (), ()))
    evidence = build_evidence_bundle(snapshot)
    context = build_decision_context(snapshot, evidence)
    signals, diagnosis = evaluate_c03(evidence, context)
    candidates = build_candidate_set(evidence, context, signals, diagnosis)
    simulations = build_simulation_bundle(
        run, snapshot, evidence, context, signals, diagnosis, candidates
    )
    packet = build_decision_packet(
        run, snapshot, evidence, context, signals, diagnosis, candidates, simulations
    )
    case = build_investigation_case(packet)
    questions = build_investigation_questions(packet, case)
    return packet, case, questions, build_investigation_plan(packet, case, questions)


def _all_family_root(source: GeneratedDataset) -> str:
    rows = _business_rows(source)
    by_work = {row["work_order_id"]: row["sales_order_id"] for row in rows["fact_work_order"]}
    rework = {str(by_work[row["work_order_id"]]) for row in rows["fact_rework"]}
    delivered = {str(row["sales_order_id"]) for row in rows["fact_delivery"]}
    roots = sorted(rework & delivered)
    assert roots, "The deterministic business fixture must exercise all nine adapters"
    return roots[0]


def _expected(
    source: GeneratedDataset,
    inputs: Inputs,
    queries: tuple[EvidenceQuerySpec, ...],
) -> tuple[EvidenceSlice, ...]:
    packet, case, _, _ = inputs
    graph = _graph(source, case.subject_id)
    order_at = cast(datetime, graph["fact_sales_order"][0]["order_at"])
    slices: list[EvidenceSlice] = []
    for query in queries:
        observations: dict[str, EvidenceObservation] = {}
        family = query.source_family_code
        for row in graph[family]:
            record = cast(str, row[EXPECTED_KEYS[family]])
            projected = project_record(
                family,
                record,
                {name: row[name] for name in SOURCE_FIELDS[family]},
                as_of_time=case.as_of_time,
                period_start=source.dataset_version.period_start,
                target_order_at=order_at,
            )
            for field in projected:
                if field.source_field not in query.requested_fields:
                    continue
                ref = SourceRef(
                    source_entity=family,
                    source_record_id=record,
                    source_field=field.source_field,
                    observed_at=field.observed_at,
                    available_at=field.available_at,
                )
                entry = SnapshotEntry(
                    entry_key=f"{family}|{record}|{field.source_field}",
                    entity=EntityRef(entity_type=family, entity_id=record),
                    field=field.source_field,
                    value=field.value,
                    observed_at=field.observed_at,
                    available_at=field.available_at,
                    source_ref=ref,
                )
                relationship, trust, freshness, _ = classify_source(entry, case.as_of_time)
                assert relationship == query.expected_relationship_code
                assert (trust,) == query.allowed_trust_classes
                obs = EvidenceObservation(
                    source_family_code=family,
                    source_record_id=record,
                    source_field=field.source_field,
                    source_value=field.value,
                    event_time=field.observed_at,
                    available_at=field.available_at,
                    freshness_code=freshness.value,
                    trust_class=trust,
                    relationship_code=relationship,
                    provenance_ref="c04prov_"
                    + sha256_hex(
                        {
                            "navigation_contract_version": "w04-c04-navigation-v1",
                            "dataset_version": packet.run.dataset_version,
                            "dataset_hash": packet.run.dataset_hash,
                            "source_family_code": family,
                            "source_record_id": record,
                            "source_field": field.source_field,
                            "source_value": field.value,
                            "event_time": field.observed_at,
                            "available_at": field.available_at,
                            "freshness_code": freshness.value,
                            "trust_class": trust,
                            "relationship_code": relationship,
                        }
                    ),
                )
                observations[obs.artifact_id] = obs
        slices.append(
            EvidenceSlice(
                case_id=query.case_id,
                plan_id=query.plan_id,
                step_id=query.step_id,
                question_id=query.question_id,
                query_id=query.artifact_id,
                as_of_time=query.as_of_time,
                observations=tuple(observations[key] for key in sorted(observations)),
            )
        )
    return tuple(slices)


@contextmanager
def _capture(engine: Engine) -> Iterator[list[str]]:
    statements: list[str] = []

    def collect(
        _connection: object,
        _cursor: object,
        statement: str,
        _parameters: object,
        _context: object,
        _executemany: bool,
    ) -> None:
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", collect)
    try:
        yield statements
    finally:
        event.remove(engine, "before_cursor_execute", collect)


def _assert_runtime_sql(statements: list[str]) -> None:
    assert "SET TRANSACTION READ ONLY" in statements
    assert "SHOW transaction_isolation" in statements
    assert "SHOW transaction_read_only" in statements
    assert "SELECT version_num FROM alembic_version" in statements
    for sql in statements:
        assert sql.startswith(("SELECT ", "SET TRANSACTION READ ONLY", "SHOW "))
        assert not re.search(
            r"\b(?:INSERT|UPDATE|DELETE|ALTER|DROP|CREATE|TRUNCATE|COPY|status)\b", sql
        )
        if sql.startswith("SELECT DISTINCT"):
            assert "LIMIT " in sql and "ORDER BY " in sql
        assert not any(
            name in sql for name in ("fact_inventory_snapshot", "dim_supplier", "dim_material")
        )


def test_n19_n24_n32_n43_n51_all_adapters_native_replay_and_zero_mutation(
    engine: Engine,
    source: GeneratedDataset,
) -> None:
    root = _all_family_root(source)
    as_of = datetime.combine(source.dataset_version.period_end, time.max, BUSINESS_TIMEZONE)
    inputs = _inputs_for(source, root, as_of)
    queries = build_evidence_query_specs(*inputs)
    counts = _counts(engine)
    business = canonical_business_payload(read_active_dataset(engine).rows_by_table)
    input_bytes = canonical_json_bytes(inputs)
    expected = _expected(source, inputs, queries)
    with _capture(engine) as statements:
        first = navigation.execute_evidence_navigation(engine, *inputs, queries)
        second = navigation.execute_evidence_navigation(engine, *inputs, queries)
        navigation.validate_evidence_navigation(engine, *inputs, queries, first)
        restored = tuple(EvidenceSlice.from_json(item.to_json()) for item in first)
        navigation.validate_evidence_navigation(engine, *inputs, queries, restored)
    assert (
        canonical_json_bytes(first)
        == canonical_json_bytes(second)
        == canonical_json_bytes(expected)
    )
    assert {obs.source_family_code for item in first for obs in item.observations} == set(
        EXPECTED_PROFILES
    )
    assert (
        len(queries) == 18
        and len({(q.source_family_code, q.requested_fields) for q in queries}) == 11
    )
    assert all(obs.available_at <= as_of for item in first for obs in item.observations)
    _assert_runtime_sql(statements)
    assert statements.count("SET TRANSACTION READ ONLY") == 4
    assert sum(sql.startswith("SELECT DISTINCT") for sql in statements) == 4 * len(queries)
    assert _counts(engine) == counts
    assert canonical_business_payload(read_active_dataset(engine).rows_by_table) == business
    assert read_active_dataset(engine).content_hash == source.content_hash
    assert canonical_json_bytes(inputs) == input_bytes


def _event_case(source: GeneratedDataset, family: str, gate: str) -> tuple[str, datetime, str]:
    rows = _business_rows(source)
    orders = {row["sales_order_id"]: row for row in rows["fact_sales_order"]}
    works = {row["work_order_id"]: row for row in rows["fact_work_order"]}
    for row in rows[family]:
        at = row[gate]
        if at is None:
            continue
        assert isinstance(at, datetime)
        if family in ("fact_work_order", "fact_delivery"):
            roots: tuple[str, ...] = (str(row["sales_order_id"]),)
        elif family == "fact_purchase_order":
            roots = tuple(
                sorted(
                    {
                        str(works[req["work_order_id"]]["sales_order_id"])
                        for req in rows["fact_material_requirement"]
                        if req["material_id"] == row["material_id"]
                    }
                )
            )
        else:
            roots = (str(works[row["work_order_id"]]["sales_order_id"]),)
        as_of = at - timedelta(microseconds=1)
        for root in roots:
            if cast(datetime, orders[root]["order_at"]) > as_of or not (
                source.dataset_version.period_start
                <= as_of.astimezone(BUSINESS_TIMEZONE).date()
                <= source.dataset_version.period_end
            ):
                continue
            if (
                family == "fact_purchase_order"
                and gate == "actual_receipt_at"
                and cast(
                    datetime,
                    row["ordered_at"],
                )
                > as_of
            ):
                continue
            if (
                family == "fact_rework"
                and gate == "rework_end_at"
                and cast(
                    datetime,
                    row["rework_start_at"],
                )
                > as_of
            ):
                continue
            return root, as_of, cast(str, row[EXPECTED_KEYS[family]])
    raise AssertionError("The deterministic business fixture must cover this future gate")


@pytest.mark.parametrize(
    "family,gate,blocked",
    [
        (
            "fact_work_order",
            "actual_start_at",
            {"actual_start_at", "actual_end_at", "completed_quantity"},
        ),
        ("fact_work_order", "actual_end_at", {"actual_end_at", "completed_quantity"}),
        ("fact_operation", "actual_start_at", {"actual_start_at", "actual_end_at"}),
        ("fact_operation", "actual_end_at", {"actual_end_at"}),
        ("fact_purchase_order", "actual_receipt_at", {"actual_receipt_at", "received_quantity"}),
        ("fact_rework", "rework_end_at", {"rework_end_at"}),
    ],
)
def test_n35_n37_actual_future_values_are_sql_masked_and_not_emitted(
    engine: Engine,
    source: GeneratedDataset,
    family: str,
    gate: str,
    blocked: set[str],
) -> None:
    root, as_of, record = _event_case(source, family, gate)
    inputs = _inputs_for(source, root, as_of)
    queries = build_evidence_query_specs(*inputs)
    with _capture(engine) as statements:
        slices = navigation.execute_evidence_navigation(engine, *inputs, queries)
    actual = {
        obs.source_field
        for item in slices
        for obs in item.observations
        if obs.source_family_code == family and obs.source_record_id == record
    }
    assert actual and actual.isdisjoint(blocked)
    assert canonical_json_bytes(slices) == canonical_json_bytes(_expected(source, inputs, queries))
    assert any("CASE WHEN" in sql and f"{family}.{gate} <= " in sql for sql in statements)
    _assert_runtime_sql(statements)


@pytest.mark.parametrize(
    "family,gate",
    [
        ("fact_quality_inspection", "inspection_at"),
        ("fact_rework", "rework_start_at"),
        ("fact_delivery", "delivery_at"),
        ("fact_purchase_order", "ordered_at"),
    ],
)
def test_n38_event_rows_after_decision_time_are_excluded_in_sql(
    engine: Engine,
    source: GeneratedDataset,
    family: str,
    gate: str,
) -> None:
    root, as_of, record = _event_case(source, family, gate)
    inputs = _inputs_for(source, root, as_of)
    queries = build_evidence_query_specs(*inputs)
    with _capture(engine) as statements:
        slices = navigation.execute_evidence_navigation(engine, *inputs, queries)
    assert not any(
        obs.source_family_code == family and obs.source_record_id == record
        for item in slices
        for obs in item.observations
    )
    assert canonical_json_bytes(slices) == canonical_json_bytes(_expected(source, inputs, queries))
    assert any(f"{family}.{gate} <= " in sql for sql in statements)
    _assert_runtime_sql(statements)


def test_n39_n47_n49_known_future_plan_and_empty_actual_profiles(
    engine: Engine,
    source: GeneratedDataset,
) -> None:
    root, as_of, record = _event_case(source, "fact_work_order", "actual_start_at")
    inputs = _inputs_for(source, root, as_of)
    queries = build_evidence_query_specs(*inputs)
    slices = navigation.execute_evidence_navigation(engine, *inputs, queries)
    assert canonical_json_bytes(slices) == canonical_json_bytes(_expected(source, inputs, queries))
    for query, item in zip(queries, slices, strict=True):
        assert item.query_id == query.artifact_id and item.as_of_time == as_of
        if (
            query.source_family_code == "fact_work_order"
            and query.expected_relationship_code == "DIRECT_EVENT"
        ):
            assert not any(obs.source_record_id == record for obs in item.observations)
    assert any(
        obs.source_family_code == "fact_work_order"
        and obs.source_field == "planned_end_at"
        and cast(datetime, obs.source_value) > as_of
        and obs.available_at <= as_of
        for item in slices
        for obs in item.observations
    )


@pytest.mark.parametrize("cap", ["records", "observations"])
def test_n34_native_bounded_query_and_scaled_cap_failure(
    engine: Engine,
    source: GeneratedDataset,
    monkeypatch: pytest.MonkeyPatch,
    cap: str,
) -> None:
    inputs = _inputs_for(
        source,
        _all_family_root(source),
        datetime.combine(
            source.dataset_version.period_end,
            time.max,
            BUSINESS_TIMEZONE,
        ),
    )
    queries = build_evidence_query_specs(*inputs)
    before = canonical_business_payload(read_active_dataset(engine).rows_by_table)
    monkeypatch.setattr(
        navigation,
        "C04_MAX_RECORDS_PER_QUERY" if cap == "records" else "C04_MAX_OBSERVATIONS_PER_SLICE",
        1 if cap == "records" else 5,
    )
    with _capture(engine) as statements:
        _error(
            lambda: navigation.execute_evidence_navigation(engine, *inputs, queries),
            "C04_RESULT_LIMIT_EXCEEDED",
        )
    _assert_runtime_sql(statements)
    assert canonical_business_payload(read_active_dataset(engine).rows_by_table) == before


def test_n21_native_hash_context_failure_is_read_only(
    engine: Engine, source: GeneratedDataset
) -> None:
    inputs = _inputs_for(
        source,
        _all_family_root(source),
        datetime.combine(
            source.dataset_version.period_end,
            time.max,
            BUSINESS_TIMEZONE,
        ),
        dataset_hash="b" * 64,
    )
    queries = build_evidence_query_specs(*inputs)
    before = _counts(engine)
    with _capture(engine) as statements:
        _error(
            lambda: navigation.execute_evidence_navigation(engine, *inputs, queries),
            "C04_SOURCE_CONTEXT_MISMATCH",
        )
    _assert_runtime_sql(statements)
    assert not any(sql.startswith("SELECT DISTINCT") for sql in statements)
    assert _counts(engine) == before


def test_n23_foreign_owned_join_row_cannot_enter_a_single_dataset_context(
    engine: Engine,
    source: GeneratedDataset,
) -> None:
    root = _all_family_root(source)
    inputs = _inputs_for(
        source,
        root,
        datetime.combine(source.dataset_version.period_end, time.max, BUSINESS_TIMEZONE),
    )
    queries = build_evidence_query_specs(*inputs)
    before = _counts(engine)
    foreign_id = "c04-cross-dataset-fixture"
    foreign_work = "c04-cross-dataset-work-order"
    work = next(
        cast(WorkOrder, row)
        for row in source.rows_for("fact_work_order")
        if cast(WorkOrder, row).sales_order_id == root
    )
    # This DML belongs only to explicitly isolated test fixture setup/cleanup;
    # capture and the C04 runtime span below contain controls and reads only.
    with engine.begin() as connection:
        connection.execute(
            Base.metadata.tables["dataset_version"]
            .insert()
            .values(
                **dict(row_values(source.dataset_version), dataset_version_id=foreign_id),
            )
        )
        connection.execute(
            Base.metadata.tables["fact_work_order"]
            .insert()
            .values(
                **dict(row_values(work), dataset_version_id=foreign_id, work_order_id=foreign_work),
            )
        )
    try:
        with _capture(engine) as statements:
            _error(
                lambda: navigation.execute_evidence_navigation(engine, *inputs, queries),
                "C04_SOURCE_CONTEXT_MISMATCH",
            )
        _assert_runtime_sql(statements)
        assert not any(sql.startswith("SELECT DISTINCT") for sql in statements)
    finally:
        with engine.begin() as connection:
            ids = set(connection.scalars(select(DatasetVersion.dataset_version_id)))
            assert ids <= {source.dataset_version.dataset_version_id, foreign_id}
            connection.execute(
                Base.metadata.tables["fact_work_order"]
                .delete()
                .where(
                    WorkOrder.dataset_version_id == foreign_id,
                    WorkOrder.work_order_id == foreign_work,
                )
            )
            connection.execute(
                Base.metadata.tables["dataset_version"]
                .delete()
                .where(
                    DatasetVersion.dataset_version_id == foreign_id,
                )
            )
    assert _counts(engine) == before


@pytest.mark.parametrize("field", ["source_value", "provenance_ref"])
def test_n50_rehashed_native_evidence_is_rejected_without_mutation(
    engine: Engine,
    source: GeneratedDataset,
    field: str,
) -> None:
    inputs = _inputs_for(
        source,
        _all_family_root(source),
        datetime.combine(
            source.dataset_version.period_end,
            time.max,
            BUSINESS_TIMEZONE,
        ),
    )
    queries = build_evidence_query_specs(*inputs)
    slices = navigation.execute_evidence_navigation(engine, *inputs, queries)
    first = slices[0]
    obs = (
        replace(first.observations[0], source_value="FORGED_C04_VALUE")
        if field == "source_value"
        else replace(first.observations[0], provenance_ref="c04prov_" + "b" * 64)
    )
    forged = replace(
        first,
        observations=tuple(
            sorted(
                (obs, *first.observations[1:]),
                key=lambda item: item.artifact_id,
            )
        ),
    )
    before = canonical_business_payload(read_active_dataset(engine).rows_by_table)
    with _capture(engine) as statements:
        _error(
            lambda: navigation.validate_evidence_navigation(
                engine,
                *inputs,
                queries,
                (forged, *slices[1:]),
            ),
            "C04_EVIDENCE_BINDING_MISMATCH",
        )
    _assert_runtime_sql(statements)
    assert canonical_business_payload(read_active_dataset(engine).rows_by_table) == before


@pytest.mark.parametrize(
    "family,gate",
    [
        ("fact_work_order", "actual_start_at"),
        ("fact_operation", "actual_end_at"),
        ("fact_purchase_order", "actual_receipt_at"),
        ("fact_rework", "rework_end_at"),
    ],
)
def test_n40_exact_event_time_boundary_is_admitted(
    engine: Engine,
    source: GeneratedDataset,
    family: str,
    gate: str,
) -> None:
    root, before_event, record = _event_case(source, family, gate)
    as_of = before_event + timedelta(microseconds=1)
    inputs = _inputs_for(source, root, as_of)
    queries = build_evidence_query_specs(*inputs)
    slices = navigation.execute_evidence_navigation(engine, *inputs, queries)
    assert any(
        obs.source_family_code == family
        and obs.source_record_id == record
        and obs.source_field == gate
        and obs.available_at == as_of
        for item in slices
        for obs in item.observations
    )
    assert canonical_json_bytes(slices) == canonical_json_bytes(_expected(source, inputs, queries))
