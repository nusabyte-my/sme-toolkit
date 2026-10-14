"""Provider Status API endpoints"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.services.tier_service import TierService
from app.providers.router import get_provider_router

router = APIRouter()


class ProviderStatus(BaseModel):
    name: str
    modality: str
    configured: bool
    available_for_tier: bool


class AllProvidersResponse(BaseModel):
    llm: Dict[str, bool]
    image: Dict[str, bool]
    video: Dict[str, bool]


class AvailableProvidersResponse(BaseModel):
    tier: str
    llm: List[str]
    image: List[str]
    video: List[str]


@router.get("/status", response_model=AllProvidersResponse)
async def get_provider_status():
    """Get status of all AI providers"""
    router_instance = get_provider_router()
    status = router_instance.get_provider_status()

    return AllProvidersResponse(
        llm=status.get("llm", {}),
        image=status.get("image", {}),
        video=status.get("video", {})
    )


@router.get("/available", response_model=AvailableProvidersResponse)
async def get_available_providers(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get providers available for user's tier"""
    tier_service = TierService(db)
    router_instance = get_provider_router()

    tier = await tier_service.get_user_tier(current_user)
    available = router_instance.get_available_providers(tier)

    return AvailableProvidersResponse(
        tier=tier,
        llm=available.get("llm", []),
        image=available.get("image", []),
        video=available.get("video", [])
    )


@router.get("/info/{provider_name}")
async def get_provider_info(
    provider_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get detailed information about a specific provider"""
    router_instance = get_provider_router()
    tier_service = TierService(db)

    # Find provider
    provider = None
    modality = None

    if provider_name in router_instance.llm_providers:
        provider = router_instance.llm_providers[provider_name]
        modality = "llm"
    elif provider_name in router_instance.image_providers:
        provider = router_instance.image_providers[provider_name]
        modality = "image"
    elif provider_name in router_instance.video_providers:
        provider = router_instance.video_providers[provider_name]
        modality = "video"

    if not provider:
        return {"error": "Provider not found", "provider": provider_name}

    # Check if available for user's tier
    user_tier = await tier_service.get_user_tier(current_user)
    available_providers = router_instance.get_available_providers(user_tier)
    is_available = provider_name in available_providers.get(modality, [])

    # Get rate limits
    rate_limits = provider.get_rate_limits()

    return {
        "name": provider_name,
        "modality": modality,
        "configured": provider.is_configured,
        "available_for_tier": is_available,
        "user_tier": user_tier,
        "rate_limits": {
            "requests_per_minute": rate_limits.requests_per_minute,
            "requests_per_day": rate_limits.requests_per_day,
            "tokens_per_minute": rate_limits.tokens_per_minute,
            "tokens_per_day": rate_limits.tokens_per_day
        }
    }


@router.get("/recommendations")
async def get_provider_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get recommended providers based on user's tier and usage"""
    tier_service = TierService(db)
    router_instance = get_provider_router()

    user_tier = await tier_service.get_user_tier(current_user)
    available = router_instance.get_available_providers(user_tier)

    recommendations = {
        "llm": {
            "primary": available.get("llm", ["mock"])[0] if available.get("llm") else "mock",
            "alternatives": available.get("llm", [])[1:] if len(available.get("llm", [])) > 1 else [],
            "recommendation": "Use primary for best quality, alternatives for fallback"
        },
        "image": {
            "primary": available.get("image", ["mock"])[0] if available.get("image") else "mock",
            "alternatives": available.get("image", [])[1:] if len(available.get("image", [])) > 1 else [],
            "recommendation": "Primary provider offers best quality for your tier"
        },
        "video": {
            "primary": available.get("video", [])[0] if available.get("video") else None,
            "alternatives": available.get("video", [])[1:] if len(available.get("video", [])) > 1 else [],
            "recommendation": "Video generation requires SME tier or higher" if not available.get("video") else "Use primary for best results"
        }
    }

    return {
        "tier": user_tier,
        "recommendations": recommendations
    }
