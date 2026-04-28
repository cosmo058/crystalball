import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Trash2, TrendingUp, TrendingDown, RefreshCw } from "lucide-react";
import { api } from "../api";

export default function Watchlist() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.getWatchlistSummary();
      setItems(data);
    } catch {
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const remove = async (ticker, e) => {
    e.stopPropagation();
    await api.removeFromWatchlist(ticker);
    setItems((prev) => prev.filter((i) => i.ticker !== ticker));
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-100">Watchlist</h1>
        <button onClick={load} className="text-slate-400 hover:text-slate-200 transition">
          <RefreshCw size={16} />
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <RefreshCw size={20} className="text-accent animate-spin" />
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-16 space-y-3">
          <p className="text-slate-400">Your watchlist is empty.</p>
          <button onClick={() => navigate("/")} className="text-accent text-sm underline">
            Search for a stock
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item) => {
            const up = item.change_pct == null ? null : item.change_pct >= 0;
            return (
              <div
                key={item.ticker}
                onClick={() => navigate(`/stock/${item.ticker}`)}
                className="flex items-center justify-between bg-card border border-border rounded-xl px-4 py-4 hover:border-accent/40 cursor-pointer transition group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center text-accent text-xs font-bold">
                    {item.ticker.slice(0, 2)}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-200">{item.ticker}</p>
                    <p className="text-xs text-slate-500 line-clamp-1">{item.name}</p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm font-semibold text-slate-200">
                      {item.price != null ? `$${item.price.toFixed(2)}` : "—"}
                    </p>
                    {item.change_pct != null && (
                      <p className={`text-xs flex items-center justify-end gap-0.5 ${up ? "text-buy" : "text-sell"}`}>
                        {up ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
                        {item.change_pct >= 0 ? "+" : ""}{item.change_pct.toFixed(2)}%
                      </p>
                    )}
                  </div>
                  <button
                    onClick={(e) => remove(item.ticker, e)}
                    className="text-slate-600 hover:text-sell transition opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
