from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StockOverview(BaseModel):
    ticker: str
    name: str
    price: float
    change: float
    change_pct: float
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    eps: Optional[float]
    dividend_yield: Optional[float]
    week_52_high: Optional[float]
    week_52_low: Optional[float]
    volume: Optional[int]
    avg_volume: Optional[int]
    sector: Optional[str]
    industry: Optional[str]


class TechnicalIndicators(BaseModel):
    rsi: Optional[float]
    macd: Optional[float]
    macd_signal: Optional[float]
    sma_20: Optional[float]
    sma_50: Optional[float]
    sma_200: Optional[float]
    bollinger_upper: Optional[float]
    bollinger_lower: Optional[float]


class ScoreBreakdown(BaseModel):
    valuation: float
    momentum: float
    technical: float
    fundamental: float
    total: float
    signal: str  # BUY, HOLD, SELL
    confidence: str  # HIGH, MEDIUM, LOW


class NewsItem(BaseModel):
    title: str
    source: str
    url: str
    published: str
    sentiment: str                      # POSITIVE, NEUTRAL, NEGATIVE
    summary: Optional[str] = None       # article excerpt from RSS
    sentiment_reason: Optional[str] = None  # AI-generated explanation


class StockAnalysis(BaseModel):
    ticker: str
    overview: StockOverview
    technicals: TechnicalIndicators
    score: ScoreBreakdown
    news: list[NewsItem]
    ai_summary: Optional[str]
    ai_provider: Optional[str]
    price_history: list[dict]
    score_explanations: Optional[dict] = None


class WatchlistItem(BaseModel):
    id: Optional[int] = None
    ticker: str
    added_at: Optional[datetime] = None


class WatchlistAdd(BaseModel):
    ticker: str


class PricePoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
