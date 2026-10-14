"""Business suggestion-related Pydantic schemas"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class SuggestionType(str, Enum):
    NEW_REVENUE_STREAM = "new_revenue_stream"
    PARTNERSHIP = "partnership"
    MARKET_EXPANSION = "market_expansion"
    PRODUCT_INNOVATION = "product_innovation"


class SuggestionStatus(str, Enum):
    SUGGESTED = "suggested"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class NewOpportunity(BaseModel):
    """New business opportunity"""
    id: str
    title: str
    type: str
    description: str
    potential_revenue: str
    investment_required: str
    time_to_market: str
    feasibility_score: float = Field(..., ge=0, le=1)
    alignment_with_current_business: float = Field(..., ge=0, le=1)
    key_advantages: List[str] = Field(default_factory=list)
    implementation_steps: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    success_probability: float = Field(..., ge=0, le=1)


class PartnershipOpportunity(BaseModel):
    """Partnership opportunity"""
    id: str
    title: str
    type: str
    partner_type: str
    potential_benefits: List[str] = Field(default_factory=list)
    required_commitment: str
    estimated_value: str
    alignment_score: float = Field(..., ge=0, le=1)


class MarketExpansion(BaseModel):
    """Market expansion opportunity"""
    id: str
    title: str
    type: str
    target_market: str
    market_size: str
    growth_rate: str
    entry_strategy: str
    required_investments: List[str] = Field(default_factory=list)
    competitive_advantage: str
    timeline: str
    potential_revenue: str


class InnovationSuggestion(BaseModel):
    """Innovation suggestion"""
    id: str
    title: str
    type: str
    description: str
    development_effort: str
    potential_impact: str
    required_resources: List[str] = Field(default_factory=list)
    competitive_advantage: str


class PrioritizedRecommendation(BaseModel):
    """Prioritized recommendation"""
    rank: int = Field(..., ge=1)
    suggestion_id: str
    reason: str
    expected_value: str


class BusinessSuggestionsData(BaseModel):
    """Complete business suggestions data"""
    new_opportunities: List[NewOpportunity] = Field(default_factory=list)
    partnership_opportunities: List[PartnershipOpportunity] = Field(default_factory=list)
    market_expansions: List[MarketExpansion] = Field(default_factory=list)
    innovation_suggestions: List[InnovationSuggestion] = Field(default_factory=list)
    prioritized_recommendations: List[PrioritizedRecommendation] = Field(default_factory=list)


class SuggestionCreate(BaseModel):
    """Schema for creating a suggestion"""
    suggestion_type: SuggestionType = Field(..., description="Type of suggestion")
    title: str = Field(..., description="Suggestion title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Suggestion description")
    potential_value: Optional[float] = Field(None, ge=0, description="Estimated value")
    feasibility_score: Optional[float] = Field(None, ge=0, le=1, description="Feasibility score (0-1)")
    suggestion_data: Optional[Dict[str, Any]] = Field(None, description="Detailed suggestion data")
    status: SuggestionStatus = Field(SuggestionStatus.SUGGESTED, description="Suggestion status")


class SuggestionUpdate(BaseModel):
    """Schema for updating a suggestion"""
    title: Optional[str] = Field(None, description="Suggestion title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Suggestion description")
    potential_value: Optional[float] = Field(None, ge=0, description="Estimated value")
    feasibility_score: Optional[float] = Field(None, ge=0, le=1, description="Feasibility score (0-1)")
    status: Optional[SuggestionStatus] = Field(None, description="Suggestion status")
    suggestion_data: Optional[Dict[str, Any]] = Field(None, description="Detailed suggestion data")


class SuggestionResponse(BaseModel):
    """Schema for suggestion response"""
    id: str
    business_profile_id: str
    suggestion_type: str
    title: str
    description: Optional[str] = None
    potential_value: Optional[float] = None
    feasibility_score: Optional[float] = None
    status: Optional[str] = None
    suggestion_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SuggestionListResponse(BaseModel):
    """Schema for suggestion list response"""
    suggestions: List[SuggestionResponse]
    total: int


class SuggestionStatistics(BaseModel):
    """Schema for suggestion statistics"""
    total_suggestions: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    total_potential_value: float
    average_feasibility: float
