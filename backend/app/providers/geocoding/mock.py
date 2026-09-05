from __future__ import annotations

from app.data import load_demo
from app.providers.base import DataProvider, NormalizedResult, SourceStatus, now_iso


class MockGeocodingProvider(DataProvider):
    name = "geocoding_mock"

    def is_configured(self) -> bool:
        return True

    def fetch(self, *, query: str = "", **_params) -> dict:
        regions = load_demo("regions")["regions"]
        query_lower = query.lower()
        matches = [r for r in regions if query_lower in r["name"].lower()] or regions
        return {"matches": matches}

    def normalize(self, raw: dict, **_params) -> NormalizedResult:
        results = [
            {"name": r["name"], "lon": r["center"][0], "lat": r["center"][1]}
            for r in raw["matches"]
        ]
        return NormalizedResult(
            data={"results": results},
            source_status=SourceStatus.DEMO,
            source_name="SUSTAINA demo region list",
            retrieved_at=now_iso(),
        )
