from models.schemas import StockOverview, TechnicalIndicators, ScoreBreakdown


def _clamp(val: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, val))


def score_valuation(overview: StockOverview) -> float:
    score = 50.0

    pe = overview.pe_ratio
    if pe is not None:
        if pe <= 0:
            score -= 20
        elif pe < 15:
            score += 20
        elif pe < 25:
            score += 10
        elif pe < 40:
            score -= 5
        else:
            score -= 20

    if overview.dividend_yield is not None and overview.dividend_yield > 0:
        score += min(overview.dividend_yield * 2, 15)

    price = overview.price
    high52 = overview.week_52_high
    low52 = overview.week_52_low
    if price and high52 and low52 and high52 != low52:
        position = (price - low52) / (high52 - low52)
        if position < 0.3:
            score += 15
        elif position > 0.85:
            score -= 10

    return _clamp(score)


def score_momentum(overview: StockOverview) -> float:
    score = 50.0
    pct = overview.change_pct
    if pct > 5:
        score += 20
    elif pct > 2:
        score += 10
    elif pct > 0:
        score += 5
    elif pct < -5:
        score -= 20
    elif pct < -2:
        score -= 10
    elif pct < 0:
        score -= 5

    vol = overview.volume
    avg = overview.avg_volume
    if vol and avg and avg > 0:
        ratio = vol / avg
        if ratio > 2:
            score += 10 if pct >= 0 else -10
        elif ratio > 1.5:
            score += 5 if pct >= 0 else -5

    return _clamp(score)


def score_technical(technicals: TechnicalIndicators, price: float) -> float:
    score = 50.0

    rsi = technicals.rsi
    if rsi is not None:
        if rsi < 30:
            score += 20
        elif rsi < 45:
            score += 10
        elif rsi > 75:
            score -= 20
        elif rsi > 60:
            score -= 10

    macd = technicals.macd
    signal = technicals.macd_signal
    if macd is not None and signal is not None:
        if macd > signal:
            score += 15
        else:
            score -= 15

    sma_20 = technicals.sma_20
    sma_50 = technicals.sma_50
    sma_200 = technicals.sma_200
    if price and sma_20:
        score += 10 if price > sma_20 else -10
    if price and sma_50:
        score += 10 if price > sma_50 else -10
    if price and sma_200:
        score += 10 if price > sma_200 else -10

    return _clamp(score)


def score_fundamental(overview: StockOverview) -> float:
    score = 50.0

    eps = overview.eps
    if eps is not None:
        if eps > 5:
            score += 20
        elif eps > 2:
            score += 10
        elif eps > 0:
            score += 5
        elif eps < 0:
            score -= 20

    cap = overview.market_cap
    if cap is not None:
        if cap > 10e9:
            score += 10
        elif cap > 2e9:
            score += 5
        elif cap < 300e6:
            score -= 5

    return _clamp(score)


def compute_score(overview: StockOverview, technicals: TechnicalIndicators) -> ScoreBreakdown:
    val = score_valuation(overview)
    mom = score_momentum(overview)
    tech = score_technical(technicals, overview.price)
    fund = score_fundamental(overview)

    weights = {"valuation": 0.30, "momentum": 0.20, "technical": 0.30, "fundamental": 0.20}
    total = (
        val * weights["valuation"]
        + mom * weights["momentum"]
        + tech * weights["technical"]
        + fund * weights["fundamental"]
    )
    total = round(_clamp(total), 1)

    if total >= 65:
        signal = "BUY"
        confidence = "HIGH" if total >= 75 else "MEDIUM"
    elif total <= 40:
        signal = "SELL"
        confidence = "HIGH" if total <= 30 else "MEDIUM"
    else:
        signal = "HOLD"
        confidence = "MEDIUM" if 45 <= total <= 60 else "LOW"

    return ScoreBreakdown(
        valuation=round(val, 1),
        momentum=round(mom, 1),
        technical=round(tech, 1),
        fundamental=round(fund, 1),
        total=total,
        signal=signal,
        confidence=confidence,
    )
