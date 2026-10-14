"""Growth plan-related Pydantic schemas"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class GrowthOpportunity(BaseModel):
    """Growth opportunity"""
    id: str
    title: str
    type: str = Field(..., description="Type of opportunity")
    potential_revenue_impact: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    required_investment: Optional[str] = None
    expected_roi: Optional[str] = None
    time_to_market: Optional[str] = None
    key_actions: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    mitigation_strategies: List[str] = Field(default_factory=list)


class GrowthChannel(BaseModel):
    """Growth channel"""
    channel: str
    priority: str
    expected_impact: Optional[str] = None
    budget_allocation: Optional[str] = None
    tactics: List[str] = Field(default_factory=list)


class ImplementationPhase(BaseModel):
    """Implementation phase"""
    phase: str
    duration: str
    objectives: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)


class ResourceRequirement(BaseModel):
    """Resource requirement"""
    team: List[str] = Field(default_factory=list)
    budget: Optional[str] = None
    tools: List[str] = Field(default_factory=list)


class KPITarget(BaseModel):
    """KPI target"""
    revenue_growth: Optional[str] = None
    customer_acquisition: Optional[str] = None
    market_penetration: Optional[str] = None


class RiskAssessment(BaseModel):
    """Risk assessment"""
    high_risks: List[Dict[str, Any]] = Field(default_factory=list)


class GrowthPlanData(BaseModel):
    """Complete growth plan data"""
    plan_id: str
    title: str
    timeframe: str
    overall_growth_potential: Optional[float] = Field(None, ge=0, le=1)
    growth_opportunities: List[GrowthOpportunity] = Field(default_factory=list)
    growth_channels: List[GrowthChannel] = Field(default_factory=list)
    implementation_roadmap: List[ImplementationPhase] = Field(default_factory=list)
    resource_requirements: Optional[ResourceRequirement] = None
    kpi_targets: Optional[KPITarget] = None
    risk_assessment: Optional[RiskAssessment] = None


class GrowthPlanCreate(BaseModel):
    """Schema for creating a growth plan"""
    title: str = Field(..., description="Plan title", min_length=1, max_length=255)
    timeframe: Optional[str] = Field(None, description="Plan timeframe (e.g., '6 months', '1 year')")
    plan_data: GrowthPlanData = Field(..., description="Complete growth plan data")
    status: str = Field("draft", description="Plan status")


class GrowthPlanUpdate(BaseModel):
    """Schema for updating a growth plan"""
    title: Optional[str] = Field(None, description="Plan title", min_length=1, max_length=255)
    timeframe: Optional[str] = Field(None, description="Plan timeframe")
    plan_data: Optional[GrowthPlanData] = Field(None, description="Complete growth plan data")
    status: Optional[str] = Field(None, description="Plan status")


class GrowthPlanResponse(BaseModel):
    """Schema for growth plan response"""
    id: str
    business_profile_id: str
    title: str
    timeframe: Optional[str] = None
    plan_data: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GrowthPlanListResponse(BaseModel):
    """Schema for growth plan list response"""
    plans: List[GrowthPlanResponse]
    total: int
