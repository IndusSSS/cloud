import os
import psycopg2
import psycopg2.extras

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# import your routers here
from .auth import router as auth_router
# from .telemetry import router as telemetry_router

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=psycopg2.extras.RealDictCursor,
        connect_timeout=3,
    )


app = FastAPI(title="SmartSecurity API", version="1.0")


# ───────────────────────────────────────────────────────────
# 1️⃣  Health‐check endpoint
# Traefik (and external monitors) can hit /api/v1/health
# ───────────────────────────────────────────────────────────
@app.get("/v1/health", tags=["health"])
async def health():
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1;")
        return {"db": "ok"}
    except Exception:
        # if the DB is down, return a 503 so k8s/Traefik knows it’s not healthy
        return JSONResponse(status_code=503, content={"db": "error"})


# ───────────────────────────────────────────────────────────
# 2️⃣  Authentication routes under /v1/auth/*
# (e.g. POST /v1/auth/login)
# ───────────────────────────────────────────────────────────
app.include_router(
    auth_router,
    prefix="/v1/auth",
    tags=["auth"],
)



#Telemetry  things are down here

@app.get("/v1/telemetry")
def telemetry(
    client_id: str | None = Query(None),
    device_id: str | None = Query(None),
    page: int = 1,
    page_size: int = 100,
):
    if page_size > 500:
        page_size = 500
    offset = (page-1) * page_size

    where, params = [], []
    if client_id:
        where.append("client_id = %s"); params.append(client_id)
    if device_id:
        where.append("device_id = %s"); params.append(device_id)

    sql = "FROM telemetry"
    if where:
        sql += " WHERE " + " AND ".join(where)

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) {sql}", params)
        total = cur.fetchone()["count"]

        cur.execute(
            f"SELECT * {sql} ORDER BY ts DESC LIMIT %s OFFSET %s",
            params + [page_size, offset]
        )
        rows = cur.fetchall()

    return {"total": total, "page": page, "page_size": page_size, "data": rows}
app = FastAPI(
    title="SmartSecurity API",
    version="1.0"
)
