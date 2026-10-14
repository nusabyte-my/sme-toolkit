"""Suggestion Service - Manage business suggestion operations"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import (
    BusinessProfile,
    BusinessSuggestion,
    SuggestionStatus
)

logger = logging.getLogger(__name__)


class SuggestionService:
    """
    Service for managing business suggestions.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_suggestion(
        self,
        business_profile_id: str,
        suggestion_type: str,
        title: str,
        description: Optional[str] = None,
        potential_value: Optional[float] = None,
        feasibility_score: Optional[float] = None,
        suggestion_data: Optional[Dict[str, Any]] = None,
        status: SuggestionStatus = SuggestionStatus.SUGGESTED
    ) -> Dict[str, Any]:
        """
        Create a new business suggestion.
        
        Args:
            business_profile_id: ID of business profile
            suggestion_type: Type of suggestion (new_revenue_stream, partnership, market_expansion, product_innovation)
            title: Suggestion title
            description: Suggestion description
            potential_value: Estimated value
            feasibility_score: Feasibility score (0-1)
            suggestion_data: Detailed suggestion data
            status: Suggestion status
            
        Returns:
            Created suggestion data
        """
        # Verify business profile exists
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.id == business_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Business profile {business_profile_id} not found")

        # Create suggestion
        suggestion = BusinessSuggestion(
            id=str(uuid.uuid4()),
            business_profile_id=business_profile_id,
            suggestion_type=suggestion_type,
            title=title,
            description=description,
            potential_value=potential_value,
            feasibility_score=feasibility_score,
            status=status,
            suggestion_data=suggestion_data,
            created_at=datetime.utcnow()
        )

        self.db.add(suggestion)
        await self.db.commit()
        await self.db.refresh(suggestion)

        logger.info(f"Created suggestion {suggestion.id} for profile {business_profile_id}")
        return self._suggestion_to_dict(suggestion)

    async def get_suggestion(self, suggestion_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific suggestion by ID.
        
        Args:
            suggestion_id: ID of suggestion
            
        Returns:
            Suggestion data or None
        """
        result = await self.db.execute(
            select(BusinessSuggestion).where(BusinessSuggestion.id == suggestion_id)
        )
        suggestion = result.scalar_one_or_none()

        if not suggestion:
            return None

        return self._suggestion_to_dict(suggestion)

    async def get_suggestions(
        self,
        business_profile_id: str,
        suggestion_type: Optional[str] = None,
        status: Optional[SuggestionStatus] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get suggestions for a business profile.
        
        Args:
            business_profile_id: ID of business profile
            suggestion_type: Filter by suggestion type
            status: Filter by status
            limit: Maximum number of suggestions to return
            
        Returns:
            List of suggestions
        """
        query = select(BusinessSuggestion).where(
            BusinessSuggestion.business_profile_id == business_profile_id
        )

        if suggestion_type:
            query = query.where(BusinessSuggestion.suggestion_type == suggestion_type)
        if status:
            query = query.where(BusinessSuggestion.status == status)

        query = query.order_by(BusinessSuggestion.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        suggestions = result.scalars().all()

        return [self._suggestion_to_dict(suggestion) for suggestion in suggestions]

    async def update_suggestion(
        self,
        suggestion_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        potential_value: Optional[float] = None,
        feasibility_score: Optional[float] = None,
        status: Optional[SuggestionStatus] = None,
        suggestion_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a suggestion.
        
        Args:
            suggestion_id: ID of suggestion to update
            title: New title
            description: New description
            potential_value: New potential value
            feasibility_score: New feasibility score
            status: New status
            suggestion_data: New suggestion data
            
        Returns:
            Updated suggestion data or None
        """
        result = await self.db.execute(
            select(BusinessSuggestion).where(BusinessSuggestion.id == suggestion_id)
        )
        suggestion = result.scalar_one_or_none()

        if not suggestion:
            return None

        # Update fields if provided
        if title is not None:
            suggestion.title = title
        if description is not None:
            suggestion.description = description
        if potential_value is not None:
            suggestion.potential_value = potential_value
        if feasibility_score is not None:
            suggestion.feasibility_score = feasibility_score
        if status is not None:
            suggestion.status = status
        if suggestion_data is not None:
            suggestion.suggestion_data = suggestion_data

        await self.db.commit()
        await self.db.refresh(suggestion)

        logger.info(f"Updated suggestion {suggestion_id}")
        return self._suggestion_to_dict(suggestion)

    async def delete_suggestion(self, suggestion_id: str) -> bool:
        """
        Delete a suggestion.
        
        Args:
            suggestion_id: ID of suggestion to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            select(BusinessSuggestion).where(BusinessSuggestion.id == suggestion_id)
        )
        suggestion = result.scalar_one_or_none()

        if not suggestion:
            return False

        await self.db.delete(suggestion)
        await self.db.commit()

        logger.info(f"Deleted suggestion {suggestion_id}")
        return True

    async def get_suggestions_by_type(
        self,
        business_profile_id: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get suggestions grouped by type.
        
        Args:
            business_profile_id: ID of business profile
            
        Returns:
            Dictionary of suggestions grouped by type
        """
        suggestions = await self.get_suggestions(business_profile_id)

        grouped = {}
        for suggestion in suggestions:
            suggestion_type = suggestion.get("suggestion_type", "other")
            if suggestion_type not in grouped:
                grouped[suggestion_type] = []
            grouped[suggestion_type].append(suggestion)

        return grouped

    async def get_top_suggestions(
        self,
        business_profile_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top suggestions based on feasibility score and potential value.
        
        Args:
            business_profile_id: ID of business profile
            limit: Maximum number of suggestions to return
            
        Returns:
            List of top suggestions
        """
        result = await self.db.execute(
            select(BusinessSuggestion)
            .where(BusinessSuggestion.business_profile_id == business_profile_id)
            .where(BusinessSuggestion.status == SuggestionStatus.SUGGESTED)
            .order_by(BusinessSuggestion.feasibility_score.desc())
            .limit(limit)
        )
        suggestions = result.scalars().all()

        return [self._suggestion_to_dict(suggestion) for suggestion in suggestions]

    async def get_suggestion_statistics(
        self,
        business_profile_id: str
    ) -> Dict[str, Any]:
        """
        Get suggestion statistics for a business profile.
        
        Args:
            business_profile_id: ID of business profile
            
        Returns:
            Suggestion statistics
        """
        suggestions = await self.get_suggestions(business_profile_id)

        total_suggestions = len(suggestions)
        by_status = {}
        by_type = {}
        total_potential_value = 0.0
        avg_feasibility = 0.0

        for suggestion in suggestions:
            # Count by status
            status = suggestion.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

            # Count by type
            suggestion_type = suggestion.get("suggestion_type", "other")
            by_type[suggestion_type] = by_type.get(suggestion_type, 0) + 1

            # Sum potential value
            potential_value = suggestion.get("potential_value")
            if potential_value is not None:
                total_potential_value += potential_value

            # Average feasibility
            feasibility = suggestion.get("feasibility_score")
            if feasibility is not None:
                avg_feasibility += feasibility

        if total_suggestions > 0:
            avg_feasibility = avg_feasibility / total_suggestions

        return {
            "total_suggestions": total_suggestions,
            "by_status": by_status,
            "by_type": by_type,
            "total_potential_value": round(total_potential_value, 2),
            "average_feasibility": round(avg_feasibility, 2)
        }

    def _suggestion_to_dict(self, suggestion: BusinessSuggestion) -> Dict[str, Any]:
        """Convert suggestion to dictionary"""
        return {
            "id": suggestion.id,
            "business_profile_id": suggestion.business_profile_id,
            "suggestion_type": suggestion.suggestion_type,
            "title": suggestion.title,
            "description": suggestion.description,
            "potential_value": suggestion.potential_value,
            "feasibility_score": suggestion.feasibility_score,
            "status": suggestion.status.value if suggestion.status else None,
            "suggestion_data": suggestion.suggestion_data,
            "created_at": suggestion.created_at.isoformat()
        }
