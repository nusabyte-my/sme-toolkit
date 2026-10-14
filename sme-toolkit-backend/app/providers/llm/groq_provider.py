"""Groq LLM Provider - Fast inference with free tier"""

from typing import Dict, Any, Optional
import json
import logging

from app.providers.base import LLMProvider, RateLimits

logger = logging.getLogger(__name__)

try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq package not installed. Run: pip install groq")


class GroqProvider(LLMProvider):
    """
    Groq LLM Provider using Llama 3.3 70B

    Free tier: 14,400 requests/day, 1M tokens/day
    Speed: 300+ tokens/second (fastest available)
    """

    name = "groq"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.model = "llama-3.3-70b-versatile"  # Best general-purpose model
        self.client = None

        if GROQ_AVAILABLE and api_key:
            self.client = AsyncGroq(api_key=api_key)
            self._is_configured = True
        else:
            self._is_configured = False

    async def is_available(self) -> bool:
        """Check if Groq is available"""
        return self._is_configured and self.client is not None

    def get_rate_limits(self) -> RateLimits:
        """Groq free tier limits"""
        return RateLimits(
            requests_per_minute=30,
            requests_per_day=14400,
            tokens_per_minute=60000,
            tokens_per_day=1000000
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text using Groq"""
        if not await self.is_available():
            raise RuntimeError("Groq provider is not available")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq generation error: {e}")
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
            raise RuntimeError("Groq provider is not available")

        # Build system prompt for JSON output
        json_system = system_prompt or ""
        if schema:
            json_system += f"\n\nYou must respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        else:
            json_system += "\n\nYou must respond with valid JSON only. No other text."

        messages = [
            {"role": "system", "content": json_system},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent JSON
                max_tokens=kwargs.get("max_tokens", 4096),
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq JSON response: {e}")
            # Try to extract JSON from response
            try:
                # Find JSON in response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(content[start:end])
            except:
                pass
            raise
        except Exception as e:
            logger.error(f"Groq JSON generation error: {e}")
            raise
