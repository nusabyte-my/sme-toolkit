"""Goal Service - Manage goal-related operations"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import (
    BusinessProfile,
    CompanyGoal,
    GoalStatus,
    GoalPriority
)

logger = logging.getLogger(__name__)


class GoalService:
    """
    Service for managing company goals.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_goal(
        self,
        business_profile_id: str,
        title: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: GoalPriority = GoalPriority.MEDIUM,
        deadline: Optional[datetime] = None,
        smart_criteria: Optional[Dict[str, Any]] = None,
        bmc_alignment: Optional[Dict[str, Any]] = None,
        milestones: Optional[List[Dict[str, Any]]] = None,
        success_metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new goal.
        
        Args:
            business_profile_id: ID of business profile
            title: Goal title
            description: Goal description
            category: Goal category (financial, operational, market, innovation)
            priority: Goal priority
            deadline: Goal deadline
            smart_criteria: SMART criteria breakdown
            bmc_alignment: Alignment with BMC blocks
            milestones: Goal milestones
            success_metrics: Success metrics
            
        Returns:
            Created goal data
        """
        # Verify business profile exists
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Business profile {business_profile_id} not found")

        # Create goal
        goal = CompanyGoal(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            progress=0.0,
            deadline=deadline,
            status=GoalStatus.ACTIVE,
            smart_criteria=smart_criteria,
            bmc_alignment=bmc_alignment,
            milestones=milestones,
            success_metrics=success_metrics,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)

        logger.info(f"Created goal {goal.id} for profile {business_profile_id}")
        return self._goal_to_dict(goal)

    async def get_goal(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific goal by ID.
        
        Args:
            goal_id: ID of goal
            
        Returns:
            Goal data or None
        """
        result = await self.db.execute(
            select(CompanyGoal).where(CompanyGoal.id == goal_id)
        )
        goal = result.scalar_one_or_none()

        if not goal:
            return None

        return self._goal_to_dict(goal)

    async def get_goals(
        self,
        business_profile_id: str,
        status: Optional[GoalStatus] = None,
        category: Optional[str] = None,
        priority: Optional[GoalPriority] = None
    ) -> List[Dict[str, Any]]:
        """
        Get goals for a business profile with optional filters.
        
        Args:
            business_profile_id: ID of business profile
            status: Filter by status
            category: Filter by category
            priority: Filter by priority
            
        Returns:
            List of goals
        """
        query = select(CompanyGoal).where(
            CompanyGoal.business_profile_id == business_profile_id
        )

        if status:
            query = query.where(CompanyGoal.status == status)
        if category:
            query = query.where(CompanyGoal.category == category)
        if priority:
            query = query.where(CompanyGoal.priority == priority)

        query = query.order_by(CompanyGoal.created_at.desc())

        result = await self.db.execute(query)
        goals = result.scalars().all()

        return [self._goal_to_dict(goal) for goal in goals]

    async def update_goal(
        self,
        goal_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[GoalPriority] = None,
        progress: Optional[float] = None,
        deadline: Optional[datetime] = None,
        status: Optional[GoalStatus] = None,
        smart_criteria: Optional[Dict[str, Any]] = None,
        bmc_alignment: Optional[Dict[str, Any]] = None,
        milestones: Optional[List[Dict[str, Any]]] = None,
        success_metrics: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a goal.
        
        Args:
            goal_id: ID of goal to update
            title: New title
            description: New description
            category: New category
            priority: New priority
            progress: New progress (0-100)
            deadline: New deadline
            status: New status
            smart_criteria: New SMART criteria
            bmc_alignment: New BMC alignment
            milestones: New milestones
            success_metrics: New success metrics
            
        Returns:
            Updated goal data or None
        """
        result = await self.db.execute(
            select(CompanyGoal).where(CompanyGoal.id == goal_id)
        )
        goal = result.scalar_one_or_none()

        if not goal:
            return None

        # Update fields if provided
        if title is not None:
            goal.title = title
        if description is not None:
            goal.description = description
        if category is not None:
            goal.category = category
        if priority is not None:
            goal.priority = priority
        if progress is not None:
            goal.progress = max(0.0, min(100.0, progress))
        if deadline is not None:
            goal.deadline = deadline
        if status is not None:
            goal.status = status
        if smart_criteria is not None:
            goal.smart_criteria = smart_criteria
        if bmc_alignment is not None:
            goal.bmc_alignment = bmc_alignment
        if milestones is not None:
            goal.milestones = milestones
        if success_metrics is not None:
            goal.success_metrics = success_metrics

        goal.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(goal)

        logger.info(f"Updated goal {goal_id}")
        return self._goal_to_dict(goal)

    async def delete_goal(self, goal_id: str) -> bool:
        """
        Delete a goal.
        
        Args:
            goal_id: ID of goal to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            select(CompanyGoal).where(CompanyGoal.id == goal_id)
        )
        goal = result.scalar_one_or_none()

        if not goal:
            return False

        await self.db.delete(goal)
        await self.db.commit()

        logger.info(f"Deleted goal {goal_id}")
        return True

    async def get_goal_statistics(
        self,
        business_profile_id: str
    ) -> Dict[str, Any]:
        """
        Get goal statistics for a business profile.
        
        Args:
            business_profile_id: ID of business profile
            
        Returns:
            Goal statistics
        """
        goals = await self.get_goals(business_profile_id)

        total_goals = len(goals)
        active_goals = len([g for g in goals if g["status"] == "active"])
        completed_goals = len([g for g in goals if g["status"] == "completed"])
        paused_goals = len([g for g in goals if g["status"] == "paused"])

        # Calculate average progress
        if active_goals > 0:
            avg_progress = sum(g["progress"] for g in goals if g["status"] == "active") / active_goals
        else:
            avg_progress = 0.0

        # Count by category
        by_category = {}
        for goal in goals:
            category = goal.get("category", "uncategorized")
            by_category[category] = by_category.get(category, 0) + 1

        # Count by priority
        by_priority = {
            "high": len([g for g in goals if g["priority"] == "high"]),
            "medium": len([g for g in goals if g["priority"] == "medium"]),
            "low": len([g for g in goals if g["priority"] == "low"])
        }

        return {
            "total_goals": total_goals,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "paused_goals": paused_goals,
            "average_progress": round(avg_progress, 2),
            "by_category": by_category,
            "by_priority": by_priority
        }

    def _goal_to_dict(self, goal: CompanyGoal) -> Dict[str, Any]:
        """Convert goal to dictionary"""
        return {
            "id": goal.id,
            "business_profile_id": goal.business_profile_id,
            "title": goal.title,
            "description": goal.description,
            "category": goal.category,
            "priority": goal.priority.value if goal.priority else None,
            "progress": goal.progress,
            "deadline": goal.deadline.isoformat() if goal.deadline else None,
            "status": goal.status.value if goal.status else None,
            "smart_criteria": goal.smart_criteria,
            "bmc_alignment": goal.bmc_alignment,
            "milestones": goal.milestones,
            "success_metrics": goal.success_metrics,
            "created_at": goal.created_at.isoformat(),
            "updated_at": goal.updated_at.isoformat()
        }
