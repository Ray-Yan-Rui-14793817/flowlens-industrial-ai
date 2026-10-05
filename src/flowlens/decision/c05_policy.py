"""Frozen deterministic policy vocabulary for W03-C05."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final

from flowlens.decision.enums import InterventionFamily, SignalType, SimulationStatus

DECISION_POLICY_VERSION: Final = "w03-c05-decision-v1"
EVALUATION_SCHEMA_VERSION: Final = "w03-c05-evaluation-v1"
PACKET_POLICY_VERSION: Final = "w03-c05-packet-v1"


class RelevanceClass(StrEnum):
    BASELINE = "BASELINE"
    ACTIVE = "ACTIVE"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


class MetricEffect(StrEnum):
    WORSE = "WORSE"
    EQUAL = "EQUAL"
    BETTER = "BETTER"
    NOT_COMPARABLE = "NOT_COMPARABLE"


class StressEffect(StrEnum):
    BASELINE = "BASELINE"
    WORSENED = "WORSENED"
    UNCHANGED = "UNCHANGED"
    MIXED = "MIXED"
    IMPROVED = "IMPROVED"
    NOT_COMPARABLE = "NOT_COMPARABLE"


DECISION_METRIC_DIRECTIONS: Final = MappingProxyType(
    {
        "target_delivered_quantity": "LOWER",
        "target_remaining_quantity": "HIGHER",
        "target_delivery_lag_seconds": "HIGHER",
        "target_failed_quantity": "HIGHER",
        "target_rework_quantity": "HIGHER",
        "target_max_operation_start_slippage_seconds": "HIGHER",
        "target_max_work_order_completion_slippage_seconds": "HIGHER",
    }
)

MEASUREMENT_UNITS: Final = MappingProxyType(
    {
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
)

MATERIAL_NONCAPACITY_SIGNALS: Final = (
    SignalType.SUPPLIER_LATE_RECEIPT,
    SignalType.MATERIAL_TIMING_RISK,
    SignalType.QUALITY_FAILURE,
    SignalType.REWORK_PRESENT,
    SignalType.QUALITY_DISPOSITION_UNKNOWN,
    SignalType.QUEUE_DELAY,
    SignalType.DELIVERY_RISK,
)

FAMILY_ORDER: Final = (
    InterventionFamily.NO_ACTION,
    InterventionFamily.SUPPLIER_INTERVENTION,
    InterventionFamily.QUALITY_INTERVENTION,
    InterventionFamily.CAPACITY_INTERVENTION,
)

SIMULATION_STATUS_ORDER: Final = MappingProxyType(
    {
        SimulationStatus.SUCCEEDED: 0,
        SimulationStatus.UNAVAILABLE: 1,
        SimulationStatus.FAILED: 2,
    }
)

STRESS_EFFECT_ORDER: Final = MappingProxyType(
    {
        StressEffect.WORSENED: 0,
        StressEffect.UNCHANGED: 1,
        StressEffect.NOT_COMPARABLE: 2,
        StressEffect.MIXED: 3,
        StressEffect.IMPROVED: 4,
        StressEffect.BASELINE: 5,
    }
)

COMMON_REASON_CODES: Final = (
    "C05_HUMAN_REVIEW_REQUIRED",
    "C05_NO_NUMERIC_CONFIDENCE",
    "C05_POLICY_V1",
)

LIMITATION_MESSAGES: Final = MappingProxyType(
    {
        "C05_HUMAN_AUTHORITY_REQUIRED": (
            "This artifact requires human review and grants no execution authority."
        ),
        "C05_INVESTIGATION_NOT_EXECUTION": (
            "A selected intervention family is only a bounded investigation focus."
        ),
        "C05_NO_ACTION_NOT_OPERATIONAL_EXECUTION": (
            "Neutral NO_ACTION is a human-review result, not an operational instruction."
        ),
        "C05_NO_CAUSAL_ROOT_CAUSE": (
            "The available evidence does not establish a causal attribution."
        ),
        "C05_NO_OPERATIONAL_ACTION_AUTHORITY": (
            "The recommendation cannot schedule, procure, release, replace, or mutate "
            "operational state."
        ),
        "C05_NO_STATISTICAL_CONFIDENCE": (
            "The categorical evaluation is not calibrated statistical confidence."
        ),
        "C05_NONMONOTONIC_STRESS_RESULT": (
            "The active stress comparison is nonmonotonic and requires human review."
        ),
        "C05_PARTIAL_COMPARISON": (
            "The active-family comparison is incomplete and is not auto-resolved."
        ),
        "C05_SCENARIO_SCOPE_NOT_ORDER_TARGETED": (
            "Frozen scenario selection is not guaranteed to target the current order."
        ),
        "C05_SIMULATION_NOT_DECISION_DISCRIMINATING": (
            "The successful stress comparison does not distinguish the active investigation "
            "family."
        ),
        "C05_STRESS_PROBE_NOT_INTERVENTION_EFFICACY": (
            "The C04 stress probe does not establish intervention efficacy."
        ),
        "C05_TIE_NOT_AUTO_RESOLVED": (
            "A semantic tie is preserved for human review and is not broken by identifier order."
        ),
    }
)

COMMON_LIMITATION_CODES: Final = (
    "C05_HUMAN_AUTHORITY_REQUIRED",
    "C05_NO_CAUSAL_ROOT_CAUSE",
    "C05_NO_OPERATIONAL_ACTION_AUTHORITY",
    "C05_NO_STATISTICAL_CONFIDENCE",
)

UNCERTAINTY_MESSAGES: Final = MappingProxyType(
    {
        "C05_TOP_TIE": "The top policy-relevant candidates remain tied for human review.",
        "C05_PARTIAL_ACTIVE_COMPARISON": (
            "At least one active family lacks a successful comparable simulation."
        ),
        "C05_INSUFFICIENT_RECOMMENDATION_BASIS": (
            "The canonical evidence is insufficient for a safe deterministic recommendation."
        ),
    }
)


def score_component_names() -> tuple[str, ...]:
    names = [
        f"evaluation.{family.value}.{field}"
        for family in FAMILY_ORDER
        for field in (
            "relevance_class",
            "simulation_status",
            "stress_effect",
            "decision_eligible",
        )
    ]
    names.extend(
        (
            "policy.active_family_count",
            "policy.active_succeeded_count",
            "policy.partial_active_comparison",
            "policy.neutral_no_action_eligible",
            "policy.top_tie_count",
        )
    )
    return tuple(sorted(names))
