# app/main.py
"""
Main FastAPI application entry-point.

• Exposes a module-level `app` object for Uvicorn.
• Creates DB tables on startup (demo-friendly).
• Seeds a default tenant and admin user if none exist.
• Mounts all API routers under the versioned prefix.
• Starts Redis subscriber for sensor data broadcasting.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlmodel import SQLModel, select

from app.core.config import settings
from app.db.session import engine, AsyncSessionLocal
from app.api.v1 import api_router
from app.api.deps import get_current_user_ws
from app.models.user import User
from app.models.tenant import Tenant
from app.models.device import Device
from app.utils.security import hash_password
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

# In-memory broadcaster for WebSocket connections
broadcaster: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections for real-time sensor data."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, tenant_id: str):
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = set()
        self.active_connections[tenant_id].add(websocket)
        logger.info(f"WebSocket connected for tenant {tenant_id}")
    
    def disconnect(self, websocket: WebSocket, tenant_id: str):
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].discard(websocket)
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
        logger.info(f"WebSocket disconnected for tenant {tenant_id}")
    
    async def broadcast_to_tenant(self, tenant_id: str, message: str):
        if tenant_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[tenant_id]:
                try:
                    await connection.send_text(message)
                except WebSocketDisconnect:
                    disconnected.add(connection)
                except Exception as e:
                    logger.error(f"Error sending to WebSocket: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection, tenant_id)


manager = ConnectionManager()


async def redis_subscriber():
    """Subscribe to Redis sensor_new channel and broadcast to WebSockets."""
    redis_client = await get_redis_client()
    pubsub = redis_client.pubsub()
    
    try:
        await pubsub.subscribe("sensor_new")
        logger.info("Subscribed to Redis channel: sensor_new")
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    tenant_id = data.get("tenant_id")
                    
                    if tenant_id:
                        # Broadcast to all WebSocket connections for this tenant
                        await manager.broadcast_to_tenant(tenant_id, message["data"])
                        logger.info(f"Broadcasted sensor data to tenant {tenant_id}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in Redis message: {e}")
                except Exception as e:
                    logger.error(f"Error processing Redis message: {e}")
                    
    except Exception as e:
        logger.error(f"Redis subscriber error: {e}")
    finally:
        await pubsub.unsubscribe("sensor_new")
        await pubsub.close()


def create_app() -> FastAPI:
    """Build and return a configured FastAPI instance."""
    
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        # Startup
        # 1) Create tables (idempotent) - only if database is available
        if engine is not None:
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(SQLModel.metadata.create_all)

                # 2) Seed default tenant and admin user if tables are empty
                if AsyncSessionLocal is not None:
                    async with AsyncSessionLocal() as session:
                        # Check if default tenant exists
                        result = await session.execute(select(Tenant).where(Tenant.name == "default"))
                        default_tenant = result.scalar_one_or_none()
                        if not default_tenant:
                            default_tenant = Tenant(name="default", plan="free")
                            session.add(default_tenant)
                            await session.commit()
                            await session.refresh(default_tenant)
                        
                        # Note: Admin users should be created using create_admin_user.py script
                        # This ensures secure password creation and proper validation
                        
                        # Create demo user for customer portal (if needed)
                        demo_user = await session.execute(
                            select(User).where(User.username == "demo")
                        )
                        if not demo_user.scalar_one_or_none():
                            demo = User(
                                username="demo",
                                email="demo@example.com",
                                hashed_password=hash_password("demo123"),
                                tenant_id=default_tenant.id,
                                is_admin=False
                            )
                            session.add(demo)
                            await session.commit()
                
                print("✅ Database initialized successfully")
            except Exception as e:
                print(f"⚠️  Database connection failed: {e}")
                print("   API will run without database functionality")
        else:
            print("Warning: Database not configured, skipping startup tasks")
        
        # 3) Start Redis subscriber in background (optional)
        try:
            asyncio.create_task(redis_subscriber())
            logger.info("Started Redis subscriber background task")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("   API will run without Redis functionality")
        
        yield
        
        # Shutdown
        # Cleanup tasks if needed
        pass
    
    application = FastAPI(
        title="SmartSecurity Cloud",
        version="3.0.0",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        lifespan=lifespan,
    )

    # ─────────────────── Rate Limiting ─────────────────── #
    limiter = Limiter(key_func=get_remote_address)
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ─────────────────── CORS Middleware ───────────────── #
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8080", 
            "https://cloud.smartsecurity.solutions",
            "https://admin.smartsecurity.solutions"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─────────────────── Health check ───────────────────── #
    @application.get(f"{settings.API_PREFIX}/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}

    @application.options(f"{settings.API_PREFIX}/health")
    async def health_check_options():
        return {"status": "ok"}

    # ─────────────────── WebSocket endpoints ────────────── #
    @application.websocket("/ws/{tenant_id}")
    async def websocket_endpoint(websocket: WebSocket, tenant_id: str):
        await manager.connect(websocket, tenant_id)
        try:
            while True:
                # Keep connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket, tenant_id)

    @application.websocket("/ws/live/{device_id}")
    async def websocket_live_device(
        websocket: WebSocket, 
        device_id: str,
        token: str = ""
    ):
        """WebSocket endpoint for live device data with authentication."""
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        try:
            # Verify user and device access
            user = await get_current_user_ws(token)
            if not user:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            
            # Verify device belongs to user's tenant
            if AsyncSessionLocal is not None:
                async with AsyncSessionLocal() as session:
                    device = await session.execute(
                        select(Device).where(
                            Device.id == device_id,
                            Device.tenant_id == user.tenant_id
                        )
                    )
                    device = device.scalar_one_or_none()
                    
                    if not device:
                        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                        return
            
            # Connect to tenant-specific WebSocket
            await manager.connect(websocket, user.tenant_id)
            
            try:
                while True:
                    # Keep connection alive
                    await websocket.receive_text()
            except WebSocketDisconnect:
                manager.disconnect(websocket, user.tenant_id)
                
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

    # ─────────────────── API Router ─────────────────────── #
    application.include_router(api_router, prefix=settings.API_PREFIX)

    return application


# Uvicorn imports `app.main` and looks for this variable:
app: FastAPI = create_app()
