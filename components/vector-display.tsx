"use client";

interface VectorBarProps {
  label: string;
  value: number;
  color: string;
  maxValue?: number;
}

export function VectorBar({
  label,
  value,
  color,
  maxValue = 1,
}: VectorBarProps) {
  const pct = Math.min((value / maxValue) * 100, 100);

  return (
    <div className="flex items-center gap-3">
      <span className="text-[13px] font-medium text-label-secondary w-20 text-right shrink-0">
        {label}
      </span>
      <div className="flex-1 h-2.5 bg-surface-secondary rounded-full overflow-hidden">
        <div
          className="vector-bar h-full rounded-full"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-[13px] font-mono text-label-tertiary w-12 text-right tabular-nums">
        {value.toFixed(3)}
      </span>
    </div>
  );
}

interface VectorCardProps {
  word: string;
  structure: number;
  force: number;
  flow: number;
  density?: number;
  compact?: boolean;
}

export function VectorCard({
  word,
  structure,
  force,
  flow,
  density,
  compact = false,
}: VectorCardProps) {
  return (
    <div className={`card ${compact ? "p-4" : "p-5"}`}>
      <div className="flex items-baseline justify-between mb-3">
        <h3 className="text-[17px] font-semibold tracking-tight">{word}</h3>
        {density !== undefined && (
          <span className="text-[13px] font-mono text-label-quaternary">
            dens = {density.toFixed(3)}
          </span>
        )}
      </div>
      <div className="flex flex-col gap-2">
        <VectorBar label="Structure" value={structure} color="#007AFF" />
        <VectorBar label="Force" value={force} color="#FF9500" />
        <VectorBar label="Flow" value={flow} color="#34C759" />
      </div>
    </div>
  );
}

interface VerdictBadgeProps {
  verdict: "congruent" | "suspect" | "conflict";
  di: number;
}

export function VerdictBadge({ verdict, di }: VerdictBadgeProps) {
  const classes = {
    congruent: "verdict-congruent",
    suspect: "verdict-suspect",
    conflict: "verdict-conflict",
  };

  const labels = {
    congruent: "Congruent",
    suspect: "Suspect",
    conflict: "Conflict",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-[13px] font-semibold ${classes[verdict]}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {labels[verdict]}
      <span className="font-mono font-normal ml-1">
        DI = {di.toFixed(4)}
      </span>
    </span>
  );
}
