from fastapi import FastAPI

from .api.routes import router as api_router
from .routes.stream import router as stream_router

app = FastAPI(title="Device API", version="0.1.0")
app.include_router(api_router, prefix="/v1")
app.include_router(stream_router, prefix="/v1")


@app.get("/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
