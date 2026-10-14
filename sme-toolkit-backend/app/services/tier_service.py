"""Tier Service - User subscription and feature management"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import UserSubscription

logger = logging.getLogger(__name__)


class TierService:
    """Service for managing user tiers and features"""

    # Tier feature configuration
    TIER_FEATURES = {
        "free": {
            "name": "Free",
            "price": 0,
            "llm_providers": ["fiqstr-v2", "groq", "mistral", "deepseek"],
            "image_providers": ["flux"],
            "video_providers": [],
            "daily_llm_requests": 50,
            "daily_image_requests": 10,
            "daily_video_requests": 0,
            "features": {
                "bmc_basic": True,
                "bmc_analysis": False,
                "lead_scoring": True,
                "copywriting": True,
                "strategy_advisor": False,
                "growth_score": False,
                "visual_studio": True,
                "video_studio": False,
                "analytics": False,
                "api_access": False
            }
        },
        "sme": {
            "name": "SME",
            "price": 19,
            "llm_providers": ["fiqstr-v2", "gemini", "groq", "mistral"],
            "image_providers": ["gemini", "flux"],
            "video_providers": ["veo_fast"],
            "daily_llm_requests": 500,
            "daily_image_requests": 50,
            "daily_video_requests": 5,
            "max_video_duration": 10,
            "features": {
                "bmc_basic": True,
                "bmc_analysis": True,
                "lead_scoring": True,
                "copywriting": True,
                "strategy_advisor": True,
                "growth_score": True,
                "visual_studio": True,
                "video_studio": True,
                "analytics": True,
                "api_access": False
            }
        },
        "business": {
            "name": "Business",
            "price": 49,
            "llm_providers": ["fiqstr-v2", "gemini_pro", "gemini", "groq"],
            "image_providers": ["imagen4", "nanobanana", "flux"],
            "video_providers": ["veo3", "kling", "nanobanana"],
            "daily_llm_requests": 2000,
            "daily_image_requests": 200,
            "daily_video_requests": 20,
            "max_video_duration": 30,
            "features": {
                "bmc_basic": True,
                "bmc_analysis": True,
                "lead_scoring": True,
                "copywriting": True,
                "strategy_advisor": True,
                "growth_score": True,
                "visual_studio": True,
                "video_studio": True,
                "analytics": True,
                "api_access": True,
                "priority_processing": True,
                "advanced_analytics": True
            }
        },
        "enterprise": {
            "name": "Enterprise",
            "price": -1,  # Custom pricing
            "llm_providers": ["fiqstr-v2", "gemini_pro", "gemini", "groq", "mistral", "deepseek"],
            "image_providers": ["imagen4", "nanobanana", "flux", "stability"],
            "video_providers": ["veo3", "kling", "nanobanana"],
            "daily_llm_requests": 10000,
            "daily_image_requests": 1000,
            "daily_video_requests": 100,
            "max_video_duration": 60,
            "features": {
                "bmc_basic": True,
                "bmc_analysis": True,
                "lead_scoring": True,
                "copywriting": True,
                "strategy_advisor": True,
                "growth_score": True,
                "visual_studio": True,
                "video_studio": True,
                "analytics": True,
                "api_access": True,
                "priority_processing": True,
                "advanced_analytics": True,
                "white_label": True,
                "sso": True,
                "custom_integrations": True,
                "dedicated_support": True
            }
        }
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """Get user's subscription record"""
        result = await self.db.execute(
            select(UserSubscription).where(UserSubscription.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_tier(self, user_id: str) -> str:
        """Get user's current tier"""
        subscription = await self.get_user_subscription(user_id)
        if subscription:
            # Check if subscription has expired
            if subscription.expires_at and subscription.expires_at < datetime.utcnow():
                return "free"
            return subscription.tier
        return "free"

    async def get_tier_features(self, tier: str) -> Dict[str, Any]:
        """Get features for a tier"""
        return self.TIER_FEATURES.get(tier, self.TIER_FEATURES["free"])

    async def get_user_features(self, user_id: str) -> Dict[str, Any]:
        """Get features for a user based on their tier"""
        tier = await self.get_user_tier(user_id)
        features = self.TIER_FEATURES.get(tier, self.TIER_FEATURES["free"]).copy()

        # Check for custom feature overrides
        subscription = await self.get_user_subscription(user_id)
        if subscription and subscription.features:
            # Merge custom features
            if "features" in features:
                features["features"].update(subscription.features)

        return features

    async def check_feature_access(self, user_id: str, feature: str) -> bool:
        """Check if user has access to a specific feature"""
        user_features = await self.get_user_features(user_id)
        return user_features.get("features", {}).get(feature, False)

    async def get_available_providers(self, user_id: str, modality: str) -> List[str]:
        """Get available providers for a user based on tier"""
        user_features = await self.get_user_features(user_id)
        key = f"{modality}_providers"
        return user_features.get(key, [])

    async def create_subscription(
        self,
        user_id: str,
        tier: str = "free",
        stripe_customer_id: Optional[str] = None,
        stripe_subscription_id: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> UserSubscription:
        """Create or update user subscription"""
        subscription = await self.get_user_subscription(user_id)

        if subscription:
            # Update existing
            subscription.tier = tier
            subscription.stripe_customer_id = stripe_customer_id
            subscription.stripe_subscription_id = stripe_subscription_id
            subscription.expires_at = expires_at
            subscription.updated_at = datetime.utcnow()
        else:
            # Create new
            subscription = UserSubscription(
                user_id=user_id,
                tier=tier,
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=stripe_subscription_id,
                expires_at=expires_at
            )
            self.db.add(subscription)

        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def upgrade_tier(
        self,
        user_id: str,
        new_tier: str,
        stripe_subscription_id: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> UserSubscription:
        """Upgrade user to a new tier"""
        return await self.create_subscription(
            user_id=user_id,
            tier=new_tier,
            stripe_subscription_id=stripe_subscription_id,
            expires_at=expires_at
        )

    async def cancel_subscription(self, user_id: str) -> bool:
        """Cancel subscription and revert to free tier"""
        subscription = await self.get_user_subscription(user_id)
        if subscription:
            subscription.tier = SubscriptionTier.FREE
            subscription.stripe_subscription_id = None
            subscription.expires_at = datetime.utcnow()
            subscription.updated_at = datetime.utcnow()
            await self.db.commit()
            return True
        return False

    @staticmethod
    def get_all_tiers() -> List[Dict[str, Any]]:
        """Get information about all tiers"""
        tiers = []
        for tier_id, config in TierService.TIER_FEATURES.items():
            tiers.append({
                "id": tier_id,
                "name": config["name"],
                "price": config["price"],
                "daily_llm_requests": config["daily_llm_requests"],
                "daily_image_requests": config["daily_image_requests"],
                "daily_video_requests": config["daily_video_requests"],
                "features": list(k for k, v in config["features"].items() if v)
            })
        return tiers
