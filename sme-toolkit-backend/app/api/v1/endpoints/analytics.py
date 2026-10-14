"""Analytics API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    MetricsRequest,
    TrendRequest,
    DashboardRequest,
    BenchmarkRequest,
    DashboardData,
    TrendAnalysis,
    BenchmarksResponse,
    ComparisonResponse,
    MetricRecord
)

router = APIRouter(tags=["Analytics"])


@router.get("/insights", response_model=list)
async def get_insights(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get actionable insights from analytics data.
    
    Returns list of insights with priorities and actions.
    """
    try:
        service = AnalyticsService(db)
        insights = await service.generate_insights(business_profile_id)
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating insights: {str(e)}"
        )


@router.get("/history/{metric_type}")
async def get_metric_history(
    metric_type: str,
    business_profile_id: str = Query(..., description="Business profile ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical metric data for a date range.
    
    Returns historical metric records.
    """
    try:
        from datetime import datetime as dt
        
        service = AnalyticsService(db)
        
        # Default to last 90 days if no dates provided
        if not start_date or not end_date:
            from datetime import timedelta
            end = dt.utcnow()
            start = end - timedelta(days=90)
        else:
            start = dt.strptime(start_date, "%Y-%m-%d").date()
            end = dt.strptime(end_date, "%Y-%m-%d").date()
        
        history = await service.get_metric_history(
            business_profile_id,
            metric_type,
            start,
            end
        )
        return {
            "metric_type": metric_type,
            "business_profile_id": business_profile_id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "history": history
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metric history: {str(e)}"
        )


@router.post("/metrics", response_model=dict)
async def collect_metrics(
    request: MetricsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Collect metrics from various sources.
    
    Returns current values for specified metrics.
    
    - **metric_names**: List of metric names to collect (required)
    - **time_range**: Time range for historical data (default: 30d)
    """
    try:
        service = AnalyticsService(db)
        metrics = await service.collect_metrics(
            business_profile_id=request.business_profile_id,
            metric_names=request.metric_names
        )
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error collecting metrics: {str(e)}"
        )


@router.get("/metrics", response_model=dict)
async def get_metrics(
    business_profile_id: str = Query(..., description="Business profile ID"),
    metric_names: Optional[str] = Query(None, description="Comma-separated list of metric names"),
    time_range: str = Query("30d", description="Time range for historical data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get metrics for a business profile.
    
    Returns metrics with current and historical values.
    """
    try:
        service = AnalyticsService(db)
        
        # Parse metric names if provided
        names = metric_names.split(',') if metric_names else None
        
        metrics = await service.get_metrics(
            business_profile_id=business_profile_id,
            metric_names=names,
            time_range=time_range
        )
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metrics: {str(e)}"
        )


@router.post("/trends", response_model=TrendAnalysis)
async def analyze_trends(
    request: TrendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze trends for a specific metric.
    
    Returns trend analysis including direction, change, and insights.
    
    - **metric_name**: Name of metric to analyze (required)
    - **time_range**: Time range for analysis (default: 90d)
    """
    try:
        service = AnalyticsService(db)
        trend = await service.analyze_trends(
            business_profile_id=request.business_profile_id,
            metric_name=request.metric_name,
            time_range=request.time_range
        )
        return TrendAnalysis(**trend)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing trends: {str(e)}"
        )


@router.get("/trends/{metric_name}", response_model=TrendAnalysis)
async def get_trend(
    metric_name: str,
    business_profile_id: str = Query(..., description="Business profile ID"),
    time_range: str = Query("90d", description="Time range for analysis"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trend analysis for a specific metric.
    
    Returns trend data for the specified metric.
    """
    try:
        service = AnalyticsService(db)
        trend = await service.analyze_trends(
            business_profile_id=business_profile_id,
            metric_name=metric_name,
            time_range=time_range
        )
        return TrendAnalysis(**trend)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving trend: {str(e)}"
        )


@router.post("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    request: DashboardRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive dashboard data.
    
    Returns key metrics, trends, and analytics data.
    
    - **time_range**: Time range for dashboard data (default: 30d)
    """
    try:
        service = AnalyticsService(db)
        dashboard = await service.get_dashboard_data(
            business_profile_id=request.business_profile_id,
            time_range=request.time_range
        )
        return DashboardData(**dashboard)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard data: {str(e)}"
        )


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    business_profile_id: str = Query(..., description="Business profile ID"),
    time_range: str = Query("30d", description="Time range for dashboard data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard data for a business profile.
    
    Returns comprehensive dashboard metrics and trends.
    """
    try:
        service = AnalyticsService(db)
        dashboard = await service.get_dashboard_data(
            business_profile_id=business_profile_id,
            time_range=time_range
        )
        return DashboardData(**dashboard)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard: {str(e)}"
        )


@router.post("/benchmarks", response_model=BenchmarksResponse)
async def get_benchmarks(
    request: BenchmarkRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get industry benchmarks for comparison.
    
    Returns benchmark data for specified industry.
    
    - **industry**: Industry to benchmark against (optional, uses profile industry if not provided)
    """
    try:
        service = AnalyticsService(db)
        benchmarks = await service.get_benchmarks(
            business_profile_id=request.business_profile_id,
            industry=request.industry
        )
        return BenchmarksResponse(**benchmarks)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving benchmarks: {str(e)}"
        )


@router.get("/benchmarks", response_model=BenchmarksResponse)
async def get_benchmark(
    business_profile_id: str = Query(..., description="Business profile ID"),
    industry: Optional[str] = Query(None, description="Industry to benchmark against"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get benchmarks for a business profile.
    
    Returns industry benchmark data.
    """
    try:
        service = AnalyticsService(db)
        benchmarks = await service.get_benchmarks(
            business_profile_id=business_profile_id,
            industry=industry
        )
        return BenchmarksResponse(**benchmarks)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving benchmarks: {str(e)}"
        )


@router.post("/compare", response_model=ComparisonResponse)
async def compare_with_benchmarks(
    request: BenchmarkRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare business metrics with industry benchmarks.
    
    Returns comparison data showing performance relative to benchmarks.
    
    - **industry**: Industry to benchmark against (optional)
    """
    try:
        service = AnalyticsService(db)
        comparison = await service.compare_with_benchmarks(
            business_profile_id=request.business_profile_id,
            industry=request.industry
        )
        return ComparisonResponse(**comparison)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing with benchmarks: {str(e)}"
        )


@router.get("/compare", response_model=ComparisonResponse)
async def get_comparison(
    business_profile_id: str = Query(..., description="Business profile ID"),
    industry: Optional[str] = Query(None, description="Industry to benchmark against"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get benchmark comparison for a business profile.
    
    Returns comparison data with industry benchmarks.
    """
    try:
        service = AnalyticsService(db)
        comparison = await service.compare_with_benchmarks(
            business_profile_id=business_profile_id,
            industry=industry
        )
        return ComparisonResponse(**comparison)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving comparison: {str(e)}"
        )


@router.post("/record", status_code=status.HTTP_201_CREATED)
async def record_metric(
    request: MetricRecord,
    db: AsyncSession = Depends(get_db)
):
    """
    Record a metric value.
    
    Manually records a metric value for tracking.
    
    - **metric_name**: Name of metric (required)
    - **metric_value**: Value of metric (required)
    - **metric_unit**: Unit of measurement (optional)
    - **metadata**: Additional metadata (optional)
    """
    try:
        service = AnalyticsService(db)
        metric_id = await service.record_metric(
            business_profile_id=request.business_profile_id,
            metric_name=request.metric_name,
            metric_value=request.metric_value,
            metric_unit=request.metric_unit,
            metadata=request.metadata
        )
        return {"id": metric_id, "message": "Metric recorded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording metric: {str(e)}"
        )
