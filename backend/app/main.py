import os
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.routes.metrics import router as metrics_router
from app.routes.logs import router as logs_router  # <-- make sure this file exists

# All of your routes will live under /v1
app = FastAPI(
    title="SmartSecurity API",
    version="1.0",
#   root_path="/v1",
)

# Allow your dashboard to hit these endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("CORS_ORIGIN", "https://admin.smartsecurity.solutions")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount your routers
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
app.include_router(logs_router,    prefix="/logs",    tags=["logs"])

@app.get("/health", tags=["health"])
async def health(session: AsyncSession = Depends(get_session)):
    """Health check: runs a simple SELECT 1 on your DB."""
    try:
        await session.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="Database unreachable")

@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse({"message": "Welcome to SmartSecurity API v1"})
