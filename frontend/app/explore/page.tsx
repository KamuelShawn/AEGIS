"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { MapView } from "@/components/map/MapView";
import { RegionPanel } from "@/components/panels/RegionPanel";
import { DataSourceBadge } from "@/components/ui/DataSourceBadge";
import { api, type Region, type SourceInfo } from "@/lib/api";

function ExploreInner() {
  const searchParams = useSearchParams();
  const [states, setStates] = useState<Region[]>([]);
  const [viewState, setViewState] = useState<Region | null>(null); // non-null when drilled into a state's districts
  const [displayedRegions, setDisplayedRegions] = useState<Region[]>([]);
  const [regionSource, setRegionSource] = useState<SourceInfo | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api.regions().then(async (r) => {
      if (cancelled) return;
      setStates(r.regions);
      setRegionSource(r.source);

      const requested = searchParams.get("region");
      if (requested && requested.includes("__")) {
        const stateSlug = requested.split("__")[0];
        const state = r.regions.find((s) => s.id === stateSlug);
        if (state) {
          const districts = await api.regions(state.id);
          if (cancelled) return;
          setViewState(state);
          setDisplayedRegions(districts.regions);
          setRegionSource(districts.source);
          setSelectedId(requested);
          setLoading(false);
          return;
        }
      }

      setDisplayedRegions(r.regions);
      const fallback = r.regions.find((s) => s.id === "karnataka") ?? r.regions[0];
      const initial = requested && r.regions.some((s) => s.id === requested) ? requested : fallback?.id ?? null;
      setSelectedId(initial);
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectedRegion = displayedRegions.find((r) => r.id === selectedId) ?? viewState ?? null;

  const enterState = async (state: Region) => {
    setLoading(true);
    const districts = await api.regions(state.id);
    setViewState(state);
    setDisplayedRegions(districts.regions);
    setRegionSource(districts.source);
    setSelectedId(districts.regions[0]?.id ?? state.id);
    setLoading(false);
  };

  const backToStates = async () => {
    setViewState(null);
    setDisplayedRegions(states);
    const fresh = await api.regions();
    setRegionSource(fresh.source);
    setSelectedId(states.find((s) => s.id === "karnataka")?.id ?? states[0]?.id ?? null);
  };

  return (
    <div className="flex h-screen w-screen bg-graphite-950">
      <div className="relative flex-1">
        <MapView regions={displayedRegions} selectedId={selectedId} onSelect={setSelectedId} />

        <div className="pointer-events-none absolute left-4 top-4 flex items-center gap-3">
          <Link href="/" className="pointer-events-auto text-sm font-bold tracking-wide text-earth-100 hover:text-sustaina-green">
            SUSTAINA
          </Link>
          <span className="text-xs text-earth-300/50">
            {viewState ? `India / ${viewState.name} / Districts` : "India / States"}
          </span>
          {regionSource && <DataSourceBadge status={regionSource.status} name={regionSource.name} />}
        </div>

        <div className="pointer-events-none absolute bottom-4 left-4 flex items-center gap-2">
          {viewState ? (
            <button
              onClick={backToStates}
              className="pointer-events-auto rounded-md bg-graphite-800/80 px-3 py-1.5 text-xs font-medium text-earth-200 hover:bg-graphite-700"
            >
              ← Back to all states
            </button>
          ) : (
            <select
              className="pointer-events-auto rounded-md bg-graphite-800/90 px-3 py-1.5 text-xs font-medium text-earth-200"
              value=""
              onChange={(e) => {
                const state = states.find((s) => s.id === e.target.value);
                if (state) enterState(state);
              }}
            >
              <option value="" disabled>
                Browse a state&apos;s districts…
              </option>
              {states.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          )}
          {loading && <span className="text-xs text-earth-300/60">Loading…</span>}
        </div>
      </div>

      <aside className="w-[420px] shrink-0 border-l border-graphite-700 bg-graphite-900">
        {selectedRegion ? (
          <RegionPanel region={selectedRegion} />
        ) : (
          <div className="flex h-full items-center justify-center p-6 text-sm text-earth-300/60">
            Select any state or district on the map to begin — the whole of India is browsable, not just one region.
          </div>
        )}
      </aside>
    </div>
  );
}

export default function ExplorePage() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center bg-graphite-950 text-earth-300">Loading…</div>}>
      <ExploreInner />
    </Suspense>
  );
}
