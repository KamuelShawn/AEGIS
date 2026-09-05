from __future__ import annotations

from app.providers.base import DataProvider, NormalizedResult, SourceStatus, now_iso

_DEMO_POPULATION = {
    "ka-chamarajanagar": {"total": 1020000, "urban_pct": 22.4, "rural_pct": 77.6, "density_per_km2": 168},
    "ka-mysuru": {"total": 3002000, "urban_pct": 45.1, "rural_pct": 54.9, "density_per_km2": 431},
}


class MockPopulationProvider(DataProvider):
    name = "population_mock"

    def is_configured(self) -> bool:
        return True

    def fetch(self, *, region_id: str = "ka-chamarajanagar", **_params) -> dict:
        return _DEMO_POPULATION.get(region_id, {})

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        return NormalizedResult(
            data=raw,
            source_status=SourceStatus.DEMO,
            source_name="SUSTAINA demo dataset (Census schema)",
            retrieved_at=now_iso(),
        )
