"""
Encryption service module using AES-256.

This module provides symmetric encryption/decryption for sensitive data
using AES-256 in GCM mode for authenticated encryption.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Tuple


class EncryptionService:
    """Provides AES-256-GCM encryption and decryption."""
    
    KEY_SIZE = 32  # 256 bits
    NONCE_SIZE = 12  # 96 bits (recommended for GCM)
    SALT_SIZE = 16  # 128 bits
    
    def __init__(self, master_key: str):
        """
        Initialize encryption service.
        
        Args:
            master_key: Master encryption key (will be used to derive actual keys)
        """
        if not master_key or len(master_key) < 32:
            raise ValueError("Master key must be at least 32 characters")
        
        self.master_key = master_key.encode('utf-8')
    
    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive an encryption key from the master key using PBKDF2.
        
        Args:
            salt: Salt for key derivation
            
        Returns:
            Derived 256-bit key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(self.master_key)
    
    def encrypt(self, plaintext: str, associated_data: str = "") -> str:
        """
        Encrypt plaintext using AES-256-GCM.
        
        Args:
            plaintext: Text to encrypt
            associated_data: Optional associated data for authentication
            
        Returns:
            Base64-encoded encrypted data (format: salt:nonce:ciphertext)
        """
        # Generate random salt and nonce
        salt = os.urandom(self.SALT_SIZE)
        nonce = os.urandom(self.NONCE_SIZE)
        
        # Derive encryption key
        key = self._derive_key(salt)
        
        # Encrypt
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(
            nonce,
            plaintext.encode('utf-8'),
            associated_data.encode('utf-8') if associated_data else None
        )
        
        # Combine salt, nonce, and ciphertext
        encrypted_data = salt + nonce + ciphertext
        
        # Return base64-encoded result
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_data: str, associated_data: str = "") -> str:
        """
        Decrypt data encrypted with AES-256-GCM.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            associated_data: Optional associated data for authentication
            
        Returns:
            Decrypted plaintext
            
        Raises:
            ValueError: If decryption fails (wrong key or tampered data)
        """
        try:
            # Decode base64
            data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            
            # Extract salt, nonce, and ciphertext
            salt = data[:self.SALT_SIZE]
            nonce = data[self.SALT_SIZE:self.SALT_SIZE + self.NONCE_SIZE]
            ciphertext = data[self.SALT_SIZE + self.NONCE_SIZE:]
            
            # Derive decryption key
            key = self._derive_key(salt)
            
            # Decrypt
            aesgcm = AESGCM(key)
            plaintext_bytes = aesgcm.decrypt(
                nonce,
                ciphertext,
                associated_data.encode('utf-8') if associated_data else None
            )
            
            return plaintext_bytes.decode('utf-8')
        
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_dict(self, data: dict, associated_data: str = "") -> dict:
        """
        Encrypt sensitive fields in a dictionary.
        
        Args:
            data: Dictionary with data to encrypt
            associated_data: Optional associated data
            
        Returns:
            Dictionary with encrypted values
        """
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, str):
                encrypted[key] = self.encrypt(value, associated_data)
            else:
                encrypted[key] = self.encrypt(str(value), associated_data)
        return encrypted
    
    def decrypt_dict(self, encrypted_data: dict, associated_data: str = "") -> dict:
        """
        Decrypt sensitive fields in a dictionary.
        
        Args:
            encrypted_data: Dictionary with encrypted values
            associated_data: Optional associated data
            
        Returns:
            Dictionary with decrypted values
        """
        decrypted = {}
        for key, value in encrypted_data.items():
            decrypted[key] = self.decrypt(value, associated_data)
        return decrypted
    
    @staticmethod
    def generate_master_key() -> str:
        """
        Generate a random master encryption key.
        
        Returns:
            Base64-encoded random key suitable for use as master key
        """
        random_bytes = os.urandom(32)
        return base64.urlsafe_b64encode(random_bytes).decode('utf-8')


def encrypt_sensitive_data(data: str, key: str) -> str:
    """
    Convenience function to encrypt sensitive data.
    
    Args:
        data: Data to encrypt
        key: Encryption key
        
    Returns:
        Encrypted data
    """
    service = EncryptionService(key)
    return service.encrypt(data)


def decrypt_sensitive_data(encrypted_data: str, key: str) -> str:
    """
    Convenience function to decrypt sensitive data.
    
    Args:
        encrypted_data: Encrypted data
        key: Decryption key
        
    Returns:
        Decrypted data
    """
    service = EncryptionService(key)
    return service.decrypt(encrypted_data)
