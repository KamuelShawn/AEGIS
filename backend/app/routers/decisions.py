from fastapi import APIRouter, HTTPException

from app.services.region_intelligence import InsufficientRegionDataError, compute_region_intelligence

router = APIRouter(prefix="/api", tags=["decisions"])


def _serialize(intel):
    return {
        "region_id": intel.region_id,
        "risk": {
            "score": intel.risk.score,
            "level": intel.risk.level.value,
            "explanation": intel.risk.explanation,
            "factors": [f.__dict__ for f in intel.risk.factors],
            "projected_threshold_year": intel.threshold_year,
        },
        "sustainability": {
            "overall": intel.sustainability.overall,
            "weakest_factor": intel.sustainability.weakest_factor,
            "explanation": intel.sustainability.explanation,
            "factors": [f.__dict__ for f in intel.sustainability.factors],
        },
        "recommendations": [
            {
                "problem": r.problem,
                "interventions": r.interventions,
                "severity": r.severity,
                "rationale": r.rationale,
            }
            for r in intel.recommendations
        ],
        "narrative": {
            "forest": intel.forest_trend_explanation,
            "water": intel.water_status_explanation,
        },
        "sources": intel.sources,
    }


def _compute_or_404(region_id: str):
    try:
        return compute_region_intelligence(region_id)
    except InsufficientRegionDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/regions/{region_id}/risk")
def region_risk(region_id: str):
    intel = _compute_or_404(region_id)
    return _serialize(intel)["risk"] | {"region_id": region_id}


@router.get("/regions/{region_id}/sustainability")
def region_sustainability(region_id: str):
    intel = _compute_or_404(region_id)
    return _serialize(intel)


@router.get("/decisions/recommendations")
def decision_recommendations(region_id: str = "bandipur"):
    intel = _compute_or_404(region_id)
    return {"region_id": region_id, "recommendations": _serialize(intel)["recommendations"]}
