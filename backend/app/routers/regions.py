"""
Nationwide region hierarchy: India -> State -> District, backed by real
OpenStreetMap administrative boundary data (see providers/regions/), not a
fixed demo list. States are fetched once and cached; districts are fetched
live per-state the first time they're requested, then cached.

IDs: a state's id is a slug of its name (e.g. "karnataka"); a district's id
is "<state-slug>__<district-slug>" (e.g. "karnataka__chamarajanagar") so
district names that repeat across states never collide.
"""
from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException

from app.providers.base import resolve
from app.providers.registry import registry

router = APIRouter(prefix="/api/regions", tags=["regions"])


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _fetch_states_with_source() -> tuple[list[dict], dict]:
    pair = registry.get("regions")
    result, connection_status = resolve(
        live=pair.live, mock=pair.mock, cache=registry.cache,
        cache_key="regions:states", params={"level": "states"},
    )
    states = []
    for r in result.data["regions"]:
        states.append(
            {
                "id": _slugify(r["name"]),
                "name": r["name"],
                "type": "state",
                "parent_id": "in",
                "center": [r["lon"], r["lat"]],
                "zoom": 6.5,
                "iso": r.get("iso"),
            }
        )
    source = {
        "status": result.source_status.value,
        "name": result.source_name,
        "retrieved_at": result.retrieved_at,
        "connection": connection_status.value,
    }
    return states, source


def _fetch_states() -> list[dict]:
    states, _ = _fetch_states_with_source()
    return states


def _fetch_districts_with_source(state_slug: str, state_name: str) -> tuple[list[dict], dict]:
    pair = registry.get("regions")
    result, connection_status = resolve(
        live=pair.live, mock=pair.mock, cache=registry.cache,
        cache_key=f"regions:districts:{state_slug}",
        params={"level": "districts", "state_name": state_name},
    )
    districts = []
    for r in result.data["regions"]:
        districts.append(
            {
                "id": f"{state_slug}__{_slugify(r['name'])}",
                "name": r["name"],
                "type": "district",
                "parent_id": state_slug,
                "center": [r["lon"], r["lat"]],
                "zoom": 9.0,
            }
        )
    source = {
        "status": result.source_status.value,
        "name": result.source_name,
        "retrieved_at": result.retrieved_at,
        "connection": connection_status.value,
    }
    return districts, source


def _fetch_districts(state_slug: str, state_name: str) -> list[dict]:
    districts, _ = _fetch_districts_with_source(state_slug, state_name)
    return districts


def _find_state(state_slug: str) -> dict | None:
    return next((s for s in _fetch_states() if s["id"] == state_slug), None)


# Legacy demo-dataset region ids (the original Bandipur case study) keep their
# hand-picked coordinates for backward compatibility with the curated demo
# datasets in app/data/demo/ — they are NOT part of the live OSM hierarchy.
_LEGACY_DEMO_COORDS = {
    "bandipur": (11.6667, 76.6333),
    "ka-chamarajanagar": (11.9261, 77.1197),
    "ka-mysuru": (12.2958, 76.6394),
    "kabini-basin": (11.95, 76.35),
}


def get_region_coords(region_id: str) -> tuple[float, float] | None:
    """
    Resolve ANY region id — legacy demo id, real state slug, or real
    state__district slug — to (lat, lon). Returns None if unresolvable,
    so callers can give an honest "not available" response instead of
    guessing/substituting a different place's coordinates.
    """
    if region_id in _LEGACY_DEMO_COORDS:
        return _LEGACY_DEMO_COORDS[region_id]

    if "__" in region_id:
        state_slug, _, _ = region_id.partition("__")
        state = _find_state(state_slug)
        if state is None:
            return None
        for d in _fetch_districts(state_slug, state["name"]):
            if d["id"] == region_id:
                return (d["center"][1], d["center"][0])
        return None

    state = _find_state(region_id)
    if state is not None:
        return (state["center"][1], state["center"][0])
    return None


@router.get("")
def list_regions(parent_id: str | None = None):
    """
    No parent_id (or parent_id="in") -> all Indian states/UTs (real, nationwide).
    parent_id=<state_id> -> that state's real districts (fetched live, then cached).
    parent_id=<district_id> -> empty (village level not built yet).
    """
    if parent_id is None or parent_id == "in":
        states, source = _fetch_states_with_source()
        return {"regions": states, "source": source}

    if "__" not in parent_id:
        state = _find_state(parent_id)
        if state is None:
            raise HTTPException(status_code=404, detail=f"Unknown state '{parent_id}'")
        districts, source = _fetch_districts_with_source(parent_id, state["name"])
        return {"regions": districts, "source": source}

    return {"regions": [], "source": None}


@router.get("/{region_id}")
def get_region(region_id: str):
    if region_id == "in":
        return {
            "id": "in", "name": "India", "type": "country", "parent_id": None,
            "center": [78.9629, 22.5937], "zoom": 4.2,
            "children": [s["id"] for s in _fetch_states()],
        }

    if "__" not in region_id:
        state = _find_state(region_id)
        if state is None:
            raise HTTPException(status_code=404, detail=f"Unknown region '{region_id}'")
        districts = _fetch_districts(region_id, state["name"])
        return {**state, "children": [d["id"] for d in districts]}

    state_slug, _, _district_slug = region_id.partition("__")
    state = _find_state(state_slug)
    if state is None:
        raise HTTPException(status_code=404, detail=f"Unknown region '{region_id}'")
    districts = _fetch_districts(state_slug, state["name"])
    district = next((d for d in districts if d["id"] == region_id), None)
    if district is None:
        raise HTTPException(status_code=404, detail=f"Unknown region '{region_id}'")
    return {**district, "children": []}
