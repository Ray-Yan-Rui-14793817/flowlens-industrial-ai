"""Simulation gates, typed failures, measurements, and config binding for W03-C04."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from types import MappingProxyType
from typing import NoReturn, cast

import pytest

from flowlens.data import Base
from flowlens.data.generation import (
    BUSINESS_TIMEZONE,
    GeneratedDataset,
    GenerationConfig,
    GenerationProfile,
    generate_baseline,
)
from flowlens.data.generation.canonical import (
    CANONICAL_TABLE_ORDER,
    canonical_business_payload,
    canonical_content_hash,
    canonicalize_rows,
)
from flowlens.data.models import (
    DatasetVersion,
    Delivery,
    Material,
    PurchaseOrder,
    SalesOrder,
    Supplier,
    WorkOrder,
)
from flowlens.data.scenarios.config import (
    CapacitySurgeConfig,
    QualityDeteriorationConfig,
    SupplierDegradationConfig,
)
from flowlens.data.scenarios.transformer import (
    ScenarioPreconditionUnavailable,
    _clone_row,
)
from flowlens.decision import c04_simulation as implementation
from flowlens.decision.c04_registry import build_candidate_set
from flowlens.decision.c04_simulation import build_simulation_bundle
from flowlens.decision.c04_validation import C04BuildError
from flowlens.decision.context import DecisionContext, build_decision_context
from flowlens.decision.contracts import (
    CandidateSet,
    DecisionRun,
    DiagnosisRecord,
    EvidenceBundle,
    SignalBundle,
    SimulationBundle,
    SimulationResult,
    StateSnapshot,
)
from flowlens.decision.diagnosis import evaluate_c03
from flowlens.decision.enums import InterventionFamily, SimulationStatus
from flowlens.decision.evidence import build_evidence_bundle
from flowlens.decision.serialization import canonical_json_bytes, derive_artifact_id
from flowlens.decision.snapshot import build_state_snapshot, source_unknowns
from flowlens.decision.temporal import ProjectedSourceField, project_record
from test_c04_registry import make_c04_fixture
from test_decision_snapshot import ORDER_AT, PERIOD_START, make_run, sample_records

MEASUREMENT_NAMES = (
    "affected_entity_count",
    "business_row_count_delta",
    "target_delivered_quantity",
    "target_delivery_lag_seconds",
    "target_failed_quantity",
    "target_last_delivery_at",
    "target_max_operation_start_slippage_seconds",
    "target_max_work_order_completion_slippage_seconds",
    "target_remaining_quantity",
    "target_rework_quantity",
)
MEASUREMENT_SCHEMA = (
    ("affected_entity_count", "count"),
    ("business_row_count_delta", "count"),
    ("target_delivered_quantity", "unit"),
    ("target_delivery_lag_seconds", "s"),
    ("target_failed_quantity", "unit"),
    ("target_last_delivery_at", None),
    ("target_max_operation_start_slippage_seconds", "s"),
    ("target_max_work_order_completion_slippage_seconds", "s"),
    ("target_remaining_quantity", "unit"),
    ("target_rework_quantity", "unit"),
)

C04Fixture = tuple[
    StateSnapshot,
    EvidenceBundle,
    DecisionContext,
    SignalBundle,
    DiagnosisRecord,
    CandidateSet,
]


def closed_baseline() -> GeneratedDataset:
    source = generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.TEST,
            seed=20_260_824,
            period_start=datetime(2026, 1, 1).date(),
            generator_version="0.1.0-c03",
            generated_at=datetime(2026, 8, 24, 9, tzinfo=BUSINESS_TIMEZONE),
        )
    )
    rows: dict[str, list[Base]] = {
        table: [
            _clone_row(row, source.dataset_version.dataset_version_id)
            for row in source.rows_for(table)
        ]
        for table in CANONICAL_TABLE_ORDER
    }
    closed_at = datetime.combine(source.dataset_version.period_end, time.max, BUSINESS_TIMEZONE)
    for purchase_order in cast(list[PurchaseOrder], rows["fact_purchase_order"]):
        if (
            purchase_order.actual_receipt_at is not None
            and purchase_order.actual_receipt_at > closed_at
        ):
            purchase_order.actual_receipt_at = None
            purchase_order.received_quantity = Decimal(0)
            purchase_order.status = "OPEN"
    ordered = canonicalize_rows(rows)
    metadata = source.dataset_version
    version = DatasetVersion(
        dataset_version_id=metadata.dataset_version_id,
        seed=metadata.seed,
        generator_version=metadata.generator_version,
        profile=metadata.profile,
        period_start=metadata.period_start,
        period_end=metadata.period_end,
        generated_at=metadata.generated_at,
        content_hash=canonical_content_hash(ordered),
        row_count_total=sum(len(items) for items in ordered.values()),
    )
    return GeneratedDataset(version, MappingProxyType(ordered))


def closed_fixture() -> tuple[GeneratedDataset, DecisionRun, C04Fixture]:
    baseline = closed_baseline()
    as_of = datetime.combine(baseline.dataset_version.period_end, time.max, BUSINESS_TIMEZONE)
    run = make_run(
        as_of,
        dataset_version=baseline.dataset_version.dataset_version_id,
        dataset_hash=baseline.dataset_version.content_hash,
    )
    fixture = make_c04_fixture(
        as_of=as_of,
        dataset_version=baseline.dataset_version.dataset_version_id,
        dataset_hash=baseline.dataset_version.content_hash,
    )
    return baseline, run, fixture


def successful_baseline() -> GeneratedDataset:
    """Build a closed, contract-valid fixture accepted by all three W2 stress probes."""

    source = generate_baseline(
        GenerationConfig(
            profile=GenerationProfile.TEST,
            seed=20_260_824,
            period_start=date(2026, 1, 1),
            generator_version="0.1.0-c03",
            generated_at=datetime(2026, 8, 24, 9, tzinfo=BUSINESS_TIMEZONE),
        )
    )
    dataset_id = source.dataset_version.dataset_version_id
    rows: dict[str, list[Base]] = {
        table: [_clone_row(row, dataset_id) for row in source.rows_for(table)]
        for table in CANONICAL_TABLE_ORDER
    }

    sales_orders = cast(list[SalesOrder], rows["fact_sales_order"])
    source_order_id = sales_orders[0].sales_order_id
    sales_orders[0].sales_order_id = "SO-1"
    for work_order in cast(list[WorkOrder], rows["fact_work_order"]):
        if work_order.sales_order_id == source_order_id:
            work_order.sales_order_id = "SO-1"
    for delivery in cast(list[Delivery], rows["fact_delivery"]):
        if delivery.sales_order_id == source_order_id:
            delivery.sales_order_id = "SO-1"

    supplier_id = cast(list[Supplier], rows["dim_supplier"])[0].supplier_id
    history_at = datetime(2025, 12, 1, 9, tzinfo=BUSINESS_TIMEZONE)
    for ordinal, material in enumerate(cast(list[Material], rows["dim_material"])):
        rows["fact_purchase_order"].append(
            PurchaseOrder(
                dataset_version_id=dataset_id,
                purchase_order_id=f"po_c04_history_{ordinal:04d}",
                supplier_id=supplier_id,
                material_id=material.material_id,
                ordered_at=history_at,
                promised_receipt_at=history_at + timedelta(days=1),
                actual_receipt_at=history_at + timedelta(days=1),
                ordered_quantity=Decimal("100"),
                received_quantity=Decimal("100"),
                status="RECEIVED",
            )
        )

    ordered = canonicalize_rows(rows)
    metadata = source.dataset_version
    version = DatasetVersion(
        dataset_version_id=dataset_id,
        seed=metadata.seed,
        generator_version=metadata.generator_version,
        profile=metadata.profile,
        period_start=metadata.period_start,
        period_end=date(2026, 4, 2),
        generated_at=metadata.generated_at,
        content_hash=canonical_content_hash(ordered),
        row_count_total=sum(len(items) for items in ordered.values()),
    )
    return GeneratedDataset(version, MappingProxyType(ordered))


def successful_fixture() -> tuple[GeneratedDataset, DecisionRun, C04Fixture]:
    baseline = successful_baseline()
    run, fixture = fixture_for_baseline_order(
        baseline,
        "so_9c21c51c1ed7_00000003",
    )
    return baseline, run, fixture


def fixture_for_baseline_order(
    baseline: GeneratedDataset, order_id: str
) -> tuple[DecisionRun, C04Fixture]:
    """Build canonical C02/C03 artifacts for a real order in a supplied baseline."""

    as_of = datetime.combine(baseline.dataset_version.period_end, time.max, BUSINESS_TIMEZONE)
    template = make_run(
        as_of,
        dataset_version=baseline.dataset_version.dataset_version_id,
        dataset_hash=baseline.dataset_version.content_hash,
    )
    identity = {
        "order_id": order_id,
        "as_of_time": as_of,
        "dataset_version": baseline.dataset_version.dataset_version_id,
        "dataset_hash": baseline.dataset_version.content_hash,
        "contract_bundle_version": template.contract_bundle_version,
        "tool_registry_version": template.tool_registry_version,
    }
    run = DecisionRun(
        run_id=derive_artifact_id("decision-run", "decision-run.v1", identity),
        schema_version="decision-run.v1",
        order_id=order_id,
        as_of_time=as_of,
        dataset_version=baseline.dataset_version.dataset_version_id,
        dataset_hash=baseline.dataset_version.content_hash,
        contract_bundle_version=template.contract_bundle_version,
        tool_registry_version=template.tool_registry_version,
        provenance=template.provenance,
    )
    projected: list[ProjectedSourceField] = []
    for entity, record_id, source_fields in sample_records():
        fields = {
            name: order_id if value == "SO-1" else value
            for name, value in source_fields.items()
        }
        selected_id = order_id if entity == "fact_sales_order" else record_id
        projected.extend(
            project_record(
                entity,
                selected_id,
                fields,
                as_of_time=as_of,
                period_start=PERIOD_START,
                target_order_at=ORDER_AT,
            )
        )
    observed_rows = {(item.source_entity, item.source_record_id) for item in projected}
    required_materials = tuple(
        str(item.value)
        for item in projected
        if item.source_entity == "fact_material_requirement"
        and item.source_field == "material_id"
    )
    inventory_materials = tuple(
        str(item.value)
        for item in projected
        if item.source_entity == "fact_inventory_snapshot"
        and item.source_field == "material_id"
    )
    unknowns = source_unknowns(
        sum(entity == "fact_work_order" for entity, _ in observed_rows),
        sum(entity == "fact_material_requirement" for entity, _ in observed_rows),
        required_materials,
        inventory_materials,
    )
    snapshot = build_state_snapshot(run, projected, unknowns)
    evidence = build_evidence_bundle(snapshot)
    context = build_decision_context(snapshot, evidence)
    signals, diagnosis = evaluate_c03(evidence, context)
    candidates = build_candidate_set(evidence, context, signals, diagnosis)
    return run, (snapshot, evidence, context, signals, diagnosis, candidates)


def result_by_family(
    bundle: SimulationBundle, candidates: CandidateSet
) -> dict[InterventionFamily, SimulationResult]:
    family_by_id = {item.candidate_id: item.family for item in candidates.candidates}
    return {family_by_id[item.candidate_id]: item for item in bundle.results}


def build_with(
    baseline: GeneratedDataset, run: DecisionRun, fixture: C04Fixture
) -> tuple[SimulationBundle, CandidateSet]:
    snapshot, evidence, context, signals, diagnosis, candidates = fixture
    bundle = build_simulation_bundle(
        run,
        snapshot,
        evidence,
        context,
        signals,
        diagnosis,
        candidates,
        baseline=baseline,
    )
    return bundle, candidates


def test_no_action_is_neutral_stable_and_has_exact_raw_measurement_schema() -> None:
    snapshot, evidence, context, signals, diagnosis, candidates = make_c04_fixture()
    run = make_run()
    first = build_simulation_bundle(
        run, snapshot, evidence, context, signals, diagnosis, candidates
    )
    second = build_simulation_bundle(
        run, snapshot, evidence, context, signals, diagnosis, candidates
    )
    assert first == second
    by_family = result_by_family(first, candidates)
    neutral = by_family[InterventionFamily.NO_ACTION]
    assert neutral.status is SimulationStatus.SUCCEEDED
    assert neutral.scenario_id is None and neutral.scenario_hash is None
    assert neutral.affected_entities == ()
    assert tuple(item.name for item in neutral.measurements) == MEASUREMENT_NAMES
    for family in set(InterventionFamily) - {InterventionFamily.NO_ACTION}:
        unavailable = by_family[family]
        assert unavailable.status is SimulationStatus.UNAVAILABLE
        assert {item.code for item in unavailable.limitations} >= {
            "C04_SIMULATION_BASELINE_NOT_SUPPLIED"
        }


def test_all_three_stress_probe_families_succeed_with_exact_artifact_bindings() -> None:
    baseline, run, fixture = successful_fixture()
    snapshot, _, _, _, _, candidates = fixture
    before = (
        baseline.dataset_version.content_hash,
        baseline.dataset_version.row_count_total,
        canonical_business_payload(baseline.rows_by_table),
    )

    first, _ = build_with(baseline, run, fixture)
    second, _ = build_with(baseline, run, fixture)

    assert first == second
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert first.run_id == run.run_id
    assert first.snapshot_id == snapshot.snapshot_id
    assert tuple((item.candidate_id, item.simulation_id) for item in first.results) == tuple(
        sorted((item.candidate_id, item.simulation_id) for item in first.results)
    )
    by_family = result_by_family(first, candidates)
    candidate_by_family = {item.family: item for item in candidates.candidates}
    for family in (
        InterventionFamily.SUPPLIER_INTERVENTION,
        InterventionFamily.QUALITY_INTERVENTION,
        InterventionFamily.CAPACITY_INTERVENTION,
    ):
        result = by_family[family]
        assert result.status is SimulationStatus.SUCCEEDED
        assert result.scenario_id is not None
        assert result.scenario_hash is not None and len(result.scenario_hash) == 64
        assert result.candidate_id == candidate_by_family[family].candidate_id
        assert result.run_id == run.run_id
        assert result.baseline_snapshot_id == snapshot.snapshot_id
        assert result.baseline_snapshot_hash == snapshot.snapshot_hash
        assert tuple((item.name, item.unit) for item in result.measurements) == (
            MEASUREMENT_SCHEMA
        )
        assert result.affected_entities == tuple(
            sorted(
                result.affected_entities,
                key=lambda item: (item.entity_type, item.entity_id),
            )
        )
        assert len(result.affected_entities) > 0

    assert (
        baseline.dataset_version.content_hash,
        baseline.dataset_version.row_count_total,
        canonical_business_payload(baseline.rows_by_table),
    ) == before


def test_closed_observation_gate_makes_zero_scenario_calls_at_earlier_as_of(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline = closed_baseline()
    closed_at = datetime.combine(baseline.dataset_version.period_end, time.max, BUSINESS_TIMEZONE)
    earlier = closed_at - timedelta(microseconds=1)
    run = make_run(
        earlier,
        dataset_version=baseline.dataset_version.dataset_version_id,
        dataset_hash=baseline.dataset_version.content_hash,
    )
    fixture = make_c04_fixture(
        as_of=earlier,
        dataset_version=baseline.dataset_version.dataset_version_id,
        dataset_hash=baseline.dataset_version.content_hash,
    )
    calls = 0

    def forbidden_call(*args: object, **kwargs: object) -> NoReturn:
        nonlocal calls
        calls += 1
        raise AssertionError("scenario engine must not run")

    monkeypatch.setattr(implementation, "apply_scenario_business_only", forbidden_call)
    bundle, candidates = build_with(baseline, run, fixture)
    assert calls == 0
    by_family = result_by_family(bundle, candidates)
    for family in set(InterventionFamily) - {InterventionFamily.NO_ACTION}:
        assert by_family[family].status is SimulationStatus.UNAVAILABLE
        assert "C04_CLOSED_OBSERVATION_WINDOW_REQUIRED" in {
            item.code for item in by_family[family].limitations
        }


@pytest.mark.parametrize(
    ("error", "expected_status", "expected_code"),
    [
        (
            ScenarioPreconditionUnavailable("private expected detail"),
            SimulationStatus.UNAVAILABLE,
            "C04_SCENARIO_PRECONDITION_UNAVAILABLE",
        ),
        (
            ValueError("private unexpected value detail"),
            SimulationStatus.FAILED,
            "C04_SCENARIO_EXECUTION_FAILED",
        ),
        (
            RuntimeError("private unexpected runtime detail"),
            SimulationStatus.FAILED,
            "C04_SCENARIO_EXECUTION_FAILED",
        ),
    ],
)
def test_typed_precondition_boundary_and_sanitized_unexpected_failures(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    expected_status: SimulationStatus,
    expected_code: str,
) -> None:
    baseline, run, fixture = closed_fixture()

    def fail(*args: object, **kwargs: object) -> NoReturn:
        raise error

    monkeypatch.setattr(implementation, "apply_scenario_business_only", fail)
    bundle, candidates = build_with(baseline, run, fixture)
    by_family = result_by_family(bundle, candidates)
    for family in set(InterventionFamily) - {InterventionFamily.NO_ACTION}:
        result = by_family[family]
        assert result.status is expected_status
        assert expected_code in {item.code for item in result.limitations}
        assert result.scenario_id is None and result.scenario_hash is None
        assert result.measurements == () and result.affected_entities == ()
    artifact = canonical_json_bytes(bundle).decode("utf-8")
    assert str(error) not in artifact
    assert "private" not in artifact


@pytest.mark.parametrize(
    "error",
    [
        ScenarioPreconditionUnavailable("expected after mutation"),
        ValueError("unexpected value after mutation"),
        RuntimeError("unexpected runtime after mutation"),
    ],
)
def test_baseline_mutation_on_every_error_path_is_a_hard_fail(
    monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    baseline, run, fixture = closed_fixture()

    def mutate_then_fail(
        supplied: GeneratedDataset, *args: object, **kwargs: object
    ) -> NoReturn:
        supplier = cast(Supplier, supplied.rows_for("dim_supplier")[0])
        supplier.supplier_code = f"{supplier.supplier_code}-MUTATED"
        raise error

    monkeypatch.setattr(implementation, "apply_scenario_business_only", mutate_then_fail)
    with pytest.raises(C04BuildError) as caught:
        build_with(baseline, run, fixture)
    assert caught.value.code == "C04_BASELINE_MUTATION"
    assert caught.value.state == "BLOCKED_INTEGRITY"


def test_baseline_version_and_hash_binding_fail_closed_before_scenario_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline = closed_baseline()
    closed_at = datetime.combine(baseline.dataset_version.period_end, time.max, BUSINESS_TIMEZONE)
    calls = 0

    def forbidden_call(*args: object, **kwargs: object) -> NoReturn:
        nonlocal calls
        calls += 1
        raise AssertionError("scenario engine must not run")

    monkeypatch.setattr(implementation, "apply_scenario_business_only", forbidden_call)
    for dataset_version, dataset_hash, expected in (
        (
            "dsv-other",
            baseline.dataset_version.content_hash,
            "C04_SIMULATION_BASELINE_BINDING_MISMATCH",
        ),
        (
            baseline.dataset_version.dataset_version_id,
            "f" * 64,
            "C04_SIMULATION_BASELINE_HASH_MISMATCH",
        ),
    ):
        run = make_run(
            closed_at,
            dataset_version=dataset_version,
            dataset_hash=dataset_hash,
        )
        fixture = make_c04_fixture(
            as_of=closed_at,
            dataset_version=dataset_version,
            dataset_hash=dataset_hash,
        )
        bundle, candidates = build_with(baseline, run, fixture)
        by_family = result_by_family(bundle, candidates)
        for family in set(InterventionFamily) - {InterventionFamily.NO_ACTION}:
            assert expected in {item.code for item in by_family[family].limitations}
    assert calls == 0


def test_canonical_candidate_parameters_exactly_construct_executed_configs() -> None:
    baseline = closed_baseline()
    *_, candidates = make_c04_fixture()
    by_family = {item.family: item for item in candidates.candidates}

    supplier = cast(
        SupplierDegradationConfig,
        implementation._scenario_config(
            by_family[InterventionFamily.SUPPLIER_INTERVENTION], baseline
        ),
    )
    supplier_params = {
        item.name: item.value
        for item in by_family[InterventionFamily.SUPPLIER_INTERVENTION].parameters
    }
    assert supplier.affected_supplier_count == supplier_params["affected_supplier_count"]
    assert (
        supplier.affected_critical_material_count
        == supplier_params["affected_critical_material_count"]
    )
    assert supplier.late_probability_delta == supplier_params["late_probability_delta"]
    assert (
        supplier.additional_delay_business_days_min
        == supplier_params["additional_delay_business_days_min"]
    )
    assert (
        supplier.additional_delay_business_days_max
        == supplier_params["additional_delay_business_days_max"]
    )

    quality = cast(
        QualityDeteriorationConfig,
        implementation._scenario_config(
            by_family[InterventionFamily.QUALITY_INTERVENTION], baseline
        ),
    )
    quality_params = {
        item.name: item.value
        for item in by_family[InterventionFamily.QUALITY_INTERVENTION].parameters
    }
    assert quality.affected_product_count == quality_params["affected_product_count"]
    assert quality.affected_work_center_count == quality_params["affected_work_center_count"]
    assert (
        quality.failure_probability_multiplier == quality_params["failure_probability_multiplier"]
    )
    assert quality.rework_probability_delta == quality_params["rework_probability_delta"]
    assert (
        quality.rework_duration_multiplier_min == quality_params["rework_duration_multiplier_min"]
    )
    assert (
        quality.rework_duration_multiplier_max == quality_params["rework_duration_multiplier_max"]
    )

    capacity = cast(
        CapacitySurgeConfig,
        implementation._scenario_config(
            by_family[InterventionFamily.CAPACITY_INTERVENTION], baseline
        ),
    )
    capacity_params = {
        item.name: item.value
        for item in by_family[InterventionFamily.CAPACITY_INTERVENTION].parameters
    }
    assert capacity.affected_work_center_count == capacity_params["affected_work_center_count"]
    assert capacity.arrival_volume_multiplier == capacity_params["arrival_volume_multiplier"]
    assert capacity.queue_time_multiplier == capacity_params["queue_time_multiplier"]

    for config, family in (
        (supplier, InterventionFamily.SUPPLIER_INTERVENTION),
        (quality, InterventionFamily.QUALITY_INTERVENTION),
        (capacity, InterventionFamily.CAPACITY_INTERVENTION),
    ):
        params = {item.name: item.value for item in by_family[family].parameters}
        assert config.scenario_version == "w03-c04-stress-v1"
        assert config.window_start == datetime.combine(
            baseline.dataset_version.period_start, time.min, BUSINESS_TIMEZONE
        )
        assert config.window_end == datetime.combine(
            baseline.dataset_version.period_end + timedelta(days=1),
            time.min,
            BUSINESS_TIMEZONE,
        )
        assert params["seed_policy"] == "SHA256_CANDIDATE_ID_63BIT"
        assert params["window_policy"] == "FULL_CLOSED_DATASET_PERIOD"
        assert isinstance(config.scenario_seed, int) and config.scenario_seed >= 0
