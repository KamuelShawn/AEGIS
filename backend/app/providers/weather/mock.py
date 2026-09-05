from __future__ import annotations

from app.data import load_demo
from app.providers.base import DataProvider, NormalizedResult, SourceStatus, now_iso


class MockWeatherProvider(DataProvider):
    name = "open_meteo_mock"

    def is_configured(self) -> bool:
        return True

    def fetch(self, *, region_id: str = "kabini-basin", **_params) -> dict:
        return load_demo("water_balance")

    def normalize(self, raw: dict, *, region_id: str = "kabini-basin", **_params) -> NormalizedResult:
        basin = raw.get("basins", {}).get(region_id, {})
        rainfall = basin.get("rainfall_trend_mm", [])
        return NormalizedResult(
            data={"rainfall_trend_mm": rainfall},
            source_status=SourceStatus.DEMO,
            source_name="SUSTAINA demo dataset (Open-Meteo schema)",
            retrieved_at=now_iso(),
            notes=raw.get("notes"),
        )
