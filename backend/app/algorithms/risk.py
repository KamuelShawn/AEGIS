"""
Risk scoring: combine environmental degradation, resource pressure,
population/development pressure, and pollution into one interpretable,
explainable risk score with a categorical state.

RULE_1..4 map to the PDF's four states: SAFE / WARNING / CRITICAL / SEVERE.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    SEVERE = "SEVERE"


# Documented, fixed weights (spec requires weights not be arbitrary/undocumented).
DEFAULT_WEIGHTS = {
    "environmental_degradation": 0.30,
    "resource_pressure": 0.25,
    "development_pressure": 0.20,
    "pollution": 0.15,
    "population_pressure": 0.10,
}


@dataclass
class RiskFactor:
    name: str
    value: float  # 0-100, higher = worse
    weight: float
    contribution: float  # weight * value, i.e. points out of 100


@dataclass
class RiskResult:
    score: float  # 0-100, higher = worse
    level: RiskLevel
    factors: list[RiskFactor]
    top_driver: str
    explanation: str


def _level_for_score(score: float) -> RiskLevel:
    if score < 30:
        return RiskLevel.SAFE
    if score < 55:
        return RiskLevel.WARNING
    if score < 80:
        return RiskLevel.CRITICAL
    return RiskLevel.SEVERE


def calculate_risk(
    *,
    environmental_degradation: float,
    resource_pressure: float,
    development_pressure: float,
    pollution: float,
    population_pressure: float,
    weights: dict[str, float] | None = None,
) -> RiskResult:
    """
    Every input is a 0-100 "badness" score (0 = no pressure, 100 = maximum
    observed pressure). Returns a weighted composite with per-factor
    contributions so the UI can show exactly why the score is what it is.
    """
    w = weights or DEFAULT_WEIGHTS
    inputs = {
        "environmental_degradation": environmental_degradation,
        "resource_pressure": resource_pressure,
        "development_pressure": development_pressure,
        "pollution": pollution,
        "population_pressure": population_pressure,
    }

    factors: list[RiskFactor] = []
    total = 0.0
    for name, value in inputs.items():
        value = max(0.0, min(100.0, value))
        weight = w.get(name, 0.0)
        contribution = value * weight
        total += contribution
        factors.append(RiskFactor(name=name, value=round(value, 1), weight=weight, contribution=round(contribution, 2)))

    factors.sort(key=lambda f: f.contribution, reverse=True)
    top_driver = factors[0].name if factors else "unknown"
    level = _level_for_score(total)

    explanation = (
        f"Composite risk is {total:.0f}/100 ({level.value}). "
        f"The largest contributor is {top_driver.replace('_', ' ')} "
        f"({factors[0].contribution:.0f} of {total:.0f} points)."
    )

    return RiskResult(score=round(total, 1), level=level, factors=factors, top_driver=top_driver, explanation=explanation)


def project_threshold_year(
    current_value: float,
    annual_rate: float,
    threshold: float,
    current_year: int,
    *,
    max_years_ahead: int = 100,
) -> int | None:
    """
    Given a linear rate of change, project the year a value crosses a critical
    threshold. Returns None if the trend never reaches it within the horizon.
    Used for "the region may cross the critical threshold by YEAR" warnings.
    """
    if annual_rate == 0:
        return None
    years_to_threshold = (threshold - current_value) / annual_rate
    if years_to_threshold < 0 or years_to_threshold > max_years_ahead:
        return None
    return current_year + int(round(years_to_threshold))
