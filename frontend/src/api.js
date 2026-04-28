const BASE = import.meta.env.VITE_API_URL ?? "";

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  searchStock: (q) => req(`/api/stocks/search?q=${encodeURIComponent(q)}`),
  getStock: (ticker, ai = true) => req(`/api/stocks/${ticker}?ai=${ai}`),
  getHistory: (ticker, period = "6mo") => req(`/api/stocks/${ticker}/history?period=${period}`),
  getWatchlist: () => req("/api/watchlist/"),
  getWatchlistSummary: () => req("/api/watchlist/summary"),
  addToWatchlist: (ticker) =>
    req("/api/watchlist/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ticker }) }),
  removeFromWatchlist: (ticker) => req(`/api/watchlist/${ticker}`, { method: "DELETE" }),
  health: () => req("/api/health"),
};
