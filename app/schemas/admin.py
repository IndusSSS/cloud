# app/schemas/admin.py
"""
Admin console Pydantic schemas.

• User management schemas with validation
• Device management schemas with tenant isolation override
• System health and monitoring schemas
• Database and backup operation schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


# ────────────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT SCHEMAS
# ────────────────────────────────────────────────────────────────────────────────

class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"
    SYSTEM_ADMIN = "system_admin"


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: Optional[EmailStr] = Field(None, description="Valid email address (auto-generated if not provided)")
    password: str = Field(..., min_length=8, description="Secure password")
    is_admin: bool = Field(default=False, description="Admin privileges")
    tenant_id: Optional[str] = Field(None, description="Tenant ID (system admin only)")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and not all(c in '._-' for c in v if not c.isalnum()):
            raise ValueError('Username must be alphanumeric with allowed special characters')
        return v.lower()
    
    @validator('email', pre=True, always=True)
    def generate_email_if_missing(cls, v, values):
        """Generate email from username if not provided."""
        if v is None and 'username' in values:
            return f"{values['username']}@smartsecurity.local"
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
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
    
    class Config:
        from_attributes = True


class UserMinimal(BaseModel):
    """Minimal user information for lists."""
    id: str
    username: str
    email: str
    is_active: bool
    is_admin: bool
    tenant_id: Optional[str]


# ────────────────────────────────────────────────────────────────────────────────
# DEVICE MANAGEMENT SCHEMAS
# ────────────────────────────────────────────────────────────────────────────────

class DeviceStatus(str, Enum):
    """Device status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class DeviceCreate(BaseModel):
    """Schema for creating a new device."""
    name: str = Field(..., min_length=1, max_length=100, description="Device name")
    description: Optional[str] = Field(None, max_length=500, description="Device description")
    serial_no: str = Field(..., description="Unique serial number")
    specifications: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Device specifications")
    tenant_id: Optional[str] = Field(None, description="Tenant ID (system admin only)")
    template_id: Optional[str] = Field(None, description="Device template ID")


class DeviceUpdate(BaseModel):
    """Schema for updating device information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    specifications: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    status: Optional[DeviceStatus] = None


class DeviceOut(BaseModel):
    """Schema for device output."""
    id: str
    name: str
    description: Optional[str]
    serial_no: str
    specifications: Optional[Dict[str, Any]]
    is_active: bool
    status: DeviceStatus
    tenant_id: str
    created_at: datetime
    last_seen: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DeviceMinimal(BaseModel):
    """Minimal device information for lists."""
    id: str
    name: str
    serial_no: str
    is_active: bool
    status: DeviceStatus
    tenant_id: str


# ────────────────────────────────────────────────────────────────────────────────
# SYSTEM HEALTH SCHEMAS
# ────────────────────────────────────────────────────────────────────────────────

class ServiceStatus(str, Enum):
    """Service status enumeration."""
    OK = "OK"
    WARNING = "WARNING"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class DatabaseHealth(BaseModel):
    """Database health information."""
    status: ServiceStatus
    pool_in_use: int = Field(..., ge=0, description="Active connections")
    pool_size: int = Field(..., ge=0, description="Total pool size")
    response_time_ms: float = Field(..., ge=0, description="Average response time")


class RedisHealth(BaseModel):
    """Redis health information."""
    status: ServiceStatus
    mem_mb: float = Field(..., ge=0, description="Memory usage in MB")
    connected_clients: int = Field(..., ge=0, description="Connected clients")
    keyspace_hits: int = Field(..., ge=0, description="Cache hit rate")


class MQTTHealth(BaseModel):
    """MQTT broker health information."""
    status: ServiceStatus
    pub_rate_msg_s: float = Field(..., ge=0, description="Publish rate per second")
    connected_devices: int = Field(..., ge=0, description="Connected devices")
    topic_count: int = Field(..., ge=0, description="Active topics")


class ContainerHealth(BaseModel):
    """Container health information."""
    name: str
    state: str
    cpu_percent: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    mem_mb: float = Field(..., ge=0, description="Memory usage in MB")
    uptime_seconds: int = Field(..., ge=0, description="Container uptime")


class SystemHealthOverview(BaseModel):
    """Complete system health overview."""
    uptime_sec: int = Field(..., ge=0, description="System uptime in seconds")
    postgres: DatabaseHealth
    redis: RedisHealth
    mqtt: MQTTHealth
    containers: List[ContainerHealth] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ────────────────────────────────────────────────────────────────────────────────
# TENANT SNAPSHOT SCHEMAS
# ────────────────────────────────────────────────────────────────────────────────

class TenantSnapshot(BaseModel):
    """Tenant snapshot with users and devices."""
    tenant_id: str
    tenant_name: str
    plan: str
    user_count: int = Field(..., ge=0, description="Number of users")
    device_count: int = Field(..., ge=0, description="Number of devices")
    active_devices: int = Field(..., ge=0, description="Active devices")
    users: List[UserMinimal] = Field(default_factory=list)
    devices: List[DeviceMinimal] = Field(default_factory=list)
    created_at: datetime


# ────────────────────────────────────────────────────────────────────────────────
# DATABASE OPERATION SCHEMAS
# ────────────────────────────────────────────────────────────────────────────────

class MigrationStatus(str, Enum):
    """Migration status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DatabaseMigration(BaseModel):
    """Database migration operation."""
    job_id: str
    status: MigrationStatus
    current_revision: Optional[str] = None
    target_revision: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class BackupStatus(str, Enum):
    """Backup status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DatabaseBackup(BaseModel):
    """Database backup operation."""
    job_id: str
    status: BackupStatus
    filename: Optional[str] = None
    size_mb: Optional[float] = None
    bucket_url: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


# ────────────────────────────────────────────────────────────────────────────────
# SEARCH AND FEATURE FLAG SCHEMAS
# ────────────────────────────────────────────────────────────────────────────────

class SearchResult(BaseModel):
    """Search result item."""
    type: str = Field(..., description="Result type (user, device, tenant)")
    id: str
    title: str
    description: Optional[str]
    tenant_id: Optional[str]
    score: float = Field(..., ge=0, le=1, description="Search relevance score")


class SearchResponse(BaseModel):
    """Search response with pagination."""
    results: List[SearchResult]
    total: int = Field(..., ge=0, description="Total results count")
    page: int = Field(..., ge=1, description="Current page")
    per_page: int = Field(..., ge=1, le=100, description="Results per page")


class FeatureFlag(BaseModel):
    """Feature flag configuration."""
    name: str = Field(..., description="Feature flag name")
    enabled: bool = Field(..., description="Flag status")
    description: Optional[str] = Field(None, description="Feature description")
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[str] = Field(None, description="Last updated by user")


class FeatureFlagUpdate(BaseModel):
    """Feature flag update request."""
    enabled: bool = Field(..., description="New flag status")
    description: Optional[str] = Field(None, description="Updated description")


# ────────────────────────────────────────────────────────────────────────────────
# SETTINGS AND CONFIGURATION SCHEMAS
# ────────────────────────────────────────────────────────────────────────────────

class SystemSetting(BaseModel):
    """System setting configuration."""
    key: str = Field(..., description="Setting key")
    value: str = Field(..., description="Setting value")
    description: Optional[str] = Field(None, description="Setting description")
    category: str = Field(..., description="Setting category")
    is_secret: bool = Field(default=False, description="Is sensitive setting")
    created_at: datetime
    updated_at: datetime


class SystemSettingUpdate(BaseModel):
    """System setting update request."""
    value: str = Field(..., description="New setting value")
    description: Optional[str] = Field(None, description="Updated description")


# ────────────────────────────────────────────────────────────────────────────────
# AUDIT AND EXPORT SCHEMAS
# ────────────────────────────────────────────────────────────────────────────────

class AuditExportRequest(BaseModel):
    """Audit log export request."""
    from_date: Optional[datetime] = Field(None, description="Start date for export")
    to_date: Optional[datetime] = Field(None, description="End date for export")
    action: Optional[str] = Field(None, description="Filter by action")
    resource_type: Optional[str] = Field(None, description="Filter by resource type")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    format: str = Field(default="csv", description="Export format (csv, json)")


class AuditExportResponse(BaseModel):
    """Audit log export response."""
    job_id: str
    filename: Optional[str] = None
    download_url: Optional[str] = None
    record_count: Optional[int] = None
    status: str = Field(..., description="Export status")
    created_at: datetime
    expires_at: datetime = Field(..., description="Download link expiration") 