"""Fiqstr LLM Provider - OpenAI-compatible API gateway."""

from typing import Dict, Any, Optional
import json
import logging

import httpx

from app.providers.base import LLMProvider, RateLimits

logger = logging.getLogger(__name__)


class FiqstrProvider(LLMProvider):
    """Fiqstr provider using the documented OpenAI-compatible chat API."""

    name = "fiqstr-v2"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://core.fiqstr.my.id/v1",
        model: str = "fiqstr/deepseek-3.2",
    ):
        super().__init__(api_key)
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._is_configured = bool(api_key)

    async def is_available(self) -> bool:
        """Check if Fiqstr is configured."""
        return self._is_configured

    def get_rate_limits(self) -> RateLimits:
        """Fiqstr limits are account dependent; use conservative defaults."""
        return RateLimits(
            requests_per_minute=60,
            requests_per_day=5000,
            tokens_per_minute=100000,
            tokens_per_day=10000000,
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
        """Generate text using Fiqstr chat completions."""
        if not await self.is_available():
            raise RuntimeError("Fiqstr provider is not available")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            data = await self._chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Fiqstr generation error: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate structured JSON output using Fiqstr."""
        if not await self.is_available():
            raise RuntimeError("Fiqstr provider is not available")

        json_system = system_prompt or ""
        if schema:
            json_system += f"\n\nRespond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        else:
            json_system += "\n\nRespond with valid JSON only. No markdown, no explanation."

        messages = [
            {"role": "system", "content": json_system},
            {"role": "user", "content": prompt},
        ]

        try:
            data = await self._chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=kwargs.get("max_tokens", 4096),
                response_format={"type": "json_object"},
            )
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Fiqstr JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"Fiqstr JSON generation error: {e}")
            raise

    async def _chat_completion(self, **payload: Any) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": self.model, **payload},
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()
