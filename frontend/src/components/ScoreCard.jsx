import SignalBadge from "./SignalBadge";

const TOOLTIPS = {
  Valuation:
    "P/E ratio · dividend yield · where price sits in its 52-week range. Weight: 30%",
  Technical:
    "RSI (overbought / oversold) · MACD vs signal line · price above/below SMA-20, SMA-50, SMA-200. Weight: 30%",
  Momentum:
    "Today's price change % · volume vs 3-month average (amplified by direction). Weight: 20%",
  Fundamental:
    "Trailing EPS (earnings per share) · company size by market cap. Weight: 20%",
};

function InfoTooltip({ text }) {
  return (
    <span className="relative group ml-1.5 cursor-default">
      <span className="inline-flex items-center justify-center w-3.5 h-3.5 rounded-full bg-slate-700 text-slate-400 text-[9px] font-bold select-none leading-none">
        i
      </span>
      <span className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2.5 w-56 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2.5 text-xs text-slate-300 leading-relaxed opacity-0 group-hover:opacity-100 transition-opacity duration-150 z-50 shadow-2xl">
        {text}
        <span className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-700" />
      </span>
    </span>
  );
}

function AiTooltip({ text }) {
  return (
    <span className="relative group ml-1 cursor-default">
      <span className="inline-flex items-center justify-center w-3.5 h-3.5 rounded-full bg-indigo-900/60 text-indigo-400 text-[8px] font-bold select-none leading-none border border-indigo-700/50">
        ✦
      </span>
      <span className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2.5 w-56 rounded-lg bg-slate-800 border border-indigo-700/40 px-3 py-2.5 text-xs text-slate-200 leading-relaxed opacity-0 group-hover:opacity-100 transition-opacity duration-150 z-50 shadow-2xl">
        <span className="block text-[10px] text-indigo-400 font-semibold mb-1 uppercase tracking-wide">AI insight</span>
        {text}
        <span className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-indigo-700/40" />
      </span>
    </span>
  );
}

function ScoreBar({ label, value, aiExplanation }) {
  const color =
    value >= 65 ? "bg-buy" : value <= 40 ? "bg-sell" : "bg-hold";
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span className="flex items-center">
          {label}
          <InfoTooltip text={TOOLTIPS[label]} />
          {aiExplanation && <AiTooltip text={aiExplanation} />}
        </span>
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

export default function ScoreCard({ score, explanations }) {
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
        <ScoreBar label="Valuation"   value={score.valuation}   aiExplanation={explanations?.valuation} />
        <ScoreBar label="Technical"   value={score.technical}   aiExplanation={explanations?.technical} />
        <ScoreBar label="Momentum"    value={score.momentum}    aiExplanation={explanations?.momentum} />
        <ScoreBar label="Fundamental" value={score.fundamental} aiExplanation={explanations?.fundamental} />
      </div>
    </div>
  );
}
