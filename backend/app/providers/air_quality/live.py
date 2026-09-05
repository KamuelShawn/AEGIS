"""
CPCB real-time air-quality data via data.gov.in.

Resource ID verified 2026-09-05 by direct query — it is genuinely the "Real
time Air Quality Index from various locations" CPCB dataset (per-pollutant
station readings), not a guess. Reuses the same DATA_GOV_API_KEY as the
water/population providers — one shared integration layer, not a key per
dataset, per the spec.

Honesty note: this live feed gives per-pollutant CURRENT station readings,
not a multi-year AQI history and not a single composite "AQI" number (CPCB
computes composite AQI from sub-indices via its own formula, which this
dataset doesn't expose pre-computed). So the live path fills
`pollutants_current` from real station data but leaves `aqi_history` empty
rather than fabricating a trend that doesn't exist in this feed — the
frontend already handles an empty history gracefully (no trend shown).
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

DATA_GOV_BASE = "https://api.data.gov.in/resource"
CPCB_RESOURCE_ID = "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"

# A generic browser User-Agent is required — data.gov.in's bot-mitigation
# silently hangs (no error, just a timeout) on requests with no/default
# client User-Agent strings, even with a valid api-key.
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SUSTAINA/1.0"}

# Demo region id -> CPCB city name, so /api/environment/air-quality?region_id=
# can filter the live feed to a relevant city.
REGION_TO_CITY = {
    "ka-mysuru": "Mysuru",
    "ka-chamarajanagar": "Mysuru",  # nearest CPCB-monitored city
    "bandipur": "Mysuru",
    "ka": "Bengaluru",
}


class LiveAirQualityProvider(DataProvider):
    name = "cpcb"

    def is_configured(self) -> bool:
        return bool(settings.DATA_GOV_API_KEY)

    def fetch(self, *, region_id: str | None = None, state: str | None = None, **_params) -> dict:
        params = {"api-key": settings.DATA_GOV_API_KEY, "format": "json", "limit": 500}
        city = REGION_TO_CITY.get(region_id) if region_id else None
        if city:
            params["filters[city]"] = city
        if state:
            params["filters[state]"] = state
        try:
            resp = httpx.get(f"{DATA_GOV_BASE}/{CPCB_RESOURCE_ID}", params=params, headers=REQUEST_HEADERS, timeout=10.0)
        except httpx.RequestError as exc:
            raise ProviderError(f"CPCB/data.gov.in network error: {exc}") from exc
        if resp.status_code in (401, 403):
            raise ProviderError("data.gov.in API key rejected")
        if resp.status_code == 429:
            raise ProviderError("data.gov.in rate limited")
        if resp.status_code >= 500:
            raise ProviderError("data.gov.in temporarily unavailable")
        if resp.status_code != 200:
            raise ProviderError(f"CPCB dataset request failed ({resp.status_code})")
        return resp.json()

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "records" in raw

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        records = raw.get("records", [])
        pollutants_current: dict[str, float] = {}
        for r in records:
            pollutant = (r.get("pollutant_id") or "").lower()
            avg = r.get("avg_value")
            if pollutant and avg not in (None, "", "NA"):
                try:
                    pollutants_current[pollutant] = float(avg)
                except ValueError:
                    continue
        return NormalizedResult(
            data={"pollutants_current": pollutants_current, "aqi_history": []},
            source_status=SourceStatus.REAL,
            source_name="CPCB real-time station data (via data.gov.in)",
            retrieved_at=now_iso(),
            confidence="MEDIUM",
            notes="Real-time per-pollutant station readings only; no multi-year AQI trend available from this feed.",
        )
