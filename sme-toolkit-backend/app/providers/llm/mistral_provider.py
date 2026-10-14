"""Mistral AI LLM Provider - High quality with generous free tier"""

from typing import Dict, Any, Optional
import json
import logging

from app.providers.base import LLMProvider, RateLimits

logger = logging.getLogger(__name__)

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    logger.warning("Mistral package not installed. Run: pip install mistralai")


class MistralProvider(LLMProvider):
    """
    Mistral AI LLM Provider

    Free tier: 1B tokens/month
    Models: mistral-large-latest, mistral-small-latest
    """

    name = "mistral"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.model = "mistral-small-latest"  # Good balance of quality/cost
        self.client = None

        if MISTRAL_AVAILABLE and api_key:
            self.client = Mistral(api_key=api_key)
            self._is_configured = True
        else:
            self._is_configured = False

    async def is_available(self) -> bool:
        """Check if Mistral is available"""
        return self._is_configured and self.client is not None

    def get_rate_limits(self) -> RateLimits:
        """Mistral free tier limits"""
        return RateLimits(
            requests_per_minute=60,
            requests_per_day=10000,
            tokens_per_minute=500000,
            tokens_per_day=33000000  # ~1B/month
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text using Mistral"""
        if not await self.is_available():
            raise RuntimeError("Mistral provider is not available")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.complete_async(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Mistral generation error: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON output"""
        if not await self.is_available():
            raise RuntimeError("Mistral provider is not available")

        # Build system prompt for JSON output
        json_system = system_prompt or ""
        if schema:
            json_system += f"\n\nRespond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        else:
            json_system += "\n\nRespond with valid JSON only."

        messages = [
            {"role": "system", "content": json_system},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await self.client.chat.complete_async(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=kwargs.get("max_tokens", 4096),
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Mistral JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"Mistral JSON generation error: {e}")
            raise
