/**
 * Mock API Service for Profiles
 * Simulates backend API responses with realistic delays and data
 * 
 * Usage:
 * - Set VITE_USE_MOCK_API=true in .env.local to enable mock mode
 * - All endpoints simulate realistic network latency
 * - Supports pagination, filtering, and search
 */

// Inline delay — ./mockDelay never existed as a module
const delay = (ms: number): Promise<void> => new Promise(resolve => setTimeout(resolve, ms));

// Import mock data generators
import { 
  generateMockUserProfiles,
  generateMockBusinessProfiles,
  generateMockSocialMediaProfiles,
  generateMockActivityLogs,
  generateMockPrivacySettings,
  generateMockProfileInsights,
  defaultMockUserProfiles,
  defaultMockBusinessProfiles,
  defaultMockSocialMediaProfiles,
  defaultMockActivityLogs,
  defaultMockPrivacySettings,
  defaultMockProfileInsights,
} from './profilesMockData';

// Import types
import type {
  UserProfile,
  BusinessProfile,
  SocialMediaProfile,
  SocialMediaProfileUpdate,
  UserActivityLog,
  PrivacySettings,
  ProfileInsight,
  UserProfileUpdate,
  BusinessProfileUpdate,
  ProfileCompletion,
  ProfileAnalytics,
  ProfileInsightsResponse,
} from '../../types/profiles';

// Type definitions for API responses
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Helper to simulate network delay
const API_DELAY = 300; // 300ms base delay
const API_DELAY_WITH_DATA = 500; // 500ms for endpoints that return data
const API_DELAY_MUTATION = 700; // 700ms for mutations

// ============================================================================
// USER PROFILE ENDPOINTS
// ============================================================================

export const userProfileMockApi = {
  /**
   * Get current user profile
   */
  async getUserProfile(userId?: string): Promise<ApiResponse<UserProfile>> {
    await delay(API_DELAY_WITH_DATA);
    
    const profiles = userId
      ? defaultMockUserProfiles.filter(p => p.user_id === userId)
      : [defaultMockUserProfiles[0]]; // Return first profile if no userId provided
    
    if (profiles.length === 0) {
      return {
        success: false,
        error: 'Profile not found',
      };
    }
    
    return {
      success: true,
      data: profiles[0] as unknown as UserProfile,
    };
  },

  /**
   * Create new user profile
   */
  async createUserProfile(userId: string, profileData: UserProfileUpdate): Promise<ApiResponse<UserProfile>> {
    await delay(API_DELAY_MUTATION);
    
    const newProfile: UserProfile = {
      id: `user-${Date.now()}`,
      user_id: userId,
      ...profileData,
      owns_business: (profileData as Partial<UserProfile>).owns_business ?? false,
      email_notifications_enabled: (profileData as Partial<UserProfile>).email_notifications_enabled ?? true,
      sms_notifications_enabled: (profileData as Partial<UserProfile>).sms_notifications_enabled ?? false,
      marketing_emails_enabled: (profileData as Partial<UserProfile>).marketing_emails_enabled ?? false,
      newsletter_subscription: (profileData as Partial<UserProfile>).newsletter_subscription ?? false,
      profile_completion_percentage: 0,
      last_profile_update: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    // Add to mock data (in-memory only)
    defaultMockUserProfiles.unshift(newProfile as unknown as (typeof defaultMockUserProfiles)[number]);
    
    return {
      success: true,
      data: newProfile,
      message: 'Profile created successfully',
    };
  },

  /**
   * Update user profile
   */
  async updateUserProfile(userId: string, profileData: UserProfileUpdate): Promise<ApiResponse<UserProfile>> {
    await delay(API_DELAY_MUTATION);
    
    const profile = defaultMockUserProfiles.find(p => p.user_id === userId);
    
    if (!profile) {
      return {
        success: false,
        error: 'Profile not found',
      };
    }
    
    const updatedProfile: UserProfile = {
      ...profile,
      ...profileData,
      created_at: (profile as { created_at?: string }).created_at ?? new Date().toISOString(),
      profile_completion_percentage: Math.min(100, profile.profile_completion_percentage + 5),
      last_profile_update: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as UserProfile;
    
    // Update in memory
    const index = defaultMockUserProfiles.findIndex(p => p.user_id === userId);
    if (index !== -1) {
      defaultMockUserProfiles[index] = updatedProfile as unknown as (typeof defaultMockUserProfiles)[number];
    }
    
    return {
      success: true,
      data: updatedProfile,
      message: 'Profile updated successfully',
    };
  },

  /**
   * Get profile completion status
   */
  async getProfileCompletion(userId: string): Promise<ApiResponse<ProfileCompletion>> {
    await delay(API_DELAY);
    
    const profile = defaultMockUserProfiles.find(p => p.user_id === userId);
    
    if (!profile) {
      return {
        success: false,
        error: 'Profile not found',
      };
    }
    
    const completionPercentage = profile.profile_completion_percentage;
    
    const missingFields: string[] = [];
    if (!profile.email) missingFields.push('email');
    if (!profile.phone) missingFields.push('phone');
    if (!profile.job_title) missingFields.push('job_title');
    if (!profile.industry_experience || profile.industry_experience.length === 0) missingFields.push('industry_experience');
    
    const recommendedFields: string[] = [];
    if (completionPercentage < 80) {
      recommendedFields.push('email', 'phone', 'job_title');
    }
    
    const completionTips: string[] = [
      completionPercentage >= 80 ? 'Your profile is excellent!' : 'Complete your profile to unlock all features',
      missingFields.length > 0 ? `You're missing ${missingFields.length} required fields` : '',
      recommendedFields.length > 0 ? 'Add recommended fields for better personalization' : '',
    ].filter(Boolean);
    
    return {
      success: true,
      data: {
        profile_id: profile.id,
        completion_percentage: completionPercentage,
        missing_fields: missingFields,
        recommended_fields: recommendedFields,
        completion_tips: completionTips,
      },
    };
  },

  /**
   * Export profile data
   */
  async exportProfileData(userId: string, format: 'json' | 'csv'): Promise<ApiResponse<string>> {
    await delay(API_DELAY_WITH_DATA * 2);
    
    const profile = defaultMockUserProfiles.find(p => p.user_id === userId);
    
    if (!profile) {
      return {
        success: false,
        error: 'Profile not found',
      };
    }
    
    // Simulate export data
    const exportData = format === 'json'
      ? JSON.stringify(profile, null, 2)
      : Object.entries(profile)
          .map(([key, value]) => `${key},"${value}"`)
          .join('\n');
    
    return {
      success: true,
      data: exportData,
      message: 'Profile data exported successfully',
    };
  },
};

// ============================================================================
// BUSINESS PROFILE ENDPOINTS
// ============================================================================

export const businessProfileMockApi = {
  /**
   * Get business profile
   */
  async getBusinessProfile(userId: string): Promise<ApiResponse<BusinessProfile>> {
    await delay(API_DELAY_WITH_DATA);
    
    const business = defaultMockBusinessProfiles.find(b => b.user_id === userId);
    
    if (!business) {
      return {
        success: false,
        error: 'Business profile not found',
      };
    }
    
    return {
      success: true,
      data: business as unknown as BusinessProfile,
    };
  },

  /**
   * Create business profile
   */
  async createBusinessProfile(userId: string, profileData: BusinessProfileUpdate): Promise<ApiResponse<BusinessProfile>> {
    await delay(API_DELAY_MUTATION);
    
    const newBusiness: BusinessProfile = {
      id: `business-${Date.now()}`,
      user_id: userId,
      ...profileData,
      profile_completeness_score: 0,
      last_data_refresh: undefined,
      data_quality_score: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    defaultMockBusinessProfiles.unshift(newBusiness as unknown as (typeof defaultMockBusinessProfiles)[number]);
    
    return {
      success: true,
      data: newBusiness,
      message: 'Business profile created successfully',
    };
  },

  /**
   * Update business profile
   */
  async updateBusinessProfile(userId: string, profileData: BusinessProfileUpdate): Promise<ApiResponse<BusinessProfile>> {
    await delay(API_DELAY_MUTATION);
    
    const business = defaultMockBusinessProfiles.find(b => b.user_id === userId);
    
    if (!business) {
      return {
        success: false,
        error: 'Business profile not found',
      };
    }
    
    const updatedBusiness: BusinessProfile = {
      ...business,
      ...profileData,
      created_at: (business as { created_at?: string }).created_at ?? new Date().toISOString(),
      profile_completeness_score: Math.min(100, business.profile_completeness_score + 5),
      last_data_refresh: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as BusinessProfile;
    
    const index = defaultMockBusinessProfiles.findIndex(b => b.user_id === userId);
    if (index !== -1) {
      defaultMockBusinessProfiles[index] = updatedBusiness as unknown as (typeof defaultMockBusinessProfiles)[number];
    }
    
    return {
      success: true,
      data: updatedBusiness,
      message: 'Business profile updated successfully',
    };
  },

  /**
   * Get business metrics
   */
  async getBusinessMetrics(businessId: string): Promise<ApiResponse<ProfileAnalytics>> {
    await delay(API_DELAY_WITH_DATA);
    
    const business = defaultMockBusinessProfiles.find(b => b.id === businessId);
    
    if (!business) {
      return {
        success: false,
        error: 'Business not found',
      };
    }
    
    // Metrics response shaped to ProfileAnalytics
    return {
      success: true,
      data: {
        user_profile_id: businessId,
        profile_completion: business.profile_completeness_score ?? 0,
        activity_summary: {
          revenue_growth: `+${(10 + Math.random() * 15).toFixed(1)}%`,
          customer_growth: `+${(5 + Math.random() * 10).toFixed(1)}%`,
        },
        social_media_summary: {},
        engagement_metrics: {
          engagement_score: (7 + Math.random() * 3).toFixed(1),
          market_position: ['Top 10%', 'Top 25%', 'Top 50%', 'Average'][Math.floor(Math.random() * 4)],
        },
        key_insights: [],
        recommendations: [],
      },
    };
  },

  /**
   * Trigger data enrichment
   */
  async enrichBusinessProfile(businessId: string): Promise<ApiResponse<any>> {
    await delay(API_DELAY_MUTATION * 2);
    
    const business = defaultMockBusinessProfiles.find(b => b.id === businessId);
    
    if (!business) {
      return {
        success: false,
        error: 'Business not found',
      };
    }
    
    return {
      success: true,
      data: {
        profile_id: businessId,
        enriched_fields: {
          'industry_classification': 'Technology',
          'business_stage_inferred': 'growth',
          'competitive_landscape': {
            'total_competitors': Math.floor(5 + Math.random() * 15),
            'market_share': (1 + Math.random() * 20).toFixed(2) + '%',
          },
        },
        recommendations: [
          'Increase social media presence',
          'Focus on customer retention',
          'Expand to international markets',
        ],
      },
      message: 'Business profile enriched successfully',
    };
  },
};

// ============================================================================
// SOCIAL MEDIA ENDPOINTS
// ============================================================================

export const socialMediaMockApi = {
  /**
   * Get all social media profiles for a user
   */
  async getSocialMediaProfiles(userId: string): Promise<ApiResponse<SocialMediaProfile[]>> {
    await delay(API_DELAY_WITH_DATA);
    
    const profiles = defaultMockSocialMediaProfiles.filter(p => p.user_profile_id === userId);
    
    return {
      success: true,
      data: profiles as unknown as SocialMediaProfile[],
    };
  },

  /**
   * Add social media profile
   */
  async addSocialMediaProfile(
    userId: string,
    profileData: SocialMediaProfileUpdate & { platform_name: string }
  ): Promise<ApiResponse<SocialMediaProfile>> {
    await delay(API_DELAY_MUTATION);
    
    const newProfile: SocialMediaProfile = {
      id: `social-${Date.now()}`,
      user_profile_id: userId,
      business_profile_id: profileData.account_type === 'business' ? userId : undefined,
      platform_name: profileData.platform_name,
      platform_display_name: profileData.platform_name.toUpperCase(),
      platform_icon: profileData.platform_name.toLowerCase(),
      handle: profileData.handle,
      profile_url: profileData.profile_url,
      account_type: profileData.account_type || 'business',
      is_verified: Math.random() > 0.7,
      is_primary: Math.random() > 0.8,
      is_connected: false,
      connection_date: undefined,
      last_sync_date: undefined,
      sync_status: 'not_synced',
      metrics: undefined,
      historical_metrics: [],
      content_categories: [],
      posting_schedule: undefined,
      auto_sync_enabled: profileData.auto_sync_enabled || false,
      sync_frequency: profileData.sync_frequency || 'daily',
      engagement_score: undefined,
      influence_score: undefined,
      growth_rate: undefined,
      performance_rating: undefined,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    defaultMockSocialMediaProfiles.unshift(newProfile as unknown as (typeof defaultMockSocialMediaProfiles)[number]);
    
    return {
      success: true,
      data: newProfile,
      message: 'Social media profile added successfully',
    };
  },

  /**
   * Sync social media profile (simulated)
   */
  async syncSocialMediaProfile(profileId: string): Promise<ApiResponse<SocialMediaProfile>> {
    await delay(API_DELAY_MUTATION * 2);
    
    const profile = defaultMockSocialMediaProfiles.find(p => p.id === profileId);
    
    if (!profile) {
      return {
        success: false,
        error: 'Social media profile not found',
      };
    }
    
    // Simulate sync with new metrics
    const updatedProfile: SocialMediaProfile = {
      ...profile,
      created_at: (profile as { created_at?: string }).created_at ?? new Date().toISOString(),
      is_connected: true,
      connection_date: new Date().toISOString(),
      last_sync_date: new Date().toISOString(),
      sync_status: 'synced',
      metrics: {
        followers: Math.floor(1000 + Math.random() * 5000),
        following: Math.floor(100 + Math.random() * 500),
        posts: Math.floor(50 + Math.random() * 200),
        engagement_rate: parseFloat((2 + Math.random() * 6).toFixed(2)),
        avg_likes: Math.floor(50 + Math.random() * 200),
        avg_comments: Math.floor(20 + Math.random() * 50),
        avg_shares: Math.floor(10 + Math.random() * 30),
        reach: Math.floor(5000 + Math.random() * 10000),
        impressions: Math.floor(10000 + Math.random() * 20000),
        profile_views: Math.floor(500 + Math.random() * 1000),
        clicks: Math.floor(100 + Math.random() * 300),
        mentions: Math.floor(5 + Math.random() * 50),
        hashtags: ['business', 'growth', 'innovation'],
        last_post_date: new Date().toISOString().split('T')[0],
        posting_frequency: ['daily', 'weekly', 'monthly'][Math.floor(Math.random() * 3)],
        best_posting_time: ['09:00', '12:00', '15:00', '18:00'][Math.floor(Math.random() * 4)],
        top_performing_content: ['video', 'carousel', 'image', 'text'].sort(() => 0.5 - Math.random()).slice(0, 2 + Math.floor(Math.random() * 2)),
        audience_demographics: {
          age: { '18-24': 20, '25-34': 40, '35-44': 30, '45+': 10 },
          gender: { 'male': 45, 'female': 55 },
          location: { 'US': 60, 'UK': 20, 'Canada': 10, 'Other': 10 },
        },
      },
      historical_metrics: Array.from({ length: 6 }, (_, i) => ({
        date: new Date(Date.now() - (6 - i) * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        metrics: {
          followers: Math.floor(500 + (6 - i) * 200 + Math.random() * 200),
          engagement_rate: parseFloat(((1.5 + (6 - i) * 0.5 + Math.random() * 2)).toFixed(2)),
        },
      })),
      engagement_score: parseFloat(((6 + Math.random() * 4)).toFixed(2)),
      influence_score: parseFloat(((5 + Math.random() * 5)).toFixed(2)),
      growth_rate: parseFloat(((3 + Math.random() * 8)).toFixed(2)),
      performance_rating: ['excellent', 'good', 'average', 'poor'][Math.floor(Math.random() * 4)],
      updated_at: new Date().toISOString(),
    };
    
    const index = defaultMockSocialMediaProfiles.findIndex(p => p.id === profileId);
    if (index !== -1) {
      defaultMockSocialMediaProfiles[index] = updatedProfile as unknown as (typeof defaultMockSocialMediaProfiles)[number];
    }
    
    return {
      success: true,
      data: updatedProfile,
      message: 'Social media profile synced successfully',
    };
  },

  /**
   * Get profile analytics
   */
  async getProfileAnalytics(profileId: string): Promise<ApiResponse<any>> {
    await delay(API_DELAY_WITH_DATA);
    
    const profile = defaultMockSocialMediaProfiles.find(p => p.id === profileId);
    
    if (!profile || !profile.is_connected) {
      return {
        success: false,
        error: 'Social media profile not found or not connected',
      };
    }
    
    return {
      success: true,
      data: {
        profile_id: profileId,
        platform_name: profile.platform_name,
        current_metrics: profile.metrics,
        historical_trends: profile.historical_metrics,
        engagement_score: profile.engagement_score,
        influence_score: profile.influence_score,
        growth_rate: profile.growth_rate,
        performance_rating: profile.performance_rating,
        insights: [
          'Your engagement rate is above industry average',
          'Consider increasing posting frequency',
          'Try video content for higher engagement',
          'Your audience demographics are well-balanced',
        ],
        recommendations: [
          'Maintain current posting schedule',
          'Expand to new content types',
          'Engage more with commenters',
        ],
      },
      message: 'Profile analytics retrieved successfully',
    };
  },
};

// ============================================================================
// ANALYTICS ENDPOINTS
// ============================================================================

export const analyticsMockApi = {
  /**
   * Get profile analytics overview
   */
  async getProfileAnalytics(userId: string, timeRange: string = '30d'): Promise<ApiResponse<ProfileAnalytics>> {
    await delay(API_DELAY_WITH_DATA * 2);
    
    const userProfiles = defaultMockUserProfiles.filter(p => p.user_id === userId);
    const userProfile = userProfiles[0];
    const businessProfiles = defaultMockBusinessProfiles.filter(b => b.user_id === userId);
    const socialProfiles = defaultMockSocialMediaProfiles.filter(p => p.user_profile_id === userId);
    const activityLogs = defaultMockActivityLogs.filter(a => a.user_profile_id === userId);
    
    const totalFollowers = socialProfiles.reduce((sum, p) => sum + (p.metrics?.followers || 0), 0);
    const avgEngagement = socialProfiles.length > 0
      ? (socialProfiles.reduce((sum, p) => sum + (p.engagement_score || 0), 0) / socialProfiles.length)
      : 0;
    
    return {
      success: true,
      data: {
        user_profile_id: userId,
        profile_completion: userProfile.profile_completion_percentage,
        activity_summary: {
          total_sessions: activityLogs.filter(a => a.activity_type === 'login').length,
          total_time_spent: activityLogs.reduce((sum, a) => sum + (a.interaction_time || 0), 0),
          most_used_features: ['dashboard', 'bmc', 'strategy'].slice(0, 3 + Math.floor(Math.random() * 3)),
          activity_by_category: {
            'dashboard': activityLogs.filter(a => a.activity_category === 'dashboard').length,
            'bmc': activityLogs.filter(a => a.activity_category === 'bmc').length,
            'strategy': activityLogs.filter(a => a.activity_category === 'strategy').length,
            'leads': activityLogs.filter(a => a.activity_category === 'leads').length,
          },
        },
        social_media_summary: {
          total_profiles: socialProfiles.filter(p => p.is_connected).length,
          total_followers: totalFollowers,
          avg_engagement: parseFloat(avgEngagement.toFixed(2)),
        },
        engagement_metrics: {
          daily_active_users: Math.floor(20 + Math.random() * 30),
          weekly_growth_rate: `+${(2 + Math.random() * 8).toFixed(1)}%`,
          best_performing_day: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][Math.floor(Math.random() * 5)],
        },
        key_insights: [
          'Your LinkedIn engagement is above industry average',
          'Consider adding Instagram to reach younger demographics',
          'Posting frequency shows optimal engagement',
          'Profile completion could be improved by adding phone number',
        ],
        recommendations: [
          'Maintain current posting frequency',
          'Expand to video content for increased reach',
          'Collaborate with industry leaders for partnerships',
        ],
      },
      message: 'Analytics overview retrieved successfully',
    };
  },

  /**
   * Get activity logs
   */
  async getActivityLogs(userId: string, options?: {
    skip?: number;
    limit?: number;
    activity_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<ApiResponse<UserActivityLog[]>> {
    await delay(API_DELAY);
    
    let logs = defaultMockActivityLogs.filter(a => a.user_profile_id === userId);
    
    if (options?.activity_type) {
      logs = logs.filter(a => a.activity_type === options.activity_type);
    }
    
    if (options?.start_date) {
      logs = logs.filter(a => new Date(a.created_at) >= new Date(options.start_date));
    }
    
    if (options?.end_date) {
      logs = logs.filter(a => new Date(a.created_at) <= new Date(options.end_date));
    }
    
    if (options?.skip) {
      logs = logs.slice(options.skip);
    }
    
    if (options?.limit) {
      logs = logs.slice(0, options.limit);
    }
    
    return {
      success: true,
      data: logs,
    };
  },
};

// ============================================================================
// INSIGHTS ENDPOINTS
// ============================================================================

export const insightsMockApi = {
  /**
   * Get profile insights
   */
  async getProfileInsights(userId: string, options?: {
    limit?: number;
    insight_type?: string;
    priority?: string;
    status?: string;
  }): Promise<ApiResponse<ProfileInsightsResponse>> {
    await delay(API_DELAY);
    
    const insights = defaultMockProfileInsights.filter(i => i.user_profile_id === userId);
    
    let filteredInsights = insights;
    
    if (options?.insight_type) {
      filteredInsights = filteredInsights.filter(i => i.insight_type === options.insight_type);
    }
    
    if (options?.priority) {
      filteredInsights = filteredInsights.filter(i => i.priority === options.priority);
    }
    
    if (options?.status) {
      filteredInsights = filteredInsights.filter(i => i.status === options.status);
    }
    
    if (options?.limit) {
      filteredInsights = filteredInsights.slice(0, options.limit);
    }
    
    const unreadCount = filteredInsights.filter(i => i.status === 'new').length;
    const highPriorityCount = filteredInsights.filter(i => i.priority === 'high').length;
    
    // Count by category
    const categories: Record<string, number> = {
      'growth_opportunity': filteredInsights.filter(i => i.insight_type === 'growth_opportunity').length,
      'risk_alert': filteredInsights.filter(i => i.insight_type === 'risk_alert').length,
      'recommendation': filteredInsights.filter(i => i.insight_type === 'recommendation').length,
    };
    
    return {
      success: true,
      data: {
        insights: filteredInsights,
        total: filteredInsights.length,
        unread_count: unreadCount,
        high_priority_count: highPriorityCount,
        categories,
      },
      message: 'Insights retrieved successfully',
    };
  },

  /**
   * Provide feedback on insight
   */
  async provideInsightFeedback(
    insightId: string,
    feedback: 'helpful' | 'not_helpful' | 'neutral'
  ): Promise<ApiResponse<any>> {
    await delay(API_DELAY_MUTATION);
    
    const insight = defaultMockProfileInsights.find(i => i.id === insightId);
    
    if (!insight) {
      return {
        success: false,
        error: 'Insight not found',
      };
    }
    
    const updatedInsight: ProfileInsight = {
      ...insight,
      user_feedback: feedback,
      last_updated: new Date().toISOString(),
    };
    
    const index = defaultMockProfileInsights.findIndex(i => i.id === insightId);
    if (index !== -1) {
      defaultMockProfileInsights[index] = updatedInsight;
    }
    
    return {
      success: true,
      data: updatedInsight,
      message: 'Feedback recorded successfully',
    };
  },

  /**
   * Dismiss an insight
   */
  async dismissInsight(insightId: string): Promise<ApiResponse<any>> {
    await delay(API_DELAY_MUTATION);
    
    const insight = defaultMockProfileInsights.find(i => i.id === insightId);
    
    if (!insight) {
      return {
        success: false,
        error: 'Insight not found',
      };
    }
    
    const updatedInsight: ProfileInsight = {
      ...insight,
      status: 'dismissed',
      last_updated: new Date().toISOString(),
    };
    
    const index = defaultMockProfileInsights.findIndex(i => i.id === insightId);
    if (index !== -1) {
      defaultMockProfileInsights[index] = updatedInsight;
    }
    
    return {
      success: true,
      data: updatedInsight,
      message: 'Insight dismissed successfully',
    };
  },
};

// ============================================================================
// COMBINED EXPORT
// ============================================================================

export const profilesMockApi = {
  // User Profile APIs
  getUserProfile: userProfileMockApi.getUserProfile,
  createUserProfile: userProfileMockApi.createUserProfile,
  updateUserProfile: userProfileMockApi.updateUserProfile,
  getProfileCompletion: userProfileMockApi.getProfileCompletion,
  exportProfileData: userProfileMockApi.exportProfileData,

  // Business Profile APIs
  getBusinessProfile: businessProfileMockApi.getBusinessProfile,
  createBusinessProfile: businessProfileMockApi.createBusinessProfile,
  updateBusinessProfile: businessProfileMockApi.updateBusinessProfile,
  getBusinessMetrics: businessProfileMockApi.getBusinessMetrics,
  enrichBusinessProfile: businessProfileMockApi.enrichBusinessProfile,

  // Social Media APIs
  getSocialMediaProfiles: socialMediaMockApi.getSocialMediaProfiles,
  addSocialMediaProfile: socialMediaMockApi.addSocialMediaProfile,
  syncSocialMediaProfile: socialMediaMockApi.syncSocialMediaProfile,
  getSocialMediaProfileAnalytics: socialMediaMockApi.getProfileAnalytics,

  // Analytics APIs
  getProfileAnalytics: analyticsMockApi.getProfileAnalytics,
  getActivityLogs: analyticsMockApi.getActivityLogs,

  // Insights APIs
  getProfileInsights: insightsMockApi.getProfileInsights,
  provideInsightFeedback: insightsMockApi.provideInsightFeedback,
  dismissInsight: insightsMockApi.dismissInsight,
};

// ============================================================================
// MOCK DELAY UTILITY
// ============================================================================

export const mockDelay = (ms: number = API_DELAY): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};
