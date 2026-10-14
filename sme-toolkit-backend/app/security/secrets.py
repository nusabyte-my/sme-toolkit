"""
Secrets management with rotation support
"""

from typing import Optional, Callable, Dict, List
import os
from functools import lru_cache
import logging
import asyncio

logger = logging.getLogger(__name__)


class SecretsManager:
    """Centralized secrets management with rotation support"""
    
    _instance: Optional["SecretsManager"] = None
    
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._rotation_callbacks: Dict[str, List[Callable]] = {}
        self._ttl: Dict[str, int] = {}
        self._loaded_at: Dict[str, float] = {}
    
    @classmethod
    def get_instance(cls) -> "SecretsManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        if key in self._cache:
            return self._cache[key]
        
        value = os.getenv(key)
        
        if value:
            self._cache[key] = value
            return value
        
        return default
    
    def get_required(self, key: str) -> str:
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required secret '{key}' not found")
        return value
    
    def set(self, key: str, value: str, ttl: Optional[int] = None):
        self._cache[key] = value
        if ttl:
            self._ttl[key] = ttl
            import time
            self._loaded_at[key] = time.time()
    
    def is_expired(self, key: str) -> bool:
        if key not in self._ttl or key not in self._loaded_at:
            return False
        
        import time
        elapsed = time.time() - self._loaded_at[key]
        return elapsed > self._ttl[key]
    
    def register_rotation_callback(self, key: str, callback: Callable):
        if key not in self._rotation_callbacks:
            self._rotation_callbacks[key] = []
        self._rotation_callbacks[key].append(callback)
        logger.debug(f"Registered rotation callback for {key}")
    
    async def rotate_secret(self, key: str, new_value: str):
        old_value = self._cache.get(key)
        self._cache[key] = new_value
        
        if key in self._loaded_at:
            import time
            self._loaded_at[key] = time.time()
        
        if key in self._rotation_callbacks:
            for callback in self._rotation_callbacks[key]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(old_value, new_value)
                    else:
                        callback(old_value, new_value)
                    logger.info(f"Executed rotation callback for {key}")
                except Exception as e:
                    logger.error(f"Rotation callback failed for {key}: {e}")
    
    def get_all_keys(self) -> List[str]:
        return list(set(list(self._cache.keys()) + self._get_env_secret_keys()))
    
    def _get_env_secret_keys(self) -> List[str]:
        secret_patterns = [
            "API_KEY", "SECRET", "PASSWORD", "TOKEN", 
            "CREDENTIAL", "PRIVATE", "JWT"
        ]
        return [
            key for key in os.environ 
            if any(pattern in key.upper() for pattern in secret_patterns)
        ]
    
    def clear_cache(self):
        self._cache.clear()
        self._loaded_at.clear()
        logger.info("Secrets cache cleared")


@lru_cache()
def get_secrets_manager() -> SecretsManager:
    return SecretsManager.get_instance()


secrets = get_secrets_manager()


def get_api_key(provider: str) -> Optional[str]:
    key_mapping = {
        "gemini": "GEMINI_API_KEY",
        "groq": "GROQ_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "fiqstr": "FIQSTR_API_KEY",
        "fiqstr-v2": "FIQSTR_API_KEY",
        "openai": "OPENAI_API_KEY",
        "replicate": "REPLICATE_API_KEY",
        "stability": "STABILITY_API_KEY",
        "kling": "KLING_API_KEY",
        "stripe": "STRIPE_SECRET_KEY",
    }
    
    env_key = key_mapping.get(provider.lower())
    if not env_key:
        env_key = f"{provider.upper()}_API_KEY"
    
    return secrets.get(env_key)


class SecretRotationHandler:
    """Handles automatic secret rotation"""
    
    def __init__(self, secrets_manager: SecretsManager):
        self.secrets_manager = secrets_manager
        self._rotation_schedule: Dict[str, int] = {}
    
    def schedule_rotation(self, key: str, interval_seconds: int):
        self._rotation_schedule[key] = interval_seconds
        logger.info(f"Scheduled rotation for {key} every {interval_seconds}s")
    
    async def check_and_rotate(self):
        for key, interval in self._rotation_schedule.items():
            if self.secrets_manager.is_expired(key):
                logger.warning(f"Secret {key} has expired and needs rotation")
