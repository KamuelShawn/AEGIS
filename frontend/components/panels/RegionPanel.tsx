"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  api,
  ApiError,
  type ForestHistory,
  type NDVIResponse,
  type Region,
  type RegionSustainability,
  type WaterBalance,
  type WeatherResponse,
} from "@/lib/api";
import { DataSourceBadge } from "@/components/ui/DataSourceBadge";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { ResourceMeter } from "@/components/ui/ResourceMeter";
import { SustainabilityScore } from "@/components/ui/SustainabilityScore";
import { ForestChart } from "@/components/charts/ForestChart";

type Loadable<T> = { status: "loading" } | { status: "ok"; data: T } | { status: "unavailable"; detail: string };

export function RegionPanel({ region }: { region: Region }) {
  const [forest, setForest] = useState<Loadable<ForestHistory>>({ status: "loading" });
  const [water, setWater] = useState<Loadable<WaterBalance>>({ status: "loading" });
  const [intel, setIntel] = useState<Loadable<RegionSustainability>>({ status: "loading" });
  const [weather, setWeather] = useState<Loadable<WeatherResponse>>({ status: "loading" });
  const [ndvi, setNdvi] = useState<{ status: "idle" | "loading" | "ok" | "error"; data?: NDVIResponse; error?: string }>({
    status: "idle",
  });

  useEffect(() => {
    let cancelled = false;

    const load = async <T,>(fn: () => Promise<T>, setter: (v: Loadable<T>) => void) => {
      setter({ status: "loading" });
      try {
        const data = await fn();
        if (!cancelled) setter({ status: "ok", data });
      } catch (err) {
        if (cancelled) return;
        const detail = err instanceof ApiError ? err.detail : "This data is not available right now.";
        setter({ status: "unavailable", detail });
      }
    };

    load(() => api.forestHistory(region.id), setForest);
    load(() => api.waterBalance(region.id), setWater);
    load(() => api.sustainability(region.id), setIntel);
    load(() => api.weather(region.id), setWeather);
    setNdvi({ status: "idle" });

    return () => {
      cancelled = true;
    };
  }, [region.id]);

  const runNdvi = async () => {
    setNdvi({ status: "loading" });
    try {
      const [lon, lat] = region.center;
      const data = await api.ndvi(lat, lon);
      setNdvi({ status: "ok", data });
    } catch (err) {
      setNdvi({ status: "error", error: err instanceof ApiError ? err.detail : "NDVI computation failed." });
    }
  };

  return (
    <div className="flex h-full flex-col gap-5 overflow-y-auto p-5">
      {/* WHERE AM I */}
      <div>
        <p className="text-xs uppercase tracking-widest text-earth-300/60">{region.type.replace("_", " ")}</p>
        <h2 className="text-2xl font-bold">{region.name}</h2>
      </div>

      {/* WHAT — central score, or an honest note that it's not available here yet */}
      {intel.status === "loading" && <p className="text-sm text-earth-300/60">Loading region intelligence…</p>}

      {intel.status === "ok" && (
        <>
          <section className="panel rounded-lg p-4">
            <SustainabilityScore
              overall={intel.data.sustainability.overall}
              factors={intel.data.sustainability.factors}
              explanation={intel.data.sustainability.explanation}
            />
          </section>

          <section className="panel rounded-lg p-4">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-earth-300/70">Risk</h3>
              <RiskBadge level={intel.data.risk.level} score={intel.data.risk.score} />
            </div>
            <p className="text-sm leading-relaxed text-earth-200/90">{intel.data.risk.explanation}</p>
            {intel.data.risk.projected_threshold_year && (
              <p className="mt-2 text-sm text-sustaina-amber">
                At current trends, a critical ecological threshold may be crossed by{" "}
                <strong>{intel.data.risk.projected_threshold_year}</strong>.
              </p>
            )}
          </section>
        </>
      )}

      {intel.status === "unavailable" && (
        <section className="panel rounded-lg p-4">
          <h3 className="mb-1 text-sm font-semibold uppercase tracking-wide text-earth-300/70">Full Sustainability Score</h3>
          <p className="text-sm text-earth-300/70">
            Not available for {region.name} yet — the curated multi-source dataset only covers the Bandipur case
            study today. Real data is nationwide-capable (weather and live satellite vegetation below); the
            missing piece is verified water/forest/population datasets for the rest of India (see project docs).
          </p>
        </section>
      )}

      {/* Weather — genuinely nationwide, works for any region */}
      <section className="panel rounded-lg p-4">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-earth-300/70">Weather (7-day)</h3>
          {weather.status === "ok" && <DataSourceBadge status={weather.data.source.status} name={weather.data.source.name} />}
        </div>
        {weather.status === "loading" && <p className="text-sm text-earth-300/60">Loading…</p>}
        {weather.status === "unavailable" && <p className="text-sm text-earth-300/60">{weather.detail}</p>}
        {weather.status === "ok" && (
          <div className="grid grid-cols-4 gap-2 text-xs text-earth-200/90">
            {weather.data.data.forecast.slice(0, 4).map((d) => (
              <div key={d.date} className="rounded bg-graphite-800 p-2 text-center">
                <p className="text-earth-300/60">{d.date.slice(5)}</p>
                <p className="font-semibold">{d.temp_max_c ?? "–"}°</p>
                <p className="text-sustaina-blue">{d.precipitation_mm ?? 0}mm</p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Live NDVI snapshot — genuinely works for any point in India, on demand (30-90s) */}
      <section className="panel rounded-lg p-4">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-earth-300/70">Live Vegetation (NDVI)</h3>
          {ndvi.status === "ok" && ndvi.data && <DataSourceBadge status={ndvi.data.source.status} name={ndvi.data.source.name} />}
        </div>
        {ndvi.status === "idle" && (
          <button
            onClick={runNdvi}
            className="rounded-md bg-graphite-700 px-3 py-2 text-xs font-medium hover:bg-graphite-600"
          >
            Compute live satellite snapshot for this location (~30-90s)
          </button>
        )}
        {ndvi.status === "loading" && <p className="text-sm text-earth-300/60">Computing NDVI from live Sentinel-2 imagery…</p>}
        {ndvi.status === "error" && <p className="text-sm text-sustaina-red">{ndvi.error}</p>}
        {ndvi.status === "ok" && ndvi.data && (
          <div>
            <p className="text-3xl font-bold tabular-nums">{(ndvi.data.vegetation_fraction * 100).toFixed(0)}%</p>
            <p className="mb-2 text-xs text-earth-300/60">
              vegetation-covered ({ndvi.data.vegetation_area_km2} km² of {ndvi.data.total_valid_area_km2} km² analyzed)
            </p>
            <p className="text-xs text-earth-300/70">{ndvi.data.source.notes}</p>
          </div>
        )}
      </section>

      {/* Forest cover — only where the curated demo series exists */}
      {forest.status === "ok" && (
        <section className="panel rounded-lg p-4">
          <div className="mb-1 flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-earth-300/70">Forest Cover History</h3>
            <DataSourceBadge status={forest.data.source.status} name={forest.data.source.name} />
          </div>
          <div className="mb-2 flex items-baseline gap-3">
            <span className="text-3xl font-bold tabular-nums">
              {forest.data.observations[forest.data.observations.length - 1]?.area.toFixed(0)} {forest.data.unit}
            </span>
            <span className={forest.data.trend.direction === "DECREASING" ? "text-sustaina-red text-sm" : "text-sustaina-green text-sm"}>
              {forest.data.trend.annual_rate_pct > 0 ? "+" : ""}
              {forest.data.trend.annual_rate_pct.toFixed(1)}%/yr
            </span>
          </div>
          <ForestChart history={forest.data} />
          <p className="mt-2 text-sm text-earth-200/80">{forest.data.trend.explanation}</p>
          {forest.data.causes.length > 0 && (
            <ul className="mt-2 list-disc pl-5 text-xs text-earth-300/70 space-y-0.5">
              {forest.data.causes.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ul>
          )}
        </section>
      )}
      {forest.status === "unavailable" && (
        <section className="panel rounded-lg p-4">
          <h3 className="mb-1 text-sm font-semibold uppercase tracking-wide text-earth-300/70">Forest Cover History</h3>
          <p className="text-sm text-earth-300/60">No historical series for {region.name} yet — try the live vegetation snapshot above.</p>
        </section>
      )}

      {/* Water resource — only where the curated demo dataset exists */}
      {water.status === "ok" && (
        <section className="panel rounded-lg p-4">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-earth-300/70">Water Balance</h3>
            <DataSourceBadge status={water.data.source.status} name={water.data.source.name} />
          </div>
          <ResourceMeter
            label="Extraction vs sustainable limit"
            pct={water.data.balance.extraction_ratio * 100}
            sublabel={water.data.balance.explanation}
          />
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-earth-300/70">
            {Object.entries(water.data.consumption_shares_pct).map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <span className="capitalize">{k}</span>
                <span className="tabular-nums">{v}%</span>
              </div>
            ))}
          </div>
        </section>
      )}
      {water.status === "unavailable" && (
        <section className="panel rounded-lg p-4">
          <h3 className="mb-1 text-sm font-semibold uppercase tracking-wide text-earth-300/70">Water Balance</h3>
          <p className="text-sm text-earth-300/60">No verified water dataset for {region.name} yet.</p>
        </section>
      )}

      {/* WHAT CAN WE DO */}
      {intel.status === "ok" && intel.data.recommendations.length > 0 && (
        <section className="panel rounded-lg p-4">
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-earth-300/70">Recommended Action</h3>
          {intel.data.recommendations.map((r) => (
            <div key={r.problem} className="mb-3 last:mb-0">
              <p className="text-sm font-medium text-earth-100">{r.problem}</p>
              <p className="text-xs text-earth-300/70 mb-1">{r.rationale}</p>
              <ul className="list-disc pl-5 text-sm text-earth-200/90 space-y-0.5">
                {r.interventions.slice(0, 3).map((iv) => (
                  <li key={iv}>{iv}</li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      )}

      <div className="flex gap-2 pt-1">
        <Link
          href={`/scenarios?region=${region.id}`}
          className="flex-1 rounded-md bg-graphite-700 px-4 py-2 text-center text-sm font-medium hover:bg-graphite-600"
        >
          What if we continue?
        </Link>
        <Link
          href="/decide"
          className="flex-1 rounded-md bg-sustaina-green px-4 py-2 text-center text-sm font-semibold text-graphite-950 hover:brightness-110"
        >
          The Sustainable Path
        </Link>
      </div>
    </div>
  );
}
