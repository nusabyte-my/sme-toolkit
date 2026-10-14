/**
 * Profile Types for Enhanced Data Profiling
 * Matches backend schemas from sme-toolkit-backend/app/schemas/profiles.py
 */

// ==================== User Profile Types ====================

export interface UserProfile {
  id: string;
  user_id: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  email?: string;
  phone?: string;
  avatar_url?: string;
  date_of_birth?: string;
  gender?: string;
  nationality?: string;
  country?: string;
  state_province?: string;
  city?: string;
  postal_code?: string;
  timezone?: string;
  language?: string;
  job_title?: string;
  company_role?: string;
  years_of_experience?: number;
  industry_experience?: Array<Record<string, any>>;
  education_level?: string;
  field_of_study?: string;
  certifications?: Array<Record<string, any>>;
  owns_business: boolean;
  number_of_businesses?: number;
  primary_business_id?: string;
  preferred_contact_method?: string;
  email_notifications_enabled: boolean;
  sms_notifications_enabled: boolean;
  marketing_emails_enabled: boolean;
  newsletter_subscription: boolean;
  interests?: string[];
  skills?: Array<Record<string, any>>;
  learning_goals?: string[];
  business_challenges?: string[];
  profile_completion_percentage: number;
  last_profile_update?: string;
  created_at: string;
  updated_at: string;
}

export interface UserProfileUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  date_of_birth?: string;
  gender?: string;
  nationality?: string;
  country?: string;
  state_province?: string;
  city?: string;
  postal_code?: string;
  timezone?: string;
  language?: string;
  job_title?: string;
  company_role?: string;
  years_of_experience?: number;
  industry_experience?: Array<Record<string, any>>;
  education_level?: string;
  field_of_study?: string;
  certifications?: Array<Record<string, any>>;
  owns_business?: boolean;
  number_of_businesses?: number;
  primary_business_id?: string;
  preferred_contact_method?: string;
  email_notifications_enabled?: boolean;
  sms_notifications_enabled?: boolean;
  marketing_emails_enabled?: boolean;
  newsletter_subscription?: boolean;
  interests?: string[];
  skills?: Array<Record<string, any>>;
  learning_goals?: string[];
  business_challenges?: string[];
}

export interface ProfileCompletion {
  profile_id: string;
  completion_percentage: number;
  missing_fields: string[];
  recommended_fields: string[];
  completion_tips: string[];
}

// ==================== Business Profile Types ====================

export interface BusinessProfile {
  id: string;
  user_id: string;
  company_name?: string;
  industry?: string;
  business_stage?: string;
  business_type?: string;
  legal_structure?: string;
  registration_number?: string;
  tax_id?: string;
  founding_date?: string;
  website_url?: string;
  business_description?: string;
  mission_statement?: string;
  vision_statement?: string;
  business_address?: Record<string, any>;
  headquarters_location?: Record<string, any>;
  operating_locations?: Array<Record<string, any>>;
  team_size?: number;
  team_structure?: Record<string, any>;
  key_team_members?: Array<Record<string, any>>;
  annual_revenue?: number;
  revenue_currency?: string;
  revenue_range?: string;
  profit_margin?: number;
  funding_stage?: string;
  funding_amount?: number;
  customer_count?: number;
  active_customers?: number;
  monthly_active_users?: number;
  customer_acquisition_cost?: number;
  customer_lifetime_value?: number;
  churn_rate?: number;
  products_services?: Array<Record<string, any>>;
  target_market?: string[];
  competitive_advantages?: string[];
  tech_stack?: string[];
  software_tools?: string[];
  integrations?: string[];
  short_term_goals?: string[];
  long_term_goals?: string[];
  current_challenges?: string[];
  growth_opportunities?: string[];
  profile_completeness_score: number;
  last_data_refresh?: string;
  data_quality_score?: number;
  created_at: string;
  updated_at: string;
}

export interface BusinessProfileUpdate {
  company_name?: string;
  industry?: string;
  business_stage?: string;
  business_type?: string;
  legal_structure?: string;
  registration_number?: string;
  tax_id?: string;
  founding_date?: string;
  website_url?: string;
  business_description?: string;
  mission_statement?: string;
  vision_statement?: string;
  business_address?: Record<string, any>;
  headquarters_location?: Record<string, any>;
  operating_locations?: Array<Record<string, any>>;
  team_size?: number;
  team_structure?: Record<string, any>;
  key_team_members?: Array<Record<string, any>>;
  annual_revenue?: number;
  revenue_currency?: string;
  revenue_range?: string;
  profit_margin?: number;
  funding_stage?: string;
  funding_amount?: number;
  customer_count?: number;
  active_customers?: number;
  monthly_active_users?: number;
  customer_acquisition_cost?: number;
  customer_lifetime_value?: number;
  churn_rate?: number;
  products_services?: Array<Record<string, any>>;
  target_market?: string[];
  competitive_advantages?: string[];
  tech_stack?: string[];
  software_tools?: string[];
  integrations?: string[];
  short_term_goals?: string[];
  long_term_goals?: string[];
  current_challenges?: string[];
  growth_opportunities?: string[];
}

// ==================== Social Media Profile Types ====================

export interface SocialMediaProfile {
  id: string;
  user_profile_id: string;
  business_profile_id?: string;
  platform_name: string;
  platform_display_name?: string;
  platform_icon?: string;
  handle?: string;
  profile_url?: string;
  account_id?: string;
  account_type?: string;
  is_verified: boolean;
  is_primary: boolean;
  is_connected: boolean;
  connection_date?: string;
  last_sync_date?: string;
  sync_status: string;
  sync_error_message?: string;
  metrics?: Record<string, any>;
  historical_metrics?: Array<Record<string, any>>;
  content_categories?: string[];
  posting_schedule?: Record<string, any>;
  content_calendar?: Record<string, any>;
  auto_sync_enabled: boolean;
  sync_frequency?: string;
  sync_settings?: Record<string, any>;
  engagement_score?: number;
  influence_score?: number;
  growth_rate?: number;
  performance_rating?: string;
  created_at: string;
  updated_at: string;
}

export interface SocialMediaProfileUpdate {
  platform_display_name?: string;
  platform_icon?: string;
  handle?: string;
  profile_url?: string;
  account_type?: string;
  is_primary?: boolean;
  auto_sync_enabled?: boolean;
  sync_frequency?: string;
  sync_settings?: Record<string, any>;
  metrics?: Record<string, any>;
}

export interface SocialMediaMetrics {
  profile_id: string;
  platform_name: string;
  current_metrics: Record<string, any>;
  historical_trends: Array<Record<string, any>>;
  performance_rating: string;
  insights: string[];
  recommendations: string[];
  benchmark_comparison?: Record<string, any>;
}

// ==================== Activity Log Types ====================

export interface UserActivityLog {
  id: string;
  user_profile_id: string;
  business_profile_id?: string;
  activity_type: string;
  activity_category?: string;
  feature_name?: string;
  action?: string;
  page_url?: string;
  referrer_url?: string;
  session_id?: string;
  device_type?: string;
  browser?: string;
  browser_version?: string;
  os?: string;
  os_version?: string;
  screen_resolution?: string;
  ip_address?: string;
  country?: string;
  city?: string;
  page_load_time?: number;
  interaction_time?: number;
  metadata?: Record<string, any>;
  error_details?: string;
  created_at: string;
}

// ==================== Privacy Settings Types ====================

export interface PrivacySettings {
  id: string;
  user_profile_id: string;
  analytics_consent: boolean;
  personalization_consent: boolean;
  marketing_consent: boolean;
  third_party_sharing_consent: boolean;
  research_consent: boolean;
  data_retention_period: string;
  auto_delete_inactive_account: boolean;
  inactivity_threshold_days?: number;
  profile_visibility: string;
  visible_profile_fields?: string[];
  hide_sensitive_fields?: string[];
  social_media_visibility: string;
  show_social_media_metrics: boolean;
  allow_social_media_sync: boolean;
  activity_tracking_enabled: boolean;
  track_page_views: boolean;
  track_feature_usage: boolean;
  track_time_spent: boolean;
  ai_insights_enabled: boolean;
  personalized_recommendations: boolean;
  predictive_analytics: boolean;
  email_communication_types?: string[];
  sms_communication_types?: string[];
  push_notification_types?: string[];
  consent_history?: Array<Record<string, any>>;
  last_consent_update: string;
  data_export_requested: boolean;
  data_export_date?: string;
  account_deletion_requested: boolean;
  account_deletion_date?: string;
  created_at: string;
  updated_at: string;
}

export interface PrivacySettingsUpdate {
  analytics_consent?: boolean;
  personalization_consent?: boolean;
  marketing_consent?: boolean;
  third_party_sharing_consent?: boolean;
  research_consent?: boolean;
  data_retention_period?: string;
  auto_delete_inactive_account?: boolean;
  inactivity_threshold_days?: number;
  profile_visibility?: string;
  visible_profile_fields?: string[];
  hide_sensitive_fields?: string[];
  social_media_visibility?: string;
  show_social_media_metrics?: boolean;
  allow_social_media_sync?: boolean;
  activity_tracking_enabled?: boolean;
  track_page_views?: boolean;
  track_feature_usage?: boolean;
  track_time_spent?: boolean;
  ai_insights_enabled?: boolean;
  personalized_recommendations?: boolean;
  predictive_analytics?: boolean;
  email_communication_types?: string[];
  sms_communication_types?: string[];
  push_notification_types?: string[];
}

// ==================== Profile Insight Types ====================

export interface ProfileInsight {
  id: string;
  user_profile_id: string;
  business_profile_id?: string;
  insight_type: string;
  insight_category?: string;
  title: string;
  description?: string;
  insight_data: Record<string, any>;
  priority?: string;
  impact_level?: string;
  confidence_score?: number;
  is_actionable: boolean;
  action_items?: string[];
  estimated_effort?: string;
  estimated_timeframe?: string;
  status: string;
  user_feedback?: string;
  user_notes?: string;
  related_insight_ids?: string[];
  parent_insight_id?: string;
  ai_model_version?: string;
  generated_at: string;
  last_updated: string;
  expires_at?: string;
  created_at: string;
}

// ==================== Analytics Types ====================

export interface ProfileAnalytics {
  user_profile_id: string;
  business_profile_id?: string;
  profile_completion: number;
  activity_summary: Record<string, any>;
  social_media_summary: Record<string, any>;
  engagement_metrics: Record<string, any>;
  key_insights: string[];
  recommendations: string[];
}

export interface UserActivityAnalytics {
  user_profile_id: string;
  time_range: string;
  total_sessions: number;
  total_time_spent: number;
  most_used_features: Array<Record<string, any>>;
  activity_by_category: Record<string, number>;
  peak_activity_times: Array<Record<string, any>>;
  engagement_trend: Array<Record<string, any>>;
}

export interface ProfileInsightsResponse {
  insights: Array<Record<string, any>>;
  total: number;
  unread_count: number;
  high_priority_count: number;
  categories: Record<string, number>;
}

// ==================== API Response Types ====================

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
