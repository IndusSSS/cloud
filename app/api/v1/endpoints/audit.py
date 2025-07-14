# app/api/v1/endpoints/audit.py
"""
Audit log API endpoints.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc
from sqlmodel import select

from app.api.deps import get_session, require_sys_admin
from app.models.audit import AuditLog
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[AuditLog])
async def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """List audit logs (system admin only)."""
    statement = select(AuditLog)
    
    # Apply filters
    if action:
        statement = statement.where(AuditLog.action == action)
    if resource_type:
        statement = statement.where(AuditLog.resource_type == resource_type)
    if user_id:
        statement = statement.where(AuditLog.user_id == user_id)
    if start_date:
        statement = statement.where(AuditLog.created_at >= start_date)
    if end_date:
        statement = statement.where(AuditLog.created_at <= end_date)
    
    # Order by creation date (newest first)
    statement = statement.order_by(desc(AuditLog.created_at))
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    result = await session.execute(statement)
    audit_logs = result.scalars().all()
    return audit_logs


@router.get("/{audit_id}", response_model=AuditLog)
async def get_audit_log(
    audit_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get a specific audit log entry (system admin only)."""
    statement = select(AuditLog).where(AuditLog.id == audit_id)
    result = await session.execute(statement)
    audit_log = result.scalar_one_or_none()
    
    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    return audit_log