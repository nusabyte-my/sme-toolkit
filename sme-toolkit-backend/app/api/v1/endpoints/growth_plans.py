"""Growth Plans API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.growth_service import GrowthService
from app.schemas.growth import (
    GrowthPlanCreate,
    GrowthPlanUpdate,
    GrowthPlanResponse,
    GrowthPlanListResponse
)

router = APIRouter(tags=["Growth Plans"])


@router.post("", response_model=GrowthPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_growth_plan(
    request: GrowthPlanCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new growth plan.
    
    Creates a comprehensive growth strategy with opportunities, channels,
    implementation roadmap, and KPI targets.
    
    - **title**: Plan title (required)
    - **timeframe**: Plan timeframe (e.g., "6 months", "1 year")
    - **plan_data**: Complete growth plan data (required)
    - **status**: Plan status (default: draft)
    """
    try:
        service = GrowthService(db)
        plan = await service.create_growth_plan(
            business_profile_id=request.business_profile_id,
            title=request.title,
            timeframe=request.timeframe,
            plan_data=request.plan_data.dict(),
            status=request.status
        )
        return GrowthPlanResponse(**plan)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating growth plan: {str(e)}"
        )


@router.get("", response_model=GrowthPlanListResponse)
async def get_growth_plans(
    business_profile_id: str = Query(..., description="Business profile ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get growth plans for a business profile.
    
    Returns a list of growth plans with optional filtering by status.
    """
    try:
        service = GrowthService(db)
        plans = await service.get_growth_plans(
            business_profile_id=business_profile_id,
            status=status
        )
        return GrowthPlanListResponse(
            plans=plans,
            total=len(plans)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving growth plans: {str(e)}"
        )


@router.get("/{plan_id}", response_model=GrowthPlanResponse)
async def get_growth_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific growth plan by ID.
    
    Returns complete growth plan details including opportunities, channels,
    roadmap, and KPI targets.
    """
    try:
        service = GrowthService(db)
        plan = await service.get_growth_plan(plan_id)
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Growth plan {plan_id} not found"
            )
        
        return GrowthPlanResponse(**plan)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving growth plan: {str(e)}"
        )


@router.get("/active", response_model=GrowthPlanResponse)
async def get_active_growth_plan(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the active growth plan for a business profile.
    
    Returns the currently active growth plan if one exists.
    """
    try:
        service = GrowthService(db)
        plan = await service.get_active_growth_plan(business_profile_id)
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active growth plan found"
            )
        
        return GrowthPlanResponse(**plan)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving active growth plan: {str(e)}"
        )


@router.put("/{plan_id}", response_model=GrowthPlanResponse)
async def update_growth_plan(
    plan_id: str,
    request: GrowthPlanUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a growth plan.
    
    Updates growth plan fields. Only provided fields will be updated.
    """
    try:
        service = GrowthService(db)
        plan = await service.update_growth_plan(
            plan_id=plan_id,
            title=request.title,
            timeframe=request.timeframe,
            plan_data=request.plan_data.dict() if request.plan_data else None,
            status=request.status
        )
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Growth plan {plan_id} not found"
            )
        
        return GrowthPlanResponse(**plan)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating growth plan: {str(e)}"
        )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_growth_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a growth plan.
    
    Permanently deletes a growth plan and all associated data.
    """
    try:
        service = GrowthService(db)
        success = await service.delete_growth_plan(plan_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Growth plan {plan_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting growth plan: {str(e)}"
        )
