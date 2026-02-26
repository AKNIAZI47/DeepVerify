"""
CSRF protection middleware using double-submit cookie pattern.

This middleware protects against Cross-Site Request Forgery attacks
by requiring a CSRF token in both a cookie and request header/body.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Set
import secrets
import logging

logger = logging.getLogger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection using double-submit cookie pattern.
    
    The middleware:
    1. Sets a CSRF token cookie on GET requests
    2. Validates CSRF token on state-changing requests (POST, PUT, DELETE, PATCH)
    3. Compares token from cookie with token from header/body
    """
    
    # HTTP methods that require CSRF protection
    PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}
    
    # Safe methods that don't require CSRF protection
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    
    def __init__(
        self,
        app,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        cookie_secure: bool = True,
        cookie_httponly: bool = False,  # Must be False so JS can read it
        cookie_samesite: str = "strict",
        exempt_paths: Optional[Set[str]] = None,
    ):
        """
        Initialize CSRF protection middleware.
        
        Args:
            app: FastAPI application
            cookie_name: Name of CSRF cookie
            header_name: Name of CSRF header
            cookie_secure: Set Secure flag on cookie (HTTPS only)
            cookie_httponly: Set HttpOnly flag (should be False for CSRF)
            cookie_samesite: SameSite cookie attribute
            exempt_paths: Set of paths exempt from CSRF protection
        """
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.exempt_paths = exempt_paths or {
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/api/v1/auth/login",  # Login doesn't need CSRF (uses credentials)
            "/api/v1/auth/signup",  # Signup doesn't need CSRF
        }
    
    def _generate_csrf_token(self) -> str:
        """
        Generate a new CSRF token.
        
        Returns:
            Random CSRF token string
        """
        return secrets.token_urlsafe(32)
    
    def _get_csrf_token_from_cookie(self, request: Request) -> Optional[str]:
        """
        Extract CSRF token from cookie.
        
        Args:
            request: FastAPI request
            
        Returns:
            CSRF token or None if not found
        """
        return request.cookies.get(self.cookie_name)
    
    def _get_csrf_token_from_header(self, request: Request) -> Optional[str]:
        """
        Extract CSRF token from header.
        
        Args:
            request: FastAPI request
            
        Returns:
            CSRF token or None if not found
        """
        return request.headers.get(self.header_name)
    
    async def _get_csrf_token_from_body(self, request: Request) -> Optional[str]:
        """
        Extract CSRF token from request body (for form submissions).
        
        Args:
            request: FastAPI request
            
        Returns:
            CSRF token or None if not found
        """
        # Only check body for form submissions
        content_type = request.headers.get("content-type", "")
        
        if "application/x-www-form-urlencoded" in content_type:
            try:
                form = await request.form()
                return form.get("csrf_token")
            except Exception:
                return None
        
        return None
    
    def _set_csrf_cookie(self, response: Response, token: str):
        """
        Set CSRF token cookie on response.
        
        Args:
            response: FastAPI response
            token: CSRF token to set
        """
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            httponly=self.cookie_httponly,
            secure=self.cookie_secure,
            samesite=self.cookie_samesite,
            max_age=3600,  # 1 hour
        )
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with CSRF protection.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response or CSRF error
        """
        path = request.url.path
        method = request.method
        
        # Skip CSRF check for exempt paths
        if path in self.exempt_paths:
            return await call_next(request)
        
        # Skip CSRF check for safe methods
        if method in self.SAFE_METHODS:
            # For GET requests, set CSRF cookie if not present
            if method == "GET":
                response = await call_next(request)
                
                # Check if CSRF cookie exists
                csrf_cookie = self._get_csrf_token_from_cookie(request)
                
                if not csrf_cookie:
                    # Generate and set new CSRF token
                    new_token = self._generate_csrf_token()
                    self._set_csrf_cookie(response, new_token)
                
                return response
            
            return await call_next(request)
        
        # For state-changing methods, validate CSRF token
        if method in self.PROTECTED_METHODS:
            # Get token from cookie
            cookie_token = self._get_csrf_token_from_cookie(request)
            
            if not cookie_token:
                logger.warning(f"CSRF validation failed: No CSRF cookie for {method} {path}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": {
                            "code": "CSRF_TOKEN_MISSING",
                            "message": "CSRF token missing from cookie",
                        }
                    }
                )
            
            # Get token from header or body
            header_token = self._get_csrf_token_from_header(request)
            
            if not header_token:
                # Try to get from body (for form submissions)
                header_token = await self._get_csrf_token_from_body(request)
            
            if not header_token:
                logger.warning(f"CSRF validation failed: No CSRF token in header/body for {method} {path}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": {
                            "code": "CSRF_TOKEN_MISSING",
                            "message": f"CSRF token missing from {self.header_name} header or request body",
                        }
                    }
                )
            
            # Compare tokens (constant-time comparison to prevent timing attacks)
            if not secrets.compare_digest(cookie_token, header_token):
                logger.warning(f"CSRF validation failed: Token mismatch for {method} {path}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": {
                            "code": "CSRF_TOKEN_INVALID",
                            "message": "CSRF token validation failed",
                        }
                    }
                )
            
            # CSRF validation passed
            logger.debug(f"CSRF validation passed for {method} {path}")
        
        # Process request
        response = await call_next(request)
        
        # Rotate CSRF token on successful state-changing request
        if method in self.PROTECTED_METHODS and response.status_code < 400:
            new_token = self._generate_csrf_token()
            self._set_csrf_cookie(response, new_token)
        
        return response


def get_csrf_token(request: Request, cookie_name: str = "csrf_token") -> Optional[str]:
    """
    Helper function to get CSRF token from request.
    
    Args:
        request: FastAPI request
        cookie_name: Name of CSRF cookie
        
    Returns:
        CSRF token or None
    """
    return request.cookies.get(cookie_name)
