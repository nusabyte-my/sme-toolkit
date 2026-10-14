"""Schemas for Ideation API - Robust ideation workflow with templates"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class IdeationRequest(BaseModel):
    """Request for ideation generation"""
    action: Literal["brainstorm", "analyze_trends", "competitive_analysis", "market_opportunity", "product_innovation", "business_model_innovation"] = Field(
        "brainstorm", description="Ideation type"
    )
    topic: str = Field(..., description="Main topic or problem statement")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context (BMC data, market info, etc.)")
    template: Optional[Literal["scamper", "mind_map", "swot", "blue_ocean", "lean_startup", "design_thinking", "first_principles", "reverse_engineering"]] = Field(
        None, description="Ideation template/framework to use"
    )
    industry: Optional[str] = Field(None, description="Industry for context-specific ideas")
    target_audience: Optional[str] = Field(None, description="Target audience/customer segment")
    constraints: Optional[List[str]] = Field(None, description="Constraints to consider")
    innovation_level: Optional[Literal["incremental", "disruptive", "radical"]] = Field("incremental", description="Level of innovation desired")
    quantity: int = Field(10, description="Number of ideas to generate", ge=1, le=50)
    enhance: bool = Field(False, description="Whether to enhance ideas with AI analysis")


class Idea(BaseModel):
    """Single idea model"""
    id: str = Field(..., description="Unique idea identifier")
    title: str = Field(..., description="Idea title")
    description: str = Field(..., description="Detailed idea description")
    category: str = Field(..., description="Idea category")
    impact: Literal["high", "medium", "low"] = Field(..., description="Expected impact")
    effort: Literal["high", "medium", "low"] = Field(..., description="Implementation effort")
    innovation_type: Literal["incremental", "disruptive", "radical"] = Field(..., description="Type of innovation")
    feasibility_score: float = Field(..., description="Feasibility score (0-100)")
    novelty_score: float = Field(..., description="Novelty score (0-100)")
    value_score: float = Field(..., description="Value score (0-100)")
    tags: List[str] = Field(default_factory=list, description="Idea tags")
    implementation_steps: Optional[List[str]] = Field(None, description="Implementation steps")
    risks: Optional[List[str]] = Field(None, description="Potential risks")
    metrics: Optional[List[str]] = Field(None, description="Success metrics")


class TrendAnalysis(BaseModel):
    """Trend analysis model"""
    trend: str = Field(..., description="Trend name")
    description: str = Field(..., description="Trend description")
    relevance_score: float = Field(..., description="Relevance to topic (0-100)")
    opportunities: List[str] = Field(default_factory=list, description="Opportunities from this trend")
    threats: List[str] = Field(default_factory=list, description="Threats from this trend")
    timeframe: Literal["emerging", "growing", "mature", "declining"] = Field(..., description="Trend maturity")


class CompetitorAnalysis(BaseModel):
    """Competitor analysis model"""
    competitor: str = Field(..., description="Competitor name")
    strengths: List[str] = Field(default_factory=list, description="Competitor strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Competitor weaknesses")
    strategies: List[str] = Field(default_factory=list, description="Strategies to differentiate")
    opportunities: List[str] = Field(default_factory=list, description="Opportunities to exploit")


class MarketOpportunity(BaseModel):
    """Market opportunity model"""
    opportunity: str = Field(..., description="Opportunity description")
    market_size: str = Field(..., description="Estimated market size")
    growth_rate: str = Field(..., description="Growth rate")
    competition_level: Literal["low", "medium", "high"] = Field(..., description="Competition level")
    barriers_to_entry: List[str] = Field(default_factory=list, description="Barriers to entry")
    success_factors: List[str] = Field(default_factory=list, description="Success factors")


class IdeationResponse(BaseModel):
    """Response for ideation generation"""
    success: bool = Field(..., description="Whether ideation was successful")
    action: str = Field(..., description="Action performed")
    ideas: Optional[List[Idea]] = Field(None, description="Generated ideas")
    trend_analysis: Optional[List[TrendAnalysis]] = Field(None, description="Trend analysis results")
    competitor_analysis: Optional[List[CompetitorAnalysis]] = Field(None, description="Competitor analysis results")
    market_opportunities: Optional[List[MarketOpportunity]] = Field(None, description="Market opportunities")
    insights: Optional[List[str]] = Field(None, description="Key insights")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations")
    template_used: Optional[str] = Field(None, description="Template used for ideation")
    error: Optional[str] = Field(None, description="Error message if failed")


class TemplateOption(BaseModel):
    """Template option model"""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    best_for: List[str] = Field(..., description="Best use cases")


class ActionOption(BaseModel):
    """Action option model"""
    name: str = Field(..., description="Action name")
    description: str = Field(..., description="Action description")


class InnovationLevelOption(BaseModel):
    """Innovation level option model"""
    name: Literal["incremental", "disruptive", "radical"] = Field(..., description="Innovation level name")
    description: str = Field(..., description="Innovation level description")
    examples: List[str] = Field(..., description="Examples of this level")


class IdeationOptionsResponse(BaseModel):
    """Response containing available ideation options"""
    actions: List[ActionOption] = Field(..., description="Available ideation actions")
    templates: List[TemplateOption] = Field(..., description="Available ideation templates")
    innovation_levels: List[InnovationLevelOption] = Field(..., description="Available innovation levels")


class TemplateCategoryCreate(BaseModel):
    """Request to create a template category"""
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, description="Category color (hex)")
    icon: Optional[str] = Field(None, description="Category icon name")


class TemplateCategoryUpdate(BaseModel):
    """Request to update a template category"""
    name: Optional[str] = Field(None, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, description="Category color (hex)")
    icon: Optional[str] = Field(None, description="Category icon name")


class TemplateCategoryResponse(BaseModel):
    """Response for template category"""
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, description="Category color")
    icon: Optional[str] = Field(None, description="Category icon")
    is_default: bool = Field(..., description="Whether this is a default category")
    template_count: int = Field(..., description="Number of templates in this category")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class IdeationTemplateCreate(BaseModel):
    """Request to create a custom ideation template"""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    framework: str = Field(..., description="Framework name")
    instructions: str = Field(..., description="Framework instructions")
    prompt_template: str = Field(..., description="Prompt template with placeholders")
    custom_instructions: Optional[str] = Field(None, description="Additional custom instructions")
    category_id: Optional[str] = Field(None, description="Category ID")
    is_public: bool = Field(False, description="Whether template is public")
    tags: Optional[List[str]] = Field(None, description="Template tags")


class IdeationTemplateUpdate(BaseModel):
    """Request to update a custom ideation template"""
    name: Optional[str] = Field(None, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    framework: Optional[str] = Field(None, description="Framework name")
    instructions: Optional[str] = Field(None, description="Framework instructions")
    prompt_template: Optional[str] = Field(None, description="Prompt template with placeholders")
    custom_instructions: Optional[str] = Field(None, description="Additional custom instructions")
    category_id: Optional[str] = Field(None, description="Category ID")
    is_public: Optional[bool] = Field(None, description="Whether template is public")
    tags: Optional[List[str]] = Field(None, description="Template tags")


class IdeationTemplateResponse(BaseModel):
    """Response for ideation template"""
    id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    framework: str = Field(..., description="Framework name")
    instructions: str = Field(..., description="Framework instructions")
    prompt_template: str = Field(..., description="Prompt template")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions")
    category_id: Optional[str] = Field(None, description="Category ID")
    is_public: bool = Field(..., description="Whether template is public")
    is_default: bool = Field(..., description="Whether this is a default template")
    tags: Optional[List[str]] = Field(None, description="Template tags")
    usage_count: int = Field(..., description="Number of times used")
    rating: Optional[float] = Field(None, description="Average rating")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class IdeationSessionResponse(BaseModel):
    """Response for ideation session"""
    id: str = Field(..., description="Session ID")
    action: str = Field(..., description="Action performed")
    topic: str = Field(..., description="Topic")
    template_name: Optional[str] = Field(None, description="Template used")
    innovation_level: str = Field(..., description="Innovation level")
    quantity: int = Field(..., description="Number of ideas requested")
    enhance_enabled: bool = Field(..., description="Whether enhancement was enabled")
    status: str = Field(..., description="Session status")
    ideas_count: int = Field(..., description="Number of ideas generated")
    insights_count: int = Field(..., description="Number of insights")
    recommendations_count: int = Field(..., description="Number of recommendations")
    started_at: str = Field(..., description="Start timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds")


class IdeationResultResponse(BaseModel):
    """Response for ideation result"""
    id: str = Field(..., description="Result ID")
    session_id: str = Field(..., description="Session ID")
    title: str = Field(..., description="Idea title")
    description: str = Field(..., description="Idea description")
    category: Optional[str] = Field(None, description="Idea category")
    impact: str = Field(..., description="Impact level")
    effort: str = Field(..., description="Effort level")
    innovation_type: str = Field(..., description="Innovation type")
    feasibility_score: int = Field(..., description="Feasibility score (0-100)")
    novelty_score: int = Field(..., description="Novelty score (0-100)")
    value_score: int = Field(..., description="Value score (0-100)")
    overall_score: int = Field(..., description="Overall score (0-100)")
    tags: Optional[List[str]] = Field(None, description="Idea tags")
    implementation_steps: Optional[List[str]] = Field(None, description="Implementation steps")
    risks: Optional[List[str]] = Field(None, description="Potential risks")
    metrics: Optional[List[str]] = Field(None, description="Success metrics")
    is_favorite: bool = Field(..., description="Whether marked as favorite")
    notes: Optional[str] = Field(None, description="User notes")
    created_at: str = Field(..., description="Creation timestamp")
