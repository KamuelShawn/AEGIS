"use client";

import maplibregl, { Map as MapLibreMap, Marker } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef } from "react";
import type { Region } from "@/lib/api";

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

const DARK_STYLE = MAPBOX_TOKEN
  ? `https://api.mapbox.com/styles/v1/mapbox/dark-v11?access_token=${MAPBOX_TOKEN}`
  : "https://demotiles.maplibre.org/style.json";

const RISK_COLORS: Record<string, string> = {
  SAFE: "#4c8c5a",
  WARNING: "#c98a34",
  CRITICAL: "#b1443a",
  SEVERE: "#7a241d",
};

export function MapView({
  regions,
  selectedId,
  riskByRegion,
  onSelect,
}: {
  regions: Region[];
  selectedId: string | null;
  riskByRegion?: Record<string, string>;
  onSelect: (id: string) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Map<string, Marker>>(new Map());

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: DARK_STYLE,
      center: [80.5, 21.5],
      zoom: 3.6,
      pitch: 0,
      attributionControl: false,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current.clear();

    regions.forEach((region) => {
      const isSelected = region.id === selectedId;
      const riskLevel = riskByRegion?.[region.id];
      const color = riskLevel ? RISK_COLORS[riskLevel] ?? "#4a544c" : region.case_study ? "#c98a34" : "#4a544c";

      const el = document.createElement("button");
      el.setAttribute("aria-label", region.name);
      el.style.width = isSelected ? "18px" : "12px";
      el.style.height = isSelected ? "18px" : "12px";
      el.style.borderRadius = "999px";
      el.style.background = color;
      el.style.border = isSelected ? "2px solid #f4f2ec" : "1px solid rgba(244,242,236,0.5)";
      el.style.cursor = "pointer";
      el.style.boxShadow = isSelected ? `0 0 0 6px ${color}33` : "none";
      el.style.transition = "all 200ms ease";
      el.onclick = () => onSelect(region.id);

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat(region.center)
        .addTo(map);
      markersRef.current.set(region.id, marker);
    });
  }, [regions, selectedId, riskByRegion, onSelect]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !selectedId) return;
    const region = regions.find((r) => r.id === selectedId);
    if (!region) return;
    map.flyTo({ center: region.center, zoom: region.zoom, duration: 1400, essential: true });
  }, [selectedId, regions]);

  return <div ref={containerRef} className="h-full w-full" />;
}
