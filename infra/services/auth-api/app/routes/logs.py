# File: backend/app/routes/logs.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session       # your existing dependency
from app.models import Log           # your ORM model

from pydantic import BaseModel

router = APIRouter()


@router.get(
    "/", 
    summary="Dummy log endpoint"
)
async def list_logs(
    session: AsyncSession = Depends(get_session)
):
    """
    Return the 10 most recent rows from a `logs` table (if it exists).
    """
    try:
        res = await session.execute(
            text("SELECT * FROM logs ORDER BY id DESC LIMIT 10")
        )
        return {"logs": [dict(r) for r in res.fetchall()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────
# New: Pydantic schema for incoming device logs
# ──────────────────────────────────────────────────────────────────────
class LogIn(BaseModel):
    device_id: str
    switch: bool
    ts: int
    temp: float | None = None   # optional if you include temperature


# ──────────────────────────────────────────────────────────────────────
# New: POST /logs — ingest one log entry from a device
# ──────────────────────────────────────────────────────────────────────
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Ingest one log entry from a device"
)
async def ingest_log(
    log: LogIn,
    session: AsyncSession = Depends(get_session)
):
    try:
        entry = Log(
            device_id=log.device_id,
            switch=log.switch,
            ts_device=log.ts,
            temp_c=log.temp      # matches your Log.temp_c column
        )
        session.add(entry)
        await session.commit()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
