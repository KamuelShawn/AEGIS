"""Test/utility endpoints for the Google Maps Platform supplemental providers."""
from fastapi import APIRouter

from app.providers.base import resolve
from app.providers.registry import registry

router = APIRouter(prefix="/api/google-maps", tags=["google-maps"])

_REGION_COORDS = {
    "bandipur": (11.6667, 76.6333),
    "ka-chamarajanagar": (11.9261, 77.1197),
    "ka-mysuru": (12.2958, 76.6394),
    "ka": (15.3173, 75.7139),
    "kabini-basin": (11.95, 76.35),
}


@router.get("/geocode")
def geocode(query: str):
    pair = registry.get("google_maps_geocoding")
    result, connection_status = resolve(
        live=pair.live, mock=pair.mock, cache=registry.cache,
        cache_key=f"google_geocode:{query}", params={"query": query},
    )
    return {
        "query": query,
        "results": result.data.get("results", []),
        "source": {
            "status": result.source_status.value,
            "name": result.source_name,
            "retrieved_at": result.retrieved_at,
            "connection": connection_status.value,
        },
    }


@router.get("/elevation")
def elevation(region_id: str = "bandipur"):
    lat, lon = _REGION_COORDS.get(region_id, (15.3173, 75.7139))
    pair = registry.get("elevation")
    result, connection_status = resolve(
        live=pair.live, mock=pair.mock, cache=registry.cache,
        cache_key=f"elevation:{region_id}", params={"lat": lat, "lon": lon, "region_id": region_id},
    )
    return {
        "region_id": region_id,
        "data": result.data,
        "source": {
            "status": result.source_status.value,
            "name": result.source_name,
            "retrieved_at": result.retrieved_at,
            "connection": connection_status.value,
        },
    }
