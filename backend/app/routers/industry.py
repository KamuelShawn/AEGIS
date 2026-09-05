from fastapi import APIRouter, HTTPException

from app.algorithms.site_suitability import SiteCandidate, score_sites
from app.data import load_demo

router = APIRouter(prefix="/api/industry", tags=["industry"])


@router.get("/site-suitability")
def site_suitability(scenario_id: str = "chamarajanagar-industrial"):
    data = load_demo("sites")
    scenario = data.get("scenarios", {}).get(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"Unknown site scenario '{scenario_id}'")

    candidates = [SiteCandidate(**c) for c in scenario["candidates"]]
    scored = score_sites(candidates)

    return {
        "scenario_id": scenario_id,
        "sites": [
            {
                "id": s.candidate.id,
                "name": s.candidate.name,
                "water_availability": s.candidate.water_availability,
                "infrastructure_access": s.candidate.infrastructure_access,
                "population_proximity": s.candidate.population_proximity,
                "environmental_sensitivity": s.candidate.environmental_sensitivity,
                "pollution_risk": s.candidate.pollution_risk,
                "land_suitability": s.candidate.land_suitability,
                "suitability_score": s.suitability_score,
                "classification": s.classification,
                "rank": s.rank,
                "explanation": s.explanation,
            }
            for s in scored
        ],
        "recommended_site_id": scored[0].candidate.id if scored else None,
        "source": {"status": data["source_status"], "notes": data["notes"]},
    }
