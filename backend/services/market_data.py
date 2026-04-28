import time
import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands
from models.schemas import StockOverview, TechnicalIndicators, PricePoint

_session_cache: dict = {}


def _get_ticker(ticker: str) -> yf.Ticker:
    return yf.Ticker(ticker)


def _fetch_info_with_retry(ticker: str, retries: int = 3, delay: float = 2.0) -> dict:
    stock = _get_ticker(ticker)
    for attempt in range(retries):
        try:
            info = stock.info
            if info and (info.get("currentPrice") or info.get("regularMarketPrice") or info.get("longName")):
                return info
        except Exception:
            pass
        if attempt < retries - 1:
            time.sleep(delay * (attempt + 1))
    return stock.info or {}


def get_stock_overview(ticker: str) -> StockOverview:
    info = _fetch_info_with_retry(ticker)

    price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose") or price
    change = round(price - prev_close, 4)
    change_pct = round((change / prev_close) * 100, 2) if prev_close else 0

    return StockOverview(
        ticker=ticker.upper(),
        name=info.get("longName") or info.get("shortName") or ticker.upper(),
        price=price,
        change=change,
        change_pct=change_pct,
        market_cap=info.get("marketCap"),
        pe_ratio=info.get("trailingPE"),
        eps=info.get("trailingEps"),
        dividend_yield=info.get("dividendYield"),
        week_52_high=info.get("fiftyTwoWeekHigh"),
        week_52_low=info.get("fiftyTwoWeekLow"),
        volume=info.get("volume") or info.get("regularMarketVolume"),
        avg_volume=info.get("averageVolume"),
        sector=info.get("sector"),
        industry=info.get("industry"),
    )


def get_price_history(ticker: str, period: str = "6mo") -> list[dict]:
    stock = _get_ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        return []
    hist = hist.reset_index()
    result = []
    for _, row in hist.iterrows():
        result.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        })
    return result


def get_technical_indicators(ticker: str) -> TechnicalIndicators:
    stock = _get_ticker(ticker)
    hist = stock.history(period="1y")

    if hist.empty or len(hist) < 30:
        return TechnicalIndicators(
            rsi=None, macd=None, macd_signal=None,
            sma_20=None, sma_50=None, sma_200=None,
            bollinger_upper=None, bollinger_lower=None,
        )

    close = hist["Close"]

    rsi = RSIIndicator(close, window=14).rsi().iloc[-1]
    macd_ind = MACD(close)
    macd_val = macd_ind.macd().iloc[-1]
    macd_sig = macd_ind.macd_signal().iloc[-1]
    sma_20 = SMAIndicator(close, window=20).sma_indicator().iloc[-1]
    sma_50 = SMAIndicator(close, window=50).sma_indicator().iloc[-1] if len(close) >= 50 else None
    sma_200 = SMAIndicator(close, window=200).sma_indicator().iloc[-1] if len(close) >= 200 else None
    bb = BollingerBands(close, window=20)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]

    def _safe(val):
        if val is None:
            return None
        v = float(val)
        return None if np.isnan(v) else round(v, 4)

    return TechnicalIndicators(
        rsi=_safe(rsi),
        macd=_safe(macd_val),
        macd_signal=_safe(macd_sig),
        sma_20=_safe(sma_20),
        sma_50=_safe(sma_50),
        sma_200=_safe(sma_200),
        bollinger_upper=_safe(bb_upper),
        bollinger_lower=_safe(bb_lower),
    )
