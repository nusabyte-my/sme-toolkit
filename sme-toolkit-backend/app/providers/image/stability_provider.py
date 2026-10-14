"""Stability AI Image Generation Provider"""

from typing import Optional
import base64
import logging
import httpx

from app.providers.base import ImageProvider, RateLimits

logger = logging.getLogger(__name__)


class StabilityProvider(ImageProvider):
    """
    Stability AI Image Generation Provider

    Uses Stable Diffusion models via Stability AI API
    """

    name = "stability"
    BASE_URL = "https://api.stability.ai/v2beta"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.engine = "stable-diffusion-xl-1024-v1-0"
        self._is_configured = bool(api_key)

    async def is_available(self) -> bool:
        """Check if Stability AI is available"""
        return self._is_configured

    def get_rate_limits(self) -> RateLimits:
        """Stability AI rate limits"""
        return RateLimits(
            requests_per_minute=10,
            requests_per_day=500,
            tokens_per_minute=0,
            tokens_per_day=0
        )

    def _parse_resolution(self, resolution: str, aspect_ratio: str) -> tuple:
        """Get width/height from resolution or aspect ratio"""
        if "x" in resolution:
            parts = resolution.lower().split("x")
            return int(parts[0]), int(parts[1])

        ratios = {
            "1:1": (1024, 1024),
            "16:9": (1344, 768),
            "9:16": (768, 1344),
            "4:3": (1152, 896),
            "3:4": (896, 1152),
            "3:2": (1216, 832),
            "2:3": (832, 1216)
        }
        return ratios.get(aspect_ratio, (1024, 1024))

    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
        resolution: str = "1024x1024",
        **kwargs
    ) -> str:
        """Generate an image using Stability AI"""
        if not await self.is_available():
            raise RuntimeError("Stability AI provider is not available")

        try:
            # Build prompt with style
            full_prompt = prompt
            if style:
                full_prompt = f"{prompt}, {style} style, high quality, detailed"

            width, height = self._parse_resolution(resolution, aspect_ratio)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/stable-image/generate/core",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Accept": "application/json"
                    },
                    files={
                        "none": ""
                    },
                    data={
                        "prompt": full_prompt,
                        "output_format": "png",
                        "aspect_ratio": aspect_ratio.replace(":", "-")
                    },
                    timeout=120.0
                )

                if response.status_code == 200:
                    data = response.json()
                    if "image" in data:
                        return data["image"]
                    elif "artifacts" in data and len(data["artifacts"]) > 0:
                        return data["artifacts"][0]["base64"]

                # Try alternative endpoint
                response = await client.post(
                    f"{self.BASE_URL}/generation/{self.engine}/text-to-image",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json={
                        "text_prompts": [{"text": full_prompt, "weight": 1}],
                        "cfg_scale": 7,
                        "height": height,
                        "width": width,
                        "samples": 1,
                        "steps": 30
                    },
                    timeout=120.0
                )

                response.raise_for_status()
                data = response.json()

                if "artifacts" in data and len(data["artifacts"]) > 0:
                    return data["artifacts"][0]["base64"]

                raise RuntimeError("No image in response")
        except httpx.HTTPStatusError as e:
            logger.error(f"Stability AI API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Stability AI generation error: {e}")
            raise
