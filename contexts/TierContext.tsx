import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiCall } from '../services/apiClient';

// Types
export interface TierFeatures {
  bmc_basic: boolean;
  bmc_analysis: boolean;
  lead_scoring: boolean;
  copywriting: boolean;
  strategy_advisor: boolean;
  growth_score: boolean;
  visual_studio: boolean;
  video_studio: boolean;
  analytics: boolean;
  api_access: boolean;
  priority_processing?: boolean;
  advanced_analytics?: boolean;
}

export interface TierLimits {
  daily_llm_requests: number;
  daily_image_requests: number;
  daily_video_requests: number;
}

export interface UsageStats {
  llm: { used: number; limit: number; remaining: number };
  image: { used: number; limit: number; remaining: number };
  video: { used: number; limit: number; remaining: number };
}

export interface TierInfo {
  id: string;
  name: string;
  price: number;
  features: string[];
  daily_llm_requests: number;
  daily_image_requests: number;
  daily_video_requests: number;
}

interface TierContextType {
  tier: string;
  tierName: string;
  features: TierFeatures;
  limits: TierLimits;
  usage: UsageStats | null;
  providers: {
    llm: string[];
    image: string[];
    video: string[];
  };
  allTiers: TierInfo[];
  loading: boolean;
  checkFeature: (feature: keyof TierFeatures) => boolean;
  refreshUsage: () => Promise<void>;
  upgradeTier: (newTier: string) => Promise<boolean>;
}

const defaultFeatures: TierFeatures = {
  bmc_basic: true,
  bmc_analysis: false,
  lead_scoring: true,
  copywriting: true,
  strategy_advisor: false,
  growth_score: false,
  visual_studio: true,
  video_studio: false,
  analytics: false,
  api_access: false
};

const defaultLimits: TierLimits = {
  daily_llm_requests: 50,
  daily_image_requests: 10,
  daily_video_requests: 0
};

const TierContext = createContext<TierContextType | undefined>(undefined);

export const TierProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [tier, setTier] = useState<string>('free');
  const [tierName, setTierName] = useState<string>('Free');
  const [features, setFeatures] = useState<TierFeatures>(defaultFeatures);
  const [limits, setLimits] = useState<TierLimits>(defaultLimits);
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [providers, setProviders] = useState<{ llm: string[]; image: string[]; video: string[] }>({
    llm: [],
    image: [],
    video: []
  });
  const [allTiers, setAllTiers] = useState<TierInfo[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch tier information
  const fetchTierInfo = useCallback(async () => {
    try {
      const response = await apiCall<{
        tier: string;
        name: string;
        features: TierFeatures;
        limits: TierLimits;
        providers: { llm: string[]; image: string[]; video: string[] };
      }>('/subscription/tier');

      setTier(response.tier);
      setTierName(response.name);
      setFeatures(response.features);
      setLimits(response.limits);
      setProviders(response.providers);
    } catch (error) {
      console.error('Failed to fetch tier info:', error);
      // Use defaults on error
    }
  }, []);

  // Fetch usage statistics
  const refreshUsage = useCallback(async () => {
    try {
      const response = await apiCall<{
        tier: string;
        usage: UsageStats;
        reset_time: string;
      }>('/subscription/usage');

      setUsage(response.usage);
    } catch (error) {
      console.error('Failed to fetch usage:', error);
    }
  }, []);

  // Fetch all available tiers
  const fetchAllTiers = useCallback(async () => {
    try {
      const response = await apiCall<{ tiers: TierInfo[] }>('/subscription/tiers');
      setAllTiers(response.tiers);
    } catch (error) {
      console.error('Failed to fetch tiers:', error);
    }
  }, []);

  // Initialize
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([
        fetchTierInfo(),
        refreshUsage(),
        fetchAllTiers()
      ]);
      setLoading(false);
    };
    init();
  }, [fetchTierInfo, refreshUsage, fetchAllTiers]);

  // Check if user has access to a feature
  const checkFeature = useCallback((feature: keyof TierFeatures): boolean => {
    return features[feature] ?? false;
  }, [features]);

  // Upgrade tier
  const upgradeTier = useCallback(async (newTier: string): Promise<boolean> => {
    try {
      const response = await apiCall<{ success: boolean; tier?: string; message: string }>(
        '/subscription/upgrade',
        'POST',
        { tier: newTier }
      );

      if (response.success) {
        await fetchTierInfo();
        await refreshUsage();
        return true;
      }

      console.error('Upgrade failed:', response.message);
      return false;
    } catch (error) {
      console.error('Failed to upgrade tier:', error);
      return false;
    }
  }, [fetchTierInfo, refreshUsage]);

  const value: TierContextType = {
    tier,
    tierName,
    features,
    limits,
    usage,
    providers,
    allTiers,
    loading,
    checkFeature,
    refreshUsage,
    upgradeTier
  };

  return (
    <TierContext.Provider value={value}>
      {children}
    </TierContext.Provider>
  );
};

export const useTier = (): TierContextType => {
  const context = useContext(TierContext);
  if (!context) {
    throw new Error('useTier must be used within a TierProvider');
  }
  return context;
};

export default TierContext;
