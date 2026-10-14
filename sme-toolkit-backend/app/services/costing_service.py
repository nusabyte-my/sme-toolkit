"""Costing Service - Manage costing analysis operations"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import (
    BusinessProfile,
    CostingAnalysis
)

logger = logging.getLogger(__name__)


class CostingService:
    """
    Service for managing costing analyses.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_costing_analysis(
        self,
        business_profile_id: str,
        cost_structure: Dict[str, Any],
        pricing_strategies: Optional[Dict[str, Any]] = None,
        optimization_opportunities: Optional[List[Dict[str, Any]]] = None,
        break_even_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new costing analysis.
        
        Args:
            business_profile_id: ID of business profile
            cost_structure: Fixed and variable costs breakdown
            pricing_strategies: Pricing recommendations
            optimization_opportunities: Cost-saving opportunities
            break_even_analysis: Break-even calculations
            
        Returns:
            Created costing analysis data
        """
        # Verify business profile exists
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Business profile {business_profile_id} not found")

        # Create costing analysis
        analysis = CostingAnalysis(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            analysis_date=datetime.utcnow(),
            cost_structure=cost_structure,
            pricing_strategies=pricing_strategies,
            optimization_opportunities=optimization_opportunities,
            break_even_analysis=break_even_analysis,
            created_at=datetime.utcnow()
        )

        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)

        logger.info(f"Created costing analysis {analysis.id} for profile {business_profile_id}")
        return self._costing_analysis_to_dict(analysis)

    async def get_costing_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific costing analysis by ID.
        
        Args:
            analysis_id: ID of costing analysis
            
        Returns:
            Costing analysis data or None
        """
        result = await self.db.execute(
            select(CostingAnalysis).where(CostingAnalysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            return None

        return self._costing_analysis_to_dict(analysis)

    async def get_costing_analyses(
        self,
        business_profile_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get costing analyses for a business profile.
        
        Args:
            business_profile_id: ID of business profile
            limit: Maximum number of analyses to return
            
        Returns:
            List of costing analyses
        """
        result = await self.db.execute(
            select(CostingAnalysis)
            .where(CostingAnalysis.business_profile_id == business_profile_id)
            .order_by(CostingAnalysis.analysis_date.desc())
            .limit(limit)
        )
        analyses = result.scalars().all()

        return [self._costing_analysis_to_dict(analysis) for analysis in analyses]

    async def get_latest_costing_analysis(
        self,
        business_profile_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent costing analysis for a business profile.
        
        Args:
            business_profile_id: ID of business profile
            
        Returns:
            Latest costing analysis or None
        """
        result = await self.db.execute(
            select(CostingAnalysis)
            .where(CostingAnalysis.business_profile_id == business_profile_id)
            .order_by(CostingAnalysis.analysis_date.desc())
            .limit(1)
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            return None

        return self._costing_analysis_to_dict(analysis)

    async def delete_costing_analysis(self, analysis_id: str) -> bool:
        """
        Delete a costing analysis.
        
        Args:
            analysis_id: ID of costing analysis to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            select(CostingAnalysis).where(CostingAnalysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            return False

        await self.db.delete(analysis)
        await self.db.commit()

        logger.info(f"Deleted costing analysis {analysis_id}")
        return True

    async def get_cost_summary(
        self,
        business_profile_id: str
    ) -> Dict[str, Any]:
        """
        Get cost summary from latest analysis.
        
        Args:
            business_profile_id: ID of business profile
            
        Returns:
            Cost summary data
        """
        latest_analysis = await self.get_latest_costing_analysis(business_profile_id)

        if not latest_analysis:
            return {
                "has_analysis": False,
                "message": "No costing analysis found"
            }

        cost_structure = latest_analysis.get("cost_structure", {})
        fixed_costs = cost_structure.get("fixed_costs", {})
        variable_costs = cost_structure.get("variable_costs", {})

        return {
            "has_analysis": True,
            "analysis_id": latest_analysis["id"],
            "analysis_date": latest_analysis["analysis_date"],
            "total_monthly_cost": cost_structure.get("total_monthly_cost", 0),
            "fixed_costs": {
                "total": fixed_costs.get("total", 0),
                "breakdown": fixed_costs.get("breakdown", [])
            },
            "variable_costs": {
                "total": variable_costs.get("total", 0),
                "breakdown": variable_costs.get("breakdown", [])
            },
            "cost_per_unit": cost_structure.get("cost_per_unit", 0),
            "pricing_strategies_count": len(latest_analysis.get("pricing_strategies", {})),
            "optimization_opportunities_count": len(latest_analysis.get("optimization_opportunities", []))
        }

    def _costing_analysis_to_dict(self, analysis: CostingAnalysis) -> Dict[str, Any]:
        """Convert costing analysis to dictionary"""
        return {
            "id": analysis.id,
            "business_profile_id": analysis.business_profile_id,
            "analysis_date": analysis.analysis_date.isoformat(),
            "cost_structure": analysis.cost_structure,
            "pricing_strategies": analysis.pricing_strategies,
            "optimization_opportunities": analysis.optimization_opportunities,
            "break_even_analysis": analysis.break_even_analysis,
            "created_at": analysis.created_at.isoformat()
        }
