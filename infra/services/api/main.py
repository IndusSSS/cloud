"""
FastAPI entry-point for the public REST API.
File: services/api/main.py
"""

from __future__ import annotations

import os
import logging
from typing import AsyncGenerator, Generator

import psycopg2
import psycopg2.extras
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from psycopg2.pool import ThreadedConnectionPool

# ───────────────────────────────────────────────
# Environment / configuration
# ───────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")
MIN_POOL = int(os.getenv("DB_POOL_MIN", "1"))
MAX_POOL = int(os.getenv("DB_POOL_MAX", "5"))

if not DATABASE_URL:
    # Fail fast—Kubernetes / Docker restart policy will keep trying
    raise RuntimeError("🚨  DATABASE_URL environment variable not set")

# ───────────────────────────────────────────────
# Logging (stdout → picked up by Docker logs)
# ───────────────────────────────────────────────
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# ───────────────────────────────────────────────
# DB connection-pool (thread-safe for Uvicorn workers)
# ───────────────────────────────────────────────
pool: ThreadedConnectionPool | None = None


def init_pool() -> ThreadedConnectionPool:  # called at startup
    global pool
    pool = ThreadedConnectionPool(
        MIN_POOL,
        MAX_POOL,
        dsn=DATABASE_URL,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    logging.info(
        "🗄️  PostgreSQL pool initialised (min=%d max=%d)", MIN_POOL, MAX_POOL
    )
    return pool


def get_conn() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    FastAPI dependency that yields a pooled connection and
    returns it afterwards.
    """
    if pool is None:
        raise RuntimeError("DB pool not initialised")
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


# ───────────────────────────────────────────────
# FastAPI application
# ───────────────────────────────────────────────
app = FastAPI(
    title="SmartSecurity API",
    version="1.0",
    docs_url="/docs",
    redoc_url=None,
)

# Import routers *after* app is created to avoid circulars
from auth import router as auth_router  # noqa: E402

app.include_router(auth_router, prefix="/v1/auth")

# ───────────────────────────────────────────────
# 0️⃣  Start-up / shutdown events
# ───────────────────────────────────────────────
@app.on_event("startup")
def _startup() -> None:
    init_pool()


@app.on_event("shutdown")
def _shutdown() -> None:
    if pool:
        pool.closeall()
        logging.info("🗄️  PostgreSQL pool closed")



# 1. Liveness: no DB dependency, returns 200 immediately
@app.get("/health", tags=["health"])
async def liveness():
    return JSONResponse({"ok": True})

# 2. Readiness: checks the DB (400+ errors if DB is down)
@app.get("/v1/health", tags=["health"])
async def readiness(conn=Depends(get_conn)):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS db_ok;")
            row = cur.fetchone()
        return JSONResponse({"db": row["db_ok"]})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DB error: {exc}")



# ───────────────────────────────────────────────
# 1️⃣  Health - liveness (no DB)
# ───────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def liveness() -> JSONResponse:
    """
    Simple ping so Docker & Traefik know the container is up.
    No external dependencies.
    """
    return JSONResponse({"ok": True})


# ───────────────────────────────────────────────
# 2️⃣  Health - readiness (DB check)
# ───────────────────────────────────────────────
@app.get("/v1/health", tags=["health"])
async def readiness(conn=Depends(get_conn)) -> JSONResponse:  # type: ignore
    try:
        with conn.cursor() as cur:  # type: ignore[attr-defined]
            cur.execute("SELECT 1 AS db_ok;")
            row = cur.fetchone()
        return JSONResponse({"db": row["db_ok"]})
    except Exception as exc:
        logging.exception("DB health-check failed")
        raise HTTPException(500, detail=f"db error: {exc}")


# ───────────────────────────────────────────────
# 3️⃣  Demo /echo endpoint
# ───────────────────────────────────────────────
@app.get("/v1/echo", tags=["demo"])
async def echo(msg: str = Query(..., max_length=100)) -> JSONResponse:
    return JSONResponse({"echo": msg})
