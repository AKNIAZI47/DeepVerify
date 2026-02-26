"""
Request size limit middleware.

This middleware enforces maximum request body size limits to prevent
denial of service attacks and resource exhaustion.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request body size limits."""
    
    def __init__(
        self,
        app,
        max_size: int = 10 * 1024 * 1024,  # 10MB default
        exempt_paths: Optional[list[str]] = None,
    ):
        """
        Initialize request size limit middleware.
        
        Args:
            app: FastAPI application
            max_size: Maximum request body size in bytes (default: 10MB)
            exempt_paths: List of paths exempt from size limits
        """
        super().__init__(app)
        self.max_size = max_size
        self.exempt_paths = set(exempt_paths or ["/health", "/docs", "/openapi.json"])
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with size limit enforcement.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response or error if size limit exceeded
        """
        path = request.url.path
        
        # Skip size check for exempt paths
        if path in self.exempt_paths:
            return await call_next(request)
        
        # Check Content-Length header
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                content_length = int(content_length)
                
                if content_length > self.max_size:
                    logger.warning(
                        f"Request size limit exceeded: {content_length} bytes "
                        f"(max: {self.max_size}) for {path}"
                    )
                    
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "error": {
                                "code": "REQUEST_TOO_LARGE",
                                "message": f"Request body too large. Maximum size is {self.max_size / (1024 * 1024):.1f}MB",
                                "max_size_bytes": self.max_size,
                                "received_size_bytes": content_length,
                            }
                        }
                    )
            except ValueError:
                # Invalid Content-Length header, let it through
                # (will be caught by request parsing if actually too large)
                pass
        
        # Process request
        return await call_next(request)


def format_size(size_bytes: int) -> str:
    """
    Format byte size to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "10.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
