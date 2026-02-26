"""
Input validation module using Pydantic.

This module provides schema-based validation for all user inputs
to prevent injection attacks and ensure data integrity.
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, Any
from enum import Enum
import re


class ValidationError(Exception):
    """Custom validation error with detailed messages."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class TextInputSchema(BaseModel):
    """Schema for text input validation."""
    
    text: str = Field(..., min_length=1, max_length=50000)
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class URLInputSchema(BaseModel):
    """Schema for URL input validation."""
    
    url: str = Field(..., min_length=1, max_length=2048)
    
    @validator('url')
    def validate_url(cls, v):
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        if not url_pattern.match(v):
            raise ValueError("Invalid URL format. Must start with http:// or https://")
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'javascript:',
            r'data:',
            r'vbscript:',
            r'file:',
            r'<script',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("URL contains suspicious content")
        
        return v


class AnalyzeInputSchema(BaseModel):
    """Schema for analysis request validation."""
    
    text: str = Field(..., min_length=5, max_length=50000)
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        
        # Check if it's a URL
        if v.strip().lower().startswith(('http://', 'https://')):
            # Validate as URL
            try:
                URLInputSchema(url=v.strip())
            except Exception as e:
                raise ValueError(f"Invalid URL: {str(e)}")
        
        return v.strip()


class ChatInputSchema(BaseModel):
    """Schema for chat message validation."""
    
    message: str = Field(..., min_length=1, max_length=10000)
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        
        # Check for excessive repetition (spam detection)
        if len(set(v)) < len(v) * 0.1 and len(v) > 50:
            raise ValueError("Message appears to be spam")
        
        return v.strip()


class EmailInputSchema(BaseModel):
    """Schema for email validation."""
    
    email: EmailStr


class PasswordInputSchema(BaseModel):
    """Schema for password validation."""
    
    password: str = Field(..., min_length=12, max_length=128)


class PaginationSchema(BaseModel):
    """Schema for pagination parameters."""
    
    page: int = Field(default=1, ge=1, le=10000)
    page_size: int = Field(default=20, ge=1, le=100)
    
    @property
    def skip(self) -> int:
        """Calculate skip value for database queries."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit value for database queries."""
        return self.page_size


class SearchFilterSchema(BaseModel):
    """Schema for search and filter parameters."""
    
    query: Optional[str] = Field(None, max_length=500)
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    @validator('query')
    def validate_query(cls, v):
        if v is not None:
            # Remove potentially dangerous characters
            v = v.strip()
            if not v:
                return None
        return v
    
    @validator('date_from', 'date_to')
    def validate_date(cls, v):
        if v is not None:
            # Basic ISO date format validation
            date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
            if not date_pattern.match(v):
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class IDSchema(BaseModel):
    """Schema for ID validation."""
    
    id: str = Field(..., min_length=1, max_length=100)
    
    @validator('id')
    def validate_id(cls, v):
        # Allow alphanumeric, hyphens, and underscores only
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("ID contains invalid characters")
        return v


class InputValidator:
    """Main input validator class."""
    
    @staticmethod
    def validate_text(text: str) -> str:
        """
        Validate text input.
        
        Args:
            text: Text to validate
            
        Returns:
            Validated and sanitized text
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            schema = TextInputSchema(text=text)
            return schema.text
        except Exception as e:
            raise ValidationError("text", str(e))
    
    @staticmethod
    def validate_url(url: str) -> str:
        """
        Validate URL input.
        
        Args:
            url: URL to validate
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            schema = URLInputSchema(url=url)
            return schema.url
        except Exception as e:
            raise ValidationError("url", str(e))
    
    @staticmethod
    def validate_analyze_input(text: str) -> str:
        """
        Validate analysis input (text or URL).
        
        Args:
            text: Text or URL to validate
            
        Returns:
            Validated input
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            schema = AnalyzeInputSchema(text=text)
            return schema.text
        except Exception as e:
            raise ValidationError("text", str(e))
    
    @staticmethod
    def validate_chat_message(message: str) -> str:
        """
        Validate chat message.
        
        Args:
            message: Message to validate
            
        Returns:
            Validated message
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            schema = ChatInputSchema(message=message)
            return schema.message
        except Exception as e:
            raise ValidationError("message", str(e))
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email address.
        
        Args:
            email: Email to validate
            
        Returns:
            Validated email
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            schema = EmailInputSchema(email=email)
            return schema.email
        except Exception as e:
            raise ValidationError("email", str(e))
    
    @staticmethod
    def validate_pagination(page: int = 1, page_size: int = 20) -> PaginationSchema:
        """
        Validate pagination parameters.
        
        Args:
            page: Page number
            page_size: Items per page
            
        Returns:
            Validated pagination schema
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            return PaginationSchema(page=page, page_size=page_size)
        except Exception as e:
            raise ValidationError("pagination", str(e))
    
    @staticmethod
    def validate_id(id_value: str) -> str:
        """
        Validate ID.
        
        Args:
            id_value: ID to validate
            
        Returns:
            Validated ID
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            schema = IDSchema(id=id_value)
            return schema.id
        except Exception as e:
            raise ValidationError("id", str(e))
