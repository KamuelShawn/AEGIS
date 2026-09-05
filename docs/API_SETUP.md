# API Setup

Every provider below works in DEMO mode with zero configuration. Fill in credentials
as you get them — the app auto-detects and switches from Mock to Live per provider,
no code changes needed. Check `/api/status` after starting the backend.

---

## 1. Mapbox — base map, geocoding
- **Purpose:** interactive map, tiles, styles, geocoding.
- **Sign up:** https://account.mapbox.com/
- **Get token:** Account → Tokens → Create a token. Name it `SUSTAINA_WEB`, scope to
  public permissions only, add URL restrictions before deploying.
- **Env var:** `NEXT_PUBLIC_MAPBOX_TOKEN` (public token only — never put a secret
  Mapbox token in frontend code).
- **Fallback:** MapLibre GL renders against free demo vector tiles (no key required)
  with reduced styling.
- **Test:** load `/explore` — map should render India.

## 2. Copernicus Data Space Ecosystem — satellite imagery
- **Purpose:** Sentinel-1/2 imagery, NDVI, land-cover/forest change detection.
- **Sign up:** https://dataspace.copernicus.eu/
- **Get credentials:** create an account, generate OAuth2 client credentials for
  programmatic access (S3/STAC). The secret is shown once — store it immediately.
- **STAC endpoint (current):** `https://stac.dataspace.copernicus.eu/v1/`
  (the older endpoint was deprecated Nov 17, 2025 — do not use it).
- **Env vars:** `COPERNICUS_CLIENT_ID`, `COPERNICUS_CLIENT_SECRET` (backend only).
- **Fallback:** cached NDVI/forest-change tiles → labelled DEMO satellite series.
- **Rate limits:** per Copernicus Data Space quota; backend caches search/asset
  results to avoid repeat queries.

## 3. data.gov.in — Indian government datasets
- **Purpose:** population, environment, water, infrastructure, industry, pollution
  statistics.
- **Sign up:** https://data.gov.in/ → create account → open a dataset → "API" tab →
  Generate API Key.
- **Env var:** `DATA_GOV_API_KEY`
- **Note:** one key is reused across all datasets you're permitted to access —
  don't try to get a separate key per dataset.
- **Fallback:** cached extract → labelled DEMO dataset (schema-identical).

## 4. India-WRIS — water resources
- **Purpose:** rivers, basins, reservoirs, groundwater, hydrology.
- **Access:** https://indiawris.gov.in/ — access model varies per dataset/service;
  no single documented API key. Where no live API exists for a dataset, download
  the official dataset, preprocess with GeoPandas, and load into PostGIS.
- **Env var:** none fixed; if a specific WRIS service issues credentials, add
  `INDIA_WRIS_API_KEY` and wire it into `providers/water/live.py`.
- **Fallback:** DEMO water-balance dataset.

## 5. Forest Survey of India (FSI) — forest cover
- **Purpose:** state/district forest cover, historical forest-cover reports.
- **Access:** https://fsi.nic.in/ — typically published reports/datasets, not a
  live REST API. Ingest pipeline: download → Python preprocessing → GeoJSON/GeoTIFF
  → PostGIS → FastAPI.
- **Fallback:** DEMO Bandipur-style forest-cover time series (clearly labelled
  SIMULATED, structured like real FSI report data).

## 6. Central Pollution Control Board (CPCB) — air quality
- **Purpose:** AQI, PM2.5, PM10, NO₂, SO₂, CO, O₃.
- **Access:** https://cpcb.nic.in/ — use documented open API/dataset if available;
  otherwise ingest the official published dataset into PostGIS.
- **Fallback:** DEMO AQI series.

## 7. OpenStreetMap / Overpass API — infrastructure
- **Purpose:** roads, railways, airports, hospitals, villages, buildings,
  industrial areas, bridges, ports.
- **Access:** https://overpass-api.de/ (public instance) — no personal API key
  required for normal use.
- **Rules:** never call Overpass from the browser; the backend queries, caches,
  and rate-limits.
- **Fallback:** cached OSM extract → DEMO infrastructure graph.

## 8. Open-Meteo — weather & rainfall
- **Purpose:** rainfall, temperature, precipitation, forecasts, historical weather.
- **Access:** https://open-meteo.com/ — no API key needed for normal use.
- **Env var:** none required.
- **Fallback:** DEMO seasonal rainfall series.

## 9. OpenTopography — elevation / terrain (optional)
- **Purpose:** elevation, slope, terrain difficulty for route optimization.
- **Sign up:** https://opentopography.org/
- **Env var:** `OPENTOPOGRAPHY_API_KEY`
- **Fallback:** DEM-free flat-terrain assumption, clearly labelled.

## 10. Google Maps Platform (optional, supplemental only)
- **Purpose:** geocoding/places/elevation backup — not the core map.
- **Sign up:** https://console.cloud.google.com/ → create project → enable
  billing → enable APIs → Credentials → Create API Key → restrict to required
  APIs and domains.
- **Env var:** `GOOGLE_MAPS_API_KEY`
- **Not required** — Mapbox + OSM + Copernicus is the primary foundation.

## 11. Gemini (or any LLM) — natural-language explanation layer (optional)
- **Purpose:** turn algorithm output into readable explanations and answer
  natural-language questions ("Why is this region critical?"). **Never** the
  source of a quantitative value — see `docs/ARCHITECTURE.md`.
- **Env var:** `GEMINI_API_KEY`
- **Fallback:** template-based explanation strings (still fully explainable,
  just less fluent).

---

## Verifying your setup

```bash
# backend
cd backend
cp ../.env.example ../.env   # then fill in what you have
pip install -r requirements.txt
uvicorn app.main:app --reload

# check provider status
curl http://localhost:8000/api/status
```

Each provider reports one of: `CONNECTED`, `NOT_CONFIGURED`, `AUTHENTICATION_ERROR`,
`RATE_LIMITED`, `TEMPORARILY_UNAVAILABLE`, `DATA_UNAVAILABLE`, `USING_CACHE`,
`USING_DEMO_DATA`.
