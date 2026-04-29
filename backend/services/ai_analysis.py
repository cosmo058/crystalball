import os
import json
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


def _build_score_explanations_prompt(
    overview: StockOverview,
    technicals: TechnicalIndicators,
    score: ScoreBreakdown,
) -> str:
    pe = f"{overview.pe_ratio:.1f}" if overview.pe_ratio else "N/A"
    eps = f"{overview.eps:.2f}" if overview.eps else "N/A"
    div = f"{overview.dividend_yield * 100:.2f}%" if overview.dividend_yield else "none"

    if overview.market_cap:
        cap = overview.market_cap
        cap_str = f"${cap/1e9:.1f}B" if cap >= 1e9 else f"${cap/1e6:.0f}M"
    else:
        cap_str = "N/A"

    high52, low52 = overview.week_52_high, overview.week_52_low
    if overview.price and high52 and low52 and high52 != low52:
        pos = round((overview.price - low52) / (high52 - low52) * 100, 1)
        pos_str = f"{pos}% of the way from 52w low to high"
    else:
        pos_str = "N/A"

    rsi = f"{technicals.rsi:.1f}" if technicals.rsi else "N/A"
    macd_dir = "bullish" if (technicals.macd or 0) > (technicals.macd_signal or 0) else "bearish"

    def vs_sma(sma):
        if overview.price and sma:
            return "above" if overview.price > sma else "below"
        return "N/A"

    vol_ratio = (
        f"{overview.volume / overview.avg_volume:.1f}x"
        if overview.volume and overview.avg_volume else "N/A"
    )

    return f"""Score these 4 sections for {overview.ticker} and explain each in ONE blunt sentence (max 18 words). Use the actual numbers.

Valuation {score.valuation}/100 — P/E {pe} | dividend yield {div} | price position {pos_str}
Technical {score.technical}/100 — RSI {rsi} | MACD {macd_dir} | vs SMA-20 {vs_sma(technicals.sma_20)} | vs SMA-50 {vs_sma(technicals.sma_50)} | vs SMA-200 {vs_sma(technicals.sma_200)}
Momentum {score.momentum}/100 — daily change {overview.change_pct:+.2f}% | volume {vol_ratio} of 3-month avg
Fundamental {score.fundamental}/100 — EPS {eps} | market cap {cap_str}

Return ONLY valid JSON, no markdown:
{{"valuation":"...","technical":"...","momentum":"...","fundamental":"..."}}"""


def generate_score_explanations(
    overview: StockOverview,
    technicals: TechnicalIndicators,
    score: ScoreBreakdown,
) -> dict | None:
    try:
        provider = _active_provider()
        prompt = _build_score_explanations_prompt(overview, technicals, score)

        if provider == "anthropic":
            client = _get_anthropic()
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text
        else:
            client = _get_gemini()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            raw = response.text

        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(raw)
    except Exception:
        return None
