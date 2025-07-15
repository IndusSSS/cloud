# app/services/admin.py
"""
Admin service layer for business logic.

• User management with validation and audit logging
• Device management with tenant isolation override
• System health monitoring and statistics
• Database operations and backup management
"""

import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.admin import (
    UserCreate, UserUpdate, UserOut, UserMinimal,
    DeviceCreate, DeviceUpdate, DeviceOut, DeviceMinimal,
    TenantSnapshot, SystemHealthOverview, SearchResponse,
    DatabaseMigration, DatabaseBackup, FeatureFlag, FeatureFlagUpdate,
    SystemSetting, SystemSettingUpdate, AuditExportRequest, AuditExportResponse
)
from app.repositories.admin import AdminUserRepository, AdminDeviceRepository, AdminSystemRepository
from app.core.rbac import log_audit_event
from app.core.redis import get_redis_client


class AdminUserService:
    """Service for admin user management operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AdminUserRepository(session)
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        tenant_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_admin: Optional[bool] = None
    ) -> Tuple[List[UserOut], int]:
        """List users with filtering and pagination."""
        return await self.repo.fetch_list(
            skip=skip,
            limit=limit,
            search=search,
            tenant_id=tenant_id,
            is_active=is_active,
            is_admin=is_admin
        )
    
    async def get_user(self, user_id: str) -> Optional[UserOut]:
        """Get user by ID."""
        return await self.repo.fetch_by_id(user_id)
    
    async def create_user(self, user_data: UserCreate, created_by: str) -> UserOut:
        """Create a new user with audit logging."""
        try:
            user = await self.repo.create(user_data, created_by)
            
            # Log audit event
            await log_audit_event(
                request=None,  # Will be passed from controller
                session=self.session,
                user_id=created_by,
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
            
            return user
        except ValueError as e:
            raise ValueError(f"User creation failed: {str(e)}")
    
    async def update_user(self, user_id: str, user_data: UserUpdate, updated_by: str) -> Optional[UserOut]:
        """Update user with audit logging."""
        user = await self.repo.update(user_id, user_data, updated_by)
        
        if user:
            # Log audit event
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=updated_by,
                action="admin.user.update",
                resource_type="user",
                resource_id=user_id,
                details=user_data.dict(exclude_unset=True)
            )
        
        return user
    
    async def delete_user(self, user_id: str, deleted_by: str) -> bool:
        """Soft delete user with audit logging."""
        success = await self.repo.delete(user_id, deleted_by)
        
        if success:
            # Log audit event
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=deleted_by,
                action="admin.user.delete",
                resource_type="user",
                resource_id=user_id,
                details={"soft_delete": True}
            )
        
        return success


class AdminDeviceService:
    """Service for admin device management operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AdminDeviceRepository(session)
    
    async def list_devices(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        tenant_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        status: Optional[str] = None
    ) -> Tuple[List[DeviceOut], int]:
        """List devices with filtering and pagination."""
        return await self.repo.fetch_list(
            skip=skip,
            limit=limit,
            search=search,
            tenant_id=tenant_id,
            is_active=is_active,
            status=status
        )
    
    async def get_device(self, device_id: str) -> Optional[DeviceOut]:
        """Get device by ID."""
        return await self.repo.fetch_by_id(device_id)
    
    async def create_device(self, device_data: DeviceCreate, created_by: str) -> DeviceOut:
        """Create a new device with audit logging."""
        try:
            device = await self.repo.create(device_data, created_by)
            
            # Log audit event
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=created_by,
                action="admin.device.create",
                resource_type="device",
                resource_id=device.id,
                details={
                    "name": device.name,
                    "serial_no": device.serial_no,
                    "tenant_id": device.tenant_id
                }
            )
            
            return device
        except ValueError as e:
            raise ValueError(f"Device creation failed: {str(e)}")
    
    async def update_device(self, device_id: str, device_data: DeviceUpdate, updated_by: str) -> Optional[DeviceOut]:
        """Update device with audit logging."""
        device = await self.repo.update(device_id, device_data, updated_by)
        
        if device:
            # Log audit event
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=updated_by,
                action="admin.device.update",
                resource_type="device",
                resource_id=device_id,
                details=device_data.dict(exclude_unset=True)
            )
        
        return device
    
    async def delete_device(self, device_id: str, deleted_by: str) -> bool:
        """Delete device with audit logging and Redis event."""
        success = await self.repo.delete(device_id, deleted_by)
        
        if success:
            # Log audit event
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=deleted_by,
                action="admin.device.delete",
                resource_type="device",
                resource_id=device_id,
                details={"hard_delete": True}
            )
        
        return success


class AdminSystemService:
    """Service for system health and monitoring operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AdminSystemRepository(session)
    
    async def get_tenant_snapshot(self) -> List[TenantSnapshot]:
        """Get tenant snapshot with users and devices."""
        return await self.repo.get_tenant_snapshot()
    
    async def get_system_health(self) -> SystemHealthOverview:
        """Get comprehensive system health overview."""
        return await self.repo.get_system_health()
    
    async def search_global(self, query: str, page: int = 1, per_page: int = 20) -> SearchResponse:
        """Global search across users, devices, and tenants."""
        results, total = await self.repo.search_global(query, page, per_page)
        
        return SearchResponse(
            results=results,
            total=total,
            page=page,
            per_page=per_page
        )
    
    async def start_database_migration(self, target_revision: str, started_by: str) -> DatabaseMigration:
        """Start database migration operation."""
        job_id = str(uuid.uuid4())
        
        # Create migration record
        migration = DatabaseMigration(
            job_id=job_id,
            status="pending",
            target_revision=target_revision,
            started_at=datetime.utcnow()
        )
        
        # Log audit event
        await log_audit_event(
            request=None,
            session=self.session,
            user_id=started_by,
            action="admin.db.migrate",
            resource_type="database",
            resource_id=job_id,
            details={"target_revision": target_revision}
        )
        
        # Start migration in background
        asyncio.create_task(self._run_migration(migration, started_by))
        
        return migration
    
    async def start_database_backup(self, started_by: str) -> DatabaseBackup:
        """Start database backup operation."""
        job_id = str(uuid.uuid4())
        
        # Create backup record
        backup = DatabaseBackup(
            job_id=job_id,
            status="pending",
            started_at=datetime.utcnow()
        )
        
        # Log audit event
        await log_audit_event(
            request=None,
            session=self.session,
            user_id=started_by,
            action="admin.db.backup",
            resource_type="database",
            resource_id=job_id,
            details={"backup_type": "full"}
        )
        
        # Start backup in background
        asyncio.create_task(self._run_backup(backup, started_by))
        
        return backup
    
    async def _run_migration(self, migration: DatabaseMigration, started_by: str):
        """Run database migration in background."""
        try:
            # Update status to running
            migration.status = "running"
            
            # Simulate migration process
            await asyncio.sleep(2)
            
            # Update status to completed
            migration.status = "completed"
            migration.completed_at = datetime.utcnow()
            
            # Log completion
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=started_by,
                action="admin.db.migrate.completed",
                resource_type="database",
                resource_id=migration.job_id,
                details={"status": "completed"}
            )
            
        except Exception as e:
            migration.status = "failed"
            migration.error_message = str(e)
            migration.completed_at = datetime.utcnow()
            
            # Log failure
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=started_by,
                action="admin.db.migrate.failed",
                resource_type="database",
                resource_id=migration.job_id,
                details={"error": str(e)}
            )
    
    async def _run_backup(self, backup: DatabaseBackup, started_by: str):
        """Run database backup in background."""
        try:
            # Update status to running
            backup.status = "running"
            
            # Simulate backup process
            await asyncio.sleep(5)
            
            # Update status to completed
            backup.status = "completed"
            backup.completed_at = datetime.utcnow()
            backup.filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"
            backup.size_mb = 150.5
            backup.bucket_url = f"s3://backups/{backup.filename}"
            
            # Log completion
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=started_by,
                action="admin.db.backup.completed",
                resource_type="database",
                resource_id=backup.job_id,
                details={"filename": backup.filename, "size_mb": backup.size_mb}
            )
            
        except Exception as e:
            backup.status = "failed"
            backup.error_message = str(e)
            backup.completed_at = datetime.utcnow()
            
            # Log failure
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=started_by,
                action="admin.db.backup.failed",
                resource_type="database",
                resource_id=backup.job_id,
                details={"error": str(e)}
            )


class AdminFeatureFlagService:
    """Service for feature flag management."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_feature_flags(self) -> List[FeatureFlag]:
        """Get all feature flags."""
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
    
    async def update_feature_flag(self, flag_name: str, flag_data: FeatureFlagUpdate, updated_by: str) -> FeatureFlag:
        """Update feature flag with audit logging."""
        # This would typically update a feature_flags table
        # For now, return mock data
        
        # Log audit event
        await log_audit_event(
            request=None,
            session=self.session,
            user_id=updated_by,
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
            updated_by=updated_by
        )


class AdminSettingsService:
    """Service for system settings management."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_settings(self, category: Optional[str] = None) -> List[SystemSetting]:
        """Get system settings."""
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
    
    async def update_setting(self, key: str, setting_data: SystemSettingUpdate, updated_by: str) -> SystemSetting:
        """Update system setting with audit logging."""
        # This would typically update a system_settings table
        # For now, return mock data
        
        # Log audit event
        await log_audit_event(
            request=None,
            session=self.session,
            user_id=updated_by,
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


class AdminAuditService:
    """Service for audit log management."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def export_audit_logs(self, export_request: AuditExportRequest, requested_by: str) -> AuditExportResponse:
        """Export audit logs with filtering."""
        job_id = str(uuid.uuid4())
        
        # Log export request
        await log_audit_event(
            request=None,
            session=self.session,
            user_id=requested_by,
            action="admin.audit.export",
            resource_type="audit_log",
            resource_id=job_id,
            details=export_request.dict()
        )
        
        # Start export in background
        asyncio.create_task(self._run_export(job_id, export_request, requested_by))
        
        return AuditExportResponse(
            job_id=job_id,
            status="pending",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
    
    async def _run_export(self, job_id: str, export_request: AuditExportRequest, requested_by: str):
        """Run audit log export in background."""
        try:
            # Simulate export process
            await asyncio.sleep(3)
            
            # Log completion
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=requested_by,
                action="admin.audit.export.completed",
                resource_type="audit_log",
                resource_id=job_id,
                details={"format": export_request.format}
            )
            
        except Exception as e:
            # Log failure
            await log_audit_event(
                request=None,
                session=self.session,
                user_id=requested_by,
                action="admin.audit.export.failed",
                resource_type="audit_log",
                resource_id=job_id,
                details={"error": str(e)}
            ) 