from fastapi import APIRouter, HTTPException, Query
from services.market_data import get_stock_overview, get_price_history, get_technical_indicators
from services.scoring import compute_score
from services.news_service import get_stock_news
from services.ai_analysis import generate_ai_summary
from models.schemas import StockAnalysis, StockOverview
import os

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/search")
async def search_stocks(q: str = Query(..., min_length=1)):
    import yfinance as yf
    try:
        ticker = yf.Ticker(q.upper())
        info = ticker.info
        if not info or not info.get("longName"):
            raise HTTPException(status_code=404, detail=f"Ticker '{q}' not found")
        return {
            "ticker": q.upper(),
            "name": info.get("longName") or info.get("shortName", q.upper()),
            "sector": info.get("sector"),
            "exchange": info.get("exchange"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}", response_model=StockAnalysis)
async def get_stock_analysis(
    ticker: str,
    ai: bool = Query(default=True, description="Include AI summary"),
):
    ticker = ticker.upper()
    try:
        overview = get_stock_overview(ticker)
        technicals = get_technical_indicators(ticker)
        score = compute_score(overview, technicals)
        news = get_stock_news(ticker)
        history = get_price_history(ticker)

        ai_summary = None
        if ai and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                ai_summary = generate_ai_summary(overview, technicals, score, news)
            except Exception:
                ai_summary = None

        return StockAnalysis(
            ticker=ticker,
            overview=overview,
            technicals=technicals,
            score=score,
            news=news,
            ai_summary=ai_summary,
            price_history=history,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/history")
async def get_history(ticker: str, period: str = Query(default="6mo")):
    valid_periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Period must be one of {valid_periods}")
    try:
        return get_price_history(ticker.upper(), period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
