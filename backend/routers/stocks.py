from fastapi import APIRouter, HTTPException, Query
from services.market_data import get_stock_overview, get_price_history, get_technical_indicators, search_ticker
from services.scoring import compute_score
from services.news_service import get_stock_news
from services.ai_analysis import generate_ai_summary, generate_score_explanations, get_ai_provider_name
from services.ticker_utils import normalize_ticker, base_symbol
from models.schemas import StockAnalysis, StockOverview
import os

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/search")
async def search_stocks(q: str = Query(..., min_length=1)):
    try:
        results = search_ticker(q)
        if not results:
            raise HTTPException(status_code=404, detail=f"No results for '{q}'")
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker:path}", response_model=StockAnalysis)
async def get_stock_analysis(
    ticker: str,
    ai: bool = Query(default=True, description="Include AI summary"),
):
    ticker = normalize_ticker(ticker)
    try:
        overview = get_stock_overview(ticker)
        technicals = get_technical_indicators(ticker)
        score = compute_score(overview, technicals)
        news = get_stock_news(base_symbol(ticker))
        history = get_price_history(ticker)

        ai_summary = None
        ai_provider = None
        score_explanations = None
        if ai and get_ai_provider_name():
            try:
                ai_summary = generate_ai_summary(overview, technicals, score, news)
                ai_provider = get_ai_provider_name()
            except Exception:
                ai_summary = None
            try:
                score_explanations = generate_score_explanations(overview, technicals, score)
            except Exception:
                score_explanations = None

        return StockAnalysis(
            ticker=ticker,
            overview=overview,
            technicals=technicals,
            score=score,
            news=news,
            ai_summary=ai_summary,
            ai_provider=ai_provider,
            price_history=history,
            score_explanations=score_explanations,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker:path}/history")
async def get_history(ticker: str, period: str = Query(default="6mo")):
    valid_periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Period must be one of {valid_periods}")
    try:
        return get_price_history(normalize_ticker(ticker), period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
