import os
import time
import logging
import threading
import collections
import httpx
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands
from models.schemas import StockOverview, TechnicalIndicators

log = logging.getLogger(__name__)

_RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")
_RAPIDAPI_HOST = "apidojo-yahoo-finance-v1.p.rapidapi.com"
_RAPIDAPI_BASE = f"https://{_RAPIDAPI_HOST}"

_quote_cache: dict = {}         # ticker -> (fetched_at, quote_dict | None)
_chart_cache: dict = {}         # (ticker, range) -> (fetched_at, df)
_search_cache: dict = {}        # query -> (fetched_at, results_list)
_QUOTE_TTL = 300                # 5 min
_CHART_TTL = 600                # 10 min
_SEARCH_TTL = 3600              # 1 hour

_api_lock = threading.Lock()
_api_call_times: collections.deque = collections.deque(maxlen=5)


def _throttle():
    with _api_lock:
        now = time.time()
        if len(_api_call_times) == 5:
            oldest = _api_call_times[0]
            wait = 1.1 - (now - oldest)
            if wait > 0:
                time.sleep(wait)
        _api_call_times.append(time.time())


def _get(path: str, params: dict) -> dict:
    _throttle()
    headers = {
        "x-rapidapi-host": _RAPIDAPI_HOST,
        "x-rapidapi-key": _RAPIDAPI_KEY,
    }
    try:
        r = httpx.get(f"{_RAPIDAPI_BASE}{path}", params=params, headers=headers, timeout=15)
    except Exception as e:
        log.warning("RapidAPI request failed: %s", e)
        return {}
    if r.status_code != 200:
        log.warning("RapidAPI %s %s returned %d", path, params, r.status_code)
        return {}
    return r.json()


def _region(ticker: str) -> str:
    t = ticker.upper()
    if t.endswith(".TO") or t.endswith(".V"):
        return "CA"
    return "US"


def _float(v):
    try:
        return float(v) if v not in (None, "", "N/A", "-") else None
    except (ValueError, TypeError):
        return None


def _int(v):
    try:
        return int(float(v)) if v not in (None, "", "N/A", "-") else None
    except (ValueError, TypeError):
        return None


def _safe(val):
    if val is None:
        return None
    v = float(val)
    return None if np.isnan(v) else round(v, 4)


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

def _fetch_quote(ticker: str) -> dict | None:
    cached = _quote_cache.get(ticker)
    if cached:
        fetched_at, data = cached
        if time.time() - fetched_at < _QUOTE_TTL:
            return data

    data = _get("/market/v2/get-quotes", {"symbols": ticker, "region": _region(ticker)})
    result = data.get("quoteResponse", {}).get("result", [])
    if not result:
        log.warning("RapidAPI: no quote for %s", ticker)
        _quote_cache[ticker] = (time.time(), None)
        return None

    quote = result[0]
    _quote_cache[ticker] = (time.time(), quote)
    return quote


def _fetch_chart_df(ticker: str, range_: str) -> pd.DataFrame:
    key = (ticker, range_)
    cached = _chart_cache.get(key)
    if cached:
        fetched_at, df = cached
        if time.time() - fetched_at < _CHART_TTL:
            return df

    data = _get("/market/get-charts", {
        "symbol": ticker,
        "region": _region(ticker),
        "interval": "1d",
        "range": range_,
    })

    df = pd.DataFrame()
    try:
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        q = result["indicators"]["quote"][0]
        rows = []
        for i, ts in enumerate(timestamps):
            o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
            if None in (o, h, l, c):
                continue
            rows.append({
                "Date": pd.Timestamp(ts, unit="s"),
                "Open": float(o),
                "High": float(h),
                "Low": float(l),
                "Close": float(c),
                "Volume": int(v) if v is not None else 0,
            })
        if rows:
            df = pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
    except (KeyError, IndexError, TypeError) as e:
        log.warning("RapidAPI: failed to parse chart for %s (%s): %s", ticker, range_, e)

    _chart_cache[key] = (time.time(), df)
    return df


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

_PERIOD_TO_RANGE = {
    "1mo": "1mo", "3mo": "3mo", "6mo": "6mo",
    "1y": "1y", "2y": "2y", "5y": "5y",
}


def get_stock_overview(ticker: str) -> StockOverview:
    q = _fetch_quote(ticker)
    if q:
        price = _float(q.get("regularMarketPrice")) or 0
        eps = _float(q.get("epsTrailingTwelveMonths"))
        trailing_pe = round(price / eps, 4) if eps and eps != 0 else None
        return StockOverview(
            ticker=ticker.upper(),
            name=q.get("longName") or q.get("shortName") or ticker.upper(),
            price=price,
            change=round(_float(q.get("regularMarketChange")) or 0, 4),
            change_pct=round(_float(q.get("regularMarketChangePercent")) or 0, 2),
            market_cap=_float(q.get("marketCap")),
            pe_ratio=trailing_pe,
            eps=eps,
            dividend_yield=_float(q.get("trailingAnnualDividendYield")),
            week_52_high=_float(q.get("fiftyTwoWeekHigh")),
            week_52_low=_float(q.get("fiftyTwoWeekLow")),
            volume=_int(q.get("regularMarketVolume")),
            avg_volume=_int(q.get("averageDailyVolume3Month")),
            sector=None,
            industry=None,
        )

    return StockOverview(
        ticker=ticker.upper(), name=ticker.upper(),
        price=0, change=0, change_pct=0,
        market_cap=None, pe_ratio=None, eps=None, dividend_yield=None,
        week_52_high=None, week_52_low=None, volume=None, avg_volume=None,
        sector=None, industry=None,
    )


def get_price_history(ticker: str, period: str = "6mo") -> list[dict]:
    df = _fetch_chart_df(ticker, _PERIOD_TO_RANGE.get(period, "6mo"))
    if df.empty:
        return []
    return [
        {
            "date": row["Date"].strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        }
        for _, row in df.iterrows()
    ]


def get_technical_indicators(ticker: str) -> TechnicalIndicators:
    _empty = TechnicalIndicators(
        rsi=None, macd=None, macd_signal=None,
        sma_20=None, sma_50=None, sma_200=None,
        bollinger_upper=None, bollinger_lower=None,
    )

    df = _fetch_chart_df(ticker, "1y")
    if df.empty or len(df) < 30:
        return _empty

    close = df["Close"]
    rsi = RSIIndicator(close, window=14).rsi().iloc[-1]
    macd_ind = MACD(close)
    sma_20 = SMAIndicator(close, window=20).sma_indicator().iloc[-1]
    sma_50 = SMAIndicator(close, window=50).sma_indicator().iloc[-1] if len(close) >= 50 else None
    sma_200 = SMAIndicator(close, window=200).sma_indicator().iloc[-1] if len(close) >= 200 else None
    bb = BollingerBands(close, window=20)

    return TechnicalIndicators(
        rsi=_safe(rsi),
        macd=_safe(macd_ind.macd().iloc[-1]),
        macd_signal=_safe(macd_ind.macd_signal().iloc[-1]),
        sma_20=_safe(sma_20),
        sma_50=_safe(sma_50),
        sma_200=_safe(sma_200),
        bollinger_upper=_safe(bb.bollinger_hband().iloc[-1]),
        bollinger_lower=_safe(bb.bollinger_lband().iloc[-1]),
    )


def search_ticker(query: str, region: str = "US") -> list[dict]:
    """Return autocomplete results for a query string."""
    key = (query.upper(), region)
    cached = _search_cache.get(key)
    if cached:
        fetched_at, results = cached
        if time.time() - fetched_at < _SEARCH_TTL:
            return results

    data = _get("/auto-complete", {"q": query, "region": region})
    quotes = data.get("quotes", [])
    results = [
        {
            "ticker": q.get("symbol", ""),
            "name": q.get("longname") or q.get("shortname") or q.get("symbol", ""),
            "exchange": q.get("exchDisp"),
            "sector": q.get("sector"),
            "industry": q.get("industry"),
            "type": q.get("quoteType"),
        }
        for q in quotes
        if q.get("quoteType") in ("EQUITY", "ETF") and q.get("isYahooFinance")
    ]
    _search_cache[key] = (time.time(), results)
    return results
