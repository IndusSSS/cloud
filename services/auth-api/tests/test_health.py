import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health() -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
