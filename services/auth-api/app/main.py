from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

from .api.routes import router

limiter = Limiter(key_func=get_remote_address)

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
]

app = FastAPI(title="Auth API", middleware=middleware)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

app.include_router(router, prefix="/v1/auth")


@app.get("/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
