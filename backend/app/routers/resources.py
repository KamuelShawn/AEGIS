from fastapi import APIRouter, HTTPException

from app.algorithms.resource import calculate_resource_balance
from app.providers.base import resolve
from app.providers.registry import registry

router = APIRouter(prefix="/api/resources", tags=["resources"])

# The only regions with a real (simulated-but-labelled) water-balance dataset
# — see app/data/demo/water_balance.json. No verified nationwide live water
# dataset exists yet (see docs/API_SETUP.md item 4) — any other region gets
# an honest "not available" rather than Kabini basin's numbers substituted in.
_WATER_BALANCE_REGIONS = ("kabini-basin", "ka-chamarajanagar")


@router.get("/water")
def water_balance(region_id: str = "kabini-basin"):
    if region_id not in _WATER_BALANCE_REGIONS:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No water-balance data available for region '{region_id}' yet — "
                "no verified nationwide water dataset is wired up (see docs/API_SETUP.md item 4)."
            ),
        )

    pair = registry.get("water")
    result, connection_status = resolve(
        live=pair.live, mock=pair.mock, cache=registry.cache,
        cache_key=f"water:{region_id}", params={"region_id": region_id},
    )
    basin = result.data
    balance = calculate_resource_balance(
        available_reserve=basin.get("available_reserve_mcm", 0),
        annual_replenishment=basin.get("annual_replenishment_mcm", 0),
        current_extraction=basin.get("current_extraction_mcm", 0),
    )
    consumption = basin.get("consumption_breakdown", {})
    total = sum(consumption.values()) or 1
    consumption_shares = {k: round(v / total * 100, 1) for k, v in consumption.items()}

    return {
        "region_id": region_id,
        "unit": "MCM/year",
        "balance": {
            "available_reserve": balance.available_reserve,
            "annual_replenishment": balance.annual_replenishment,
            "current_extraction": balance.current_extraction,
            "sustainable_extraction_limit": balance.sustainable_extraction_limit,
            "extraction_ratio": balance.extraction_ratio,
            "remaining_capacity": balance.remaining_capacity,
            "years_to_depletion": balance.years_to_depletion,
            "status": balance.status.value,
            "explanation": balance.explanation,
        },
        "consumption_breakdown": consumption,
        "consumption_shares_pct": consumption_shares,
        "source": {
            "status": result.source_status.value,
            "name": result.source_name,
            "retrieved_at": result.retrieved_at,
            "connection": connection_status.value,
        },
    }
