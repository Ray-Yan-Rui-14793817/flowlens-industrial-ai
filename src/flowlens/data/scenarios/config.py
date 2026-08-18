"""Frozen typed configuration for deterministic C04 scenario transformations."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import Final
from zoneinfo import ZoneInfo

from flowlens.data.generation.canonical import normalize_scalar
from flowlens.data.generation.config import GenerationProfile, add_calendar_months

BUSINESS_TIMEZONE: Final = ZoneInfo("Asia/Shanghai")
MAX_SCENARIO_SEED: Final = 9_223_372_036_854_775_807
MAX_SCENARIO_VERSION_LENGTH: Final = 32


class ScenarioType(StrEnum):
    """The complete frozen W02-C04 scenario inventory."""

    SUPPLIER_DEGRADATION = "SCN_SUPPLIER_DEGRADATION"
    QUALITY_DETERIORATION = "SCN_QUALITY_DETERIORATION"
    CAPACITY_SURGE = "SCN_CAPACITY_SURGE"


def _validate_common(
    scenario_version: str,
    scenario_seed: int,
    window_start: datetime,
    window_end: datetime,
) -> None:
    if not isinstance(scenario_version, str):
        raise TypeError("scenario_version must be a string")
    if not scenario_version or scenario_version != scenario_version.strip():
        raise ValueError("scenario_version must be non-empty without surrounding whitespace")
    if len(scenario_version) > MAX_SCENARIO_VERSION_LENGTH:
        raise ValueError(
            f"scenario_version must be at most {MAX_SCENARIO_VERSION_LENGTH} characters"
        )
    if isinstance(scenario_seed, bool) or not isinstance(scenario_seed, int):
        raise TypeError("scenario_seed must be an integer")
    if not 0 <= scenario_seed <= MAX_SCENARIO_SEED:
        raise ValueError("scenario_seed must fit a nonnegative PostgreSQL BIGINT")
    for field_name, value in (("window_start", window_start), ("window_end", window_end)):
        if not isinstance(value, datetime):
            raise TypeError(f"{field_name} must be a datetime")
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} must be timezone-aware")
        if not isinstance(value.tzinfo, ZoneInfo) or value.tzinfo.key != BUSINESS_TIMEZONE.key:
            raise ValueError(f"{field_name} must use Asia/Shanghai timezone semantics")
    if window_start >= window_end:
        raise ValueError("scenario window must satisfy window_start < window_end")


def _require_positive_int(field_name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_positive_decimal(field_name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal):
        raise TypeError(f"{field_name} must be a Decimal")
    if not value.is_finite() or value <= 0:
        raise ValueError(f"{field_name} must be a finite positive Decimal")


def _require_probability(field_name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal):
        raise TypeError(f"{field_name} must be a Decimal")
    if not value.is_finite() or not Decimal("0") <= value <= Decimal("1"):
        raise ValueError(f"{field_name} must be between 0 and 1 inclusive")


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierDegradationConfig:
    """Typed contract for the future supplier-degradation intervention."""

    scenario_version: str
    scenario_seed: int
    window_start: datetime
    window_end: datetime
    affected_supplier_count: int = 2
    affected_critical_material_count: int = 5
    late_probability_delta: Decimal = Decimal("0.25")
    additional_delay_business_days_min: int = 3
    additional_delay_business_days_max: int = 8
    scenario_type: ScenarioType = field(
        default=ScenarioType.SUPPLIER_DEGRADATION,
        init=False,
    )

    def __post_init__(self) -> None:
        _validate_common(
            self.scenario_version,
            self.scenario_seed,
            self.window_start,
            self.window_end,
        )
        _require_positive_int("affected_supplier_count", self.affected_supplier_count)
        _require_positive_int(
            "affected_critical_material_count",
            self.affected_critical_material_count,
        )
        _require_probability("late_probability_delta", self.late_probability_delta)
        _require_positive_int(
            "additional_delay_business_days_min",
            self.additional_delay_business_days_min,
        )
        _require_positive_int(
            "additional_delay_business_days_max",
            self.additional_delay_business_days_max,
        )
        if self.additional_delay_business_days_min > self.additional_delay_business_days_max:
            raise ValueError("additional delay minimum must not exceed maximum")


@dataclass(frozen=True, slots=True, kw_only=True)
class QualityDeteriorationConfig:
    """Typed contract for the future quality-deterioration intervention."""

    scenario_version: str
    scenario_seed: int
    window_start: datetime
    window_end: datetime
    affected_product_count: int = 2
    affected_work_center_count: int = 1
    failure_probability_multiplier: Decimal = Decimal("2.2")
    rework_probability_delta: Decimal = Decimal("0.30")
    rework_duration_multiplier_min: Decimal = Decimal("1.2")
    rework_duration_multiplier_max: Decimal = Decimal("1.5")
    scenario_type: ScenarioType = field(
        default=ScenarioType.QUALITY_DETERIORATION,
        init=False,
    )

    def __post_init__(self) -> None:
        _validate_common(
            self.scenario_version,
            self.scenario_seed,
            self.window_start,
            self.window_end,
        )
        _require_positive_int("affected_product_count", self.affected_product_count)
        _require_positive_int("affected_work_center_count", self.affected_work_center_count)
        _require_positive_decimal(
            "failure_probability_multiplier",
            self.failure_probability_multiplier,
        )
        if self.failure_probability_multiplier < Decimal("1"):
            raise ValueError("failure_probability_multiplier must be at least 1")
        _require_probability("rework_probability_delta", self.rework_probability_delta)
        _require_positive_decimal(
            "rework_duration_multiplier_min",
            self.rework_duration_multiplier_min,
        )
        _require_positive_decimal(
            "rework_duration_multiplier_max",
            self.rework_duration_multiplier_max,
        )
        if self.rework_duration_multiplier_min < Decimal("1"):
            raise ValueError("rework duration multipliers must be at least 1")
        if self.rework_duration_multiplier_min > self.rework_duration_multiplier_max:
            raise ValueError("rework duration multiplier minimum must not exceed maximum")


@dataclass(frozen=True, slots=True, kw_only=True)
class CapacitySurgeConfig:
    """Typed contract for the future capacity-surge intervention."""

    scenario_version: str
    scenario_seed: int
    window_start: datetime
    window_end: datetime
    affected_work_center_count: int = 2
    arrival_volume_multiplier: Decimal = Decimal("1.5")
    queue_time_multiplier: Decimal = Decimal("1.7")
    scenario_type: ScenarioType = field(
        default=ScenarioType.CAPACITY_SURGE,
        init=False,
    )

    def __post_init__(self) -> None:
        _validate_common(
            self.scenario_version,
            self.scenario_seed,
            self.window_start,
            self.window_end,
        )
        _require_positive_int("affected_work_center_count", self.affected_work_center_count)
        _require_positive_decimal("arrival_volume_multiplier", self.arrival_volume_multiplier)
        _require_positive_decimal("queue_time_multiplier", self.queue_time_multiplier)
        if self.arrival_volume_multiplier < Decimal("1"):
            raise ValueError("arrival_volume_multiplier must be at least 1")
        if self.queue_time_multiplier < Decimal("1"):
            raise ValueError("queue_time_multiplier must be at least 1")


type ScenarioConfig = (
    SupplierDegradationConfig | QualityDeteriorationConfig | CapacitySurgeConfig
)

type CanonicalConfigValue = None | bool | int | str


def scenario_parameters(config: ScenarioConfig) -> Mapping[str, int | Decimal]:
    """Return the exact scenario-family parameter set in stable key order."""

    if isinstance(config, SupplierDegradationConfig):
        values: dict[str, int | Decimal] = {
            "additional_delay_business_days_max": config.additional_delay_business_days_max,
            "additional_delay_business_days_min": config.additional_delay_business_days_min,
            "affected_critical_material_count": config.affected_critical_material_count,
            "affected_supplier_count": config.affected_supplier_count,
            "late_probability_delta": config.late_probability_delta,
        }
    elif isinstance(config, QualityDeteriorationConfig):
        values = {
            "affected_product_count": config.affected_product_count,
            "affected_work_center_count": config.affected_work_center_count,
            "failure_probability_multiplier": config.failure_probability_multiplier,
            "rework_duration_multiplier_max": config.rework_duration_multiplier_max,
            "rework_duration_multiplier_min": config.rework_duration_multiplier_min,
            "rework_probability_delta": config.rework_probability_delta,
        }
    elif isinstance(config, CapacitySurgeConfig):
        values = {
            "affected_work_center_count": config.affected_work_center_count,
            "arrival_volume_multiplier": config.arrival_volume_multiplier,
            "queue_time_multiplier": config.queue_time_multiplier,
        }
    else:
        raise TypeError("config must be one of the three frozen scenario config types")
    return MappingProxyType(dict(sorted(values.items())))


def _require_parameter_keys(
    parameters: Mapping[str, object],
    expected: set[str],
) -> None:
    actual = set(parameters)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"scenario parameter set mismatch; missing={missing}, extra={extra}")


def _integer_parameter(parameters: Mapping[str, object], key: str) -> int:
    value = parameters[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"scenario parameter {key} must be an integer")
    return value


def _decimal_parameter(parameters: Mapping[str, object], key: str) -> Decimal:
    value = parameters[key]
    if not isinstance(value, Decimal):
        raise TypeError(f"scenario parameter {key} must be a Decimal")
    return value


def scenario_config_from_parameters(
    *,
    scenario_type: ScenarioType,
    scenario_version: str,
    scenario_seed: int,
    window_start: datetime,
    window_end: datetime,
    parameters: Mapping[str, object],
) -> ScenarioConfig:
    """Reconstruct and validate typed semantics from an exact parameter mapping."""

    if scenario_type is ScenarioType.SUPPLIER_DEGRADATION:
        _require_parameter_keys(
            parameters,
            {
                "affected_supplier_count",
                "affected_critical_material_count",
                "late_probability_delta",
                "additional_delay_business_days_min",
                "additional_delay_business_days_max",
            },
        )
        return SupplierDegradationConfig(
            scenario_version=scenario_version,
            scenario_seed=scenario_seed,
            window_start=window_start,
            window_end=window_end,
            affected_supplier_count=_integer_parameter(parameters, "affected_supplier_count"),
            affected_critical_material_count=_integer_parameter(
                parameters,
                "affected_critical_material_count",
            ),
            late_probability_delta=_decimal_parameter(parameters, "late_probability_delta"),
            additional_delay_business_days_min=_integer_parameter(
                parameters,
                "additional_delay_business_days_min",
            ),
            additional_delay_business_days_max=_integer_parameter(
                parameters,
                "additional_delay_business_days_max",
            ),
        )
    if scenario_type is ScenarioType.QUALITY_DETERIORATION:
        _require_parameter_keys(
            parameters,
            {
                "affected_product_count",
                "affected_work_center_count",
                "failure_probability_multiplier",
                "rework_probability_delta",
                "rework_duration_multiplier_min",
                "rework_duration_multiplier_max",
            },
        )
        return QualityDeteriorationConfig(
            scenario_version=scenario_version,
            scenario_seed=scenario_seed,
            window_start=window_start,
            window_end=window_end,
            affected_product_count=_integer_parameter(parameters, "affected_product_count"),
            affected_work_center_count=_integer_parameter(
                parameters,
                "affected_work_center_count",
            ),
            failure_probability_multiplier=_decimal_parameter(
                parameters,
                "failure_probability_multiplier",
            ),
            rework_probability_delta=_decimal_parameter(
                parameters,
                "rework_probability_delta",
            ),
            rework_duration_multiplier_min=_decimal_parameter(
                parameters,
                "rework_duration_multiplier_min",
            ),
            rework_duration_multiplier_max=_decimal_parameter(
                parameters,
                "rework_duration_multiplier_max",
            ),
        )
    if scenario_type is ScenarioType.CAPACITY_SURGE:
        _require_parameter_keys(
            parameters,
            {
                "affected_work_center_count",
                "arrival_volume_multiplier",
                "queue_time_multiplier",
            },
        )
        return CapacitySurgeConfig(
            scenario_version=scenario_version,
            scenario_seed=scenario_seed,
            window_start=window_start,
            window_end=window_end,
            affected_work_center_count=_integer_parameter(
                parameters,
                "affected_work_center_count",
            ),
            arrival_volume_multiplier=_decimal_parameter(
                parameters,
                "arrival_volume_multiplier",
            ),
            queue_time_multiplier=_decimal_parameter(parameters, "queue_time_multiplier"),
        )
    raise TypeError("scenario_type must be one of the three frozen scenario families")


def canonical_scenario_configuration(
    config: ScenarioConfig,
) -> Mapping[str, CanonicalConfigValue | Mapping[str, CanonicalConfigValue]]:
    """Build the stable configuration object that participates in scenario identity."""

    parameters = {
        key: normalize_scalar(value)
        for key, value in scenario_parameters(config).items()
    }
    values: dict[str, CanonicalConfigValue | Mapping[str, CanonicalConfigValue]] = {
        "parameters": MappingProxyType(parameters),
        "window_end": normalize_scalar(config.window_end),
        "window_start": normalize_scalar(config.window_start),
    }
    return MappingProxyType(values)


def canonical_scenario_identity_payload(
    baseline_dataset_version_id: str,
    config: ScenarioConfig,
) -> str:
    """Serialize the exact C04-A identity inputs without repr or locale dependence."""

    if not isinstance(baseline_dataset_version_id, str):
        raise TypeError("baseline_dataset_version_id must be a string")
    if not baseline_dataset_version_id or baseline_dataset_version_id != (
        baseline_dataset_version_id.strip()
    ):
        raise ValueError("baseline_dataset_version_id must be non-empty without whitespace")
    canonical_config = canonical_scenario_configuration(config)
    canonical_parameters = canonical_config["parameters"]
    if not isinstance(canonical_parameters, Mapping):
        raise AssertionError("canonical scenario parameters must be a mapping")
    payload = {
        "baseline_dataset_version_id": baseline_dataset_version_id,
        "scenario_configuration": {
            "parameters": dict(canonical_parameters),
            "window_end": canonical_config["window_end"],
            "window_start": canonical_config["window_start"],
        },
        "scenario_seed": config.scenario_seed,
        "scenario_type": config.scenario_type.value,
        "scenario_version": config.scenario_version,
    }
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def scenario_namespace(
    baseline_dataset_version_id: str,
    config: ScenarioConfig,
) -> str:
    """Derive the single canonical scenario SHA-256 namespace."""

    payload = canonical_scenario_identity_payload(baseline_dataset_version_id, config)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def default_demo_window(
    scenario_type: ScenarioType,
    period_start: date,
    profile: GenerationProfile,
) -> tuple[datetime, datetime]:
    """Return the frozen DEMO window; shorter profiles must supply one explicitly."""

    if not isinstance(scenario_type, ScenarioType):
        raise TypeError("scenario_type must be a ScenarioType")
    if isinstance(period_start, datetime) or not isinstance(period_start, date):
        raise TypeError("period_start must be a date")
    if profile is not GenerationProfile.DEMO:
        raise ValueError("default scenario windows are defined only for the DEMO profile")
    month_bounds = {
        ScenarioType.SUPPLIER_DEGRADATION: (5, 9),
        ScenarioType.QUALITY_DETERIORATION: (9, 12),
        ScenarioType.CAPACITY_SURGE: (13, 16),
    }
    start_month, end_month = month_bounds[scenario_type]
    start_date = add_calendar_months(period_start, start_month - 1)
    end_date = add_calendar_months(period_start, end_month - 1)
    return (
        datetime.combine(start_date, time.min, BUSINESS_TIMEZONE),
        datetime.combine(end_date, time.min, BUSINESS_TIMEZONE),
    )


def validate_config_for_baseline_period(
    config: ScenarioConfig,
    period_start: date,
    period_end: date,
) -> None:
    """Require the scenario interval to be contained by the inclusive business period."""

    if isinstance(period_start, datetime) or not isinstance(period_start, date):
        raise TypeError("period_start must be a date")
    if isinstance(period_end, datetime) or not isinstance(period_end, date):
        raise TypeError("period_end must be a date")
    if period_start >= period_end:
        raise ValueError("baseline period must satisfy period_start < period_end")
    baseline_start = datetime.combine(period_start, time.min, BUSINESS_TIMEZONE)
    baseline_end_exclusive = datetime.combine(
        period_end + timedelta(days=1),
        time.min,
        BUSINESS_TIMEZONE,
    )
    if config.window_start < baseline_start or config.window_end > baseline_end_exclusive:
        raise ValueError("scenario window must lie inside the baseline business period")
