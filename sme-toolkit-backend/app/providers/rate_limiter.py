"""Rate limiting service for AI providers"""

from typing import Optional, Dict
from dataclasses import dataclass
from datetime import date, datetime
import logging

from app.services.cache_service import get_cache

logger = logging.getLogger(__name__)


@dataclass
class RateLimitResult:
    """Result of a rate limit check"""
    allowed: bool
    remaining: int
    reset_time: Optional[datetime] = None
    limit: int = 0


class TierRateLimiter:
    """Rate limiter based on user subscription tier"""

    # Tier limits configuration
    TIER_LIMITS = {
        "free": {
            "llm": {"daily": 50, "per_minute": 5},
            "image": {"daily": 10, "per_minute": 2},
            "video": {"daily": 0, "per_minute": 0}  # No video for free tier
        },
        "sme": {
            "llm": {"daily": 500, "per_minute": 30},
            "image": {"daily": 50, "per_minute": 5},
            "video": {"daily": 5, "per_minute": 1}
        },
        "business": {
            "llm": {"daily": 2000, "per_minute": 100},
            "image": {"daily": 200, "per_minute": 20},
            "video": {"daily": 20, "per_minute": 5}
        },
        "enterprise": {
            "llm": {"daily": 10000, "per_minute": 500},
            "image": {"daily": 1000, "per_minute": 100},
            "video": {"daily": 100, "per_minute": 20}
        }
    }

    def __init__(self):
        self.cache = get_cache()

    def _get_daily_key(self, user_id: str, modality: str) -> str:
        """Generate cache key for daily limit"""
        today = date.today().isoformat()
        return f"ratelimit:daily:{user_id}:{modality}:{today}"

    def _get_minute_key(self, user_id: str, modality: str) -> str:
        """Generate cache key for per-minute limit"""
        current_minute = datetime.utcnow().strftime("%Y%m%d%H%M")
        return f"ratelimit:minute:{user_id}:{modality}:{current_minute}"

    def get_limits(self, tier: str, modality: str) -> Dict[str, int]:
        """Get limits for a tier and modality"""
        tier_config = self.TIER_LIMITS.get(tier, self.TIER_LIMITS["free"])
        return tier_config.get(modality, {"daily": 0, "per_minute": 0})

    async def check_rate_limit(
        self,
        user_id: str,
        tier: str,
        modality: str
    ) -> RateLimitResult:
        """Check if user is within rate limits (doesn't increment)"""
        limits = self.get_limits(tier, modality)
        daily_limit = limits["daily"]
        minute_limit = limits["per_minute"]

        if daily_limit == 0:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                limit=0
            )

        # Check daily limit
        daily_key = self._get_daily_key(user_id, modality)
        daily_count = self.cache.get(daily_key) or 0

        if daily_count >= daily_limit:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                limit=daily_limit
            )

        # Check per-minute limit
        minute_key = self._get_minute_key(user_id, modality)
        minute_count = self.cache.get(minute_key) or 0

        if minute_count >= minute_limit:
            return RateLimitResult(
                allowed=False,
                remaining=daily_limit - daily_count,
                limit=minute_limit
            )

        return RateLimitResult(
            allowed=True,
            remaining=daily_limit - daily_count,
            limit=daily_limit
        )

    async def increment_usage(
        self,
        user_id: str,
        modality: str
    ) -> None:
        """Increment usage counters after successful request"""
        # Increment daily counter (TTL: 24 hours)
        daily_key = self._get_daily_key(user_id, modality)
        current_daily = self.cache.get(daily_key) or 0
        self.cache.set(daily_key, current_daily + 1, ttl=86400)

        # Increment minute counter (TTL: 60 seconds)
        minute_key = self._get_minute_key(user_id, modality)
        current_minute = self.cache.get(minute_key) or 0
        self.cache.set(minute_key, current_minute + 1, ttl=60)

    async def get_usage_stats(
        self,
        user_id: str,
        tier: str
    ) -> Dict[str, Dict[str, int]]:
        """Get current usage statistics for a user"""
        stats = {}

        for modality in ["llm", "image", "video"]:
            limits = self.get_limits(tier, modality)
            daily_key = self._get_daily_key(user_id, modality)
            daily_count = self.cache.get(daily_key) or 0

            stats[modality] = {
                "used": daily_count,
                "limit": limits["daily"],
                "remaining": max(0, limits["daily"] - daily_count)
            }

        return stats

    async def reset_user_limits(self, user_id: str) -> None:
        """Reset all limits for a user (admin function)"""
        for modality in ["llm", "image", "video"]:
            daily_key = self._get_daily_key(user_id, modality)
            minute_key = self._get_minute_key(user_id, modality)
            # Set to 0 instead of deleting to maintain cache entry
            self.cache.set(daily_key, 0, ttl=86400)
            self.cache.set(minute_key, 0, ttl=60)


# Singleton instance
_rate_limiter: Optional[TierRateLimiter] = None


def get_rate_limiter() -> TierRateLimiter:
    """Get the singleton rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = TierRateLimiter()
    return _rate_limiter
