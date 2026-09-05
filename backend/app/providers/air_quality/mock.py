from __future__ import annotations

from app.data import load_demo
from app.providers.base import DataProvider, NormalizedResult, SourceStatus, now_iso


class MockAirQualityProvider(DataProvider):
    name = "air_quality_mock"

    def is_configured(self) -> bool:
        return True

    def fetch(self, *, region_id: str = "ka-mysuru", **_params) -> dict:
        return load_demo("air_quality")

    def normalize(self, raw: dict, *, region_id: str = "ka-mysuru", **_params) -> NormalizedResult:
        station = raw.get("stations", {}).get(region_id, {})
        return NormalizedResult(
            data=station,
            source_status=SourceStatus.SIMULATED,
            source_name="SUSTAINA demo dataset (CPCB schema)",
            retrieved_at=now_iso(),
            notes=raw.get("notes"),
        )
