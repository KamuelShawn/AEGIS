"""
Central registry of every Live/Mock provider pair, plus a shared FileCache.

Routers call `registry.get(domain)` to obtain a `(live, mock)` pair and then
`resolve(live=..., mock=..., cache=registry.cache, cache_key=...)`.
GET /api/status iterates `registry.all()` to report every provider's health.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.providers.air_quality.live import LiveAirQualityProvider
from app.providers.air_quality.mock import MockAirQualityProvider
from app.providers.base import ConnectionStatus, DataProvider, FileCache
from app.providers.elevation.live import LiveGoogleElevationProvider
from app.providers.elevation.mock import MockElevationProvider
from app.providers.environment.live import LiveCopernicusProvider
from app.providers.environment.mock import MockForestProvider
from app.providers.geocoding.live import LiveMapboxGeocodingProvider
from app.providers.geocoding.mock import MockGeocodingProvider
from app.providers.google_maps.live import LiveGoogleGeocodingProvider
from app.providers.google_maps.mock import MockGoogleGeocodingProvider
from app.providers.infrastructure.live import LiveOSMProvider
from app.providers.infrastructure.mock import MockOSMProvider
from app.providers.llm.live import LiveGeminiProvider
from app.providers.llm.mock import TemplateExplanationProvider
from app.providers.population.live import LivePopulationProvider
from app.providers.population.mock import MockPopulationProvider
from app.providers.regions.live import LiveOSMRegionsProvider
from app.providers.regions.mock import MockOSMRegionsProvider
from app.providers.water.live import LiveWaterProvider
from app.providers.water.mock import MockWaterProvider
from app.providers.weather.live import LiveOpenMeteoProvider
from app.providers.weather.mock import MockWeatherProvider


@dataclass
class ProviderPair:
    domain: str
    live: DataProvider
    mock: DataProvider
    purpose: str


class ProviderRegistry:
    def __init__(self) -> None:
        self.cache = FileCache()
        self._pairs: dict[str, ProviderPair] = {
            "environment": ProviderPair("environment", LiveCopernicusProvider(), MockForestProvider(), "Forest cover / satellite change"),
            "water": ProviderPair("water", LiveWaterProvider(), MockWaterProvider(), "Water resources"),
            "air_quality": ProviderPair("air_quality", LiveAirQualityProvider(), MockAirQualityProvider(), "AQI / pollution"),
            "infrastructure": ProviderPair("infrastructure", LiveOSMProvider(), MockOSMProvider(), "Roads, hospitals, rail"),
            "weather": ProviderPair("weather", LiveOpenMeteoProvider(), MockWeatherProvider(), "Rainfall / weather"),
            "population": ProviderPair("population", LivePopulationProvider(), MockPopulationProvider(), "Population / settlements"),
            "geocoding": ProviderPair("geocoding", LiveMapboxGeocodingProvider(), MockGeocodingProvider(), "Place search"),
            "llm": ProviderPair("llm", LiveGeminiProvider(), TemplateExplanationProvider(), "Natural-language explanation"),
            "elevation": ProviderPair("elevation", LiveGoogleElevationProvider(), MockElevationProvider(), "Elevation / terrain (Google Elevation API)"),
            "google_maps_geocoding": ProviderPair("google_maps_geocoding", LiveGoogleGeocodingProvider(), MockGoogleGeocodingProvider(), "Supplemental geocoding (Google Maps, backup to Mapbox)"),
            "regions": ProviderPair("regions", LiveOSMRegionsProvider(), MockOSMRegionsProvider(), "Nationwide administrative regions (OSM)"),
        }

    def get(self, domain: str) -> ProviderPair:
        return self._pairs[domain]

    def all(self) -> dict[str, ProviderPair]:
        return self._pairs

    def status_report(self) -> dict[str, dict]:
        report = {}
        for domain, pair in self._pairs.items():
            live_status = pair.live.get_status()
            detail = "configured and reachable" if live_status == ConnectionStatus.CONNECTED else "credentials not set — serving demo data"
            report[domain] = {
                "purpose": pair.purpose,
                "status": live_status.value,
                "detail": detail,
            }
        return report


registry = ProviderRegistry()
