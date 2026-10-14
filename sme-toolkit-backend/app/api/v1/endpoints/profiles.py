"""Profiles API endpoints for enhanced data profiling"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, SocialMediaProfile
from app.auth import get_current_user
from sqlalchemy import select
from app.services.profile_service import ProfileService
from app.schemas.profiles import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    ProfileCompletionResponse,
    BusinessProfileCreate,
    BusinessProfileUpdate,
    BusinessProfileResponse,
    BusinessEnrichmentResponse,
    BusinessClassificationResponse,
    SocialMediaProfileCreate,
    SocialMediaProfileUpdate,
    SocialMediaProfileResponse,
    SocialMediaMetricsResponse,
    UserActivityLogResponse,
    PrivacySettingsCreate,
    PrivacySettingsUpdate,
    PrivacySettingsResponse,
    ProfileInsightResponse,
    ProfileAnalyticsOverview,
    UserActivityAnalytics,
    ProfileInsightsResponse,
)

async def require_profile_owner(request: Request, actor: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    requested_user = request.query_params.get('user_id')
    if requested_user is not None and requested_user != actor:
        raise HTTPException(403, 'You can only access your own profile.')
    profile_id = request.path_params.get('profile_id')
    if profile_id:
        owned = await db.scalar(select(SocialMediaProfile.id).where(SocialMediaProfile.id == profile_id, SocialMediaProfile.user_id == actor))
        if not owned:
            raise HTTPException(404, 'Profile not found')


router = APIRouter(tags=['Profiles'], dependencies=[Depends(require_profile_owner)])


# ==================== User Profile Endpoints ====================

@router.get("/user", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user profile.
    
    Returns the user profile for the specified user ID.
    """
    try:
        service = ProfileService(db)
        profile = await service.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User profile for user {user_id} not found"
            )
        
        return UserProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profile: {str(e)}"
        )


@router.put("/user", response_model=UserProfileResponse)
async def update_user_profile(
    request: UserProfileUpdate,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile.
    
    Updates the user profile with the provided data.
    Only provided fields will be updated.
    """
    try:
        service = ProfileService(db)
        
        # Convert Pydantic model to dict
        profile_data = request.model_dump(exclude_unset=True)
        
        profile = await service.update_user_profile(user_id, profile_data)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User profile for user {user_id} not found"
            )
        
        return UserProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}"
        )


@router.get("/user/completion", response_model=ProfileCompletionResponse)
async def get_profile_completion(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get profile completion percentage.
    
    Returns the completion percentage, missing fields, and tips.
    """
    try:
        service = ProfileService(db)
        completion = await service.calculate_profile_completion(user_id)
        return ProfileCompletionResponse(**completion)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating profile completion: {str(e)}"
        )


@router.get("/user/export")
async def export_user_profile(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Export profile data.
    
    Returns all profile data including social media, activity, and insights.
    """
    try:
        service = ProfileService(db)
        export_data = await service.export_user_profile(user_id)
        
        if not export_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User profile for user {user_id} not found"
            )
        
        return export_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting user profile: {str(e)}"
        )


# ==================== Business Profile Endpoints ====================

@router.get("/business", response_model=BusinessProfileResponse)
async def get_business_profile(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get business profile.
    
    Returns the business profile for the specified user ID.
    """
    try:
        service = ProfileService(db)
        profile = await service.get_business_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business profile for user {user_id} not found"
            )
        
        return BusinessProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving business profile: {str(e)}"
        )


@router.put("/business", response_model=BusinessProfileResponse)
async def update_business_profile(
    request: BusinessProfileUpdate,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update business profile.
    
    Updates the business profile with the provided data.
    Only provided fields will be updated.
    """
    try:
        service = ProfileService(db)
        
        # Convert Pydantic model to dict
        business_data = request.model_dump(exclude_unset=True)
        
        profile = await service.update_business_profile(user_id, business_data)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business profile for user {user_id} not found"
            )
        
        return BusinessProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating business profile: {str(e)}"
        )


@router.get("/business/enrich", response_model=BusinessEnrichmentResponse)
async def enrich_business_data(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Enrich business data with AI inference.
    
    Returns enriched business data with inferred fields and recommendations.
    """
    try:
        service = ProfileService(db)
        enrichment = await service.enrich_business_data(user_id)
        
        if not enrichment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business profile for user {user_id} not found"
            )
        
        return BusinessEnrichmentResponse(**enrichment)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enriching business data: {str(e)}"
        )


@router.get("/business/classify", response_model=BusinessClassificationResponse)
async def classify_business(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Classify business stage and industry.
    
    Returns business classification with confidence scores.
    """
    try:
        service = ProfileService(db)
        classification = await service.classify_business(user_id)
        
        if not classification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business profile for user {user_id} not found"
            )
        
        return BusinessClassificationResponse(**classification)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error classifying business: {str(e)}"
        )


# ==================== Social Media Endpoints ====================

@router.get("/social", response_model=list[SocialMediaProfileResponse])
async def get_social_media_profiles(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all social media profiles.
    
    Returns all social media profiles for the user.
    """
    try:
        service = ProfileService(db)
        profiles = await service.get_social_media_profiles(user_id)
        return [SocialMediaProfileResponse(**p) for p in profiles]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving social media profiles: {str(e)}"
        )


@router.post("/social", response_model=SocialMediaProfileResponse, status_code=status.HTTP_201_CREATED)
async def add_social_media_profile(
    request: SocialMediaProfileCreate,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Add social media profile.
    
    Creates a new social media profile for the user.
    """
    try:
        service = ProfileService(db)
        
        # Convert Pydantic model to dict
        profile_data = request.model_dump(exclude_unset=True)
        
        profile = await service.add_social_media_profile(user_id, profile_data)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User profile for user {user_id} not found"
            )
        
        return SocialMediaProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding social media profile: {str(e)}"
        )


@router.put("/social/{profile_id}", response_model=SocialMediaProfileResponse)
async def update_social_media_profile(
    profile_id: str,
    request: SocialMediaProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update social media profile.
    
    Updates the social media profile with the provided data.
    """
    try:
        service = ProfileService(db)
        
        # Convert Pydantic model to dict
        profile_data = request.model_dump(exclude_unset=True)
        
        profile = await service.update_social_media_profile(profile_id, profile_data)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Social media profile {profile_id} not found"
            )
        
        return SocialMediaProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating social media profile: {str(e)}"
        )


@router.delete("/social/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_media_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete social media profile.
    
    Permanently deletes a social media profile.
    """
    try:
        service = ProfileService(db)
        success = await service.delete_social_media_profile(profile_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Social media profile {profile_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting social media profile: {str(e)}"
        )


@router.get("/social/{profile_id}/metrics", response_model=SocialMediaMetricsResponse)
async def get_social_media_metrics(
    profile_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get social media metrics.
    
    Returns metrics, trends, insights, and recommendations for a social media profile.
    """
    try:
        service = ProfileService(db)
        metrics = await service.get_social_media_metrics(profile_id)
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Social media profile {profile_id} not found"
            )
        
        return SocialMediaMetricsResponse(**metrics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving social media metrics: {str(e)}"
        )


# ==================== Analytics Endpoints ====================

@router.get("/analytics/overview", response_model=ProfileAnalyticsOverview)
async def get_profile_analytics(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get profile analytics overview.
    
    Returns comprehensive analytics including completion, activity, social media, and insights.
    """
    try:
        service = ProfileService(db)
        analytics = await service.get_profile_analytics(user_id)
        
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User profile for user {user_id} not found"
            )
        
        return ProfileAnalyticsOverview(**analytics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile analytics: {str(e)}"
        )


@router.get("/analytics/activity", response_model=UserActivityAnalytics)
async def get_user_activity_analytics(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of activity logs"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user activity analytics.
    
    Returns activity analytics including sessions, feature usage, and engagement trends.
    """
    try:
        service = ProfileService(db)
        activity_logs = await service.get_user_activity(user_id, limit=limit)
        
        # Calculate analytics from activity logs
        total_sessions = len(activity_logs)
        total_time_spent = sum(log.get("interaction_time", 0) for log in activity_logs)
        
        # Get most used features
        from collections import Counter
        feature_names = [log.get("feature_name", "other") for log in activity_logs]
        most_used_features = [
            {"feature": feature, "count": count}
            for feature, count in Counter(feature_names).most_common(10)
        ]
        
        # Get activity by category
        categories = [log.get("activity_category", "other") for log in activity_logs]
        activity_by_category = dict(Counter(categories))
        
        # Get peak activity times
        hours = [log.get("created_at").hour for log in activity_logs if log.get("created_at")]
        peak_activity_times = [
            {"hour": hour, "count": count}
            for hour, count in Counter(hours).most_common(5)
        ]
        
        # Calculate engagement trend (simplified)
        engagement_trend = [
            {"date": log.get("created_at").date().isoformat(), "activities": 1}
            for log in activity_logs[:30]  # Last 30 activities
        ]
        
        return UserActivityAnalytics(
            user_profile_id=user_id,
            time_range="last_30_days",
            total_sessions=total_sessions,
            total_time_spent=total_time_spent,
            most_used_features=most_used_features,
            activity_by_category=activity_by_category,
            peak_activity_times=peak_activity_times,
            engagement_trend=engagement_trend
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user activity analytics: {str(e)}"
        )


@router.get("/analytics/insights", response_model=ProfileInsightsResponse)
async def get_profile_insights(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated insights.
    
    Returns stored insights for the user including unread and high priority counts.
    """
    try:
        service = ProfileService(db)
        insights = await service.get_profile_insights(user_id)
        
        # Calculate statistics
        total = len(insights)
        unread_count = len([i for i in insights if i.get("status") == "new"])
        high_priority_count = len([i for i in insights if i.get("priority") == "high"])
        
        # Count by category
        from collections import Counter
        categories = [i.get("insight_category", "other") for i in insights]
        categories_dict = dict(Counter(categories))
        
        return ProfileInsightsResponse(
            insights=insights,
            total=total,
            unread_count=unread_count,
            high_priority_count=high_priority_count,
            categories=categories_dict
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile insights: {str(e)}"
        )


@router.post("/analytics/insights/generate", response_model=list[dict])
async def generate_profile_insights(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI insights for profile.
    
    Triggers AI insight generation based on profile data.
    """
    try:
        service = ProfileService(db)
        insights = await service.generate_profile_insights(user_id)
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating profile insights: {str(e)}"
        )


# ==================== Privacy Settings Endpoints ====================

@router.get("/privacy", response_model=PrivacySettingsResponse)
async def get_privacy_settings(
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get privacy settings.
    
    Returns privacy settings for the user.
    """
    try:
        service = ProfileService(db)
        settings = await service.get_privacy_settings(user_id)
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Privacy settings for user {user_id} not found"
            )
        
        return PrivacySettingsResponse(**settings)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving privacy settings: {str(e)}"
        )


@router.put("/privacy", response_model=PrivacySettingsResponse)
async def update_privacy_settings(
    request: PrivacySettingsUpdate,
    user_id: str = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update privacy settings.
    
    Updates privacy settings with the provided data.
    """
    try:
        service = ProfileService(db)
        
        # Convert Pydantic model to dict
        settings_data = request.model_dump(exclude_unset=True)
        
        settings = await service.update_privacy_settings(user_id, settings_data)
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Privacy settings for user {user_id} not found"
            )
        
        return PrivacySettingsResponse(**settings)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating privacy settings: {str(e)}"
        )
