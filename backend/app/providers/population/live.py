"""Population/settlement statistics via data.gov.in (Census-derived datasets)."""
from __future__ import annotations

import httpx

from app.config import settings
from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

DATA_GOV_BASE = "https://api.data.gov.in/resource"

# IMPORTANT: verified 2026-09-05 — "6176ee09-3d56-4a3b-8115-21841576b2f6" is the
# "All India Pincode Directory" dataset, NOT population/census data. There is
# no verified real population/census resource ID wired up yet. Rather than
# guess another one and risk silently mislabeling the wrong dataset as REAL
# population data, this stays unset until a human finds and confirms the
# correct data.gov.in resource ID (search data.gov.in for "Census" or
# "District-wise Population"). Until then, fetch() always defers to the
# DEMO provider — this is the safe, honest behavior per docs/ARCHITECTURE.md.
POPULATION_RESOURCE_ID: str | None = None

# A generic browser User-Agent is required — data.gov.in's bot-mitigation
# silently hangs (no error, just a timeout) on requests with no/default
# client User-Agent strings, even with a valid api-key.
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SUSTAINA/1.0"}


class LivePopulationProvider(DataProvider):
    name = "data_gov_in_population"

    def is_configured(self) -> bool:
        return bool(settings.DATA_GOV_API_KEY) and bool(POPULATION_RESOURCE_ID)

    def fetch(self, *, district: str | None = None, **_params) -> dict:
        if not POPULATION_RESOURCE_ID:
            raise ProviderError("No verified data.gov.in population/census resource ID configured yet")
        params = {"api-key": settings.DATA_GOV_API_KEY, "format": "json", "limit": 200}
        if district:
            params["filters[district]"] = district
        try:
            resp = httpx.get(
                f"{DATA_GOV_BASE}/{POPULATION_RESOURCE_ID}", params=params, headers=REQUEST_HEADERS, timeout=10.0
            )
        except httpx.RequestError as exc:
            raise ProviderError(f"data.gov.in network error: {exc}") from exc
        if resp.status_code in (401, 403):
            raise ProviderError("data.gov.in API key rejected")
        if resp.status_code == 429:
            raise ProviderError("data.gov.in rate limited")
        if resp.status_code >= 500:
            raise ProviderError("data.gov.in temporarily unavailable")
        if resp.status_code != 200:
            raise ProviderError(f"Population dataset request failed ({resp.status_code})")
        return resp.json()

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "records" in raw

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        return NormalizedResult(
            data={"records": raw.get("records", [])},
            source_status=SourceStatus.REAL,
            source_name="data.gov.in (Census-derived)",
            retrieved_at=now_iso(),
            confidence="MEDIUM",
        )
