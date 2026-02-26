"""
Configuration module.

Provides centralized configuration management using Pydantic Settings.
"""

from .settings import Settings, get_settings, reload_settings

# Get settings instance for backward compatibility exports
_settings = get_settings()

# Backward compatibility exports
MONGO_URI = _settings.mongo_uri
MONGO_DB = _settings.mongo_db
JWT_SECRET = _settings.jwt_secret
JWT_ALGO = _settings.jwt_algorithm
ACCESS_EXPIRE_MIN = _settings.access_token_expire_minutes
REFRESH_EXPIRE_MIN = _settings.refresh_token_expire_minutes
FRONTEND_ORIGINS = _settings.cors_origins_list if hasattr(_settings, 'cors_origins_list') else _settings.frontend_origins
REDIS_URL = _settings.redis_url

__all__ = [
    "Settings", 
    "get_settings", 
    "reload_settings",
    "MONGO_URI",
    "MONGO_DB",
    "JWT_SECRET",
    "JWT_ALGO",
    "ACCESS_EXPIRE_MIN",
    "REFRESH_EXPIRE_MIN",
    "FRONTEND_ORIGINS",
    "REDIS_URL",
]
