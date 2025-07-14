# app/api/v1/__init__.py
"""
API v1 endpoints.

Version 1 of the REST API endpoints.
"""

from fastapi import APIRouter
from .endpoints import auth, users, devices, ingest, tenants, audit, ws, users_admin, devices_admin, ota

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["data ingestion"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(ws.router, prefix="/ws", tags=["websockets"])

# Admin endpoints (prefixed with /admin)
api_router.include_router(tenants.router, prefix="/admin/tenants", tags=["admin-tenants"])
api_router.include_router(users_admin.router, prefix="/admin/users", tags=["admin-users"])
api_router.include_router(devices_admin.router, prefix="/admin/devices", tags=["admin-devices"])
api_router.include_router(audit.router, prefix="/admin/audit", tags=["admin-audit"])
api_router.include_router(ota.router, prefix="/admin/ota", tags=["admin-ota"])