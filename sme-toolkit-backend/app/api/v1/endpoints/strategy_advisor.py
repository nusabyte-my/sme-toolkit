"""Strategy Advisor API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.strategy_orchestrator import StrategyOrchestrator
from app.schemas.orchestration import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisListResponse
)

router = APIRouter(tags=["Strategy Advisor"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_strategy(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Perform comprehensive strategy analysis using multiple advisors.
    
    This endpoint orchestrates the execution of multiple advisor agents to provide
    a comprehensive analysis of the business strategy.
    
    - **business_profile_id**: ID of the business profile to analyze
    - **analysis_type**: Type of analysis (comprehensive, goals, growth, costing, suggestions)
    - **config**: Optional configuration for which agents to include
    """
    try:
        orchestrator = StrategyOrchestrator(db)
        
        result = await orchestrator.analyze_comprehensive(
            business_profile_id=request.business_profile_id,
            analysis_config=request.config.dict() if request.config else None
        )
        
        return AnalysisResponse(
            id=result["analysis_id"],
            business_profile_id=request.business_profile_id,
            analysis_type=request.analysis_type.value,
            results=result["results"],
            scores=result["scores"],
            insights=result["insights"],
            status="completed",
            created_at=result["results"].get("aggregated_at"),
            updated_at=result["results"].get("aggregated_at")
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing analysis: {str(e)}"
        )


@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific analysis by ID.
    
    Returns the complete analysis results including scores and insights.
    """
    try:
        orchestrator = StrategyOrchestrator(db)
        analysis = await orchestrator.get_analysis(analysis_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
        
        return AnalysisResponse(**analysis)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analysis: {str(e)}"
        )


@router.get("/analysis", response_model=AnalysisListResponse)
async def list_analyses(
    business_profile_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    List all analyses for a business profile.
    
    Returns a paginated list of analyses for the specified business profile.
    """
    try:
        orchestrator = StrategyOrchestrator(db)
        analyses = await orchestrator.list_analyses(
            business_profile_id=business_profile_id,
            limit=limit
        )
        
        return AnalysisListResponse(
            analyses=analyses,
            total=len(analyses)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing analyses: {str(e)}"
        )
