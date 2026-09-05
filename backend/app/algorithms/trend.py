"""
Trend analysis: direction, rate of change, acceleration/deceleration.

Used for forest-cover history, AQI history, rainfall history, water-table
history — anything expressed as (year, value) observations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class Direction(str, Enum):
    INCREASING = "INCREASING"
    DECREASING = "DECREASING"
    STABLE = "STABLE"


@dataclass
class TrendResult:
    direction: Direction
    annual_rate: float  # units per year (linear slope)
    annual_rate_pct: float  # % of the first value, per year
    is_accelerating: bool
    acceleration: float  # second derivative (units per year^2)
    r_squared: float
    explanation: str


def _linear_fit(years: np.ndarray, values: np.ndarray) -> tuple[float, float, float]:
    """Returns (slope, intercept, r_squared) for a 1D linear regression."""
    if len(years) < 2:
        return 0.0, float(values[0]) if len(values) else 0.0, 0.0
    coeffs = np.polyfit(years, values, 1)
    slope, intercept = coeffs[0], coeffs[1]
    predicted = slope * years + intercept
    ss_res = float(np.sum((values - predicted) ** 2))
    ss_tot = float(np.sum((values - np.mean(values)) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return float(slope), float(intercept), r_squared


def analyze_trend(years: list[float], values: list[float], *, stable_threshold_pct: float = 0.5) -> TrendResult:
    """
    Determine direction, rate, and acceleration of a time series.

    stable_threshold_pct: annual rate below this % of the first value counts
    as STABLE rather than increasing/decreasing (avoids over-reporting noise
    as a "trend").
    """
    if len(years) != len(values) or len(years) == 0:
        raise ValueError("years and values must be same non-zero length")

    years_arr = np.array(years, dtype=float)
    values_arr = np.array(values, dtype=float)

    slope, _, r_squared = _linear_fit(years_arr, values_arr)
    baseline = values_arr[0] if values_arr[0] != 0 else (np.mean(values_arr) or 1.0)
    annual_rate_pct = (slope / baseline) * 100 if baseline else 0.0

    if abs(annual_rate_pct) < stable_threshold_pct:
        direction = Direction.STABLE
    elif slope > 0:
        direction = Direction.INCREASING
    else:
        direction = Direction.DECREASING

    # Acceleration: split series into two halves, compare slopes.
    acceleration = 0.0
    is_accelerating = False
    if len(years_arr) >= 4:
        mid = len(years_arr) // 2
        slope_first, _, _ = _linear_fit(years_arr[: mid + 1], values_arr[: mid + 1])
        slope_second, _, _ = _linear_fit(years_arr[mid:], values_arr[mid:])
        acceleration = slope_second - slope_first
        # "Accelerating" means the harmful/decreasing trend is speeding up,
        # i.e. the magnitude of slope is growing in the same direction.
        is_accelerating = bool(
            abs(slope_second) > abs(slope_first) and np.sign(slope_second or 1) == np.sign(slope_first or 1)
        )

    explanation = _explain(direction, annual_rate_pct, is_accelerating)

    return TrendResult(
        direction=direction,
        annual_rate=round(slope, 4),
        annual_rate_pct=round(annual_rate_pct, 3),
        is_accelerating=is_accelerating,
        acceleration=round(acceleration, 4),
        r_squared=round(r_squared, 3),
        explanation=explanation,
    )


def _explain(direction: Direction, rate_pct: float, accelerating: bool) -> str:
    if direction == Direction.STABLE:
        return "Values have remained broadly stable over the observed period."
    verb = "declined" if direction == Direction.DECREASING else "increased"
    accel_clause = " and the rate of change is accelerating" if accelerating else ""
    return f"Values have {verb} by approximately {abs(rate_pct):.1f}% per year{accel_clause}."
