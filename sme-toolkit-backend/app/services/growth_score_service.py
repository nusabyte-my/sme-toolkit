"""Growth Score Service - Calculates and manages multi-factor growth scores"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import GrowthScoreRecord, BusinessProfile
from app.tools.gemini_tools import get_gemini_client


@dataclass
class ScoreComponent:
    """Individual score component with breakdown"""
    name: str
    score: float  # 0-100
    weight: float  # 0-1
    factors: List[Dict[str, Any]]
    recommendations: List[str]

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight


class GrowthScoreCalculator:
    """
    Multi-factor growth score calculation.
    Components: BMC Quality, Strategy Alignment, Market Readiness, Execution Capability
    """

    WEIGHTS = {
        "bmc_quality": 0.25,
        "strategy_alignment": 0.25,
        "market_readiness": 0.30,
        "execution_capability": 0.20
    }

    def __init__(self):
        self.client = get_gemini_client()

    def calculate(
        self,
        bmc_data: Dict[str, List[str]],
        market_analysis: Optional[Dict[str, Any]] = None,
        financial_data: Optional[Dict[str, Any]] = None,
        operations_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive growth score"""

        components = {
            "bmc_quality": self._calculate_bmc_quality(bmc_data),
            "strategy_alignment": self._calculate_strategy_alignment(bmc_data, market_analysis, financial_data),
            "market_readiness": self._calculate_market_readiness(market_analysis),
            "execution_capability": self._calculate_execution_capability(operations_data, financial_data)
        }

        overall_score = sum(
            comp.weighted_score for comp in components.values()
        )

        grade = self._score_to_grade(overall_score)
        summary = self._generate_summary(overall_score, components)
        improvement_priorities = self._get_improvement_priorities(components)

        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "components": {
                name: {
                    "score": round(comp.score, 1),
                    "weight": comp.weight,
                    "weighted_score": round(comp.weighted_score, 1),
                    "factors": comp.factors,
                    "recommendations": comp.recommendations
                }
                for name, comp in components.items()
            },
            "summary": summary,
            "improvement_priorities": improvement_priorities,
            "next_steps": self._generate_next_steps(components, improvement_priorities)
        }

    def _calculate_bmc_quality(self, bmc_data: Dict[str, List[str]]) -> ScoreComponent:
        """
        Assess BMC quality based on:
        - Completeness (all 9 blocks filled)
        - Depth (items per block)
        - Coherence (logical connections)
        - Specificity (actionable vs generic)
        """
        factors = []
        recommendations = []

        # Completeness check
        filled_blocks = sum(1 for items in bmc_data.values() if items and len(items) > 0)
        completeness = (filled_blocks / 9) * 100
        factors.append({
            "name": "Completeness",
            "score": round(completeness, 1),
            "detail": f"{filled_blocks}/9 blocks filled"
        })

        if filled_blocks < 9:
            missing_blocks = [k for k, v in bmc_data.items() if not v or len(v) == 0]
            recommendations.append(f"Complete missing blocks: {', '.join(missing_blocks[:3])}")

        # Depth check (target: 3+ items per block)
        total_items = sum(len(items) for items in bmc_data.values() if items)
        avg_items = total_items / 9 if filled_blocks > 0 else 0
        depth_score = min(100, (avg_items / 3) * 100)
        factors.append({
            "name": "Depth",
            "score": round(depth_score, 1),
            "detail": f"{total_items} total items, {avg_items:.1f} average per block"
        })

        if avg_items < 3:
            recommendations.append("Add more detail to each block (aim for 3-5 items)")

        # Coherence check (simplified heuristic)
        # Check if value props align with customer segments
        has_value = bool(bmc_data.get("valuePropositions"))
        has_customers = bool(bmc_data.get("customerSegments"))
        has_revenue = bool(bmc_data.get("revenueStreams"))
        coherence_score = 100 if (has_value and has_customers and has_revenue) else 60
        factors.append({
            "name": "Coherence",
            "score": coherence_score,
            "detail": "Value-Customer-Revenue alignment"
        })

        if coherence_score < 100:
            recommendations.append("Ensure value propositions clearly address customer segments")

        # Calculate overall BMC quality score
        score = (completeness * 0.4 + depth_score * 0.35 + coherence_score * 0.25)

        return ScoreComponent(
            name="BMC Quality",
            score=score,
            weight=self.WEIGHTS["bmc_quality"],
            factors=factors,
            recommendations=recommendations[:3]
        )

    def _calculate_strategy_alignment(
        self,
        bmc_data: Dict[str, List[str]],
        market_analysis: Optional[Dict[str, Any]],
        financial_data: Optional[Dict[str, Any]]
    ) -> ScoreComponent:
        """
        Assess alignment between:
        - Value proposition and customer segments
        - Channels and target market
        - Revenue model and market position
        """
        factors = []
        recommendations = []
        scores = []

        # Value-Customer alignment
        value_props = bmc_data.get("valuePropositions", [])
        customer_segments = bmc_data.get("customerSegments", [])
        if value_props and customer_segments:
            # Heuristic: both should have similar specificity
            value_customer_score = min(100, (len(value_props) + len(customer_segments)) * 15)
            factors.append({
                "name": "Value-Customer Fit",
                "score": value_customer_score,
                "detail": f"{len(value_props)} value props for {len(customer_segments)} segments"
            })
            scores.append(value_customer_score)
        else:
            scores.append(30)
            recommendations.append("Define clear value propositions for each customer segment")

        # Channel-Market alignment
        channels = bmc_data.get("channels", [])
        if channels:
            channel_score = min(100, len(channels) * 25)
            factors.append({
                "name": "Channel Coverage",
                "score": channel_score,
                "detail": f"{len(channels)} channels defined"
            })
            scores.append(channel_score)
        else:
            scores.append(30)
            recommendations.append("Define distribution and communication channels")

        # Revenue model strength (from financial data if available)
        if financial_data and financial_data.get("success"):
            revenue_score = financial_data.get("financial_health_score", 50)
            factors.append({
                "name": "Revenue Model",
                "score": revenue_score,
                "detail": "Based on financial analysis"
            })
            scores.append(revenue_score)
        else:
            revenue_streams = bmc_data.get("revenueStreams", [])
            revenue_score = min(100, len(revenue_streams) * 30) if revenue_streams else 40
            factors.append({
                "name": "Revenue Model",
                "score": revenue_score,
                "detail": f"{len(revenue_streams)} revenue streams"
            })
            scores.append(revenue_score)

        overall_score = sum(scores) / len(scores) if scores else 50

        return ScoreComponent(
            name="Strategy Alignment",
            score=overall_score,
            weight=self.WEIGHTS["strategy_alignment"],
            factors=factors,
            recommendations=recommendations[:3]
        )

    def _calculate_market_readiness(
        self,
        market_analysis: Optional[Dict[str, Any]]
    ) -> ScoreComponent:
        """
        Assess market readiness based on:
        - Market size and growth
        - Competitive positioning
        - Barrier to entry
        - Timing factors
        """
        factors = []
        recommendations = []

        if market_analysis and market_analysis.get("success"):
            # Use market analysis results
            market_score = market_analysis.get("market_readiness_score", 50)

            timing = market_analysis.get("timing_assessment", "neutral")
            timing_score = {"favorable": 80, "neutral": 50, "challenging": 30}.get(timing, 50)
            factors.append({
                "name": "Market Timing",
                "score": timing_score,
                "detail": f"Timing: {timing}"
            })

            # Competitive analysis
            comp_analysis = market_analysis.get("competitive_analysis", {})
            advantages = comp_analysis.get("competitive_advantages", [])
            comp_score = min(100, len(advantages) * 25) if advantages else 40
            factors.append({
                "name": "Competitive Position",
                "score": comp_score,
                "detail": f"{len(advantages)} competitive advantages"
            })

            if len(advantages) < 2:
                recommendations.append("Identify more competitive advantages")

            overall_score = (market_score * 0.5 + timing_score * 0.25 + comp_score * 0.25)
        else:
            # Default scores when no analysis available
            factors.append({
                "name": "Market Analysis",
                "score": 50,
                "detail": "No market analysis available"
            })
            recommendations.append("Complete market analysis for better assessment")
            overall_score = 50

        return ScoreComponent(
            name="Market Readiness",
            score=overall_score,
            weight=self.WEIGHTS["market_readiness"],
            factors=factors,
            recommendations=recommendations[:3]
        )

    def _calculate_execution_capability(
        self,
        operations_data: Optional[Dict[str, Any]],
        financial_data: Optional[Dict[str, Any]]
    ) -> ScoreComponent:
        """
        Assess ability to execute based on:
        - Resource availability
        - Financial runway
        - Team capabilities
        - Process maturity
        """
        factors = []
        recommendations = []
        scores = []

        if operations_data and operations_data.get("success"):
            exec_score = operations_data.get("execution_capability_score", 50)
            factors.append({
                "name": "Operational Readiness",
                "score": exec_score,
                "detail": "Based on operations analysis"
            })
            scores.append(exec_score)

            priorities = operations_data.get("operational_priorities", [])
            if priorities:
                recommendations.extend(priorities[:2])
        else:
            factors.append({
                "name": "Operational Readiness",
                "score": 50,
                "detail": "No operations analysis available"
            })
            scores.append(50)

        if financial_data and financial_data.get("success"):
            funding_readiness = financial_data.get("funding_readiness", "early")
            funding_score = {"ready": 80, "developing": 60, "early": 40}.get(funding_readiness, 50)
            factors.append({
                "name": "Financial Readiness",
                "score": funding_score,
                "detail": f"Funding: {funding_readiness}"
            })
            scores.append(funding_score)
        else:
            scores.append(50)

        overall_score = sum(scores) / len(scores) if scores else 50

        return ScoreComponent(
            name="Execution Capability",
            score=overall_score,
            weight=self.WEIGHTS["execution_capability"],
            factors=factors,
            recommendations=recommendations[:3]
        )

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90: return "A+"
        if score >= 85: return "A"
        if score >= 80: return "A-"
        if score >= 75: return "B+"
        if score >= 70: return "B"
        if score >= 65: return "B-"
        if score >= 60: return "C+"
        if score >= 55: return "C"
        if score >= 50: return "C-"
        return "D"

    def _generate_summary(self, score: float, components: Dict[str, ScoreComponent]) -> str:
        """Generate human-readable summary"""
        if score >= 80:
            return "Your business model shows strong potential across all dimensions. Focus on execution and scaling."
        elif score >= 60:
            return "Good foundation with room for improvement. Address the weaker areas to strengthen your position."
        elif score >= 40:
            return "Several areas need attention. Consider refining your business model before scaling."
        else:
            return "Significant improvements needed. Focus on building a stronger foundation first."

    def _get_improvement_priorities(self, components: Dict[str, ScoreComponent]) -> List[str]:
        """Identify top areas for improvement"""
        sorted_components = sorted(
            components.items(),
            key=lambda x: x[1].score
        )
        return [name for name, _ in sorted_components[:2]]

    def _generate_next_steps(
        self,
        components: Dict[str, ScoreComponent],
        priorities: List[str]
    ) -> List[str]:
        """Generate actionable next steps"""
        next_steps = []

        for priority in priorities:
            component = components.get(priority)
            if component and component.recommendations:
                next_steps.append(component.recommendations[0])

        if not next_steps:
            next_steps.append("Complete all BMC blocks with 3-5 specific items each")
            next_steps.append("Validate value propositions with potential customers")

        return next_steps[:3]


class GrowthScoreService:
    """Service for managing growth scores in database"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.calculator = GrowthScoreCalculator()

    async def calculate_and_save(
        self,
        business_profile_id: str,
        bmc_data: Dict[str, List[str]],
        market_analysis: Optional[Dict[str, Any]] = None,
        financial_data: Optional[Dict[str, Any]] = None,
        operations_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate growth score and save to database"""

        # Calculate score
        score_data = self.calculator.calculate(
            bmc_data=bmc_data,
            market_analysis=market_analysis,
            financial_data=financial_data,
            operations_data=operations_data
        )

        # Save to database
        record = GrowthScoreRecord(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            overall_score=score_data["overall_score"],
            grade=score_data["grade"],
            components=score_data["components"],
            summary=score_data["summary"],
            improvement_priorities=score_data["improvement_priorities"],
            calculated_at=datetime.utcnow()
        )

        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        return {
            **score_data,
            "id": record.id,
            "calculated_at": record.calculated_at.isoformat()
        }

    async def get_latest_score(self, business_profile_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent growth score for a profile"""
        result = await self.db.execute(
            select(GrowthScoreRecord)
            .where(GrowthScoreRecord.business_profile_id == business_profile_id)
            .order_by(GrowthScoreRecord.calculated_at.desc())
            .limit(1)
        )
        record = result.scalar_one_or_none()

        if not record:
            return None

        return {
            "id": record.id,
            "overall_score": record.overall_score,
            "grade": record.grade,
            "components": record.components,
            "summary": record.summary,
            "improvement_priorities": record.improvement_priorities,
            "calculated_at": record.calculated_at.isoformat()
        }

    async def get_score_history(
        self,
        business_profile_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get growth score history for a profile"""
        result = await self.db.execute(
            select(GrowthScoreRecord)
            .where(GrowthScoreRecord.business_profile_id == business_profile_id)
            .order_by(GrowthScoreRecord.calculated_at.desc())
            .limit(limit)
        )
        records = result.scalars().all()

        return [
            {
                "id": record.id,
                "overall_score": record.overall_score,
                "grade": record.grade,
                "calculated_at": record.calculated_at.isoformat()
            }
            for record in records
        ]
