import { AnimatedNumber } from "./AnimatedNumber";

interface Factor {
  name: string;
  score: number;
}

export function SustainabilityScore({ overall, factors, explanation }: { overall: number; factors: Factor[]; explanation: string }) {
  return (
    <div>
      <div className="flex items-end gap-3">
        <span className="text-6xl font-extrabold tabular-nums leading-none">
          <AnimatedNumber value={overall} />
        </span>
        <div className="pb-1">
          <p className="text-xs uppercase tracking-widest text-earth-300/60">Sustainability Index</p>
          <p className="text-sm text-earth-300/80">out of 100</p>
        </div>
      </div>
      <div className="mt-4 space-y-2">
        {factors.map((f) => (
          <div key={f.name} className="flex items-center gap-3">
            <span className="w-28 text-xs capitalize text-earth-300/70">{f.name}</span>
            <div className="flex-1 h-1.5 rounded-full bg-graphite-700 overflow-hidden">
              <div
                className="h-full rounded-full bg-sustaina-green transition-all duration-700"
                style={{ width: `${Math.max(0, Math.min(100, f.score))}%` }}
              />
            </div>
            <span className="w-8 text-right text-xs tabular-nums text-earth-300/70">{Math.round(f.score)}</span>
          </div>
        ))}
      </div>
      <p className="mt-3 text-sm text-earth-200/90 leading-relaxed">{explanation}</p>
    </div>
  );
}
