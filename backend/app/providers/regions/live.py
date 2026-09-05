"""
Real, nationwide administrative regions via OpenStreetMap/Overpass.

This replaces what used to be a hardcoded 6-region demo list scoped to
Karnataka/Bandipur. India → State is fetched once (admin_level=4, ~37 real
states/UTs) and State → District is fetched on demand per state
(admin_level=5) the first time a user drills into that state, then cached —
there is no reason to pre-load all ~766 districts up front.

Verified against live Overpass on 2026-09-05:
- admin_level=4 nationally returns 37 real states/UTs with correct names
  and ISO3166-2 codes and real centroids.
- admin_level=5 within a state's area returns real districts (confirmed:
  Karnataka -> 31 districts, including Chamarajanagar).

Known Overpass quirk: the public overpass-api.de mirror returns HTTP 406 for
requests using httpx's default User-Agent string (same class of bot-mitigation
as data.gov.in) — a plain, non-empty User-Agent header fixes it. This was
previously silently masking failures in providers/infrastructure/live.py too.
"""
from __future__ import annotations

import httpx

from app.providers.base import DataProvider, NormalizedResult, ProviderError, SourceStatus, now_iso

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
REQUEST_HEADERS = {"User-Agent": "SUSTAINA/1.0 (sustainability decision platform)"}

STATES_QUERY = """
[out:json][timeout:90];
area["ISO3166-1"="IN"][admin_level=2]->.india;
relation(area.india)[admin_level=4][boundary=administrative];
out center tags;
"""

DISTRICTS_QUERY_TEMPLATE = """
[out:json][timeout:60];
area["name"="{state_name}"]["admin_level"="4"]->.state;
relation(area.state)[boundary=administrative][admin_level="5"];
out center tags;
"""


class LiveOSMRegionsProvider(DataProvider):
    name = "osm_regions"

    def is_configured(self) -> bool:
        return True  # public Overpass instance, no key required

    def fetch(self, *, level: str, state_name: str | None = None, **_params) -> dict:
        if level == "states":
            query = STATES_QUERY
        elif level == "districts":
            if not state_name:
                raise ProviderError("state_name is required to fetch districts")
            query = DISTRICTS_QUERY_TEMPLATE.format(state_name=state_name)
        else:
            raise ProviderError(f"Unknown region level '{level}'")

        try:
            resp = httpx.post(OVERPASS_URL, data={"data": query}, headers=REQUEST_HEADERS, timeout=100.0)
        except httpx.RequestError as exc:
            raise ProviderError(f"Overpass network error: {exc}") from exc
        if resp.status_code == 429:
            raise ProviderError("Overpass rate limited")
        if resp.status_code >= 500:
            raise ProviderError("Overpass temporarily unavailable")
        if resp.status_code != 200:
            raise ProviderError(f"Overpass returned {resp.status_code}")
        return resp.json()

    def validate(self, raw: dict) -> bool:
        return isinstance(raw, dict) and "elements" in raw

    def normalize(self, raw: dict, *, level: str, state_name: str | None = None, **_params) -> NormalizedResult:
        regions = []
        for el in raw.get("elements", []):
            tags = el.get("tags", {})
            center = el.get("center") or {}
            name = tags.get("name")
            lat, lon = center.get("lat"), center.get("lon")
            if not name or lat is None or lon is None:
                continue
            if level == "states":
                # The area["ISO3166-1"="IN"] query can pull in neighboring
                # administrative relations near disputed border areas whose
                # OSM tagging bleeds across the boundary (observed: a Tibet/
                # China entity appearing in results despite the India area
                # filter). Requiring a genuine "IN-" ISO3166-2 code is an
                # objective data-quality filter that excludes these, since
                # only actual Indian states/UTs carry that tag.
                iso = tags.get("ISO3166-2", "")
                if not iso.startswith("IN-"):
                    continue
            regions.append(
                {
                    "osm_id": el.get("id"),
                    "name": name,
                    "iso": tags.get("ISO3166-2"),
                    "lat": lat,
                    "lon": lon,
                }
            )
        regions.sort(key=lambda r: r["name"])
        return NormalizedResult(
            data={"regions": regions, "level": level, "state_name": state_name},
            source_status=SourceStatus.REAL,
            source_name="OpenStreetMap (Overpass administrative boundaries)",
            retrieved_at=now_iso(),
            confidence="MEDIUM",
            notes="Centroids only — real admin-boundary polygons are a separate, larger gap (see docs/ARCHITECTURE.md).",
        )
