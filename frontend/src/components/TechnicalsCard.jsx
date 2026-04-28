function Stat({ label, value, hint }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-slate-500">{label}</span>
      <span className="text-sm font-medium text-slate-200">{value ?? "—"}</span>
      {hint && <span className="text-xs text-slate-600">{hint}</span>}
    </div>
  );
}

function RsiGauge({ rsi }) {
  if (rsi == null) return null;
  const zone = rsi < 30 ? "Oversold" : rsi > 70 ? "Overbought" : "Neutral";
  const color = rsi < 30 ? "text-buy" : rsi > 70 ? "text-sell" : "text-hold";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-surface rounded-full relative overflow-hidden">
        <div
          className="h-full rounded-full bg-accent transition-all duration-500"
          style={{ width: `${rsi}%` }}
        />
      </div>
      <span className={`text-xs font-medium ${color}`}>{zone}</span>
    </div>
  );
}

export default function TechnicalsCard({ technicals, price }) {
  if (!technicals) return null;
  const { rsi, macd, macd_signal, sma_20, sma_50, sma_200, bollinger_upper, bollinger_lower } = technicals;

  const macdBull = macd != null && macd_signal != null && macd > macd_signal;

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-4">
      <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
        Technical Indicators
      </h3>

      <div>
        <div className="flex justify-between text-xs text-slate-400 mb-1.5">
          <span>RSI (14)</span>
          <span className="text-slate-200">{rsi?.toFixed(1) ?? "—"}</span>
        </div>
        <RsiGauge rsi={rsi} />
      </div>

      <div className="grid grid-cols-2 gap-3 pt-1">
        <Stat
          label="MACD"
          value={macd?.toFixed(3)}
          hint={macd != null && macd_signal != null ? (macdBull ? "Bullish crossover" : "Bearish crossover") : null}
        />
        <Stat label="MACD Signal" value={macd_signal?.toFixed(3)} />
        <Stat
          label="SMA 20"
          value={sma_20?.toFixed(2)}
          hint={sma_20 && price ? (price > sma_20 ? "Price above" : "Price below") : null}
        />
        <Stat
          label="SMA 50"
          value={sma_50?.toFixed(2)}
          hint={sma_50 && price ? (price > sma_50 ? "Price above" : "Price below") : null}
        />
        <Stat
          label="SMA 200"
          value={sma_200?.toFixed(2)}
          hint={sma_200 && price ? (price > sma_200 ? "Price above" : "Price below") : null}
        />
        <Stat label="BB Upper" value={bollinger_upper?.toFixed(2)} />
        <Stat label="BB Lower" value={bollinger_lower?.toFixed(2)} />
      </div>
    </div>
  );
}
