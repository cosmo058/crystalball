import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, BarChart2, Sparkles, Bookmark } from "lucide-react";
import { normalizeTicker } from "../utils/ticker";

const POPULAR = ["AAPL", "TSLA", "NVDA", "MSFT", "SHOP.TO", "RY.TO", "CNQ.TO", "AMD"];

export default function Home() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    const t = normalizeTicker(query);
    if (t) navigate(`/stock/${encodeURIComponent(t)}`);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4 text-center space-y-10">
      <div className="space-y-4">
        <div className="flex items-center justify-center">
          <span className="text-6xl leading-none">🔮</span>
        </div>
        <h1 className="text-5xl font-bold text-slate-100 tracking-tight">
          Crystal<span className="text-accent">ball</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-md">
          AI-powered stock intelligence. Analyze any ticker for signals, technicals, sentiment, and more.
        </p>
      </div>

      <form onSubmit={handleSearch} className="w-full max-w-md space-y-3">
        <div className="relative">
          <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter a ticker (AAPL, TSX:ASCU, SHOP.TO)…"
            className="w-full bg-card border border-border rounded-xl pl-12 pr-4 py-4 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-accent text-base transition"
            autoFocus
          />
        </div>
        <button
          type="submit"
          className="w-full bg-accent hover:bg-accent/90 text-white font-semibold py-3 rounded-xl transition"
        >
          Analyze Stock
        </button>
      </form>

      <div className="space-y-2">
        <p className="text-xs text-slate-600 uppercase tracking-widest">Popular tickers</p>
        <div className="flex flex-wrap justify-center gap-2">
          {POPULAR.map((t) => (
            <button
              key={t}
              onClick={() => navigate(`/stock/${t}`)}
              className="px-3 py-1.5 bg-card border border-border text-slate-400 hover:text-slate-200 hover:border-accent/50 text-sm rounded-lg transition"
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl w-full text-left">
        {[
          { icon: BarChart2, title: "Technical Analysis", desc: "RSI, MACD, Bollinger Bands, and moving averages." },
          { icon: Sparkles, title: "AI Intelligence", desc: "AI-powered narrative summaries, sentiment analysis, and score insights." },
          { icon: Bookmark, title: "Watchlist", desc: "Track your favorite tickers in one place." },
        ].map(({ icon: Icon, title, desc }) => (
          <div key={title} className="bg-card border border-border rounded-xl p-4 space-y-1.5">
            <Icon size={18} className="text-accent" />
            <p className="text-sm font-semibold text-slate-200">{title}</p>
            <p className="text-xs text-slate-500">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
