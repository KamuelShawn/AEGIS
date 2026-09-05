from fastapi import APIRouter, HTTPException

from app.algorithms.forecasting import forecast_linear
from app.algorithms.risk import project_threshold_year
from app.algorithms.trend import analyze_trend
from app.providers.base import resolve
from app.providers.registry import registry
from app.routers.regions import get_region_coords
from app.services.ndvi_pipeline import NDVIPipelineError, compute_ndvi_vegetation_area

router = APIRouter(prefix="/api/environment", tags=["environment"])

# The only regions with a real (simulated-but-labelled) multi-year forest
# history series — see app/data/demo/forest_history.json. Any other region
# does NOT get Bandipur's numbers substituted for it (that was a real bug,
# fixed here) — it gets an honest "not available" pointing at the live NDVI
# snapshot endpoint instead.
_FOREST_HISTORY_REGIONS = ("bandipur", "ka-chamarajanagar")


@router.get("/forest-history")
def forest_history(region_id: str = "bandipur", forecast_years: int = 15):
    if region_id not in _FOREST_HISTORY_REGIONS:
        coords = get_region_coords(region_id)
        detail = f"No historical forest-cover series available for region '{region_id}' yet."
        if coords:
            lat, lon = coords
            detail += (
                f" A live current-vegetation snapshot is available instead: "
                f"/api/environment/ndvi?lat={lat}&lon={lon}"
            )
        raise HTTPException(status_code=404, detail=detail)

    pair = registry.get("environment")
    result, connection_status = resolve(
        live=pair.live, mock=pair.mock, cache=registry.cache,
        cache_key=f"forest_history:{region_id}", params={"region_id": region_id},
    )
    series = result.data
    observations = series.get("observations", [])
    if not observations:
        raise HTTPException(status_code=404, detail=f"No forest-cover series for region '{region_id}'")

    years = [o["year"] for o in observations]
    values = [o["area"] for o in observations]
    trend = analyze_trend(years, values)

    threshold = series.get("critical_threshold_area")
    threshold_year = None
    if threshold is not None:
        threshold_year = project_threshold_year(values[-1], trend.annual_rate, threshold, years[-1])

    target_year = years[-1] + forecast_years
    forecast = forecast_linear(years, values, target_years=[target_year], min_value=0)

    return {
        "region_id": region_id,
        "unit": series.get("unit", "km2"),
        "observations": observations,
        "trend": {
            "direction": trend.direction.value,
            "annual_rate": trend.annual_rate,
            "annual_rate_pct": trend.annual_rate_pct,
            "is_accelerating": trend.is_accelerating,
            "explanation": trend.explanation,
        },
        "critical_threshold_area": threshold,
        "projected_threshold_year": threshold_year,
        "forecast": [p.__dict__ for p in forecast.points],
        "forecast_confidence": forecast.confidence,
        "causes": series.get("causes", []),
        "source": {
            "status": result.source_status.value,
            "name": result.source_name,
            "retrieved_at": result.retrieved_at,
            "connection": connection_status.value,
        },
    }


@router.get("/weather")
def weather(region_id: str = "kabini-basin"):
    coords = get_region_coords(region_id)
    if coords is None:
        raise HTTPException(status_code=404, detail=f"Unknown region '{region_id}' — cannot resolve coordinates")
    lat, lon = coords
    pair = registry.get("weather")
    result, connection_status = resolve(
        live=pair.live, mock=pair.mock, cache=registry.cache,
        cache_key=f"weather:{region_id}", params={"lat": lat, "lon": lon, "region_id": region_id},
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


@router.get("/air-quality")
def air_quality(region_id: str = "ka-mysuru"):
    pair = registry.get("air_quality")
    result, connection_status = resolve(
        live=pair.live, mock=pair.mock, cache=registry.cache,
        cache_key=f"air_quality:{region_id}", params={"region_id": region_id},
    )
    data = result.data
    history = data.get("aqi_history", [])
    trend = None
    if len(history) >= 2:
        t = analyze_trend([h["year"] for h in history], [h["aqi"] for h in history])
        trend = {"direction": t.direction.value, "annual_rate_pct": t.annual_rate_pct, "explanation": t.explanation}
    return {
        "region_id": region_id,
        "aqi_history": history,
        "pollutants_current": data.get("pollutants_current", {}),
        "trend": trend,
        "source": {
            "status": result.source_status.value,
            "name": result.source_name,
            "retrieved_at": result.retrieved_at,
            "connection": connection_status.value,
        },
    }


@router.get("/ndvi")
def ndvi(
    region_id: str = "custom",
    lat: float | None = None,
    lon: float | None = None,
    date_from: str = "2026-01-01",
    date_to: str = "2026-03-01",
    threshold: float = 0.4,
):
    """
    Real, live NDVI computation over Sentinel-2 imagery via Copernicus openEO.
    Works for ANY location in India — pass lat/lon for an arbitrary point, or
    region_id="bandipur" for the hand-picked demo box. Takes 30-90 seconds
    (synchronous satellite processing) — this is not a cached/instant
    endpoint. See services/ndvi_pipeline.py for the full honesty notes on
    what this number does and doesn't represent.
    """
    if lat is None and lon is None and region_id == "custom":
        raise HTTPException(status_code=400, detail="Provide either lat & lon, or a region_id (e.g. 'bandipur')")
    try:
        result = compute_ndvi_vegetation_area(
            region_id, date_from=date_from, date_to=date_to, lat=lat, lon=lon, threshold=threshold
        )
    except NDVIPipelineError as exc:
        raise HTTPException(status_code=503, detail=f"NDVI computation unavailable: {exc}") from exc

    return {
        "region_id": result.region_id,
        "bbox": result.bbox,
        "date_from": result.date_from,
        "date_to": result.date_to,
        "ndvi_threshold": result.threshold,
        "pixel_size_m": result.pixel_size_m,
        "total_valid_area_km2": result.total_valid_area_km2,
        "vegetation_area_km2": result.vegetation_area_km2,
        "vegetation_fraction": result.vegetation_fraction,
        "ndvi_mean": result.ndvi_mean,
        "ndvi_min": result.ndvi_min,
        "ndvi_max": result.ndvi_max,
        "max_cloud_cover_pct": result.max_cloud_cover,
        "source": {
            "status": "DERIVED",
            "name": "Copernicus Sentinel-2 L2A via openEO (real-time NDVI computation)",
            "notes": (
                "Vegetation area is computed within a fixed bounding box, not a true "
                "administrative/ecological boundary polygon — see docs/ARCHITECTURE.md."
            ),
        },
    }
