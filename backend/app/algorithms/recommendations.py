"""
Rule-based recommendation engine: detected problem -> ranked interventions.

Deliberately not an LLM — recommendations must be deterministic and
traceable to the triggering condition (spec RULE_6: "Recommendations must be
explainable"). An optional LLM layer (providers/llm) may phrase these in
prose, but never invents the list itself.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Recommendation:
    problem: str
    interventions: list[str]
    severity: str  # WARNING | CRITICAL | SEVERE
    rationale: str


def recommend_for_water_stress(extraction_ratio: float) -> Recommendation | None:
    if extraction_ratio < 1.0:
        return None
    severity = "SEVERE" if extraction_ratio >= 1.3 else "CRITICAL"
    return Recommendation(
        problem="Groundwater/water extraction exceeds the sustainable recharge limit.",
        interventions=[
            "Reduce extraction toward the sustainable limit",
            "Increase recharge capacity (check dams, rainwater harvesting)",
            "Promote water-efficient agriculture (drip irrigation, crop shift)",
            "Redirect new industrial water demand to lower-stress zones",
            "Restrict new high-consumption facilities in this basin",
        ],
        severity=severity,
        rationale=f"Extraction is at {extraction_ratio * 100:.0f}% of the sustainable limit.",
    )


def recommend_for_route_forest_intersection(forest_overlap_km: float) -> Recommendation | None:
    if forest_overlap_km <= 0:
        return None
    severity = "SEVERE" if forest_overlap_km > 5 else "CRITICAL" if forest_overlap_km > 1 else "WARNING"
    return Recommendation(
        problem=f"Proposed infrastructure route intersects {forest_overlap_km:.1f} km of sensitive forest.",
        interventions=[
            "Redirect the route around the core forest zone",
            "Create a dedicated wildlife crossing/underpass",
            "Establish a buffer zone along the corridor edge",
            "Reduce corridor width where a full realignment is not feasible",
            "Select an alternative candidate route with lower forest overlap",
        ],
        severity=severity,
        rationale=f"{forest_overlap_km:.1f} km of the route passes through classified sensitive forest.",
    )


def recommend_for_industrial_population_proximity(population_proximity: float, distance_km: float) -> Recommendation | None:
    if population_proximity < 60:
        return None
    severity = "SEVERE" if population_proximity >= 85 else "CRITICAL"
    return Recommendation(
        problem=f"Proposed industrial site is only {distance_km:.1f} km from a dense population center.",
        interventions=[
            "Evaluate an alternative industrial zone farther from settlements",
            "Increase the buffer distance between the site and residential areas",
            "Restrict the scale/category of permitted expansion",
            "Require improved pollution controls (emissions/effluent limits) before approval",
        ],
        severity=severity,
        rationale=f"Population-proximity pressure score is {population_proximity:.0f}/100.",
    )


def recommend_for_forest_decline(annual_rate_pct: float, threshold_year: int | None) -> Recommendation | None:
    if annual_rate_pct >= 0:
        return None
    severity = "SEVERE" if abs(annual_rate_pct) > 3 else "CRITICAL" if abs(annual_rate_pct) > 1 else "WARNING"
    rationale = f"Forest cover is declining at {abs(annual_rate_pct):.1f}% per year."
    if threshold_year:
        rationale += f" At this rate, the region may cross a critical ecological threshold by {threshold_year}."
    return Recommendation(
        problem="Forest cover is declining.",
        interventions=[
            "Restrict new development in the sensitive/core zone",
            "Establish or expand buffer zones around the remaining forest",
            "Redirect planned infrastructure away from the forest boundary",
            "Fund active restoration of degraded/fragmented patches",
            "Strengthen enforcement against encroachment",
        ],
        severity=severity,
        rationale=rationale,
    )


def collect_recommendations(**signals) -> list[Recommendation]:
    """Convenience aggregator — pass whichever signals are available; None-returning checks are skipped."""
    candidates = [
        recommend_for_water_stress(signals["extraction_ratio"]) if "extraction_ratio" in signals else None,
        recommend_for_route_forest_intersection(signals["forest_overlap_km"]) if "forest_overlap_km" in signals else None,
        recommend_for_industrial_population_proximity(
            signals["population_proximity"], signals.get("distance_km", 0.0)
        )
        if "population_proximity" in signals
        else None,
        recommend_for_forest_decline(signals["annual_rate_pct"], signals.get("threshold_year"))
        if "annual_rate_pct" in signals
        else None,
    ]
    return [c for c in candidates if c is not None]
