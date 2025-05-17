# File: backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routes.metrics import router as metrics_router

app = FastAPI(title="SmartSecurity API", version="0.1.0")
# allow requests from your Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# mount metrics router after the app exists
app.include_router(metrics_router)

# Health-check route
@app.get("/v1/health", tags=["health"])
async def health():
    return {"status": "ok"}
