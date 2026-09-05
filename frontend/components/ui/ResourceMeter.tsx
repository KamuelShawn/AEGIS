export function ResourceMeter({ label, pct, sublabel }: { label: string; pct: number; sublabel?: string }) {
  const clamped = Math.max(0, Math.min(100, pct));
  const color = clamped < 70 ? "bg-sustaina-green" : clamped < 100 ? "bg-sustaina-amber" : "bg-sustaina-red";
  return (
    <div>
      <div className="flex items-baseline justify-between mb-1">
        <span className="text-xs uppercase tracking-wide text-earth-300/70">{label}</span>
        <span className="text-sm font-semibold tabular-nums">{clamped.toFixed(0)}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-graphite-700 overflow-hidden">
        <div
          className={`h-full rounded-full ${color} transition-all duration-700 ease-out`}
          style={{ width: `${Math.min(100, clamped)}%` }}
        />
      </div>
      {sublabel && <p className="text-xs text-earth-300/60 mt-1">{sublabel}</p>}
    </div>
  );
}
