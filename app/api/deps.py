# app/api/deps.py
"""
FastAPI dependencies for authentication and authorization.
"""

import logging
from typing import Optional, Generator, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import verify_jwt_token, create_access_token
from app.utils.security import verify_api_token
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_session() -> AsyncSession:
    """Dependency to get database session."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not configured")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    session: Annotated[AsyncSession, Depends(get_session)]
) -> User:
    """Get current authenticated user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = verify_jwt_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    # Get user with tenant info
    statement = select(User).options(selectinload(User.tenant)).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    
    return user


async def get_api_token_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    session: Annotated[AsyncSession, Depends(get_session)]
) -> dict:
    """Get API token payload for external service authentication."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = verify_api_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API token",
            )
        
        # Check if token is expired
        if "exp" in payload:
            from datetime import datetime
            if datetime.utcnow().timestamp() > payload["exp"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API token expired",
                )
        
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token",
        )


async def get_current_user_ws(token: str) -> Optional[User]:
    """Get current authenticated user from JWT token for WebSocket connections."""
    if not token:
        return None
    
    try:
        payload = verify_jwt_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except Exception as e:
        logger.error(f"WebSocket token verification failed: {e}")
        return None
    
    # Get user with tenant info
    async with AsyncSessionLocal() as session:
        statement = select(User).options(selectinload(User.tenant)).where(User.id == user_id)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()
        
        if user is None or not user.is_active:
            return None
        
        return user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Require user to be a tenant admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def require_sys_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Require user to be a system admin (no tenant restriction)."""
    if not current_user.is_admin or current_user.tenant_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System admin access required",
        )
    return current_user


def tenant_filter(query, user: User):
    """Add tenant filter to query based on user's tenant."""
    if user.tenant_id:
        return query.where(query.table.tenant_id == user.tenant_id)
    return query


async def get_tenant_for_user(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
) -> Optional[Tenant]:
    """Get tenant for current user."""
    if not current_user.tenant_id:
        return None
    
    statement = select(Tenant).where(Tenant.id == current_user.tenant_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def log_audit_event(
    request: Request,
    session: AsyncSession,
    user: User,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None
):
    """Log an audit event."""
    from app.models.audit import AuditLog
    
    audit_log = AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    session.add(audit_log)
    await session.commit()