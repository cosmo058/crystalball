const EXCHANGE_MAP = {
  TSX: ".TO",
  TSXV: ".V",
  CVE: ".TO",
};

export function normalizeTicker(input) {
  const t = input.trim().toUpperCase();
  if (t.includes(":")) {
    const [prefix, symbol] = t.split(":", 2);
    const suffix = EXCHANGE_MAP[prefix] ?? "";
    return symbol + suffix;
  }
  return t;
}

export function displayTicker(ticker) {
  if (ticker.endsWith(".TO")) return `${ticker.slice(0, -3)} (TSX)`;
  if (ticker.endsWith(".V")) return `${ticker.slice(0, -2)} (TSXV)`;
  if (ticker.endsWith(".AX")) return `${ticker.slice(0, -3)} (ASX)`;
  if (ticker.endsWith(".L")) return `${ticker.slice(0, -2)} (LSE)`;
  return ticker;
}
