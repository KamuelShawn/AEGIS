from __future__ import annotations

from app.providers.base import DataProvider, NormalizedResult, SourceStatus, now_iso

# Illustrative elevations for the demo region set (meters) — Western Ghats foothills.
_DEMO_ELEVATIONS = {
    "bandipur": 850.0,
    "ka-chamarajanagar": 810.0,
    "ka-mysuru": 770.0,
    "kabini-basin": 700.0,
    "ka": 900.0,
}


class MockElevationProvider(DataProvider):
    name = "elevation_mock"

    def is_configured(self) -> bool:
        return True

    def fetch(self, *, region_id: str = "bandipur", lat: float = 0.0, lon: float = 0.0, **_params) -> dict:
        return {"elevation_m": _DEMO_ELEVATIONS.get(region_id, 750.0)}

    def normalize(self, raw: dict, *, lat: float = 0.0, lon: float = 0.0, **_params) -> NormalizedResult:
        return NormalizedResult(
            data={"elevation_m": raw["elevation_m"], "lat": lat, "lon": lon},
            source_status=SourceStatus.DEMO,
            source_name="SUSTAINA demo dataset (elevation schema)",
            retrieved_at=now_iso(),
        )
