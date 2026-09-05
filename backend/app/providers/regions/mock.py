from __future__ import annotations

from app.providers.base import DataProvider, NormalizedResult, SourceStatus, now_iso

# Used only if OSM/Overpass is unreachable. A handful of states so the app
# stays usable, NOT presented as a substitute for the real nationwide list.
_FALLBACK_STATES = [
    {"osm_id": None, "name": "Karnataka", "iso": "IN-KA", "lat": 15.3173, "lon": 75.7139},
    {"osm_id": None, "name": "Maharashtra", "iso": "IN-MH", "lat": 19.7515, "lon": 75.7139},
    {"osm_id": None, "name": "Rajasthan", "iso": "IN-RJ", "lat": 27.0238, "lon": 74.2179},
    {"osm_id": None, "name": "Tamil Nadu", "iso": "IN-TN", "lat": 11.1271, "lon": 78.6569},
    {"osm_id": None, "name": "Uttar Pradesh", "iso": "IN-UP", "lat": 26.8467, "lon": 80.9462},
    {"osm_id": None, "name": "West Bengal", "iso": "IN-WB", "lat": 22.9868, "lon": 87.8550},
]

_FALLBACK_DISTRICTS = {
    "Karnataka": [
        {"osm_id": None, "name": "Chamarajanagar", "iso": None, "lat": 11.9261, "lon": 77.1197},
        {"osm_id": None, "name": "Mysuru", "iso": None, "lat": 12.2958, "lon": 76.6394},
    ],
}


class MockOSMRegionsProvider(DataProvider):
    name = "osm_regions_mock"

    def is_configured(self) -> bool:
        return True

    def fetch(self, *, level: str, state_name: str | None = None, **_params) -> dict:
        if level == "states":
            return {"regions": _FALLBACK_STATES}
        return {"regions": _FALLBACK_DISTRICTS.get(state_name or "", [])}

    def normalize(self, raw: dict, *, level: str, state_name: str | None = None, **_params) -> NormalizedResult:
        return NormalizedResult(
            data={"regions": raw["regions"], "level": level, "state_name": state_name},
            source_status=SourceStatus.DEMO,
            source_name="SUSTAINA fallback region list (OSM unreachable)",
            retrieved_at=now_iso(),
        )
