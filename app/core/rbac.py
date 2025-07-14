# app/core/rbac.py
"""
Role-Based Access Control (RBAC) helpers.

• System admin authorization checks.
• Tenant-scoped query filtering.
• Audit logging for admin actions.
"""

import json
from typing import Optional, Any
from fastapi import Depends, HTTPException, status, Request
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session
from app.models.user import User
from app.models.audit import AuditLog


async def require_sys_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be a system admin (no tenant restriction)."""
    if not current_user.is_admin or current_user.tenant_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System admin access required"
        )
    return current_user


async def require_tenant_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be a tenant admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def tenant_scope(query, user: User):
    """Add tenant filter to query based on user's tenant."""
    if user.tenant_id:
        return query.where(query.table.tenant_id == user.tenant_id)
    return query


async def log_audit_event(
    request: Request,
    session: AsyncSession,
    user: User,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None
):
    """Log an audit event for admin actions."""
    audit_log = AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=json.dumps(details) if details else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    session.add(audit_log)
    await session.commit() 