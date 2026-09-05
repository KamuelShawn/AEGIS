"""
Google Maps Platform — Elevation API.

Gives a real point-elevation number in meters, which is simpler to consume
than OpenTopography's bbox DEM-raster endpoint (that one returns a GeoTIFF
and needs a rasterio pipeline to turn into numbers — not yet built). This is
the elevation input route-optimization's terrain-difficulty factor should
eventually read from, once wired into that algorithm.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

ELEVATION_URL = "https://maps.googleapis.com/maps/api/elevation/json"


class LiveGoogleElevationProvider(DataProvider):
    name = "google_elevation"

    def is_configured(self) -> bool:
        return bool(settings.GOOGLE_MAPS_API_KEY)

    def fetch(self, *, lat: float, lon: float, **_params) -> dict:
        try:
            resp = httpx.get(
                ELEVATION_URL,
                params={"locations": f"{lat},{lon}", "key": settings.GOOGLE_MAPS_API_KEY},
                timeout=8.0,
            )
        except httpx.RequestError as exc:
            raise ProviderError(f"Google Elevation network error: {exc}") from exc
        if resp.status_code != 200:
            raise ProviderError(f"Google Elevation returned {resp.status_code}")
        data = resp.json()
        status = data.get("status")
        if status == "REQUEST_DENIED":
            raise ProviderError("Google Maps API key rejected (Elevation API not enabled, or key restricted)")
        if status == "OVER_QUERY_LIMIT":
            raise ProviderError("Google Elevation rate limited")
        if status != "OK":
            raise ProviderError(f"Google Elevation status: {status}")
        return data

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and raw.get("status") == "OK" and bool(raw.get("results"))

    def normalize(self, raw: dict, *, lat: float = 0.0, lon: float = 0.0, **_params) -> NormalizedResult:
        result = raw["results"][0]
        return NormalizedResult(
            data={"elevation_m": result["elevation"], "lat": lat, "lon": lon, "resolution_m": result.get("resolution")},
            source_status=SourceStatus.REAL,
            source_name="Google Maps Elevation API",
            retrieved_at=now_iso(),
            confidence="HIGH",
        )
