# services/auth-api/app/db.py

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://ssc:ChangeMeToAStrongPass@db:5432/sensordb",
)

# ─── The shared Base for all models ───────────────────────────────
Base = declarative_base()

# ─── Engine & Async Session Factory ──────────────────────────────
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# ─── Dependency for FastAPI ────────────────────────────────────────
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
