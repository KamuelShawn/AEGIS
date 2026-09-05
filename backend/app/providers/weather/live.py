"""
Open-Meteo — the only provider in this project that needs no API key at all,
so LiveOpenMeteoProvider.is_configured() is always True. It still respects
the same ProviderError contract so resolve() falls back to demo data on a
network failure during a live demo.
"""
from __future__ import annotations

import httpx

from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


class LiveOpenMeteoProvider(DataProvider):
    name = "open_meteo"

    def is_configured(self) -> bool:
        return True  # public API, no key required

    def fetch(self, *, lat: float, lon: float, **_params) -> dict:
        try:
            response = httpx.get(
                OPEN_METEO_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
                    "timezone": "auto",
                    "forecast_days": 7,
                },
                timeout=8.0,
            )
        except httpx.RequestError as exc:
            raise ProviderError(f"Open-Meteo network error: {exc}") from exc

        if response.status_code == 429:
            raise ProviderError("Open-Meteo rate limited")
        if response.status_code >= 500:
            raise ProviderError("Open-Meteo temporarily unavailable")
        if response.status_code != 200:
            raise ProviderError(f"Open-Meteo returned {response.status_code}")

        return response.json()

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "daily" in raw

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        daily = raw.get("daily", {})
        days = daily.get("time", [])
        forecast = [
            {
                "date": day,
                "precipitation_mm": daily.get("precipitation_sum", [None] * len(days))[i],
                "temp_max_c": daily.get("temperature_2m_max", [None] * len(days))[i],
                "temp_min_c": daily.get("temperature_2m_min", [None] * len(days))[i],
            }
            for i, day in enumerate(days)
        ]
        return NormalizedResult(
            data={"forecast": forecast},
            source_status=SourceStatus.REAL,
            source_name="Open-Meteo",
            retrieved_at=now_iso(),
            confidence="HIGH",
        )
