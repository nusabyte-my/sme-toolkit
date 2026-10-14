# 🚀 SME Toolkit Comprehensive Improvement Plan

**Generated:** January 15, 2026  
**Based on:** Codebase analysis, external research, and industry best practices

---

## Executive Summary

This document provides a comprehensive improvement roadmap for the SME Toolkit, addressing all major areas:
1. Visual/Mage Editor (Canva-like UI improvements)
2. Profiling API enhancements (mock data strategy)
3. Tokenized billing system for multi-modal/multi-agent AI
4. Model/LLM selection capability for content generation
5. Full-stack upgrade (Bun, Biome, Hono, PostgreSQL)
6. Agentix agent system for user assistance
7. HuggingFace model recommendations (image/video)
8. Ollama containerization options
9. Google Colab GPU sharing alternatives

---

## Current State Analysis

### Technology Stack
**Frontend:**
- React 19.2.3 with TypeScript
- Vite 6.2.0 (build tool)
- Tailwind CSS (styling)
- Lucide React (icons)

**Backend:**
- FastAPI 0.109.0 (Python web framework)
- SQLAlchemy (async ORM)
- SQLite (database)
- LangGraph 0.2 (agent orchestration)
- LangChain 0.3 (AI framework)

**AI Providers (Multi-Provider System):**
- **LLM:** Gemini (primary), Groq, Mistral, DeepSeek (fallbacks)
- **Image:** Gemini/Imagen, FLUX.2, Stability AI
- **Video:** Veo 3, Kling AI, Nano Banana

**Current Modules:**
1. Business Model Canvas (BMC) - AI-guided conversational discovery
2. Strategy Advisor - Multi-agent analysis with growth scoring
3. Lead Manager - AI-powered lead scoring and CRM
4. Copywriter - Marketing copy generation
5. Visual Studio - Image generation (mage editor)
6. Video Studio - Video generation
7. Analytics Dashboard - Business insights
8. Profiles System - Enhanced user/business/social media profiles

### Architecture Pattern
- Monolithic structure with modular components
- JWT authentication
- REST API design
- Multi-tier subscription (Free, SME, Business, Enterprise)
- Rate limiting per user (daily/minute)
- Automatic provider fallback on failure

---

## Section 1: Mage Editor Improvements (Canva-like UI)

### Current State
**File:** `components/visual/EnhancedVisualGenerator.tsx`
- Basic image generation with prompt input
- Simple mockup templates (browser, phone, social card)
- Limited editing capabilities
- Background presets and viewport controls

### Research Findings

**Best Canvas Libraries (2024-2025):**
1. **Konva.js** - Most popular for React Canva clones
   - Direct React integration: `react-konva` or `@konva/react-konva`
   - Excellent performance with 2D canvas rendering
   - Supports: shapes, text, images, drawing, layers, transforms
   - Built-in drag-and-drop
   - Export to PNG, JPEG, SVG

2. **Fabric.js** - Alternative with more features
   - More mature ecosystem
   - Supports complex objects (groups, paths, text)
   - Better for PDF/PPT export
   - Active community: `react-fabricjs-image-editor`

3. **Tldraw** - Modern whiteboard/canvas
   - Perfect for collaborative editing
   - Infinite canvas with zoom/pan
   - Excellent touch support
   - Built for diagrams and design work

**Recommended Libraries:**
- Primary choice: **Konva.js** (better React integration)
- Secondary: **Tldraw** (for future collaborative features)
- Avoid Fabric.js (heavier, less maintained)

### Improvement Plan

#### Phase 1: Core Canvas Enhancement (Priority: HIGH)
```typescript
// Upgrade from simple generator to full design editor

Tech Stack:
- konva/react-konva (canvas engine)
- immer (state management for undo/redo)
- react-beautiful-dnd (drag and drop)
- html2canvas (already installed - for export)
```

**Features to Implement:**

1. **Advanced Canvas Layer System**
   - Layer panel with visibility/lock controls
   - Drag-to-reorder layers
   - Group/ungroup layers
   - Layer filtering (images, text, shapes)

2. **Comprehensive Element Tools**
   - Shapes: rectangle, circle, triangle, star, polygon
   - Text: rich text editor with fonts, colors, sizes
   - Images: upload from device, add from library
   - Icons: extensive icon library
   - Lines/Arrows: connectors between elements
   - Frames: decorative borders and containers

3. **Canva-Like Templates Library**
   - Template categories: Social Media, Presentations, Marketing, Documents
   - Searchable template gallery
   - Template preview and instant apply
   - Template customization wizard

4. **Real-Time Collaboration**
   - WebSocket-based multi-user editing
   - User cursors with names/colors
   - Live presence indicators
   - Change synchronization
   - Comment/chat sidebar

5. **Advanced Export Options**
   - PNG, JPEG, SVG, PDF (via jsPDF, already installed)
   - Custom resolution settings
   - Transparent background option
   - Export for web/social media presets

#### Phase 2: UI/UX Modernization (Priority: HIGH)

**Modern Design Principles (2024-2025):**
1. **Dark Mode Support**
   ```css
   :root {
     --canvas-bg: #ffffff;
   --canvas-text: #1f2937;
   }
   [data-theme="dark"] {
     --canvas-bg: #1e1e1e;
     --canvas-text: #e2e8f0;
   }
   ```

2. **Glassmorphism & Neumorphism**
   - Frosted glass sidebars
   - Soft shadows and gradients
   - Modern depth effects

3. **Micro-Interactions**
   - Subtle hover states (0.2s transitions)
   - Click ripples
   - Smooth scroll with momentum
   - Keyboard shortcuts (Ctrl+Z, Ctrl+Y, Ctrl+S)

4. **Responsive Editor Layout**
   - Mobile: Collapsible toolbars, touch-optimized controls
   - Tablet: Two-column layout with expandable properties
   - Desktop: Full three-column layout

5. **Smart Property Panel**
   - Context-aware properties (shows relevant options)
   - AI-powered suggestions for adjustments
   - Quick presets and styles
   - Live preview changes

#### Phase 3: AI-Powered Features (Priority: MEDIUM)

**Integration with Existing AI Providers:**
1. **AI Background Generation**
   - Generate backgrounds from text descriptions
   - Use FLUX.2 or Gemini Imagen
   - Style controls: minimal, professional, creative

2. **AI Image Enhancement**
   - Upscale/HD quality
   - Remove backgrounds automatically
   - Apply consistent color grading
   - Fix perspective and composition

3. **AI Copy Suggestions**
   - Generate marketing copy for designs
   - Ad headlines for social media
   - Product descriptions

4. **Smart Layouts**
   - Auto-arrange elements based on templates
   - Balance composition using AI rules
   - Suggest color palettes

#### Implementation Roadmap

**Week 1-2: Foundation**
- Install konva dependencies
- Set up basic canvas with undo/redo
- Implement basic shape tools

**Week 3-4: Core Features**
- Text and image elements
- Basic drag-and-drop
- Template system (v1)
- Export functionality

**Week 5-6: Advanced Features**
- Full layer system
- Advanced transforms (rotate, scale, skew)
- Rich text editor
- AI background generation

**Week 7-8: Polish**
- Collaboration features
- Dark mode
- Performance optimization
- Extensive template library

---

## Section 2: Profiling API Improvements

### Current State
**Files:**
- `sme-toolkit-backend/app/api/v1/endpoints/profiles.py` (651 lines)
- `sme-toolkit-backend/app/services/profile_service.py`
- `types/profiles.ts` (421 lines)

**Current Capabilities:**
- User profiles (comprehensive demographic data)
- Business profiles (detailed company information)
- Social media profiles (platform connections with metrics)
- Activity tracking
- Privacy settings
- AI-generated insights

### Improvement Plan

#### Mock Data Strategy (Priority: HIGH)

**Purpose:** Enable frontend development without backend dependency

**Mock Data Structure:**
```typescript
// services/mock/profilesMockService.ts

export const mockUserProfiles: UserProfile[] = [
  {
    id: "user-1",
    user_id: "user-1",
    first_name: "John",
    last_name: "Doe",
    full_name: "John Doe",
    email: "john.doe@example.com",
    phone: "+1-555-123-4567",
    avatar_url: "https://i.pravatar.cc/150x150",
    date_of_birth: "1985-05-15",
    gender: "male",
    nationality: "US",
    country: "United States",
    state_province: "California",
    city: "San Francisco",
    postal_code: "94102",
    timezone: "America/Los_Angeles",
    language: "en",
    job_title: "CEO",
    company_role: "owner",
    years_of_experience: 15,
    industry_experience: [
      { industry: "Technology", years: 12 },
      { industry: "Finance", years: 3 }
    ],
    education_level: "master",
    field_of_study: "Computer Science",
    certifications: [
      { name: "AWS Solutions Architect", year: 2020 },
      { name: "PMP", year: 2018 }
    ],
    owns_business: true,
    number_of_businesses: 1,
    profile_completion_percentage: 85
  }
  // ... 5-10 more realistic profiles
];

export const mockBusinessProfiles: BusinessProfile[] = [
  {
    id: "business-1",
    user_id: "user-1",
    company_name: "Tech Innovations Inc.",
    industry: "Technology",
    business_stage: "growth",
    business_type: "corporation",
    legal_structure: "LLC",
    registration_number: "1234567890",
    tax_id: "US123456789",
    founding_date: "2015-03-15",
    website_url: "https://techinnovations.com",
    business_description: "AI-powered business solutions for SMEs",
    mission_statement: "Empowering small businesses with intelligent tools",
    vision_statement: "Become the leading AI toolkit platform by 2028",
    team_size: 25,
    annual_revenue: 1500000,
    revenue_currency: "USD",
    profit_margin: 35.5,
    funding_stage: "series_b",
    funding_amount: 500000,
    customer_count: 250,
    products_services: [
      {
        name: "SME Toolkit Platform",
        category: "Software",
        description: "Comprehensive business toolkit"
      }
    ],
    profile_completeness_score: 92.5
  }
  // ... 5-10 realistic business profiles
];

export const mockSocialMediaProfiles: SocialMediaProfile[] = [
  {
    id: "social-1",
    user_profile_id: "user-1",
    business_profile_id: "business-1",
    platform_name: "linkedin",
    platform_display_name: "LinkedIn",
    platform_icon: "fab:linkedin",
    handle: "techinnovations",
    profile_url: "https://linkedin.com/company/techinnovations",
    is_connected: true,
    is_primary: true,
    metrics: {
      followers: 12500,
      following: 850,
      posts: 342,
      engagement_rate: 4.2,
      avg_likes: 350,
      avg_comments: 45,
      reach: 50000,
      profile_views: 5200,
      last_post_date: "2024-01-15",
      posting_frequency: "weekly",
      best_posting_time: "09:00",
      top_performing_content: ["video", "carousel"],
      audience_demographics: {
        age: { "18-24": 20, "25-34": 40, "35-44": 30, "45+": 10 },
        gender: { "male": 45, "female": 55 }
      }
    },
    historical_metrics: [
      { date: "2024-01", followers: 10500, engagement_rate: 3.8 },
      { date: "2024-02", followers: 11200, engagement_rate: 4.0 }
    ],
    content_categories: ["technology", "business", "innovation"],
    posting_schedule: {
      frequency: "weekly",
      best_days: ["Tuesday", "Thursday"],
      best_times: ["09:00", "14:00"]
    },
    auto_sync_enabled: true,
    sync_frequency: "daily",
    engagement_score: 7.8,
    influence_score: 8.2,
    growth_rate: 5.5,
    performance_rating: "excellent"
  }
  // ... more mock profiles for different platforms
];
```

**Mock API Service:**
```typescript
// services/mock/profilesMockApi.ts

import { 
  mockUserProfiles, 
  mockBusinessProfiles, 
  mockSocialMediaProfiles 
} from './profilesMockData';

// Simulate network delay for realistic experience
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const profilesMockApi = {
  // User Profile Endpoints
  getUserProfile: async (userId: string) => {
    await delay(300);
    const profile = mockUserProfiles.find(p => p.user_id === userId);
    return profile || null;
  },
  
  updateUserProfile: async (userId: string, data: Partial<UserProfileUpdate>) => {
    await delay(500);
    const profile = mockUserProfiles.find(p => p.user_id === userId);
    if (!profile) throw new Error('Profile not found');
    return { ...profile, ...data, updated_at: new Date().toISOString() };
  },
  
  getProfileCompletion: async (userId: string) => {
    await delay(200);
    const profile = mockUserProfiles.find(p => p.user_id === userId);
    if (!profile) return { completion_percentage: 0, missing_fields: [] };
    
    const completion = profile.profile_completion_percentage || 0;
    const missingFields: string[] = [];
    
    if (!profile.email) missingFields.push('email');
    if (!profile.phone) missingFields.push('phone');
    if (!profile.job_title) missingFields.push('job_title');
    
    return {
      profile_id: userId,
      completion_percentage: completion,
      missing_fields,
      recommended_fields: missingFields,
      completion_tips: [
        'Add your email to unlock notifications',
        'Complete job information for personalized recommendations'
      ]
    };
  },
  
  // Business Profile Endpoints
  getBusinessProfile: async (userId: string) => {
    await delay(400);
    const profile = mockBusinessProfiles.find(p => p.user_id === userId);
    return profile || null;
  },
  
  updateBusinessProfile: async (userId: string, data: Partial<BusinessProfileUpdate>) => {
    await delay(600);
    const profile = mockBusinessProfiles.find(p => p.user_id === userId);
    if (!profile) throw new Error('Business profile not found');
    return { ...profile, ...data, updated_at: new Date().toISOString() };
  },
  
  getBusinessMetrics: async (businessId: string) => {
    await delay(250);
    const profile = mockBusinessProfiles.find(p => p.id === businessId);
    if (!profile) return null;
    
    return {
      business_id,
      metrics: {
        revenue_growth: '+15.2%',
        customer_growth: '+8.5%',
        engagement_score: 7.2,
        market_position: 'Top 25%'
      },
      benchmarks: {
        industry_avg_revenue: 1200000,
        industry_avg_customers: 180,
        industry_avg_margin: 28.5
      }
    };
  },
  
  // Social Media Endpoints
  getSocialMediaProfiles: async (userId: string) => {
    await delay(350);
    const profiles = mockSocialMediaProfiles.filter(p => p.user_profile_id === userId);
    return profiles;
  },
  
  addSocialMediaProfile: async (userId: string, data: SocialMediaProfileCreate) => {
    await delay(700);
    const newProfile: SocialMediaProfile = {
      id: `social-${Date.now()}`,
      user_profile_id: userId,
      business_profile_id: data.business_profile_id,
      ...data,
      is_connected: false,
      is_primary: false,
      sync_status: 'not_synced',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    // Add metrics if platform is LinkedIn
    if (data.platform_name === 'linkedin') {
      newProfile.metrics = {
        followers: Math.floor(Math.random() * 5000) + 1000,
        engagement_rate: (Math.random() * 2 + 2).toFixed(1),
        posts: Math.floor(Math.random() * 100)
      };
    }
    
    return newProfile;
  },
  
  syncSocialMediaProfile: async (profileId: string) => {
    await delay(1000);
    const profile = mockSocialMediaProfiles.find(p => p.id === profileId);
    if (!profile) throw new Error('Social media profile not found');
    
    // Simulate sync with new metrics
    return {
      ...profile,
      is_connected: true,
      sync_status: 'synced',
      last_sync_date: new Date().toISOString(),
      metrics: {
        ...profile.metrics,
        followers: (profile.metrics?.followers || 0) + Math.floor(Math.random() * 100)
      }
    };
  },
  
  // Analytics Endpoints
  getProfileAnalytics: async (userId: string, timeRange: string = '30d') => {
    await delay(500);
    
    // Generate analytics from mock data
    const activity = generateMockActivityData(timeRange);
    const socialProfiles = mockSocialMediaProfiles.filter(p => p.user_profile_id === userId);
    
    const totalFollowers = socialProfiles.reduce((sum, p) => 
      sum + (p.metrics?.followers || 0), 0);
    
    return {
      user_profile_id: userId,
      profile_completion: 85,
      activity_summary: {
        total_sessions: activity.length,
        total_time_spent: activity.reduce((sum, a) => 
          sum + (a.interaction_time || 0), 0),
        most_used_features: ['dashboard', 'bmc', 'strategy'],
        activity_by_category: { 'dashboard': 40, 'bmc': 30, 'strategy': 30 }
      },
      social_media_summary: {
        total_profiles: socialProfiles.length,
        total_followers,
        avg_engagement: socialProfiles.reduce((sum, p) => 
          sum + (p.metrics?.engagement_rate || 0), 0) / socialProfiles.length
      },
      engagement_metrics: {
        daily_active_users: Math.floor(Math.random() * 50 + 20),
        weekly_growth_rate: (Math.random() * 5 + 2).toFixed(1),
        best_performing_day: 'Tuesday'
      },
      key_insights: [
        'Your LinkedIn engagement is 20% above industry average',
        'Consider adding Instagram to reach younger demographics',
        'Posting frequency of 3x/week shows optimal engagement'
      ],
      recommendations: [
        'Maintain current posting frequency',
        'Expand to video content to increase reach',
        'Collaborate with industry leaders for partnerships'
      ]
    };
  },
  
  // Insights Endpoints
  getProfileInsights: async (userId: string, limit: number = 20) => {
    await delay(400);
    
    const insights: ProfileInsight[] = [
      {
        id: `insight-${Date.now()}-1`,
        user_profile_id: userId,
        insight_type: 'growth_opportunity',
        insight_category: 'social_media',
        title: 'High Engagement Opportunity',
        description: 'Your recent carousel post achieved 3x your average engagement',
        insight_data: {
          post_id: 'post-123',
          engagement_rate: 12.5,
          avg_engagement: 4.2,
          improvement: '+197%'
        },
        priority: 'high',
        impact_level: 'high',
        confidence_score: 0.85,
        is_actionable: true,
        action_items: [
          'Create 2-3 more carousel posts this month',
          'A/B test different content formats'
        ],
        estimated_effort: 'medium',
        estimated_timeframe: 'short_term',
        status: 'new',
        generated_at: new Date().toISOString(),
        last_updated: new Date().toISOString()
      },
      // ... more insights
    ];
    
    return {
      insights: insights.slice(0, limit),
      total: insights.length,
      unread_count: insights.filter(i => i.status === 'new').length,
      high_priority_count: insights.filter(i => i.priority === 'high').length,
      categories: {
        'growth_opportunity': insights.filter(i => i.insight_type === 'growth_opportunity').length,
        'risk_alert': insights.filter(i => i.insight_type === 'risk_alert').length,
        'recommendation': insights.filter(i => i.insight_type === 'recommendation').length
      }
    };
  }
};

function generateMockActivityData(timeRange: string) {
  const days = timeRange === '30d' ? 30 : 90;
  const activities: UserActivityLog[] = [];
  
  const activities = [
    'login', 'logout', 'page_view', 'feature_use', 
    'data_update', 'profile_view', 'social_media_sync'
  ];
  
  for (let i = 0; i < days; i++) {
    activities.push({
      id: `activity-${Date.now()}-${i}`,
      user_profile_id: 'user-1',
      activity_type: activities[Math.floor(Math.random() * activities.length)],
      activity_category: ['dashboard', 'bmc', 'strategy', 'leads'][Math.floor(Math.random() * 4)],
      feature_name: ['dashboard', 'bmc', 'strategy_advisor', 'lead_manager'][Math.floor(Math.random() * 4)],
      action: 'viewed',
      page_url: '/dashboard',
      session_id: `session-${Math.random().toString(36).substr(2, 8)}`,
      device_type: ['desktop', 'mobile', 'tablet'][Math.floor(Math.random() * 3)],
      browser: 'Chrome',
      browser_version: '120.0.0',
      os: 'Windows 11',
      os_version: '10.0',
      screen_resolution: '1920x1080',
      page_load_time: Math.random() * 2 + 0.5,
      interaction_time: Math.floor(Math.random() * 300 + 30),
      metadata: { },
      created_at: new Date(Date.now() - i * 86400000).toISOString()
    });
  }
  
  return activities;
}
```

**Implementation Strategy:**

1. **Create Mock Configuration**
   ```typescript
   // config/useMockApi.ts
   
   export const useMockApi = import.meta.env.VITE_USE_MOCK_API === 'true';
   ```
   
2. **Environment Variables**
   ```env
   # .env.local
   
   VITE_USE_MOCK_API=false  # Set to true for development without backend
   VITE_MOCK_API_DELAY=300  # Simulate network delay (ms)
   ```

3. **Service Switching Pattern**
   ```typescript
   // services/profileService.ts
   
   import { profilesMockApi } from './mock/profilesMockApi';
   import { profilesRealApi } from './api/profilesRealApi';
   import { useMockApi } from '../config/useMockApi';
   
   export const getUserProfile = useMockApi 
     ? profilesMockApi.getUserProfile 
     : profilesRealApi.getUserProfile;
   
   export const updateUserProfile = useMockApi 
     ? profilesMockApi.updateUserProfile 
     : profilesRealApi.updateUserProfile;
   
   // ... continue pattern for all endpoints
   ```

4. **Mock Data Generator CLI**
   ```bash
   npm run generate:mock-data
   ```
   
   ```typescript
   // scripts/generateMockData.ts
   
   import fs from 'fs';
   import { generateRealisticProfiles } from '../lib/mockDataGenerator';
   
   const profiles = generateRealisticProfiles(10);
   fs.writeFileSync(
     'services/mock/profilesMockData.ts',
     profiles
   );
   ```

#### API Connection Improvements

1. **Retry Strategy**
   ```typescript
   // services/apiClient.ts
   
   import axios, { AxiosError } from 'axios';
   
   const apiClient = axios.create({
     baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
     timeout: 30000,
     retries: 3,
     retryDelay: 1000
   });
   
   // Exponential backoff retry
   apiClient.interceptors.request.use(async config => {
     return config;
   }, async error => {
     const shouldRetry = !error.response && 
       error.config?.retries < error.config?.maxRetries;
     
     if (shouldRetry) {
       const delay = Math.pow(2, error.config?.retries || 0) * 1000;
       await new Promise(resolve => setTimeout(resolve, delay));
       return apiClient.request(error.config);
     }
     
     return Promise.reject(error);
   });
   ```

2. **Request Caching**
   ```typescript
   // services/cache/profileCache.ts
   
   const profileCache = new Map<string, { data: any; timestamp: number }>();
   const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
   
   export const getCachedProfile = (userId: string) => {
     const cached = profileCache.get(userId);
     if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
       return cached.data;
     }
     return null;
   };
   
   export const setCachedProfile = (userId: string, data: any) => {
     profileCache.set(userId, { data, timestamp: Date.now() });
   };
   ```

3. **Offline Support with IndexedDB**
   ```typescript
   // services/offline/profileOfflineStore.ts
   
   const DB_NAME = 'SMEToolkit';
   const STORE_NAME = 'profiles';
   
   export const offlineProfileStore = {
     async init() {
       return idb.open(DB_NAME, 1, STORE_NAME);
     },
     
     async getAllProfiles() {
       const db = await this.init();
       return db.getAll(STORE_NAME);
     },
     
     async saveProfile(profile: UserProfile) {
       const db = await this.init();
       await db.put(STORE_NAME, profile);
       return db.transaction(['profiles'], 'readwrite');
     },
     
     async syncWhenOnline() {
       const local = await this.getAllProfiles();
       // Push to server when connection restored
       for (const profile of local) {
         await profilesRealApi.updateUserProfile(profile.id, profile);
       }
     }
   };
   ```

#### Enhanced Dashboard Features

1. **Real-time Profile Health**
   ```typescript
   // components/dashboard/profiles/ProfileHealthGauge.tsx
   
   interface ProfileHealthProps {
     completenessScore: number;
     lastSyncStatus: 'success' | 'pending' | 'error';
     dataQualityScore: number;
   }
   
   export const ProfileHealthGauge: React.FC<ProfileHealthProps> = ({
     completenessScore,
     lastSyncStatus,
     dataQualityScore
   }) => {
     const getHealthColor = (score: number) => {
       if (score >= 90) return '#10b981'; // green
       if (score >= 70) return '#f59e0b'; // yellow
       return '#ef4444'; // red
     };
     
     return (
       <div className="health-gauge">
         <div className="gauge-container">
           <svg viewBox="0 0 36 20" className="gauge">
             {/* Gauge implementation */}
           </svg>
           <div className="score-display">{completenessScore}%</div>
         </div>
         <div className="status-indicators">
           <SyncIcon status={lastSyncStatus} />
           <DataQualityIcon score={dataQualityScore} />
         </div>
       </div>
     );
   };
   ```

2. **Advanced Analytics Visualization**
   ```typescript
   // components/dashboard/profiles/ProfileAnalyticsDashboard.tsx
   
   export const ProfileAnalyticsDashboard: React.FC = () => {
     return (
       <div className="analytics-dashboard">
         {/* Engagement trend chart */}
         <EngagementTrendChart />
         
         {/* Social media comparison */}
         <SocialMediaComparison />
         
         {/* Activity heatmap */}
         <ActivityHeatmap />
         
         {/* Insight cards */}
         <InsightsFeed />
       </div>
     );
   };
   ```

---

## Section 3: Tokenized Billing System

### Research Findings

**Industry Standards (2024-2025):**

1. **Token-Based Pricing** (Most Popular for AI)
   - OpenAI, Anthropic, Cohere use token-based pricing
   - Granular control over usage
   - Predictable billing for users
   - 1K tokens ≈ 750-1000 words

2. **Credit-Based Pricing** (Enterprise & SaaS)
   - Pre-purchased buckets of tokens/credits
   - Volume discounts available
   - Better for budget management
   - Subscription-like recurring revenue

3. **Usage-Based Pricing** (Per-Use)
   - Charge per action/generation
   - Simple to understand
   - Common in AI services (e.g., image generation)

**Key Metrics from Research:**
- AI agent costs average **$1,000–$5,000/month**
- 70% of expenses driven by LLM token usage
- GPT-4 Turbo costs **$0.01–$0.03 per 1,000 tokens**
- Complex agents can consume **5–10 million tokens/month**

### Design Philosophy

**Multi-Modal Token Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                  TOKENIZED BILLING SYSTEM                │
└─────────────────────────────────────────────────────────────┘

Core Principles:
1. Unified Token Economy
   - Single token type across all AI services
   - Convertible across modalities (text, image, video)
   - Fair exchange rates

2. Multi-Modal Support
   - Text generation: 1 token ≈ 750 characters
   - Image generation: 100 tokens per image (1024x1024)
   - Video generation: 500 tokens per 10-second clip
   - Multi-agent orchestration: 50 tokens per agent invocation

3. Usage Tracking
   - Real-time consumption monitoring
   - Per-model cost breakdown
   - Historical usage analytics
   - Predictive cost alerts

4. Subscription Integration
   - Token quotas per tier
   - Overage charges at reduced rates
   - Rollover/accumulation for business tiers
   - Volume discounts for large users

5. Provider Cost Optimization
   - Auto-route to cheapest available provider
   - Tier-specific provider pools
   - Provider failure cost absorption
   - Negotiated rates with providers
```

### Implementation Architecture

#### Database Schema

```sql
-- Tokenized Billing Tables

CREATE TABLE token_accounts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    balance DECIMAL(15, 4) DEFAULT 0.0000,  -- Token balance
    currency VARCHAR(3) DEFAULT 'USD',
    tier VARCHAR(20) NOT NULL,  -- Free, SME, Business, Enterprise
    status VARCHAR(20) DEFAULT 'active',  -- active, suspended, cancelled
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
);

CREATE INDEX idx_token_user ON token_accounts(user_id, tier);
CREATE INDEX idx_token_balance ON token_accounts(balance);

CREATE TABLE token_transactions (
    id VARCHAR(36) PRIMARY KEY,
    token_account_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    
    -- Transaction Details
    transaction_type VARCHAR(50) NOT NULL,  -- purchase, usage, refund, bonus, rollover
    amount DECIMAL(15, 4) NOT NULL,  -- Positive for addition, negative for deduction
    balance_after DECIMAL(15, 4) NOT NULL,
    
    -- Service Details
    service_type VARCHAR(50) NOT NULL,  -- text_llm, image_generation, video_generation, agent_orchestration
    model_id VARCHAR(100),  -- Specific model used
    provider_id VARCHAR(50),  -- AI provider used
    modality VARCHAR(20) NOT NULL,  -- text, image, video, multi_modal
    operation_id VARCHAR(100),  -- Reference to operation
    operation_type VARCHAR(50),  -- generation, edit, analysis, upload, download
    
    -- Usage Metrics
    input_tokens INT,  -- Tokens for input text
    output_tokens INT,  -- Tokens generated
    tokens_consumed INT,  -- Total tokens used
    estimated_cost_usd DECIMAL(10, 4),
    
    -- Metadata
    metadata JSON,  -- Flexible additional data
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (token_account_id) REFERENCES token_accounts(id),
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
);

CREATE INDEX idx_transaction_user_date ON token_transactions(user_id, created_at);
CREATE INDEX idx_transaction_type ON token_transactions(transaction_type, service_type);
CREATE INDEX idx_transaction_operation ON token_transactions(operation_id);

CREATE TABLE token_packages (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 4) NOT NULL,
    token_amount DECIMAL(12, 0) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    tier VARCHAR(20),  -- Free, SME, Business, Enterprise
    bonus_tokens INT DEFAULT 0,
    features JSON,  -- Additional features included
    is_active BOOLEAN DEFAULT true,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_package_tier ON token_packages(tier, is_active);

CREATE TABLE usage_quotas (
    id VARCHAR(36) PRIMARY KEY,
    token_account_id VARCHAR(36) NOT NULL,
    tier VARCHAR(20) NOT NULL,
    period_type VARCHAR(20) NOT NULL,  -- daily, monthly, annual
    
    -- Quota Limits
    max_tokens INT NOT NULL,
    max_images INT DEFAULT 0,
    max_videos INT DEFAULT 0,
    max_agents INT DEFAULT 0,
    max_api_calls INT DEFAULT 0,
    
    -- Usage Tracking
    tokens_used INT DEFAULT 0,
    images_used INT DEFAULT 0,
    videos_used INT DEFAULT 0,
    agents_used INT DEFAULT 0,
    api_calls_used INT DEFAULT 0,
    
    -- Reset Schedule
    reset_day INT,  -- Day of month for reset (1-31)
    last_reset DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (token_account_id) REFERENCES token_accounts(id),
    UNIQUE (token_account_id, tier, period_type)
);

CREATE TABLE provider_cost_rates (
    id VARCHAR(36) PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL UNIQUE,
    provider_name VARCHAR(100) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    model_id VARCHAR(100),
    
    -- Cost Configuration
    price_per_1k_tokens DECIMAL(10, 6) NOT NULL,
    price_per_image DECIMAL(10, 4),
    price_per_video_second DECIMAL(10, 4),
    price_per_agent_call DECIMAL(10, 4),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Negotiated Rates
    is_negotiated BOOLEAN DEFAULT false,
    volume_discount_percent DECIMAL(5, 2) DEFAULT 0.00,
    
    -- Performance
    avg_latency_ms INT,
    success_rate DECIMAL(5, 2),
    last_updated DATETIME,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Token Economics

```python
# sme-toolkit-backend/app/services/token_service.py

from enum import Enum
from typing import Optional
from decimal import Decimal

class ServiceType(str, Enum):
    TEXT_LLM = "text_llm"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    AGENT_ORCHESTRATION = "agent_orchestration"
    ANALYSIS = "analysis"
    TRANSCRIPTION = "transcription"

class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MULTI_MODAL = "multi_modal"

class TransactionType(str, Enum):
    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"
    BONUS = "bonus"
    ROLLOVER = "rollover"
    ADJUSTMENT = "adjustment"

# Token Conversion Rates (1 Token Base Unit)
TOKEN_RATES = {
    # Text Generation
    "text": {
        "input_chars_per_token": 750,      # ~750 chars per token
        "output_chars_per_token": 750,     # ~750 chars per token
        "words_per_token": 150,           # ~150 words per token
    },
    
    # Image Generation
    "image": {
        "base_image_tokens": 100,          # 1024x1024 image
        "resolution_multiplier": {           # Multipliers for other resolutions
            "512x512": 0.5,
            "2048x2048": 2.0,
            "4096x4096": 4.0,
        },
        "quality_multiplier": {
            "standard": 1.0,
            "hd": 2.0,
            "4k": 4.0,
        }
    },
    
    # Video Generation
    "video": {
        "base_video_tokens": 500,        # Per 10-second clip
        "duration_multiplier": {            # Per second
            "5s": 0.5,
            "15s": 1.5,
            "30s": 3.0,
            "60s": 6.0,
        },
        "resolution_multiplier": {
            "480p": 1.0,
            "720p": 1.5,
            "1080p": 2.0,
        }
    },
    
    # Agent Orchestration
    "agent": {
        "base_call_tokens": 50,           # Per agent invocation
        "complexity_multiplier": {
            "simple": 1.0,
            "medium": 2.0,
            "complex": 3.0,
        },
        "agent_type_multiplier": {
            "goal_advisor": 1.5,
            "growth_plan": 1.2,
            "costing_advisor": 1.3,
            "business_suggestion": 1.0,
        }
    },
}

class TokenService:
    """
    Service for managing token-based billing system
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_token_cost(
        self,
        service_type: ServiceType,
        modality: Modality,
        model_id: str,
        input_data: dict,
        output_data: dict,
        provider_id: str
    ) -> dict:
        """
        Calculate token cost for an AI operation
        """
        # Get provider cost rates
        cost_rates = await self._get_provider_rates(provider_id, service_type)
        
        # Calculate input tokens
        input_tokens = 0
        if modality in [Modality.TEXT, Modality.MULTI_MODAL]:
            text = input_data.get("prompt", "") + input_data.get("content", "")
            input_tokens = len(text) // TOKEN_RATES["text"]["input_chars_per_token"]
        
        # Calculate output tokens based on service type
        output_tokens = 0
        if service_type == ServiceType.TEXT_LLM:
            output_tokens = len(output_data.get("text", "")) // TOKEN_RATES["text"]["output_chars_per_token"]
        
        elif service_type == ServiceType.IMAGE_GENERATION:
            base_tokens = TOKEN_RATES["image"]["base_image_tokens"]
            resolution = output_data.get("resolution", "1024x1024")
            quality = output_data.get("quality", "standard")
            
            tokens = base_tokens * \
                TOKEN_RATES["image"]["resolution_multiplier"].get(resolution, 1.0) * \
                TOKEN_RATES["image"]["quality_multiplier"].get(quality, 1.0)
            output_tokens = tokens
        
        elif service_type == ServiceType.VIDEO_GENERATION:
            base_tokens = TOKEN_RATES["video"]["base_video_tokens"]
            duration = output_data.get("duration", 10)  # seconds
            resolution = output_data.get("resolution", "720p")
            
            tokens = base_tokens * \
                TOKEN_RATES["video"]["duration_multiplier"].get(f"{duration}s", 1.0) * \
                TOKEN_RATES["video"]["resolution_multiplier"].get(resolution, 1.0)
            output_tokens = tokens
        
        elif service_type == ServiceType.AGENT_ORCHESTRATION:
            base_tokens = TOKEN_RATES["agent"]["base_call_tokens"]
            complexity = output_data.get("complexity", "medium")
            agent_type = output_data.get("agent_type", "general")
            
            tokens = base_tokens * \
                TOKEN_RATES["agent"]["complexity_multiplier"].get(complexity, 1.0) * \
                TOKEN_RATES["agent"]["agent_type_multiplier"].get(agent_type, 1.0)
            output_tokens = tokens
        
        total_tokens = input_tokens + output_tokens
        
        # Calculate estimated cost
        estimated_cost = 0.0
        if cost_rates:
            if service_type == ServiceType.TEXT_LLM:
                cost_per_1k = cost_rates.price_per_1k_tokens
                estimated_cost = Decimal(total_tokens) * cost_per_1k / 1000
            
            elif service_type == ServiceType.IMAGE_GENERATION:
                estimated_cost = cost_rates.price_per_image
            
            elif service_type == ServiceType.VIDEO_GENERATION:
                estimated_cost = total_tokens * cost_rates.price_per_video_second
            
            elif service_type == ServiceType.AGENT_ORCHESTRATION:
                estimated_cost = total_tokens * cost_rates.price_per_agent_call
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": float(estimated_cost),
            "cost_breakdown": {
                "service_type": service_type.value,
                "modality": modality.value,
                "model_id": model_id,
                "provider_id": provider_id
            }
        }
    
    async def charge_tokens(
        self,
        user_id: str,
        tokens: int,
        service_type: ServiceType,
        operation_id: str,
        metadata: dict = None
    ) -> dict:
        """
        Deduct tokens from user account
        """
        # Get token account
        account = await self._get_token_account(user_id)
        
        # Check sufficient balance
        if account.balance < tokens:
            raise InsufficientTokensError(
                requested=tokens,
                available=account.balance,
                user_id=user_id
            )
        
        # Create transaction
        transaction = TokenTransaction(
            id=str(uuid.uuid4()),
            token_account_id=account.id,
            user_id=user_id,
            transaction_type=TransactionType.USAGE,
            amount=-tokens,  # Deduction
            balance_after=account.balance - Decimal(tokens),
            service_type=service_type.value,
            operation_id=operation_id,
            tokens_consumed=tokens,
            estimated_cost_usd=Decimal(tokens) * account.token_value,  # USD per token
            metadata=metadata or {}
        )
        
        # Update account balance
        account.balance -= Decimal(tokens)
        account.updated_at = datetime.utcnow()
        
        # Update quotas
        await self._update_quotas(user_id, service_type, tokens)
        
        # Save
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(account)
        
        return {
            "transaction_id": transaction.id,
            "new_balance": float(account.balance),
            "tokens_remaining": account.balance
        }
    
    async def check_quota_limits(
        self,
        user_id: str,
        service_type: ServiceType,
        tokens_required: int
    ) -> dict:
        """
        Check if operation is within user's quota limits
        """
        account = await self._get_token_account(user_id)
        tier = account.tier
        
        # Get quotas for tier
        quotas = await self._get_quotas(tier)
        
        # Check service-specific quota
        quota_available = False
        quota_exceeded = False
        quota_reset = None
        
        if service_type == ServiceType.TEXT_LLM:
            tokens_used = quotas.tokens_used + tokens_required
            quota_available = tokens_used <= quotas.max_tokens
            quota_exceeded = tokens_used > quotas.max_tokens
            quota_reset = quotas.last_reset
        
        elif service_type == ServiceType.IMAGE_GENERATION:
            images_used = quotas.images_used + 1  # Per image
            quota_available = images_used <= quotas.max_images
            quota_exceeded = images_used > quotas.max_images
            quota_reset = quotas.last_reset
        
        elif service_type == ServiceType.VIDEO_GENERATION:
            videos_used = quotas.videos_used + 1  # Per video
            quota_available = videos_used <= quotas.max_videos
            quota_exceeded = videos_used > quotas.max_videos
            quota_reset = quotas.last_reset
        
        return {
            "quota_available": quota_available,
            "quota_exceeded": quota_exceeded,
            "tokens_remaining": quotas.max_tokens - quotas.tokens_used,
            "images_remaining": quotas.max_images - quotas.images_used,
            "videos_remaining": quotas.max_videos - quotas.videos_used,
            "quota_reset": quota_reset.isoformat() if quota_reset else None,
            "tier": tier
        }
```

#### API Endpoints

```python
# sme-toolkit-backend/app/api/v1/endpoints/tokens.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.token_service import TokenService
from app.schemas.tokens import *

router = APIRouter(prefix="/tokens", tags=["Tokens"])

@router.get("/balance")
async def get_token_balance(
    current_user: str = Depends(get_current_user)
):
    """
    Get user's current token balance
    """
    service = TokenService(db)
    balance = await service.get_token_balance(current_user)
    return balance

@router.get("/transactions")
async def get_token_transactions(
    current_user: str = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    service_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Get token transaction history
    """
    service = TokenService(db)
    transactions = await service.get_transactions(
        user_id=current_user,
        skip=skip,
        limit=limit,
        service_type=service_type,
        start_date=start_date,
        end_date=end_date
    )
    return transactions

@router.post("/purchase")
async def purchase_tokens(
    package_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Purchase token package
    """
    service = TokenService(db)
    
    # Get package details
    package = await service.get_package(package_id)
    if not package or not package.is_active:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # Process payment (integration with Stripe)
    payment_result = await service.process_payment(
        current_user=current_user,
        amount=package.price,
        currency=package.currency,
        metadata={"package_id": package_id}
    )
    
    if not payment_result["success"]:
        raise HTTPException(status_code=400, detail="Payment failed")
    
    # Add tokens to account
    result = await service.credit_tokens(
        user_id=current_user,
        amount=package.token_amount,
        transaction_type="purchase",
        metadata={"package_id": package_id}
    )
    
    return result

@router.get("/usage")
async def get_usage_report(
    current_user: str = Depends(get_current_user),
    period: str = "month",  # day, week, month, year
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed usage report
    """
    service = TokenService(db)
    report = await service.generate_usage_report(
        user_id=current_user,
        period=period
    )
    return report

@router.post("/webhooks/stripe")
async def stripe_webhook(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe payment webhooks
    """
    service = TokenService(db)
    
    event_type = payload.get("type")
    
    if event_type == "payment_intent.succeeded":
        # Payment successful - credit tokens
        await service.handle_successful_payment(payload)
    elif event_type == "invoice.payment_succeeded":
        # Subscription payment - handle recurring billing
        await service.handle_subscription_payment(payload)
    elif event_type == "charge.refunded":
        # Refund - restore tokens
        await service.handle_refund(payload)
```

#### Tier-Based Pricing Structure

```python
# Pricing tiers with token allocations

TIER_CONFIG = {
    "Free": {
        "monthly_cost": 0,
        "token_quota": 0,  # No tokens
        "daily_requests": 50,
        "daily_images": 10,
        "daily_videos": 0,
        "features": ["bmc", "leads", "copywriter", "visual"]
    },
    
    "SME": {
        "monthly_cost": 19,
        "token_quota": 10000,  # ~$0.002/token
        "daily_requests": 500,
        "daily_images": 50,
        "daily_videos": 5,
        "features": ["all_free", "strategy_advisor", "analytics"],
        "token_breakdown": {
            "text_llm": 4000,      # 40% for text
            "image_generation": 3000,  # 30% for images
            "video_generation": 2000,   # 20% for video
            "agent_orchestration": 1000 # 10% for agents
        }
    },
    
    "Business": {
        "monthly_cost": 49,
        "token_quota": 40000,  # ~$0.0012/token
        "daily_requests": 2000,
        "daily_images": 200,
        "daily_videos": 20,
        "features": ["all_sme", "api_access"],
        "token_breakdown": {
            "text_llm": 16000,     # 40% for text
            "image_generation": 12000,  # 30% for images
            "video_generation": 8000,   # 20% for video
            "agent_orchestration": 4000   # 10% for agents
        }
    },
    
    "Enterprise": {
        "monthly_cost": "custom",
        "token_quota": "unlimited",
        "daily_requests": 10000,
        "daily_images": 1000,
        "daily_videos": 100,
        "features": ["all_business", "api_access", "white_label", "priority_support"],
        "token_breakdown": {
            "text_llm": "unlimited",
            "image_generation": "unlimited",
            "video_generation": "unlimited",
            "agent_orchestration": "unlimited"
        }
    }
}
```

---

## Section 4: Model/LLM Selection Capability

### Current State

**Multi-Provider System Already Exists:**
- Provider router in `sme-toolkit-backend/app/providers/router.py`
- Individual providers for LLM, image, video
- Automatic fallback on failure
- Tier-based access control

### Enhancement Plan

#### Unified Model Selection Interface

**Frontend: Model Selector Component**
```typescript
// components/common/ModelSelector.tsx

interface ModelProvider {
  id: string;
  name: string;
  provider: string;
  type: 'llm' | 'image' | 'video';
  models: Model[];
  logo: string;
  isDefault: boolean;
}

interface Model {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  costPerToken?: number;  // For LLM
  costPerImage?: number;  // For image
  costPerSecond?: number; // For video
  performance?: {
    speed: string;  // tokens/second
    quality: string; // high, medium, low
  };
  available: boolean;
  category: 'premium' | 'standard' | 'free';
}

interface ModelSelectorProps {
  type: 'llm' | 'image' | 'video' | 'agent';
  onModelSelect: (modelId: string) => void;
  currentModel?: string;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  type,
  onModelSelect,
  currentModel
}) => {
  const [providers, setProviders] = useState<ModelProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | null>(currentModel || null);
  
  useEffect(() => {
    // Load available providers and models based on user tier
    const loadAvailableProviders = async () => {
      const result = await providersApi.getAvailableProviders(type);
      setProviders(result.providers);
    };
    
    loadAvailableProviders();
  }, [type]);
  
  return (
    <div className="model-selector">
      <div className="provider-tabs">
        {providers.map(provider => (
          <div 
            key={provider.id}
            className={`provider-tab ${selectedProvider === provider.id ? 'active' : ''}`}
            onClick={() => setSelectedProvider(provider.id)}
          >
            <img src={provider.logo} alt={provider.name} />
            <span>{provider.name}</span>
            {provider.isDefault && <Badge variant="success">Default</Badge>}
          </div>
        ))}
      </div>
      
      {selectedProvider && (
        <div className="model-grid">
          {providers
            .find(p => p.id === selectedProvider)
            ?.models.map(model => (
              <div 
                key={model.id}
                className={`model-card ${selectedModel === model.id ? 'selected' : ''}`}
                onClick={() => onModelSelect(model.id)}
              >
                <div className="model-header">
                  <h3>{model.name}</h3>
                  <Badge variant={model.category}>
                    {model.category}
                  </Badge>
                </div>
                <p className="model-description">{model.description}</p>
                
                {model.costPerToken && (
                  <div className="cost-info">
                    <span>{model.costPerToken} tokens/1K</span>
                  </div>
                )}
                
                <div className="capabilities">
                  {model.capabilities.map(cap => (
                    <span key={cap} className="capability-tag">{cap}</span>
                  ))}
                </div>
                
                {model.performance && (
                  <div className="performance-metrics">
                    <div>Speed: {model.performance.speed}</div>
                    <div>Quality: {model.performance.quality}</div>
                  </div>
                )}
                
                {!model.available && (
                  <div className="unavailable-badge">
                    Upgrade plan to access
                  </div>
                )}
              </div>
            ))}
        </div>
      )}
    </div>
  );
};
```

**Backend: Model Management Service**

```python
# sme-toolkit-backend/app/services/model_management_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ModelManagementService:
    """
    Service for managing AI model selection and availability
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_available_models(
        self,
        user_id: str,
        modality: str
    ) -> List[Dict[str, Any]]:
        """
        Get available models based on user tier and preferences
        """
        # Get user tier
        user = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        user_profile = user.scalar_one_or_none()
        
        if not user_profile:
            return []
        
        tier = user_profile.tier
        
        # Get models available for this tier
        models = []
        
        if modality == "llm":
            # LLM models based on tier
            if tier in ["Free", "SME"]:
                models.extend([
                    {
                        "id": "gpt-4-turbo",
                        "name": "GPT-4 Turbo",
                        "provider": "groq",
                        "description": "Fastest inference, ideal for quick responses",
                        "cost_per_1k_tokens": 0.01,
                        "performance": {"speed": "300 tok/s", "quality": "high"},
                        "capabilities": ["chat", "completion", "code", "reasoning"],
                        "category": "standard",
                        "available": True
                    },
                    {
                        "id": "gemini-1.5-pro",
                        "name": "Gemini 1.5 Pro",
                        "provider": "google",
                        "description": "High-quality reasoning with 1M context",
                        "cost_per_1k_tokens": 0.035,
                        "performance": {"speed": "50 tok/s", "quality": "very_high"},
                        "capabilities": ["chat", "completion", "code", "reasoning", "multimodal"],
                        "category": "premium",
                        "available": True
                    }
                ])
            
            elif tier == "Business":
                models.extend([
                    # Add Claude, GPT-4, etc.
                    {
                        "id": "claude-3-opus",
                        "name": "Claude 3 Opus",
                        "provider": "anthropic",
                        "description": "Advanced reasoning and analysis",
                        "cost_per_1k_tokens": 0.015,
                        "performance": {"speed": "80 tok/s", "quality": "very_high"},
                        "capabilities": ["chat", "completion", "code", "reasoning", "analysis"],
                        "category": "premium",
                        "available": True
                    }
                ])
            
            elif tier == "Enterprise":
                # All models available
                models.extend([
                    # GPT-4, Claude 3, Gemini, etc.
                    {
                        "id": "gpt-4",
                        "name": "GPT-4",
                        "provider": "openai",
                        "description": "Most advanced model with 8K context",
                        "cost_per_1k_tokens": 0.03,
                        "performance": {"speed": "40 tok/s", "quality": "excellent"},
                        "capabilities": ["chat", "completion", "code", "reasoning", "analysis", "multimodal"],
                        "category": "premium",
                        "available": True
                    },
                    {
                        "id": "claude-3.5-sonnet",
                        "name": "Claude 3.5 Sonnet",
                        "provider": "anthropic",
                        "description": "Next-generation reasoning",
                        "cost_per_1k_tokens": 0.018,
                        "performance": {"speed": "60 tok/s", "quality": "excellent"},
                        "capabilities": ["chat", "completion", "code", "reasoning", "analysis", "vision"],
                        "category": "premium",
                        "available": True
                    }
                ])
        
        return models
        
        elif modality == "image":
            # Image generation models
            if tier in ["Free", "SME"]:
                models.extend([
                    {
                        "id": "flux-1-dev",
                        "name": "FLUX.1-dev",
                        "provider": "replicate",
                        "description": "Open source, fast generation",
                        "cost_per_image": 0.0025,
                        "performance": {"speed": "2s", "quality": "high"},
                        "capabilities": ["text-to-image", "image-editing", "style-transfer"],
                        "category": "standard",
                        "available": True
                    },
                    {
                        "id": "imagen-2",
                        "name": "Imagen 2",
                        "provider": "google",
                        "description": "Google's high-quality model",
                        "cost_per_image": 0.01,
                        "performance": {"speed": "8s", "quality": "very_high"},
                        "capabilities": ["text-to-image"],
                        "category": "premium",
                        "available": tier == "SME"
                    }
                ])
            
            elif tier == "Business":
                models.extend([
                    {
                        "id": "dall-e-3",
                        "name": "DALL-E 3",
                        "provider": "openai",
                        "description": "OpenAI's latest model",
                        "cost_per_image": 0.04,
                        "performance": {"speed": "5s", "quality": "excellent"},
                        "capabilities": ["text-to-image", "image-editing", "inpainting"],
                        "category": "premium",
                        "available": True
                    }
                ])
        
        elif modality == "video":
            # Video generation models
            if tier == ["Business", "Enterprise"]:
                models.extend([
                    {
                        "id": "veo-3",
                        "name": "Veo 3",
                        "provider": "google",
                        "description": "Google's high-quality video model",
                        "cost_per_second": 0.05,
                        "performance": {"speed": "fast", "quality": "very_high"},
                        "capabilities": ["text-to-video", "video-editing"],
                        "category": "premium",
                        "available": True
                    },
                    {
                        "id": "kling-ai",
                        "name": "Kling AI",
                        "provider": "kling",
                        "description": "Up to 3-minute videos",
                        "cost_per_second": 0.02,
                        "performance": {"speed": "medium", "quality": "high"},
                        "capabilities": ["text-to-video"],
                        "category": "standard",
                        "available": True
                    }
                ])
        
        return models
    
    async def set_user_model_preference(
        self,
        user_id: str,
        modality: str,
        model_id: str,
        provider_id: str
    ) -> bool:
        """
        Set user's preferred model for a modality
        """
        # Check if model is available for user's tier
        available = await self.get_available_models(user_id, modality)
        model_available = any(m["id"] == model_id for m in available)
        
        if not model_available:
            raise ValueError(f"Model {model_id} not available for user's tier")
        
        # Store preference
        user_prefs = await self.db.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        prefs = user_prefs.scalar_one_or_none()
        
        preference_data = {
            f"preferred_{modality}_model": model_id,
            f"preferred_{modality}_provider": provider_id,
            "updated_at": datetime.utcnow()
        }
        
        if prefs:
            for key, value in preference_data.items():
                setattr(prefs, key, value)
        else:
            # Create new preferences record
            prefs = UserPreference(
                id=str(uuid.uuid4()),
                user_id=user_id,
                **preference_data
            )
            self.db.add(prefs)
        
        await self.db.commit()
        return True
```

#### Model Selection UX Patterns

1. **Smart Default Selection**
   - Auto-select best model based on task type
   - Learn from user preferences
   - Balance cost vs. quality automatically

2. **Cost Estimates**
   - Show token/cost estimates before generation
   - Real-time cost calculator in UI
   - Budget warnings when approaching limits

3. **Model Comparison**
   - Side-by-side model comparison
   - Quality benchmarks with examples
   - Performance metrics visualization

---

[DOCUMENT CONTINUED IN NEXT RESPONSE...]
