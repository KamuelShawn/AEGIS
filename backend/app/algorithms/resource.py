"""
Resource sustainability: compare consumption vs replenishment for any
extractable/renewable resource (groundwater, surface water, minerals) and
determine a sustainable extraction limit and depletion risk.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SustainabilityStatus(str, Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    SEVERE = "SEVERE"


@dataclass
class ResourceBalance:
    available_reserve: float
    annual_replenishment: float
    current_extraction: float
    sustainable_extraction_limit: float
    extraction_ratio: float  # current_extraction / sustainable_extraction_limit
    remaining_capacity: float  # sustainable_limit - current_extraction, can be negative
    years_to_depletion: float | None  # None if not depleting under current trend
    status: SustainabilityStatus
    explanation: str


def calculate_resource_balance(
    *,
    available_reserve: float,
    annual_replenishment: float,
    current_extraction: float,
    safety_margin: float = 0.9,
) -> ResourceBalance:
    """
    safety_margin: fraction of annual replenishment considered sustainably
    extractable (0.9 = extracting up to 90% of natural recharge is considered
    the sustainable ceiling; the remaining 10% preserves baseflow/ecology).
    """
    sustainable_limit = annual_replenishment * safety_margin
    extraction_ratio = current_extraction / sustainable_limit if sustainable_limit > 0 else float("inf")
    remaining_capacity = sustainable_limit - current_extraction

    net_annual_change = annual_replenishment - current_extraction
    years_to_depletion = None
    if net_annual_change < 0 and available_reserve > 0:
        years_to_depletion = round(available_reserve / abs(net_annual_change), 1)

    if extraction_ratio < 0.7:
        status = SustainabilityStatus.SAFE
    elif extraction_ratio < 1.0:
        status = SustainabilityStatus.WARNING
    elif extraction_ratio < 1.3:
        status = SustainabilityStatus.CRITICAL
    else:
        status = SustainabilityStatus.SEVERE

    pct = extraction_ratio * 100
    explanation = f"Current extraction is {pct:.0f}% of the sustainable limit."
    if years_to_depletion is not None:
        explanation += f" At this rate, reserves are projected to deplete in approximately {years_to_depletion:.0f} years."

    return ResourceBalance(
        available_reserve=round(available_reserve, 2),
        annual_replenishment=round(annual_replenishment, 2),
        current_extraction=round(current_extraction, 2),
        sustainable_extraction_limit=round(sustainable_limit, 2),
        extraction_ratio=round(extraction_ratio, 3),
        remaining_capacity=round(remaining_capacity, 2),
        years_to_depletion=years_to_depletion,
        status=status,
        explanation=explanation,
    )


@dataclass
class ConsumptionBreakdown:
    agriculture: float
    industry: float
    domestic: float
    other: float

    @property
    def total(self) -> float:
        return self.agriculture + self.industry + self.domestic + self.other

    def as_shares(self) -> dict[str, float]:
        t = self.total or 1.0
        return {
            "agriculture": round(self.agriculture / t * 100, 1),
            "industry": round(self.industry / t * 100, 1),
            "domestic": round(self.domestic / t * 100, 1),
            "other": round(self.other / t * 100, 1),
        }
