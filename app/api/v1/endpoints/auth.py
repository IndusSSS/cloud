# app/api/v1/endpoints/auth.py
"""
Authentication endpoints.

• User login and token generation.
• Token refresh and validation.
• User registration (admin only).
• API token generation and management.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api.deps import get_session, get_current_user, require_admin
from app.models.user import User
from app.services.auth import authenticate_user, create_user, create_user_token
from app.models.tenant import Tenant
from app.utils.security import create_smartsecurity_api_token, verify_api_token
from sqlmodel import select

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
) -> Any:
    """Authenticate user and return access token."""
    # Handle both OAuth2PasswordRequestForm and direct form data
    username = form_data.username
    password = form_data.password
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    user = await authenticate_user(session, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_user_token(user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "username": user.username,
        "is_admin": user.is_admin
    }


@router.post("/login-json")
async def login_json(
    login_data: LoginRequest,
    session: AsyncSession = Depends(get_session)
) -> Any:
    """Authenticate user with JSON data and return access token."""
    user = await authenticate_user(session, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_user_token(user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "username": user.username,
        "is_admin": user.is_admin
    }


@router.post("/register")
async def register(
    username: str,
    email: str,
    password: str,
    session: AsyncSession = Depends(get_session)
) -> Any:
    """Register a new user account."""
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
    user = await create_user(session, username, email, password, default_tenant.id)
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active
    }


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
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
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