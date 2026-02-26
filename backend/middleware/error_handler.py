"""
Centralized error handling middleware.

This middleware catches all unhandled exceptions and formats them
into consistent JSON error responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
from datetime import datetime
import traceback
import logging
import uuid

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standard error response format."""
    
    def __init__(
        self,
        code: str,
        message: str,
        details: dict = None,
        error_id: str = None,
    ):
        """
        Initialize error response.
        
        Args:
            code: Error code (e.g., "VALIDATION_ERROR")
            message: Human-readable error message
            details: Additional error details
            error_id: Unique error identifier for tracking
        """
        self.code = code
        self.message = message
        self.details = details or {}
        self.error_id = error_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "error_id": self.error_id,
                "timestamp": self.timestamp,
            }
        }


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Centralized error handling middleware.
    
    Catches all exceptions and returns consistent JSON error responses.
    """
    
    def __init__(self, app, debug: bool = False):
        """
        Initialize error handler middleware.
        
        Args:
            app: FastAPI application
            debug: Whether to include stack traces in responses
        """
        super().__init__(app)
        self.debug = debug
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with error handling.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response or error response
        """
        try:
            response = await call_next(request)
            return response
        
        except HTTPException as exc:
            # FastAPI HTTP exceptions (already formatted)
            return self._handle_http_exception(exc, request)
        
        except StarletteHTTPException as exc:
            # Starlette HTTP exceptions
            return self._handle_http_exception(exc, request)
        
        except RequestValidationError as exc:
            # Pydantic validation errors
            return self._handle_validation_error(exc, request)
        
        except ValidationError as exc:
            # Pydantic validation errors (direct)
            return self._handle_pydantic_validation_error(exc, request)
        
        except Exception as exc:
            # All other unhandled exceptions
            return self._handle_unexpected_error(exc, request)
    
    def _handle_http_exception(
        self,
        exc: HTTPException,
        request: Request
    ) -> JSONResponse:
        """
        Handle HTTP exceptions.
        
        Args:
            exc: HTTP exception
            request: Request object
            
        Returns:
            JSON error response
        """
        error_id = str(uuid.uuid4())
        
        # Log the error
        logger.warning(
            f"HTTP {exc.status_code} on {request.method} {request.url.path}: "
            f"{exc.detail} [error_id: {error_id}]"
        )
        
        # Determine error code
        status_code = exc.status_code
        if status_code == 400:
            code = "BAD_REQUEST"
        elif status_code == 401:
            code = "UNAUTHORIZED"
        elif status_code == 403:
            code = "FORBIDDEN"
        elif status_code == 404:
            code = "NOT_FOUND"
        elif status_code == 409:
            code = "CONFLICT"
        elif status_code == 422:
            code = "UNPROCESSABLE_ENTITY"
        elif status_code == 429:
            code = "RATE_LIMIT_EXCEEDED"
        else:
            code = f"HTTP_{status_code}"
        
        error = ErrorResponse(
            code=code,
            message=str(exc.detail),
            error_id=error_id,
        )
        
        return JSONResponse(
            status_code=status_code,
            content=error.to_dict(),
        )
    
    def _handle_validation_error(
        self,
        exc: RequestValidationError,
        request: Request
    ) -> JSONResponse:
        """
        Handle request validation errors.
        
        Args:
            exc: Validation error
            request: Request object
            
        Returns:
            JSON error response
        """
        error_id = str(uuid.uuid4())
        
        # Extract validation errors
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })
        
        # Log the error
        logger.warning(
            f"Validation error on {request.method} {request.url.path}: "
            f"{len(errors)} field(s) [error_id: {error_id}]"
        )
        
        error = ErrorResponse(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": errors},
            error_id=error_id,
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error.to_dict(),
        )
    
    def _handle_pydantic_validation_error(
        self,
        exc: ValidationError,
        request: Request
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors.
        
        Args:
            exc: Validation error
            request: Request object
            
        Returns:
            JSON error response
        """
        error_id = str(uuid.uuid4())
        
        # Extract validation errors
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })
        
        # Log the error
        logger.warning(
            f"Pydantic validation error on {request.method} {request.url.path}: "
            f"{len(errors)} field(s) [error_id: {error_id}]"
        )
        
        error = ErrorResponse(
            code="VALIDATION_ERROR",
            message="Data validation failed",
            details={"errors": errors},
            error_id=error_id,
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error.to_dict(),
        )
    
    def _handle_unexpected_error(
        self,
        exc: Exception,
        request: Request
    ) -> JSONResponse:
        """
        Handle unexpected errors.
        
        Args:
            exc: Exception
            request: Request object
            
        Returns:
            JSON error response
        """
        error_id = str(uuid.uuid4())
        
        # Log the full error with stack trace
        logger.error(
            f"Unexpected error on {request.method} {request.url.path}: "
            f"{type(exc).__name__}: {str(exc)} [error_id: {error_id}]",
            exc_info=True
        )
        
        # Build error response
        details = {}
        
        if self.debug:
            # Include stack trace in debug mode
            details["exception_type"] = type(exc).__name__
            details["exception_message"] = str(exc)
            details["traceback"] = traceback.format_exc()
        
        error = ErrorResponse(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
            details=details,
            error_id=error_id,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error.to_dict(),
        )


def create_error_response(
    code: str,
    message: str,
    status_code: int = 500,
    details: dict = None,
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        code: Error code
        message: Error message
        status_code: HTTP status code
        details: Additional details
        
    Returns:
        JSON error response
    """
    error = ErrorResponse(code=code, message=message, details=details)
    return JSONResponse(status_code=status_code, content=error.to_dict())
