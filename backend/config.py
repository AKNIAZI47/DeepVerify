"""
Legacy configuration module for backward compatibility.

This module imports from the new settings module to maintain
backward compatibility with existing code.
"""

from config.settings import get_settings

# Get settings instance
_settings = get_settings()

# Backward compatibility exports
MONGO_URI = _settings.mongo_uri
MONGO_DB = _settings.mongo_db
JWT_SECRET = _settings.jwt_secret
JWT_ALGO = _settings.jwt_algorithm
ACCESS_EXPIRE_MIN = _settings.access_token_expire_minutes
REFRESH_EXPIRE_MIN = _settings.refresh_token_expire_minutes

# CORS Configuration
FRONTEND_ORIGINS = _settings.cors_origins_list

# CORS allowed methods - restrict to only what's needed
CORS_ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

# CORS allowed headers - restrict to only what's needed
CORS_ALLOWED_HEADERS = [
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
    "X-Requested-With",
]

# CORS expose headers
CORS_EXPOSE_HEADERS = [
    "X-RateLimit-Limit",
    "X-RateLimit-Remaining",
    "X-RateLimit-Reset",
]

# CORS max age (how long browsers cache preflight requests)
CORS_MAX_AGE = _settings.cors_max_age