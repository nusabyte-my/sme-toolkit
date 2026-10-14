"""Google Veo Video Generation Provider"""

from typing import Dict, Any, Optional
import logging

from app.providers.base import VideoProvider, RateLimits

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("Google GenerativeAI package not installed")


class VeoProvider(VideoProvider):
    """
    Veo 3 Video Generation Provider

    High quality video generation with audio support
    Pricing: $0.40-0.75 per second
    """

    name = "veo3"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.model_name = "veo-3.0-generate-preview"

        if GENAI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            self._is_configured = True
        else:
            self._is_configured = False

    async def is_available(self) -> bool:
        """Check if Veo is available"""
        return self._is_configured

    def get_rate_limits(self) -> RateLimits:
        """Veo 3 rate limits"""
        return RateLimits(
            requests_per_minute=5,
            requests_per_day=50,
            tokens_per_minute=0,
            tokens_per_day=0
        )

    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        audio: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Veo 3"""
        if not await self.is_available():
            raise RuntimeError("Veo provider is not available")

        try:
            # Build generation config
            generation_config = {
                "video_duration": f"{duration}s",
                "aspect_ratio": aspect_ratio,
                "person_generation": "allow",
            }

            if resolution == "1080p":
                generation_config["output_resolution"] = "1080p"
            else:
                generation_config["output_resolution"] = "720p"

            if audio:
                generation_config["audio"] = "enable"

            # Create video model
            video_model = genai.GenerativeModel(self.model_name)

            # Generate video (async operation)
            operation = await video_model.generate_content_async(
                prompt,
                generation_config=genai.GenerationConfig(**generation_config)
            )

            # Check if we got a video response
            if hasattr(operation, 'video_uri'):
                return {
                    "status": "completed",
                    "video_url": operation.video_uri,
                    "duration": duration
                }

            # For async generation, return job info
            if hasattr(operation, 'operation_name'):
                return {
                    "status": "processing",
                    "job_id": operation.operation_name,
                    "message": "Video generation in progress"
                }

            return {
                "status": "completed",
                "message": "Video generated",
                "response": str(operation)
            }
        except Exception as e:
            logger.error(f"Veo generation error: {e}")
            raise


class VeoFastProvider(VeoProvider):
    """
    Veo 3 Fast Video Generation Provider

    Faster, more cost-effective option
    Pricing: $0.15 per second
    """

    name = "veo_fast"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.model_name = "veo-3.0-fast-generate-preview"

    def get_rate_limits(self) -> RateLimits:
        """Veo Fast rate limits (more generous)"""
        return RateLimits(
            requests_per_minute=10,
            requests_per_day=100,
            tokens_per_minute=0,
            tokens_per_day=0
        )

    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        audio: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Veo 3 Fast (720p only)"""
        # Veo Fast only supports 720p
        return await super().generate_video(
            prompt=prompt,
            duration=min(duration, 8),  # Max 8 seconds for fast
            resolution="720p",
            aspect_ratio=aspect_ratio,
            audio=False,  # No audio in fast mode
            **kwargs
        )
