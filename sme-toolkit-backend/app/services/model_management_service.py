"""
Model Management Service (Backend)
Handles model selection, availability, and preferences.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import ModelPreference, TokenAccount
from app.schemas.tokens import ServiceType

logger = logging.getLogger(__name__)


PREFERENCE_FIELD_PREFIX = {
    "llm": "text_llm",
    "image": "image_generation",
    "video": "video_generation",
}


PROVIDER_DISPLAY_NAMES = {
    "fiqstr-v2": "Fiqstr V2",
}


# Available models configuration
AVAILABLE_MODELS = {
    "llm": {
        "fiqstr-v2": [
            {
                "id": "fiqstr/deepseek-3.2",
                "name": "Deepseek 3.2",
                "description": "Fiqstr OpenAI-compatible reasoning model",
                "cost_per_1k_tokens": 0.0,
                "performance": {"speed": "fast", "quality": "excellent"},
                "capabilities": ["chat", "completion", "code", "reasoning", "vision", "function_calling"],
                "tiers": ["Free", "SME", "Business", "Enterprise"],
                "category": "standard",
            },
            {
                "id": "fiqstr/glm-5",
                "name": "Glm 5",
                "description": "Fiqstr OpenAI-compatible chat model",
                "cost_per_1k_tokens": 0.0,
                "performance": {"speed": "fast", "quality": "excellent"},
                "capabilities": ["chat", "completion", "code", "reasoning"],
                "tiers": ["Free", "SME", "Business", "Enterprise"],
                "category": "standard",
            },
            {
                "id": "fiqstr/minimax-m2.1",
                "name": "Minimax M2.1",
                "description": "Fiqstr OpenAI-compatible chat model",
                "cost_per_1k_tokens": 0.0,
                "performance": {"speed": "fast", "quality": "excellent"},
                "capabilities": ["chat", "completion", "code", "reasoning"],
                "tiers": ["Free", "SME", "Business", "Enterprise"],
                "category": "standard",
            },
            {
                "id": "fiqstr/minimax-m2.5",
                "name": "Minimax M2.5",
                "description": "Fiqstr OpenAI-compatible chat model",
                "cost_per_1k_tokens": 0.0,
                "performance": {"speed": "fast", "quality": "excellent"},
                "capabilities": ["chat", "completion", "code", "reasoning"],
                "tiers": ["Free", "SME", "Business", "Enterprise"],
                "category": "standard",
            },
            {
                "id": "fiqstr/qwen3-coder-next",
                "name": "Qwen3 Coder Next",
                "description": "Fiqstr OpenAI-compatible coding model",
                "cost_per_1k_tokens": 0.0,
                "performance": {"speed": "fast", "quality": "excellent"},
                "capabilities": ["chat", "completion", "code", "reasoning", "function_calling"],
                "tiers": ["Free", "SME", "Business", "Enterprise"],
                "category": "standard",
            },
        ],
        "google": [
            {
                "id": "gemini-2.0-flash",
                "name": "Gemini 2.0 Flash",
                "description": "Fastest inference with excellent quality",
                "cost_per_1k_tokens": 0.00001,
                "performance": {"speed": "500 tok/s", "quality": "excellent"},
                "capabilities": ["chat", "completion", "code", "reasoning", "multimodal"],
                "tiers": ["Free", "SME", "Business", "Enterprise"],
                "category": "standard",
            },
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "description": "High-quality reasoning with 2M context window",
                "cost_per_1k_tokens": 0.000035,
                "performance": {"speed": "50 tok/s", "quality": "excellent"},
                "capabilities": ["chat", "completion", "code", "reasoning", "multimodal", "analysis"],
                "tiers": ["SME", "Business", "Enterprise"],
                "category": "premium",
            },
        ],
        "groq": [
            {
                "id": "llama-3.3-70b",
                "name": "Llama 3.3 70B",
                "description": "Ultra-fast open source model",
                "cost_per_1k_tokens": 0.00059,
                "performance": {"speed": "300 tok/s", "quality": "high"},
                "capabilities": ["chat", "completion", "code", "reasoning"],
                "tiers": ["Free", "SME", "Business", "Enterprise"],
                "category": "standard",
            },
            {
                "id": "mixtral-8x7b",
                "name": "Mixtral 8x7B",
                "description": "Mixture of experts model",
                "cost_per_1k_tokens": 0.00027,
                "performance": {"speed": "400 tok/s", "quality": "high"},
                "capabilities": ["chat", "completion", "code"],
                "tiers": ["Free", "SME", "Business", "Enterprise"],
                "category": "free",
            },
        ],
        "mistral": [
            {
                "id": "mistral-large",
                "name": "Mistral Large",
                "description": "Top-tier reasoning and multilingual",
                "cost_per_1k_tokens": 0.002,
                "performance": {"speed": "60 tok/s", "quality": "excellent"},
                "capabilities": ["chat", "completion", "code", "reasoning", "multilingual"],
                "tiers": ["Business", "Enterprise"],
                "category": "premium",
            },
        ],
        "deepseek": [
            {
                "id": "deepseek-v3",
                "name": "DeepSeek V3",
                "description": "State-of-the-art reasoning at low cost",
                "cost_per_1k_tokens": 0.00014,
                "performance": {"speed": "80 tok/s", "quality": "excellent"},
                "capabilities": ["chat", "completion", "code", "reasoning", "math"],
                "tiers": ["SME", "Business", "Enterprise"],
                "category": "standard",
            },
        ],
    },
    "image": {
        "google": [
            {
                "id": "imagen-3",
                "name": "Imagen 3",
                "description": "Google's highest quality image model",
                "cost_per_image": 0.04,
                "performance": {"speed": "8s", "quality": "excellent"},
                "capabilities": ["text-to-image", "photorealistic", "artistic"],
                "tiers": ["SME", "Business", "Enterprise"],
                "category": "premium",
            },
        ],
        "flux": [
            {
                "id": "flux-1.1-pro",
                "name": "FLUX 1.1 Pro",
                "description": "Latest FLUX model with enhanced quality",
                "cost_per_image": 0.04,
                "performance": {"speed": "10s", "quality": "excellent"},
                "capabilities": ["text-to-image", "artistic", "photorealistic"],
                "tiers": ["Business", "Enterprise"],
                "category": "premium",
            },
            {
                "id": "flux-1-schnell",
                "name": "FLUX.1 Schnell",
                "description": "Fast generation for quick iterations",
                "cost_per_image": 0.003,
                "performance": {"speed": "2s", "quality": "high"},
                "capabilities": ["text-to-image"],
                "tiers": ["Free", "SME", "Business", "Enterprise"],
                "category": "free",
            },
        ],
        "stability": [
            {
                "id": "sdxl-turbo",
                "name": "SDXL Turbo",
                "description": "Real-time image generation",
                "cost_per_image": 0.002,
                "performance": {"speed": "1s", "quality": "high"},
                "capabilities": ["text-to-image", "real-time"],
                "tiers": ["Free", "SME", "Business", "Enterprise"],
                "category": "free",
            },
        ],
    },
    "video": {
        "google": [
            {
                "id": "veo-3",
                "name": "Veo 3",
                "description": "Google's advanced video generation",
                "cost_per_second": 0.05,
                "performance": {"speed": "fast", "quality": "excellent"},
                "capabilities": ["text-to-video", "high-resolution", "audio"],
                "tiers": ["Business", "Enterprise"],
                "category": "premium",
            },
        ],
        "kling": [
            {
                "id": "kling-1.6",
                "name": "Kling 1.6",
                "description": "Up to 3-minute videos with cinematic quality",
                "cost_per_second": 0.02,
                "performance": {"speed": "slow", "quality": "excellent"},
                "capabilities": ["text-to-video", "long-form", "cinematic"],
                "tiers": ["Business", "Enterprise"],
                "category": "premium",
            },
        ],
    },
}


class ModelManagementService:
    """Service for managing AI model selection and availability"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_available_models(
        self,
        user_id: str,
        modality: str,
    ) -> List[Dict[str, Any]]:
        """Get available models based on user tier and modality"""
        # Get user tier
        account_result = await self.db.execute(
            select(TokenAccount).where(TokenAccount.user_id == user_id)
        )
        account = account_result.scalar_one_or_none()
        tier = account.tier if account else "Free"

        # Get models for the modality
        modality_models = AVAILABLE_MODELS.get(modality, {})
        available_models = []

        for provider_id, models in modality_models.items():
            provider_models = []
            for model in models:
                is_available = tier in model.get("tiers", [])
                provider_models.append({
                    **model,
                    "provider_id": provider_id,
                    "available": is_available,
                })
            
            if provider_models:
                available_models.append({
                    "provider_id": provider_id,
                    "provider_name": PROVIDER_DISPLAY_NAMES.get(provider_id, provider_id.title()),
                    "models": provider_models,
                })

        return available_models

    async def set_user_model_preference(
        self,
        user_id: str,
        modality: str,
        model_id: str,
        provider_id: str,
    ) -> bool:
        """Set user's preferred model for a modality"""
        # Verify model is available
        available = await self.get_available_models(user_id, modality)
        model_available = any(
            any(m["id"] == model_id and m["available"] for m in p["models"])
            for p in available
        )

        if not model_available:
            raise ValueError(f"Model {model_id} not available for user's tier")

        # Update or create preference
        account_result = await self.db.execute(
            select(TokenAccount).where(TokenAccount.user_id == user_id)
        )
        account = account_result.scalar_one_or_none()
        if not account:
            raise ValueError(f"Token account not found for user {user_id}")

        pref = await self.db.execute(
            select(ModelPreference).where(ModelPreference.token_account_id == account.id)
        )
        existing = pref.scalar_one_or_none()
        field_prefix = PREFERENCE_FIELD_PREFIX[modality]

        if existing:
            setattr(existing, f"preferred_{field_prefix}_model", model_id)
            setattr(existing, f"preferred_{field_prefix}_provider", provider_id)
            existing.updated_at = datetime.utcnow()
        else:
            new_pref = ModelPreference(
                id=str(uuid.uuid4()),
                token_account_id=account.id,
                **{
                    f"preferred_{field_prefix}_model": model_id,
                    f"preferred_{field_prefix}_provider": provider_id,
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(new_pref)

        await self.db.commit()
        return True

    async def get_user_model_preference(
        self,
        user_id: str,
        modality: str,
    ) -> Dict[str, str]:
        """Get user's preferred model for a modality"""
        account_result = await self.db.execute(
            select(TokenAccount).where(TokenAccount.user_id == user_id)
        )
        account = account_result.scalar_one_or_none()
        if account:
            pref = await self.db.execute(
                select(ModelPreference).where(ModelPreference.token_account_id == account.id)
            )
            existing = pref.scalar_one_or_none()
        else:
            existing = None

        if existing:
            field_prefix = PREFERENCE_FIELD_PREFIX[modality]
            return {
                "model_id": getattr(existing, f"preferred_{field_prefix}_model", None),
                "provider_id": getattr(existing, f"preferred_{field_prefix}_provider", None),
            }

        # Return default based on modality
        defaults = {
            "llm": {"model_id": "fiqstr/deepseek-3.2", "provider_id": "fiqstr-v2"},
            "image": {"model_id": "flux-1-schnell", "provider_id": "flux"},
            "video": {"model_id": "veo-3", "provider_id": "google"},
        }
        return defaults.get(modality, {"model_id": None, "provider_id": None})

    async def get_model_cost(
        self,
        modality: str,
        model_id: str,
        provider_id: str,
    ) -> Dict[str, Any]:
        """Get cost information for a specific model"""
        modality_models = AVAILABLE_MODELS.get(modality, {})
        provider_models = modality_models.get(provider_id, [])

        for model in provider_models:
            if model["id"] == model_id:
                return {
                    "model_id": model_id,
                    "provider_id": provider_id,
                    "cost_per_1k_tokens": model.get("cost_per_1k_tokens"),
                    "cost_per_image": model.get("cost_per_image"),
                    "cost_per_second": model.get("cost_per_second"),
                    "category": model.get("category"),
                }

        return {"error": "Model not found"}
