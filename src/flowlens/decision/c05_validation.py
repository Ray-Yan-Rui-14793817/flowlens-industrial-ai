"""Fail-closed canonical input validation for W03-C05."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType
from typing import Final

from flowlens.decision.c03_validation import EvidenceIndex
from flowlens.decision.c04_registry import SCENARIO_ADAPTER_VERSION, build_candidate_set
from flowlens.decision.c04_validation import (
    C04BuildError,
    validate_c04_inputs,
    validate_candidate_set,
    validate_run_snapshot,
)
from flowlens.decision.c05_policy import MEASUREMENT_UNITS
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
from flowlens.decision.primitives import VersionRef
from flowlens.decision.serialization import canonical_json_text, derive_artifact_id

_C04_RESULT_LIMITATION_MESSAGES: Final = MappingProxyType(
    {
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
)

_C04_CONTRACT_VERSIONS: Final = (
    VersionRef(name="w03-c01", version="v1"),
    VersionRef(name="w03-c04-measurements", version="v1"),
    VersionRef(name="w03-c04-registry", version="v1"),
    VersionRef(name="w03-c04-scenario-adapter", version="v1"),
)


class C05BuildError(ValueError):
    """A deterministic C05 contract, temporal, trust, or isolation failure."""

    def __init__(self, code: str, state: str) -> None:
        self.code = code
        self.state = state
        super().__init__(f"{state}: {code}")


@dataclass(frozen=True, slots=True)
class CanonicalC05Inputs:
    index: EvidenceIndex
    signals: SignalBundle
    diagnosis: DiagnosisRecord
    candidates: CandidateSet
    simulations: SimulationBundle


def _fail(code: str = "C05_NONCANONICAL_C04_SIMULATION") -> None:
    raise C05BuildError(code, "BLOCKED_CONTRACT")


def _valid_measurements(result: SimulationResult) -> bool:
    if tuple(item.name for item in result.measurements) != tuple(sorted(MEASUREMENT_UNITS)):
        return False
    values = {item.name: item for item in result.measurements}
    if any(values[name].unit != unit for name, unit in MEASUREMENT_UNITS.items()):
        return False
    integer_names = {
        "affected_entity_count",
        "business_row_count_delta",
        "target_delivered_quantity",
        "target_failed_quantity",
        "target_remaining_quantity",
        "target_rework_quantity",
    }
    decimal_names = {
        "target_delivery_lag_seconds",
        "target_max_operation_start_slippage_seconds",
        "target_max_work_order_completion_slippage_seconds",
    }
    if any(type(values[name].value) is not int for name in integer_names):
        return False
    if any(
        values[name].value is not None and type(values[name].value) is not Decimal
        for name in decimal_names
    ):
        return False
    last_delivery = values["target_last_delivery_at"].value
    return last_delivery is None or type(last_delivery) is datetime


def _result_identity(result: SimulationResult) -> dict[str, object]:
    return {
        "run_id": result.run_id,
        "candidate_id": result.candidate_id,
        "status": result.status,
        "baseline_snapshot_id": result.baseline_snapshot_id,
        "baseline_snapshot_hash": result.baseline_snapshot_hash,
        "scenario_id": result.scenario_id,
        "scenario_hash": result.scenario_hash,
        "affected_entities": result.affected_entities,
        "measurements": result.measurements,
    }


def _validate_result(
    result: SimulationResult,
    candidate: InterventionCandidate,
    run: DecisionRun,
    snapshot: StateSnapshot,
) -> None:
    if (
        result.run_id != run.run_id
        or result.candidate_id != candidate.candidate_id
        or result.baseline_snapshot_id != snapshot.snapshot_id
        or result.baseline_snapshot_hash != snapshot.snapshot_hash
        or result.simulation_id
        != derive_artifact_id("simulation-result", "simulation-result.v1", _result_identity(result))
        or result.provenance.producer != "flowlens.decision.c04_simulation"
        or result.provenance.producer_version != SCENARIO_ADAPTER_VERSION
        or result.provenance.input_artifact_ids
        != tuple(sorted((run.run_id, snapshot.snapshot_id, candidate.candidate_id)))
        or result.provenance.source_refs != candidate.provenance.source_refs
        or result.provenance.contract_versions != _C04_CONTRACT_VERSIONS
    ):
        _fail()
    if any(ref.available_at > run.as_of_time for ref in result.provenance.source_refs):
        raise C05BuildError("C05_FUTURE_INPUT", "BLOCKED_TEMPORAL")
    if candidate.family is InterventionFamily.NO_ACTION:
        if (
            result.status is not SimulationStatus.SUCCEEDED
            or result.scenario_id is not None
            or result.scenario_hash is not None
            or result.affected_entities
            or not _valid_measurements(result)
            or result.limitations != candidate.limitations
        ):
            _fail()
    elif result.status is SimulationStatus.SUCCEEDED:
        if (
            result.scenario_id is None
            or result.scenario_hash is None
            or not _valid_measurements(result)
            or result.limitations != candidate.limitations
        ):
            _fail()
    elif result.status in (SimulationStatus.UNAVAILABLE, SimulationStatus.FAILED):
        if (
            result.scenario_id is not None
            or result.scenario_hash is not None
            or result.affected_entities
            or result.measurements
        ):
            _fail()
        extras = set(result.limitations) - set(candidate.limitations)
        expected_codes = (
            {"C04_SCENARIO_EXECUTION_FAILED"}
            if result.status is SimulationStatus.FAILED
            else set(_C04_RESULT_LIMITATION_MESSAGES) - {"C04_SCENARIO_EXECUTION_FAILED"}
        )
        if len(extras) != 1 or next(iter(extras)).code not in expected_codes:
            _fail()
        extra = next(iter(extras))
        if extra.message != _C04_RESULT_LIMITATION_MESSAGES[extra.code]:
            _fail()
        expected_limitations = tuple(
            sorted((*candidate.limitations, extra), key=lambda item: (item.code, item.message))
        )
        if result.limitations != expected_limitations:
            _fail()
    else:
        _fail()


def validate_simulation_bundle(
    actual: SimulationBundle,
    candidates: CandidateSet,
    run: DecisionRun,
    snapshot: StateSnapshot,
) -> None:
    if not isinstance(actual, SimulationBundle):
        _fail()
    candidate_by_id = {item.candidate_id: item for item in candidates.candidates}
    if (
        actual.run_id != run.run_id
        or actual.snapshot_id != snapshot.snapshot_id
        or len(actual.results) != len(candidate_by_id) != 0
        or {item.candidate_id for item in actual.results} != set(candidate_by_id)
        or tuple((item.candidate_id, item.simulation_id) for item in actual.results)
        != tuple(sorted((item.candidate_id, item.simulation_id) for item in actual.results))
    ):
        _fail()
    for result in actual.results:
        _validate_result(result, candidate_by_id[result.candidate_id], run, snapshot)
    identity = {
        "run_id": run.run_id,
        "snapshot_id": snapshot.snapshot_id,
        "candidate_simulation_ids": tuple(
            (item.candidate_id, item.simulation_id) for item in actual.results
        ),
    }
    if (
        actual.simulation_bundle_id
        != derive_artifact_id("simulation-bundle", "simulation-bundle.v1", identity)
        or actual.provenance.producer != "flowlens.decision.c04_simulation"
        or actual.provenance.producer_version != SCENARIO_ADAPTER_VERSION
        or actual.provenance.input_artifact_ids
        != tuple(
            sorted(
                (
                    run.run_id,
                    snapshot.snapshot_id,
                    candidates.candidate_set_id,
                    *(item.simulation_id for item in actual.results),
                )
            )
        )
        or actual.provenance.source_refs != candidates.provenance.source_refs
        or actual.provenance.contract_versions != _C04_CONTRACT_VERSIONS
    ):
        _fail()
    lowered = canonical_json_text(actual).lower()
    if any(token in lowered for token in ("hidden_ground_truth", "ground_truth", "hgt_")):
        raise C05BuildError("C05_HGT_INPUT_PROHIBITED", "BLOCKED_HGT")


def validate_c05_inputs(
    run: DecisionRun,
    snapshot: StateSnapshot,
    bundle: EvidenceBundle,
    context: DecisionContext,
    signals: SignalBundle,
    diagnosis: DiagnosisRecord,
    candidates: CandidateSet,
    simulations: SimulationBundle,
) -> CanonicalC05Inputs:
    """Rebuild frozen upstream outputs and validate the supplied C04 result without rerunning it."""

    lowered = canonical_json_text(
        (run, snapshot, bundle, context, signals, diagnosis, candidates, simulations)
    ).lower()
    if any(token in lowered for token in ("hidden_ground_truth", "ground_truth", "hgt_")):
        raise C05BuildError("C05_HGT_INPUT_PROHIBITED", "BLOCKED_HGT")
    if any(
        item.available_at > run.as_of_time
        or (item.observed_at is not None and item.observed_at > run.as_of_time)
        for item in bundle.evidence
    ):
        raise C05BuildError("C05_FUTURE_INPUT", "BLOCKED_TEMPORAL")
    try:
        validate_run_snapshot(run, snapshot, context)
        canonical = validate_c04_inputs(bundle, context, signals, diagnosis)
    except (C04BuildError, TypeError, ValueError) as error:
        raise C05BuildError("C05_NONCANONICAL_C03_INPUT", "BLOCKED_CONTRACT") from error
    expected = build_candidate_set(bundle, context, canonical.signals, canonical.diagnosis)
    try:
        validate_candidate_set(candidates, expected)
    except (C04BuildError, TypeError, ValueError) as error:
        raise C05BuildError(
            "C05_NONCANONICAL_C04_CANDIDATES", "BLOCKED_CONTRACT"
        ) from error
    validate_simulation_bundle(simulations, expected, run, snapshot)
    return CanonicalC05Inputs(
        canonical.index,
        canonical.signals,
        canonical.diagnosis,
        expected,
        simulations,
    )
