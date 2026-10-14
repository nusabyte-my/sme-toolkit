"""Growth Service - Manage growth plan operations"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import (
    BusinessProfile,
    GrowthPlan
)

logger = logging.getLogger(__name__)


class GrowthService:
    """
    Service for managing growth plans.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_growth_plan(
        self,
        business_profile_id: str,
        title: str,
        plan_data: Dict[str, Any],
        timeframe: Optional[str] = None,
        status: str = "draft"
    ) -> Dict[str, Any]:
        """
        Create a new growth plan.
        
        Args:
            business_profile_id: ID of business profile
            title: Plan title
            timeframe: Plan timeframe (e.g., "6 months", "1 year")
            plan_data: Complete growth plan data
            status: Plan status (draft, active, completed, archived)
            
        Returns:
            Created growth plan data
        """
        # Verify business profile exists
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Business profile {business_profile_id} not found")

        # Create growth plan
        growth_plan = GrowthPlan(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            title=title,
            timeframe=timeframe,
            plan_data=plan_data,
            status=status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(growth_plan)
        await self.db.commit()
        await self.db.refresh(growth_plan)

        logger.info(f"Created growth plan {growth_plan.id} for profile {business_profile_id}")
        return self._growth_plan_to_dict(growth_plan)

    async def get_growth_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific growth plan by ID.
        
        Args:
            plan_id: ID of growth plan
            
        Returns:
            Growth plan data or None
        """
        result = await self.db.execute(
            select(GrowthPlan).where(GrowthPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()

        if not plan:
            return None

        return self._growth_plan_to_dict(plan)

    async def get_growth_plans(
        self,
        business_profile_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get growth plans for a business profile.
        
        Args:
            business_profile_id: ID of business profile
            status: Filter by status
            
        Returns:
            List of growth plans
        """
        query = select(GrowthPlan).where(
            GrowthPlan.business_profile_id == business_profile_id
        )

        if status:
            query = query.where(GrowthPlan.status == status)

        query = query.order_by(GrowthPlan.created_at.desc())

        result = await self.db.execute(query)
        plans = result.scalars().all()

        return [self._growth_plan_to_dict(plan) for plan in plans]

    async def update_growth_plan(
        self,
        plan_id: str,
        title: Optional[str] = None,
        timeframe: Optional[str] = None,
        plan_data: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a growth plan.
        
        Args:
            plan_id: ID of growth plan to update
            title: New title
            timeframe: New timeframe
            plan_data: New plan data
            status: New status
            
        Returns:
            Updated growth plan data or None
        """
        result = await self.db.execute(
            select(GrowthPlan).where(GrowthPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()

        if not plan:
            return None

        # Update fields if provided
        if title is not None:
            plan.title = title
        if timeframe is not None:
            plan.timeframe = timeframe
        if plan_data is not None:
            plan.plan_data = plan_data
        if status is not None:
            plan.status = status

        plan.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(plan)

        logger.info(f"Updated growth plan {plan_id}")
        return self._growth_plan_to_dict(plan)

    async def delete_growth_plan(self, plan_id: str) -> bool:
        """
        Delete a growth plan.
        
        Args:
            plan_id: ID of growth plan to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            select(GrowthPlan).where(GrowthPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()

        if not plan:
            return False

        await self.db.delete(plan)
        await self.db.commit()

        logger.info(f"Deleted growth plan {plan_id}")
        return True

    async def get_active_growth_plan(
        self,
        business_profile_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the active growth plan for a business profile.
        
        Args:
            business_profile_id: ID of business profile
            
        Returns:
            Active growth plan or None
        """
        result = await self.db.execute(
            select(GrowthPlan)
            .where(GrowthPlan.business_profile_id == business_profile_id)
            .where(GrowthPlan.status == "active")
            .order_by(GrowthPlan.created_at.desc())
            .limit(1)
        )
        plan = result.scalar_one_or_none()

        if not plan:
            return None

        return self._growth_plan_to_dict(plan)

    def _growth_plan_to_dict(self, plan: GrowthPlan) -> Dict[str, Any]:
        """Convert growth plan to dictionary"""
        return {
            "id": plan.id,
            "business_profile_id": plan.business_profile_id,
            "title": plan.title,
            "timeframe": plan.timeframe,
            "plan_data": plan.plan_data,
            "status": plan.status,
            "created_at": plan.created_at.isoformat(),
            "updated_at": plan.updated_at.isoformat()
        }
