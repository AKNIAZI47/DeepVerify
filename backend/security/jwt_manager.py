"""
JWT token management module.

This module provides JWT token creation, validation, and refresh functionality
with secure defaults and proper error handling.
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum


class TokenType(Enum):
    """Token type enumeration."""
    ACCESS = "access"
    REFRESH = "refresh"


class JWTManager:
    """Manages JWT token creation and validation."""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_minutes: int = 1440,  # 24 hours
    ):
        """
        Initialize JWT manager.
        
        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_minutes: Refresh token expiration in minutes
        """
        if not secret_key or len(secret_key) < 16:
            raise ValueError("JWT secret key must be at least 16 characters")
        
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes
    
    def create_token(
        self,
        subject: str,
        token_type: TokenType,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a JWT token.
        
        Args:
            subject: Token subject (usually user ID)
            token_type: Type of token (access or refresh)
            expires_delta: Custom expiration delta (overrides defaults)
            additional_claims: Additional claims to include in token
            
        Returns:
            Encoded JWT token string
        """
        if expires_delta is None:
            if token_type == TokenType.ACCESS:
                expires_delta = timedelta(minutes=self.access_token_expire_minutes)
            else:
                expires_delta = timedelta(minutes=self.refresh_token_expire_minutes)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": subject,
            "type": token_type.value,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_access_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create an access token.
        
        Args:
            subject: Token subject (usually user ID)
            expires_delta: Custom expiration delta
            additional_claims: Additional claims to include
            
        Returns:
            Encoded access token
        """
        return self.create_token(
            subject=subject,
            token_type=TokenType.ACCESS,
            expires_delta=expires_delta,
            additional_claims=additional_claims,
        )
    
    def create_refresh_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a refresh token.
        
        Args:
            subject: Token subject (usually user ID)
            expires_delta: Custom expiration delta
            additional_claims: Additional claims to include
            
        Returns:
            Encoded refresh token
        """
        return self.create_token(
            subject=subject,
            token_type=TokenType.REFRESH,
            expires_delta=expires_delta,
            additional_claims=additional_claims,
        )
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            jwt.ExpiredSignatureError: If token has expired
            jwt.InvalidTokenError: If token is invalid
        """
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
    
    def verify_token(self, token: str, expected_type: Optional[TokenType] = None) -> Dict[str, Any]:
        """
        Verify a token and optionally check its type.
        
        Args:
            token: JWT token string
            expected_type: Expected token type (access or refresh)
            
        Returns:
            Decoded token payload
            
        Raises:
            jwt.ExpiredSignatureError: If token has expired
            jwt.InvalidTokenError: If token is invalid
            ValueError: If token type doesn't match expected type
        """
        payload = self.decode_token(token)
        
        if expected_type is not None:
            token_type = payload.get("type")
            if token_type != expected_type.value:
                raise ValueError(
                    f"Invalid token type. Expected {expected_type.value}, got {token_type}"
                )
        
        return payload
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Create a new access token from a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            jwt.ExpiredSignatureError: If refresh token has expired
            jwt.InvalidTokenError: If refresh token is invalid
            ValueError: If token is not a refresh token
        """
        payload = self.verify_token(refresh_token, TokenType.REFRESH)
        subject = payload.get("sub")
        
        if not subject:
            raise ValueError("Token missing subject claim")
        
        return self.create_access_token(subject)


# Backward compatibility with existing code
def create_token(user_id: str, expire_minutes: int, token_type: str) -> str:
    """Legacy function for backward compatibility."""
    from config.settings import get_settings
    
    settings = get_settings()
    manager = JWTManager(
        secret_key=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    
    expires_delta = timedelta(minutes=expire_minutes)
    
    if token_type == "access":
        return manager.create_access_token(user_id, expires_delta)
    else:
        return manager.create_refresh_token(user_id, expires_delta)


def decode_token(token: str) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    from config.settings import get_settings
    
    settings = get_settings()
    manager = JWTManager(secret_key=settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return manager.decode_token(token)
