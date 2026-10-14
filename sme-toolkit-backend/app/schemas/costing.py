"""Costing analysis-related Pydantic schemas"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CostBreakdown(BaseModel):
    """Cost breakdown item"""
    category: str
    amount: str
    percentage: float = Field(..., ge=0, le=100)


class FixedCosts(BaseModel):
    """Fixed costs breakdown"""
    total: str
    breakdown: List[CostBreakdown] = Field(default_factory=list)


class VariableCosts(BaseModel):
    """Variable costs breakdown"""
    total: str
    breakdown: List[CostBreakdown] = Field(default_factory=list)


class CostStructure(BaseModel):
    """Complete cost structure"""
    fixed_costs: FixedCosts
    variable_costs: VariableCosts
    total_monthly_cost: str
    cost_per_unit: str


class PricingStrategy(BaseModel):
    """Pricing strategy"""
    strategy: str
    recommended_price: str
    rationale: str
    expected_margin: str
    market_position: str
    target_customers: str


class OptimizationOpportunity(BaseModel):
    """Cost optimization opportunity"""
    area: str
    current_cost: str
    potential_savings: str
    savings_percentage: float = Field(..., ge=0, le=100)
    actions: List[str] = Field(default_factory=list)
    implementation_effort: str
    time_to_impact: str


class BreakEvenAnalysis(BaseModel):
    """Break-even analysis"""
    current_price: str
    break_even_units: int = Field(..., ge=0)
    break_even_revenue: str
    margin_of_safety: str
    sensitivity_analysis: Dict[str, Any] = Field(default_factory=dict)


class CostBenchmarks(BaseModel):
    """Cost benchmarks"""
    industry_average: Dict[str, Any]
    your_business: Dict[str, Any]
    performance: str


class CostingAnalysisData(BaseModel):
    """Complete costing analysis data"""
    current_cost_structure: CostStructure
    pricing_strategies: List[PricingStrategy] = Field(default_factory=list)
    optimization_opportunities: List[OptimizationOpportunity] = Field(default_factory=list)
    break_even_analysis: Optional[BreakEvenAnalysis] = None
    cost_benchmarks: Optional[CostBenchmarks] = None


class CostingAnalysisCreate(BaseModel):
    """Schema for creating a costing analysis"""
    cost_structure: CostStructure = Field(..., description="Fixed and variable costs breakdown")
    pricing_strategies: Optional[List[PricingStrategy]] = Field(None, description="Pricing recommendations")
    optimization_opportunities: Optional[List[OptimizationOpportunity]] = Field(None, description="Cost-saving opportunities")
    break_even_analysis: Optional[BreakEvenAnalysis] = Field(None, description="Break-even calculations")


class CostingAnalysisResponse(BaseModel):
    """Schema for costing analysis response"""
    id: str
    business_profile_id: str
    analysis_date: datetime
    cost_structure: Dict[str, Any]
    pricing_strategies: Optional[List[Dict[str, Any]]] = None
    optimization_opportunities: Optional[List[Dict[str, Any]]] = None
    break_even_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CostingAnalysisListResponse(BaseModel):
    """Schema for costing analysis list response"""
    analyses: List[CostingAnalysisResponse]
    total: int


class CostSummary(BaseModel):
    """Schema for cost summary"""
    has_analysis: bool
    analysis_id: Optional[str] = None
    analysis_date: Optional[datetime] = None
    total_monthly_cost: float = 0
    fixed_costs: Dict[str, Any] = Field(default_factory=dict)
    variable_costs: Dict[str, Any] = Field(default_factory=dict)
    cost_per_unit: float = 0
    pricing_strategies_count: int = 0
    optimization_opportunities_count: int = 0
