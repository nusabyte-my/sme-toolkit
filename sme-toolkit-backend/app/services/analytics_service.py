"""Analytics Service - Manage analytics data and calculations"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import (
    BusinessProfile,
    AnalyticsMetric,
    CompanyGoal,
    GrowthScoreRecord
)
from app.utils.trend_analysis import TrendAnalyzer
from app.data.benchmarks import get_benchmarks, get_metric_benchmarks

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for collecting, processing, and analyzing business metrics.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def collect_metrics(
        self,
        business_profile_id: str,
        metric_names: List[str]
    ) -> Dict[str, Any]:
        """
        Collect metrics from various sources.
        
        Args:
            business_profile_id: ID of business profile
            metric_names: List of metric names to collect
            
        Returns:
            Dictionary of metric values
        """
        metrics = {}
        
        for metric_name in metric_names:
            try:
                value = await self._collect_metric(business_profile_id, metric_name)
                metrics[metric_name] = value
                logger.info(f"Collected metric {metric_name}: {value}")
            except Exception as e:
                logger.error(f"Error collecting metric {metric_name}: {e}")
                metrics[metric_name] = None

        return metrics

    async def _collect_metric(
        self,
        business_profile_id: str,
        metric_name: str
    ) -> Optional[float]:
        """
        Collect a specific metric from data sources.
        
        Args:
            business_profile_id: ID of business profile
            metric_name: Name of metric to collect
            
        Returns:
            Metric value or None
        """
        # Load profile with related data
        result = await self.db.execute(
            select(BusinessProfile)
            .options(
                selectinload(BusinessProfile.goals),
                selectinload(BusinessProfile.growth_scores)
            )
            .where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            return None

        # Calculate metric based on type
        if metric_name == "goal_completion_rate":
            return await self._calculate_goal_completion_rate(profile)
        elif metric_name == "average_growth_score":
            return await self._calculate_average_growth_score(profile)
        elif metric_name == "total_goals":
            return len(profile.goals)
        elif metric_name == "active_goals":
            return len([g for g in profile.goals if g.status.value == "active"])
        elif metric_name == "completed_goals":
            return len([g for g in profile.goals if g.status.value == "completed"])
        elif metric_name == "revenue_growth":
            return await self._calculate_revenue_growth(profile)
        elif metric_name == "profitability":
            return await self._calculate_profitability(profile)
        elif metric_name == "customer_satisfaction":
            return await self._calculate_customer_satisfaction(profile)
        elif metric_name == "market_share":
            return await self._calculate_market_share(profile)
        elif metric_name == "operational_efficiency":
            return await self._calculate_operational_efficiency(profile)
        elif metric_name == "innovation_index":
            return await self._calculate_innovation_index(profile)
        else:
            # Try to get from BMC data
            return await self._get_metric_from_bmc(profile, metric_name)

    async def _calculate_goal_completion_rate(self, profile: BusinessProfile) -> float:
        """Calculate goal completion rate"""
        if not profile.goals:
            return 0.0

        total_progress = sum(goal.progress for goal in profile.goals)
        return round(total_progress / len(profile.goals), 2)

    async def _calculate_average_growth_score(self, profile: BusinessProfile) -> float:
        """Calculate average growth score"""
        if not profile.growth_scores:
            return 0.0

        total_score = sum(score.overall_score for score in profile.growth_scores)
        return round(total_score / len(profile.growth_scores), 2)

    async def _calculate_revenue_growth(self, profile: BusinessProfile) -> float:
        """Calculate revenue growth from BMC data"""
        bmc_data = profile.bmc_data or {}
        financials = bmc_data.get("financials", {})
        return financials.get("revenue_growth", 0.0)

    async def _calculate_profitability(self, profile: BusinessProfile) -> float:
        """Calculate profitability from BMC data"""
        bmc_data = profile.bmc_data or {}
        financials = bmc_data.get("financials", {})
        return financials.get("profitability", 0.0)

    async def _calculate_customer_satisfaction(self, profile: BusinessProfile) -> float:
        """Calculate customer satisfaction from BMC data"""
        bmc_data = profile.bmc_data or {}
        customer = bmc_data.get("customer", {})
        return customer.get("satisfaction", 50.0)

    async def _calculate_market_share(self, profile: BusinessProfile) -> float:
        """Calculate market share from BMC data"""
        bmc_data = profile.bmc_data or {}
        market = bmc_data.get("market", {})
        return market.get("market_share", 0.0)

    async def _calculate_operational_efficiency(self, profile: BusinessProfile) -> float:
        """Calculate operational efficiency from BMC data"""
        bmc_data = profile.bmc_data or {}
        operations = bmc_data.get("operations", {})
        return operations.get("efficiency", 50.0)

    async def _calculate_innovation_index(self, profile: BusinessProfile) -> float:
        """Calculate innovation index from BMC data"""
        bmc_data = profile.bmc_data or {}
        innovation = bmc_data.get("innovation", {})
        return innovation.get("index", 50.0)

    async def _get_metric_from_bmc(self, profile: BusinessProfile, metric_name: str) -> Optional[float]:
        """Get metric value from BMC data"""
        bmc_data = profile.bmc_data or {}
        
        # Flatten BMC data to find metric
        for section in bmc_data.values():
            if isinstance(section, dict) and metric_name in section:
                return section[metric_name]
        
        return None

    async def record_metric(
        self,
        business_profile_id: str,
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a metric value.
        
        Args:
            business_profile_id: ID of business profile
            metric_name: Name of metric
            metric_value: Value of metric
            metric_unit: Unit of measurement (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            ID of recorded metric
        """
        metric = AnalyticsMetric(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
            metric_metadata=metadata,
            recorded_at=datetime.utcnow()
        )

        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)

        logger.info(f"Recorded metric {metric_name} = {metric_value} for profile {business_profile_id}")
        return metric.id

    async def get_metrics(
        self,
        business_profile_id: str,
        metric_names: Optional[List[str]] = None,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get metrics for a business profile.
        
        Args:
            business_profile_id: ID of business profile
            metric_names: List of metric names (optional, returns all if None)
            time_range: Time range for historical data (e.g., "30d", "90d")
            
        Returns:
            Dictionary of metrics with current and historical values
        """
        # Calculate date range
        days = int(time_range.rstrip('d'))
        start_date = datetime.utcnow() - timedelta(days=days)

        # Build query
        query = select(AnalyticsMetric).where(
            AnalyticsMetric.business_profile_id == business_profile_id
        ).where(
            AnalyticsMetric.recorded_at >= start_date
        )

        if metric_names:
            query = query.where(AnalyticsMetric.metric_name.in_(metric_names))

        query = query.order_by(AnalyticsMetric.recorded_at.desc())

        result = await self.db.execute(query)
        metrics = result.scalars().all()

        # Organize by metric name
        metrics_by_name = {}
        for metric in metrics:
            if metric.metric_name not in metrics_by_name:
                metrics_by_name[metric.metric_name] = {
                    "current_value": metric.metric_value,
                    "unit": metric.metric_unit,
                    "metadata": metric.metric_metadata,
                    "history": []
                }
            
            metrics_by_name[metric.metric_name]["history"].append({
                "value": metric.metric_value,
                "recorded_at": metric.recorded_at.isoformat()
            })

        return metrics_by_name

    async def analyze_trends(
        self,
        business_profile_id: str,
        metric_name: str,
        time_range: str = "90d"
    ) -> Dict[str, Any]:
        """
        Analyze trends for a specific metric.
        
        Args:
            business_profile_id: ID of business profile
            metric_name: Name of metric to analyze
            time_range: Time range for analysis
            
        Returns:
            Trend analysis data
        """
        # Get historical data
        days = int(time_range.rstrip('d'))
        start_date = datetime.utcnow() - timedelta(days=days)

        result = await self.db.execute(
            select(AnalyticsMetric)
            .where(AnalyticsMetric.business_profile_id == business_profile_id)
            .where(AnalyticsMetric.metric_name == metric_name)
            .where(AnalyticsMetric.recorded_at >= start_date)
            .order_by(AnalyticsMetric.recorded_at.asc())
        )
        metrics = result.scalars().all()

        if not metrics:
            return {
                "metric": metric_name,
                "time_range": time_range,
                "trend": "no_data",
                "change": 0.0,
                "change_percentage": 0.0,
                "insights": ["No historical data available"],
                "forecast": [],
                "confidence": "low"
            }

        # Calculate trend using TrendAnalyzer
        values = [m.metric_value for m in metrics if m.metric_value is not None]
        
        if len(values) < 2:
            return {
                "metric": metric_name,
                "time_range": time_range,
                "trend": "insufficient_data",
                "change": 0.0,
                "change_percentage": 0.0,
                "insights": ["Insufficient data for trend analysis"],
                "forecast": [],
                "confidence": "low"
            }

        # Use TrendAnalyzer for comprehensive analysis
        trend_analysis = TrendAnalyzer.analyze_trend(values, forecast_periods=5)
        
        # Generate insights
        insights = TrendAnalyzer.generate_insights(metric_name, trend_analysis)

        return {
            "metric": metric_name,
            "time_range": time_range,
            "historical_data": [
                {
                    "value": m.metric_value,
                    "recorded_at": m.recorded_at.isoformat()
                }
                for m in metrics
            ],
            "trend": trend_analysis["trend"],
            "change": trend_analysis["change"],
            "change_percentage": trend_analysis["change_percentage"],
            "growth_rate": trend_analysis["growth_rate"],
            "volatility": trend_analysis["volatility"],
            "forecast": trend_analysis["forecast"],
            "confidence": trend_analysis["confidence"],
            "insights": insights
        }

    async def calculate_trends(
        self,
        business_profile_id: int,
        metric_type: str,
        period: str = "90d"
    ) -> Dict[str, Any]:
        """
        Calculate trends with forecasting for a metric type.
        
        Args:
            business_profile_id: ID of business profile
            metric_type: Type of metric to analyze
            period: Time period for analysis
            
        Returns:
            Trend analysis with forecasting
        """
        return await self.analyze_trends(business_profile_id, metric_type, period)

    async def get_dashboard_data(
        self,
        business_profile_id: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data.
        
        Args:
            business_profile_id: ID of business profile
            time_range: Time range for data
            
        Returns:
            Dashboard data with key metrics and trends
        """
        # Load profile with related data
        result = await self.db.execute(
            select(BusinessProfile)
            .options(
                selectinload(BusinessProfile.goals),
                selectinload(BusinessProfile.growth_scores)
            )
            .where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Business profile {business_profile_id} not found")

        # Collect key metrics
        key_metrics = await self.collect_metrics(
            business_profile_id,
            [
                "goal_completion_rate",
                "average_growth_score",
                "total_goals",
                "active_goals",
                "completed_goals"
            ]
        )

        # Get trend data for key metrics
        trends = {}
        for metric_name in ["goal_completion_rate", "average_growth_score"]:
            try:
                trend_data = await self.analyze_trends(
                    business_profile_id,
                    metric_name,
                    time_range
                )
                trends[metric_name] = trend_data
            except Exception as e:
                logger.error(f"Error analyzing trend for {metric_name}: {e}")
                trends[metric_name] = None

        return {
            "business_profile_id": business_profile_id,
            "time_range": time_range,
            "key_metrics": key_metrics,
            "trends": trends,
            "generated_at": datetime.utcnow().isoformat()
        }

    async def get_benchmarks(
        self,
        business_profile_id: str,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get industry benchmarks for comparison.
        
        Args:
            business_profile_id: ID of business profile
            industry: Industry to benchmark against (optional)
            
        Returns:
            Benchmark data
        """
        # Load profile to get industry and business size
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Business profile {business_profile_id} not found")

        industry = industry or profile.industry or "general"
        business_size = profile.business_stage or "small"  # Use business_stage as size proxy

        # Get benchmarks from benchmark data
        benchmarks = get_benchmarks(industry, business_size)

        return {
            "industry": industry,
            "business_size": business_size,
            "metrics": benchmarks,
            "generated_at": datetime.utcnow().isoformat()
        }

    async def compare_with_benchmarks(
        self,
        business_profile_id: str,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare business metrics with industry benchmarks.
        
        Args:
            business_profile_id: ID of business profile
            industry: Industry to benchmark against (optional)
            
        Returns:
            Comparison data
        """
        # Get current metrics
        current_metrics = await self.collect_metrics(
            business_profile_id,
            [
                "goal_completion_rate",
                "average_growth_score",
                "revenue_growth",
                "profitability",
                "customer_satisfaction",
                "market_share",
                "operational_efficiency",
                "innovation_index"
            ]
        )

        # Get benchmarks
        benchmarks = await self.get_benchmarks(business_profile_id, industry)

        # Compare
        comparisons = {}
        for metric_name, current_value in current_metrics.items():
            if current_value is None:
                continue

            benchmark_data = benchmarks["metrics"].get(metric_name)
            if not benchmark_data:
                continue

            industry_avg = benchmark_data["industry_average"]
            difference = current_value - industry_avg
            difference_percentage = (difference / industry_avg * 100) if industry_avg != 0 else 0.0

            # Determine performance level
            if current_value >= benchmark_data["top_quartile"]:
                performance = "top_quartile"
            elif current_value >= benchmark_data["median"]:
                performance = "above_average"
            elif current_value >= benchmark_data["bottom_quartile"]:
                performance = "below_average"
            else:
                performance = "bottom_quartile"

            comparisons[metric_name] = {
                "current_value": current_value,
                "industry_average": industry_avg,
                "difference": round(difference, 2),
                "difference_percentage": round(difference_percentage, 2),
                "performance": performance,
                "percentile": self._calculate_percentile(current_value, benchmark_data)
            }

        return {
            "business_profile_id": business_profile_id,
            "industry": benchmarks["industry"],
            "business_size": benchmarks.get("business_size", "unknown"),
            "comparisons": comparisons,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _calculate_percentile(
        self,
        value: float,
        benchmark_data: Dict[str, float]
    ) -> float:
        """Calculate approximate percentile based on benchmark data"""
        if value >= benchmark_data["top_quartile"]:
            return 75.0 + min(25.0, ((value - benchmark_data["top_quartile"]) / (benchmark_data["top_quartile"] - benchmark_data["median"]) * 25))
        elif value >= benchmark_data["median"]:
            return 50.0 + ((value - benchmark_data["median"]) / (benchmark_data["top_quartile"] - benchmark_data["median"]) * 25)
        elif value >= benchmark_data["bottom_quartile"]:
            return 25.0 + ((value - benchmark_data["bottom_quartile"]) / (benchmark_data["median"] - benchmark_data["bottom_quartile"]) * 25)
        else:
            return max(0.0, (value / benchmark_data["bottom_quartile"]) * 25)

    async def delete_old_metrics(
        self,
        business_profile_id: str,
        days_to_keep: int = 365
    ) -> int:
        """
        Delete old metrics beyond retention period.
        
        Args:
            business_profile_id: ID of business profile
            days_to_keep: Number of days to keep
            
        Returns:
            Number of metrics deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        result = await self.db.execute(
            select(AnalyticsMetric)
            .where(AnalyticsMetric.business_profile_id == business_profile_id)
            .where(AnalyticsMetric.recorded_at < cutoff_date)
        )
        old_metrics = result.scalars().all()

        count = len(old_metrics)
        for metric in old_metrics:
            await self.db.delete(metric)

        await self.db.commit()

        logger.info(f"Deleted {count} old metrics for profile {business_profile_id}")
        return count

    async def generate_insights(
        self,
        business_profile_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable insights from analytics data.
        
        Args:
            business_profile_id: ID of business profile
            
        Returns:
            List of actionable insights
        """
        insights = []
        
        # Get current metrics
        metrics = await self.collect_metrics(
            business_profile_id,
            [
                "goal_completion_rate",
                "average_growth_score",
                "revenue_growth",
                "profitability",
                "customer_satisfaction"
            ]
        )
        
        # Get trend analysis for key metrics
        for metric_name, value in metrics.items():
            if value is None:
                continue
            
            try:
                trend_data = await self.analyze_trends(
                    business_profile_id,
                    metric_name,
                    "90d"
                )
                
                # Generate insight based on trend
                if trend_data["trend"] == "declining":
                    insights.append({
                        "type": "warning",
                        "metric": metric_name,
                        "message": f"{metric_name} is declining by {abs(trend_data['change_percentage']):.1f}%",
                        "priority": "high" if abs(trend_data['change_percentage']) > 20 else "medium",
                        "action": f"Review {metric_name} strategies and implement corrective actions"
                    })
                elif trend_data["trend"] == "improving":
                    insights.append({
                        "type": "success",
                        "metric": metric_name,
                        "message": f"{metric_name} is improving by {trend_data['change_percentage']:.1f}%",
                        "priority": "low",
                        "action": "Continue current strategies to maintain positive trend"
                    })
            except Exception as e:
                logger.error(f"Error generating insight for {metric_name}: {e}")
        
        # Get benchmark comparison
        try:
            comparison = await self.compare_with_benchmarks(business_profile_id)
            
            for metric_name, comp_data in comparison["comparisons"].items():
                if comp_data["performance"] == "bottom_quartile":
                    insights.append({
                        "type": "alert",
                        "metric": metric_name,
                        "message": f"{metric_name} is in bottom quartile compared to industry",
                        "priority": "high",
                        "action": f"Focus on improving {metric_name} to reach industry average"
                    })
                elif comp_data["performance"] == "below_average":
                    insights.append({
                        "type": "warning",
                        "metric": metric_name,
                        "message": f"{metric_name} is below industry average",
                        "priority": "medium",
                        "action": f"Consider strategies to improve {metric_name}"
                    })
        except Exception as e:
            logger.error(f"Error generating benchmark insights: {e}")
        
        return insights

    async def get_metric_history(
        self,
        business_profile_id: str,
        metric_type: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get historical metric data for a date range.
        
        Args:
            business_profile_id: ID of business profile
            metric_type: Type of metric
            start_date: Start date
            end_date: End date
            
        Returns:
            List of metric records
        """
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        result = await self.db.execute(
            select(AnalyticsMetric)
            .where(AnalyticsMetric.business_profile_id == business_profile_id)
            .where(AnalyticsMetric.metric_name == metric_type)
            .where(AnalyticsMetric.recorded_at >= start_datetime)
            .where(AnalyticsMetric.recorded_at <= end_datetime)
            .order_by(AnalyticsMetric.recorded_at.asc())
        )
        metrics = result.scalars().all()
        
        return [
            {
                "id": metric.id,
                "metric_name": metric.metric_name,
                "metric_value": metric.metric_value,
                "metric_unit": metric.metric_unit,
                "recorded_at": metric.recorded_at.isoformat(),
                "metadata": metric.metric_metadata
            }
            for metric in metrics
        ]
