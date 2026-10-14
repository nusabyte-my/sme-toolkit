"""Scoring-related Pydantic schemas"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ScoreType(str, Enum):
    BUSINESS_HEALTH = "business_health"
    GROWTH_POTENTIAL = "growth_potential"
    FINANCIAL_STABILITY = "financial_stability"
    MARKET_POSITION = "market_position"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    INNOVATION_READINESS = "innovation_readiness"


class SubMetric(BaseModel):
    """Sub-metric with factors"""
    score: float = Field(..., ge=0, le=100)
    weight: float = Field(..., ge=0, le=1)
    factors: List[str] = Field(default_factory=list)


class ScoreData(BaseModel):
    """Complete score data"""
    overall_score: float = Field(..., ge=0, le=100)
    sub_metrics: Dict[str, SubMetric]
    interpretation: str


class ScoreResponse(BaseModel):
    """Schema for score response"""
    id: str
    business_profile_id: str
    score_type: str
    overall_score: float
    sub_metrics: Dict[str, Any]
    calculated_at: datetime

    class Config:
        from_attributes = True


class ScoreHistoryItem(BaseModel):
    """Score history item"""
    id: str
    overall_score: float
    sub_metrics: Dict[str, Any]
    calculated_at: datetime


class ScoreHistoryResponse(BaseModel):
    """Schema for score history response"""
    score_type: str
    history: List[ScoreHistoryItem]
    total: int


class AllScoresResponse(BaseModel):
    """Schema for all scores response"""
    business_profile_id: str
    scores: Dict[str, Optional[Dict[str, Any]]]
    generated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ScoreRecalculateRequest(BaseModel):
    """Schema for score recalculation request"""
    score_types: Optional[List[ScoreType]] = Field(None, description="Specific score types to recalculate (all if not provided)")


class ScoreComparison(BaseModel):
    """Score comparison data"""
    current_score: float
    previous_score: Optional[float] = None
    change: Optional[float] = None
    change_percentage: Optional[float] = None
    trend: str = Field(..., description="Trend: improving, stable, declining")


class ScoreTrendResponse(BaseModel):
    """Schema for score trend response"""
    score_type: str
    current_score: float
    comparison: ScoreComparison
    history: List[ScoreHistoryItem] = Field(default_factory=list)


class ScoreBenchmark(BaseModel):
    """Score benchmark data"""
    industry_average: float
    top_quartile: float
    median: float
    bottom_quartile: float


class ScoreBenchmarkResponse(BaseModel):
    """Schema for score benchmark response"""
    score_type: str
    current_score: float
    benchmark: ScoreBenchmark
    percentile: float
    performance: str = Field(..., description="Performance level: top_quartile, above_average, below_average, bottom_quartile")


class ScoreTrendResponse(BaseModel):
    """Schema for score trend response"""
    score_type: str
    current_score: float
    previous_score: Optional[float] = None
    change: Optional[float] = None
    change_percentage: Optional[float] = None
    trend: str = Field(..., description="Trend: improving, stable, declining")
    forecast: List[float] = Field(default_factory=list, description="Forecasted values")
    data_points: int = Field(..., description="Number of data points used")


class ScoreComparisonResponse(BaseModel):
    """Schema for score comparison response"""
    business_profile_id: str
    industry: str
    business_size: str
    comparisons: Dict[str, Dict[str, Any]]
