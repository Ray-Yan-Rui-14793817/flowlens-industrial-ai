"""Frozen deterministic policy vocabulary for W03-C07."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final

from flowlens.data.scenarios.config import ScenarioType
from flowlens.decision.enums import InterventionFamily, SignalType

EVALUATOR_VERSION: Final = "w03-c07-evaluator-v1"
METRIC_POLICY_VERSION: Final = "w03-c07-metrics-v1"
REPLAY_POLICY_VERSION: Final = "w03-c07-replay-v1"
PRODUCER: Final = "flowlens.evaluation.c07_recommendation"


class TruthEffectMode(StrEnum):
    """Closed C07 truth-observability classification."""

    NEUTRAL_CONTROL = "NEUTRAL_CONTROL"
    EFFECTFUL_OBSERVABLE = "EFFECTFUL_OBSERVABLE"
    EFFECTFUL_NOT_OBSERVABLE = "EFFECTFUL_NOT_OBSERVABLE"


SCENARIO_FAMILY: Final = MappingProxyType(
    {
        ScenarioType.SUPPLIER_DEGRADATION: InterventionFamily.SUPPLIER_INTERVENTION,
        ScenarioType.QUALITY_DETERIORATION: InterventionFamily.QUALITY_INTERVENTION,
        ScenarioType.CAPACITY_SURGE: InterventionFamily.CAPACITY_INTERVENTION,
    }
)

EXPECTED_SIGNALS: Final = MappingProxyType(
    {
        ScenarioType.SUPPLIER_DEGRADATION: (
            SignalType.SUPPLIER_LATE_RECEIPT,
            SignalType.MATERIAL_TIMING_RISK,
        ),
        ScenarioType.QUALITY_DETERIORATION: (
            SignalType.QUALITY_FAILURE,
            SignalType.REWORK_PRESENT,
        ),
        ScenarioType.CAPACITY_SURGE: (SignalType.QUEUE_DELAY,),
    }
)

METRIC_TYPES: Final = MappingProxyType(
    {
        "evaluation.applicable": (bool,),
        "evaluation.candidate_relevance": (bool, type(None)),
        "evaluation.cause_direction_correct": (bool, type(None)),
        "evaluation.false_positive": (bool, type(None)),
        "evaluation.neutral_stability": (bool, type(None)),
        "evaluation.recommendation_coverage": (bool, type(None)),
        "recommendation.disposition": (str,),
        "recommendation.selected_family": (str, type(None)),
        "truth.effect_mode": (str,),
        "truth.expected_family": (str, type(None)),
        "truth.hgt_hash": (str,),
        "truth.hgt_id": (str,),
        "truth.observable_by_c03": (bool,),
        "truth.order_affected": (bool,),
        "truth.scenario_dataset_version_id": (str,),
        "truth.scenario_id": (str,),
        "truth.scenario_type": (str,),
    }
)
METRIC_NAMES: Final = tuple(METRIC_TYPES)

COMMON_REASON_CODES: Final = (
    "C07_POLICY_V1",
    "C07_PROTECTED_EVALUATION_ONLY",
)

RESULT_REASON_CODES: Final = frozenset(
    {
        "C07_CANDIDATE_RELEVANCE_MISSING",
        "C07_CANDIDATE_RELEVANCE_NOT_APPLICABLE",
        "C07_CANDIDATE_RELEVANCE_PRESENT",
        "C07_CAUSE_DIRECTION_CORRECT",
        "C07_CAUSE_DIRECTION_MISMATCH",
        "C07_CAUSE_DIRECTION_NOT_APPLICABLE",
        "C07_EFFECTFUL_NOT_OBSERVABLE",
        "C07_EFFECTFUL_OBSERVABLE",
        "C07_FALSE_POSITIVE_NONE",
        "C07_FALSE_POSITIVE_NOT_APPLICABLE",
        "C07_FALSE_POSITIVE_PRESENT",
        "C07_NEUTRAL_CONTROL",
        "C07_NEUTRAL_STABILITY_NOT_APPLICABLE",
        "C07_NEUTRAL_STABLE",
        "C07_NEUTRAL_UNSTABLE",
        "C07_RECOMMENDATION_COVERAGE_MISSING",
        "C07_RECOMMENDATION_COVERAGE_NOT_APPLICABLE",
        "C07_RECOMMENDATION_COVERAGE_PRESENT",
    }
)

LIMITATION_MESSAGES: Final = MappingProxyType(
    {
        "C07_CAPACITY_ARRIVAL_ONLY_NOT_IDENTIFIABLE": (
            "C03 v1 does not expose a causal capacity-arrival signal; HGT cannot be used "
            "to retroactively grant runtime causal knowledge."
        ),
        "C07_CASE_LEVEL_ONLY": (
            "C07 v1 emits deterministic case-level evaluation artifacts; aggregate corpus "
            "rates belong only to the harness/report."
        ),
        "C07_NO_STATISTICAL_ACCURACY": (
            "A case-level protected evaluation is not calibrated accuracy, probability or "
            "confidence."
        ),
        "C07_OUTCOME_EVALUATION_DEFERRED": (
            "C07 v1 evaluates the frozen recommendation; operational outcome evaluation is "
            "not implemented."
        ),
        "C07_STRESS_PROBE_NOT_EFFICACY": (
            "C04 stress probes do not establish intervention efficacy or operational benefit."
        ),
        "C07_SYNTHETIC_HGT_ONLY": (
            "The protected truth is synthetic scenario evaluation truth and is not "
            "production causal truth."
        ),
    }
)

UNIVERSAL_LIMITATION_CODES: Final = (
    "C07_CASE_LEVEL_ONLY",
    "C07_NO_STATISTICAL_ACCURACY",
    "C07_OUTCOME_EVALUATION_DEFERRED",
    "C07_STRESS_PROBE_NOT_EFFICACY",
    "C07_SYNTHETIC_HGT_ONLY",
)
