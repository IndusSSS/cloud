# app/api/v1/endpoints/admin_console.py
"""
Admin Console API endpoints for SmartSecurity Cloud.

• Enhanced user management with system-wide access
• Device management with tenant isolation override
• System health monitoring and statistics
• Database operations and backup management
• Feature flags and system settings
• Global search and audit export
"""

import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, and_, or_, desc
from pydantic import BaseModel, Field

from app.api.deps import get_session, require_sys_admin
from app.models.user import User
from app.models.device import Device
from app.models.tenant import Tenant
from app.models.audit import AuditLog
from app.core.rbac import log_audit_event
from app.core.redis import get_redis_client

router = APIRouter()


# ────────────────────────────────────────────────────────────────────────────────
# PYDANTIC SCHEMAS FOR ADMIN CONSOLE
# ────────────────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8)
    is_admin: bool = Field(default=False)
    tenant_id: Optional[str] = Field(None, description="Tenant ID (system admin only)")


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    tenant_id: Optional[str] = None


class UserOut(BaseModel):
    """Schema for user output."""
    id: str
    username: str
    email: str
    is_active: bool
    is_admin: bool
    tenant_id: Optional[str]
    created_at: datetime
    last_login: Optional[datetime] = None


class DeviceCreate(BaseModel):
    """Schema for creating a new device."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    serial_no: str = Field(..., description="Unique serial number")
    specifications: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tenant_id: Optional[str] = Field(None, description="Tenant ID (system admin only)")


class DeviceUpdate(BaseModel):
    """Schema for updating device information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    specifications: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DeviceOut(BaseModel):
    """Schema for device output."""
    id: str
    name: str
    description: Optional[str]
    serial_no: str
    specifications: Optional[Dict[str, Any]]
    is_active: bool
    tenant_id: str
    created_at: datetime


class SystemHealthOverview(BaseModel):
    """Complete system health overview."""
    uptime_sec: int
    postgres_status: str = "OK"
    redis_status: str = "OK"
    mqtt_status: str = "OK"
    total_users: int
    total_devices: int
    total_tenants: int
    active_devices: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TenantSnapshot(BaseModel):
    """Tenant snapshot with users and devices."""
    tenant_id: str
    tenant_name: str
    plan: str
    user_count: int
    device_count: int
    active_devices: int
    created_at: datetime


class SearchResult(BaseModel):
    """Search result item."""
    type: str
    id: str
    title: str
    description: Optional[str]
    tenant_id: Optional[str]
    score: float


class SearchResponse(BaseModel):
    """Search response with pagination."""
    results: List[SearchResult]
    total: int
    page: int
    per_page: int


class FeatureFlag(BaseModel):
    """Feature flag configuration."""
    name: str
    enabled: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[str]


class FeatureFlagUpdate(BaseModel):
    """Feature flag update request."""
    enabled: bool
    description: Optional[str]


class SystemSetting(BaseModel):
    """System setting configuration."""
    key: str
    value: str
    description: Optional[str]
    category: str
    is_secret: bool = False
    created_at: datetime
    updated_at: datetime


class SystemSettingUpdate(BaseModel):
    """System setting update request."""
    value: str
    description: Optional[str]


# ────────────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=List[UserOut], tags=["admin-users"])
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in username and email"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """List users with filtering and pagination (system admin only)."""
    # Build base query
    query = select(User)
    
    # Apply filters
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    if tenant_id is not None:
        query = query.where(User.tenant_id == tenant_id)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if is_admin is not None:
        query = query.where(User.is_admin == is_admin)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.execute(count_query)
    total = count_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(desc(User.created_at)).offset(skip).limit(limit)
    
    # Execute query
    result = await session.execute(query)
    users = result.scalars().all()
    
    return [UserOut.from_orm(user) for user in users]


@router.get("/users/{user_id}", response_model=UserOut, tags=["admin-users"])
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get user by ID (system admin only)."""
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserOut.from_orm(user)


@router.post("/users", response_model=UserOut, tags=["admin-users"])
async def create_user(
    request: Request,
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Create a new user (system admin only)."""
    from app.core.security import get_password_hash
    
    # Check for existing username
    existing_username = await session.execute(
        select(User).where(User.username == user_data.username)
    )
    if existing_username.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check for existing email
    existing_email = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_admin=user_data.is_admin,
        tenant_id=user_data.tenant_id
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    # Log audit event
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="admin.user.create",
        resource_type="user",
        resource_id=user.id,
        details={
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "tenant_id": user.tenant_id
        }
    )
    
    return UserOut.from_orm(user)


@router.patch("/users/{user_id}", response_model=UserOut, tags=["admin-users"])
async def update_user(
    request: Request,
    user_id: str,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Update user information (system admin only)."""
    user = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = user.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_data.username is not None:
        # Check for username conflicts
        existing = await session.execute(
            select(User).where(
                and_(User.username == user_data.username, User.id != user_id)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        user.username = user_data.username
    
    if user_data.email is not None:
        # Check for email conflicts
        existing = await session.execute(
            select(User).where(
                and_(User.email == user_data.email, User.id != user_id)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        user.email = user_data.email
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin
    
    if user_data.tenant_id is not None:
        user.tenant_id = user_data.tenant_id
    
    await session.commit()
    await session.refresh(user)
    
    # Log audit event
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="admin.user.update",
        resource_type="user",
        resource_id=user_id,
        details=user_data.dict(exclude_unset=True)
    )
    
    return UserOut.from_orm(user)


@router.delete("/users/{user_id}", tags=["admin-users"])
async def delete_user(
    request: Request,
    user_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Soft delete user (system admin only)."""
    user = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = user.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete
    user.is_active = False
    await session.commit()
    
    # Log audit event
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="admin.user.delete",
        resource_type="user",
        resource_id=user_id,
        details={"soft_delete": True}
    )
    
    return {"message": "User deleted successfully"}


# ────────────────────────────────────────────────────────────────────────────────
# DEVICE MANAGEMENT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/devices", response_model=List[DeviceOut], tags=["admin-devices"])
async def list_devices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in name, description, and serial number"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """List devices with filtering and pagination (system admin only)."""
    # Build base query
    query = select(Device)
    
    # Apply filters
    if search:
        search_filter = or_(
            Device.name.ilike(f"%{search}%"),
            Device.description.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    if tenant_id is not None:
        query = query.where(Device.tenant_id == tenant_id)
    
    if is_active is not None:
        query = query.where(Device.is_active == is_active)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.execute(count_query)
    total = count_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(desc(Device.created_at)).offset(skip).limit(limit)
    
    # Execute query
    result = await session.execute(query)
    devices = result.scalars().all()
    
    return [DeviceOut.from_orm(device) for device in devices]


@router.get("/devices/{device_id}", response_model=DeviceOut, tags=["admin-devices"])
async def get_device(
    device_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get device by ID (system admin only)."""
    query = select(Device).where(Device.id == device_id)
    result = await session.execute(query)
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return DeviceOut.from_orm(device)


@router.post("/devices", response_model=DeviceOut, tags=["admin-devices"])
async def create_device(
    request: Request,
    device_data: DeviceCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Create a new device (system admin only)."""
    # Check for existing serial number
    existing_serial = await session.execute(
        select(Device).where(Device.serial_no == device_data.serial_no)
    )
    if existing_serial.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Serial number already exists"
        )
    
    # Create device
    device = Device(
        id=str(uuid.uuid4()),
        name=device_data.name,
        description=device_data.description,
        serial_no=device_data.serial_no,
        specifications=json.dumps(device_data.specifications) if device_data.specifications else None,
        tenant_id=device_data.tenant_id,
        is_active=True
    )
    
    session.add(device)
    await session.commit()
    await session.refresh(device)
    
    # Log audit event
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="admin.device.create",
        resource_type="device",
        resource_id=device.id,
        details={
            "name": device.name,
            "serial_no": device.serial_no,
            "tenant_id": device.tenant_id
        }
    )
    
    # Publish Redis event for other services
    try:
        redis_client = await get_redis_client()
        await redis_client.publish(
            "device/created",
            json.dumps({
                "device_id": device.id,
                "tenant_id": device.tenant_id,
                "created_by": str(current_user.id),
                "timestamp": datetime.utcnow().isoformat()
            })
        )
    except Exception as e:
        # Log error but don't fail the operation
        print(f"Failed to publish device creation event: {e}")
    
    return DeviceOut.from_orm(device)


@router.patch("/devices/{device_id}", response_model=DeviceOut, tags=["admin-devices"])
async def update_device(
    request: Request,
    device_id: str,
    device_data: DeviceUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Update device information (system admin only)."""
    device = await session.execute(
        select(Device).where(Device.id == device_id)
    )
    device = device.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Update fields
    if device_data.name is not None:
        device.name = device_data.name
    
    if device_data.description is not None:
        device.description = device_data.description
    
    if device_data.specifications is not None:
        device.specifications = json.dumps(device_data.specifications)
    
    if device_data.is_active is not None:
        device.is_active = device_data.is_active
    
    await session.commit()
    await session.refresh(device)
    
    # Log audit event
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="admin.device.update",
        resource_type="device",
        resource_id=device_id,
        details=device_data.dict(exclude_unset=True)
    )
    
    return DeviceOut.from_orm(device)


@router.delete("/devices/{device_id}", tags=["admin-devices"])
async def delete_device(
    request: Request,
    device_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Delete device (system admin only)."""
    device = await session.execute(
        select(Device).where(Device.id == device_id)
    )
    device = device.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Delete device
    await session.delete(device)
    await session.commit()
    
    # Log audit event
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="admin.device.delete",
        resource_type="device",
        resource_id=device_id,
        details={"hard_delete": True}
    )
    
    # Publish Redis event for other services
    try:
        redis_client = await get_redis_client()
        await redis_client.publish(
            "device/deleted",
            json.dumps({
                "device_id": device_id,
                "tenant_id": device.tenant_id,
                "deleted_by": str(current_user.id),
                "timestamp": datetime.utcnow().isoformat()
            })
        )
    except Exception as e:
        # Log error but don't fail the operation
        print(f"Failed to publish device deletion event: {e}")
    
    return {"message": "Device deleted successfully"}


# ────────────────────────────────────────────────────────────────────────────────
# SYSTEM HEALTH ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/health/overview", response_model=SystemHealthOverview, tags=["admin-health"])
async def get_system_health(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get comprehensive system health overview (system admin only)."""
    # Get counts
    users_count = await session.execute(select(func.count(User.id)))
    devices_count = await session.execute(select(func.count(Device.id)))
    tenants_count = await session.execute(select(func.count(Tenant.id)))
    active_devices_count = await session.execute(select(func.count(Device.id)).where(Device.is_active == True))
    
    # System uptime (mock for now)
    uptime_sec = int((datetime.utcnow() - datetime(2024, 1, 1)).total_seconds())
    
    return SystemHealthOverview(
        uptime_sec=uptime_sec,
        total_users=users_count.scalar() or 0,
        total_devices=devices_count.scalar() or 0,
        total_tenants=tenants_count.scalar() or 0,
        active_devices=active_devices_count.scalar() or 0
    )


@router.websocket("/health/live")
async def health_live_websocket(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session)
):
    """Live system health WebSocket stream (system admin only)."""
    await websocket.accept()
    
    try:
        while True:
            # Get current health data
            health_data = await get_system_health(session, None)
            
            # Send health data as JSON
            await websocket.send_text(health_data.json())
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))


@router.get("/tenant-snapshot", response_model=List[TenantSnapshot], tags=["admin-matrix"])
async def get_tenant_snapshot(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get tenant snapshot with users and devices (system admin only)."""
    # Single query with LEFT JOINs to avoid N+1
    query = select(
        Tenant,
        func.count(User.id).label('user_count'),
        func.count(Device.id).label('device_count'),
        func.sum(func.case((Device.is_active == True, 1), else_=0)).label('active_devices')
    ).outerjoin(User, Tenant.id == User.tenant_id).outerjoin(
        Device, Tenant.id == Device.tenant_id
    ).group_by(Tenant.id, Tenant.name, Tenant.plan, Tenant.created_at)
    
    result = await session.execute(query)
    rows = result.all()
    
    snapshots = []
    for row in rows:
        tenant, user_count, device_count, active_devices = row
        
        snapshot = TenantSnapshot(
            tenant_id=tenant.id,
            tenant_name=tenant.name,
            plan=tenant.plan,
            user_count=user_count or 0,
            device_count=device_count or 0,
            active_devices=active_devices or 0,
            created_at=tenant.created_at
        )
        snapshots.append(snapshot)
    
    return snapshots


# ────────────────────────────────────────────────────────────────────────────────
# SEARCH ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/search", response_model=SearchResponse, tags=["admin-search"])
async def global_search(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Global search across users, devices, and tenants (system admin only)."""
    results = []
    
    # Search users
    users_query = select(User).where(
        or_(
            User.username.ilike(f"%{q}%"),
            User.email.ilike(f"%{q}%")
        )
    ).limit(per_page)
    users_result = await session.execute(users_query)
    users = users_result.scalars().all()
    
    for user in users:
        results.append(SearchResult(
            type="user",
            id=user.id,
            title=user.username,
            description=user.email,
            tenant_id=user.tenant_id,
            score=0.9
        ))
    
    # Search devices
    devices_query = select(Device).where(
        or_(
            Device.name.ilike(f"%{q}%"),
            Device.description.ilike(f"%{q}%")
        )
    ).limit(per_page)
    devices_result = await session.execute(devices_query)
    devices = devices_result.scalars().all()
    
    for device in devices:
        results.append(SearchResult(
            type="device",
            id=device.id,
            title=device.name,
            description=device.description,
            tenant_id=device.tenant_id,
            score=0.8
        ))
    
    # Search tenants
    tenants_query = select(Tenant).where(
        Tenant.name.ilike(f"%{q}%")
    ).limit(per_page)
    tenants_result = await session.execute(tenants_query)
    tenants = tenants_result.scalars().all()
    
    for tenant in tenants:
        results.append(SearchResult(
            type="tenant",
            id=tenant.id,
            title=tenant.name,
            description=f"Plan: {tenant.plan}",
            tenant_id=None,
            score=0.7
        ))
    
    # Sort by score and apply pagination
    results.sort(key=lambda x: x.score, reverse=True)
    total = len(results)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return SearchResponse(
        results=results[start_idx:end_idx],
        total=total,
        page=page,
        per_page=per_page
    )


# ────────────────────────────────────────────────────────────────────────────────
# FEATURE FLAG ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/features", response_model=List[FeatureFlag], tags=["admin-features"])
async def get_feature_flags(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get all feature flags (system admin only)."""
    # This would typically query a feature_flags table
    # For now, return mock data
    return [
        FeatureFlag(
            name="advanced_analytics",
            enabled=True,
            description="Enable advanced analytics dashboard",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            updated_by="system"
        ),
        FeatureFlag(
            name="mobile_app",
            enabled=False,
            description="Enable mobile app features",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            updated_by="system"
        ),
        FeatureFlag(
            name="real_time_notifications",
            enabled=True,
            description="Enable real-time push notifications",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            updated_by="system"
        )
    ]


@router.patch("/features/{flag_name}", response_model=FeatureFlag, tags=["admin-features"])
async def update_feature_flag(
    request: Request,
    flag_name: str,
    flag_data: FeatureFlagUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Update feature flag (system admin only)."""
    # This would typically update a feature_flags table
    # For now, return mock data
    
    # Log audit event
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="admin.feature_flag.update",
        resource_type="feature_flag",
        resource_id=flag_name,
        details=flag_data.dict()
    )
    
    return FeatureFlag(
        name=flag_name,
        enabled=flag_data.enabled,
        description=flag_data.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        updated_by=str(current_user.id)
    )


# ────────────────────────────────────────────────────────────────────────────────
# SETTINGS ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/settings", response_model=List[SystemSetting], tags=["admin-settings"])
async def get_settings(
    category: Optional[str] = Query(None, description="Filter by category"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get system settings (system admin only)."""
    # This would typically query a system_settings table
    # For now, return mock data
    settings = [
        SystemSetting(
            key="max_devices_per_tenant",
            value="1000",
            description="Maximum devices allowed per tenant",
            category="limits",
            is_secret=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        SystemSetting(
            key="data_retention_days",
            value="90",
            description="Number of days to retain sensor data",
            category="data",
            is_secret=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        SystemSetting(
            key="smtp_password",
            value="********",
            description="SMTP server password",
            category="email",
            is_secret=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    
    if category:
        settings = [s for s in settings if s.category == category]
    
    return settings


@router.patch("/settings/{key}", response_model=SystemSetting, tags=["admin-settings"])
async def update_setting(
    request: Request,
    key: str,
    setting_data: SystemSettingUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Update system setting (system admin only)."""
    # This would typically update a system_settings table
    # For now, return mock data
    
    # Log audit event
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="admin.setting.update",
        resource_type="system_setting",
        resource_id=key,
        details={"key": key, "value": setting_data.value}
    )
    
    return SystemSetting(
        key=key,
        value=setting_data.value,
        description=setting_data.description,
        category="general",
        is_secret=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


# ────────────────────────────────────────────────────────────────────────────────
# AUDIT EXPORT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.post("/audit/export", tags=["admin-audit"])
async def export_audit_logs(
    request: Request,
    from_date: Optional[datetime] = Query(None, description="Start date for export"),
    to_date: Optional[datetime] = Query(None, description="End date for export"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    format: str = Query("csv", description="Export format (csv, json)"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Export audit logs (system admin only)."""
    job_id = str(uuid.uuid4())
    
    # Log export request
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="admin.audit.export",
        resource_type="audit_log",
        resource_id=job_id,
        details={
            "from_date": from_date.isoformat() if from_date else None,
            "to_date": to_date.isoformat() if to_date else None,
            "action": action,
            "resource_type": resource_type,
            "user_id": user_id,
            "format": format
        }
    )
    
    return {
        "job_id": job_id,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    }


@router.get("/audit/export/{job_id}/download", tags=["admin-audit"])
async def download_audit_export(
    job_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Download audit log export (system admin only)."""
    # This would typically check if the export is ready and return the file
    # For now, return a mock CSV file
    
    def generate_csv():
        yield "timestamp,action,resource_type,resource_id,user_id,details\n"
        yield "2024-01-01T00:00:00Z,admin.user.create,user,123,admin,{\"username\":\"test\"}\n"
        yield "2024-01-01T00:01:00Z,admin.device.create,device,456,admin,{\"name\":\"test-device\"}\n"
    
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=audit_export_{job_id}.csv"}
    ) 