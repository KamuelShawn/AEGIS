"""
Forecasting: project a time series forward with an explicit confidence range.

Rule from the spec: never present a forecast as a single certain number.
Always return (low, mid, high) plus a confidence label and the method used.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.algorithms.trend import _linear_fit


@dataclass
class ForecastPoint:
    year: int
    low: float
    mid: float
    high: float


@dataclass
class ForecastResult:
    method: str
    points: list[ForecastPoint]
    confidence: str  # HIGH | MEDIUM | LOW
    r_squared: float
    explanation: str


def forecast_linear(
    years: list[float],
    values: list[float],
    target_years: list[int],
    *,
    min_value: float | None = None,
    max_value: float | None = None,
) -> ForecastResult:
    """
    Linear-regression forecast with a widening uncertainty band based on
    residual standard error and how far the target year is from observed data.
    """
    if len(years) < 2:
        raise ValueError("Need at least 2 observations to forecast")

    years_arr = np.array(years, dtype=float)
    values_arr = np.array(values, dtype=float)
    slope, intercept, r_squared = _linear_fit(years_arr, values_arr)

    predicted = slope * years_arr + intercept
    residual_std = float(np.std(values_arr - predicted)) if len(values_arr) > 2 else abs(values_arr[-1]) * 0.05
    # A perfectly linear fit has zero residual error, but a forecast should
    # never claim zero uncertainty — floor it to a small fraction of scale.
    residual_std = max(residual_std, abs(float(np.mean(values_arr))) * 0.02, 0.01)
    last_year = years_arr[-1]

    points: list[ForecastPoint] = []
    for ty in target_years:
        mid = slope * ty + intercept
        years_ahead = max(ty - last_year, 1)
        # Uncertainty grows with distance from observed data.
        band = residual_std * (1 + 0.15 * years_ahead)
        low, high = mid - band, mid + band
        if min_value is not None:
            low = max(low, min_value)
            mid = max(mid, min_value)
        if max_value is not None:
            high = min(high, max_value)
            mid = min(mid, max_value)
        points.append(ForecastPoint(year=int(ty), low=round(low, 2), mid=round(mid, 2), high=round(high, 2)))

    if r_squared > 0.8:
        confidence = "HIGH"
    elif r_squared > 0.5:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    explanation = (
        f"Linear trend fit to {len(years)} observations (R²={r_squared:.2f}). "
        f"Projection uncertainty widens for years further from the last observed data point."
    )

    return ForecastResult(
        method="linear_regression",
        points=points,
        confidence=confidence,
        r_squared=round(r_squared, 3),
        explanation=explanation,
    )


def forecast_exponential_smoothing(values: list[float], periods_ahead: int, *, alpha: float = 0.4) -> ForecastResult:
    """Simple exponential smoothing — useful for noisy series without a clear linear trend."""
    if len(values) < 2:
        raise ValueError("Need at least 2 observations")

    smoothed = [values[0]]
    for v in values[1:]:
        smoothed.append(alpha * v + (1 - alpha) * smoothed[-1])

    last = smoothed[-1]
    residuals = np.array(values) - np.array(smoothed)
    residual_std = float(np.std(residuals)) if len(residuals) > 1 else abs(last) * 0.05

    points = []
    for i in range(1, periods_ahead + 1):
        band = residual_std * (1 + 0.2 * i)
        points.append(ForecastPoint(year=i, low=round(last - band, 2), mid=round(last, 2), high=round(last + band, 2)))

    return ForecastResult(
        method="exponential_smoothing",
        points=points,
        confidence="MEDIUM",
        r_squared=0.0,
        explanation=f"Exponential smoothing (alpha={alpha}) projects the level forward; no strong trend assumed.",
    )
