/**
 * Mock Data Service for Profiles
 * Enables frontend development without backend dependency
 * 
 * Provides realistic mock data for:
 * - User profiles (demographics, preferences, interests)
 * - Business profiles (company details, metrics, goals)
 * - Social media profiles (platform connections, metrics)
 * - Activity logs (user engagement patterns)
 * - Privacy settings (consent management)
 * - Profile insights (AI-generated recommendations)
 */

import type { UserProfile, BusinessProfile, SocialMediaProfile, UserActivityLog, PrivacySettings as PrivacySettings, ProfileInsight } from '../../types/profiles';

// uuid replacement: RFC4122-shaped id without a dependency (crypto.randomUUID
// is unavailable in some jsdom runtimes this file serves).
const uuidv4 = (): string => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

// Type definitions for mock data
interface UserProfileMock {
  id: string;
  user_id: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  email?: string;
  phone?: string;
  avatar_url?: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'non_binary' | 'prefer_not_to_say' | 'other';
  nationality?: string;
  country?: string;
  state_province?: string;
  city?: string;
  postal_code?: string;
  timezone?: string;
  language?: string;
  job_title?: string;
  company_role?: 'owner' | 'ceo' | 'manager' | 'employee' | 'consultant';
  years_of_experience?: number;
  industry_experience?: Array<{ industry: string; years: number }>;
  education_level?: 'high_school' | 'bachelor' | 'master' | 'phd' | 'other';
  field_of_study?: string;
  certifications?: Array<{ name: string; year: number }>;
  owns_business?: boolean;
  number_of_businesses?: number;
  primary_business_id?: string;
  profile_completion_percentage: number;
  interests?: string[];
  skills?: Array<{ skill: string; proficiency: 'beginner' | 'intermediate' | 'advanced' | 'expert' }>;
  learning_goals?: string[];
  business_challenges?: string[];
}

interface BusinessProfileMock {
  id: string;
  user_id: string;
  company_name: string;
  industry: string;
  business_stage: 'startup' | 'growth' | 'established' | 'mature';
  business_type?: 'sole_proprietorship' | 'partnership' | 'llc' | 'corporation';
  legal_structure?: string;
  registration_number?: string;
  tax_id?: string;
  founding_date?: string;
  website_url?: string;
  business_description?: string;
  mission_statement?: string;
  vision_statement?: string;
  team_size?: number;
  annual_revenue?: number;
  revenue_currency?: string;
  profit_margin?: number;
  funding_stage?: 'bootstrapped' | 'seed' | 'series_a' | 'series_b';
  funding_amount?: number;
  customer_count?: number;
  products_services?: Array<{ name: string; category: string; description: string }>;
  target_market?: string[];
  competitive_advantages?: string[];
  profile_completeness_score: number;
}

interface SocialMediaProfileMock {
  id: string;
  user_profile_id: string;
  business_profile_id?: string;
  platform_name: string;
  platform_display_name: string;
  platform_icon: string;
  handle?: string;
  profile_url?: string;
  account_type?: 'personal' | 'business' | 'creator';
  is_verified: boolean;
  is_primary: boolean;
  is_connected: boolean;
  connection_date?: string;
  last_sync_date?: string;
  sync_status: 'not_synced' | 'syncing' | 'synced' | 'error';
  metrics?: {
    followers?: number;
    following?: number;
    posts?: number;
    engagement_rate?: number;
    avg_likes?: number;
    avg_comments?: number;
    avg_shares?: number;
    reach?: number;
    impressions?: number;
    profile_views?: number;
    clicks?: number;
    mentions?: number;
    hashtags?: string[];
    last_post_date?: string;
    posting_frequency?: string;
    best_posting_time?: string;
    top_performing_content?: string[];
    audience_demographics?: {
      age?: Record<string, number>;
      gender?: Record<string, number>;
      location?: Record<string, number>;
    };
  };
  historical_metrics?: Array<{ date: string; metrics: Record<string, number> }>;
  content_categories?: string[];
  posting_schedule?: { frequency?: string; best_days?: string[]; best_times?: string[] };
  auto_sync_enabled: boolean;
  sync_frequency?: 'hourly' | 'daily' | 'weekly';
  engagement_score?: number;
  influence_score?: number;
  growth_rate?: number;
  performance_rating?: 'excellent' | 'good' | 'average' | 'poor';
}

// Generate realistic mock user profiles
export const generateMockUserProfiles = (count: number = 10): UserProfileMock[] => {
  const firstNames = ['John', 'Sarah', 'Michael', 'Emma', 'David', 'Jennifer', 'Robert', 'Lisa', 'James', 'Patricia'];
  const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'];
  const countries = ['United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Australia', 'Japan'];
  const industries = ['Technology', 'Finance', 'Marketing', 'Healthcare', 'Retail', 'Manufacturing', 'Consulting'];
  const cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego'];
  const states = ['California', 'Texas', 'New York', 'Florida', 'Illinois', 'Pennsylvania', 'Ohio', 'Georgia'];

  return Array.from({ length: count }, (_, i) => {
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const gender = ['male', 'female'][Math.floor(Math.random() * 2)] as any;

    return {
      id: uuidv4(),
      user_id: `user-${i + 1}`,
      first_name: firstName,
      last_name: lastName,
      full_name: `${firstName} ${lastName}`,
      email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`,
      phone: `+1-${Math.floor(100 + Math.random() * 900)}-${Math.floor(100 + Math.random() * 900)}-${Math.floor(1000 + Math.random() * 9000)}`,
      avatar_url: `https://i.pravatar.cc/150?img=${i + 1}`,
      date_of_birth: new Date(Date.now() - (25 + Math.random() * 20) * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      gender: gender,
      nationality: countries[Math.floor(Math.random() * countries.length)],
      country: 'United States',
      state_province: states[Math.floor(Math.random() * states.length)],
      city: cities[Math.floor(Math.random() * cities.length)],
      postal_code: `${Math.floor(10000 + Math.random() * 90000)}`,
      timezone: 'America/New_York',
      language: 'en',
      job_title: ['CEO', 'Founder', 'Manager', 'Director', 'Consultant'][Math.floor(Math.random() * 5)],
      company_role: ['owner', 'ceo', 'manager', 'employee', 'consultant'][Math.floor(Math.random() * 5)] as any,
      years_of_experience: Math.floor(5 + Math.random() * 20),
      industry_experience: Array.from({ length: Math.floor(1 + Math.random() * 4) }, () => ({
        industry: industries[Math.floor(Math.random() * industries.length)],
        years: Math.floor(1 + Math.random() * 10),
      })),
      education_level: ['bachelor', 'master', 'phd'][Math.floor(Math.random() * 3)] as any,
      field_of_study: ['Computer Science', 'Business Administration', 'Marketing', 'Finance', 'Engineering'][Math.floor(Math.random() * 5)],
      certifications: Array.from({ length: Math.floor(Math.random() * 4) }, () => ({
        name: ['AWS Solutions Architect', 'PMP', 'Six Sigma', 'Google Cloud Professional'][Math.floor(Math.random() * 4)],
        year: Math.floor(2015 + Math.random() * 8),
      })),
      owns_business: Math.random() > 0.5,
      number_of_businesses: Math.random() > 0.5 ? 1 : 0,
      profile_completion_percentage: Math.floor(70 + Math.random() * 30),
      interests: [
        'Technology', 'Marketing', 'Finance', 'Leadership', 'Innovation',
        'Digital Transformation', 'Data Analytics', 'Customer Experience'
      ].sort(() => 0.5 - Math.random()).slice(0, 5 + Math.floor(Math.random() * 3)),
      skills: Array.from({ length: 5 + Math.floor(Math.random() * 5) }, () => {
        const skill = ['JavaScript', 'React', 'Python', 'Marketing', 'Sales', 'Finance', 'Leadership', 'Strategy'][Math.floor(Math.random() * 8)];
        const proficiency = ['beginner', 'intermediate', 'advanced', 'expert'][Math.floor(Math.random() * 4)] as any;
        return { skill, proficiency };
      }),
      learning_goals: [
        'Improve data analysis skills',
        'Learn advanced marketing strategies',
        'Develop leadership capabilities',
        'Master AI/ML technologies',
        'Enhance financial management'
      ].sort(() => 0.5 - Math.random()).slice(0, 3 + Math.floor(Math.random() * 2)),
      business_challenges: [
        'Limited budget for marketing',
        'Competition from larger companies',
        'Scaling operations efficiently',
        'Hiring and retention challenges',
        'Adapting to market changes',
        'Managing remote teams',
        'Cash flow management'
      ].sort(() => 0.5 - Math.random()).slice(0, 2 + Math.floor(Math.random() * 3)),
    };
  });
};

// Generate realistic mock business profiles
export const generateMockBusinessProfiles = (count: number = 10): BusinessProfileMock[] => {
  const industries = ['Technology', 'Finance', 'Marketing', 'Healthcare', 'Retail', 'Manufacturing', 'Consulting', 'Education'];
  const stages = ['startup', 'growth', 'established', 'mature'];
  const businessTypes = ['sole_proprietorship', 'partnership', 'llc', 'corporation'];

  const companyNames = [
    'Tech Innovations Inc.', 'NextGen Solutions LLC', 'Global Marketing Co.', 'Data Dynamics Inc.',
    'Future Finance Group', 'Smart Retail Solutions', 'Cloud Services Pro', 'Digital Growth Agency',
    'Advanced Manufacturing Co.', 'Creative Design Studio', 'Health Tech Innovations'
  ];

  const missionStatements = [
    'Empowering small businesses with intelligent tools',
    'Transforming marketing through data-driven insights',
    'Delivering innovative financial solutions to SMEs',
    'Revolutionizing retail with AI-powered analytics',
    'Providing world-class consulting services',
    'Making advanced technology accessible to everyone'
  ];

  const visionStatements = [
    'Become the leading AI toolkit platform for SMEs by 2028',
    'Establish global presence as the go-to marketing partner for SMBs',
    'Transform how businesses manage their financial operations',
    'Create the most comprehensive retail intelligence platform',
    'Build a global network of successful business consultants',
    'Democratize access to enterprise-grade AI tools'
  ];

  return Array.from({ length: count }, (_, i) => ({
    id: uuidv4(),
    user_id: `user-${i + 1}`,
    company_name: companyNames[i % companyNames.length],
    industry: industries[Math.floor(Math.random() * industries.length)],
    business_stage: stages[Math.floor(Math.random() * stages.length)] as any,
    business_type: businessTypes[Math.floor(Math.random() * businessTypes.length)] as any,
    legal_structure: ['LLC', 'Corporation', 'Partnership'][Math.floor(Math.random() * 3)],
    registration_number: `${Math.floor(1000000 + Math.random() * 9000000)}`,
    tax_id: `US${Math.floor(10 + Math.random() * 90)}-${Math.floor(1000000 + Math.random() * 9000000)}`,
    founding_date: new Date(Date.now() - (1 + Math.random() * 15) * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    website_url: `https://${companyNames[i % companyNames.length].toLowerCase().replace(/\s/g, '')}.com`,
    business_description: `Leading ${industries[Math.floor(Math.random() * industries.length)]} company providing innovative solutions for businesses worldwide. Specialized in digital transformation and growth strategies.`,
    mission_statement: missionStatements[i % missionStatements.length],
    vision_statement: visionStatements[i % visionStatements.length],
    team_size: Math.floor(5 + Math.random() * 95),
    annual_revenue: Math.floor(50000 + Math.random() * 9500000),
    revenue_currency: 'USD',
    profit_margin: parseFloat((15 + Math.random() * 35).toFixed(2)),
    funding_stage: ['bootstrapped', 'seed', 'series_a', 'series_b'][Math.floor(Math.random() * 4)] as any,
    funding_amount: Math.random() > 0.5 ? Math.floor(100000 + Math.random() * 4900000) : 0,
    customer_count: Math.floor(50 + Math.random() * 950),
    products_services: Array.from({ length: 2 + Math.floor(Math.random() * 4) }, () => ({
      name: ['AI Analytics Platform', 'Marketing Automation Suite', 'Financial Dashboard', 'Consulting Services', 'Custom Development', 'Training Programs'][Math.floor(Math.random() * 6)],
      category: ['Software', 'Service', 'Consulting', 'Training'][Math.floor(Math.random() * 4)],
      description: 'Comprehensive solution for business optimization and growth.',
    })),
    target_market: [
      'Small businesses (10-50 employees)',
      'Medium enterprises (51-500 employees)',
      'Large corporations (500+ employees)',
      'B2B marketplace',
      'B2C direct sales'
    ].sort(() => 0.5 - Math.random()).slice(0, 2 + Math.floor(Math.random() * 2)),
    competitive_advantages: [
      'Proprietary AI algorithms',
      'Deep domain expertise',
      'First-mover advantage',
      'Strong brand recognition',
      'Strategic partnerships',
      'Cost-effective pricing',
      'Superior customer support',
      'Rapid innovation cycle'
    ].sort(() => 0.5 - Math.random()).slice(0, 2 + Math.floor(Math.random() * 3)),
    profile_completeness_score: parseFloat((70 + Math.random() * 30).toFixed(2)),
  }));
};

// Generate realistic mock social media profiles
export const generateMockSocialMediaProfiles = (count: number = 20): SocialMediaProfileMock[] => {
  const platforms = [
    { name: 'linkedin', display: 'LinkedIn', icon: 'linkedin' },
    { name: 'twitter', display: 'Twitter', icon: 'twitter' },
    { name: 'facebook', display: 'Facebook', icon: 'facebook' },
    { name: 'instagram', display: 'Instagram', icon: 'instagram' },
    { name: 'youtube', display: 'YouTube', icon: 'youtube' },
    { name: 'tiktok', display: 'TikTok', icon: 'tiktok' },
  ];

  const accountTypes = ['personal', 'business', 'creator'];
  const performanceRatings = ['excellent', 'good', 'average', 'poor'];
  const syncStatuses = ['not_synced', 'syncing', 'synced', 'error'];

  return Array.from({ length: count }, (_, i) => {
    const platform = platforms[i % platforms.length];
    const isConnected = Math.random() > 0.3;
    const followers = Math.floor(100 + Math.random() * 50000);
    const engagementRate = parseFloat((2 + Math.random() * 6).toFixed(2));

    return {
      id: uuidv4(),
      user_profile_id: `user-${(i % 10) + 1}`,
      business_profile_id: i < 10 ? `business-${(i % 10) + 1}` : undefined,
      platform_name: platform.name,
      platform_display_name: platform.display,
      platform_icon: platform.icon,
      handle: `@${platform.name.toLowerCase()}_${i + 1}`,
      profile_url: `https://www.${platform.name.toLowerCase()}.com/${platform.name.toLowerCase()}_${i + 1}`,
      account_type: accountTypes[Math.floor(Math.random() * accountTypes.length)] as any,
      is_verified: Math.random() > 0.7,
      is_primary: i % platforms.length === 0,
      is_connected: isConnected,
      connection_date: isConnected ? new Date(Date.now() - Math.floor(Math.random() * 365) * 24 * 60 * 60 * 1000).toISOString().split('T')[0] : undefined,
      last_sync_date: isConnected ? new Date(Date.now() - Math.floor(Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString().split('T')[0] : undefined,
      sync_status: isConnected ? syncStatuses[Math.floor(Math.random() * 4)] as any : 'not_synced',
      metrics: isConnected ? {
        followers,
        following: Math.floor(50 + Math.random() * 1000),
        posts: Math.floor(50 + Math.random() * 1000),
        engagement_rate: engagementRate,
        avg_likes: Math.floor(followers * engagementRate * 0.02),
        avg_comments: Math.floor(followers * engagementRate * 0.005),
        avg_shares: Math.floor(followers * engagementRate * 0.003),
        reach: Math.floor(followers * (3 + Math.random() * 7)),
        impressions: Math.floor(followers * (10 + Math.random() * 20)),
        profile_views: Math.floor(followers * (2 + Math.random() * 5)),
        clicks: Math.floor(followers * (0.5 + Math.random() * 2)),
        mentions: Math.floor(5 + Math.random() * 100),
        hashtags: ['business', 'growth', 'innovation', 'technology', 'marketing'].sort(() => 0.5 - Math.random()).slice(0, 3 + Math.floor(Math.random() * 3)),
        last_post_date: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        posting_frequency: ['daily', 'weekly', 'monthly'][Math.floor(Math.random() * 3)],
        best_posting_time: ['09:00', '12:00', '15:00', '18:00'][Math.floor(Math.random() * 4)],
        top_performing_content: ['video', 'carousel', 'image', 'text'].sort(() => 0.5 - Math.random()).slice(0, 2 + Math.floor(Math.random() * 2)),
        audience_demographics: {
          age: { '18-24': 20, '25-34': 40, '35-44': 30, '45+': 10 },
          gender: { 'male': 45, 'female': 55 },
          location: { 'US': 60, 'UK': 20, 'Canada': 10, 'Other': 10 },
        },
      } : undefined,
      historical_metrics: isConnected ? Array.from({ length: 6 }, (_, j) => ({
        date: new Date(Date.now() - (5 - j) * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        metrics: {
          followers: Math.floor(followers * (0.9 + Math.random() * 0.2)),
          engagement_rate: parseFloat((engagementRate * (0.9 + Math.random() * 0.2)).toFixed(2)),
        },
      })) : [],
      content_categories: isConnected ? [
        'technology', 'business', 'innovation', 'marketing',
        'education', 'news', 'entertainment', 'lifestyle'
      ].sort(() => 0.5 - Math.random()).slice(0, 2 + Math.floor(Math.random() * 3)) : [],
      posting_schedule: isConnected ? {
        frequency: ['hourly', 'daily', 'weekly'][Math.floor(Math.random() * 3)],
        best_days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].sort(() => 0.5 - Math.random()).slice(0, 2 + Math.floor(Math.random() * 2)),
        best_times: ['09:00', '12:00', '15:00', '18:00'].sort(() => 0.5 - Math.random()).slice(0, 1 + Math.floor(Math.random() * 2)),
      } : undefined,
      auto_sync_enabled: isConnected && Math.random() > 0.5,
      sync_frequency: ['hourly', 'daily', 'weekly'][Math.floor(Math.random() * 3)] as SocialMediaProfileMock['sync_frequency'],
      engagement_score: parseFloat((5 + Math.random() * 5).toFixed(2)),
      influence_score: parseFloat((6 + Math.random() * 5).toFixed(2)),
      growth_rate: parseFloat((2 + Math.random() * 10).toFixed(2)),
      performance_rating: performanceRatings[Math.floor(Math.random() * performanceRatings.length)] as any,
    };
  });
};

// Generate mock user activity logs
export const generateMockActivityLogs = (count: number = 50, userId?: string): UserActivityLog[] => {
  const activityTypes = [
    'login', 'logout', 'page_view', 'feature_use', 'data_update',
    'profile_view', 'social_media_sync', 'settings_change', 'export_data'
  ];

  const activityCategories = ['dashboard', 'bmc', 'strategy', 'leads', 'visual', 'video', 'analytics'];
  const featureNames = [
    'dashboard', 'business_model_canvas', 'strategy_advisor', 'lead_manager',
    'copywriter', 'visual_studio', 'video_studio', 'profiles',
    'analytics', 'settings', 'billing'
  ];

  const deviceTypes = ['desktop', 'mobile', 'tablet'];
  const browsers = ['Chrome', 'Firefox', 'Safari', 'Edge'];
  const operatingSystems = ['Windows 11', 'macOS', 'Linux', 'iOS', 'Android'];

  return Array.from({ length: count }, (_, i) => ({
    id: uuidv4(),
    user_profile_id: userId || `user-${(i % 10) + 1}`,
    business_profile_id: `business-${(i % 10) + 1}`,
    activity_type: activityTypes[Math.floor(Math.random() * activityTypes.length)] as any,
    activity_category: activityCategories[Math.floor(Math.random() * activityCategories.length)] as any,
    feature_name: featureNames[Math.floor(Math.random() * featureNames.length)] as any,
    action: 'viewed',
    page_url: `/feature/${featureNames[Math.floor(Math.random() * featureNames.length)]}`,
    referrer_url: '/dashboard',
    session_id: `session-${uuidv4()}`,
    device_type: deviceTypes[Math.floor(Math.random() * deviceTypes.length)] as any,
    browser: browsers[Math.floor(Math.random() * browsers.length)],
    browser_version: `${Math.floor(100 + Math.random() * 20)}.0.0`,
    os: operatingSystems[Math.floor(Math.random() * operatingSystems.length)],
    os_version: String(Math.floor(10 + Math.random() * 5)),
    screen_resolution: ['1920x1080', '1366x768', '2560x1440', '3840x2160'][Math.floor(Math.random() * 4)],
    page_load_time: parseFloat((0.5 + Math.random() * 2).toFixed(2)),
    interaction_time: Math.floor(30 + Math.random() * 300),
    metadata: {
      success: Math.random() > 0.1,
      performance_score: parseFloat((70 + Math.random() * 30).toFixed(2)),
    },
    error_details: undefined,
    created_at: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
  }));
};

// Generate mock privacy settings
export const generateMockPrivacySettings = (count: number = 10): PrivacySettings[] => {
  const dataRetentionPeriods = ['30_days', '90_days', '1_year', 'indefinite'];
  const profileVisibilityOptions = ['private', 'public', 'limited'];

  return Array.from({ length: count }, (_, i) => ({
    id: uuidv4(),
    user_profile_id: `user-${i + 1}`,
    analytics_consent: Math.random() > 0.2,
    personalization_consent: Math.random() > 0.3,
    marketing_consent: Math.random() > 0.7,
    third_party_sharing_consent: Math.random() > 0.8,
    research_consent: Math.random() > 0.9,
    data_retention_period: dataRetentionPeriods[Math.floor(Math.random() * dataRetentionPeriods.length)] as any,
    auto_delete_inactive_account: Math.random() > 0.95,
    inactivity_threshold_days: Math.floor(90 + Math.random() * 270),
    profile_visibility: profileVisibilityOptions[Math.floor(Math.random() * profileVisibilityOptions.length)] as any,
    visible_profile_fields: Math.random() > 0.5 ? ['email', 'company_name'] : [],
    hide_sensitive_fields: Math.random() > 0.5 ? ['phone', 'address'] : [],
    social_media_visibility: profileVisibilityOptions[Math.floor(Math.random() * profileVisibilityOptions.length)] as any,
    show_social_media_metrics: Math.random() > 0.3,
    allow_social_media_sync: Math.random() > 0.2,
    activity_tracking_enabled: Math.random() > 0.1,
    track_page_views: Math.random() > 0.2,
    track_feature_usage: Math.random() > 0.3,
    track_time_spent: Math.random() > 0.4,
    ai_insights_enabled: Math.random() > 0.2,
    personalized_recommendations: Math.random() > 0.3,
    predictive_analytics: Math.random() > 0.4,
    email_communication_types: ['marketing', 'updates', 'alerts'].sort(() => 0.5 - Math.random()).slice(0, 1 + Math.floor(Math.random() * 2)),
    sms_communication_types: Math.random() > 0.5 ? ['alerts'] : [],
    push_notification_types: ['all', 'urgent'].sort(() => 0.5 - Math.random()).slice(0, 1 + Math.floor(Math.random() * 1)),
    consent_history: [],
    last_consent_update: new Date().toISOString(),
    data_export_requested: Math.random() > 0.95,
    data_export_date: undefined,
    account_deletion_requested: Math.random() > 0.99,
    account_deletion_date: undefined,
    created_at: new Date(Date.now() - Math.floor(Math.random() * 365) * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
  }));
};

// Generate mock profile insights
export const generateMockProfileInsights = (count: number = 20, userId?: string): ProfileInsight[] => {
  const insightTypes = ['growth_opportunity', 'risk_alert', 'recommendation', 'trend', 'pattern'];
  const insightCategories = ['business', 'social_media', 'engagement', 'financial', 'operational'];
  const priorities = ['high', 'medium', 'low'];
  const impactLevels = ['high', 'medium', 'low'];
  const statuses = ['new', 'viewed', 'acknowledged', 'in_progress', 'completed', 'dismissed'];

  const growthOpportunityTitles = [
    'High Engagement Opportunity',
    'Growing Follower Base',
    'Strong Content Performance',
    'Optimal Posting Schedule',
    'Audience Growth Trend',
    'Viral Content Potential',
    'Cross-Platform Success',
    'Influencer Partnership Opportunity',
  ];

  const riskAlertTitles = [
    'Engagement Rate Decline',
    'Follower Loss Trend',
    'Content Performance Drop',
    'Platform Algorithm Change Impact',
    'Competitor Growth Warning',
    'Brand Sentiment Negative',
    'Inactive Account Risk',
  ];

  const recommendationTitles = [
    'Maintain Current Posting Frequency',
    'Expand to Video Content',
    'Collaborate with Industry Leaders',
    'Increase Content Variety',
    'Leverage Trending Topics',
    'Optimize Posting Schedule',
    'Improve Visual Content Quality',
    'Engage with Commenters',
  ];

  return Array.from({ length: count }, (_, i) => {
    const insightType = insightTypes[Math.floor(Math.random() * insightTypes.length)] as any;
    let title = '';

    if (insightType === 'growth_opportunity') {
      title = growthOpportunityTitles[i % growthOpportunityTitles.length];
    } else if (insightType === 'risk_alert') {
      title = riskAlertTitles[i % riskAlertTitles.length];
    } else if (insightType === 'recommendation') {
      title = recommendationTitles[i % recommendationTitles.length];
    } else {
      title = `Analysis Result ${i + 1}`;
    }

    return {
      id: uuidv4(),
      user_profile_id: userId || `user-${(i % 10) + 1}`,
      business_profile_id: i < 10 ? `business-${(i % 10) + 1}` : undefined,
      insight_type: insightType,
      insight_category: insightCategories[Math.floor(Math.random() * insightCategories.length)] as any,
      title,
      description: `Based on your recent activity and metrics, we've identified this ${insightType.replace('_', ' ')} that requires attention.`,
      insight_data: {
        summary: `Your ${['LinkedIn', 'Twitter', 'Instagram'][Math.floor(Math.random() * 3)]} ${['followers', 'engagement', 'posts'][Math.floor(Math.random() * 3)]} is ${Math.random() > 0.5 ? 'above' : 'below'} industry average`,
        metrics: {
          your_rate: parseFloat((3 + Math.random() * 4).toFixed(2)),
          industry_average: 3.2,
          top_quartile: 5.0,
        },
        factors: [
          'Consistent posting',
          'Engaging content',
          'Active community',
          'Strategic hashtags',
        ].sort(() => 0.5 - Math.random()).slice(0, 2 + Math.floor(Math.random() * 2)),
        recommendations: [
          'Maintain current posting frequency',
          'Expand to video content',
          'Collaborate with industry leaders',
        ].sort(() => 0.5 - Math.random()).slice(0, 2 + Math.floor(Math.random() * 1)),
        potential_impact: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)],
        confidence_score: parseFloat((0.7 + Math.random() * 0.3).toFixed(2)),
      },
      priority: priorities[Math.floor(Math.random() * priorities.length)] as any,
      impact_level: impactLevels[Math.floor(Math.random() * impactLevels.length)] as any,
      confidence_score: parseFloat((0.6 + Math.random() * 0.4).toFixed(2)),
      is_actionable: Math.random() > 0.2,
      action_items: Math.random() > 0.5 ? [
        'Increase posting frequency',
        'Diversify content types',
        'Engage with community comments',
      ] : [],
      estimated_effort: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
      estimated_timeframe: ['immediate', 'short_term', 'long_term'][Math.floor(Math.random() * 3)],
      status: statuses[Math.floor(Math.random() * statuses.length)] as any,
      user_feedback: undefined,
      user_notes: undefined,
      related_insight_ids: Math.random() > 0.5 ? [uuidv4(), uuidv4()] : [],
      parent_insight_id: undefined,
      ai_model_version: '1.5.0',
      generated_at: new Date(Date.now() - Math.floor(Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString(),
      last_updated: new Date(Date.now() - Math.floor(Math.random() * 3) * 24 * 60 * 60 * 1000).toISOString(),
      expires_at: new Date(Date.now() + Math.floor(7 + Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(Date.now() - Math.floor(Math.random() * 14) * 24 * 60 * 60 * 1000).toISOString(),
    };
  });
};

// Default mock datasets
export const defaultMockUserProfiles = generateMockUserProfiles(10);
export const defaultMockBusinessProfiles = generateMockBusinessProfiles(10);
export const defaultMockSocialMediaProfiles = generateMockSocialMediaProfiles(20);
export const defaultMockActivityLogs = generateMockActivityLogs(50);
export const defaultMockPrivacySettings = generateMockPrivacySettings(10);
export const defaultMockProfileInsights = generateMockProfileInsights(20);
