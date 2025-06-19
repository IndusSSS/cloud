from __future__ import annotations

from fastapi import APIRouter, status
import redis.asyncio as redis

from ..core.config import settings
from ..models.stream import StreamPayload

router = APIRouter()

redis_client = redis.from_url(settings.redis_url)


@router.post("/stream/{device_id}", status_code=status.HTTP_202_ACCEPTED)
async def ingest_stream(device_id: str, payload: StreamPayload) -> None:
    channel = f"stream:{device_id}"
    await redis_client.publish(channel, payload.model_dump_json())

