"""
OpenStreetMap via the public Overpass API — no personal key required.

RULE from the Word doc: never hammer public Overpass servers from the
frontend. This class is only ever called from the backend, and results are
cached by `resolve()` before reaching the client.
"""
from __future__ import annotations

import httpx

from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# amenity/highway/railway tags relevant to the Infrastructure module
FEATURE_QUERY = """
[out:json][timeout:20];
(
  node["amenity"="hospital"]({bbox});
  node["amenity"="school"]({bbox});
  way["highway"~"^(trunk|primary|secondary)$"]({bbox});
  way["railway"="rail"]({bbox});
  node["railway"="station"]({bbox});
);
out center 100;
"""


class LiveOSMProvider(DataProvider):
    name = "openstreetmap"

    def is_configured(self) -> bool:
        return True  # public instance, no key required

    def fetch(self, *, bbox: str, **_params) -> dict:
        """bbox format: 'south,west,north,east'"""
        query = FEATURE_QUERY.format(bbox=bbox)
        try:
            resp = httpx.post(OVERPASS_URL, data={"data": query}, timeout=25.0)
        except httpx.RequestError as exc:
            raise ProviderError(f"Overpass network error: {exc}") from exc
        if resp.status_code == 429:
            raise ProviderError("Overpass rate limited")
        if resp.status_code >= 500:
            raise ProviderError("Overpass temporarily unavailable")
        if resp.status_code != 200:
            raise ProviderError(f"Overpass returned {resp.status_code}")
        return resp.json()

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "elements" in raw

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        features = []
        for el in raw.get("elements", []):
            tags = el.get("tags", {})
            lat = el.get("lat") or (el.get("center") or {}).get("lat")
            lon = el.get("lon") or (el.get("center") or {}).get("lon")
            if lat is None or lon is None:
                continue
            features.append(
                {
                    "id": el.get("id"),
                    "type": tags.get("amenity") or tags.get("highway") or tags.get("railway") or "feature",
                    "name": tags.get("name"),
                    "lat": lat,
                    "lon": lon,
                }
            )
        return NormalizedResult(
            data={"features": features},
            source_status=SourceStatus.REAL,
            source_name="OpenStreetMap (Overpass API)",
            retrieved_at=now_iso(),
            confidence="MEDIUM",
        )
