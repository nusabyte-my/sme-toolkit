"""Unified AI Client that routes through the multi-provider system"""

import json
import asyncio
from typing import Optional, Dict, Any
from functools import lru_cache
import logging

from app.config import settings
from app.providers.router import get_provider_router
from app.providers.base import LLMRequest, ImageRequest, VideoRequest

logger = logging.getLogger(__name__)


class AIClient:
    """
    Unified AI Client that routes requests through the multi-provider system.

    This client automatically:
    - Routes to the best available provider based on user tier
    - Falls back to alternative providers if primary fails
    - Enforces rate limits
    - Tracks usage
    """

    def __init__(self, user_id: str = "default", tier: str = "free"):
        self.user_id = user_id
        self.tier = tier
        self.router = get_provider_router()

    def with_user(self, user_id: str, tier: str = "free") -> "AIClient":
        """Return a new client instance with different user context"""
        return AIClient(user_id=user_id, tier=tier)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        use_pro: bool = False
    ) -> str:
        """
        Generate text using the best available LLM provider.

        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt for context
            temperature: Creativity control (0-1)
            max_tokens: Maximum tokens to generate
            use_pro: If True, prefer pro-level models (affects provider selection)

        Returns:
            Generated text content
        """
        # If use_pro is requested, temporarily upgrade tier for this request
        effective_tier = "business" if use_pro and self.tier in ["free", "sme"] else self.tier

        request = LLMRequest(
            prompt=prompt,
            user_id=self.user_id,
            tier=effective_tier,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format="text"
        )

        response = await self.router.route_llm_request(request, self.user_id, effective_tier)

        if response.success:
            logger.debug(f"Text generated via {response.provider_name}")
            return response.content
        else:
            logger.error(f"Text generation failed: {response.error}")
            return f"[ERROR] {response.error}"

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        use_pro: bool = False
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output using the best available LLM provider.

        Args:
            prompt: The input prompt requesting JSON output
            system_prompt: Optional system prompt for context
            schema: Optional JSON schema for structured output
            use_pro: If True, prefer pro-level models

        Returns:
            Parsed JSON dictionary
        """
        effective_tier = "business" if use_pro and self.tier in ["free", "sme"] else self.tier

        # Append JSON instruction to prompt
        full_prompt = f"{prompt}\n\nRespond with valid JSON only, no markdown formatting."

        request = LLMRequest(
            prompt=full_prompt,
            user_id=self.user_id,
            tier=effective_tier,
            system_prompt=system_prompt,
            temperature=0.5,  # Lower temperature for structured output
            max_tokens=4096,
            response_format="json",
            json_schema=schema
        )

        response = await self.router.route_llm_request(request, self.user_id, effective_tier)

        if response.success:
            # Try to parse JSON from content
            try:
                if response.metadata and "json_response" in response.metadata:
                    return response.metadata["json_response"]

                # Clean up and parse
                text = response.content.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

                return json.loads(text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                return {"error": str(e), "raw_content": response.content}
        else:
            logger.error(f"JSON generation failed: {response.error}")
            return {"error": response.error}

    async def enhance_prompt(self, original: str) -> str:
        """Enhance a user prompt to be more descriptive"""
        prompt = f"""Improve this prompt to be more detailed and effective while keeping the core intent:

Original: {original}

Provide an enhanced version in 1-2 sentences. Return only the enhanced text, no explanations."""

        return await self.generate_text(prompt, temperature=0.7)

    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
        resolution: str = "1024x1024",
        reference_image: Optional[str] = None
    ) -> str:
        """
        Generate an image using the best available image provider.

        Args:
            prompt: Text description of the image
            style: Visual style (Photorealistic, Minimalist Vector, etc.)
            aspect_ratio: Image aspect ratio
            resolution: Target resolution
            reference_image: Optional base64 reference image

        Returns:
            Base64 encoded image data (with data URI prefix)
        """
        request = ImageRequest(
            prompt=prompt,
            user_id=self.user_id,
            tier=self.tier,
            style=style,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            reference_image=reference_image
        )

        response = await self.router.route_image_request(request, self.user_id, self.tier)

        if response.success:
            logger.debug(f"Image generated via {response.provider_name}")
            image_data = response.image_data or response.image_url
            if image_data and not image_data.startswith("data:"):
                image_data = f"data:image/png;base64,{image_data}"
            return image_data
        else:
            logger.error(f"Image generation failed: {response.error}")
            raise ValueError(f"Image generation failed: {response.error}")

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
        # Use image generation with reference
        return await self.generate_image(
            prompt=f"Edit this image: {instruction}",
            reference_image=source_image
        )

    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        style: Optional[str] = None,
        audio: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a video using the best available video provider.

        Args:
            prompt: Visual description for the video
            duration: Target duration in seconds
            resolution: Video resolution (720p, 1080p)
            aspect_ratio: Video aspect ratio
            style: Optional style filter
            audio: Whether to generate audio

        Returns:
            Dict with video_url or video_data
        """
        request = VideoRequest(
            prompt=prompt,
            user_id=self.user_id,
            tier=self.tier,
            duration=duration,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            style=style,
            audio=audio
        )

        response = await self.router.route_video_request(request, self.user_id, self.tier)

        if response.success:
            logger.debug(f"Video generated via {response.provider_name}")
            return {
                "success": True,
                "video_url": response.video_url,
                "video_data": response.video_data,
                "job_id": response.job_id,
                "status": response.status,
                "provider": response.provider_name
            }
        else:
            logger.error(f"Video generation failed: {response.error}")
            return {
                "success": False,
                "error": response.error,
                "status": "failed"
            }


# Singleton with default user
_default_client: Optional[AIClient] = None


def get_ai_client(user_id: str = "default", tier: str = "free") -> AIClient:
    """
    Get an AI client instance.

    For the default user, returns a cached singleton.
    For specific users, returns a new instance.
    """
    global _default_client

    if user_id == "default" and tier == "free":
        if _default_client is None:
            _default_client = AIClient()
        return _default_client

    return AIClient(user_id=user_id, tier=tier)


# Backwards compatibility - GeminiClient wrapper
class GeminiClient:
    """
    Backwards-compatible wrapper that uses the new AIClient.

    Deprecated: Use AIClient directly for new code.
    """

    def __init__(self, api_key: Optional[str] = None, user_id: str = "default", tier: str = "free"):
        self._client = AIClient(user_id=user_id, tier=tier)
        self.is_mock = False  # Provider system handles mocking

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_pro: bool = False,
        temperature: float = 0.7
    ) -> str:
        return await self._client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            use_pro=use_pro,
            temperature=temperature
        )

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_pro: bool = False
    ) -> Dict[str, Any]:
        return await self._client.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            use_pro=use_pro
        )

    async def enhance_prompt(self, original: str) -> str:
        return await self._client.enhance_prompt(original)


@lru_cache()
def get_gemini_client() -> GeminiClient:
    """Get singleton Gemini client (backwards compatible)"""
    return GeminiClient()
