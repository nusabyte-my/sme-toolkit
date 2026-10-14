"""Profile schemas for enhanced data profiling"""

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== User Profile Schemas ====================

class UserProfileCreate(BaseModel):
    """Schema for creating a user profile"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = "en"
    job_title: Optional[str] = None
    company_role: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry_experience: Optional[List[Dict[str, Any]]] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    owns_business: Optional[bool] = False
    number_of_businesses: Optional[int] = None
    primary_business_id: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    email_notifications_enabled: Optional[bool] = True
    sms_notifications_enabled: Optional[bool] = False
    marketing_emails_enabled: Optional[bool] = False
    newsletter_subscription: Optional[bool] = False
    interests: Optional[List[str]] = None
    skills: Optional[List[Dict[str, Any]]] = None
    learning_goals: Optional[List[str]] = None
    business_challenges: Optional[List[str]] = None


class UserProfileUpdate(BaseModel):
    """Schema for updating a user profile"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    job_title: Optional[str] = None
    company_role: Optional[str] = None
    years_of_experience: Optional[int] = None
    industry_experience: Optional[List[Dict[str, Any]]] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    owns_business: Optional[bool] = None
    number_of_businesses: Optional[int] = None
    primary_business_id: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    email_notifications_enabled: Optional[bool] = None
    sms_notifications_enabled: Optional[bool] = None
    marketing_emails_enabled: Optional[bool] = None
    newsletter_subscription: Optional[bool] = None
    interests: Optional[List[str]] = None
    skills: Optional[List[Dict[str, Any]]] = None
    learning_goals: Optional[List[str]] = None
    business_challenges: Optional[List[str]] = None


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""
    id: str
    user_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    nationality: Optional[str]
    country: Optional[str]
    state_province: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    timezone: Optional[str]
    language: Optional[str]
    job_title: Optional[str]
    company_role: Optional[str]
    years_of_experience: Optional[int]
    industry_experience: Optional[List[Dict[str, Any]]]
    education_level: Optional[str]
    field_of_study: Optional[str]
    certifications: Optional[List[Dict[str, Any]]]
    owns_business: bool
    number_of_businesses: Optional[int]
    primary_business_id: Optional[str]
    preferred_contact_method: Optional[str]
    email_notifications_enabled: bool
    sms_notifications_enabled: bool
    marketing_emails_enabled: bool
    newsletter_subscription: bool
    interests: Optional[List[str]]
    skills: Optional[List[Dict[str, Any]]]
    learning_goals: Optional[List[str]]
    business_challenges: Optional[List[str]]
    profile_completion_percentage: int
    last_profile_update: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileCompletionResponse(BaseModel):
    """Schema for profile completion status"""
    profile_id: str
    completion_percentage: int
    missing_fields: List[str]
    recommended_fields: List[str]
    completion_tips: List[str]


# ==================== Business Profile Schemas ====================

class BusinessProfileCreate(BaseModel):
    """Schema for creating a business profile"""
    company_name: str
    industry: Optional[str] = None
    business_stage: Optional[str] = None
    business_type: Optional[str] = None
    legal_structure: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    founding_date: Optional[datetime] = None
    website_url: Optional[HttpUrl] = None
    business_description: Optional[str] = None
    mission_statement: Optional[str] = None
    vision_statement: Optional[str] = None
    business_address: Optional[Dict[str, Any]] = None
    headquarters_location: Optional[Dict[str, Any]] = None
    operating_locations: Optional[List[Dict[str, Any]]] = None
    team_size: Optional[int] = None
    team_structure: Optional[Dict[str, Any]] = None
    key_team_members: Optional[List[Dict[str, Any]]] = None
    annual_revenue: Optional[float] = None
    revenue_currency: Optional[str] = "USD"
    revenue_range: Optional[str] = None
    profit_margin: Optional[float] = None
    funding_stage: Optional[str] = None
    funding_amount: Optional[float] = None
    customer_count: Optional[int] = None
    active_customers: Optional[int] = None
    monthly_active_users: Optional[int] = None
    customer_acquisition_cost: Optional[float] = None
    customer_lifetime_value: Optional[float] = None
    churn_rate: Optional[float] = None
    products_services: Optional[List[Dict[str, Any]]] = None
    target_market: Optional[List[str]] = None
    competitive_advantages: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    software_tools: Optional[List[str]] = None
    integrations: Optional[List[str]] = None
    short_term_goals: Optional[List[str]] = None
    long_term_goals: Optional[List[str]] = None
    current_challenges: Optional[List[str]] = None
    growth_opportunities: Optional[List[str]] = None


class BusinessProfileUpdate(BaseModel):
    """Schema for updating a business profile"""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    business_stage: Optional[str] = None
    business_type: Optional[str] = None
    legal_structure: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    founding_date: Optional[datetime] = None
    website_url: Optional[HttpUrl] = None
    business_description: Optional[str] = None
    mission_statement: Optional[str] = None
    vision_statement: Optional[str] = None
    business_address: Optional[Dict[str, Any]] = None
    headquarters_location: Optional[Dict[str, Any]] = None
    operating_locations: Optional[List[Dict[str, Any]]] = None
    team_size: Optional[int] = None
    team_structure: Optional[Dict[str, Any]] = None
    key_team_members: Optional[List[Dict[str, Any]]] = None
    annual_revenue: Optional[float] = None
    revenue_currency: Optional[str] = None
    revenue_range: Optional[str] = None
    profit_margin: Optional[float] = None
    funding_stage: Optional[str] = None
    funding_amount: Optional[float] = None
    customer_count: Optional[int] = None
    active_customers: Optional[int] = None
    monthly_active_users: Optional[int] = None
    customer_acquisition_cost: Optional[float] = None
    customer_lifetime_value: Optional[float] = None
    churn_rate: Optional[float] = None
    products_services: Optional[List[Dict[str, Any]]] = None
    target_market: Optional[List[str]] = None
    competitive_advantages: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    software_tools: Optional[List[str]] = None
    integrations: Optional[List[str]] = None
    short_term_goals: Optional[List[str]] = None
    long_term_goals: Optional[List[str]] = None
    current_challenges: Optional[List[str]] = None
    growth_opportunities: Optional[List[str]] = None


class BusinessProfileResponse(BaseModel):
    """Schema for business profile response"""
    id: str
    user_id: str
    company_name: Optional[str]
    industry: Optional[str]
    business_stage: Optional[str]
    business_type: Optional[str]
    legal_structure: Optional[str]
    registration_number: Optional[str]
    tax_id: Optional[str]
    founding_date: Optional[datetime]
    website_url: Optional[str]
    business_description: Optional[str]
    mission_statement: Optional[str]
    vision_statement: Optional[str]
    business_address: Optional[Dict[str, Any]]
    headquarters_location: Optional[Dict[str, Any]]
    operating_locations: Optional[List[Dict[str, Any]]]
    team_size: Optional[int]
    team_structure: Optional[Dict[str, Any]]
    key_team_members: Optional[List[Dict[str, Any]]]
    annual_revenue: Optional[float]
    revenue_currency: Optional[str]
    revenue_range: Optional[str]
    profit_margin: Optional[float]
    funding_stage: Optional[str]
    funding_amount: Optional[float]
    customer_count: Optional[int]
    active_customers: Optional[int]
    monthly_active_users: Optional[int]
    customer_acquisition_cost: Optional[float]
    customer_lifetime_value: Optional[float]
    churn_rate: Optional[float]
    products_services: Optional[List[Dict[str, Any]]]
    target_market: Optional[List[str]]
    competitive_advantages: Optional[List[str]]
    tech_stack: Optional[List[str]]
    software_tools: Optional[List[str]]
    integrations: Optional[List[str]]
    short_term_goals: Optional[List[str]]
    long_term_goals: Optional[List[str]]
    current_challenges: Optional[List[str]]
    growth_opportunities: Optional[List[str]]
    profile_completeness_score: float
    last_data_refresh: Optional[datetime]
    data_quality_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessEnrichmentResponse(BaseModel):
    """Schema for business enrichment response"""
    profile_id: str
    enriched_fields: Dict[str, Any]
    inferred_business_stage: Optional[str]
    inferred_industry: Optional[str]
    confidence_scores: Dict[str, float]
    recommendations: List[str]


class BusinessClassificationResponse(BaseModel):
    """Schema for business classification response"""
    profile_id: str
    business_stage: Optional[str]
    industry: Optional[str]
    business_type: Optional[str]
    confidence_score: float
    classification_details: Dict[str, Any]


# ==================== Social Media Profile Schemas ====================

class SocialMediaProfileCreate(BaseModel):
    """Schema for creating a social media profile"""
    platform_name: str
    platform_display_name: Optional[str] = None
    platform_icon: Optional[str] = None
    handle: Optional[str] = None
    profile_url: Optional[HttpUrl] = None
    account_id: Optional[str] = None
    account_type: Optional[str] = None
    is_primary: bool = False
    auto_sync_enabled: bool = False
    sync_frequency: Optional[str] = None
    sync_settings: Optional[Dict[str, Any]] = None


class SocialMediaProfileUpdate(BaseModel):
    """Schema for updating a social media profile"""
    platform_display_name: Optional[str] = None
    platform_icon: Optional[str] = None
    handle: Optional[str] = None
    profile_url: Optional[HttpUrl] = None
    account_type: Optional[str] = None
    is_primary: Optional[bool] = None
    auto_sync_enabled: Optional[bool] = None
    sync_frequency: Optional[str] = None
    sync_settings: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None


class SocialMediaProfileResponse(BaseModel):
    """Schema for social media profile response"""
    id: str
    user_profile_id: str
    business_profile_id: Optional[str]
    platform_name: str
    platform_display_name: Optional[str]
    platform_icon: Optional[str]
    handle: Optional[str]
    profile_url: Optional[str]
    account_id: Optional[str]
    account_type: Optional[str]
    is_verified: bool
    is_primary: bool
    is_connected: bool
    connection_date: Optional[datetime]
    last_sync_date: Optional[datetime]
    sync_status: str
    sync_error_message: Optional[str]
    metrics: Optional[Dict[str, Any]]
    historical_metrics: Optional[List[Dict[str, Any]]]
    content_categories: Optional[List[str]]
    posting_schedule: Optional[Dict[str, Any]]
    content_calendar: Optional[Dict[str, Any]]
    auto_sync_enabled: bool
    sync_frequency: Optional[str]
    sync_settings: Optional[Dict[str, Any]]
    engagement_score: Optional[float]
    influence_score: Optional[float]
    growth_rate: Optional[float]
    performance_rating: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SocialMediaMetricsResponse(BaseModel):
    """Schema for social media metrics response"""
    profile_id: str
    platform_name: str
    current_metrics: Dict[str, Any]
    historical_trends: List[Dict[str, Any]]
    performance_rating: str
    insights: List[str]
    recommendations: List[str]
    benchmark_comparison: Optional[Dict[str, Any]]


# ==================== Activity Log Schemas ====================

class UserActivityLogResponse(BaseModel):
    """Schema for user activity log response"""
    id: str
    user_profile_id: str
    business_profile_id: Optional[str]
    activity_type: str
    activity_category: Optional[str]
    feature_name: Optional[str]
    action: Optional[str]
    page_url: Optional[str]
    referrer_url: Optional[str]
    session_id: Optional[str]
    device_type: Optional[str]
    browser: Optional[str]
    browser_version: Optional[str]
    os: Optional[str]
    os_version: Optional[str]
    screen_resolution: Optional[str]
    ip_address: Optional[str]
    country: Optional[str]
    city: Optional[str]
    page_load_time: Optional[float]
    interaction_time: Optional[float]
    metadata: Optional[Dict[str, Any]]
    error_details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Privacy Settings Schemas ====================

class PrivacySettingsCreate(BaseModel):
    """Schema for creating privacy settings"""
    analytics_consent: bool = True
    personalization_consent: bool = True
    marketing_consent: bool = False
    third_party_sharing_consent: bool = False
    research_consent: bool = False
    data_retention_period: str = "indefinite"
    auto_delete_inactive_account: bool = False
    inactivity_threshold_days: Optional[int] = None
    profile_visibility: str = "private"
    visible_profile_fields: Optional[List[str]] = None
    hide_sensitive_fields: Optional[List[str]] = None
    social_media_visibility: str = "private"
    show_social_media_metrics: bool = True
    allow_social_media_sync: bool = True
    activity_tracking_enabled: bool = True
    track_page_views: bool = True
    track_feature_usage: bool = True
    track_time_spent: bool = True
    ai_insights_enabled: bool = True
    personalized_recommendations: bool = True
    predictive_analytics: bool = True
    email_communication_types: Optional[List[str]] = None
    sms_communication_types: Optional[List[str]] = None
    push_notification_types: Optional[List[str]] = None


class PrivacySettingsUpdate(BaseModel):
    """Schema for updating privacy settings"""
    analytics_consent: Optional[bool] = None
    personalization_consent: Optional[bool] = None
    marketing_consent: Optional[bool] = None
    third_party_sharing_consent: Optional[bool] = None
    research_consent: Optional[bool] = None
    data_retention_period: Optional[str] = None
    auto_delete_inactive_account: Optional[bool] = None
    inactivity_threshold_days: Optional[int] = None
    profile_visibility: Optional[str] = None
    visible_profile_fields: Optional[List[str]] = None
    hide_sensitive_fields: Optional[List[str]] = None
    social_media_visibility: Optional[str] = None
    show_social_media_metrics: Optional[bool] = None
    allow_social_media_sync: Optional[bool] = None
    activity_tracking_enabled: Optional[bool] = None
    track_page_views: Optional[bool] = None
    track_feature_usage: Optional[bool] = None
    track_time_spent: Optional[bool] = None
    ai_insights_enabled: Optional[bool] = None
    personalized_recommendations: Optional[bool] = None
    predictive_analytics: Optional[bool] = None
    email_communication_types: Optional[List[str]] = None
    sms_communication_types: Optional[List[str]] = None
    push_notification_types: Optional[List[str]] = None


class PrivacySettingsResponse(BaseModel):
    """Schema for privacy settings response"""
    id: str
    user_profile_id: str
    analytics_consent: bool
    personalization_consent: bool
    marketing_consent: bool
    third_party_sharing_consent: bool
    research_consent: bool
    data_retention_period: str
    auto_delete_inactive_account: bool
    inactivity_threshold_days: Optional[int]
    profile_visibility: str
    visible_profile_fields: Optional[List[str]]
    hide_sensitive_fields: Optional[List[str]]
    social_media_visibility: str
    show_social_media_metrics: bool
    allow_social_media_sync: bool
    activity_tracking_enabled: bool
    track_page_views: bool
    track_feature_usage: bool
    track_time_spent: bool
    ai_insights_enabled: bool
    personalized_recommendations: bool
    predictive_analytics: bool
    email_communication_types: Optional[List[str]]
    sms_communication_types: Optional[List[str]]
    push_notification_types: Optional[List[str]]
    consent_history: Optional[List[Dict[str, Any]]]
    last_consent_update: datetime
    data_export_requested: bool
    data_export_date: Optional[datetime]
    account_deletion_requested: bool
    account_deletion_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Profile Insight Schemas ====================

class ProfileInsightResponse(BaseModel):
    """Schema for profile insight response"""
    id: str
    user_profile_id: str
    business_profile_id: Optional[str]
    insight_type: str
    insight_category: Optional[str]
    title: str
    description: Optional[str]
    insight_data: Dict[str, Any]
    priority: Optional[str]
    impact_level: Optional[str]
    confidence_score: Optional[float]
    is_actionable: bool
    action_items: Optional[List[str]]
    estimated_effort: Optional[str]
    estimated_timeframe: Optional[str]
    status: str
    user_feedback: Optional[str]
    user_notes: Optional[str]
    related_insight_ids: Optional[List[str]]
    parent_insight_id: Optional[str]
    ai_model_version: Optional[str]
    generated_at: datetime
    last_updated: datetime
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Analytics Schemas ====================

class ProfileAnalyticsOverview(BaseModel):
    """Schema for profile analytics overview"""
    user_profile_id: str
    business_profile_id: Optional[str]
    profile_completion: int
    activity_summary: Dict[str, Any]
    social_media_summary: Dict[str, Any]
    engagement_metrics: Dict[str, Any]
    key_insights: List[str]
    recommendations: List[str]


class UserActivityAnalytics(BaseModel):
    """Schema for user activity analytics"""
    user_profile_id: str
    time_range: str
    total_sessions: int
    total_time_spent: float
    most_used_features: List[Dict[str, Any]]
    activity_by_category: Dict[str, int]
    peak_activity_times: List[Dict[str, Any]]
    engagement_trend: List[Dict[str, Any]]


class ProfileInsightsResponse(BaseModel):
    """Schema for profile insights list response"""
    insights: List[Dict[str, Any]]
    total: int
    unread_count: int
    high_priority_count: int
    categories: Dict[str, int]
