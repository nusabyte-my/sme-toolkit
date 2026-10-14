"""Goals API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.goal_service import GoalService
from app.schemas.goals import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalListResponse,
    GoalStatistics,
    GoalPriority,
    GoalStatus
)

router = APIRouter(tags=["Goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    request: GoalCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new goal.
    
    Creates a new strategic goal with optional SMART criteria, BMC alignment,
    milestones, and success metrics.
    
    - **title**: Goal title (required)
    - **description**: Goal description (optional)
    - **category**: Goal category (financial, operational, market, innovation)
    - **priority**: Goal priority (high, medium, low)
    - **deadline**: Goal deadline (optional)
    - **smart_criteria**: SMART criteria breakdown (optional)
    - **bmc_alignment**: Alignment with BMC blocks (optional)
    - **milestones**: Goal milestones (optional)
    - **success_metrics**: Success metrics (optional)
    """
    try:
        service = GoalService(db)
        goal = await service.create_goal(
            business_profile_id=request.business_profile_id,
            title=request.title,
            description=request.description,
            category=request.category,
            priority=request.priority,
            deadline=request.deadline,
            smart_criteria=request.smart_criteria.dict() if request.smart_criteria else None,
            bmc_alignment=request.bmc_alignment.dict() if request.bmc_alignment else None,
            milestones=[m.dict() for m in request.milestones] if request.milestones else None,
            success_metrics=request.success_metrics
        )
        return GoalResponse(**goal)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating goal: {str(e)}"
        )


@router.get("", response_model=GoalListResponse)
async def get_goals(
    business_profile_id: str = Query(..., description="Business profile ID"),
    status: Optional[GoalStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[GoalPriority] = Query(None, description="Filter by priority"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get goals for a business profile.
    
    Returns a list of goals with optional filtering by status, category, or priority.
    """
    try:
        service = GoalService(db)
        goals = await service.get_goals(
            business_profile_id=business_profile_id,
            status=status,
            category=category,
            priority=priority
        )
        return GoalListResponse(
            goals=goals,
            total=len(goals)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving goals: {str(e)}"
        )


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific goal by ID.
    
    Returns complete goal details including SMART criteria, BMC alignment,
    milestones, and success metrics.
    """
    try:
        service = GoalService(db)
        goal = await service.get_goal(goal_id)
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Goal {goal_id} not found"
            )
        
        return GoalResponse(**goal)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving goal: {str(e)}"
        )


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    request: GoalUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a goal.
    
    Updates goal fields. Only provided fields will be updated.
    """
    try:
        service = GoalService(db)
        goal = await service.update_goal(
            goal_id=goal_id,
            title=request.title,
            description=request.description,
            category=request.category,
            priority=request.priority,
            progress=request.progress,
            deadline=request.deadline,
            status=request.status,
            smart_criteria=request.smart_criteria.dict() if request.smart_criteria else None,
            bmc_alignment=request.bmc_alignment.dict() if request.bmc_alignment else None,
            milestones=[m.dict() for m in request.milestones] if request.milestones else None,
            success_metrics=request.success_metrics
        )
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Goal {goal_id} not found"
            )
        
        return GoalResponse(**goal)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating goal: {str(e)}"
        )


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a goal.
    
    Permanently deletes a goal and all associated data.
    """
    try:
        service = GoalService(db)
        success = await service.delete_goal(goal_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Goal {goal_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting goal: {str(e)}"
        )


@router.get("/statistics", response_model=GoalStatistics)
async def get_goal_statistics(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get goal statistics for a business profile.
    
    Returns comprehensive statistics including total goals, breakdown by status,
    category, and priority.
    """
    try:
        service = GoalService(db)
        stats = await service.get_goal_statistics(business_profile_id)
        return GoalStatistics(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving goal statistics: {str(e)}"
        )
