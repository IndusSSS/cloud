from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from common import Device
from ..db.session import get_session

router = APIRouter()


@router.get("/devices")
async def list_devices(session=Depends(get_session)):
    result = await session.execute(select(Device))
    return result.scalars().all()


@router.post("/devices")
async def create_device(device: Device, session=Depends(get_session)):
    session.add(device)
    await session.commit()
    await session.refresh(device)
    return device
