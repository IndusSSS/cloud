from fastapi import FastAPI
from .api.routes import router

app = FastAPI(title="Device API")
app.include_router(router, prefix="/v1")


@app.get("/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
