import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from auth import router as auth_router
from analyze_router import router as analyze_router
from history import router as history_router
from stats import router as stats_router
from chat import router as chat_router
from middleware.rate_limiter import RateLimitMiddleware, RateLimitConfig
from middleware.request_size_limit import RequestSizeLimitMiddleware
# from middleware.csrf_protection import CSRFProtectionMiddleware  # DISABLED in development
from middleware.error_handler import ErrorHandlerMiddleware
from services.analysis_service import get_analysis_service
import logging

logger = logging.getLogger(__name__)

# Get port from environment variable (Render provides this)
PORT = int(os.getenv("PORT", 8000))

# Get settings
settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    
    Loads ML models asynchronously in background to avoid blocking startup.
    """
    logger.info("Starting VeriGlow application...")
    
    # Load ML models asynchronously
    try:
        analysis_service = get_analysis_service()
        await analysis_service.load_models_async(
            settings.model_path,
            settings.tfidf_path
        )
        logger.info("ML models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ML models: {e}")
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down VeriGlow application...")
    
    # Disconnect cache if needed
    from cache import get_cache_manager
    try:
        cache = get_cache_manager()
        await cache.disconnect()
        logger.info("Cache disconnected")
    except Exception as e:
        logger.warning(f"Error disconnecting cache: {e}")
    
    logger.info("Application shutdown complete")

# Error handling middleware (first to catch all errors)
app.add_middleware(ErrorHandlerMiddleware, debug=settings.debug)

# Request size limit middleware
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_size=settings.max_request_size_bytes,
    exempt_paths=["/health", "/docs", "/openapi.json", "/redoc"],
)

# CSRF protection middleware - DISABLED in development
# app.add_middleware(
#     CSRFProtectionMiddleware,
#     cookie_secure=False,  # Allow HTTP in development
#     cookie_samesite="lax",  # Lax for cross-origin in development
#     exempt_paths={"/health", "/docs", "/openapi.json", "/redoc", "/api/v1/auth/login", "/api/v1/auth/signup", "/api/v1/chat", "/api/v1/chat/health", "/api/v1/analyze"},
# )

# CORS middleware with strict configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Strict whitelist from config
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With", "X-CSRF-Token"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    max_age=settings.cors_max_age,
)

# Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    redis_url=settings.redis_url,
    default_config=RateLimitConfig(requests_per_minute=settings.rate_limit_default),
    endpoint_configs={
        "/api/v1/analyze": RateLimitConfig(requests_per_minute=settings.rate_limit_analyze),
        "/api/v1/chat": RateLimitConfig(requests_per_minute=settings.rate_limit_chat),
        "/api/v1/auth/login": RateLimitConfig(requests_per_minute=settings.rate_limit_login),
    },
    exempt_paths=["/health", "/docs", "/openapi.json", "/redoc"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Debug: Print router info
print(f"Auth router: {auth_router}")
print(f"Auth router prefix: {auth_router.prefix}")
print(f"Auth router routes: {len(auth_router.routes)}")

app.include_router(auth_router)
app.include_router(analyze_router)
app.include_router(history_router)
app.include_router(stats_router)
app.include_router(chat_router)

# Debug: Print all registered routes
print("\n=== ALL REGISTERED ROUTES ===")
for route in app.routes:
    print(f"  {route.path} - {route.methods if hasattr(route, 'methods') else 'N/A'}")
print("=" * 40)

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=PORT, reload=settings.is_development)