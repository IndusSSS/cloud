from __future__ import annotations

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import select

from ..db.session import get_session
from ..models.device_metric import DeviceMetric

router = APIRouter()


def _parse_last(last: str) -> timedelta:
    unit = last[-1]
    value = int(last[:-1])
    if unit == "h":
        return timedelta(hours=value)
    if unit == "m":
        return timedelta(minutes=value)
    return timedelta(seconds=value)


@router.get("/metrics/{device_id}")
async def get_metrics(
    device_id: str,
    type: str,
    last: str = Query("1h"),
    session=Depends(get_session),
) -> list[dict[str, float | str]]:
    start = datetime.utcnow() - _parse_last(last)
    stmt = (
        select(
            func.date_trunc("minute", DeviceMetric.ts).label("bucket"),
            func.avg(DeviceMetric.value).label("value"),
            DeviceMetric.unit,
        )
        .where(
            DeviceMetric.device_id == device_id,
            DeviceMetric.type == type,
            DeviceMetric.ts >= start,
        )
        .group_by("bucket", DeviceMetric.unit)
        .order_by("bucket")
    )
    res = await session.execute(stmt)
    rows = res.all()
    return [
        {"ts": row.bucket.isoformat(), "value": row.value, "unit": row.unit}
        for row in rows
    ]

