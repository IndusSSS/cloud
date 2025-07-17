# app/api/v1/endpoints/auth.py
"""
Enhanced authentication endpoints for MESSS framework - Phase 1 Implementation.

• User login with rate limiting and security checks
• Session management with device tracking
• Password change with validation
• Security audit logging
• Account recovery features
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
import redis

from app.api.deps import get_session, get_current_user, require_admin
from app.models.user import User, UserSession
from app.services.auth import AuthenticationService, authenticate_user, create_user, create_user_token
from app.models.tenant import Tenant
from app.utils.security import (
    create_smartsecurity_api_token, 
    verify_api_token,
    validate_password_strength,
    generate_secure_password
)
from app.core.redis import get_redis_client
from sqlmodel import select

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str
    device_name: str = "Unknown Device"


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Any:
    """Enhanced user login with security features."""
    # Get client information
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Initialize authentication service
    auth_service = AuthenticationService(redis_client)
    
    # Authenticate user
    user, auth_result = await auth_service.authenticate_user(
        session, form_data.username, form_data.password, ip_address, user_agent
    )
    
    if not auth_result["success"]:
        if auth_result.get("rate_limited"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=auth_result["error"],
                headers={"Retry-After": str(auth_result.get("reset_time", 900))}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=auth_result["error"],
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Create user session
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    session_data = await auth_service.create_user_session(
        session, user, ip_address, user_agent
    )
    
    return {
        "access_token": session_data["access_token"],
        "refresh_token": session_data["refresh_token"],
        "token_type": "bearer",
        "expires_in": session_data["expires_in"],
        "user_id": str(user.id),
        "username": user.username,
        "is_admin": user.is_admin,
        "requires_mfa": session_data["requires_mfa"],
        "session_id": session_data["session_id"]
    }


@router.post("/login-json")
async def login_json(
    request: Request,
    login_data: LoginRequest,
    session: AsyncSession = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Any:
    """Enhanced JSON login with device tracking."""
    # Get client information
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Initialize authentication service
    auth_service = AuthenticationService(redis_client)
    
    # Authenticate user
    user, auth_result = await auth_service.authenticate_user(
        session, login_data.username, login_data.password, ip_address, user_agent
    )
    
    if not auth_result["success"]:
        if auth_result.get("rate_limited"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=auth_result["error"],
                headers={"Retry-After": str(auth_result.get("reset_time", 900))}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=auth_result["error"],
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Create user session with device name
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    session_data = await auth_service.create_user_session(
        session, user, ip_address, user_agent, login_data.device_name
    )
    
    return {
        "access_token": session_data["access_token"],
        "refresh_token": session_data["refresh_token"],
        "token_type": "bearer",
        "expires_in": session_data["expires_in"],
        "user_id": str(user.id),
        "username": user.username,
        "is_admin": user.is_admin,
        "requires_mfa": session_data["requires_mfa"],
        "session_id": session_data["session_id"],
        "device_fingerprint": session_data["device_fingerprint"]
    }


@router.post("/refresh")
async def refresh_token(
    request: Request,
    refresh_token: str = Form(...),
    session: AsyncSession = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Any:
    """Refresh access token."""
    from app.utils.security import verify_token, create_access_token
    
    # Verify refresh token
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Find user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    new_access_token = create_access_token({"sub": user.id, "username": user.username})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": user.session_timeout_minutes * 60
    }


@router.post("/logout")
async def logout(
    request: Request,
    access_token: str = Form(...),
    session: AsyncSession = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Any:
    """Logout user and invalidate session."""
    # Get client information
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Initialize authentication service
    auth_service = AuthenticationService(redis_client)
    
    # Logout user
    success = await auth_service.logout_user(session, access_token, ip_address, user_agent)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session token"
        )
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Any:
    """Logout all sessions for the current user."""
    # Get client information
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Initialize authentication service
    auth_service = AuthenticationService(redis_client)
    
    # Logout all sessions
    sessions_terminated = await auth_service.logout_all_sessions(
        session, current_user.id, ip_address, user_agent
    )
    
    return {
        "message": f"Successfully logged out from {sessions_terminated} sessions",
        "sessions_terminated": sessions_terminated
    }


@router.post("/change-password")
async def change_password(
    request: Request,
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Any:
    """Change user password with enhanced validation."""
    # Get client information
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Initialize authentication service
    auth_service = AuthenticationService(redis_client)
    
    # Change password
    result = await auth_service.change_password(
        session, current_user, password_data.current_password, 
        password_data.new_password, ip_address, user_agent
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"message": result["message"]}


@router.post("/register")
async def register(
    request: Request,
    username: str,
    email: str,
    password: str,
    session: AsyncSession = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Any:
    """Register a new user account with enhanced security."""
    # Get client information
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Validate password strength
    password_validation = validate_password_strength(password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password does not meet security requirements: {', '.join(password_validation['issues'])}"
        )
    
    # Fetch default tenant
    result = await session.execute(select(Tenant).where(Tenant.name == "default"))
    default_tenant = result.scalar_one_or_none()
    if not default_tenant:
        raise HTTPException(status_code=500, detail="Default tenant not found")
    
    # Check if user already exists
    existing_user = await session.execute(
        select(User).where(
            (User.username == username) | (User.email == email)
        )
    )
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    try:
        user = await create_user(session, username, email, password, default_tenant.id)
        
        # Log registration event
        auth_service = AuthenticationService(redis_client)
        auth_service.auditor.log_security_event(
            event_type="user_registration",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            details={"username": username, "email": email},
            severity="low"
        )
        
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "message": "User registered successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information."""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login,
        "email_verified": current_user.email_verified,
        "phone_verified": current_user.phone_verified,
        "mfa_enabled": current_user.mfa_enabled,
        "mfa_setup_completed": current_user.mfa_setup_completed,
        "max_concurrent_sessions": current_user.max_concurrent_sessions,
        "session_timeout_minutes": current_user.session_timeout_minutes
    }


@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Any:
    """Get active sessions for the current user."""
    result = await session.execute(
        select(UserSession).where(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        )
    )
    user_sessions = result.scalars().all()
    
    return {
        "sessions": [user_session.to_dict() for user_session in user_sessions],
        "total_sessions": len(user_sessions)
    }


@router.delete("/sessions/{session_id}")
async def terminate_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Any:
    """Terminate a specific session."""
    # Find session
    result = await session.execute(
        select(UserSession).where(
            UserSession.id == session_id,
            UserSession.user_id == current_user.id
        )
    )
    user_session = result.scalar_one_or_none()
    
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Terminate session
    user_session.is_active = False
    await session.commit()
    
    return {"message": "Session terminated successfully"}


@router.post("/generate-secure-password")
async def generate_secure_password_endpoint() -> Any:
    """Generate a secure password for users."""
    password = generate_secure_password()
    return {
        "password": password,
        "strength": "very_strong",
        "message": "Use this password or generate a new one"
    }


@router.post("/validate-password")
async def validate_password_endpoint(password: str) -> Any:
    """Validate password strength."""
    validation = validate_password_strength(password)
    return {
        "valid": validation["valid"],
        "score": validation["score"],
        "strength": validation["strength"],
        "issues": validation["issues"],
        "suggestions": validation["suggestions"]
    }


@router.post("/generate-api-token")
async def generate_api_token(
    current_user: User = Depends(require_admin)
) -> Any:
    """Generate a SmartSecurity Cloud API token for external service authentication."""
    try:
        api_token_data = create_smartsecurity_api_token()
        return {
            "success": True,
            "message": "API token generated successfully",
            "data": api_token_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate API token: {str(e)}"
        )


@router.post("/verify-api-token")
async def verify_api_token_endpoint(
    token: str,
    current_user: User = Depends(require_admin)
) -> Any:
    """Verify an API token and return its payload."""
    try:
        payload = verify_api_token(token)
        if payload:
            return {
                "valid": True,
                "payload": payload
            }
        else:
            return {
                "valid": False,
                "message": "Invalid or expired API token"
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token verification failed: {str(e)}"
        )