"""
Password hashing module using bcrypt.

This module provides secure password hashing and verification using bcrypt.
"""

import bcrypt
from typing import Tuple
import re


class PasswordHasher:
    """Handles password hashing and verification using bcrypt."""
    
    # Password requirements
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        # Bcrypt has a 72 byte limit, truncate if needed
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            password_bytes = plain_password.encode('utf-8')[:72]
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False
    
    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """
        Check if a password hash needs to be updated.
        
        Args:
            hashed_password: Hashed password to check
            
        Returns:
            False (bcrypt doesn't need rehashing)
        """
        return False
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, list[str]]:
        """
        Validate password strength against security requirements.
        
        Requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        if len(password) < PasswordHasher.MIN_LENGTH:
            errors.append(f"Password must be at least {PasswordHasher.MIN_LENGTH} characters long")
        
        if PasswordHasher.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if PasswordHasher.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if PasswordHasher.REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if PasswordHasher.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def hash_and_validate(password: str) -> Tuple[str, bool, list[str]]:
        """
        Validate password strength and hash if valid.
        
        Args:
            password: Password to validate and hash
            
        Returns:
            Tuple of (hashed_password or empty_string, is_valid, error_messages)
        """
        is_valid, errors = PasswordHasher.validate_password_strength(password)
        
        if is_valid:
            hashed = PasswordHasher.hash_password(password)
            return (hashed, True, [])
        else:
            return ("", False, errors)


# Backward compatibility with existing code
def hash_password(password: str) -> str:
    """Legacy function for backward compatibility."""
    return PasswordHasher.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Legacy function for backward compatibility."""
    return PasswordHasher.verify_password(plain_password, hashed_password)
