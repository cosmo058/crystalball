import SignalBadge from "./SignalBadge";

function ScoreBar({ label, value }) {
  const color =
    value >= 65 ? "bg-buy" : value <= 40 ? "bg-sell" : "bg-hold";
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span className="text-slate-200">{value}</span>
      </div>
      <div className="h-1.5 bg-surface rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

export default function ScoreCard({ score }) {
  if (!score) return null;
  const ringColor =
    score.total >= 65 ? "#10b981" : score.total <= 40 ? "#ef4444" : "#f59e0b";
  const circumference = 2 * Math.PI * 38;
  const offset = circumference - (score.total / 100) * circumference;

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-4">
      <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
        Crystalball Score
      </h3>

      <div className="flex items-center gap-5">
        <div className="relative shrink-0">
          <svg width="90" height="90" className="-rotate-90">
            <circle cx="45" cy="45" r="38" fill="none" stroke="#2a2d3a" strokeWidth="6" />
            <circle
              cx="45" cy="45" r="38" fill="none"
              stroke={ringColor} strokeWidth="6"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className="transition-all duration-700"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xl font-bold" style={{ color: ringColor }}>
              {score.total}
            </span>
          </div>
        </div>

        <div className="space-y-1">
          <SignalBadge signal={score.signal} confidence={score.confidence} size="lg" />
          <p className="text-xs text-slate-500 mt-1">out of 100</p>
        </div>
      </div>

      <div className="space-y-2 pt-1">
        <ScoreBar label="Valuation" value={score.valuation} />
        <ScoreBar label="Technical" value={score.technical} />
        <ScoreBar label="Momentum" value={score.momentum} />
        <ScoreBar label="Fundamental" value={score.fundamental} />
      </div>
    </div>
  );
}
