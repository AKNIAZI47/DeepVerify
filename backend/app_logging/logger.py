"""
Structured logging configuration for VeriGlow.

This module provides JSON-formatted structured logging with configurable
log levels and context enrichment for better observability.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import traceback


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Outputs log records as JSON with consistent structure including:
    - timestamp
    - level
    - message
    - logger name
    - context fields
    - exception info (if present)
    """
    
    def __init__(
        self,
        include_extra: bool = True,
        include_exc_info: bool = True,
    ):
        """
        Initialize JSON formatter.
        
        Args:
            include_extra: Include extra fields from log record
            include_exc_info: Include exception information
        """
        super().__init__()
        self.include_extra = include_extra
        self.include_exc_info = include_exc_info
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        # Base log structure
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add source location
        if record.pathname:
            log_data["source"] = {
                "file": Path(record.pathname).name,
                "line": record.lineno,
                "function": record.funcName,
            }
        
        # Add process/thread info
        log_data["process"] = {
            "pid": record.process,
            "thread": record.thread,
            "thread_name": record.threadName,
        }
        
        # Add exception info if present
        if record.exc_info and self.include_exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }
        
        # Add extra fields
        if self.include_extra:
            # Get all extra fields (not standard LogRecord attributes)
            standard_attrs = {
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'message', 'pathname', 'process', 'processName', 'relativeCreated',
                'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
            }
            
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in standard_attrs and not key.startswith('_'):
                    # Ensure value is JSON serializable
                    try:
                        json.dumps(value)
                        extra_fields[key] = value
                    except (TypeError, ValueError):
                        extra_fields[key] = str(value)
            
            if extra_fields:
                log_data["context"] = extra_fields
        
        return json.dumps(log_data)


class ContextLogger(logging.LoggerAdapter):
    """
    Logger adapter that adds context to all log messages.
    
    Useful for adding request-specific context like user_id, request_id, etc.
    """
    
    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        """
        Initialize context logger.
        
        Args:
            logger: Base logger
            context: Context dictionary to add to all logs
        """
        super().__init__(logger, context)
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message to add context.
        
        Args:
            msg: Log message
            kwargs: Log kwargs
            
        Returns:
            Tuple of (message, kwargs)
        """
        # Add context to extra
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        kwargs['extra'].update(self.extra)
        
        return msg, kwargs


class SecurityEventLogger:
    """
    Specialized logger for security events.
    
    Logs security-related events with consistent structure for
    security monitoring and alerting.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize security event logger.
        
        Args:
            logger: Base logger
        """
        self.logger = logger
    
    def log_failed_login(
        self,
        email: str,
        ip_address: str,
        reason: str,
        attempts: int = 1,
    ):
        """
        Log failed login attempt.
        
        Args:
            email: User email
            ip_address: Client IP address
            reason: Failure reason
            attempts: Number of attempts
        """
        self.logger.warning(
            "Failed login attempt",
            extra={
                "event_type": "failed_login",
                "email": email,
                "ip_address": ip_address,
                "reason": reason,
                "attempts": attempts,
            }
        )
    
    def log_account_lockout(
        self,
        email: str,
        ip_address: str,
        lockout_duration_minutes: int,
    ):
        """
        Log account lockout.
        
        Args:
            email: User email
            ip_address: Client IP address
            lockout_duration_minutes: Lockout duration
        """
        self.logger.warning(
            "Account locked due to failed login attempts",
            extra={
                "event_type": "account_lockout",
                "email": email,
                "ip_address": ip_address,
                "lockout_duration_minutes": lockout_duration_minutes,
            }
        )
    
    def log_rate_limit_exceeded(
        self,
        ip_address: str,
        endpoint: str,
        limit: int,
        current_count: int,
    ):
        """
        Log rate limit violation.
        
        Args:
            ip_address: Client IP address
            endpoint: API endpoint
            limit: Rate limit
            current_count: Current request count
        """
        self.logger.warning(
            "Rate limit exceeded",
            extra={
                "event_type": "rate_limit_exceeded",
                "ip_address": ip_address,
                "endpoint": endpoint,
                "limit": limit,
                "current_count": current_count,
            }
        )
    
    def log_suspicious_activity(
        self,
        activity_type: str,
        description: str,
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs,
    ):
        """
        Log suspicious activity.
        
        Args:
            activity_type: Type of suspicious activity
            description: Activity description
            ip_address: Client IP address
            user_id: User ID if authenticated
            **kwargs: Additional context
        """
        extra = {
            "event_type": "suspicious_activity",
            "activity_type": activity_type,
            "description": description,
        }
        
        if ip_address:
            extra["ip_address"] = ip_address
        if user_id:
            extra["user_id"] = user_id
        
        extra.update(kwargs)
        
        self.logger.warning("Suspicious activity detected", extra=extra)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format ("json" or "text")
        log_file: Optional log file path
        
    Returns:
        Configured root logger
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # Create formatter
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def get_context_logger(
    name: str,
    context: Dict[str, Any],
) -> ContextLogger:
    """
    Get a context logger instance.
    
    Args:
        name: Logger name
        context: Context dictionary
        
    Returns:
        Context logger instance
    """
    logger = get_logger(name)
    return ContextLogger(logger, context)


def get_security_logger(name: str = "security") -> SecurityEventLogger:
    """
    Get a security event logger.
    
    Args:
        name: Logger name
        
    Returns:
        Security event logger
    """
    logger = get_logger(name)
    return SecurityEventLogger(logger)


# Initialize logging on module import
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
LOG_FILE = os.getenv("LOG_FILE")

setup_logging(
    log_level=LOG_LEVEL,
    log_format=LOG_FORMAT,
    log_file=LOG_FILE,
)
