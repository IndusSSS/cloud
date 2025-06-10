# File services/auth-api/app/routes/devices.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models    import Device
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceOut
from app.security import get_current_tenant, TokenData

router = APIRouter(tags=["devices"])

# ─── LIST ────────────────────────────────────────────────────
@router.get("/", response_model=list[DeviceOut], summary="List devices")
async def list_devices(
    token: TokenData = Depends(get_current_tenant),
    db:    AsyncSession = Depends(get_session),
):
    stmt = select(Device).where(Device.tenant_id == token.tenant_id)
    res  = await db.execute(stmt)
    return res.scalars().all()


# ─── CREATE ──────────────────────────────────────────────────
@router.post(
    "/",
    response_model=DeviceOut,
    status_code=201,
    summary="Create a new device",
)
async def create_device(
    data:  DeviceCreate,
    token: TokenData    = Depends(get_current_tenant),
    db:    AsyncSession = Depends(get_session),
):
    new = Device(
        tenant_id=token.tenant_id,
        name=data.name,
        status="offline",
    )
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new


# (Later you can add GET /{id}, PATCH /{id}, DELETE /{id} here)
