from __future__ import annotations

import asyncio
import time
from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis

from ..core.config import settings

redis_client = redis.from_url(settings.redis_url)


async def stream_ws(websocket: WebSocket, device_id: str) -> None:
    await websocket.accept()
    pubsub = redis_client.pubsub()
    channel = f"stream:{device_id}"
    await pubsub.subscribe(channel)
    last_activity = time.monotonic()

    async def ping_loop() -> None:
        nonlocal last_activity
        while True:
            await asyncio.sleep(30)
            if time.monotonic() - last_activity > 120:
                await websocket.close()
                break
            await websocket.send_json({"type": "ping"})

    async def forward_loop() -> None:
        nonlocal last_activity
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    await websocket.send_text(message["data"].decode())
                    last_activity = time.monotonic()
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

    ping_task = asyncio.create_task(ping_loop())
    forward_task = asyncio.create_task(forward_loop())
    try:
        await asyncio.gather(ping_task, forward_task)
    except WebSocketDisconnect:
        ping_task.cancel()
        forward_task.cancel()
        await pubsub.unsubscribe(channel)
        await pubsub.close()

