from __future__ import annotations

from app.providers.base import DataProvider, NormalizedResult, SourceStatus, now_iso

_DEMO_FEATURES = [
    {"id": 1, "type": "hospital", "name": "Chamarajanagar District Hospital", "lat": 11.9236, "lon": 76.9391},
    {"id": 2, "type": "school", "name": "Govt High School, Gundlupet", "lat": 11.8078, "lon": 76.6947},
    {"id": 3, "type": "trunk", "name": "NH 766 (Mysuru–Ooty)", "lat": 11.75, "lon": 76.65},
    {"id": 4, "type": "railway", "name": "Nanjangud Town Rail Corridor", "lat": 12.1187, "lon": 76.6830},
]


class MockOSMProvider(DataProvider):
    name = "openstreetmap_mock"

    def is_configured(self) -> bool:
        return True

    def fetch(self, **_params) -> dict:
        return {"elements": _DEMO_FEATURES}

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        return NormalizedResult(
            data={"features": raw["elements"]},
            source_status=SourceStatus.DEMO,
            source_name="SUSTAINA demo dataset (OSM schema)",
            retrieved_at=now_iso(),
        )
