# app/api/v1/endpoints/tenants.py
"""
Tenant management API endpoints.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select

from app.api.deps import get_session, require_sys_admin, log_audit_event
from app.models.tenant import Tenant
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[Tenant])
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """List all tenants (system admin only)."""
    statement = select(Tenant).offset(skip).limit(limit)
    tenants = session.exec(statement).all()
    return tenants


@router.post("/", response_model=Tenant)
def create_tenant(
    tenant: Tenant,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_sys_admin),
    request: Request = None
):
    """Create a new tenant (system admin only)."""
    # Check if tenant name already exists
    existing = session.exec(select(Tenant).where(Tenant.name == tenant.name)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant name already exists"
        )
    
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    
    if request:
        log_audit_event(
            request=request,
            session=session,
            user=current_user,
            action="create",
            resource_type="tenant",
            resource_id=str(tenant.id),
            details={"name": tenant.name, "plan": tenant.plan}
        )
    
    return tenant


@router.get("/{tenant_id}", response_model=Tenant)
def get_tenant(
    tenant_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_sys_admin)
):
    """Get a specific tenant (system admin only)."""
    tenant = session.exec(select(Tenant).where(Tenant.id == tenant_id)).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return tenant


@router.put("/{tenant_id}", response_model=Tenant)
def update_tenant(
    tenant_id: UUID,
    tenant_update: Tenant,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_sys_admin),
    request: Request = None
):
    """Update a tenant (system admin only)."""
    tenant = session.exec(select(Tenant).where(Tenant.id == tenant_id)).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Check if new name conflicts with existing tenant
    if tenant_update.name != tenant.name:
        existing = session.exec(select(Tenant).where(Tenant.name == tenant_update.name)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant name already exists"
            )
    
    # Update fields
    tenant.name = tenant_update.name
    tenant.plan = tenant_update.plan
    
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    
    if request:
        log_audit_event(
            request=request,
            session=session,
            user=current_user,
            action="update",
            resource_type="tenant",
            resource_id=str(tenant.id),
            details={"name": tenant.name, "plan": tenant.plan}
        )
    
    return tenant


@router.delete("/{tenant_id}")
def delete_tenant(
    tenant_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_sys_admin),
    request: Request = None
):
    """Delete a tenant (system admin only)."""
    tenant = session.exec(select(Tenant).where(Tenant.id == tenant_id)).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Check if tenant has users or devices
    from app.models.user import User
    from app.models.device import Device
    
    users = session.exec(select(User).where(User.tenant_id == tenant_id)).all()
    devices = session.exec(select(Device).where(Device.tenant_id == tenant_id)).all()
    
    if users or devices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete tenant with existing users or devices"
        )
    
    session.delete(tenant)
    session.commit()
    
    if request:
        log_audit_event(
            request=request,
            session=session,
            user=current_user,
            action="delete",
            resource_type="tenant",
            resource_id=str(tenant_id),
            details={"name": tenant.name}
        )
    
    return {"message": "Tenant deleted successfully"} 