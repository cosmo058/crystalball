import { useState } from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api } from "../api";

const PERIODS = ["1mo", "3mo", "6mo", "1y", "2y"];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-card border border-border rounded-lg px-3 py-2 text-sm shadow-xl">
      <p className="text-slate-400 text-xs mb-1">{label}</p>
      <p className="text-slate-100 font-semibold">${payload[0].value?.toFixed(2)}</p>
    </div>
  );
};

export default function PriceChart({ ticker, initialData }) {
  const [data, setData] = useState(initialData || []);
  const [period, setPeriod] = useState("6mo");
  const [loading, setLoading] = useState(false);

  const changePeriod = async (p) => {
    if (p === period) return;
    setPeriod(p);
    setLoading(true);
    try {
      const hist = await api.getHistory(ticker, p);
      setData(hist);
    } catch {
    } finally {
      setLoading(false);
    }
  };

  const isUp = data.length >= 2 && data[data.length - 1].close >= data[0].close;
  const color = isUp ? "#10b981" : "#ef4444";

  const chartData = data.map((d) => ({
    date: d.date.slice(5),
    close: d.close,
  }));

  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Price History</h3>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button
              key={p}
              onClick={() => changePeriod(p)}
              className={`text-xs px-2.5 py-1 rounded-md transition ${
                period === p
                  ? "bg-accent text-white"
                  : "text-slate-400 hover:text-slate-200 hover:bg-surface"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="h-52 flex items-center justify-center text-slate-500 text-sm">Loading...</div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: "#64748b" }}
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 11, fill: "#64748b" }}
              axisLine={false}
              tickLine={false}
              domain={["auto", "auto"]}
              tickFormatter={(v) => `$${v}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="close"
              stroke={color}
              strokeWidth={2}
              fill="url(#colorClose)"
              dot={false}
              activeDot={{ r: 4, fill: color }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
