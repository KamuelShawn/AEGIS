"""
Copernicus Data Space Ecosystem — satellite-derived forest/vegetation change.

This is a real integration skeleton against the CURRENT (post Nov 17 2025) STAC
endpoint. It authenticates, searches Sentinel-2 scenes over a bounding box, and
returns scene metadata; full NDVI raster processing (rasterio-based) is the
next step once credentials are supplied — see docs/API_SETUP.md item 2.

Until COPERNICUS_CLIENT_ID/SECRET are set, is_configured() is False and
resolve() falls straight to cache/demo, so this file being incomplete never
blocks the rest of the app.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

STAC_SEARCH_URL = "https://stac.dataspace.copernicus.eu/v1/search"
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"


class LiveCopernicusProvider(DataProvider):
    name = "copernicus"

    def is_configured(self) -> bool:
        return bool(settings.COPERNICUS_CLIENT_ID and settings.COPERNICUS_CLIENT_SECRET)

    def _get_token(self) -> str:
        try:
            resp = httpx.post(
                TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.COPERNICUS_CLIENT_ID,
                    "client_secret": settings.COPERNICUS_CLIENT_SECRET,
                },
                timeout=10.0,
            )
        except httpx.RequestError as exc:
            raise ProviderError(f"Copernicus auth network error: {exc}") from exc
        if resp.status_code == 401:
            raise ProviderError("Copernicus credentials rejected", status=None)
        if resp.status_code != 200:
            raise ProviderError(f"Copernicus auth failed ({resp.status_code})")
        return resp.json()["access_token"]

    def fetch(self, *, bbox: list[float], date_from: str, date_to: str, max_cloud_cover: int = 20, **_params) -> dict:
        token = self._get_token()
        try:
            resp = httpx.post(
                STAC_SEARCH_URL,
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "collections": ["sentinel-2-l2a"],
                    "bbox": bbox,
                    "datetime": f"{date_from}/{date_to}",
                    "limit": 20,
                    "query": {"eo:cloud_cover": {"lt": max_cloud_cover}},
                },
                timeout=15.0,
            )
        except httpx.RequestError as exc:
            raise ProviderError(f"Copernicus STAC network error: {exc}") from exc
        if resp.status_code == 429:
            raise ProviderError("Copernicus rate limited")
        if resp.status_code >= 500:
            raise ProviderError("Copernicus temporarily unavailable")
        if resp.status_code != 200:
            raise ProviderError(f"Copernicus STAC search failed ({resp.status_code})")
        return resp.json()

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "features" in raw

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        scenes = [
            {
                "id": f["id"],
                "datetime": f["properties"].get("datetime"),
                "cloud_cover": f["properties"].get("eo:cloud_cover"),
                "assets": list(f.get("assets", {}).keys()),
            }
            for f in raw.get("features", [])
        ]
        return NormalizedResult(
            data={"scenes": scenes},
            source_status=SourceStatus.REAL,
            source_name="Copernicus Data Space (Sentinel-2 STAC)",
            retrieved_at=now_iso(),
            confidence="HIGH",
            notes="Scene metadata only; NDVI raster processing pipeline not yet wired to this response.",
        )
