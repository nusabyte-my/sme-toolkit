"""Costing Analysis API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.costing_service import CostingService
from app.schemas.costing import (
    CostingAnalysisCreate,
    CostingAnalysisResponse,
    CostingAnalysisListResponse,
    CostSummary
)

router = APIRouter(tags=["Costing"])


@router.post("/analyze", response_model=CostingAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_costing(
    request: CostingAnalysisCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze costs and pricing.
    
    Creates a comprehensive costing analysis including cost structure,
    pricing strategies, optimization opportunities, and break-even analysis.
    
    - **cost_structure**: Fixed and variable costs breakdown (required)
    - **pricing_strategies**: Pricing recommendations (optional)
    - **optimization_opportunities**: Cost-saving opportunities (optional)
    - **break_even_analysis**: Break-even calculations (optional)
    """
    try:
        service = CostingService(db)
        analysis = await service.create_costing_analysis(
            business_profile_id=request.business_profile_id,
            cost_structure=request.cost_structure.dict(),
            pricing_strategies=[s.dict() for s in request.pricing_strategies] if request.pricing_strategies else None,
            optimization_opportunities=[o.dict() for o in request.optimization_opportunities] if request.optimization_opportunities else None,
            break_even_analysis=request.break_even_analysis.dict() if request.break_even_analysis else None
        )
        return CostingAnalysisResponse(**analysis)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating costing analysis: {str(e)}"
        )


@router.get("", response_model=CostingAnalysisListResponse)
async def get_costing_analyses(
    business_profile_id: str = Query(..., description="Business profile ID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of analyses to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get costing analyses for a business profile.
    
    Returns a paginated list of costing analyses.
    """
    try:
        service = CostingService(db)
        analyses = await service.get_costing_analyses(
            business_profile_id=business_profile_id,
            limit=limit
        )
        return CostingAnalysisListResponse(
            analyses=analyses,
            total=len(analyses)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving costing analyses: {str(e)}"
        )


@router.get("/{analysis_id}", response_model=CostingAnalysisResponse)
async def get_costing_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific costing analysis by ID.
    
    Returns complete costing analysis details.
    """
    try:
        service = CostingService(db)
        analysis = await service.get_costing_analysis(analysis_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Costing analysis {analysis_id} not found"
            )
        
        return CostingAnalysisResponse(**analysis)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving costing analysis: {str(e)}"
        )


@router.get("/latest", response_model=CostingAnalysisResponse)
async def get_latest_costing_analysis(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent costing analysis for a business profile.
    
    Returns the latest costing analysis if one exists.
    """
    try:
        service = CostingService(db)
        analysis = await service.get_latest_costing_analysis(business_profile_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No costing analysis found"
            )
        
        return CostingAnalysisResponse(**analysis)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving latest costing analysis: {str(e)}"
        )


@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cost summary from latest analysis.
    
    Returns a summary of costs including fixed, variable, and total costs.
    """
    try:
        service = CostingService(db)
        summary = await service.get_cost_summary(business_profile_id)
        return CostSummary(**summary)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cost summary: {str(e)}"
        )


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_costing_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a costing analysis.
    
    Permanently deletes a costing analysis.
    """
    try:
        service = CostingService(db)
        success = await service.delete_costing_analysis(analysis_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Costing analysis {analysis_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting costing analysis: {str(e)}"
        )
