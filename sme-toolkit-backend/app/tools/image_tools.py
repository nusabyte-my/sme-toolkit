"""
Image generation tools using the multi-provider system.

This module provides image generation and editing capabilities
that automatically route through the best available provider
based on user tier.
"""

import base64
from typing import Optional
import logging

from app.config import settings
from app.tools.ai_client import AIClient, get_ai_client
from app.prompts.visual_prompts import STYLE_GUIDES

logger = logging.getLogger(__name__)


class ImageTools:
    """
    Tools for image generation and editing using the multi-provider system.

    Automatically routes requests to the best available image provider
    based on user tier (FLUX for free tier, Gemini/Imagen for paid tiers).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        user_id: str = "default",
        tier: str = "free"
    ):
        """
        Initialize ImageTools.

        Args:
            api_key: Ignored - provider system manages API keys
            user_id: User ID for rate limiting and tier resolution
            tier: Subscription tier (free, sme, business, enterprise)
        """
        self._client = AIClient(user_id=user_id, tier=tier)
        self.user_id = user_id
        self.tier = tier

    def with_user(self, user_id: str, tier: str = "free") -> "ImageTools":
        """Return a new instance with different user context"""
        return ImageTools(user_id=user_id, tier=tier)

    def _apply_style(self, prompt: str, style: Optional[str]) -> str:
        """Apply style modifiers to prompt"""
        if not style or style not in STYLE_GUIDES:
            return prompt
        return f"{prompt}, {STYLE_GUIDES[style].get('characteristics', '')}"

    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
        reference_image: Optional[str] = None
    ) -> str:
        """
        Generate an image from text prompt.

        Automatically routes to the best available provider based on tier:
        - Free: FLUX.2 via Replicate
        - SME: Gemini Image
        - Business/Enterprise: Imagen 4 or Nano Banana

        Args:
            prompt: Text description of the image
            style: Visual style (Photorealistic, Minimalist Vector, etc.)
            aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, etc.)
            reference_image: Optional base64 reference image

        Returns:
            Base64 encoded image data with data URI prefix
        """
        # Apply style to prompt
        styled_prompt = self._apply_style(prompt, style)

        # If reference image provided, add context
        if reference_image:
            styled_prompt = f"Using this reference image as inspiration, generate: {styled_prompt}"

        try:
            return await self._client.generate_image(
                prompt=styled_prompt,
                style=style,
                aspect_ratio=aspect_ratio,
                reference_image=reference_image
            )
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise ValueError(f"Image generation failed: {str(e)}")

    async def edit_image(
        self,
        source_image: str,
        instruction: str
    ) -> str:
        """
        Edit an existing image based on instruction.

        Args:
            source_image: Base64 encoded source image
            instruction: Edit instruction

        Returns:
            Base64 encoded edited image
        """
        try:
            return await self._client.edit_image(
                source_image=source_image,
                instruction=instruction
            )
        except Exception as e:
            logger.error(f"Image editing failed: {e}")
            raise ValueError(f"Image editing failed: {str(e)}")


def get_image_tools(user_id: str = "default", tier: str = "free") -> ImageTools:
    """Get ImageTools instance for a specific user/tier"""
    return ImageTools(user_id=user_id, tier=tier)
