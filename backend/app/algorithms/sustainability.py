"""
Overall sustainability score: weighted composite of environment, resources,
infrastructure efficiency, social impact, and pollution/future risk — the
central animated score in the UI (0-100, higher = more sustainable).

Note the sign convention differs from risk.py: here higher is better.
"""
from __future__ import annotations

from dataclasses import dataclass

# Documented weights (spec: "do not arbitrarily choose weights without
# documenting them"). Sum to 1.0.
DEFAULT_WEIGHTS = {
    "environment": 0.30,
    "resources": 0.25,
    "infrastructure": 0.15,
    "social": 0.15,
    "pollution": 0.15,
}


@dataclass
class ScoreFactor:
    name: str
    score: float  # 0-100, higher = healthier
    weight: float
    contribution: float


@dataclass
class SustainabilityScore:
    overall: float
    factors: list[ScoreFactor]
    weakest_factor: str
    explanation: str


def calculate_sustainability_score(
    *,
    environment: float,
    resources: float,
    infrastructure: float,
    social: float,
    pollution: float,
    weights: dict[str, float] | None = None,
) -> SustainabilityScore:
    w = weights or DEFAULT_WEIGHTS
    inputs = {
        "environment": environment,
        "resources": resources,
        "infrastructure": infrastructure,
        "social": social,
        "pollution": pollution,
    }

    factors: list[ScoreFactor] = []
    overall = 0.0
    for name, value in inputs.items():
        value = max(0.0, min(100.0, value))
        weight = w.get(name, 0.0)
        contribution = value * weight
        overall += contribution
        factors.append(ScoreFactor(name=name, score=round(value, 1), weight=weight, contribution=round(contribution, 2)))

    factors_sorted = sorted(factors, key=lambda f: f.score)
    weakest = factors_sorted[0].name

    # How many points the weakest factor "cost" vs. if it were perfect (100).
    weakest_factor_obj = next(f for f in factors if f.name == weakest)
    points_lost = round((100 - weakest_factor_obj.score) * weakest_factor_obj.weight, 1)

    explanation = (
        f"Overall sustainability is {overall:.0f}/100. "
        f"{weakest.capitalize()} is the weakest dimension ({weakest_factor_obj.score:.0f}/100), "
        f"reducing the overall score by approximately {points_lost:.0f} points."
    )

    return SustainabilityScore(
        overall=round(overall, 1),
        factors=factors,
        weakest_factor=weakest,
        explanation=explanation,
    )
