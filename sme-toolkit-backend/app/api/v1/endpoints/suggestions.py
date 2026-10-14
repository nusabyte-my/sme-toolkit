"""Business Suggestions API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.suggestion_service import SuggestionService
from app.schemas.suggestions import (
    SuggestionCreate,
    SuggestionUpdate,
    SuggestionResponse,
    SuggestionListResponse,
    SuggestionStatistics,
    SuggestionType,
    SuggestionStatus
)

router = APIRouter(tags=["Suggestions"])


@router.post("", response_model=SuggestionResponse, status_code=status.HTTP_201_CREATED)
async def create_suggestion(
    request: SuggestionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new business suggestion.
    
    Creates a business opportunity suggestion with type, title, description,
    potential value, and feasibility score.
    
    - **suggestion_type**: Type of suggestion (required)
    - **title**: Suggestion title (required)
    - **description**: Suggestion description (optional)
    - **potential_value**: Estimated value (optional)
    - **feasibility_score**: Feasibility score 0-1 (optional)
    - **suggestion_data**: Detailed suggestion data (optional)
    - **status**: Suggestion status (default: suggested)
    """
    try:
        service = SuggestionService(db)
        suggestion = await service.create_suggestion(
            business_profile_id=request.business_profile_id,
            suggestion_type=request.suggestion_type.value,
            title=request.title,
            description=request.description,
            potential_value=request.potential_value,
            feasibility_score=request.feasibility_score,
            suggestion_data=request.suggestion_data,
            status=request.status
        )
        return SuggestionResponse(**suggestion)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating suggestion: {str(e)}"
        )


@router.get("", response_model=SuggestionListResponse)
async def get_suggestions(
    business_profile_id: str = Query(..., description="Business profile ID"),
    suggestion_type: Optional[SuggestionType] = Query(None, description="Filter by suggestion type"),
    status: Optional[SuggestionStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of suggestions to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get suggestions for a business profile.
    
    Returns a list of suggestions with optional filtering by type or status.
    """
    try:
        service = SuggestionService(db)
        suggestions = await service.get_suggestions(
            business_profile_id=business_profile_id,
            suggestion_type=suggestion_type.value if suggestion_type else None,
            status=status,
            limit=limit
        )
        return SuggestionListResponse(
            suggestions=suggestions,
            total=len(suggestions)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving suggestions: {str(e)}"
        )


@router.get("/{suggestion_id}", response_model=SuggestionResponse)
async def get_suggestion(
    suggestion_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific suggestion by ID.
    
    Returns complete suggestion details.
    """
    try:
        service = SuggestionService(db)
        suggestion = await service.get_suggestion(suggestion_id)
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suggestion {suggestion_id} not found"
            )
        
        return SuggestionResponse(**suggestion)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving suggestion: {str(e)}"
        )


@router.put("/{suggestion_id}", response_model=SuggestionResponse)
async def update_suggestion(
    suggestion_id: str,
    request: SuggestionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a suggestion.
    
    Updates suggestion fields. Only provided fields will be updated.
    """
    try:
        service = SuggestionService(db)
        suggestion = await service.update_suggestion(
            suggestion_id=suggestion_id,
            title=request.title,
            description=request.description,
            potential_value=request.potential_value,
            feasibility_score=request.feasibility_score,
            status=request.status,
            suggestion_data=request.suggestion_data
        )
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suggestion {suggestion_id} not found"
            )
        
        return SuggestionResponse(**suggestion)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating suggestion: {str(e)}"
        )


@router.delete("/{suggestion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_suggestion(
    suggestion_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a suggestion.
    
    Permanently deletes a suggestion.
    """
    try:
        service = SuggestionService(db)
        success = await service.delete_suggestion(suggestion_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suggestion {suggestion_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting suggestion: {str(e)}"
        )


@router.get("/by-type", response_model=dict)
async def get_suggestions_by_type(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get suggestions grouped by type.
    
    Returns suggestions organized by suggestion type.
    """
    try:
        service = SuggestionService(db)
        grouped = await service.get_suggestions_by_type(business_profile_id)
        return grouped
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving suggestions by type: {str(e)}"
        )


@router.get("/top", response_model=SuggestionListResponse)
async def get_top_suggestions(
    business_profile_id: str = Query(..., description="Business profile ID"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top suggestions based on feasibility score and potential value.
    
    Returns the highest-rated suggestions.
    """
    try:
        service = SuggestionService(db)
        suggestions = await service.get_top_suggestions(
            business_profile_id=business_profile_id,
            limit=limit
        )
        return SuggestionListResponse(
            suggestions=suggestions,
            total=len(suggestions)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving top suggestions: {str(e)}"
        )


@router.get("/statistics", response_model=SuggestionStatistics)
async def get_suggestion_statistics(
    business_profile_id: str = Query(..., description="Business profile ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get suggestion statistics for a business profile.
    
    Returns comprehensive statistics including total suggestions, breakdown by
    status and type, total potential value, and average feasibility.
    """
    try:
        service = SuggestionService(db)
        stats = await service.get_suggestion_statistics(business_profile_id)
        return SuggestionStatistics(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving suggestion statistics: {str(e)}"
        )
