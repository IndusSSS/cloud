import asyncio
import json

import pytest
import websockets
from redis.asyncio import Redis
from testcontainers.redis import RedisContainer
import uvicorn

from app.main import app
from app.core import config as config_module


@pytest.mark.asyncio
async def test_websocket_stream() -> None:
    with RedisContainer() as redis_container:
        config_module.settings.redis_url = redis_container.get_connection_url()
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8765, log_level="info"))
        task = asyncio.create_task(server.serve())
        await asyncio.sleep(0.5)

        redis_client = Redis.from_url(config_module.settings.redis_url)
        ws = await websockets.connect("ws://127.0.0.1:8765/ws/stream/device1")

        await redis_client.publish("stream:device1", json.dumps({"ts": "2025-06-19T09:41:15Z", "type": "temperature", "value": 42, "unit": "C"}))
        data = json.loads(await ws.recv())
        assert data["value"] == 42

        await ws.close()
        server.should_exit = True
        await task
        await redis_client.close()

