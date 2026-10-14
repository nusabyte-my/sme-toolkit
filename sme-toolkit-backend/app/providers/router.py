"""Provider router with automatic fallback support"""

from typing import Dict, List, Optional, Type
import logging

from app.providers.base import (
    AIProvider,
    LLMProvider,
    ImageProvider,
    VideoProvider,
    ProviderRequest,
    ProviderResponse,
    LLMRequest,
    LLMResponse,
    ImageRequest,
    ImageResponse,
    VideoRequest,
    VideoResponse,
    MockLLMProvider,
    MockImageProvider,
    MockVideoProvider,
    ProviderModality
)
from app.providers.rate_limiter import get_rate_limiter, TierRateLimiter
from app.config import settings

logger = logging.getLogger(__name__)


class ProviderRouter:
    """Routes AI requests to appropriate providers with fallback support"""

    # Provider priority by tier
    TIER_PROVIDER_CONFIG = {
        "free": {
            "llm": ["fiqstr-v2", "groq", "mistral", "deepseek"],
            "image": ["flux"],
            "video": []  # No video for free tier
        },
        "sme": {
            "llm": ["fiqstr-v2", "gemini", "groq", "mistral"],
            "image": ["gemini", "flux"],
            "video": ["veo_fast"]
        },
        "business": {
            "llm": ["fiqstr-v2", "gemini_pro", "gemini", "groq"],
            "image": ["imagen4", "nanobanana", "flux"],
            "video": ["veo3", "kling", "nanobanana"]
        },
        "enterprise": {
            "llm": ["fiqstr-v2", "gemini_pro", "gemini", "groq", "mistral"],
            "image": ["imagen4", "nanobanana", "flux", "stability"],
            "video": ["veo3", "kling", "nanobanana"]
        }
    }

    def __init__(self):
        self.llm_providers: Dict[str, LLMProvider] = {}
        self.image_providers: Dict[str, ImageProvider] = {}
        self.video_providers: Dict[str, VideoProvider] = {}
        self.rate_limiter = get_rate_limiter()
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize all available providers based on API keys"""
        # Initialize LLM providers
        self._init_llm_providers()
        # Initialize image providers
        self._init_image_providers()
        # Initialize video providers
        self._init_video_providers()

        logger.info(f"Initialized providers - LLM: {list(self.llm_providers.keys())}, "
                    f"Image: {list(self.image_providers.keys())}, "
                    f"Video: {list(self.video_providers.keys())}")

    def _init_llm_providers(self) -> None:
        """Initialize LLM providers"""
        # Fiqstr (OpenAI-compatible)
        try:
            from app.providers.llm.fiqstr_provider import FiqstrProvider
            self.llm_providers["fiqstr-v2"] = FiqstrProvider(
                api_key=settings.fiqstr_api_key,
                base_url=settings.fiqstr_base_url,
                model=settings.fiqstr_model,
            )
        except ImportError:
            logger.warning("Fiqstr provider not available")

        # Groq
        if settings.groq_api_key:
            try:
                from app.providers.llm.groq_provider import GroqProvider
                self.llm_providers["groq"] = GroqProvider(settings.groq_api_key)
            except ImportError:
                logger.warning("Groq provider not available")

        # Mistral
        if settings.mistral_api_key:
            try:
                from app.providers.llm.mistral_provider import MistralProvider
                self.llm_providers["mistral"] = MistralProvider(settings.mistral_api_key)
            except ImportError:
                logger.warning("Mistral provider not available")

        # DeepSeek
        if settings.deepseek_api_key:
            try:
                from app.providers.llm.deepseek_provider import DeepSeekProvider
                self.llm_providers["deepseek"] = DeepSeekProvider(settings.deepseek_api_key)
            except ImportError:
                logger.warning("DeepSeek provider not available")

        # Gemini (regular and pro)
        if settings.gemini_api_key:
            try:
                from app.providers.llm.gemini_provider import GeminiProvider, GeminiProProvider
                self.llm_providers["gemini"] = GeminiProvider(settings.gemini_api_key)
                self.llm_providers["gemini_pro"] = GeminiProProvider(settings.gemini_api_key)
            except ImportError:
                logger.warning("Gemini provider not available")

        # Always add mock provider as final fallback
        self.llm_providers["mock"] = MockLLMProvider()

    def _init_image_providers(self) -> None:
        """Initialize image providers"""
        # Gemini Image
        if settings.gemini_api_key:
            try:
                from app.providers.image.gemini_image_provider import GeminiImageProvider, Imagen4Provider
                self.image_providers["gemini"] = GeminiImageProvider(settings.gemini_api_key)
                self.image_providers["imagen4"] = Imagen4Provider(settings.gemini_api_key)
                self.image_providers["nanobanana"] = GeminiImageProvider(settings.gemini_api_key)  # Uses same API
            except ImportError:
                logger.warning("Gemini image provider not available")

        # FLUX via Replicate
        if settings.replicate_api_key:
            try:
                from app.providers.image.flux_provider import FluxProvider
                self.image_providers["flux"] = FluxProvider(settings.replicate_api_key)
            except ImportError:
                logger.warning("FLUX provider not available")

        # Stability AI
        if settings.stability_api_key:
            try:
                from app.providers.image.stability_provider import StabilityProvider
                self.image_providers["stability"] = StabilityProvider(settings.stability_api_key)
            except ImportError:
                logger.warning("Stability provider not available")

        # Always add mock provider
        self.image_providers["mock"] = MockImageProvider()

    def _init_video_providers(self) -> None:
        """Initialize video providers"""
        # Veo (Google)
        if settings.gemini_api_key:
            try:
                from app.providers.video.veo_provider import VeoProvider, VeoFastProvider
                self.video_providers["veo3"] = VeoProvider(settings.gemini_api_key)
                self.video_providers["veo_fast"] = VeoFastProvider(settings.gemini_api_key)
            except ImportError:
                logger.warning("Veo provider not available")

        # Kling AI
        if settings.kling_api_key:
            try:
                from app.providers.video.kling_provider import KlingProvider
                self.video_providers["kling"] = KlingProvider(settings.kling_api_key)
            except ImportError:
                logger.warning("Kling provider not available")

        # Nano Banana (uses Gemini)
        if settings.gemini_api_key:
            try:
                from app.providers.video.nanobanana_provider import NanoBananaProvider
                self.video_providers["nanobanana"] = NanoBananaProvider(settings.gemini_api_key)
            except ImportError:
                logger.warning("NanoBanana provider not available")

        # Always add mock provider
        self.video_providers["mock"] = MockVideoProvider()

    def _get_providers_for_tier(
        self,
        modality: str,
        tier: str
    ) -> List[AIProvider]:
        """Get ordered list of providers for a tier"""
        config = self.TIER_PROVIDER_CONFIG.get(tier, self.TIER_PROVIDER_CONFIG["free"])
        provider_names = config.get(modality, [])

        if modality == "llm":
            providers = self.llm_providers
        elif modality == "image":
            providers = self.image_providers
        elif modality == "video":
            providers = self.video_providers
        else:
            return []

        # Return providers in priority order, only if they exist
        result = []
        for name in provider_names:
            if name in providers:
                result.append(providers[name])

        # Always add mock as last fallback
        if "mock" in providers:
            result.append(providers["mock"])

        return result

    async def route_llm_request(
        self,
        request: LLMRequest,
        user_id: str,
        tier: str = "free"
    ) -> LLMResponse:
        """Route an LLM request with automatic fallback"""
        # Check rate limit first
        rate_check = await self.rate_limiter.check_rate_limit(user_id, tier, "llm")
        if not rate_check.allowed:
            return LLMResponse(
                success=False,
                provider_name="rate_limiter",
                error=f"Rate limit exceeded. Daily limit: {rate_check.limit}, remaining: {rate_check.remaining}"
            )

        providers = self._get_providers_for_tier("llm", tier)
        return await self._execute_with_fallback(request, providers, user_id, "llm")

    async def route_image_request(
        self,
        request: ImageRequest,
        user_id: str,
        tier: str = "free"
    ) -> ImageResponse:
        """Route an image request with automatic fallback"""
        # Check rate limit first
        rate_check = await self.rate_limiter.check_rate_limit(user_id, tier, "image")
        if not rate_check.allowed:
            return ImageResponse(
                success=False,
                provider_name="rate_limiter",
                error=f"Rate limit exceeded. Daily limit: {rate_check.limit}, remaining: {rate_check.remaining}"
            )

        providers = self._get_providers_for_tier("image", tier)
        return await self._execute_with_fallback(request, providers, user_id, "image")

    async def route_video_request(
        self,
        request: VideoRequest,
        user_id: str,
        tier: str = "free"
    ) -> VideoResponse:
        """Route a video request with automatic fallback"""
        # Check rate limit first
        rate_check = await self.rate_limiter.check_rate_limit(user_id, tier, "video")
        if not rate_check.allowed:
            return VideoResponse(
                success=False,
                provider_name="rate_limiter",
                error=f"Video not available for your tier or rate limit exceeded"
            )

        providers = self._get_providers_for_tier("video", tier)
        if not providers or (len(providers) == 1 and providers[0].name == "mock"):
            return VideoResponse(
                success=False,
                provider_name="none",
                error="Video generation is not available for your subscription tier"
            )

        return await self._execute_with_fallback(request, providers, user_id, "video")

    async def _execute_with_fallback(
        self,
        request: ProviderRequest,
        providers: List[AIProvider],
        user_id: str,
        modality: str
    ) -> ProviderResponse:
        """Execute request with automatic fallback through provider chain"""
        errors = []

        for provider in providers:
            try:
                # Skip mock provider unless it's the last option
                if provider.name == "mock" and len(providers) > 1 and provider != providers[-1]:
                    continue

                # Check if provider is available
                if not await provider.is_available():
                    errors.append((provider.name, "Provider not available"))
                    continue

                logger.debug(f"Trying {modality} provider: {provider.name}")
                result = await provider.execute(request)

                if result.success:
                    # Increment usage on success
                    await self.rate_limiter.increment_usage(user_id, modality)
                    logger.info(f"Successfully used {modality} provider: {provider.name}")
                    return result
                else:
                    errors.append((provider.name, result.error or "Unknown error"))

            except Exception as e:
                logger.error(f"Provider {provider.name} failed: {e}")
                errors.append((provider.name, str(e)))
                continue

        # All providers failed
        error_summary = "; ".join([f"{name}: {err}" for name, err in errors])
        logger.error(f"All {modality} providers failed: {error_summary}")

        # Return appropriate response type
        if modality == "llm":
            return LLMResponse(
                success=False,
                provider_name="none",
                error=f"All providers failed: {error_summary}"
            )
        elif modality == "image":
            return ImageResponse(
                success=False,
                provider_name="none",
                error=f"All providers failed: {error_summary}"
            )
        else:
            return VideoResponse(
                success=False,
                provider_name="none",
                error=f"All providers failed: {error_summary}"
            )

    def get_available_providers(self, tier: str) -> Dict[str, List[str]]:
        """Get list of available providers for a tier"""
        config = self.TIER_PROVIDER_CONFIG.get(tier, self.TIER_PROVIDER_CONFIG["free"])

        available = {}
        for modality, provider_names in config.items():
            if modality == "llm":
                providers = self.llm_providers
            elif modality == "image":
                providers = self.image_providers
            elif modality == "video":
                providers = self.video_providers
            else:
                continue

            available[modality] = [
                name for name in provider_names
                if name in providers
            ]

        return available

    def get_provider_status(self) -> Dict[str, Dict[str, bool]]:
        """Get status of all providers"""
        status = {
            "llm": {},
            "image": {},
            "video": {}
        }

        for name, provider in self.llm_providers.items():
            if name != "mock":
                status["llm"][name] = provider.is_configured

        for name, provider in self.image_providers.items():
            if name != "mock":
                status["image"][name] = provider.is_configured

        for name, provider in self.video_providers.items():
            if name != "mock":
                status["video"][name] = provider.is_configured

        return status


# Singleton instance
_provider_router: Optional[ProviderRouter] = None


def get_provider_router() -> ProviderRouter:
    """Get the singleton provider router instance"""
    global _provider_router
    if _provider_router is None:
        _provider_router = ProviderRouter()
    return _provider_router
