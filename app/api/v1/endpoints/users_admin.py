# app/api/v1/endpoints/users_admin.py
"""
Admin user management endpoints.

• CRUD operations for user accounts within tenant scope.
• User profile management by tenant admins.
• Tenant-aware user administration.
"""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.deps import get_session, get_current_user, require_admin
from app.models.user import User
from app.core.rbac import log_audit_event

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> Any:
    """Get list of users (tenant admin only)."""
    statement = select(User).where(User.tenant_id == current_user.tenant_id)
    statement = statement.offset(skip).limit(limit)
    result = await session.execute(statement)
    users = result.scalars().all()
    
    return [
        {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at
        }
        for user in users
    ]


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get user by ID."""
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Users can only see their own profile or users in their tenant (if admin)
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Tenant admins can only see users in their tenant
    if current_user.is_admin and current_user.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at
    }


@router.put("/{user_id}")
async def update_user(
    request: Request,
    user_id: UUID,
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> Any:
    """Update user status (tenant admin only)."""
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Tenant admins can only update users in their tenant
    if current_user.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if is_active is not None:
        user.is_active = is_active
    if is_admin is not None:
        user.is_admin = is_admin
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="update",
        resource_type="user",
        resource_id=str(user_id),
        details={"is_active": is_active, "is_admin": is_admin}
    )
    
    return {
        "id": str(user.id),
        "username": user.username,
        "is_active": user.is_active,
        "is_admin": user.is_admin
    }


@router.post("/", response_model=dict)
async def create_user(
    request: Request,
    username: str,
    email: str,
    password: str,
    is_admin: bool = False,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> Any:
    """Create a new user (tenant admin only)."""
    from app.core.security import get_password_hash
    
    # Check if username already exists in tenant
    existing = await session.execute(
        select(User).where(
            User.username == username,
            User.tenant_id == current_user.tenant_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists in tenant"
        )
    
    # Check if email already exists
    existing_email = await session.execute(select(User).where(User.email == email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=is_admin,
        tenant_id=current_user.tenant_id
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    await log_audit_event(
        request=request,
        session=session,
        user=current_user,
        action="create",
        resource_type="user",
        resource_id=str(new_user.id),
        details={"username": username, "email": email, "is_admin": is_admin}
    )
    
    return {
        "id": str(new_user.id),
        "username": new_user.username,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "is_admin": new_user.is_admin,
        "created_at": new_user.created_at
    } 