"use client";

import { Area, AreaChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ForestHistory } from "@/lib/api";

export function ForestChart({ history }: { history: ForestHistory }) {
  const observed = history.observations.map((o) => ({ year: o.year, area: o.area }));
  const forecast = history.forecast.map((f) => ({ year: f.year, low: f.low, mid: f.mid, high: f.high }));
  const data = [
    ...observed.map((o) => ({ year: o.year, area: o.area, low: undefined, high: undefined })),
    ...forecast.map((f) => ({ year: f.year, area: undefined, low: f.low, high: f.high })),
  ];

  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="forestFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#4c8c5a" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#4c8c5a" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="forecastFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#c98a34" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#c98a34" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#262c28" />
        <XAxis dataKey="year" stroke="#4a544c" fontSize={11} />
        <YAxis stroke="#4a544c" fontSize={11} width={50} />
        <Tooltip
          contentStyle={{ background: "#121513", border: "1px solid #262c28", fontSize: 12 }}
          labelStyle={{ color: "#ece9e2" }}
        />
        {history.critical_threshold_area && (
          <ReferenceLine
            y={history.critical_threshold_area}
            stroke="#b1443a"
            strokeDasharray="4 4"
            label={{ value: "Critical threshold", fill: "#b1443a", fontSize: 10, position: "insideTopLeft" }}
          />
        )}
        <Area type="monotone" dataKey="area" stroke="#4c8c5a" fill="url(#forestFill)" strokeWidth={2} connectNulls={false} />
        <Area type="monotone" dataKey="high" stroke="none" fill="url(#forecastFill)" connectNulls />
        <Area type="monotone" dataKey="low" stroke="#c98a34" strokeDasharray="4 4" fill="none" connectNulls />
      </AreaChart>
    </ResponsiveContainer>
  );
}
