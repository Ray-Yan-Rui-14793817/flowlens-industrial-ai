"""Fail-closed protected input validation for W03-C07."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn

from flowlens.data.generation.canonical import canonical_content_hash
from flowlens.data.generation.generator import GeneratedDataset
from flowlens.data.scenarios.config import ScenarioType
from flowlens.data.scenarios.ground_truth import HiddenGroundTruth, canonical_hgt_payload
from flowlens.data.scenarios.transformer import ScenarioResult
from flowlens.decision.c05_packet import build_decision_packet
from flowlens.decision.context import build_decision_context
from flowlens.decision.contracts import DecisionPacket
from flowlens.decision.enums import (
    InterventionFamily,
    RecommendationDisposition,
    SignalState,
    SignalType,
)
from flowlens.decision.serialization import canonical_json_bytes
from flowlens.evaluation.c07_policy import SCENARIO_FAMILY, TruthEffectMode
from flowlens.evaluation.c07_replay import (
    dataset_order_ids,
    derive_affected_order_ids,
    hgt_proves_capacity_arrival,
    hgt_proves_capacity_queue,
)


class C07EvaluationError(ValueError):
    """A bounded C07 contract, integrity, pairing, or isolation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class ValidatedEvaluationInputs:
    scenario_packet: DecisionPacket
    scenario: ScenarioResult
    baseline_dataset: GeneratedDataset
    baseline_packet: DecisionPacket | None
    effect_mode: TruthEffectMode
    expected_family: InterventionFamily | None
    affected_order_ids: tuple[str, ...]
    order_affected: bool
    observable_by_c03: bool
    scenario_created_order: bool


def _fail(code: str, error: Exception | None = None) -> NoReturn:
    if error is None:
        raise C07EvaluationError(code)
    raise C07EvaluationError(code) from error


def _validate_dataset(dataset: GeneratedDataset, label: str) -> str:
    if not isinstance(dataset, GeneratedDataset):
        _fail(f"C07_{label}_DATASET_TYPE")
    try:
        recomputed = canonical_content_hash(dataset.rows_by_table)
    except (KeyError, TypeError, ValueError) as error:
        _fail(f"C07_{label}_DATASET_NONCANONICAL", error)
    if recomputed != dataset.dataset_version.content_hash:
        _fail(f"C07_{label}_DATASET_HASH_MISMATCH")
    if sum(len(rows) for rows in dataset.rows_by_table.values()) != (
        dataset.dataset_version.row_count_total
    ):
        _fail(f"C07_{label}_DATASET_ROW_COUNT_MISMATCH")
    return recomputed


def _validate_hgt(scenario: ScenarioResult) -> HiddenGroundTruth:
    if not isinstance(scenario, ScenarioResult):
        _fail("C07_SCENARIO_RESULT_TYPE")
    try:
        ScenarioResult.__post_init__(scenario)
        supplied = scenario.ground_truth
        rebuilt = HiddenGroundTruth(
            schema_version=supplied.schema_version,
            scenario_id=supplied.scenario_id,
            scenario_type=supplied.scenario_type,
            scenario_version=supplied.scenario_version,
            scenario_seed=supplied.scenario_seed,
            baseline_dataset_version_id=supplied.baseline_dataset_version_id,
            scenario_dataset_version_id=supplied.scenario_dataset_version_id,
            window_start=supplied.window_start,
            window_end=supplied.window_end,
            parameters=supplied.parameters,
            target_entity_ids=supplied.target_entity_ids,
            affected_entities_by_table=supplied.affected_entities_by_table,
            causal_chain=supplied.causal_chain,
        )
    except (AttributeError, TypeError, ValueError) as error:
        _fail("C07_HGT_NONCANONICAL", error)
    if (
        rebuilt.hgt_hash != supplied.hgt_hash
        or rebuilt.hgt_id != supplied.hgt_id
        or canonical_hgt_payload(rebuilt) != canonical_hgt_payload(supplied)
    ):
        _fail("C07_HGT_IDENTITY_MISMATCH")
    return supplied


def _validate_packet(packet: DecisionPacket, label: str) -> None:
    if not isinstance(packet, DecisionPacket):
        _fail(f"C07_{label}_PACKET_TYPE")
    if packet.recommendation.disposition is RecommendationDisposition.CANDIDATE_RECOMMENDED:
        _fail("C07_CANDIDATE_RECOMMENDED_PROHIBITED")
    try:
        context = build_decision_context(packet.snapshot, packet.evidence)
        rebuilt = build_decision_packet(
            packet.run,
            packet.snapshot,
            packet.evidence,
            context,
            packet.signals,
            packet.diagnosis,
            packet.candidates,
            packet.simulations,
            recommendation=packet.recommendation,
        )
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        _fail(f"C07_{label}_PACKET_NONCANONICAL", error)
    if canonical_json_bytes(rebuilt) != canonical_json_bytes(packet):
        _fail(f"C07_{label}_PACKET_NONCANONICAL")


def _signal_state(packet: DecisionPacket, signal_type: SignalType) -> SignalState:
    values = tuple(
        signal.state for signal in packet.signals.signals if signal.signal_type is signal_type
    )
    if len(values) != 1:
        _fail("C07_SIGNAL_ENVELOPE_MISMATCH")
    return values[0]


def _is_neutral(ground_truth: HiddenGroundTruth) -> bool:
    return not any(ground_truth.affected_entities_by_table.values()) and not (
        ground_truth.causal_chain
    )


def validate_evaluation_inputs(
    scenario_packet: DecisionPacket,
    scenario: ScenarioResult,
    *,
    baseline_dataset: GeneratedDataset,
    baseline_packet: DecisionPacket | None,
) -> ValidatedEvaluationInputs:
    """Validate canonical runtime artifacts before admitting protected truth."""

    _validate_packet(scenario_packet, "SCENARIO")
    if baseline_packet is not None:
        _validate_packet(baseline_packet, "BASELINE")
    ground_truth = _validate_hgt(scenario)
    scenario_hash = _validate_dataset(scenario.dataset, "SCENARIO")
    baseline_hash = _validate_dataset(baseline_dataset, "BASELINE")

    scenario_dataset_id = scenario.dataset.dataset_version.dataset_version_id
    baseline_dataset_id = baseline_dataset.dataset_version.dataset_version_id
    if scenario_dataset_id != ground_truth.scenario_dataset_version_id:
        _fail("C07_HGT_SCENARIO_DATASET_MISMATCH")
    if baseline_dataset_id != ground_truth.baseline_dataset_version_id:
        _fail("C07_HGT_BASELINE_DATASET_MISMATCH")
    if (
        scenario_packet.run.dataset_version != scenario_dataset_id
        or scenario_packet.run.dataset_hash != scenario_hash
    ):
        _fail("C07_SCENARIO_PACKET_DATASET_MISMATCH")
    if baseline_packet is not None and (
        baseline_packet.run.dataset_version != baseline_dataset_id
        or baseline_packet.run.dataset_hash != baseline_hash
    ):
        _fail("C07_BASELINE_PACKET_DATASET_MISMATCH")

    try:
        affected_order_ids = derive_affected_order_ids(scenario.dataset, ground_truth)
        scenario_order_ids = set(dataset_order_ids(scenario.dataset))
        baseline_order_ids = set(dataset_order_ids(baseline_dataset))
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        _fail("C07_AFFECTED_ORDER_BINDING_MISMATCH", error)
    order_id = scenario_packet.run.order_id
    if order_id not in scenario_order_ids:
        _fail("C07_SCENARIO_ORDER_MISSING")
    neutral = _is_neutral(ground_truth)
    order_affected = order_id in affected_order_ids
    scenario_created = order_id not in baseline_order_ids

    if neutral:
        if affected_order_ids or scenario_created:
            _fail("C07_NEUTRAL_ORDER_BINDING_MISMATCH")
    elif not order_affected:
        _fail("C07_EFFECTFUL_ORDER_NOT_AFFECTED")

    if scenario_created:
        if baseline_packet is not None:
            _fail("C07_CREATED_ORDER_BASELINE_PACKET_PROHIBITED")
        if (
            ground_truth.scenario_type is not ScenarioType.CAPACITY_SURGE
            or not hgt_proves_capacity_arrival(ground_truth, order_id)
        ):
            _fail("C07_CREATED_ORDER_ARRIVAL_NOT_PROVEN")
    else:
        if baseline_packet is None:
            _fail("C07_BASELINE_PACKET_REQUIRED")
        if (
            baseline_packet.run.order_id != order_id
            or baseline_packet.run.as_of_time != scenario_packet.run.as_of_time
            or baseline_packet.run.contract_bundle_version
            != scenario_packet.run.contract_bundle_version
            or baseline_packet.run.tool_registry_version
            != scenario_packet.run.tool_registry_version
        ):
            _fail("C07_BASELINE_PAIR_MISMATCH")

    if neutral:
        effect_mode = TruthEffectMode.NEUTRAL_CONTROL
        expected_family = None
    else:
        try:
            expected_family = SCENARIO_FAMILY[ground_truth.scenario_type]
        except KeyError as error:
            _fail("C07_SCENARIO_TYPE_UNSUPPORTED", error)
        if ground_truth.scenario_type is ScenarioType.CAPACITY_SURGE:
            try:
                queue_observable = hgt_proves_capacity_queue(
                    scenario.dataset, ground_truth, order_id
                )
            except (AttributeError, KeyError, TypeError, ValueError) as error:
                _fail("C07_CAPACITY_QUEUE_BINDING_MISMATCH", error)
            effect_mode = (
                TruthEffectMode.EFFECTFUL_OBSERVABLE
                if queue_observable
                else TruthEffectMode.EFFECTFUL_NOT_OBSERVABLE
            )
        else:
            effect_mode = TruthEffectMode.EFFECTFUL_OBSERVABLE

    if ground_truth.scenario_type is ScenarioType.CAPACITY_SURGE and (
        _signal_state(scenario_packet, SignalType.CAPACITY_PRESSURE) is not SignalState.UNKNOWN
    ):
        _fail("C07_CAPACITY_PRESSURE_MUST_REMAIN_UNKNOWN")

    return ValidatedEvaluationInputs(
        scenario_packet=scenario_packet,
        scenario=scenario,
        baseline_dataset=baseline_dataset,
        baseline_packet=baseline_packet,
        effect_mode=effect_mode,
        expected_family=expected_family,
        affected_order_ids=affected_order_ids,
        order_affected=order_affected,
        observable_by_c03=effect_mode is TruthEffectMode.EFFECTFUL_OBSERVABLE,
        scenario_created_order=scenario_created,
    )
