"""
Industrial/infrastructure site suitability: weighted spatial criteria scoring.
"""
from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_SITE_WEIGHTS = {
    "water_availability": 0.20,
    "infrastructure_access": 0.20,
    "population_proximity": 0.15,   # higher input = closer to dense population = worse
    "environmental_sensitivity": 0.25,  # higher input = more sensitive = worse
    "pollution_risk": 0.10,
    "land_suitability": 0.10,
}


@dataclass
class SiteCandidate:
    id: str
    name: str
    water_availability: float  # 0-100, higher = better
    infrastructure_access: float  # 0-100, higher = better
    population_proximity: float  # 0-100, higher = closer/worse
    environmental_sensitivity: float  # 0-100, higher = more sensitive/worse
    pollution_risk: float  # 0-100, higher = worse
    land_suitability: float  # 0-100, higher = better


@dataclass
class ScoredSite:
    candidate: SiteCandidate
    suitability_score: float  # 0-100, higher = better site
    classification: str  # SUSTAINABLE | POTENTIALLY_SUSTAINABLE | UNSUSTAINABLE
    rank: int
    explanation: str


def _classify(score: float) -> str:
    if score >= 65:
        return "SUSTAINABLE"
    if score >= 40:
        return "POTENTIALLY_SUSTAINABLE_WITH_RESTRICTIONS"
    return "UNSUSTAINABLE"


def score_sites(candidates: list[SiteCandidate], weights: dict[str, float] | None = None) -> list[ScoredSite]:
    w = weights or DEFAULT_SITE_WEIGHTS
    total_weight = sum(w.values()) or 1.0

    scored: list[ScoredSite] = []
    for c in candidates:
        # Convert every dimension to a 0-100 "goodness" score before weighting.
        goodness = {
            "water_availability": c.water_availability,
            "infrastructure_access": c.infrastructure_access,
            "population_proximity": 100 - c.population_proximity,
            "environmental_sensitivity": 100 - c.environmental_sensitivity,
            "pollution_risk": 100 - c.pollution_risk,
            "land_suitability": c.land_suitability,
        }
        score = sum(goodness[k] * w.get(k, 0.0) for k in goodness) / total_weight
        scored.append(
            ScoredSite(
                candidate=c,
                suitability_score=round(score, 1),
                classification=_classify(score),
                rank=0,
                explanation="",
            )
        )

    scored.sort(key=lambda s: s.suitability_score, reverse=True)
    for i, s in enumerate(scored, start=1):
        s.rank = i
        c = s.candidate
        weakest = min(
            ["water_availability", "infrastructure_access", "environmental_sensitivity"],
            key=lambda k: getattr(c, k) if k != "environmental_sensitivity" else 100 - getattr(c, k),
        )
        s.explanation = (
            f"{c.name} scores {s.suitability_score:.0f}/100 ({s.classification.replace('_', ' ').title()}). "
            f"Weakest dimension: {weakest.replace('_', ' ')}."
        )

    return scored
