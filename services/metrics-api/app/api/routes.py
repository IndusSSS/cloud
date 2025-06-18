from fastapi import APIRouter, Depends
from sqlmodel import select

from common import Metric
from ..db.session import get_session

router = APIRouter()


@router.post("/metrics/push")
async def push(metrics: list[Metric], session=Depends(get_session)):
    session.add_all(metrics)
    await session.commit()
    return {"count": len(metrics)}


@router.get("/metrics/query")
async def query(session=Depends(get_session)):
    result = await session.execute(select(Metric))
    return result.scalars().all()
