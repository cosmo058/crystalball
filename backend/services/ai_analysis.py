import os
import anthropic
from models.schemas import StockOverview, TechnicalIndicators, ScoreBreakdown, NewsItem

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def generate_ai_summary(
    overview: StockOverview,
    technicals: TechnicalIndicators,
    score: ScoreBreakdown,
    news: list[NewsItem],
) -> str:
    news_lines = "\n".join(
        f"- [{item.sentiment}] {item.title}" for item in news[:5]
    ) or "No recent news available."

    prompt = f"""You are a financial analyst assistant. Analyze the following stock data and provide a concise 3-4 paragraph investment intelligence summary.

**Stock:** {overview.name} ({overview.ticker})
**Price:** ${overview.price} ({overview.change_pct:+.2f}% today)
**Sector:** {overview.sector or 'N/A'} | **Industry:** {overview.industry or 'N/A'}

**Fundamentals:**
- P/E Ratio: {overview.pe_ratio or 'N/A'}
- EPS: {overview.eps or 'N/A'}
- Market Cap: ${overview.market_cap:,.0f if overview.market_cap else 'N/A'}
- Dividend Yield: {f"{overview.dividend_yield*100:.2f}%" if overview.dividend_yield else 'None'}
- 52-Week Range: ${overview.week_52_low} – ${overview.week_52_high}

**Technical Indicators:**
- RSI (14): {technicals.rsi or 'N/A'}
- MACD: {technicals.macd or 'N/A'} | Signal: {technicals.macd_signal or 'N/A'}
- SMA 20/50/200: {technicals.sma_20 or 'N/A'} / {technicals.sma_50 or 'N/A'} / {technicals.sma_200 or 'N/A'}

**Crystalball Score:** {score.total}/100 — Signal: **{score.signal}** ({score.confidence} confidence)
- Valuation: {score.valuation} | Momentum: {score.momentum} | Technical: {score.technical} | Fundamental: {score.fundamental}

**Recent News:**
{news_lines}

Provide:
1. A brief company and market position overview
2. Key technical and fundamental observations
3. Risk factors to watch
4. A clear investment perspective based on the data (not personalized financial advice)

Be direct, data-driven, and professional. No bullet points — write in flowing paragraphs."""

    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
