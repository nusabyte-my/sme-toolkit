"""
GeminiClient - Legacy wrapper for the unified AI provider system.

This module provides backwards compatibility for code that uses GeminiClient.
New code should use AIClient from app.tools.ai_client directly.
"""

import json
import asyncio
from typing import Optional, Dict, Any
from functools import lru_cache
import logging

from app.config import settings
from app.tools.ai_client import AIClient, get_ai_client

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Legacy Gemini client wrapper that routes through the multi-provider system.

    This class maintains backwards compatibility with existing code while
    using the new provider routing system under the hood.

    For new code, use AIClient from app.tools.ai_client instead.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        user_id: str = "default",
        tier: str = "free"
    ):
        """
        Initialize the Gemini client.

        Args:
            api_key: Ignored - provider system manages API keys
            user_id: User ID for rate limiting and tier resolution
            tier: Subscription tier (free, sme, business, enterprise)
        """
        self._client = AIClient(user_id=user_id, tier=tier)
        self.user_id = user_id
        self.tier = tier

        # For backwards compatibility - always False as provider system handles mocking
        self.is_mock = False

    def with_user(self, user_id: str, tier: str = "free") -> "GeminiClient":
        """Return a new client instance with different user context"""
        return GeminiClient(user_id=user_id, tier=tier)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_pro: bool = False,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using the best available LLM provider.

        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt for context
            use_pro: If True, prefer pro-level models
            temperature: Creativity control (0-1)

        Returns:
            Generated text content
        """
        return await self._client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            use_pro=use_pro
        )

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_pro: bool = False
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output.

        Args:
            prompt: The input prompt requesting JSON output
            system_prompt: Optional system prompt for context
            use_pro: If True, prefer pro-level models

        Returns:
            Parsed JSON dictionary
        """
        return await self._client.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            use_pro=use_pro
        )

    async def enhance_prompt(self, original: str) -> str:
        """
        Enhance a user prompt to be more descriptive.

        Args:
            original: The original prompt

        Returns:
            Enhanced prompt
        """
        return await self._client.enhance_prompt(original)


@lru_cache()
def get_gemini_client() -> GeminiClient:
    """
    Get singleton Gemini client.

    This uses the default user context. For user-specific requests,
    create a new client with GeminiClient(user_id=..., tier=...).
    """
    return GeminiClient()


# Re-export AIClient for new code
__all__ = ["GeminiClient", "get_gemini_client", "AIClient", "get_ai_client"]
