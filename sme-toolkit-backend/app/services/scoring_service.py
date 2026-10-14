"""Scoring Service - Handle all scoring calculations for strategy advisor"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import (
    BusinessProfile,
    ScoreRecord
)
from app.utils.scoring_calculators import (
    BusinessHealthCalculator,
    GrowthPotentialCalculator,
    FinancialStabilityCalculator,
    MarketPositionCalculator,
    OperationalEfficiencyCalculator,
    InnovationReadinessCalculator
)
from app.data.benchmarks import get_benchmarks, get_metric_benchmarks
from app.schemas.scoring import ScoreType

logger = logging.getLogger(__name__)


# Score calculators are now imported from utils.scoring_calculators


class ScoringService:
    """
    Service for calculating and managing business scores.
    Supports both real-time and stored score calculations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.calculators = {
            ScoreType.BUSINESS_HEALTH: BusinessHealthCalculator(),
            ScoreType.GROWTH_POTENTIAL: GrowthPotentialCalculator(),
            ScoreType.FINANCIAL_STABILITY: FinancialStabilityCalculator(),
            ScoreType.MARKET_POSITION: MarketPositionCalculator(),
            ScoreType.OPERATIONAL_EFFICIENCY: OperationalEfficiencyCalculator(),
            ScoreType.INNOVATION_READINESS: InnovationReadinessCalculator()
        }

    async def calculate_all_scores(
        self,
        profile: BusinessProfile,
        analysis_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate all scores for a business profile.
        
        Args:
            profile: Business profile to calculate scores for
            analysis_data: Analysis data from advisors (optional)
            
        Returns:
            Dictionary of all scores
        """
        # Prepare profile data from BMC and other sources
        profile_data = self._prepare_profile_data(profile, analysis_data)
        
        scores = {}
        
        for score_type, calculator in self.calculators.items():
            try:
                score_data = calculator.calculate(profile_data)
                scores[score_type.value] = score_data
                logger.info(f"Calculated {score_type.value} score: {score_data['overall_score']}")
            except Exception as e:
                logger.error(f"Error calculating {score_type.value} score: {e}")
                scores[score_type.value] = {
                    "overall_score": 0.0,
                    "level": "error",
                    "sub_metrics": {},
                    "interpretation": "Error calculating score",
                    "error": str(e)
                }

        return scores

    def _prepare_profile_data(
        self,
        profile: Any,
        analysis_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare profile data for scoring calculations.
        
        Args:
            profile: Business profile (model instance or dict)
            analysis_data: Additional analysis data
            
        Returns:
            Prepared profile data dictionary
        """
        if isinstance(profile, dict):
            bmc_data = dict(profile.get("bmc_data", profile))
            if "financial_data" in profile:
                bmc_data["financial_data"] = profile["financial_data"]
            if "operational_data" in profile:
                bmc_data["operational_data"] = profile["operational_data"]
            if "customer_data" in profile:
                bmc_data["customer_data"] = profile["customer_data"]
        else:
            bmc_data = dict(getattr(profile, "bmc_data", {}) or {})
        
        # Merge with analysis data if provided
        if analysis_data:
            for key, value in analysis_data.items():
                if isinstance(value, dict):
                    bmc_data.setdefault(key, {}).update(value)
                else:
                    bmc_data[key] = value
        
        # Ensure all required sections exist
        required_sections = ["financials", "operations", "customer", "market", "innovation", "competitive", "execution"]
        for section in required_sections:
            bmc_data.setdefault(section, {})
        
        return bmc_data

    async def calculate_business_health_score(self, profile_data: Any) -> Dict[str, Any]:
        data = self._prepare_profile_data(profile_data)
        return self.calculators[ScoreType.BUSINESS_HEALTH].calculate(data)

    async def calculate_growth_potential_score(self, profile_data: Any) -> Dict[str, Any]:
        data = self._prepare_profile_data(profile_data)
        return self.calculators[ScoreType.GROWTH_POTENTIAL].calculate(data)

    async def calculate_financial_stability_score(self, profile_data: Any) -> Dict[str, Any]:
        data = self._prepare_profile_data(profile_data)
        return self.calculators[ScoreType.FINANCIAL_STABILITY].calculate(data)

    async def calculate_market_position_score(self, profile_data: Any) -> Dict[str, Any]:
        data = self._prepare_profile_data(profile_data)
        return self.calculators[ScoreType.MARKET_POSITION].calculate(data)

    async def calculate_operational_efficiency_score(self, profile_data: Any) -> Dict[str, Any]:
        data = self._prepare_profile_data(profile_data)
        return self.calculators[ScoreType.OPERATIONAL_EFFICIENCY].calculate(data)

    async def calculate_innovation_readiness_score(self, profile_data: Any) -> Dict[str, Any]:
        data = self._prepare_profile_data(profile_data)
        return self.calculators[ScoreType.INNOVATION_READINESS].calculate(data)

    async def calculate_score(
        self,
        business_profile_id: str,
        score_type: ScoreType,
        analysis_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate a specific score type.
        
        Args:
            business_profile_id: ID of business profile
            score_type: Type of score to calculate
            analysis_data: Optional analysis data
            
        Returns:
            Score data
        """
        # Load profile
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Business profile {business_profile_id} not found")

        # Get calculator
        calculator = self.calculators.get(score_type)
        if not calculator:
            raise ValueError(f"Unknown score type: {score_type}")

        # Prepare profile data
        profile_data = self._prepare_profile_data(profile, analysis_data)
        
        # Calculate score
        score_data = calculator.calculate(profile_data)
        
        # Validate score is in range
        overall_score = score_data.get("overall_score", 0.0)
        if not (0 <= overall_score <= 100):
            logger.warning(f"Score {overall_score} out of range for {score_type.value}, clamping to 0-100")
            score_data["overall_score"] = max(0.0, min(100.0, overall_score))

        # Store score
        record_id = await self._store_score(business_profile_id, score_type, score_data)
        score_data["id"] = record_id
        score_data["calculated_at"] = datetime.utcnow().isoformat()

        return score_data

    async def _store_score(
        self,
        business_profile_id: str,
        score_type: ScoreType,
        score_data: Dict[str, Any]
    ) -> str:
        """Store score in database for historical tracking"""
        record = ScoreRecord(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            score_type=score_type,
            overall_score=score_data["overall_score"],
            sub_metrics=score_data["sub_metrics"],
            calculated_at=datetime.utcnow()
        )

        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        logger.info(f"Stored score record {record.id} for {score_type.value}")
        return record.id

    async def store_scores(self, business_profile_id: str, scores: Dict[str, Any]) -> List[str]:
        """Store multiple score records in database"""
        record_ids = []
        for score_type_str, score_data in scores.items():
            try:
                st = ScoreType(score_type_str)
                if isinstance(score_data, dict) and "overall_score" in score_data:
                    rid = await self._store_score(business_profile_id, st, score_data)
                    record_ids.append(rid)
            except ValueError:
                pass
        return record_ids

    async def get_latest_scores(
        self,
        business_profile_id: str
    ) -> Dict[str, Any]:
        """
        Get the most recent scores for all score types.
        
        Args:
            business_profile_id: ID of business profile
            
        Returns:
            Dictionary of latest scores
        """
        scores = {}
        
        for score_type in ScoreType:
            result = await self.db.execute(
                select(ScoreRecord)
                .where(ScoreRecord.business_profile_id == business_profile_id)
                .where(ScoreRecord.score_type == score_type)
                .order_by(ScoreRecord.calculated_at.desc())
                .limit(1)
            )
            record = result.scalar_one_or_none()
            
            if record:
                scores[score_type.value] = {
                    "id": record.id,
                    "overall_score": record.overall_score,
                    "sub_metrics": record.sub_metrics,
                    "calculated_at": record.calculated_at.isoformat()
                }

        return scores

    async def get_score_history(
        self,
        business_profile_id: str,
        score_type: Any,
        limit: Any = 10
    ) -> List[Dict[str, Any]]:
        """
        Get historical score data for a specific score type.
        """
        if isinstance(limit, str):
            clean_str = limit.rstrip("dD")
            try:
                limit = int(clean_str)
            except ValueError:
                limit = 10

        st = score_type.value if hasattr(score_type, "value") else str(score_type)
        result = await self.db.execute(
            select(ScoreRecord)
            .where(ScoreRecord.business_profile_id == business_profile_id)
            .where(ScoreRecord.score_type == score_type)
            .order_by(ScoreRecord.calculated_at.desc())
            .limit(limit)
        )
        records = result.scalars().all()

        return [
            {
                "id": record.id,
                "overall_score": record.overall_score,
                "sub_metrics": record.sub_metrics,
                "calculated_at": record.calculated_at.isoformat()
            }
            for record in records
        ]

    async def get_score_trends(
        self,
        business_profile_id: str
    ) -> Dict[str, Any]:
        """
        Get score trends with forecasting.
        
        Args:
            business_profile_id: ID of business profile
            
        Returns:
            Score trends for all score types
        """
        trends = {}
        
        for score_type in ScoreType:
            # Get historical data
            result = await self.db.execute(
                select(ScoreRecord)
                .where(ScoreRecord.business_profile_id == business_profile_id)
                .where(ScoreRecord.score_type == score_type)
                .order_by(ScoreRecord.calculated_at.asc())
            )
            records = result.scalars().all()
            
            if len(records) < 2:
                trends[score_type.value] = {
                    "trend": "insufficient_data",
                    "change": 0.0,
                    "change_percentage": 0.0,
                    "forecast": []
                }
                continue
            
            # Calculate trend
            values = [record.overall_score for record in records]
            first_value = values[0]
            last_value = values[-1]
            change = last_value - first_value
            change_percentage = (change / first_value * 100) if first_value != 0 else 0.0
            
            # Determine trend direction
            if change_percentage > 5:
                trend = "improving"
            elif change_percentage < -5:
                trend = "declining"
            else:
                trend = "stable"
            
            # Simple forecast (linear extrapolation)
            if len(values) >= 3:
                avg_change = sum(values[i+1] - values[i] for i in range(len(values)-1)) / (len(values)-1)
                forecast = [last_value + avg_change * (i+1) for i in range(5)]
                forecast = [max(0.0, min(100.0, f)) for f in forecast]
            else:
                forecast = [last_value] * 5
            
            trends[score_type.value] = {
                "trend": trend,
                "change": round(change, 2),
                "change_percentage": round(change_percentage, 2),
                "current_score": round(last_value, 2),
                "previous_score": round(first_value, 2),
                "forecast": [round(f, 2) for f in forecast],
                "data_points": len(values)
            }
        
        return trends

    async def compare_with_benchmarks(
        self,
        business_profile_id: str
    ) -> Dict[str, Any]:
        """
        Compare scores with industry benchmarks.
        
        Args:
            business_profile_id: ID of business profile
            
        Returns:
            Comparison data for all scores
        """
        # Load profile
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Business profile {business_profile_id} not found")
        
        # Get current scores
        current_scores = await self.get_latest_scores(business_profile_id)
        
        # Get benchmarks
        industry = profile.industry or "general"
        business_size = profile.business_stage or "small"
        benchmarks = get_benchmarks(industry, business_size)
        
        # Compare
        comparisons = {}
        for score_type, score_data in current_scores.items():
            if not score_data or "overall_score" not in score_data:
                continue
            
            current_score = score_data["overall_score"]
            benchmark_data = benchmarks.get(score_type)
            
            if not benchmark_data:
                continue
            
            industry_avg = benchmark_data["industry_average"]
            difference = current_score - industry_avg
            difference_percentage = (difference / industry_avg * 100) if industry_avg != 0 else 0.0
            
            # Determine performance level
            if current_score >= benchmark_data["top_quartile"]:
                performance = "top_quartile"
            elif current_score >= benchmark_data["median"]:
                performance = "above_average"
            elif current_score >= benchmark_data["bottom_quartile"]:
                performance = "below_average"
            else:
                performance = "bottom_quartile"
            
            comparisons[score_type] = {
                "current_score": current_score,
                "industry_average": industry_avg,
                "difference": round(difference, 2),
                "difference_percentage": round(difference_percentage, 2),
                "performance": performance,
                "percentile": self._calculate_percentile(current_score, benchmark_data)
            }
        
        return {
            "business_profile_id": business_profile_id,
            "industry": industry,
            "business_size": business_size,
            "comparisons": comparisons
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

    async def recalculate_scores(
        self,
        business_profile_id: str,
        score_types: Optional[List[ScoreType]] = None
    ) -> Dict[str, Any]:
        """
        Force recalculation of scores.
        
        Args:
            business_profile_id: ID of business profile
            score_types: Specific score types to recalculate (all if None)
            
        Returns:
            Dictionary of recalculated scores
        """
        # Load profile
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Business profile {business_profile_id} not found")
        
        # Determine which scores to recalculate
        types_to_recalculate = score_types if score_types else list(ScoreType)
        
        # Recalculate each score type
        scores = {}
        for score_type in types_to_recalculate:
            try:
                score_data = await self.calculate_score(
                    business_profile_id,
                    score_type
                )
                scores[score_type.value] = score_data
                logger.info(f"Recalculated {score_type.value} score: {score_data['overall_score']}")
            except Exception as e:
                logger.error(f"Error recalculating {score_type.value} score: {e}")
                scores[score_type.value] = {
                    "error": str(e)
                }
        
        return scores
