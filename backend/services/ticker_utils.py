EXCHANGE_SUFFIXES = {
    "TSX": ".TO",
    "TSXV": ".V",
    "CVE": ".TO",
    "NYSE": "",
    "NASDAQ": "",
    "AMEX": "",
}

SUFFIX_TO_EXCHANGE = {
    ".TO": "TSX",
    ".V": "TSXV",
    ".AX": "ASX",
    ".L": "LSE",
    ".DE": "XETRA",
    ".PA": "Euronext Paris",
    ".HK": "HKEX",
}


def normalize_ticker(ticker: str) -> str:
    """Convert exchange-prefixed or plain tickers to yfinance format.

    TSX:ASCU  -> ASCU.TO
    TSXV:XYZ  -> XYZ.V
    ASCU.TO   -> ASCU.TO  (passthrough)
    AAPL      -> AAPL     (passthrough)
    """
    t = ticker.strip().upper()
    if ":" in t:
        prefix, symbol = t.split(":", 1)
        suffix = EXCHANGE_SUFFIXES.get(prefix, "")
        return symbol + suffix
    return t


def display_exchange(ticker: str) -> str | None:
    """Return a human-readable exchange name from a yfinance ticker suffix."""
    for suffix, name in SUFFIX_TO_EXCHANGE.items():
        if ticker.upper().endswith(suffix):
            return name
    return None


def base_symbol(ticker: str) -> str:
    """Strip the exchange suffix to get the bare symbol (e.g. ASCU.TO -> ASCU)."""
    for suffix in SUFFIX_TO_EXCHANGE:
        if ticker.upper().endswith(suffix):
            return ticker[: -len(suffix)]
    return ticker
