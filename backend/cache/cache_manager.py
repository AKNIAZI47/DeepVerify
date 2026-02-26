"""
Redis cache manager for application-wide caching.

This module provides a high-level interface for caching with Redis,
including TTL management, serialization, and error handling.
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Union, Callable
from datetime import timedelta
import redis.asyncio as redis
from redis.asyncio import Redis
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis-based cache manager with automatic serialization.
    
    Supports both JSON and pickle serialization for different data types.
    """
    
    def __init__(self, redis_url: str, default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds (default: 1 hour)
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._client: Optional[Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        if self._client is None:
            self._client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False,  # We handle encoding ourselves
            )
            logger.info("Connected to Redis cache")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Disconnected from Redis cache")
    
    async def get(self, key: str, deserialize: str = "json") -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            deserialize: Deserialization method ("json" or "pickle")
            
        Returns:
            Cached value or None if not found
        """
        try:
            await self.connect()
            value = await self._client.get(key)
            
            if value is None:
                return None
            
            if deserialize == "json":
                return json.loads(value)
            elif deserialize == "pickle":
                return pickle.loads(value)
            else:
                return value.decode("utf-8")
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: str = "json"
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = use default)
            serialize: Serialization method ("json" or "pickle")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.connect()
            
            if serialize == "json":
                serialized = json.dumps(value)
            elif serialize == "pickle":
                serialized = pickle.dumps(value)
            else:
                serialized = str(value)
            
            ttl = ttl or self.default_ttl
            await self._client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            await self.connect()
            result = await self._client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists, False otherwise
        """
        try:
            await self.connect()
            result = await self._client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "analysis:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            await self.connect()
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds or None if key doesn't exist
        """
        try:
            await self.connect()
            ttl = await self._client.ttl(key)
            return ttl if ttl > 0 else None
        except Exception as e:
            logger.error(f"Cache get TTL error for key {key}: {e}")
            return None
    
    @staticmethod
    def generate_key(*args, prefix: str = "", **kwargs) -> str:
        """
        Generate cache key from arguments.
        
        Args:
            *args: Positional arguments
            prefix: Key prefix
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create a deterministic string from args and kwargs
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_string = ":".join(key_parts)
        
        # Hash for consistent length
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        if prefix:
            return f"{prefix}:{key_hash}"
        return key_hash


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager(redis_url: str = "redis://localhost:6379", default_ttl: int = 3600) -> CacheManager:
    """
    Get global cache manager instance.
    
    Args:
        redis_url: Redis connection URL
        default_ttl: Default TTL in seconds
        
    Returns:
        CacheManager instance
    """
    global _cache_manager
    
    if _cache_manager is None:
        _cache_manager = CacheManager(redis_url, default_ttl)
    
    return _cache_manager


def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    serialize: str = "json"
):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache key
        serialize: Serialization method ("json" or "pickle")
        
    Example:
        @cached(ttl=300, key_prefix="analysis")
        async def analyze_text(text: str):
            # expensive operation
            return result
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Generate cache key
            cache_key = CacheManager.generate_key(
                *args,
                prefix=key_prefix or func.__name__,
                **kwargs
            )
            
            # Try to get from cache
            cached_value = await cache.get(cache_key, deserialize=serialize)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Execute function
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl=ttl, serialize=serialize)
            
            return result
        
        return wrapper
    return decorator
