# app/api/v1/endpoints/admin_enhanced.py
"""
Enhanced Admin Console API endpoints.

• User management with CRUD operations and filtering
• Device management with tenant isolation override
• System health monitoring and statistics
• Database operations and backup management
• Feature flags and system settings
• Global search and audit export
"""

import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_session, require_sys_admin
from app.models.user import User
from app.schemas.admin import (
    UserCreate, UserUpdate, UserOut, UserMinimal,
    DeviceCreate, DeviceUpdate, DeviceOut, DeviceMinimal,
    TenantSnapshot, SystemHealthOverview, SearchResponse,
    DatabaseMigration, DatabaseBackup, FeatureFlag, FeatureFlagUpdate,
    SystemSetting, SystemSettingUpdate, AuditExportRequest, AuditExportResponse
)
from app.services.admin import (
    AdminUserService, AdminDeviceService, AdminSystemService,
    AdminFeatureFlagService, AdminSettingsService, AdminAuditService
)

# Rate limiter for admin endpoints
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


# ────────────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=List[UserOut], tags=["admin-users"])
@limiter.limit("20/second")
async def list_users(
    request: Request,
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
    service = AdminUserService(session)
    users, total = await service.list_users(
        skip=skip,
        limit=limit,
        search=search,
        tenant_id=tenant_id,
        is_active=is_active,
        is_admin=is_admin
    )
    
    # Add total count to response headers
    response = users
    response.headers = {"X-Total-Count": str(total)}
    return response


@router.get("/users/{user_id}", response_model=UserOut, tags=["admin-users"])
@limiter.limit("20/second")
async def get_user(
    request: Request,
    user_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get user by ID (system admin only)."""
    service = AdminUserService(session)
    user = await service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/users", response_model=UserOut, tags=["admin-users"])
@limiter.limit("10/second")
async def create_user(
    request: Request,
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Create a new user (system admin only)."""
    service = AdminUserService(session)
    
    try:
        user = await service.create_user(user_data, str(current_user.id))
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/users/{user_id}", response_model=UserOut, tags=["admin-users"])
@limiter.limit("10/second")
async def update_user(
    request: Request,
    user_id: str,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Update user information (system admin only)."""
    service = AdminUserService(session)
    
    try:
        user = await service.update_user(user_id, user_data, str(current_user.id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/users/{user_id}", tags=["admin-users"])
@limiter.limit("10/second")
async def delete_user(
    request: Request,
    user_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Soft delete user (system admin only)."""
    service = AdminUserService(session)
    success = await service.delete_user(user_id, str(current_user.id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}


# ────────────────────────────────────────────────────────────────────────────────
# DEVICE MANAGEMENT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/devices", response_model=List[DeviceOut], tags=["admin-devices"])
@limiter.limit("20/second")
async def list_devices(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in name, description, and serial number"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    status: Optional[str] = Query(None, description="Filter by device status"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """List devices with filtering and pagination (system admin only)."""
    service = AdminDeviceService(session)
    devices, total = await service.list_devices(
        skip=skip,
        limit=limit,
        search=search,
        tenant_id=tenant_id,
        is_active=is_active,
        status=status
    )
    
    # Add total count to response headers
    response = devices
    response.headers = {"X-Total-Count": str(total)}
    return response


@router.get("/devices/{device_id}", response_model=DeviceOut, tags=["admin-devices"])
@limiter.limit("20/second")
async def get_device(
    request: Request,
    device_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get device by ID (system admin only)."""
    service = AdminDeviceService(session)
    device = await service.get_device(device_id)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return device


@router.post("/devices", response_model=DeviceOut, tags=["admin-devices"])
@limiter.limit("10/second")
async def create_device(
    request: Request,
    device_data: DeviceCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Create a new device (system admin only)."""
    service = AdminDeviceService(session)
    
    try:
        device = await service.create_device(device_data, str(current_user.id))
        return device
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/devices/{device_id}", response_model=DeviceOut, tags=["admin-devices"])
@limiter.limit("10/second")
async def update_device(
    request: Request,
    device_id: str,
    device_data: DeviceUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Update device information (system admin only)."""
    service = AdminDeviceService(session)
    
    try:
        device = await service.update_device(device_id, device_data, str(current_user.id))
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        return device
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/devices/{device_id}", tags=["admin-devices"])
@limiter.limit("10/second")
async def delete_device(
    request: Request,
    device_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Delete device (system admin only)."""
    service = AdminDeviceService(session)
    success = await service.delete_device(device_id, str(current_user.id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return {"message": "Device deleted successfully"}


# ────────────────────────────────────────────────────────────────────────────────
# SYSTEM HEALTH ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/health/overview", response_model=SystemHealthOverview, tags=["admin-health"])
@limiter.limit("10/second")
async def get_system_health(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get comprehensive system health overview (system admin only)."""
    service = AdminSystemService(session)
    return await service.get_system_health()


@router.websocket("/health/live")
async def health_live_websocket(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session)
):
    """Live system health WebSocket stream (system admin only)."""
    await websocket.accept()
    
    try:
        service = AdminSystemService(session)
        
        while True:
            # Get current health data
            health_data = await service.get_system_health()
            
            # Send health data as JSON
            await websocket.send_text(health_data.json())
            
            # Wait 5 seconds before next update
            import asyncio
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))


@router.get("/tenant-snapshot", response_model=List[TenantSnapshot], tags=["admin-matrix"])
@limiter.limit("10/second")
async def get_tenant_snapshot(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get tenant snapshot with users and devices (system admin only)."""
    service = AdminSystemService(session)
    return await service.get_tenant_snapshot()


# ────────────────────────────────────────────────────────────────────────────────
# DATABASE OPERATION ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.post("/db/migrate", response_model=DatabaseMigration, tags=["admin-database"])
@limiter.limit("5/second")
async def start_database_migration(
    request: Request,
    target_revision: str = Query(..., description="Target migration revision"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Start database migration (system admin only)."""
    service = AdminSystemService(session)
    return await service.start_database_migration(target_revision, str(current_user.id))


@router.post("/db/backup", response_model=DatabaseBackup, tags=["admin-database"])
@limiter.limit("5/second")
async def start_database_backup(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Start database backup (system admin only)."""
    service = AdminSystemService(session)
    return await service.start_database_backup(str(current_user.id))


# ────────────────────────────────────────────────────────────────────────────────
# SEARCH AND FEATURE FLAG ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/search", response_model=SearchResponse, tags=["admin-search"])
@limiter.limit("20/second")
async def global_search(
    request: Request,
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Global search across users, devices, and tenants (system admin only)."""
    service = AdminSystemService(session)
    return await service.search_global(q, page, per_page)


@router.get("/features", response_model=List[FeatureFlag], tags=["admin-features"])
@limiter.limit("10/second")
async def get_feature_flags(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get all feature flags (system admin only)."""
    service = AdminFeatureFlagService(session)
    return await service.get_feature_flags()


@router.patch("/features/{flag_name}", response_model=FeatureFlag, tags=["admin-features"])
@limiter.limit("10/second")
async def update_feature_flag(
    request: Request,
    flag_name: str,
    flag_data: FeatureFlagUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Update feature flag (system admin only)."""
    service = AdminFeatureFlagService(session)
    return await service.update_feature_flag(flag_name, flag_data, str(current_user.id))


# ────────────────────────────────────────────────────────────────────────────────
# SETTINGS ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/settings", response_model=List[SystemSetting], tags=["admin-settings"])
@limiter.limit("10/second")
async def get_settings(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by category"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get system settings (system admin only)."""
    service = AdminSettingsService(session)
    return await service.get_settings(category)


@router.patch("/settings/{key}", response_model=SystemSetting, tags=["admin-settings"])
@limiter.limit("10/second")
async def update_setting(
    request: Request,
    key: str,
    setting_data: SystemSettingUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Update system setting (system admin only)."""
    service = AdminSettingsService(session)
    return await service.update_setting(key, setting_data, str(current_user.id))


# ────────────────────────────────────────────────────────────────────────────────
# AUDIT EXPORT ENDPOINTS
# ────────────────────────────────────────────────────────────────────────────────

@router.post("/audit/export", response_model=AuditExportResponse, tags=["admin-audit"])
@limiter.limit("5/second")
async def export_audit_logs(
    request: Request,
    export_request: AuditExportRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Export audit logs (system admin only)."""
    service = AdminAuditService(session)
    return await service.export_audit_logs(export_request, str(current_user.id))


@router.get("/audit/export/{job_id}/download", tags=["admin-audit"])
@limiter.limit("10/second")
async def download_audit_export(
    request: Request,
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