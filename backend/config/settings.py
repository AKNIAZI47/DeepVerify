"""
Application settings using Pydantic Settings.

This module provides type-safe configuration management with
environment variable support and validation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = Field(default="VeriGlow", description="Application name")
    app_version: str = Field(default="3.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Database
    mongo_uri: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URI")
    mongo_db: str = Field(default="veriglow", description="MongoDB database name")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    
    # Security
    jwt_secret: str = Field(default="change-me", description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration (minutes)")
    refresh_token_expire_minutes: int = Field(default=1440, description="Refresh token expiration (minutes)")
    
    # CORS
    frontend_origins: str = Field(default="http://localhost:3000", description="Allowed CORS origins (comma-separated)")
    cors_max_age: int = Field(default=600, description="CORS preflight cache duration (seconds)")
    
    # Rate Limiting
    rate_limit_default: int = Field(default=100, description="Default rate limit (requests per minute)")
    rate_limit_analyze: int = Field(default=20, description="Analysis endpoint rate limit")
    rate_limit_chat: int = Field(default=30, description="Chat endpoint rate limit")
    rate_limit_login: int = Field(default=5, description="Login endpoint rate limit")
    
    # Request Limits
    max_request_size_mb: int = Field(default=10, description="Maximum request size (MB)")
    
    # Account Security
    max_failed_login_attempts: int = Field(default=5, description="Max failed login attempts before lockout")
    account_lockout_minutes: int = Field(default=30, description="Account lockout duration (minutes)")
    failed_attempt_window_minutes: int = Field(default=15, description="Failed attempt tracking window (minutes)")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # External APIs
    google_factcheck_api_key: Optional[str] = Field(default=None, description="Google Fact Check API key")
    google_gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    news_api_key: Optional[str] = Field(default=None, description="News API key")
    
    # ML Model
    model_path: str = Field(default="model_final.pkl", description="ML model file path")
    tfidf_path: str = Field(default="tfidf_final.pkl", description="TF-IDF vectorizer file path")
    
    # Celery
    celery_broker_url: Optional[str] = Field(default=None, description="Celery broker URL (defaults to redis_url)")
    celery_result_backend: Optional[str] = Field(default=None, description="Celery result backend (defaults to redis_url)")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    
    @property
    def celery_broker(self) -> str:
        """Get Celery broker URL."""
        return self.celery_broker_url or self.redis_url
    
    @property
    def celery_backend(self) -> str:
        """Get Celery result backend URL."""
        return self.celery_result_backend or self.redis_url
    
    @validator("frontend_origins")
    def parse_origins(cls, v):
        """Parse comma-separated origins into list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {', '.join(allowed)}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"Log level must be one of: {', '.join(allowed)}")
        return v_upper
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    @property
    def max_request_size_bytes(self) -> int:
        """Get max request size in bytes."""
        return self.max_request_size_mb * 1024 * 1024
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list."""
        if isinstance(self.frontend_origins, list):
            return self.frontend_origins
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]
    
    class Config:
        """Pydantic config."""
        # Use absolute path to .env file
        import os
        _current_dir = os.path.dirname(os.path.abspath(__file__))
        _backend_dir = os.path.dirname(_current_dir)
        env_file = os.path.join(_backend_dir, ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings instance
    """
    global _settings
    
    if _settings is None:
        _settings = Settings()
    
    return _settings


# Convenience function to reload settings
def reload_settings():
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
