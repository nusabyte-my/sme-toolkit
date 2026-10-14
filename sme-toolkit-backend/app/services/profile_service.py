"""Profile Service - Manage profile-related operations"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import (
    UserProfile,
    BusinessProfile,
    SocialMediaProfile,
    UserActivityLog,
    PrivacySetting,
    ProfileInsight,
)

logger = logging.getLogger(__name__)


class ProfileService:
    """
    Service for managing user and business profiles.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== User Profile Methods ====================

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile by user_id.

        Args:
            user_id: User ID

        Returns:
            User profile data or None
        """
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return None

        return self._user_profile_to_dict(profile)

    async def create_user_profile(
        self, user_id: str, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new user profile.

        Args:
            user_id: User ID
            profile_data: Profile data

        Returns:
            Created profile data
        """
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            **profile_data,
            profile_completion_percentage=0,
            last_profile_update=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        # Create default privacy settings
        await self._create_default_privacy_settings(profile.id)

        logger.info(f"Created user profile for user {user_id}")
        return self._user_profile_to_dict(profile)

    async def update_user_profile(
        self, user_id: str, profile_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update user profile.

        Args:
            user_id: User ID
            profile_data: Profile data to update

        Returns:
            Updated profile data or None
        """
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return None

        # Update fields
        for key, value in profile_data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)

        # Update full name if first or last name changed
        if "first_name" in profile_data or "last_name" in profile_data:
            profile.full_name = (
                f"{profile.first_name or ''} {profile.last_name or ''}".strip()
            )

        profile.last_profile_update = datetime.utcnow()
        profile.updated_at = datetime.utcnow()

        # Recalculate completion percentage
        profile.profile_completion_percentage = self._calculate_profile_completion(
            profile
        )

        await self.db.commit()
        await self.db.refresh(profile)

        logger.info(f"Updated user profile for user {user_id}")
        return self._user_profile_to_dict(profile)

    async def calculate_profile_completion(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate profile completion percentage.

        Args:
            user_id: User ID

        Returns:
            Completion data with percentage, missing fields, and tips
        """
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return {
                "profile_id": "",
                "completion_percentage": 0,
                "missing_fields": [],
                "recommended_fields": [],
                "completion_tips": [],
            }

        completion_percentage = self._calculate_profile_completion(profile)
        missing_fields = self._get_missing_fields(profile)
        recommended_fields = self._get_recommended_fields(profile)
        completion_tips = self._get_completion_tips(completion_percentage)

        return {
            "profile_id": profile.id,
            "completion_percentage": completion_percentage,
            "missing_fields": missing_fields,
            "recommended_fields": recommended_fields,
            "completion_tips": completion_tips,
        }

    async def export_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Export user profile data.

        Args:
            user_id: User ID

        Returns:
            Exported profile data or None
        """
        profile = await self.get_user_profile(user_id)

        if not profile:
            return None

        # Get related data
        social_media = await self.get_social_media_profiles(user_id)
        activity_logs = await self.get_user_activity(user_id, limit=100)
        privacy_settings = await self.get_privacy_settings(user_id)
        insights = await self.get_profile_insights(user_id)

        return {
            "user_profile": profile,
            "social_media_profiles": social_media,
            "recent_activity": activity_logs,
            "privacy_settings": privacy_settings,
            "insights": insights,
            "exported_at": datetime.utcnow().isoformat(),
        }

    # ==================== Business Profile Methods ====================

    async def get_business_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve business profile by user_id.

        Args:
            user_id: User ID

        Returns:
            Business profile data or None
        """
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return None

        return self._business_profile_to_dict(profile)

    async def create_business_profile(
        self, user_id: str, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new business profile.

        Args:
            user_id: User ID
            profile_data: Business profile data

        Returns:
            Created business profile data
        """
        profile = BusinessProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            **profile_data,
            profile_completeness_score=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        # Update user profile to link to this business
        await self._link_user_to_business(user_id, profile.id)

        logger.info(f"Created business profile for user {user_id}")
        return self._business_profile_to_dict(profile)

    async def update_business_profile(
        self, user_id: str, business_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update business profile.

        Args:
            user_id: User ID
            business_data: Business data to update

        Returns:
            Updated business profile data or None
        """
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return None

        # Update fields
        for key, value in profile_data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)

        # Update connection status if API key is provided
        if "sync_settings" in profile_data:
            sync_settings = profile_data["sync_settings"] or {}
            if sync_settings.get("api_key"):
                profile.is_connected = "true"
                profile.sync_status = "synced"

        profile.updated_at = datetime.utcnow()

        # Recalculate completeness score
        profile.profile_completeness_score = self._calculate_business_completeness(
            profile
        )

        await self.db.commit()
        await self.db.refresh(profile)

        logger.info(f"Updated business profile for user {user_id}")
        return self._business_profile_to_dict(profile)

    async def enrich_business_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Enrich business data with AI inference (placeholder).

        Args:
            user_id: User ID

        Returns:
            Enrichment data or None
        """
        profile = await self.get_business_profile(user_id)

        if not profile:
            return None

        # Placeholder for AI enrichment
        # In production, this would call AI services to infer:
        # - Business stage from revenue, team size, years in business
        # - Industry from description and products/services
        # - Market segments from target market data

        enriched_fields = {
            "inferred_stage": "growth",
            "inferred_industry": profile.get("industry", "unknown"),
            "market_segments": profile.get("target_market", []),
            "competitive_position": "emerging",
        }

        confidence_scores = {
            "stage_confidence": 0.75,
            "industry_confidence": 0.85,
            "market_confidence": 0.70,
        }

        recommendations = [
            "Consider expanding your digital presence",
            "Focus on customer retention strategies",
            "Explore partnership opportunities",
        ]

        return {
            "profile_id": profile["id"],
            "enriched_fields": enriched_fields,
            "inferred_business_stage": enriched_fields["inferred_stage"],
            "inferred_industry": enriched_fields["inferred_industry"],
            "confidence_scores": confidence_scores,
            "recommendations": recommendations,
        }

    async def classify_business(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Classify business stage and industry (placeholder).

        Args:
            user_id: User ID

        Returns:
            Classification data or None
        """
        profile = await self.get_business_profile(user_id)

        if not profile:
            return None

        # Placeholder for business classification
        # In production, this would use ML models to classify

        business_stage = profile.get("business_stage", "startup")
        industry = profile.get("industry", "other")
        business_type = profile.get("business_type", "sole_proprietorship")

        confidence_score = 0.80

        classification_details = {
            "revenue_based_stage": self._infer_stage_from_revenue(
                profile.get("annual_revenue")
            ),
            "team_based_stage": self._infer_stage_from_team(profile.get("team_size")),
            "industry_keywords": self._extract_industry_keywords(
                profile.get("business_description", "")
            ),
            "business_maturity": "early",
        }

        return {
            "profile_id": profile["id"],
            "business_stage": business_stage,
            "industry": industry,
            "business_type": business_type,
            "confidence_score": confidence_score,
            "classification_details": classification_details,
        }

    # ==================== Social Media Methods ====================

    async def get_social_media_profiles(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all social media profiles for a user.

        Args:
            user_id: User ID

        Returns:
            List of social media profiles
        """
        # Get user profile first
        user_profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        user_profile = user_profile_result.scalar_one_or_none()

        if not user_profile:
            return []

        # Get social media profiles
        result = await self.db.execute(
            select(SocialMediaProfile)
            .where(SocialMediaProfile.user_profile_id == user_profile.id)
            .order_by(SocialMediaProfile.created_at.desc())
        )
        profiles = result.scalars().all()

        return [self._social_media_profile_to_dict(p) for p in profiles]

    async def add_social_media_profile(
        self, user_id: str, profile_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Add a social media profile.

        Args:
            user_id: User ID
            profile_data: Social media profile data

        Returns:
            Created social media profile or None
        """
        # Get user profile
        user_profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        user_profile = user_profile_result.scalar_one_or_none()

        if not user_profile:
            return None

        # Get business profile
        business_profile_result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.user_id == user_id)
        )
        business_profile = business_profile_result.scalar_one_or_none()

        # Check if API key is provided to set connection status
        sync_settings = profile_data.get("sync_settings", {})
        is_connected = (
            "true" if sync_settings and sync_settings.get("api_key") else "false"
        )
        sync_status = "synced" if is_connected == "true" else "not_synced"

        profile = SocialMediaProfile(
            id=str(uuid.uuid4()),
            user_profile_id=user_profile.id,
            business_profile_id=business_profile.id if business_profile else None,
            **profile_data,
            is_connected=is_connected,
            sync_status=sync_status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        logger.info(f"Added social media profile for user {user_id}")
        return self._social_media_profile_to_dict(profile)

    async def update_social_media_profile(
        self, profile_id: str, profile_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a social media profile.

        Args:
            profile_id: Social media profile ID
            profile_data: Profile data to update

        Returns:
            Updated profile or None
        """
        result = await self.db.execute(
            select(SocialMediaProfile).where(SocialMediaProfile.id == profile_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return None

        # Update fields
        for key, value in profile_data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)

        profile.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(profile)

        logger.info(f"Updated social media profile {profile_id}")
        return self._social_media_profile_to_dict(profile)

    async def delete_social_media_profile(self, profile_id: str) -> bool:
        """
        Delete a social media profile.

        Args:
            profile_id: Social media profile ID

        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            select(SocialMediaProfile).where(SocialMediaProfile.id == profile_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return False

        await self.db.delete(profile)
        await self.db.commit()

        logger.info(f"Deleted social media profile {profile_id}")
        return True

    async def get_social_media_metrics(
        self, profile_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get social media metrics for a profile (placeholder).

        Args:
            profile_id: Social media profile ID

        Returns:
            Metrics data or None
        """
        result = await self.db.execute(
            select(SocialMediaProfile).where(SocialMediaProfile.id == profile_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return None

        # Placeholder for metrics calculation
        # In production, this would analyze historical metrics and calculate trends

        current_metrics = profile.metrics or {}
        historical_trends = profile.historical_metrics or []

        performance_rating = self._calculate_performance_rating(current_metrics)
        insights = self._generate_social_media_insights(current_metrics)
        recommendations = self._generate_social_media_recommendations(current_metrics)

        return {
            "profile_id": profile.id,
            "platform_name": profile.platform_name,
            "current_metrics": current_metrics,
            "historical_trends": historical_trends,
            "performance_rating": performance_rating,
            "insights": insights,
            "recommendations": recommendations,
            "benchmark_comparison": None,
        }

    # ==================== Analytics Methods ====================

    async def get_profile_analytics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive profile analytics.

        Args:
            user_id: User ID

        Returns:
            Analytics data or None
        """
        user_profile = await self.get_user_profile(user_id)
        if not user_profile:
            return None

        business_profile = await self.get_business_profile(user_id)
        social_media = await self.get_social_media_profiles(user_id)
        activity_logs = await self.get_user_activity(user_id, limit=50)
        insights = await self.get_profile_insights(user_id)

        # Calculate completion
        completion_data = await self.calculate_profile_completion(user_id)

        # Activity summary
        activity_summary = {
            "total_activities": len(activity_logs),
            "recent_activities": len(
                [
                    a
                    for a in activity_logs
                    if (datetime.utcnow() - a["created_at"]).days <= 7
                ]
            ),
            "most_active_category": self._get_most_active_category(activity_logs),
        }

        # Social media summary
        social_media_summary = {
            "total_profiles": len(social_media),
            "connected_profiles": len([p for p in social_media if p["is_connected"]]),
            "total_followers": sum(
                p.get("metrics", {}).get("followers", 0) for p in social_media
            ),
            "avg_engagement_rate": self._calculate_avg_engagement(social_media),
        }

        # Engagement metrics
        engagement_metrics = {
            "avg_session_duration": self._calculate_avg_session_duration(activity_logs),
            "feature_usage": self._calculate_feature_usage(activity_logs),
            "peak_activity_hours": self._get_peak_activity_hours(activity_logs),
        }

        # Key insights
        key_insights = [
            "Your profile is {}% complete".format(
                completion_data["completion_percentage"]
            ),
            f"You have {len(social_media)} social media profiles connected",
            f"Most active feature: {activity_summary['most_active_category']}",
        ]

        # Recommendations
        recommendations = [
            "Complete your profile to unlock all features",
            "Connect more social media platforms for better insights",
            "Update your business information regularly",
        ]

        return {
            "user_profile_id": user_profile["id"],
            "business_profile_id": business_profile["id"] if business_profile else None,
            "profile_completion": completion_data["completion_percentage"],
            "activity_summary": activity_summary,
            "social_media_summary": social_media_summary,
            "engagement_metrics": engagement_metrics,
            "key_insights": key_insights,
            "recommendations": recommendations,
        }

    async def get_user_activity(
        self, user_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get user activity logs.

        Args:
            user_id: User ID
            limit: Maximum number of logs to return

        Returns:
            List of activity logs
        """
        # Get user profile
        user_profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        user_profile = user_profile_result.scalar_one_or_none()

        if not user_profile:
            return []

        # Get activity logs
        result = await self.db.execute(
            select(UserActivityLog)
            .where(UserActivityLog.user_profile_id == user_profile.id)
            .order_by(UserActivityLog.created_at.desc())
            .limit(limit)
        )
        logs = result.scalars().all()

        return [self._activity_log_to_dict(log) for log in logs]

    async def generate_profile_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate AI insights for a profile (placeholder).

        Args:
            user_id: User ID

        Returns:
            List of generated insights
        """
        user_profile = await self.get_user_profile(user_id)
        if not user_profile:
            return []

        business_profile = await self.get_business_profile(user_id)
        social_media = await self.get_social_media_profiles(user_id)

        # Placeholder for AI insight generation
        # In production, this would use AI models to analyze profile data

        insights = []

        # Insight 1: Profile completion
        if user_profile["profile_completion_percentage"] < 50:
            insights.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_profile_id": user_profile["id"],
                    "business_profile_id": business_profile["id"]
                    if business_profile
                    else None,
                    "insight_type": "recommendation",
                    "insight_category": "engagement",
                    "title": "Complete Your Profile",
                    "description": "Your profile is less than 50% complete. Adding more information will help us provide better insights.",
                    "insight_data": {
                        "summary": "Profile completion is low",
                        "current_completion": user_profile[
                            "profile_completion_percentage"
                        ],
                        "target_completion": 80,
                    },
                    "priority": "medium",
                    "impact_level": "medium",
                    "confidence_score": 0.95,
                    "is_actionable": "true",
                    "action_items": [
                        "Add your business details",
                        "Connect social media accounts",
                        "Upload a profile picture",
                    ],
                    "estimated_effort": "low",
                    "estimated_timeframe": "short_term",
                    "status": "new",
                    "generated_at": datetime.utcnow().isoformat(),
                }
            )

        # Insight 2: Social media opportunity
        if len(social_media) < 2:
            insights.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_profile_id": user_profile["id"],
                    "business_profile_id": business_profile["id"]
                    if business_profile
                    else None,
                    "insight_type": "growth_opportunity",
                    "insight_category": "social_media",
                    "title": "Expand Your Social Media Presence",
                    "description": "Connecting more social media platforms can increase your reach and engagement.",
                    "insight_data": {
                        "summary": "Limited social media presence",
                        "current_platforms": len(social_media),
                        "recommended_platforms": ["LinkedIn", "Twitter", "Instagram"],
                    },
                    "priority": "high",
                    "impact_level": "high",
                    "confidence_score": 0.85,
                    "is_actionable": "true",
                    "action_items": [
                        "Connect LinkedIn",
                        "Connect Twitter",
                        "Connect Instagram",
                    ],
                    "estimated_effort": "medium",
                    "estimated_timeframe": "short_term",
                    "status": "new",
                    "generated_at": datetime.utcnow().isoformat(),
                }
            )

        # Store insights in database
        for insight in insights:
            await self._store_insight(insight)

        return insights

    async def get_profile_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get stored insights for a user.

        Args:
            user_id: User ID

        Returns:
            List of insights
        """
        # Get user profile
        user_profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        user_profile = user_profile_result.scalar_one_or_none()

        if not user_profile:
            return []

        # Get insights
        result = await self.db.execute(
            select(ProfileInsight)
            .where(ProfileInsight.user_profile_id == user_profile.id)
            .order_by(ProfileInsight.created_at.desc())
            .limit(20)
        )
        insights = result.scalars().all()

        return [self._insight_to_dict(insight) for insight in insights]

    async def log_user_activity(
        self,
        user_id: str,
        activity_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Log user activity.

        Args:
            user_id: User ID
            activity_type: Type of activity
            metadata: Additional metadata

        Returns:
            Created activity log or None
        """
        # Get user profile
        user_profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        user_profile = user_profile_result.scalar_one_or_none()

        if not user_profile:
            return None

        # Get business profile
        business_profile_result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.user_id == user_id)
        )
        business_profile = business_profile_result.scalar_one_or_none()

        activity_log = UserActivityLog(
            id=str(uuid.uuid4()),
            user_profile_id=user_profile.id,
            business_profile_id=business_profile.id if business_profile else None,
            activity_type=activity_type,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )

        self.db.add(activity_log)
        await self.db.commit()
        await self.db.refresh(activity_log)

        return self._activity_log_to_dict(activity_log)

    async def get_privacy_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get privacy settings for a user.

        Args:
            user_id: User ID

        Returns:
            Privacy settings or None
        """
        # Get user profile
        user_profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        user_profile = user_profile_result.scalar_one_or_none()

        if not user_profile:
            return None

        # Get privacy settings
        result = await self.db.execute(
            select(PrivacySetting).where(
                PrivacySetting.user_profile_id == user_profile.id
            )
        )
        settings = result.scalar_one_or_none()

        if not settings:
            return None

        return self._privacy_settings_to_dict(settings)

    async def update_privacy_settings(
        self, user_id: str, settings_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update privacy settings.

        Args:
            user_id: User ID
            settings_data: Settings to update

        Returns:
            Updated settings or None
        """
        # Get user profile
        user_profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        user_profile = user_profile_result.scalar_one_or_none()

        if not user_profile:
            return None

        # Get privacy settings
        result = await self.db.execute(
            select(PrivacySetting).where(
                PrivacySetting.user_profile_id == user_profile.id
            )
        )
        settings = result.scalar_one_or_none()

        if not settings:
            return None

        # Update fields
        for key, value in settings_data.items():
            if hasattr(settings, key) and value is not None:
                setattr(settings, key, value)

        settings.last_consent_update = datetime.utcnow()
        settings.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(settings)

        logger.info(f"Updated privacy settings for user {user_id}")
        return self._privacy_settings_to_dict(settings)

    # ==================== Helper Methods ====================

    async def _create_default_privacy_settings(self, user_profile_id: str):
        """Create default privacy settings for a user profile"""
        settings = PrivacySetting(
            id=str(uuid.uuid4()),
            user_profile_id=user_profile_id,
            analytics_consent="true",
            personalization_consent="true",
            marketing_consent="false",
            third_party_sharing_consent="false",
            research_consent="false",
            data_retention_period="indefinite",
            auto_delete_inactive_account="false",
            profile_visibility="private",
            social_media_visibility="private",
            show_social_media_metrics="true",
            allow_social_media_sync="true",
            activity_tracking_enabled="true",
            track_page_views="true",
            track_feature_usage="true",
            track_time_spent="true",
            ai_insights_enabled="true",
            personalized_recommendations="true",
            predictive_analytics="true",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(settings)
        await self.db.commit()

    async def _link_user_to_business(self, user_id: str, business_id: str):
        """Link user profile to business profile"""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if profile:
            profile.primary_business_id = business_id
            profile.owns_business = "true"
            await self.db.commit()

    async def _store_insight(self, insight_data: Dict[str, Any]):
        """Store an insight in the database"""
        insight = ProfileInsight(
            id=insight_data["id"],
            user_profile_id=insight_data["user_profile_id"],
            business_profile_id=insight_data.get("business_profile_id"),
            insight_type=insight_data["insight_type"],
            insight_category=insight_data.get("insight_category"),
            title=insight_data["title"],
            description=insight_data.get("description"),
            insight_data=insight_data["insight_data"],
            priority=insight_data.get("priority"),
            impact_level=insight_data.get("impact_level"),
            confidence_score=insight_data.get("confidence_score"),
            is_actionable=insight_data.get("is_actionable", "true"),
            action_items=insight_data.get("action_items"),
            estimated_effort=insight_data.get("estimated_effort"),
            estimated_timeframe=insight_data.get("estimated_timeframe"),
            status=insight_data.get("status", "new"),
            generated_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )

        self.db.add(insight)
        await self.db.commit()

    def _calculate_profile_completion(self, profile: UserProfile) -> int:
        """Calculate profile completion percentage"""
        required_fields = [
            "first_name",
            "last_name",
            "email",
            "country",
            "city",
            "job_title",
            "years_of_experience",
            "education_level",
        ]
        filled_fields = sum(
            1 for field in required_fields if getattr(profile, field, None)
        )
        return int((filled_fields / len(required_fields)) * 100)

    def _calculate_business_completeness(self, profile: BusinessProfile) -> float:
        """Calculate business profile completeness score"""
        required_fields = [
            "company_name",
            "industry",
            "business_stage",
            "team_size",
            "annual_revenue",
            "products_services",
            "target_market",
        ]
        filled_fields = sum(
            1 for field in required_fields if getattr(profile, field, None)
        )
        return (filled_fields / len(required_fields)) * 100

    def _get_missing_fields(self, profile: UserProfile) -> List[str]:
        """Get list of missing required fields"""
        required_fields = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email Address",
            "country": "Country",
            "city": "City",
            "job_title": "Job Title",
            "years_of_experience": "Years of Experience",
            "education_level": "Education Level",
        }
        return [
            name
            for field, name in required_fields.items()
            if not getattr(profile, field, None)
        ]

    def _get_recommended_fields(self, profile: UserProfile) -> List[str]:
        """Get list of recommended optional fields"""
        optional_fields = {
            "phone": "Phone Number",
            "avatar_url": "Profile Picture",
            "interests": "Interests",
            "skills": "Skills",
            "learning_goals": "Learning Goals",
        }
        return [
            name
            for field, name in optional_fields.items()
            if not getattr(profile, field, None)
        ]

    def _get_completion_tips(self, completion_percentage: int) -> List[str]:
        """Get completion tips based on percentage"""
        if completion_percentage < 30:
            return [
                "Start by adding your basic information",
                "Upload a profile picture",
            ]
        elif completion_percentage < 60:
            return [
                "Add your professional background",
                "Specify your interests and skills",
            ]
        elif completion_percentage < 90:
            return ["Connect your social media accounts", "Add your learning goals"]
        else:
            return [
                "Your profile is almost complete!",
                "Review your information for accuracy",
            ]

    def _infer_stage_from_revenue(self, revenue: Optional[float]) -> str:
        """Infer business stage from revenue"""
        if not revenue:
            return "startup"
        elif revenue < 100000:
            return "startup"
        elif revenue < 1000000:
            return "growth"
        else:
            return "established"

    def _infer_stage_from_team(self, team_size: Optional[int]) -> str:
        """Infer business stage from team size"""
        if not team_size:
            return "startup"
        elif team_size < 10:
            return "startup"
        elif team_size < 50:
            return "growth"
        else:
            return "established"

    def _extract_industry_keywords(self, description: str) -> List[str]:
        """Extract industry keywords from description (placeholder)"""
        # Placeholder for NLP-based keyword extraction
        return []

    def _calculate_performance_rating(self, metrics: Dict[str, Any]) -> str:
        """Calculate performance rating from metrics"""
        if not metrics:
            return "average"

        engagement_rate = metrics.get("engagement_rate", 0)
        if engagement_rate > 5:
            return "excellent"
        elif engagement_rate > 3:
            return "good"
        elif engagement_rate > 1:
            return "average"
        else:
            return "poor"

    def _generate_social_media_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate insights from social media metrics (placeholder)"""
        insights = []
        if metrics.get("engagement_rate", 0) > 3:
            insights.append("Your engagement rate is above average")
        if metrics.get("followers", 0) > 10000:
            insights.append("You have a strong follower base")
        return insights

    def _generate_social_media_recommendations(
        self, metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations from social media metrics (placeholder)"""
        recommendations = []
        if metrics.get("engagement_rate", 0) < 2:
            recommendations.append("Try posting more engaging content")
        if metrics.get("followers", 0) < 1000:
            recommendations.append("Focus on growing your audience")
        return recommendations

    def _get_most_active_category(self, activity_logs: List[Dict[str, Any]]) -> str:
        """Get most active category from activity logs"""
        if not activity_logs:
            return "none"

        categories = [log.get("activity_category", "other") for log in activity_logs]
        from collections import Counter

        return Counter(categories).most_common(1)[0][0]

    def _calculate_avg_engagement(self, social_media: List[Dict[str, Any]]) -> float:
        """Calculate average engagement rate across social media profiles"""
        if not social_media:
            return 0.0

        rates = [p.get("metrics", {}).get("engagement_rate", 0) for p in social_media]
        return sum(rates) / len(rates) if rates else 0.0

    def _calculate_avg_session_duration(
        self, activity_logs: List[Dict[str, Any]]
    ) -> float:
        """Calculate average session duration"""
        durations = [
            log.get("interaction_time", 0)
            for log in activity_logs
            if log.get("interaction_time")
        ]
        return sum(durations) / len(durations) if durations else 0.0

    def _calculate_feature_usage(
        self, activity_logs: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate feature usage statistics"""
        features = [log.get("feature_name", "other") for log in activity_logs]
        from collections import Counter

        return dict(Counter(features))

    def _get_peak_activity_hours(
        self, activity_logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get peak activity hours"""
        hours = [
            log["created_at"].hour for log in activity_logs if log.get("created_at")
        ]
        from collections import Counter

        hour_counts = Counter(hours)

        return [
            {"hour": hour, "count": count} for hour, count in hour_counts.most_common(5)
        ]

    # ==================== Dictionary Conversion Methods ====================

    def _user_profile_to_dict(self, profile: UserProfile) -> Dict[str, Any]:
        """Convert user profile to dictionary"""
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "full_name": profile.full_name,
            "email": profile.email,
            "phone": profile.phone,
            "avatar_url": profile.avatar_url,
            "date_of_birth": profile.date_of_birth.isoformat()
            if profile.date_of_birth
            else None,
            "gender": profile.gender,
            "nationality": profile.nationality,
            "country": profile.country,
            "state_province": profile.state_province,
            "city": profile.city,
            "postal_code": profile.postal_code,
            "timezone": profile.timezone,
            "language": profile.language,
            "job_title": profile.job_title,
            "company_role": profile.company_role,
            "years_of_experience": profile.years_of_experience,
            "industry_experience": profile.industry_experience,
            "education_level": profile.education_level,
            "field_of_study": profile.field_of_study,
            "certifications": profile.certifications,
            "owns_business": profile.owns_business == "true",
            "number_of_businesses": profile.number_of_businesses,
            "primary_business_id": profile.primary_business_id,
            "preferred_contact_method": profile.preferred_contact_method,
            "email_notifications_enabled": profile.email_notifications_enabled
            == "true",
            "sms_notifications_enabled": profile.sms_notifications_enabled == "true",
            "marketing_emails_enabled": profile.marketing_emails_enabled == "true",
            "newsletter_subscription": profile.newsletter_subscription == "true",
            "interests": profile.interests,
            "skills": profile.skills,
            "learning_goals": profile.learning_goals,
            "business_challenges": profile.business_challenges,
            "profile_completion_percentage": profile.profile_completion_percentage,
            "last_profile_update": profile.last_profile_update.isoformat()
            if profile.last_profile_update
            else None,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        }

    def _business_profile_to_dict(self, profile: BusinessProfile) -> Dict[str, Any]:
        """Convert business profile to dictionary"""
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "company_name": profile.company_name,
            "industry": profile.industry,
            "business_stage": profile.business_stage,
            "business_type": profile.business_type,
            "legal_structure": profile.legal_structure,
            "registration_number": profile.registration_number,
            "tax_id": profile.tax_id,
            "founding_date": profile.founding_date.isoformat()
            if profile.founding_date
            else None,
            "website_url": profile.website_url,
            "business_description": profile.business_description,
            "mission_statement": profile.mission_statement,
            "vision_statement": profile.vision_statement,
            "business_address": profile.business_address,
            "headquarters_location": profile.headquarters_location,
            "operating_locations": profile.operating_locations,
            "team_size": profile.team_size,
            "team_structure": profile.team_structure,
            "key_team_members": profile.key_team_members,
            "annual_revenue": profile.annual_revenue,
            "revenue_currency": profile.revenue_currency,
            "revenue_range": profile.revenue_range,
            "profit_margin": profile.profit_margin,
            "funding_stage": profile.funding_stage,
            "funding_amount": profile.funding_amount,
            "customer_count": profile.customer_count,
            "active_customers": profile.active_customers,
            "monthly_active_users": profile.monthly_active_users,
            "customer_acquisition_cost": profile.customer_acquisition_cost,
            "customer_lifetime_value": profile.customer_lifetime_value,
            "churn_rate": profile.churn_rate,
            "products_services": profile.products_services,
            "target_market": profile.target_market,
            "competitive_advantages": profile.competitive_advantages,
            "tech_stack": profile.tech_stack,
            "software_tools": profile.software_tools,
            "integrations": profile.integrations,
            "short_term_goals": profile.short_term_goals,
            "long_term_goals": profile.long_term_goals,
            "current_challenges": profile.current_challenges,
            "growth_opportunities": profile.growth_opportunities,
            "profile_completeness_score": profile.profile_completeness_score,
            "last_data_refresh": profile.last_data_refresh.isoformat()
            if profile.last_data_refresh
            else None,
            "data_quality_score": profile.data_quality_score,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        }

    def _social_media_profile_to_dict(
        self, profile: SocialMediaProfile
    ) -> Dict[str, Any]:
        """Convert social media profile to dictionary"""
        return {
            "id": profile.id,
            "user_profile_id": profile.user_profile_id,
            "business_profile_id": profile.business_profile_id,
            "platform_name": profile.platform_name,
            "platform_display_name": profile.platform_display_name,
            "platform_icon": profile.platform_icon,
            "handle": profile.handle,
            "profile_url": profile.profile_url,
            "account_id": profile.account_id,
            "account_type": profile.account_type,
            "is_verified": profile.is_verified == "true",
            "is_primary": profile.is_primary == "true",
            "is_connected": profile.is_connected == "true",
            "connection_date": profile.connection_date.isoformat()
            if profile.connection_date
            else None,
            "last_sync_date": profile.last_sync_date.isoformat()
            if profile.last_sync_date
            else None,
            "sync_status": profile.sync_status,
            "sync_error_message": profile.sync_error_message,
            "metrics": profile.metrics,
            "historical_metrics": profile.historical_metrics,
            "content_categories": profile.content_categories,
            "posting_schedule": profile.posting_schedule,
            "content_calendar": profile.content_calendar,
            "auto_sync_enabled": profile.auto_sync_enabled == "true",
            "sync_frequency": profile.sync_frequency,
            "sync_settings": profile.sync_settings,
            "engagement_score": profile.engagement_score,
            "influence_score": profile.influence_score,
            "growth_rate": profile.growth_rate,
            "performance_rating": profile.performance_rating,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        }

    def _activity_log_to_dict(self, log: UserActivityLog) -> Dict[str, Any]:
        """Convert activity log to dictionary"""
        return {
            "id": log.id,
            "user_profile_id": log.user_profile_id,
            "business_profile_id": log.business_profile_id,
            "activity_type": log.activity_type,
            "activity_category": log.activity_category,
            "feature_name": log.feature_name,
            "action": log.action,
            "page_url": log.page_url,
            "referrer_url": log.referrer_url,
            "session_id": log.session_id,
            "device_type": log.device_type,
            "browser": log.browser,
            "browser_version": log.browser_version,
            "os": log.os,
            "os_version": log.os_version,
            "screen_resolution": log.screen_resolution,
            "ip_address": log.ip_address,
            "country": log.country,
            "city": log.city,
            "page_load_time": log.page_load_time,
            "interaction_time": log.interaction_time,
            "metadata": log.metadata,
            "error_details": log.error_details,
            "created_at": log.created_at.isoformat(),
        }

    def _privacy_settings_to_dict(self, settings: PrivacySetting) -> Dict[str, Any]:
        """Convert privacy settings to dictionary"""
        return {
            "id": settings.id,
            "user_profile_id": settings.user_profile_id,
            "analytics_consent": settings.analytics_consent == "true",
            "personalization_consent": settings.personalization_consent == "true",
            "marketing_consent": settings.marketing_consent == "true",
            "third_party_sharing_consent": settings.third_party_sharing_consent
            == "true",
            "research_consent": settings.research_consent == "true",
            "data_retention_period": settings.data_retention_period,
            "auto_delete_inactive_account": settings.auto_delete_inactive_account
            == "true",
            "inactivity_threshold_days": settings.inactivity_threshold_days,
            "profile_visibility": settings.profile_visibility,
            "visible_profile_fields": settings.visible_profile_fields,
            "hide_sensitive_fields": settings.hide_sensitive_fields,
            "social_media_visibility": settings.social_media_visibility,
            "show_social_media_metrics": settings.show_social_media_metrics == "true",
            "allow_social_media_sync": settings.allow_social_media_sync == "true",
            "activity_tracking_enabled": settings.activity_tracking_enabled == "true",
            "track_page_views": settings.track_page_views == "true",
            "track_feature_usage": settings.track_feature_usage == "true",
            "track_time_spent": settings.track_time_spent == "true",
            "ai_insights_enabled": settings.ai_insights_enabled == "true",
            "personalized_recommendations": settings.personalized_recommendations
            == "true",
            "predictive_analytics": settings.predictive_analytics == "true",
            "email_communication_types": settings.email_communication_types,
            "sms_communication_types": settings.sms_communication_types,
            "push_notification_types": settings.push_notification_types,
            "consent_history": settings.consent_history,
            "last_consent_update": settings.last_consent_update.isoformat(),
            "data_export_requested": settings.data_export_requested == "true",
            "data_export_date": settings.data_export_date.isoformat()
            if settings.data_export_date
            else None,
            "account_deletion_requested": settings.account_deletion_requested == "true",
            "account_deletion_date": settings.account_deletion_date.isoformat()
            if settings.account_deletion_date
            else None,
            "created_at": settings.created_at.isoformat(),
            "updated_at": settings.updated_at.isoformat(),
        }

    def _insight_to_dict(self, insight: ProfileInsight) -> Dict[str, Any]:
        """Convert insight to dictionary"""
        return {
            "id": insight.id,
            "user_profile_id": insight.user_profile_id,
            "business_profile_id": insight.business_profile_id,
            "insight_type": insight.insight_type,
            "insight_category": insight.insight_category,
            "title": insight.title,
            "description": insight.description,
            "insight_data": insight.insight_data,
            "priority": insight.priority,
            "impact_level": insight.impact_level,
            "confidence_score": insight.confidence_score,
            "is_actionable": insight.is_actionable == "true",
            "action_items": insight.action_items,
            "estimated_effort": insight.estimated_effort,
            "estimated_timeframe": insight.estimated_timeframe,
            "status": insight.status,
            "user_feedback": insight.user_feedback,
            "user_notes": insight.user_notes,
            "related_insight_ids": insight.related_insight_ids,
            "parent_insight_id": insight.parent_insight_id,
            "ai_model_version": insight.ai_model_version,
            "generated_at": insight.generated_at.isoformat()
            if insight.generated_at
            else None,
            "last_updated": insight.last_updated.isoformat()
            if insight.last_updated
            else None,
            "expires_at": insight.expires_at.isoformat()
            if insight.expires_at
            else None,
            "created_at": insight.created_at.isoformat(),
        }
