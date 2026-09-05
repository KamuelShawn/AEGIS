"""
data.gov.in resource API — used for water-resource datasets published there.

India-WRIS itself does not expose one universal documented API key (see
docs/API_SETUP.md item 4); where a specific WRIS dataset is only available as
a download, ingest it offline into PostGIS instead of trying to call it live
here. This class covers the data.gov.in-hosted subset.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

DATA_GOV_BASE = "https://api.data.gov.in/resource"

# A generic browser User-Agent is required — data.gov.in's bot-mitigation
# silently hangs (no error, just a timeout) on requests with no/default
# client User-Agent strings, even with a valid api-key.
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SUSTAINA/1.0"}

# No verified real India-WRIS/data.gov.in water-balance resource ID has been
# found yet (see docs/API_SETUP.md item 4 — India-WRIS has no single
# documented dataset ID). No router currently passes a resource_id, so this
# provider always safely falls back to the DEMO provider until one is found
# and wired through resources.py.


class LiveWaterProvider(DataProvider):
    name = "data_gov_in_water"

    def is_configured(self) -> bool:
        return bool(settings.DATA_GOV_API_KEY)

    def fetch(self, *, resource_id: str, **_params) -> dict:
        try:
            resp = httpx.get(
                f"{DATA_GOV_BASE}/{resource_id}",
                params={"api-key": settings.DATA_GOV_API_KEY, "format": "json", "limit": 500},
                headers=REQUEST_HEADERS,
                timeout=10.0,
            )
        except httpx.RequestError as exc:
            raise ProviderError(f"data.gov.in network error: {exc}") from exc
        if resp.status_code == 401 or resp.status_code == 403:
            raise ProviderError("data.gov.in API key rejected")
        if resp.status_code == 429:
            raise ProviderError("data.gov.in rate limited")
        if resp.status_code >= 500:
            raise ProviderError("data.gov.in temporarily unavailable")
        if resp.status_code != 200:
            raise ProviderError(f"data.gov.in returned {resp.status_code}")
        return resp.json()

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "records" in raw

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        return NormalizedResult(
            data={"records": raw.get("records", [])},
            source_status=SourceStatus.REAL,
            source_name="data.gov.in",
            retrieved_at=now_iso(),
            confidence="MEDIUM",
        )
