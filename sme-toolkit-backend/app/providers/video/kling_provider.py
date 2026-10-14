"""Kling AI Video Generation Provider"""

from typing import Dict, Any, Optional
import logging
import httpx

from app.providers.base import VideoProvider, RateLimits

logger = logging.getLogger(__name__)


class KlingProvider(VideoProvider):
    """
    Kling AI Video Generation Provider

    Credit-based pricing: $10-180/month
    Up to 1080p, 3-minute videos
    """

    name = "kling"
    BASE_URL = "https://api.klingai.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self._is_configured = bool(api_key)

    async def is_available(self) -> bool:
        """Check if Kling AI is available"""
        return self._is_configured

    def get_rate_limits(self) -> RateLimits:
        """Kling AI rate limits"""
        return RateLimits(
            requests_per_minute=5,
            requests_per_day=30,  # Based on standard plan credits
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
        """Generate video using Kling AI"""
        if not await self.is_available():
            raise RuntimeError("Kling AI provider is not available")

        try:
            # Map resolution to Kling format
            kling_mode = "standard"
            if resolution == "1080p":
                kling_mode = "professional"

            # Map aspect ratio
            kling_ratio = "16:9"
            if aspect_ratio == "9:16":
                kling_ratio = "9:16"
            elif aspect_ratio == "1:1":
                kling_ratio = "1:1"

            async with httpx.AsyncClient() as client:
                # Create video generation task
                response = await client.post(
                    f"{self.BASE_URL}/videos/text2video",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": prompt,
                        "duration": str(duration),
                        "aspect_ratio": kling_ratio,
                        "mode": kling_mode,
                        "cfg_scale": 0.5
                    },
                    timeout=60.0
                )

                response.raise_for_status()
                data = response.json()

                # Kling returns a task ID for async generation
                if "task_id" in data:
                    return {
                        "status": "processing",
                        "job_id": data["task_id"],
                        "message": "Video generation started"
                    }

                if "video_url" in data:
                    return {
                        "status": "completed",
                        "video_url": data["video_url"],
                        "duration": duration
                    }

                return {
                    "status": "processing",
                    "message": "Video generation in progress",
                    "response": data
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"Kling AI API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Kling AI generation error: {e}")
            raise

    async def check_status(self, job_id: str) -> Dict[str, Any]:
        """Check the status of a video generation task"""
        if not await self.is_available():
            raise RuntimeError("Kling AI provider is not available")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/videos/text2video/{job_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    timeout=30.0
                )

                response.raise_for_status()
                data = response.json()

                status = data.get("status", "unknown")
                if status == "completed":
                    return {
                        "status": "completed",
                        "video_url": data.get("video_url"),
                        "duration": data.get("duration")
                    }
                elif status == "failed":
                    return {
                        "status": "failed",
                        "error": data.get("error", "Generation failed")
                    }
                else:
                    return {
                        "status": "processing",
                        "progress": data.get("progress", 0)
                    }
        except Exception as e:
            logger.error(f"Kling AI status check error: {e}")
            raise
