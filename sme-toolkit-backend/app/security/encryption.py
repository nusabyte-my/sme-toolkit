"""
API key encryption for sensitive credential storage
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Encryption/decryption error"""
    pass


class APIKeyEncryption:
    """Encrypt/decrypt sensitive API keys in database"""
    
    _instance: Optional["APIKeyEncryption"] = None
    
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or os.getenv("ENCRYPTION_MASTER_KEY")
        self._fernet: Optional[Fernet] = None
        
        if not self.master_key:
            logger.warning(
                "ENCRYPTION_MASTER_KEY not set. Credentials will not be encrypted. "
                "Set ENCRYPTION_MASTER_KEY in production."
            )
    
    @classmethod
    def get_instance(cls) -> "APIKeyEncryption":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def fernet(self) -> Fernet:
        if not self.master_key:
            raise EncryptionError("Encryption master key not configured")
        
        if self._fernet is None:
            salt = os.getenv("ENCRYPTION_SALT", "sme_toolkit_salt_2024").encode()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(
                kdf.derive(self.master_key.encode())
            )
            self._fernet = Fernet(key)
        
        return self._fernet
    
    def encrypt(self, plaintext: Optional[str]) -> Optional[str]:
        if not plaintext:
            return plaintext
        
        if not self.master_key:
            return plaintext
        
        try:
            encrypted = self.fernet.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError(f"Failed to encrypt: {e}")
    
    def decrypt(self, ciphertext: Optional[str]) -> Optional[str]:
        if not ciphertext:
            return ciphertext
        
        if not self.master_key:
            return ciphertext
        
        try:
            decoded = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise EncryptionError(f"Failed to decrypt: {e}")
    
    def encrypt_dict(self, data: dict, keys_to_encrypt: list) -> dict:
        result = data.copy()
        for key in keys_to_encrypt:
            if key in result and result[key]:
                result[key] = self.encrypt(str(result[key]))
        return result
    
    def decrypt_dict(self, data: dict, keys_to_decrypt: list) -> dict:
        result = data.copy()
        for key in keys_to_decrypt:
            if key in result and result[key]:
                result[key] = self.decrypt(result[key])
        return result
    
    def is_encrypted(self, value: str) -> bool:
        if not value:
            return False
        
        try:
            base64.urlsafe_b64decode(value.encode())
            return True
        except Exception:
            return False


encryption = APIKeyEncryption.get_instance()


SENSITIVE_FIELDS = [
    "api_key",
    "secret_key",
    "access_token",
    "refresh_token",
    "password",
    "private_key",
    "credential",
]


def encrypt_sensitive_fields(data: dict) -> dict:
    return encryption.encrypt_dict(data, SENSITIVE_FIELDS)


def decrypt_sensitive_fields(data: dict) -> dict:
    return encryption.decrypt_dict(data, SENSITIVE_FIELDS)
