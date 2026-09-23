"""Typed configuration and frozen profile definitions for baseline generation."""

from __future__ import annotations

import calendar
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import StrEnum
from types import MappingProxyType
from typing import Final


class GenerationProfile(StrEnum):
    """Supported synthetic dataset profiles."""

    TEST = "test"
    CI = "ci"
    DEMO = "demo"


@dataclass(frozen=True, slots=True)
class ProfileDefinition:
    """Contract-defined scale for one generation profile."""

    months: int
    sales_orders: int
    products: int
    materials: int
    suppliers: int
    customers: int
    work_centers: int


PROFILE_DEFINITIONS: Final[Mapping[GenerationProfile, ProfileDefinition]] = MappingProxyType(
    {
        GenerationProfile.TEST: ProfileDefinition(3, 150, 12, 25, 8, 15, 4),
        GenerationProfile.CI: ProfileDefinition(6, 800, 20, 50, 12, 30, 6),
        GenerationProfile.DEMO: ProfileDefinition(18, 12_000, 30, 80, 24, 60, 8),
    }
)
DEFAULT_DEMO_SEED: Final = 20_260_824
_MAX_BIGINT: Final = 9_223_372_036_854_775_807


def add_calendar_months(value: date, months: int) -> date:
    """Shift a date by whole calendar months using only the standard library."""

    if months < 0:
        raise ValueError("months must be nonnegative")
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    """All caller-controlled inputs that define one reproducible baseline run."""

    profile: GenerationProfile
    seed: int
    period_start: date
    generator_version: str
    generated_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.profile, GenerationProfile):
            raise TypeError("profile must be a GenerationProfile")
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise TypeError("seed must be an integer")
        if not 0 <= self.seed <= _MAX_BIGINT:
            raise ValueError("seed must fit a nonnegative PostgreSQL BIGINT")
        if isinstance(self.period_start, datetime) or not isinstance(self.period_start, date):
            raise TypeError("period_start must be a date")
        if not self.generator_version or not self.generator_version.strip():
            raise ValueError("generator_version must be non-empty")
        if len(self.generator_version) > 32:
            raise ValueError("generator_version must fit VARCHAR(32)")
        if self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("generated_at must be timezone-aware")

    @property
    def definition(self) -> ProfileDefinition:
        """Return the frozen scale associated with the selected profile."""

        return PROFILE_DEFINITIONS[self.profile]

    @property
    def period_end(self) -> date:
        """Return the inclusive final day of the profile's calendar period."""

        return add_calendar_months(self.period_start, self.definition.months) - timedelta(days=1)
