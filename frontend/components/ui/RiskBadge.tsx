const LEVEL_STYLES: Record<string, { cls: string; icon: string }> = {
  SAFE: { cls: "bg-sustaina-green-dim text-sustaina-green", icon: "●" },
  WARNING: { cls: "bg-sustaina-amber/20 text-sustaina-amber", icon: "▲" },
  CRITICAL: { cls: "bg-sustaina-red/20 text-sustaina-red", icon: "▲" },
  SEVERE: { cls: "bg-sustaina-red/30 text-sustaina-red", icon: "■" },
};

export function RiskBadge({ level, score }: { level: string; score?: number }) {
  const style = LEVEL_STYLES[level] ?? LEVEL_STYLES.WARNING;
  return (
    <span className={`badge ${style.cls}`}>
      <span aria-hidden>{style.icon}</span>
      {level}
      {typeof score === "number" && <span className="opacity-70">· {Math.round(score)}</span>}
    </span>
  );
}
