"""
Legacy security module - maintained for backward compatibility.

This module provides backward-compatible wrappers around the new security module.
New code should import from backend.security package directly.
"""

from security.password_hasher import hash_password, verify_password
from security.jwt_manager import create_token, decode_token
from security.secret_generator import SecretGenerator

# Ensure JWT secret is secure on import
SecretGenerator.ensure_jwt_secret()

__all__ = [
    "hash_password",
    "verify_password", 
    "create_token",
    "decode_token",
    "SecretGenerator",
]