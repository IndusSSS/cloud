# app/api/v1/endpoints/devices.py
"""
Device management endpoints.

• CRUD operations for IoT devices.
• Device status monitoring.
• Device registration and configuration.
"""

from typing import Any, List, Optional, Dict
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlmodel import Session, select

from app.api.deps import get_session, get_current_user, log_audit_event
from app.models.device import Device
from app.models.sensor import SensorData
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[dict], tags=["Customer"])
def get_devices(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get list of devices for current tenant."""
    statement = select(Device).where(Device.tenant_id == current_user.tenant_id)
    statement = statement.offset(skip).limit(limit)
    devices = session.exec(statement).all()
    
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
def create_device(
    name: str,
    description: Optional[str] = None,
    specifications: Optional[Dict[str, Any]] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None
) -> Any:
    """Create a new device."""
    # Check if device name already exists in tenant
    existing = session.exec(
        select(Device).where(
            Device.name == name,
            Device.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device name already exists in tenant"
        )
    
    device = Device(
        name=name,
        description=description,
        specifications=specifications,
        tenant_id=current_user.tenant_id
    )
    session.add(device)
    session.commit()
    session.refresh(device)
    
    if request:
        log_audit_event(
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


@router.get("/{device_id}", tags=["Customer"])
def get_device(
    device_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get device by ID."""
    statement = select(Device).where(Device.id == device_id)
    device = session.exec(statement).first()
    
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


@router.put("/{device_id}", tags=["Customer"])
def update_device(
    device_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    specifications: Optional[Dict[str, Any]] = None,
    is_active: Optional[bool] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None
) -> Any:
    """Update device information."""
    statement = select(Device).where(Device.id == device_id)
    device = session.exec(statement).first()
    
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
        existing = session.exec(
            select(Device).where(
                Device.name == name,
                Device.tenant_id == current_user.tenant_id,
                Device.id != device_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device name already exists in tenant"
            )
    
    if name is not None:
        device.name = name
    if description is not None:
        device.description = description
    if specifications is not None:
        device.specifications = specifications
    if is_active is not None:
        device.is_active = is_active
    
    session.add(device)
    session.commit()
    session.refresh(device)
    
    if request:
        log_audit_event(
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


@router.delete("/{device_id}", tags=["Customer"])
def delete_device(
    device_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None
) -> Any:
    """Delete device."""
    statement = select(Device).where(Device.id == device_id)
    device = session.exec(statement).first()
    
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
    
    session.delete(device)
    session.commit()
    
    if request:
        log_audit_event(
            request=request,
            session=session,
            user=current_user,
            action="delete",
            resource_type="device",
            resource_id=str(device_id),
            details={"name": device.name}
        )
    
    return {"message": "Device deleted successfully"}


@router.get("/{device_id}/sensor-data", tags=["Customer"])
def get_device_sensor_data(
    device_id: UUID,
    from_time: Optional[datetime] = Query(None, description="Start time for data range"),
    to_time: Optional[datetime] = Query(None, description="End time for data range"),
    limit: int = Query(100, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get sensor data history for a specific device."""
    # First verify the device belongs to the user's tenant
    device = session.exec(
        select(Device).where(
            Device.id == device_id,
            Device.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Build query for sensor data
    query = select(SensorData).where(SensorData.device_id == str(device_id))
    
    # Add time range filters if provided
    if from_time:
        query = query.where(SensorData.timestamp >= from_time)
    if to_time:
        query = query.where(SensorData.timestamp <= to_time)
    
    # Order by timestamp descending and limit results
    query = query.order_by(SensorData.timestamp.desc()).limit(limit)
    
    sensor_data = session.exec(query).all()
    
    return {
        "device_id": str(device_id),
        "device_name": device.name,
        "data": [
            {
                "id": str(data.id),
                "payload": data.payload,
                "timestamp": data.timestamp.isoformat(),
                "created_at": data.created_at.isoformat()
            }
            for data in sensor_data
        ],
        "total": len(sensor_data)
    }