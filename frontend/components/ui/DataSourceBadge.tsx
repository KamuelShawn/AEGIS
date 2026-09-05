const STYLES: Record<string, string> = {
  REAL: "bg-sustaina-green-dim text-sustaina-green",
  CACHED: "bg-sustaina-blue-dim text-sustaina-blue",
  DERIVED: "bg-graphite-700 text-earth-200",
  MODELLED: "bg-graphite-700 text-earth-200",
  SIMULATED: "bg-sustaina-amber/20 text-sustaina-amber",
  DEMO: "bg-sustaina-amber/20 text-sustaina-amber",
};

export function DataSourceBadge({ status, name }: { status: string; name?: string }) {
  const cls = STYLES[status] ?? "bg-graphite-700 text-earth-200";
  return (
    <span className={`badge ${cls}`} title={name}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}
