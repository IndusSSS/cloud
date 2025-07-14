# app/db/session.py
"""
Database session management.

• Creates async database engine with connection pooling.
• Provides session factory for dependency injection.
• Handles database URL configuration and connection setup.
"""

import os
from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def create_database_engine():
    """Create database engine with fallback support."""
    try:
        # Try PostgreSQL first
        if "postgresql" in settings.DATABASE_URL:
            return create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DATABASE_ECHO,
                pool_pre_ping=True,
                pool_recycle=300,
            )
        # Fallback to SQLite
        elif "sqlite" in settings.DATABASE_URL:
            # Install aiosqlite if not available
            try:
                import aiosqlite
            except ImportError:
                print("⚠️  Installing aiosqlite for SQLite support...")
                import subprocess
                subprocess.check_call(["pip", "install", "aiosqlite"])
                import aiosqlite
            
            return create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DATABASE_ECHO,
                connect_args={"check_same_thread": False}
            )
        else:
            raise ValueError(f"Unsupported database URL: {settings.DATABASE_URL}")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("   Using in-memory SQLite for development")
        return create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=settings.DATABASE_ECHO,
            connect_args={"check_same_thread": False}
        )


# Create async engine
engine = create_database_engine()

# Create sync engine for migrations and startup tasks (with fallback)
try:
    if "postgresql" in settings.DATABASE_URL:
        sync_engine = create_engine(
            settings.DATABASE_URL.replace("+asyncpg", ""),
            echo=settings.DATABASE_ECHO,
        )
    elif "sqlite" in settings.DATABASE_URL:
        sync_engine = create_engine(
            settings.DATABASE_URL.replace("+aiosqlite", ""),
            echo=settings.DATABASE_ECHO,
            connect_args={"check_same_thread": False}
        )
    else:
        sync_engine = None
except Exception as e:
    print(f"⚠️  Sync engine creation failed: {e}")
    sync_engine = None

# Session factory for dependency injection
if engine is not None:
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
else:
    AsyncSessionLocal = None


async def get_session() -> AsyncSession:
    """Dependency to get database session."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not configured")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()