# Market Data API Reference

**Provider:** [RapidAPI — Yahoo Finance v1](https://rapidapi.com/apidojo/api/yahoo-finance1) by apidojo  
**Base URL:** `https://apidojo-yahoo-finance-v1.p.rapidapi.com`  
**Auth:** `x-rapidapi-key: <your key>` header (set via `RAPIDAPI_KEY` env var)

---

## Endpoints in use

### `GET /market/v2/get-quotes`

Real-time quote + fundamentals for one or more symbols. Used by `get_stock_overview()`.

**Parameters**

| Param | Type | Required | Example |
|-------|------|----------|---------|
| `symbols` | string | Yes | `AAPL`, `SHOP.TO`, `MU.TO` |
| `region` | string | Yes | `US`, `CA` |

**Key response fields** (`quoteResponse.result[0]`)

| Field | Maps to |
|-------|---------|
| `regularMarketPrice` | price |
| `regularMarketChange` | change |
| `regularMarketChangePercent` | change % (already a percentage, e.g. `11.24`) |
| `regularMarketVolume` | volume |
| `averageDailyVolume3Month` | avg volume |
| `marketCap` | market cap |
| `epsTrailingTwelveMonths` | EPS (trailing 12 months) |
| `trailingAnnualDividendYield` | dividend yield (decimal, e.g. `0.026` = 2.6%) |
| `fiftyTwoWeekHigh` / `fiftyTwoWeekLow` | 52-week range |
| `longName` / `shortName` | company name |
| `preMarketPrice` / `preMarketChange` | pre-market data |
| `targetPriceMean` / `targetPriceHigh` / `targetPriceLow` | analyst price targets |
| `forwardPE` | forward P/E ratio |

> **Note:** `trailingPE` is not returned directly. The app calculates it as `regularMarketPrice / epsTrailingTwelveMonths`.  
> `sector` and `industry` are not available from this endpoint — use `/auto-complete` to retrieve them.

**Region mapping by ticker suffix**

| Ticker suffix | Region |
|--------------|--------|
| `.TO` (TSX) | `CA` |
| `.V` (TSXV) | `CA` |
| none (US) | `US` |

---

### `GET /market/get-charts`

Daily OHLCV candlestick data. Used by `get_price_history()` and `get_technical_indicators()`.

**Parameters**

| Param | Type | Required | Example |
|-------|------|----------|---------|
| `symbol` | string | Yes | `INTC` |
| `region` | string | Yes | `US`, `CA` |
| `interval` | string | Yes | `1d`, `1wk`, `1mo` |
| `range` | string | Yes | `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `max` |

**Response structure**

```
chart.result[0]
  ├── meta            (symbol, currency, exchange info)
  ├── timestamp[]     (Unix seconds, one per bar)
  └── indicators
        └── quote[0]
              ├── open[]
              ├── high[]
              ├── low[]
              ├── close[]
              └── volume[]
```

Bars with `null` values (holidays, missing data) are filtered out before returning.

---

### `GET /auto-complete`

Ticker search / autocomplete. Used by `search_ticker()` and the `GET /api/stocks/search` route.

**Parameters**

| Param | Type | Required | Example |
|-------|------|----------|---------|
| `q` | string | Yes | `INTC`, `Apple`, `shop` |
| `region` | string | No | `US` (default) |

**Key response fields** (`quotes[]`)

| Field | Description |
|-------|-------------|
| `symbol` | Ticker (e.g. `INTC`, `SHOP.TO`) |
| `longname` / `shortname` | Company name |
| `exchDisp` | Exchange label (e.g. `NASDAQ`, `Toronto`) |
| `quoteType` | `EQUITY`, `ETF`, `INDEX`, `MUTUALFUND`, etc. |
| `sector` / `sectorDisp` | Sector (equities only) |
| `industry` / `industryDisp` | Industry (equities only) |
| `isYahooFinance` | Filter to `true` to exclude third-party entries |

Results are filtered to `EQUITY` and `ETF` types with `isYahooFinance: true`.

---

## Caching

All three fetchers cache responses in-process to avoid redundant calls.

| Cache | TTL | Key |
|-------|-----|-----|
| Quote | 5 min | ticker |
| Chart | 10 min | (ticker, range) |
| Search | 1 hour | (query, region) |

---

## Endpoints available but not yet used

These endpoints exist on this plan and may be useful for future features. Verify availability against your subscription tier — some return `204 No Content` on lower tiers.

| Endpoint | Description |
|----------|-------------|
| `GET /market/get-trending-tickers?region=US` | Currently trending tickers |
| `GET /market/get-movers?region=US&count=25` | Top gainers / losers |
| `GET /market/get-summary?region=US` | Major index snapshots (S&P 500, Dow, etc.) |
| `GET /stock/v2/get-analysis?symbol=X&region=US` | Analyst ratings and recommendations |
| `GET /stock/v2/get-financials?symbol=X&region=US` | Income statement |
| `GET /stock/v2/get-balance-sheet?symbol=X&region=US` | Balance sheet |
| `GET /stock/v2/get-cash-flow?symbol=X&region=US` | Cash flow statement |
| `GET /stock/v2/get-options?symbol=X&region=US` | Options chain |

> **Confirmed not available** on the current plan (return `204`):  
> `GET /stock/v3/get-historical-data`, `GET /stock/v2/get-historical-data`, `GET /stock/v2/get-summary`

---

## Rate limits

Limits depend on your RapidAPI subscription tier. The app uses a sliding-window throttle (`_throttle()` in `market_data.py`) that enforces a maximum of 5 in-flight calls per second to stay safely within free-tier quotas. Adjust `maxlen` and the sleep window if you upgrade.
