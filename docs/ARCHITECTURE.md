# SUSTAINA — Architecture

"Develop Without Destroying" — a geospatial decision-support platform for India.

## Layered pipeline (mandatory shape)

```
External API / official dataset
        ↓
Provider adapter (fetch → validate → normalize → cache → get_status)
        ↓
PostgreSQL + PostGIS (with source/confidence/timestamp metadata)
        ↓
Intelligence engine (algorithms/: risk, sustainability, forecasting,
route optimization, site suitability — pure Python, zero API deps)
        ↓
FastAPI (backend/app/routers/*)
        ↓
Next.js / React / MapLibre / D3 / GSAP (frontend/)
```

The frontend never calls an external API directly. It calls our own FastAPI, which
returns already-validated, already-labelled data.

## Provider abstraction

Every external data source has a `Provider` interface (`backend/app/providers/base.py`):

```python
class DataProvider(Protocol):
    def fetch(self, **params) -> RawResult: ...
    def validate(self, raw: RawResult) -> bool: ...
    def normalize(self, raw: RawResult) -> NormalizedResult: ...
    def get_status(self) -> ProviderStatus: ...
```

Each domain (environment, water, forest, air_quality, infrastructure, weather,
elevation, geocoding, population, llm) has:

- `LiveXProvider` — talks to the real API, requires credentials.
- `MockXProvider` — returns structured, schema-identical demo data, labelled `DEMO`.

A `ProviderRegistry` picks Live if credentials are configured and the live call
succeeds, falls back to a cache table, then falls back to Mock — never crashing,
never silently presenting synthetic numbers as real. See `docs/data-sources.md`
for the full fallback flowchart and `/api/status` for the live status board.

## Data honesty

Every value returned by the API carries a `source_status` field, one of:
`REAL | CACHED | DERIVED | MODELLED | SIMULATED | DEMO`. The frontend renders this
next to every metric and chart (`DataSourceBadge` component). Algorithms may only
consume REAL/CACHED/DEMO inputs and produce DERIVED/MODELLED outputs — an LLM is
never allowed to originate a quantitative value (see `algorithms/` — no network
calls in that package, verified by tests).

## Why PostGIS and not "call the API from the browser"

Rate limits, licensing, latency, and reproducibility. Government/satellite sources
are ingested once, normalized into PostGIS with full provenance metadata, and
served from our own database — this is also what the Word-doc API spec mandates.

## Directory map

```
backend/
  app/
    algorithms/     pure-python intelligence engine (tested w/o network)
    providers/      per-source adapters (mock + live), provider_registry.py
    routers/        FastAPI endpoints
    db/             PostGIS schema + session
    data/demo/      structured demo datasets (labelled DEMO)
  tests/
frontend/
  app/              Next.js App Router pages (landing, explore, scenarios, decide)
  components/       map, panels, charts, design-system primitives
  lib/              API client, types
docs/
  ARCHITECTURE.md
  API_SETUP.md                       — how to obtain every credential
  FEATURE_DATA_ALGORITHM_MATRIX.md   — feature → data → algorithm → endpoint → UI
  data-sources.md                    — provider fallback + status reference
```
