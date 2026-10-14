"""Gemini/Imagen Image Generation Provider"""

from typing import Optional
import base64
import logging

from app.providers.base import ImageProvider, RateLimits

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("Google GenerativeAI package not installed")


class GeminiImageProvider(ImageProvider):
    """
    Gemini Image Generation Provider

    Uses Gemini 2.0 Flash for image generation
    """

    name = "gemini"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.model_name = "gemini-2.0-flash-exp"
        self.model = None

        if GENAI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self._is_configured = True
        else:
            self._is_configured = False

    async def is_available(self) -> bool:
        """Check if provider is available"""
        return self._is_configured and self.model is not None

    def get_rate_limits(self) -> RateLimits:
        """Gemini image generation limits"""
        return RateLimits(
            requests_per_minute=10,
            requests_per_day=100,
            tokens_per_minute=0,
            tokens_per_day=0
        )

    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
        resolution: str = "1024x1024",
        **kwargs
    ) -> str:
        """Generate an image and return base64 encoded data"""
        if not await self.is_available():
            raise RuntimeError("Gemini image provider is not available")

        try:
            # Build enhanced prompt with style
            full_prompt = f"Generate an image: {prompt}"
            if style:
                full_prompt = f"{full_prompt}. Style: {style}"
            full_prompt += f". Aspect ratio: {aspect_ratio}"

            # Configure for image generation
            generation_config = genai.GenerationConfig(
                response_mime_type="image/png"
            )

            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )

            # Extract image data
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        return base64.b64encode(part.inline_data.data).decode('utf-8')

            raise RuntimeError("No image generated in response")
        except Exception as e:
            logger.error(f"Gemini image generation error: {e}")
            raise


class Imagen4Provider(ImageProvider):
    """
    Imagen 4 Provider - Google's latest image model

    Higher quality images for business tier
    """

    name = "imagen4"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.model_name = "imagen-4.0-generate-preview"
        self.model = None

        if GENAI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            try:
                self.model = genai.GenerativeModel(self.model_name)
                self._is_configured = True
            except Exception as e:
                logger.warning(f"Imagen 4 not available: {e}")
                self._is_configured = False
        else:
            self._is_configured = False

    async def is_available(self) -> bool:
        """Check if provider is available"""
        return self._is_configured and self.model is not None

    def get_rate_limits(self) -> RateLimits:
        """Imagen 4 rate limits"""
        return RateLimits(
            requests_per_minute=5,
            requests_per_day=50,
            tokens_per_minute=0,
            tokens_per_day=0
        )

    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
        resolution: str = "1024x1024",
        **kwargs
    ) -> str:
        """Generate high-quality image using Imagen 4"""
        if not await self.is_available():
            raise RuntimeError("Imagen 4 provider is not available")

        try:
            full_prompt = prompt
            if style:
                full_prompt = f"{prompt}. Style: {style}"

            generation_config = genai.GenerationConfig(
                response_mime_type="image/png"
            )

            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )

            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        return base64.b64encode(part.inline_data.data).decode('utf-8')

            raise RuntimeError("No image generated in response")
        except Exception as e:
            logger.error(f"Imagen 4 generation error: {e}")
            raise
