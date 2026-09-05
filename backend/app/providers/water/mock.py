from __future__ import annotations

from app.data import load_demo
from app.providers.base import DataProvider, NormalizedResult, SourceStatus, now_iso


class MockWaterProvider(DataProvider):
    name = "water_mock"

    def is_configured(self) -> bool:
        return True

    def fetch(self, *, region_id: str = "kabini-basin", **_params) -> dict:
        return load_demo("water_balance")

    def normalize(self, raw: dict, *, region_id: str = "kabini-basin", **_params) -> NormalizedResult:
        basin = raw.get("basins", {}).get(region_id, {})
        return NormalizedResult(
            data=basin,
            source_status=SourceStatus.SIMULATED,
            source_name="SUSTAINA demo dataset (India-WRIS schema)",
            retrieved_at=now_iso(),
            notes=raw.get("notes"),
        )
