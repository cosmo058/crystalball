import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { Search, TrendingUp } from "lucide-react";

export default function Navbar() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    const t = query.trim().toUpperCase();
    if (t) {
      navigate(`/stock/${t}`);
      setQuery("");
    }
  };

  return (
    <nav className="sticky top-0 z-50 bg-card border-b border-border px-6 py-3 flex items-center gap-4">
      <Link to="/" className="flex items-center gap-2 text-accent font-bold text-xl shrink-0">
        <TrendingUp size={22} />
        Crystalball
      </Link>

      <form onSubmit={handleSearch} className="flex-1 max-w-md mx-auto">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search ticker (e.g. AAPL, TSLA)..."
            className="w-full bg-surface border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-accent transition"
          />
        </div>
      </form>

      <Link to="/watchlist" className="text-sm text-slate-400 hover:text-slate-200 transition shrink-0">
        Watchlist
      </Link>
    </nav>
  );
}
