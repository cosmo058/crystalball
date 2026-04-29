import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import stocks, watchlist


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    await init_db()
    yield


app = FastAPI(title="Crystalball", version="1.0.0", lifespan=lifespan)

_cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:80,http://localhost"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)
app.include_router(watchlist.router)


@app.get("/api/health")
async def health():
    from services.ai_analysis import get_ai_provider_name
    return {"status": "ok", "version": "1.0.0", "ai_provider": get_ai_provider_name()}
