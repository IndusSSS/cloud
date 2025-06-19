import json
from datetime import datetime

import pytest
from httpx import AsyncClient
from redis.asyncio import Redis
from testcontainers.redis import RedisContainer

from app.main import app
from app.core import config as config_module


@pytest.mark.asyncio
async def test_ingest_publishes() -> None:
    with RedisContainer() as redis_container:
        config_module.settings.redis_url = redis_container.get_connection_url()
        redis_client = Redis.from_url(config_module.settings.redis_url)
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("stream:device1")

        async with AsyncClient(app=app, base_url="http://test") as ac:
            payload = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "type": "temperature",
                "value": 25.0,
                "unit": "C",
            }
            resp = await ac.post("/v1/stream/device1", json=payload)
            assert resp.status_code == 202

        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=2.0)
        assert message is not None
        data = json.loads(message["data"].decode())
        assert data["type"] == "temperature"

        await pubsub.unsubscribe("stream:device1")
        await pubsub.close()
        await redis_client.close()


from app.models.stream import StreamPayload


def test_model_validation() -> None:
    data = {
        "ts": "2025-06-19T09:41:15Z",
        "type": "humidity",
        "value": 50.1,
        "unit": "%",
    }
    payload = StreamPayload(**data)
    assert payload.type == "humidity"
