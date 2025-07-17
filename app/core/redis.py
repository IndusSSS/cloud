# app/core/redis.py
"""
Redis client configuration for MESSS framework.

• Redis connection management
• Connection pooling and error handling
• Health checks and monitoring
"""

import redis
from typing import Optional
from app.core.config import settings


def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    try:
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        # Test connection
        client.ping()
        return client
    except Exception as e:
        # Fallback to in-memory storage for development
        print(f"Warning: Redis connection failed: {e}")
        print("Using in-memory storage for development")
        return None


def is_redis_available() -> bool:
    """Check if Redis is available."""
    try:
        client = get_redis_client()
        if client:
            client.ping()
            return True
        return False
    except:
        return False


class RedisManager:
    """Redis connection manager with fallback support."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._fallback_storage = {}
    
    def get_client(self) -> Optional[redis.Redis]:
        """Get Redis client with fallback."""
        if self.client is None:
            self.client = get_redis_client()
        return self.client
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set key-value with fallback to in-memory storage."""
        client = self.get_client()
        if client:
            try:
                return client.set(key, value, ex=ex)
            except:
                pass
        
        # Fallback to in-memory storage
        self._fallback_storage[key] = value
        return True
    
    def get(self, key: str) -> Optional[str]:
        """Get value with fallback to in-memory storage."""
        client = self.get_client()
        if client:
            try:
                return client.get(key)
            except:
                pass
        
        # Fallback to in-memory storage
        return self._fallback_storage.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete key with fallback to in-memory storage."""
        client = self.get_client()
        if client:
            try:
                return bool(client.delete(key))
            except:
                pass
        
        # Fallback to in-memory storage
        if key in self._fallback_storage:
            del self._fallback_storage[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists with fallback to in-memory storage."""
        client = self.get_client()
        if client:
            try:
                return bool(client.exists(key))
            except:
                pass
        
        # Fallback to in-memory storage
        return key in self._fallback_storage


# Global Redis manager instance
redis_manager = RedisManager() 