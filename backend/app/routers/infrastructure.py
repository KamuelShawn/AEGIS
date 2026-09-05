from fastapi import APIRouter, HTTPException

from app.algorithms.route_optimization import RouteCandidate, score_routes
from app.data import load_demo
from app.providers.base import resolve
from app.providers.registry import registry

router = APIRouter(prefix="/api/infrastructure", tags=["infrastructure"])


@router.get("/routes")
def get_routes(
    scenario_id: str = "bandipur-corridor",
    economic_cost: float = 25,
    environmental_impact: float = 30,
    social_impact: float = 25,
    connectivity_benefit: float = 20,
):
    data = load_demo("routes")
    scenario = data.get("scenarios", {}).get(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"Unknown route scenario '{scenario_id}'")

    candidates = [RouteCandidate(**c) for c in scenario["candidates"]]
    weights = {
        "economic_cost": economic_cost,
        "environmental_impact": environmental_impact,
        "social_impact": social_impact,
        "connectivity_benefit": connectivity_benefit,
    }
    scored = score_routes(candidates, weights=weights)

    return {
        "scenario_id": scenario_id,
        "origin": scenario["origin"],
        "destination": scenario["destination"],
        "weights": weights,
        "routes": [
            {
                "id": s.candidate.id,
                "name": s.candidate.name,
                "distance_km": s.candidate.distance_km,
                "construction_cost_cr": s.candidate.construction_cost_cr,
                "environmental_impact": s.candidate.environmental_impact,
                "social_impact": s.candidate.social_impact,
                "connectivity_benefit": s.candidate.connectivity_benefit,
                "terrain_difficulty": s.candidate.terrain_difficulty,
                "affected_ecosystems": s.candidate.affected_ecosystems,
                "affected_villages": s.candidate.affected_villages,
                "weighted_score": s.weighted_score,
                "rank": s.rank,
                "explanation": s.explanation,
            }
            for s in scored
        ],
        "recommended_route_id": scored[0].candidate.id if scored else None,
        "source": {"status": data["source_status"], "notes": data["notes"]},
    }


@router.get("/features")
def get_features(bbox: str = "11.5,76.4,11.9,76.9"):
    pair = registry.get("infrastructure")
    result, connection_status = resolve(
        live=pair.live, mock=pair.mock, cache=registry.cache,
        cache_key=f"osm_features:{bbox}", params={"bbox": bbox},
    )
    return {
        "features": result.data.get("features", []),
        "source": {
            "status": result.source_status.value,
            "name": result.source_name,
            "retrieved_at": result.retrieved_at,
            "connection": connection_status.value,
        },
    }
