"""
Test configuration and fixtures for the SmartSecurity Cloud platform.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from app.main import create_app
from app.db.session import get_session
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Override database session for testing."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_app():
    """Create a test application with overridden dependencies."""
    app = create_app()
    # Override database session
    app.dependency_overrides[get_session] = override_get_session
    return app

@pytest.fixture(scope="session")
async def setup_test_db():
    """Set up test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture(scope="session")
def anyio_backend():
    return 'asyncio'

@pytest.fixture
def db_session(setup_test_db):
    """Get a database session for testing."""
    async def _get_session():
        async with TestingSessionLocal() as session:
            yield session
    return _get_session

@pytest.fixture
def client(test_app):
    """Create a test client."""
    from fastapi.testclient import TestClient
    with TestClient(test_app) as tc:
        yield tc 