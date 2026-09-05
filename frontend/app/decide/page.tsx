"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type RoutesResponse, type SitesResponse } from "@/lib/api";

const DEFAULT_WEIGHTS = { economic_cost: 25, environmental_impact: 30, social_impact: 25, connectivity_benefit: 20 };

export default function DecidePage() {
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [routes, setRoutes] = useState<RoutesResponse | null>(null);
  const [sites, setSites] = useState<SitesResponse | null>(null);
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);

  useEffect(() => {
    api.routes("bandipur-corridor", weights).then((r) => {
      setRoutes(r);
      setSelectedRouteId(r.recommended_route_id);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weights]);

  useEffect(() => {
    api.sites("chamarajanagar-industrial").then(setSites);
  }, []);

  const recommendedRoute = routes?.routes.find((r) => r.id === routes.recommended_route_id);
  const recommendedSite = sites?.sites.find((s) => s.id === sites.recommended_site_id);

  return (
    <div className="min-h-screen bg-graphite-950 px-6 py-8 md:px-16">
      <Link href="/explore" className="text-xs text-earth-300/60 hover:text-earth-100">
        ← Back to Explore
      </Link>
      <h1 className="mt-1 text-3xl font-bold">The Sustainable Path</h1>
      <p className="max-w-2xl text-sm text-earth-300/70">
        Every candidate below is scored on the same weighted criteria used across the platform — cost, environmental
        impact, social impact, and connectivity. Adjust the weights and watch the recommendation update in real time.
      </p>

      {/* ROUTE OPTIMIZATION */}
      <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-[280px_1fr]">
        <div className="panel space-y-5 rounded-lg p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-earth-300/70">Route Weights</h2>
          {(Object.keys(weights) as (keyof typeof weights)[]).map((key) => (
            <div key={key}>
              <div className="mb-1 flex justify-between text-xs">
                <span className="capitalize text-earth-200">{key.replace(/_/g, " ")}</span>
                <span className="tabular-nums text-earth-300/70">{weights[key]}</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={weights[key]}
                onChange={(e) => setWeights((prev) => ({ ...prev, [key]: Number(e.target.value) }))}
                className="w-full accent-sustaina-green"
              />
            </div>
          ))}
        </div>

        <div className="panel rounded-lg p-5">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-earth-300/70">
            Candidate Routes — {routes?.origin} → {routes?.destination}
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-graphite-700 text-left text-xs uppercase tracking-wide text-earth-300/60">
                  <th className="py-2 pr-4">Route</th>
                  <th className="py-2 pr-4">Cost (₹ Cr)</th>
                  <th className="py-2 pr-4">Environment</th>
                  <th className="py-2 pr-4">Social</th>
                  <th className="py-2 pr-4">Connectivity</th>
                  <th className="py-2 pr-4">Overall</th>
                </tr>
              </thead>
              <tbody>
                {routes?.routes.map((r) => (
                  <tr
                    key={r.id}
                    onClick={() => setSelectedRouteId(r.id)}
                    className={`cursor-pointer border-b border-graphite-800 transition ${
                      selectedRouteId === r.id ? "bg-graphite-800" : "hover:bg-graphite-800/50"
                    }`}
                  >
                    <td className="py-2 pr-4 font-medium">
                      {r.name} {r.id === routes.recommended_route_id && <span className="ml-1 text-sustaina-green">★</span>}
                    </td>
                    <td className="py-2 pr-4 tabular-nums">{r.construction_cost_cr}</td>
                    <td className="py-2 pr-4 tabular-nums">{r.environmental_impact}</td>
                    <td className="py-2 pr-4 tabular-nums">{r.social_impact}</td>
                    <td className="py-2 pr-4 tabular-nums">{r.connectivity_benefit}</td>
                    <td className="py-2 pr-4 font-semibold tabular-nums">{r.weighted_score.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {recommendedRoute && (
            <div className="mt-4 rounded-md bg-sustaina-green-dim/40 p-4 text-sm">
              <p className="mb-1 font-semibold text-sustaina-green">Recommended: {recommendedRoute.name}</p>
              <p className="text-earth-200/90">{recommendedRoute.explanation}</p>
              {recommendedRoute.affected_ecosystems.length > 0 && (
                <p className="mt-1 text-xs text-earth-300/60">Affects: {recommendedRoute.affected_ecosystems.join(", ")}</p>
              )}
            </div>
          )}
        </div>
      </section>

      {/* SITE SUITABILITY */}
      <section className="mt-10">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-earth-300/70">Industrial Site Suitability</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {sites?.sites.map((s) => (
            <div key={s.id} className={`panel rounded-lg p-4 ${s.id === sites.recommended_site_id ? "ring-1 ring-sustaina-green" : ""}`}>
              <div className="mb-2 flex items-center justify-between">
                <h3 className="font-semibold">{s.name}</h3>
                {s.id === sites.recommended_site_id && <span className="text-sustaina-green">★</span>}
              </div>
              <p className="mb-2 text-3xl font-bold tabular-nums">{s.suitability_score.toFixed(0)}</p>
              <p className="mb-2 text-xs uppercase tracking-wide text-earth-300/60">{s.classification.replace(/_/g, " ")}</p>
              <p className="text-sm text-earth-200/80">{s.explanation}</p>
            </div>
          ))}
        </div>
      </section>

      {/* FINAL DECISION SUMMARY */}
      {recommendedRoute && recommendedSite && (
        <section className="mt-10 panel rounded-lg p-6">
          <h2 className="mb-4 text-xl font-bold">Decision Summary</h2>
          <div className="grid grid-cols-2 gap-6 text-sm md:grid-cols-4">
            <div>
              <p className="text-earth-300/60">Route</p>
              <p className="font-semibold">{recommendedRoute.name}</p>
            </div>
            <div>
              <p className="text-earth-300/60">Industrial Site</p>
              <p className="font-semibold">{recommendedSite.name}</p>
            </div>
            <div>
              <p className="text-earth-300/60">Est. Route Cost</p>
              <p className="font-semibold">₹{recommendedRoute.construction_cost_cr} Cr</p>
            </div>
            <div>
              <p className="text-earth-300/60">Site Suitability</p>
              <p className="font-semibold">{recommendedSite.suitability_score.toFixed(0)}/100</p>
            </div>
          </div>
          <p className="mt-6 text-lg font-semibold text-sustaina-green">
            Development is not the enemy. Uninformed development is. There is another path.
          </p>
        </section>
      )}
    </div>
  );
}
