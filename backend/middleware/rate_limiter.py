"""
Rate limiting middleware using Redis backend.

This module provides configurable rate limiting for API endpoints
to prevent abuse and ensure fair resource usage.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict, Callable
import time
import redis.asyncio as redis
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Configuration for rate limiting."""
    
    def __init__(
        self,
        requests_per_minute: int = 100,
        burst_size: Optional[int] = None,
        key_prefix: str = "ratelimit",
    ):
        """
        Initialize rate limit configuration.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
            burst_size: Maximum burst size (defaults to requests_per_minute)
            key_prefix: Redis key prefix for rate limit counters
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute
        self.key_prefix = key_prefix
        self.window_seconds = 60


class RateLimitStore:
    """Redis-backed storage for rate limit counters."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize rate limit store.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Establish Redis connection."""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
    
    async def increment(
        self,
        key: str,
        window_seconds: int,
        max_requests: int
    ) -> tuple[int, int, bool]:
        """
        Increment request counter using sliding window algorithm.
        
        Args:
            key: Rate limit key (usually IP address or user ID)
            window_seconds: Time window in seconds
            max_requests: Maximum requests allowed in window
            
        Returns:
            Tuple of (current_count, remaining, is_allowed)
        """
        if not self.redis_client:
            await self.connect()
        
        now = time.time()
        window_start = now - window_seconds
        
        # Use Redis pipeline for atomic operations
        pipe = self.redis_client.pipeline()
        
        # Remove old entries outside the window
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Set expiration
        pipe.expire(key, window_seconds)
        
        results = await pipe.execute()
        current_count = results[1] + 1  # Count before adding + 1
        
        is_allowed = current_count <= max_requests
        remaining = max(0, max_requests - current_count)
        
        return current_count, remaining, is_allowed
    
    async def get_reset_time(self, key: str, window_seconds: int) -> int:
        """
        Get time until rate limit resets.
        
        Args:
            key: Rate limit key
            window_seconds: Time window in seconds
            
        Returns:
            Seconds until reset
        """
        if not self.redis_client:
            await self.connect()
        
        ttl = await self.redis_client.ttl(key)
        return max(0, ttl) if ttl > 0 else window_seconds


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    def __init__(
        self,
        app,
        redis_url: str = "redis://localhost:6379",
        default_config: Optional[RateLimitConfig] = None,
        endpoint_configs: Optional[Dict[str, RateLimitConfig]] = None,
        key_func: Optional[Callable] = None,
        exempt_paths: Optional[list[str]] = None,
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            app: FastAPI application
            redis_url: Redis connection URL
            default_config: Default rate limit configuration
            endpoint_configs: Per-endpoint rate limit configurations
            key_func: Custom function to extract rate limit key from request
            exempt_paths: List of paths exempt from rate limiting
        """
        super().__init__(app)
        self.store = RateLimitStore(redis_url)
        self.default_config = default_config or RateLimitConfig()
        self.endpoint_configs = endpoint_configs or {}
        self.key_func = key_func or self._default_key_func
        self.exempt_paths = set(exempt_paths or ["/health", "/docs", "/openapi.json"])
    
    @staticmethod
    def _default_key_func(request: Request) -> str:
        """
        Default function to extract rate limit key from request.
        
        Uses client IP address as the key.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Rate limit key string
        """
        # Try to get real IP from X-Forwarded-For header (if behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _get_config(self, path: str) -> RateLimitConfig:
        """
        Get rate limit configuration for a specific path.
        
        Args:
            path: Request path
            
        Returns:
            Rate limit configuration
        """
        # Check for exact path match
        if path in self.endpoint_configs:
            return self.endpoint_configs[path]
        
        # Check for prefix match
        for endpoint_path, config in self.endpoint_configs.items():
            if path.startswith(endpoint_path):
                return config
        
        return self.default_config
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response or rate limit error
        """
        path = request.url.path
        
        # Skip rate limiting for exempt paths
        if path in self.exempt_paths:
            return await call_next(request)
        
        # Get configuration for this endpoint
        config = self._get_config(path)
        
        # Extract rate limit key
        key = self.key_func(request)
        redis_key = f"{config.key_prefix}:{key}:{path}"
        
        try:
            # Check rate limit
            current, remaining, is_allowed = await self.store.increment(
                redis_key,
                config.window_seconds,
                config.requests_per_minute
            )
            
            if not is_allowed:
                # Rate limit exceeded
                reset_time = await self.store.get_reset_time(
                    redis_key,
                    config.window_seconds
                )
                
                logger.warning(
                    f"Rate limit exceeded for {key} on {path}. "
                    f"Count: {current}/{config.requests_per_minute}"
                )
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests. Please try again later.",
                            "retry_after": reset_time,
                        }
                    },
                    headers={
                        "X-RateLimit-Limit": str(config.requests_per_minute),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + reset_time),
                        "Retry-After": str(reset_time),
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to response
            response.headers["X-RateLimit-Limit"] = str(config.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(
                int(time.time()) + config.window_seconds
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # On error, allow request through (fail open)
            return await call_next(request)


async def get_rate_limit_status(
    store: RateLimitStore,
    key: str,
    config: RateLimitConfig
) -> Dict[str, int]:
    """
    Get current rate limit status for a key.
    
    Args:
        store: Rate limit store
        key: Rate limit key
        config: Rate limit configuration
        
    Returns:
        Dictionary with limit, remaining, and reset information
    """
    redis_key = f"{config.key_prefix}:{key}"
    
    if not store.redis_client:
        await store.connect()
    
    now = time.time()
    window_start = now - config.window_seconds
    
    # Count requests in current window
    count = await store.redis_client.zcount(redis_key, window_start, now)
    remaining = max(0, config.requests_per_minute - count)
    reset_time = await store.get_reset_time(redis_key, config.window_seconds)
    
    return {
        "limit": config.requests_per_minute,
        "remaining": remaining,
        "reset": int(time.time()) + reset_time,
    }
