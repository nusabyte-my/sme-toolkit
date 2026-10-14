"""DeepSeek LLM Provider - Cost-effective with strong reasoning"""

from typing import Dict, Any, Optional
import json
import logging
import httpx

from app.providers.base import LLMProvider, RateLimits

logger = logging.getLogger(__name__)


class DeepSeekProvider(LLMProvider):
    """
    DeepSeek LLM Provider using OpenAI-compatible API

    Very cost-effective: 27x cheaper than GPT-4
    Models: deepseek-chat, deepseek-reasoner
    """

    name = "deepseek"
    BASE_URL = "https://api.deepseek.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.model = "deepseek-chat"
        self._is_configured = bool(api_key)

    async def is_available(self) -> bool:
        """Check if DeepSeek is available"""
        return self._is_configured

    def get_rate_limits(self) -> RateLimits:
        """DeepSeek rate limits"""
        return RateLimits(
            requests_per_minute=60,
            requests_per_day=5000,
            tokens_per_minute=100000,
            tokens_per_day=10000000
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text using DeepSeek"""
        if not await self.is_available():
            raise RuntimeError("DeepSeek provider is not available")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek generation error: {e}")
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
            raise RuntimeError("DeepSeek provider is not available")

        # Build system prompt for JSON output
        json_system = system_prompt or ""
        if schema:
            json_system += f"\n\nRespond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        else:
            json_system += "\n\nRespond with valid JSON only. No markdown, no explanation."

        messages = [
            {"role": "system", "content": json_system},
            {"role": "user", "content": prompt}
        ]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": kwargs.get("max_tokens", 4096),
                        "response_format": {"type": "json_object"}
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse DeepSeek JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"DeepSeek JSON generation error: {e}")
            raise
