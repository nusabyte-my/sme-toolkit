"""Trend analysis utilities for analytics"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyze trends in metric data"""
    
    @staticmethod
    def calculate_moving_average(values: List[float], window: int = 3) -> List[float]:
        """
        Calculate moving average for smoothing trend data.
        
        Args:
            values: List of values
            window: Window size for moving average
            
        Returns:
            List of moving averages
        """
        if len(values) < window:
            return values.copy()
        
        moving_avg = []
        for i in range(len(values) - window + 1):
            window_values = values[i:i + window]
            avg = sum(window_values) / window
            moving_avg.append(avg)
        
        return moving_avg
    
    @staticmethod
    def calculate_linear_regression(values: List[float]) -> Dict[str, float]:
        """
        Calculate linear regression for trend forecasting.
        
        Args:
            values: List of values
            
        Returns:
            Dictionary with slope, intercept, and r_squared
        """
        if len(values) < 2:
            return {"slope": 0.0, "intercept": 0.0, "r_squared": 0.0}
        
        n = len(values)
        x = list(range(n))
        y = values
        
        # Calculate sums
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)
        sum_y2 = sum(yi ** 2 for yi in y)
        
        # Calculate slope and intercept
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return {"slope": 0.0, "intercept": sum_y / n, "r_squared": 0.0}
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate R-squared
        y_mean = sum_y / n
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        
        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared
        }
    
    @staticmethod
    def forecast(values: List[float], periods: int = 5) -> List[float]:
        """
        Forecast future values using linear regression.
        
        Args:
            values: Historical values
            periods: Number of periods to forecast
            
        Returns:
            List of forecasted values
        """
        if len(values) < 2:
            return [values[-1]] * periods if values else [0.0] * periods
        
        regression = TrendAnalyzer.calculate_linear_regression(values)
        slope = regression["slope"]
        intercept = regression["intercept"]
        
        forecasts = []
        n = len(values)
        for i in range(1, periods + 1):
            forecast = slope * (n + i - 1) + intercept
            forecasts.append(max(0.0, forecast))  # Ensure non-negative
        
        return forecasts
    
    @staticmethod
    def detect_trend(values: List[float]) -> str:
        """
        Detect trend direction from values.
        
        Args:
            values: List of values
            
        Returns:
            Trend direction: "improving", "stable", "declining"
        """
        if len(values) < 2:
            return "stable"
        
        # Calculate percentage change
        first_value = values[0]
        last_value = values[-1]
        
        if first_value == 0:
            return "stable"
        
        change_percentage = ((last_value - first_value) / first_value) * 100
        
        # Determine trend
        if change_percentage > 5:
            return "improving"
        elif change_percentage < -5:
            return "declining"
        else:
            return "stable"
    
    @staticmethod
    def calculate_volatility(values: List[float]) -> float:
        """
        Calculate volatility (standard deviation).
        
        Args:
            values: List of values
            
        Returns:
            Volatility measure
        """
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    @staticmethod
    def calculate_growth_rate(values: List[float]) -> float:
        """
        Calculate compound annual growth rate (CAGR).
        
        Args:
            values: List of values
            
        Returns:
            Growth rate as percentage
        """
        if len(values) < 2:
            return 0.0
        
        first_value = values[0]
        last_value = values[-1]
        
        if first_value <= 0:
            return 0.0
        
        n = len(values) - 1
        cagr = ((last_value / first_value) ** (1 / n) - 1) * 100
        
        return cagr
    
    @staticmethod
    def analyze_trend(
        values: List[float],
        forecast_periods: int = 5
    ) -> Dict[str, Any]:
        """
        Perform comprehensive trend analysis.
        
        Args:
            values: Historical values
            forecast_periods: Number of periods to forecast
            
        Returns:
            Comprehensive trend analysis
        """
        if not values:
            return {
                "trend": "no_data",
                "change": 0.0,
                "change_percentage": 0.0,
                "growth_rate": 0.0,
                "volatility": 0.0,
                "forecast": [],
                "confidence": "low"
            }
        
        # Calculate trend direction
        trend = TrendAnalyzer.detect_trend(values)
        
        # Calculate change
        first_value = values[0]
        last_value = values[-1]
        change = last_value - first_value
        change_percentage = (change / first_value * 100) if first_value != 0 else 0.0
        
        # Calculate growth rate
        growth_rate = TrendAnalyzer.calculate_growth_rate(values)
        
        # Calculate volatility
        volatility = TrendAnalyzer.calculate_volatility(values)
        
        # Calculate forecast
        forecast = TrendAnalyzer.forecast(values, forecast_periods)
        
        # Calculate confidence based on data points and volatility
        confidence = "high"
        if len(values) < 5:
            confidence = "low"
        elif len(values) < 10:
            confidence = "medium"
        
        if volatility > (sum(values) / len(values) * 0.5):
            confidence = "low"
        elif confidence == "high" and volatility > (sum(values) / len(values) * 0.3):
            confidence = "medium"
        
        return {
            "trend": trend,
            "change": round(change, 2),
            "change_percentage": round(change_percentage, 2),
            "growth_rate": round(growth_rate, 2),
            "volatility": round(volatility, 2),
            "forecast": [round(f, 2) for f in forecast],
            "confidence": confidence,
            "data_points": len(values)
        }
    
    @staticmethod
    def generate_insights(
        metric_name: str,
        trend_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Generate actionable insights from trend analysis.
        
        Args:
            metric_name: Name of the metric
            trend_analysis: Trend analysis results
            
        Returns:
            List of insights
        """
        insights = []
        trend = trend_analysis.get("trend", "stable")
        change_percentage = trend_analysis.get("change_percentage", 0.0)
        growth_rate = trend_analysis.get("growth_rate", 0.0)
        volatility = trend_analysis.get("volatility", 0.0)
        confidence = trend_analysis.get("confidence", "low")
        
        # Trend-based insights
        if trend == "improving":
            insights.append(
                f"{metric_name} is improving by {abs(change_percentage):.1f}% over the period"
            )
            insights.append("Continue current strategies to maintain positive trend")
            
            if growth_rate > 10:
                insights.append("Strong growth rate indicates effective strategies")
            elif growth_rate > 5:
                insights.append("Moderate growth rate - consider optimization")
        elif trend == "declining":
            insights.append(
                f"{metric_name} is declining by {abs(change_percentage):.1f}% over the period"
            )
            insights.append("Investigate causes and implement corrective actions")
            
            if growth_rate < -10:
                insights.append("Critical decline - immediate intervention required")
            elif growth_rate < -5:
                insights.append("Significant decline - review strategies urgently")
        else:
            insights.append(f"{metric_name} is stable with minimal change")
            insights.append("Monitor for changes and optimize if needed")
        
        # Volatility insights
        if volatility > 0:
            avg_value = trend_analysis.get("change", 0) + trend_analysis.get("change", 0)
            if avg_value != 0 and volatility / abs(avg_value) > 0.5:
                insights.append("High volatility detected - consider stabilizing measures")
        
        # Confidence insights
        if confidence == "low":
            insights.append("Limited data - collect more data for accurate analysis")
        elif confidence == "medium":
            insights.append("Moderate confidence - continue monitoring")
        
        # Forecast insights
        forecast = trend_analysis.get("forecast", [])
        if forecast and confidence in ["medium", "high"]:
            forecast_change = forecast[-1] - trend_analysis.get("change", 0)
            if forecast_change > 0:
                insights.append(
                    f"Forecast suggests continued improvement in next {len(forecast)} periods"
                )
            elif forecast_change < 0:
                insights.append(
                    f"Forecast suggests potential decline in next {len(forecast)} periods"
                )
        
        return insights
