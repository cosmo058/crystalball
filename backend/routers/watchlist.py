from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_session, WatchlistDB
from models.schemas import WatchlistItem, WatchlistAdd
from services.market_data import get_stock_overview
from datetime import datetime

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("/", response_model=list[WatchlistItem])
async def list_watchlist(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WatchlistDB).order_by(WatchlistDB.added_at.desc()))
    items = result.scalars().all()
    return [WatchlistItem(id=i.id, ticker=i.ticker, added_at=i.added_at) for i in items]


@router.post("/", response_model=WatchlistItem)
async def add_to_watchlist(body: WatchlistAdd, session: AsyncSession = Depends(get_session)):
    ticker = body.ticker.upper()
    existing = await session.execute(select(WatchlistDB).where(WatchlistDB.ticker == ticker))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"{ticker} is already in your watchlist")

    try:
        overview = get_stock_overview(ticker)
        if not overview.name:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

    item = WatchlistDB(ticker=ticker, added_at=datetime.utcnow())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return WatchlistItem(id=item.id, ticker=item.ticker, added_at=item.added_at)


@router.delete("/{ticker}")
async def remove_from_watchlist(ticker: str, session: AsyncSession = Depends(get_session)):
    ticker = ticker.upper()
    result = await session.execute(delete(WatchlistDB).where(WatchlistDB.ticker == ticker))
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"{ticker} not found in watchlist")
    return {"message": f"{ticker} removed from watchlist"}


@router.get("/summary")
async def watchlist_summary(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(WatchlistDB))
    items = result.scalars().all()
    summaries = []
    for item in items:
        try:
            overview = get_stock_overview(item.ticker)
            summaries.append({
                "ticker": item.ticker,
                "name": overview.name,
                "price": overview.price,
                "change_pct": overview.change_pct,
            })
        except Exception:
            summaries.append({"ticker": item.ticker, "name": item.ticker, "price": None, "change_pct": None})
    return summaries
