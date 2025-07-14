# app/services/auth.py
"""
Authentication service for user management.

• User authentication and login.
• Token generation and validation.
• User registration and profile management.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import verify_password, create_access_token, hash_password


async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password."""
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    if not user.is_active:
        return None
    
    # Update last login
    user.last_login = datetime.utcnow()
    session.add(user)
    await session.commit()
    
    return user


async def create_user(
    session: AsyncSession, 
    username: str, 
    email: str, 
    password: str,
    tenant_id: str,
    is_admin: bool = False
) -> User:
    """Create a new user account."""
    hashed_password = hash_password(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=is_admin,
        tenant_id=tenant_id
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


def create_user_token(user: User) -> str:
    """Create an access token for a user."""
    token_data = {"sub": str(user.id), "username": user.username}
    return create_access_token(data=token_data)