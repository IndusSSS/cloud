# File: backend/app/routes/metrics.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session

router = APIRouter()

@router.get("/")
async def list_metrics(session: AsyncSession = Depends(get_session)):
    """
    Example endpoint: fetches up to 10 rows from a 'metrics' table.
    Adjust the query and table/column names to fit your schema.
    """
    try:
        result = await session.execute(text("SELECT * FROM metrics LIMIT 10"))
        rows = [dict(row._mapping) for row in result.fetchall()]
        return {"metrics": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
