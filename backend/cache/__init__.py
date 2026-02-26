"""
Cache module.

Provides Redis-based caching functionality for the application.
"""

from .cache_manager import CacheManager, get_cache_manager, cached

__all__ = ["CacheManager", "get_cache_manager", "cached"]
