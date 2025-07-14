# app/api/v1/endpoints/users.py
"""
User management endpoints.

• User CRUD operations.
• User authentication and authorization.
• User profile management.
"""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlmodel import Session, select
from pydantic import BaseModel

from app.api.deps import get_session, get_current_user, log_audit_event, require_admin
from app.models.user import User
from app.utils.security import hash_password, verify_password

router = APIRouter()


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    tenant_id: Optional[str] = None
    is_admin: bool = False


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.get("/me", response_model=UserProfile, tags=["Customer"])
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user's profile information."""
    return UserProfile(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        tenant_id=current_user.tenant_id,
        is_admin=current_user.is_admin
    )


@router.put("/me/password", tags=["Customer"])
def change_password(
    password_change: PasswordChange,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None
) -> Any:
    """Change current user's password."""
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = hash_password(password_change.new_password)
    session.add(current_user)
    session.commit()
    
    if request:
        log_audit_event(
            request=request,
            session=session,
            user=current_user,
            action="change_password",
            resource_type="user",
            resource_id=str(current_user.id)
        )
    
    return {"message": "Password changed successfully"}


@router.get("/", response_model=List[dict])
def get_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
) -> Any:
    """Get list of users (tenant admin only)."""
    statement = select(User).where(User.tenant_id == current_user.tenant_id)
    statement = statement.offset(skip).limit(limit)
    users = session.exec(statement).all()
    
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
def get_user(
    user_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get user by ID."""
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    
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
        "created_at": user.created_at,
        "last_login": user.last_login
    }


@router.put("/{user_id}")
def update_user(
    user_id: UUID,
    is_active: bool = None,
    is_admin: bool = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
    request: Request = None
) -> Any:
    """Update user status (tenant admin only)."""
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    
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
    session.commit()
    session.refresh(user)
    
    if request:
        log_audit_event(
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
def create_user(
    username: str,
    email: str,
    password: str,
    is_admin: bool = False,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
    request: Request = None
) -> Any:
    """Create a new user (tenant admin only)."""
    from app.core.security import get_password_hash
    
    # Check if username already exists in tenant
    existing = session.exec(
        select(User).where(
            User.username == username,
            User.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists in tenant"
        )
    
    # Check if email already exists
    existing_email = session.exec(select(User).where(User.email == email)).first()
    if existing_email:
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
    session.commit()
    session.refresh(new_user)
    
    if request:
        log_audit_event(
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