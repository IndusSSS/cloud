# app/api/v1/endpoints/devices_admin.py
"""
Admin device management endpoints.

• CRUD operations for IoT devices with specifications.
• Device status monitoring and configuration.
• Tenant-scoped device administration.
"""

import json
from typing import Any, List, Optional, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.deps import get_session, get_current_user, require_admin
from app.models.device import Device
from app.models.user import User
from app.core.rbac import log_audit_event

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_devices(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> Any:
    """Get list of devices for current tenant."""
    statement = select(Device).where(Device.tenant_id == current_user.tenant_id)
    statement = statement.offset(skip).limit(limit)
    result = await session.execute(statement)
    devices = result.scalars().all()
    
    return [
        {
            "id": str(device.id),
            "name": device.name,
            "description": device.description,
            "specifications": device.specifications,
            "is_active": device.is_active
        }
        for device in devices
    ]


@router.post("/")
async def create_device(
    request: Request,
    name: str,
    description: Optional[str] = None,
    specifications: Optional[Dict[str, Any]] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> Any:
    """Create a new device."""
    # Check if device name already exists in tenant
    existing = await session.execute(
        select(Device).where(
            Device.name == name,
            Device.tenant_id == current_user.tenant_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device name already exists in tenant"
        )
    
    device = Device(
        name=name,
        description=description,
        specifications=json.dumps(specifications) if specifications else None,
        tenant_id=current_user.tenant_id
    )
    session.add(device)
    await session.commit()
    await session.refresh(device)
    
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="create",
        resource_type="device",
        resource_id=str(device.id),
        details={"name": name, "description": description}
    )
    
    return {
        "id": str(device.id),
        "name": device.name,
        "description": device.description,
        "specifications": device.specifications,
        "is_active": device.is_active
    }


@router.get("/{device_id}")
async def get_device(
    device_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get device by ID."""
    statement = select(Device).where(Device.id == device_id)
    result = await session.execute(statement)
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Check if device belongs to user's tenant
    if device.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return {
        "id": str(device.id),
        "name": device.name,
        "description": device.description,
        "specifications": device.specifications,
        "is_active": device.is_active
    }


@router.put("/{device_id}")
async def update_device(
    request: Request,
    device_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    specifications: Optional[Dict[str, Any]] = None,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> Any:
    """Update device information."""
    statement = select(Device).where(Device.id == device_id)
    result = await session.execute(statement)
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Check if device belongs to user's tenant
    if device.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if new name conflicts with existing device in tenant
    if name and name != device.name:
        existing = await session.execute(
            select(Device).where(
                Device.name == name,
                Device.tenant_id == current_user.tenant_id,
                Device.id != device_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device name already exists in tenant"
            )
    
    if name is not None:
        device.name = name
    if description is not None:
        device.description = description
    if specifications is not None:
        device.specifications = json.dumps(specifications)
    if is_active is not None:
        device.is_active = is_active
    
    session.add(device)
    await session.commit()
    await session.refresh(device)
    
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="update",
        resource_type="device",
        resource_id=str(device_id),
        details={"name": name, "description": description, "is_active": is_active}
    )
    
    return {
        "id": str(device.id),
        "name": device.name,
        "description": device.description,
        "specifications": device.specifications,
        "is_active": device.is_active
    }


@router.delete("/{device_id}")
async def delete_device(
    request: Request,
    device_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> Any:
    """Delete device."""
    statement = select(Device).where(Device.id == device_id)
    result = await session.execute(statement)
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Check if device belongs to user's tenant
    if device.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await session.delete(device)
    await session.commit()
    
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="delete",
        resource_type="device",
        resource_id=str(device_id),
        details={"name": device.name}
    )
    
    return {"message": "Device deleted successfully"} 