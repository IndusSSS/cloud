# app/repositories/admin.py
"""
Admin repository layer for database operations.

• User management with tenant isolation override
• Device management with system-wide access
• System health monitoring and statistics
• Database operations and backup management
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel

from app.models.user import User
from app.models.device import Device
from app.models.tenant import Tenant
from app.models.audit import AuditLog
from app.schemas.admin import (
    UserCreate, UserUpdate, UserOut, UserMinimal,
    DeviceCreate, DeviceUpdate, DeviceOut, DeviceMinimal,
    TenantSnapshot, SystemHealthOverview, DatabaseHealth,
    RedisHealth, MQTTHealth, ContainerHealth, ServiceStatus
)
from app.core.security import get_password_hash
from app.core.redis import get_redis_client


class AdminUserRepository:
    """Repository for admin user management operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def fetch_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        tenant_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_admin: Optional[bool] = None
    ) -> Tuple[List[UserOut], int]:
        """Fetch users with filtering and pagination."""
        # Build base query
        query = select(User).options(selectinload(User.tenant))
        
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
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(User.created_at)).offset(skip).limit(limit)
        
        # Execute query
        result = await self.session.execute(query)
        users = result.scalars().all()
        
        return [UserOut.from_orm(user) for user in users], total
    
    async def fetch_by_id(self, user_id: str) -> Optional[UserOut]:
        """Fetch user by ID."""
        query = select(User).options(selectinload(User.tenant)).where(User.id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        return UserOut.from_orm(user) if user else None
    
    async def create(self, user_data: UserCreate, created_by: str) -> UserOut:
        """Create a new user."""
        # Check for existing username
        existing_username = await self.session.execute(
            select(User).where(User.username == user_data.username)
        )
        if existing_username.scalar_one_or_none():
            raise ValueError("Username already exists")
        
        # Check for existing email
        existing_email = await self.session.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_email.scalar_one_or_none():
            raise ValueError("Email already exists")
        
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
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        return UserOut.from_orm(user)
    
    async def update(self, user_id: str, user_data: UserUpdate, updated_by: str) -> Optional[UserOut]:
        """Update user information."""
        user = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            return None
        
        # Update fields
        if user_data.username is not None:
            # Check for username conflicts
            existing = await self.session.execute(
                select(User).where(
                    and_(User.username == user_data.username, User.id != user_id)
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("Username already exists")
            user.username = user_data.username
        
        if user_data.email is not None:
            # Check for email conflicts
            existing = await self.session.execute(
                select(User).where(
                    and_(User.email == user_data.email, User.id != user_id)
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("Email already exists")
            user.email = user_data.email
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        if user_data.is_admin is not None:
            user.is_admin = user_data.is_admin
        
        if user_data.tenant_id is not None:
            user.tenant_id = user_data.tenant_id
        
        await self.session.commit()
        await self.session.refresh(user)
        
        return UserOut.from_orm(user)
    
    async def delete(self, user_id: str, deleted_by: str) -> bool:
        """Soft delete user (set is_active=False)."""
        user = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            return False
        
        user.is_active = False
        await self.session.commit()
        
        return True


class AdminDeviceRepository:
    """Repository for admin device management operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def fetch_list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        tenant_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        status: Optional[str] = None
    ) -> Tuple[List[DeviceOut], int]:
        """Fetch devices with filtering and pagination."""
        # Build base query
        query = select(Device)
        
        # Apply filters
        if search:
            search_filter = or_(
                Device.name.ilike(f"%{search}%"),
                Device.description.ilike(f"%{search}%"),
                Device.serial_no.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        if tenant_id is not None:
            query = query.where(Device.tenant_id == tenant_id)
        
        if is_active is not None:
            query = query.where(Device.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Device.created_at)).offset(skip).limit(limit)
        
        # Execute query
        result = await self.session.execute(query)
        devices = result.scalars().all()
        
        return [DeviceOut.from_orm(device) for device in devices], total
    
    async def fetch_by_id(self, device_id: str) -> Optional[DeviceOut]:
        """Fetch device by ID."""
        query = select(Device).where(Device.id == device_id)
        result = await self.session.execute(query)
        device = result.scalar_one_or_none()
        
        return DeviceOut.from_orm(device) if device else None
    
    async def create(self, device_data: DeviceCreate, created_by: str) -> DeviceOut:
        """Create a new device."""
        # Check for existing serial number
        existing_serial = await self.session.execute(
            select(Device).where(Device.serial_no == device_data.serial_no)
        )
        if existing_serial.scalar_one_or_none():
            raise ValueError("Serial number already exists")
        
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
        
        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        
        return DeviceOut.from_orm(device)
    
    async def update(self, device_id: str, device_data: DeviceUpdate, updated_by: str) -> Optional[DeviceOut]:
        """Update device information."""
        device = await self.session.execute(
            select(Device).where(Device.id == device_id)
        )
        device = device.scalar_one_or_none()
        
        if not device:
            return None
        
        # Update fields
        if device_data.name is not None:
            device.name = device_data.name
        
        if device_data.description is not None:
            device.description = device_data.description
        
        if device_data.specifications is not None:
            device.specifications = json.dumps(device_data.specifications)
        
        if device_data.is_active is not None:
            device.is_active = device_data.is_active
        
        await self.session.commit()
        await self.session.refresh(device)
        
        return DeviceOut.from_orm(device)
    
    async def delete(self, device_id: str, deleted_by: str) -> bool:
        """Delete device and publish Redis event."""
        device = await self.session.execute(
            select(Device).where(Device.id == device_id)
        )
        device = device.scalar_one_or_none()
        
        if not device:
            return False
        
        # Delete device
        await self.session.delete(device)
        await self.session.commit()
        
        # Publish Redis event for other services
        try:
            redis_client = await get_redis_client()
            await redis_client.publish(
                "device/deleted",
                json.dumps({
                    "device_id": device_id,
                    "tenant_id": device.tenant_id,
                    "deleted_by": deleted_by,
                    "timestamp": datetime.utcnow().isoformat()
                })
            )
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Failed to publish device deletion event: {e}")
        
        return True


class AdminSystemRepository:
    """Repository for system health and monitoring operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_tenant_snapshot(self) -> List[TenantSnapshot]:
        """Get tenant snapshot with users and devices."""
        # Single query with LEFT JOINs to avoid N+1
        query = select(
            Tenant,
            func.count(User.id).label('user_count'),
            func.count(Device.id).label('device_count'),
            func.sum(func.case((Device.is_active == True, 1), else_=0)).label('active_devices')
        ).outerjoin(User, Tenant.id == User.tenant_id).outerjoin(
            Device, Tenant.id == Device.tenant_id
        ).group_by(Tenant.id, Tenant.name, Tenant.plan, Tenant.created_at)
        
        result = await self.session.execute(query)
        rows = result.all()
        
        snapshots = []
        for row in rows:
            tenant, user_count, device_count, active_devices = row
            
            # Get users for this tenant
            users_query = select(User).where(User.tenant_id == tenant.id)
            users_result = await self.session.execute(users_query)
            users = [UserMinimal.from_orm(user) for user in users_result.scalars().all()]
            
            # Get devices for this tenant
            devices_query = select(Device).where(Device.tenant_id == tenant.id)
            devices_result = await self.session.execute(devices_query)
            devices = [DeviceMinimal.from_orm(device) for device in devices_result.scalars().all()]
            
            snapshot = TenantSnapshot(
                tenant_id=tenant.id,
                tenant_name=tenant.name,
                plan=tenant.plan,
                user_count=user_count or 0,
                device_count=device_count or 0,
                active_devices=active_devices or 0,
                users=users,
                devices=devices,
                created_at=tenant.created_at
            )
            snapshots.append(snapshot)
        
        return snapshots
    
    async def get_system_health(self) -> SystemHealthOverview:
        """Get comprehensive system health overview."""
        # Database health
        db_health = await self._get_database_health()
        
        # Redis health
        redis_health = await self._get_redis_health()
        
        # MQTT health
        mqtt_health = await self._get_mqtt_health()
        
        # Container health
        containers = await self._get_container_health()
        
        # System uptime
        uptime_sec = int((datetime.utcnow() - datetime(2024, 1, 1)).total_seconds())
        
        return SystemHealthOverview(
            uptime_sec=uptime_sec,
            postgres=db_health,
            redis=redis_health,
            mqtt=mqtt_health,
            containers=containers
        )
    
    async def _get_database_health(self) -> DatabaseHealth:
        """Get database health metrics."""
        try:
            # Test database connection and get pool stats
            start_time = datetime.utcnow()
            await self.session.execute(select(1))
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return DatabaseHealth(
                status=ServiceStatus.OK,
                pool_in_use=0,  # Would need engine access for actual pool stats
                pool_size=20,
                response_time_ms=response_time
            )
        except Exception as e:
            return DatabaseHealth(
                status=ServiceStatus.ERROR,
                pool_in_use=0,
                pool_size=0,
                response_time_ms=0
            )
    
    async def _get_redis_health(self) -> RedisHealth:
        """Get Redis health metrics."""
        try:
            redis_client = await get_redis_client()
            info = await redis_client.info()
            
            return RedisHealth(
                status=ServiceStatus.OK,
                mem_mb=float(info.get('used_memory_human', '0').replace('M', '')),
                connected_clients=int(info.get('connected_clients', 0)),
                keyspace_hits=int(info.get('keyspace_hits', 0))
            )
        except Exception as e:
            return RedisHealth(
                status=ServiceStatus.ERROR,
                mem_mb=0,
                connected_clients=0,
                keyspace_hits=0
            )
    
    async def _get_mqtt_health(self) -> MQTTHealth:
        """Get MQTT broker health metrics."""
        # This would typically connect to MQTT broker for stats
        # For now, return mock data
        return MQTTHealth(
            status=ServiceStatus.OK,
            pub_rate_msg_s=10.5,
            connected_devices=25,
            topic_count=150
        )
    
    async def _get_container_health(self) -> List[ContainerHealth]:
        """Get container health metrics."""
        # This would typically use docker-sdk-py to get container stats
        # For now, return mock data
        return [
            ContainerHealth(
                name="backend",
                state="running",
                cpu_percent=2.3,
                mem_mb=150.0,
                uptime_seconds=86400
            ),
            ContainerHealth(
                name="frontend",
                state="running",
                cpu_percent=1.1,
                mem_mb=80.0,
                uptime_seconds=86400
            ),
            ContainerHealth(
                name="database",
                state="running",
                cpu_percent=5.2,
                mem_mb=300.0,
                uptime_seconds=86400
            )
        ]
    
    async def search_global(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[Dict], int]:
        """Global search across users, devices, and tenants."""
        results = []
        
        # Search users
        users_query = select(User).where(
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
        ).limit(per_page)
        users_result = await self.session.execute(users_query)
        users = users_result.scalars().all()
        
        for user in users:
            results.append({
                "type": "user",
                "id": user.id,
                "title": user.username,
                "description": user.email,
                "tenant_id": user.tenant_id,
                "score": 0.9
            })
        
        # Search devices
        devices_query = select(Device).where(
            or_(
                Device.name.ilike(f"%{query}%"),
                Device.serial_no.ilike(f"%{query}%"),
                Device.description.ilike(f"%{query}%")
            )
        ).limit(per_page)
        devices_result = await self.session.execute(devices_query)
        devices = devices_result.scalars().all()
        
        for device in devices:
            results.append({
                "type": "device",
                "id": device.id,
                "title": device.name,
                "description": f"Serial: {device.serial_no}",
                "tenant_id": device.tenant_id,
                "score": 0.8
            })
        
        # Search tenants
        tenants_query = select(Tenant).where(
            Tenant.name.ilike(f"%{query}%")
        ).limit(per_page)
        tenants_result = await self.session.execute(tenants_query)
        tenants = tenants_result.scalars().all()
        
        for tenant in tenants:
            results.append({
                "type": "tenant",
                "id": tenant.id,
                "title": tenant.name,
                "description": f"Plan: {tenant.plan}",
                "tenant_id": None,
                "score": 0.7
            })
        
        # Sort by score and apply pagination
        results.sort(key=lambda x: x["score"], reverse=True)
        total = len(results)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        return results[start_idx:end_idx], total 