# Feature → Data → Algorithm Matrix

Living reference. Update when a feature's data source or algorithm changes.

| Feature | Required data | Data source | Provider | Auth required | DB table | Processing | Algorithm | Endpoint | Frontend | Fallback |
|---|---|---|---|---|---|---|---|---|---|---|
| Forest change detection | Sentinel NDVI time series | Copernicus | `environment` | Yes (client id/secret) | `satellite_observations` | NDVI diff, cloud filter | `algorithms/trend.py` (rate + acceleration) | `/api/environment/forest-history` | Timeline + area chart | DEMO Bandipur series |
| Environmental risk score | Forest cover, degradation rate | Copernicus / FSI | `environment` | Optional | `risk_scores` | trend → threshold | `algorithms/risk.py` | `/api/environment/risk` | Risk badge + warning panel | DEMO |
| Water sustainability | Availability, extraction, recharge | India-WRIS / data.gov.in | `water` | Optional | `water_balance` | consumption vs replenishment | `algorithms/resource.py` | `/api/resources/water` | Resource meter | DEMO Karnataka basin |
| Groundwater depletion warning | Extraction rate, recharge rate | India-WRIS | `water` | Optional | `water_balance` | sustainable-limit comparison | `algorithms/resource.py` | `/api/resources/water/status` | Warning panel | DEMO |
| Air quality | AQI, PM2.5, PM10, NO2, SO2, CO, O3 | CPCB | `air_quality` | Optional | `air_quality_readings` | station aggregation, trend | `algorithms/trend.py` | `/api/environment/air-quality` | Heatmap + trend chart | DEMO |
| Infrastructure gap analysis | Roads, hospitals, villages | OpenStreetMap/Overpass | `infrastructure` | No (public) | `infrastructure_features` | nearest-feature distance | plain geospatial query (PostGIS `ST_Distance`) | `/api/infrastructure/gaps` | Gap table + map layer | DEMO OSM extract |
| Route optimization | Candidate paths, terrain, forest/water overlap | OSRM/Mapbox Directions + OpenTopography + PostGIS layers | `routing`, `elevation` | Optional | `candidate_routes` | multi-factor scoring | `algorithms/route_optimization.py` (weighted A\*/Dijkstra candidates + multi-objective score) | `/api/infrastructure/routes` | Route comparison table + map | DEMO 3-route set |
| Industrial site suitability | Water, infra access, pop proximity, sensitivity | data.gov.in + OSM + PostGIS | `industry` | Optional | `site_candidates` | weighted spatial scoring | `algorithms/site_suitability.py` | `/api/industry/site-suitability` | Site selector | DEMO candidate sites |
| Population/settlement layer | District/village population | data.gov.in / Census | `population` | Optional | `population_layers` | density join | none (raw + join) | `/api/population/{region}` | Population overlay | DEMO |
| Rainfall / weather | Precipitation, temperature | Open-Meteo | `weather` | No | `weather_observations` | seasonal aggregation | `algorithms/trend.py` | `/api/environment/weather` | Rainfall chart | Live (no key needed) or DEMO on outage |
| Forecasting (any metric) | Historical time series | any of the above | n/a | n/a | n/a | regression/smoothing | `algorithms/forecasting.py` | `/api/*/forecast` | "What if we continue?" screen | Confidence interval always shown |
| Sustainability score | Environment, resources, infra, social, pollution | aggregated above | n/a | n/a | `sustainability_scores` | weighted composite | `algorithms/sustainability.py` | `/api/regions/{id}/sustainability` | Central animated score + breakdown | Weights documented in code |
| Scenario simulation | Sliders (industrial/pop/water/forest/infra growth) | derived from current state | n/a | n/a | n/a | re-run all algorithms with modified inputs | `algorithms/sustainability.py`, `forecasting.py` | `/api/scenarios/simulate` | Scenario sliders screen | Always DERIVED/MODELLED |
| Recommendation engine | Detected problems (risk/warning states) | risk + resource outputs | n/a | n/a | `recommendations` | rule-based mapping problem→interventions | `algorithms/recommendations.py` | `/api/decisions/recommendations` | Recommendation panel | Rule-based, no LLM needed |
| Natural-language explanation | Any algorithm result | n/a | `llm` | Optional (Gemini) | n/a | template or LLM prose over existing numbers | n/a (post-processing only) | `/api/explain` | Chat/explanation panel | Template strings if no LLM key |
| Elevation / terrain difficulty | DEM | OpenTopography | `elevation` | Optional | `terrain_cache` | slope calc | used inside `route_optimization.py` | (internal) | Route planner cost factor | Flat-terrain fallback, labelled |
| Geocoding | Place ↔ coordinates | Mapbox | `geocoding` | Yes (public token) | n/a | n/a | n/a | `/api/geocode` | Region search box | Static Indian place list |

See `docs/data-sources.md` for the provider status/fallback flow shared by every row above.
