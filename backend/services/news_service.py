import feedparser
import httpx
from models.schemas import NewsItem

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


def _simple_sentiment(text: str) -> str:
    lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in lower)
    if pos > neg:
        return "POSITIVE"
    elif neg > pos:
        return "NEGATIVE"
    return "NEUTRAL"


def get_stock_news(ticker: str, limit: int = 8) -> list[NewsItem]:
    items: list[NewsItem] = []

    feeds = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
        f"https://feeds.marketwatch.com/marketwatch/marketpulse/",
    ]

    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                published = entry.get("published", "")
                source = feed.feed.get("title", "News")
                sentiment = _simple_sentiment(title)
                items.append(NewsItem(
                    title=title,
                    source=source,
                    url=link,
                    published=published,
                    sentiment=sentiment,
                ))
                if len(items) >= limit:
                    break
        except Exception:
            continue
        if len(items) >= limit:
            break

    return items[:limit]
