/**
 * Profile Service
 * Handles all API calls for user profiles, business profiles, and social media profiles
 */

import type {
  UserProfile,
  UserProfileUpdate,
  ProfileCompletion,
  BusinessProfile,
  BusinessProfileUpdate,
  SocialMediaProfile,
  SocialMediaProfileUpdate,
  ProfileAnalytics,
  UserActivityAnalytics,
  ProfileInsightsResponse,
  ProfileInsight,
  UserActivityLog,
} from '../types/profiles';

import { apiCall } from './apiClient';

// ==================== User Profile APIs ====================

/**
 * Get user profile
 */
export const getUserProfile = async (): Promise<UserProfile> => {
  return apiCall<UserProfile>('/api/v1/profiles/user');
};

/**
 * Update user profile
 */
export const updateUserProfile = async (data: UserProfileUpdate): Promise<UserProfile> => {
  return apiCall<UserProfile>('/api/v1/profiles/user', 'PUT', data);
};

/**
 * Get profile completion percentage
 */
export const getProfileCompletion = async (): Promise<ProfileCompletion> => {
  return apiCall<ProfileCompletion>('/api/v1/profiles/user/completion');
};

// ==================== Business Profile APIs ====================

/**
 * Get business profile
 */
export const getBusinessProfile = async (): Promise<BusinessProfile> => {
  return apiCall<BusinessProfile>('/api/v1/profiles/business');
};

/**
 * Update business profile
 */
export const updateBusinessProfile = async (data: BusinessProfileUpdate): Promise<BusinessProfile> => {
  return apiCall<BusinessProfile>('/api/v1/profiles/business', 'PUT', data);
};

// ==================== Social Media Profile APIs ====================

/**
 * Get all social media profiles
 */
export const getSocialMediaProfiles = async (): Promise<SocialMediaProfile[]> => {
  return apiCall<SocialMediaProfile[]>('/api/v1/profiles/social');
};

/**
 * Add a new social media profile
 */
export const addSocialMediaProfile = async (data: {
  platform_name: string;
  platform_display_name?: string;
  platform_icon?: string;
  handle?: string;
  profile_url?: string;
  account_id?: string;
  account_type?: string;
  is_primary?: boolean;
  auto_sync_enabled?: boolean;
  sync_frequency?: string;
  sync_settings?: Record<string, any>;
}): Promise<SocialMediaProfile> => {
  return apiCall<SocialMediaProfile>('/api/v1/profiles/social', 'POST', data);
};

/**
 * Update a social media profile
 */
export const updateSocialMediaProfile = async (
  id: string,
  data: SocialMediaProfileUpdate
): Promise<SocialMediaProfile> => {
  return apiCall<SocialMediaProfile>(`/api/v1/profiles/social/${id}`, 'PUT', data);
};

/**
 * Delete a social media profile
 */
export const deleteSocialMediaProfile = async (id: string): Promise<void> => {
  return apiCall<void>(`/api/v1/profiles/social/${id}`, 'DELETE');
};

/**
 * Get social media metrics for a profile
 */
export const getSocialMediaMetrics = async (id: string): Promise<{
  profile_id: string;
  platform_name: string;
  current_metrics: Record<string, any>;
  historical_trends: Array<Record<string, any>>;
  performance_rating: string;
  insights: string[];
  recommendations: string[];
  benchmark_comparison?: Record<string, any>;
}> => {
  return apiCall(`/api/v1/profiles/social/${id}/metrics`);
};

// ==================== Analytics APIs ====================

/**
 * Get profile analytics overview
 */
export const getProfileAnalytics = async (): Promise<ProfileAnalytics> => {
  return apiCall<ProfileAnalytics>('/api/v1/profiles/analytics/overview');
};

/**
 * Get user activity data
 */
export const getUserActivity = async (timeRange: string = '7d'): Promise<UserActivityAnalytics> => {
  return apiCall<UserActivityAnalytics>(`/api/v1/profiles/analytics/activity?time_range=${timeRange}`);
};

/**
 * Get AI-generated insights
 */
export const getProfileInsights = async (
  limit: number = 10,
  unreadOnly: boolean = false
): Promise<ProfileInsightsResponse> => {
  const params = new URLSearchParams({ limit: limit.toString() });
  if (unreadOnly) params.append('unread_only', 'true');
  return apiCall<ProfileInsightsResponse>(`/api/v1/profiles/analytics/insights?${params.toString()}`);
};

/**
 * Generate new insights
 */
export const generateProfileInsights = async (): Promise<ProfileInsight[]> => {
  return apiCall<ProfileInsight[]>('/api/v1/profiles/analytics/insights/generate', 'POST');
};

/**
 * Mark insight as helpful/not helpful
 */
export const markInsightFeedback = async (
  id: string,
  feedback: 'helpful' | 'not_helpful',
  notes?: string
): Promise<ProfileInsight> => {
  return apiCall<ProfileInsight>(`/api/v1/profiles/analytics/insights/${id}/feedback`, 'POST', {
    feedback,
    notes,
  });
};

// ==================== Activity Log APIs ====================

/**
 * Get user activity logs
 */
export const getActivityLogs = async (
  limit: number = 20,
  offset: number = 0,
  activityType?: string
): Promise<{ items: UserActivityLog[]; total: number }> => {
  const params = new URLSearchParams({ limit: limit.toString(), offset: offset.toString() });
  if (activityType) params.append('activity_type', activityType);
  return apiCall(`/api/v1/profiles/activity?${params.toString()}`);
};

// ==================== Privacy Settings APIs ====================

/**
 * Get privacy settings
 */
export const getPrivacySettings = async (): Promise<{
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
}> => {
  return apiCall('/api/v1/profiles/privacy');
};

/**
 * Update privacy settings
 */
export const updatePrivacySettings = async (data: {
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
}): Promise<any> => {
  return apiCall('/api/v1/profiles/privacy', 'PUT', data);
};

// ==================== Utility Functions ====================

/**
 * Format date to readable string
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Format number with commas
 */
export const formatNumber = (num: number): string => {
  return num.toLocaleString('en-US');
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number): string => {
  return `${value.toFixed(1)}%`;
};

/**
 * Get platform icon based on platform name
 */
export const getPlatformIcon = (platformName: string): string => {
  const icons: Record<string, string> = {
    facebook: '📘',
    instagram: '📷',
    twitter: '🐦',
    linkedin: '💼',
    youtube: '📺',
    tiktok: '🎵',
    pinterest: '📌',
    snapchat: '👻',
    reddit: '🤖',
    whatsapp: '💬',
    telegram: '✈️',
    discord: '🎮',
  };
  return icons[platformName.toLowerCase()] || '🌐';
};

/**
 * Get platform color based on platform name
 */
export const getPlatformColor = (platformName: string): string => {
  const colors: Record<string, string> = {
    facebook: 'bg-blue-600',
    instagram: 'bg-pink-600',
    twitter: 'bg-sky-500',
    linkedin: 'bg-blue-700',
    youtube: 'bg-red-600',
    tiktok: 'bg-black',
    pinterest: 'bg-red-700',
    snapchat: 'bg-yellow-400',
    reddit: 'bg-orange-600',
    whatsapp: 'bg-green-500',
    telegram: 'bg-blue-400',
    discord: 'bg-indigo-600',
  };
  return colors[platformName.toLowerCase()] || 'bg-slate-600';
};
