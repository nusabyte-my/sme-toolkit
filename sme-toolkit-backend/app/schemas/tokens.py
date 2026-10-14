"""
Token System Schemas
Pydantic models for token billing system
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


# ============================================================================
# ENUMS
# ============================================================================


class TransactionType(str, Enum):
    """Types of token transactions"""

    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"
    BONUS = "bonus"
    ROLLOVER = "rollover"
    ADJUSTMENT = "adjustment"


class ServiceType(str, Enum):
    """Types of AI services"""

    TEXT_LLM = "text_llm"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    AGENT_ORCHESTRATION = "agent_orchestration"
    ANALYSIS = "analysis"
    TRANSCRIPTION = "transcription"


class Modality(str, Enum):
    """Content modalities"""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MULTI_MODAL = "multi_modal"


class TierType(str, Enum):
    """Subscription tiers"""

    FREE = "Free"
    SME = "SME"
    BUSINESS = "Business"
    ENTERPRISE = "Enterprise"


# ============================================================================
# REQUEST MODELS
# ============================================================================


class TokenPurchaseRequest(BaseModel):
    """Request to purchase tokens"""

    package_id: str = Field(..., description="ID of token package to purchase")


class TokenChargeRequest(BaseModel):
    """Request to charge tokens for an operation"""

    user_id: str = Field(..., description="User ID")
    service_type: ServiceType = Field(..., description="Type of service")
    operation_id: str = Field(..., description="Operation identifier")
    tokens_required: int = Field(..., gt=0, description="Tokens required")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ModelPreferenceUpdate(BaseModel):
    """Request to update model preferences"""

    preferred_text_llm_model: Optional[str] = Field(
        None, description="Preferred text LLM model"
    )
    preferred_text_llm_provider: Optional[str] = Field(
        None, description="Preferred text LLM provider"
    )
    preferred_image_generation_model: Optional[str] = Field(
        None, description="Preferred image generation model"
    )
    preferred_image_generation_provider: Optional[str] = Field(
        None, description="Preferred image generation provider"
    )
    preferred_video_generation_model: Optional[str] = Field(
        None, description="Preferred video generation model"
    )
    preferred_video_generation_provider: Optional[str] = Field(
        None, description="Preferred video generation provider"
    )
    preferred_agent_orchestration_provider: Optional[str] = Field(
        None, description="Preferred agent orchestration provider"
    )

    smart_selection_enabled: Optional[bool] = Field(
        None, description="Enable smart model selection"
    )
    auto_select_cheapest: Optional[bool] = Field(
        None, description="Auto-select cheapest model"
    )
    max_cost_per_operation: Optional[float] = Field(
        None, description="Max cost per operation"
    )


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class TokenAccountResponse(BaseModel):
    """Token account information"""

    id: str
    user_id: str
    balance: float
    currency: str
    tier: str
    status: str
    rollover_balance: float
    last_token_charge_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenBalanceResponse(BaseModel):
    """Token balance information"""

    success: bool = True
    data: Dict[str, Any] = Field(
        ...,
        description="Balance data including token_account_id, balance, currency, tier, status, rollover_balance",
    )


class TransactionResponse(BaseModel):
    """Transaction history response"""

    success: bool = True
    data: Dict[str, Any] = Field(
        ..., description="Transaction data including list, total, page, total_pages"
    )


class QuotaCheckResponse(BaseModel):
    """Quota check response"""

    success: bool
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = Field(None, description="Quota information")


class TokenPackageResponse(BaseModel):
    """Token purchase response"""

    success: bool = True
    data: Dict[str, Any] = Field(
        ...,
        description="Purchase data including transaction_id, package_name, tokens_purchased, amount_charged",
    )


class UsageReportResponse(BaseModel):
    """Usage report response"""

    success: bool = True
    data: Dict[str, Any] = Field(..., description="Comprehensive usage report")


class TokenPackageInfo(BaseModel):
    """Token package information"""

    id: str
    name: str
    description: Optional[str]
    price: float
    token_amount: float
    currency: str
    tier: str
    bonus_tokens: int
    features: Optional[Any] = None
    is_active: bool

    class Config:
        from_attributes = True


class TransactionInfo(BaseModel):
    """Transaction information"""

    id: str
    token_account_id: str
    user_id: str
    transaction_type: str
    amount: float
    balance_after: float
    service_type: Optional[str]
    model_id: Optional[str]
    provider_id: Optional[str]
    modality: Optional[str]
    operation_id: Optional[str]
    operation_type: Optional[str]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    tokens_consumed: Optional[int]
    estimated_cost_usd: Optional[float]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class QuotaInfo(BaseModel):
    """Quota information"""

    id: str
    token_account_id: str
    tier: str
    period_type: str
    max_tokens: Optional[int]
    max_images: int
    max_videos: int
    max_agents: int
    max_api_calls: int
    tokens_used: int
    images_used: int
    videos_used: int
    agents_used: int
    api_calls_used: int
    reset_day: Optional[int]
    last_reset: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProviderCostInfo(BaseModel):
    """Provider cost rate information"""

    id: str
    provider_id: str
    provider_name: str
    service_type: str
    model_id: Optional[str]
    price_per_1k_tokens: Optional[float]
    price_per_image: Optional[float]
    price_per_video_second: Optional[float]
    price_per_agent_call: Optional[float]
    currency: str
    is_negotiated: bool
    volume_discount_percent: float
    avg_latency_ms: Optional[int]
    success_rate: float
    last_updated: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelPreferenceInfo(BaseModel):
    """Model preference information"""

    id: str
    token_account_id: str
    preferred_text_llm_model: Optional[str]
    preferred_text_llm_provider: Optional[str]
    preferred_image_generation_model: Optional[str]
    preferred_image_generation_provider: Optional[str]
    preferred_video_generation_model: Optional[str]
    preferred_video_generation_provider: Optional[str]
    preferred_agent_orchestration_provider: Optional[str]
    smart_selection_enabled: bool
    auto_select_cheapest: bool
    max_cost_per_operation: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertInfo(BaseModel):
    """Token usage alert information"""

    id: str
    token_account_id: str
    alert_type: str
    severity: str
    service_type: str
    message: str
    current_tokens_remaining: int
    percentage_used: float
    estimated_time_remaining: Optional[int]
    is_resolved: bool
    resolved_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# COMPLEX RESPONSES
# ============================================================================


class AvailableModel(BaseModel):
    """Available model for a service type"""

    provider_id: str
    provider_name: str
    model_id: Optional[str]
    model_name: str
    service_type: str
    price_info: Dict[str, float]
    features: List[str]
    is_available: bool


class ModelPreferenceResponse(BaseModel):
    """Model preference response"""

    success: bool = True
    data: ModelPreferenceInfo


class AvailableModelsResponse(BaseModel):
    """Available models response"""

    success: bool = True
    data: Dict[str, Any] = Field(
        ..., description="Available models, current preference, and provider rates"
    )


class AlertsResponse(BaseModel):
    """Alerts response"""

    success: bool = True
    data: Dict[str, Any] = Field(
        ..., description="Alerts list, unread count, high priority count, categories"
    )


class PackagesResponse(BaseModel):
    """Packages response"""

    success: bool = True
    data: Dict[str, Any] = Field(..., description="Available packages filtered by tier")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    services: Dict[str, str]


# ============================================================================
# ERROR RESPONSES
# ============================================================================


class ErrorResponse(BaseModel):
    """Error response"""

    success: bool = False
    error: str = Field(..., description="Error message")


class InsufficientTokensError(BaseModel):
    """Insufficient tokens error detail"""

    tokens_required: int
    available: float


class QuotaExceededError(BaseModel):
    """Quota exceeded error detail"""

    service_type: str
    limit: int
    usage: int
    tier: str
    reset_date: Optional[datetime]
