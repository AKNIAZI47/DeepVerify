"""
Cryptographic secret generation module.

This module provides secure secret generation for JWT tokens and API keys
with minimum 256-bit entropy as required by security standards.
"""

import secrets
import base64
from typing import Optional
from pathlib import Path
import os


class SecretGenerator:
    """Generates cryptographically secure secrets with minimum 256-bit entropy."""
    
    MIN_ENTROPY_BYTES = 32  # 256 bits
    
    @staticmethod
    def generate_jwt_secret(entropy_bytes: int = MIN_ENTROPY_BYTES) -> str:
        """
        Generate a cryptographically secure JWT secret.
        
        Args:
            entropy_bytes: Number of random bytes (default: 32 for 256-bit entropy)
            
        Returns:
            Base64-encoded secret string
            
        Raises:
            ValueError: If entropy_bytes is less than MIN_ENTROPY_BYTES
        """
        if entropy_bytes < SecretGenerator.MIN_ENTROPY_BYTES:
            raise ValueError(
                f"Entropy must be at least {SecretGenerator.MIN_ENTROPY_BYTES} bytes "
                f"(256 bits), got {entropy_bytes}"
            )
        
        random_bytes = secrets.token_bytes(entropy_bytes)
        return base64.urlsafe_b64encode(random_bytes).decode('utf-8')
    
    @staticmethod
    def generate_api_key(prefix: str = "vg", entropy_bytes: int = MIN_ENTROPY_BYTES) -> str:
        """
        Generate a cryptographically secure API key with optional prefix.
        
        Args:
            prefix: Optional prefix for the API key (default: "vg")
            entropy_bytes: Number of random bytes (default: 32)
            
        Returns:
            API key string in format: prefix_base64encodedtoken
        """
        if entropy_bytes < SecretGenerator.MIN_ENTROPY_BYTES:
            raise ValueError(
                f"Entropy must be at least {SecretGenerator.MIN_ENTROPY_BYTES} bytes"
            )
        
        random_bytes = secrets.token_bytes(entropy_bytes)
        token = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
        return f"{prefix}_{token}"
    
    @staticmethod
    def ensure_jwt_secret(env_file_path: Optional[str] = None) -> str:
        """
        Ensure JWT secret exists, generate if missing.
        
        Checks if JWT_SECRET exists in environment or .env file.
        If not found or is the default weak value, generates a new secure secret.
        
        Args:
            env_file_path: Path to .env file (default: backend/.env)
            
        Returns:
            The JWT secret (existing or newly generated)
        """
        if env_file_path is None:
            env_file_path = Path(__file__).parent.parent / ".env"
        else:
            env_file_path = Path(env_file_path)
        
        # Check existing secret
        existing_secret = os.getenv("JWT_SECRET")
        
        # Weak default values that should be replaced
        weak_defaults = {"change-me", "secret", "dev", "test", ""}
        
        if existing_secret and existing_secret not in weak_defaults:
            return existing_secret
        
        # Generate new secret
        new_secret = SecretGenerator.generate_jwt_secret()
        
        # Update or create .env file
        env_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if env_file_path.exists():
            # Read existing content
            with open(env_file_path, 'r') as f:
                lines = f.readlines()
            
            # Update JWT_SECRET line or add if not present
            jwt_secret_found = False
            for i, line in enumerate(lines):
                if line.strip().startswith('JWT_SECRET='):
                    lines[i] = f'JWT_SECRET={new_secret}\n'
                    jwt_secret_found = True
                    break
            
            if not jwt_secret_found:
                lines.append(f'\nJWT_SECRET={new_secret}\n')
            
            # Write back
            with open(env_file_path, 'w') as f:
                f.writelines(lines)
        else:
            # Create new .env file
            with open(env_file_path, 'w') as f:
                f.write(f'JWT_SECRET={new_secret}\n')
        
        # Set in current environment
        os.environ['JWT_SECRET'] = new_secret
        
        return new_secret
    
    @staticmethod
    def generate_csrf_token() -> str:
        """
        Generate a CSRF token.
        
        Returns:
            URL-safe CSRF token string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_session_id() -> str:
        """
        Generate a session ID.
        
        Returns:
            URL-safe session ID string
        """
        return secrets.token_urlsafe(32)
