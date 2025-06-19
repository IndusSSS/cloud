from fastapi import FastAPI
from .api.routes import router as api_router
from .routes.metrics import router as metrics_router
from .consumers.stream_consumer import consume_streams

app = FastAPI(title="Metrics API", version="0.1.0")
app.include_router(api_router, prefix="/v1")
app.include_router(metrics_router, prefix="/v1")


@app.on_event("startup")
async def start_consumer() -> None:
    import asyncio
    asyncio.create_task(consume_streams())


@app.get("/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
