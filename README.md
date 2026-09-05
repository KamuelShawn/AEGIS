# AEGIS — Develop Without Destroying

A sustainability intelligence & geospatial decision platform for India. See
`docs/ARCHITECTURE.md` for the full design and `docs/API_SETUP.md` to wire up
real credentials — the app runs end-to-end in DEMO mode with zero configuration.

## Quick start

```bash
# Backend
cd backend
python -m venv .venv
./.venv/Scripts/activate        # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp ../.env.example ../.env      # fill in whatever credentials you have
uvicorn app.main:app --reload --port 8010

# Frontend (separate terminal)
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8010" > .env.local
npm run dev
```

Open http://localhost:3000 (landing) → **Enter the Platform** → India/Karnataka
map → click a region marker → forest history, water balance, risk, and
sustainability score populate from the backend (demo data, honestly labelled).
**What if we continue?** opens the scenario simulator; **The Sustainable
Path** opens route optimization + industrial site suitability + the final
decision summary.

## What's implemented

- **Algorithms** (`backend/app/algorithms/`): trend analysis, forecasting with
  confidence bands, risk scoring, resource sustainability, composite
  sustainability score, A*/multi-objective route optimization, weighted site
  suitability, rule-based recommendations. 43 unit tests, zero network
  dependency (`pytest` in `backend/`).
- **Provider abstraction** (`backend/app/providers/`): Live + Mock pair for
  every data source in the API spec (Copernicus, data.gov.in, India-WRIS/CPCB
  schema, OpenStreetMap/Overpass — real and working with no key, Open-Meteo —
  real and working with no key, Mapbox geocoding, Gemini). Automatic
  LIVE → CACHE → DEMO fallback (`providers/base.py::resolve`). `GET
  /api/status` reports every provider's connection state.
- **Central Intelligence Engine** (`backend/app/services/region_intelligence.py`):
  connects environment → resources → pollution → population into one risk
  score, sustainability score, and recommendation set per region, plus a
  what-if scenario simulator.
- **Frontend** (`frontend/`): cinematic landing page, map-first Explore screen
  (MapLibre, region drill-down, progressive-disclosure intelligence panel with
  data-source badges), What-If scenario sliders, and a Decide screen (route
  weight sliders + live re-ranking, site suitability, final decision summary).
- **Bandipur case study** demo dataset per the PDF spec (section 9), clearly
  labelled SIMULATED throughout.

## What's next (not yet built)

- PostGIS schema + real spatial joins (regions are a fixed demo list today,
  not polygons); GeoPandas/Rasterio NDVI processing behind the Copernicus
  live provider (currently returns scene metadata only); real drill-down to
  district/village/forest polygon boundaries on the map; GSAP cinematic
  camera intro; presentation/command-center mode; report generation (PDF/CSV
  export); mobile-responsive layout pass; natural-language exploration via
  the LLM provider (the provider exists, no chat UI yet).

Run `pytest` in `backend/` and `npm run build` in `frontend/` before every
commit — both are green as of this writing.
