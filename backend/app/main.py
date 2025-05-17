# File: backend/app/main.py
from fastapi import FastAPI

app = FastAPI(title="SmartSecurity API", version="0.1.0")

# Health-check route
@app.get("/v1/health", tags=["health"])
async def health():
    return {"status": "ok"}
