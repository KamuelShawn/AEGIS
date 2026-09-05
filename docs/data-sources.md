# Data Sources — Status & Fallback Reference

## Fallback flow (every provider)

```
Call live API
   │
   ├── success → validate → normalize → cache (with metadata) → return REAL/CACHED
   │
   └── failure
         │
         ├── cached data available? → return CACHED (labelled, with retrieval date)
         │
         └── no cache → return DEMO (clearly labelled, schema-identical)
```

Implemented once in `backend/app/providers/base.py::ProviderRegistry.resolve()` and
reused by every domain provider — a new integration only implements
`fetch/validate/normalize`, not the fallback logic.

## Status values

| Status | Meaning |
|---|---|
| `CONNECTED` | Live call succeeded this request |
| `NOT_CONFIGURED` | No credentials set for this provider |
| `AUTHENTICATION_ERROR` | Credentials present but rejected |
| `RATE_LIMITED` | Provider returned 429 / quota exceeded |
| `TEMPORARILY_UNAVAILABLE` | Network/5xx error |
| `DATA_UNAVAILABLE` | Provider reachable but no data for this query |
| `USING_CACHE` | Serving a previously cached response |
| `USING_DEMO_DATA` | Serving structured demo data |

`GET /api/status` returns this for every registered provider, e.g.:

```json
{
  "mapbox": {"status": "NOT_CONFIGURED", "detail": "NEXT_PUBLIC_MAPBOX_TOKEN not set"},
  "copernicus": {"status": "USING_DEMO_DATA", "detail": "credentials not set"},
  "data_gov_in": {"status": "USING_DEMO_DATA", "detail": "DATA_GOV_API_KEY not set"},
  "openstreetmap": {"status": "CONNECTED", "detail": "public Overpass instance"},
  "open_meteo": {"status": "CONNECTED", "detail": "no key required"}
}
```

## Data classification (shown on every metric in the UI)

`REAL` (verified external dataset) · `CACHED` · `DERIVED` (calculated from
real/simulated inputs) · `MODELLED` (forecast/regression output) · `SIMULATED` /
`DEMO` (synthetic, schema-identical demo data). The badge component is
`frontend/components/ui/DataSourceBadge.tsx`; the backend attaches
`source_status` + `source_name` + `retrieved_at` to every response payload via
`backend/app/providers/base.py::NormalizedResult`.
