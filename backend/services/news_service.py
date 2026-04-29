import time
import re
import feedparser
from urllib.parse import quote
from models.schemas import NewsItem
from services.ticker_utils import base_symbol

POSITIVE_WORDS = {
    "surge", "soar", "rally", "gain", "beat", "record", "growth", "profit",
    "upgrade", "bullish", "outperform", "strong", "rise", "jump", "exceed",
    "positive", "boost", "buy", "opportunity", "revenue", "earnings beat",
}
NEGATIVE_WORDS = {
    "fall", "drop", "decline", "loss", "miss", "cut", "downgrade", "bearish",
    "underperform", "weak", "plunge", "crash", "sell", "risk", "concern",
    "warning", "layoff", "lawsuit", "fraud", "investigate", "debt", "default",
}

_news_cache: dict = {}          # ticker -> (fetched_at, list[NewsItem])
_enriched_cache: dict = {}      # ticker -> (fetched_at, list[NewsItem])
_NEWS_TTL = 600                 # 10 min
_ENRICHED_TTL = 900             # 15 min


def _keyword_sentiment(text: str) -> str:
    lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in lower)
    if pos > neg:
        return "POSITIVE"
    elif neg > pos:
        return "NEGATIVE"
    return "NEUTRAL"


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _feeds(ticker: str, name: str | None = None) -> list[str]:
    # For cross-listed Canadian stocks use the base US symbol on Yahoo Finance
    # (e.g. MU.TO → MU, RY.TO → RY) so we get the full news volume
    yf_symbol = base_symbol(ticker) if ticker != base_symbol(ticker) else ticker
    # Google News: company name is far more precise than a bare symbol
    gn_raw = f'"{name}" stock' if name else f"{ticker} stock"
    gn_query = quote(gn_raw)
    return [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={yf_symbol}&region=US&lang=en-US",
        f"https://news.google.com/rss/search?q={gn_query}&hl=en-US&gl=US&ceid=US:en",
    ]


def get_stock_news(ticker: str, name: str | None = None, limit: int = 8) -> list[NewsItem]:
    cache_key = ticker
    cached = _news_cache.get(cache_key)
    if cached:
        fetched_at, items = cached
        if time.time() - fetched_at < _NEWS_TTL:
            return items

    per_feed = max(limit // 2, 4)
    all_items: list[NewsItem] = []
    seen_titles: set[str] = set()

    for url in _feeds(ticker, name):
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                if not title:
                    continue
                key = title.lower()[:80]
                if key in seen_titles:
                    continue
                seen_titles.add(key)
                raw_summary = entry.get("summary") or entry.get("description") or ""
                summary = _strip_html(raw_summary)[:400] or None
                sentiment_text = f"{title} {summary or ''}"
                all_items.append(NewsItem(
                    title=title,
                    source=feed.feed.get("title", "News"),
                    url=entry.get("link", ""),
                    published=entry.get("published", ""),
                    sentiment=_keyword_sentiment(sentiment_text),
                    summary=summary,
                ))
                count += 1
                if count >= per_feed:
                    break
        except Exception:
            continue

    items = all_items

    items = items[:limit]
    _news_cache[cache_key] = (time.time(), items)
    return items


def get_enriched_news(ticker: str, name: str | None = None, limit: int = 8) -> list[NewsItem]:
    """Return AI-filtered and sentiment-analyzed news. Falls back to keyword sentiment."""
    cache_key = ticker
    cached = _enriched_cache.get(cache_key)
    if cached:
        fetched_at, items = cached
        if time.time() - fetched_at < _ENRICHED_TTL:
            return items

    # Fetch extra so we still have `limit` relevant articles after AI filters noise
    raw = get_stock_news(ticker, name, limit + 5)
    if not raw:
        return raw

    try:
        from services.ai_analysis import analyze_news_sentiment
        enriched = analyze_news_sentiment(raw, ticker, limit)
        _enriched_cache[cache_key] = (time.time(), enriched)
        return enriched
    except Exception:
        return raw[:limit]
