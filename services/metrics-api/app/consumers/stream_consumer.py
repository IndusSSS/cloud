from __future__ import annotations

import asyncio
import json

import redis.asyncio as redis

from ..core.config import settings
from ..db.session import SessionLocal
from ..models.device_metric import DeviceMetric

redis_client = redis.from_url(settings.redis_url)


async def consume_streams() -> None:
    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("stream:*")
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if not message:
                await asyncio.sleep(0.1)
                continue
            channel = message["channel"].decode()
            device_id = channel.split(":", 1)[1]
            data = json.loads(message["data"].decode())
            metric = DeviceMetric(device_id=device_id, **data)
            async with SessionLocal() as session:
                session.add(metric)
                await session.commit()
    finally:
        await pubsub.close()

