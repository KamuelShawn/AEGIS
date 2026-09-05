"""
Google Maps Platform — supplemental geocoding + directions.

Mapbox (providers/geocoding/) is SUSTAINA's primary geocoder — this module is
the documented Google Maps fallback, kept as a separate, optional domain so
it's never a hard dependency (per the API spec: "Do not make Google Maps a
mandatory dependency if the core application can operate using Mapbox + OSM").

LiveGoogleDirectionsProvider is written but NOT wired into any router yet —
route candidates currently come from algorithms/route_optimization.py over a
static demo route set, not a live routing engine. It's here so that work is
a router + registry entry away instead of starting from scratch.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"


class LiveGoogleGeocodingProvider(DataProvider):
    name = "google_geocoding"

    def is_configured(self) -> bool:
        return bool(settings.GOOGLE_MAPS_API_KEY)

    def fetch(self, *, query: str, **_params) -> dict:
        try:
            resp = httpx.get(
                GEOCODE_URL,
                params={"address": query, "region": "in", "key": settings.GOOGLE_MAPS_API_KEY},
                timeout=8.0,
            )
        except httpx.RequestError as exc:
            raise ProviderError(f"Google Geocoding network error: {exc}") from exc
        if resp.status_code != 200:
            raise ProviderError(f"Google Geocoding returned {resp.status_code}")
        data = resp.json()
        status = data.get("status")
        if status == "REQUEST_DENIED":
            raise ProviderError("Google Maps API key rejected (Geocoding API not enabled, or key restricted)")
        if status == "OVER_QUERY_LIMIT":
            raise ProviderError("Google Geocoding rate limited")
        if status not in ("OK", "ZERO_RESULTS"):
            raise ProviderError(f"Google Geocoding status: {status}")
        return data

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "results" in raw

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        results = [
            {
                "name": r["formatted_address"],
                "lat": r["geometry"]["location"]["lat"],
                "lon": r["geometry"]["location"]["lng"],
            }
            for r in raw.get("results", [])
        ]
        return NormalizedResult(
            data={"results": results},
            source_status=SourceStatus.REAL,
            source_name="Google Maps Geocoding API",
            retrieved_at=now_iso(),
            confidence="HIGH",
        )


class LiveGoogleDirectionsProvider(DataProvider):
    """Not yet called from any router — see module docstring."""

    name = "google_directions"

    def is_configured(self) -> bool:
        return bool(settings.GOOGLE_MAPS_API_KEY)

    def fetch(self, *, origin: str, destination: str, **_params) -> dict:
        try:
            resp = httpx.get(
                DIRECTIONS_URL,
                params={"origin": origin, "destination": destination, "key": settings.GOOGLE_MAPS_API_KEY},
                timeout=10.0,
            )
        except httpx.RequestError as exc:
            raise ProviderError(f"Google Directions network error: {exc}") from exc
        if resp.status_code != 200:
            raise ProviderError(f"Google Directions returned {resp.status_code}")
        data = resp.json()
        status = data.get("status")
        if status == "REQUEST_DENIED":
            raise ProviderError("Google Maps API key rejected (Directions API not enabled, or key restricted)")
        if status not in ("OK", "ZERO_RESULTS"):
            raise ProviderError(f"Google Directions status: {status}")
        return data

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "routes" in raw

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        routes = []
        for r in raw.get("routes", []):
            leg = r["legs"][0]
            routes.append(
                {
                    "summary": r.get("summary"),
                    "distance_km": round(leg["distance"]["value"] / 1000, 2),
                    "duration_min": round(leg["duration"]["value"] / 60, 1),
                    "polyline": r["overview_polyline"]["points"],
                }
            )
        return NormalizedResult(
            data={"routes": routes},
            source_status=SourceStatus.REAL,
            source_name="Google Maps Directions API",
            retrieved_at=now_iso(),
            confidence="MEDIUM",
        )
