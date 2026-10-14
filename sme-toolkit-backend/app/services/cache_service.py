"""
Cache service for performance optimization
"""
import json
from typing import Any, Optional
from datetime import datetime, timedelta
import hashlib


class CacheService:
    """
    Simple in-memory cache service for performance optimization
    Can be extended to use Redis for distributed caching
    """
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._default_ttl = 300  # 5 minutes default TTL
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        """
        if key not in self._cache:
            return None
        
        # Check if expired
        if key in self._timestamps:
            timestamp = self._timestamps[key]
            if datetime.utcnow() - timestamp > timedelta(seconds=self._default_ttl):
                # Expired, remove from cache
                self.delete(key)
                return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache with optional TTL
        """
        self._cache[key] = value
        self._timestamps[key] = datetime.utcnow()
        
        # Set expiration if TTL provided
        if ttl:
            # In a real implementation, this would use a proper TTL mechanism
            pass
    
    def delete(self, key: str) -> None:
        """
        Delete value from cache
        """
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
    
    def clear(self) -> None:
        """
        Clear all cache entries
        """
        self._cache.clear()
        self._timestamps.clear()
    
    def generate_key(self, *args: Any) -> str:
        """
        Generate a cache key from arguments
        """
        key_string = "|".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        """
        return {
            "size": len(self._cache),
            "keys": list(self._cache.keys())
        }


# Global cache instance
_cache_service = CacheService()


def get_cache() -> CacheService:
    """
    Get the global cache service instance
    """
    return _cache_service
