# services/auth-api/app/routes/health.py
from fastapi import APIRouter

router = APIRouter()          # ← this exact name is what main.py imports

@router.get("/v1/health", tags=["health"])
async def health():
    return {"status": "ok"}
