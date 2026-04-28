import os
import anthropic
from google import genai
from models.schemas import StockOverview, TechnicalIndicators, ScoreBreakdown, NewsItem

_anthropic_client: anthropic.Anthropic | None = None
_gemini_client: genai.Client | None = None


def _active_provider() -> str:
    """Returns 'anthropic', 'gemini', or raises if neither key is set."""
    provider = os.environ.get("AI_PROVIDER", "").lower()
    if provider in ("anthropic", "gemini"):
        return provider
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    raise EnvironmentError("No AI provider configured. Set ANTHROPIC_API_KEY or GEMINI_API_KEY.")


def get_ai_provider_name() -> str | None:
    try:
        return _active_provider()
    except EnvironmentError:
        return None


def _get_anthropic() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _anthropic_client


def _get_gemini() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _gemini_client


def _build_prompt(
    overview: StockOverview,
    technicals: TechnicalIndicators,
    score: ScoreBreakdown,
    news: list[NewsItem],
) -> str:
    news_lines = "\n".join(
        f"- [{item.sentiment}] {item.title}" for item in news[:5]
    ) or "No recent news available."

    market_cap_str = f"${overview.market_cap:,.0f}" if overview.market_cap else "N/A"
    div_yield_str = f"{overview.dividend_yield:.2f}%" if overview.dividend_yield else "None"

    return f"""You are a financial analyst assistant. Analyze the following stock data and provide a concise 3-4 paragraph investment intelligence summary.

**Stock:** {overview.name} ({overview.ticker})
**Price:** ${overview.price} ({overview.change_pct:+.2f}% today)
**Sector:** {overview.sector or 'N/A'} | **Industry:** {overview.industry or 'N/A'}

**Fundamentals:**
- P/E Ratio: {overview.pe_ratio or 'N/A'}
- EPS: {overview.eps or 'N/A'}
- Market Cap: {market_cap_str}
- Dividend Yield: {div_yield_str}
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


def generate_ai_summary(
    overview: StockOverview,
    technicals: TechnicalIndicators,
    score: ScoreBreakdown,
    news: list[NewsItem],
) -> str:
    provider = _active_provider()
    prompt = _build_prompt(overview, technicals, score, news)

    if provider == "anthropic":
        client = _get_anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    client = _get_gemini()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text
