"""
Redis cache manager for production scale
"""

import redis.asyncio as redis
from typing import Optional, Any, List
import json
import hashlib
from functools import wraps
import logging
import os

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))


class RedisCacheManager:
    """Production Redis cache with cluster support"""
    
    _instance: Optional["RedisCacheManager"] = None
    
    def __init__(self, redis_url: str = REDIS_URL):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
    
    @classmethod
    def get_instance(cls) -> "RedisCacheManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    async def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=REDIS_MAX_CONNECTIONS,
                socket_keepalive=True,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )
        return self._client
    
    async def get(self, key: str) -> Optional[Any]:
        value = await (await self.client).get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 300,
        nx: bool = False
    ) -> bool:
        try:
            serialized = json.dumps(value) if not isinstance(value, str) else value
            return await (await self.client).set(
                key, 
                serialized, 
                ex=ttl,
                nx=nx
            )
        except (TypeError, ValueError) as e:
            logger.error(f"Cache serialization error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        return await (await self.client).delete(key) > 0
    
    async def delete_many(self, keys: List[str]) -> int:
        if not keys:
            return 0
        return await (await self.client).delete(*keys)
    
    async def invalidate_pattern(self, pattern: str) -> int:
        keys = []
        async for key in (await self.client).scan_iter(match=pattern):
            keys.append(key)
        if keys:
            return await (await self.client).delete(*keys)
        return 0
    
    async def exists(self, key: str) -> bool:
        return await (await self.client).exists(key) > 0
    
    async def ttl(self, key: str) -> int:
        return await (await self.client).ttl(key)
    
    async def increment(self, key: str, amount: int = 1) -> int:
        return await (await self.client).incrby(key, amount)
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        return await (await self.client).decrby(key, amount)
    
    async def get_or_set(
        self, 
        key: str, 
        factory: callable,
        ttl: int = 300
    ) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        value = await factory() if callable(factory) else factory
        await self.set(key, value, ttl)
        return value
    
    @staticmethod
    def cache_key(*args, **kwargs) -> str:
        key_data = f"{':'.join(str(a) for a in args)}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def health_check(self) -> dict:
        try:
            client = await self.client
            await client.ping()
            info = await client.info()
            return {
                "healthy": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"healthy": False, "error": str(e)}
    
    async def close(self):
        if self._client:
            await self._client.close()
            logger.info("Redis connection closed")


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching async function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = RedisCacheManager.get_instance()
            
            instance = args[0] if args else None
            cache_key = f"{key_prefix}:{func.__name__}:{cache.cache_key(*args[1:] if instance else args, **kwargs)}"
            
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = await func(*args, **kwargs)
            
            if result is not None:
                await cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


CACHE_TTLS = {
    "user_profile": 1800,
    "user_subscription": 300,
    "token_balance": 60,
    "provider_status": 30,
    "business_scores": 3600,
    "analytics_dashboard": 900,
    "available_models": 7200,
    "lead_scores": 300,
    "marketplace_connections": 600,
}


def get_cache_key(prefix: str, *identifiers) -> str:
    return f"{prefix}:{':'.join(str(i) for i in identifiers)}"


cache = RedisCacheManager.get_instance()
