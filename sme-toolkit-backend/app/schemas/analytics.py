"""Analytics-related Pydantic schemas"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class MetricData(BaseModel):
    """Metric data point"""
    value: Optional[float] = None
    recorded_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class MetricHistory(BaseModel):
    """Metric history"""
    current_value: Optional[float] = None
    unit: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    history: List[MetricData] = Field(default_factory=list)


class TrendAnalysis(BaseModel):
    """Trend analysis result"""
    metric: str
    time_range: str
    historical_data: List[Dict[str, Any]] = Field(default_factory=list)
    trend: str = Field(..., description="Trend direction: improving, stable, declining")
    change: float
    change_percentage: float
    insights: List[str] = Field(default_factory=list)


class BenchmarkData(BaseModel):
    """Benchmark data"""
    industry_average: float
    top_quartile: float
    median: float
    bottom_quartile: float


class BenchmarksResponse(BaseModel):
    """Schema for benchmarks response"""
    industry: str
    metrics: Dict[str, BenchmarkData]
    generated_at: datetime


class ComparisonData(BaseModel):
    """Comparison with benchmarks"""
    current_value: float
    industry_average: float
    difference: float
    difference_percentage: float
    performance: str = Field(..., description="Performance level: top_quartile, above_average, below_average, bottom_quartile")
    percentile: float


class ComparisonResponse(BaseModel):
    """Schema for comparison response"""
    business_profile_id: str
    industry: str
    comparisons: Dict[str, ComparisonData]
    generated_at: datetime


class DashboardData(BaseModel):
    """Dashboard data"""
    business_profile_id: str
    time_range: str
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    trends: Dict[str, Optional[TrendAnalysis]] = Field(default_factory=dict)
    generated_at: datetime


class TrendDirection(str, Enum):
    """Trend direction enum"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    NO_DATA = "no_data"
    INSUFFICIENT_DATA = "insufficient_data"


class InsightType(str, Enum):
    """Insight type enum"""
    SUCCESS = "success"
    WARNING = "warning"
    ALERT = "alert"
    INFO = "info"


class Insight(BaseModel):
    """Actionable insight"""
    type: InsightType = Field(..., description="Type of insight")
    metric: str = Field(..., description="Metric insight is about")
    message: str = Field(..., description="Insight message")
    priority: str = Field(..., description="Priority level: high, medium, low")
    action: str = Field(..., description="Recommended action")


class InsightsResponse(BaseModel):
    """Schema for insights response"""
    business_profile_id: str
    insights: List[Insight]
    generated_at: datetime


class MetricHistoryResponse(BaseModel):
    """Schema for metric history response"""
    metric_type: str
    business_profile_id: str
    start_date: str
    end_date: str
    history: List[Dict[str, Any]]


class MetricRecord(BaseModel):
    """Schema for recording a metric"""
    metric_name: str = Field(..., description="Name of metric")
    metric_value: float = Field(..., description="Value of metric")
    metric_unit: Optional[str] = Field(None, description="Unit of measurement")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MetricsRequest(BaseModel):
    """Schema for requesting metrics"""
    metric_names: List[str] = Field(..., description="List of metric names to collect")
    time_range: str = Field("30d", description="Time range for historical data")


class TrendRequest(BaseModel):
    """Schema for trend analysis request"""
    metric_name: str = Field(..., description="Name of metric to analyze")
    time_range: str = Field("90d", description="Time range for analysis")


class DashboardRequest(BaseModel):
    """Schema for dashboard data request"""
    time_range: str = Field("30d", description="Time range for dashboard data")


class BenchmarkRequest(BaseModel):
    """Schema for benchmark request"""
    industry: Optional[str] = Field(None, description="Industry to benchmark against")
