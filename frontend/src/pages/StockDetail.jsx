import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { BookmarkPlus, BookmarkCheck, ArrowLeft, RefreshCw } from "lucide-react";
import { api } from "../api";
import { displayTicker } from "../utils/ticker";
import OverviewCard from "../components/OverviewCard";
import ScoreCard from "../components/ScoreCard";
import PriceChart from "../components/PriceChart";
import TechnicalsCard from "../components/TechnicalsCard";
import NewsCard from "../components/NewsCard";
import AiSummary from "../components/AiSummary";

export default function StockDetail() {
  const { ticker: rawTicker } = useParams();
  const ticker = decodeURIComponent(rawTicker);
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [watchlistLoading, setWatchlistLoading] = useState(false);

  const load = async (withAi = true) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getStock(ticker, withAi);
      setData(result);
      const wl = await api.getWatchlist();
      setInWatchlist(wl.some((i) => i.ticker === ticker.toUpperCase()));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [ticker]);

  const toggleWatchlist = async () => {
    setWatchlistLoading(true);
    try {
      if (inWatchlist) {
        await api.removeFromWatchlist(ticker);
        setInWatchlist(false);
      } else {
        await api.addToWatchlist(ticker);
        setInWatchlist(true);
      }
    } catch {
    } finally {
      setWatchlistLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <RefreshCw size={24} className="text-accent animate-spin" />
        <p className="text-slate-400 text-sm">Analyzing {displayTicker(ticker)}…</p>
        <p className="text-slate-600 text-xs">Fetching market data & generating AI insights</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <p className="text-sell text-sm">{error}</p>
        <button onClick={() => load(false)} className="text-accent text-sm underline">Try without AI</button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-5">
      <div className="flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1.5 text-slate-400 hover:text-slate-200 text-sm transition">
          <ArrowLeft size={16} />
          Back
        </button>
        <div className="flex items-center gap-3">
          <span className="text-slate-500 text-sm">{displayTicker(data?.ticker ?? ticker)}</span>
          <button
            onClick={toggleWatchlist}
            disabled={watchlistLoading}
            className={`flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border transition ${
              inWatchlist
                ? "border-accent text-accent hover:bg-accent/10"
                : "border-border text-slate-400 hover:text-slate-200 hover:border-slate-400"
            }`}
          >
            {inWatchlist ? <BookmarkCheck size={15} /> : <BookmarkPlus size={15} />}
            {inWatchlist ? "Watching" : "Add to Watchlist"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <OverviewCard overview={data?.overview} />
          <PriceChart ticker={ticker} initialData={data?.price_history} />
          <TechnicalsCard technicals={data?.technicals} price={data?.overview?.price} />
        </div>
        <div className="space-y-4">
          <ScoreCard score={data?.score} />
          <NewsCard news={data?.news} />
        </div>
      </div>

      {data?.ai_summary && <AiSummary summary={data.ai_summary} provider={data.ai_provider} />}
    </div>
  );
}
