"""Frozen W03-C03 signal and diagnosis policy constants.

This module deliberately compiles the published policy into Python constants so
runtime evaluation never reads repository files or any other ambient state.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from flowlens.decision.enums import ClaimType, SignalType
from flowlens.decision.primitives import Limitation

C03_POLICY_VERSION: Final = "w03-c03-v1"
C03_PRODUCER_VERSION: Final = "w03-c03-v1"
C03_POLICY_REASON: Final = "C03_POLICY_V1"

LIMITATION_MESSAGES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "C03_ACCOUNTING_NOT_RELEASE": (
            "Failed-quantity accounting does not establish formal quality release or a "
            "specific disposition."
        ),
        "C03_ASSOCIATION_NOT_ALLOCATION": (
            "Material/time association does not establish order-specific procurement allocation."
        ),
        "C03_CAPACITY_NOT_IDENTIFIABLE": (
            "An order-centric snapshot lacks complete competing workload, shift calendars, and "
            "allocatable capacity."
        ),
        "C03_CLOSED_WORLD_OBSERVATION_ASSUMPTION": (
            "Absence means absence in the admitted C02 synthetic observation scope; late-arriving "
            "real-world records are not modeled."
        ),
        "C03_INACTIVE_NOT_ALL_CLEAR": (
            "INACTIVE denotes absence of the specified indicator in the admitted observation "
            "scope, not an all-clear business decision."
        ),
        "C03_INSPECTION_NOT_RELEASE": (
            "An inspection result does not establish a formal release event."
        ),
        "C03_NOT_MATERIAL_AVAILABILITY": (
            "This timing warning does not establish net stock, material consumption, or "
            "production-time availability."
        ),
        "C03_OBSERVED_HISTORY_NOT_CURRENT_CAUSE": (
            "A recorded historical warning may persist after resolution and must not be described "
            "as a current causal impediment."
        ),
        "C03_REWORK_NOT_RELEASE": ("Recorded rework does not establish formal quality release."),
        "C03_RULE_BASED_NOT_CAUSAL": (
            "This is a versioned rule indicator, not causal or root-cause evidence."
        ),
        "C03_RULE_INDICATOR_NOT_FORECAST": (
            "The rule is a deterministic commitment warning, not a calibrated forecast or "
            "probability."
        ),
        "C03_SCOPE_PARTIALLY_OBSERVED": (
            "Some rule-relevant scope lacks required evidence; a positive witness does not resolve "
            "the remaining uncertainty."
        ),
        "C03_START_SLIPPAGE_NOT_QUEUE_MEASUREMENT": (
            "Planned-versus-observed start slippage is not measured queue residence time; the "
            "plan availability includes the C02 synthetic proxy."
        ),
    }
)

COMMON_LIMITATION_CODES: Final = (
    "C03_CLOSED_WORLD_OBSERVATION_ASSUMPTION",
    "C03_INACTIVE_NOT_ALL_CLEAR",
    "C03_RULE_BASED_NOT_CAUSAL",
)


@dataclass(frozen=True, slots=True)
class SignalPolicy:
    entities: tuple[str, ...]
    domain_limitation_codes: tuple[str, ...]
    active_statement: str | None
    unknown_statement: str
    active_claim_type: ClaimType | None


SIGNAL_POLICIES: Final[Mapping[SignalType, SignalPolicy]] = MappingProxyType(
    {
        SignalType.CAPACITY_PRESSURE: SignalPolicy(
            entities=("dim_work_center", "fact_operation"),
            domain_limitation_codes=("C03_CAPACITY_NOT_IDENTIFIABLE",),
            active_statement=None,
            unknown_statement=(
                "Real capacity pressure is unknown because the order-centric input does not "
                "establish complete competing workload, shift calendars, or allocatable capacity."
            ),
            active_claim_type=None,
        ),
        SignalType.DELIVERY_RISK: SignalPolicy(
            entities=("fact_delivery", "fact_sales_order", "fact_work_order"),
            domain_limitation_codes=("C03_RULE_INDICATOR_NOT_FORECAST",),
            active_statement=(
                "The delivery commitment is overdue with remaining quantity, or an incomplete "
                "work-order plan ends after that commitment; this is a deterministic warning, not "
                "a delivery probability or causal attribution."
            ),
            unknown_statement=(
                "The available observations do not support a delivery forecast before fulfillment "
                "or a defined commitment warning."
            ),
            active_claim_type=ClaimType.DERIVED_CLAIM,
        ),
        SignalType.MATERIAL_TIMING_RISK: SignalPolicy(
            entities=("fact_material_requirement", "fact_purchase_order"),
            domain_limitation_codes=(
                "C03_ASSOCIATION_NOT_ALLOCATION",
                "C03_NOT_MATERIAL_AVAILABILITY",
                "C03_OBSERVED_HISTORY_NOT_CURRENT_CAUSE",
            ),
            active_statement=(
                "A purchase order associated by material has a timing warning relative to a "
                "requirement need-by time; this does not prove a material shortage or an "
                "order-specific allocation."
            ),
            unknown_statement=(
                "The available requirement and associated procurement records do not establish "
                "the material-timing indicator."
            ),
            active_claim_type=ClaimType.ASSOCIATIVE_CLAIM,
        ),
        SignalType.QUALITY_DISPOSITION_UNKNOWN: SignalPolicy(
            entities=("fact_quality_inspection", "fact_rework"),
            domain_limitation_codes=("C03_ACCOUNTING_NOT_RELEASE",),
            active_statement=(
                "The versioned failed-quantity accounting leaves a positive disposition gap; the "
                "disposition is unknown and no scrap, replacement, concession, or release is "
                "inferred."
            ),
            unknown_statement=(
                "The available evidence is insufficient to determine a failed-quantity "
                "disposition gap."
            ),
            active_claim_type=ClaimType.DERIVED_CLAIM,
        ),
        SignalType.QUALITY_FAILURE: SignalPolicy(
            entities=("fact_quality_inspection",),
            domain_limitation_codes=(
                "C03_INSPECTION_NOT_RELEASE",
                "C03_OBSERVED_HISTORY_NOT_CURRENT_CAUSE",
            ),
            active_statement=(
                "At least one eligible inspection records a positive failed quantity; this "
                "observation does not establish formal quality-release status."
            ),
            unknown_statement=(
                "Eligible inspection evidence is insufficient to determine the "
                "recorded-quality-failure indicator."
            ),
            active_claim_type=ClaimType.FACT_CLAIM,
        ),
        SignalType.QUEUE_DELAY: SignalPolicy(
            entities=("fact_operation",),
            domain_limitation_codes=(
                "C03_OBSERVED_HISTORY_NOT_CURRENT_CAUSE",
                "C03_START_SLIPPAGE_NOT_QUEUE_MEASUREMENT",
            ),
            active_statement=(
                "A recorded operation started after its planned start or has not recorded a start "
                "by an overdue planned-start time; this is a start-slippage proxy, not a measured "
                "queue duration or a causal capacity finding."
            ),
            unknown_statement=(
                "Eligible operation timing evidence is insufficient to determine the "
                "start-slippage proxy."
            ),
            active_claim_type=ClaimType.DERIVED_CLAIM,
        ),
        SignalType.REWORK_PRESENT: SignalPolicy(
            entities=("fact_quality_inspection", "fact_rework"),
            domain_limitation_codes=(
                "C03_OBSERVED_HISTORY_NOT_CURRENT_CAUSE",
                "C03_REWORK_NOT_RELEASE",
            ),
            active_statement=(
                "Eligible rework has been recorded; this does not imply that it is still in "
                "progress or that formal quality release has occurred."
            ),
            unknown_statement=(
                "The available observation scope is insufficient to determine recorded rework "
                "presence."
            ),
            active_claim_type=ClaimType.FACT_CLAIM,
        ),
        SignalType.SUPPLIER_LATE_RECEIPT: SignalPolicy(
            entities=("fact_material_requirement", "fact_purchase_order"),
            domain_limitation_codes=(
                "C03_ASSOCIATION_NOT_ALLOCATION",
                "C03_OBSERVED_HISTORY_NOT_CURRENT_CAUSE",
            ),
            active_statement=(
                "Associated procurement records contain receipt lateness or overdue outstanding "
                "quantity; they do not establish target-order allocation or causation."
            ),
            unknown_statement=(
                "Associated procurement evidence is insufficient to determine the "
                "receipt-lateness indicator."
            ),
            active_claim_type=ClaimType.ASSOCIATIVE_CLAIM,
        ),
    }
)


def limitations_for(signal_type: SignalType, partial: bool) -> tuple[Limitation, ...]:
    codes = {
        *COMMON_LIMITATION_CODES,
        *SIGNAL_POLICIES[signal_type].domain_limitation_codes,
    }
    if partial:
        codes.add("C03_SCOPE_PARTIALLY_OBSERVED")
    return tuple(Limitation(code=code, message=LIMITATION_MESSAGES[code]) for code in sorted(codes))
