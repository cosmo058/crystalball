from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, func
from sqlalchemy.ext.asyncio import async_sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./crystalball.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class WatchlistDB(Base):
    __tablename__ = "watchlist"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
