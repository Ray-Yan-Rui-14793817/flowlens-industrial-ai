"""Deterministic HGT-free stress-probe simulation for W03-C04."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from decimal import Decimal
from typing import Final, cast

from flowlens.data import Base
from flowlens.data.generation import BUSINESS_TIMEZONE, GeneratedDataset
from flowlens.data.generation.canonical import (
    CANONICAL_TABLE_ORDER,
    canonical_business_payload,
    canonical_content_hash,
    normalize_scalar,
)
from flowlens.data.models import (
    Delivery,
    Operation,
    QualityInspection,
    Rework,
    SalesOrder,
    WorkOrder,
)
from flowlens.data.scenarios.config import (
    CapacitySurgeConfig,
    QualityDeteriorationConfig,
    ScenarioConfig,
    SupplierDegradationConfig,
)
from flowlens.data.scenarios.runtime_adapter import apply_scenario_business_only
from flowlens.data.scenarios.transformer import (
    ScenarioPreconditionUnavailable,
    build_scenario_identity,
)
from flowlens.decision.c03_validation import EvidenceIndex
from flowlens.decision.c04_registry import (
    SCENARIO_ADAPTER_VERSION,
    STRESS_SCENARIO_VERSION,
    build_candidate_set,
)
from flowlens.decision.c04_validation import (
    C04BuildError,
    validate_c04_inputs,
    validate_candidate_set,
    validate_run_snapshot,
)
from flowlens.decision.context import DecisionContext
from flowlens.decision.contracts import (
    CandidateSet,
    DecisionRun,
    DiagnosisRecord,
    EvidenceBundle,
    InterventionCandidate,
    SignalBundle,
    SimulationBundle,
    SimulationResult,
    StateSnapshot,
)
from flowlens.decision.enums import InterventionFamily, SimulationStatus
from flowlens.decision.primitives import (
    ArtifactProvenance,
    EntityRef,
    Limitation,
    NamedValue,
    ScalarValue,
    VersionRef,
)
from flowlens.decision.serialization import derive_artifact_id

_MEASUREMENT_UNITS: Final = {
    "affected_entity_count": "count",
    "business_row_count_delta": "count",
    "target_delivered_quantity": "unit",
    "target_delivery_lag_seconds": "s",
    "target_failed_quantity": "unit",
    "target_last_delivery_at": None,
    "target_max_operation_start_slippage_seconds": "s",
    "target_max_work_order_completion_slippage_seconds": "s",
    "target_remaining_quantity": "unit",
    "target_rework_quantity": "unit",
}

_SIMULATION_LIMITATION_MESSAGES: Final = {
    "C04_BASELINE_MUTATION": "The supplied baseline changed during C04 execution.",
    "C04_CLOSED_OBSERVATION_WINDOW_REQUIRED": (
        "A full scenario baseline is allowed only at its closed observation instant."
    ),
    "C04_SCENARIO_EXECUTION_FAILED": (
        "The deterministic scenario engine failed after its preconditions passed."
    ),
    "C04_SCENARIO_PRECONDITION_UNAVAILABLE": (
        "The frozen W2 scenario preconditions are not satisfied by this baseline."
    ),
    "C04_SIMULATION_BASELINE_BINDING_MISMATCH": (
        "The supplied baseline dataset version does not match the DecisionRun."
    ),
    "C04_SIMULATION_BASELINE_HASH_MISMATCH": (
        "The supplied baseline stored, recomputed and DecisionRun hashes do not agree."
    ),
    "C04_SIMULATION_BASELINE_NOT_SUPPLIED": (
        "No already-materialized in-memory simulation baseline was supplied."
    ),
}

_EVENT_FIELDS: Final = {
    "fact_sales_order": ("order_at",),
    "fact_work_order": ("actual_start_at", "actual_end_at"),
    "fact_operation": ("actual_start_at", "actual_end_at"),
    "fact_purchase_order": ("ordered_at", "actual_receipt_at"),
    "fact_inventory_snapshot": ("snapshot_at",),
    "fact_quality_inspection": ("inspection_at",),
    "fact_rework": ("rework_start_at", "rework_end_at"),
    "fact_delivery": ("delivery_at",),
}


@dataclass(frozen=True, slots=True)
class _BaselineSignature:
    content_hash: str
    row_counts: tuple[tuple[str, int], ...]
    payload: object
    row_values: tuple[
        tuple[str, tuple[tuple[tuple[str, object], ...], ...]], ...
    ]
    all_detached: bool


def _seconds(delta: timedelta) -> Decimal:
    return Decimal(delta.days * 86400 + delta.seconds) + Decimal(delta.microseconds) / Decimal(
        1_000_000
    )


def _measurements(values: Mapping[str, ScalarValue]) -> tuple[NamedValue, ...]:
    if set(values) != set(_MEASUREMENT_UNITS):
        raise C04BuildError("C04_MEASUREMENT_SCHEMA_MISMATCH", "BLOCKED_CONTRACT")
    return tuple(
        NamedValue(name=name, value=values[name], unit=_MEASUREMENT_UNITS[name])
        for name in sorted(values)
    )


def _target_values(
    *,
    order_quantity: int,
    promised_delivery_at: datetime,
    deliveries: Sequence[tuple[int, datetime]],
    inspections: Sequence[int],
    reworks: Sequence[int],
    operation_windows: Sequence[tuple[datetime, datetime]],
    work_order_windows: Sequence[tuple[datetime, datetime]],
    affected_count: int,
    row_count_delta: int,
) -> tuple[NamedValue, ...]:
    delivered = sum(item[0] for item in deliveries)
    last_delivery = max((item[1] for item in deliveries), default=None)
    lag = (
        max(_seconds(last_delivery - promised_delivery_at), Decimal(0))
        if delivered >= order_quantity and last_delivery is not None
        else None
    )
    operation_slippage = (
        max(
            (max(_seconds(actual - planned), Decimal(0)) for planned, actual in operation_windows),
            default=None,
        )
        if operation_windows
        else None
    )
    completion_slippage = (
        max(
            (max(_seconds(actual - planned), Decimal(0)) for planned, actual in work_order_windows),
            default=None,
        )
        if work_order_windows
        else None
    )
    return _measurements(
        {
            "affected_entity_count": affected_count,
            "business_row_count_delta": row_count_delta,
            "target_delivered_quantity": delivered,
            "target_delivery_lag_seconds": lag,
            "target_failed_quantity": sum(inspections),
            "target_last_delivery_at": last_delivery,
            "target_max_operation_start_slippage_seconds": operation_slippage,
            "target_max_work_order_completion_slippage_seconds": completion_slippage,
            "target_remaining_quantity": max(order_quantity - delivered, 0),
            "target_rework_quantity": sum(reworks),
        }
    )


def _evidence_measurements(index: EvidenceIndex, order_id: str) -> tuple[NamedValue, ...]:
    order = index.rows.get(("fact_sales_order", order_id), {})
    quantity = order.get("order_quantity")
    promise = order.get("promised_delivery_at")
    if (
        quantity is None
        or type(quantity.value) is not int
        or promise is None
        or type(promise.value) is not datetime
    ):
        raise C04BuildError("C04_BASELINE_MEASUREMENT_UNAVAILABLE", "BLOCKED_CONTRACT")
    work_ids = {
        record_id
        for (entity, record_id), fields in index.rows.items()
        if entity == "fact_work_order"
        and fields.get("sales_order_id") is not None
        and fields["sales_order_id"].value == order_id
    }
    deliveries = [
        (fields["delivered_quantity"].value, fields["delivery_at"].value)
        for (entity, _), fields in index.rows.items()
        if entity == "fact_delivery"
        and fields.get("sales_order_id") is not None
        and fields["sales_order_id"].value == order_id
        and fields.get("delivered_quantity") is not None
        and type(fields["delivered_quantity"].value) is int
        and fields.get("delivery_at") is not None
        and type(fields["delivery_at"].value) is datetime
    ]
    inspections = [
        fields["failed_quantity"].value
        for (entity, _), fields in index.rows.items()
        if entity == "fact_quality_inspection"
        and fields.get("work_order_id") is not None
        and fields["work_order_id"].value in work_ids
        and fields.get("failed_quantity") is not None
        and type(fields["failed_quantity"].value) is int
    ]
    reworks = [
        fields["rework_quantity"].value
        for (entity, _), fields in index.rows.items()
        if entity == "fact_rework"
        and fields.get("work_order_id") is not None
        and fields["work_order_id"].value in work_ids
        and fields.get("rework_quantity") is not None
        and type(fields["rework_quantity"].value) is int
    ]
    operation_windows = [
        (
            fields["planned_start_at"].value,
            fields["actual_start_at"].value,
        )
        for (entity, _), fields in index.rows.items()
        if entity == "fact_operation"
        and fields.get("work_order_id") is not None
        and fields["work_order_id"].value in work_ids
        and fields.get("planned_start_at") is not None
        and type(fields["planned_start_at"].value) is datetime
        and fields.get("actual_start_at") is not None
        and type(fields["actual_start_at"].value) is datetime
    ]
    work_order_windows = [
        (
            fields["planned_end_at"].value,
            fields["actual_end_at"].value,
        )
        for (entity, record_id), fields in index.rows.items()
        if entity == "fact_work_order"
        and record_id in work_ids
        and fields.get("planned_end_at") is not None
        and type(fields["planned_end_at"].value) is datetime
        and fields.get("actual_end_at") is not None
        and type(fields["actual_end_at"].value) is datetime
    ]
    return _target_values(
        order_quantity=quantity.value,
        promised_delivery_at=promise.value,
        deliveries=deliveries,
        inspections=inspections,
        reworks=reworks,
        operation_windows=operation_windows,
        work_order_windows=work_order_windows,
        affected_count=0,
        row_count_delta=0,
    )


def _dataset_measurements(
    dataset: GeneratedDataset,
    order_id: str,
    affected: tuple[EntityRef, ...],
    row_count_delta: int,
) -> tuple[NamedValue, ...]:
    orders = [
        item
        for item in cast(tuple[SalesOrder, ...], dataset.rows_for("fact_sales_order"))
        if item.sales_order_id == order_id
    ]
    if len(orders) != 1:
        raise ValueError("target sales order is unavailable in scenario data")
    order = orders[0]
    work_orders = [
        item
        for item in cast(tuple[WorkOrder, ...], dataset.rows_for("fact_work_order"))
        if item.sales_order_id == order_id
    ]
    work_ids = {item.work_order_id for item in work_orders}
    deliveries = [
        (item.delivered_quantity, item.delivery_at)
        for item in cast(tuple[Delivery, ...], dataset.rows_for("fact_delivery"))
        if item.sales_order_id == order_id
    ]
    inspections = [
        item.failed_quantity
        for item in cast(
            tuple[QualityInspection, ...], dataset.rows_for("fact_quality_inspection")
        )
        if item.work_order_id in work_ids
    ]
    reworks = [
        item.rework_quantity
        for item in cast(tuple[Rework, ...], dataset.rows_for("fact_rework"))
        if item.work_order_id in work_ids
    ]
    operation_windows = [
        (item.planned_start_at, item.actual_start_at)
        for item in cast(tuple[Operation, ...], dataset.rows_for("fact_operation"))
        if item.work_order_id in work_ids and item.actual_start_at is not None
    ]
    work_order_windows = [
        (item.planned_end_at, item.actual_end_at)
        for item in work_orders
        if item.actual_end_at is not None
    ]
    return _target_values(
        order_quantity=order.order_quantity,
        promised_delivery_at=order.promised_delivery_at,
        deliveries=deliveries,
        inspections=inspections,
        reworks=reworks,
        operation_windows=cast(Sequence[tuple[datetime, datetime]], operation_windows),
        work_order_windows=cast(Sequence[tuple[datetime, datetime]], work_order_windows),
        affected_count=len(affected),
        row_count_delta=row_count_delta,
    )


def _business_key(row: Base) -> tuple[str, ...]:
    values = tuple(
        str(getattr(row, column.name))
        for column in row.__mapper__.primary_key
        if column.name != "dataset_version_id"
    )
    if not values:
        raise ValueError("business row has no ownership-independent primary key")
    return values


def _semantic_row(row: Base) -> tuple[tuple[str, object], ...]:
    return tuple(
        (column.name, normalize_scalar(getattr(row, column.name)))
        for column in row.__mapper__.columns
        if column.name != "dataset_version_id"
    )


def semantic_affected_entities(
    baseline: GeneratedDataset, scenario: GeneratedDataset
) -> tuple[EntityRef, ...]:
    """Return an ownership-independent semantic business diff without protected truth."""

    affected: list[EntityRef] = []
    for table in CANONICAL_TABLE_ORDER:
        before = {_business_key(row): _semantic_row(row) for row in baseline.rows_for(table)}
        after = {_business_key(row): _semantic_row(row) for row in scenario.rows_for(table)}
        for key in sorted(set(before) | set(after)):
            if before.get(key) != after.get(key):
                affected.append(EntityRef(entity_type=table, entity_id="|".join(key)))
    return tuple(sorted(affected, key=lambda item: (item.entity_type, item.entity_id)))


def _signature(dataset: GeneratedDataset) -> _BaselineSignature:
    row_counts = tuple((table, len(dataset.rows_for(table))) for table in CANONICAL_TABLE_ORDER)
    row_values = tuple(
        (
            table,
            tuple(
                tuple((column.name, getattr(row, column.name)) for column in row.__mapper__.columns)
                for row in dataset.rows_for(table)
            ),
        )
        for table in CANONICAL_TABLE_ORDER
    )
    return _BaselineSignature(
        content_hash=canonical_content_hash(dataset.rows_by_table),
        row_counts=row_counts,
        payload=canonical_business_payload(dataset.rows_by_table),
        row_values=row_values,
        all_detached=all(
            getattr(row.__dict__.get("_sa_instance_state"), "session_id", None) is None
            for table in CANONICAL_TABLE_ORDER
            for row in dataset.rows_for(table)
        ),
    )


def _baseline_gate(run: DecisionRun, baseline: GeneratedDataset) -> str | None:
    if baseline.dataset_version.dataset_version_id != run.dataset_version:
        return "C04_SIMULATION_BASELINE_BINDING_MISMATCH"
    recomputed = canonical_content_hash(baseline.rows_by_table)
    if recomputed != baseline.dataset_version.content_hash or recomputed != run.dataset_hash:
        return "C04_SIMULATION_BASELINE_HASH_MISMATCH"
    closed_at = datetime.combine(
        baseline.dataset_version.period_end,
        time.max,
        BUSINESS_TIMEZONE,
    )
    if run.as_of_time.astimezone(BUSINESS_TIMEZONE) != closed_at:
        return "C04_CLOSED_OBSERVATION_WINDOW_REQUIRED"
    for table, fields in _EVENT_FIELDS.items():
        for row in baseline.rows_for(table):
            for field in fields:
                value = getattr(row, field)
                if value is not None and (
                    not isinstance(value, datetime)
                    or value.tzinfo is None
                    or value.utcoffset() is None
                    or value > run.as_of_time
                ):
                    return "C04_CLOSED_OBSERVATION_WINDOW_REQUIRED"
    return None


def _scenario_config(
    candidate: InterventionCandidate, baseline: GeneratedDataset
) -> ScenarioConfig:
    start = datetime.combine(baseline.dataset_version.period_start, time.min, BUSINESS_TIMEZONE)
    end = datetime.combine(
        baseline.dataset_version.period_end + timedelta(days=1), time.min, BUSINESS_TIMEZONE
    )
    digest = hashlib.sha256(candidate.candidate_id.encode("utf-8")).hexdigest()
    seed = int(digest[:16], 16) & 0x7FFF_FFFF_FFFF_FFFF
    parameters = {item.name: item.value for item in candidate.parameters}
    policies = {
        "seed_policy": "SHA256_CANDIDATE_ID_63BIT",
        "window_policy": "FULL_CLOSED_DATASET_PERIOD",
    }
    if any(parameters.get(name) != value for name, value in policies.items()):
        raise C04BuildError("C04_REGISTRY_MAPPING_INVALID", "BLOCKED_CONTRACT")
    if candidate.family is InterventionFamily.SUPPLIER_INTERVENTION:
        expected = {
            "additional_delay_business_days_max",
            "additional_delay_business_days_min",
            "affected_critical_material_count",
            "affected_supplier_count",
            "late_probability_delta",
            *policies,
        }
        if set(parameters) != expected:
            raise C04BuildError("C04_REGISTRY_MAPPING_INVALID", "BLOCKED_CONTRACT")
        return SupplierDegradationConfig(
            scenario_version=STRESS_SCENARIO_VERSION,
            scenario_seed=seed,
            window_start=start,
            window_end=end,
            affected_supplier_count=cast(int, parameters["affected_supplier_count"]),
            affected_critical_material_count=cast(
                int, parameters["affected_critical_material_count"]
            ),
            late_probability_delta=cast(Decimal, parameters["late_probability_delta"]),
            additional_delay_business_days_min=cast(
                int, parameters["additional_delay_business_days_min"]
            ),
            additional_delay_business_days_max=cast(
                int, parameters["additional_delay_business_days_max"]
            ),
        )
    if candidate.family is InterventionFamily.QUALITY_INTERVENTION:
        expected = {
            "affected_product_count",
            "affected_work_center_count",
            "failure_probability_multiplier",
            "rework_duration_multiplier_max",
            "rework_duration_multiplier_min",
            "rework_probability_delta",
            *policies,
        }
        if set(parameters) != expected:
            raise C04BuildError("C04_REGISTRY_MAPPING_INVALID", "BLOCKED_CONTRACT")
        return QualityDeteriorationConfig(
            scenario_version=STRESS_SCENARIO_VERSION,
            scenario_seed=seed,
            window_start=start,
            window_end=end,
            affected_product_count=cast(int, parameters["affected_product_count"]),
            affected_work_center_count=cast(
                int, parameters["affected_work_center_count"]
            ),
            failure_probability_multiplier=cast(
                Decimal, parameters["failure_probability_multiplier"]
            ),
            rework_probability_delta=cast(Decimal, parameters["rework_probability_delta"]),
            rework_duration_multiplier_min=cast(
                Decimal, parameters["rework_duration_multiplier_min"]
            ),
            rework_duration_multiplier_max=cast(
                Decimal, parameters["rework_duration_multiplier_max"]
            ),
        )
    if candidate.family is InterventionFamily.CAPACITY_INTERVENTION:
        expected = {
            "affected_work_center_count",
            "arrival_volume_multiplier",
            "queue_time_multiplier",
            *policies,
        }
        if set(parameters) != expected:
            raise C04BuildError("C04_REGISTRY_MAPPING_INVALID", "BLOCKED_CONTRACT")
        return CapacitySurgeConfig(
            scenario_version=STRESS_SCENARIO_VERSION,
            scenario_seed=seed,
            window_start=start,
            window_end=end,
            affected_work_center_count=cast(
                int, parameters["affected_work_center_count"]
            ),
            arrival_volume_multiplier=cast(
                Decimal, parameters["arrival_volume_multiplier"]
            ),
            queue_time_multiplier=cast(Decimal, parameters["queue_time_multiplier"]),
        )
    raise C04BuildError("C04_REGISTRY_MAPPING_INVALID", "BLOCKED_CONTRACT")


def _result_provenance(
    run: DecisionRun,
    snapshot: StateSnapshot,
    candidate: InterventionCandidate,
) -> ArtifactProvenance:
    return ArtifactProvenance(
        producer="flowlens.decision.c04_simulation",
        producer_version=SCENARIO_ADAPTER_VERSION,
        input_artifact_ids=tuple(
            sorted((run.run_id, snapshot.snapshot_id, candidate.candidate_id))
        ),
        source_refs=candidate.provenance.source_refs,
        contract_versions=(
            VersionRef(name="w03-c01", version="v1"),
            VersionRef(name="w03-c04-measurements", version="v1"),
            VersionRef(name="w03-c04-registry", version="v1"),
            VersionRef(name="w03-c04-scenario-adapter", version="v1"),
        ),
        implementation_sha=None,
    )


def _make_result(
    run: DecisionRun,
    snapshot: StateSnapshot,
    candidate: InterventionCandidate,
    *,
    status: SimulationStatus,
    scenario_id: str | None,
    scenario_hash: str | None,
    affected: tuple[EntityRef, ...],
    measurements: tuple[NamedValue, ...],
    limitations: tuple[Limitation, ...],
) -> SimulationResult:
    identity = {
        "run_id": run.run_id,
        "candidate_id": candidate.candidate_id,
        "status": status,
        "baseline_snapshot_id": snapshot.snapshot_id,
        "baseline_snapshot_hash": snapshot.snapshot_hash,
        "scenario_id": scenario_id,
        "scenario_hash": scenario_hash,
        "affected_entities": affected,
        "measurements": measurements,
    }
    return SimulationResult(
        simulation_id=derive_artifact_id("simulation-result", "simulation-result.v1", identity),
        schema_version="simulation-result.v1",
        run_id=run.run_id,
        candidate_id=candidate.candidate_id,
        status=status,
        baseline_snapshot_id=snapshot.snapshot_id,
        baseline_snapshot_hash=snapshot.snapshot_hash,
        scenario_id=scenario_id,
        scenario_hash=scenario_hash,
        affected_entities=affected,
        measurements=measurements,
        limitations=tuple(sorted(set(limitations), key=lambda item: (item.code, item.message))),
        provenance=_result_provenance(run, snapshot, candidate),
    )


def _limited_result(
    run: DecisionRun,
    snapshot: StateSnapshot,
    candidate: InterventionCandidate,
    status: SimulationStatus,
    code: str,
) -> SimulationResult:
    return _make_result(
        run,
        snapshot,
        candidate,
        status=status,
        scenario_id=None,
        scenario_hash=None,
        affected=(),
        measurements=(),
        limitations=(
            *candidate.limitations,
            Limitation(code=code, message=_SIMULATION_LIMITATION_MESSAGES[code]),
        ),
    )


def build_simulation_bundle(
    run: DecisionRun,
    snapshot: StateSnapshot,
    bundle: EvidenceBundle,
    context: DecisionContext,
    signals: SignalBundle,
    diagnosis: DiagnosisRecord,
    candidates: CandidateSet,
    *,
    baseline: GeneratedDataset | None = None,
) -> SimulationBundle:
    """Build one deterministic result per canonical registry candidate."""

    validate_run_snapshot(run, snapshot, context)
    canonical = validate_c04_inputs(bundle, context, signals, diagnosis)
    expected = build_candidate_set(bundle, context, canonical.signals, canonical.diagnosis)
    validate_candidate_set(candidates, expected)
    results: list[SimulationResult] = []
    baseline_measurements = _evidence_measurements(canonical.index, context.order_id)
    for candidate in candidates.candidates:
        if candidate.family is InterventionFamily.NO_ACTION:
            results.append(
                _make_result(
                    run,
                    snapshot,
                    candidate,
                    status=SimulationStatus.SUCCEEDED,
                    scenario_id=None,
                    scenario_hash=None,
                    affected=(),
                    measurements=baseline_measurements,
                    limitations=candidate.limitations,
                )
            )
            continue
        if baseline is None:
            results.append(
                _limited_result(
                    run,
                    snapshot,
                    candidate,
                    SimulationStatus.UNAVAILABLE,
                    "C04_SIMULATION_BASELINE_NOT_SUPPLIED",
                )
            )
            continue
        gate = _baseline_gate(run, baseline)
        if gate is not None:
            results.append(
                _limited_result(
                    run, snapshot, candidate, SimulationStatus.UNAVAILABLE, gate
                )
            )
            continue
        before = _signature(baseline)
        if not before.all_detached:
            results.append(
                _limited_result(
                    run,
                    snapshot,
                    candidate,
                    SimulationStatus.UNAVAILABLE,
                    "C04_SIMULATION_BASELINE_BINDING_MISMATCH",
                )
            )
            continue
        config = _scenario_config(candidate, baseline)
        identity = build_scenario_identity(baseline, config)
        try:
            scenario = apply_scenario_business_only(
                baseline,
                config,
                generated_at=run.as_of_time,
            )
            if (
                scenario.dataset_version.dataset_version_id
                != identity.scenario_dataset_version_id
            ):
                raise RuntimeError("scenario dataset identity mismatch")
            affected = semantic_affected_entities(baseline, scenario)
            row_delta = (
                scenario.dataset_version.row_count_total
                - baseline.dataset_version.row_count_total
            )
            measurements = _dataset_measurements(
                scenario, context.order_id, affected, row_delta
            )
        except ScenarioPreconditionUnavailable as error:
            after = _signature(baseline)
            if after != before:
                raise C04BuildError(
                    "C04_BASELINE_MUTATION", "BLOCKED_INTEGRITY"
                ) from error
            results.append(
                _limited_result(
                    run,
                    snapshot,
                    candidate,
                    SimulationStatus.UNAVAILABLE,
                    "C04_SCENARIO_PRECONDITION_UNAVAILABLE",
                )
            )
            continue
        except Exception as error:
            after = _signature(baseline)
            if after != before:
                raise C04BuildError(
                    "C04_BASELINE_MUTATION", "BLOCKED_INTEGRITY"
                ) from error
            results.append(
                _limited_result(
                    run,
                    snapshot,
                    candidate,
                    SimulationStatus.FAILED,
                    "C04_SCENARIO_EXECUTION_FAILED",
                )
            )
            continue
        after = _signature(baseline)
        if after != before:
            raise C04BuildError("C04_BASELINE_MUTATION", "BLOCKED_INTEGRITY")
        results.append(
            _make_result(
                run,
                snapshot,
                candidate,
                status=SimulationStatus.SUCCEEDED,
                scenario_id=identity.scenario_id,
                scenario_hash=scenario.dataset_version.content_hash,
                affected=affected,
                measurements=measurements,
                limitations=candidate.limitations,
            )
        )
    ordered = tuple(sorted(results, key=lambda item: (item.candidate_id, item.simulation_id)))
    bundle_identity = {
        "run_id": run.run_id,
        "snapshot_id": snapshot.snapshot_id,
        "candidate_simulation_ids": tuple(
            (item.candidate_id, item.simulation_id) for item in ordered
        ),
    }
    return SimulationBundle(
        simulation_bundle_id=derive_artifact_id(
            "simulation-bundle", "simulation-bundle.v1", bundle_identity
        ),
        schema_version="simulation-bundle.v1",
        run_id=run.run_id,
        snapshot_id=snapshot.snapshot_id,
        results=ordered,
        provenance=ArtifactProvenance(
            producer="flowlens.decision.c04_simulation",
            producer_version=SCENARIO_ADAPTER_VERSION,
            input_artifact_ids=tuple(
                sorted(
                    (
                        run.run_id,
                        snapshot.snapshot_id,
                        candidates.candidate_set_id,
                        *(item.simulation_id for item in ordered),
                    )
                )
            ),
            source_refs=candidates.provenance.source_refs,
            contract_versions=(
                VersionRef(name="w03-c01", version="v1"),
                VersionRef(name="w03-c04-measurements", version="v1"),
                VersionRef(name="w03-c04-registry", version="v1"),
                VersionRef(name="w03-c04-scenario-adapter", version="v1"),
            ),
            implementation_sha=None,
        ),
    )
