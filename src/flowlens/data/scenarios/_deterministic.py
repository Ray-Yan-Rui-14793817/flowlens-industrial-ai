"""Internal purpose-separated deterministic helpers for C04 interventions."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable, Sequence
from datetime import datetime, timedelta
from decimal import ROUND_CEILING, Decimal
from zoneinfo import ZoneInfo

from flowlens.data.scenarios.config import BUSINESS_TIMEZONE
from flowlens.data.scenarios.transformer import ScenarioIdentity


def purpose_digest(
    identity: ScenarioIdentity,
    purpose: str,
    entity_identity: str,
) -> str:
    """Hash one semantic decision independently from every other decision."""

    if not purpose or purpose != purpose.strip():
        raise ValueError("purpose must be non-empty without surrounding whitespace")
    if not entity_identity or entity_identity != entity_identity.strip():
        raise ValueError("entity_identity must be non-empty without surrounding whitespace")
    payload = {
        "entity_identity": entity_identity,
        "purpose": purpose,
        "scenario_namespace": identity.namespace,
    }
    serialized = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def rank_candidates[T](
    candidates: Iterable[T],
    identity: ScenarioIdentity,
    purpose: str,
    stable_id: Callable[[T], str],
) -> list[T]:
    """Deduplicate and sort candidates by frozen hash and stable-ID order."""

    by_id: dict[str, T] = {}
    for candidate in candidates:
        candidate_id = stable_id(candidate)
        if candidate_id in by_id:
            continue
        by_id[candidate_id] = candidate
    return sorted(
        by_id.values(),
        key=lambda candidate: (
            purpose_digest(identity, purpose, stable_id(candidate)),
            stable_id(candidate),
        ),
    )


def choose_value[T](
    values: Sequence[T],
    identity: ScenarioIdentity,
    purpose: str,
    entity_identity: str,
) -> T:
    """Map a SHA-256 value onto one non-empty discrete sequence."""

    if not values:
        raise ValueError("deterministic choice requires at least one value")
    digest_value = int(purpose_digest(identity, purpose, entity_identity), 16)
    return values[digest_value % len(values)]


def choose_inclusive_int(
    minimum: int,
    maximum: int,
    identity: ScenarioIdentity,
    purpose: str,
    entity_identity: str,
) -> int:
    """Choose one integer from an inclusive interval."""

    if minimum > maximum:
        raise ValueError("inclusive integer minimum must not exceed maximum")
    return choose_value(
        tuple(range(minimum, maximum + 1)),
        identity,
        purpose,
        entity_identity,
    )


def choose_hundredth_decimal(
    minimum: Decimal,
    maximum: Decimal,
    identity: ScenarioIdentity,
    purpose: str,
    entity_identity: str,
) -> Decimal:
    """Choose one Decimal from an inclusive 0.01-resolution interval."""

    step = Decimal("0.01")
    if minimum != minimum.quantize(step) or maximum != maximum.quantize(step):
        raise ValueError("configured duration multipliers must use 0.01 resolution")
    if minimum > maximum:
        raise ValueError("duration multiplier minimum must not exceed maximum")
    step_count = int(((maximum - minimum) / step).to_integral_exact())
    values = tuple(minimum + (step * index) for index in range(step_count + 1))
    return choose_value(values, identity, purpose, entity_identity)


def probability_target_count(population: int, probability: Decimal) -> int:
    """Return min(N, ceil(N*p)) using exact Decimal arithmetic."""

    if population < 0:
        raise ValueError("population must be nonnegative")
    if not Decimal("0") <= probability <= Decimal("1"):
        raise ValueError("probability must be between 0 and 1 inclusive")
    target = int(
        (Decimal(population) * probability).to_integral_value(rounding=ROUND_CEILING)
    )
    return min(population, target)


def add_business_days(timestamp: datetime, days: int) -> datetime:
    """Add positive Monday-Friday business days with the starting day excluded."""

    if isinstance(days, bool) or not isinstance(days, int) or days <= 0:
        raise ValueError("business-day count must be a positive integer")
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("business-day timestamp must be timezone-aware")
    if not isinstance(timestamp.tzinfo, ZoneInfo) or timestamp.tzinfo.key != (
        BUSINESS_TIMEZONE.key
    ):
        raise ValueError("business-day timestamp must use Asia/Shanghai semantics")
    result = timestamp
    remaining = days
    while remaining:
        result += timedelta(days=1)
        if result.weekday() < 5:
            remaining -= 1
    return result


def duration_microseconds(duration: timedelta) -> int:
    """Return exact signed microseconds without float conversion."""

    return (
        ((duration.days * 86_400) + duration.seconds) * 1_000_000
        + duration.microseconds
    )


def ceil_microsecond_duration(
    microseconds: Decimal,
    multiplier: Decimal,
) -> timedelta:
    """Multiply exact reference microseconds and round upward to a whole second."""

    if microseconds < 0:
        raise ValueError("baseline duration must be nonnegative")
    seconds = (
        (microseconds * multiplier) / Decimal(1_000_000)
    ).to_integral_value(rounding=ROUND_CEILING)
    return timedelta(seconds=int(seconds))


def ceil_duration(duration: timedelta, multiplier: Decimal) -> timedelta:
    """Multiply a duration exactly and round upward to a whole second."""

    return ceil_microsecond_duration(Decimal(duration_microseconds(duration)), multiplier)


def median_duration_microseconds(durations: Sequence[timedelta]) -> Decimal:
    """Return exact median microseconds, averaging the middle pair when even."""

    if not durations:
        raise ValueError("at least one baseline duration is required")
    microseconds = sorted(duration_microseconds(value) for value in durations)
    if microseconds[0] < 0:
        raise ValueError("baseline duration must be nonnegative")
    middle = len(microseconds) // 2
    if len(microseconds) % 2:
        median_microseconds = Decimal(microseconds[middle])
    else:
        median_microseconds = (
            Decimal(microseconds[middle - 1]) + Decimal(microseconds[middle])
        ) / Decimal(2)
    return median_microseconds
