"""
Video generation tools using the multi-provider system.

This module provides video generation capabilities that automatically
route through the best available provider based on user tier.
"""

import asyncio
import uuid
from typing import Optional, Literal, Dict, Any
from datetime import datetime
import logging

from app.config import settings
from app.tools.ai_client import AIClient, get_ai_client
from app.prompts.video_prompts import STYLE_FILTERS

logger = logging.getLogger(__name__)


class VideoTools:
    """
    Tools for video generation using the multi-provider system.

    Automatically routes requests to the best available video provider
    based on user tier:
    - Free: Video not available
    - SME: Veo Fast (720p, 10-sec max)
    - Business: Veo 3 + Kling AI fallback
    - Enterprise: All providers
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        user_id: str = "default",
        tier: str = "free"
    ):
        """
        Initialize VideoTools.

        Args:
            api_key: Ignored - provider system manages API keys
            user_id: User ID for rate limiting and tier resolution
            tier: Subscription tier (free, sme, business, enterprise)
        """
        self._client = AIClient(user_id=user_id, tier=tier)
        self.user_id = user_id
        self.tier = tier

    def with_user(self, user_id: str, tier: str = "free") -> "VideoTools":
        """Return a new instance with different user context"""
        return VideoTools(user_id=user_id, tier=tier)

    def _apply_style_filter(self, prompt: str, style_filter: Optional[str]) -> str:
        """Apply style filter to video prompt"""
        if not style_filter or style_filter not in STYLE_FILTERS:
            return prompt
        return f"{STYLE_FILTERS[style_filter]}: {prompt}"

    async def generate_video(
        self,
        prompt: str,
        resolution: Literal["720p", "1080p"] = "720p",
        aspect_ratio: Literal["16:9", "9:16"] = "16:9",
        style_filter: Optional[str] = None,
        duration: int = 5,
        audio: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a video from text prompt.

        Automatically routes to the best available provider based on tier:
        - Free: Video not available
        - SME: Veo Fast (720p, 10-sec max)
        - Business/Enterprise: Veo 3 + Kling AI fallback

        Args:
            prompt: Visual description for the video
            resolution: Video resolution (720p or 1080p)
            aspect_ratio: Video aspect ratio
            style_filter: Optional style filter
            duration: Target duration in seconds
            audio: Whether to generate audio (if supported)

        Returns:
            Dict with video_url, status, and provider info
        """
        # Apply style filter
        styled_prompt = self._apply_style_filter(prompt, style_filter)

        try:
            result = await self._client.generate_video(
                prompt=styled_prompt,
                duration=duration,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                style=style_filter,
                audio=audio
            )

            return result
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "error"
            }

    async def generate_video_async(
        self,
        prompt: str,
        resolution: Literal["720p", "1080p"] = "720p",
        aspect_ratio: Literal["16:9", "9:16"] = "16:9",
        style_filter: Optional[str] = None,
        duration: int = 5
    ) -> Dict[str, Any]:
        """
        Start async video generation and return job ID.

        This is for use with the job queue - starts generation
        without waiting for completion.

        Args:
            prompt: Visual description for the video
            resolution: Video resolution
            aspect_ratio: Video aspect ratio
            style_filter: Optional style filter
            duration: Target duration in seconds

        Returns:
            Dict with job_id for tracking
        """
        job_id = str(uuid.uuid4())

        # Apply style filter
        styled_prompt = self._apply_style_filter(prompt, style_filter)

        # Start the video generation in background
        result = await self._client.generate_video(
            prompt=styled_prompt,
            duration=duration,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            style=style_filter
        )

        if result.get("job_id"):
            return {
                "job_id": result["job_id"],
                "status": result.get("status", "queued"),
                "prompt": styled_prompt,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio
            }

        # If provider returned immediately (no async support)
        return {
            "job_id": job_id,
            "status": result.get("status", "completed"),
            "video_url": result.get("video_url"),
            "prompt": styled_prompt,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio
        }

    def is_available_for_tier(self) -> bool:
        """Check if video generation is available for the current tier"""
        return self.tier in ["sme", "business", "enterprise"]

    def get_tier_limits(self) -> Dict[str, Any]:
        """Get video generation limits for the current tier"""
        limits = {
            "free": {
                "available": False,
                "daily_limit": 0,
                "max_duration": 0,
                "max_resolution": None
            },
            "sme": {
                "available": True,
                "daily_limit": 5,
                "max_duration": 10,
                "max_resolution": "720p"
            },
            "business": {
                "available": True,
                "daily_limit": 20,
                "max_duration": 30,
                "max_resolution": "1080p"
            },
            "enterprise": {
                "available": True,
                "daily_limit": 100,
                "max_duration": 60,
                "max_resolution": "1080p"
            }
        }
        return limits.get(self.tier, limits["free"])


def get_video_tools(user_id: str = "default", tier: str = "free") -> VideoTools:
    """Get VideoTools instance for a specific user/tier"""
    return VideoTools(user_id=user_id, tier=tier)
