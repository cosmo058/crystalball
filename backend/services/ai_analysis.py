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

    return f"""You are a sharp financial analyst. Give a 2-paragraph max snapshot on {overview.name} ({overview.ticker}).

Data: Price ${overview.price} ({overview.change_pct:+.2f}% today) | Score {score.total}/100 → {score.signal} ({score.confidence}) | RSI {technicals.rsi or 'N/A'} | MACD {'bullish' if (technicals.macd or 0) > (technicals.macd_signal or 0) else 'bearish'} | P/E {overview.pe_ratio or 'N/A'} | EPS {overview.eps or 'N/A'} | Cap {market_cap_str} | 52w ${overview.week_52_low}–${overview.week_52_high} | Price vs SMA200 {'above' if overview.price and technicals.sma_200 and overview.price > technicals.sma_200 else 'below'}
News: {news_lines}

Paragraph 1: What's driving price action right now — technicals, momentum, news catalyst.
Paragraph 2: The key risk or opportunity. End with one clear takeaway sentence.

Be blunt and specific. No filler. No disclaimers."""


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
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    client = _get_gemini()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text
