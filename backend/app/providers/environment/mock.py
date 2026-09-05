from __future__ import annotations

from app.data import load_demo
from app.providers.base import DataProvider, NormalizedResult, SourceStatus, now_iso


class MockForestProvider(DataProvider):
    """Schema-identical stand-in for Copernicus/FSI forest-cover history."""

    name = "environment_mock"

    def is_configured(self) -> bool:
        return True

    def fetch(self, *, region_id: str = "bandipur", **_params) -> dict:
        return load_demo("forest_history")

    def normalize(self, raw: dict, *, region_id: str = "bandipur", **_params) -> NormalizedResult:
        series = raw.get("series", {}).get(region_id, {})
        return NormalizedResult(
            data=series,
            source_status=SourceStatus.SIMULATED,
            source_name="SUSTAINA demo dataset (Copernicus/FSI schema)",
            retrieved_at=now_iso(),
            notes=raw.get("notes"),
        )
