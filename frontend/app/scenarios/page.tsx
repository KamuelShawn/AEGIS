"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api, type ScenarioResult } from "@/lib/api";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { AnimatedNumber } from "@/components/ui/AnimatedNumber";

const SLIDERS: { key: keyof Sliders; label: string; min: number; max: number }[] = [
  { key: "industrial_growth_pct", label: "Industrial Growth", min: -50, max: 150 },
  { key: "population_growth_pct", label: "Population Growth", min: -50, max: 150 },
  { key: "water_consumption_pct", label: "Water Consumption", min: -50, max: 150 },
  { key: "forest_protection_pct", label: "Forest Protection", min: 0, max: 100 },
  { key: "infrastructure_expansion_pct", label: "Infrastructure Expansion", min: -50, max: 150 },
];

interface Sliders {
  industrial_growth_pct: number;
  population_growth_pct: number;
  water_consumption_pct: number;
  forest_protection_pct: number;
  infrastructure_expansion_pct: number;
}

const DEFAULT_SLIDERS: Sliders = {
  industrial_growth_pct: 0,
  population_growth_pct: 0,
  water_consumption_pct: 0,
  forest_protection_pct: 0,
  infrastructure_expansion_pct: 0,
};

function ScenariosInner() {
  const searchParams = useSearchParams();
  const regionId = searchParams.get("region") || "bandipur";
  const [sliders, setSliders] = useState<Sliders>(DEFAULT_SLIDERS);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .simulateScenario({ region_id: regionId, ...sliders })
      .then((r) => !cancelled && setResult(r))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [regionId, sliders]);

  return (
    <div className="min-h-screen bg-graphite-950 px-6 py-8 md:px-16">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <Link href={`/explore?region=${regionId}`} className="text-xs text-earth-300/60 hover:text-earth-100">
            ← Back to Explore
          </Link>
          <h1 className="mt-1 text-3xl font-bold">What If We Continue?</h1>
          <p className="text-sm text-earth-300/60">Region: {regionId}</p>
        </div>
        <span className="badge bg-graphite-700 text-earth-200">MODELLED PROJECTION</span>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_1.2fr]">
        <div className="panel space-y-6 rounded-lg p-6">
          {SLIDERS.map((s) => (
            <div key={s.key}>
              <div className="mb-1 flex justify-between text-sm">
                <span className="text-earth-200">{s.label}</span>
                <span className="tabular-nums text-earth-300/70">{sliders[s.key]}%</span>
              </div>
              <input
                type="range"
                min={s.min}
                max={s.max}
                value={sliders[s.key]}
                onChange={(e) => setSliders((prev) => ({ ...prev, [s.key]: Number(e.target.value) }))}
                className="w-full accent-sustaina-green"
              />
            </div>
          ))}
          <button
            onClick={() => setSliders(DEFAULT_SLIDERS)}
            className="rounded-md border border-graphite-600 px-4 py-2 text-sm text-earth-300 hover:border-earth-300/40"
          >
            Reset to current trajectory
          </button>
        </div>

        <div className="panel rounded-lg p-6">
          {result && (
            <>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <p className="text-xs uppercase tracking-widest text-earth-300/60">Today</p>
                  <p className="text-5xl font-extrabold tabular-nums">
                    <AnimatedNumber value={result.baseline_sustainability} />
                  </p>
                  <p className="text-xs text-earth-300/60">Sustainability</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-widest text-earth-300/60">Projected</p>
                  <p
                    className={`text-5xl font-extrabold tabular-nums ${
                      result.projected_sustainability < result.baseline_sustainability ? "text-sustaina-red" : "text-sustaina-green"
                    }`}
                  >
                    <AnimatedNumber value={result.projected_sustainability} />
                  </p>
                  <p className="text-xs text-earth-300/60">Sustainability</p>
                </div>
              </div>

              <div className="mt-6 flex items-center gap-3">
                <span className="text-sm text-earth-300/70">Projected risk:</span>
                <RiskBadge level={result.risk_level} score={result.projected_risk} />
              </div>

              <p className="mt-4 text-sm leading-relaxed text-earth-200/90">{result.explanation}</p>

              <div className="mt-6 space-y-2">
                {Object.entries(result.factors).map(([k, v]) => (
                  <div key={k} className="flex items-center gap-3">
                    <span className="w-44 text-xs capitalize text-earth-300/70">{k.replace(/_/g, " ")}</span>
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-graphite-700">
                      <div className="h-full rounded-full bg-sustaina-amber transition-all duration-500" style={{ width: `${v}%` }} />
                    </div>
                    <span className="w-8 text-right text-xs tabular-nums text-earth-300/70">{Math.round(v)}</span>
                  </div>
                ))}
              </div>
            </>
          )}
          {loading && !result && <p className="text-sm text-earth-300/60">Simulating…</p>}
        </div>
      </div>
    </div>
  );
}

export default function ScenariosPage() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center bg-graphite-950 text-earth-300">Loading…</div>}>
      <ScenariosInner />
    </Suspense>
  );
}
