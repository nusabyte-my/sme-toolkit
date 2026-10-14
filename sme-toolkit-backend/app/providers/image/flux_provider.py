"""FLUX.2 Image Generation Provider via Replicate"""

from typing import Optional
import base64
import logging
import httpx

from app.providers.base import ImageProvider, RateLimits

logger = logging.getLogger(__name__)

try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False
    logger.warning("Replicate package not installed. Run: pip install replicate")


class FluxProvider(ImageProvider):
    """
    FLUX.2 Image Generation Provider via Replicate

    Free tier available with Replicate
    High quality, open-source model
    """

    name = "flux"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        # FLUX.2 model on Replicate
        self.model_id = "black-forest-labs/flux-schnell"

        if REPLICATE_AVAILABLE and api_key:
            self.client = replicate.Client(api_token=api_key)
            self._is_configured = True
        else:
            self.client = None
            self._is_configured = False

    async def is_available(self) -> bool:
        """Check if FLUX is available"""
        return self._is_configured and self.client is not None

    def get_rate_limits(self) -> RateLimits:
        """FLUX via Replicate rate limits"""
        return RateLimits(
            requests_per_minute=10,
            requests_per_day=100,  # Free tier
            tokens_per_minute=0,
            tokens_per_day=0
        )

    def _parse_aspect_ratio(self, aspect_ratio: str) -> tuple:
        """Convert aspect ratio string to width/height"""
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
        """Generate an image using FLUX.2"""
        if not await self.is_available():
            raise RuntimeError("FLUX provider is not available")

        try:
            # Build enhanced prompt
            full_prompt = prompt
            if style:
                full_prompt = f"{prompt}, {style} style"

            width, height = self._parse_aspect_ratio(aspect_ratio)

            # Run prediction
            output = await self._run_prediction(
                prompt=full_prompt,
                width=width,
                height=height,
                num_outputs=1,
                num_inference_steps=4  # FLUX schnell uses fewer steps
            )

            if output and len(output) > 0:
                image_url = output[0]
                # Download and encode as base64
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url, timeout=60.0)
                    response.raise_for_status()
                    return base64.b64encode(response.content).decode('utf-8')

            raise RuntimeError("No image generated")
        except Exception as e:
            logger.error(f"FLUX generation error: {e}")
            raise

    async def _run_prediction(self, **kwargs) -> list:
        """Run prediction on Replicate (sync wrapper for async context)"""
        import asyncio

        def sync_run():
            return self.client.run(
                self.model_id,
                input=kwargs
            )

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sync_run)
