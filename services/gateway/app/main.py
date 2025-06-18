from fastapi import FastAPI
from httpx import AsyncClient
from .core.config import settings

app = FastAPI(title="Gateway")


@app.get("/v1/health")
async def health() -> dict[str, str]:
    async with AsyncClient(base_url=settings.auth_api_url) as client:
        await client.get("/v1/health")
    return {"db": "ok"}
