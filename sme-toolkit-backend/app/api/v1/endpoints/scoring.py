"""Scoring API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.scoring_service import ScoringService
from app.schemas.scoring import (
    ScoreRecalculateRequest,
    ScoreResponse,
    ScoreHistoryResponse,
    AllScoresResponse,
    ScoreType
)

router = APIRouter(tags=["Scoring"])


@router.get("/current", response_model=AllScoresResponse)
async def get_current_scores(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current scores for all categories.
    
    Returns the most recent scores for all score types.
    """
    try:
        service = ScoringService(db)
        scores = await service.get_latest_scores(business_profile_id)
        # Get the most recent calculated_at timestamp from any score
        generated_at = None
        if scores:
            for score_data in scores.values():
                if score_data and "calculated_at" in score_data:
                    generated_at = score_data["calculated_at"]
                    break
        return AllScoresResponse(
            business_profile_id=business_profile_id,
            scores=scores,
            generated_at=generated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving current scores: {str(e)}"
        )


@router.get("/history", response_model=ScoreHistoryResponse)
async def get_score_history(
    business_profile_id: str = Query(..., description="Business profile ID"),
    score_type: ScoreType = Query(..., description="Type of score"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical score data for a specific score type.
    
    Returns historical score records for trend analysis.
    """
    try:
        service = ScoringService(db)
        history = await service.get_score_history(
            business_profile_id=business_profile_id,
            score_type=score_type,
            limit=limit
        )
        return ScoreHistoryResponse(
            score_type=score_type.value,
            history=history,
            total=len(history)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving score history: {str(e)}"
        )


@router.get("/{score_type}", response_model=ScoreResponse)
async def get_score_details(
    score_type: ScoreType,
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed breakdown of a specific score.
    
    Returns complete score data including sub-metrics and interpretation.
    """
    try:
        service = ScoringService(db)
        score_data = await service.calculate_score(
            business_profile_id=business_profile_id,
            score_type=score_type
        )
        return ScoreResponse(
            id=score_data.get("id", ""),
            business_profile_id=business_profile_id,
            score_type=score_type.value,
            overall_score=score_data["overall_score"],
            sub_metrics=score_data["sub_metrics"],
            calculated_at=score_data.get("calculated_at")
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving score details: {str(e)}"
        )


@router.post("/recalculate", response_model=AllScoresResponse)
async def recalculate_scores(
    business_profile_id: str = Query(..., description="Business profile ID"),
    request: Optional[ScoreRecalculateRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger score recalculation.
    
    Recalculates specified score types or all if not specified.
    
    - **score_types**: Specific score types to recalculate (all if not provided)
    """
    try:
        service = ScoringService(db)
        
        # Determine which scores to recalculate
        score_types = request.score_types if request else list(ScoreType)
        
        # Recalculate each score type
        scores = {}
        for score_type in score_types:
            try:
                score_data = await service.calculate_score(
                    business_profile_id=business_profile_id,
                    score_type=score_type
                )
                scores[score_type.value] = {
                    "overall_score": score_data["overall_score"],
                    "sub_metrics": score_data["sub_metrics"],
                    "calculated_at": score_data.get("calculated_at")
                }
            except Exception as e:
                # Log error but continue with other scores
                scores[score_type.value] = {
                    "error": str(e)
                }
        
        return AllScoresResponse(
            business_profile_id=business_profile_id,
            scores=scores,
            generated_at=None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recalculating scores: {str(e)}"
        )


@router.get("/benchmarks", response_model=dict)
async def get_score_benchmarks(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get score benchmarks for comparison.
    
    Returns benchmark data for score comparison.
    """
    try:
        from app.database import BusinessProfile
        from sqlalchemy import select
        
        # Load profile to get industry and size
        result = await db.execute(
            select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business profile {business_profile_id} not found"
            )
        
        from app.data.benchmarks import get_benchmarks
        
        # Get benchmarks
        industry = profile.industry or "general"
        business_size = profile.business_stage or "small"
        benchmarks = get_benchmarks(industry, business_size)
        
        return {
            "industry": industry,
            "business_size": business_size,
            "benchmarks": benchmarks
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving score benchmarks: {str(e)}"
        )


@router.get("/trends", response_model=dict)
async def get_score_trends(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get score trends with forecasting.
    
    Returns trend data for all score types.
    """
    try:
        service = ScoringService(db)
        trends = await service.get_score_trends(business_profile_id)
        return trends
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving score trends: {str(e)}"
        )


@router.get("/compare", response_model=dict)
async def compare_scores_with_benchmarks(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare scores with industry benchmarks.
    
    Returns comparison data for all scores.
    """
    try:
        service = ScoringService(db)
        comparison = await service.compare_with_benchmarks(business_profile_id)
        return comparison
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing scores with benchmarks: {str(e)}"
        )
