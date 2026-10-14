/**
 * Profile Context
 * Manages state for user profiles, business profiles, and social media profiles
 */

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
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
import {
  getUserProfile,
  updateUserProfile,
  getProfileCompletion,
  getBusinessProfile,
  updateBusinessProfile,
  getSocialMediaProfiles,
  addSocialMediaProfile as addSocialMediaProfileApi,
  updateSocialMediaProfile as updateSocialMediaProfileApi,
  deleteSocialMediaProfile as deleteSocialMediaProfileApi,
  getProfileAnalytics,
  getUserActivity,
  getProfileInsights,
  generateProfileInsights,
  markInsightFeedback,
  getActivityLogs,
} from '../services/profileService';

export enum ProfileSetupState {
  NOT_STARTED = 'not_started',
  AI_INITIALIZING = 'ai_initializing',
  AWAITING_BUSINESS_INFO = 'awaiting_business_info',
  AWAITING_SOCIAL_SYNC = 'awaiting_social_sync',
  ENRICHING_DATA = 'enriching_data',
  READY_FOR_AI = 'ready_for_ai',
  COMPLETED = 'completed'
}

export interface SetupPrompt {
  id: string;
  type: 'critical' | 'enhancement' | 'social' | 'verification';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  value_prop: string;
  action_label: string;
  fields?: string[];
  suggested_value?: string;
  confidence_score?: number;
}

export interface AISuggestion {
  id: string;
  field: string;
  suggested_value: string;
  confidence_score: number;
  reason: string;
  accepted: boolean;
}

export interface PlatformRecommendation {
  platform: string;
  platform_name: string;
  icon: string;
  priority: 'high' | 'medium' | 'low';
  reason: string;
  value_prop: string;
  expected_benefits: string[];
  connection_status?: 'not_connected' | 'connecting' | 'connected' | 'error';
}

interface ProfileState {
  // User Profile
  userProfile: UserProfile | null;
  userProfileLoading: boolean;
  userProfileError: string | null;

  // Profile Completion
  profileCompletion: ProfileCompletion | null;
  profileCompletionLoading: boolean;
  profileCompletionError: string | null;

  // Business Profile
  businessProfile: BusinessProfile | null;
  businessProfileLoading: boolean;
  businessProfileError: string | null;

  // Social Media Profiles
  socialMediaProfiles: SocialMediaProfile[];
  socialMediaLoading: boolean;
  socialMediaError: string | null;

  // Analytics
  profileAnalytics: ProfileAnalytics | null;
  analyticsLoading: boolean;
  analyticsError: string | null;

  // User Activity
  userActivity: UserActivityAnalytics | null;
  activityLoading: boolean;
  activityError: string | null;

  // Insights
  insights: ProfileInsight[];
  insightsLoading: boolean;
  insightsError: string | null;
  insightsTotal: number;
  insightsUnread: number;
  insightsHighPriority: number;

  // Activity Logs
  activityLogs: UserActivityLog[];
  activityLogsLoading: boolean;
  activityLogsError: string | null;
  activityLogsTotal: number;

  // AI Profile Assistant
  profileState: ProfileSetupState;
  setupPrompts: SetupPrompt[];
  aiSuggestions: AISuggestion[];
  platformRecommendations: PlatformRecommendation[];
  enrichmentProgress: number;
  assistantLoading: boolean;
  assistantError: string | null;
}

interface ProfileContextType extends ProfileState {
  // User Profile Actions
  fetchUserProfile: () => Promise<void>;
  updateUserProfileData: (data: UserProfileUpdate) => Promise<void>;
  fetchProfileCompletion: () => Promise<void>;

  // Business Profile Actions
  fetchBusinessProfile: () => Promise<void>;
  updateBusinessProfileData: (data: BusinessProfileUpdate) => Promise<void>;

  // Social Media Actions
  fetchSocialMediaProfiles: () => Promise<void>;
  addSocialMediaProfile: (data: {
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
  }) => Promise<void>;
  updateSocialMediaProfile: (id: string, data: SocialMediaProfileUpdate) => Promise<void>;
  deleteSocialMediaProfile: (id: string) => Promise<void>;

  // Analytics Actions
  fetchProfileAnalytics: () => Promise<void>;
  fetchUserActivity: (timeRange?: string) => Promise<void>;

  // Insights Actions
  fetchInsights: (limit?: number, unreadOnly?: boolean) => Promise<void>;
  generateNewInsights: () => Promise<void>;
  provideInsightFeedback: (id: string, feedback: 'helpful' | 'not_helpful', notes?: string) => Promise<void>;

  // Activity Logs Actions
  fetchActivityLogs: (limit?: number, offset?: number, activityType?: string) => Promise<void>;

  // AI Profile Assistant Actions
  fetchProfileAnalysis: () => Promise<void>;
  fetchSetupPrompts: () => Promise<void>;
  enrichProfile: () => Promise<void>;
  acceptAISuggestion: (suggestionId: string) => Promise<void>;
  dismissPrompt: (promptId: string) => void;
  connectPlatform: (platform: string) => Promise<void>;

  // Refresh All
  refreshAll: () => Promise<void>;

  // Reset Actions
  resetUserProfile: () => void;
  resetBusinessProfile: () => void;
  resetSocialMediaProfiles: () => void;
  resetAnalytics: () => void;
  resetInsights: () => void;
  resetActivityLogs: () => void;
  resetAssistant: () => void;
  resetAll: () => void;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

const initialState: ProfileState = {
  userProfile: null,
  userProfileLoading: false,
  userProfileError: null,

  profileCompletion: null,
  profileCompletionLoading: false,
  profileCompletionError: null,

  businessProfile: null,
  businessProfileLoading: false,
  businessProfileError: null,

  socialMediaProfiles: [],
  socialMediaLoading: false,
  socialMediaError: null,

  profileAnalytics: null,
  analyticsLoading: false,
  analyticsError: null,

  userActivity: null,
  activityLoading: false,
  activityError: null,

  insights: [],
  insightsLoading: false,
  insightsError: null,
  insightsTotal: 0,
  insightsUnread: 0,
  insightsHighPriority: 0,

  activityLogs: [],
  activityLogsLoading: false,
  activityLogsError: null,
  activityLogsTotal: 0,

  profileState: ProfileSetupState.NOT_STARTED,
  setupPrompts: [],
  aiSuggestions: [],
  platformRecommendations: [],
  enrichmentProgress: 0,
  assistantLoading: false,
  assistantError: null,
};

export const ProfileProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<ProfileState>(initialState);

  // User Profile Actions
  const fetchUserProfile = useCallback(async () => {
    setState((prev) => ({ ...prev, userProfileLoading: true, userProfileError: null }));
    try {
      const profile = await getUserProfile();
      setState((prev) => ({ ...prev, userProfile: profile, userProfileLoading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        userProfileError: error instanceof Error ? error.message : 'Failed to fetch user profile',
        userProfileLoading: false,
      }));
    }
  }, []);

  const updateUserProfileData = useCallback(async (data: UserProfileUpdate) => {
    setState((prev) => ({ ...prev, userProfileLoading: true, userProfileError: null }));
    try {
      const updatedProfile = await updateUserProfile(data);
      setState((prev) => ({ ...prev, userProfile: updatedProfile, userProfileLoading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        userProfileError: error instanceof Error ? error.message : 'Failed to update user profile',
        userProfileLoading: false,
      }));
      throw error;
    }
  }, []);

  const fetchProfileCompletion = useCallback(async () => {
    setState((prev) => ({ ...prev, profileCompletionLoading: true, profileCompletionError: null }));
    try {
      const completion = await getProfileCompletion();
      setState((prev) => ({ ...prev, profileCompletion: completion, profileCompletionLoading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        profileCompletionError: error instanceof Error ? error.message : 'Failed to fetch profile completion',
        profileCompletionLoading: false,
      }));
    }
  }, []);

  // Business Profile Actions
  const fetchBusinessProfile = useCallback(async () => {
    setState((prev) => ({ ...prev, businessProfileLoading: true, businessProfileError: null }));
    try {
      const profile = await getBusinessProfile();
      setState((prev) => ({ ...prev, businessProfile: profile, businessProfileLoading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        businessProfileError: error instanceof Error ? error.message : 'Failed to fetch business profile',
        businessProfileLoading: false,
      }));
    }
  }, []);

  const updateBusinessProfileData = useCallback(async (data: BusinessProfileUpdate) => {
    setState((prev) => ({ ...prev, businessProfileLoading: true, businessProfileError: null }));
    try {
      const updatedProfile = await updateBusinessProfile(data);
      setState((prev) => ({ ...prev, businessProfile: updatedProfile, businessProfileLoading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        businessProfileError: error instanceof Error ? error.message : 'Failed to update business profile',
        businessProfileLoading: false,
      }));
      throw error;
    }
  }, []);

  // Social Media Actions
  const fetchSocialMediaProfiles = useCallback(async () => {
    setState((prev) => ({ ...prev, socialMediaLoading: true, socialMediaError: null }));
    try {
      const profiles = await getSocialMediaProfiles();
      setState((prev) => ({ ...prev, socialMediaProfiles: profiles, socialMediaLoading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        socialMediaError: error instanceof Error ? error.message : 'Failed to fetch social media profiles',
        socialMediaLoading: false,
      }));
    }
  }, []);

  const addSocialMediaProfile = useCallback(async (data: {
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
  }) => {
    setState((prev) => ({ ...prev, socialMediaLoading: true, socialMediaError: null }));
    try {
      const newProfile = await addSocialMediaProfileApi(data);
      setState((prev) => ({
        ...prev,
        socialMediaProfiles: [...prev.socialMediaProfiles, newProfile],
        socialMediaLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        socialMediaError: error instanceof Error ? error.message : 'Failed to add social media profile',
        socialMediaLoading: false,
      }));
      throw error;
    }
  }, []);

  const updateSocialMediaProfile = useCallback(async (id: string, data: SocialMediaProfileUpdate) => {
    setState((prev) => ({ ...prev, socialMediaLoading: true, socialMediaError: null }));
    try {
      const updatedProfile = await updateSocialMediaProfileApi(id, data);
      setState((prev) => ({
        ...prev,
        socialMediaProfiles: prev.socialMediaProfiles.map((p) => (p.id === id ? updatedProfile : p)),
        socialMediaLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        socialMediaError: error instanceof Error ? error.message : 'Failed to update social media profile',
        socialMediaLoading: false,
      }));
      throw error;
    }
  }, []);

  const deleteSocialMediaProfile = useCallback(async (id: string) => {
    setState((prev) => ({ ...prev, socialMediaLoading: true, socialMediaError: null }));
    try {
      await deleteSocialMediaProfileApi(id);
      setState((prev) => ({
        ...prev,
        socialMediaProfiles: prev.socialMediaProfiles.filter((p) => p.id !== id),
        socialMediaLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        socialMediaError: error instanceof Error ? error.message : 'Failed to delete social media profile',
        socialMediaLoading: false,
      }));
      throw error;
    }
  }, []);

  // Analytics Actions
  const fetchProfileAnalytics = useCallback(async () => {
    setState((prev) => ({ ...prev, analyticsLoading: true, analyticsError: null }));
    try {
      const analytics = await getProfileAnalytics();
      setState((prev) => ({ ...prev, profileAnalytics: analytics, analyticsLoading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        analyticsError: error instanceof Error ? error.message : 'Failed to fetch profile analytics',
        analyticsLoading: false,
      }));
    }
  }, []);

  const fetchUserActivity = useCallback(async (timeRange: string = '7d') => {
    setState((prev) => ({ ...prev, activityLoading: true, activityError: null }));
    try {
      const activity = await getUserActivity(timeRange);
      setState((prev) => ({ ...prev, userActivity: activity, activityLoading: false }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        activityError: error instanceof Error ? error.message : 'Failed to fetch user activity',
        activityLoading: false,
      }));
    }
  }, []);

  // Insights Actions
  const fetchInsights = useCallback(async (limit: number = 10, unreadOnly: boolean = false) => {
    setState((prev) => ({ ...prev, insightsLoading: true, insightsError: null }));
    try {
      const response = await getProfileInsights(limit, unreadOnly);
      setState((prev) => ({
        ...prev,
        insights: response.insights as ProfileInsight[],
        insightsTotal: response.total,
        insightsUnread: response.unread_count,
        insightsHighPriority: response.high_priority_count,
        insightsLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        insightsError: error instanceof Error ? error.message : 'Failed to fetch insights',
        insightsLoading: false,
      }));
    }
  }, []);

  const generateNewInsights = useCallback(async () => {
    setState((prev) => ({ ...prev, insightsLoading: true, insightsError: null }));
    try {
      const newInsights = await generateProfileInsights();
      setState((prev) => ({
        ...prev,
        insights: [...newInsights, ...prev.insights],
        insightsLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        insightsError: error instanceof Error ? error.message : 'Failed to generate insights',
        insightsLoading: false,
      }));
      throw error;
    }
  }, []);

  const provideInsightFeedback = useCallback(async (id: string, feedback: 'helpful' | 'not_helpful', notes?: string) => {
    try {
      const updatedInsight = await markInsightFeedback(id, feedback, notes);
      setState((prev) => ({
        ...prev,
        insights: prev.insights.map((i) => (i.id === id ? updatedInsight : i)),
      }));
    } catch (error) {
      console.error('Failed to provide feedback:', error);
      throw error;
    }
  }, []);

  // Activity Logs Actions
  const fetchActivityLogs = useCallback(async (limit: number = 20, offset: number = 0, activityType?: string) => {
    setState((prev) => ({ ...prev, activityLogsLoading: true, activityLogsError: null }));
    try {
      const response = await getActivityLogs(limit, offset, activityType);
      setState((prev) => ({
        ...prev,
        activityLogs: response.items,
        activityLogsTotal: response.total,
        activityLogsLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        activityLogsError: error instanceof Error ? error.message : 'Failed to fetch activity logs',
        activityLogsLoading: false,
      }));
    }
  }, []);

  // AI Profile Assistant Actions
  const fetchProfileAnalysis = useCallback(async () => {
    setState((prev) => ({ ...prev, assistantLoading: true, assistantError: null }));

    try {
      const userProfile = await getUserProfile();
      const businessProfile = await getBusinessProfile();
      const socialProfiles = await getSocialMediaProfiles();
      const completion = await getProfileCompletion();

      let profileState: ProfileSetupState = ProfileSetupState.NOT_STARTED;
      let setupPrompts: SetupPrompt[] = [];
      let platformRecommendations: PlatformRecommendation[] = [];
      let aiSuggestions: AISuggestion[] = [];

      const completionScore = completion?.completion_percentage || 0;

      if (completionScore === 0) {
        profileState = ProfileSetupState.NOT_STARTED;
        setupPrompts.push({
          id: 'user-profile-basic',
          type: 'critical',
          priority: 'high',
          title: 'Complete Your User Profile',
          description: 'Add your basic information to get started',
          value_prop: 'A complete user profile enables personalized AI recommendations',
          action_label: 'Add Profile Info',
          fields: ['name', 'email', 'preferences'],
        });
      } else if (completionScore < 30) {
        profileState = ProfileSetupState.AI_INITIALIZING;
        setupPrompts.push({
          id: 'business-profile-basic',
          type: 'critical',
          priority: 'high',
          title: 'Add Your Business Information',
          description: 'Tell us about your business to unlock AI insights',
          value_prop: 'Business information powers our AI analysis and recommendations',
          action_label: 'Add Business Info',
          fields: ['company_name', 'industry', 'business_type'],
        });
      } else if (completionScore < 60) {
        profileState = ProfileSetupState.AWAITING_SOCIAL_SYNC;
        setupPrompts.push({
          id: 'social-media-sync',
          type: 'social',
          priority: 'high',
          title: 'Connect Your Social Media',
          description: 'Sync your social media accounts to unlock audience insights',
          value_prop: 'Social media data enhances AI-powered audience analysis and competitive insights',
          action_label: 'Connect Platforms',
        });

        if (businessProfile?.industry) {
          const industry = businessProfile.industry.toLowerCase();
          if (industry.includes('retail') || industry.includes('ecommerce')) {
            platformRecommendations.push({
              platform: 'instagram',
              platform_name: 'Instagram',
              icon: '📸',
              priority: 'high',
              reason: 'Your business is visual-focused',
              value_prop: 'Unlock product showcase and brand visibility insights',
              expected_benefits: ['Visual content analysis', 'Audience demographics', 'Competitor tracking'],
            });
          }
          if (industry.includes('b2b') || industry.includes('consulting') || industry.includes('saas')) {
            platformRecommendations.push({
              platform: 'linkedin',
              platform_name: 'LinkedIn',
              icon: '💼',
              priority: 'high',
              reason: 'B2B businesses perform better on LinkedIn',
              value_prop: 'Access professional audience insights and lead generation data',
              expected_benefits: ['Professional network analysis', 'Lead scoring', 'Content performance'],
            });
          }
        }
      } else if (completionScore < 80) {
        profileState = ProfileSetupState.ENRICHING_DATA;
        setupPrompts.push({
          id: 'enhance-profile',
          type: 'enhancement',
          priority: 'medium',
          title: 'Enhance Your Profile',
          description: 'Add more details to improve AI recommendations',
          value_prop: 'Complete profiles receive more accurate and personalized AI insights',
          action_label: 'Enhance Profile',
        });

        if (businessProfile) {
          if (!businessProfile.target_market?.length) {
            aiSuggestions.push({
              id: 'suggestion-target-audience',
              field: 'target_market',
              suggested_value: 'Based on your industry, we recommend targeting professionals aged 25-45',
              confidence_score: 0.75,
              reason: 'Your industry typically targets this demographic',
              accepted: false,
            });
          }
          if (!businessProfile.short_term_goals?.length && !businessProfile.long_term_goals?.length) {
            aiSuggestions.push({
              id: 'suggestion-business-goals',
              field: 'business_goals',
              suggested_value: 'Increase brand awareness, generate leads, improve customer retention',
              confidence_score: 0.70,
              reason: 'Common goals for your business stage',
              accepted: false,
            });
          }
        }
      } else if (completionScore < 100) {
        profileState = ProfileSetupState.READY_FOR_AI;
        setupPrompts.push({
          id: 'complete-profile',
          type: 'verification',
          priority: 'low',
          title: 'Complete Your Profile',
          description: 'Add final details to reach 100% completion',
          value_prop: 'Fully optimized profiles unlock all AI features',
          action_label: 'Complete Profile',
        });
      } else {
        profileState = ProfileSetupState.COMPLETED;
      }

      setState((prev) => ({
        ...prev,
        profileState,
        setupPrompts,
        aiSuggestions,
        platformRecommendations,
        userProfile,
        businessProfile,
        socialMediaProfiles: socialProfiles,
        profileCompletion: completion,
        assistantLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        assistantError: error instanceof Error ? error.message : 'Failed to analyze profile',
        assistantLoading: false,
        profileState: ProfileSetupState.NOT_STARTED,
      }));
    }
  }, []);

  const fetchSetupPrompts = useCallback(async () => {
    setState((prev) => ({ ...prev, assistantLoading: true, assistantError: null }));
    try {
      await fetchProfileAnalysis();
    } catch (error) {
      console.error('Failed to fetch setup prompts:', error);
    }
  }, [fetchProfileAnalysis]);

  const enrichProfile = useCallback(async () => {
    setState((prev) => ({ ...prev, assistantLoading: true, enrichmentProgress: 0, assistantError: null }));

    try {
      for (let i = 0; i <= 100; i += 20) {
        await new Promise(resolve => setTimeout(resolve, 200));
        setState((prev) => ({ ...prev, enrichmentProgress: i }));
      }

      await fetchProfileAnalysis();

      setState((prev) => ({
        ...prev,
        profileState: ProfileSetupState.READY_FOR_AI,
        enrichmentProgress: 100,
        assistantLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        assistantError: error instanceof Error ? error.message : 'Failed to enrich profile',
        assistantLoading: false,
      }));
    }
  }, [fetchProfileAnalysis]);

  const acceptAISuggestion = useCallback(async (suggestionId: string) => {
    try {
      const suggestion = state.aiSuggestions.find(s => s.id === suggestionId);
      if (!suggestion) return;

      const field = suggestion.field;
      let updateData: any = {};

      if (field === 'target_audience') {
        updateData.target_audience = suggestion.suggested_value;
      } else if (field === 'business_goals') {
        updateData.business_goals = suggestion.suggested_value;
      }

      if (Object.keys(updateData).length > 0) {
        await updateBusinessProfile(updateData);
      }

      setState((prev) => ({
        ...prev,
        aiSuggestions: prev.aiSuggestions.map(s =>
          s.id === suggestionId ? { ...s, accepted: true } : s
        ),
      }));

      await fetchProfileAnalysis();
    } catch (error) {
      console.error('Failed to accept AI suggestion:', error);
      throw error;
    }
  }, [state.aiSuggestions, updateBusinessProfile, fetchProfileAnalysis]);

  const dismissPrompt = useCallback((promptId: string) => {
    setState((prev) => ({
      ...prev,
      setupPrompts: prev.setupPrompts.filter(p => p.id !== promptId),
    }));
  }, []);

  const connectPlatform = useCallback(async (platform: string) => {
    try {
      setState((prev) => ({
        ...prev,
        platformRecommendations: prev.platformRecommendations.map(r =>
          r.platform === platform ? { ...r, connection_status: 'connecting' } : r
        ),
      }));

      await new Promise(resolve => setTimeout(resolve, 1500));

      const platformName = state.platformRecommendations.find(r => r.platform === platform)?.platform_name || platform;

      await addSocialMediaProfile({
        platform_name: platform,
        platform_display_name: platformName,
        handle: '@' + platform.toLowerCase(),
        is_primary: false,
        auto_sync_enabled: true,
      });

      setState((prev) => ({
        ...prev,
        platformRecommendations: prev.platformRecommendations.map(r =>
          r.platform === platform ? { ...r, connection_status: 'connected' } : r
        ),
      }));

      await fetchProfileAnalysis();
    } catch (error) {
      setState((prev) => ({
        ...prev,
        platformRecommendations: prev.platformRecommendations.map(r =>
          r.platform === platform ? { ...r, connection_status: 'error' } : r
        ),
        assistantError: error instanceof Error ? error.message : 'Failed to connect platform',
      }));
      throw error;
    }
  }, [state.platformRecommendations, addSocialMediaProfile, fetchProfileAnalysis]);

  // Refresh All
  const refreshAll = useCallback(async () => {
    await Promise.all([
      fetchUserProfile(),
      fetchProfileCompletion(),
      fetchBusinessProfile(),
      fetchSocialMediaProfiles(),
      fetchProfileAnalytics(),
      fetchUserActivity(),
      fetchInsights(),
    ]);
  }, [
    fetchUserProfile,
    fetchProfileCompletion,
    fetchBusinessProfile,
    fetchSocialMediaProfiles,
    fetchProfileAnalytics,
    fetchUserActivity,
    fetchInsights,
  ]);

  // Reset Actions
  const resetUserProfile = useCallback(() => {
    setState((prev) => ({
      ...prev,
      userProfile: null,
      userProfileLoading: false,
      userProfileError: null,
    }));
  }, []);

  const resetBusinessProfile = useCallback(() => {
    setState((prev) => ({
      ...prev,
      businessProfile: null,
      businessProfileLoading: false,
      businessProfileError: null,
    }));
  }, []);

  const resetSocialMediaProfiles = useCallback(() => {
    setState((prev) => ({
      ...prev,
      socialMediaProfiles: [],
      socialMediaLoading: false,
      socialMediaError: null,
    }));
  }, []);

  const resetAnalytics = useCallback(() => {
    setState((prev) => ({
      ...prev,
      profileAnalytics: null,
      analyticsLoading: false,
      analyticsError: null,
      userActivity: null,
      activityLoading: false,
      activityError: null,
    }));
  }, []);

  const resetInsights = useCallback(() => {
    setState((prev) => ({
      ...prev,
      insights: [],
      insightsLoading: false,
      insightsError: null,
      insightsTotal: 0,
      insightsUnread: 0,
      insightsHighPriority: 0,
    }));
  }, []);

  const resetActivityLogs = useCallback(() => {
    setState((prev) => ({
      ...prev,
      activityLogs: [],
      activityLogsLoading: false,
      activityLogsError: null,
      activityLogsTotal: 0,
    }));
  }, []);

  const resetAssistant = useCallback(() => {
    setState((prev) => ({
      ...prev,
      profileState: ProfileSetupState.NOT_STARTED,
      setupPrompts: [],
      aiSuggestions: [],
      platformRecommendations: [],
      enrichmentProgress: 0,
      assistantLoading: false,
      assistantError: null,
    }));
  }, []);

  const resetAll = useCallback(() => {
    setState(initialState);
  }, []);

  const contextValue: ProfileContextType = {
    ...state,
    fetchUserProfile,
    updateUserProfileData,
    fetchProfileCompletion,
    fetchBusinessProfile,
    updateBusinessProfileData,
    fetchSocialMediaProfiles,
    addSocialMediaProfile,
    updateSocialMediaProfile,
    deleteSocialMediaProfile,
    fetchProfileAnalytics,
    fetchUserActivity,
    fetchInsights,
    generateNewInsights,
    provideInsightFeedback,
    fetchActivityLogs,
    fetchProfileAnalysis,
    fetchSetupPrompts,
    enrichProfile,
    acceptAISuggestion,
    dismissPrompt,
    connectPlatform,
    refreshAll,
    resetUserProfile,
    resetBusinessProfile,
    resetSocialMediaProfiles,
    resetAnalytics,
    resetInsights,
    resetActivityLogs,
    resetAssistant,
    resetAll,
  };

  return (
    <ProfileContext.Provider value={contextValue}>
      {children}
    </ProfileContext.Provider>
  );
};

export const useProfile = (): ProfileContextType => {
  const context = useContext(ProfileContext);
  if (context === undefined) {
    throw new Error('useProfile must be used within a ProfileProvider');
  }
  return context;
};
