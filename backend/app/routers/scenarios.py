from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.region_intelligence import InsufficientRegionDataError, simulate_scenario

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


class ScenarioRequest(BaseModel):
    region_id: str = "bandipur"
    industrial_growth_pct: float = Field(0.0, ge=-100, le=200)
    population_growth_pct: float = Field(0.0, ge=-100, le=200)
    water_consumption_pct: float = Field(0.0, ge=-100, le=200)
    forest_protection_pct: float = Field(0.0, ge=-100, le=100)
    infrastructure_expansion_pct: float = Field(0.0, ge=-100, le=200)


@router.post("/simulate")
def simulate(request: ScenarioRequest):
    try:
        result = simulate_scenario(
            request.region_id,
            industrial_growth_pct=request.industrial_growth_pct,
            population_growth_pct=request.population_growth_pct,
            water_consumption_pct=request.water_consumption_pct,
            forest_protection_pct=request.forest_protection_pct,
            infrastructure_expansion_pct=request.infrastructure_expansion_pct,
        )
    except InsufficientRegionDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "region_id": result.region_id,
        "baseline_sustainability": result.baseline_sustainability,
        "projected_sustainability": result.projected_sustainability,
        "baseline_risk": result.baseline_risk,
        "projected_risk": result.projected_risk,
        "risk_level": result.risk_level,
        "factors": result.factors,
        "explanation": result.explanation,
        "source_status": "MODELLED",
    }
