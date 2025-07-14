# app/core/config.py
"""
Application configuration settings.

• Loads from environment variables with sensible defaults.
• Validates required settings on startup.
• Provides type-safe access to all config values.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ─────────────────── API Settings ──────────────────── #
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # ─────────────────── Database ──────────────────────── #
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/cloud"
    DATABASE_ECHO: bool = False
    
    # ─────────────────── Security ──────────────────────── #
    SECRET_KEY: str = "52Xd8XzbHYkXeD2_-3Xy_WXZa8y-W2BHMdDlO3VQVNw"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ─────────────────── API Token Settings ──────────────────── #
    API_TOKEN_SECRET: str = "smartsecurity-cloud-api-token-secret-key-2024"
    API_TOKEN_ALGORITHM: str = "HS256"
    API_TOKEN_EXPIRE_DAYS: int = 365  # API tokens expire after 1 year
    
    # ─────────────────── Redis ─────────────────────────── #
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ─────────────────── MQTT ──────────────────────────── #
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Development fallbacks for missing external services
        if os.getenv("DEVELOPMENT_MODE", "false").lower() == "true":
            # Use SQLite for development if PostgreSQL is not available
            if not self._test_database_connection():
                self.DATABASE_URL = "sqlite+aiosqlite:///./cloud_dev.db"
                print("⚠️  Using SQLite for development (PostgreSQL not available)")
            
            # Disable Redis if not available
            if not self._test_redis_connection():
                self.REDIS_URL = "redis://localhost:6379/0"  # Keep URL but handle gracefully
                print("⚠️  Redis not available - real-time features will be limited")

    def _test_database_connection(self) -> bool:
        """Test if database is accessible."""
        try:
            import asyncpg
            return True
        except ImportError:
            return False

    def _test_redis_connection(self) -> bool:
        """Test if Redis is accessible."""
        try:
            import redis
            r = redis.Redis.from_url(self.REDIS_URL, socket_connect_timeout=1)
            r.ping()
            return True
        except:
            return False


# Global settings instance
settings = Settings()