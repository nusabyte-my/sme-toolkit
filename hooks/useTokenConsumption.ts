import { useCallback } from 'react';
import { useTokens } from './useTokens';

export const SERVICE_TOKEN_COSTS = {
  text_llm: 10,
  image_generation: 100,
  video_generation: 500,
  agent_orchestration: 50,
  profile_analysis: 25,
} as const;

export type ServiceType = keyof typeof SERVICE_TOKEN_COSTS;

export const AI_SERVICE_MAP: Record<string, ServiceType> = {
  analyzeLead: 'profile_analysis',
  generateMarketingCopy: 'text_llm',
  generateVisual: 'image_generation',
  enhancePrompt: 'text_llm',
  generateVideoScript: 'text_llm',
  generateVideo: 'video_generation',
  generateStoryboard: 'text_llm',
  generateStorySceneVideo: 'video_generation',
  createGoals: 'text_llm',
  createGrowthPlan: 'text_llm',
  analyzeCosting: 'agent_orchestration',
  getBusinessSuggestions: 'text_llm',
  runOrchestrationJob: 'agent_orchestration',
  runComprehensiveAnalysis: 'agent_orchestration',
};

interface TokenCheckResult {
  allowed: boolean;
  reason?: string;
}

const useTokenConsumption = () => {
  const { hasEnoughTokens, canMakeRequest, consumeTokens, balance } = useTokens();

  const checkAccess = useCallback(
    (serviceType: ServiceType): TokenCheckResult => {
      const cost = SERVICE_TOKEN_COSTS[serviceType];
      if (balance.balance < cost) {
        return {
          allowed: false,
          reason: `Insufficient tokens. Need ${cost} tokens, have ${balance.balance}. Purchase more tokens to continue.`,
        };
      }
      if (!canMakeRequest()) {
        return {
          allowed: false,
          reason: `Daily request limit reached (${balance.dailyUsed}/${balance.dailyLimit}). Try again tomorrow.`,
        };
      }
      return { allowed: true };
    },
    [balance.balance, balance.dailyUsed, balance.dailyLimit, canMakeRequest]
  );

  const guard = useCallback(
    async <T>(
      serviceType: ServiceType,
      fn: () => Promise<T>,
      metadata?: Record<string, any>
    ): Promise<{ data?: T; error?: string }> => {
      const check = checkAccess(serviceType);
      if (!check.allowed) {
        return { error: check.reason };
      }
      const consumption = await consumeTokens(serviceType, metadata);
      if (!consumption.success) {
        return { error: consumption.error || 'Failed to process token consumption.' };
      }
      try {
        const data = await fn();
        return { data };
      } catch (err) {
        return { error: err instanceof Error ? err.message : 'An unexpected error occurred.' };
      }
    },
    [checkAccess, consumeTokens]
  );

  return { guard, checkAccess };
};

export default useTokenConsumption;
