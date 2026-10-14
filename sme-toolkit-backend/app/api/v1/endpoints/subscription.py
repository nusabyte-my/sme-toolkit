"""Subscription API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.services.tier_service import TierService
from app.providers.rate_limiter import get_rate_limiter

router = APIRouter()


class TierResponse(BaseModel):
    tier: str
    name: str
    features: Dict[str, Any]
    limits: Dict[str, int]
    providers: Dict[str, List[str]]


class UsageResponse(BaseModel):
    tier: str
    usage: Dict[str, Dict[str, int]]
    reset_time: str


class UpgradeRequest(BaseModel):
    tier: str
    stripe_token: Optional[str] = None


class AllTiersResponse(BaseModel):
    tiers: List[Dict[str, Any]]


@router.get("/tier", response_model=TierResponse)
async def get_current_tier(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get user's current subscription tier and features"""
    tier_service = TierService(db)
    tier = await tier_service.get_user_tier(current_user)
    features = await tier_service.get_user_features(current_user)

    return TierResponse(
        tier=tier,
        name=features.get("name", "Free"),
        features=features.get("features", {}),
        limits={
            "daily_llm_requests": features.get("daily_llm_requests", 50),
            "daily_image_requests": features.get("daily_image_requests", 10),
            "daily_video_requests": features.get("daily_video_requests", 0)
        },
        providers={
            "llm": features.get("llm_providers", []),
            "image": features.get("image_providers", []),
            "video": features.get("video_providers", [])
        }
    )


@router.get("/usage", response_model=UsageResponse)
async def get_usage_stats(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get current usage statistics against limits"""
    tier_service = TierService(db)
    rate_limiter = get_rate_limiter()

    tier = await tier_service.get_user_tier(current_user)
    usage = await rate_limiter.get_usage_stats(current_user, tier)

    # Calculate reset time (midnight UTC)
    now = datetime.utcnow()
    reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    reset_time = reset_time.replace(day=now.day + 1)

    return UsageResponse(
        tier=tier,
        usage=usage,
        reset_time=reset_time.isoformat()
    )


@router.get("/tiers", response_model=AllTiersResponse)
async def get_all_tiers():
    """Get information about all available tiers"""
    return AllTiersResponse(tiers=TierService.get_all_tiers())


class PackageInfo(BaseModel):
    id: str
    name: str
    description: str
    price: int
    tokenAmount: int
    tier: str
    bonusTokens: int
    features: Any
    isActive: bool


class PackagesResponse(BaseModel):
    packages: List[PackageInfo]


@router.get("/packages", response_model=PackagesResponse)
async def get_subscription_packages():
    """Get all available subscription packages with pricing and tokens"""
    tiers = TierService.get_all_tiers()
    packages = []
    for tier in tiers:
        tier_id = tier.get("id", "free")
        tier_name = tier.get("name", "Free")
        tier_price = tier.get("price", 0)
        tier_features = tier.get("features", {})
        token_map = {"free": 1000, "sme": 10000, "business": 40000, "enterprise": 100000}
        bonus_map = {"free": 0, "sme": 1000, "business": 5000, "enterprise": 20000}
        desc_map = {
            "free": "Get started with basic features",
            "sme": "Perfect for growing businesses",
            "business": "For professional teams",
            "enterprise": "Custom solutions for large organizations",
        }

        packages.append(PackageInfo(
            id=f"{tier_id}-monthly",
            name=f"{tier_name} Monthly" if tier_id != "enterprise" else "Enterprise",
            description=desc_map.get(tier_id, "Subscription package"),
            price=tier_price,
            tokenAmount=token_map.get(tier_id, 1000),
            tier=tier_id,
            bonusTokens=bonus_map.get(tier_id, 0),
            features=tier_features,
            isActive=True,
        ))

    return PackagesResponse(packages=packages)


@router.post("/upgrade")
async def upgrade_tier(
    request: UpgradeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Initiate tier upgrade"""
    tier_service = TierService(db)

    # Validate tier
    valid_tiers = ["free", "sme", "business", "enterprise"]
    if request.tier not in valid_tiers:
        raise HTTPException(status_code=400, detail="Invalid tier")

    # For now, directly upgrade (Stripe integration would go here)
    # In production, this would:
    # 1. Create Stripe checkout session
    # 2. Handle payment via webhook
    # 3. Then upgrade the tier

    if request.tier == "enterprise":
        return {
            "success": False,
            "message": "Enterprise tier requires contacting sales",
            "contact": "enterprise@sme-toolkit.com"
        }

    if request.tier != "free" and not request.stripe_token:
        return {
            "success": False,
            "message": "Payment required for paid tiers",
            "requires_payment": True,
            "tier": request.tier,
            "price": TierService.TIER_FEATURES[request.tier]["price"]
        }

    # Upgrade tier (demo mode - no payment)
    subscription = await tier_service.upgrade_tier(
        user_id=current_user,
        new_tier=request.tier
    )

    return {
        "success": True,
        "tier": subscription.tier.value,
        "message": f"Successfully upgraded to {request.tier} tier"
    }


@router.post("/cancel")
async def cancel_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Cancel subscription and revert to free tier"""
    tier_service = TierService(db)
    success = await tier_service.cancel_subscription(current_user)

    if success:
        return {"success": True, "message": "Subscription cancelled. Reverted to free tier."}

    return {"success": False, "message": "No active subscription found"}


@router.get("/features/{feature}")
async def check_feature_access(
    feature: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Check if user has access to a specific feature"""
    tier_service = TierService(db)
    has_access = await tier_service.check_feature_access(current_user, feature)

    if has_access:
        return {"feature": feature, "access": True}

    # Get upgrade info
    current_tier = await tier_service.get_user_tier(current_user)
    upgrade_tier = None

    # Find lowest tier with this feature
    for tier_id in ["sme", "business", "enterprise"]:
        if tier_id == current_tier:
            continue
        tier_features = TierService.TIER_FEATURES[tier_id]
        if tier_features["features"].get(feature, False):
            upgrade_tier = tier_id
            break

    return {
        "feature": feature,
        "access": False,
        "current_tier": current_tier,
        "upgrade_to": upgrade_tier,
        "upgrade_price": TierService.TIER_FEATURES.get(upgrade_tier, {}).get("price") if upgrade_tier else None
    }
