"""
Auth-API – handles login, token refresh & RBAC.
"""

import os
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health import router as health_router


app.include_router(health_router)

# ──────────────── DB helper ────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL env-var not set!")

def get_conn():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=psycopg2.extras.RealDictCursor,
        connect_timeout=3,
    )

# ──────────────── FastAPI app ────────────────
app = FastAPI(
    title="SmartSecurity Auth-API",
    version="1.0",
    docs_url="/docs",
    redoc_url=None,
)

# Optional: allow dashboard origin in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────── include your routers ────────────────
# from .routes.auth import router as auth_router
# app.include_router(auth_router, prefix="/v1/auth")

# ──────────────── health & ping ────────────────
@app.get("/ping", tags=["health"])
async def ping():
    return {"pong": True}

@app.get("/health", tags=["health"])
async def health():
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1;")
        return {"db": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"db error: {exc}")
