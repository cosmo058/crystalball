# Crystalball

Stock analysis app — real-time quotes, technical indicators, AI-generated summaries, and a watchlist.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React + Vite, Recharts |
| Backend | FastAPI (Python) |
| Database | SQLite via SQLAlchemy + aiosqlite |
| Market data | RapidAPI — Yahoo Finance v1 (`apidojo`) |
| AI summary | Google Gemini (default) or Anthropic Claude |
| Deployment | Docker + nginx reverse proxy |

## Running locally (development)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev            # http://localhost:5173
```

## Running with Docker

```bash
cp .env.example .env   # fill in keys
docker compose up -d --build
# App is served at http://localhost:${PORT:-80}
```

## Environment variables

### Root `.env` (Docker)

| Variable | Required | Description |
|----------|----------|-------------|
| `RAPIDAPI_KEY` | Yes | RapidAPI key — Yahoo Finance v1 |
| `GEMINI_API_KEY` | One of these | Google Gemini API key |
| `ANTHROPIC_API_KEY` | One of these | Anthropic Claude API key |
| `AI_PROVIDER` | No | `gemini` or `claude` (defaults to Claude if both keys set) |
| `PORT` | No | Host port for the frontend (default `80`) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |

### `backend/.env` (local dev only)

Same variables as above. `load_dotenv()` in `main.py` loads this file automatically when running `uvicorn` from the `backend/` directory.

## Project layout

```
crystalball/
├── backend/
│   ├── main.py                  # FastAPI app, CORS, lifespan
│   ├── database.py              # SQLite init
│   ├── models/schemas.py        # Pydantic models
│   ├── routers/
│   │   ├── stocks.py            # GET /api/stocks/*
│   │   └── watchlist.py         # GET/POST /api/watchlist/*
│   └── services/
│       ├── market_data.py       # RapidAPI data fetching + caching
│       ├── scoring.py           # Rule-based stock score (0–100)
│       ├── ai_analysis.py       # AI summary generation
│       ├── news_service.py      # RSS news aggregation
│       └── ticker_utils.py      # Ticker normalization (TSX:X → X.TO)
├── frontend/
│   └── src/
├── docker-compose.yml
└── docs/
    └── market-data-api.md       # RapidAPI endpoint reference
```

## Ticker formats

| Input | Normalized | Market |
|-------|-----------|--------|
| `AAPL` | `AAPL` | US (NASDAQ/NYSE) |
| `TSX:SHOP` | `SHOP.TO` | Toronto Stock Exchange |
| `TSXV:XYZ` | `XYZ.V` | TSX Venture |
| `SHOP.TO` | `SHOP.TO` | passthrough |

## API endpoints

See [`docs/market-data-api.md`](docs/market-data-api.md) for the external data source reference.

Internal backend endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/stocks/search?q=AAPL` | Autocomplete ticker search |
| `GET` | `/api/stocks/{ticker}?ai=true` | Full stock analysis |
| `GET` | `/api/stocks/{ticker}/history?period=6mo` | OHLCV price history |
| `GET` | `/api/watchlist/` | List watchlist entries |
| `POST` | `/api/watchlist/` | Add ticker to watchlist |
| `DELETE` | `/api/watchlist/{ticker}` | Remove from watchlist |
| `GET` | `/api/health` | Health check + AI provider info |
