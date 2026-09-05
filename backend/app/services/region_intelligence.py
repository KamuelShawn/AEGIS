"""
Central Intelligence Engine (PDF section 20): connects Environment -> Resources
-> Infrastructure -> Industry -> Population -> Decision for a given region.

This is the only place that combines multiple providers' outputs into a single
risk score, sustainability score, and recommendation set. Individual routers
(environment.py, resources.py, ...) still expose each domain independently.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.algorithms.recommendations import Recommendation, collect_recommendations
from app.algorithms.resource import calculate_resource_balance
from app.algorithms.risk import RiskResult, calculate_risk, project_threshold_year
from app.algorithms.sustainability import SustainabilityScore, calculate_sustainability_score
from app.algorithms.trend import analyze_trend
from app.providers.base import resolve
from app.providers.registry import registry

# Legacy demo region -> underlying dataset id mapping. These are the ONLY
# regions with the curated multi-source demo dataset (forest history, water
# balance, AQI, population) needed for a full composite score. This used to
# silently fall back to Bandipur's numbers for ANY unrecognized region_id —
# that was a real bug (fixed here): compute_region_intelligence() now raises
# InsufficientRegionDataError for anything not in this map, rather than
# mislabeling one place's data as another's. Full nationwide coverage needs
# the real datasets from docs/API_SETUP.md items 4-6 (water, forest, census).
REGION_DATA_MAP = {
    "bandipur": {"forest": "bandipur", "water": "kabini-basin", "air": "ka-mysuru", "population": "ka-chamarajanagar"},
    "ka-chamarajanagar": {"forest": "ka-chamarajanagar", "water": "ka-chamarajanagar", "air": "ka-mysuru", "population": "ka-chamarajanagar"},
    "kabini-basin": {"forest": "bandipur", "water": "kabini-basin", "air": "ka-mysuru", "population": "ka-chamarajanagar"},
    "ka-mysuru": {"forest": "ka-chamarajanagar", "water": "kabini-basin", "air": "ka-mysuru", "population": "ka-mysuru"},
}


class InsufficientRegionDataError(Exception):
    """Raised when a region has no curated demo dataset — no full composite score can be honestly computed yet."""

    def __init__(self, region_id: str):
        super().__init__(
            f"No full sustainability dataset available for region '{region_id}' yet. "
            f"Only these regions have the curated demo dataset needed for a composite score: "
            f"{', '.join(REGION_DATA_MAP)}. Weather (/api/environment/weather) and a live NDVI "
            f"vegetation snapshot (/api/environment/ndvi) work nationwide for any region."
        )
        self.region_id = region_id


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


@dataclass
class RegionIntelligence:
    region_id: str
    risk: RiskResult
    sustainability: SustainabilityScore
    recommendations: list[Recommendation]
    forest_trend_explanation: str
    water_status_explanation: str
    threshold_year: int | None
    sources: dict


def compute_region_intelligence(region_id: str) -> RegionIntelligence:
    ids = REGION_DATA_MAP.get(region_id)
    if ids is None:
        raise InsufficientRegionDataError(region_id)
    sources: dict[str, dict] = {}

    # --- Environment: forest trend -------------------------------------------------
    env_pair = registry.get("environment")
    forest_result, forest_conn = resolve(
        live=env_pair.live, mock=env_pair.mock, cache=registry.cache,
        cache_key=f"forest_history:{ids['forest']}", params={"region_id": ids["forest"]},
    )
    observations = forest_result.data.get("observations", [])
    years = [o["year"] for o in observations]
    values = [o["area"] for o in observations]
    forest_trend = analyze_trend(years, values)
    threshold = forest_result.data.get("critical_threshold_area")
    threshold_year = (
        project_threshold_year(values[-1], forest_trend.annual_rate, threshold, years[-1]) if threshold else None
    )
    environmental_degradation = _clamp(-forest_trend.annual_rate_pct * 20)
    sources["environment"] = {"status": forest_result.source_status.value, "name": forest_result.source_name}

    # --- Resources: water balance ---------------------------------------------------
    water_pair = registry.get("water")
    water_result, water_conn = resolve(
        live=water_pair.live, mock=water_pair.mock, cache=registry.cache,
        cache_key=f"water:{ids['water']}", params={"region_id": ids["water"]},
    )
    basin = water_result.data
    balance = calculate_resource_balance(
        available_reserve=basin.get("available_reserve_mcm", 0),
        annual_replenishment=basin.get("annual_replenishment_mcm", 0),
        current_extraction=basin.get("current_extraction_mcm", 0),
    )
    resource_pressure = _clamp(balance.extraction_ratio * 70)
    sources["resources"] = {"status": water_result.source_status.value, "name": water_result.source_name}

    # --- Pollution: air quality -------------------------------------------------------
    air_pair = registry.get("air_quality")
    air_result, air_conn = resolve(
        live=air_pair.live, mock=air_pair.mock, cache=registry.cache,
        cache_key=f"air_quality:{ids['air']}", params={"region_id": ids["air"]},
    )
    aqi_history = air_result.data.get("aqi_history", [])
    current_aqi = aqi_history[-1]["aqi"] if aqi_history else 60
    pollution = _clamp(current_aqi / 2)
    sources["pollution"] = {"status": air_result.source_status.value, "name": air_result.source_name}

    # --- Population pressure ----------------------------------------------------------
    pop_pair = registry.get("population")
    pop_result, pop_conn = resolve(
        live=pop_pair.live, mock=pop_pair.mock, cache=registry.cache,
        cache_key=f"population:{ids['population']}", params={"region_id": ids["population"]},
    )
    density = pop_result.data.get("density_per_km2", 150)
    population_pressure = _clamp(density / 5)
    sources["population"] = {"status": pop_result.source_status.value, "name": pop_result.source_name}

    # --- Development pressure (derived composite, no independent live source yet) -----
    development_pressure = _clamp(population_pressure * 0.5 + pollution * 0.5)

    risk = calculate_risk(
        environmental_degradation=environmental_degradation,
        resource_pressure=resource_pressure,
        development_pressure=development_pressure,
        pollution=pollution,
        population_pressure=population_pressure,
    )

    sustainability = calculate_sustainability_score(
        environment=100 - environmental_degradation,
        resources=100 - resource_pressure,
        infrastructure=70,  # static proxy until OSM-derived infra-access scoring is wired in
        social=100 - population_pressure,
        pollution=100 - pollution,
    )

    recommendations = collect_recommendations(
        extraction_ratio=balance.extraction_ratio,
        annual_rate_pct=forest_trend.annual_rate_pct,
        threshold_year=threshold_year,
    )

    return RegionIntelligence(
        region_id=region_id,
        risk=risk,
        sustainability=sustainability,
        recommendations=recommendations,
        forest_trend_explanation=forest_trend.explanation,
        water_status_explanation=balance.explanation,
        threshold_year=threshold_year,
        sources=sources,
    )


@dataclass
class ScenarioResult:
    region_id: str
    baseline_sustainability: float
    projected_sustainability: float
    baseline_risk: float
    projected_risk: float
    risk_level: str
    factors: dict
    explanation: str


def simulate_scenario(
    region_id: str,
    *,
    industrial_growth_pct: float = 0.0,
    population_growth_pct: float = 0.0,
    water_consumption_pct: float = 0.0,
    forest_protection_pct: float = 0.0,
    infrastructure_expansion_pct: float = 0.0,
) -> ScenarioResult:
    """
    Every *_pct slider is centered on 0 = "current trajectory continues
    unchanged". Positive values push the corresponding pressure up (except
    forest_protection_pct, which pushes environmental degradation down).
    All outputs here are MODELLED/DERIVED, never REAL — this is a projection.
    """
    baseline = compute_region_intelligence(region_id)

    base_factors = {f.name: f.value for f in baseline.risk.factors}

    environmental_degradation = _clamp(
        base_factors["environmental_degradation"] * (1 - forest_protection_pct / 100) * (1 + infrastructure_expansion_pct / 200)
    )
    resource_pressure = _clamp(base_factors["resource_pressure"] * (1 + water_consumption_pct / 100))
    population_pressure = _clamp(base_factors["population_pressure"] * (1 + population_growth_pct / 100))
    pollution = _clamp(base_factors["pollution"] * (1 + industrial_growth_pct / 150))
    development_pressure = _clamp(
        base_factors["development_pressure"] * (1 + (industrial_growth_pct + infrastructure_expansion_pct) / 200)
    )

    projected_risk = calculate_risk(
        environmental_degradation=environmental_degradation,
        resource_pressure=resource_pressure,
        development_pressure=development_pressure,
        pollution=pollution,
        population_pressure=population_pressure,
    )
    projected_sustainability = calculate_sustainability_score(
        environment=100 - environmental_degradation,
        resources=100 - resource_pressure,
        infrastructure=_clamp(70 + infrastructure_expansion_pct / 4),
        social=100 - population_pressure,
        pollution=100 - pollution,
    )

    delta = projected_sustainability.overall - baseline.sustainability.overall
    direction = "improves" if delta > 0.5 else "worsens" if delta < -0.5 else "leaves roughly unchanged"
    explanation = (
        f"Under this scenario, the sustainability score {direction} from "
        f"{baseline.sustainability.overall:.0f} to {projected_sustainability.overall:.0f}, "
        f"and risk moves from {baseline.risk.level.value} ({baseline.risk.score:.0f}) "
        f"to {projected_risk.level.value} ({projected_risk.score:.0f})."
    )

    return ScenarioResult(
        region_id=region_id,
        baseline_sustainability=baseline.sustainability.overall,
        projected_sustainability=projected_sustainability.overall,
        baseline_risk=baseline.risk.score,
        projected_risk=projected_risk.score,
        risk_level=projected_risk.level.value,
        factors={
            "environmental_degradation": environmental_degradation,
            "resource_pressure": resource_pressure,
            "development_pressure": development_pressure,
            "pollution": pollution,
            "population_pressure": population_pressure,
        },
        explanation=explanation,
    )
