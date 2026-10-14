"""Gemini LLM Provider - Google's primary AI model"""

from typing import Dict, Any, Optional
import json
import logging

from app.providers.base import LLMProvider, RateLimits

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("Google GenerativeAI package not installed. Run: pip install google-generativeai")


class GeminiProvider(LLMProvider):
    """
    Gemini Flash LLM Provider

    Free tier: 1M tokens/minute via AI Studio
    Fast and efficient for most tasks
    """

    name = "gemini"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.model_name = "gemini-2.0-flash"
        self.model = None

        if GENAI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self._is_configured = True
        else:
            self._is_configured = False

    async def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self._is_configured and self.model is not None

    def get_rate_limits(self) -> RateLimits:
        """Gemini Flash free tier limits"""
        return RateLimits(
            requests_per_minute=60,
            requests_per_day=1500,
            tokens_per_minute=1000000,
            tokens_per_day=50000000
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text using Gemini"""
        if not await self.is_available():
            raise RuntimeError("Gemini provider is not available")

        try:
            # Combine system prompt with user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
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
            raise RuntimeError("Gemini provider is not available")

        # Build prompt for JSON output
        json_prompt = system_prompt or ""
        if schema:
            json_prompt += f"\n\nRespond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        else:
            json_prompt += "\n\nRespond with valid JSON only."
        json_prompt += f"\n\n{prompt}"

        try:
            generation_config = genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=kwargs.get("max_tokens", 4096),
                response_mime_type="application/json"
            )

            response = await self.model.generate_content_async(
                json_prompt,
                generation_config=generation_config
            )

            content = response.text
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            # Try to extract JSON from response
            try:
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(content[start:end])
            except:
                pass
            raise
        except Exception as e:
            logger.error(f"Gemini JSON generation error: {e}")
            raise


class GeminiProProvider(GeminiProvider):
    """
    Gemini Pro LLM Provider

    Higher quality, better reasoning
    For business/enterprise tiers
    """

    name = "gemini_pro"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.model_name = "gemini-2.0-pro"

        if GENAI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self._is_configured = True

    def get_rate_limits(self) -> RateLimits:
        """Gemini Pro rate limits (more restrictive)"""
        return RateLimits(
            requests_per_minute=30,
            requests_per_day=500,
            tokens_per_minute=500000,
            tokens_per_day=25000000
        )
