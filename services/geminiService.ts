import { apiCall, authenticatedFetch } from './apiClient';

// Business Canvas
export const generateBusinessCanvas = async (
  description: string,
  userInputs?: Record<string, string>
): Promise<any> => {
  const response = await apiCall<any>('/api/v1/canvas/generate', 'POST', {
    description,
    user_inputs: userInputs,
    mode: userInputs ? 'wizard' : 'quick',
    enhance: false,
  });

  return response.canvas;
};

export const enhancePrompt = async (originalPrompt: string): Promise<string> => {
  const response = await apiCall<any>('/api/v1/canvas/enhance', 'POST', {
    description: originalPrompt,
  });

  return response.enhanced_description || originalPrompt;
};

// Marketing Copy
export const generateMarketingCopy = async (
  topic: string,
  format: string,
  tone: string,
  targetAudience: string = '',
  count: number = 1,
  persona: string = 'General',
  abTestingMode: boolean = false,
  templateId?: string
): Promise<any> => {
  const response = await apiCall<any>('/api/v1/copywriter/generate', 'POST', {
    topic,
    format,
    tone,
    target_audience: targetAudience,
    variation_count: count,
    enhance: false,
    persona,
    ab_testing_mode: abTestingMode,
    template_id: templateId
  });

  return response;
};

// Strategy
export const generateStrategy = async (
  businessContext: string,
  type: 'TIPS' | 'GROWTH_PLAN' | 'INSIGHTS' | 'CREATIVE'
): Promise<string> => {
  const response = await apiCall<any>('/api/v1/strategy/generate', 'POST', {
    business_context: businessContext,
    advice_type: type,
    enhance: false,
  });

  return response.content || 'Failed to generate strategy.';
};

// Visual Generation
export const generateVisual = async (
  prompt: string,
  aspectRatio: string = '1:1',
  referenceImage?: string
): Promise<string> => {
  const response = await apiCall<any>('/api/v1/visual/generate', 'POST', {
    prompt,
    aspect_ratio: aspectRatio,
    reference_image: referenceImage,
    style: 'Photorealistic',
    enhance: false,
  });

  return response.image;
};

export const editVisual = async (base64Image: string, editInstruction: string): Promise<string> => {
  const response = await apiCall<any>('/api/v1/visual/edit', 'POST', {
    prompt: editInstruction,
    source_image: base64Image,
  });

  return response.image;
};

// Video Generation
export const generateVideoScript = async (topic: string, context: string): Promise<string> => {
  const response = await apiCall<any>('/api/v1/video/script', 'POST', {
    topic,
    context,
  });

  return response.script || '';
};

export const generateStoryboard = async (
  script: string
): Promise<Array<{ description: string; prompt: string }>> => {
  const response = await apiCall<any>('/api/v1/video/storyboard', 'POST', {
    script,
  });

  return response.scenes || [];
};

export const generateVideo = async (
  prompt: string,
  resolution: '720p' | '1080p' = '720p',
  aspectRatio: '16:9' | '9:16' = '16:9'
): Promise<string> => {
  const response = await apiCall<any>('/api/v1/video/generate', 'POST', {
    prompt,
    resolution,
    aspect_ratio: aspectRatio,
  });

  return response.video_url || '';
};

// Lead Analysis
export const analyzeLead = async (
  leadData: any
): Promise<{ score: number; suggestions: string }> => {
  // Ensure structure matches LeadRequest expected by backend
  const response = await apiCall<any>('/api/v1/leads/score', 'POST', {
    action: 'score',
    lead: leadData,
  });

  return {
    score: response.score || 0,
    suggestions: response.suggestions || 'Analysis failed',
  };
};

// Lead Management (CRUD)
export const createLead = async (lead: any): Promise<any> => {
  return apiCall<any>('/api/v1/leads/', 'POST', lead);
};

export const getLeads = async (
  page: number = 1, 
  size: number = 20, 
  status?: string, 
  search?: string
): Promise<{ items: any[]; total: number }> => {
  const query = new URLSearchParams({ 
    page: page.toString(), 
    size: size.toString() 
  });
  if (status) query.append('status', status);
  if (search) query.append('search', search);
  
  return apiCall<any>(`/api/v1/leads/?${query.toString()}`);
};

export const getLead = async (id: string): Promise<any> => {
  return apiCall<any>(`/api/v1/leads/${id}`);
};

export const updateLead = async (id: string, lead: any): Promise<any> => {
  return apiCall<any>(`/api/v1/leads/${id}`, 'PUT', lead);
};

export const assignLead = async (id: string, agentId: string): Promise<any> => {
  return apiCall<any>(`/api/v1/leads/${id}/assign?agent_id=${agentId}`, 'POST');
};

export const exportLeads = async (): Promise<Blob> => {
  const response = await authenticatedFetch('/api/v1/leads/export');
  return response.blob();
};

// Sales Tracking
export const trackSales = async (platform: string = 'shopee'): Promise<any[]> => {
  return apiCall<any[]>(`/api/v1/sales/track?platform=${platform}`);
};

export const getSalesTransactions = async (
  page: number = 1, 
  size: number = 20, 
  platform?: string
): Promise<{ items: any[]; total: number }> => {
  const query = new URLSearchParams({ 
    page: page.toString(), 
    size: size.toString() 
  });
  if (platform) query.append('platform', platform);
  
  return apiCall<any>(`/api/v1/sales/?${query.toString()}`);
};

// Marketplace Connections
export const getMarketplaceConnections = async (): Promise<any[]> => {
  return apiCall<any[]>('/api/v1/sales/connections');
};

export const getMarketplaceAuthUrl = async (platform: string): Promise<{ url: string }> => {
  return apiCall<{ url: string }>(`/api/v1/sales/auth/${platform}/url`);
};

export const disconnectMarketplace = async (platform: string): Promise<any> => {
  return apiCall<any>(`/api/v1/sales/connections/${platform}`, 'DELETE');
};

// =============================================================================
// TOKEN & SUBSCRIPTION API
// =============================================================================

export interface TokenBalanceResponse {
  balance: number;
  tier: string;
  dailyLimit: number;
  dailyUsed: number;
  rolloverBalance: number;
}

export interface TokenTransaction {
  id: string;
  type: string;
  amount: number;
  balanceAfter: number;
  serviceType?: string;
  createdAt: string;
}

export interface SubscriptionPackage {
  id: string;
  name: string;
  description: string;
  price: number;
  tokenAmount: number;
  tier: string;
  bonusTokens: number;
  features: Record<string, any>;
  isActive: boolean;
}

const unwrapData = <T>(response: any): T => {
  if (response && typeof response === 'object' && 'data' in response) {
    return response.data as T;
  }
  return response as T;
};

// Get current token balance
export const getTokenBalance = async (): Promise<TokenBalanceResponse> => {
  const response = await apiCall<any>('/api/v1/tokens/balance');
  const data = unwrapData<any>(response);
  return {
    balance: data.balance || 0,
    tier: data.tier || 'free',
    dailyLimit: data.daily_limit ?? data.dailyLimit ?? 50,
    dailyUsed: data.daily_used ?? data.dailyUsed ?? 0,
    rolloverBalance: data.rollover_balance ?? data.rolloverBalance ?? 0,
  };
};

// Get token transactions history
export const getTokenTransactions = async (
  page: number = 1,
  limit: number = 20,
  serviceType?: string
): Promise<{ items: TokenTransaction[]; total: number }> => {
  const query = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (serviceType) query.append('service_type', serviceType);
  
  try {
    const response = await apiCall<any>(`/api/v1/tokens/transactions?${query.toString()}`);
    const data = unwrapData<any>(response);
    return {
      items: data.transactions || data.items || [],
      total: data.total || 0,
    };
  } catch (err) {
    return { items: [], total: 0 };
  }
};

// Get available subscription packages
export const getSubscriptionPackages = async (): Promise<SubscriptionPackage[]> => {
  try {
    const response = await apiCall<any>('/api/v1/subscription/packages');
    const data = unwrapData<any>(response);
    return data.packages || response.packages || [];
  } catch (err) {
    // Return default packages
    return [
      {
        id: 'free',
        name: 'Free',
        description: 'Get started with basic features',
        price: 0,
        tokenAmount: 1000,
        tier: 'free',
        bonusTokens: 0,
        features: {},
        isActive: true,
      },
      {
        id: 'sme-monthly',
        name: 'SME Monthly',
        description: 'Perfect for growing businesses',
        price: 19,
        tokenAmount: 10000,
        tier: 'sme',
        bonusTokens: 1000,
        features: {},
        isActive: true,
      },
      {
        id: 'business-monthly',
        name: 'Business Monthly',
        description: 'For professional teams',
        price: 49,
        tokenAmount: 40000,
        tier: 'business',
        bonusTokens: 5000,
        features: {},
        isActive: true,
      },
      {
        id: 'enterprise-monthly',
        name: 'Enterprise',
        description: 'Custom solutions for large organizations',
        price: 199,
        tokenAmount: 100000,
        tier: 'enterprise',
        bonusTokens: 20000,
        features: {},
        isActive: true,
      },
    ];
  }
};

// Purchase tokens (creates Stripe checkout)
export const purchaseTokens = async (packageId: string): Promise<{ checkoutUrl: string }> => {
  return apiCall<{ checkoutUrl: string }>('/api/v1/tokens/purchase', 'POST', { package_id: packageId });
};

// Get current subscription info
export const getSubscription = async (): Promise<{
  tier: string;
  status: string;
  expiresAt: string | null;
  features: Record<string, any>;
}> => {
  try {
    const response = await apiCall<any>('/api/v1/subscription/tier');
    const data = unwrapData<any>(response);
    return {
      tier: data.tier || 'free',
      status: data.status || 'active',
      expiresAt: data.expires_at ?? data.expiresAt ?? null,
      features: data.features || {},
    };
  } catch (err) {
    return {
      tier: 'free',
      status: 'active',
      expiresAt: null,
      features: {},
    };
  }
};

// Get usage statistics
export const getUsageStats = async (period: string = 'month'): Promise<{
  totalRequests: number;
  totalTokens: number;
  byService: Record<string, number>;
  byDay: Array<{ date: string; count: number }>;
}> => {
  try {
    const response = await apiCall<any>(`/api/v1/subscription/usage?period=${period}`);
    const data = unwrapData<any>(response);
    return {
      totalRequests: data.total_requests ?? data.totalRequests ?? 0,
      totalTokens: data.total_tokens ?? data.totalTokens ?? 0,
      byService: data.by_service ?? data.byService ?? {},
      byDay: data.by_day ?? data.byDay ?? [],
    };
  } catch (err) {
    return {
      totalRequests: 150,
      totalTokens: 5000,
      byService: {
        text_llm: 3000,
        image_generation: 1500,
        agent_orchestration: 500,
      },
      byDay: [],
    };
  }
};

// Consume tokens (internal use)
export const consumeTokens = async (
  amount: number,
  serviceType: string,
  metadata?: Record<string, any>
): Promise<{ success: boolean; remaining: number }> => {
  return apiCall('/api/v1/tokens/consume', 'POST', {amount, service_type: serviceType, metadata});
};

export const addTokens = async (amount: number, source: string): Promise<boolean> => {
  await apiCall('/api/v1/tokens/add', 'POST', {amount, source});
  return true;
};

// Check feature access
export const checkFeatureAccess = async (feature: string): Promise<{ allowed: boolean; reason?: string }> => {
  try {
    const response = await apiCall<any>(`/api/v1/subscription/features/${feature}`);
    const data = unwrapData<any>(response);
    return {
      allowed: data.access ?? data.allowed ?? true,
      reason: data.reason,
    };
  } catch (err) {
    // Allow in demo mode
    return { allowed: true };
  }
};

export const geminiService = {
  getTokenBalance,
  consumeTokens,
  addTokens,
  generateBusinessCanvas,
  enhancePrompt,
  generateMarketingCopy,
  generateStrategy,
  generateVisual,
  editVisual,
  generateVideoScript,
  generateStoryboard,
  generateVideo,
  analyzeLead,
  createLead,
  getLeads,
  getLead,
  updateLead,
  assignLead,
  exportLeads,
  trackSales,
  getSalesTransactions,
  getMarketplaceConnections,
  getMarketplaceAuthUrl,
  disconnectMarketplace,
  getTokenTransactions,
  getSubscriptionPackages,
  purchaseTokens,
  getSubscription,
  getUsageStats,
  checkFeatureAccess,
};