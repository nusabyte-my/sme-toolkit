import { useState, useEffect, useCallback } from 'react';
import { geminiService } from '../services/geminiService';

export interface TokenBalance {
  balance: number;
  tier: string;
  dailyLimit: number;
  dailyUsed: number;
  rolloverBalance: number;
}

export interface TokenUsage {
  serviceType: string;
  tokens: number;
  timestamp: Date;
  cost: number;
}

export interface SubscriptionTier {
  name: string;
  monthlyTokens: number;
  dailyRequests: number;
  dailyImages: number;
  dailyVideos: number;
  features: string[];
}

export const SUBSCRIPTION_TIERS: Record<string, SubscriptionTier> = {
  free: {
    name: 'Free',
    monthlyTokens: 1000,
    dailyRequests: 50,
    dailyImages: 10,
    dailyVideos: 0,
    features: ['dashboard', 'bmc', 'leads', 'copywriter', 'visual_studio'],
  },
  sme: {
    name: 'SME',
    monthlyTokens: 10000,
    dailyRequests: 500,
    dailyImages: 50,
    dailyVideos: 5,
    features: ['dashboard', 'bmc', 'leads', 'copywriter', 'visual_studio', 'ideation', 'video_studio', 'strategy'],
  },
  business: {
    name: 'Business',
    monthlyTokens: 40000,
    dailyRequests: 2000,
    dailyImages: 200,
    dailyVideos: 20,
    features: ['dashboard', 'bmc', 'leads', 'copywriter', 'visual_studio', 'ideation', 'video_studio', 'strategy', 'api_access'],
  },
  enterprise: {
    name: 'Enterprise',
    monthlyTokens: 100000,
    dailyRequests: 10000,
    dailyImages: 1000,
    dailyVideos: 100,
    features: ['dashboard', 'bmc', 'leads', 'copywriter', 'visual_studio', 'ideation', 'video_studio', 'strategy', 'api_access', 'white_label', 'priority_support'],
  },
};

const TOKEN_COSTS = {
  text_llm: 10,        // tokens per request
  image_generation: 100,
  video_generation: 500,
  agent_orchestration: 50,
  profile_analysis: 25,
};

export function useTokens() {
  const [balance, setBalance] = useState<TokenBalance>({
    balance: 0,
    tier: 'free',
    dailyLimit: 50,
    dailyUsed: 0,
    rolloverBalance: 0,
  });
  const [usage, setUsage] = useState<TokenUsage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load token balance from backend
  const fetchBalance = useCallback(async () => {
    try {
      setLoading(true);
      const response = await geminiService.getTokenBalance();
      if (response) {
        setBalance({
          balance: response.balance || 0,
          tier: response.tier || 'free',
          dailyLimit: response.dailyLimit || SUBSCRIPTION_TIERS[response.tier || 'free']?.dailyRequests || 50,
          dailyUsed: response.dailyUsed || 0,
          rolloverBalance: response.rolloverBalance || 0,
        });
        setError(null);
      }
    } catch (err) {
      // Nielsen #1/#9: backend failure must be visible, not masked by fake data.
      // Keep last-known balance rather than silently showing mock 1000.
      const message = err instanceof Error ? err.message : 'Could not load token balance';
      console.error('Failed to fetch token balance:', err);
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Check if user has enough tokens
  const hasEnoughTokens = useCallback((serviceType: keyof typeof TOKEN_COSTS): boolean => {
    const cost = TOKEN_COSTS[serviceType];
    return balance.balance >= cost;
  }, [balance.balance]);

  // Check daily request limit
  const canMakeRequest = useCallback((): boolean => {
    return balance.dailyUsed < balance.dailyLimit;
  }, [balance.dailyUsed, balance.dailyLimit]);

  // Consume tokens for a service
  const consumeTokens = useCallback(async (
    serviceType: keyof typeof TOKEN_COSTS,
    metadata?: Record<string, any>
  ): Promise<{ success: boolean; remaining: number; error?: string }> => {
    const cost = TOKEN_COSTS[serviceType];
    
    // Check balance
    if (balance.balance < cost) {
      return {
        success: false,
        remaining: balance.balance,
        error: `Insufficient tokens. Need ${cost} tokens, have ${balance.balance}`,
      };
    }

    // Check daily limit
    if (!canMakeRequest()) {
      return {
        success: false,
        remaining: balance.balance,
        error: `Daily request limit reached. Try again tomorrow.`,
      };
    }

    try {
      // Call backend to consume tokens
      await geminiService.consumeTokens(cost, serviceType, metadata);
      
      // Update local state
      setBalance(prev => ({
        ...prev,
        balance: prev.balance - cost,
        dailyUsed: prev.dailyUsed + 1,
      }));

      // Track usage
      setUsage(prev => [{
        serviceType,
        tokens: cost,
        timestamp: new Date(),
        cost: cost / 1000, // Convert to approximate USD
      }, ...prev].slice(0, 50));

      return {
        success: true,
        remaining: balance.balance - cost,
      };
    } catch (err) {
      // Nielsen #9: never report success when the backend rejected the spend.
      const message = err instanceof Error ? err.message : 'Token service unavailable';
      console.error('Failed to consume tokens:', err);
      return {
        success: false,
        remaining: balance.balance,
        error: `${message}. Your tokens were not spent — retry when the service is back.`,
      };
    }
  }, [balance, canMakeRequest]);

  // Add tokens (after purchase or bonus)
  const addTokens = useCallback(async (amount: number, source: string): Promise<boolean> => {
    try {
      await geminiService.addTokens(amount, source);
      setBalance(prev => ({
        ...prev,
        balance: prev.balance + amount,
      }));
      setError(null);
      return true;
    } catch (err) {
      // Nielsen #9: a failed top-up must not pretend success.
      const message = err instanceof Error ? err.message : 'Token service unavailable';
      console.error('Failed to add tokens:', err);
      setError(`Token top-up failed: ${message}. Balance unchanged.`);
      return false;
    }
  }, []);

  // Get remaining daily requests
  const getRemainingRequests = useCallback((): number => {
    return Math.max(0, balance.dailyLimit - balance.dailyUsed);
  }, [balance.dailyLimit, balance.dailyUsed]);

  // Get feature access
  const hasFeatureAccess = useCallback((feature: string): boolean => {
    const tier = SUBSCRIPTION_TIERS[balance.tier.toLowerCase()];
    if (!tier) return false;
    return tier.features.includes(feature);
  }, [balance.tier]);

  // Get tier info
  const getTierInfo = useCallback((): SubscriptionTier => {
    return SUBSCRIPTION_TIERS[balance.tier.toLowerCase()] || SUBSCRIPTION_TIERS.free;
  }, [balance.tier]);

  // Set tier (after upgrade or onboarding)
  const setTier = useCallback((newTier: string, monthlyTokens?: number) => {
    const tierInfo = SUBSCRIPTION_TIERS[newTier.toLowerCase()];
    if (tierInfo) {
      setBalance(prev => ({
        ...prev,
        tier: newTier.toLowerCase(),
        dailyLimit: tierInfo.dailyRequests,
        balance: monthlyTokens ?? tierInfo.monthlyTokens,
      }));
    }
  }, []);

  useEffect(() => {
    fetchBalance();
  }, [fetchBalance]);

  return {
    balance,
    usage,
    loading,
    error,
    fetchBalance,
    hasEnoughTokens,
    canMakeRequest,
    consumeTokens,
    addTokens,
    getRemainingRequests,
    hasFeatureAccess,
    getTierInfo,
    setTier,
    TOKEN_COSTS,
  };
}

export default useTokens;