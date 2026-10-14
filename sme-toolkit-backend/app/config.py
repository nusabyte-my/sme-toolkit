from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Primary AI Provider - Gemini
    gemini_api_key: str = ""
    gemini_text_model: str = 'gemini-3.8-flash'
    gemini_image_model: str = 'gemini-3.1-flash-image'
    gemini_video_model: str = 'veo-3.1-fast-generate-preview'
    ffmpeg_path: str = 'ffmpeg'

    # LLM Providers
    groq_api_key: str = ""
    mistral_api_key: str = ""
    deepseek_api_key: str = ""
    openai_api_key: str = ""  # For OpenAI-compatible providers
    fiqstr_api_key: str = ""
    fiqstr_base_url: str = "https://core.fiqstr.my.id/v1"
    fiqstr_model: str = "fiqstr/deepseek-3.2"

    # Image Generation Providers
    replicate_api_key: str = ""  # For FLUX.2
    stability_api_key: str = ""  # For Stable Diffusion

    # Video Generation Providers
    kling_api_key: str = ""

    # Provider Priority (comma-separated, first = highest priority)
    llm_provider_priority: str = "fiqstr-v2,gemini,groq,mistral,deepseek"
    image_provider_priority: str = "gemini,flux,stability"
    video_provider_priority: str = "veo3,kling,nanobanana"

    # Tier Rate Limits
    free_tier_daily_requests: int = 50
    sme_tier_daily_requests: int = 500
    business_tier_daily_requests: int = 2000

    # JWT Settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    admin_password: str = ''
    n8n_password: str = ''

    # Database
    database_url: str = "sqlite+aiosqlite:///./sme_toolkit.db"

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # App
    debug: bool = True
    automation_scheduler_enabled: bool = True
    automation_poll_seconds: int = Field(default=60, ge=5, le=3600)
    channel_encryption_key: str = ''
    public_webhook_base_url: str = ''
    whatsapp_api_version: str = 'v23.0'

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
