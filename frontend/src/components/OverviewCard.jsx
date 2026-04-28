function Stat({ label, value }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-slate-500">{label}</span>
      <span className="text-sm text-slate-200 font-medium">{value ?? "—"}</span>
    </div>
  );
}

function fmt(num, decimals = 2) {
  if (num == null) return null;
  if (num >= 1e12) return `$${(num / 1e12).toFixed(1)}T`;
  if (num >= 1e9) return `$${(num / 1e9).toFixed(1)}B`;
  if (num >= 1e6) return `$${(num / 1e6).toFixed(1)}M`;
  return `$${num.toFixed(decimals)}`;
}

export default function OverviewCard({ overview }) {
  if (!overview) return null;
  const changeColor = overview.change_pct >= 0 ? "text-buy" : "text-sell";

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-4">
      <div>
        <div className="flex items-start justify-between gap-2">
          <div>
            <h2 className="text-lg font-bold text-slate-100">{overview.name}</h2>
            <p className="text-slate-500 text-sm">{overview.sector} · {overview.industry}</p>
          </div>
          <div className="text-right shrink-0">
            <p className="text-2xl font-bold text-slate-100">${overview.price?.toFixed(2)}</p>
            <p className={`text-sm font-medium ${changeColor}`}>
              {overview.change >= 0 ? "+" : ""}{overview.change?.toFixed(2)} ({overview.change_pct >= 0 ? "+" : ""}{overview.change_pct?.toFixed(2)}%)
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 pt-1">
        <Stat label="Market Cap" value={fmt(overview.market_cap)} />
        <Stat label="P/E Ratio" value={overview.pe_ratio?.toFixed(2)} />
        <Stat label="EPS (TTM)" value={overview.eps != null ? `$${overview.eps?.toFixed(2)}` : null} />
        <Stat label="Dividend Yield" value={overview.dividend_yield != null ? `${overview.dividend_yield.toFixed(2)}%` : null} />
        <Stat label="52w High" value={overview.week_52_high != null ? `$${overview.week_52_high?.toFixed(2)}` : null} />
        <Stat label="52w Low" value={overview.week_52_low != null ? `$${overview.week_52_low?.toFixed(2)}` : null} />
        <Stat label="Volume" value={overview.volume?.toLocaleString()} />
        <Stat label="Avg Volume" value={overview.avg_volume?.toLocaleString()} />
      </div>
    </div>
  );
}
