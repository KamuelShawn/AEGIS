"""Mapbox Geocoding — reuses NEXT_PUBLIC_MAPBOX_TOKEN (public token, safe server-side too)."""
from __future__ import annotations

import httpx

from app.config import settings
from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

GEOCODE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"


class LiveMapboxGeocodingProvider(DataProvider):
    name = "mapbox_geocoding"

    def is_configured(self) -> bool:
        return bool(settings.NEXT_PUBLIC_MAPBOX_TOKEN)

    def fetch(self, *, query: str, **_params) -> dict:
        url = GEOCODE_URL.format(query=httpx.QueryParams({"q": query})["q"])
        try:
            resp = httpx.get(
                url,
                params={"access_token": settings.NEXT_PUBLIC_MAPBOX_TOKEN, "country": "in", "limit": 5},
                timeout=8.0,
            )
        except httpx.RequestError as exc:
            raise ProviderError(f"Mapbox network error: {exc}") from exc
        if resp.status_code == 401:
            raise ProviderError("Mapbox token rejected")
        if resp.status_code == 429:
            raise ProviderError("Mapbox rate limited")
        if resp.status_code >= 500:
            raise ProviderError("Mapbox temporarily unavailable")
        if resp.status_code != 200:
            raise ProviderError(f"Mapbox geocoding returned {resp.status_code}")
        return resp.json()

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "features" in raw

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        results = [
            {"name": f.get("place_name"), "lon": f["center"][0], "lat": f["center"][1]}
            for f in raw.get("features", [])
        ]
        return NormalizedResult(
            data={"results": results},
            source_status=SourceStatus.REAL,
            source_name="Mapbox Geocoding",
            retrieved_at=now_iso(),
            confidence="HIGH",
        )
